
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "system_v1.txt"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


def load_system_prompt():
    """Load the versioned WeekendYatri system prompt."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_response(system_prompt, user_message):
    """Generate an AI response using Groq."""

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is missing from .env")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_completion_tokens=1000
    )

    return response.choices[0].message.content

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "system_v1.txt"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


def load_system_prompt():
    """Load the versioned WeekendYatri system prompt."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_response(system_prompt, user_message):
    """Generate an AI response using Groq."""

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is missing from .env")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_completion_tokens=1000
    )

    return response.choices[0].message.content
