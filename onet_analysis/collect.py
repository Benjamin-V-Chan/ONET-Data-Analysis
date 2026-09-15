"""Data-collection stage: thin wrappers over the ``onet_data_collector`` package.

This keeps the analytics repo's CLI self-contained (``onet-analyze collect ...``)
while delegating all API interaction to the sibling collector package, so the two
repositories share exactly one implementation of the ETL logic.
"""

from __future__ import annotations

import logging

import pandas as pd

from onet_data_collector import (
    condense_job_details,
    fetch_job_details,
    keyword_search_many,
    resolve_credentials,
)

from .paths import Paths

log = logging.getLogger("onet_analysis.collect")

DEFAULT_KEYWORDS = [
    "engineering", "healthcare", "finance", "technology", "education",
    "marketing", "construction", "management", "science", "design",
]


def collect_all(
    keywords: list[str],
    paths: Paths,
    *,
    username: str | None = None,
    password: str | None = None,
    max_results: int | None = None,
) -> pd.DataFrame:
    """Run search -> details -> condense and write artifacts into ``paths``.

    Returns the condensed DataFrame.
    """
    paths.make_all()
    user, pw = resolve_credentials(username, password, allow_prompt=True)

    log.info("Collecting keyword search results for %d keywords.", len(keywords))
    search_df = keyword_search_many(user, pw, keywords, max_results=max_results)
    search_df.to_csv(paths.keyword_search_csv, index=False)

    log.info("Fetching full occupation details.")
    fetch_job_details(user, pw, str(paths.keyword_search_csv), str(paths.job_details_json))

    log.info("Condensing occupation details.")
    return condense_job_details(str(paths.job_details_json), str(paths.condensed_csv))
