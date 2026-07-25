#!/usr/bin/env python3
"""Fetch a YouTube video's captions/transcript from the command line.

Used by the Accountability Check Claude skill. Self-contained: only needs
`youtube-transcript-api`. No API key or audio processing required.

Usage:
    python transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
    python transcript.py VIDEO_ID --text        # plain text only
    python transcript.py URL --languages en hi  # preferred caption languages

Outputs JSON (segments with timestamps) or, with --text, the plain transcript.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    YouTubeTranscriptApi,
)

# Ensure UTF-8 output so non-ASCII transcripts (Hindi, symbols) don't crash on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_ID_RE = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})")


def extract_video_id(url: str) -> str | None:
    match = _ID_RE.search(url or "")
    if match:
        return match.group(1)
    stripped = (url or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", stripped):
        return stripped
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch YouTube captions.")
    parser.add_argument("url", help="YouTube URL or 11-char video id.")
    parser.add_argument("--languages", nargs="+", default=["en", "hi"])
    parser.add_argument("--text", action="store_true", help="Output plain text only.")
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    if not video_id:
        print(json.dumps({"error": "Could not extract a YouTube video ID."}))
        return 1

    try:
        segments = YouTubeTranscriptApi().fetch(video_id, languages=args.languages).to_raw_data()
    except CouldNotRetrieveTranscript as exc:
        print(json.dumps({"error": f"No transcript available: {exc}"}))
        return 1

    if args.text:
        text = " ".join(s.get("text", "").replace("\n", " ") for s in segments).strip()
        sys.stdout.write(text + "\n")
        return 0

    print(json.dumps({"videoId": video_id, "segments": segments}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
