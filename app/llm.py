import hashlib
import logging
import os
import time
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

logger = logging.getLogger("weekendyatri.llm")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Load environment variables from the project root .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

PROMPTS_DIR = BASE_DIR / "prompts"
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY) if API_KEY else None

# Simple bounded LRU + TTL cache for LLM responses
CACHE_MAX_SIZE = 128
CACHE_TTL_SECONDS = 3600
_RESPONSE_CACHE: OrderedDict[str, tuple[float, str]] = OrderedDict()

METRICS = {
    "total_llm_calls": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_tokens": 0,
    "last_latency_ms": 0.0,
}


def clear_cache() -> None:
    """Clear the in-memory LLM response cache."""
    _RESPONSE_CACHE.clear()


def _cache_key(system_prompt: str, user_message: str) -> str:
    digest = hashlib.sha256(
        f"{MODEL_NAME}::{system_prompt}::{user_message}".encode("utf-8")
    ).hexdigest()
    return digest


def load_system_prompt(version="v2"):
    """Load the selected version of the WeekendYatri system prompt."""
    if version not in {"v1", "v2"}:
        raise ValueError("Invalid prompt version. Choose v1 or v2.")

    prompt_path = PROMPTS_DIR / f"system_{version}.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def generate_response(system_prompt, user_message, use_cache: bool = True):
    """Generate an AI response using Groq with caching, latency, and token logging."""
    start = time.perf_counter()
    key = _cache_key(system_prompt, user_message)

    if use_cache and key in _RESPONSE_CACHE:
        cached_at, cached_text = _RESPONSE_CACHE[key]
        if (time.time() - cached_at) < CACHE_TTL_SECONDS:
            _RESPONSE_CACHE.move_to_end(key)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            METRICS["cache_hits"] += 1
            METRICS["last_latency_ms"] = latency_ms
            logger.info(
                "llm_call cache_hit=True model=%s latency_ms=%.2f prompt_tokens=0 completion_tokens=0 total_tokens=0",
                MODEL_NAME,
                latency_ms,
            )
            return cached_text
        del _RESPONSE_CACHE[key]

    if not API_KEY or client is None:
        raise ValueError("GROQ_API_KEY is missing from the .env file.")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_completion_tokens=1000,
    )

    content = response.choices[0].message.content
    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    total_tokens = getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or 0

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    METRICS["total_llm_calls"] += 1
    METRICS["cache_misses"] += 1
    METRICS["total_prompt_tokens"] += prompt_tokens
    METRICS["total_completion_tokens"] += completion_tokens
    METRICS["total_tokens"] += total_tokens
    METRICS["last_latency_ms"] = latency_ms

    logger.info(
        "llm_call cache_hit=False model=%s latency_ms=%.2f prompt_tokens=%d completion_tokens=%d total_tokens=%d",
        MODEL_NAME,
        latency_ms,
        prompt_tokens,
        completion_tokens,
        total_tokens,
    )

    if use_cache and content:
        _RESPONSE_CACHE[key] = (time.time(), content)
        if len(_RESPONSE_CACHE) > CACHE_MAX_SIZE:
            _RESPONSE_CACHE.popitem(last=False)

    return content
