import aiohttp
import asyncio


async def fetch_json(session, url, headers=None):
    """
    Fetch JSON asynchronously with timeout and error handling.
    """

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            return await response.json()

    except Exception as e:
        print(f"Async fetch error: {e}")
        return None


async def fetch_all(requests):
    """
    Fetch multiple API endpoints concurrently.
    """

    async with aiohttp.ClientSession() as session:

        tasks = [
            fetch_json(session, url, headers)
            for url, headers in requests
        ]

        results = await asyncio.gather(*tasks)

    return results

async def fetch_job_sources():
    """
    Fetch all job APIs concurrently.
    """

    requests = [
        ("https://remoteok.com/api", {"User-Agent": "Mozilla/5.0"}),
        ("https://remotive.com/api/remote-jobs", None),
        ("https://www.arbeitnow.com/api/job-board-api", None)
    ]

    results = await fetch_all(requests)

    return {
        "remoteok": results[0],
        "remotive": results[1],
        "arbeitnow": results[2]
    }