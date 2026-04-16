"""accounts.py — generate 10 realistic target accounts from the company profile."""

import json
from . import llm


def generate(company_profile: dict) -> list:
    system = llm.load_prompt("system")
    user = llm.load_prompt("account_generation").format(
        company_profile=json.dumps(company_profile, indent=2),
        card_example=llm.load_prompt("examples/card"),
    )
    raw = llm.call(system, user, max_tokens=2000)
    data = llm.extract_json(raw)
    return data.get("accounts", [])
