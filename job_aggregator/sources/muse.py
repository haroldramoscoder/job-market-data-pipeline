import requests
import logging

MUSE_BASE_URL = "https://www.themuse.com/api/public/jobs?page={}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_muse_paginated(max_pages):
    results = []

    for page in range(1, max_pages + 1):
        logger = logging.getLogger(__name__)
        logger.debug(f"Fetching The Muse page {page}...")
        response = requests.get(MUSE_BASE_URL.format(page), headers=HEADERS)

        if response.status_code != 200:
            break

        jobs = response.json().get("results", [])
        if not jobs:
            break

        results.extend(jobs)

    return results


def process_muse(jobs, match_keywords, keywords):
    results = []

    for job in jobs:
        combined = f"{job.get('name','')} {job.get('contents','')}"
        if match_keywords(combined, keywords):
            results.append({
                "Source": "TheMuse",
                "Title": job.get("name"),
                "Company": job.get("company", {}).get("name"),
                "Location": ", ".join(
                    [loc["name"] for loc in job.get("locations", [])]
                ),
                "Date Posted": job.get("publication_date"),
                "URL": job.get("refs", {}).get("landing_page")
            })

    return results