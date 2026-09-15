# Interactive BI Analytics Dashboard

Explore which regions, products and customer segments contribute to revenue and profit, then inspect and export the supporting records.

An independent Streamlit portfolio project demonstrating filters, aggregations, KPI presentation and interactive exploration. **The data is synthetic, generated locally with a fixed random seed. It is not a live business feed or an enterprise deployment.**

[Portfolio case study](https://amitkumaranalytics.com/projects/interactive-analytics-dashboard) · [About Amit](https://amitkumaranalytics.com)

## What to explore

| View | Question it helps investigate |
|---|---|
| Overview | How do revenue and profit vary over time, by region and by channel? |
| Product Analysis | Which product lines contribute revenue, profit and orders? |
| Customer Insights | How do revenue and average order value differ across segments? |
| Detailed Data | Which records support the displayed summaries? |

The sidebar filters by date, region, product, customer segment and sales channel. Daily, weekly and monthly aggregations support different reporting views. CSV downloads provide filtered records, monthly summaries and product analysis.

## Data and metric definitions

`load_data()` generates one row per calendar day from January 2023 through December 2024. Each row receives a region, product, segment and channel; it represents a synthetic daily observation, not an individual customer transaction.

- Revenue and orders: sums across selected rows.
- Profit: generated revenue minus generated cost.
- Displayed profit margin: the arithmetic mean of row-level margins, **not** total profit divided by total revenue.
- Segment and product average order value: aggregated revenue divided by aggregated orders.
- Date presets are relative to the latest date in the sample, not today's date.

The previous-period option is exploratory. Its inclusive date boundaries currently produce unequal period lengths, and early selections may lack a complete comparison period. Treat its percentage changes accordingly.

## Run locally

Use **Python 3.12 or newer**: the current application uses f-string syntax introduced in Python 3.12.

```bash
git clone https://github.com/amit1820/interactive-bi-analytics-app.git
cd interactive-bi-analytics-app
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Then:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. No API key, database or uploaded dataset is required.

## A short walkthrough

1. Start with all dimensions selected and the default six-month sample window.
2. Review revenue, profit and orders in Overview.
3. Select one region and compare products and customer segments.
4. Inspect the underlying daily observations in Detailed Data.
5. Export a CSV to examine the same filtered population outside the app.

## Implementation

`app.py` contains cached sample-data generation, sidebar controls, pandas filtering and aggregation, Plotly charts and CSV exports. `requirements.txt` lists the dependencies.

To connect real data, replace `load_data()` and define its grain, currency, date coverage and validation rules before reusing the KPI calculations.

## Current limits

- Synthetic data cannot establish measured business impact.
- No authentication, persistent database or scheduled ingestion is implemented.
- Empty or very small selections need stronger handling, particularly when fitting trend lines.
- Period comparison coverage and metric definitions need review before production use.
- Dependencies use minimum versions rather than a reproducible lockfile.
- Exports are CSV; Excel and PDF exports are not implemented.

Built by [Amit Kumar](https://amitkumaranalytics.com).
