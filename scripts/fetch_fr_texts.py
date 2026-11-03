"""Fetch Federal Register full text (plain text wrapped in HTML) for each unique
executive order number in the FR API download. Polite, public, no sign in.
Saves one .txt per EO number plus a word count index. Failures are logged, not faked."""
import json, os, re, time, urllib.request, urllib.error
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
OUT = os.path.join(RAW, "fr_texts")
os.makedirs(OUT, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (educational research project)"}
def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")
def clean(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t
fr = json.load(open(os.path.join(RAW, "federal_register.json")))
seen = {}
for r in fr:
    eo = r.get("executive_order_number")
    if not eo:
        continue
    doc = r.get("document_number")
    if not doc or str(eo) in seen:
        continue
    seen[str(eo)] = doc
index = {}
failed = []
for i, (eo, doc) in enumerate(sorted(seen.items(), key=lambda x: int(re.match(r"(\d+)", x[0]).group(1)))):
    path = os.path.join(OUT, f"eo_{eo}.txt")
    if os.path.exists(path):
        txt = open(path, encoding="utf-8").read()
    else:
        # document_number may be like 2026-03832; raw text path needs publication date, derive from html_url
        rec = next(r for r in fr if r.get("document_number") == doc)
        html_url = rec.get("html_url", "")
        m = re.search(r"/documents/(\d{4})/(\d{2})/(\d{2})/", html_url)
        if not m:
            failed.append((eo, doc, "no date in html_url"))
            continue
        url = f"https://www.federalregister.gov/documents/full_text/text/{m.group(1)}/{m.group(2)}/{m.group(3)}/{doc}.txt"
        try:
            txt = clean(fetch(url))
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
        except Exception as e:
            failed.append((eo, doc, str(e)))
            continue
        time.sleep(0.15)
    index[eo] = len(txt.split())
    if i % 200 == 0:
        print(f"{i} of {len(seen)} EO {eo} words {index[eo]}", flush=True)
json.dump({"word_counts": index, "failed": failed, "n_unique_eo": len(seen)}, open(os.path.join(RAW, "fr_text_index.json"), "w"), indent=1)
print("done unique:", len(seen), "with text:", len(index), "failed:", len(failed))
