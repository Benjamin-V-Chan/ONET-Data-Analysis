"""Legacy entry point — kept for backwards compatibility.

Prefer the CLI:  ``onet-analyze collect <keywords...>``

This shim delegates to :mod:`onet_analysis.collect` so behaviour stays in one
place. It runs only the keyword-search stage and writes
``data/raw/keyword_search_results.csv``.
"""

from __future__ import annotations

from onet_data_collector import keyword_search_many, resolve_credentials

from onet_analysis.collect import DEFAULT_KEYWORDS
from onet_analysis.paths import default_paths


def main() -> None:
    paths = default_paths().make_all()
    username, password = resolve_credentials(allow_prompt=True)
    df = keyword_search_many(username, password, DEFAULT_KEYWORDS)
    df.to_csv(paths.keyword_search_csv, index=False)
    print(f"Keyword search results saved to {paths.keyword_search_csv}")


if __name__ == "__main__":
    main()
