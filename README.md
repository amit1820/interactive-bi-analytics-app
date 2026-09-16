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
- Profit margin: total profit divided by total revenue, consistently applied to KPIs, product summaries and monthly exports. Margin comparisons use percentage points; daily records retain their row-level margins.
- Segment and product average order value: aggregated revenue divided by aggregated orders.
- Date presets are relative to the latest date in the sample, not today's date.

Previous-period comparisons use the immediately preceding window with the same number of inclusive calendar days and the same dimension filters. Changes are hidden when either window lacks full sample coverage or no prior records match. Percentage changes with zero or negative baselines are unavailable. Last 30/90 Days includes exactly 30/90 days; Last 6 Months uses a calendar-month offset.

## Run locally

Use **Python 3.10 or newer**.

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

`app.py` contains cached sample-data generation, sidebar controls, pandas filtering and aggregation, Plotly charts and CSV exports. `metrics.py` defines comparison windows and KPI calculations. `requirements.txt` lists the runtime dependencies.

To connect real data, replace `load_data()` and define its grain, currency, date coverage and validation rules before reusing the KPI calculations.

## Regression checks

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover inclusive comparison windows, missing dates, metric calculations, exact presets, empty filters and recovery, partial date selection, unavailable comparisons and single-bucket charts. Trend lines require at least two time buckets.

## Current limits

- Synthetic data cannot establish measured business impact.
- No authentication, persistent database or scheduled ingestion is implemented.
- Dependencies use minimum versions rather than a reproducible lockfile.
- Exports are CSV; Excel and PDF exports are not implemented.

Built by [Amit Kumar](https://amitkumaranalytics.com).

