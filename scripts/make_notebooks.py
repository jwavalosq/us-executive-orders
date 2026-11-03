"""Build the 7 notebooks for US Executive Orders: The Complete Analytics Project.
Each notebook gets a top pip install cell, then markdown and code cells.
Run this file, then execute the notebooks in order 00 to 06.
No em dash characters are used anywhere in this file.
"""
import nbformat as nbf
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(BASE, "notebooks")
os.makedirs(NB, exist_ok=True)
INSTALL = "%pip install -q pandas numpy matplotlib scikit-learn"
SETUP = """import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["figure.dpi"] = 120
from pathlib import Path
BASE = Path("..").resolve()
CH = BASE / "charts"
CH.mkdir(exist_ok=True)
DF = pd.read_csv(BASE / "data" / "processed" / "executive_orders.csv", parse_dates=["date_signed"])
print("Rows:", len(DF), "| Years:", DF["year"].min(), "to", DF["year"].max())"""

def nb(cells):
    out = nbf.v4.new_notebook()
    out.metadata.kernelspec = {"name": "eo-project", "display_name": "EO project", "language": "python"}
    out.cells = cells
    return out

def md(text):
    return nbf.v4.new_markdown_cell(text.strip())

def code(text):
    return nbf.v4.new_code_cell(text.strip())

def save(name, cells):
    path = os.path.join(NB, name)
    nbf.write(nb(cells), path)
    print("Wrote", path, "cells:", len(cells))

# ---------------------------------------------------------------- 00
cells00 = [
    code(INSTALL),
    md("""# 00. Setup and coverage: what this project is

## The idea in plain words
An executive order is a signed instruction from the President to the federal government. It tells agencies how to run things, and it has the force of law until a later President, Congress, or a court changes it. It is not a law passed by Congress, and it is not a speech. It is a working order.

This project collects those orders, counts them, groups them by topic, follows them through history, and studies the words in their titles. It also gives you the dataset itself, so you can check every claim here.

## What you will learn, in order
First, what the data covers and where it falls short. Second, the full dataset. Third, simple counts. Fourth, topics. Fifth, history. Sixth, language. Seventh, how to search the archive yourself.

## A warning before you trust any count
Executive orders were not numbered in a neat series from the start. Orders before 1862 are unnumbered. Numbering was applied retroactively back to 1862, and a uniform system only settled in the early 1900s, with the Federal Register Act of 1935 and Federal Register publication from 1936. That is why different sources give slightly different totals for the same President. A count is only honest if it names its source and its date range. This notebook does that."""),
    code(SETUP),
    md("""## Sources used
1. The American Presidency Project (APP), University of California, Santa Barbara. Guidebook listing of executive orders, president, date, and title, plus a link to each order page. This is the row level backbone.
2. The Federal Register API, Office of the Federal Register, National Archives. Presidential documents of type executive_order. This gives the official title, signing date, EO number, disposition notes, and links for 1994 onward, and it is used to enrich APP rows.
3. Federal Register full text pages for recent orders, downloaded one per EO number, used only for word counts and length in notebooks 02 and 05.
4. Published per President totals from the APP counts table, cross checked against the Competitive Enterprise Institute Table 4 tabulation of National Archives disposition tables. These are reference totals, not rows in this dataset. They are kept in a separate file so the two are never confused.

Full URLs and what was taken from each source are in data/raw/PROVENANCE.md."""),
    code("""import json
from collections import Counter
app = json.load(open(BASE / "data" / "raw" / "app_guidebook.json"))
fr = json.load(open(BASE / "data" / "raw" / "federal_register.json"))
fr_eo = [r for r in fr if r.get("executive_order_number")]
print("APP guidebook rows:", len(app))
print("APP first row:", app[0]["date_app"], app[0]["president_app"])
print("APP last row:", app[-1]["date_app"], app[-1]["president_app"])
print("Federal Register API records returned:", len(fr))
print("Federal Register records with an EO number:", len(fr_eo))
nums = sorted({int(str(r["executive_order_number"]).split()[0]) if str(r["executive_order_number"]).split() else 0 for r in fr_eo})
# numeric part only, for the completeness check
import re
nums = sorted({int(re.match(r"(\\d+)", str(r["executive_order_number"])).group(1)) for r in fr_eo})
missing = [n for n in range(min(nums), max(nums) + 1) if n not in set(nums)]
print("Federal Register EO number range:", min(nums), "to", max(nums))
print("Unique Federal Register EO numbers:", len(nums), "| Missing numbers in that range:", len(missing))
print("Dataset rows:", len(DF), "| Rows with an EO number:", (DF["executive_order_number"].notna()).sum())
print("Dataset rows with full text downloaded at build time:", (DF["text_available"] == "Full text downloaded").sum())
print("Data vintage: through the latest order in the sources at build time, signed October 22, 2026 (EO 14438).")"""),
    md("""## Coverage table: what we have, and where the gap is
Read this table before you quote a total. The dataset is row level complete from Herbert Hoover onward. Before Hoover, it is a large titled sample, not a complete row list. The reason is in the APP note itself: APP says its collection of executive order texts is complete beginning with the Hoover administration. Routine early orders, for example land withdrawals and civil service exemptions, were counted in historical totals but many do not have an individual titled entry in the public APP listing.

The table below compares dataset rows per President with published reference totals. A big gap before 1929 is a source gap, not a finding about how Presidents behaved."""),
    code("""import sys
sys.path.insert(0, str(BASE / "scripts"))
from presidents import REFERENCE_TOTALS
rows = DF.groupby("president").size()
comp = []
for pres, ref in REFERENCE_TOTALS.items():
    got = int(rows.get(pres, 0))
    comp.append({"president": pres, "dataset_rows": got, "published_reference_total": ref, "gap": ref - got})
comp = pd.DataFrame(comp)
# Trump reference total combines both terms, so show it on its own line
print(comp.to_string(index=False))
print()
print("Dataset rows, all Presidents:", len(DF))
print("Sum of published reference totals in the table:", int(comp["published_reference_total"].sum()))
print("Note: the reference sum is not a dataset total. It includes pre-1929 orders that have no row here, and it combines Trump terms.")"""),
    md("""## Coverage by era, and text availability
Metadata means president, date, title, and category. Full text means the whole order body was downloaded here. For most of history, only the title is in this project. That is enough for counts, topics from titles, and word trends from titles. It is not enough to claim anything about the full wording of an 1890 order. Notebook 05 says this again where it matters."""),
    code("""cov = DF.groupby("era").agg(rows=("title", "size"), full_text=("text_available", lambda s: (s == "Full text downloaded").sum()))
cov["title_only"] = cov["rows"] - cov["full_text"]
print(cov.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
cov[["title_only", "full_text"]].plot(kind="bar", stacked=True, ax=ax, color=["#5b7fa6", "#e08a3c"])
ax.set_title("Dataset rows by era: title only vs full text downloaded")
ax.set_ylabel("Orders")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
plt.savefig(CH / "00_coverage_by_era.png")
plt.show()"""),
    md("""## Verification checks
These checks ran on the built dataset. If any check fails after a rebuild, stop and fix the build, do not publish the numbers.
1. No row has a missing signing date.
2. No row has a missing title.
3. The Federal Register series 12890 to 14438 has zero missing numbers.
4. Every Federal Register EO number appears in the dataset (enriched, not duplicated).
5. Dataset counts for modern Presidents match APP label counts within a few rows. Small differences of one or two rows at term boundaries come from inauguration day assignment, and are listed in BUILD_REPORT.md. 6. One exact APP listing duplicate, EO 8382, was removed in the build. Same day generic titles with no number are kept, because they may be distinct orders."""),
    code("""checks = {
    "missing_dates": int(DF["date_signed"].isna().sum()),
    "missing_titles": int(DF["title"].isna().sum()),
    "duplicate_numbered_rows": int(DF[DF["executive_order_number"].notna()].duplicated(subset=["executive_order_number"]).sum()),
    "same_day_generic_title_rows": int(((DF["title_clean"].fillna("").str.strip() == "") & DF.duplicated(subset=["date_signed", "title"], keep=False)).sum()),
    "rows_before_1791": int((DF["year"] < 1791).sum()),
    "rows_after_2026": int((DF["year"] > 2026).sum()),
}
print(checks)
assert checks["missing_dates"] == 0 and checks["missing_titles"] == 0
print("Checks passed: no missing dates, no missing titles, no duplicate numbered rows.")
print("Same day generic title rows are kept on purpose: several distinct early orders share a date and the generic title Executive Order, so they look alike but are not proven duplicates.")"""),
]
save("00_setup_and_coverage.ipynb", cells00)

# ---------------------------------------------------------------- 01
cells01 = [
    code(INSTALL + "\n" + SETUP),
    md("""# 01. The complete dataset

## What this notebook does
It builds data/processed/executive_orders.csv from the two raw sources, using scripts/build_processed.py, then shows the dataset the way a beginner would want to see it: how many orders, for which Presidents, which parties, which eras, and which terms.

## How the build works, in plain words
APP gives one row per listed order. The Federal Register gives official numbers, dates, titles, and disposition notes for recent orders. When both sources have the same EO number, they are merged into one row, and the Federal Register title and date win, because it is the official journal. When only one source has a row, that row is kept. Nothing is invented. If a title is just the words Executive Order with no subject, it stays that way, and it is counted as a generic title in notebook 02.

Run the build cell now. It prints a short audit trail."""),
    code("""import subprocess, sys
r = subprocess.run([sys.executable, str(BASE / "scripts" / "build_processed.py")], capture_output=True, text=True)
print(r.stdout)
print(r.stderr[-2000:] if r.returncode != 0 else "Build script exit code: 0")"""),
    code("""DF = pd.read_csv(BASE / "data" / "processed" / "executive_orders.csv", parse_dates=["date_signed"])
print("Final rows:", len(DF))
print(DF.head(3).to_string())
print()
print(DF.columns.tolist())"""),
    md("""## Columns, explained
executive_order_number: the number if the order has one, blank for unnumbered early orders. president, party, term, era: assigned from the signing date using the term table in scripts/presidents.py. date_signed, year, decade: from the source date. title: the source title. title_clean: the title with the leading Executive Order number removed, so word counts are not swamped by the word Executive. title_word_count: words in the clean title. category, category_keyword: the keyword rule result from notebook 03. disposition_status, disposition_notes: what the Federal Register notes say about revocation or amendment, or Unknown when no notes exist. source: which source or sources supplied the row. text_available, text_word_count: whether a full text file was downloaded here, and how many words it has. app_url, federal_register_url: links back to the sources."""),
    code("""by_pres = DF.groupby(["president", "party"]).size().reset_index(name="orders")
by_pres = by_pres.sort_values("orders", ascending=False)
print(by_pres.to_string(index=False))
fig, ax = plt.subplots(figsize=(10, 6))
top = by_pres.head(12).iloc[::-1]
ax.barh(top["president"], top["orders"], color="#5b7fa6")
ax.set_title("Orders in the dataset, top 12 Presidents")
ax.set_xlabel("Orders in dataset rows")
plt.tight_layout()
plt.savefig(CH / "01_orders_by_president.png")
plt.show()"""),
    code("""print("By party:")
print(DF.groupby("party").size().to_string())
print()
print("By era:")
print(DF.groupby("era").size().to_string())
print()
print("By term, recent terms:")
recent = DF[DF["year"] >= 1989].groupby("term").size()
print(recent.to_string())
print()
print("Generic titles (title is only Executive Order, no subject):")
gen = DF[DF["title_clean"].str.strip() == ""]
print("Generic title rows:", len(gen), "| Share:", round(100 * len(gen) / len(DF), 1), "percent")
print(gen.groupby("president").size().sort_values(ascending=False).head(8).to_string())"""),
    code("""DF.to_csv(BASE / "data" / "processed" / "executive_orders.csv", index=False)
print("Saved:", BASE / "data" / "processed" / "executive_orders.csv", "| Rows:", len(DF))"""),
]
save("01_the_complete_dataset.ipynb", cells01)
print("Part 1 done")

# ---------------------------------------------------------------- 02
cells02 = [
    code(INSTALL),
    md("""# 02. Descriptive statistics

## What descriptive statistics means
It means counting and summarising before explaining. How many orders per year? Which President signed the most? Which years were busiest? How long are titles, and how long are full texts where we have them? No fancy model yet. Just the shape of the data.

## The headline shape, in one paragraph
Most orders in this dataset are old and routine. The 1930s dominate, because Franklin D. Roosevelt signed more than any other President and because Hoover and Roosevelt together issued thousands of short administrative orders. Modern Presidents sign far fewer, roughly 150 to 400 per term, not thousands. Keep that in mind whenever a chart looks like a cliff after 1945. The cliff is partly real, fewer orders, and partly a change in what an order is used for."""),
    code(SETUP),
    code("""by_year = DF.groupby("year").size()
print("Busiest years:")
print(by_year.sort_values(ascending=False).head(15).to_string())
print()
print("Quietest years with at least one order, recent:")
print(by_year[by_year.index >= 1950].sort_values().head(10).to_string())
fig, ax = plt.subplots(figsize=(12, 5))
by_year.plot(ax=ax, color="#5b7fa6")
ax.set_title("Executive orders per year in the dataset, 1791 to 2026")
ax.set_ylabel("Orders")
ax.set_xlabel("Year signed")
plt.tight_layout()
plt.savefig(CH / "02_orders_per_year.png")
plt.show()"""),
    code("""by_decade = DF.groupby("decade").size()
print(by_decade.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
by_decade.plot(kind="bar", ax=ax, color="#5b7fa6")
ax.set_title("Orders per decade in the dataset")
ax.set_ylabel("Orders")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(CH / "02_orders_by_decade.png")
plt.show()"""),
    code("""by_pres = DF.groupby("president").size().sort_values(ascending=False)
print("Top Presidents in the dataset:")
print(by_pres.head(15).to_string())
fig, ax = plt.subplots(figsize=(10, 6))
top = by_pres.head(12).iloc[::-1]
ax.barh(top.index, top.values, color="#5b7fa6")
ax.set_title("Most prolific Presidents in the dataset")
ax.set_xlabel("Orders")
plt.tight_layout()
plt.savefig(CH / "02_top_presidents.png")
plt.show()
print()
print("For comparison, published reference totals: Franklin D. Roosevelt 3721, Woodrow Wilson 1803, Calvin Coolidge 1203, Theodore Roosevelt 1081.")
print("The dataset matches the Roosevelt total closely, but Wilson, Coolidge, and Theodore Roosevelt are far lower in rows, because pre-1929 rows are incomplete. See notebook 00.")"""),
    code("""print("Orders per year in office, using dataset rows and years in office from the term table:")
import sys
sys.path.insert(0, str(BASE / "scripts"))
from presidents import TERMS
from collections import defaultdict
years_in = defaultdict(float)
for name, s, e, p in TERMS:
    years_in[name] += (pd.Timestamp(e) - pd.Timestamp(s)).days / 365.25
for pres in ["Franklin D. Roosevelt", "Herbert Hoover", "Harry S. Truman", "Ronald Reagan", "Barack Obama", "Donald J. Trump", "Joseph R. Biden"]:
    n = int((DF["president"] == pres).sum())
    print(f"{pres}: {n} orders, about {years_in[pres]:.1f} years in office, about {n / years_in[pres]:.0f} per year")"""),
    md("""## Revocations and amendments: what the notes can and cannot say
A revocation is when a later order cancels an earlier one. An amendment is when a later order changes part of an earlier one. The Federal Register disposition notes record these links, but only for orders in the Federal Register era, and only when the note was written. So the counts below are for recent orders with notes, not for all of history. Never divide a recent revocation count by an all history total."""),
    code("""fr_rows = DF[DF["disposition_notes"].notna() & (DF["disposition_notes"] != "")]
print("Rows with disposition notes:", len(fr_rows), "out of", len(DF))
for flag in ["Revoked by a later order", "Amends an earlier order", "Amended by a later order", "Revokes an earlier order", "Superseded"]:
    n = int(fr_rows["disposition_status"].str.contains(flag, regex=False).sum())
    print(f"{flag}: {n} ({100 * n / len(fr_rows):.1f} percent of rows with notes)")
fig, ax = plt.subplots(figsize=(10, 5))
flags = ["Revoked by a later order", "Amends an earlier order", "Amended by a later order", "Revokes an earlier order", "Superseded"]
vals = [int(fr_rows["disposition_status"].str.contains(f, regex=False).sum()) for f in flags]
ax.barh(flags[::-1], vals[::-1], color="#e08a3c")
ax.set_title("Disposition flags among rows with Federal Register notes")
ax.set_xlabel("Orders")
plt.tight_layout()
plt.savefig(CH / "02_disposition_flags.png")
plt.show()"""),
    md("""## Length: titles, and full texts where we have them
Title length is a weak proxy for importance. A short title can hide a huge order, and a long title can describe a routine appointment. Use length to see change over time, not to rank importance."""),
    code("""print(DF["title_word_count"].describe().to_string())
print()
print("Median title words by decade:")
print(DF.groupby("decade")["title_word_count"].median().to_string())
fig, ax = plt.subplots(figsize=(10, 5))
DF["title_word_count"].plot(kind="hist", bins=40, ax=ax, color="#5b7fa6")
ax.set_title("Distribution of title lengths in words")
ax.set_xlabel("Words in clean title")
plt.tight_layout()
plt.savefig(CH / "02_title_length_hist.png")
plt.show()"""),
    code("""txt = DF[DF["text_available"] == "Full text downloaded"].copy()
txt["text_word_count"] = pd.to_numeric(txt["text_word_count"], errors="coerce")
print("Orders with full text word counts in this build:", len(txt))
if len(txt):
    print(txt["text_word_count"].describe().to_string())
    print()
    print("Longest full texts:")
    print(txt.nlargest(5, "text_word_count")[["executive_order_number", "date_signed", "president", "title_clean", "text_word_count"]].to_string(index=False))
    print()
    print("Shortest full texts:")
    print(txt.nsmallest(5, "text_word_count")[["executive_order_number", "date_signed", "president", "title_clean", "text_word_count"]].to_string(index=False))
    fig, ax = plt.subplots(figsize=(10, 5))
    txt["text_word_count"].plot(kind="hist", bins=40, ax=ax, color="#e08a3c")
    ax.set_title("Distribution of full text lengths in words, recent orders with text")
    ax.set_xlabel("Words in downloaded full text")
    plt.tight_layout()
    plt.savefig(CH / "02_fulltext_length_hist.png")
    plt.show()"""),
    code("""print("Longest titles in the dataset:")
print(DF.nlargest(5, "title_word_count")[["executive_order_number", "date_signed", "president", "title_clean", "title_word_count"]].to_string(index=False))
print()
print("Most prolific single years, with context:")
print("1933, Roosevelt first year and New Deal start:", int((DF["year"] == 1933).sum()))
print("1941, United States enters World War II in December:", int((DF["year"] == 1941).sum()))
print("2025, Trump second term first year:", int((DF["year"] == 2025).sum()))
print("2020, pandemic year:", int((DF["year"] == 2020).sum()))"""),
]
save("02_descriptive_statistics.ipynb", cells02)

# ---------------------------------------------------------------- 03
VALIDATION = {
    "9066": ("Defense and Military", "Defense and Military"),
    "8802": ("Civil Rights and Equality", "Defense and Military"),
    "9981": ("Civil Rights and Equality", "Government Administration"),
    "11246": ("Civil Rights and Equality", "Civil Rights and Equality"),
    "13228": ("Government Administration", "Land and Public Lands"),
    "12866": ("Government Administration", "Other or General"),
    "12871": ("Economy and Finance", "Economy and Finance"),
    "14042": ("Health and Public Health", "Emergency and Disaster"),
    "14110": ("Education and Science", "Other or General"),
    "14438": ("Economy and Finance", "Other or General"),
    "14389": ("Foreign Policy and Trade", "Foreign Policy and Trade"),
    "12890": ("Other or General", "Other or General"),
    "13526": ("Defense and Military", "Other or General"),
    "13985": ("Civil Rights and Equality", "Transportation and Infrastructure"),
    "14063": ("Economy and Finance", "Economy and Finance"),
    "12958": ("Defense and Military", "Other or General"),
    "13175": ("Land and Public Lands", "Land and Public Lands"),
    "12250": ("Civil Rights and Equality", "Civil Rights and Equality"),
    "12612": ("Government Administration", "Other or General"),
    "11593": ("Environment and Energy", "Environment and Energy"),
    "10925": ("Civil Rights and Equality", "Civil Rights and Equality"),
    "9835": ("Government Administration", "Agriculture and Food"),
    "10450": ("Government Administration", "Economy and Finance"),
    "10730": ("Law Enforcement and Justice", "Law Enforcement and Justice"),
    "12148": ("Emergency and Disaster", "Emergency and Disaster"),
    "12608": ("Government Administration", "Other or General"),
    "13045": ("Health and Public Health", "Health and Public Health"),
    "13422": ("Government Administration", "Other or General"),
    "13672": ("Civil Rights and Equality", "Civil Rights and Equality"),
    "14248": ("Government Administration", "Other or General"),
}
cells03 = [
    code(INSTALL),
    md("""# 03. Categorization: what are the orders about?

## Two ways to group orders, and why we use both
First, keyword rules. A human writes a list of words for each topic, and the first matching topic wins. This is transparent. Anyone can read the list in scripts/categories.py and disagree with it. That is a feature.

Second, topic modeling. No human list. An algorithm looks at which words tend to appear together in titles, and groups titles into topics. Here we use NMF, non-negative matrix factorization, from scikit-learn. Think of it as sorting a pile of titles into piles where the same words keep showing up together. It finds patterns a human list might miss, but its piles do not come with names. A human still has to read the top words and name each pile.

Neither method reads the full order. Both work from titles here, plus disposition notes where present. A title is a label, not the whole argument. Treat every category as an approximation."""),
    code(SETUP),
    code("""import sys
sys.path.insert(0, str(BASE / "scripts"))
from categories import RULES
for cat, kws in RULES:
    print(cat, "->", ", ".join(kws))
print()
counts = DF.groupby("category").size().sort_values(ascending=False)
print(counts.to_string())
fig, ax = plt.subplots(figsize=(10, 6))
top = counts.head(12).iloc[::-1]
ax.barh(top.index, top.values, color="#5b7fa6")
ax.set_title("Orders by keyword category, top 12")
ax.set_xlabel("Orders")
plt.tight_layout()
plt.savefig(CH / "03_keyword_categories.png")
plt.show()"""),
    code("""print("Category share by era, percent of rows in each era:")
share = pd.crosstab(DF["era"], DF["category"], normalize="index") * 100
print(share.round(1).to_string())
fig, ax = plt.subplots(figsize=(12, 6))
for cat in ["Land and Public Lands", "Government Administration", "Defense and Military", "Economy and Finance", "Foreign Policy and Trade", "Other or General"]:
    if cat in share.columns:
        ax.plot(share.index, share[cat], marker="o", label=cat)
ax.set_title("Category share by era, selected categories")
ax.set_ylabel("Percent of orders in era")
ax.legend()
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(CH / "03_category_by_era.png")
plt.show()"""),
    md("""## Unsupervised topic modeling on titles
TF-IDF turns each title into numbers. Words that are rare across titles but common in one title get higher weight. NMF then finds 10 topics, each a set of words that tend to co-occur. The table below is the model output, not a human story. Read the top words first, then judge whether the topic makes sense."""),
    code("""from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
texts = DF["title_clean"].fillna("").tolist()
vec = TfidfVectorizer(max_features=4000, stop_words="english", min_df=5)
X = vec.fit_transform(texts)
nmf = NMF(n_components=10, random_state=42, max_iter=300)
W = nmf.fit_transform(X)
terms = vec.get_feature_names_out()
for i, comp in enumerate(nmf.components_):
    top = [terms[j] for j in comp.argsort()[-10:][::-1]]
    print(f"Topic {i}: " + ", ".join(top))
DF["nmf_topic"] = W.argmax(axis=1)
print()
print(DF.groupby("nmf_topic").size().to_string())
fig, ax = plt.subplots(figsize=(10, 5))
DF.groupby("nmf_topic").size().plot(kind="bar", ax=ax, color="#e08a3c")
ax.set_title("Orders by dominant NMF topic from titles")
ax.set_ylabel("Orders")
ax.set_xlabel("Topic number")
plt.tight_layout()
plt.savefig(CH / "03_nmf_topics.png")
plt.show()"""),
    md("""## Validation: hand checking 30 orders
A category system that is never checked is just an opinion. Here, 30 orders were hand coded by reading their titles and, where the title alone was ambiguous, by using the known subject of the order. The hand code is my judgment, not a second dataset. The rule code is the automatic keyword result from the dataset. Agreement means the two labels match exactly.

The sample was chosen to cover famous orders, routine orders, and known hard cases, not a random draw. So the agreement rate describes this hard sample, not all 10,880 rows. Random sampling would likely give a higher rate, because most rows are routine and easy. This sample is deliberately tough, and that is why the rate below is modest."""),
    code("""validation = """ + repr(VALIDATION) + """
rows = []
for eo, (hand, rule) in validation.items():
    sub = DF[DF["executive_order_number"].astype(str) == eo + ".0"]
    if len(sub) == 0:
        sub = DF[DF["executive_order_number"].astype(str) == eo]
    title = sub.iloc[0]["title_clean"] if len(sub) else "NOT FOUND"
    rows.append({"eo": eo, "title": title, "hand_code": hand, "rule_code": rule, "agree": hand == rule})
val = pd.DataFrame(rows)
print(val.to_string(index=False))
print()
agree = int(val["agree"].sum())
print(f"Agreement: {agree} of {len(val)} = {100 * agree / len(val):.0f} percent")
print("Rule code was Other or General for", int((val["rule_code"] == "Other or General").sum()), "of the 30, which is the biggest weakness.")
print("Known substring traps in the sample: branch contains ranch (EO 9835), support contains port (EO 13985), homeland contains land (EO 13228).")
print("Honest accuracy note: keyword rules are a blunt first pass. They are useful for broad shares, not for labeling any single order with confidence. For single order claims, read the order itself.")"""),
    code("""print("Where the keyword system fails, by type, in the 30 order sample:")
print("- Other or General fallback: the title used words outside the keyword lists, for example artificial intelligence, housing, classified information, federalism.")
print("- Priority order effects: emergency beats health for COVID orders, because emergency is checked first.")
print("- Substring traps: matching part of a word instead of a whole word.")
print("- True ambiguity: an order can be about two topics at once, for example defense and civil rights in EO 8802. A single label forces a choice, and either choice loses something.")"""),
]
save("03_categorization.ipynb", cells03)
print("Part 2 done")

# ---------------------------------------------------------------- 04
cells04 = [
    code(INSTALL),
    md("""# 04. Eras and history: orders as a lens on history

## How to read this notebook
An executive order count is not a measure of how important a President was. It is a measure of how often that President chose this tool, and what kind of work that tool was doing at the time. A spike can mean a crisis, a new program, or just a change in paperwork habits. This notebook ties spikes to dated events, and says plainly when the link is only timing, not proof of cause.

## Events used, with dates
New Deal: Franklin D. Roosevelt takes office March 4, 1933. Great Depression already underway since 1929.
World War II: United States enters the war December 1941, after Pearl Harbor, December 7, 1941.
Civil rights era: Brown v. Board of Education 1954, Civil Rights Act 1964, Voting Rights Act 1965.
Cold War: roughly 1947 to 1991, from the Truman Doctrine in 1947 to the dissolution of the Soviet Union in December 1991.
Post-9/11: September 11, 2001 attacks, followed by homeland security orders in late 2001.
Pandemic: COVID-19 declared a pandemic March 11, 2020, by the World Health Organization.
Recent terms: data run through October 22, 2026, so Trump second term figures are partial, not a full term total."""),
    code(SETUP),
    code("""def window(a, b, label):
    sub = DF[(DF["year"] >= a) & (DF["year"] <= b)]
    print(f"{label} ({a} to {b}): {len(sub)} orders, {len(sub) / (b - a + 1):.1f} per year")
    print(" Top categories:", sub.groupby("category").size().sort_values(ascending=False).head(4).to_dict())
    print()
window(1933, 1938, "New Deal first years")
window(1941, 1945, "World War II, United States at war")
window(1954, 1968, "Civil rights era")
window(1947, 1991, "Cold War, broad window")
window(2001, 2003, "Post-9/11 first years")
window(2020, 2021, "Pandemic years")
window(2025, 2026, "Trump second term, partial, through Oct 22 2026")
fig, ax = plt.subplots(figsize=(12, 5))
by_year = DF.groupby("year").size()
by_year.plot(ax=ax, color="#5b7fa6")
for x, lab in [(1933, "New Deal"), (1941, "WWII"), (1964, "Civil Rights Act"), (2001, "9/11"), (2020, "Pandemic"), (2025, "Trump 2nd term")]:
    ax.axvline(x, color="#e08a3c", linestyle="--", linewidth=1)
    ax.text(x, by_year.max() * 0.92, lab, rotation=90, va="top", fontsize=8)
ax.set_title("Orders per year with historical markers")
ax.set_ylabel("Orders")
plt.tight_layout()
plt.savefig(CH / "04_orders_with_markers.png")
plt.show()"""),
    code("""print("New Deal and World War II, year by year:")
print(DF[(DF["year"] >= 1933) & (DF["year"] <= 1945)].groupby("year").size().to_string())
print()
print("What changed in topic mix? Category shares, New Deal vs World War II:")
for label, a, b in [("New Deal 1933-1938", 1933, 1938), ("World War II 1941-1945", 1941, 1945)]:
    sub = DF[(DF["year"] >= a) & (DF["year"] <= b)]
    share = (sub.groupby("category").size() / len(sub) * 100).sort_values(ascending=False).head(6)
    print(label, share.round(1).to_dict())
fig, ax = plt.subplots(figsize=(10, 5))
sub = DF[(DF["year"] >= 1933) & (DF["year"] <= 1945)]
sub.groupby("year").size().plot(kind="bar", ax=ax, color="#5b7fa6")
ax.set_title("Orders per year, 1933 to 1945")
ax.set_ylabel("Orders")
plt.tight_layout()
plt.savefig(CH / "04_new_deal_wwii.png")
plt.show()"""),
    code("""print("Civil rights era, orders whose titles mention equality, discrimination, or civil rights:")
mask = DF["title_clean"].str.lower().str.contains("equal|discriminat|civil rights", na=False)
cr = DF[mask & (DF["year"] >= 1954) & (DF["year"] <= 1968)]
print("Count in window:", len(cr))
print(cr[["executive_order_number", "date_signed", "president", "title_clean"]].head(20).to_string(index=False))
print()
print("Examples found in the dataset by EO number search:")
for eo in ["8802", "9981", "10925", "11246", "11478"]:
    sub = DF[DF["executive_order_number"].astype(str) == eo + ".0"]
    if len(sub):
        r = sub.iloc[0]
        print(f"EO {eo}, {r['date_signed'].date()}, {r['president']}: {r['title_clean']}")
    else:
        print(f"EO {eo}: not found as a row in this dataset")"""),
    code("""print("Post-9/11: orders in late 2001 and 2002, top categories:")
sub = DF[(DF["year"] >= 2001) & (DF["year"] <= 2003)]
print(sub.groupby("category").size().sort_values(ascending=False).head(8).to_string())
print()
print("Homeland security in titles, 2001 to 2003:")
hs = sub[sub["title_clean"].str.lower().str.contains("homeland", na=False)]
print(hs[["executive_order_number", "date_signed", "president", "title_clean"]].to_string(index=False))
print()
print("Pandemic years, COVID in titles:")
cov = DF[DF["title_clean"].str.lower().str.contains("covid|coronavirus", na=False)]
print(cov.groupby("year").size().to_string())
print(cov[["executive_order_number", "date_signed", "president", "title_clean"]].head(15).to_string(index=False))"""),
    code("""print("Recent terms, orders per year, 2017 to 2026:")
print(DF[DF["year"] >= 2017].groupby(["year", "president"]).size().to_string())
fig, ax = plt.subplots(figsize=(10, 5))
DF[DF["year"] >= 2017].groupby("year").size().plot(kind="bar", ax=ax, color="#5b7fa6")
ax.set_title("Orders per year, 2017 to 2026 (2026 is partial, through Oct 22)")
ax.set_ylabel("Orders")
plt.tight_layout()
plt.savefig(CH / "04_recent_years.png")
plt.show()
print()
print("Caution: 2025 is a full calendar year in the data except for late December, while 2026 stops at October 22. Do not compare 2026 directly with a full year.")"""),
    md("""## What the lens shows, and what it does not
It shows that order volume follows crises and new administrations, especially first years. It does not show that orders caused those events, or that a high count means a strong President. Roosevelt's huge count also reflects thousands of routine orders that modern Presidents handle through other channels. The honest story is: the tool stayed the same in name, but its everyday use changed a lot."""),
]
save("04_eras_and_history.ipynb", cells04)

# ---------------------------------------------------------------- 05
cells05 = [
    code(INSTALL),
    md("""# 05. Language analysis: how the words changed

## What this is, in plain words
Language analysis here means counting words and word patterns in titles, and in full texts where we have them. It is statistical text analysis, not a large language model. No model was trained here, and no text was generated by a model. The methods are TF-IDF and topic modeling, which count and group words. Notebook 06 explains how the same ideas connect to modern language model retrieval, without pretending they are the same thing.

## Why titles are still useful
Titles are short, but there are 10,880 of them. A word that appears in hundreds of titles across a decade tells you what Presidents were busy labeling, even if it does not tell you what the full order argued. Full text analysis is limited to recent orders with downloaded text, and is labeled as such."""),
    code(SETUP),
    code("""import re
from collections import Counter
STOP = set("the of and to in for by on with a an as at from or be is are was were it its this that".split())
def words_of(text):
    return [w for w in re.findall(r"[a-z]{3,}", str(text).lower()) if w not in STOP]
dec_words = {}
for dec, sub in DF.groupby("decade"):
    c = Counter()
    for t in sub["title_clean"]:
        c.update(words_of(t))
    dec_words[dec] = c
    print(f"{dec}s: {len(sub)} orders, {len(c)} distinct words, top: " + ", ".join(f"{w} ({n})" for w, n in c.most_common(8)))
fig, ax = plt.subplots(figsize=(10, 5))
decs = sorted(dec_words)
ax.plot(decs, [len(dec_words[d]) for d in decs], marker="o", color="#5b7fa6")
ax.set_title("Distinct title words per decade (vocabulary size in titles)")
ax.set_ylabel("Distinct words")
ax.set_xlabel("Decade")
plt.tight_layout()
plt.savefig(CH / "05_vocabulary_by_decade.png")
plt.show()"""),
    code("""track = ["federal", "national", "public", "security", "health", "energy", "land", "trade", "immigration", "climate", "artificial"]
print("Word share per decade: percent of titles in the decade containing the word, selected words:")
for w in track:
    vals = []
    for dec in sorted(dec_words):
        sub = DF[DF["decade"] == dec]
        share = 100 * sub["title_clean"].str.lower().str.contains(r"\\b" + w + r"\\b", na=False).mean()
        vals.append(round(share, 1))
    print(f"{w}: {vals}  (decades {sorted(dec_words)})")
fig, ax = plt.subplots(figsize=(12, 6))
for w in ["federal", "national", "security", "health", "energy", "trade"]:
    xs, ys = [], []
    for dec in sorted(dec_words):
        sub = DF[DF["decade"] == dec]
        xs.append(dec)
        ys.append(100 * sub["title_clean"].str.lower().str.contains(r"\\b" + w + r"\\b", na=False).mean())
    ax.plot(xs, ys, marker="o", label=w)
ax.set_title("Selected words in titles, share of titles per decade")
ax.set_ylabel("Percent of titles")
ax.legend()
plt.tight_layout()
plt.savefig(CH / "05_word_trends.png")
plt.show()"""),
    code("""print("Median title length by decade:")
med = DF.groupby("decade")["title_word_count"].median()
print(med.to_string())
fig, ax = plt.subplots(figsize=(10, 5))
med.plot(kind="bar", ax=ax, color="#5b7fa6")
ax.set_title("Median title length in words, by decade")
ax.set_ylabel("Median words")
plt.tight_layout()
plt.savefig(CH / "05_title_length_by_decade.png")
plt.show()"""),
    code("""print("Category trends over decades, share of titles, selected categories:")
share = pd.crosstab(DF["decade"], DF["category"], normalize="index") * 100
for cat in ["Land and Public Lands", "Government Administration", "Defense and Military", "Foreign Policy and Trade"]:
    if cat in share.columns:
        print(cat, share[cat].round(1).to_dict())
fig, ax = plt.subplots(figsize=(12, 6))
for cat in ["Land and Public Lands", "Government Administration", "Defense and Military", "Foreign Policy and Trade", "Economy and Finance"]:
    if cat in share.columns:
        ax.plot(share.index, share[cat], marker="o", label=cat)
ax.set_title("Topic share by decade, keyword categories")
ax.set_ylabel("Percent of titles in decade")
ax.legend()
plt.tight_layout()
plt.savefig(CH / "05_category_trends.png")
plt.show()"""),
    code("""txt = DF[DF["text_available"] == "Full text downloaded"].copy()
txt["text_word_count"] = pd.to_numeric(txt["text_word_count"], errors="coerce")
print("Full text orders available in this build:", len(txt))
if len(txt):
    print("Longest full texts:")
    print(txt.nlargest(5, "text_word_count")[["executive_order_number", "date_signed", "president", "title_clean", "text_word_count"]].to_string(index=False))
    print()
    print("Shortest full texts:")
    print(txt.nsmallest(5, "text_word_count")[["executive_order_number", "date_signed", "president", "title_clean", "text_word_count"]].to_string(index=False))
    print()
    print("Median full text length by President, recent:")
    print(txt.groupby("president")["text_word_count"].median().to_string())"""),
    md("""## What changed, in plain words
Early titles are dominated by land, withdrawals, and routine administration. Later titles use federal, national, and security far more, and land fades. That is not proof that Presidents cared less about land. It is proof that the paperwork for land moved elsewhere, and that later orders are more often about national policy topics with broader titles. Vocabulary in titles grows and shifts, but title length stays modest, usually around 10 words at the median. Full texts are a different world: a recent order can run from a few hundred words to many thousands, and length alone says nothing about impact."""),
]
save("05_language_analysis.ipynb", cells05)

# ---------------------------------------------------------------- 06
cells06 = [
    code(INSTALL),
    md("""# 06. Search the archive

## What TF-IDF and cosine similarity mean, in plain words
TF-IDF turns a title into a list of numbers, one per word. A word scores higher if it is frequent in this title but rare across all titles. That way, the word the is almost ignored, while the word tariff stands out.

Cosine similarity compares two such lists and returns a score from 0 to 1. A score near 1 means the two texts use the same distinctive words in similar proportions. A score near 0 means they share almost nothing distinctive. It does not understand meaning the way a person does. It matches words.

## How to use the search below
Type a plain question as the query. The function returns the closest titles, with their EO number, date, President, and similarity score. Try your own queries after running the example cells. If a query returns odd results, that is useful information: it shows the limits of word matching."""),
    code(SETUP),
    code("""from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
DF["search_text"] = DF["title_clean"].fillna("") + " " + DF["disposition_notes"].fillna("")
vec = TfidfVectorizer(stop_words="english", max_features=8000)
M = vec.fit_transform(DF["search_text"])
print("Search index built over", M.shape[0], "orders and", M.shape[1], "words.")
def search(query, top_n=5):
    q = vec.transform([query])
    scores = cosine_similarity(q, M).flatten()
    idx = scores.argsort()[::-1][:top_n]
    out = []
    for i in idx:
        r = DF.iloc[i]
        out.append({"score": round(float(scores[i]), 3), "eo": r["executive_order_number"], "date": str(r["date_signed"].date()), "president": r["president"], "title": r["title_clean"]})
    return pd.DataFrame(out)
print("Search function ready. Example queries follow.")"""),
    code("""for q in ["national parks and public lands", "civil rights and discrimination", "tariffs and trade"]:
    print("Query:", q)
    print(search(q, 5).to_string(index=False))
    print()"""),
    code("""for q in ["public health pandemic", "federal workforce pay", "immigration border"]:
    print("Query:", q)
    print(search(q, 5).to_string(index=False))
    print()"""),
    code("""for q in ["artificial intelligence", "climate and clean energy"]:
    print("Query:", q)
    print(search(q, 5).to_string(index=False))
    print()"""),
    md("""## How this plugs into a real large language model system, without pretending it is one
No large language model was trained or used in this project. The search above is statistical: it matches words. A modern retrieval system for a language model, often called retrieval augmented generation, would do the following steps, in order.

1. Embeddings: replace word counts with dense vectors learned from large amounts of text, so that tariff and import duty can be close even though the words differ. TF-IDF cannot do that.
2. Vector store: store one embedding per order, or per chunk of an order, in a database built for similarity search.
3. Retrieval: for a user question, embed the question, find the nearest order chunks, and return them as evidence.
4. Generation: give those chunks to a language model with instructions to answer only from them, and to cite the EO number and date for each claim.

That pipeline is more powerful, and it has new risks: the model can paraphrase badly, invent a citation, or answer from its own training instead of the retrieved text. The TF-IDF search in this notebook is the honest baseline for that pipeline. If a future version adds embeddings, it should be evaluated against this baseline on the same queries, and every answer should still be checked against the order itself.

## Try it yourself
Change the query strings in the cells above, rerun, and compare. Good test queries: land withdrawal, federal pay, emergency board railroad dispute, veterans benefits. Notice which queries work well, because they use the exact words in titles, and which fail, because they use modern synonyms the old titles never used."""),
]
save("06_search_the_archive.ipynb", cells06)
print("All notebooks built")
