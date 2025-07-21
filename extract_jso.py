import json
from playwright.sync_api import sync_playwright

URL = "https://jacksonvilleso.mycusthelp.com/WEBAPP/_rs/(S(dddnslbkyvdto3ye4snf1law))/OpenRecordsSummary.aspx?sSessionID="

# Maximum number of pages to scrape (set to None to scrape all)
MAX_PAGES = 3


def scrape_page(page):
    records = []
    rows = page.locator("#gridView_DXMainTable > tbody > tr")
    count = rows.count()
    for i in range(1, count):
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
        browser = p.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.goto(URL)
        page.wait_for_selector("#gridView_DXMainTable")
        pages_scraped = 0
        while True:
            data.extend(scrape_page(page))
            pages_scraped += 1
            if MAX_PAGES and pages_scraped >= MAX_PAGES:
                break
            next_btn = page.locator("#gridView_DXPagerBottom_PBN")
            classes = next_btn.get_attribute("class") or ""
            if "dxp-disabledButton" in classes:
                break
            next_btn.click()
            page.wait_for_timeout(1000)
        browser.close()
    with open("jso_records_requests.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
