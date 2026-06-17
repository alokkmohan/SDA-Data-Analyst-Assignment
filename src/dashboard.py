import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

st.set_page_config(
    page_title="SDA UP Metadata Compliance Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 SDA Uttar Pradesh — Metadata Compliance Dashboard")
st.caption("State Data Authority | Data Governance Lead View | As of 25 April 2026")


@st.cache_data
def load_data():
    submissions = pd.read_csv(DATA_DIR / "metadata_submissions.csv")
    tracker = pd.read_csv(DATA_DIR / "compliance_tracker.csv")
    tracker["final_status"] = tracker["final_status"].str.strip()
    quality_flags = pd.read_csv(PROCESSED_DIR / "quality_flags.csv")
    compliance_report = pd.read_csv(PROCESSED_DIR / "compliance_report.csv")
    return submissions, tracker, quality_flags, compliance_report


submissions, tracker, quality_flags, compliance_report = load_data()

total = len(tracker)
approved = (tracker["final_status"] == "Approved").sum()
pending = tracker["final_status"].str.startswith("Pending", na=False).sum()
dpdp_issues = len(
    submissions[
        (submissions["dpdp_personal_data"] == "Yes") &
        (~submissions["data_classification"].isin(["Restricted", "Confidential"]))
    ]
)

# ------------------------------------------------------------------ #
# Panel 1: Overview
# ------------------------------------------------------------------ #
st.header("Panel 1: Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Submissions", total)
col2.metric("Approved", f"{approved} ({round(approved/total*100)}%)")
col3.metric("Pending", f"{pending} ({round(pending/total*100)}%)")
col4.metric("DPDP Flag Issues", dpdp_issues)

st.divider()

# ------------------------------------------------------------------ #
# Panel 2: Department Status
# ------------------------------------------------------------------ #
st.header("Panel 2: Department Status")

dept_display = compliance_report.rename(columns={
    "department": "Department",
    "datasets_submitted": "Submitted",
    "approved": "Approved",
    "pending": "Pending",
    "approval_pct": "Approval %",
    "followup_sent_for_all_pending": "Follow-up Sent",
    "no_response_7plus_days": "No Response 7+ Days",
})

dept_filter = st.multiselect(
    "Filter by Department",
    options=dept_display["Department"].tolist(),
    default=dept_display["Department"].tolist(),
)
filtered = dept_display[dept_display["Department"].isin(dept_filter)]

def highlight_row(row):
    if row["Approval %"] == 0:
        return ["background-color: #ffe0e0"] * len(row)
    elif row["Approval %"] == 100:
        return ["background-color: #e0ffe0"] * len(row)
    else:
        return ["background-color: #fff8e0"] * len(row)

st.dataframe(
    filtered.style.apply(highlight_row, axis=1),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ------------------------------------------------------------------ #
# Panel 3: Issue Breakdown
# ------------------------------------------------------------------ #
st.header("Panel 3: Issue Breakdown (Pending Submissions)")

pending_ids = set(tracker[tracker["final_status"].str.startswith("Pending", na=False)]["submission_id"])
pending_flags = quality_flags[quality_flags["submission_id"].isin(pending_ids)]

issue_counts = {}
for issues_str in pending_flags["issues"].dropna():
    for issue in issues_str.split("; "):
        key = issue.split(":")[0].strip()
        issue_counts[key] = issue_counts.get(key, 0) + 1

if issue_counts:
    issue_df = pd.DataFrame(
        sorted(issue_counts.items(), key=lambda x: -x[1]),
        columns=["Issue Type", "Count"],
    )
    st.bar_chart(issue_df.set_index("Issue Type"))
    st.dataframe(issue_df, use_container_width=True, hide_index=True)
else:
    st.success("No pending issues found.")

st.divider()

# ------------------------------------------------------------------ #
# Panel 4: DPDP Flag Tracker
# ------------------------------------------------------------------ #
st.header("Panel 4: DPDP Flag Tracker (Personal Data Submissions)")

personal = submissions[submissions["dpdp_personal_data"] == "Yes"].copy()
personal["Classification OK"] = personal["data_classification"].isin(["Restricted", "Confidential"])
personal["Steward Assigned"] = personal["data_steward_assigned"] == "Yes"
personal["Fully Compliant"] = personal["Classification OK"] & personal["Steward Assigned"]

dpdp_display = personal[[
    "submission_id", "department", "dataset_title",
    "data_classification", "Classification OK", "Steward Assigned", "Fully Compliant"
]].rename(columns={
    "submission_id": "ID",
    "department": "Department",
    "dataset_title": "Dataset",
    "data_classification": "Classification",
})

def highlight_dpdp(row):
    if not row["Fully Compliant"]:
        return ["background-color: #ffe0e0"] * len(row)
    return ["background-color: #e0ffe0"] * len(row)

st.dataframe(
    dpdp_display.style.apply(highlight_dpdp, axis=1),
    use_container_width=True,
    hide_index=True,
)

non_compliant_count = (~personal["Fully Compliant"]).sum()
if non_compliant_count:
    st.warning(f"⚠️ {non_compliant_count} dataset(s) with personal data are NOT fully DPDP compliant.")
else:
    st.success("All datasets with personal data are DPDP compliant.")
