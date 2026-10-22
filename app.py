"""Project 27 demo app.

    .venv\\Scripts\\streamlit run app.py

Four pages: watch one run, explore the landscapes, race GA against MA, and
browse the saved 30-run experiment results.
"""
import streamlit as st

from app_pages import ui

st.set_page_config(
    page_title="Project 27 · GA and MA",
    page_icon=":material/scatter_plot:",
    layout="wide",
    initial_sidebar_state="auto",
)
ui.inject_css()

page = st.navigation(
    [
        st.Page("app_pages/run.py", title="Watch a run", icon=":material/play_circle:", default=True),
        st.Page("app_pages/explore.py", title="Explore landscapes", icon=":material/landscape:"),
        st.Page("app_pages/compare.py", title="GA vs MA", icon=":material/compare_arrows:"),
        st.Page("app_pages/results.py", title="Saved results", icon=":material/table_chart:"),
    ]
)
page.run()
ui.sidebar_brand()
