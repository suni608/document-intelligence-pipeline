import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC API KEY") or os.getenv("ANTHROPIC_API_KEY")

# Options: "claude-3-5-haiku-20241022" (cheaper/faster) or "claude-3-5-sonnet-20241022"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

MAX_RETRIES = 5

REQUEST_DELAY_SECONDS = 5