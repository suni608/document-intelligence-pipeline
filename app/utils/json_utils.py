import re

def clean_json_response(response_text: str) -> str:
    """
    Cleans raw markdown syntax wrappers (e.g. ```json ... ```) from LLM responses,
    returning a clean JSON string that can be deserialized.
    
    Args:
        response_text (str): Raw output string from LLM messages.
        
    Returns:
        str: Sanitized plain JSON string.
    """
    # Strip markdown block indicators if returned by the LLM
    cleaned = re.sub(r"```json", "", response_text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()
