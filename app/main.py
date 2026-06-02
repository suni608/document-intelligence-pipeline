import json
import sys
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


# Default NIST AI RAG standard specification PDF as sample ingestion target
PDF_URL = "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
PDF_PATH = "sample_data/sample.pdf"


def main() -> None:
    """
    Main orchestrator execution workflow. Executes 5 sequential stages:
      Stage 1: Fetch - Downloads raw target PDF.
      Stage 2: Ingest/Parse - Converts PDF pages to plaintext stream.
      Stage 3: Structure - Sends text to LLM (Claude) and validates structure using Pydantic.
      Stage 4: Publish - Translates data structure into formatted Markdown article.
      Stage 5: Verify - Performs accuracy verification grading using LLM auditor.
    """
    logger.info("=== STARTING DOCUMENT INTELLIGENCE PIPELINE RUN ===")
    start_time = time.time()
    
    try:
        # --- STAGE 01: FETCH ---
        logger.info("[STAGE 01] Fetching target source document PDF...")
        download_pdf(PDF_URL, PDF_PATH)

        # --- STAGE 02: PARSE ---
        logger.info("[STAGE 02] Extracting text content from local PDF file...")
        raw_text = extract_text(PDF_PATH)
        if not raw_text.strip():
            raise ValueError(f"Extracted document text is empty. Ingestion failed for path: {PDF_PATH}")

        # --- STAGE 03: STRUCTURE & SCHEMA VALIDATION ---
        logger.info("[STAGE 03] Segmenting document text and applying structured schema extraction...")
        chunks = chunk_text(raw_text)
        
        extracted_results = []
        # In happy-path MVP scope: Process the primary chunk (chunk 0) representing the core document info
        for index, chunk in enumerate(chunks[:1]):
            logger.info(f"Processing text chunk index {index} ({len(chunk)} characters)...")
            prompt = build_prompt(chunk)
            
            # API extraction
            raw_response = extract_structured_data(SYSTEM_PROMPT, prompt)
            
            # Sanitization of markdown formatting wrappers from output
            cleaned_json = clean_json_response(raw_response)
            parsed_data = json.loads(cleaned_json)
            
            # Schema validation using Pydantic BaseModel
            validated_doc = ExtractedDocument(**parsed_data)
            extracted_results.append(validated_doc.dict())
            
        final_extracted_data = extracted_results[0]
        
        # Save validated JSON to workspace
        save_json(final_extracted_data, "outputs/extracted.json")
        logger.info("Structured JSON saved successfully to outputs/extracted.json")

        # --- STAGE 04: PUBLISH ---
        logger.info("[STAGE 04] Translating structured JSON to publication Markdown target...")
        markdown_content = generate_markdown(ExtractedDocument(**final_extracted_data))
        save_markdown(markdown_content, "outputs/result.md")
        logger.info("Markdown publication draft saved to outputs/result.md")

        # --- STAGE 05: VERIFY ---
        logger.info("[STAGE 05] Initiating self-verification rubric auditor stage...")
        # Compare first 4000 characters of source text against the extracted output JSON
        verification_response = verify_extraction(
            raw_text[:4000],
            json.dumps(final_extracted_data)
        )
        cleaned_verification = clean_json_response(verification_response)
        save_markdown(cleaned_verification, "outputs/verification.json")
        logger.info("Self-verification details saved to outputs/verification.json")

        total_duration = time.time() - start_time
        logger.info(f"=== PIPELINE RUN COMPLETED SUCCESSFULY IN {total_duration:.2f} SECONDS ===")

    except Exception as e:
        logger.critical(f"Pipeline crashed during execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
