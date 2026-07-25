"""Heuristic check-worthy claim extraction.

This is a lightweight, dependency-free fallback used by the web app / API.
The Claude skill replaces this step with Claude's own judgement, which is
far better at spotting nuanced factual claims. Keep this simple.
"""

from __future__ import annotations

import re

# Small English stopword list for building search-friendly keyword queries.
STOPWORDS = set(
    """a an the and or but if then than that this these those of in on at to for from with
    without into onto over under again further is are was were be been being have has had do
    does did will would shall should can could may might must it its it's we you they he she
    him her them our your their my me i as by about not no yes so such very more most just
    also only own same too here there when where why how what which who whom""".split()
)

_HAS_NUMBER = re.compile(r"\d")
_SUPERLATIVES = (
    "highest", "lowest", "largest", "biggest", "smallest", "first", "last",
    "most", "least", "record", "never", "always", "every", "fastest", "worst",
    "best", "only", "double", "triple", "percent", "crore", "lakh", "billion",
    "million", "trillion",
)


def split_sentences(text: str) -> list[str]:
    """Naive sentence splitter that works well enough on transcript text."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def is_checkworthy(sentence: str) -> bool:
    """A sentence is check-worthy if it carries a number or a strong claim word."""
    lower = sentence.lower()
    if _HAS_NUMBER.search(sentence):
        return True
    return any(word in lower for word in _SUPERLATIVES)


def extract_claims(text: str, max_claims: int = 10) -> list[str]:
    """Return up to max_claims distinct check-worthy sentences from text."""
    seen: set[str] = set()
    claims: list[str] = []
    for sentence in split_sentences(text):
        if len(sentence.split()) < 4:
            continue
        if not is_checkworthy(sentence):
            continue
        key = sentence.lower()
        if key in seen:
            continue
        seen.add(key)
        claims.append(sentence)
        if len(claims) >= max_claims:
            break
    return claims


def to_keywords(sentence: str, limit: int = 8) -> str:
    """Turn a sentence into a compact keyword query for the Fact Check API."""
    words = re.findall(r"[A-Za-z0-9]+", sentence.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return " ".join(keywords[:limit]) or sentence.strip()
