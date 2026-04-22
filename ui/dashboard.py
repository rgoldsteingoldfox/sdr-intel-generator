"""
dashboard.py — SDR pipeline dashboard.

Clean internal sales tool. Simple, readable, scan-first.

Run:
  streamlit run ui/dashboard.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from config import LATEST_JSON, OUTPUT_DIR
from modules.slug import slugify

st.set_page_config(
    page_title="SDR Pipeline",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── Data helpers ────────────────────────────────────────────────────────────
def list_companies():
    """Return list of (slug, display_name) tuples for every saved report."""
    items = []
    for f in sorted(OUTPUT_DIR.glob("*.json")):
        if f.name == "latest_report.json":
            continue
        try:
            data = json.loads(f.read_text())
            name = data.get("meta", {}).get("company", f.stem)
            items.append((f.stem, name))
        except Exception:
            continue
    return items


def load():
    """Load a company's report based on ?company=<slug> URL param, else latest."""
    params = st.query_params
    slug = params.get("company", "")
    if isinstance(slug, list):
        slug = slug[0] if slug else ""
    slug = (slug or "").strip().lower()

    if slug:
        target = OUTPUT_DIR / f"{slug}.json"
        if target.exists():
            return json.loads(target.read_text()), slug

    if LATEST_JSON.exists():
        return json.loads(LATEST_JSON.read_text()), ""

    st.error("No report yet. Run:  python3 main.py <company> --icp-file <file>")
    st.stop()


report, active_slug = load()


def priority_score(acc: dict, idx: int) -> int:
    for k in ("priority_score", "warmth_score", "score"):
        v = acc.get(k)
        if isinstance(v, (int, float)):
            return int(v)
    return 10 if idx < 3 else 8 if idx < 6 else 6


def priority_label(p: int) -> str:
    if p >= 9:
        return f"Priority {p} (High likelihood to engage)"
    if p >= 7:
        return f"Priority {p} (Moderate likelihood)"
    return f"Priority {p} (Longer-term watchlist)"


def one_line(txt: str, max_chars: int = 80) -> str:
    if not txt:
        return "—"
    txt = " ".join(txt.split())
    return txt[: max_chars - 1].rstrip() + "…" if len(txt) > max_chars else txt


meta     = report.get("meta", {})
accounts = report.get("accounts", [])
triggers = {t.get("account"): t for t in report.get("triggers", [])}
outreach = {o.get("account"): o for o in report.get("outreach", [])}
company  = meta.get("company", "Company")

for i, a in enumerate(accounts):
    a["_priority"] = priority_score(a, i)

sorted_accounts = sorted(accounts, key=lambda a: -a["_priority"])


# ── Layout CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      /* Centered, width-capped container with generous top padding */
      .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1000px !important;
        margin: 0 auto;
        overflow: visible !important;
      }
      header[data-testid="stHeader"] { background: transparent; }
      .stApp { overflow: visible !important; }

      /* Header block */
      .page-title    { font-size: 1.65rem; font-weight: 700; line-height: 1.2; margin: 0 0 4px 0; }
      .page-subtitle { font-size: 0.9rem;  color: #94a3b8; margin: 0 0 20px 0; }

      /* Cards — consistent padding + spacing */
      div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 14px 18px !important;
        margin-bottom: 16px !important;
        border-radius: 8px !important;
      }
      div[data-testid="stVerticalBlockBorderWrapper"] p {
        margin-bottom: 0 !important;
        line-height: 1.5 !important;
        font-size: 0.90rem;
      }

      /* KPI metrics — compact, consistent */
      div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
      div[data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
      }

      /* Top-5 highlight box */
      .kill-box {
        background: linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(139,92,246,0.08) 100%);
        border: 1px solid rgba(139,92,246,0.30);
        border-radius: 10px;
        padding: 20px 22px;
        margin-bottom: 28px;
      }
      .kill-title   { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.15em; color: #a78bfa; }
      .kill-head    { font-size: 1.08rem; font-weight: 700; margin: 4px 0 4px 0; line-height: 1.35; }
      .kill-sub     { font-size: 0.82rem; color: #94a3b8; margin-bottom: 14px; }
      .kill-row     { font-size: 0.92rem; line-height: 1.7; padding: 3px 0; }
      .kill-num     { color: #60a5fa; font-weight: 700; margin-right: 8px; }
      .kill-arrow   { color: #94a3b8; margin: 0 4px; }
      .kill-outcome { color: #cbd5e1; }

      /* Card row hierarchy */
      .row-name  { font-weight: 700; font-size: 1.00rem; }
      .row-meta  { color: #94a3b8; font-size: 0.82rem; }
      .pri       { text-align: right; font-size: 0.84rem; color: #f8fafc; font-weight: 600; padding-top: 3px; }

      /* Section heading above pipeline */
      .pipeline-heading {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #94a3b8;
        text-transform: uppercase;
        margin: 8px 0 12px 0;
      }

      /* Label tags */
      .tag   { font-weight: 600; font-size: 0.82rem; margin-right: 4px; }
      .tag-t { color: #ef4444; }
      .tag-w { color: #f59e0b; }
      .tag-f { color: #10b981; }

      /* View Details button breathing room */
      div[data-testid="stPopover"] { padding-top: 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Company switcher (only shown when no specific company is selected) ─────
_all_companies = list_companies()
if len(_all_companies) > 1 and not active_slug:
    links = " · ".join(
        f"<a href='?company={slug}' target='_self' style='color:#94a3b8; text-decoration:none;'>{name}</a>"
        for slug, name in _all_companies
    )
    st.markdown(
        f"<div style='font-size:0.78rem; color:#64748b; margin-bottom:12px;'>"
        f"<span style='text-transform:uppercase; letter-spacing:0.12em; margin-right:8px;'>Dashboards:</span>"
        f"{links}</div>",
        unsafe_allow_html=True,
    )


# ── HEADER ──────────────────────────────────────────────────────────────────
h1, h2 = st.columns([6, 2])
with h1:
    st.markdown(f"<div class='page-title'>{company} · SDR Pipeline</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>High-priority accounts, ranked by trigger signal</div>",
        unsafe_allow_html=True,
    )
with h2:
    k1, k2 = st.columns(2)
    k1.metric("Accounts", len(accounts))
    high = sum(1 for a in accounts if a["_priority"] >= 9)
    k2.metric("High Priority", high)


# ── KILLER TOP-5 SECTION ────────────────────────────────────────────────────
top5 = sorted_accounts[:5]
rows_html = ""
for i, acc in enumerate(top5, 1):
    t = triggers.get(acc.get("name"), {})
    trig_short    = one_line(t.get("trigger_event") or t.get("headline", ""), 55)
    outcome_short = one_line(t.get("why_it_matters") or t.get("why_now") or acc.get("why_fit", ""), 45)
    rows_html += (
        f"<div class='kill-row'>"
        f"<span class='kill-num'>{i}.</span>"
        f"<b>{acc.get('name','?')}</b> — {trig_short} "
        f"<span class='kill-arrow'>→</span>"
        f"<span class='kill-outcome'> {outcome_short}</span>"
        f"</div>"
    )

st.markdown(
    f"""
    <div class="kill-box">
      <div class="kill-title">💡 DAY-1 PRIORITY LIST</div>
      <div class="kill-head">These are the exact accounts I would call if I started tomorrow.</div>
      <div class="kill-sub">Selected on recent triggers, multi-location exposure, and 3–6 month buying probability.</div>
      {rows_html}
    </div>
    """,
    unsafe_allow_html=True,
)


# ── PIPELINE LIST ───────────────────────────────────────────────────────────
st.markdown("<div class='pipeline-heading'>Pipeline · All Accounts</div>", unsafe_allow_html=True)

for acc in sorted_accounts:
    name     = acc.get("name", "Unknown")
    industry = acc.get("industry", "—")
    location = acc.get("location") or f"{acc.get('hq_city','')}, {acc.get('hq_state','')}".strip(", ")
    priority = acc["_priority"]
    why_fit  = acc.get("why_fit", "")

    trig = triggers.get(name, {})
    trigger_text = one_line(trig.get("trigger_event") or trig.get("headline", ""), 75)
    why_now      = one_line(trig.get("why_now", ""), 70)
    why_matters  = one_line(trig.get("why_it_matters") or why_fit, 70)

    out = outreach.get(name, {})
    subj     = out.get("email_subject", "")
    ctx      = out.get("context", "")
    prob     = out.get("problem", "")
    ques     = out.get("question", "")
    linkedin = out.get("linkedin_connect", "")

    with st.container(border=True):
        c1, c2, c3 = st.columns([6, 3, 2])
        with c1:
            st.markdown(
                f"<span class='row-name'>{name}</span> "
                f"<span class='row-meta'>· {industry}"
                f"{' · ' + location if location else ''}</span>",
                unsafe_allow_html=True,
            )
        with c2:
            dot = "🟢" if priority >= 9 else "🟡" if priority >= 7 else "⚪"
            st.markdown(f"<div class='pri'>{dot} {priority_label(priority)}</div>", unsafe_allow_html=True)
        with c3:
            with st.popover("View Details", use_container_width=True):
                st.markdown(f"#### {name}")
                st.caption(f"{industry}{' · ' + location if location else ''}")
                st.markdown("##### 🚨 Trigger")
                st.write(trig.get("trigger_event") or trig.get("headline", "—"))
                st.markdown("##### ⏰ Why Now")
                st.write(trig.get("why_now", "—"))
                st.markdown(f"##### 🎯 Why {company} Fits")
                st.write(trig.get("why_it_matters") or why_fit or "—")
                if ctx or prob or ques:
                    st.markdown("##### 💬 Call Opener")
                    st.info(" ".join(x for x in [ctx, prob, ques] if x))
                if subj or ctx:
                    st.markdown("##### ✉️ Email")
                    if subj:
                        st.markdown(f"**Subject:** {subj}")
                    body = "\n\n".join(x for x in [ctx, prob, ques] if x)
                    if body:
                        st.write(body)
                if linkedin:
                    st.markdown("##### 🔗 LinkedIn Note")
                    st.code(linkedin, language=None)

        st.markdown(
            f"<div style='margin-top:6px;'>"
            f"<span class='tag tag-t'>🚨 Trigger:</span> {trigger_text}<br>"
            f"<span class='tag tag-w'>⏰ Why Now:</span> {why_now}<br>"
            f"<span class='tag tag-f'>🎯 Why {company} Fits:</span> {why_matters}"
            f"</div>",
            unsafe_allow_html=True,
        )
