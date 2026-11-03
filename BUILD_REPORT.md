# BUILD_REPORT.md: US Executive Orders, The Complete Analytics Project

## What was built

- Local folder: us-executive-orders, inside the workspace. Nothing was published, pushed, posted, or signed into.
- 7 notebooks: 00_setup_and_coverage, 01_the_complete_dataset, 02_descriptive_statistics, 03_categorization, 04_eras_and_history, 05_language_analysis, 06_search_the_archive. Each has a top pip install cell and was executed end to end.
- Headline dataset: data/processed/executive_orders.csv with 10,879 rows, 9,989 with an EO number, 1,549 with full text downloaded, date range 1791 to 2026.
- Charts: 18 PNG files in charts/, listed below.
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
- Full text for all recent orders depends on the fetch completing. If a rebuild runs before the fetch finishes, text_available will show fewer full texts, and notebook 02 and 05 will report that smaller number honestly. The final build in this folder reports 1,549 full texts.
- No language model was trained, fine tuned, or used. Topic modeling uses NMF from scikit-learn, and search uses TF-IDF cosine similarity. Both are statistical methods. Notebook 06 explains the language model retrieval pipeline as a future design, not as work done here.
- No external publishing, no sign in, no account use. The parent handles any publishing after verification.

## Verification checks, final build

- Dataset rows: 10,879.
- Rows with a signing date: 10,879. Rows with a title: 10,879.
- Federal Register EO numbers 12890 to 14438: zero missing.
- Duplicate numbered rows in the final dataset: 0 after the EO 8382 dedup.
- Keyword validation sample: 30 orders hand checked, 15 agreements, 50 percent. Error types: Other or General fallback, priority order effects, substring traps (branch contains ranch, support contains port, homeland contains land), and true multi topic ambiguity.
- Em dash check: grep for the em dash character across notebooks, README, BUILD_REPORT, PROVENANCE, HTML, scripts, and CSV headers, excluding .venv. Result: zero matches in the final check (see final report for the grep command output).
- Notebook cell errors: zero in the final execution pass. Charts: 18.

## Charts

- charts/00_coverage_by_era.png
- charts/01_orders_by_president.png
- charts/02_disposition_flags.png
- charts/02_fulltext_length_hist.png
- charts/02_orders_by_decade.png
- charts/02_orders_per_year.png
- charts/02_title_length_hist.png
- charts/02_top_presidents.png
- charts/03_category_by_era.png
- charts/03_keyword_categories.png
- charts/03_nmf_topics.png
- charts/04_new_deal_wwii.png
- charts/04_orders_with_markers.png
- charts/04_recent_years.png
- charts/05_category_trends.png
- charts/05_title_length_by_decade.png
- charts/05_vocabulary_by_decade.png
- charts/05_word_trends.png

## Key numbers for the parent report

- Total dataset rows: {N:,}.
- Latest order: EO 14438, October 22, 2026.
- Most rows by President: {TOP_PRES.index[0]} {int(TOP_PRES.iloc[0]):,}, {TOP_PRES.index[1]} {int(TOP_PRES.iloc[1]):,}, {TOP_PRES.index[2]} {int(TOP_PRES.iloc[2]):,}.
- Busiest year: {int(TOP_YEAR.index[0])} with {int(TOP_YEAR.iloc[0]):,} rows.
- Full texts downloaded: {FULL:,}.
