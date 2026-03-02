import requests

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

def fetch_remotive():
    response = requests.get(REMOTIVE_URL)
    return response.json().get("jobs", []) if response.status_code == 200 else []

def process_remotive(jobs, match_keywords, keywords):
    results = []
    for job in jobs:
        combined = f"{job.get('title','')} {job.get('category','')} {job.get('description','')}"
        if match_keywords(combined, keywords):
            results.append({
                "Source": "Remotive",
                "Title": job.get("title"),
                "Company": job.get("company_name"),
                "Location": job.get("candidate_required_location"),
                "Date Posted": job.get("publication_date"),
                "URL": job.get("url")
            })
    return results