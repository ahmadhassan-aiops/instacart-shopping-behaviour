"""What they buy: top products, first in cart, departments, aisles, basket size (Q7, Q8, Q12)."""

import streamlit as st

from lib import charts, data
from lib.ui import chart, footer, header, insight, section


def render() -> None:
    m = data.meta()
    p = data.products()

    header(
        "Products & baskets",
        "What they buy",
        "Which products sell, which go into the cart first, and how big a typical basket is.",
    )

    section("Best-selling products", "Q7 and Q12. The most popular products, and the items people add to the cart first.")
    a, b = st.columns([2, 1])
    rank = a.segmented_control(
        "Rank by", ["Times ordered", "First item in the cart"], default="Times ordered",
        key="rank_by", label_visibility="collapsed",
    ) or "Times ordered"
    n = b.slider("How many products", 5, 40, 15, key="top_n")
    col = "orders" if rank == "Times ordered" else "first_in_cart"
    top = p.nlargest(n, col)
    word = "orders" if col == "orders" else "times first in cart"
    chart(charts.bars(
        top["product_name"].values, top[col].values, horizontal=True,
        customdata=top[["department"]].values,
        hover=f"<b>%{{y}}</b><br>%{{x:,}} {word}<br>%{{customdata[0]}}",
        xtitle="Times ordered" if col == "orders" else "Times added to the cart first",
    ), key=f"top_{col}")
    top10 = p.nlargest(10, "orders")
    produce_in_top10 = int((top10["department"] == "produce").sum())
    lines_top1pct = p.nlargest(max(1, len(p) // 100), "orders")["orders"].sum() / p["orders"].sum()
    if col == "orders":
        insight(
            f"<b>{produce_in_top10} of the top 10</b> are fresh produce; bananas alone were ordered "
            f"{top10.iloc[0]['orders']:,} times. The catalogue has a very long tail: the top 1% of products "
            f"account for <b>{lines_top1pct:.0%}</b> of all items bought."
        )
    else:
        fc = p.groupby("department")["first_in_cart"].sum()
        insight(
            "The first item in the cart is usually a staple: bananas, milk, berries, avocados, water. "
            f"Produce and dairy together are <b>{(fc['produce'] + fc['dairy eggs']) / fc.sum():.0%}</b> of first "
            "items, so customers start their shop with fresh food."
        )

    left, right = st.columns(2, gap="large")
    d = data.departments()
    with left:
        section("Departments", "Share of all items bought, by department.")
        chart(charts.bars(
            d["department"].str.capitalize().values, d["share"].values, horizontal=True,
            highlight=(d.index < 2), customdata=d[["orders"]].values,
            hover="<b>%{y}</b><br>%{x:.1%} of items (%{customdata[0]:,})",
        ).update_xaxes(tickformat=".0%"))
        insight(
            f"Produce (<b>{d.iloc[0]['share']:.0%}</b>) and dairy & eggs (<b>{d.iloc[1]['share']:.0%}</b>) "
            "are nearly half of everything bought."
        )
    with right:
        al = data.aisles()
        section("Aisles", "Share of all items bought, by aisle.")
        k = st.slider("Top aisles", 10, 30, 15, key="top_aisles")
        top_a = al.head(k)
        chart(charts.bars(
            top_a["aisle"].str.capitalize().values, top_a["share"].values, horizontal=True,
            customdata=top_a[["orders"]].values,
            hover="<b>%{y}</b><br>%{x:.1%} of items (%{customdata[0]:,})",
        ).update_xaxes(tickformat=".0%"))
        insight(
            f"Of {m['aisles']} aisles, fresh fruits and fresh vegetables alone are "
            f"<b>{al.iloc[:2]['share'].sum():.0%}</b> of items."
        )

    section("Basket size", "Q8. How many items do people buy in one order?")
    s = data.table("order_sizes")
    c = st.columns(3)
    c[0].metric("Median basket", f"{m['items_median']:.0f} items", border=True)
    c[1].metric("Average basket", f"{m['items_mean']:.1f} items", border=True)
    c[2].metric("Largest order", f"{m['items_max']} items", border=True)
    show = s[s["items"] <= 60]
    fig = charts.bars(
        show["items"].values, show["orders"].values,
        customdata=(show["orders"] / s["orders"].sum()).values,
        hover="%{x} items<br><b>%{y:,} orders</b> (%{customdata:.1%})",
        xtitle="Items in the order (up to 60 shown)", ytitle="Orders",
    )
    charts.vline(fig, m["items_median"], f"Median {m['items_median']:.0f}")
    chart(fig)
    small = s.loc[s["items"] <= 15, "orders"].sum() / s["orders"].sum()
    big = s.loc[s["items"] > 40, "orders"].sum() / s["orders"].sum()
    insight(
        f"The most common basket is <b>{int(s.loc[s['orders'].idxmax(), 'items'])} items</b>, and "
        f"<b>{small:.0%}</b> of orders have 15 items or fewer. Only {big:.1%} have more than 40: this is a "
        "top-up service more than a once-a-month bulk shop."
    )

    footer()
