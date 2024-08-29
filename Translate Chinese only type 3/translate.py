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
max_retries = 999  # Max retries for rate limit errors
initial_wait_time = 5  # Initial wait time before retrying (in seconds)

# Paths
file_path = r"./keys.env"
translation_directory = r"D:\Documents\Self help websites and data for games etc\paradox\ck3\Auto-translator-for-paradox-localisations\Translate Chinese only type 3\to be translated2"

# Load environment variables and API key
debug_load_dotenv(file_path)
api_key = debug_get_api_key()
openai.api_key = api_key

# Initialize tiktoken encoding based on the selected model
encoding = tiktoken.encoding_for_model(model_name)

# Regular expression for extracting Chinese text
chinese_text_regex = r'"([\u4e00-\u9fff]+[^"]*)"'

# Define token and line limits
TOKEN_LIMIT = 3500  # Adjust if necessary for other models
LINE_LIMIT = 100  # Max lines or IDs in a chunk
ID_FORMAT = "ID{:06d}"  # ID format: ID000000 to ID999999

# Mode selector: 'input', 'pause', or 'normal'
mode = "normal"  # Set to 'input', 'pause', or 'normal'


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
        if (
            current_tokens + phrase_tokens > TOKEN_LIMIT
            or len(current_chunk) >= LINE_LIMIT
        ):
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0
        current_chunk.append((unique_id, phrase))
        current_tokens += phrase_tokens

    if current_chunk:
        chunks.append(current_chunk)

    print(f"Split into {len(chunks)} chunks for translation.")
    return chunks


async def translate_chunk_async(chunk, session, chunk_index, semaphore, log_dir):
    async with semaphore:
        text_to_translate = "\n".join([f"{uid} {phrase}" for uid, phrase in chunk])
        print(
            f"Translating chunk {chunk_index + 1} with {len(chunk)} phrases asynchronously."
        )

        if log_chunks:
            with open(
                os.path.join(log_dir, f"log_chunk_{chunk_index + 1}_sent.txt"),
                "w",
                encoding="utf-8",
            ) as log_file:
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
                                    "Translate only the Chinese text into English while preserving the identifiers and formatting. "
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

                # Log received data immediately before processing
                if log_chunks:
                    with open(
                        os.path.join(
                            log_dir, f"log_chunk_{chunk_index + 1}_received.txt"
                        ),
                        "w",
                        encoding="utf-8",
                    ) as log_file:
                        log_file.write(
                            f"Chunk {chunk_index + 1} received from API:\n{translated_text}\n\n"
                        )

                translated_phrases = translated_text.split("\n")

                # Skip lines that don't split into two parts (ID and phrase)
                translated_map = {}
                for line in translated_phrases:
                    try:
                        uid, phrase = line.split(" ", 1)
                        translated_map[uid] = phrase
                    except ValueError:
                        if log_chunks:
                            with open(
                                os.path.join(
                                    log_dir, f"log_chunk_{chunk_index + 1}_skipped.txt"
                                ),
                                "a",
                                encoding="utf-8",
                            ) as log_file:
                                log_file.write(f"Skipped line: {line}\n")
                        continue

                return translated_map

            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Too Many Requests
                    print(
                        f"Rate limit hit. Retrying chunk {chunk_index + 1} in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                    retries += 1
                    wait_time *= 2  # Exponential backoff
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


def save_reassembled_chunks(translated_chunks, file_path):
    reassembled_file_path = file_path.replace(".yml", "_chunks_reassembled.yml")
    with open(reassembled_file_path, "w", encoding="utf-8") as file:
        for chunk in translated_chunks:
            for uid, translation in chunk.items():
                file.write(f"{uid}: {translation}\n")
    print(f"Reassembled chunks saved to {reassembled_file_path}")
    return reassembled_file_path


def reassemble_text(file_content, translated_chunks):
    for chunk in translated_chunks:
        for unique_id, translation in chunk.items():
            file_content = file_content.replace(f'"{unique_id}"', f'"{translation}"')
    print(f"Reassembled translated content.")
    return file_content


def pause_for_input_or_time():
    if mode == "input":
        input("Press Enter to continue...")
    elif mode == "pause":
        time.sleep(delay_time)
    elif mode == "pause_on_input":
        try:
            print(
                f"Pausing for {delay_time} seconds... Press Enter to resume immediately."
            )
            time.sleep(delay_time)
        except KeyboardInterrupt:
            input("Paused. Press Enter to resume...")


async def translate_yaml_file(file_path):
    print(f"Processing file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    phrases = extract_chinese_phrases(file_content)
    file_content, id_map = replace_with_ids(file_content, phrases)
    chunks = split_into_chunks(id_map)

    log_dir = os.path.join(
        os.path.dirname(file_path), os.path.basename(file_path).replace(".yml", "")
    )
    os.makedirs(log_dir, exist_ok=True)

    translated_chunks = await translate_chunks_async(chunks, log_dir)

    # Save reassembled chunks to file and pause for manual review
    reassembled_file_path = save_reassembled_chunks(translated_chunks, file_path)
    pause_for_input_or_time()

    # Re-read the reassembled chunks after modification
    modified_chunks = {}
    with open(reassembled_file_path, "r", encoding="utf-8") as file:
        for line in file:
            uid, translation = line.strip().split(": ", 1)
            modified_chunks[uid] = translation

    # Reassemble the text with the modified chunks
    translated_content = reassemble_text(file_content, [modified_chunks])

    output_file_path = (
        file_path if overwrite_original else file_path.replace(".yml", "_final.yml")
    )

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(translated_content)

    print(f"Final translated file saved as {output_file_path}")

    return output_file_path


async def translate_all_files_in_subdirectory():
    yaml_files = glob.glob(os.path.join(translation_directory, "*.yml"))

    print(f"Found {len(yaml_files)} files to translate.")
    tasks = [translate_yaml_file(yaml_file) for yaml_file in yaml_files]
    await asyncio.gather(*tasks)


# Run the translation on all YAML files in the specified subdirectory asynchronously
asyncio.run(translate_all_files_in_subdirectory())
