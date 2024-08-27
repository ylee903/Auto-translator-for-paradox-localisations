def read_yaml_content(file_path):
    """Reads the original YAML content from the file."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def save_translated_content(file_path, final_translated_content):
    """Saves the final translated content back to the original file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(final_translated_content)
