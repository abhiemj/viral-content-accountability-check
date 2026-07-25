"""Fetch captions/transcripts from a YouTube link (no audio processing)."""

from __future__ import annotations

import re

from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

_ID_RE = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})")


def extract_video_id(url: str) -> str | None:
    """Pull the 11-char video id out of any common YouTube URL form."""
    if not url:
        return None
    match = _ID_RE.search(url)
    if match:
        return match.group(1)
    stripped = url.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", stripped):
        return stripped
    return None


def get_transcript(url: str, languages: tuple[str, ...] = ("en", "hi")) -> tuple[str, list[dict]]:
    """Return (video_id, segments). Each segment is {text, start, duration}."""
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Could not extract a YouTube video ID from the input.")
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id, languages=list(languages))
    except (TranscriptsDisabled, NoTranscriptFound) as exc:
        raise ValueError(f"No transcript/captions available for this video: {exc}") from exc
    return video_id, segments


def full_text(segments: list[dict]) -> str:
    """Join transcript segments into one string."""
    return " ".join(seg.get("text", "").replace("\n", " ") for seg in segments).strip()


def locate_timestamp(claim: str, segments: list[dict]) -> float | None:
    """Best-effort start time (seconds) for where a claim appears."""
    head = " ".join(claim.split()[:4]).lower()
    if not head:
        return None
    for seg in segments:
        if head in seg.get("text", "").lower():
            return float(seg.get("start", 0))
    # fall back to matching any single distinctive word
    for word in claim.lower().split():
        if len(word) < 5:
            continue
        for seg in segments:
            if word in seg.get("text", "").lower():
                return float(seg.get("start", 0))
    return None
