"""Loads the pre-computed summaries in data/ (built by build_data.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parent.parent / "data"

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAYS_SHORT = [d[:3] for d in DAYS]

NOTEBOOK_URL = (
    "https://github.com/ahmadhassan-aiops/AIOPS-Portfolio-Projects/blob/main/"
    "1.%20Data-analysis-with-python-Projects/Instacart-Analysis/Instacart_Analysis_Project.ipynb"
)
LEARN_URL = "https://learn.ahmadhassanrx.com"


def hour_label(h: int) -> str:
    if h == 0:
        return "12 am"
    if h == 12:
        return "12 pm"
    return f"{h} am" if h < 12 else f"{h - 12} pm"


@st.cache_data
def meta() -> dict:
    return json.loads((DATA / "meta.json").read_text(encoding="utf-8"))


@st.cache_data
def table(name: str) -> pd.DataFrame:
    return pd.read_parquet(DATA / f"{name}.parquet")


@st.cache_data
def heat() -> pd.DataFrame:
    df = table("heat")
    df["day"] = df["dow"].map(dict(enumerate(DAYS)))
    return df


@st.cache_data
def products() -> pd.DataFrame:
    df = table("products")
    df["reorder_rate"] = df["reorders"] / df["orders"]
    return df


@st.cache_data
def departments() -> pd.DataFrame:
    p = products()
    d = p.groupby("department", as_index=False)[["orders", "reorders", "first_in_cart"]].sum()
    d["share"] = d["orders"] / d["orders"].sum()
    d["reorder_rate"] = d["reorders"] / d["orders"]
    return d.sort_values("orders", ascending=False, ignore_index=True)


@st.cache_data
def aisles() -> pd.DataFrame:
    p = products()
    a = p.groupby("aisle", as_index=False)[["orders", "reorders"]].sum()
    a["share"] = a["orders"] / a["orders"].sum()
    return a.sort_values("orders", ascending=False, ignore_index=True)


TENURE_BINS = [0, 1, 3, 5, 10, 20, 30, 50, 100]
TENURE_LABELS = ["1", "2-3", "4-5", "6-10", "11-20", "21-30", "31-50", "51-100"]


@st.cache_data
def customers() -> pd.DataFrame:
    c = table("customers")
    c["tenure"] = pd.cut(c["lifetime_orders"], TENURE_BINS, labels=TENURE_LABELS)
    c["reorder_share"] = (c["reordered"] / c["items"].where(c["items"] > 0)).astype(float)
    return c


@st.cache_data
def tenure_summary() -> pd.DataFrame:
    c = customers()
    t = c.groupby("tenure", observed=False).agg(
        customers=("lifetime_orders", "size"), reorder_share=("reorder_share", "mean")
    ).reset_index()
    t["customer_share"] = t["customers"] / t["customers"].sum()
    return t
