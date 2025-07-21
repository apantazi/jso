import json
from playwright.sync_api import sync_playwright
import os

URL = "https://jacksonvilleso.mycusthelp.com/WEBAPP/_rs/(S(dddnslbkyvdto3ye4snf1law))/OpenRecordsSummary.aspx?sSessionID="

# Maximum number of pages to scrape (set to None to scrape all)
MAX_PAGES = 10

def scrape_page(page):
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
    data = []
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        print("Navigating to page...")
        page.goto(URL)
        page.wait_for_selector("#gridView_DXMainTable")
        pages_scraped = 0
        while True:
            print(f"Scraping page {pages_scraped + 1}")
            page_data = scrape_page(page)
            print(f"Found {len(page_data)} records on page {pages_scraped + 1}")
            data.extend(page_data)
            pages_scraped += 1
            if MAX_PAGES and pages_scraped >= MAX_PAGES:
                print("Max pages reached, stopping scrape.")
                break
            next_btn = page.locator("#gridView_DXPagerBottom_PBN")
            classes = next_btn.get_attribute("class") or ""
            if "dxp-disabledButton" in classes:
                print("No more pages, finished scraping.")
                break
            # Track first record to detect repeated pages
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
            # Wait for the table to update by monitoring the first row value
            page.wait_for_function(
                "(prev) => document.querySelector('#gridView_DXMainTable > tbody > tr.dxgvDataRow_Moderno td').innerText.trim() !== prev",
                arg=first_ref,
            )
            page.wait_for_timeout(1000)
        browser.close()
    print(f"Total records scraped: {len(data)}")
    out_file = "jso_records_requests.json"
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)
    # Print the absolute path for certainty
    import os
    abs_path = os.path.abspath(out_file)
    print(f"JSON file written: {abs_path}")


if __name__ == "__main__":
    main()
