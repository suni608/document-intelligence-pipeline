from typing import List

def chunk_text(text: str, chunk_size: int = 4000) -> List[str]:
    """
    Splits the extracted document text into sequential sub-strings (chunks) to respect LLM input context limits.
    
    Args:
        text (str): The raw input text extracted from the document.
        chunk_size (int): The maximum character length of each chunk. Defaults to 4000.
        
    Returns:
        List[str]: A list of text chunks.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks
