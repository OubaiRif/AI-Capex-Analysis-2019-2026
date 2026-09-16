# AI Capex vs. Revenue (FY2019–2026)

How much of Big Tech's revenue is going into AI infrastructure, and how is each company actually paying for it? This project answers that using only primary sources — SEC filings, earnings call transcripts, and official press releases — not analyst estimates.

Five companies: Microsoft, Alphabet, Amazon, Meta, Oracle.

## What's in this repo

**Data pipeline**
- `fetch_sec_data.py` — pulls capex and revenue directly from SEC EDGAR's XBRL Company Facts API for all five companies, handles restated/duplicate filings, and stores results in a local SQLite database (`fin_data.db` — not included; regenerate by running this script).
- `explore_tags.py` — utility for discovering which XBRL tag a company uses for a given financial concept, since tag names vary by company and change over time (e.g. Amazon reports capex under a non-standard tag).

**Analysis & charts**
- `queries/capex_pct.sql` — computes capex as a percentage of revenue, per company per fiscal year.
- `plot_capex_pct.py` — generates the headline chart from live data.
- `plot_fy_windows.py` — generates a supporting chart showing each company's actual fiscal-year calendar coverage (Microsoft's fiscal year ends in June, Oracle's in May — neither aligns with the calendar-year companies).
- `capex_pct_chart.jpg`, `fy_windows.jpg`, `article_cover.jpg` — rendered output images.

**Manual disclosures layer**
- `ai_disclosures.csv` — hand-extracted findings per company on AI-specific revenue, forward capex guidance, depreciation/useful-life policy, and financing activity (debt raises, equity raises, joint ventures). Sourced from 10-Ks, 10-Qs, earnings call transcripts, and official investor-relations releases — third-party transcript sites were used only to locate the right document, never cited as the source of record.

**Methodology**
- `Methodology.odt` — full documentation of sourcing rules, tag-mapping decisions, verification steps, and known limitations.
- `data_map.csv` — the original data-needs planning document (source, method, and limitations per data point).

## How to run it

```bash
pip install requests python-dotenv pandas matplotlib
```

Create a `.env` file in the project root:
```
SEC_USER_AGENT=Your Name your.email@example.com
```
SEC requires a real, working contact in the User-Agent header on every request — this isn't optional, it's their fair-access policy.

Then:
```bash
python3 fetch_sec_data.py      # builds fin_data.db from scratch
python3 plot_capex_pct.py      # regenerates the headline chart
python3 plot_fy_windows.py     # regenerates the fiscal-year alignment chart
```

## Key findings

- Capex as a share of revenue held in a fairly steady band for most companies through 2023, then broke out sharply starting 2024 — Oracle led the shift by about a year, the other four followed in 2024.
- Oracle is the extreme case: capex went from ~4% of revenue in 2019 to a reported 83% in fiscal 2026, alongside a Remaining Performance Obligations (contracted backlog) figure of $638B, up 363% year-over-year, attributed mostly to AI compute contracts.
- All five companies disclosed unusual financing activity to fund the buildout, and no two took the same approach — from Microsoft funding its entire increase out of operating cash flow, to Amazon taking direct equity stakes in OpenAI and Anthropic while simultaneously being their cloud compute provider.

## Scope and limitations

- Five companies only — not representative of the broader AI infrastructure sector.
- Microsoft (June) and Oracle (May) fiscal year-ends don't align with the calendar-year companies (Alphabet, Amazon, Meta) — the "same" fiscal year label can span calendar windows up to ~7 months apart. See `fy_windows.jpg` and `Methodology.odt` for detail.
- Only Meta and Amazon disclosed isolated, AI-specific revenue figures; the other companies report AI revenue as part of a broader segment (Azure, AWS, Google Cloud) — flagged as "Partial" in `ai_disclosures.csv` rather than treated as precise.

## Author

Oubai Rifai — Data Analyst
