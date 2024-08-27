import os
from initialize_text_holder import initialize_text_holder
from text_processing import extract_chinese_phrases
from api_calls import translate_chinese_phrases


def load_translation_map(translated_holder_path):
    """Loads the translation map from the translated holder file."""
    translation_map = {}
    with open(translated_holder_path, "r", encoding="utf-8") as translated_holder:
        translated_lines = translated_holder.read().strip().split("\n")
        for line in translated_lines:
            if ": " in line:
                unique_id, translated_phrase = line.split(": ", 1)
                translation_map[unique_id.strip()] = translated_phrase.strip()
    return translation_map


def apply_translations(text, translation_map):
    """Applies the translations from the translation map to the original text."""
    for unique_id, translated_phrase in translation_map.items():
        text = text.replace(unique_id, translated_phrase)
    return text


def replace_identifiers_with_translations(text, translated_holder_path):
    """Replaces unique identifiers in the original text with their corresponding translated phrases."""
    translation_map = load_translation_map(translated_holder_path)
    return apply_translations(text, translation_map)


def translate_file(file_path, client):
    """Main function to handle the translation of a YAML file."""
    # Step 1: Initialize both the text holder for untranslated and translated text
    text_holder_path = initialize_text_holder(file_path)
    translated_holder_path = f"{text_holder_path}_translated.txt"  # Assuming you want the translated holder initialized as well
    with open(translated_holder_path, "w", encoding="utf-8") as file:
        file.write("")  # Start with an empty file

    # Step 2: Read the original YAML content
    content = read_yaml_content(file_path)

    # Step 3: Process the translation (extract, translate, replace)
    final_translated_content = process_translation(content, text_holder_path, client)

    # Step 4: Save the final translated content back to the original file
    save_translated_content(file_path, final_translated_content)

    print(f"Translation complete. Translated file saved as {file_path}")


# added functions
def read_yaml_content(file_path):
    """Reads the original YAML content from the file."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def process_translation(content, text_holder_path, client):
    """Handles the processing steps: extract, translate, and replace."""
    # Step 1: Extract Chinese phrases and replace them with unique identifiers
    content_with_placeholders = extract_chinese_phrases(content, text_holder_path)

    # Step 2: Translate the extracted Chinese phrases
    translated_holder_path = translate_chinese_phrases(text_holder_path, client)

    # Step 3: Replace placeholders with translated phrases
    final_translated_content = replace_identifiers_with_translations(
        content_with_placeholders, translated_holder_path
    )

    return final_translated_content


def save_translated_content(file_path, final_translated_content):
    """Saves the final translated content back to the original file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(final_translated_content)
