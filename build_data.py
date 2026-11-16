"""
Offline build step: turn the raw Instacart CSVs (about 110 MB) into the small
summary files the app ships with (data/*.parquet + data/meta.json).

Run it once on your machine whenever the analysis changes:

    python build_data.py "W:/Portfolio Projects/1. Data-analysis-with-python-Projects/Instacart-Analysis"

The raw files are never deployed. Cleaning rules (see the Data & method page):
  * instacart_orders: drop the 15 exact duplicate rows.
  * days_since_prior_order is missing exactly for each customer's first order,
    so those rows are flagged as first orders and left out of the gap stats
    (not filled with a mean or 0).
  * add_to_cart_order is missing only for items past position 64 in very large
    orders (the source system stops numbering there). Those rows are real
    purchases, so they are kept; only "first in cart" uses the position.
  * products with no name are kept in totals but labelled "Unnamed product".
  * order_dow: 0 = Sunday ... 6 = Saturday.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

DEFAULT_RAW = Path("W:/Portfolio Projects/1. Data-analysis-with-python-Projects/Instacart-Analysis")
OUT = Path(__file__).parent / "data"


def read(raw: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(raw / f"{name}.csv", sep=";")


def main(raw: Path) -> None:
    OUT.mkdir(exist_ok=True)

    orders = read(raw, "instacart_orders")
    op = read(raw, "order_products")
    products = read(raw, "products")
    aisles = read(raw, "aisles")
    departments = read(raw, "departments")

    # ── Samples of the raw tables (before cleaning) for the Data page ────────
    for name, df in {
        "orders": orders, "order_products": op, "products": products,
        "aisles": aisles, "departments": departments,
    }.items():
        df.sample(min(50, len(df)), random_state=7).to_parquet(OUT / f"sample_{name}.parquet", index=False)

    raw_shapes = {
        "instacart_orders": list(orders.shape), "order_products": list(op.shape),
        "products": list(products.shape), "aisles": list(aisles.shape), "departments": list(departments.shape),
    }

    # ── Cleaning ──────────────────────────────────────────────────────────────
    dup_orders = int(orders.duplicated().sum())
    orders = orders.drop_duplicates().reset_index(drop=True)

    first_mask = orders["days_since_prior_order"].isna()
    assert (orders.loc[first_mask, "order_number"] == 1).all(), "missing gaps should be first orders"
    first_orders = int(first_mask.sum())

    missing_pos = op["add_to_cart_order"].isna()
    missing_pos_rows = int(missing_pos.sum())
    missing_pos_orders = int(op.loc[missing_pos, "order_id"].nunique())
    sizes = op.groupby("order_id").size()
    min_size_missing = int(sizes[op.loc[missing_pos, "order_id"].unique()].min())

    unnamed = int(products["product_name"].isna().sum())
    products["product_name"] = products["product_name"].fillna("Unnamed product")
    prod = (
        products.merge(aisles, on="aisle_id", how="left")
        .merge(departments, on="department_id", how="left")
    )

    # ── When people shop ──────────────────────────────────────────────────────
    heat = (
        orders.groupby(["order_dow", "order_hour_of_day"]).size()
        .rename("orders").reset_index()
        .rename(columns={"order_dow": "dow", "order_hour_of_day": "hour"})
    )
    heat.to_parquet(OUT / "heat.parquet", index=False)

    gaps = (
        orders.loc[~first_mask, "days_since_prior_order"].astype(int)
        .value_counts().sort_index().rename_axis("days").rename("orders").reset_index()
    )
    gaps.to_parquet(OUT / "gaps.parquet", index=False)
    gap_values = orders.loc[~first_mask, "days_since_prior_order"]

    # ── Order sizes ───────────────────────────────────────────────────────────
    order_sizes = sizes.value_counts().sort_index().rename_axis("items").rename("orders").reset_index()
    order_sizes.to_parquet(OUT / "order_sizes.parquet", index=False)

    # ── Products ──────────────────────────────────────────────────────────────
    per_prod = op.groupby("product_id").agg(orders=("order_id", "size"), reorders=("reordered", "sum"))
    first_cart = op.loc[op["add_to_cart_order"] == 1].groupby("product_id").size().rename("first_in_cart")
    prod_stats = (
        prod.merge(per_prod, on="product_id", how="inner")
        .merge(first_cart, on="product_id", how="left")
    )
    prod_stats["first_in_cart"] = prod_stats["first_in_cart"].fillna(0).astype("int32")
    prod_stats["orders"] = prod_stats["orders"].astype("int32")
    prod_stats["reorders"] = prod_stats["reorders"].astype("int32")
    prod_stats = prod_stats[["product_id", "product_name", "aisle", "department", "orders", "reorders", "first_in_cart"]]
    prod_stats.to_parquet(OUT / "products.parquet", index=False)

    # ── Customers ─────────────────────────────────────────────────────────────
    # The file holds a sample of each customer's orders; order_number is their
    # lifetime order count on the platform, so max(order_number) is the true
    # "how many orders has this customer placed".
    per_order_items = op.groupby("order_id").agg(items=("product_id", "size"), reordered=("reordered", "sum"))
    cust = (
        orders[["order_id", "user_id", "order_number"]]
        .merge(per_order_items, on="order_id", how="left")
        .fillna({"items": 0, "reordered": 0})
        .groupby("user_id")
        .agg(lifetime_orders=("order_number", "max"), orders_in_sample=("order_id", "size"),
             items=("items", "sum"), reordered=("reordered", "sum"))
        .reset_index(drop=True)
    )
    cust = cust.astype("int32")
    cust.to_parquet(OUT / "customers.parquet", index=False)

    # ── Headline numbers ──────────────────────────────────────────────────────
    lines = len(op)
    meta = {
        "built": date.today().isoformat(),
        "raw_shapes": raw_shapes,
        "orders": int(orders["order_id"].nunique()),
        "customers": int(orders["user_id"].nunique()),
        "products_ordered": int(len(prod_stats)),
        "products_catalogue": int(len(products)),
        "aisles": int(len(aisles)),
        "departments": int(len(departments)),
        "order_lines": int(lines),
        "reorder_rate": float(op["reordered"].mean()),
        "items_mean": float(sizes.mean()),
        "items_median": float(sizes.median()),
        "items_max": int(sizes.max()),
        "gap_mean": float(gap_values.mean()),
        "gap_median": float(gap_values.median()),
        "gap_30_share": float((gap_values == 30).mean()),
        "gap_7_share": float((gap_values == 7).mean()),
        "cleaning": {
            "duplicate_orders": dup_orders,
            "first_orders": first_orders,
            "missing_cart_position_rows": missing_pos_rows,
            "missing_cart_position_orders": missing_pos_orders,
            "missing_cart_position_min_order_size": min_size_missing,
            "unnamed_products": unnamed,
        },
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    total = sum(p.stat().st_size for p in OUT.iterdir())
    print(f"Wrote {len(list(OUT.iterdir()))} files to {OUT} ({total / 1e6:.2f} MB)")
    print(json.dumps({k: v for k, v in meta.items() if k not in ("raw_shapes",)}, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RAW)
