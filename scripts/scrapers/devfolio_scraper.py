"""
PlacementPulse - Devfolio Hackathon Scraper
Devfolio lists hackathons on their explore page with a public GraphQL endpoint.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import get

GRAPHQL_URL = "https://api.devfolio.co/api/search/hackathons"

QUERY_PAYLOAD = {
    "from": 0,
    "size": 50,
    "type": "hackathon",
    "status": "open",
}


class DevfolioScraper(BaseScraper):
    name = "devfolio"
    base_url = "https://devfolio.co"

    def scrape(self) -> List[Opportunity]:
        resp = get(
            GRAPHQL_URL,
            params=QUERY_PAYLOAD,
            headers={
                "Accept": "application/json",
                "Origin": "https://devfolio.co",
                "Referer": "https://devfolio.co/hackathons",
            },
        )
        if not resp:
            self.log.warning("No response from Devfolio API")
            return []

        try:
            data = resp.json()
        except ValueError:
            return []

        hits = (
            data.get("hits", {}).get("hits", [])
            or data.get("results", [])
            or []
        )
        opps: List[Opportunity] = []
        for hit in hits:
            src = hit.get("_source") or hit
            if not isinstance(src, dict):
                continue
            title = src.get("name") or src.get("title") or ""
            slug = src.get("slug") or ""
            url = f"https://devfolio.co/hackathons/{slug}" if slug else self.base_url
            description = src.get("description") or src.get("tagline") or ""
            deadline = src.get("submission_deadline") or src.get("end_date") or ""
            prize_amount = src.get("prize_pool") or ""

            if not title:
                continue

            tags = []
            if prize_amount:
                tags.append(f"Prize: {prize_amount}")

            opps.append(Opportunity(
                title=title,
                company="Devfolio",
                category="hackathon",
                apply_link=url,
                source_url=self.base_url,
                source_name="Devfolio",
                location="Remote / India",
                deadline=deadline[:10] if deadline else "",
                description=description[:500],
                work_mode="remote",
                is_india=True,
                tags=tags,
            ))

        self.log.info("Devfolio → %d hackathons", len(opps))
        return opps
