# 🔎 Viral Content Accountability Check

[![CI](https://github.com/abhiemj/viral-content-accountability-check/actions/workflows/ci.yml/badge.svg)](https://github.com/abhiemj/viral-content-accountability-check/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Open-source tool to **fact-check claims made by news channels, ministers, and public
figures**. Paste a claim, a quote, or a video/article URL — get back the matching
**published fact-checks** with ratings and sources.

It uses the **[Google Fact Check Tools API](https://developers.google.com/fact-check/tools/api)**
— the same data source that powers the public
[Fact Check Explorer](https://toolbox.google.com/factcheck/explorer).

There are **two ways to use it**:

1. **A web app + API** you can run locally or host (`backend/` + `frontend/`).
2. **A Claude skill** (`skill/`) where **Claude itself** reads/transcribes the news,
   picks out the check-worthy claims, and verifies each against the fact-check
   repository — no separate LLM key needed.

> ⚖️ **This tool does not decide truth.** It surfaces what independent
> fact-checkers have published, with links. "Unverified" means no fact-check was
> found — **not** that a claim is true or false.

---

## ⚡ Quick install with Claude (one paste)

If you use **[Claude Code](https://claude.com/claude-code)**, you don't have to run
anything by hand. **Copy the prompt below, paste it into Claude, and press enter.**
Claude will walk you through getting a free API key, install everything (including
the Claude skill), and open the app for you.

```text
Install and launch "Viral Content Accountability Check" for me. Do each step, ask me for input where needed, and confirm as you go:

1. Explain how to get a FREE Google Fact Check Tools API key:
   - Open https://console.cloud.google.com/ and create or pick a project
   - Enable the "Fact Check Tools API"
   - Go to APIs & Services -> Credentials -> Create credentials -> API key
   - Edit the key -> API restrictions -> allow "Fact Check Tools API" (or "Don't restrict key")
   Then ask me to paste the key.

2. If this repo is not already in my current folder, clone it and cd into it:
   git clone https://github.com/abhiemj/viral-content-accountability-check.git

3. Save my API key into a .env file using your file-writing tool. Do NOT print the key on the command line or commit it.

4. Run: python install.py
   (this installs dependencies, copies the Claude skill into ~/.claude/skills/, and validates my key)

5. Start the server in the background (uvicorn backend.main:app) and open http://127.0.0.1:8000 in the browser.

6. Tell me it is ready and give me 2-3 example claims and a YouTube URL I can try.
```

Once it's done, the skill is installed too — so any time, you can just tell Claude:
> *"accountability check this: `<a claim, or a YouTube link>`"*

Prefer to do it manually? See **[Quick start](#quick-start-web-app)** below.

---

## Features

- ✅ Verify a single claim / quote / news statement
- ✅ Verify a **YouTube link** — pulls captions, extracts check-worthy claims, checks each
- ✅ Every result links to the original published fact-check
- ✅ Conservative verdicts (defaults to *Unverified*, never guesses)
- ✅ Works as a standalone web app **or** a Claude skill

---

## Quick start (web app)

### 1. Get a Google Fact Check API key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project → **APIs & Services** → enable **Fact Check Tools API**.
3. Create an **API key** under **Credentials**.

### 2. Install & configure
```bash
git clone https://github.com/abhiemj/viral-content-accountability-check.git
cd viral-content-accountability-check
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your key into .env
```

### 3. Run
```bash
uvicorn backend.main:app --reload
```
Open <http://127.0.0.1:8000> and start checking claims.

---

## API

Interactive docs auto-generated at `/docs` (Swagger UI).

### `POST /api/verify/claim`
```json
{ "query": "unemployment at a 40-year low", "language": "en" }
```

### `POST /api/verify/link`
```json
{ "url": "https://www.youtube.com/watch?v=VIDEO_ID" }
```
Returns the extracted claims, each with its fact-check results and a rough video
timestamp.

### Example (`curl`)
```bash
curl -s -X POST http://127.0.0.1:8000/api/verify/claim \
  -H "Content-Type: application/json" \
  -d '{"query":"protest in india"}' | python -m json.tool
```

---

## Use it as a Claude skill

The `skill/accountability-check/` folder is a ready-to-install
[Claude skill](https://docs.claude.com/en/docs/claude-code/skills).

### Install
Copy the skill into your Claude skills directory:
```bash
cp -r skill/accountability-check ~/.claude/skills/
pip install -r ~/.claude/skills/accountability-check/requirements.txt
export GOOGLE_FACTCHECK_API_KEY="your_key_here"
```

### Use
Just ask Claude:
- *"Accountability check this: 'The government created 2 crore jobs last year.'"*
- *"Fact-check the claims in this video: https://youtube.com/watch?v=..."*

Claude will read/transcribe the content, extract the factual claims, call the
Google Fact Check API via the bundled scripts, and write a sourced accountability
report.

The helper scripts also work on their own:
```bash
python skill/accountability-check/scripts/transcript.py "<youtube-url>" --text
python skill/accountability-check/scripts/factcheck.py --query "gdp growth india"
```

---

## Project structure

```
accountability-check/
├── backend/                 # FastAPI app + fact-check logic
│   ├── main.py              # API routes, serves the frontend
│   ├── factcheck.py         # Google Fact Check API client
│   ├── youtube.py           # caption fetching
│   ├── claims.py            # heuristic claim extraction (web-app fallback)
│   └── config.py
├── frontend/                # static web UI (HTML/CSS/JS)
├── skill/accountability-check/   # installable Claude skill
│   ├── SKILL.md
│   └── scripts/             # standalone transcript.py + factcheck.py
├── tests/                   # pytest unit tests (no network)
├── requirements.txt
└── .env.example
```

---

## Running tests
```bash
pip install pytest
pytest
```

---

## Roadmap / ideas for contributors

- [x] YouTube caption fetching + claim extraction + fact-check pipeline
- [ ] Article-URL mode (scrape + fact-check a news article's text)
- [ ] Better claim extraction in the web app (smarter sentence filtering)
- [ ] Local Whisper transcription for videos **without** captions
- [ ] Multi-language claim matching (Hindi + regional languages)
- [ ] Cache verified videos so repeat checks are instant
- [ ] A browser-extension frontend on top of this same API
- [ ] Pull from additional fact-check aggregators beyond Google

## Contributing

Contributions are very welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)** for
setup, workflow, and ground rules.

The short version:

1. **Fork** the repo and create a branch (`feat/...`, `fix/...`).
2. Make your change, add tests, and run `pytest -q`.
3. Open a **Pull Request** against `main` — CI must pass and a maintainer reviews.

`main` is protected: no direct pushes, and every change lands through a reviewed,
CI-passing PR.

> **Maintainers:** see **[MAINTAINERS.md](MAINTAINERS.md)** for how to publish the
> repo and configure branch protection so `main` stays secure while the project
> is open to contributors.

---

## Limitations & ethics

- The Google fact-check repository is **incomplete**, especially for very recent
  or regional claims. Absence of a result is not evidence of anything.
- This tool **reports** what published fact-checkers found; it does not make
  original accusations. Keep contributions neutral, sourced, and non-defamatory.
- Attribute every finding to its publisher.

---

## License

[MIT](LICENSE) — free to use, modify, and build on.
