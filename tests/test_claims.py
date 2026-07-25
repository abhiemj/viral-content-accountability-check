"""Unit tests for claim extraction and fact-check normalization (no network)."""

from backend import claims, factcheck


def test_checkworthy_detects_numbers():
    assert claims.is_checkworthy("GDP grew by 8 percent last year")
    assert claims.is_checkworthy("This is the highest ever recorded")
    assert not claims.is_checkworthy("We care deeply about the people")


def test_extract_claims_filters_and_dedupes():
    text = (
        "We will build a bright future. "
        "The government built 50000 km of roads in 2023. "
        "The government built 50000 km of roads in 2023. "
        "Unemployment is at a 40-year low."
    )
    result = claims.extract_claims(text, max_claims=10)
    assert "The government built 50000 km of roads in 2023." in result
    assert "We will build a bright future." not in result
    # duplicate collapsed
    assert len(result) == 2


def test_to_keywords_strips_stopwords():
    kw = claims.to_keywords("The government built roads in the country")
    assert "the" not in kw.split()
    assert "government" in kw.split()


def test_normalize_claims_flattens_reviews():
    raw = {
        "claims": [
            {
                "text": "Some claim",
                "claimant": "A politician",
                "claimReview": [
                    {
                        "publisher": {"name": "Alt News", "site": "altnews.in"},
                        "url": "https://altnews.in/x",
                        "title": "Old video shared as recent",
                        "textualRating": "False",
                    }
                ],
            }
        ]
    }
    rows = factcheck.normalize_claims(raw)
    assert len(rows) == 1
    assert rows[0]["publisher"] == "Alt News"
    assert rows[0]["rating"] == "False"


def test_summarize_conservative_default():
    assert factcheck.summarize([]) == "unverified"
    assert factcheck.summarize([{"rating": "False"}]) == "disputed"
    assert factcheck.summarize([{"rating": "True"}]) == "supported"
    assert factcheck.summarize([{"rating": "True"}, {"rating": "False"}]) == "mixed"
