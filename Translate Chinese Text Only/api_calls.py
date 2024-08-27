from openai import OpenAI

def translate_chinese_phrases(text_holder_path, client):
    """Translates the Chinese text stored in the text holder file."""
    with open(text_holder_path, 'r', encoding='utf-8') as holder:
        content = holder.read().strip()

    print(f"\nSending the following text to the API for translation:\n{content}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust model as needed
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional translator with expertise in translating video game localization files. "
                    "You are given text extracted from .YML from a Crusader Kings 3 or even a mod for the game."
                    "Translate only the Chinese text into English while preserving the identifiers and formatting."
                )
            },
            {"role": "user", "content": content},
        ]
    )

    translated_content = response.choices[0].message.content.strip()

    print(f"\nReceived the following translated content:\n{translated_content}")

    translated_holder_path = f"{text_holder_path}_translated.txt"
    with open(translated_holder_path, 'w', encoding='utf-8') as translated_holder:
        translated_holder.write(translated_content)
    
    return translated_holder_path
