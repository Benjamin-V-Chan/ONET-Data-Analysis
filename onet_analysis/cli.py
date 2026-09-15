"""Command-line interface for the analytics pipeline (``onet-analyze``).

    onet-analyze collect "healthcare" "technology"        # run the collector ETL
    onet-analyze eda                                       # coverage + distribution plots
    onet-analyze keywords                                  # keyword -> field attribution
    onet-analyze cluster --clusters 6                      # role clustering
    onet-analyze all "healthcare" "technology"            # collect + every analysis

Paths default to ``<cwd>/data`` and ``<cwd>/results`` and can be relocated with
``--base``.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .clustering import cluster_occupations, plot_clusters
from .eda import run_eda
from .keyword_attribution import analyze_keywords, plot_attribution
from .loading import load_csv
from .paths import default_paths

log = logging.getLogger("onet_analysis.cli")


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    # Keep third-party libraries from flooding the console at INFO.
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="onet-analyze", description=__doc__.split("\n", 1)[0])
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--base", default=".", help="Base directory for data/ and results/.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_collect = sub.add_parser("collect", help="Run the collector ETL (search/details/condense).")
    p_collect.add_argument("keywords", nargs="*", help="Search terms (defaults to a starter set).")
    p_collect.add_argument("--username")
    p_collect.add_argument("--password")
    p_collect.add_argument("--max-results", type=int, default=None)

    sub.add_parser("eda", help="Coverage and distribution analysis of keyword results.")
    sub.add_parser("keywords", help="Keyword-to-field attribution over condensed details.")

    p_cluster = sub.add_parser("cluster", help="Cluster occupations from their text.")
    p_cluster.add_argument("--clusters", type=int, default=5)

    p_all = sub.add_parser("all", help="Collect then run every analysis.")
    p_all.add_argument("keywords", nargs="*")
    p_all.add_argument("--username")
    p_all.add_argument("--password")
    p_all.add_argument("--max-results", type=int, default=None)
    p_all.add_argument("--clusters", type=int, default=5)

    return parser


def _run_collect(args, paths) -> None:
    from .collect import DEFAULT_KEYWORDS, collect_all

    keywords = args.keywords or DEFAULT_KEYWORDS
    collect_all(keywords, paths, username=args.username, password=args.password,
                max_results=args.max_results)


def _run_eda(paths) -> None:
    data = load_csv(paths.keyword_search_csv)
    result = run_eda(data, paths.results, paths.processed)
    log.info("SOC coverage:\n%s", result.soc_code_coverage.to_string(index=False))
    _write_summary(paths, result)


def _run_keywords(paths) -> None:
    keyword_df = load_csv(paths.keyword_search_csv)
    condensed_df = load_csv(paths.condensed_csv)
    result = analyze_keywords(keyword_df, condensed_df)
    paths.data_results.mkdir(parents=True, exist_ok=True)
    result.to_csv(paths.keyword_analysis_csv)
    plot_attribution(result, paths.data_results)
    log.info("Keyword attribution written to %s", paths.keyword_analysis_csv)


def _run_cluster(paths, n_clusters) -> None:
    condensed_df = load_csv(paths.condensed_csv, required=False)
    df = condensed_df if condensed_df is not None else load_csv(paths.keyword_search_csv)
    result = cluster_occupations(df, n_clusters=n_clusters)
    assignments_path = paths.processed / "cluster_assignments.csv"
    paths.processed.mkdir(parents=True, exist_ok=True)
    result.assignments.to_csv(assignments_path, index=False)
    plot_clusters(result, paths.results / "occupation_clusters.png")
    log.info("Clustering done (k=%d, silhouette=%s).", result.n_clusters, result.silhouette)
    for cid, terms in sorted(result.top_terms.items()):
        log.info("Cluster %d: %s", cid, ", ".join(terms) or "(no distinctive terms)")


def _write_summary(paths, eda_result) -> None:
    summary = paths.results / "keyword_search_evaluation_summary.txt"
    lines = [
        "Keyword Search Evaluation Summary",
        "=" * 33,
        "",
        "SOC Code Coverage:",
        eda_result.soc_code_coverage.to_string(index=False),
        "",
        f"Plots written: {', '.join(p.name for p in eda_result.plots)}",
    ]
    summary.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _configure_logging(args.verbose)
    paths = default_paths(args.base)
    try:
        if args.command == "collect":
            _run_collect(args, paths)
        elif args.command == "eda":
            _run_eda(paths)
        elif args.command == "keywords":
            _run_keywords(paths)
        elif args.command == "cluster":
            _run_cluster(paths, args.clusters)
        elif args.command == "all":
            _run_collect(args, paths)
            _run_eda(paths)
            _run_keywords(paths)
            _run_cluster(paths, args.clusters)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        log.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
