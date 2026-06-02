import requests
from app.logger import logger

def download_pdf(url: str, output_path: str) -> str:
    """
    Downloads a public PDF from a URL and saves it to a specified local path.
    
    Args:
        url (str): The public URL of the PDF to fetch.
        output_path (str): The local path where the PDF should be written.
        
    Returns:
        str: The path to the downloaded PDF file if successful.
        
    Raises:
        requests.RequestException: If the HTTP request fails or status code is not 200.
    """
    logger.info(f"Initiating download from URL: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, "wb") as file:
            file.write(response.content)
            
        logger.info(f"Successfully downloaded PDF and saved to: {output_path}")
        return output_path
    except requests.RequestException as e:
        logger.error(f"Failed to download PDF from {url}. Error: {e}")
        raise e
