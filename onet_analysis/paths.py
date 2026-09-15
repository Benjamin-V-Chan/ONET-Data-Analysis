"""Canonical on-disk layout for the analytics pipeline.

All paths are relative to a configurable base directory (default: current working
directory), so the same code runs locally, in notebooks, or in CI.

    <base>/
      data/raw/        keyword_search_results.csv, job_details.json
      data/processed/  condensed_job_details.csv, coverage tables, cluster assignments
      data/results/    keyword_analysis_results.csv
      results/         plots (.png) and summary text
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """Resolved paths for every pipeline artifact."""

    base: Path

    @property
    def raw(self) -> Path:
        return self.base / "data" / "raw"

    @property
    def processed(self) -> Path:
        return self.base / "data" / "processed"

    @property
    def data_results(self) -> Path:
        return self.base / "data" / "results"

    @property
    def results(self) -> Path:
        return self.base / "results"

    # Individual artifacts -------------------------------------------------
    @property
    def keyword_search_csv(self) -> Path:
        return self.raw / "keyword_search_results.csv"

    @property
    def job_details_json(self) -> Path:
        return self.raw / "job_details.json"

    @property
    def condensed_csv(self) -> Path:
        return self.processed / "condensed_job_details.csv"

    @property
    def keyword_analysis_csv(self) -> Path:
        return self.data_results / "keyword_analysis_results.csv"

    def make_all(self) -> "Paths":
        """Create every directory in the layout and return self."""
        for d in (self.raw, self.processed, self.data_results, self.results):
            d.mkdir(parents=True, exist_ok=True)
        return self


def default_paths(base: str | Path = ".") -> Paths:
    return Paths(Path(base).resolve())
