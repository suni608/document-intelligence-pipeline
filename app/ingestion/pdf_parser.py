import fitz  # PyMuPDF
from app.logger import logger

def extract_text(pdf_path: str) -> str:
    """
    Parses a PDF document locally using PyMuPDF and extracts its full plain text content.
    
    Args:
        pdf_path (str): Absolute or relative file path to the PDF.
        
    Returns:
        str: All extracted plain text concatenated across all pages.
        
    Raises:
        FileNotFoundError: If the PDF path does not exist.
        fitz.FileDataError: If PyMuPDF fails to parse the document format.
    """
    logger.info(f"Opening PDF document for text extraction: {pdf_path}")
    try:
        document = fitz.open(pdf_path)
        text = ""
        
        for page_num, page in enumerate(document, start=1):
            page_text = page.get_text()
            text += page_text
            
        logger.info(f"Text extraction completed. Total parsed pages: {len(document)}. Extracted {len(text)} characters.")
        return text
    except FileNotFoundError as e:
        logger.error(f"PDF file not found at path: {pdf_path}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred while parsing PDF {pdf_path}: {e}")
        raise e
