"""Build data/processed/executive_orders.csv from the two raw sources.
Rules, in plain words:
1. Start with every APP guidebook row (president as listed, date, title, APP link).
2. Extract an EO number from the APP title when it is there, like Executive Order 14438.
3. Add every Federal Register record that has an EO number. If that number is already
   in the APP rows, keep one row and prefer the Federal Register title, signing date,
   disposition notes, and links, because the Federal Register is the official journal.
4. If an FR number is not in APP, add it as its own row. This is how the recent
   complete series 12890 to 14438 is preserved even where APP listing rows differ.
5. President, party, and term are assigned from the signing date using scripts/presidents.py,
   not from the APP label alone, so Grover Cleveland's two terms stay separate in dates
   even though the name repeats, and Trump first and second terms stay separate.
6. Category comes from scripts/categories.py keyword rules, first match wins.
7. Disposition: parsed from FR disposition_notes when present. Otherwise Unknown.
   A row is marked Revoked if its own disposition notes say Revoked by, Amended if they
   say Amends or Amended by, and so on. This only describes what the notes say, it is
   not a full legal status check for old orders.
8. Text availability: full text if a Federal Register text file was downloaded for that
   EO number, title only otherwise. APP text links exist for many rows but were not
   bulk downloaded, so they are not counted as full text here. That is an honest cut.
"""
import json, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from presidents import TERMS
from categories import categorize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")
os.makedirs(PROC, exist_ok=True)

def parse_app_date(s):
    return pd.to_datetime(s, errors="coerce")

def president_for(date):
    # Assign by the latest term start on or before the signing date. This puts
    # inauguration day orders with the incoming president and avoids double
    # counting the one day overlap between outgoing and incoming terms.
    if pd.isna(date):
        return "", "", ""
    terms = sorted(TERMS, key=lambda x: x[1])
    chosen = terms[0]
    for term in terms:
        if pd.Timestamp(term[1]) <= date:
            chosen = term
        else:
            break
    name, start, end, party = chosen
    return name, party, f"{name} ({start[:4]}-{end[:4]})"

def era_for(year):
    if pd.isna(year):
        return ""
    y = int(year)
    if y <= 1828: return "Founding era"
    if y <= 1860: return "Antebellum era"
    if y <= 1877: return "Civil War and Reconstruction"
    if y <= 1900: return "Gilded Age"
    if y <= 1920: return "Progressive Era"
    if y <= 1932: return "Interwar years"
    if y <= 1945: return "New Deal and World War II"
    if y <= 1968: return "Postwar and Cold War"
    if y <= 1980: return "Vietnam and Watergate era"
    if y <= 1992: return "Reagan era and Cold War end"
    if y <= 2000: return "Post Cold War"
    if y <= 2008: return "War on Terror era"
    if y <= 2016: return "Obama era"
    if y <= 2020: return "Trump first term"
    if y <= 2024: return "Biden era"
    return "Trump second term"

def disposition_from_notes(notes):
    if not notes:
        return "Unknown"
    n = notes.lower()
    tags = []
    if "revoked by" in n or "revokes:" in n and "revoked" in n:
        pass
    if "revoked by" in n: tags.append("Revoked by a later order")
    if "revokes:" in n: tags.append("Revokes an earlier order")
    if "amended by" in n: tags.append("Amended by a later order")
    if "amends:" in n: tags.append("Amends an earlier order")
    if "superseded by" in n: tags.append("Superseded")
    if "supersedes:" in n: tags.append("Supersedes an earlier order")
    if "see:" in n: tags.append("See also noted")
    return "; ".join(tags) if tags else "Noted, no revocation or amendment flag found"

def main():
    app = json.load(open(os.path.join(RAW, "app_guidebook.json")))
    fr = json.load(open(os.path.join(RAW, "federal_register.json")))
    # FR by EO number, prefer a record whose title is not Correction
    fr_by_eo = {}
    for r in fr:
        eo = r.get("executive_order_number")
        if not eo:
            continue
        eo_s = str(eo)
        if eo_s not in fr_by_eo or r.get("title") != "Correction":
            if r.get("title") == "Correction" and eo_s in fr_by_eo:
                continue
            fr_by_eo[eo_s] = r
    text_index = {}
    text_dir = os.path.join(RAW, "fr_texts")
    if os.path.isdir(text_dir):
        for fn in os.listdir(text_dir):
            m = re.match(r"eo_(\d+[A-Za-z]?)\.txt$", fn)
            if m:
                try:
                    with open(os.path.join(text_dir, fn), encoding="utf-8", errors="ignore") as f:
                        text_index[m.group(1)] = len(f.read().split())
                except Exception:
                    pass
    rows = []
    app_eo_seen = set()
    for a in app:
        title = a["title_app"].replace("\u2014", " - ").replace("\u2013", " - ")
        m = re.search(r"Executive Order\s+(?:No\.\s*)?(\d+)", title)
        eo = m.group(1) if m else ""
        if eo:
            app_eo_seen.add(eo)
        date = parse_app_date(a["date_app"])
        rows.append({
            "executive_order_number": eo,
            "president_app_label": a["president_app"],
            "date_signed": date,
            "title": title,
            "app_url": a.get("app_url", ""),
            "source": "American Presidency Project",
            "federal_register_url": "",
            "disposition_notes": "",
            "text_available": "Title only",
            "text_word_count": "",
        })
    # Enrich or add FR rows
    by_eo_index = {}
    for i, r in enumerate(rows):
        if r["executive_order_number"]:
            by_eo_index.setdefault(r["executive_order_number"], i)
    added = 0
    enriched = 0
    for eo, r in fr_by_eo.items():
        disp = (r.get("disposition_notes") or "").replace("\u2014", " - ").replace("\u2013", " - ")
        wc = text_index.get(eo, "")
        if eo in by_eo_index:
            i = by_eo_index[eo]
            rows[i]["title"] = (r.get("title") or rows[i]["title"]).replace("\u2014", " - ").replace("\u2013", " - ")
            if r.get("signing_date"):
                rows[i]["date_signed"] = pd.to_datetime(r["signing_date"])
            rows[i]["federal_register_url"] = r.get("html_url", "")
            rows[i]["disposition_notes"] = disp
            rows[i]["source"] = "American Presidency Project and Federal Register"
            if wc != "":
                rows[i]["text_available"] = "Full text downloaded"
                rows[i]["text_word_count"] = wc
            enriched += 1
        else:
            date = pd.to_datetime(r.get("signing_date")) if r.get("signing_date") else pd.NaT
            rows.append({
                "executive_order_number": eo,
                "president_app_label": "",
                "date_signed": date,
                "title": (r.get("title") or "").replace("\u2014", " - ").replace("\u2013", " - "),
                "app_url": "",
                "source": "Federal Register",
                "federal_register_url": r.get("html_url", ""),
                "disposition_notes": disp,
                "text_available": "Full text downloaded" if wc != "" else "Title only",
                "text_word_count": wc,
            })
            added += 1
    df = pd.DataFrame(rows)
    before = len(df)
    df = df[~((df["executive_order_number"] != "") & df.duplicated(subset=["executive_order_number", "date_signed", "title"], keep="first"))]
    print(f"Dropped {before - len(df)} exact duplicate rows with an EO number (APP listing duplicates, for example EO 8382 listed twice). Same day generic titles with no number are kept, because they may be distinct orders.")
    df["date_signed"] = pd.to_datetime(df["date_signed"], errors="coerce")
    df = df.dropna(subset=["date_signed"]).sort_values(["date_signed", "executive_order_number"]).reset_index(drop=True)
    # Clean titles: strip leading Executive Order NNNN prefix for a clean short title, keep full title too
    def short_title(t):
        t = str(t)
        t = re.sub(r"^Executive Order\s+(?:No\.\s*)?\d+[A-Za-z]?\s*[\u2014\-:]\s*", "", t)
        t = re.sub(r"^Executive Order\s*[\u2014\-:]\s*", "", t)
        t = re.sub(r"^Executive Order\s*$", "", t)
        return t.strip()
    df["title_clean"] = df["title"].apply(short_title)
    df["year"] = df["date_signed"].dt.year
    df["decade"] = (df["year"] // 10 * 10).astype(int)
    pres = df["date_signed"].apply(president_for)
    df["president"] = [p[0] for p in pres]
    df["party"] = [p[1] for p in pres]
    df["term"] = [p[2] for p in pres]
    df["era"] = df["year"].apply(era_for)
    cats = df["title_clean"].apply(categorize)
    df["category"] = [c[0] for c in cats]
    df["category_keyword"] = [c[1] for c in cats]
    df["disposition_status"] = df["disposition_notes"].apply(disposition_from_notes)
    df["title_word_count"] = df["title_clean"].apply(lambda x: len(str(x).split()))
    cols = ["executive_order_number", "president", "party", "term", "era", "date_signed", "year", "decade",
            "title", "title_clean", "title_word_count", "category", "category_keyword",
            "disposition_status", "disposition_notes", "source", "text_available", "text_word_count",
            "app_url", "federal_register_url", "president_app_label"]
    df = df[cols]
    out = os.path.join(PROC, "executive_orders.csv")
    df.to_csv(out, index=False)
    print(f"APP rows: {len(app)}")
    print(f"FR unique EO numbers: {len(fr_by_eo)}")
    print(f"FR rows enriched into APP rows: {enriched}")
    print(f"FR rows added as new rows: {added}")
    print(f"Final dataset rows: {len(df)}")
    print(f"Date range: {df['date_signed'].min().date()} to {df['date_signed'].max().date()}")
    print(f"Rows with EO number: {(df['executive_order_number'] != '').sum()}")
    print(f"Rows with full text: {(df['text_available'] == 'Full text downloaded').sum()}")
    print(f"Wrote {out}")
    # by president summary for notebooks
    summ = df.groupby(["president", "party"]).size().reset_index(name="orders_in_dataset")
    summ.to_csv(os.path.join(PROC, "orders_by_president_dataset.csv"), index=False)
    yearly = df.groupby("year").size().reset_index(name="orders")
    yearly.to_csv(os.path.join(PROC, "orders_by_year.csv"), index=False)
    return df

if __name__ == "__main__":
    main()
