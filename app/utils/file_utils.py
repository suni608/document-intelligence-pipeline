import os
import json
from typing import Any

def save_json(data: Any, path: str) -> None:
    """
    Saves serializable Python structures to a local JSON file.
    Creates parent directories dynamically if they do not exist.
    
    Args:
        data (Any): A JSON-serializable object (dict, list, etc.).
        path (str): File system destination path.
    """
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def save_markdown(content: str, path: str) -> None:
    """
    Writes content string to a local text file.
    Creates parent directories dynamically if they do not exist.
    
    Args:
        content (str): Plain text or Markdown block content.
        path (str): File system destination path.
    """
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
