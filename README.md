---
title: Instacart Shopping Behaviour
emoji: 🛒
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: cc-by-nc-nd-4.0
short_description: How 157,000 Instacart customers shop for groceries (EDA)
---

# How 157,000 Instacart customers shop for groceries

**Live app:** [instacart-shopping-behaviour.streamlit.app](https://instacart-shopping-behaviour.streamlit.app/) · **Notebook and project folder:** [AIOPS-Portfolio-Projects](https://github.com/ahmadhassan-aiops/AIOPS-Portfolio-Projects/tree/main/1.%20Data-analysis-with-python-Projects/Instacart-Analysis)

An interactive presentation of an exploratory data analysis by **Ahmad Hassan** (AI Engineer).
It opens straight onto the findings; there is nothing to upload.

- **Key findings**: five headline results with the numbers behind them, and what the business could do about them.
- **When people shop**: hour × day heatmap, time of day, day of week, Wednesday vs Saturday, days between orders.
- **What they buy**: best sellers, first item in the cart, departments, aisles, basket size.
- **Customers**: lifetime orders per customer, and how the reorder share grows with every order.
- **Reorders**: most reordered products, reorder rate by department, popularity vs reorder rate, product search.
- **Data & method**: the raw tables, every cleaning decision and why, the twelve questions, and the limits of the data.

Notebook (updated with the corrections described in the app): [AIOPS-Portfolio-Projects / Instacart-Analysis](https://github.com/ahmadhassan-aiops/AIOPS-Portfolio-Projects/tree/main/1.%20Data-analysis-with-python-Projects/Instacart-Analysis)

## How it is built

```
app.py            entry point (top navigation)
nav.py            page registry
views/            one module per page
lib/data.py       cached loaders for data/
lib/charts.py     Plotly styling and chart builders
lib/ui.py         headers, insight callouts, footer
build_data.py     offline: raw CSVs -> data/*.parquet + data/meta.json
data/             ~2 MB of pre-computed summaries (shipped with the app)
Dockerfile        Hugging Face Docker Space (port 7860)
```

The raw data (five CSVs, about 110 MB) is never deployed. `build_data.py` cleans it and writes the
small summaries the app reads, so the app starts fast and fits any free host.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the summaries after changing the analysis:

```bash
python build_data.py "path/to/Instacart-Analysis"   # folder with the 5 semicolon-separated CSVs
```

## Data

A sample of the public Instacart Market Basket dataset (2017). Independent analysis, not affiliated with or
endorsed by Instacart.
