import os
import glob
import re
import tiktoken
from translate import (
    custom_yml_parser,
    extract_chinese_phrases,
    replace_with_ids,
    split_into_chunks,
)

# Path to the directory containing YAML files
translation_directory = r"./to be translated2"

# Initialize tiktoken encoding based on the selected model
model_name = "gpt-4o"  # Use the same model as in your main script
encoding = tiktoken.encoding_for_model(model_name)

# Define token and line limits
TOKEN_LIMIT = 3500  # Adjust if necessary for other models
LINE_LIMIT = 100  # Max lines or IDs in a chunk
ID_FORMAT = "ID{:06d}"  # ID format: ID000000 to ID999999


# Custom YAML-like parser function (same as in your main script)
def custom_yml_parser(file_content):
    data = {}
    lines = file_content.splitlines()
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()

        # Skip empty lines or lines that are comments
        if not line or line.startswith("#"):
            continue

        # Match a key-value pair
        match = re.match(r"^(.*?):\s*(.*)$", line)
        if match:
            key, value = match.groups()

            # Handle cases where the value is in quotes and may contain Chinese text
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]  # Strip surrounding quotes
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]  # Strip surrounding single quotes

            # Add to dictionary
            data[key] = value
        else:
            print(f"Warning: Skipping malformed line at {line_number}: {line}")

    return data


# Function to log the chunks as they would be sent to the API
def log_chunks(chunks, log_file_path):
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        for i, chunk in enumerate(chunks, start=1):
            log_file.write(f"Chunk {i}:\n")
            for uid, phrase in chunk:
                log_file.write(f"{uid}: {phrase}\n")
            log_file.write("\n")
    print(f"Chunks have been logged to {log_file_path}")


# Testing function to create and log chunks
def test_create_chunks():
    # Find the first .yml file in the directory to test with
    yaml_files = glob.glob(os.path.join(translation_directory, "*.yml"))
    if not yaml_files:
        print("No .yml files found in the specified directory.")
        return

    test_file_path = yaml_files[0]
    print(f"Testing with file: {test_file_path}")

    # Read the file content
    with open(test_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    # Extract Chinese phrases using the custom parser
    phrases = extract_chinese_phrases(file_content)

    # Replace extracted phrases with unique IDs
    file_content, id_map = replace_with_ids(file_content, phrases)

    # Split the content into chunks
    chunks = split_into_chunks(id_map)

    # Log the chunks to a file for review
    log_file_path = test_file_path.replace(".yml", "_chunks_logged.txt")
    log_chunks(chunks, log_file_path)

    print("Chunk creation and logging complete.")


# Run the test function
if __name__ == "__translate__":
    test_create_chunks()
