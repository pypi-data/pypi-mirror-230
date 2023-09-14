import typer
import os
import re


app = typer.Typer()


@app.command()
def createTemplate(name: str):

    # Define the parent directory where you want to create a new folder
    parent_directory = '/workspaces/Custom-ETL/Jobs'

    # Define the name of the new folder
    new_folder_name = name

    # Define the name of the file to be created
    file_name = 'script.py'

    # Define the template file name
    template_file_name = 'template.py'

    # Create the full path for the new folder
    new_folder_path = os.path.join(parent_directory, new_folder_name)

    # Create the new folder if it doesn't exist
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    # Create the full path for the new file
    new_file_path = os.path.join(new_folder_path, file_name)

    # Read content from the template file
    template_file_path = os.path.join(os.path.dirname(__file__), template_file_name)
    with open(template_file_path, 'r') as template_file:
        file_content = template_file.read()
    
    file_content = file_content.replace("%SCHEMA%", name)

    # Create and write the content to the new file
    with open(new_file_path, 'w') as file:
        file.write(file_content)

    print(f"Created folder: {new_folder_path}")
    print(f"Created file: {new_file_path}")

@app.command()
def makedev(folder: str, file: str):

    parent_directory = '/workspaces/Custom-ETL/Jobs/{folder}'
    # Define the name of the file to be created
    file_name = '{file}.py'
    # Read content from the file
    file_path = os.path.join(parent_directory, file_name)
    
    file_path = '/workspaces/Custom-ETL/Jobs/Simplifi/report.py'
    with open(file_path, 'r') as template_file:
        file_content = template_file.read()

    patterns = ["[\",\']TOUKIL[\"\']",r'General.get_secret\("Snowflake_PW"\)']
    replacements = [r"os.getenv('snowflake_username')",r"os.getenv('snowflake_password')"]
    print(patterns[0] + patterns[1])
    print(replacements[0] + replacements[1])
    file_content = re.sub(patterns[0], replacements[0], file_content)
    file_content = re.sub(patterns[1], replacements[1], file_content)

    # file_content = file_content.replace("os.getenv\('snowflake_username'\)", "TOUKIL")
    # file_content = file_content.replace("os.getenv(\'snowflake_password\')", "General.get_secret(\"Snowflake_PW\")")


    # Create and write the content to the new file
    with open(file_path, 'w') as file:
        file.write(file_content)

    print(f"File accomodated for development: {file_path}")

@app.command()
def makeprod(folder: str, file: str):

    parent_directory = '/workspaces/Custom-ETL/Jobs/{folder}'
    # Define the name of the file to be created
    file_name = '{file}.py'
    # Read content from the file
    file_path = os.path.join(parent_directory, file_name)
    
    file_path = '/workspaces/Custom-ETL/Jobs/Simplifi/report.py'
    with open(file_path, 'r') as template_file:
        file_content = template_file.read()

    replacements = ["\"TOUKIL\"",r'General.get_secret("Snowflake_PW")']
    patterns = [r"os.getenv\('snowflake_username'\)",r"os.getenv\('snowflake_password'\)"]
    print(patterns[0] + patterns[1])
    print(replacements[0] + replacements[1])

    file_content = re.sub(patterns[0], replacements[0], file_content)
    file_content = re.sub(patterns[1], replacements[1], file_content)

    # Create and write the content to the new file
    with open(file_path, 'w') as file:
        file.write(file_content)

    print(f"File accomodated for development: {file_path}")