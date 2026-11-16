"""
Instacart Shopping Behaviour: an interactive presentation of Ahmad Hassan's
exploratory data analysis. All data ships with the app (data/, built by
build_data.py), so it opens straight onto the findings.
"""

import streamlit as st

st.set_page_config(
    page_title="Instacart Shopping Behaviour | Ahmad Hassan",
    page_icon=":material/shopping_cart:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from lib.ui import inject_css  # noqa: E402
from nav import PAGES  # noqa: E402

inject_css()
st.navigation(PAGES, position="top").run()
