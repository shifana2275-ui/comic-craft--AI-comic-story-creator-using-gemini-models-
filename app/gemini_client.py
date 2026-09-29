"""
Shared Gemini API client.

Requires the GEMINI_API_KEY environment variable (loaded from a .env file
by app/main.py via python-dotenv). Get a key at https://aistudio.google.com/apikey
"""
import os
from google import genai

_client = None


def get_client() -> "genai.Client":
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to a .env file in the project "
                "root or export it as an environment variable."
            )
        _client = genai.Client(api_key=api_key)
    return _client
