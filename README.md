# US Executive Orders: The Complete Analytics Project

A beginner friendly, story driven tour of every executive order we could put in a row level dataset, from 1791 to 2026, with the dataset itself as the main deliverable.

## Start here, in plain words

An executive order is a signed instruction from the President to the federal government. It has the force of law until a later President, Congress, or a court changes it. Presidents have used this tool since George Washington, but they have not used it the same way in every era. Early orders were often short, routine paperwork. Later orders are more often about national policy.

This project does not ask you to trust a headline. It gives you the rows, the counts, the topics, and the search tool, and it tells you where the data runs out.

## Headline findings, all from the dataset in this folder

- Dataset rows: 10,879. Date range: 1791 to 2026. Latest order in the data: EO 14438, signed 2026-10-22, titled "Decreasing Housing Costs for the American People".
- Most orders in the dataset: Franklin D. Roosevelt with 3,725 rows, followed by Herbert Hoover with 1,004 and Harry S. Truman with 907.
- Busiest year in the dataset: 1933 with 657 orders. Next: 1934 with 472 and 1935 with 384.
- Busiest decade in the dataset: the 1930s, with 3,313 orders.
- Largest keyword category: Other or General with 3,612 orders. Next: Land and Public Lands with 1,714 and Government Administration with 1,351.
- Titles are short. Median title length: 10 words. 508 rows have a generic title, just the words Executive Order with no subject, mostly from the 1800s.
- Full text downloaded here: 1,549 recent orders. Median full text length among those: 974 words.
- The Federal Register series from EO 12890 to EO 14438 has zero missing numbers in this build. That is the recent complete spine of the dataset.
- Keyword categorization is a blunt first pass. On a deliberately hard hand checked sample of 30 orders, it agreed with a human reading on 15 of 30, or 50 percent. Use categories for broad shares, not for labeling any single order. See notebook 03 for the full sample and the error types.

## The honest cut, read this before you quote a total

This dataset is row level complete from Herbert Hoover onward. Before Hoover, it is a large titled sample, not a complete row list. The American Presidency Project itself says its collection of executive order texts is complete beginning with the Hoover administration. Published historical totals are much higher for Woodrow Wilson, Calvin Coolidge, Theodore Roosevelt, and William Howard Taft than the rows here, because many routine early orders, for example land withdrawals and civil service exemptions, were counted in totals but do not have an individual titled entry in the public listing used here.

To keep the two ideas separate, this project ships both: the row level dataset, and a reference table of published per President totals in notebook 00 and in the build report. Never quote a row count as if it were the published historical total for a pre-1929 President.

Other cuts:

- Full text is only for recent orders, from the Federal Register. Older orders are title only here. That is enough for counts, title topics, and title word trends. It is not enough for claims about the full wording of an old order.
- Disposition notes, revocation and amendment links, exist only for orders with Federal Register notes, 1,137 rows here. Do not divide those counts by the full dataset total.
- 9,989 rows have an EO number. The rest are unnumbered early orders, which is historically correct, not a data error.
- Abraham Lincoln is an exception in the other direction: the dataset has 119 Lincoln rows, while the published reference total used here is 48. The Presidency Project listing for Lincoln includes general orders and other Lincoln documents alongside executive orders, while the reference count uses a narrower definition. That difference is a definition difference, not a hidden error. It is flagged in notebook 00.

## What is in this folder

- data/processed/executive_orders.csv: the full clean dataset, one row per order in the dataset.
- data/processed/orders_by_president_dataset.csv and orders_by_year.csv: summaries built from the dataset.
- data/raw/PROVENANCE.md: every source, with URL and what was taken from it.
- notebooks/00 to 06: seven executed notebooks, zero to hero, from coverage to search.
- charts/: 18 charts, also copied into docs/charts for the story site.
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
