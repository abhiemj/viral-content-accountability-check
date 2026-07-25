#!/usr/bin/env python3
"""Query the Google Fact Check Tools API from the command line.

Used by the Accountability Check Claude skill. Self-contained: only needs
`requests` and the GOOGLE_FACTCHECK_API_KEY environment variable.

Usage:
    python factcheck.py --query "protest in india"
    python factcheck.py --query "gdp growth" --language en --max-age-days 365
    echo "claim text" | python factcheck.py --stdin

Outputs JSON to stdout so Claude can read and interpret the results.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import requests

SEARCH_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


def search(query: str, language: str, page_size: int, max_age_days: int | None) -> dict:
    key = os.environ.get("GOOGLE_FACTCHECK_API_KEY", "").strip()
    if not key:
        return {"error": "Missing GOOGLE_FACTCHECK_API_KEY environment variable."}
    params = {
        "query": query,
        "key": key,
        "languageCode": language,
        "pageSize": page_size,
    }
    if max_age_days:
        params["maxAgeDays"] = max_age_days
    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=20)
    except requests.RequestException as exc:
        return {"error": f"Network error: {exc}"}
    if resp.status_code != 200:
        return {"error": f"API {resp.status_code}: {resp.text[:300]}"}
    return resp.json()


def normalize(raw: dict) -> list[dict]:
    out = []
    for claim in raw.get("claims", []) or []:
        for review in claim.get("claimReview") or [{}]:
            pub = review.get("publisher") or {}
            out.append(
                {
                    "text": claim.get("text", ""),
                    "claimant": claim.get("claimant", ""),
                    "claimDate": claim.get("claimDate", ""),
                    "publisher": pub.get("name", ""),
                    "publisherSite": pub.get("site", ""),
                    "url": review.get("url", ""),
                    "title": review.get("title", ""),
                    "reviewDate": review.get("reviewDate", ""),
                    "rating": review.get("textualRating", ""),
                    "languageCode": review.get("languageCode", ""),
                }
            )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Google Fact Check Tools API.")
    parser.add_argument("--query", help="Claim / keywords to search for.")
    parser.add_argument("--stdin", action="store_true", help="Read query from stdin.")
    parser.add_argument("--language", default="en", help="Language code (default: en).")
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--max-age-days", type=int, default=None)
    args = parser.parse_args()

    query = args.query
    if args.stdin:
        query = sys.stdin.read().strip()
    if not query:
        print(json.dumps({"error": "No query provided."}))
        return 1

    raw = search(query, args.language, args.page_size, args.max_age_days)
    if "error" in raw:
        print(json.dumps(raw))
        return 1

    results = normalize(raw)
    print(json.dumps({"query": query, "count": len(results), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
