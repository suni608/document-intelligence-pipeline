import re
import json

def clean_json_response(response_text):

    cleaned = re.sub(r"```json", "", response_text)
    cleaned = re.sub(r"```", "", cleaned)

    return cleaned.strip()