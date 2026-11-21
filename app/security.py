import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"reveal\s+(your\s+)?(system\s+prompt|instructions|rules)",
    r"print\s+(your\s+)?(system\s+prompt|hidden\s+prompt)",
    r"you\s+are\s+now\s+(in\s+)?developer\s+mode",
    r"jailbreak",
    r"bypass\s+(safety|security|guardrails|rules)",
    r"act\s+as\s+an?\s+unrestricted",
]

_COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS
]


def detect_prompt_injection(text: str) -> str | None:
    """Return the matched injection rule if text contains an injection attempt."""
    if not text:
        return None

    for pattern in _COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0)

    return None


def validate_safe_input(text: str, max_chars: int = 1000) -> str:
    """Validate input length and block prompt-injection attempts."""
    cleaned = text.strip()
    if len(cleaned) > max_chars:
        raise ValueError(f"Input exceeds maximum length of {max_chars} characters.")

    matched = detect_prompt_injection(cleaned)
    if matched:
        raise ValueError(
            f"Blocked potential prompt-injection pattern: '{matched}'."
        )

    return cleaned
