import requests

def download_pdf(url: str, output_path: str):

    response = requests.get(url)

    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)

    return output_path