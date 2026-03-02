import requests
import pandas as pd
import os
import argparse
from datetime import datetime, timedelta
from cli import parse_arguments
from sources.remoteok import fetch_remoteok, process_remoteok
from sources.remotive import fetch_remotive, process_remotive
from sources.arbeitnow import fetch_arbeitnow, process_arbeitnow
from sources.muse import fetch_muse_paginated, process_muse

# =============================== 
# CLI Setup (Professional)
# ===============================

args = parse_arguments()

USER_KEYWORDS = args.keywords
DAYS_FILTER = args.days
MUSE_MAX_PAGES = args.pages
STRICT_MODE = args.strict

# ===============================
# API URLs
# ===============================

REMOTEOK_URL = "https://remoteok.com/api"
REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"
MUSE_BASE_URL = "https://www.themuse.com/api/public/jobs?page={}"

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ===============================
# Keyword Expansion
# ===============================

ROLE_PRESETS = {
    "data": [
        "data", "analytics", "analyst", "scientist",
        "machine learning", "ml", "ai", "sql", "python"
    ]
}

def expand_keywords(keywords):
    if STRICT_MODE:
        return [k.lower() for k in keywords]

    expanded = set()
    for keyword in keywords:
        keyword_lower = keyword.lower()
        expanded.add(keyword_lower)
        if keyword_lower in ROLE_PRESETS:
            expanded.update(ROLE_PRESETS[keyword_lower])
    return list(expanded)

KEYWORDS = expand_keywords(USER_KEYWORDS)

# ===============================
# Utilities
# ===============================

def match_keywords(text, keywords):
    text = text.lower()
    return any(keyword in text for keyword in keywords)

def fetch_json(url):
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else {}

# ===============================
# Deduplicate
# ===============================

def deduplicate(jobs):
    seen = set()
    unique = []
    for job in jobs:
        url = job.get("URL")
        if url and url not in seen:
            seen.add(url)
            unique.append(job)
    return unique

# ===============================
# Save
# ===============================

def save_to_excel(jobs):
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"output/aggregated_jobs_{timestamp}.xlsx"

    df = pd.DataFrame(jobs)

    if not df.empty:
        df["Date Posted"] = pd.to_datetime(
            df["Date Posted"], errors="coerce"
        ).dt.tz_localize(None)

        if DAYS_FILTER:
            cutoff = datetime.now() - timedelta(days=DAYS_FILTER)
            df = df[df["Date Posted"] >= cutoff]
            print(f"\nFiltered to last {DAYS_FILTER} days.")

        df = df.sort_values(by="Date Posted", ascending=False)

    df.to_excel(filename, index=False)

    print(f"\nSaved {len(df)} total jobs to {filename}")

# ===============================
# Main
# ===============================

def main():
    print(f"\nUser keywords: {USER_KEYWORDS}")
    print(f"Expanded keywords: {KEYWORDS}")
    if DAYS_FILTER:
        print(f"Freshness filter: last {DAYS_FILTER} days")

    all_jobs = []

    remoteok_data = fetch_remoteok()
    all_jobs += process_remoteok(remoteok_data, match_keywords, KEYWORDS)
    print("RemoteOK processed")

    remotive_data = fetch_remotive()
    all_jobs += process_remotive(remotive_data, match_keywords, KEYWORDS)
    print("Remotive processed")

    arbeitnow_data = fetch_arbeitnow()
    all_jobs += process_arbeitnow(arbeitnow_data, match_keywords, KEYWORDS)
    print("Arbeitnow processed")

    muse_raw_jobs = fetch_muse_paginated(MUSE_MAX_PAGES)
    all_jobs += process_muse(muse_raw_jobs, match_keywords, KEYWORDS)
    print("The Muse processed")

    unique_jobs = deduplicate(all_jobs)
    save_to_excel(unique_jobs)

if __name__ == "__main__":
    main()