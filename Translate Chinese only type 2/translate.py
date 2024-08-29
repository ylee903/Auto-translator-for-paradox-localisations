import openai
import yaml
import re
import os
import glob
import tiktoken
import time
import asyncio
import aiohttp
from api_key_loader import debug_load_dotenv, debug_get_api_key

# Central delay parameter (in seconds)
delay_time = 1  # Set to 0 for no delay, or any integer for a delay in seconds

# Parameter to control whether to log chunks to a text file
log_chunks = True  # Set to True to log chunks, False to disable logging

# Parameter to control whether to overwrite the original .yml files
overwrite_original = True  # Set to True to overwrite, False to save as _translated.yml

# Parameter to control whether to add unique sub-IDs to each line
enable_sub_ids = True  # Set to True to add sub-IDs, False to disable

# Parameter to control the maximum number of concurrent asynchronous requests
max_concurrent_requests = 3  # Adjust this value to control concurrency

# Parameter to select the model to use for both tokenization and API calls
model_name = (
    "gpt-4o-mini"  # Can be "gpt-4", "gpt-3.5-turbo", or any other supported model
)

# Parameter to determine if the program will ignore mismatches in the number of lines/sub-IDs
ignore_mismatch = True  # Set to True to ignore mismatches, False to raise an error

# Retry configuration
max_retries = 999  # Maximum number of retries for rate limit errors (customizable)
initial_wait_time = 5  # Initial wait time before retrying (in seconds)

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

# Initialize tiktoken encoding based on the selected model
encoding = tiktoken.encoding_for_model(model_name)

# Define regular expression for extracting Chinese text
chinese_text_regex = r'"([\u4e00-\u9fff]+[^"]*)"'

# Define token limit and line limit
TOKEN_LIMIT = (
    3500  # This is generally safe for GPT-4; adjust if necessary for other models
)
LINE_LIMIT = 50  # Maximum number of lines or IDs in a chunk
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
        # Check if adding the next line will exceed the line or token limit
        if (
            current_tokens + phrase_tokens > TOKEN_LIMIT
            or len(current_chunk) >= LINE_LIMIT
        ):
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0
        if enable_sub_ids:
            phrase = f"{ID_FORMAT.format(len(current_chunk))} {phrase}"
        current_chunk.append((unique_id, phrase))
        current_tokens += phrase_tokens

    if current_chunk:
        chunks.append(current_chunk)

    print(f"Split into {len(chunks)} chunks for translation.")
    return chunks

async def translate_chunk_async(chunk, session, chunk_index, semaphore, log_dir):
    async with semaphore:
        text_to_translate = "\n".join([phrase for _, phrase in chunk])
        print(
            f"Translating chunk {chunk_index + 1} with {len(chunk)} phrases asynchronously."
        )

        if log_chunks:
            # Log before sending the chunk to the API
            with open(os.path.join(log_dir, f"log_chunk_{chunk_index + 1}_sent.txt"), "w", encoding="utf-8") as log_file:
                log_file.write(
                    f"Chunk {chunk_index + 1} sent to API:\n{text_to_translate}\n\n"
                )

        retries = 0
        wait_time = initial_wait_time

        while retries < max_retries:
            try:
                response = await session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a professional translator with expertise in translating video game localization files. "
                                    "You are given text extracted from .YML files from a Crusader Kings 3 mod. "
                                    "Translate only the Chinese text into English while maintaining the identifiers and formatting. "
                                    "Ensure that the number of lines/IDs in the translated output matches the number of lines/IDs in the input. "
                                    "If a perfect match cannot be achieved, fill the missing translated lines with the placeholder text '[MISSING]'. "
                                    "If you encounter any issues or have difficulties translating certain lines, include diagnostic information at the end of the response, clearly separated by '===DIAGNOSTIC===' without affecting the translation."
                                ),
                            },
                            {"role": "user", "content": text_to_translate},
                        ],
                    },
                    headers={"Authorization": f"Bearer {openai.api_key}"},
                )
                response.raise_for_status()
                response_json = await response.json()
                translated_text = response_json["choices"][0]["message"][
                    "content"
                ].strip()

                # Split the response into translation and diagnostics
                if "===DIAGNOSTIC===" in translated_text:
                    translated_text, diagnostics = translated_text.split(
                        "===DIAGNOSTIC==="
                    )
                    diagnostics = diagnostics.strip()
                    print(
                        f"Diagnostic information for chunk {chunk_index + 1}:\n{diagnostics}"
                    )
                    if log_chunks:
                        with open(os.path.join(log_dir, f"log_chunk_{chunk_index + 1}_diagnostic.txt"), "w", encoding="utf-8") as log_file:
                            log_file.write(
                                f"Diagnostic for chunk {chunk_index + 1}:\n{diagnostics}\n\n"
                            )
                else:
                    diagnostics = None

                translated_phrases = translated_text.split("\n")

                # Log after receiving the chunk from the API
                if log_chunks:
                    with open(os.path.join(log_dir, f"log_chunk_{chunk_index + 1}_received.txt"), "w", encoding="utf-8") as log_file:
                        log_file.write(
                            f"Chunk {chunk_index + 1} received from API:\n{translated_text}\n\n"
                        )

                # Remove sub-IDs before further processing
                if enable_sub_ids:
                    translated_phrases = [
                        phrase.split(" ", 1)[-1] for phrase in translated_phrases
                    ]

                # Check if the number of sub-IDs (or lines if sub-IDs are disabled) match
                if enable_sub_ids:
                    original_sub_ids = [i for i, _ in enumerate(chunk)]
                    translated_sub_ids = [i for i in range(len(translated_phrases))]
                    if original_sub_ids != translated_sub_ids:
                        aligned_phrases = [None] * len(chunk)
                        for i, (unique_id, _) in enumerate(chunk):
                            if i < len(translated_phrases):
                                aligned_phrases[i] = translated_phrases[i]
                            else:
                                aligned_phrases[i] = f"[MISSING]"
                        if not ignore_mismatch:
                            raise ValueError(
                                f"Error: Mismatch in the number of sub-IDs sent and received "
                                f"for chunk {chunk_index + 1}. "
                                f"Sent {len(chunk)} sub-IDs, received {len(translated_phrases)} sub-IDs."
                            )
                    else:
                        aligned_phrases = translated_phrases
                else:
                    if len(translated_phrases) != len(
