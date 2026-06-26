"""
PlacementPulse - GitHub Repository Opportunity Scraper
Pulls opportunity lists from curated public GitHub repositories that
maintain internship/job boards as JSON or Markdown.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import fetch_json, fetch_text

# ─── Curated public GitHub sources ────────────────────────────────────────────
GITHUB_SOURCES: List[Dict] = [
    {
        "name": "pittcsc-summer2026",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json",
        "source_name": "SimplifyJobs / PittCSC",
        "category": "internship",
        "parser": "simplify_json",
    },
    {
        "name": "pittcsc-new-grad",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json",
        "source_name": "SimplifyJobs New Grad",
        "category": "fresher-job",
        "parser": "simplify_json",
    },
    {
        "name": "india-internships-md",
        "url": "https://raw.githubusercontent.com/Aveek-Saha/InternList/master/README.md",
        "source_name": "InternList GitHub",
        "category": "internship",
        "parser": "markdown_table",
    },
    {
        "name": "gsoc-orgs",
        "url": "https://raw.githubusercontent.com/nicedoc/gsoc-orgs/main/orgs.json",
        "source_name": "GSoC Organisations",
        "category": "open-source-program",
        "parser": "gsoc_json",
    },
]


class GitHubOpportunitiesScraper(BaseScraper):
    """Pulls structured opportunity data from curated public GitHub repos."""

    name = "github-opportunities"

    def scrape(self) -> List[Opportunity]:
        all_opps: List[Opportunity] = []
        for source in GITHUB_SOURCES:
            try:
                opps = self._handle(source)
                all_opps.extend(opps)
                self.log.info("  %s → %d items", source["name"], len(opps))
            except Exception as exc:
                self.log.warning("GitHub source '%s' error: %s", source["name"], exc)
        return all_opps

    def _handle(self, source: Dict) -> List[Opportunity]:
        parser = source.get("parser", "simplify_json")
        if parser == "simplify_json":
            return self._simplify_json(source)
        if parser == "markdown_table":
            return self._markdown_table(source)
        if parser == "gsoc_json":
            return self._gsoc_json(source)
        return []

    # ── SimplifyJobs JSON ─────────────────────────────────────────────────────

    def _simplify_json(self, source: Dict) -> List[Opportunity]:
        data = fetch_json(source["url"])
        if not data or not isinstance(data, list):
            return []
        opps = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if not item.get("active", True):
                continue
            title = item.get("title") or item.get("role") or ""
            company = item.get("company_name") or ""
            locations = item.get("locations") or [item.get("location") or ""]
            location = ", ".join(locations) if isinstance(locations, list) else str(locations)
            link = item.get("url") or ""
            salary = item.get("compensation") or ""
            opps.append(Opportunity(
                title=title,
                company=company,
                category=source["category"],
                apply_link=link,
                source_url=source["url"],
                source_name=source["source_name"],
                location=location,
                salary=salary,
            ))
        return opps

    # ── Markdown table parser ──────────────────────────────────────────────────

    def _markdown_table(self, source: Dict) -> List[Opportunity]:
        content = fetch_text(source["url"])
        if not content:
            return []
        opps = []
        # Typical format: | Company | Role | Location | Link |
        table_row = re.compile(
            r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
            r"\s*\[.*?\]\((https?://[^)]+)\)"
        )
        for m in table_row.finditer(content):
            company, title, location, link = m.group(1), m.group(2), m.group(3), m.group(4)
            if company.lower() in ("company", "organisation", "org", "---"):
                continue
            opps.append(Opportunity(
                title=title.strip(),
                company=company.strip(),
                category=source["category"],
                apply_link=link,
                source_url=source["url"],
                source_name=source["source_name"],
                location=location.strip(),
            ))
        return opps

    # ── GSoC JSON ─────────────────────────────────────────────────────────────

    def _gsoc_json(self, source: Dict) -> List[Opportunity]:
        data = fetch_json(source["url"])
        if not data:
            return []
        if isinstance(data, dict):
            items = list(data.values())
        else:
            items = data
        opps = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or ""
            url = item.get("url") or item.get("website") or ""
            desc = item.get("description") or ""
            opps.append(Opportunity(
                title=f"GSoC – {name}",
                company=name,
                category="open-source-program",
                apply_link=url,
                source_url=source["url"],
                source_name=source["source_name"],
                description=desc[:500],
                location="Remote",
                work_mode="remote",
            ))
        return opps
