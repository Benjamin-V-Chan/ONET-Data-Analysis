"""Legacy entry point — kept for backwards compatibility.

Prefer the CLI:  ``onet-analyze collect`` (which runs this stage too).

Flattens ``data/raw/job_details.json`` into
``data/processed/condensed_job_details.csv``.
"""

from __future__ import annotations

from onet_data_collector import condense_job_details

from onet_analysis.paths import default_paths


def main() -> None:
    paths = default_paths().make_all()
    condense_job_details(str(paths.job_details_json), str(paths.condensed_csv))


if __name__ == "__main__":
    main()
