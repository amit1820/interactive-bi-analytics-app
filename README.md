# Revenue Atlas

A commercial analytics workspace for understanding recurring revenue growth and customer retention. Built with Python, pandas, Plotly and Streamlit by [Amit Kumar](https://amitkumaranalytics.com).

**Independent portfolio project. All accounts, invoices and commercial outcomes are synthetic.** No real customer records, measured business impact or predictive claims.

## Explore

- **Executive overview:** MRR, annualized run rate, active customers and net revenue retention. A calculated narrative explains the selected month's changes.
- **Revenue movements:** a reconciled waterfall separates new business, expansion, contraction and churn. Historical stacked movements explain growth composition.
- **Customer retention:** customer and revenue cohort heatmaps, plus comparisons at a common cohort age. Future observations remain blank.
- **Customer explorer:** search accounts and trace their monthly balances to supporting invoices.
- **Data & definitions:** calculation rules and a ZIP download of the linked source tables, respecting current filters and reporting month.

## Local setup (Windows PowerShell)

Use Python 3.10 or newer. From the repository directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On macOS/Linux, use `python3 -m venv .venv` and `.venv/bin/python` for the remaining commands. No database, API credentials or Docker are needed.

## Data model

`revenue.py` generates 600 accounts with seed 42 across January 2023–December 2025:

| Table | Grain | Links |
|---|---|---|
| Customers | One account | customer_id |
| Subscriptions | One monthly subscription per account | customer_id, subscription_id |
| Invoices | One active subscription per month | customer_id, subscription_id, invoice_id |
| Cancellations | One cancellation event | customer_id, subscription_id |

Acquisition segment, region and channel stay fixed. Monthly price changes model expansion and contraction. Cancellation takes effect before billing that month. There are no reactivations, annual plans, taxes, prorations, refunds or payment defaults. Monthly invoice amount equals month-end MRR under these simplifying assumptions; it is not cash collection data.

Segment-specific starting price and cancellation assumptions are illustrative. Retention patterns are generated, not evidence about a real business.

## Metric contract

- Closing MRR = opening MRR + new + expansion − contraction − churn.
- NRR = current MRR from the opening customer base / opening MRR.
- GRR = (opening MRR − contraction − churn) / opening MRR.
- Customer churn = opening customers lost / opening active customers.
- Annualized run rate = current MRR × 12; not realized annual revenue or a forecast.
- Customer cohort retention uses original cohort size; revenue cohort retention uses original cohort MRR. Revenue retention can exceed 100%.
- Empty denominators display unavailable values. First-month comparisons have no opening base.
- Filters apply fixed customer attributes to both sides of comparisons. All views and exports end at the selected reporting month; future cohort ages remain missing.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Tests verify keys and relationships, cancellation timing, invoice totals, all monthly bridges by segment, independently calculated movement examples, cohort censoring, reproducibility, every page at initial and final reporting months, empty filters and search.

## Hosting

Streamlit Community Cloud entry point: `app.py`; dependencies: `requirements.txt`. The app generates its sample locally and needs no secrets. This repository does not imply an already deployed public URL.

## Scope

This upgrade replaces the original random daily-observation BI dashboard. The focus is traceable commercial analysis and explicit metric definitions. Scenario forecasting, actual-versus-target reporting and predictive customer risk scoring are not implemented. Real adoption would require source contracts, billing edge-case handling, access control and validated revenue accounting policies.
