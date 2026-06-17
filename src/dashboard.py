import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

st.set_page_config(
    page_title="SDA UP — Metadata Compliance",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
  /* Page background */
  .stApp { background-color: #f0f2f6; }

  /* Hide default Streamlit header padding */
  .block-container { padding-top: 0rem !important; }

  /* ── Hero header ── */
  .hero {
    background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 60%, #1e7bbf 100%);
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 0 0 16px 16px;
    margin-bottom: 1.5rem;
    color: white;
  }
  .hero h1 { color: white; font-size: 1.9rem; margin: 0; font-weight: 700; }
  .hero p  { color: #c8dff5; margin: 0.3rem 0 0; font-size: 0.9rem; }
  .hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.78rem;
    margin-top: 0.6rem;
    margin-right: 0.4rem;
    color: #ddeeff;
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-top: 4px solid #2563a8;
  }
  .kpi-card.green  { border-top-color: #16a34a; }
  .kpi-card.amber  { border-top-color: #d97706; }
  .kpi-card.red    { border-top-color: #dc2626; }
  .kpi-value { font-size: 2.2rem; font-weight: 800; color: #1e293b; line-height:1; }
  .kpi-label { font-size: 0.82rem; color: #64748b; margin-top: 0.35rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }
  .kpi-sub   { font-size: 0.92rem; font-weight: 600; color: #475569; margin-top: 0.2rem; }

  /* ── Section headers ── */
  .section-header {
    background: white;
    border-left: 5px solid #2563a8;
    border-radius: 8px;
    padding: 0.7rem 1.1rem;
    margin: 1.5rem 0 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .section-header h2 {
    margin: 0; font-size: 1.1rem; color: #1a3a5c; font-weight: 700;
  }
  .section-header p {
    margin: 0.15rem 0 0; font-size: 0.8rem; color: #64748b;
  }

  /* ── Panel containers ── */
  .panel-box {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
  }

  /* ── Status badges ── */
  .badge-green { background:#dcfce7; color:#166534; padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }
  .badge-red   { background:#fee2e2; color:#991b1b; padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }
  .badge-amber { background:#fef3c7; color:#92400e; padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600; }

  /* ── Footer ── */
  .footer {
    text-align: center; color: #94a3b8; font-size: 0.76rem;
    margin-top: 2rem; padding: 1rem 0;
    border-top: 1px solid #e2e8f0;
  }

  /* Hide plotly modebar */
  .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────── #
@st.cache_data
def load_data():
    submissions       = pd.read_csv(DATA_DIR / "metadata_submissions.csv")
    tracker           = pd.read_csv(DATA_DIR / "compliance_tracker.csv")
    tracker["final_status"] = tracker["final_status"].str.strip()
    quality_flags     = pd.read_csv(PROCESSED_DIR / "quality_flags.csv")
    compliance_report = pd.read_csv(PROCESSED_DIR / "compliance_report.csv")
    return submissions, tracker, quality_flags, compliance_report

submissions, tracker, quality_flags, compliance_report = load_data()

total    = len(tracker)
approved = (tracker["final_status"] == "Approved").sum()
pending  = tracker["final_status"].str.startswith("Pending", na=False).sum()
dpdp_issues = len(
    submissions[
        (submissions["dpdp_personal_data"] == "Yes") &
        (~submissions["data_classification"].isin(["Restricted", "Confidential"]))
    ]
)

# ── HERO HEADER ───────────────────────────────────────────────────────────── #
st.markdown("""
<div class="hero">
  <h1>🏛️ SDA Uttar Pradesh — Metadata Compliance Dashboard</h1>
  <p>State Data Authority &nbsp;|&nbsp; Data Governance Lead View</p>
  <span class="hero-badge">📅 As of 25 April 2026</span>
  <span class="hero-badge">April 2026 Batch</span>
  <span class="hero-badge">25 Departments</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 1 — Overview KPIs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <h2>📊 Panel 1: Overview</h2>
  <p>Key metrics across all submissions — no interaction required</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-value">{total}</div>
      <div class="kpi-label">Total Submissions</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card green">
      <div class="kpi-value" style="color:#16a34a">{approved}</div>
      <div class="kpi-sub">{round(approved/total*100)}% of total</div>
      <div class="kpi-label">Approved</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card amber">
      <div class="kpi-value" style="color:#d97706">{pending}</div>
      <div class="kpi-sub">{round(pending/total*100)}% of total</div>
      <div class="kpi-label">Pending Correction</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card red">
      <div class="kpi-value" style="color:#dc2626">{dpdp_issues}</div>
      <div class="kpi-sub">DPDP non-compliant</div>
      <div class="kpi-label">DPDP Flag Issues</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# Mini donut chart alongside KPIs
fig_donut = go.Figure(go.Pie(
    labels=["Approved", "Pending"],
    values=[approved, pending],
    hole=0.6,
    marker_colors=["#16a34a", "#d97706"],
    textinfo="percent+label",
    hovertemplate="%{label}: %{value}<extra></extra>",
))
fig_donut.update_layout(
    height=220, margin=dict(t=10, b=10, l=10, r=10),
    showlegend=False,
    annotations=[dict(text=f"<b>{round(approved/total*100)}%</b><br>Approved", x=0.5, y=0.5,
                      font_size=15, showarrow=False)],
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
)
_, mid, _ = st.columns([2, 1, 2])
with mid:
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 2 — Department Status
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <h2>🏢 Panel 2: Department Status</h2>
  <p>Per-department breakdown — sort by approval rate (ascending) to see most problematic departments first</p>
</div>
""", unsafe_allow_html=True)

with st.container():
    filter_col, _ = st.columns([2, 3])
    with filter_col:
        dept_options = compliance_report["department"].tolist()
        selected_depts = st.multiselect("Filter by Department", dept_options, default=dept_options, label_visibility="collapsed")

    filtered_cr = compliance_report[compliance_report["department"].isin(selected_depts)].copy()

    # Build colored HTML table
    def dept_table_html(df):
        rows_html = ""
        for _, r in df.iterrows():
            pct = r["approval_pct"]
            if pct == 100:
                row_bg = "#f0fdf4"
                badge = f'<span class="badge-green">{pct}%</span>'
            elif pct == 0:
                row_bg = "#fff1f2"
                badge = f'<span class="badge-red">{pct}%</span>'
            else:
                row_bg = "#fffbeb"
                badge = f'<span class="badge-amber">{pct}%</span>'

            nr = r["no_response_7plus_days"]
            nr_html = '<span class="badge-red">Yes</span>' if nr == "Yes" else '<span class="badge-green">No</span>'

            fu = r["followup_sent_for_all_pending"]
            fu_html = f'<span class="badge-amber">{fu}</span>' if fu in ("No","Partial") else f'<span>{"—" if fu=="N/A" else fu}</span>'

            rows_html += f"""
            <tr style="background:{row_bg}; border-bottom:1px solid #e2e8f0;">
              <td style="padding:8px 12px;font-weight:500">{r['department']}</td>
              <td style="padding:8px 12px;text-align:center">{int(r['datasets_submitted'])}</td>
              <td style="padding:8px 12px;text-align:center;color:#16a34a;font-weight:600">{int(r['approved'])}</td>
              <td style="padding:8px 12px;text-align:center;color:#d97706;font-weight:600">{int(r['pending'])}</td>
              <td style="padding:8px 12px;text-align:center">{badge}</td>
              <td style="padding:8px 12px;text-align:center">{fu_html}</td>
              <td style="padding:8px 12px;text-align:center">{nr_html}</td>
            </tr>"""

        return f"""
        <div class="panel-box" style="padding:0;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem">
          <thead>
            <tr style="background:#1a3a5c;color:white">
              <th style="padding:10px 12px;text-align:left">Department</th>
              <th style="padding:10px 12px;text-align:center">Submitted</th>
              <th style="padding:10px 12px;text-align:center">Approved</th>
              <th style="padding:10px 12px;text-align:center">Pending</th>
              <th style="padding:10px 12px;text-align:center">Approval %</th>
              <th style="padding:10px 12px;text-align:center">Follow-up Sent</th>
              <th style="padding:10px 12px;text-align:center">No Response 7+ Days</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        </div>"""

    st.markdown(dept_table_html(filtered_cr), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 3 — Issue Breakdown
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <h2>⚠️ Panel 3: Issue Breakdown</h2>
  <p>Most common quality issues across all pending submissions</p>
</div>
""", unsafe_allow_html=True)

pending_ids   = set(tracker[tracker["final_status"].str.startswith("Pending", na=False)]["submission_id"])
pending_flags = quality_flags[quality_flags["submission_id"].isin(pending_ids)]

issue_counts = {}
for issues_str in pending_flags["issues"].dropna():
    for issue in issues_str.split("; "):
        key = issue.split(":")[0].strip()
        issue_counts[key] = issue_counts.get(key, 0) + 1

chart_col, table_col = st.columns([3, 2])
with chart_col:
    if issue_counts:
        issue_df = pd.DataFrame(
            sorted(issue_counts.items(), key=lambda x: x[1]),
            columns=["Issue Type", "Count"],
        )
        short_labels = {
            "Missing data owner name": "Missing data owner",
            "Description missing or too short (<20 chars)": "Description missing",
            "Record count missing (not a live API dataset)": "Record count missing",
            "DPDP inconsistency": "DPDP inconsistency",
            "Classification blank or invalid (must be Public/Restricted/Confidential)": "Classification blank/invalid",
            "Invalid last_updated date format": "Invalid last_updated date",
            "Invalid submitted_on date format": "Invalid submitted_on date",
        }
        issue_df["Short Label"] = issue_df["Issue Type"].map(lambda x: short_labels.get(x, x))

        colors = ["#1e40af","#2563eb","#3b82f6","#60a5fa","#93c5fd","#bfdbfe","#dbeafe"]
        fig_bar = px.bar(
            issue_df, x="Count", y="Short Label", orientation="h",
            color="Short Label",
            color_discrete_sequence=colors[::-1],
            text="Count",
        )
        fig_bar.update_layout(
            height=320, showlegend=False,
            xaxis_title="", yaxis_title="",
            margin=dict(t=10, b=10, l=0, r=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#e2e8f0"),
            yaxis=dict(showgrid=False),
        )
        fig_bar.update_traces(textposition="outside", textfont_size=12)
        st.markdown('<div class="panel-box" style="padding:0.8rem 1rem">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

with table_col:
    if issue_counts:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        st.markdown("**Issue Count Table**")
        table_rows = ""
        for _, r in issue_df.sort_values("Count", ascending=False).iterrows():
            table_rows += f"""
            <tr style="border-bottom:1px solid #f1f5f9">
              <td style="padding:7px 8px;font-size:0.82rem">{r['Short Label']}</td>
              <td style="padding:7px 8px;text-align:center;font-weight:700;color:#2563a8">{int(r['Count'])}</td>
            </tr>"""
        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse">
          <thead><tr style="background:#f8fafc">
            <th style="padding:8px;text-align:left;font-size:0.8rem;color:#64748b">Issue Type</th>
            <th style="padding:8px;text-align:center;font-size:0.8rem;color:#64748b">Count</th>
          </tr></thead>
          <tbody>{table_rows}</tbody>
        </table>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 4 — DPDP Flag Tracker
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <h2>🔒 Panel 4: DPDP Flag Tracker</h2>
  <p>All datasets containing personal data — classification and steward assignment status</p>
</div>
""", unsafe_allow_html=True)

personal = submissions[submissions["dpdp_personal_data"] == "Yes"].copy()
personal["classification_ok"] = personal["data_classification"].isin(["Restricted", "Confidential"])
personal["steward_ok"]        = personal["data_steward_assigned"] == "Yes"
personal["fully_compliant"]   = personal["classification_ok"] & personal["steward_ok"]

def dpdp_table_html(df):
    rows_html = ""
    for _, r in df.iterrows():
        row_bg    = "#f0fdf4" if r["fully_compliant"] else "#fff1f2"
        cls_badge = '<span class="badge-green">✓ OK</span>' if r["classification_ok"] else '<span class="badge-red">✗ Non-compliant</span>'
        swd_badge = '<span class="badge-green">✓ Assigned</span>' if r["steward_ok"] else '<span class="badge-red">✗ Missing</span>'
        cmp_badge = '<span class="badge-green">✓ Compliant</span>' if r["fully_compliant"] else '<span class="badge-red">✗ Not Compliant</span>'
        cls_val   = str(r["data_classification"]) if pd.notna(r["data_classification"]) else "—"
        rows_html += f"""
        <tr style="background:{row_bg};border-bottom:1px solid #e2e8f0">
          <td style="padding:9px 12px;font-weight:600;font-size:0.82rem">{r['submission_id']}</td>
          <td style="padding:9px 12px;font-size:0.82rem">{r['department']}</td>
          <td style="padding:9px 12px;font-size:0.82rem">{r['dataset_title']}</td>
          <td style="padding:9px 12px;text-align:center;font-size:0.82rem">{cls_val}</td>
          <td style="padding:9px 12px;text-align:center">{cls_badge}</td>
          <td style="padding:9px 12px;text-align:center">{swd_badge}</td>
          <td style="padding:9px 12px;text-align:center">{cmp_badge}</td>
        </tr>"""

    return f"""
    <div class="panel-box" style="padding:0;overflow:hidden">
    <table style="width:100%;border-collapse:collapse;font-size:0.84rem">
      <thead>
        <tr style="background:#7c3aed;color:white">
          <th style="padding:10px 12px;text-align:left">ID</th>
          <th style="padding:10px 12px;text-align:left">Department</th>
          <th style="padding:10px 12px;text-align:left">Dataset</th>
          <th style="padding:10px 12px;text-align:center">Classification</th>
          <th style="padding:10px 12px;text-align:center">Classification OK?</th>
          <th style="padding:10px 12px;text-align:center">Steward Assigned?</th>
          <th style="padding:10px 12px;text-align:center">DPDP Status</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>"""

st.markdown(dpdp_table_html(personal), unsafe_allow_html=True)

non_compliant_count = (~personal["fully_compliant"]).sum()
compliant_count     = personal["fully_compliant"].sum()

dcol1, dcol2 = st.columns(2)
with dcol1:
    st.markdown(f'<div style="background:#fee2e2;border-radius:8px;padding:0.7rem 1rem;color:#991b1b;font-weight:600">⚠️ {non_compliant_count} dataset(s) with personal data are NOT fully DPDP compliant</div>', unsafe_allow_html=True)
with dcol2:
    st.markdown(f'<div style="background:#dcfce7;border-radius:8px;padding:0.7rem 1rem;color:#166534;font-weight:600">✅ {compliant_count} dataset(s) with personal data are fully compliant</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────── #
st.markdown("""
<div class="footer">
  State Data Authority (SDA), Uttar Pradesh &nbsp;|&nbsp; Metadata Platform &nbsp;|&nbsp; April 2026 Batch Report<br>
  Data sourced from <code>data/processed/</code> — not hardcoded
</div>
""", unsafe_allow_html=True)
