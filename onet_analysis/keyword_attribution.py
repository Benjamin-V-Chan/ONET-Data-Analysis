"""Keyword-to-feature attribution.

For each search keyword, measures how often that keyword appears across the
condensed occupation fields (tasks, skills, knowledge, ...) for the occupations
it surfaced. This answers "*why* did this keyword match these roles?" in terms of
concrete descriptors — the basis for explainable recommendations.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from pandas.api import types as ptypes  # noqa: E402

from .schema import resolve_column  # noqa: E402

log = logging.getLogger("onet_analysis.keyword_attribution")


def _text_columns(condensed: pd.DataFrame, code_col: str) -> list[str]:
    """Text (non-numeric, non-boolean) columns to scan for keyword occurrences.

    Works across pandas versions, including pandas >= 3.0 where string columns
    use a dedicated ``str`` dtype rather than ``object``.
    """
    return [
        c
        for c in condensed.columns
        if c != code_col
        and not ptypes.is_numeric_dtype(condensed[c])
        and not ptypes.is_bool_dtype(condensed[c])
    ]


def analyze_keywords(keyword_df: pd.DataFrame, condensed_df: pd.DataFrame) -> pd.DataFrame:
    """Return a (keyword x condensed-column) matrix of keyword-occurrence counts.

    Args:
        keyword_df: Keyword-search results (maps keyword -> job codes).
        condensed_df: Flattened occupation details (one row per occupation).

    Returns:
        A DataFrame indexed by keyword, one column per condensed text field,
        holding total case-insensitive substring occurrences.
    """
    kw_keyword = resolve_column(keyword_df, "keyword")
    kw_code = resolve_column(keyword_df, "job_code")
    cond_code = resolve_column(condensed_df, "job_code", "occupation_code")

    text_cols = _text_columns(condensed_df, cond_code)
    cond = condensed_df.set_index(cond_code)

    rows: dict[str, dict[str, int]] = {}
    for keyword in keyword_df[kw_keyword].dropna().unique():
        pattern = re.escape(str(keyword).lower())
        codes = keyword_df.loc[keyword_df[kw_keyword] == keyword, kw_code].dropna().unique()
        subset = cond.reindex([c for c in codes if c in cond.index])
        counts = {
            col: int(subset[col].astype(str).str.lower().str.count(pattern).sum())
            for col in text_cols
        }
        rows[str(keyword)] = counts

    result = pd.DataFrame.from_dict(rows, orient="index").fillna(0).astype(int)
    log.info("Attributed %d keywords across %d fields.", len(result), len(text_cols))
    return result


def plot_attribution(result: pd.DataFrame, out_dir: str | Path) -> list[Path]:
    """Render one bar chart per keyword showing counts across fields."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for keyword, counts in result.iterrows():
        plt.figure(figsize=(10, 6))
        plt.bar(counts.index, counts.values)
        plt.title(f"Keyword '{keyword}' occurrences by field")
        plt.xlabel("Condensed field")
        plt.ylabel("Count")
        plt.xticks(rotation=90)
        plt.tight_layout()
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(keyword))
        path = out_dir / f"{safe}_keyword_counts.png"
        plt.savefig(path)
        plt.close()
        paths.append(path)
    return paths
