import time

import anthropic

from app.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def extract_structured_data(system_prompt, user_prompt):

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

            time.sleep(REQUEST_DELAY_SECONDS)

            return response.content[0].text

        except anthropic.APIError as exc:

            if exc.status_code in (429, 500, 502, 503, 529):

                wait_time = 5 * (attempt + 1)

                print(f"Anthropic API returned status {exc.status_code}. Waiting {wait_time} seconds and retrying (attempt {attempt + 1}/{MAX_RETRIES})...")

                time.sleep(wait_time)

            else:
                raise exc

    raise RuntimeError("Failed after retries.")