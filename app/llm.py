
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# Load environment variables from the project root .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Prompt directory
PROMPTS_DIR = BASE_DIR / "prompts"


# Groq configuration
MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY) if API_KEY else None


def load_system_prompt(version="v2"):
    """Load the selected version of the WeekendYatri system prompt."""

    if version not in {"v1", "v2"}:
        raise ValueError(
            "Invalid prompt version. Choose v1 or v2."
        )

    prompt_path = PROMPTS_DIR / f"system_{version}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}"
        )

    return prompt_path.read_text(encoding="utf-8")


def generate_response(system_prompt, user_message):
    """Generate an AI response using the Groq API."""

    if not API_KEY or client is None:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.3,
        max_completion_tokens=1000
    )

    return response.choices[0].message.content
