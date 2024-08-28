# initialize_text_Holder.py

import os


def initialize_text_holder(file_path):
    """Initializes an empty text holder file."""
    with open(file_path, "w", encoding="utf-8") as file:
        pass


def initialize_translated_text_holder(file_path):
    """Initializes an empty translated text holder file."""
    with open(file_path, "w", encoding="utf-8") as file:
        pass
