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
