"""Download row level sources. No sign in, public pages and public API only.
APP guidebook listing: 218 pages, 50 rows per page, newest first.
Federal Register API v1 documents endpoint, presidential_document_type=executive_order.
"""
import json, re, time, urllib.request, urllib.parse, os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
os.makedirs(RAW, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (educational research project; contact via project README)"}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")

def app_scrape():
    rows = []
    for page in range(0, 218):
        html = fetch(f"https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/executive-orders-beginning-with-jq-adams?page={page}")
        cells = re.findall(r"<td[^>]*>(.*?)</td>", html, flags=re.S)
        clean = []
        for c in cells:
            # keep link href for the title cell if present
            m = re.search(r'href="([^"]+)"', c)
            text = re.sub(r"<[^>]+>", " ", c).strip()
            text = re.sub(r"\s+", " ", text)
            clean.append((text, m.group(1) if m else ""))
        for i in range(0, len(clean) - 2, 3):
            pres, date, title = clean[i][0], clean[i+1][0], clean[i+2][0]
            href = clean[i+2][1]
            if pres and date and title:
                rows.append({"president_app": pres, "date_app": date, "title_app": title, "app_url": ("https://www.presidency.ucsb.edu" + href) if href.startswith("/") else href, "app_page": page})
        if page % 20 == 0:
            print(f"APP page {page} rows so far {len(rows)}", flush=True)
        time.sleep(0.25)
    with open(os.path.join(RAW, "app_guidebook.json"), "w") as f:
        json.dump(rows, f, indent=1)
    print("APP total rows:", len(rows))
    return rows

def fr_fetch():
    base = ("https://www.federalregister.gov/api/v1/documents.json?conditions%5Bpresidential_document_type%5D=executive_order"
            "&conditions%5Btype%5D=PRESDOCU&fields%5B%5D=executive_order_number&fields%5B%5D=title&fields%5B%5D=signing_date"
            "&fields%5B%5D=publication_date&fields%5B%5D=abstract&fields%5B%5D=disposition_notes&fields%5B%5D=html_url"
            "&fields%5B%5D=pdf_url&fields%5B%5D=document_number&fields%5B%5D=citation&order=executive_order_number&per_page=1000")
    all_rows = []
    page = 1
    while True:
        d = json.loads(fetch(base + f"&page={page}"))
        res = d.get("results", [])
        if not res:
            break
        all_rows.extend(res)
        print(f"FR page {page} rows {len(res)} total {len(all_rows)} api_count {d.get('count')}", flush=True)
        if len(res) < 1000:
            break
        page += 1
        time.sleep(0.3)
    with open(os.path.join(RAW, "federal_register.json"), "w") as f:
        json.dump(all_rows, f, indent=1)
    print("FR total records:", len(all_rows))
    return all_rows

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "app"):
        app_scrape()
    if which in ("all", "fr"):
        fr_fetch()
