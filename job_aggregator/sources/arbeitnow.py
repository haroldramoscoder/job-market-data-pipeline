import requests

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"

def fetch_arbeitnow():
    try:
        response = requests.get(ARBEITNOW_URL, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"Arbeitnow API error: {e}")
        return []

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
                "URL": job.get("url"),
                "Description": job.get("description"),
                "Tags": job.get("tags")
            })
    return results