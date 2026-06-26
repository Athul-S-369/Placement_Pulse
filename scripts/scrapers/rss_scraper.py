"""
PlacementPulse - Generic RSS/Atom Feed Scraper
Handles any standard RSS 2.0 or Atom feed.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import fetch_text

try:
    from lxml import etree as ET
except ImportError:
    import xml.etree.ElementTree as ET  # type: ignore


# ─── Feed definitions ─────────────────────────────────────────────────────────
# Add more feeds here without touching any other code.

RSS_FEEDS: List[Dict] = [
    {
        "name": "HackerNews-Jobs",
        "url": "https://hnrss.org/jobs",
        "company": "Various",
        "category": "fresher-job",
        "source_name": "Hacker News",
    },
    {
        "name": "MLH-Hackathons",
        "url": "https://mlh.io/seasons/2025/events.rss",
        "company": "Various",
        "category": "hackathon",
        "source_name": "MLH",
    },
    {
        "name": "Devfolio-Hackathons",
        "url": "https://devfolio.co/hackathons.rss",
        "company": "Various",
        "category": "hackathon",
        "source_name": "Devfolio",
    },
    {
        "name": "GitHub-Internships",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/.github/scripts/listings.json",
        "company": "Various",
        "category": "internship",
        "source_name": "SimplifyJobs GitHub",
        "is_json": True,
    },
]


class RssScraper(BaseScraper):
    """Scrapes all configured RSS / Atom feeds."""

    name = "rss-feeds"
    base_url = ""

    def scrape(self) -> List[Opportunity]:
        all_opps: List[Opportunity] = []
        for feed in RSS_FEEDS:
            try:
                if feed.get("is_json"):
                    opps = self._parse_json_feed(feed)
                else:
                    opps = self._parse_rss(feed)
                all_opps.extend(opps)
                self.log.info("  %s → %d items", feed["name"], len(opps))
            except Exception as exc:
                self.log.warning("Feed '%s' failed: %s", feed["name"], exc)
        return all_opps

    # ── RSS / Atom ─────────────────────────────────────────────────────────────

    def _parse_rss(self, feed: Dict) -> List[Opportunity]:
        content = fetch_text(feed["url"])
        if not content:
            return []

        try:
            root = ET.fromstring(content.encode())
        except ET.ParseError as exc:
            self.log.warning("XML parse error for %s: %s", feed["name"], exc)
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        opps = []

        # RSS 2.0
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()

            if not title or not link:
                continue

            opps.append(Opportunity(
                title=title,
                company=feed.get("company", ""),
                category=feed.get("category", "internship"),
                apply_link=link,
                source_url=feed["url"],
                source_name=feed["source_name"],
                description=desc[:500],
                date_posted=_parse_date(pub_date),
                location="Remote",
            ))

        # Atom feeds
        if not opps:
            for entry in root.findall(".//atom:entry", ns):
                title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                link_el = entry.find("atom:link", ns)
                link = (link_el.get("href") if link_el is not None else "") or ""
                summary = (entry.findtext("atom:summary", namespaces=ns) or "").strip()
                updated = (entry.findtext("atom:updated", namespaces=ns) or "").strip()

                if not title or not link:
                    continue

                opps.append(Opportunity(
                    title=title,
                    company=feed.get("company", ""),
                    category=feed.get("category", "internship"),
                    apply_link=link,
                    source_url=feed["url"],
                    source_name=feed["source_name"],
                    description=summary[:500],
                    date_posted=updated[:10],
                    location="Remote",
                ))

        return opps

    # ── JSON GitHub feed ───────────────────────────────────────────────────────

    def _parse_json_feed(self, feed: Dict) -> List[Opportunity]:
        """Parse SimplifyJobs-style JSON listing."""
        from scripts.core.http_client import fetch_json
        data = fetch_json(feed["url"])
        if not data or not isinstance(data, list):
            return []

        opps = []
        for item in data[:100]:  # cap to avoid massive payloads
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("role") or ""
            company = item.get("company_name") or item.get("company") or ""
            link = item.get("url") or item.get("apply_link") or ""
            location = item.get("location") or "Remote / Various"
            active = item.get("active", True)
            if not active:
                continue

            opps.append(Opportunity(
                title=title,
                company=company,
                category=feed.get("category", "internship"),
                apply_link=link,
                source_url=feed["url"],
                source_name=feed["source_name"],
                location=location,
            ))
        return opps


def _parse_date(raw: str) -> str:
    """Try to extract an ISO date from an RSS pubDate string."""
    import re as _re
    # Normalise timezone offset: "+0000" → "+00:00" for %z (Python <3.7 compat)
    normalised = _re.sub(r"([+-])(\d{2})(\d{2})$", r"\1\2:\3", raw.strip())
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        for candidate in (normalised, raw.strip()):
            try:
                return datetime.strptime(candidate[:35], fmt).date().isoformat()
            except ValueError:
                continue
    return ""
