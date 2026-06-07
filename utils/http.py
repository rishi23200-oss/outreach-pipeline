"""
Shared HTTP helpers — retry on 429 / 5xx, surface clear errors.
"""

import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def make_session(retries: int = 3, backoff: float = 1.5) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def safe_get(session: requests.Session, url: str, **kwargs) -> dict | None:
    return _safe_request(session, "GET", url, **kwargs)


def safe_post(session: requests.Session, url: str, **kwargs) -> dict | None:
    return _safe_request(session, "POST", url, **kwargs)


def _safe_request(session, method, url, rate_delay=1.0, **kwargs):
    try:
        resp = session.request(method, url, timeout=30, **kwargs)

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 5))
            logger.warning(f"Rate-limited by {url}. Waiting {wait}s …")
            time.sleep(wait)
            resp = session.request(method, url, timeout=30, **kwargs)

        resp.raise_for_status()
        time.sleep(rate_delay)   # polite delay between calls
        return resp.json()

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} from {url}: {e.response.text[:300]}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None
