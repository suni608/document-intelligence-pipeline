import time
import anthropic
from app.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS
)
from app.verification.verification_prompt import VERIFICATION_PROMPT
from app.logger import logger

# Initialize the Anthropic Client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def verify_extraction(source_text: str, extracted_output: str) -> str:
    """
    Validates the accuracy, completeness, and lack of hallucinations in the extracted output
    by comparing it directly back against the source document using an LLM-based rubric auditor.
    
    Args:
        source_text (str): The original document chunk or full text.
        extracted_output (str): The JSON extraction output representation.
        
    Returns:
        str: Raw JSON representation of the verification results containing accuracy score out of 100.
        
    Raises:
        RuntimeError: If all retries fail.
    """
    # Create cache-busting prompt wrapper
    user_prompt = f"""
Cache-Buster-ID: {time.time()}

SOURCE DOCUMENT:
{source_text}

EXTRACTED OUTPUT:
{extracted_output}
"""
    logger.info("Executing self-verification auditor model run...")
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                system=VERIFICATION_PROMPT,
                max_tokens=2000,
                temperature=0,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            time.sleep(REQUEST_DELAY_SECONDS)
            return response.content[0].text

        except anthropic.APIError as exc:
            # Handle rate limits or service disruptions gracefully with retry policies
            if exc.status_code in (429, 500, 502, 503, 529):
                wait_time = 5 * (attempt + 1)
                logger.warning(
                    f"Anthropic API returned status {exc.status_code}. "
                    f"Waiting {wait_time}s and retrying (attempt {attempt + 1}/{MAX_RETRIES})..."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Fatal Anthropic API error during verification: {exc}")
                raise exc

    raise RuntimeError("Verification failed after exhausting maximum retries.")
