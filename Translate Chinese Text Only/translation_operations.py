from text_processing import extract_chinese_phrases
from api_calls import translate_chinese_phrases
from file_operations import replace_identifiers_with_translations


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
