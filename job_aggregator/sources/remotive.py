import requests

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

def fetch_remotive():
    try:
        response = requests.get(REMOTIVE_URL, timeout=10)
        response.raise_for_status()
        return response.json().get("jobs", [])
    except requests.RequestException as e:
        print(f"Remotive API error: {e}")
        return []

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
                "URL": job.get("url"),
                "Description": job.get("description"),
                "Tags": job.get("category")
            })
    return results