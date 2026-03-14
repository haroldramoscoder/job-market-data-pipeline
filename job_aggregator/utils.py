import pandas as pd
from collections import Counter
import re
from job_aggregator.skills import SKILLS, SKILL_CATEGORIES
import json
import os
from datetime import datetime
from pathlib import Path
import hashlib
import logging

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

    logging.debug(f"Raw data saved: {filepath}")

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

    logging.debug(f"Processed dataset saved: {filepath}")

def update_warehouse(df):

    directory = "data/warehouse"
    os.makedirs(directory, exist_ok=True)

    warehouse_path = os.path.join(directory, "jobs.parquet")

    if os.path.exists(warehouse_path):
        existing_df = pd.read_parquet(warehouse_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["URL"])
    else:
        combined_df = df

    combined_df.to_parquet(warehouse_path, index=False)

    logging.debug(f"Warehouse updated: {warehouse_path}")

def validate_dataset(df):

    initial_rows = len(df)

    missing_title = df["Title"].isna().sum()
    missing_company = df["Company"].isna().sum()
    missing_url = df["URL"].isna().sum()
    missing_description = df["Description"].isna().sum()

    if logging.getLogger().isEnabledFor(logging.DEBUG):

        print("\nDATA QUALITY REPORT")
        print("-------------------")
        print(f"Rows before validation: {initial_rows}")
        print(f"Missing title: {missing_title}")
        print(f"Missing company: {missing_company}")
        print(f"Missing URL: {missing_url}")
        print(f"Missing description: {missing_description}")

    df = df.dropna(subset=["Title", "Company", "URL"])

    final_rows = len(df)

    logging.debug(f"Rows after validation: {final_rows}")

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
        logging.debug(f"[Cleanup] {directory}: {file_count} files (within limit {limit})")
        return

    files_to_delete = files[: file_count - limit]

    logging.debug(f"[Cleanup] {directory}: removing {len(files_to_delete)} old files")

    for file in files_to_delete:
        logging.debug(f"[Cleanup] Deleting: {file.name}")
        file.unlink()

def generate_job_id(row):

    base_string = f"{row.get('Title','')}_{row.get('Company','')}_{row.get('Location','')}_{row.get('Source','')}"

    return hashlib.md5(base_string.encode()).hexdigest()

def analyze_skill_categories(df):

    category_counter = Counter()

    skill_counts = analyze_skills(df)

    for skill, count in skill_counts.items():

        for category, skills in SKILL_CATEGORIES.items():

            if skill in skills:
                category_counter[category] += count

    return category_counter

def print_skill_categories(df):

    category_counts = analyze_skill_categories(df)

    if not category_counts:
        return

    print("\nSkill Demand by Category")
    print("-" * 30)

    for category, count in category_counts.most_common():

        print(f"{category}: {count}")

def skill_trends_last_30_days(df):

    cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)

    recent_jobs = df[df["Date Posted"] >= cutoff]

    skill_counts = analyze_skills(recent_jobs)

    return skill_counts

def print_skill_trends(df):

    trends = skill_trends_last_30_days(df)

    print("\nTop Skills Last 30 Days")
    print("-" * 30)

    for skill, count in trends.most_common(10):
        if count < 2:
            continue
        print(f"{skill}: {count}")

def export_ml_dataset(df):

    directory = "data/ml"
    os.makedirs(directory, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    filepath = os.path.join(directory, f"job_market_dataset_{today}.parquet")

    ml_columns = [
        "job_id",
        "Title",
        "Company",
        "Location",
        "Date Posted",
        "Source",
        "Description",
        "Skills"
    ]

    ml_df = df[ml_columns].copy()

    # Normalize column names for ML pipelines
    ml_df.columns = [
        "job_id",
        "title",
        "company",
        "location",
        "date_posted",
        "source",
        "description",
        "skills"
    ]

    ml_df.to_parquet(filepath, index=False)

    logging.debug(f"ML dataset exported: {filepath}")

def log_pipeline_run(runtime, jobs_before, jobs_after):

    directory = "data/pipeline_runs"
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, "pipeline_runs.parquet")

    run_data = pd.DataFrame([{
        "run_timestamp": datetime.now(),
        "runtime_seconds": runtime,
        "jobs_collected": jobs_before,
        "jobs_after_dedup": jobs_after
    }])

    if os.path.exists(filepath):

        existing = pd.read_parquet(filepath)
        run_data = pd.concat([existing, run_data], ignore_index=True)

    run_data.to_parquet(filepath, index=False)

    logging.debug("Pipeline run metadata logged.")

def export_skill_trends(df):

    directory = "data/analytics"
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, "skill_trends.parquet")

    skills = []

    today = datetime.now().date()

    for skill_string in df["Skills"].dropna():

        for skill in skill_string.split("|"):

            skills.append({"date": today, "skill": skill})

    trends_df = pd.DataFrame(skills)

    trends_df = trends_df.groupby(["date", "skill"]).size().reset_index(name="count")

    if os.path.exists(filepath):

        existing = pd.read_parquet(filepath)
        trends_df = pd.concat([existing, trends_df], ignore_index=True)

    trends_df.to_parquet(filepath, index=False)

    logging.debug("Skill trends dataset updated.")

def validate_schema(df):

    required_columns = [
        "Title",
        "Company",
        "Location",
        "Date Posted",
        "URL",
        "Description"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Dataset schema error: missing columns {missing}")

    logging.debug("Dataset schema validation passed.")

def detect_job_changes(df):

    warehouse_path = "data/warehouse/jobs.parquet"

    if not os.path.exists(warehouse_path):
        print("\nJOB UPDATE REPORT")
        print("-----------------")
        print("First pipeline run — no previous warehouse to compare.")
        return

    previous = pd.read_parquet(warehouse_path)

    previous_ids = set(previous["job_id"])
    current_ids = set(df["job_id"])

    new_jobs = current_ids - previous_ids
    removed_jobs = previous_ids - current_ids

    print("\nJOB UPDATE REPORT")
    print("-----------------")
    print(f"New jobs detected: {len(new_jobs)}")
    print(f"Jobs removed since last run: {len(removed_jobs)}")