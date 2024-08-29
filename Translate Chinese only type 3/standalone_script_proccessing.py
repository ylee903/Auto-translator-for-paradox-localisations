import os

# Define paths
file_path = r"D:\Documents\Self help websites and data for games etc\paradox\ck3\Auto-translator-for-paradox-localisations\Translate Chinese only type 3\to be translated2\oe_cultural_innovations_l_simp_chinese.yml"
reassembled_file_path = file_path.replace(".yml", "_chunks_reassembled.yml")
overwrite_original = (
    True  # Set this to False if you don't want to overwrite the original .yml
)


# Function to log warnings and track malformed lines
def process_reassembled_file(file_content):
    modified_chunks = {}
    with open(reassembled_file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line or ": " not in line:
                print(f"Warning: Skipping malformed line at {line_number}: {line}")
                continue
            try:
                uid, translation = line.split(": ", 1)
                modified_chunks[uid] = translation
            except ValueError:
                print(f"Warning: Failed to unpack line at {line_number}: {line}")
                continue
    return modified_chunks


# Function to reassemble the text with the modified chunks
def reassemble_text(file_content, modified_chunks):
    for unique_id, translation in modified_chunks.items():
        file_content = file_content.replace(f'"{unique_id}"', f'"{translation}"')
    print(f"Reassembled translated content.")
    return file_content


# Main process
def main():
    # Read the original .yml file content
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    # Process the reassembled chunks and get modified chunks
    modified_chunks = process_reassembled_file(file_content)

    # Reassemble the .yml content with the modified chunks
    translated_content = reassemble_text(file_content, modified_chunks)

    # Define the output file path
    output_file_path = (
        file_path if overwrite_original else file_path.replace(".yml", "_final.yml")
    )

    # Write the final translated content to the output file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(translated_content)

    print(f"Final translated file saved as {output_file_path}")


# Run the script
if __name__ == "__main__":
    main()
