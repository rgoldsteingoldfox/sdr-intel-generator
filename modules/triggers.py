"""triggers.py — generate a plausible trigger event for each account."""

import json
from . import llm


def generate(accounts: list, company_name: str) -> list:
    system = llm.load_prompt("system")
    user = llm.load_prompt("trigger_generation").format(
        accounts=json.dumps(accounts, indent=2),
        company_name=company_name,
        top5_example=llm.load_prompt("examples/top5"),
        card_example=llm.load_prompt("examples/card"),
    )
    raw = llm.call(system, user, max_tokens=2500)
    data = llm.extract_json(raw)
    return data.get("triggers", [])
