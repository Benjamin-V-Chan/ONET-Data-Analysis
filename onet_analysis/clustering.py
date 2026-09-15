"""Occupation clustering: TF-IDF -> TruncatedSVD -> KMeans.

Turns occupation text (titles, and descriptions when available) into an
interpretable clustering that groups roles into higher-level families. Returns
cluster assignments, a silhouette score, and the most distinctive terms per
cluster, and can render a 2-D scatter plot.

Design choices
--------------
* **TF-IDF** (unigrams + bigrams) is a transparent, dependency-light baseline —
  no GPU or model download needed — and its vocabulary makes clusters explainable
  via top terms.
* **TruncatedSVD** (LSA) reduces the sparse TF-IDF matrix without densifying it,
  which is both memory-safe and the mathematically appropriate PCA analogue for
  sparse text.
* **KMeans** with fixed ``random_state`` and ``n_init`` gives stable, repeatable
  groupings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.decomposition import TruncatedSVD  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.metrics import silhouette_score  # noqa: E402

from .schema import optional_column, resolve_column  # noqa: E402

log = logging.getLogger("onet_analysis.clustering")


@dataclass
class ClusterResult:
    """Outputs of :func:`cluster_occupations`."""

    assignments: pd.DataFrame          # original rows + 'cluster' + 2-D coords
    n_clusters: int
    silhouette: float | None
    top_terms: dict[int, list[str]]    # cluster id -> distinctive terms
    plot_path: Path | None = None


def _build_text(df: pd.DataFrame) -> pd.Series:
    """Combine the most informative available text columns into one field."""
    title_col = resolve_column(df, "job_title")
    parts = [df[title_col].fillna("").astype(str)]
    desc_col = optional_column(df, "description")
    if desc_col:
        parts.append(df[desc_col].fillna("").astype(str))
    text = parts[0]
    for extra in parts[1:]:
        text = text.str.cat(extra, sep=" ")
    return text.str.strip()


def cluster_occupations(
    df: pd.DataFrame,
    *,
    n_clusters: int = 5,
    n_components: int = 2,
    random_state: int = 42,
    top_n_terms: int = 8,
) -> ClusterResult:
    """Cluster occupations from their text fields.

    ``n_clusters`` is automatically clamped to the number of distinct samples so
    the routine never fails on tiny inputs.
    """
    df = df.reset_index(drop=True)
    text = _build_text(df)
    mask = text.str.len() > 0
    df = df[mask].reset_index(drop=True)
    text = text[mask].reset_index(drop=True)

    n_samples = len(df)
    if n_samples < 2:
        raise ValueError("Need at least 2 non-empty text rows to cluster.")

    k = max(2, min(n_clusters, n_samples))

    tfidf = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1)
    x = tfidf.fit_transform(text)

    n_comp = min(n_components, x.shape[1] - 1, n_samples - 1)
    n_comp = max(n_comp, 1)
    svd = TruncatedSVD(n_components=n_comp, random_state=random_state)
    reduced = svd.fit_transform(x)

    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(reduced)

    sil = None
    if 1 < k < n_samples:
        try:
            sil = float(silhouette_score(reduced, labels))
        except ValueError:  # pragma: no cover - degenerate clustering
            sil = None

    assignments = df.copy()
    assignments["cluster"] = labels
    assignments["svd_x"] = reduced[:, 0]
    assignments["svd_y"] = reduced[:, 1] if reduced.shape[1] > 1 else 0.0

    top_terms = _top_terms_per_cluster(x, labels, tfidf.get_feature_names_out(), k, top_n_terms)

    log.info("Clustered %d occupations into %d clusters (silhouette=%s).", n_samples, k, sil)
    return ClusterResult(assignments=assignments, n_clusters=k, silhouette=sil, top_terms=top_terms)


def _top_terms_per_cluster(x, labels, vocab, k, top_n) -> dict[int, list[str]]:
    """Highest mean-TF-IDF terms within each cluster (makes clusters legible)."""
    out: dict[int, list[str]] = {}
    for c in range(k):
        rows = np.where(labels == c)[0]
        if len(rows) == 0:
            out[c] = []
            continue
        mean_tfidf = np.asarray(x[rows].mean(axis=0)).ravel()
        top_idx = mean_tfidf.argsort()[::-1][:top_n]
        out[c] = [vocab[i] for i in top_idx if mean_tfidf[i] > 0]
    return out


def plot_clusters(result: ClusterResult, out_path: str | Path) -> Path:
    """Render a 2-D scatter of the clustered occupations."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    a = result.assignments
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(a["svd_x"], a["svd_y"], c=a["cluster"], cmap="tab10", alpha=0.6)
    plt.legend(*scatter.legend_elements(), title="Cluster", loc="best")
    plt.title("Occupation Clusters (TF-IDF -> SVD -> KMeans)")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    result.plot_path = out_path
    return out_path
