import pandas as pd

def print_summary(df):
    if df.empty:
        print("\nNo jobs found.")
        return

    print("\n" + "="*50)
    print("JOB SUMMARY")
    print("="*50)

    # Total jobs
    print(f"Total Jobs: {len(df)}")

    # Jobs by source
    print("\nJobs by Source:")
    source_counts = df["Source"].value_counts()
    for source, count in source_counts.items():
        print(f"  {source}: {count}")

    # Top companies
    print("\nTop 5 Companies:")
    company_counts = df["Company"].value_counts().head(5)
    for company, count in company_counts.items():
        print(f"  {company}: {count}")

    # Newest job
    newest_date = df["Date Posted"].max()
    print(f"\nMost Recent Job Posted: {newest_date}")

    # Jobs in last 7 days
    recent_jobs = df[df["Date Posted"] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
    print(f"Jobs Posted in Last 7 Days: {len(recent_jobs)}")

    print("="*50 + "\n")