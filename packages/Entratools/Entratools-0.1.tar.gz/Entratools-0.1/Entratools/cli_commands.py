# Utils/utils/cli_commands.py
import argparse

def cli_command():
    # Define your CLI command using argparse
    parser = argparse.ArgumentParser(description='Description of your command')
    # Add arguments and options
    parser.add_argument('--option', help='Description of an option')
    args = parser.parse_args()
    # Command logic based on args
    pass