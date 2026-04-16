"""
config.py — single place for environment + model config.
Keep it boring.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# ── LLM ─────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL              = "claude-haiku-4-5-20251001"   # fast + cheap, good enough for demo
MAX_TOKENS         = 1500

# ── Paths ───────────────────────────────────────────────────────────────────
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR  = BASE_DIR / "output"
LATEST_JSON = OUTPUT_DIR / "latest_report.json"

OUTPUT_DIR.mkdir(exist_ok=True)
