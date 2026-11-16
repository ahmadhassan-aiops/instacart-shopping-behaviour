"""Data & method: the source tables, the cleaning decisions, the twelve questions and the limits."""

import pandas as pd
import streamlit as st

from lib import data
from lib.ui import footer, header, section


def render() -> None:
    m = data.meta()
    cl = m["cleaning"]
    rs = m["raw_shapes"]

    header(
        "Data & method",
        "How the analysis was done",
        "The data, the cleaning decisions and why each was made, and the questions the analysis answers. "
        f'The full Python work is in the <a href="{data.NOTEBOOK_URL}" target="_blank">original notebook</a>.',
    )

    section("The data")
    st.markdown(
        "A sample of the public **Instacart Market Basket** dataset (2017), as five semicolon-separated tables. "
        "The data has no calendar dates, only day of week, hour and days since the previous order."
    )
    st.table(
        pd.DataFrame([
            ("instacart_orders", "One row per order: customer, order number, day, hour, days since the previous order", *rs["instacart_orders"]),
            ("order_products", "One row per item in an order: product, position in the cart, reordered or not", *rs["order_products"]),
            ("products", "Product catalogue with its aisle and department", *rs["products"]),
            ("aisles", "Aisle names", *rs["aisles"]),
            ("departments", "Department names", *rs["departments"]),
        ], columns=["Table", "What it holds", "Rows", "Columns"]).assign(Rows=lambda d: d["Rows"].map("{:,}".format)),
        hide_index=True, border="horizontal",
    )
    with st.expander("Look at the raw data (50 random rows per table)"):
        tabs = st.tabs(["Orders", "Order items", "Products", "Aisles", "Departments"])
        for tab, name in zip(tabs, ["orders", "order_products", "products", "aisles", "departments"]):
            with tab:
                st.dataframe(data.table(f"sample_{name}"), hide_index=True, height=300)

    section("Cleaning decisions")
    st.markdown(
        "Every issue found while checking the tables, and how it was handled. Three of them were revisited "
        "for this app after a closer look at *why* the values were missing."
    )
    st.table(
        pd.DataFrame([
            ("Duplicate orders", f"{cl['duplicate_orders']} identical rows in instacart_orders, all at the same "
             "day and hour (likely a logging error)", "Removed"),
            ("Missing days since previous order", f"{cl['first_orders']:,} rows, and every one is the customer's "
             "first order: there is no previous order to measure from", "Kept as first orders and left out of the "
             "gap statistics. The notebook filled them with the mean; that would invent an 11-day gap for new customers"),
            ("Missing cart position", f"{cl['missing_cart_position_rows']} items in {cl['missing_cart_position_orders']} "
             f"orders, all orders of {cl['missing_cart_position_min_order_size']}+ items: the system stops numbering "
             "after position 64", f"Kept, because they are real purchases. Dropping them (as the notebook did) "
             f"capped the largest order at 64 items; it is really {m['items_max']}"),
            ("Missing product names", f"{cl['unnamed_products']:,} products in the catalogue",
             "Labelled \"Unnamed product\" so their sales still count in department totals"),
            ("Float columns", "add_to_cart_order and days_since_prior_order were stored as decimals", "Converted to whole numbers"),
            ("Day of week coding", "order_dow runs 0 to 6", "Read as 0 = Sunday. The notebook's Wednesday vs Saturday "
             "comparison used days 4 and 0; this app uses 3 and 6"),
        ], columns=["Issue", "What was found", "How it was handled"]),
        hide_index=True, border="horizontal",
    )

    section("The twelve questions")
    st.table(
        pd.DataFrame([
            ("Q1", "Are the hour (0-23) and day (0-6) values sensible?", "Yes: 24 hours and 7 days, no stray values"),
            ("Q2", "What time of day do people shop?", "When people shop"),
            ("Q3", "What day of the week do people shop?", "When people shop"),
            ("Q4", "How long do people wait between orders?", "When people shop"),
            ("Q5", "Do Wednesday and Saturday differ by hour?", "When people shop"),
            ("Q6", "How many orders does each customer place?", "Customers"),
            ("Q7", "What are the 20 most popular products?", "What they buy"),
            ("Q8", "How many items are in a typical order?", "What they buy"),
            ("Q9", "Which 20 items are reordered most?", "Reorders"),
            ("Q10", "For each product, what share of its orders are reorders?", "Reorders"),
            ("Q11", "For each customer, what share of their items are reorders?", "Customers"),
            ("Q12", "Which 20 items go into the cart first?", "What they buy"),
        ], columns=["#", "Question", "Answered on"]),
        hide_index=True, border="horizontal",
    )

    section("Limits of this data")
    st.markdown(
        "- **It is a sample.** Each customer has only a few of their orders in the file, so lifetime order "
        "counts come from the order number, not from counting rows.\n"
        "- **No dates or prices.** Seasonality, spend and basket value can't be studied.\n"
        "- **Gaps are capped at 30 days**, so \"30\" means \"30 or more\".\n"
        "- **Descriptive, not causal.** The recommendations are hypotheses to test, not proven effects."
    )

    section("How this app is built")
    st.markdown(
        "Python, pandas and Plotly in a Streamlit app. The 110 MB of raw CSVs are cleaned and summarised once by "
        "`build_data.py` into about 2 MB of Parquet files that ship with the app, so it opens instantly without "
        f"uploading anything. Data summaries built on {m['built']}."
    )

    footer()
