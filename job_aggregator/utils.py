import pandas as pd
from collections import Counter
import re
from job_aggregator.skills import SKILLS
import json
import os
from datetime import datetime

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

def save_raw_data(data, source_name):
    """
    Save raw API responses to the data/raw directory.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    directory = f"data/raw/{source_name}"
    os.makedirs(directory, exist_ok=True)

    filename = f"{directory}/{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filename

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

    import os
    from datetime import datetime

    directory = "data/processed"
    os.makedirs(directory, exist_ok=True)

    # Create date-based dataset version
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filepath = os.path.join(directory, f"jobs_{timestamp}.parquet")

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