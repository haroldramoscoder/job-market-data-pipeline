import pandas as pd
from job_aggregator.utils import print_summary

def test_print_summary_empty():
    df = pd.DataFrame()
    print_summary(df)  # Should not crash

def test_print_summary_basic():
    df = pd.DataFrame({
        "Source": ["RemoteOK", "Remotive"],
        "Company": ["A", "B"],
        "Date Posted": pd.to_datetime(["2026-01-01", "2026-01-02"])
    })
    print_summary(df)