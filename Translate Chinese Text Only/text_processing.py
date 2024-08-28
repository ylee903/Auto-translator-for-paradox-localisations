# text_processing.py
import re
from main import EXTRACTION_PATTERN
from error_handling import handle_error, CustomFileError


def extract_chinese_phrases(content, text_holder_path):
    try:
        # Find all Chinese text in the content
        chinese_phrases = re.findall(EXTRACTION_PATTERN, content)
        unique_id_map = {}

        with open(text_holder_path, "w", encoding="utf-8") as holder:
            for i, phrase in enumerate(chinese_phrases):
                unique_id = f"UNIQUE_ID_{i:08d}"
                unique_id_map[unique_id] = phrase
                content = content.replace(phrase, unique_id)
                holder.write(f"{unique_id}: {phrase}\n")

        return content, unique_id_map
    except Exception as e:
        handle_error(CustomFileError(f"Failed to extract Chinese phrases: {str(e)}"))
        raise
