import openai
import re
import os

# Set your OpenAI API key
openai.api_key = 'your-api-key-here'

def extract_chinese(text):
    """Extracts Chinese text from the input string."""
    chinese_blocks = re.findall(r'[\u4e00-\u9fff]+', text)
    return chinese_blocks

def replace_chinese(text, translations):
    """Replaces Chinese text in the original string with translated text."""
    def replace_match(match):
        nonlocal translations
        return translations.pop(0) if translations else match.group(0)

    translated_text = re.sub(r'[\u4e00-\u9fff]+', replace_match, text)
    return translated_text

def translate_text(chinese_blocks):
    translated_blocks = []
    for block in chinese_blocks:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Adjust model as needed
            messages=[
                {
                    "role": "system",
                    "content": (
                    "You are a professional translator with expertise in translating video game localization files. "
                    "Your task is to translate only the Chinese text into English while preserving all other text, "
                    "including code, special characters, formatting, and structure. "
                    "Do not alter any non-Chinese text, numerical values, or special characters such as "
                    "[SCOPE.Custom('...')], and do not modify the structure of the file."
                    "we are translating a Chinese mod for the game Crusader Kings 3 into english"
                    )
                },
                {"role": "user", "content": block},
            ]
        )
        translated_blocks.append(response['choices'][0]['message']['content'].strip())
    return translated_blocks

def translate_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract Chinese text blocks
    chinese_blocks = extract_chinese(content)

    # Translate the Chinese text blocks
    translations = translate_text(chinese_blocks)

    # Replace the original Chinese text with the translations
    translated_content = replace_chinese(content, translations)

    # Save the translated content back to the file
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
