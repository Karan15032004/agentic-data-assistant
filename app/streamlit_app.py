# =========================================================
# app/streamlit_app.py
# Agentic Data Assistant — Streamlit Frontend
# =========================================================

import streamlit as st
import requests
import json
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Agentic Data Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    :root {
        --bg-primary:   #0a0e1a;
        --bg-secondary: #0f1629;
        --bg-card:      #131c35;
        --accent-cyan:  #00f5ff;
        --accent-amber: #ffb700;
        --accent-green: #00ff88;
        --accent-red:   #ff4757;
        --text-primary: #e8eaf6;
        --text-muted:   #7986a8;
        --border:       #1e2d50;
    }

    .stApp {
        background-color: var(--bg-primary);
        font-family: 'Syne', sans-serif;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    section[data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
        min-width: 260px !important;
    }
    section[data-testid="stSidebar"] > div {
        display: flex !important;
        visibility: visible !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
    }

    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }

    .app-header {
        background: linear-gradient(135deg, #0f1629 0%, #131c35 50%, #0a1628 100%);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent-cyan);
        border-radius: 8px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
    }
    .app-title {
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 800;
        color: var(--accent-cyan); letter-spacing: -0.5px; margin: 0;
        text-shadow: 0 0 30px rgba(0,245,255,0.3);
    }
    .app-subtitle {
        color: var(--text-muted); font-size: 0.9rem;
        font-family: 'JetBrains Mono', monospace; margin-top: 0.3rem;
    }

    .section-header {
        font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700;
        color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 2px;
        border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }

    .metric-card {
        background: var(--bg-card); border: 1px solid var(--border);
        border-radius: 8px; padding: 1.2rem 1.5rem; text-align: center;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace; font-size: 2rem;
        font-weight: 700; color: var(--accent-cyan);
    }
    .metric-label {
        color: var(--text-muted); font-size: 0.75rem;
        text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0.3rem;
    }

    .badge-success {
        background: rgba(0,255,136,0.15); color: var(--accent-green);
        border: 1px solid rgba(0,255,136,0.3); padding: 0.2rem 0.8rem;
        border-radius: 20px; font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase;
    }
    .badge-error {
        background: rgba(255,71,87,0.15); color: var(--accent-red);
        border: 1px solid rgba(255,71,87,0.3); padding: 0.2rem 0.8rem;
        border-radius: 20px; font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase;
    }
    .badge-warning {
        background: rgba(255,183,0,0.15); color: var(--accent-amber);
        border: 1px solid rgba(255,183,0,0.3); padding: 0.2rem 0.8rem;
        border-radius: 20px; font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase;
    }

    .info-box {
        background: rgba(0,245,255,0.05); border: 1px solid rgba(0,245,255,0.2);
        border-left: 3px solid var(--accent-cyan); border-radius: 6px;
        padding: 1rem 1.2rem; margin: 1rem 0;
        color: var(--text-primary); font-size: 0.9rem;
    }

    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--accent-cyan) !important;
        color: var(--accent-cyan) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important; letter-spacing: 1px !important;
        text-transform: uppercase !important; border-radius: 6px !important;
        padding: 0.5rem 1.5rem !important; transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: rgba(0,245,255,0.1) !important;
        box-shadow: 0 0 20px rgba(0,245,255,0.2) !important;
    }

    [data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border) !important; border-radius: 8px !important;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important; border-radius: 8px !important;
    }
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important; border-radius: 8px !important;
    }

    .status-dot-done {
        width: 10px; height: 10px; background: var(--accent-green);
        border-radius: 50%; display: inline-block;
        box-shadow: 0 0 8px rgba(0,255,136,0.6);
    }
    .status-dot-pending {
        width: 10px; height: 10px; background: var(--text-muted);
        border-radius: 50%; display: inline-block;
    }

    .chat-user {
        background: rgba(0,245,255,0.08); border: 1px solid rgba(0,245,255,0.2);
        border-radius: 12px 12px 4px 12px;
        padding: 0.8rem 1.2rem; margin: 0.8rem 0 0.8rem 3rem;
        color: var(--text-primary); font-size: 0.95rem;
    }
    .chat-assistant {
        background: var(--bg-card); border: 1px solid var(--border);
        border-radius: 12px 12px 12px 4px;
        padding: 0.8rem 1.2rem; margin: 0.8rem 3rem 0.8rem 0;
        color: var(--text-primary); font-size: 0.95rem;
    }
    .chat-label {
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px;
        margin-bottom: 0.4rem; font-family: 'JetBrains Mono', monospace;
    }

    .sql-block {
        background: #0d1117; border: 1px solid var(--border);
        border-left: 3px solid var(--accent-amber); border-radius: 6px;
        padding: 1rem; font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem; color: var(--accent-amber);
        margin: 0.8rem 0; overflow-x: auto; white-space: pre-wrap;
    }

    .quality-bar-container {
        background: var(--border); border-radius: 4px; height: 6px; margin-top: 0.3rem;
    }

    .json-viewer {
        background: #0d1117; border: 1px solid var(--border);
        border-radius: 8px; padding: 1rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #79c0ff;
        max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;
    }

    .styled-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; }
    .styled-table th { background: var(--bg-secondary); color: var(--accent-cyan); padding: 0.7rem 1rem; text-align: left; border-bottom: 1px solid var(--border); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
    .styled-table td { padding: 0.6rem 1rem; border-bottom: 1px solid var(--border); color: var(--text-primary); }
    .styled-table tr:hover td { background: rgba(0,245,255,0.03); }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=300)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API."}, 503
    except Exception as e:
        return {"error": str(e)}, 500


def api_post(endpoint, data=None, files=None):
    try:
        if files:
            r = requests.post(f"{API_BASE}{endpoint}", files=files, timeout=300)
        else:
            r = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=300)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API."}, 503
    except Exception as e:
        return {"error": str(e)}, 500


def get_pipeline_status():
    result, code = api_get("/status")
    if code == 200:
        return result
    return {"etl_done": False, "metadata_done": False, "quality_done": False}


def render_risk_badge(risk):
    mapping = {"LOW": "success", "MEDIUM": "warning", "HIGH": "error", "CRITICAL": "error"}
    t = mapping.get(risk.upper(), "warning")
    return f'<span class="badge-{t}">{risk}</span>'


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem 0; border-bottom:1px solid #1e2d50;">
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800;
                    color:#00f5ff; letter-spacing:-0.3px;">
            ⚡ Agentic Data
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.7rem;
                    color:#7986a8; margin-top:0.2rem;">
            AI-Powered Pipeline v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🚀 Pipeline", "🔍 Data Explorer", "💬 Query Chat"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:2px;
                color:#7986a8; font-family:'JetBrains Mono',monospace;
                padding-bottom:0.5rem; border-bottom:1px solid #1e2d50;">
        Pipeline Status
    </div>
    """, unsafe_allow_html=True)

    pstate = get_pipeline_status()
    for step_name, key in [("ETL", "etl_done"), ("Metadata", "metadata_done"), ("Quality", "quality_done")]:
        done = pstate.get(key, False)
        dot  = "status-dot-done" if done else "status-dot-pending"
        col  = "#00ff88" if done else "#7986a8"
        lbl  = "DONE" if done else "PENDING"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.7rem;padding:0.5rem 0;'
            f'font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;">'
            f'<span class="{dot}"></span>'
            f'<span style="color:{col};flex:1;">{step_name}</span>'
            f'<span style="color:{col};font-size:0.65rem;">{lbl}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    health, code = api_get("/")
    if code == 200:
        st.markdown("""
        <div style="background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.2);
                    border-radius:6px; padding:0.6rem 1rem;
                    font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#00ff88;">
            🟢 API ONLINE
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(255,71,87,0.08); border:1px solid rgba(255,71,87,0.2);
                    border-radius:6px; padding:0.6rem 1rem;
                    font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#ff4757;">
            🔴 API OFFLINE
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown("""
<div class="app-header">
    <div class="app-title">⚡ Agentic Data Assistant</div>
    <div class="app-subtitle">// AI-Powered Data Pipeline & Query Engine — v1.0.0</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# PAGE 1 — PIPELINE
# =========================================================

if page == "🚀 Pipeline":

    st.markdown('<div class="section-header">01 — Upload & Run Pipeline</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        Upload a CSV, Excel, or JSON file to begin. The pipeline will automatically
        ingest your data, document the schema, and run quality checks.
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in zip(
        [c1, c2, c3],
        ["📥", "🔍", "🛡️"],
        ["ETL Pipeline", "Metadata Agent", "Quality Agent"],
        ["Ingest, clean, store", "Schema discovery", "Data governance"]
    ):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:1.5rem;margin-bottom:0.3rem;">{icon}</div>'
                f'<div style="font-family:\'Syne\',sans-serif;font-weight:700;color:#e8eaf6;font-size:0.9rem;">{title}</div>'
                f'<div style="color:#7986a8;font-size:0.75rem;margin-top:0.3rem;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">02 — Upload File</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your data file here",
        type=["csv", "xlsx", "xls", "json"],
        help="Supported formats: CSV, Excel, JSON"
    )

    if uploaded_file:
        st.markdown(
            f'<div style="background:rgba(0,245,255,0.05);border:1px solid rgba(0,245,255,0.2);'
            f'border-radius:6px;padding:0.8rem 1.2rem;margin:0.5rem 0;'
            f'font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;color:#00f5ff;">'
            f'📄 {uploaded_file.name} &nbsp;&nbsp;'
            f'<span style="color:#7986a8;">{round(uploaded_file.size/1024, 1)} KB</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if st.button("▶ Run Full Pipeline", use_container_width=True):

            with st.status("⚙️ Running Pipeline...", expanded=True) as s:

                st.write("📥 Step 1 — ETL Pipeline...")
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                etl_r, etl_c = api_post("/upload", files=files)
                if etl_c == 200:
                    st.write(f"✅ {etl_r.get('rows_written', 0):,} rows written to `{etl_r.get('table_name')}`")
                    st.session_state["etl_result"] = etl_r
                else:
                    st.write(f"❌ ETL Failed: {etl_r.get('detail', 'Unknown')}")
                    s.update(label="Pipeline Failed", state="error")
                    st.stop()

                st.write("🔍 Step 2 — Metadata Agent (1-2 mins)...")
                meta_r, meta_c = api_post("/run-metadata")
                if meta_c == 200:
                    n = meta_r.get("database_summary", {}).get("total_tables", "?")
                    st.write(f"✅ {n} table(s) documented")
                    st.session_state["metadata_result"] = meta_r
                else:
                    st.write(f"❌ Metadata Failed: {meta_r.get('detail', 'Unknown')}")
                    s.update(label="Pipeline Failed", state="error")
                    st.stop()

                st.write("🛡️ Step 3 — Quality Agent...")
                qual_r, qual_c = api_post("/run-quality")
                if qual_c == 200:
                    st.write("✅ Quality report generated")
                    st.session_state["quality_result"] = qual_r
                else:
                    st.write(f"❌ Quality Failed: {qual_r.get('detail', 'Unknown')}")
                    s.update(label="Pipeline Failed", state="error")
                    st.stop()

                s.update(label="✅ Pipeline Complete!", state="complete")

            st.markdown('<div class="section-header">03 — Results</div>', unsafe_allow_html=True)

            etl  = st.session_state.get("etl_result", {})
            qual = st.session_state.get("quality_result", {})
            qtbl = qual.get("data_quality_summary", {}).get("tables", [])
            score = qtbl[0].get("quality_score", "N/A") if qtbl else "N/A"

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{etl.get("rows_written",0):,}</div><div class="metric-label">Rows Written</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{etl.get("columns_detected",0)}</div><div class="metric-label">Columns</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{etl.get("duplicates_removed",0)}</div><div class="metric-label">Duplicates Removed</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#00ff88;">{score}</div><div class="metric-label">Quality Score</div></div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="info-box" style="margin-top:1rem;">
                ✅ Pipeline complete. Head to <strong>Data Explorer</strong> or <strong>Query Chat</strong>.
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#7986a8;
                    font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
            ↑ Upload a file to get started
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# PAGE 2 — DATA EXPLORER
# =========================================================

elif page == "🔍 Data Explorer":

    st.markdown('<div class="section-header">01 — Schema Documentation</div>', unsafe_allow_html=True)

    meta_data, meta_code = api_get("/metadata")

    if meta_code != 200:
        st.markdown('<div class="info-box">⚠️ No metadata found. Please run the pipeline first.</div>', unsafe_allow_html=True)
    else:
        db  = meta_data.get("database_summary", {})
        tbl = db.get("tables", [])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{db.get("total_tables",0)}</div><div class="metric-label">Tables</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{sum(len(t.get("schema",[])) for t in tbl)}</div><div class="metric-label">Total Columns</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{sum(t.get("row_count",0) for t in tbl):,}</div><div class="metric-label">Total Rows</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for table in tbl:
            tname  = table.get("table_name", "unknown")
            schema = table.get("schema", [])
            rcount = table.get("row_count", 0)

            with st.expander(f"📋 {tname}  —  {rcount:,} rows  •  {len(schema)} columns", expanded=True):
                if schema:
                    rows_html = ""
                    for col in schema:
                        pk = "🔑" if col.get("is_primary_key") else ""
                        nn = "✓"  if col.get("not_null") else ""
                        rows_html += (
                            f"<tr>"
                            f"<td>{pk} {col.get('column_name','')}</td>"
                            f"<td style='color:#ffb700;'>{col.get('data_type','')}</td>"
                            f"<td style='color:#00ff88;'>{nn}</td>"
                            f"</tr>"
                        )
                    st.markdown(
                        f'<table class="styled-table">'
                        f'<thead><tr><th>Column Name</th><th>Data Type</th><th>Not Null</th></tr></thead>'
                        f'<tbody>{rows_html}</tbody>'
                        f'</table>',
                        unsafe_allow_html=True
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">02 — Data Quality Report</div>', unsafe_allow_html=True)

    qual_data, qual_code = api_get("/quality")

    if qual_code != 200:
        st.markdown('<div class="info-box">⚠️ No quality report found. Please run the pipeline first.</div>', unsafe_allow_html=True)
    else:
        for qt in qual_data.get("data_quality_summary", {}).get("tables", []):
            tname  = qt.get("table_name", "")
            score  = qt.get("quality_score", "")
            risk   = qt.get("risk_level", "")
            issues = qt.get("issues_found", [])
            checks = qt.get("checks", {})

            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(
                    f'<div style="font-family:\'Syne\',sans-serif;font-weight:700;'
                    f'font-size:1rem;color:#e8eaf6;margin-bottom:0.5rem;">📊 {tname}</div>',
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f'<div style="text-align:right;">{render_risk_badge(risk)}</div>',
                    unsafe_allow_html=True
                )

            try:
                score_num = float(str(score).replace("%", ""))
            except Exception:
                score_num = 0
            bar = "#00ff88" if score_num >= 80 else "#ffb700" if score_num >= 60 else "#ff4757"

            st.markdown(
                f'<div style="margin:0.5rem 0 1rem 0;">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;'
                f'color:#7986a8;margin-bottom:0.3rem;">'
                f'<span>Quality Score</span>'
                f'<span style="color:{bar};font-weight:700;">{score}</span>'
                f'</div>'
                f'<div class="quality-bar-container">'
                f'<div style="width:{score_num}%;height:100%;background:{bar};border-radius:4px;"></div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            if checks:
                cc = st.columns(min(len(checks), 4))
                for i, (k, v) in enumerate(checks.items()):
                    passed = str(v).lower() in ["true", "pass", "passed", "ok"]
                    with cc[i % 4]:
                        icon = "✅" if passed else "❌"
                        st.markdown(
                            f'<div class="metric-card" style="padding:0.8rem;">'
                            f'<div style="font-size:1.2rem;">{icon}</div>'
                            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7rem;'
                            f'color:#7986a8;margin-top:0.3rem;text-transform:uppercase;">'
                            f'{k.replace("_"," ")}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

            if issues:
                issues_html = "".join(
                    f'<div style="color:#e8eaf6;font-size:0.85rem;padding:0.2rem 0;">• {iss}</div>'
                    for iss in issues
                )
                st.markdown(
                    f'<div style="background:rgba(255,71,87,0.08);border:1px solid rgba(255,71,87,0.2);'
                    f'border-radius:6px;padding:0.8rem 1.2rem;margin:0.8rem 0;">'
                    f'<div style="color:#ff4757;font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;'
                    f'text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">⚠ Issues Detected</div>'
                    f'{issues_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("<hr style='border-color:#1e2d50;margin:1.5rem 0;'>", unsafe_allow_html=True)


# =========================================================
# PAGE 3 — QUERY CHAT
# =========================================================

elif page == "💬 Query Chat":

    st.markdown('<div class="section-header">01 — Natural Language Query</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        Ask questions about your data in plain English. The Query Agent will convert
        your question to SQL, execute it, and return the results.
    </div>
    """, unsafe_allow_html=True)

    pstate = get_pipeline_status()
    if not pstate.get("quality_done"):
        st.markdown("""
        <div style="background:rgba(255,183,0,0.08);border:1px solid rgba(255,183,0,0.2);
                    border-left:3px solid #ffb700;border-radius:6px;padding:1rem 1.2rem;
                    margin:1rem 0;color:#ffb700;font-family:'JetBrains Mono',monospace;font-size:0.85rem;">
            ⚠ Pipeline not complete. Please run the full pipeline first.
        </div>
        """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown('<div class="section-header">02 — Example Questions</div>', unsafe_allow_html=True)

    examples = [
        "Who are the top 5 customers by total sales?",
        "What is the total revenue by category?",
        "Which region has the highest number of orders?",
        "What are the top 3 states by sales?",
    ]

    ex_cols = st.columns(2)
    for i, ex in enumerate(examples):
        with ex_cols[i % 2]:
            if st.button(f"💡 {ex}", key=f"ex_{i}", use_container_width=True):
                st.session_state["prefill_question"] = ex

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown('<div class="section-header">03 — Conversation</div>', unsafe_allow_html=True)

        for entry in st.session_state.chat_history:
            st.markdown(
                f'<div class="chat-user">'
                f'<div class="chat-label" style="color:#00f5ff;">You</div>'
                f'{entry["question"]}'
                f'</div>',
                unsafe_allow_html=True
            )

            result = entry.get("result", {})

            if result.get("status") == "success":
                answer = result.get("answer_summary", "No summary")
                rows   = result.get("rows", 0)
                data   = result.get("data", [])

                st.markdown(
                    f'<div class="chat-assistant">'
                    f'<div class="chat-label" style="color:#00ff88;">Agent</div>'
                    f'{answer}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Show data table only if there are multiple rows worth displaying
                if data and rows > 1:
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

            else:
                st.markdown(
                    f'<div class="chat-assistant" style="border-left:3px solid #ff4757;">'
                    f'<div class="chat-label" style="color:#ff4757;">Agent</div>'
                    f'Sorry, I couldn\'t answer that. Please try rephrasing your question.'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.markdown('<div class="section-header">04 — Ask a Question</div>', unsafe_allow_html=True)

    prefill  = st.session_state.pop("prefill_question", "")
    question = st.text_input(
        "Your question",
        value=prefill,
        placeholder="e.g. Who are the top 5 customers by revenue?",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        ask_clicked = st.button("⚡ Ask Agent", use_container_width=True)
    with col2:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if ask_clicked and question.strip():

        history_to_send = []
        for h in st.session_state.chat_history[-3:]:
            r = h.get("result", {})
            if r.get("status") == "success":
                history_to_send.append({
                    "question":       h["question"],
                    "answer_summary": r.get("answer_summary", "")
                })

        with st.spinner("🤖 Agent is thinking..."):
            result, code = api_post("/query", data={
                "question":             question,
                "conversation_history": history_to_send
            })

        st.session_state.chat_history.append({"question": question, "result": result})
        st.rerun()

    elif ask_clicked and not question.strip():
        st.warning("Please enter a question first.")