from pathlib import Path


def save_to_file(filename: str, content: str):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def load_file_content(filename: str) -> str:
    if Path(filename).exists():
        return None
    with open(filename, 'r', encoding='utf-8') as file:
        file_content = file.read()
    return file_content