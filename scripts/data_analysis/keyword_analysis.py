"""Legacy entry point — kept for backwards compatibility.

Prefer the CLI:  ``onet-analyze keywords``

Delegates to :mod:`onet_analysis.keyword_attribution`.
"""

from __future__ import annotations

from onet_analysis.keyword_attribution import analyze_keywords, plot_attribution
from onet_analysis.loading import load_csv
from onet_analysis.paths import default_paths


def main() -> None:
    paths = default_paths().make_all()
    keyword_df = load_csv(paths.keyword_search_csv)
    condensed_df = load_csv(paths.condensed_csv)

    result = analyze_keywords(keyword_df, condensed_df)
    result.to_csv(paths.keyword_analysis_csv)
    plot_attribution(result, paths.data_results)
    print(f"Keyword analysis results saved to {paths.keyword_analysis_csv}")


if __name__ == "__main__":
    main()
