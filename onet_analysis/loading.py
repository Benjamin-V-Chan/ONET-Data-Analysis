"""Small IO helpers for loading pipeline artifacts."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger("onet_analysis.loading")


def load_csv(path: str | Path, *, required: bool = True) -> pd.DataFrame | None:
    """Load a CSV, returning ``None`` (or raising) when it does not exist.

    Args:
        path: CSV path.
        required: If ``True``, raise ``FileNotFoundError`` when missing;
            otherwise log a warning and return ``None``.
    """
    p = Path(path)
    if not p.is_file():
        if required:
            raise FileNotFoundError(
                f"Required input not found: {p}. Run the collection stage first "
                "(`onet-analyze collect ...`)."
            )
        log.warning("Optional input not found: %s", p)
        return None
    return pd.read_csv(p)


def ensure_dir(path: str | Path) -> Path:
    """Create a directory (and parents) if needed and return it as a Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
