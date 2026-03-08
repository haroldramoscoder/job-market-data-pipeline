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
from job_aggregator.utils import print_summary
from job_aggregator.utils import print_skill_summary
from job_aggregator.utils import extract_skills


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
        url = job.get("URL")
        if url and url not in seen:
            seen.add(url)
            unique.append(job)
    return unique


def save_output(jobs, output_format, days_filter):
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    df = pd.DataFrame(jobs)

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

    # -----------------------------
    # Export
    # -----------------------------
    if output_format == "excel":
        filename = f"output/jobs_{timestamp}.xlsx"
        df.to_excel(filename, index=False)

    elif output_format == "csv":
        filename = f"output/jobs_{timestamp}.csv"
        df.to_csv(filename, index=False)

    elif output_format == "json":
        filename = f"output/jobs_{timestamp}.json"
        df.to_json(filename, orient="records", indent=2)

    print(f"\nSaved {len(df)} jobs to {filename}")


# ===============================
# Main
# ===============================

def main():
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

    remoteok_data = fetch_remoteok()
    all_jobs += process_remoteok(remoteok_data, match_keywords, KEYWORDS)
    logger.info("RemoteOK processed")

    remotive_data = fetch_remotive()
    all_jobs += process_remotive(remotive_data, match_keywords, KEYWORDS)
    logger.info("Remotive processed")

    arbeitnow_data = fetch_arbeitnow()
    all_jobs += process_arbeitnow(arbeitnow_data, match_keywords, KEYWORDS)
    logger.info("Arbeitnow processed")

    muse_raw_jobs = fetch_muse_paginated(MUSE_MAX_PAGES)
    all_jobs += process_muse(muse_raw_jobs, match_keywords, KEYWORDS)
    logger.info("The Muse processed")

    unique_jobs = deduplicate(all_jobs)

    save_output(unique_jobs, OUTPUT_FORMAT, DAYS_FILTER)


if __name__ == "__main__":
    main()