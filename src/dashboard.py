import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

st.markdown("""
<style>
  .stApp { background-color: #f0f2f6; }
  .block-container { padding-top: 0rem !important; max-width: 1100px; }

  /* Hero */
  .hero {
    background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 60%, #1e7bbf 100%);
    padding: 2.2rem 2rem 1.8rem;
    border-radius: 0 0 16px 16px;
    margin-bottom: 1.8rem;
    text-align: center;
  }
  .hero h1  { color: white; font-size: 1.75rem; margin: 0; font-weight: 700; letter-spacing: -0.01em; }
  .hero p   { color: #b8d4f0; margin: 0.4rem 0 0.8rem; font-size: 0.85rem; }
  .hero-badges { display:flex; justify-content:center; gap:0.5rem; flex-wrap:wrap; }
  .hero-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.85rem;
    font-size: 0.76rem;
    color: #ddeeff;
  }

  /* KPI cards */
  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 1.3rem 1rem 1.1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-top: 4px solid #2563a8;
  }
  .kpi-card.green { border-top-color: #16a34a; }
  .kpi-card.amber { border-top-color: #d97706; }
  .kpi-card.red   { border-top-color: #dc2626; }
  .kpi-value { font-size: 2.4rem; font-weight: 800; color: #1e293b; line-height: 1; }
  .kpi-label { font-size: 0.75rem; color: #64748b; margin-top: 0.4rem; font-weight: 600;
               text-transform: uppercase; letter-spacing: 0.05em; }
  .kpi-sub   { font-size: 0.88rem; font-weight: 600; color: #475569; margin-top: 0.15rem; }

  /* Section headers */
  .sec {
    background: white;
    border-left: 5px solid #2563a8;
    border-radius: 8px;
    padding: 0.65rem 1.1rem;
    margin: 1.8rem 0 0.9rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .sec h2 { margin:0; font-size:1.05rem; color:#1a3a5c; font-weight:700; }
  .sec p  { margin:0.1rem 0 0; font-size:0.76rem; color:#64748b; }

  /* Panels */
  .panel { background:white; border-radius:12px; padding:1.2rem 1.4rem;
           box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:0.8rem; }

  /* Badges */
  .bg { background:#dcfce7; color:#166534; padding:2px 10px; border-radius:12px; font-size:0.76rem; font-weight:600; }
  .br { background:#fee2e2; color:#991b1b; padding:2px 10px; border-radius:12px; font-size:0.76rem; font-weight:600; }
  .ba { background:#fef3c7; color:#92400e; padding:2px 10px; border-radius:12px; font-size:0.76rem; font-weight:600; }

  /* Footer */
  .footer { text-align:center; color:#94a3b8; font-size:0.74rem; margin-top:2rem;
            padding:1rem 0; border-top:1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    submissions       = pd.read_csv(DATA_DIR / "metadata_submissions.csv")
    tracker           = pd.read_csv(DATA_DIR / "compliance_tracker.csv")
    tracker["final_status"] = tracker["final_status"].str.strip()
    quality_flags     = pd.read_csv(PROCESSED_DIR / "quality_flags.csv")
    compliance_report = pd.read_csv(PROCESSED_DIR / "compliance_report.csv")
    return submissions, tracker, quality_flags, compliance_report

submissions, tracker, quality_flags, compliance_report = load_data()

total       = len(tracker)
approved    = (tracker["final_status"] == "Approved").sum()
pending     = tracker["final_status"].str.startswith("Pending", na=False).sum()
dpdp_issues = len(submissions[
    (submissions["dpdp_personal_data"] == "Yes") &
    (~submissions["data_classification"].isin(["Restricted", "Confidential"]))
])


# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>SDA Uttar Pradesh &mdash; Metadata Compliance Dashboard</h1>
  <p>State Data Authority &nbsp;&bull;&nbsp; Data Governance Lead View</p>
  <div class="hero-badges">
    <span class="hero-badge">As of 25 April 2026</span>
    <span class="hero-badge">April 2026 Batch</span>
    <span class="hero-badge">25 Departments</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── PANEL 1: Overview ───────────────────────────────────────────────────────
st.markdown("""
<div class="sec">
  <h2>Panel 1: Overview</h2>
  <p>Key metrics across all submissions</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{total}</div><div class="kpi-label">Total Submissions</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card green"><div class="kpi-value" style="color:#16a34a">{approved}</div><div class="kpi-sub">{round(approved/total*100)}% of total</div><div class="kpi-label">Approved</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card amber"><div class="kpi-value" style="color:#d97706">{pending}</div><div class="kpi-sub">{round(pending/total*100)}% of total</div><div class="kpi-label">Pending</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card red"><div class="kpi-value" style="color:#dc2626">{dpdp_issues}</div><div class="kpi-sub">DPDP non-compliant</div><div class="kpi-label">DPDP Flag Issues</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# Centered donut chart
_, mid, _ = st.columns([1, 2, 1])
with mid:
    fig_donut = go.Figure(go.Pie(
        labels=["Approved", "Pending"],
        values=[approved, pending],
        hole=0.62,
        marker_colors=["#16a34a", "#d97706"],
        textinfo="percent+label",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig_donut.update_layout(
        height=250, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        annotations=[dict(
            text=f"<b>{round(approved/total*100)}%</b><br>Approved",
            x=0.5, y=0.5, font_size=16, showarrow=False
        )],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})


# ─── PANEL 2: Department Status ──────────────────────────────────────────────
st.markdown("""
<div class="sec">
  <h2>Panel 2: Department Status</h2>
  <p>Sorted by approval rate (ascending) — most problematic departments first</p>
</div>
""", unsafe_allow_html=True)

dept_options   = compliance_report["department"].tolist()
selected_depts = st.multiselect(
    "Filter departments", dept_options, default=dept_options, label_visibility="collapsed"
)
filtered_cr = compliance_report[compliance_report["department"].isin(selected_depts)].copy()

def dept_table_html(df):
    rows = ""
    for _, r in df.iterrows():
        pct = r["approval_pct"]
        bg  = "#f0fdf4" if pct == 100 else ("#fff1f2" if pct == 0 else "#fffbeb")
        pct_badge = (f'<span class="bg">{pct}%</span>' if pct == 100
                     else f'<span class="br">{pct}%</span>' if pct == 0
                     else f'<span class="ba">{pct}%</span>')
        nr = r["no_response_7plus_days"]
        nr_html = '<span class="br">Yes</span>' if nr == "Yes" else '<span class="bg">No</span>'
        fu = r["followup_sent_for_all_pending"]
        fu_html = (f'<span class="ba">{fu}</span>' if fu in ("No", "Partial")
                   else ("<span style='color:#94a3b8'>N/A</span>" if fu == "N/A" else f"<span>{fu}</span>"))
        rows += f"""<tr style="background:{bg};border-bottom:1px solid #e2e8f0">
          <td style="padding:9px 12px;font-weight:500;font-size:0.83rem">{r['department']}</td>
          <td style="padding:9px 12px;text-align:center">{int(r['datasets_submitted'])}</td>
          <td style="padding:9px 12px;text-align:center;color:#16a34a;font-weight:600">{int(r['approved'])}</td>
          <td style="padding:9px 12px;text-align:center;color:#d97706;font-weight:600">{int(r['pending'])}</td>
          <td style="padding:9px 12px;text-align:center">{pct_badge}</td>
          <td style="padding:9px 12px;text-align:center">{fu_html}</td>
          <td style="padding:9px 12px;text-align:center">{nr_html}</td>
        </tr>"""
    return f"""<div class="panel" style="padding:0;overflow:hidden">
    <table style="width:100%;border-collapse:collapse;font-size:0.83rem">
      <thead><tr style="background:#1a3a5c;color:white">
        <th style="padding:10px 12px;text-align:left">Department</th>
        <th style="padding:10px 12px;text-align:center">Submitted</th>
        <th style="padding:10px 12px;text-align:center">Approved</th>
        <th style="padding:10px 12px;text-align:center">Pending</th>
        <th style="padding:10px 12px;text-align:center">Approval %</th>
        <th style="padding:10px 12px;text-align:center">Follow-up Sent</th>
        <th style="padding:10px 12px;text-align:center">No Response 7+ Days</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""

st.markdown(dept_table_html(filtered_cr), unsafe_allow_html=True)


# ─── PANEL 3: Issue Breakdown ────────────────────────────────────────────────
st.markdown("""
<div class="sec">
  <h2>Panel 3: Issue Breakdown</h2>
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

SHORT = {
    "Missing data owner name":                                                    "Missing data owner name",
    "Description missing or too short (<20 chars)":                               "Description missing / too short",
    "Record count missing (not a live API dataset)":                               "Record count missing",
    "DPDP inconsistency":                                                          "DPDP inconsistency",
    "Classification blank or invalid (must be Public/Restricted/Confidential)":    "Classification blank / invalid",
    "Invalid last_updated date format":                                            "Invalid last_updated date",
    "Invalid submitted_on date format":                                            "Invalid submitted_on date",
}

if issue_counts:
    issue_df = pd.DataFrame(
        sorted(issue_counts.items(), key=lambda x: x[1]),
        columns=["Issue Type", "Count"],
    )
    issue_df["Label"] = issue_df["Issue Type"].map(lambda x: SHORT.get(x, x))

    chart_col, gap, table_col = st.columns([3, 0.2, 2])
    with chart_col:
        fig_bar = px.bar(
            issue_df, x="Count", y="Label", orientation="h",
            color="Count",
            color_continuous_scale=["#93c5fd", "#2563a8"],
            text="Count",
        )
        fig_bar.update_layout(
            height=300,
            margin=dict(t=10, b=10, l=0, r=40),
            xaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9", tickfont_size=11),
            yaxis=dict(title="", showgrid=False, tickfont_size=12),
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig_bar.update_traces(textposition="outside", textfont_size=12, marker_line_width=0)
        st.markdown('<div class="panel" style="padding:0.8rem 1rem">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with table_col:
        rows = ""
        for _, r in issue_df.sort_values("Count", ascending=False).iterrows():
            rows += f"""<tr style="border-bottom:1px solid #f1f5f9">
              <td style="padding:8px 10px;font-size:0.81rem;color:#374151">{r['Label']}</td>
              <td style="padding:8px 10px;text-align:center;font-weight:700;font-size:0.9rem;color:#2563a8">{int(r['Count'])}</td>
            </tr>"""
        st.markdown(f"""<div class="panel">
        <table style="width:100%;border-collapse:collapse">
          <thead><tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0">
            <th style="padding:9px 10px;text-align:left;font-size:0.76rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.05em">Issue Type</th>
            <th style="padding:9px 10px;text-align:center;font-size:0.76rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.05em">Count</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table></div>""", unsafe_allow_html=True)


# ─── PANEL 4: DPDP Flag Tracker ──────────────────────────────────────────────
st.markdown("""
<div class="sec" style="border-left-color:#7c3aed">
  <h2>Panel 4: DPDP Flag Tracker</h2>
  <p>All datasets containing personal data — classification and steward assignment status</p>
</div>
""", unsafe_allow_html=True)

personal = submissions[submissions["dpdp_personal_data"] == "Yes"].copy()
personal["cls_ok"] = personal["data_classification"].isin(["Restricted", "Confidential"])
personal["swd_ok"] = personal["data_steward_assigned"] == "Yes"
personal["ok"]     = personal["cls_ok"] & personal["swd_ok"]

def dpdp_table_html(df):
    rows = ""
    for _, r in df.iterrows():
        bg      = "#f0fdf4" if r["ok"] else "#fff1f2"
        cls_b   = '<span class="bg">OK</span>' if r["cls_ok"] else '<span class="br">Non-compliant</span>'
        swd_b   = '<span class="bg">Assigned</span>' if r["swd_ok"] else '<span class="br">Missing</span>'
        ok_b    = '<span class="bg">Compliant</span>' if r["ok"] else '<span class="br">Not Compliant</span>'
        cls_val = str(r["data_classification"]) if pd.notna(r["data_classification"]) else "—"
        rows += f"""<tr style="background:{bg};border-bottom:1px solid #e2e8f0">
          <td style="padding:9px 12px;font-weight:600;font-size:0.81rem">{r['submission_id']}</td>
          <td style="padding:9px 12px;font-size:0.81rem">{r['department']}</td>
          <td style="padding:9px 12px;font-size:0.81rem">{r['dataset_title']}</td>
          <td style="padding:9px 12px;text-align:center;font-size:0.81rem">{cls_val}</td>
          <td style="padding:9px 12px;text-align:center">{cls_b}</td>
          <td style="padding:9px 12px;text-align:center">{swd_b}</td>
          <td style="padding:9px 12px;text-align:center">{ok_b}</td>
        </tr>"""
    return f"""<div class="panel" style="padding:0;overflow:hidden">
    <table style="width:100%;border-collapse:collapse;font-size:0.83rem">
      <thead><tr style="background:#5b21b6;color:white">
        <th style="padding:10px 12px;text-align:left">ID</th>
        <th style="padding:10px 12px;text-align:left">Department</th>
        <th style="padding:10px 12px;text-align:left">Dataset</th>
        <th style="padding:10px 12px;text-align:center">Classification</th>
        <th style="padding:10px 12px;text-align:center">Classification OK</th>
        <th style="padding:10px 12px;text-align:center">Steward Assigned</th>
        <th style="padding:10px 12px;text-align:center">DPDP Status</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""

st.markdown(dpdp_table_html(personal), unsafe_allow_html=True)

st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
nc = (~personal["ok"]).sum()
co = personal["ok"].sum()
a1, a2 = st.columns(2)
with a1:
    st.markdown(f'<div style="background:#fee2e2;border-radius:8px;padding:0.7rem 1.1rem;color:#991b1b;font-weight:600;font-size:0.85rem">&#9888; {nc} dataset(s) with personal data are NOT fully DPDP compliant</div>', unsafe_allow_html=True)
with a2:
    st.markdown(f'<div style="background:#dcfce7;border-radius:8px;padding:0.7rem 1.1rem;color:#166534;font-weight:600;font-size:0.85rem">&#10003; {co} dataset(s) with personal data are fully DPDP compliant</div>', unsafe_allow_html=True)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  State Data Authority (SDA), Uttar Pradesh &nbsp;&bull;&nbsp; Metadata Platform &nbsp;&bull;&nbsp; April 2026 Batch
</div>
""", unsafe_allow_html=True)
