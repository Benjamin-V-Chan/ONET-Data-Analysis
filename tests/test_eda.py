"""Tests for the EDA module."""

from __future__ import annotations

from onet_analysis.eda import clean_keyword_frame, run_eda, soc_code_coverage


def test_soc_coverage(keyword_df):
    df, cols = clean_keyword_frame(keyword_df)
    cov = soc_code_coverage(df, cols)
    row = cov.set_index("Keyword")["Unique SOC Codes"]
    assert row["technology"] == 1  # both SOC 15
    assert row["healthcare"] == 1  # both SOC 29


def test_run_eda_writes_outputs(keyword_df, tmp_path):
    results = tmp_path / "results"
    processed = tmp_path / "processed"
    out = run_eda(keyword_df, results, processed)

    assert (processed / "soc_code_coverage.csv").is_file()
    assert (processed / "occupation_distribution.csv").is_file()
    assert len(out.plots) >= 1
    for p in out.plots:
        assert p.is_file()
