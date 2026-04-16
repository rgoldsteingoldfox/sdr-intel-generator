"""
main.py — SDR Intel Generator CLI

ICP is REQUIRED. The system will not infer it.

Usage:
  # Full override — hand-built ICP JSON (fastest, most accurate)
  python3 main.py "Ontic" --icp-file examples/ontic_icp.json

  # OR grounded LLM — paste a real company description as --description
  python3 main.py "Ontic" --description "Ontic is a Connected Intelligence Platform..."

  # Optional role title
  python3 main.py "Ontic" "Senior SDR" --icp-file examples/ontic_icp.json
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

from config import LATEST_JSON, OUTPUT_DIR
from modules import company, accounts, triggers, outreach, strategy
from modules.slug import slugify


def run(company_name: str, role: str, description: str = "", icp_file: str = "") -> dict:
    print(f"\n🔍 {company_name} — {role}\n")

    print("  [1/5] Company profile + ICP...")
    if icp_file:
        print(f"        ↳ ICP from {icp_file}")
    elif description:
        print(f"        ↳ Grounded with {len(description)}-char description")
    profile = company.analyze(company_name, role, description=description, icp_file=icp_file)

    print("  [2/5] Target accounts...")
    accts = accounts.generate(profile)

    print("  [3/5] Triggers...")
    trigs = triggers.generate(accts, company_name)

    print("  [4/5] Outreach...")
    reach = outreach.generate(profile, trigs, accts)

    print("  [5/5] Strategy...")
    strat = strategy.generate(profile, trigs)

    report = {
        "meta": {
            "company": company_name,
            "role": role,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "grounding": "icp_file" if icp_file else "description",
        },
        "profile":  profile,
        "accounts": accts,
        "triggers": trigs,
        "outreach": reach,
        "strategy": strat,
    }

    # Save per-company snapshot (e.g. output/ontic.json) + keep latest_report.json
    # as the default fallback for the dashboard.
    slug = slugify(company_name)
    per_company_path = OUTPUT_DIR / f"{slug}.json"
    per_company_path.write_text(json.dumps(report, indent=2))
    LATEST_JSON.write_text(json.dumps(report, indent=2))
    print(f"\n✓ {per_company_path}")
    print(f"  ?company={slug}  (use as URL param on the Streamlit dashboard)")
    return report


def main():
    p = argparse.ArgumentParser(description="SDR Intel Generator — requires ICP input")
    p.add_argument("company", help="Company name to research")
    p.add_argument("role", nargs="?", default="Sales Development Representative")
    p.add_argument("--description", default="",
                   help="Company description (will ground the LLM ICP analysis).")
    p.add_argument("--description-file", default="",
                   help="Path to .txt file containing company description.")
    p.add_argument("--icp-file", default="",
                   help="Path to a JSON file with a pre-built company profile (skips LLM analysis).")
    args = p.parse_args()

    description = args.description
    if args.description_file:
        description = Path(args.description_file).read_text()

    # ── Strict input check — NO ICP INFERENCE ──────────────────────────────
    if not args.icp_file and not description:
        print("ERROR: ICP is required — refusing to infer.")
        print()
        print("Provide one of:")
        print("  --icp-file examples/<company>_icp.json   (best — skips LLM analysis)")
        print("  --description '...'                       (grounds LLM with real info)")
        print("  --description-file path/to/description.txt")
        print()
        print("Template: examples/_template_icp.json")
        sys.exit(2)

    if args.icp_file and not Path(args.icp_file).exists():
        print(f"ERROR: --icp-file not found: {args.icp_file}")
        sys.exit(2)

    run(args.company, args.role, description=description, icp_file=args.icp_file)


if __name__ == "__main__":
    main()
