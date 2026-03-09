import aiohttp
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from job_aggregator.config_loader import load_sources_config


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

    sources = load_sources_config()

    requests = []

    for source in sources:

        endpoint = source["endpoint"]
        headers = source.get("headers")

        requests.append((endpoint, headers))

    results = await fetch_all(requests)

    source_results = {}

    for i, source in enumerate(sources):

        result = results[i]

        source_results[source["name"]] = (
            result if not isinstance(result, Exception) else None
        )

    return source_results