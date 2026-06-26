"""
PlacementPulse - Robust HTTP client with retry, rate-limiting, and UA rotation.
"""

from __future__ import annotations

import random
import time
from typing import Optional, Dict, Any
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import (
    REQUEST_TIMEOUT, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
    MAX_RETRIES, BACKOFF_FACTOR, USER_AGENTS,
)
from scripts.core.logger import get_logger

log = get_logger(__name__)


def _make_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_SESSION = _make_session()


def get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = REQUEST_TIMEOUT,
    respect_delay: bool = True,
) -> Optional[requests.Response]:
    """
    Send a GET request with automatic retry, UA rotation, and polite delays.
    Returns None on any unrecoverable error.
    """
    if respect_delay:
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    merged_headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    if headers:
        merged_headers.update(headers)

    try:
        response = _SESSION.get(
            url,
            params=params,
            headers=merged_headers,
            timeout=timeout,
        )
        log.debug("GET %s → %s", url, response.status_code)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as exc:
        log.warning("HTTP error for %s: %s", url, exc)
    except requests.exceptions.ConnectionError as exc:
        log.warning("Connection error for %s: %s", url, exc)
    except requests.exceptions.Timeout:
        log.warning("Timeout for %s", url)
    except requests.exceptions.RequestException as exc:
        log.error("Unexpected request error for %s: %s", url, exc)
    return None


def fetch_json(url: str, **kwargs) -> Optional[dict]:
    """Convenience wrapper that parses JSON."""
    resp = get(url, headers={"Accept": "application/json"}, **kwargs)
    if resp is None:
        return None
    try:
        return resp.json()
    except ValueError as exc:
        log.warning("JSON parse error for %s: %s", url, exc)
        return None


def fetch_text(url: str, **kwargs) -> Optional[str]:
    """Convenience wrapper that returns raw text."""
    resp = get(url, **kwargs)
    return resp.text if resp else None
