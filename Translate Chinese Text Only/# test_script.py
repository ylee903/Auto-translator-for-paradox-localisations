# test_script.py

import os
from translation_operations import process_translation
from initialize_text_holder import (
    initialize_text_holder,
    initialize_translated_text_holder,
)


def test_translation():
    test_file_path = "TESTING.yml"
    text_holder_path = test_file_path + "_text_holder.txt"
    translated_text_holder_path = test_file_path + "_translated_text_holder.txt"

    initialize_text_holder(text_holder_path)
    initialize_translated_text_holder(translated_text_holder_path)

    print(f"Initialized text holder file: {text_holder_path}")
    print(f"Initialized translated text holder file: {translated_text_holder_path}")

    # Mock process_translation call
    print(f"Processing translation for {test_file_path}")
    process_translation(
        test_file_path, None, text_holder_path, translated_text_holder_path
    )
    print("Translation process complete.")


if __name__ == "__main__":
    test_translation()
