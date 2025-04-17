#!/usr/bin/env python
"""
Streamlit Web App for AI Resume Analyzer
Run:  streamlit run app.py
"""
import streamlit as st
import tempfile, json
from pathlib import Path
from datetime import datetime

# Import core analysis
from src.resume_analyzer import analyze_resume, load_config, DEFAULT_CONFIG

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("🔍 AI Resume Analyzer")

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.header("Settings")
cfg_file   = st.sidebar.file_uploader("Upload config.yaml (optional)", type=("yaml","yml"))
save_json  = st.sidebar.checkbox("Save JSON report", value=False)

def get_cfg():
    if cfg_file:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        tmp.write(cfg_file.read()); tmp.flush()
        return load_config(Path(tmp.name))
    return DEFAULT_CONFIG
cfg = get_cfg()

# ── Inputs ─────────────────────────────────────────────────────────────────
resume   = st.file_uploader("Upload résumé (PDF / DOCX)", type=("pdf","docx"))
job_desc = st.text_area("Paste Job Description", height=200,
                        placeholder="Paste the full job description here…")

# ── Run analysis ───────────────────────────────────────────────────────────
if st.button("Analyze"):
    if not resume or not job_desc.strip():
        st.error("Please upload a résumé and paste a job description.")
        st.stop()

    with st.spinner("Analyzing…"):
        # save resume temp
        suffix = Path(resume.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(resume.getbuffer()); tmp.flush()
            res_path = Path(tmp.name)

        report = analyze_resume(res_path, job_desc, cfg)

    # ── Results ──
    st.subheader("📊 Results")
    st.write(f"**Candidate:** {report['candidate']}")
    for c in report['contacts'] or ["No contact info"]:
        st.write(f"**Contact:** {c}")
    st.metric("Match %", f"{report['match_pct']} %")

    st.subheader("💡 Recommendations")
    st.write("\n".join(f"- {r}" for r in report['recommendations'])
             or "None 🎉 Perfect match!")

    # ── Save reports ──
    reports = Path("reports"); reports.mkdir(exist_ok=True)
    stamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_fp  = reports / f"analysis_{stamp}.txt"
    txt_fp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    st.success(f"Saved TXT to {txt_fp}")

    if save_json:
        json_fp = txt_fp.with_suffix(".json")
        json_fp.write_text(json.dumps(report, indent=2), encoding="utf-8")
        st.success(f"Saved JSON to {json_fp}")

    # ── Download buttons ──
    st.download_button("⬇ Download TXT", txt_fp.read_text(), file_name=txt_fp.name)
    if save_json:
        st.download_button("⬇ Download JSON", json_fp.read_text(), file_name=json_fp.name)

