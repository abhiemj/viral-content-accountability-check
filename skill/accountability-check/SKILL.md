---
name: accountability-check
description: Fact-check claims made by news channels, ministers, or public figures. Use when the user provides a news statement, quote, or a video/article URL and wants the factual claims verified against Google's fact-check repository. Triggers include "fact check this", "verify this claim", "is this true", "accountability check", or when the user pastes a news clip URL or a politician's remark.
---

# Accountability Check

Turn a piece of news — raw text, a quote, or a URL — into a sourced
accountability report. **You (Claude) are the intelligence here**: you read or
transcribe the content, decide which statements are check-worthy factual claims,
and then verify each one against published fact-checks via the Google Fact Check
Tools API. No separate LLM is involved.

## Prerequisites

- `GOOGLE_FACTCHECK_API_KEY` must be set in the environment. If it is missing,
  the `factcheck.py` script returns an error — tell the user how to get a key
  (Google Cloud Console → enable "Fact Check Tools API" → create an API key).
- Python packages: `requests`, `youtube-transcript-api`
  (`pip install requests youtube-transcript-api`).

## Inputs you may receive

1. **Plain text / a quote** — e.g. "The minister said unemployment is at a 40-year low."
2. **A YouTube URL** — you fetch its captions first.
3. **An article URL** — use your web-reading ability (WebFetch) to read it.

## Workflow

### Step 1 — Get the content

- **Text:** use it directly.
- **YouTube URL:** run the transcript script:
  ```bash
  python scripts/transcript.py "<URL>" --text
  ```
  If captions are unavailable, tell the user and ask for the text instead.
- **Article URL:** read it with WebFetch.

### Step 2 — Extract check-worthy claims (your judgement)

Read the content and list the **verifiable factual claims** — statements with
numbers, statistics, dated events, named comparisons, or attributed quotes.
**Ignore** opinions, predictions, promises, and rhetoric.

For each claim, note who said it (the claimant) and, for videos, roughly when.

### Step 3 — Verify each claim

For every claim, build a short **keyword query** (drop filler words) and run:
```bash
python scripts/factcheck.py --query "<keywords>" --language en
```
Read the returned JSON. Each result has a `publisher`, `rating`
(e.g. "False", "Misleading", "True"), `title`, and `url`.

Tips:
- Try a couple of keyword variations if the first search returns nothing.
- Use `--language hi` (or another code) for non-English claims.
- Use `--max-age-days` to restrict to recent reviews when relevant.

### Step 4 — Assign a status to each claim

Base the status **only on what the fact-checks say** — never assert a verdict
the sources don't support:

- **Disputed** — one or more reputable fact-checks rate it False/Misleading.
- **Supported** — fact-checks rate it True/Accurate.
- **Mixed** — sources disagree or the claim is partly true.
- **Unverified** — no published fact-check found. This does NOT mean the claim
  is true or false; say so explicitly.

### Step 5 — Write the accountability report

Produce a clear, neutral report:

```
## Accountability Report
Source: <url or "pasted text">   |   Speaker/Channel: <if known>

### 1. "<the claim, quoted>"
- Status: Disputed
- What fact-checkers found: <1–2 sentence summary>
- Sources:
  - <Publisher> — "<title>" (<rating>) — <url>

### 2. "<next claim>"
- Status: Unverified
- No published fact-check found for this claim.
...

### Summary
<X claims checked: N disputed, N supported, N unverified.>
```

## Rules

- **Always cite sources.** Every non-"unverified" status must link to a
  published fact-check. Never invent a verdict or a source.
- **Stay neutral and non-defamatory.** Report what fact-checkers found; attribute
  it ("According to <publisher>…"). Do not add your own accusations.
- **Default to Unverified** when evidence is absent. Absence of a fact-check is
  not proof of anything.
- **Be transparent about coverage.** The Fact Check repository is incomplete,
  especially for very recent or regional claims. Say when coverage is thin.
