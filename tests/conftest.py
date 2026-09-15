"""Shared fixtures: small synthetic keyword-search and condensed frames."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def keyword_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Keyword": "technology", "Job Code": "15-2051.00", "Job Title": "Data Scientists", "SOC Code": "15"},
            {"Keyword": "technology", "Job Code": "15-1252.00", "Job Title": "Software Developers", "SOC Code": "15"},
            {"Keyword": "healthcare", "Job Code": "29-1141.00", "Job Title": "Registered Nurses", "SOC Code": "29"},
            {"Keyword": "healthcare", "Job Code": "29-1215.00", "Job Title": "Family Medicine Physicians", "SOC Code": "29"},
            {"Keyword": "design", "Job Code": "27-1024.00", "Job Title": "Graphic Designers", "SOC Code": "27"},
        ]
    )


@pytest.fixture
def condensed_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"occupation_code": "15-2051.00", "occupation_title": "Data Scientists",
             "description": "Analyze data using technology and statistics.",
             "skills": "Programming; Mathematics", "tasks": "Build technology models"},
            {"occupation_code": "15-1252.00", "occupation_title": "Software Developers",
             "description": "Design software and technology systems.",
             "skills": "Programming; Design", "tasks": "Write technology code"},
            {"occupation_code": "29-1141.00", "occupation_title": "Registered Nurses",
             "description": "Provide healthcare to patients.",
             "skills": "Care; Medicine", "tasks": "Deliver healthcare services"},
            {"occupation_code": "29-1215.00", "occupation_title": "Family Medicine Physicians",
             "description": "Diagnose and treat patients in healthcare settings.",
             "skills": "Medicine; Diagnosis", "tasks": "Practice healthcare"},
            {"occupation_code": "27-1024.00", "occupation_title": "Graphic Designers",
             "description": "Create visual design concepts.",
             "skills": "Design; Creativity", "tasks": "Produce design work"},
        ]
    )
