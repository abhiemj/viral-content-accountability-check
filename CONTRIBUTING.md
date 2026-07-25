# Contributing to Accountability Check

Thanks for helping build a tool for public accountability! 🙏
Contributions of all kinds are welcome — new features, bug fixes, docs,
translations, and ideas.

## Ground rules (please read first)

This project **reports what independent fact-checkers have published** — it does
not make original accusations. To keep it credible and safe:

- **Always cite sources.** Any verdict must link to a published fact-check.
- **Stay neutral and non-defamatory.** Attribute findings to their publisher.
- **Default to "Unverified"** when there is no evidence. Absence of a fact-check
  is not proof of anything.
- Keep contributions apolitical in tone — the goal is a fair tool, not a
  partisan one.

By contributing, you agree your work is licensed under the project's
[MIT License](LICENSE), and that you will follow our
[Code of Conduct](CODE_OF_CONDUCT.md). Found a security issue or leaked a key? See
[SECURITY.md](SECURITY.md) — report privately, don't open a public issue.

## Development setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/abhiemj/viral-content-accountability-check.git
cd viral-content-accountability-check

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install pytest

# 4. Add your API key (never commit this file)
cp .env.example .env             # then paste your GOOGLE_FACTCHECK_API_KEY

# 5. Run the app
uvicorn backend.main:app --reload
```

## Workflow

1. **Open an issue first** for anything non-trivial, so we can agree on the
   approach before you write code.
2. **Create a branch** off `main` with a descriptive name:
   `feat/article-url-support`, `fix/transcript-encoding`, `docs/readme`.
3. **Make your change** and add/adjust tests.
4. **Run the checks locally** (see below) — they must pass.
5. **Open a Pull Request** against `main`. Fill in the PR template, link the
   issue, and describe what you changed and how you tested it.
6. A maintainer reviews. Once approved and CI is green, it gets merged.

> `main` is protected — you can't push to it directly. All changes go through a
> Pull Request that passes CI and review.

## Running checks

```bash
pytest -q                                   # unit tests (no network needed)
python -c "from backend.main import app"    # import sanity check
```

CI runs these automatically on every PR (Python 3.10–3.12). PRs can't be merged
until they're green.

## Code style

- Python: standard library + type hints; keep functions small and readable.
- Match the style of the surrounding code; no large reformatting in feature PRs.
- Keep secrets out of the repo. Never commit `.env` or API keys.
- Frontend: vanilla HTML/CSS/JS, no build step — keep it dependency-free.

## Good first issues / feature ideas

- Article-URL mode (scrape + fact-check a news article's text)
- Better claim extraction in the web app (smarter sentence filtering)
- Local Whisper transcription for videos without captions
- Multi-language claim matching (Hindi + regional languages)
- Result caching so repeat checks are instant
- A browser-extension frontend on top of the existing API

See the [issues tab](../../issues) for the current list.

## Reporting bugs / requesting features

Use the issue templates. For bugs, include steps to reproduce, what you expected,
and what happened (with any error output). **Never paste your API key** into an
issue.
