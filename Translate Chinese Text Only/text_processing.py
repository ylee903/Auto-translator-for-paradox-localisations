import re

def extract_chinese_phrases(text, text_holder_path):
    """Extracts Chinese text phrases within quotation marks from the input string and stores them in a text holder."""
    chinese_phrases = re.findall(r'"([\u4e00-\u9fff]+[^"]*)"', text)
    print(f"\nExtracted Chinese Text Phrases:\n{chinese_phrases}")

    with open(text_holder_path, 'a', encoding='utf-8') as holder:
        for i, phrase in enumerate(chinese_phrases):
            unique_id = f"UNIQUE_ID_{i:08d}"
            holder.write(f"{unique_id}: {phrase}\n")
            text = text.replace(f'"{phrase}"', f'"{unique_id}"')
    
    return text
