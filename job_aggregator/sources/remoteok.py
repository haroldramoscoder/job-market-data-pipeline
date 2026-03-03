import requests

REMOTEOK_URL = "https://remoteok.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_remoteok():
    response = requests.get(REMOTEOK_URL, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

def process_remoteok(jobs, match_keywords, keywords):
    results = []
    for job in jobs:
        if isinstance(job, dict) and "position" in job:
            combined = f"{job.get('position','')} {' '.join(job.get('tags', []))} {job.get('description','')}"
            if match_keywords(combined, keywords):
                results.append({
                    "Source": "RemoteOK",
                    "Title": job.get("position"),
                    "Company": job.get("company"),
                    "Location": job.get("location"),
                    "Date Posted": job.get("date"),
                    "URL": job.get("url")
                })
    return results