"""Shared text tokenization and phrase-matching helpers."""

import re

_TOKEN_RE = re.compile(r"[a-z0-9#+]+")


def tokenize(text: str | None) -> list[str]:
    """Lowercase and split text into alphanumeric tokens (word-boundary safe)."""
    if not text:
        return []
    return _TOKEN_RE.findall(text.lower())


def contains_phrase(text: str | None, phrase: str) -> bool:
    """Return True if the phrase's tokens appear contiguously in the text."""
    phrase_tokens = tokenize(phrase)
    if not phrase_tokens:
        return False

    tokens = tokenize(text)
    n = len(phrase_tokens)
    return any(tokens[i : i + n] == phrase_tokens for i in range(len(tokens) - n + 1))


def matches_any(text: str | None, phrases: list[str]) -> bool:
    """Return True if any phrase appears in the text."""
    return any(contains_phrase(text, phrase) for phrase in phrases)
