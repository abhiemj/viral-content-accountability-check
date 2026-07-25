# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in Accountability Check, **please report
it privately** — do not open a public issue, and do not include exploit details
in a public PR.

**Report to: aiburnerofficial25@gmail.com**

Preferably, use GitHub's **[Private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)**
(Repo → **Security** tab → **Report a vulnerability**), which keeps the report
confidential until a fix is ready.

Please include:

- A description of the issue and its potential impact
- Steps to reproduce (proof of concept if possible)
- Affected component (web app / API / Claude skill / scripts) and version/commit

**What to expect:**

- Acknowledgement of your report within a few days
- An assessment and, if confirmed, a fix and coordinated disclosure
- Credit for the discovery if you'd like it

## Supported versions

This is an early-stage project; only the latest `main` is supported. Please make
sure you're on the newest commit before reporting.

## Handling API keys & secrets

This project uses a **Google Fact Check Tools API key**. To keep it safe:

- The key lives only in a local `.env` file, which is **git-ignored** and must
  **never** be committed.
- **Never** paste your API key into an issue, a pull request, logs, or a
  screenshot.
- If you accidentally expose a key:
  1. **Revoke/delete it immediately** in the
     [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials).
  2. Create a new key and update your local `.env`.
  3. If it was committed, remember that rotating the key is what matters —
     removing it from git history alone does **not** make an exposed key safe.
- Restrict your API key (Console → your key → **API restrictions** →
  *Fact Check Tools API* only) so a leaked key can't be abused for other
  Google services.

## Scope notes

- This tool only performs **read-only** searches against a public Google API and
  fetches **public** YouTube captions. It does not store user data or write to
  any external service by default.
- If you add features that handle user data, network writes, or authentication,
  please flag the security implications in your PR.
