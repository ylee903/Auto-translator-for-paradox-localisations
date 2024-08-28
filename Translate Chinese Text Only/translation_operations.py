# translation_operations.py
from file_io import read_file, write_file
from text_processing import extract_chinese_phrases
from api_calls import translate_text


def process_translation(
    file_path, client, text_holder_path, translated_text_holder_path
):
    try:
        # Read the file content
        content = read_file(file_path)

        # Extract Chinese phrases and replace with unique IDs
        content, unique_id_map = extract_chinese_phrases(content, text_holder_path)

        # Write the modified content back to the file
        write_file(file_path, content)

        # Read the untranslated text from the text holder
        untranslated_text = read_file(text_holder_path)

        # Translate the entire text holder content
        translated_text = translate_text(client, untranslated_text)

        # Write the translated text to the translated text holder
        write_file(translated_text_holder_path, translated_text)

    except Exception as e:
        print(f"Error in translating {file_path}: {str(e)}")
