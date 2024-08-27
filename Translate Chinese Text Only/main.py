import re
import os
from openai import OpenAI
from dotenv import load_dotenv
from initialize_text_holder import initialize_text_holder
from text_processing import extract_chinese_phrases
from api_calls import translate_chinese_phrases
from file_operations import (
    replace_identifiers_with_translations,
    translate_file,
    translate_all_yml_files_in_directory,
)


# Debug functions for loading .env and initializing OpenAI client
def debug_load_dotenv(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Couldn't find the file at {file_path}")
    try:
        load_dotenv(file_path)
        print(f"Loaded .env file from {file_path}")
    except Exception as e:
        raise Exception(f"Error: Couldn't load .env file. {str(e)}")


def debug_get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError(
            "Error: Couldn't find the desired API key in the environment variables"
        )
    print("API key retrieved successfully")
    return api_key


def debug_openai_client(api_key):
    try:
        client = OpenAI(api_key=api_key)
        print("OpenAI client initialized successfully")
    except Exception as e:
        raise Exception(f"Error: Couldn't initialize OpenAI client. {str(e)}")
    return client


# Path to the .env file
file_path = r"D:\Documents\Self help websites and data for games etc\paradox\ck3\Auto-translator-for-paradox-localisations\keys.env"

# Load environment variables from .env file
debug_load_dotenv(file_path)

# Get the OpenAI API key
api_key = debug_get_api_key()

# Print the API key for confirmation (remove in production)
print(f"API Key: {api_key}")

# Initialize OpenAI client
client = debug_openai_client(api_key)

# Path to the directory that needs to be translated (function related to this to be implemented at a later time)
directory_path = r""

# Wait mode: determines whether program should wait for user input before continuing (function related to this to be implemented at a later time)
# yes or no
wait_mode = "no"


def translate_all_yml_files_in_directory(client):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for file_name in os.listdir(current_directory):
        if file_name.endswith(".yml"):
            file_path = os.path.join(current_directory, file_name)
            print(f"\nTranslating file: {file_name}")
            translate_file(file_path, client)
            print("\nWaiting a few seconds before moving to the next file...\n")


# Example usage:
translate_all_yml_files_in_directory(client)
