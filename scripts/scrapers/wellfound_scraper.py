"""
PlacementPulse - Wellfound (AngelList Talent) Public Scraper
Scrapes the publicly visible job search page for India internships/jobs.
Does NOT use any API key; only public HTML.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import get

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

SEARCH_URLS = [
    "https://wellfound.com/jobs?country=IN&role=engineer&jobType=internship",
    "https://wellfound.com/jobs?country=IN&role=engineer&jobType=full_time&experience=0_2",
]


class WellfoundScraper(BaseScraper):
    name = "wellfound"
    base_url = "https://wellfound.com"

    def scrape(self) -> List[Opportunity]:
        if not BS4_AVAILABLE:
            self.log.warning("BeautifulSoup4 not installed — skipping Wellfound")
            return []

        all_opps: List[Opportunity] = []
        for url in SEARCH_URLS:
            opps = self._scrape_page(url)
            all_opps.extend(opps)
            self.log.info("  Wellfound %s → %d items", url.split("?")[1][:30], len(opps))
        return all_opps

    def _scrape_page(self, url: str) -> List[Opportunity]:
        resp = get(url, headers={
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://wellfound.com/",
        })
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []

        # Wellfound uses React / Next.js — try JSON data islands first
        for script in soup.find_all("script", type="application/json"):
            text = script.string or ""
            if "jobListings" in text or "jobs" in text.lower():
                opps.extend(self._extract_json_island(text, url))
                if opps:
                    return opps

        # Fallback: HTML selectors
        for card in soup.select("[class*='JobCard'], [class*='job-card'], [data-test*='job']"):
            title_el = card.select_one("h2, h3, [class*='title'], [class*='role']")
            company_el = card.select_one("[class*='company'], [class*='startup']")
            link_el = card.select_one("a[href]")
            loc_el = card.select_one("[class*='location']")

            if not title_el or not link_el:
                continue

            href = link_el["href"]
            if not href.startswith("http"):
                href = self.base_url + href

            opps.append(Opportunity(
                title=title_el.get_text(strip=True),
                company=company_el.get_text(strip=True) if company_el else "Various",
                category="internship" if "internship" in url else "fresher-job",
                apply_link=href,
                source_url=url,
                source_name="Wellfound",
                location=loc_el.get_text(strip=True) if loc_el else "India",
                is_india=True,
            ))
        return opps

    def _extract_json_island(self, text: str, url: str) -> List[Opportunity]:
        """Parse Next.js data island for job listings."""
        import json
        try:
            data = json.loads(text)
        except ValueError:
            return []

        opps = []
        def _walk(obj):
            if isinstance(obj, list):
                for v in obj:
                    _walk(v)
            elif isinstance(obj, dict):
                title = obj.get("title") or obj.get("role") or ""
                company = (obj.get("company") or {}).get("name") or obj.get("startupName") or ""
                link = obj.get("remoteUrl") or obj.get("url") or ""
                location = obj.get("locationNames") or obj.get("locations") or ["India"]
                if isinstance(location, list):
                    location = ", ".join(location)
                if title and company:
                    opps.append(Opportunity(
                        title=title,
                        company=company,
                        category="internship" if "internship" in url else "fresher-job",
                        apply_link=link,
                        source_url=url,
                        source_name="Wellfound",
                        location=location,
                        is_india=True,
                    ))
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        _walk(v)

        _walk(data)
        return opps[:50]
