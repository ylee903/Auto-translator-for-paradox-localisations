import openai
import yaml
import re
import os
import glob
import tiktoken
import time
from api_key_loader import debug_load_dotenv, debug_get_api_key

# Central delay parameter (in seconds)
delay_time = 1  # Set to 0 for no delay, or any integer for a delay in seconds

# Parameter to control whether to log chunks to a text file
log_chunks = True  # Set to True to log chunks, False to disable logging

# Parameter to control whether to overwrite the original .yml files
overwrite_original = True  # Set to True to overwrite, False to save as _translated.yml

# Path to the .env file
file_path = r"D:\Documents\Self help websites and data for games etc\paradox\ck3\Auto-translator-for-paradox-localisations\keys.env"

# Load environment variables from .env file
debug_load_dotenv(file_path)

# Get the OpenAI API key
api_key = debug_get_api_key()

# Print the API key for confirmation (remove in production)
print(f"API Key: {api_key}")

# Load your OpenAI API key
openai.api_key = api_key

# Initialize tiktoken encoding
encoding = tiktoken.encoding_for_model("gpt-4")

# Define regular expression for extracting Chinese text
chinese_text_regex = r'"([\u4e00-\u9fff]+[^"]*)"'

# Define token limit
TOKEN_LIMIT = 3500
ID_FORMAT = "ID{:03d}"


def extract_chinese_phrases(file_content):
    matches = re.findall(chinese_text_regex, file_content)
    print(f"Extracted {len(matches)} Chinese phrases.")
    return matches


def replace_with_ids(file_content, phrases):
    id_map = {}
    for i, phrase in enumerate(phrases):
        unique_id = ID_FORMAT.format(i)
        file_content = file_content.replace(f'"{phrase}"', f'"{unique_id}"')
        id_map[unique_id] = phrase
    print(f"Replaced phrases with {len(id_map)} unique IDs.")
    return file_content, id_map


def split_into_chunks(id_map):
    chunks = []
    current_chunk = []
    current_tokens = 0

    for unique_id, phrase in id_map.items():
        phrase_tokens = len(encoding.encode(phrase))
        if current_tokens + phrase_tokens > TOKEN_LIMIT:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0
        current_chunk.append((unique_id, phrase))
        current_tokens += phrase_tokens

    if current_chunk:
        chunks.append(current_chunk)

    print(f"Split into {len(chunks)} chunks for translation.")
    return chunks


def translate_chunks(chunks, client):
    translated_chunks = []
    for chunk_index, chunk in enumerate(chunks):
        text_to_translate = "\n".join([phrase for _, phrase in chunk])
        print(f"Translating chunk {chunk_index + 1} with {len(chunk)} phrases.")

        if log_chunks:
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"Chunk {chunk_index + 1} sent to API:\n{text_to_translate}\n\n"
                )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator with expertise in translating video game localization files. "
                        "You are given text extracted from .YML files from a Crusader Kings 3 mod. "
                        "Translate only the Chinese text into English while preserving the identifiers and formatting."
                    ),
                },
                {"role": "user", "content": text_to_translate},
            ],
        )

        translated_text = response.choices[0].message.content.strip()
        translated_phrases = translated_text.split("\n")

        # Check if the number of lines sent matches the number of lines received
        if len(translated_phrases) != len(chunk):
            error_message = (
                f"Error: Mismatch in the number of lines sent and received "
                f"for chunk {chunk_index + 1}. "
                f"Sent {len(chunk)} lines, received {len(translated_phrases)} lines."
            )
            print(error_message)
            raise ValueError(error_message)

        if log_chunks:
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"Chunk {chunk_index + 1} received from API:\n{translated_text}\n\n"
                )

        translated_chunk = {
            unique_id: translated_phrase
            for (unique_id, _), translated_phrase in zip(chunk, translated_phrases)
        }
        translated_chunks.append(translated_chunk)

    print(f"Translation completed for {len(chunks)} chunks.")
    return translated_chunks


def reassemble_text(file_content, translated_chunks):
    for translated_chunk in translated_chunks:
        for unique_id, translated_phrase in translated_chunk.items():
            file_content = file_content.replace(
                f'"{unique_id}"', f'"{translated_phrase}"'
            )
    print(f"Reassembled translated content.")
    return file_content


def translate_yaml_file(file_path, client):
    print(f"Processing file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    phrases = extract_chinese_phrases(file_content)
    file_content, id_map = replace_with_ids(file_content, phrases)
    chunks = split_into_chunks(id_map)
    translated_chunks = translate_chunks(chunks, client)
    translated_content = reassemble_text(file_content, translated_chunks)

    # Determine the output file path based on the overwrite_original parameter
    if overwrite_original:
        output_file_path = file_path
    else:
        output_file_path = file_path.replace(".yml", "_translated.yml")

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(translated_content)

    print(f"Translated file saved as {output_file_path}")

    if delay_time > 0:
        time.sleep(delay_time)

    return output_file_path


def translate_all_files_in_subdirectory(client):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Define the log file path
    global log_file_path
    log_file_path = os.path.join(script_dir, "chunks_log.txt")

    # Define the subdirectory where YAML files are located
    subdirectory = os.path.join(script_dir, "to be translated")

    # Find all .yml files in the subdirectory
    yaml_files = glob.glob(os.path.join(subdirectory, "*.yml"))

    print(f"Found {len(yaml_files)} files to translate.")
    for yaml_file in yaml_files:
        output_file = translate_yaml_file(yaml_file, client)


# Assuming `client` is already initialized and configured
client = openai

# Run the translation on all YAML files in the specified subdirectory
translate_all_files_in_subdirectory(client)
