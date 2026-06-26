"""
PlacementPulse - Unstop (formerly Dare2Compete) Public API Scraper
Unstop exposes a public JSON endpoint used by their own website.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import fetch_json

BASE = "https://unstop.com/api/public/opportunity/search-result"

PARAMS_LIST = [
    {"oppType": "hackathon",   "page": 1, "size": 40, "country": "India"},
    {"oppType": "internship",  "page": 1, "size": 40, "country": "India"},
    {"oppType": "job",         "page": 1, "size": 40, "country": "India"},
    {"oppType": "competition", "page": 1, "size": 40, "country": "India"},
    {"oppType": "scholarship", "page": 1, "size": 40, "country": "India"},
    {"oppType": "fellowship",  "page": 1, "size": 20, "country": "India"},
]

_OPP_TYPE_MAP = {
    "hackathon": "hackathon",
    "internship": "internship",
    "job": "fresher-job",
    "competition": "hiring-challenge",
    "scholarship": "scholarship",
    "fellowship": "fellowship",
}


class UnstopScraper(BaseScraper):
    name = "unstop"
    base_url = "https://unstop.com"

    def scrape(self) -> List[Opportunity]:
        all_opps: List[Opportunity] = []
        for params in PARAMS_LIST:
            opps = self._fetch(params)
            all_opps.extend(opps)
            self.log.info(
                "  Unstop %s → %d items",
                params["oppType"],
                len(opps),
            )
        return all_opps

    def _fetch(self, params: dict) -> List[Opportunity]:
        data = fetch_json(BASE, params=params)
        if not data:
            return []

        items = (
            data.get("data", {}).get("data", [])
            or data.get("data", [])
            or []
        )
        opps = []
        for item in items:
            if not isinstance(item, dict):
                continue

            title = item.get("title") or item.get("name") or ""
            organisation = item.get("organisation", {}) or {}
            company = organisation.get("name") or item.get("company_name") or "Various"
            slug = item.get("public_url") or item.get("slug") or ""
            apply_link = f"https://unstop.com/{slug}" if slug else self.base_url
            deadline = item.get("end_date") or item.get("deadline") or ""
            location = item.get("city") or item.get("location") or "India"
            description = item.get("description") or ""
            opp_type = _OPP_TYPE_MAP.get(params["oppType"], "internship")

            if not title:
                continue

            opps.append(Opportunity(
                title=title,
                company=company,
                category=opp_type,
                apply_link=apply_link,
                source_url=self.base_url,
                source_name="Unstop",
                location=location,
                deadline=deadline[:10] if deadline else "",
                description=description[:500],
                is_india=True,
            ))
        return opps
