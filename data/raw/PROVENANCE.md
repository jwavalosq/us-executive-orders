# PROVENANCE.md: every source, with URL and what was taken from it

## 1. American Presidency Project, guidebook listing of executive orders

- URL: https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/executive-orders-beginning-with-jq-adams
- Paginated as ?page=0 through ?page=217, 50 rows per page except the last page with 30 rows.
- What was taken: president as listed, date, title, and the link to each order page. Saved as data/raw/app_guidebook.json, 10,880 rows, October 22, 2026 back to January 22, 1791.
- Note from the source itself: APP says its collection of executive order texts is complete beginning with the administration of Herbert Hoover. That is why pre-Hoover rows are a sample, not a complete list. See notebook 00.
- Summary page, for context: https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/executive-orders-beginning-with-jq-adams

## 2. Federal Register API, presidential documents of type executive_order

- API base: https://www.federalregister.gov/api/v1/documents.json
- Query used: conditions[presidential_document_type]=executive_order, conditions[type]=PRESDOCU, fields executive_order_number, title, signing_date, publication_date, abstract, disposition_notes, html_url, pdf_url, document_number, citation, ordered by executive_order_number, 1000 per page.
- What was taken: EO number, title, signing date, publication date, disposition notes, HTML and PDF links, document number, citation. Saved as data/raw/federal_register.json, 1,574 records returned, 1,552 with an EO number, 1,549 unique EO numbers from 12890 to 14438, zero missing numbers in that range.
- Abstract field: empty for presidential documents in this API response, so no abstract column is claimed in the dataset.

## 3. Federal Register full text pages

- Pattern: https://www.federalregister.gov/documents/full_text/text/YYYY/MM/DD/DOCUMENT-NUMBER.txt
- What was taken: the full text body for each unique EO number in the Federal Register download, saved as one text file per EO number in data/raw/fr_texts/, with word counts in the dataset as text_word_count. Only the word count is in the CSV, not the full text, to keep the CSV usable.
- Note: the text files are listed in .gitignore, because they are large and rebuildable from the script scripts/fetch_fr_texts.py.

## 4. National Archives, Executive Orders Disposition Tables

- Index URL: https://www.archives.gov/federal-register/executive-orders/disposition.html
- What was taken: context only, for cross checking that disposition tables list EO number, signing date, Federal Register citation, title, amendments, and current status, and that they are arranged by administration beginning with Franklin D. Roosevelt. No rows were scraped from these tables for this build, because the APP plus Federal Register union already covers the recent series completely, and the tables do not cover pre-1937 orders.

## 5. Published per President totals, reference only

- Source: American Presidency Project executive orders counts table, by Gerhard Peters, via the APP executive orders summary.
- Cross check: Competitive Enterprise Institute, Table 4, Executive Orders by Administration, which tabulates National Archives disposition tables and APP data. URL: https://cei.org/wp-content/uploads/2023/11/table-4.pdf
- What was taken: reference totals per President, stored in scripts/presidents.py as REFERENCE_TOTALS, used only for the coverage comparison in notebook 00. These totals are not rows in the dataset.
- Known differences between sources: the APP counts table gives Franklin D. Roosevelt 3,721, while the CEI table gives 3,467 for the numbered series, a difference explained by unnumbered and early orders counted differently. Herbert Hoover is 968 in CEI and about 996 to 1,003 in APP based counts. These differences are why this project never quotes a single total without naming its source.

## 6. Historical event dates used in notebook 04

- New Deal start: Franklin D. Roosevelt takes office March 4, 1933.
- Pearl Harbor: December 7, 1941, United States enters World War II in December 1941.
- Brown v. Board of Education: 1954. Civil Rights Act: 1964. Voting Rights Act: 1965.
- Truman Doctrine: 1947. Dissolution of the Soviet Union: December 1991.
- September 11, 2001 attacks.
- COVID-19 declared a pandemic: March 11, 2020, World Health Organization.
- These are standard historical dates, used only to label windows, not as dataset rows.

## Data vintage

Through October 22, 2026, the latest order in the sources at build time, EO 14438, Decreasing Housing Costs for the American People. The 2026 total is partial.
