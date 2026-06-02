import json
import time
from app.utils.json_utils import clean_json_response
from app.logger import logger

from app.ingestion.pdf_fetcher import download_pdf
from app.ingestion.pdf_parser import extract_text

from app.extraction.chunking import chunk_text
from app.extraction.prompts import SYSTEM_PROMPT, build_prompt
from app.extraction.extractor import extract_structured_data
from app.extraction.schema import ExtractedDocument

from app.publishing.markdown_publisher import generate_markdown

from app.verification.verifier import verify_extraction

from app.utils.file_utils import save_json, save_markdown


PDF_URL = "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"

PDF_PATH = "sample_data/sample.pdf"


def main():

    logger.info("Downloading PDF...")

    download_pdf(PDF_URL, PDF_PATH)

    logger.info("Extracting text...")

    text = extract_text(PDF_PATH)

    logger.info("Chunking text...")

    chunks = chunk_text(text)

    extracted_results = []

    for chunk in chunks[:1]:

        prompt = build_prompt(chunk)

        response = extract_structured_data(
            SYSTEM_PROMPT,
            prompt
        )
        time.sleep(15)
        # parsed = json.loads(response)
        cleaned_response = clean_json_response(response)
        parsed = json.loads(cleaned_response)

        validated = ExtractedDocument(**parsed)

        extracted_results.append(validated.dict())

    final_output = extracted_results[0]

    logger.info("Saving extracted JSON...")

    save_json(
        final_output,
        "outputs/extracted.json"
    )

    logger.info("Generating markdown...")

    markdown = generate_markdown(
        ExtractedDocument(**final_output)
    )

    save_markdown(
        markdown,
        "outputs/result.md"
    )

    logger.info("Running verification...")

    verification = verify_extraction(
        text[:4000],
        json.dumps(final_output)
    )

    cleaned_verification = clean_json_response(verification)

    save_markdown(
        cleaned_verification,
        "outputs/verification.json"
    )

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()