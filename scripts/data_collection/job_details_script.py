"""Legacy entry point — kept for backwards compatibility.

Prefer the CLI:  ``onet-analyze collect`` (which runs this stage too).

Fetches full occupation details for the codes in
``data/raw/keyword_search_results.csv`` and writes ``data/raw/job_details.json``.
"""

from __future__ import annotations

from onet_data_collector import fetch_job_details, resolve_credentials

from onet_analysis.paths import default_paths


def main() -> None:
    paths = default_paths().make_all()
    username, password = resolve_credentials(allow_prompt=True)
    fetch_job_details(
        username, password, str(paths.keyword_search_csv), str(paths.job_details_json)
    )


if __name__ == "__main__":
    main()
