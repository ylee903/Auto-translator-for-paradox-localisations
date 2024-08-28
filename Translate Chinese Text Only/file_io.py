# file_io.py
import os


def read_file(file_path):
    """Reads the content of a file and returns it."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_file(file_path, content):
    """Writes the given content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def append_to_file(file_path, content):
    """Appends the given content to a file."""
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content)


def create_directory(directory_path):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
