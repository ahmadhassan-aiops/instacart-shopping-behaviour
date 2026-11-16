"""Customers: how many orders they place and how loyal their baskets are (Q6, Q11)."""

import numpy as np
import streamlit as st

from lib import charts, data
from lib.ui import chart, footer, header, insight, section


def render() -> None:
    c = data.customers()
    t = data.tenure_summary()

    header(
        "Customer behaviour",
        "Customers",
        "How many orders customers place over their lifetime, and how much of each basket is a repeat purchase.",
    )

    k = st.columns(4)
    k[0].metric("Customers", f"{len(c):,}", border=True)
    k[1].metric("Median lifetime orders", f"{c['lifetime_orders'].median():.0f}", border=True)
    k[2].metric("Customers with 30+ orders", f"{(c['lifetime_orders'] >= 30).mean():.0%}", border=True)
    k[3].metric("Average reorder share", f"{c['reorder_share'].mean():.0%}", border=True)

    section("Orders per customer", "Q6. What is the distribution of the number of orders per customer?")
    chart(charts.bars(
        t["tenure"].astype(str).values, t["customer_share"].values,
        customdata=t[["customers"]].values,
        hover="%{x} orders<br><b>%{y:.1%} of customers</b> (%{customdata[0]:,})",
        xtitle="Lifetime orders placed", ytitle="Share of customers",
    ).update_yaxes(tickformat=".0%"))
    few = (c["lifetime_orders"] <= 5).mean()
    many = (c["lifetime_orders"] > 30).mean()
    insight(
        f"The distribution is strongly skewed to the right. <b>{few:.0%}</b> of customers have placed 5 orders "
        f"or fewer, while <b>{many:.0%}</b> have placed more than 30, up to the dataset's cap of 100. "
        "A small group of regulars places a large share of all orders."
    )
    st.caption(
        "Counted with each customer's lifetime order number. The file holds only a sample of each customer's "
        f"orders (about {c['orders_in_sample'].mean():.0f} each), so counting rows in the file would undercount."
    )

    section("Loyalty grows with every order", "Q11. What share of each customer's basket is a reorder?")
    show = t[t["tenure"] != "1"]
    fig = charts.bars(
        show["tenure"].astype(str).values, show["reorder_share"].values,
        customdata=show[["customers"]].values,
        hover="%{x} lifetime orders<br><b>%{y:.0%} of items are reorders</b><br>%{customdata[0]:,} customers",
        xtitle="Lifetime orders placed", ytitle="Average share of items that are reorders",
        text=[f"{v:.0%}" for v in show["reorder_share"]],
    )
    fig.update_yaxes(tickformat=".0%", range=[0, 0.85])
    chart(fig)
    insight(
        f"A customer on their 2nd or 3rd order reorders <b>{show.iloc[0]['reorder_share']:.0%}</b> of their "
        f"basket; one with more than 50 orders reorders <b>{show.iloc[-1]['reorder_share']:.0%}</b>. "
        "The climb is steepest in the first ten orders, which is where habits (and the \"Buy it again\" list) form. "
        "First-time customers are left out: by definition they cannot reorder yet."
    )

    section("Every customer's reorder share", "Distribution across customers who bought at least one item.")
    v = c["reorder_share"].dropna()


    counts, edges = np.histogram(v, bins=20, range=(0, 1))
    mids = [f"{edges[i]:.0%}-{edges[i + 1]:.0%}" for i in range(len(counts))]
    fig = charts.bars(
        mids, counts, hover="%{x} reorders<br><b>%{y:,} customers</b>",
        xtitle="Share of the customer's items that are reorders", ytitle="Customers",
    )
    fig.update_xaxes(nticks=10)
    chart(fig)
    zero = c[c["reorder_share"] == 0]
    insight(
        f"Customers spread across the whole range, centred near <b>{v.median():.0%}</b>. The "
        f"{(v == 0).mean():.0%} who have never reordered are mostly newcomers ("
        f"{(zero['lifetime_orders'] <= 2).mean():.0%} of them have placed only one or two orders), so they have "
        f"not had the chance yet. At the other end, {(v > 0.8).mean():.0%} reorder more than 80% of what they buy."
    )

    footer()
