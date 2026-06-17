import pandas as pd
from pathlib import Path
from datetime import date

DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

REVIEW_CUTOFF = date(2026, 4, 25)
NO_RESPONSE_DAYS = 7


def main():
    tracker = pd.read_csv(DATA_DIR / "compliance_tracker.csv")
    submissions = pd.read_csv(DATA_DIR / "metadata_submissions.csv")

    tracker["final_status"] = tracker["final_status"].str.strip()
    tracker["follow_up_date"] = pd.to_datetime(tracker["follow_up_date"], errors="coerce")

    # ------------------------------------------------------------------ #
    # 2.1  Department-Level Compliance Table
    # ------------------------------------------------------------------ #
    dept_rows = []
    for dept, grp in tracker.groupby("department"):
        submitted = len(grp)
        approved = (grp["final_status"] == "Approved").sum()
        pending = grp["final_status"].str.startswith("Pending", na=False).sum()
        approval_pct = round(approved / submitted * 100, 1) if submitted else 0

        pending_grp = grp[grp["final_status"].str.startswith("Pending", na=False)]

        # Follow-up sent for all pending?
        if pending == 0:
            followup_status = "N/A"
        elif (pending_grp["follow_up_sent"] == "Yes").all():
            followup_status = "Yes"
        elif (pending_grp["follow_up_sent"] == "Yes").any():
            followup_status = "Partial"
        else:
            followup_status = "No"

        # Any pending with no response after 7+ days?
        no_response_flag = False
        for _, row in pending_grp.iterrows():
            if row["follow_up_sent"] == "Yes" and row["department_responded"] == "No":
                fu_date = row["follow_up_date"]
                if pd.notna(fu_date):
                    days_waiting = (REVIEW_CUTOFF - fu_date.date()).days
                    if days_waiting >= NO_RESPONSE_DAYS:
                        no_response_flag = True
                        break

        dept_rows.append({
            "department": dept,
            "datasets_submitted": submitted,
            "approved": approved,
            "pending": pending,
            "approval_pct": approval_pct,
            "followup_sent_for_all_pending": followup_status,
            "no_response_7plus_days": "Yes" if no_response_flag else "No",
        })

    dept_df = pd.DataFrame(dept_rows).sort_values("approval_pct")
    print("\n=== 2.1 Department-Level Compliance Table ===")
    print(dept_df.to_string(index=False))

    # ------------------------------------------------------------------ #
    # 2.2  Issue Type Analysis
    # ------------------------------------------------------------------ #
    quality_flags = pd.read_csv(PROCESSED_DIR / "quality_flags.csv")
    pending_ids = set(tracker[tracker["final_status"].str.startswith("Pending", na=False)]["submission_id"])
    pending_flags = quality_flags[quality_flags["submission_id"].isin(pending_ids)]

    issue_counts = {}
    for issues_str in pending_flags["issues"].dropna():
        for issue in issues_str.split("; "):
            key = issue.split(":")[0].strip()
            issue_counts[key] = issue_counts.get(key, 0) + 1

    issue_df = pd.DataFrame(
        sorted(issue_counts.items(), key=lambda x: -x[1]),
        columns=["issue_type", "count"]
    )
    print("\n=== 2.2 Issue Type Analysis (Pending Submissions) ===")
    print(issue_df.to_string(index=False))

    # Non-response rate per issue
    non_response_by_issue = {}
    for _, row in pending_flags.iterrows():
        tracker_row = tracker[tracker["submission_id"] == row["submission_id"]]
        if tracker_row.empty:
            continue
        responded = tracker_row.iloc[0]["department_responded"]
        for issue in str(row["issues"]).split("; "):
            key = issue.split(":")[0].strip()
            if key not in non_response_by_issue:
                non_response_by_issue[key] = {"total": 0, "no_response": 0}
            non_response_by_issue[key]["total"] += 1
            if responded == "No":
                non_response_by_issue[key]["no_response"] += 1

    nr_rows = []
    for issue, counts in non_response_by_issue.items():
        rate = round(counts["no_response"] / counts["total"] * 100, 1) if counts["total"] else 0
        nr_rows.append({"issue_type": issue, "non_response_rate_pct": rate})
    nr_df = pd.DataFrame(nr_rows).sort_values("non_response_rate_pct", ascending=False)
    print("\n  Non-Response Rate by Issue Type:")
    print(nr_df.to_string(index=False))

    # ------------------------------------------------------------------ #
    # 2.3  DPDP Compliance Flag
    # ------------------------------------------------------------------ #
    personal_data = submissions[submissions["dpdp_personal_data"] == "Yes"].copy()
    personal_data["classification_ok"] = personal_data["data_classification"].isin(["Restricted", "Confidential"])
    personal_data["steward_ok"] = personal_data["data_steward_assigned"] == "Yes"
    personal_data["fully_compliant"] = personal_data["classification_ok"] & personal_data["steward_ok"]

    non_compliant = personal_data[~personal_data["fully_compliant"]][[
        "submission_id", "department", "dataset_title",
        "data_classification", "data_steward_assigned",
        "classification_ok", "steward_ok"
    ]]

    print("\n=== 2.3 DPDP Non-Compliant Datasets ===")
    if non_compliant.empty:
        print("All datasets with personal data are fully compliant.")
    else:
        print(non_compliant.to_string(index=False))

    # ------------------------------------------------------------------ #
    # 2.4  Save compliance_report.csv
    # ------------------------------------------------------------------ #
    dept_df.to_csv(PROCESSED_DIR / "compliance_report.csv", index=False)
    print(f"\nCompliance report saved to {PROCESSED_DIR / 'compliance_report.csv'}")


if __name__ == "__main__":
    main()
