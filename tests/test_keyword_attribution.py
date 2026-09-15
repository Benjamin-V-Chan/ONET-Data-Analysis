"""Tests for keyword-to-feature attribution."""

from __future__ import annotations

from onet_analysis.keyword_attribution import analyze_keywords, plot_attribution


def test_attribution_counts(keyword_df, condensed_df):
    result = analyze_keywords(keyword_df, condensed_df)

    # Every keyword should appear as a row.
    assert set(result.index) == {"technology", "healthcare", "design"}
    # 'technology' occurs in description/tasks of the two tech occupations.
    assert result.loc["technology", "description"] >= 2
    assert result.loc["healthcare", "description"] >= 2
    # 'design' appears in the graphic designer row's fields.
    assert result.loc["design", "skills"] >= 1


def test_attribution_ignores_unknown_codes(keyword_df, condensed_df):
    kd = keyword_df.copy()
    kd.loc[len(kd)] = {"Keyword": "technology", "Job Code": "99-9999.99",
                       "Job Title": "Ghost", "SOC Code": "99"}
    result = analyze_keywords(kd, condensed_df)
    assert "technology" in result.index  # unknown code simply contributes nothing


def test_plot_attribution_writes(keyword_df, condensed_df, tmp_path):
    result = analyze_keywords(keyword_df, condensed_df)
    paths = plot_attribution(result, tmp_path)
    assert len(paths) == len(result)
    for p in paths:
        assert p.is_file()
