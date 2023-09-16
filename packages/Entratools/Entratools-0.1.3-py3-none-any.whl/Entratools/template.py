import requests
import pandas
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
import sys
from Entratools import General
import logging
from datetime import date, timedelta, datetime
import time

# Configure Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
Handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
Handler.setFormatter(formatter)
logger.addHandler(Handler)

def main(BUSINESS_UNIT, REPORT, DAYS_BACK, OFFSET):
    
    # Get database, schema, and table through environment variable
    logger.info(f"Business Unit: {BUSINESS_UNIT}")
    stagingDatabase = os.getenv('stagingDatabase')
    targetDatabase = os.getenv('targetDatabase')
    targetSchema = "%SCHEMA%"
    metaDatabase = os.getenv('metaDatabase')
    environmentDict = {'stagingDatabase' : stagingDatabase, 'targetDatabase': targetDatabase, 'schema' : targetSchema, 'metaDatabase': metaDatabase}
    
    # Create snowflake connection
    con = snow.connect(
        account = 'EVCAGILE',
        user=os.getenv('snowflake_username'),
        password=os.getenv('snowflake_password'),
        database=stagingDatabase,
        schema="%SCHEMA%"
    )

    conMeta = snow.connect(
        account = 'EVCAGILE',
        user=os.getenv('snowflake_username'),
        password=os.getenv('snowflake_password'),
        database=metaDatabase,
        schema="%SCHEMA%"
    )

    # Query metadata tables for API token and business unit prefix
    accountsQuery = f"select * from {metaDatabase}.{targetSchema}.ACCOUNTS WHERE BUSINESS_UNIT = '{BUSINESS_UNIT}'"
    accountsDf = General.query_meta_data(con, accountsQuery)
    apiToken = accountsDf.iloc[0,1]
    accountPrefix = accountsDf.iloc[0,2]
    
    # Query metadata for url information (Target table, base URL, endpoint, parameters, primary key)
    reportQuery = f"select * from {metaDatabase}.{targetSchema}.{targetSchema}_REPORTS WHERE NAME = '{REPORT}'"
    reportDf = General.query_meta_data(con, reportQuery)
    targetTable = reportDf.iloc[0,2]
    baseUrl = reportDf.iloc[0,3]
    endpoint = reportDf.iloc[0,4]
    Parameters = reportDf.iloc[0,6]
    primaryKey = reportDf.iloc[0,7]

    # Define target table, start and end dates. Log endpoint
    targetTable = {targetTable}
    endDate = (date.today() - timedelta(days=OFFSET))
    startDate = (endDate - timedelta(days=DAYS_BACK))
    logger.info(f"Endpoint: {endpoint}")

    # Truncating staging table
    con.cursor().execute(f"truncate table {stagingDatabase}.{targetSchema}.{targetTable}")

    
    df = pd.DataFrame()
    attempt = 1
    while True:
        url = """URL HERE"""

        logger.info(f"Request ({i})")
        logger.info(f"From date: {startDate} to {endDate}")
        logger.info(f"url={url}")

        # Make API call
        message = 'OK'
        try:
            response = """Make API call"""
            statusCode = response.status_code
            response = response.content
            logger.info(f"Status code: {statusCode}")

            if statusCode != 200:
                raise Exception

        except Exception as e:
            """Add errorhandling here"""

            logger.warning(response)
            message = response

            # Retry 3 times
            if (attempt < 3):
                logger.warning("Retrying in 90 seconds..\n")
                attempt = attempt + 1
                time.sleep(90)
                logger.warning(f"Attempt {attempt}")
                continue
            # After 3 retries
            if attempt == 3:
                logger.error("Failed 3 times, exiting..")
                sys.exit(1)

        # If no exceptions have been raised, the rest of the code will continue to execute
        else:
            
            # Use pandas library to load the response into a datafarme
            try:
                """Create dataframe logic here"""
                if len(df) == 0:
                    raise Exception
            # Warning for empty data
            except Exception:
                logger.warning("Data frame is empty\n")
            else:
                # Reorder and drop columns
                OrigHeaderList = General.headers_list(conMeta, REPORT, "ORIGINAL_HEADER", environmentDict)
                df = df[OrigHeaderList]
                # Rename new headers
                newHeaderList = General.headers_list(conMeta, REPORT, "NEW_HEADER", environmentDict)
                df.columns = newHeaderList

                # Write data to snowflake staging table
                write_pandas(con, df, targetTable)

                logger.info(f"{len(df)} records have been loaded into the data frame")
                logger.info(f"{len(df)} records written to {targetTable}\n")
            break

    responseList = list([None, statusCode, len(df), startDate, endDate, str(message)])
    General.sys_event_log(conMeta, BUSINESS_UNIT, REPORT, responseList, environmentDict)
        
    """
        INCREMENTAL LOGIC BELOW
    """
    General.incrmental_model(con,targetSchema,targetTable,primaryKey,'Upsert-merge')

    logger.info(f"Processes Completed Succesfully")

if __name__ == '__main__':

    BUSINESS_UNIT = sys.argv[1]
    REPORT = sys.argv[2]
    DAYS_BACK = int(sys.argv[3])
    OFFSET = int(sys.argv[4])

    main(BUSINESS_UNIT, REPORT, DAYS_BACK, OFFSET)
