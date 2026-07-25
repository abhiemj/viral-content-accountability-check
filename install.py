#!/usr/bin/env python3
"""One-shot installer for Viral Content Accountability Check.

Typical use (after your API key is already in .env):
    python install.py

Or write the key and install in one go:
    python install.py --api-key AIza...        # avoid this in shared shells; prefer .env

What it does:
  1. Ensures a .env file exists with your Google Fact Check API key
  2. Installs the Python dependencies (requirements.txt)
  3. Installs the bundled Claude skill into ~/.claude/skills/
  4. Validates the key with a live test query

Flags:
  --api-key KEY     write/overwrite the key in .env (otherwise read from .env)
  --no-deps         skip pip install
  --no-skill        skip installing the Claude skill
  --no-validate     skip the live API test
  --skills-dir DIR  install the skill somewhere other than ~/.claude/skills
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_SRC = ROOT / "skill" / "accountability-check"
ENV_PATH = ROOT / ".env"


def ok(msg: str) -> None:
    print(f"  [ok] {msg}")


def warn(msg: str) -> None:
    print(f"  [!!] {msg}")


def read_env_key() -> str:
    """Manually parse .env (dotenv may not be installed yet)."""
    if not ENV_PATH.exists():
        return ""
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GOOGLE_FACTCHECK_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""


def write_env_key(key: str) -> None:
    ENV_PATH.write_text(
        "# Google Fact Check Tools API key (keep this file private; never commit it).\n"
        f"GOOGLE_FACTCHECK_API_KEY={key}\n"
        "DEFAULT_LANGUAGE=en\n"
        "MAX_CLAIMS=10\n",
        encoding="utf-8",
    )
    ok(f"wrote API key to {ENV_PATH.name}")


def install_deps() -> None:
    print("\n> Installing dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")],
        check=True,
    )
    ok("dependencies installed")


def install_skill(skills_dir: Path) -> None:
    print(f"\n> Installing Claude skill into {skills_dir} ...")
    skills_dir.mkdir(parents=True, exist_ok=True)
    dest = skills_dir / "accountability-check"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILL_SRC, dest)
    ok(f"skill installed -> {dest}")


def validate_key(key: str) -> bool:
    print("\n> Validating API key with a live test query...")
    try:
        import requests  # available after install_deps
    except ImportError:
        warn("requests not installed; skipping validation")
        return False
    try:
        resp = requests.get(
            "https://factchecktools.googleapis.com/v1alpha1/claims:search",
            params={"query": "test", "key": key, "languageCode": "en", "pageSize": 1},
            timeout=20,
        )
    except requests.RequestException as exc:
        warn(f"network error during validation: {exc}")
        return False
    if resp.status_code == 200:
        ok("API key works! 🎉")
        return True
    warn(f"API returned {resp.status_code}. Check that the key is valid and that")
    warn("'Fact Check Tools API' is enabled and allowed in the key's API restrictions.")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Viral Content Accountability Check.")
    parser.add_argument("--api-key")
    parser.add_argument("--no-deps", action="store_true")
    parser.add_argument("--no-skill", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--skills-dir", default=str(Path.home() / ".claude" / "skills"))
    args = parser.parse_args()

    print("=== Viral Content Accountability Check — installer ===")

    if args.api_key:
        write_env_key(args.api_key)

    key = read_env_key()
    if not key:
        warn("No API key found in .env.")
        warn("Create a free key at https://console.cloud.google.com/apis/credentials")
        warn("(enable 'Fact Check Tools API'), then either paste it into .env as")
        warn("GOOGLE_FACTCHECK_API_KEY=... or re-run: python install.py --api-key <KEY>")
        return 1
    ok(".env has an API key")

    if not args.no_deps:
        install_deps()
    if not args.no_skill:
        install_skill(Path(args.skills_dir))
    if not args.no_validate:
        validate_key(key)

    print("\n=== Done! ===")
    print("Start the web app:")
    print("    uvicorn backend.main:app --reload")
    print("Then open http://127.0.0.1:8000")
    print("\nOr just ask Claude: \"accountability check this: <claim or YouTube URL>\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
