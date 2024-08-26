import re
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
        raise ValueError("Error: Couldn't find the desired API key in the environment variables")
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





def initialize_text_holder(file_path):
    text_holder_path = f"{file_path}_text_holder.txt"
    with open(text_holder_path, 'w', encoding='utf-8') as file:
        file.write("")  # Start with an empty file
    print(f"Initialized text holder file: {text_holder_path}")
    return text_holder_path

def extract_chinese_phrases(text, text_holder_path):
    """Extracts Chinese text phrases within quotation marks from the input string and stores them in a text holder."""
    # This regex is stricter and looks for Chinese characters strictly within quotation marks
    chinese_phrases = re.findall(r'"([\u4e00-\u9fff]+[^"]*)"', text)
    print(f"\nExtracted Chinese Text Phrases:\n{chinese_phrases}")

    with open(text_holder_path, 'a', encoding='utf-8') as holder:
        for i, phrase in enumerate(chinese_phrases):
            unique_id = f"UNIQUE_ID_{i:08d}"
            holder.write(f"{unique_id}: {phrase}\n")
            text = text.replace(f'"{phrase}"', f'"{unique_id}"')
    
    return text

def translate_chinese_phrases(text_holder_path):
    """Translates the Chinese text stored in the text holder file."""
    with open(text_holder_path, 'r', encoding='utf-8') as holder:
        content = holder.read().strip()

    print(f"\nSending the following text to the API for translation:\n{content}")

    # Translate the content using the appropriate model and API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust model as needed
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional translator with expertise in translating video game localization files. "
                    "You are given text extracted from .YML from a Crusader Kings 3 or even a mod for the game."
                    "Translate only the Chinese text into English while preserving the identifiers and formatting."
                )
            },
            {"role": "user", "content": content},
        ]
    )

    translated_content = response.choices[0].message.content.strip()

    print(f"\nReceived the following translated content:\n{translated_content}")

    translated_holder_path = f"{text_holder_path}_translated.txt"
    with open(translated_holder_path, 'w', encoding='utf-8') as translated_holder:
        translated_holder.write(translated_content)
    
    return translated_holder_path

def replace_identifiers_with_translations(text, translated_holder_path):
    """Replaces unique identifiers in the original text with their corresponding translated phrases."""
    with open(translated_holder_path, 'r', encoding='utf-8') as translated_holder:
        translated_lines = translated_holder.read().strip().split("\n")
        translation_map = {}
        for line in translated_lines:
            if ": " in line:
                unique_id, translated_phrase = line.split(": ", 1)
                translation_map[unique_id.strip()] = translated_phrase.strip()

    for unique_id, translated_phrase in translation_map.items():
        text = text.replace(unique_id, translated_phrase)

    return text

def translate_file(file_path):
    # Step 1: Initialize the text holder
    text_holder_path = initialize_text_holder(file_path)

    # Step 2: Read the original YAML content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    print(f"\nProcessing File: {file_path}")

    # Step 3: Extract Chinese phrases and replace them with unique identifiers
    content_with_placeholders = extract_chinese_phrases(content, text_holder_path)

    # Step 4: Translate the extracted Chinese phrases
    translated_holder_path = translate_chinese_phrases(text_holder_path)

    # Step 5: Replace placeholders with translated phrases
    final_translated_content = replace_identifiers_with_translations(content_with_placeholders, translated_holder_path)

    # Step 6: Save the final translated content back to the original file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(final_translated_content)

    print(f"Translation complete. Translated file saved as {file_path}")

def translate_all_yml_files_in_directory():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.yml'):
            file_path = os.path.join(current_directory, file_name)
            print(f"\nTranslating file: {file_name}")
            translate_file(file_path)
            print("\nWaiting a few seconds before moving to the next file...\n")

# Example usage:
translate_all_yml_files_in_directory()