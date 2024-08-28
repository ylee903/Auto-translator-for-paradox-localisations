# file_operations.py
import os
from file_io import read_file, write_file


def process_file(file_path):
    """Example function for processing a file."""
    content = read_file(file_path)
    # Process the content as needed
    processed_content = content.upper()  # Example processing
    write_file(file_path, processed_content)


def iterate_directory(directory_path):
    """Iterates over all files in a directory and processes them."""
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            process_file(file_path)
