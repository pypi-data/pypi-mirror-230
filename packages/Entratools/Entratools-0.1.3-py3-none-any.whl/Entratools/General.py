import pandas as pd
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError
import json
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import time
import snowflake.connector as snow

def query_meta_data(connMeta, metaQuery):
    metaCursor = connMeta.cursor()

    # Execute query
    metaCursor.execute(metaQuery)
    query_response = metaCursor.fetch_pandas_all()

    # read all rows from snowflake query and store in variable
    df = pd.DataFrame(query_response)

    # close connection cursor
    metaCursor.close()

    return df


def headers_list(connMeta, report, field, environmentDict):
    metaDatabase = environmentDict['metaDatabase']
    schema = environmentDict['schema']

    origHeaderQuery = f"SELECT {field} FROM {metaDatabase}.{schema}.TABLE_COLUMNS WHERE upper(API) ='{report}' ORDER BY ROW_COUNT::INT asc"

    dfHeader = query_meta_data(connMeta, origHeaderQuery)

    #Remove Null rows
    dfHeader = dfHeader.dropna()

    HeaderList = []
    for row in range(len(dfHeader)):
        HeaderList.append(dfHeader.iloc[row, 0])

    return HeaderList


def sys_event_log(connSnF, business_unit,api, api_response_list,environmentDict):
    # Establish cursor to execute snowflake queries
    curs_event = connSnF.cursor()
    # list([advertiser_id, code, len(df), start_date, end_date, message])
    app_id = api_response_list[0]
    status_code = api_response_list[1]
    num_records = api_response_list[2]
    request_date = api_response_list[3]
    response_message = api_response_list[5]
    from_date_time = api_response_list[3]
    to_date_time =  api_response_list[4]
    metaDatabase = environmentDict['metaDatabase']
    schema = environmentDict['schema']

    # LOG EVENT
    run_time = datetime.now()

    response_message = response_message.replace("'","")

    log_statement = f"INSERT INTO {metaDatabase}.{schema}.ETL_API_CALL_LOG (BUSINESS_UNIT, APP_ID ,API, STATUS_CODE , RECORDS_LOADED, REQUEST_DATE, SYS_RUN_TIME, FROM_DATE_TIME, TO_DATE_TIME, RESPONSE_MESSAGE)" \
                    f"VALUES ('{str(business_unit)}', '{str(app_id)}', '{str(api)}', '{str(status_code)}', '{str(num_records)}', '{str(request_date)}', '{str(run_time)}', '{str(from_date_time)}', '{str(to_date_time)}', '{str(response_message)}')"


    curs_event.execute(log_statement)

    # Close cursor
    curs_event.close()


# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/




def get_secret(secretNameValue):

    secretName = secretNameValue
    regionName = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=regionName
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secretName
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secretDict = json.loads(get_secret_value_response['SecretString'])
    secret = secretDict[secretNameValue]

    return secret

def email(subject, body):

    email_list = ["tyler.klukken@entravision.com", "tarik.oukil@entravision.com", "emiliano.fripp@entravision.com"]

    for person in email_list:

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = "bi.ingest@entravision.com"
        msg['To'] = person

        # add body as an attachment
        attach1 = MIMEText(body, 'html')

        # Attach parts into message container.
        msg.attach(attach1)

        # Send the message via gmail SMTP server.
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login("bi.ingest@entravision.com", get_secret("BI_GMAIL_PW"))
        s.send_message(msg)
        s.quit()

def incrmental_model(con,targetSchema,targetTable,primaryKey=None,type='Upsert-Merge'):
    failed = False
    stagingDatabase = os.environ.get('stagingDatabase')
    targetDatabase = os.environ.get('targetDatabase')
    if type == 'Upsert-Merge':
        con.cursor().execute(f"DELETE FROM {targetDatabase}.{targetSchema}.{targetTable} WHERE {primaryKey} in (SELECT {primaryKey} from {stagingDatabase}.{targetSchema}.{targetTable})")
        con.cursor().execute(f"INSERT INTO {targetDatabase}.{targetSchema}.{targetTable} (SELECT *, CURRENT_TIMESTAMP from {stagingDatabase}.{targetSchema}.{targetTable})")
    elif type == 'Append':
        con.cursor().execute(f"INSERT INTO {targetDatabase}.{targetSchema}.{targetTable} (SELECT *, CURRENT_TIMESTAMP from {stagingDatabase}.{targetSchema}.{targetTable})")
    else:
        failed = True
    con.cursor().execute(f"TRUNCATE TABLE {stagingDatabase}.{targetSchema}.{targetTable}")
    if failed == True:
        raise Exception("Incremental model type doesn't exist")


if __name__ == '__main__':
    pass