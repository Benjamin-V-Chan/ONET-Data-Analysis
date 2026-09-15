"""Tests for occupation clustering."""

from __future__ import annotations

import pandas as pd
import pytest

from onet_analysis.clustering import cluster_occupations, plot_clusters


def test_cluster_basic(condensed_df):
    result = cluster_occupations(condensed_df, n_clusters=3)
    assert result.n_clusters == 3
    assert "cluster" in result.assignments.columns
    assert len(result.assignments) == len(condensed_df)
    assert set(result.top_terms.keys()) == set(range(3))


def test_cluster_clamps_k_to_samples():
    df = pd.DataFrame({"occupation_title": ["data science role", "healthcare nursing role"]})
    result = cluster_occupations(df, n_clusters=10)
    assert result.n_clusters == 2  # clamped to sample count


def test_cluster_requires_two_rows():
    df = pd.DataFrame({"occupation_title": ["only one"]})
    with pytest.raises(ValueError):
        cluster_occupations(df)


def test_plot_clusters_writes_file(condensed_df, tmp_path):
    result = cluster_occupations(condensed_df, n_clusters=2)
    path = plot_clusters(result, tmp_path / "clusters.png")
    assert path.is_file()
