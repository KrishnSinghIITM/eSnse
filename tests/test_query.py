import os


def test_placeholder():
    # simple sanity test to ensure tests run
    assert os.path.exists("app/data/finance.db")
