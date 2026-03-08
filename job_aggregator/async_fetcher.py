import aiohttp
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential


logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def fetch_json(session, url, headers=None):
    """
    Fetch JSON asynchronously with retries and exponential backoff.
    """

    try:
        async with session.get(url, headers=headers, timeout=10) as response:

            response.raise_for_status()

            return await response.json()

    except Exception as e:

        logger.warning(f"Request failed for {url}: {e}")

        raise


async def fetch_all(requests):
    """
    Fetch multiple API endpoints concurrently with rate limiting.
    """

    connector = aiohttp.TCPConnector(limit=5)

    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:

        tasks = [
            fetch_json(session, url, headers)
            for url, headers in requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

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
        "remoteok": results[0] if not isinstance(results[0], Exception) else None,
        "remotive": results[1] if not isinstance(results[1], Exception) else None,
        "arbeitnow": results[2] if not isinstance(results[2], Exception) else None,
    }