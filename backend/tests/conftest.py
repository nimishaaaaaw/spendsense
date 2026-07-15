"""
Shared pytest fixtures for backend tests.

Loads the real generated dataset (not synthetic test fixtures) so accuracy
numbers reported here are the same real numbers we hand-verified manually
during development -- these tests exist to catch regressions against that
known-good baseline, not to test against toy data.
"""

import pathlib
import pandas as pd
import pytest

from app.core.categorizer import categorize_df
from app.core.subscription_detector import detect_subscriptions

_DATA_DIR = pathlib.Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def raw_df() -> pd.DataFrame:
    return pd.read_csv(_DATA_DIR / "transactions_raw.csv")


@pytest.fixture(scope="session")
def truth_df() -> pd.DataFrame:
    return pd.read_csv(_DATA_DIR / "transactions_truth.csv")


@pytest.fixture(scope="session")
def categorized_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorized once per test session (not per test) since categorize_df
    is deterministic and re-running it for every single test would be
    wasteful -- all tests in this session share the same result.
    """
    return categorize_df(raw_df).reset_index(drop=True)


@pytest.fixture(scope="session")
def subscriptions(categorized_df: pd.DataFrame) -> list[dict]:
    return detect_subscriptions(categorized_df)