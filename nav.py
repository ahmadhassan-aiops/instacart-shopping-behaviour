"""Page registry, shared by app.py and pages that link to other pages."""

import streamlit as st

from views import basket, customers, findings, method, reorders, timing

FINDINGS = st.Page(findings.render, title="Key findings", icon=":material/insights:", url_path="findings", default=True)
TIMING = st.Page(timing.render, title="When people shop", icon=":material/schedule:", url_path="timing")
BASKET = st.Page(basket.render, title="What they buy", icon=":material/shopping_basket:", url_path="basket")
CUSTOMERS = st.Page(customers.render, title="Customers", icon=":material/group:", url_path="customers")
REORDERS = st.Page(reorders.render, title="Reorders", icon=":material/autorenew:", url_path="reorders")
METHOD = st.Page(method.render, title="Data & method", icon=":material/dataset:", url_path="method")

PAGES = [FINDINGS, TIMING, BASKET, CUSTOMERS, REORDERS, METHOD]
