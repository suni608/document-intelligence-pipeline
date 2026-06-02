import os
import json

def save_json(data, path):

    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def save_markdown(content, path):

    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)