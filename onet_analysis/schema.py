"""Resilient column resolution.

O*NET exports vary in how columns are named ("Job Title" vs "job_title" vs
"occupation_title"). These helpers let the analysis code ask for a logical
column and get whatever real column matches, case-insensitively.
"""

from __future__ import annotations

import pandas as pd

# Logical name -> accepted aliases (case-insensitive, whitespace-insensitive).
ALIASES: dict[str, tuple[str, ...]] = {
    "keyword": ("keyword",),
    "job_code": ("job code", "job_code", "code", "occupation_code"),
    "job_title": ("job title", "job_title", "occupation_title", "occupation title", "title"),
    "soc_code": ("soc code", "soc_code", "soc"),
    "description": ("description",),
}


def _index(df: pd.DataFrame) -> dict[str, str]:
    return {str(c).strip().lower(): c for c in df.columns}


def resolve_column(df: pd.DataFrame, logical: str, *extra_aliases: str) -> str:
    """Return the real column name for a logical field, or raise ``KeyError``.

    Args:
        df: The DataFrame to search.
        logical: A key in :data:`ALIASES` (or any string; it is also tried).
        extra_aliases: Additional accepted names for this lookup.
    """
    index = _index(df)
    candidates = (logical, *ALIASES.get(logical, ()), *extra_aliases)
    for cand in candidates:
        key = cand.strip().lower()
        if key in index:
            return index[key]
    raise KeyError(
        f"Could not find a column for '{logical}'. Tried {candidates}. "
        f"Available: {list(df.columns)}"
    )


def optional_column(df: pd.DataFrame, logical: str, *extra_aliases: str) -> str | None:
    """Like :func:`resolve_column` but returns ``None`` instead of raising."""
    try:
        return resolve_column(df, logical, *extra_aliases)
    except KeyError:
        return None
