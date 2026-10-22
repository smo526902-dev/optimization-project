"""Smoke tests: every page of the Streamlit app runs with its default settings."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

PAGES = ["app_pages/run.py", "app_pages/explore.py", "app_pages/compare.py", "app_pages/results.py"]


@pytest.mark.parametrize("page", PAGES)
def test_page_runs_without_errors(page):
    app = AppTest.from_file(APP, default_timeout=120)
    app.run()
    if page != PAGES[0]:
        app.switch_page(page)
        app.run()
    assert not app.exception, [e.message for e in app.exception]


def test_run_page_opens_on_a_finished_run():
    app = AppTest.from_file(APP, default_timeout=120).run()
    assert app.title[0].value == "Rastrigin, 2-D"
    assert any("solved" in h.body for h in app.get("html") if hasattr(h, "body"))
