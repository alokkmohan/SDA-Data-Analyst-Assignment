# SDA Data Analyst Assignment
**State Data Authority (SDA), Uttar Pradesh: Metadata Platform Quality Review**

## Live Dashboard

**[View Dashboard →](https://sda-data-analyst-assignment.streamlit.app)**

> The dashboard loads from the processed CSV files in `data/processed/` and shows real-time compliance metrics for the April 2026 batch.

---

## Project Structure

```
sda-metadata-review/
├── src/
│   ├── quality_review.py       # Section 1: metadata quality checks
│   ├── compliance_analysis.py  # Section 2: department-level compliance analysis
│   └── dashboard.py            # Section 3: Streamlit compliance dashboard
├── data/
│   ├── metadata_submissions.csv
│   ├── compliance_tracker.csv
│   └── processed/
│       ├── quality_flags.csv       # submissions with issues
│       ├── clean_submissions.csv   # submissions that pass all checks
│       ├── review_summary.txt      # summary report
│       └── compliance_report.csv  # department-level compliance table
├── outputs/
│   ├── monthly_progress_report.md
│   └── followup_email_draft.md
├── README.md
└── requirements.txt
```

---

## How to Run (Fresh Setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the quality review (generates data/processed/ outputs)
python src/quality_review.py

# 3. Run compliance analysis (generates compliance_report.csv)
python src/compliance_analysis.py

# 4. Run the dashboard locally
streamlit run src/dashboard.py
```

The dashboard will open at `http://localhost:8501`.

---

## Data Quality Decisions and Assumptions

| Decision | Rationale |
|----------|-----------|
| Record count blank is acceptable for live API datasets | If `formats` contains "API", blank record_count is valid — the count changes continuously |
| Submission date checked separately from last_updated | Both `submitted_on` and `last_updated` must be YYYY-MM-DD; they represent different events |
| Classification blank treated same as invalid | A blank classification cannot be verified against DPDP requirements |
| META-006 treated as clean | The raw data shows a valid data_owner_name; the tracker's earlier flag reflects the pre-revision state, and revised_submission_received = Yes confirms the fix |
| DPDP check: Public + personal data = non-compliant | The DPDP Act requires personal data to be Restricted or Confidential |

---

## What I Would Add with More Time

- Automated email sending via SMTP when follow-up deadline passes
- Historical tracking across multiple submission batches (trend charts)
- Per-submission issue drill-down in the dashboard
- Department login so stewards can see only their own submissions
- Export to PDF from the dashboard for offline reporting
