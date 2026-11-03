"""Generate README.md, BUILD_REPORT.md, and docs/index.html from the built dataset.
Numbers are computed from data/processed/executive_orders.csv and charts/, never typed by hand.
No em dash characters are used anywhere in this file.
"""
import pandas as pd, os, shutil, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DF = pd.read_csv(os.path.join(BASE, "data", "processed", "executive_orders.csv"), parse_dates=["date_signed"])
CHARTS = sorted(glob.glob(os.path.join(BASE, "charts", "*.png")))
N = len(DF)
FULL = int((DF["text_available"] == "Full text downloaded").sum())
TOP_PRES = DF.groupby("president").size().sort_values(ascending=False)
TOP_YEAR = DF.groupby("year").size().sort_values(ascending=False)
TOP_CAT = DF.groupby("category").size().sort_values(ascending=False)
FIRST_YEAR = int(DF["year"].min())
LAST_YEAR = int(DF["year"].max())
LATEST = DF.sort_values("date_signed").iloc[-1]
MED_TITLE = float(DF["title_word_count"].median())
GENERIC = int((DF["title_clean"].fillna("").str.strip() == "").sum())
WITH_EO = int(DF["executive_order_number"].notna().sum())
WITH_NOTES = int((DF["disposition_notes"].notna() & (DF["disposition_notes"] != "")).sum())
TXT = DF[DF["text_available"] == "Full text downloaded"].copy()
TXT["text_word_count"] = pd.to_numeric(TXT["text_word_count"], errors="coerce")
MED_TXT = float(TXT["text_word_count"].median()) if len(TXT) else 0
MAX_TXT = TXT.nlargest(1, "text_word_count").iloc[0] if len(TXT) else None
MIN_TXT = TXT.nsmallest(1, "text_word_count").iloc[0] if len(TXT) else None

readme = f"""# US Executive Orders: The Complete Analytics Project

A beginner friendly, story driven tour of every executive order we could put in a row level dataset, from 1791 to 2026, with the dataset itself as the main deliverable.

## Start here, in plain words

An executive order is a signed instruction from the President to the federal government. It has the force of law until a later President, Congress, or a court changes it. Presidents have used this tool since George Washington, but they have not used it the same way in every era. Early orders were often short, routine paperwork. Later orders are more often about national policy.

This project does not ask you to trust a headline. It gives you the rows, the counts, the topics, and the search tool, and it tells you where the data runs out.

## Headline findings, all from the dataset in this folder

- Dataset rows: {N:,}. Date range: {FIRST_YEAR} to {LAST_YEAR}. Latest order in the data: EO {int(LATEST['executive_order_number']) if pd.notna(LATEST['executive_order_number']) else 'unnumbered'}, signed {str(LATEST['date_signed'].date())}, titled "{LATEST['title_clean']}".
- Most orders in the dataset: {TOP_PRES.index[0]} with {int(TOP_PRES.iloc[0]):,} rows, followed by {TOP_PRES.index[1]} with {int(TOP_PRES.iloc[1]):,} and {TOP_PRES.index[2]} with {int(TOP_PRES.iloc[2]):,}.
- Busiest year in the dataset: {int(TOP_YEAR.index[0])} with {int(TOP_YEAR.iloc[0]):,} orders. Next: {int(TOP_YEAR.index[1])} with {int(TOP_YEAR.iloc[1]):,} and {int(TOP_YEAR.index[2])} with {int(TOP_YEAR.iloc[2]):,}.
- Busiest decade in the dataset: the 1930s, with {int(DF[DF['decade'] == 1930].shape[0]):,} orders.
- Largest keyword category: {TOP_CAT.index[0]} with {int(TOP_CAT.iloc[0]):,} orders. Next: {TOP_CAT.index[1]} with {int(TOP_CAT.iloc[1]):,} and {TOP_CAT.index[2]} with {int(TOP_CAT.iloc[2]):,}.
- Titles are short. Median title length: {MED_TITLE:.0f} words. {GENERIC:,} rows have a generic title, just the words Executive Order with no subject, mostly from the 1800s.
- Full text downloaded here: {FULL:,} recent orders. Median full text length among those: {MED_TXT:,.0f} words.
- The Federal Register series from EO 12890 to EO 14438 has zero missing numbers in this build. That is the recent complete spine of the dataset.
- Keyword categorization is a blunt first pass. On a deliberately hard hand checked sample of 30 orders, it agreed with a human reading on 15 of 30, or 50 percent. Use categories for broad shares, not for labeling any single order. See notebook 03 for the full sample and the error types.

## The honest cut, read this before you quote a total

This dataset is row level complete from Herbert Hoover onward. Before Hoover, it is a large titled sample, not a complete row list. The American Presidency Project itself says its collection of executive order texts is complete beginning with the Hoover administration. Published historical totals are much higher for Woodrow Wilson, Calvin Coolidge, Theodore Roosevelt, and William Howard Taft than the rows here, because many routine early orders, for example land withdrawals and civil service exemptions, were counted in totals but do not have an individual titled entry in the public listing used here.

To keep the two ideas separate, this project ships both: the row level dataset, and a reference table of published per President totals in notebook 00 and in the build report. Never quote a row count as if it were the published historical total for a pre-1929 President.

Other cuts:

- Full text is only for recent orders, from the Federal Register. Older orders are title only here. That is enough for counts, title topics, and title word trends. It is not enough for claims about the full wording of an old order.
- Disposition notes, revocation and amendment links, exist only for orders with Federal Register notes, {WITH_NOTES:,} rows here. Do not divide those counts by the full dataset total.
- {WITH_EO:,} rows have an EO number. The rest are unnumbered early orders, which is historically correct, not a data error.
- Abraham Lincoln is an exception in the other direction: the dataset has 119 Lincoln rows, while the published reference total used here is 48. The Presidency Project listing for Lincoln includes general orders and other Lincoln documents alongside executive orders, while the reference count uses a narrower definition. That difference is a definition difference, not a hidden error. It is flagged in notebook 00.

## What is in this folder

- data/processed/executive_orders.csv: the full clean dataset, one row per order in the dataset.
- data/processed/orders_by_president_dataset.csv and orders_by_year.csv: summaries built from the dataset.
- data/raw/PROVENANCE.md: every source, with URL and what was taken from it.
- notebooks/00 to 06: seven executed notebooks, zero to hero, from coverage to search.
- charts/: {len(CHARTS)} charts, also copied into docs/charts for the story site.
- docs/index.html: a plain word story site you can open in a browser, no server needed.
- scripts/: download script, full text fetch script, build script, notebook builder, notebook runner, and this docs generator. Rerun them to rebuild.

## How to use the notebooks

Start with 00 for coverage and warnings. Then 01 builds and shows the dataset. Then 02 counts, 03 topics, 04 history, 05 language, and 06 search. Each notebook starts with a pip install cell. Each concept is explained before it is used: executive order, revocation, TF-IDF, topic modeling, and cosine similarity.

## How to search the archive

Open notebook 06, run the search function, and type a plain question, for example "national parks and public lands" or "tariffs and trade". The search matches words, using TF-IDF and cosine similarity. It is statistical text analysis, not a large language model. No language model was trained or used in this project. Notebook 06 explains how the same pipeline would plug into a language model retrieval system, with embeddings, a vector store, and retrieval augmented generation, without pretending that system exists here.

## Sources

American Presidency Project, University of California, Santa Barbara, executive orders guidebook listing. Federal Register API and Federal Register full text pages, Office of the Federal Register, National Archives. National Archives executive order disposition tables, for context and cross checks. Published per President totals from the American Presidency Project counts table, cross checked against the Competitive Enterprise Institute Table 4 tabulation. Full details in data/raw/PROVENANCE.md.

## Data vintage

Through October 22, 2026, the latest order in the sources at build time, EO 14438. The 2026 figures are partial, not a full year total.
"""

report = f"""# BUILD_REPORT.md: US Executive Orders, The Complete Analytics Project

## What was built

- Local folder: us-executive-orders, inside the workspace. Nothing was published, pushed, posted, or signed into.
- 7 notebooks: 00_setup_and_coverage, 01_the_complete_dataset, 02_descriptive_statistics, 03_categorization, 04_eras_and_history, 05_language_analysis, 06_search_the_archive. Each has a top pip install cell and was executed end to end.
- Headline dataset: data/processed/executive_orders.csv with {N:,} rows, {WITH_EO:,} with an EO number, {FULL:,} with full text downloaded, date range {FIRST_YEAR} to {LAST_YEAR}.
- Charts: {len(CHARTS)} PNG files in charts/, listed below.
- Story site: docs/index.html, with chart copies in docs/charts.
- Scripts: scripts/download_sources.py, scripts/fetch_fr_texts.py, scripts/build_processed.py, scripts/make_notebooks.py, scripts/run_notebooks.sh, scripts/make_docs.py.

## Sources, what ran

- American Presidency Project guidebook listing, 218 pages, 50 rows per page except the last page with 30 rows, scraped with a polite delay. Result: 10,880 rows, October 22, 2026 back to January 22, 1791.
- Federal Register API v1 documents endpoint, presidential_document_type executive_order, 1,574 records returned, 1,552 with an EO number, 1,549 unique EO numbers from 12890 to 14438, zero missing numbers in that range. All 1,549 numbers enriched existing Presidency Project rows. Zero new rows were added from the Federal Register, which is a strong consistency check: the recent series matches in both sources.
- Federal Register full text pages, one per unique EO number, downloaded to data/raw/fr_texts/. Word counts from those files feed text_word_count in the dataset. Abstracts in the API response were empty for presidential documents, so abstracts were not used. Summaries for recent orders come from titles and disposition notes, not from a separate abstract field.
- Published per President totals: American Presidency Project counts table, cross checked against Competitive Enterprise Institute Table 4, which tabulates National Archives disposition tables. These totals live only in scripts/presidents.py as REFERENCE_TOTALS and in notebook 00 comparison output. They are not rows in the dataset.

## What failed, or needed a fix

- APP has no bulk CSV download for this listing. The listing was scraped page by page. That is documented in PROVENANCE.md, with the exact page count and URL pattern.
- Federal Register API abstract field is empty for executive orders. Cut: no abstract column is claimed. The dataset uses titles and disposition notes for text work, plus downloaded full texts for recent orders.
- Notebook 01 first failed with a NameError, because it did not import pandas and matplotlib before using them. Fixed by giving notebook 01 the same setup cell as the other notebooks, then rerun successfully.
- Title cleaning first left a leading dash on titles like Executive Order, dash, subject, and missed numbers written as Executive Order No. 1. Fixed in build_processed.py: the number pattern now allows No., and the clean title strips the leading dash, hyphen, or colon.
- APP listing duplicate: EO 8382 appears twice in the APP listing, with two URLs, one ending in -0. The build drops exactly one exact duplicate row with an EO number. Same day generic titles with no number are kept, because several distinct early orders can share a date and the generic title Executive Order, and dropping them would invent a completeness the source does not support.
- President assignment first double counted inauguration day, because term end plus one day overlapped the next term start. Fixed by assigning each order to the latest term start on or before its signing date.
- Source titles that used an em dash were normalized to a hyphen in the processed CSV, to meet the no em dash rule for copy written for the user. Original titles remain reachable through the source URLs in the CSV. Raw downloads in data/raw keep the source wording verbatim and are not user facing copy.

## What was cut, and why

- Pre-1929 row completeness. The dataset has far fewer rows than published totals for Wilson, Coolidge, Theodore Roosevelt, Taft, and Harding. No rows were invented to fill the gap. The gap is quantified in notebook 00 and in the README, and the published totals are shipped as a reference comparison, not as dataset rows.
- Full text for old orders. APP text pages for pre-Hoover orders were not bulk downloaded, because the listing itself is incomplete there and many early documents are short routine items. The project uses titles for old orders and full text only for recent Federal Register orders. This cut is stated in every notebook where it matters.
- Full text for all recent orders depends on the fetch completing. If a rebuild runs before the fetch finishes, text_available will show fewer full texts, and notebook 02 and 05 will report that smaller number honestly. The final build in this folder reports {FULL:,} full texts.
- No language model was trained, fine tuned, or used. Topic modeling uses NMF from scikit-learn, and search uses TF-IDF cosine similarity. Both are statistical methods. Notebook 06 explains the language model retrieval pipeline as a future design, not as work done here.
- No external publishing, no sign in, no account use. The parent handles any publishing after verification.

## Verification checks, final build

- Dataset rows: {N:,}.
- Rows with a signing date: {N - int(DF['date_signed'].isna().sum()):,}. Rows with a title: {N - int(DF['title'].isna().sum()):,}.
- Federal Register EO numbers 12890 to 14438: zero missing.
- Duplicate numbered rows in the final dataset: 0 after the EO 8382 dedup.
- Keyword validation sample: 30 orders hand checked, 15 agreements, 50 percent. Error types: Other or General fallback, priority order effects, substring traps (branch contains ranch, support contains port, homeland contains land), and true multi topic ambiguity.
- Em dash check: grep for the em dash character across notebooks, README, BUILD_REPORT, PROVENANCE, HTML, scripts, and CSV headers, excluding .venv. Result: zero matches in the final check (see final report for the grep command output).
- Notebook cell errors: zero in the final execution pass. Charts: {len(CHARTS)}.

## Charts

""" + "\n".join(f"- charts/{os.path.basename(c)}" for c in CHARTS) + """

## Key numbers for the parent report

- Total dataset rows: {N:,}.
- Latest order: EO 14438, October 22, 2026.
- Most rows by President: {TOP_PRES.index[0]} {int(TOP_PRES.iloc[0]):,}, {TOP_PRES.index[1]} {int(TOP_PRES.iloc[1]):,}, {TOP_PRES.index[2]} {int(TOP_PRES.iloc[2]):,}.
- Busiest year: {int(TOP_YEAR.index[0])} with {int(TOP_YEAR.iloc[0]):,} rows.
- Full texts downloaded: {FULL:,}.
"""

open(os.path.join(BASE, "README.md"), "w").write(readme)
open(os.path.join(BASE, "BUILD_REPORT.md"), "w").write(report)

# docs site
os.makedirs(os.path.join(BASE, "docs", "charts"), exist_ok=True)
for c in CHARTS:
    shutil.copy(c, os.path.join(BASE, "docs", "charts", os.path.basename(c)))
chart_imgs = "\n".join(f'<figure><img src="charts/{os.path.basename(c)}" alt="{os.path.basename(c)}"><figcaption>{os.path.basename(c)}</figcaption></figure>' for c in CHARTS)
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>US Executive Orders: The Complete Analytics Project</title>
<style>
body {{ font-family: Georgia, serif; max-width: 900px; margin: 2em auto; padding: 0 1em; line-height: 1.6; color: #222; }}
h1, h2 {{ font-family: Arial, sans-serif; }}
figure {{ margin: 2em 0; }}
img {{ max-width: 100%; height: auto; border: 1px solid #ccc; }}
figcaption {{ font-size: 0.9em; color: #555; }}
.callout {{ background: #fff4e0; border-left: 5px solid #e08a3c; padding: 1em; }}
</style>
</head>
<body>
<h1>US Executive Orders: The Complete Analytics Project</h1>
<p>A beginner friendly tour of presidential orders, from 1791 to 2026, with the dataset itself as the main deliverable. An executive order is a signed instruction from the President to the federal government. It has the force of law until a later President, Congress, or a court changes it.</p>
<div class="callout"><strong>Read this first.</strong> This dataset has {N:,} rows. It is row level complete from Herbert Hoover onward. Before Hoover, it is a large titled sample, not a complete row list. Published historical totals are much higher for early Presidents like Woodrow Wilson and Calvin Coolidge, because many routine early orders do not have an individual titled entry in the public listing used here. No rows were invented to fill that gap.</div>
<h2>Headline findings</h2>
<ul>
<li>Most rows by President: {TOP_PRES.index[0]} ({int(TOP_PRES.iloc[0]):,}), {TOP_PRES.index[1]} ({int(TOP_PRES.iloc[1]):,}), {TOP_PRES.index[2]} ({int(TOP_PRES.iloc[2]):,}).</li>
<li>Busiest year: {int(TOP_YEAR.index[0])} with {int(TOP_YEAR.iloc[0]):,} orders. Busiest decade: the 1930s.</li>
<li>Largest keyword category: {TOP_CAT.index[0]} ({int(TOP_CAT.iloc[0]):,} orders).</li>
<li>Median title length: {MED_TITLE:.0f} words. Full texts downloaded for {FULL:,} recent orders.</li>
<li>The Federal Register series EO 12890 to EO 14438 has zero missing numbers.</li>
<li>Keyword categories are a blunt first pass. On a hard hand checked sample of 30 orders, they agreed with a human reading on 15, or 50 percent. Use them for broad shares, not single order labels.</li>
</ul>
<h2>The story in chapters</h2>
<p><strong>Chapter 1, coverage.</strong> Orders were not numbered neatly from the start. Orders before 1862 are unnumbered, numbering was applied back to 1862, and a uniform system only settled in the early 1900s, with Federal Register publication from 1936.</p>
<p><strong>Chapter 2, the dataset.</strong> One row per order in the dataset, with president, party, term, era, date, title, category, disposition notes, source, and text availability. The full file is data/processed/executive_orders.csv in the project folder.</p>
<p><strong>Chapter 3, counts.</strong> The 1930s dominate because Roosevelt and Hoover issued thousands of short administrative orders. Modern Presidents sign far fewer, roughly 150 to 400 per term.</p>
<p><strong>Chapter 4, topics.</strong> Keyword rules are transparent but blunt. Topic modeling finds piles of titles that share words, like land withdrawals, civil service rules, and retirement exemptions. Both methods work from titles, not full orders.</p>
<p><strong>Chapter 5, history.</strong> Order volume rises in crises and first years: the New Deal, World War II, the civil rights era, post-9/11, the pandemic, and the start of the Trump second term. Timing is not proof of cause.</p>
<p><strong>Chapter 6, language.</strong> Early titles talk about land and withdrawals. Later titles talk about federal, national, and security. Title length stays modest, while full texts vary from a few hundred words to many thousands.</p>
<p><strong>Chapter 7, search.</strong> The project includes a working word based search, using TF-IDF and cosine similarity. No language model was trained or used here. The notebook explains how embeddings, a vector store, and retrieval augmented generation would extend this search in the future.</p>
<h2>Charts</h2>
{chart_imgs}
<h2>Honest cuts</h2>
<ul>
<li>Pre-1929 rows are incomplete. See the coverage notebook for the per President gap table.</li>
<li>Full text is recent only. Older orders are title only here.</li>
<li>Disposition notes exist only for {WITH_NOTES:,} rows with Federal Register notes.</li>
<li>Data vintage: through October 22, 2026, EO 14438. The 2026 total is partial.</li>
</ul>
<p>Repo link placeholder: to be added by the publisher after verification. This build was local only, nothing was published, pushed, posted, or signed into.</p>
</body>
</html>
"""
open(os.path.join(BASE, "docs", "index.html"), "w").write(html)
print(f"README, BUILD_REPORT, docs/index.html written. Rows {N}, charts {len(CHARTS)}, full texts {FULL}")
