"""
llm.py — thin Claude wrapper.

Every call auto-injects `prompts/global_context.txt` into the system prompt
so every generation honors the global output rules.
"""

import json
import re
import anthropic

from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, PROMPTS_DIR

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def load_prompt(name: str) -> str:
    """Load a prompt file by basename (supports subpaths like 'examples/top5')."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text()


def _global_context() -> str:
    try:
        return load_prompt("global_context")
    except FileNotFoundError:
        return ""


def call(system: str, user: str, max_tokens: int = MAX_TOKENS) -> str:
    """
    Call Claude with a system + user prompt. Returns raw text.
    Auto-prepends the global context to the system prompt.
    """
    ctx = _global_context()
    full_system = f"{ctx}\n\n---\n\n{system}" if ctx else system

    resp = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=full_system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text.strip()


def extract_json(text: str):
    """Pull the first JSON object or array out of a response."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = None
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start is None:
        raise ValueError(f"No JSON found in: {text[:200]}")
    end = text.rfind("}") if text[start] == "{" else text.rfind("]")
    return json.loads(text[start:end + 1])
