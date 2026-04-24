from pathlib import Path


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