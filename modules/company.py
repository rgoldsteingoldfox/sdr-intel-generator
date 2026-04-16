"""company.py — ICP + value-prop profile for the target company.

Supports 3 modes:
  1. Generated:  LLM analyzes the company from scratch (risk of hallucination
                 for less-known companies).
  2. Grounded:   LLM analyzes + expands on a user-provided description.
  3. Override:   User provides a full ICP JSON file → skip the LLM entirely.
"""

import json
from pathlib import Path

from . import llm


def analyze(company: str, role: str = "", description: str = "", icp_file: str = "") -> dict:
    # Mode 3 — full override
    if icp_file:
        data = json.loads(Path(icp_file).read_text())
        # Make sure the "company" key is populated
        data.setdefault("company", company)
        return data

    # Mode 2 — grounded with a user-provided description
    if description:
        description_block = (
            "Ground your analysis in this description of the company "
            "(treat it as authoritative; expand on it, don't contradict it):\n\n"
            f"{description.strip()}\n"
        )
    else:
        description_block = ""

    system = llm.load_prompt("system")
    user = llm.load_prompt("company_analysis").format(
        company_name=company,
        description_block=description_block,
    )
    raw = llm.call(system, user)
    return llm.extract_json(raw)
