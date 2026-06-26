"""
PlacementPulse - Scraper Base Class
All scrapers inherit from BaseScraper. Implement `scrape()` to return
a list of Opportunity objects.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from scripts.core.storage import save_raw


class BaseScraper(ABC):
    """
    Contract every scraper must fulfil.

    Usage::

        class MyScraper(BaseScraper):
            name = "my-source"
            base_url = "https://example.com"

            def scrape(self) -> List[Opportunity]:
                ...
    """

    name: str = "unnamed"
    base_url: str = ""
    enabled: bool = True

    def __init__(self) -> None:
        self.log = get_logger(f"scraper.{self.name}")

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self) -> List[Opportunity]:
        """
        Entry-point called by the pipeline.
        Wraps `scrape()` with error handling and raw-data persistence.
        """
        if not self.enabled:
            self.log.info("Scraper '%s' is disabled — skipping", self.name)
            return []

        self.log.info("Starting scraper: %s", self.name)
        start = time.monotonic()

        try:
            results = self.scrape()
        except Exception as exc:
            self.log.error("Scraper '%s' failed: %s", self.name, exc, exc_info=True)
            return []

        elapsed = time.monotonic() - start
        self.log.info(
            "Scraper '%s' finished in %.1fs — %d opportunities found",
            self.name, elapsed, len(results),
        )

        if results:
            save_raw(self.name, [r.to_dict() for r in results])

        return results

    @abstractmethod
    def scrape(self) -> List[Opportunity]:
        """Subclasses implement this. Must return a list of Opportunity."""
        ...
