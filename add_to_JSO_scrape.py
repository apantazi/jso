import json
import os
from typing import List, Optional
from playwright.sync_api import sync_playwright

URL = "https://jacksonvilleso.mycusthelp.com/WEBAPP/_rs/(S(dddnslbkyvdto3ye4snf1law))/OpenRecordsSummary.aspx?sSessionID="

# Maximum number of pages to scrape (set to None to scrape all)
MAX_PAGES = 10

OUT_FILE = "jso_records_requests.json"

def load_existing_data(filename: str):
    """Load existing JSON data if present and return the list and most recent ref."""
    if not os.path.exists(filename):
        return [], None
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return [], None
    if isinstance(data, list) and data:
        latest_ref = data[0].get("Reference No")
    else:
        latest_ref = None
    return data if isinstance(data, list) else [], latest_ref

def scrape_page(page) -> List[dict]:
    records = []
    rows = page.locator("#gridView_DXMainTable > tbody > tr[class*='dxgvDataRow']")
    count = rows.count()
    for i in range(count):
        cells = rows.nth(i).locator("td")
        if cells.count() < 5:
            continue
        ref = cells.nth(0).inner_text().strip()
        if not ref:
            continue
        status = cells.nth(1).inner_text().strip()
        desc = cells.nth(2).inner_text().strip()
        close = cells.nth(3).inner_text().strip()
        link = cells.nth(4).locator("a")
        files_text = link.inner_text().strip() if link.count() else cells.nth(4).inner_text().strip()
        onclick = link.get_attribute("onclick") if link.count() else None
        records.append({
            "Reference No": ref,
            "Status": status,
            "Public Record Request": desc,
            "Close Date": close,
            "Files": files_text,
            "FileLinkOnClick": onclick,
        })
    return records

def main():
    existing_data, latest_ref = load_existing_data(OUT_FILE)
    new_data: List[dict] = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        print("Navigating to page...")
        page.goto(URL)
        page.wait_for_selector("#gridView_DXMainTable")
        pages_scraped = 0
        found_latest = False
        while True:
            print(f"Scraping page {pages_scraped + 1}")
            page_data = scrape_page(page)
            print(f"Found {len(page_data)} records on page {pages_scraped + 1}")
            for record in page_data:
                if latest_ref and record.get("Reference No") == latest_ref:
                    found_latest = True
                    break
                new_data.append(record)
            if found_latest:
                print("Reached previously scraped record. Stopping.")
                break
            pages_scraped += 1
            if MAX_PAGES and pages_scraped >= MAX_PAGES:
                print("Max pages reached, stopping scrape.")
                break
            next_btn = page.locator("#gridView_DXPagerBottom_PBN")
            classes = next_btn.get_attribute("class") or ""
            if "dxp-disabledButton" in classes:
                print("No more pages, finished scraping.")
                break
            if page_data:
                first_ref = page_data[0]["Reference No"]
                if hasattr(main, "last_first_ref") and first_ref == main.last_first_ref:
                    print("Same page detected—probably at last page. Exiting.")
                    break
                main.last_first_ref = first_ref
            else:
                print("No data, stopping.")
                break
            if pages_scraped > 1500:
                print("Hard stop at 1500 pages.")
                break
            next_btn.click()
            page.wait_for_function(
                "(prev) => document.querySelector('#gridView_DXMainTable > tbody > tr.dxgvDataRow_Moderno td').innerText.trim() !== prev",
                arg=first_ref,
            )
            page.wait_for_timeout(1000)
        browser.close()

    if new_data:
        combined_data = new_data + existing_data
    else:
        combined_data = existing_data

    print(f"Total new records scraped: {len(new_data)}")
    with open(OUT_FILE, "w") as f:
        json.dump(combined_data, f, indent=2)
    abs_path = os.path.abspath(OUT_FILE)
    print(f"JSON file written: {abs_path}")

if __name__ == "__main__":
    main()
