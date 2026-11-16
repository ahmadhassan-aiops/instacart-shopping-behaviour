"""When people shop: hour, day, Wednesday vs Saturday, days between orders (Q1-Q5)."""

import streamlit as st

from lib import charts, data
from lib.ui import chart, footer, header, insight, section


def render() -> None:
    m = data.meta()
    h = data.heat()
    hours = list(range(24))
    labels = [data.hour_label(x) for x in hours]
    by_hour = h.groupby("hour")["orders"].sum().reindex(hours)
    by_day = h.groupby("dow")["orders"].sum().reindex(range(7))
    total = by_hour.sum()

    header(
        "Shopping patterns",
        "When people shop",
        "Order time and day tell the business when to have shoppers, drivers and stock ready. "
        "Hover any chart for exact numbers.",
    )

    section("The whole week at a glance", "Orders by day of week and hour of day. Darker means more orders.")
    chart(charts.heatmap(h, data.DAYS, labels))
    insight(
        "Two things stand out: the <b>daytime plateau</b> from about 9 am to 5 pm on every day, and the "
        "<b>darker Sunday and Monday rows</b>. Nights are almost empty."
    )

    left, right = st.columns(2, gap="large")
    with left:
        section("Time of day", "Q2. What time of day do people shop for groceries?")
        fig = charts.bars(
            labels, by_hour.values, highlight=[10 <= x <= 16 for x in hours],
            customdata=(by_hour / total).values,
            hover="%{x}<br><b>%{y:,} orders</b> (%{customdata:.1%})",
            ytitle="Orders",
        )
        fig.update_xaxes(nticks=8)
        chart(fig)
        insight(
            f"<b>{by_hour.loc[10:16].sum() / total:.0%}</b> of orders are placed from 10 am to 5 pm (highlighted). "
            f"The single busiest hour is {data.hour_label(int(by_hour.idxmax()))}."
        )
    with right:
        section("Day of week", "Q3. What day of the week do people shop?")
        chart(charts.bars(
            data.DAYS_SHORT, by_day.values, highlight=[d in (0, 1) for d in range(7)],
            customdata=(by_day / total).values,
            hover="%{x}<br><b>%{y:,} orders</b> (%{customdata:.1%})",
            ytitle="Orders",
        ))
        insight(
            f"Sunday and Monday together take <b>{by_day.loc[[0, 1]].sum() / total:.0%}</b> of the week. "
            f"Tuesday to Saturday are flat at about {by_day.loc[2:6].mean() / total:.0%} each."
        )

    section(
        "Wednesday vs Saturday",
        "Q5. Is there a difference in the hour-of-day distribution on Wednesdays and Saturdays?",
    )
    mode = st.segmented_control(
        "Show", ["Share of the day's orders", "Number of orders"],
        default="Share of the day's orders", key="wed_sat_mode", label_visibility="collapsed",
    )
    wed = h[h["dow"] == 3].set_index("hour")["orders"].reindex(hours, fill_value=0)
    sat = h[h["dow"] == 6].set_index("hour")["orders"].reindex(hours, fill_value=0)
    if mode == "Number of orders":
        y1, y2, fmt, ytitle = wed.values, sat.values, ",", "Orders"
    else:
        y1, y2, fmt, ytitle = (wed / wed.sum()).values, (sat / sat.sum()).values, ".1%", "Share of the day's orders"
    fig = charts.two_lines(labels, y1, y2, ("Wednesday", "Saturday"), hover_fmt=fmt, ytitle=ytitle)
    if mode != "Number of orders":
        fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(nticks=12)
    chart(fig)
    insight(
        f"The two days have <b>almost the same shape</b>. Saturday has {sat.sum() - wed.sum():,} more orders and "
        f"peaks an hour earlier ({data.hour_label(int(sat.idxmax()))} against "
        f"{data.hour_label(int(wed.idxmax()))}); Wednesday leans slightly more to the morning and evening. "
        "Time of day matters far more than which weekday it is."
    )

    section("Days between orders", "Q4. How long do people wait before placing another order?")
    g = data.table("gaps")
    c = st.columns(3)
    c[0].metric("Median gap", f"{m['gap_median']:.0f} days", border=True)
    c[1].metric("Average gap", f"{m['gap_mean']:.1f} days", border=True)
    c[2].metric("First orders (no gap yet)", f"{m['cleaning']['first_orders']:,}", border=True)
    xlabels = [f"{d}+" if d == 30 else str(d) for d in g["days"]]
    fig = charts.bars(
        xlabels, g["orders"].values, highlight=[d in (7, 30) for d in g["days"]],
        customdata=(g["orders"] / g["orders"].sum()).values,
        hover="%{x} days<br><b>%{y:,} orders</b> (%{customdata:.1%})",
        xtitle="Days since the customer's previous order", ytitle="Orders",
    )
    fig.update_xaxes(type="category", nticks=16)
    chart(fig)
    insight(
        f"Half of repeat orders come within <b>{m['gap_median']:.0f} days</b>. The two spikes are the story: "
        f"<b>exactly 7 days</b> ({m['gap_7_share']:.0%}, the weekly shop) and <b>30 or more days</b> "
        f"({m['gap_30_share']:.0%}). The dataset caps gaps at 30, so that bar also holds everyone who waited longer."
    )
    st.caption(
        "A customer's first order has no previous order, so it has no gap. Those orders are left out here "
        "instead of being filled with an average or zero (see Data & method)."
    )

    footer()
