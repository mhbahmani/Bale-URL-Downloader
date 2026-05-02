from pathlib import Path
from urllib.parse import unquote

import requests
import shutil
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def save_to_file(filename: str, content: str):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def load_file_content(filename: str) -> str:
    full_path = PROJECT_ROOT / filename
    if not full_path.exists():
        return None
    with open(full_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    return file_content

def download_file(url, path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
            print("Download complete!")
        else:
            print("Failed to download the file.")
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")

def compress_directory_to_zip(directory: str) -> str:
    shutil.make_archive(directory, 'zip', directory)
    return directory.rstrip("/") + ".zip"

def sanitize_url(url):
    return unquote(url)
