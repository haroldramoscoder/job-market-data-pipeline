import pandas as pd
from collections import Counter
import re
from job_aggregator.skills import SKILLS
import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

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

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:

        # create word-boundary regex
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills

def analyze_skills(df):
    """
    Analyze most common skills across jobs.
    Uses Title + Tags + Description if available.
    """

    skill_counter = Counter()

    for _, row in df.iterrows():

        combined_text = ""

        if "Title" in df.columns and pd.notna(row["Title"]):
            combined_text += row["Title"] + " "

        tags = row.get("Tags")

        if tags:
            if isinstance(tags, list):
                combined_text += " ".join(tags) + " "
            else:
                combined_text += str(tags) + " "

        if "Description" in df.columns and pd.notna(row["Description"]):
            combined_text += row["Description"]

        if combined_text:
            skills = extract_skills(combined_text)
            skill_counter.update(skills)

    return skill_counter

def print_skill_summary(df):

    skill_counts = analyze_skills(df)

    if not skill_counts:
        print("\nNo job descriptions available for skill analysis.")
        return

    print("\nTop Skills in Job Market")
    print("-" * 30)

    for skill, count in skill_counts.most_common(10):

        if count < 2:
            continue

        print(f"{skill}: {count}")

def save_raw_data(data, source):

    today = datetime.now().strftime("%Y-%m-%d")

    directory = f"data/raw/{source}"
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, f"{today}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Raw data saved: {filepath}")

def load_raw_data(source_name):
    """
    Load all raw JSON files for a source.
    """

    directory = f"data/raw/{source_name}"

    if not os.path.exists(directory):
        return []

    all_records = []

    for file in os.listdir(directory):
        if file.endswith(".json"):

            filepath = os.path.join(directory, file)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    all_records.extend(data)
                else:
                    all_records.append(data)

    return all_records

def save_processed_dataset(df):
    """
    Save cleaned dataset to the processed data layer with versioning.
    """

    directory = "data/processed"
    os.makedirs(directory, exist_ok=True)

    # Create date-based dataset version
    today = datetime.now().strftime("%Y-%m-%d")

    filepath = os.path.join(directory, f"jobs_{today}.parquet")

    # Normalize Tags column for parquet compatibility
    if "Tags" in df.columns:

        def normalize_tags(tags):
            if isinstance(tags, list):
                return "|".join(tags)
            elif tags:
                return str(tags)
            return None

        df["Tags"] = df["Tags"].apply(normalize_tags)

    df.to_parquet(filepath, index=False)

    print(f"\nProcessed dataset saved to {filepath}")

def update_warehouse(df):

    warehouse_path = "data/warehouse/jobs.parquet"

    # If warehouse already exists, load it
    if os.path.exists(warehouse_path):
        existing_df = pd.read_parquet(warehouse_path)

        combined_df = pd.concat([existing_df, df], ignore_index=True)

        # remove duplicates based on job URL
        combined_df = combined_df.drop_duplicates(subset=["URL"])

    else:
        combined_df = df

    combined_df.to_parquet(warehouse_path, index=False)

    print(f"\nWarehouse updated: {warehouse_path}")

def validate_dataset(df):

    initial_rows = len(df)

    missing_title = df["Title"].isna().sum()
    missing_company = df["Company"].isna().sum()
    missing_url = df["URL"].isna().sum()
    missing_description = df["Description"].isna().sum()

    print("\nDATA QUALITY REPORT")
    print("-------------------")
    print(f"Rows before validation: {initial_rows}")
    print(f"Missing title: {missing_title}")
    print(f"Missing company: {missing_company}")
    print(f"Missing URL: {missing_url}")
    print(f"Missing description: {missing_description}")

    df = df.dropna(subset=["Title", "Company", "URL"])

    final_rows = len(df)

    print(f"Rows after validation: {final_rows}")

    return df

def cleanup_old_files(directory, limit):

    path = Path(directory)

    if not path.exists():
        return

    files = sorted(
        [f for f in path.iterdir() if f.is_file()],
        key=lambda x: x.stat().st_mtime
    )

    file_count = len(files)

    if file_count <= limit:
        print(f"[Cleanup] {directory}: {file_count} files (within limit {limit})")
        return

    files_to_delete = files[: file_count - limit]

    print(f"[Cleanup] {directory}: removing {len(files_to_delete)} old files")

    for file in files_to_delete:
        print(f"[Cleanup] Deleting: {file.name}")
        file.unlink()

def generate_job_id(row):

    base_string = f"{row['Title']}_{row['Company']}_{row['Location']}_{row['Source']}"

    return hashlib.md5(base_string.encode()).hexdigest()