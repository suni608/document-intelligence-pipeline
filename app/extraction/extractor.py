import time
import anthropic
from app.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS
)
from app.logger import logger

# Initialize the Anthropic Client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def extract_structured_data(system_prompt: str, user_prompt: str) -> str:
    """
    Calls the Anthropic Messages API to extract structured JSON data from a text chunk.
    Implements error handling and exponential backoff retry logic for transient API issues (429, 5xx).
    
    Args:
        system_prompt (str): Instructions defining the persona, schema, and extraction guidelines.
        user_prompt (str): The actual text chunk packaged inside structural tags.
        
    Returns:
        str: Raw JSON string returned from Claude.
        
    Raises:
        anthropic.APIError: Non-transient API failure or persistent errors.
        RuntimeError: If all retry attempts are exhausted.
    """
    logger.info(f"Extracting structured data using model: {CLAUDE_MODEL}")
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                system=system_prompt,
                max_tokens=4000,
                temperature=0,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            # Add static request delay to protect against immediate rate limit penalties
            time.sleep(REQUEST_DELAY_SECONDS)
            return response.content[0].text

        except anthropic.APIError as exc:
            # Check for transient codes (Rate Limit 429, or server errors 500, 502, 503, 529)
            if exc.status_code in (429, 500, 502, 503, 529):
                wait_time = 5 * (attempt + 1)
                logger.warning(
                    f"Anthropic API returned status {exc.status_code}. "
                    f"Waiting {wait_time}s and retrying (attempt {attempt + 1}/{MAX_RETRIES})..."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Fatal Anthropic API error (non-retryable): {exc}")
                raise exc

    raise RuntimeError("Structured data extraction failed after exhausting maximum retries.")
