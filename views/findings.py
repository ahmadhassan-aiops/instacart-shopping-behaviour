"""Landing page: the question, the headline numbers, five findings and what to do about them."""

import streamlit as st

from lib import charts, data
from lib.ui import cap, finding, footer, header, method_card, recommendations, spotlight


def render() -> None:
    from nav import BASKET, CUSTOMERS, METHOD, REORDERS, TIMING

    m = data.meta()
    h = data.heat()
    by_hour = h.groupby("hour")["orders"].sum()
    by_day = h.groupby("dow")["orders"].sum()
    total = by_hour.sum()
    day_share = by_hour.loc[10:16].sum() / total
    sun_mon = by_day.loc[[0, 1]].sum() / total
    dept = data.departments()
    produce = dept.loc[dept["department"] == "produce", "share"].iloc[0]
    t = data.tenure_summary().set_index("tenure")

    header(
        "Exploratory data analysis · Python, pandas",
        "How 157,000 Instacart customers shop for groceries",
        "When do people order, what goes in the basket, and what keeps them coming back? "
        f"I analysed <b>{m['orders']:,} orders</b> and <b>{m['order_lines']:,} purchased items</b> to answer "
        "these questions for the business. Here is what the data says.",
        chips=[("code", "Python, pandas"), ("bar_chart", "Plotly"), ("shopping_basket", "Market basket data"),
               ("group", f"{m['customers']:,} customers")],
    )

    c = st.columns(4)
    c[0].metric("Orders analysed", f"{m['orders']:,}", border=True)
    c[1].metric("Customers", f"{m['customers']:,}", border=True)
    c[2].metric("Products bought", f"{m['products_ordered']:,}", border=True)
    c[3].metric("Items that were reorders", f"{m['reorder_rate']:.0%}", border=True)

    labels = [data.hour_label(x) for x in range(24)]
    spotlight("A week of grocery orders",
              "Orders by day of week and hour of day; darker means busier. The <b>daytime plateau</b> from 9 am to 5 pm "
              "and the <b>heavy Sunday and Monday rows</b> are the rhythm every recommendation below is built on.",
              charts.heatmap(h, data.DAYS, labels), key="spot")

    st.subheader("Key findings", anchor=False)
    r1 = st.columns(3)
    finding(
        r1[0], f"{day_share:.0%}", "of orders are placed between 10 am and 5 pm",
        "Grocery shopping is a daytime habit",
        f"Orders climb from 7 am and stay on a plateau until late afternoon. Midnight to 6 am "
        f"is only {by_hour.loc[0:5].sum() / total:.1%} of the week.",
        TIMING, "When people shop", card_icon="schedule",
    )
    finding(
        r1[1], f"{sun_mon:.0%}", "of the week's orders land on Sunday and Monday",
        "The week starts with a big shop",
        f"Sunday is {by_day[0] / by_day.min() - 1:.0%} busier than the quietest day. Midweek and Saturday "
        "keep the same hourly shape, only the volume changes.",
        TIMING, "Daily and weekly rhythm", card_icon="calendar_view_week",
    )
    finding(
        r1[2], f"{m['gap_median']:.0f} days", "is the typical gap between two orders",
        "Customers restock weekly or monthly",
        f"The gaps spike at exactly 7 days ({m['gap_7_share']:.0%} of repeat orders) and at "
        f"30 or more days ({m['gap_30_share']:.0%}): two distinct shopping rhythms.",
        TIMING, "Days between orders", card_icon="event_repeat",
    )
    r2 = st.columns(3)
    finding(
        r2[0], f"{produce:.0%}", "of everything bought is fresh produce",
        "Fresh food drives the basket",
        "Nine of the ten best sellers are fruit and vegetables (the tenth is organic milk), and bananas are the "
        "most common first item in a cart.",
        BASKET, "What they buy", card_icon="nutrition",
    )
    finding(
        r2[1], f"{t.loc['2-3', 'reorder_share']:.0%} → {t.loc['51-100', 'reorder_share']:.0%}",
        "share of the basket that is a reorder, from 2-3 orders to 50+",
        "Loyalty builds with every order",
        "The more often someone orders, the more of their basket is things they bought before. "
        "Habits form in the first handful of orders.",
        CUSTOMERS, "Customer loyalty", card_icon="loyalty",
    )
    finding(
        r2[2], "19 of 20", "top sellers are also among the top 20 reorders",
        "Popular products are the sticky ones",
        "Best sellers are bought again and again, led by bananas at 84%. Dairy, beverages and produce have the "
        "highest reorder rates; pantry and personal care the lowest.",
        REORDERS, "Reorders", card_icon="autorenew",
    )

    st.subheader("What I would recommend", anchor=False)
    recommendations([
        ("groups", "Plan capacity around the peaks",
         "Staff shoppers and delivery slots for 10 am to 5 pm and the Sunday-Monday peak; use midweek offers to move "
         "some demand to Tuesday to Thursday."),
        ("notifications_active", "Time reminders to the restock cycle",
         "A \"time to restock?\" nudge at <b>day 7</b>, and a win-back message before <b>day 30</b>, match the two "
         "rhythms customers already follow."),
        ("rocket_launch", "Invest in the first five orders",
         "Reorder share rises steeply with tenure, so onboarding offers and a strong \"Buy it again\" list early on "
         "are where loyalty is won."),
        ("eco", "Protect produce and dairy",
         "They are most of the volume, the first thing in the cart and the most reordered. Stock-outs there hurt "
         "the most."),
    ])
    cap(
        "These are hypotheses from a descriptive analysis, to be tested (for example with A/B tests), "
        "not proven effects."
    )

    method_card("<b>How this was done.</b> Five tables (orders, order items, products, aisles, departments) were "
                "checked, cleaned and joined in pandas, then analysed against twelve business questions. The "
                "cleaning decisions, the raw data and the notebook are on the methods page.",
                METHOD, tools=["pandas", "Plotly", "Data cleaning", "Joins across 5 tables"])

    footer()
