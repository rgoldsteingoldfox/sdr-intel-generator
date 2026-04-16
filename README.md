# SDR Intel Generator

A lightweight tool that turns a company + ICP into a ready-to-call SDR pipeline dashboard.

**What the dashboard shows:**
- Top-5 priority list (the exact accounts I'd call day 1)
- All 10 target accounts with trigger + why now + why-fit
- Drafted outreach (email subject, call opener, LinkedIn note)
- Day-1 territory strategy

**Built for:** Sending hiring managers a "here's what I'd do on day 1" portfolio piece when applying to SDR roles.

---

## Usage

```bash
# Required: provide an ICP file (tool refuses to infer ICP)
python3 main.py "Ontic" "Senior SDR" --icp-file examples/ontic_icp.json

# Launch dashboard
python3 -m streamlit run ui/dashboard.py
```

## Per-company workflow

1. Copy `examples/_template_icp.json` → `examples/<company>_icp.json`
2. Fill in ICP (company types, size, industry, personas, pain points, buying triggers, use cases)
3. Run `main.py` with `--icp-file`
4. Refresh the dashboard

## Tech

Python · Anthropic Claude (Haiku) · Streamlit · ~300 lines of core pipeline.
