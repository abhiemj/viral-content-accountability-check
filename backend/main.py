"""Accountability Check API + static web app.

Run with:
    uvicorn backend.main:app --reload
Then open http://127.0.0.1:8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import claims as claim_utils
from . import factcheck, youtube
from .config import DEFAULT_LANGUAGE, MAX_CLAIMS

app = FastAPI(
    title="Accountability Check API",
    description="Fact-check news/minister claims against Google's fact-check repository.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ---------- request models ----------

class ClaimRequest(BaseModel):
    query: str
    language: str | None = None
    maxAgeDays: int | None = None


class LinkRequest(BaseModel):
    url: str
    language: str | None = None
    maxClaims: int | None = None


# ---------- API routes ----------

@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/verify/claim")
def verify_claim(body: ClaimRequest) -> dict:
    """Fact-check a single piece of text / claim."""
    try:
        raw = factcheck.search_claims(
            body.query,
            language_code=body.language or DEFAULT_LANGUAGE,
            max_age_days=body.maxAgeDays,
        )
    except factcheck.FactCheckError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = factcheck.normalize_claims(raw)
    return {
        "query": body.query,
        "verdict": factcheck.summarize(results),
        "count": len(results),
        "results": results,
    }


@app.post("/api/verify/link")
def verify_link(body: LinkRequest) -> dict:
    """Fetch a YouTube transcript, extract claims, and fact-check each one."""
    try:
        video_id, segments = youtube.get_transcript(body.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = youtube.full_text(segments)
    max_claims = body.maxClaims or MAX_CLAIMS
    extracted = claim_utils.extract_claims(text, max_claims=max_claims)

    checked = []
    for claim_text in extracted:
        query = claim_utils.to_keywords(claim_text)
        try:
            raw = factcheck.search_claims(
                query, language_code=body.language or DEFAULT_LANGUAGE
            )
            results = factcheck.normalize_claims(raw)
        except factcheck.FactCheckError as exc:
            results = []
            verdict = f"error: {exc}"
        else:
            verdict = factcheck.summarize(results)
        checked.append(
            {
                "claim": claim_text,
                "query": query,
                "timestamp": youtube.locate_timestamp(claim_text, segments),
                "verdict": verdict,
                "count": len(results),
                "results": results,
            }
        )

    return {
        "videoId": video_id,
        "claimsFound": len(extracted),
        "claims": checked,
    }


# ---------- static frontend (mounted last so /api routes win) ----------

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
