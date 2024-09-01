import os
import re


# Function to reassemble text from IDs and translations
def reassemble_text(file_content, translated_chunks):
    for chunk in translated_chunks:
        for unique_id, translation in chunk.items():
            file_content = file_content.replace(f"{unique_id}", f'"{translation}"', 1)
    print(f"Reassembled translated content.")
    return file_content


def reassemble_file(input_file_path, translated_file_path, output_file_path):
    # Load the original file content
    with open(input_file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    # Load the translated chunks
    translated_chunks = []
    with open(translated_file_path, "r", encoding="utf-8") as file:
        chunk = {}
        for line in file:
            line = line.strip()
            if not line or ": " not in line:
                continue
            try:
                uid, translation = line.split(": ", 1)
                chunk[uid] = translation
            except ValueError:
                print(f"Warning: Failed to unpack line: {line}")
                continue
        translated_chunks.append(chunk)

    # Reassemble the text with the translated chunks
    reassembled_content = reassemble_text(file_content, translated_chunks)

    # Save the reassembled content to the output file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(reassembled_content)

    print(f"Final reassembled file saved as {output_file_path}")


if __name__ == "__translate__":
    input_file = r"D:\path\to\your\original_file.yml"
    translated_file = r"D:\path\to\your\translated_chunks_file.yml"
    output_file = r"D:\path\to\your\final_reassembled_file.yml"

    reassemble_file(input_file, translated_file, output_file)
