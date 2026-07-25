"""Thin client for the Google Fact Check Tools API (claims:search).

Docs: https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search
This is the same data source that powers the public Fact Check Explorer.
"""

from __future__ import annotations

import requests

from .config import GOOGLE_FACTCHECK_API_KEY

SEARCH_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


class FactCheckError(Exception):
    """Raised when the Fact Check API call fails or is misconfigured."""


def search_claims(
    query: str,
    language_code: str = "en",
    page_size: int = 10,
    max_age_days: int | None = None,
    api_key: str | None = None,
) -> dict:
    """Query Google's repository of published fact-checks.

    Returns the raw JSON response. Raises FactCheckError on failure.
    """
    key = (api_key or GOOGLE_FACTCHECK_API_KEY).strip()
    if not key:
        raise FactCheckError(
            "Missing Google Fact Check API key. "
            "Set GOOGLE_FACTCHECK_API_KEY in your .env file."
        )
    if not query or not query.strip():
        raise FactCheckError("Query must not be empty.")

    params = {
        "query": query.strip(),
        "key": key,
        "languageCode": language_code,
        "pageSize": page_size,
    }
    if max_age_days:
        params["maxAgeDays"] = max_age_days

    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=20)
    except requests.RequestException as exc:  # network-level failure
        raise FactCheckError(f"Network error contacting Fact Check API: {exc}") from exc

    if resp.status_code != 200:
        raise FactCheckError(
            f"Fact Check API returned {resp.status_code}: {resp.text[:300]}"
        )

    return resp.json()


def normalize_claims(raw: dict) -> list[dict]:
    """Flatten the API response into a simple list of review records.

    Each published fact-check may carry multiple reviews; we emit one row
    per review so the frontend can render them as individual cards.
    """
    results: list[dict] = []
    for claim in raw.get("claims", []) or []:
        reviews = claim.get("claimReview") or [{}]
        for review in reviews:
            publisher = review.get("publisher") or {}
            results.append(
                {
                    "text": claim.get("text", ""),
                    "claimant": claim.get("claimant", ""),
                    "claimDate": claim.get("claimDate", ""),
                    "publisher": publisher.get("name", ""),
                    "publisherSite": publisher.get("site", ""),
                    "url": review.get("url", ""),
                    "title": review.get("title", ""),
                    "reviewDate": review.get("reviewDate", ""),
                    "rating": review.get("textualRating", ""),
                    "languageCode": review.get("languageCode", ""),
                }
            )
    return results


def summarize(results: list[dict]) -> str:
    """Derive a coarse overall signal from a set of review ratings.

    Intentionally conservative: defaults to 'unverified' when no published
    fact-check exists, rather than asserting a verdict of its own.
    """
    if not results:
        return "unverified"

    ratings = " ".join((r.get("rating") or "").lower() for r in results)
    false_markers = ("false", "misleading", "incorrect", "fake", "no evidence", "pants on fire")
    true_markers = ("true", "correct", "accurate", "mostly true")

    has_false = any(m in ratings for m in false_markers)
    has_true = any(m in ratings for m in true_markers)

    if has_false and not has_true:
        return "disputed"
    if has_true and not has_false:
        return "supported"
    if has_false and has_true:
        return "mixed"
    return "reviewed"
