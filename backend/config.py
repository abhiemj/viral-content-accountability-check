"""Configuration loaded from environment / .env file."""

import os

from dotenv import load_dotenv

load_dotenv()

# Google Fact Check Tools API key (the same backend that powers the
# Fact Check Explorer: https://toolbox.google.com/factcheck/explorer ).
GOOGLE_FACTCHECK_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY", "").strip()

# Default language code for queries (ISO 639-1, e.g. "en", "hi").
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en").strip() or "en"

# Maximum number of claims to auto-extract from a video transcript.
try:
    MAX_CLAIMS = int(os.getenv("MAX_CLAIMS", "10"))
except ValueError:
    MAX_CLAIMS = 10
