import os
import time
from initialize_text_holder import initialize_text_holder
from translation_operations import process_translation
from file_io import read_yaml_content, save_translated_content
from api_key_loader import debug_load_dotenv, debug_get_api_key, debug_openai_client


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
# yes or no or interger (for seconds)


# Wait mode: determines whether program should wait for user input before continuing
# yes or no or integer (for seconds)
wait_mode = "no"


def wait_if_needed(wait_mode):
    if wait_mode.lower() == "yes":
        input("Press Enter to continue...")
    elif wait_mode.isdigit():
        time.sleep(int(wait_mode))
    elif wait_mode.lower() == "no":
        pass
    else:
        print("Invalid wait mode. Continuing without waiting.")


def translate_file(file_path, client):
    # Step 1: Initialize both the text holder for untranslated and translated text
    print("Initializing text holders")
    wait_if_needed(wait_mode)
    """Main function to handle the translation of a YAML file."""
    text_holder_path = initialize_text_holder(file_path)
    translated_holder_path = f"{text_holder_path}_translated.txt"  # Assuming you want the translated holder initialized as well
    with open(translated_holder_path, "w", encoding="utf-8") as file:
        file.write("")  # Start with an empty file

    # Step 2: Read the original YAML content
    print("Reading the original YAML content")
    wait_if_needed(wait_mode)
    content = read_yaml_content(file_path)

    # Step 3: Process the translation (extract, translate, replace)
    print("Processing the translation (extract, translate, replace)")
    wait_if_needed(wait_mode)
    final_translated_content = process_translation(content, text_holder_path, client)

    # Step 4: Save the final translated content back to the original file
    print("Saving the final translated content back to the original file")
    wait_if_needed(wait_mode)
    save_translated_content(file_path, final_translated_content)

    print(f"Translation complete. Translated file saved as {file_path}")
    wait_if_needed(wait_mode)


import os
from initialize_text_holder import (
    initialize_text_holder,
    initialize_translated_text_holder,
)
from translation_operations import process_translation
from api_key_loader import load_api_key
from api_calls import initialize_openai_client


def main():
    api_key = load_api_key(".env")
    client = initialize_openai_client(api_key)

    current_directory = os.getcwd()
    print(f"Current directory path: {current_directory}")

    for root, dirs, files in os.walk(current_directory):
        for file_name in files:
            if file_name.endswith(".yml"):
                file_path = os.path.join(root, file_name)
                print(f"Translating file: {file_name}")
                text_holder_path = file_path + "_text_holder.txt"
                initialize_text_holder(text_holder_path)
                translated_text_holder_path = file_path + "_translated_text_holder.txt"
                initialize_translated_text_holder(translated_text_holder_path)
                process_translation(
                    file_path, client, text_holder_path, translated_text_holder_path
                )


if __name__ == "__main__":
    main()


# This function will order the translation of all files with the extension .yml in the current directory
def manage_translation_tasks(client):

    # Print fetching current directory path
    print(f"Current directory path: {os.path.dirname(os.path.abspath(__file__))}")
    wait_if_needed(wait_mode)
    # Get the absolute path of the current directory where this script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # prinnt iterating over all files in the current directory
    print("Iterating over all files in the current directory")
    wait_if_needed(wait_mode)
    # Iterate over all files in the current directory
    for file_name in os.listdir(current_directory):
        # Check if the file has a .yml extension
        if file_name.endswith(".yml"):
            # Construct the full file path
            file_path = os.path.join(current_directory, file_name)

            # Print a message indicating which file is being translated
            print(f"\nTranslating file: {file_name}")

            # Call the translate_file function to translate the content of the file
            translate_file(file_path, client)

            # Print a message indicating a pause before moving to the next file
            print("\nWaiting a few seconds before moving to the next file...\n")


# Example usage:
manage_translation_tasks(client)
