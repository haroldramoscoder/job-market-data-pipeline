import requests

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"

def fetch_arbeitnow():
    response = requests.get(ARBEITNOW_URL)
    return response.json().get("data", []) if response.status_code == 200 else []

def process_arbeitnow(jobs, match_keywords, keywords):
    results = []
    for job in jobs:
        combined = f"{job.get('title','')} {job.get('description','')}"
        if match_keywords(combined, keywords):
            results.append({
                "Source": "Arbeitnow",
                "Title": job.get("title"),
                "Company": job.get("company_name"),
                "Location": job.get("location"),
                "Date Posted": job.get("created_at"),
                "URL": job.get("url")
            })
    return results