import requests
import pandas as pd
import os
import logging
from datetime import datetime, timedelta

from job_aggregator.cli import parse_arguments
from job_aggregator.sources.remoteok import fetch_remoteok, process_remoteok
from job_aggregator.sources.remotive import fetch_remotive, process_remotive
from job_aggregator.sources.arbeitnow import fetch_arbeitnow, process_arbeitnow
from job_aggregator.sources.muse import fetch_muse_paginated, process_muse
from job_aggregator.utils import print_summary, print_skill_summary, extract_skills, save_raw_data, load_raw_data, save_processed_dataset, validate_dataset, update_warehouse, cleanup_old_files, generate_job_id, print_skill_categories, print_skill_trends
from job_aggregator.cleaning import clean_jobs_dataframe
import asyncio
from job_aggregator.async_fetcher import fetch_job_sources
import time

# ===============================
# Keyword Expansion Presets
# ===============================

ROLE_PRESETS = {
    "data": [
        "data", "analytics", "analyst", "scientist",
        "machine learning", "ml", "ai", "sql", "python"
    ]
}


# ===============================
# Utilities
# ===============================

def expand_keywords(keywords, strict_mode):
    if strict_mode:
        return [k.lower() for k in keywords]

    expanded = set()
    for keyword in keywords:
        keyword_lower = keyword.lower()
        expanded.add(keyword_lower)
        if keyword_lower in ROLE_PRESETS:
            expanded.update(ROLE_PRESETS[keyword_lower])
    return list(expanded)


def match_keywords(text, keywords):
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def deduplicate(jobs):
    seen = set()
    unique = []

    for job in jobs:

        key = (
            job.get("Source"),
            job.get("URL")
        )

        if key not in seen and job.get("URL"):
            seen.add(key)
            unique.append(job)

    return unique


def save_output(jobs, output_format, days_filter):

    os.makedirs("output", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    df = pd.DataFrame(jobs)

    df = clean_jobs_dataframe(df)
    df = validate_dataset(df)
    df["job_id"] = df.apply(generate_job_id, axis=1)
    # Final deduplication using stable identifier
    before = len(df)
    df = df.drop_duplicates(subset=["job_id"])
    after = len(df)

    print(f"Job ID dedup removed {before-after} duplicates")

    if not df.empty:

        # -----------------------------
        # Detect skills per job
        # -----------------------------
        def detect_skills(row):
            text = ""

            if "Title" in df.columns and pd.notna(row.get("Title")):
                text += row["Title"] + " "

            tags = row.get("Tags")

            if tags:
                if isinstance(tags, list):
                    text += " ".join(tags) + " "
                else:
                    text += str(tags) + " "

            if "Description" in df.columns and pd.notna(row.get("Description")):
                text += row["Description"]

            skills = extract_skills(text)

            return "|".join(skills)

        df["Skills"] = df.apply(detect_skills, axis=1)

        # -----------------------------
        # Skill count
        # -----------------------------
        def count_skills(skill_string):

            if not skill_string:
                return 0

            return len(skill_string.split("|"))

        df["Skill_Count"] = df["Skills"].apply(count_skills)


        # -----------------------------
        # Primary skill category
        # -----------------------------
        from job_aggregator.skills import SKILL_CATEGORIES

        def get_primary_category(skill_string):

            if not skill_string:
                return None

            skills = skill_string.split("|")

            category_scores = {}

            for skill in skills:

                for category, category_skills in SKILL_CATEGORIES.items():

                    if skill in category_skills:
                        category_scores[category] = category_scores.get(category, 0) + 1

            if not category_scores:
                return None

            return max(category_scores, key=category_scores.get)

        df["Primary_Skill_Category"] = df["Skills"].apply(get_primary_category)

        # -----------------------------
        # Date cleaning
        # -----------------------------
        df["Date Posted"] = pd.to_datetime(
            df["Date Posted"], errors="coerce"
        ).dt.tz_localize(None)

        # -----------------------------
        # Freshness filter
        # -----------------------------
        if days_filter:
            cutoff = datetime.now() - timedelta(days=days_filter)
            df = df[df["Date Posted"] >= cutoff]
            print(f"\nFiltered to last {days_filter} days.")

        # -----------------------------
        # Sorting
        # -----------------------------
        df = df.sort_values(by="Date Posted", ascending=False)

        # -----------------------------
        # Console summaries
        # -----------------------------
        print_summary(df)
        print_skill_summary(df)
        print_skill_categories(df)
        print_skill_trends(df)

        save_processed_dataset(df)
        update_warehouse(df)

    # -----------------------------
    # Export
    # -----------------------------
    if output_format == "excel":
        filename = f"output/jobs_{today}.xlsx"
        df.to_excel(filename, index=False)

    elif output_format == "csv":
        filename = f"output/jobs_{today}.csv"
        df.to_csv(filename, index=False)

    elif output_format == "json":
        filename = f"output/jobs_{today}.json"
        df.to_json(filename, orient="records", indent=2)

    print(f"\nSaved {len(df)} jobs to {filename}")
    return len(df)


# ===============================
# Main
# ===============================

def main():
    pipeline_start = time.time()
    args = parse_arguments()

    USER_KEYWORDS = args.keywords
    DAYS_FILTER = args.days
    MUSE_MAX_PAGES = args.pages
    STRICT_MODE = args.strict
    OUTPUT_FORMAT = args.format

    # Logging setup
    log_level = logging.DEBUG if args.verbose else logging.INFO

    logger = logging.getLogger()
    logger.setLevel(log_level)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(console_handler)

        if args.logfile:
            file_handler = logging.FileHandler(args.logfile)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Expand keywords
    KEYWORDS = expand_keywords(USER_KEYWORDS, STRICT_MODE)

    print(f"\nUser keywords: {USER_KEYWORDS}")
    print(f"Expanded keywords: {KEYWORDS}")
    if DAYS_FILTER:
        print(f"Freshness filter: last {DAYS_FILTER} days")

    all_jobs = []

    if args.use_raw:

        print("\nLoading raw data instead of calling APIs...")

        remoteok_data = load_raw_data("remoteok")
        all_jobs += process_remoteok(remoteok_data, match_keywords, KEYWORDS)

        remotive_data = load_raw_data("remotive")
        all_jobs += process_remotive(remotive_data, match_keywords, KEYWORDS)

        arbeitnow_data = load_raw_data("arbeitnow")
        all_jobs += process_arbeitnow(arbeitnow_data, match_keywords, KEYWORDS)

        muse_raw_jobs = load_raw_data("muse")
        all_jobs += process_muse(muse_raw_jobs, match_keywords, KEYWORDS)

    else:

        print("\nFetching APIs asynchronously...")
        fetch_start = time.time()

        api_results = asyncio.run(fetch_job_sources())

        fetch_time = round(time.time() - fetch_start, 2)
        logger.info(f"API fetch completed in {fetch_time} seconds")

        # ---- RemoteOK ----
        remoteok_data = api_results.get("remoteok") or []
        save_raw_data(remoteok_data, "remoteok")
        all_jobs += process_remoteok(remoteok_data, match_keywords, KEYWORDS)
        logger.info("RemoteOK processed")

        # ---- Remotive ----
        remotive_response = api_results.get("remotive") or {}
        remotive_data = remotive_response.get("jobs", [])
        save_raw_data(remotive_data, "remotive")
        all_jobs += process_remotive(remotive_data, match_keywords, KEYWORDS)
        logger.info("Remotive processed")

        # ---- Arbeitnow ----
        arbeitnow_response = api_results.get("arbeitnow") or {}
        arbeitnow_data = arbeitnow_response.get("data", [])
        save_raw_data(arbeitnow_data, "arbeitnow")
        all_jobs += process_arbeitnow(arbeitnow_data, match_keywords, KEYWORDS)
        logger.info("Arbeitnow processed")

        # ---- Muse (still synchronous due to pagination) ----
        muse_raw_jobs = fetch_muse_paginated(MUSE_MAX_PAGES)
        save_raw_data(muse_raw_jobs, "muse")
        all_jobs += process_muse(muse_raw_jobs, match_keywords, KEYWORDS)
        logger.info("The Muse processed")

    before_count = len(all_jobs)

    unique_jobs = deduplicate(all_jobs)

    after_count = len(unique_jobs)

    logger.info(f"Deduplicated jobs: {before_count - after_count} duplicates removed")

    try:
        final_count = save_output(unique_jobs, OUTPUT_FORMAT, DAYS_FILTER)
    except Exception as e:
        logger.exception("Pipeline failed during output stage")
        raise
    
    pipeline_time = round(time.time() - pipeline_start, 2)

    print("\nPIPELINE RUN SUMMARY")
    print("-------------------")
    print(f"Total jobs collected: {before_count}")
    print(f"Jobs after deduplication: {final_count}")
    print(f"Pipeline runtime: {pipeline_time} seconds")

    cleanup_old_files("data/raw/remoteok", 90)
    cleanup_old_files("data/raw/remotive", 90)
    cleanup_old_files("data/raw/arbeitnow", 90)
    cleanup_old_files("data/raw/muse", 90)
    cleanup_old_files("data/processed", 30)
    cleanup_old_files("output", 7)


if __name__ == "__main__":
    main()