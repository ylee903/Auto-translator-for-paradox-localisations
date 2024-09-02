import os
from openai import OpenAI
from dotenv import load_dotenv


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
