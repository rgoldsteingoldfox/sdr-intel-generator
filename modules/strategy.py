"""strategy.py — Day-1 territory strategy synthesized from profile + triggers."""

import json
from . import llm


def generate(company_profile: dict, triggers: list) -> dict:
    system = llm.load_prompt("system")
    user = llm.load_prompt("strategy").format(
        company_profile=json.dumps(company_profile, indent=2),
        triggers_json=json.dumps(triggers, indent=2),
    )
    raw = llm.call(system, user, max_tokens=1500)
    return llm.extract_json(raw)
