"""Tests for resilient column resolution."""

from __future__ import annotations

import pandas as pd
import pytest

from onet_analysis.schema import optional_column, resolve_column


def test_resolve_exact():
    df = pd.DataFrame(columns=["Keyword", "Job Code", "Job Title", "SOC Code"])
    assert resolve_column(df, "keyword") == "Keyword"
    assert resolve_column(df, "job_code") == "Job Code"
    assert resolve_column(df, "job_title") == "Job Title"
    assert resolve_column(df, "soc_code") == "SOC Code"


def test_resolve_alias_variants():
    df = pd.DataFrame(columns=["keyword", "occupation_code", "occupation_title"])
    assert resolve_column(df, "job_code") == "occupation_code"
    assert resolve_column(df, "job_title") == "occupation_title"


def test_resolve_missing_raises():
    df = pd.DataFrame(columns=["foo"])
    with pytest.raises(KeyError):
        resolve_column(df, "keyword")


def test_optional_column_returns_none():
    df = pd.DataFrame(columns=["foo"])
    assert optional_column(df, "description") is None
