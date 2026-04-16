"""outreach.py — draft 3-variable + email + LinkedIn openers per account."""

import json
from . import llm


def generate(company_profile: dict, triggers: list, accounts: list) -> list:
    # Merge account buyer titles into trigger records for richer context
    by_name = {a["name"]: a for a in accounts}
    enriched = []
    for t in triggers:
        acc = by_name.get(t["account"], {})
        enriched.append({**t, "buyer_title": acc.get("likely_buyer", ""), "industry": acc.get("industry", "")})

    system = llm.load_prompt("system")
    user = llm.load_prompt("outreach_generation").format(
        company_profile_one_line=company_profile.get("one_line", ""),
        value_prop=company_profile.get("value_prop", ""),
        triggers_json=json.dumps(enriched, indent=2),
    )
    raw = llm.call(system, user, max_tokens=3000)
    data = llm.extract_json(raw)
    return data.get("outreach", [])
