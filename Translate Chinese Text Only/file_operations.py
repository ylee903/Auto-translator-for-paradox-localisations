import os
from initialize_text_holder import initialize_text_holder
from text_processing import extract_chinese_phrases
from api_calls import translate_chinese_phrases
from file_operations import replace_identifiers_with_translations, translate_file, translate_all_yml_files_in_directory

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

def translate_file(file_path, client):
    # Step 1: Initialize the text holder
    text_holder_path = initialize_text_holder(file_path)

    # Step 2: Read the original YAML content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    print(f"\nProcessing File: {file_path}")

    # Step 3: Extract Chinese phrases and replace them with unique identifiers
    content_with_placeholders = extract_chinese_phrases(content, text_holder_path)

    # Step 4: Translate the extracted Chinese phrases
    translated_holder_path = translate_chinese_phrases(text_holder_path, client)

    # Step 5: Replace placeholders with translated phrases
    final_translated_content = replace_identifiers_with_translations(content_with_placeholders, translated_holder_path)

    # Step 6: Save the final translated content back to the original file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(final_translated_content)

    print(f"Translation complete. Translated file saved as {file_path}")

def translate_all_yml_files_in_directory(client):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.yml'):
            file_path = os.path.join(current_directory, file_name)
            print(f"\nTranslating file: {file_name}")
            translate_file(file_path, client)
            print("\nWaiting a few seconds before moving to the next file...\n")
