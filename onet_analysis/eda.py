"""Exploratory data analysis over keyword-search results.

Computes coverage/distribution tables and renders plots. Seaborn is used when
available; otherwise matplotlib-only fallbacks keep everything working. All
plotting uses the non-interactive ``Agg`` backend so it runs headless (CI,
servers, notebooks) without a display.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe; must precede pyplot import
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .schema import resolve_column  # noqa: E402

log = logging.getLogger("onet_analysis.eda")

try:
    import seaborn as sns

    HAS_SEABORN = True
except ImportError:  # pragma: no cover - environment dependent
    HAS_SEABORN = False


@dataclass
class EdaResult:
    """Artifacts produced by :func:`run_eda`."""

    soc_code_coverage: pd.DataFrame
    occupation_distribution: pd.DataFrame
    plots: list[Path] = field(default_factory=list)


def clean_keyword_frame(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Normalise column names and strip/drop empty rows.

    Returns the cleaned frame plus a mapping of logical -> real column names
    (``keyword``, ``soc_code``, ``job_title``).
    """
    cols = {
        "keyword": resolve_column(data, "keyword"),
        "soc_code": resolve_column(data, "soc_code"),
        "job_title": resolve_column(data, "job_title"),
    }
    df = data.copy()
    for key in cols.values():
        df[key] = df[key].astype(str).str.strip()
    df = df[df[cols["job_title"]].str.len() > 0].reset_index(drop=True)
    return df, cols


def soc_code_coverage(df: pd.DataFrame, cols: dict[str, str]) -> pd.DataFrame:
    """Unique SOC major groups discovered per keyword."""
    return (
        df.groupby(cols["keyword"])[cols["soc_code"]]
        .nunique()
        .reset_index()
        .rename(columns={cols["keyword"]: "Keyword", cols["soc_code"]: "Unique SOC Codes"})
        .sort_values("Unique SOC Codes", ascending=False)
        .reset_index(drop=True)
    )


def occupation_distribution(df: pd.DataFrame, cols: dict[str, str]) -> pd.DataFrame:
    """Long-form count of (keyword, job title) pairs."""
    return (
        df.groupby([cols["keyword"], cols["job_title"]])
        .size()
        .reset_index(name="Counts")
    )


def _save(fig_path: Path) -> Path:
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close()
    return fig_path


def plot_soc_distribution(df: pd.DataFrame, cols: dict[str, str], out_dir: Path) -> Path:
    plt.figure(figsize=(14, 10))
    order = df[cols["soc_code"]].value_counts().index
    if HAS_SEABORN:
        sns.countplot(y=cols["soc_code"], data=df, order=order)
    else:
        counts = df[cols["soc_code"]].value_counts().reindex(order)
        plt.barh(counts.index.astype(str), counts.values)
        plt.gca().invert_yaxis()
    plt.title("SOC Code Distribution")
    plt.xlabel("Count")
    plt.ylabel("SOC Code")
    return _save(out_dir / "soc_code_distribution.png")


def plot_keywords_per_soc(coverage: pd.DataFrame, out_dir: Path) -> Path:
    plt.figure(figsize=(12, 7))
    plt.bar(coverage["Keyword"], coverage["Unique SOC Codes"])
    plt.title("Unique SOC Major Groups per Keyword")
    plt.xlabel("Keyword")
    plt.ylabel("Unique SOC Codes")
    plt.xticks(rotation=45, ha="right")
    return _save(out_dir / "unique_soc_per_keyword.png")


def run_eda(data: pd.DataFrame, out_dir: str | Path, processed_dir: str | Path) -> EdaResult:
    """Run the full EDA and persist tables + plots.

    Args:
        data: Raw keyword-search DataFrame.
        out_dir: Where plots and the summary are written (``results/``).
        processed_dir: Where coverage/distribution CSVs are written.
    """
    out_dir, processed_dir = Path(out_dir), Path(processed_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    df, cols = clean_keyword_frame(data)
    coverage = soc_code_coverage(df, cols)
    distribution = occupation_distribution(df, cols)

    coverage.to_csv(processed_dir / "soc_code_coverage.csv", index=False)
    distribution.to_csv(processed_dir / "occupation_distribution.csv", index=False)

    plots = [
        plot_soc_distribution(df, cols, out_dir),
        plot_keywords_per_soc(coverage, out_dir),
    ]

    log.info("EDA complete: %d keywords, %d rows.", df[cols["keyword"]].nunique(), len(df))
    return EdaResult(soc_code_coverage=coverage, occupation_distribution=distribution, plots=plots)
