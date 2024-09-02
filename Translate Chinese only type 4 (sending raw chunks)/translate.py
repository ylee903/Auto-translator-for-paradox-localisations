import openai
import re
import os
import glob
import tiktoken
import time
import asyncio
import aiohttp

from api_key_loader import debug_load_dotenv, debug_get_api_key


# Key parameters
delay_time = 1  # Delay between requests (in seconds)
log_chunks = True  # Log chunks sent/received for debugging
overwrite_original = True  # Overwrite original YAML files
max_concurrent_requests = 3  # Control concurrency of asynchronous requests
model_name = "gpt-4o-mini"  # Model for both tokenization and API calls
ignore_mismatch = (
    True  # Ignore mismatches in line counts between sent and received chunks
)

# Retry configuration
max_retries = 99999999  # Max retries for rate limit errors
initial_wait_time = 5  # Initial wait time before retrying (in seconds)

# Paths
file_path = r"./keys.env"
translation_directory = r"D:\Documents\Self help websites and data for games etc\paradox\ck3\Auto-translator-for-paradox-localisations\Translate Chinese only type 4 (sending raw chunks)\target translation"

# Load environment variables and API key
debug_load_dotenv(file_path)
api_key = debug_get_api_key()
openai.api_key = api_key

# Initialize tiktoken encoding based on the selected model
encoding = tiktoken.encoding_for_model(model_name)

# Regular expression for extracting Chinese text
chinese_text_regex = r'".*[\u4e00-\u9fff].*"'

# Define token and line limits
TOKEN_LIMIT = 3500  # Adjust if necessary for other models
LINE_LIMIT = 100  # Max lines or IDs in a chunk

# Mode selector: 'input' (pause until input received), 'pause' (waits for x seconds), or 'pause_on_input (pauses if input received within x time)' or 'normal'
mode = "input"


def chunk_yaml_file(file_content):
    lines = file_content.splitlines()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for line in lines:
        line_tokens = len(encoding.encode(line))

        # Check if adding this line would exceed token or line limits
        if (current_tokens + line_tokens > TOKEN_LIMIT) or (
            len(current_chunk) >= LINE_LIMIT
        ):
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_tokens = 0

        current_chunk.append(line)
        current_tokens += line_tokens

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    print(f"File split into {len(chunks)} chunks.")
    return chunks


async def translate_chunk_async(chunk, session, chunk_index, semaphore, log_dir):
    async with semaphore:
        print(f"Translating chunk {chunk_index + 1} asynchronously.")

        if log_chunks:
            with open(
                os.path.join(log_dir, f"log_chunk_{chunk_index + 1}_sent.txt"),
                "w",
                encoding="utf-8",
            ) as log_file:
                log_file.write(chunk)

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
                                    "You are given cut up localizations from a chinese CK3 mod localization file. This is beiong translated asynchrously. "
                                    "Translate only the Chinese text into English while preserving the identifiers and formatting. And do not add any other elements. "
                                ),
                            },
                            {"role": "user", "content": chunk},
                        ],
                    },
                    headers={"Authorization": f"Bearer {openai.api_key}"},
                )
                response.raise_for_status()
                response_json = await response.json()
                translated_text = response_json["choices"][0]["message"][
                    "content"
                ].strip()

                if log_chunks:
                    with open(
                        os.path.join(
                            log_dir, f"log_chunk_{chunk_index + 1}_received.txt"
                        ),
                        "w",
                        encoding="utf-8",
                    ) as log_file:
                        log_file.write(translated_text)

                return translated_text

            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Too Many Requests
                    print(
                        f"Rate limit hit. Retrying chunk {chunk_index + 1} in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                    retries += 1
                    wait_time += 1
                else:
                    print(
                        f"An error occurred while translating chunk {chunk_index + 1}: {e}"
                    )
                    raise

        print(f"Max retries reached for chunk {chunk_index + 1}. Skipping this chunk.")
        return None


async def translate_chunks_async(chunks, log_dir):
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    async with aiohttp.ClientSession() as session:
        tasks = [
            translate_chunk_async(chunk, session, i, semaphore, log_dir)
            for i, chunk in enumerate(chunks)
        ]
        translated_chunks = await asyncio.gather(*tasks)
    translated_chunks = [chunk for chunk in translated_chunks if chunk is not None]
    print(f"Translation completed for {len(translated_chunks)} chunks.")
    return translated_chunks


def save_translated_chunks(translated_chunks, file_path):
    reassembled_file_path = file_path.replace(".yml", "_translated.yml")
    with open(reassembled_file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(translated_chunks))
    print(f"Translated file saved as {reassembled_file_path}")
    return reassembled_file_path


async def translate_yaml_file(file_path):
    print(f"Processing file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    # Split the file into chunks
    chunks = chunk_yaml_file(file_content)

    log_dir = os.path.join(
        os.path.dirname(file_path), os.path.basename(file_path).replace(".yml", "")
    )
    os.makedirs(log_dir, exist_ok=True)

    # Translate the chunks
    translated_chunks = await translate_chunks_async(chunks, log_dir)

    # Save the translated chunks to a file
    translated_file_path = save_translated_chunks(translated_chunks, file_path)

    # Pause for manual review if needed
    pause_for_input_or_time(mode, delay_time)

    return translated_file_path


async def translate_all_files_in_subdirectory():
    yaml_files = glob.glob(os.path.join(translation_directory, "*.yml"))

    print(f"Found {len(yaml_files)} files to translate.")
    tasks = [translate_yaml_file(yaml_file) for yaml_file in yaml_files]
    await asyncio.gather(*tasks)


# Run the translation on all YAML files in the specified subdirectory asynchronously
asyncio.run(translate_all_files_in_subdirectory())
