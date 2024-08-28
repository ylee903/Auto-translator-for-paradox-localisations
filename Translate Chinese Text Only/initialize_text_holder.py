def initialize_untranslated_text_holder(file_path):
    text_holder_path = f"{file_path}_text_holder.txt"
    with open(text_holder_path, "w", encoding="utf-8") as file:
        file.write("")  # Start with an empty file
    print(f"Initialized text holder file: {text_holder_path}")
    return text_holder_path


# initialise text holder for translated text
def initialize_translated_holder(file_path):
    translated_holder_path = f"{file_path}_translated.txt"
    with open(translated_holder_path, "w", encoding="utf-8") as file:
        file.write("")  # Start with an empty file
    print(f"Initialized translated holder file: {translated_holder_path}")
    return translated_holder_path
