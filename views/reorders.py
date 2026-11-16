"""Reorders: which products customers come back for (Q9, Q10)."""

import plotly.graph_objects as go
import streamlit as st

from lib import charts, data
from lib.ui import chart, footer, header, insight, section


def render() -> None:
    m = data.meta()
    p = data.products()
    d = data.departments()

    header(
        "Repeat purchases",
        "Reorders",
        f"<b>{m['reorder_rate']:.0%}</b> of all items bought were reorders: products the customer had bought "
        "before. Here is which products and departments earn that loyalty.",
    )

    section("Most reordered products", "Q9. Which items are reordered most often?")
    n = st.slider("How many products", 5, 40, 15, key="reorder_n")
    top = p.nlargest(n, "reorders")
    chart(charts.bars(
        top["product_name"].values, top["reorders"].values, horizontal=True,
        customdata=top[["reorder_rate", "orders"]].values,
        hover="<b>%{y}</b><br>%{x:,} reorders<br>%{customdata[0]:.0%} of its %{customdata[1]:,} orders",
        xtitle="Times reordered",
    ), key="top_reorders")
    overlap = len(set(p.nlargest(20, "orders")["product_id"]) & set(p.nlargest(20, "reorders")["product_id"]))
    insight(
        f"<b>{overlap} of the top 20</b> reordered products are also in the top 20 best sellers. "
        "Popularity and loyalty go together: what people buy most is what they come back for."
    )

    section("Reorder rate by department", "Q10, rolled up. What share of each department's items are reorders?")
    dd = d[~d["department"].isin(["missing", "other"])].sort_values("reorder_rate", ascending=False)
    fig = charts.bars(
        dd["department"].str.capitalize().values, dd["reorder_rate"].values, horizontal=True,
        highlight=(dd["reorder_rate"] >= m["reorder_rate"]).values,
        customdata=dd[["orders"]].values,
        hover="<b>%{y}</b><br>%{x:.0%} reordered<br>%{customdata[0]:,} items bought",
    )
    fig.update_xaxes(tickformat=".0%")
    charts.vline(fig, m["reorder_rate"], f"All items {m['reorder_rate']:.0%}", bottom=True)
    chart(fig)
    insight(
        "Departments above the overall rate (highlighted) are mostly everyday perishables (dairy, beverages, "
        "produce, bakery, deli), plus pet food. Things that last, like <b>pantry</b> goods and <b>personal care</b>, are reordered least, "
        "because people simply need them less often."
    )

    section("Popularity vs reorder rate", "Q10. For each product, what percentage of its orders are reorders?")
    a, b = st.columns(2)
    min_orders = a.select_slider(
        "Only products ordered at least", options=[10, 25, 50, 100, 250, 500, 1000], value=100, key="min_orders",
    )
    depts = ["All departments"] + sorted(d["department"].str.capitalize())
    pick = b.selectbox("Highlight a department", depts, key="dept_pick")
    q = p[p["orders"] >= min_orders]


    fig = go.Figure()
    sel = q["department"].str.capitalize() == pick if pick != "All departments" else None
    groups = [(q, charts.BLUE, "Products")] if sel is None else [
        (q[~sel], charts.QUIET, "Other departments"), (q[sel], charts.BLUE, pick),
    ]
    for g, color, name in groups:
        fig.add_trace(go.Scattergl(
            x=g["orders"], y=g["reorder_rate"], mode="markers", name=name,
            marker=dict(color=color, size=7, opacity=0.6 if sel is None or color == charts.BLUE else 0.4,
                        line=dict(width=0.5, color=charts.SURFACE)),
            customdata=g[["product_name", "department"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{x:,} orders, %{y:.0%} reordered<extra></extra>",
        ))
    charts.style(fig, height=440, legend=sel is not None)
    fig.update_xaxes(type="log", title="Times ordered (log scale)", showgrid=True, gridcolor=charts.GRID)
    fig.update_yaxes(title="Share of orders that are reorders", tickformat=".0%", range=[0, 1])
    chart(fig, key="scatter")
    rho = q[["orders", "reorder_rate"]].corr(method="spearman").iloc[0, 1]
    hits = p[p["orders"] >= 5000]
    insight(
        f"{len(q):,} products shown. Reorder rate rises with popularity (Spearman correlation "
        f"<b>{rho:.2f}</b>, a moderate link). Of the {len(hits)} products ordered 5,000+ times, "
        f"<b>{(hits['reorder_rate'] >= 0.6).mean():.0%}</b> are reordered at least 60% of the time, while "
        "rarely bought products are spread across the whole range. Pick a department to see where it sits."
    )

    with st.expander("Search every product"):
        term = st.text_input("Product name contains", key="search", placeholder="e.g. yogurt")
        t = p if not term else p[p["product_name"].str.contains(term, case=False, regex=False)]
        st.dataframe(
            t.sort_values("orders", ascending=False)[
                ["product_name", "department", "aisle", "orders", "reorders", "reorder_rate", "first_in_cart"]
            ],
            hide_index=True,
            height=380,
            column_config={
                "product_name": st.column_config.TextColumn("Product", width="large"),
                "department": "Department",
                "aisle": "Aisle",
                "orders": st.column_config.NumberColumn("Orders", format="localized"),
                "reorders": st.column_config.NumberColumn("Reorders", format="localized"),
                "reorder_rate": st.column_config.ProgressColumn("Reorder rate", format="percent", min_value=0, max_value=1),
                "first_in_cart": st.column_config.NumberColumn("First in cart", format="localized"),
            },
        )
        st.caption(f"{len(t):,} products")

    footer()
