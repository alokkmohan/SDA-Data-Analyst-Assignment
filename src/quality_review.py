import pandas as pd
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

VALID_CLASSIFICATIONS = {"Public", "Restricted", "Confidential"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_live_api(row):
    formats = str(row.get("formats", ""))
    return "API" in formats.upper()


def check_submission(row):
    issues = []

    # 1. Data owner present
    if pd.isna(row["data_owner_name"]) or str(row["data_owner_name"]).strip() == "":
        issues.append("Missing data owner name")

    # 2. Description adequate
    desc = str(row["description"]).strip() if not pd.isna(row["description"]) else ""
    if desc == "" or len(desc) < 20:
        issues.append("Description missing or too short (<20 chars)")

    # 3. Classification present and valid
    classification = str(row["data_classification"]).strip() if not pd.isna(row["data_classification"]) else ""
    if classification not in VALID_CLASSIFICATIONS:
        issues.append("Classification blank or invalid (must be Public/Restricted/Confidential)")

    # 4. DPDP flag consistent
    dpdp = str(row["dpdp_personal_data"]).strip()
    if dpdp == "Yes" and classification == "Public":
        issues.append("DPDP inconsistency: personal data classified as Public (must be Restricted or Confidential)")

    # 5. last_updated date format valid
    last_updated = str(row["last_updated"]).strip() if not pd.isna(row["last_updated"]) else ""
    if not DATE_PATTERN.match(last_updated):
        issues.append(f"Invalid last_updated date format: '{last_updated}' (expected YYYY-MM-DD)")

    # 6. Record count present (blank OK only for live API datasets)
    record_count = row["record_count"]
    if pd.isna(record_count) or str(record_count).strip() == "":
        if not is_live_api(row):
            issues.append("Record count missing (not a live API dataset)")

    # 7. Submission date format
    submitted_on = str(row["submitted_on"]).strip() if not pd.isna(row["submitted_on"]) else ""
    if not DATE_PATTERN.match(submitted_on):
        issues.append(f"Invalid submitted_on date format: '{submitted_on}' (expected YYYY-MM-DD)")

    return issues


def main():
    df = pd.read_csv(DATA_DIR / "metadata_submissions.csv")

    flagged_rows = []
    clean_rows = []

    for _, row in df.iterrows():
        issues = check_submission(row)
        if issues:
            flagged_rows.append({
                "submission_id": row["submission_id"],
                "department": row["department"],
                "dataset_title": row["dataset_title"],
                "issues": "; ".join(issues)
            })
        else:
            clean_rows.append(row)

    quality_flags = pd.DataFrame(flagged_rows)
    clean_submissions = pd.DataFrame(clean_rows)

    quality_flags.to_csv(PROCESSED_DIR / "quality_flags.csv", index=False)
    clean_submissions.to_csv(PROCESSED_DIR / "clean_submissions.csv", index=False)

    # Cross-check against compliance tracker
    tracker = pd.read_csv(DATA_DIR / "compliance_tracker.csv")
    tracker["final_status"] = tracker["final_status"].str.strip()

    flagged_ids = set(quality_flags["submission_id"])
    tracker_approved = set(tracker[tracker["final_status"] == "Approved"]["submission_id"])
    tracker_pending = set(tracker[tracker["final_status"].str.startswith("Pending", na=False)]["submission_id"])

    mis_approved = flagged_ids & tracker_approved
    correctly_approved = tracker_approved - flagged_ids
    correctly_pending = flagged_ids & tracker_pending
    potentially_ready = tracker_pending - flagged_ids

    total = len(df)
    passing = len(clean_rows)
    failing = len(flagged_rows)

    issue_counts = {}
    for row in flagged_rows:
        for issue in row["issues"].split("; "):
            key = issue.split(":")[0].strip()
            issue_counts[key] = issue_counts.get(key, 0) + 1

    sorted_issues = sorted(issue_counts.items(), key=lambda x: -x[1])

    summary_lines = [
        "=== SDA Metadata Quality Review Summary ===",
        f"Report date        : 25 April 2026",
        f"Total submissions  : {total}",
        f"Pass all checks    : {passing}",
        f"Fail one or more   : {failing}",
        "",
        "--- Most Common Issues ---",
    ]
    for issue, count in sorted_issues:
        summary_lines.append(f"  {issue:<55}: {count}")

    summary_lines += [
        "",
        "--- Cross-check with Compliance Tracker ---",
        f"Correctly Approved  (clean + tracker=Approved)  : {len(correctly_approved)}",
        f"Correctly Pending   (flagged + tracker=Pending) : {len(correctly_pending)}",
        f"Potentially Mis-Approved (flagged + tracker=Approved): {len(mis_approved)}",
        f"Potentially Ready to Approve (clean + tracker=Pending): {len(potentially_ready)}",
    ]

    if mis_approved:
        summary_lines.append(f"\nMis-Approved IDs: {', '.join(sorted(mis_approved))}")
    if potentially_ready:
        summary_lines.append(f"Ready to Approve IDs: {', '.join(sorted(potentially_ready))}")

    summary_text = "\n".join(summary_lines)
    print(summary_text)

    with open(PROCESSED_DIR / "review_summary.txt", "w") as f:
        f.write(summary_text)

    print(f"\nOutputs saved to {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
