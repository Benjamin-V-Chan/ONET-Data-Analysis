"""Legacy entry point — kept for backwards compatibility.

Prefer the CLI:  ``onet-analyze eda``  and  ``onet-analyze cluster``

Delegates to :mod:`onet_analysis.eda` and :mod:`onet_analysis.clustering` so the
analysis logic lives in one place and is unit-tested.
"""

from __future__ import annotations

from onet_analysis.clustering import cluster_occupations, plot_clusters
from onet_analysis.eda import run_eda
from onet_analysis.loading import load_csv
from onet_analysis.paths import default_paths


def main() -> None:
    paths = default_paths().make_all()
    data = load_csv(paths.keyword_search_csv)

    eda_result = run_eda(data, paths.results, paths.processed)
    print("SOC Code Coverage:")
    print(eda_result.soc_code_coverage.to_string(index=False))

    cluster_result = cluster_occupations(data, n_clusters=5)
    plot_clusters(cluster_result, paths.results / "occupation_clusters.png")
    print(f"Clustering complete (k={cluster_result.n_clusters}, "
          f"silhouette={cluster_result.silhouette}).")
    print("Findings saved to data/processed/ and results/.")


if __name__ == "__main__":
    main()
