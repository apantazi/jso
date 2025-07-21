# AGENTS.md

## Purpose of this Repository

This repository exists solely to support AI agent tasks focused on scraping and extracting structured data from the Jacksonville Sheriff's Office (JSO) public records portal.

**Target Site:**
https://jacksonvilleso.mycusthelp.com/WEBAPP/_rs/(S(dddnslbkyvdto3ye4snf1law))/OpenRecordsSummary.aspx?sSessionID=

---

## Agent Task Instructions

### Objective:
Extract all "Published Media Requests" from the public records portal, including the following fields:
- **Reference Number**
- **Status**
- **Public Record Request** (description)
- **Close Date**
- **Files** (including any URLs referenced)

---

### Expected Outputs:
1. A Python script named `extract_jso.py`  
   - Uses Playwright (or another headless browser) to automate extraction.
   - Saves the data locally to a JSON file.

2. A JSON file named `jso_records_requests.json`  
   - Contains the extracted data with as much detail as reasonably available.

---

## Submission Guidelines for Agents
- Submit a Pull Request with the new or modified files.
- Include a clear commit message summarizing what you did.
- If applicable, note any limitations, skipped entries, or failed scrapes in the PR description.

---

## Environment Configuration
- Internet access: **Unrestricted**
- Python dependencies may be installed as needed (Playwright is recommended).

---

## Constraints & Considerations
- Be efficient with requests; avoid overloading the target server.
- Ensure data accuracy through validation if possible.
- No need to create any UI; this is purely a data extraction repository.

---

## Why This Matters
This repository helps support journalism and public accountability by making difficult-to-access government records easier to analyze, track, and archive.
