# US Executive Orders: The Complete Analytics Project

I started with a question that sounded simple and turned out not to be. What has every President actually ordered, in writing, since George Washington, and how has that power changed over 235 years?

I had seen plenty of headlines about executive orders, usually about one order at a time. I had never seen the whole record in one place, as rows I could count, sort, and search. So I built it myself: every executive order I could put in a row level dataset, from 1791 to 2026, with the dataset itself as the main deliverable.

Read it as a story: https://jwavalosq.github.io/us-executive-orders/

## Why this matters

An executive order is a signed instruction from the President to the federal government. It has the force of law until a later President, Congress, or a court changes it. Presidents have used this tool since Washington, but they have not used it the same way in every era. Early orders were often short, routine paperwork. Later orders are more often about national policy.

If you want to understand presidential power, you need more than opinions about it. You need the record. This project gives you the rows, the counts, the topics, and a search tool, and it tells you plainly where the data runs out. It is written for a beginner. Each concept is explained before I use it: executive order, revocation, TF-IDF, topic modeling, and cosine similarity.

## What I did

I built the dataset first, then I analyzed it in seven notebooks, in order.

1. `notebooks/00_setup_and_coverage.ipynb`. I checked coverage first, before counting anything, so I would know exactly where the dataset is complete and where it is not.
2. `notebooks/01_the_complete_dataset.ipynb`. I built and showed the dataset itself: one row per order, with president, party, term, era, date, title, category, disposition notes, source, and text availability.
3. `notebooks/02_descriptive_statistics.ipynb`. I counted: orders by president, by year, by decade, title lengths, and full text lengths.
4. `notebooks/03_categorization.ipynb`. I sorted orders into topics with transparent keyword rules, and I tested those rules by hand so I could report honestly how blunt they are.
5. `notebooks/04_eras_and_history.ipynb`. I traced the big eras: the New Deal, World War II, the civil rights era, post-9/11, the pandemic, and the start of the Trump second term.
6. `notebooks/05_language_analysis.ipynb`. I tracked how the words in titles changed across decades.
7. `notebooks/06_search_the_archive.ipynb`. I built a working word based search over the archive, using TF-IDF and cosine similarity.

My sources are the American Presidency Project executive orders listing at UC Santa Barbara, the Federal Register API and Federal Register full text pages, and National Archives disposition tables for context and cross checks. Full details are in `data/raw/PROVENANCE.md`.

## What I found

The dataset has 10,879 rows. The date range runs from January 22, 1791 to October 22, 2026. The latest order in the data is EO 14438, signed October 22, 2026, titled "Decreasing Housing Costs for the American People".

Franklin D. Roosevelt dominates the record, with 3,725 rows, followed by Herbert Hoover with 1,004 and Harry S. Truman with 907. The busiest year in the dataset is 1933, with 657 orders. Next come 1934 with 472 and 1935 with 384. The busiest decade is the 1930s, with 3,313 orders.

The largest keyword category is Other or General, with 3,612 orders. Next are Land and Public Lands with 1,714 and Government Administration with 1,351. That big Other bucket is itself a finding: a lot of early orders were routine paperwork that does not fit a neat policy label.

Titles are short. The median title length is 10 words. 508 rows have a generic title, just the words Executive Order with no subject, mostly from the 1800s. I downloaded full text for 1,549 recent orders. The median full text length among those is 974 words.

One consistency check made me trust the recent data more: the Federal Register series from EO 12890 to EO 14438 has zero missing numbers in this build. That is the recent complete spine of the dataset.

The history chapter shows order volume rising in crises and first years: the New Deal, World War II, the civil rights era, post-9/11, the pandemic, and the start of the Trump second term. Timing is not proof of cause, and I do not claim it is. But the pattern is clear enough to see in the charts.

The language chapter shows the same shift in words. Early titles talk about land and withdrawals. Later titles talk about federal, national, and security. Title length stays modest, while full texts vary from a few hundred words to many thousands.

## What it means, and who it helps

Three lessons stand out for me. First, the modern image of the executive order as a big policy weapon is only half the story. For much of American history, orders were mostly small administrative acts, and the Roosevelt years are an outlier, not the norm. Second, counting first changes the argument. Once you see that one president accounts for more than a third of the rows, you stop treating every presidency as the same. Third, a search tool matters as much as a chart. A dataset you can ask a question of is more useful than a dataset you can only admire.

This project helps anyone who needs the record, not just a headline: a recruiter checking how I think, a student or journalist who wants a clean dataset to explore, or a reader who wants to check a claim about a president against the numbers. If you run notebook 06, you can search the archive yourself.

## How to search the archive

Open notebook 06, run the search function, and type a plain question, for example "national parks and public lands" or "tariffs and trade". The search matches words, using TF-IDF and cosine similarity. It is statistical text analysis, not a large language model. No language model was trained or used in this project. Notebook 06 explains how the same pipeline would plug into a language model retrieval system, with embeddings, a vector store, and retrieval augmented generation, without pretending that system exists here.

## How to run it yourself

Start with notebook 00 for coverage and warnings. Then 01 builds and shows the dataset. Then 02 counts, 03 topics, 04 history, 05 language, and 06 search. Each notebook starts with a pip install cell, so it also runs in Google Colab.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

## What is in this folder

- `data/processed/executive_orders.csv`: the full clean dataset, one row per order in the dataset.
- `data/processed/orders_by_president_dataset.csv` and `orders_by_year.csv`: summaries built from the dataset.
- `data/raw/PROVENANCE.md`: every source, with URL and what was taken from it.
- `notebooks/00` to `06`: seven executed notebooks, zero to hero, from coverage to search.
- `charts/`: 18 charts, also copied into `docs/charts` for the story site.
- `docs/index.html`: a plain word story site you can open in a browser, no server needed. Live version: https://jwavalosq.github.io/us-executive-orders/
- `scripts/`: download script, full text fetch script, build script, notebook builder, notebook runner, and docs generator. Rerun them to rebuild.
- `BUILD_REPORT.md`: exactly what was built, what ran, what failed, and what was cut.

## The honest cut, read this before you quote a total

This dataset is row level complete from Herbert Hoover onward. Before Hoover, it is a large titled sample, not a complete row list. The American Presidency Project itself says its collection of executive order texts is complete beginning with the Hoover administration. Published historical totals are much higher for Woodrow Wilson, Calvin Coolidge, Theodore Roosevelt, and William Howard Taft than the rows here, because many routine early orders, for example land withdrawals and civil service exemptions, were counted in totals but do not have an individual titled entry in the public listing I used.

To keep the two ideas separate, I ship both: the row level dataset, and a reference table of published per President totals in notebook 00 and in the build report. Never quote a row count as if it were the published historical total for a pre-1929 President.

Other cuts:

- Full text is only for recent orders, from the Federal Register. Older orders are title only here. That is enough for counts, title topics, and title word trends. It is not enough for claims about the full wording of an old order.
- Disposition notes, revocation and amendment links, exist only for orders with Federal Register notes, 1,137 rows here. Do not divide those counts by the full dataset total.
- 9,989 rows have an EO number. The rest are unnumbered early orders, which is historically correct, not a data error.
- Abraham Lincoln is an exception in the other direction: the dataset has 119 Lincoln rows, while the published reference total used here is 48. The Presidency Project listing for Lincoln includes general orders and other Lincoln documents alongside executive orders, while the reference count uses a narrower definition. That difference is a definition difference, not a hidden error. It is flagged in notebook 00.
- Keyword categorization is a blunt first pass. On a deliberately hard hand checked sample of 30 orders, it agreed with a human reading on 15 of 30, or 50 percent. Use categories for broad shares, not for labeling any single order. See notebook 03 for the full sample and the error types.
- The 1,549 downloaded Federal Register texts ship in this repo as one archive, `data/raw/fr_texts.zip`, to keep the file count manageable. Unzip it into `data/raw/` to get the `data/raw/fr_texts/` folder with one text file per order. The word counts in the dataset come from those files, and `scripts/fetch_fr_texts.py` can also re-download them individually.

## Sources

American Presidency Project, University of California, Santa Barbara, executive orders guidebook listing. Federal Register API and Federal Register full text pages, Office of the Federal Register, National Archives. National Archives executive order disposition tables, for context and cross checks. Published per President totals from the American Presidency Project counts table, cross checked against the Competitive Enterprise Institute Table 4 tabulation. Full details in `data/raw/PROVENANCE.md`.

## Data vintage

Through October 22, 2026, the latest order in the sources at build time, EO 14438. The 2026 figures are partial, not a full year total.
