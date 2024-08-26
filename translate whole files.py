from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('keys.env')

# Set your OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def split_text(text, max_tokens=4000):
    """Splits the text into smaller chunks that fit within the token limit, without cutting through code."""
    chunks = []
    current_chunk = []
    current_length = 0

    for line in text.splitlines(keepends=True):
        line_length = len(line)
        
        # Check if adding this line would exceed the token limit
        if current_length + line_length > max_tokens:
            # Only split if we're at a safe spot (end of a line, not in the middle of code)
            chunks.append("".join(current_chunk))
            current_chunk = []
            current_length = 0
        
        # Add the line to the current chunk
        current_chunk.append(line)
        current_length += line_length

    if current_chunk:
        chunks.append("".join(current_chunk))
    return chunks

def translate_text(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using GPT-4o mini
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional translator with expertise in translating video game localization files. "
                    "Your task is to translate only the Chinese text into English while preserving all other text, "
                    "including code, special characters, formatting, and structure. "
                    "Do not alter any non-Chinese text, numerical values, or special characters such as "
                    "[SCOPE.Custom('...')], and do not modify the structure of the file."
                    "We are translating a Chinese mod for the game Crusader Kings 3 into English."
                )
            },
            {"role": "user", "content": text},
        ]
    )
    return response.choices[0].message.content.strip()

def translate_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into smaller chunks
    chunks = split_text(content, max_tokens=4000)

    # Translate each chunk and combine the results
    translated_chunks = [translate_text(chunk) for chunk in chunks]
    translated_content = "".join(translated_chunks)

    # Overwrite the original file with the translated content
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(translated_content)

    print(f"Translation complete. Translated file saved as {file_path}")

def translate_all_yml_files_in_directory():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.yml'):
            file_path = os.path.join(current_directory, file_name)
            print(f"Translating file: {file_name}")
            translate_file(file_path)

# Example usage:
translate_all_yml_files_in_directory()
