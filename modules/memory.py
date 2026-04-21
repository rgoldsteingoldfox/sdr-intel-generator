"""memory.py — auto-update memory.json after each pipeline run."""

import json
from datetime import datetime
from pathlib import Path

MEMORY_PATH = Path(__file__).parent.parent / "memory.json"


def load() -> dict:
    if MEMORY_PATH.exists():
        return json.loads(MEMORY_PATH.read_text())
    return {"last_updated": None, "total_runs": 0, "runs": [], "application_tracker": {}, "patterns": {}}


def save(data: dict):
    data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    MEMORY_PATH.write_text(json.dumps(data, indent=2))


def record_run(company: str, role: str, slug: str, icp_file: str, top_accounts: list):
    """Record a pipeline run to memory.json."""
    mem = load()
    base_url = "https://sdr-intel-generator-v67rwrtespbdmjq9audq28.streamlit.app"

    # Check if this company already has a run — update instead of duplicate
    existing = next((r for r in mem["runs"] if r["slug"] == slug), None)
    entry = {
        "company": company,
        "role": role,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "icp_file": icp_file,
        "slug": slug,
        "dashboard_url": f"{base_url}/?company={slug}",
        "top_accounts": top_accounts[:5],
        "application_status": "generated",
        "notes": "",
    }

    if existing:
        idx = mem["runs"].index(existing)
        entry["application_status"] = existing.get("application_status", "generated")
        entry["notes"] = existing.get("notes", "")
        mem["runs"][idx] = entry
    else:
        mem["runs"].append(entry)

    mem["total_runs"] = len(mem["runs"])
    save(mem)
    return entry
