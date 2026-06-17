# Monthly Progress Report — Metadata Registry
**To:** Data Governance Lead, State Data Authority (SDA), Uttar Pradesh
**From:** Data Analyst, SDA Metadata Platform Team
**Date:** 25 April 2026
**Subject:** Metadata Submission Status Report — April 2026 Batch

---

## 1. Overall Registration Progress

As of 25 April 2026, the SDA Metadata Platform has received **25 submissions** from 20 departments across Uttar Pradesh.

| Status   | Count | Percentage |
|----------|-------|------------|
| Approved | 13    | 52%        |
| Pending  | 12    | 48%        |

Of the 12 pending submissions, all have received at least one follow-up from the SDA team. Nine departments have not yet responded despite being contacted more than 7 days ago.

---

## 2. Top 3 Compliance Issues

**Issue 1: Missing Data Owner Name (4 submissions)**
This is the most frequently occurring problem. Submissions from the Energy Department (META-010), Home Department (META-013), Basic Education Department (META-002), and Labour Department (META-024) were all submitted without identifying who is responsible for the dataset. This likely reflects a gap in the submission form guidance — departments may not understand that a named individual is required, not just a designation or office. None of these four departments have responded to follow-up.

**Issue 2: Invalid Date Formats (2 submissions)**
Two submissions used non-standard date formats — META-010 used DD-MM-YYYY and META-015 used MM/DD/YYYY — instead of the required YYYY-MM-DD format. This suggests that departments are entering dates manually without a validated input field. A form-level date picker would eliminate this class of error entirely.

**Issue 3: Classification Blank or DPDP Inconsistency (4 submissions across 2 issue types)**
Four submissions either left the data_classification field blank (META-007, META-020) or classified a dataset containing personal data as "Public" (META-005, META-015). Under the DPDP Act, any dataset with personal data must be classified as Restricted or Confidential. This is a substantive compliance risk — not just a form error — and requires direct engagement with the concerned departments.

---

## 3. Departments with Unresolved Pending Items

The following departments have pending submissions with no response after 7 or more days:

| Department               | Issue(s)                              | Follow-up Sent | Days Waiting |
|--------------------------|---------------------------------------|----------------|--------------|
| Energy Department        | Missing data owner; invalid date      | 13 April 2026  | 12 days      |
| Home Department          | Missing data owner; steward not assigned | 15 April 2026 | 10 days    |
| Basic Education Dept.    | Missing data owner (META-002)         | 9 April 2026   | 16 days      |
| Food & Civil Supplies    | Classification blank; DPDP issue      | 18 April 2026  | 7 days       |
| Women & Child Devt.      | Invalid date; DPDP inconsistency      | 16 April 2026  | 9 days       |
| Health Department        | Personal data classified as Public    | 10 April 2026  | 15 days      |

---

## 4. Recommended Actions (Next Two Weeks)

**Action 1: Second follow-up to non-responding departments**
Send a second, more formal follow-up to the Energy Department, Home Department, Basic Education Department, and Health Department. These have the oldest outstanding items and the most consequential issues (DPDP compliance, missing owner). Set a revised submission deadline of 5 May 2026.

**Action 2: Add a validated date field and mandatory data owner field to the submission form**
The two most common error types — missing owner name and wrong date format — are preventable at the form level. Working with the platform team to add input validation will reduce these errors in the next submission cycle.

**Action 3: Issue a guidance note on DPDP classification requirements**
Four submissions reflect a misunderstanding of when Restricted or Confidential classification is required. A one-page guidance note, shared with all department data stewards before the next submission cycle, would reduce this risk and signal the SDA's expectations clearly.
