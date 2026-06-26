"""
PlacementPulse - HackerEarth Public API Scraper
HackerEarth exposes public JSON for challenges and hackathons.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import fetch_json

CHALLENGES_URL = "https://www.hackerearth.com/chrome-extension/challenges/"


class HackerEarthScraper(BaseScraper):
    name = "hackerearth"
    base_url = "https://www.hackerearth.com"

    def scrape(self) -> List[Opportunity]:
        data = fetch_json(CHALLENGES_URL)
        if not data:
            self.log.warning("No data from HackerEarth API")
            return []

        opps: List[Opportunity] = []
        for section_key in ("ongoing", "upcoming"):
            section = data.get(section_key, [])
            for item in section:
                if not isinstance(item, dict):
                    continue
                title = item.get("title") or ""
                url = item.get("url") or self.base_url
                company = item.get("company_name") or "HackerEarth"
                deadline = item.get("end_utc_tz") or item.get("end_date") or ""
                description = item.get("description") or ""
                challenge_type = item.get("type", "").lower()

                category = "hackathon"
                if "hiring" in challenge_type or "hiring" in title.lower():
                    category = "hiring-challenge"

                opps.append(Opportunity(
                    title=title,
                    company=company,
                    category=category,
                    apply_link=url,
                    source_url=self.base_url,
                    source_name="HackerEarth",
                    location="Remote / India",
                    deadline=deadline[:10] if deadline else "",
                    description=description[:500],
                    work_mode="remote",
                    is_india=True,
                ))

        self.log.info("HackerEarth → %d challenges", len(opps))
        return opps
