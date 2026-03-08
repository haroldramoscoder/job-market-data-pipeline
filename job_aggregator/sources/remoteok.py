import requests

REMOTEOK_URL = "https://remoteok.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_remoteok():
    try:
        response = requests.get(REMOTEOK_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"RemoteOK API error: {e}")
        return []

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
                    "URL": job.get("url"),
                    "Description": job.get("description"),
                    "Tags": job.get("tags")
                })
    return results