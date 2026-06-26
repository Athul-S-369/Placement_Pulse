"""
PlacementPulse - Student Programs & Fellowships Scraper
Scrapes open-source programs, fellowships, and ambassador programs
from their official public pages (all allow indexing).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.http_client import fetch_json
from scripts.core.models import Opportunity
from scripts.scrapers.base import BaseScraper


PROGRAMS: List[Dict] = [
    # ── GSoC ───────────────────────────────────────────────────────────────────
    {
        "name": "Google Summer of Code",
        "category": "open-source-program",
        "apply_link": "https://summerofcode.withgoogle.com/",
        "deadline": "2026-04-08",
        "description": (
            "Google Summer of Code is a global program focused on bringing "
            "more student developers into open-source software development. "
            "Stipend provided. Open to 18+ worldwide."
        ),
        "skills": ["open-source", "programming"],
        "location": "Remote",
        "work_mode": "remote",
        "company": "Google",
        "batch_eligible": ["2024", "2025", "2026"],
        "salary": "Stipend: $1500-$3300 USD",
        "tags": ["gsoc", "google", "open-source"],
    },
    # ── Outreachy ──────────────────────────────────────────────────────────────
    {
        "name": "Outreachy Internship",
        "category": "fellowship",
        "apply_link": "https://www.outreachy.org/apply/",
        "deadline": "",
        "description": (
            "Outreachy provides internships in open source and open science. "
            "Outreachy provides a stipend of $7,000 USD for the three-month internship. "
            "Interns are required to work 30 hours per week."
        ),
        "skills": ["open-source"],
        "location": "Remote",
        "work_mode": "remote",
        "company": "Outreachy",
        "salary": "Stipend: $7000 USD",
        "tags": ["outreachy", "diversity", "open-source"],
    },
    # ── MLH Fellowship ────────────────────────────────────────────────────────
    {
        "name": "MLH Fellowship",
        "category": "fellowship",
        "apply_link": "https://fellowship.mlh.io/",
        "deadline": "",
        "description": (
            "The MLH Fellowship is a remote internship alternative for software engineers. "
            "Participants work on open source projects alongside a mentor "
            "from top tech companies. Stipend available."
        ),
        "skills": ["software-engineering", "open-source"],
        "location": "Remote",
        "work_mode": "remote",
        "company": "MLH",
        "tags": ["mlh", "fellowship", "remote"],
    },
    # ── GitHub Campus Expert ──────────────────────────────────────────────────
    {
        "name": "GitHub Campus Expert Program",
        "category": "student-ambassador",
        "apply_link": "https://education.github.com/experts",
        "deadline": "",
        "description": (
            "GitHub Campus Experts are student leaders who build technical "
            "communities on campus. Learn industry skills and gain access "
            "to exclusive GitHub resources."
        ),
        "skills": ["community-building", "git", "github"],
        "location": "India (Campus)",
        "work_mode": "onsite",
        "company": "GitHub",
        "tags": ["github", "ambassador", "student"],
        "is_india": True,
    },
    # ── Microsoft Student Partners ────────────────────────────────────────────
    {
        "name": "Microsoft Learn Student Ambassadors",
        "category": "student-ambassador",
        "apply_link": "https://studentambassadors.microsoft.com/",
        "deadline": "",
        "description": (
            "The Microsoft Learn Student Ambassadors program is a global program "
            "for students who are passionate about technology and want to build "
            "community on their campus. Benefits include Azure credits, certifications, "
            "and mentorship."
        ),
        "skills": ["azure", "microsoft", "cloud"],
        "location": "India (Campus)",
        "work_mode": "onsite",
        "company": "Microsoft",
        "tags": ["microsoft", "ambassador", "azure"],
        "is_india": True,
    },
    # ── Linux Foundation Mentorship ────────────────────────────────────────────
    {
        "name": "Linux Foundation Mentorship Program",
        "category": "open-source-program",
        "apply_link": "https://mentorship.lfx.linuxfoundation.org/",
        "deadline": "",
        "description": (
            "The Linux Foundation Mentorship Program is designed to help "
            "developers with the necessary skills and experience to engage with "
            "open source communities and create technology solutions."
        ),
        "skills": ["open-source", "linux", "cloud-native"],
        "location": "Remote",
        "work_mode": "remote",
        "company": "Linux Foundation",
        "salary": "Stipend available",
        "tags": ["linux", "cncf", "open-source"],
    },
    # ── Season of Docs ─────────────────────────────────────────────────────────
    {
        "name": "Google Season of Docs",
        "category": "open-source-program",
        "apply_link": "https://developers.google.com/season-of-docs",
        "deadline": "",
        "description": (
            "Season of Docs provides support for open source projects to improve "
            "their documentation and gives professional technical writers an "
            "opportunity to gain experience in open source."
        ),
        "skills": ["technical-writing", "documentation"],
        "location": "Remote",
        "work_mode": "remote",
        "company": "Google",
        "tags": ["google", "open-source", "documentation"],
    },
]


class ProgramsScraper(BaseScraper):
    """
    Emits well-known student programs as static opportunities.
    Also fetches live data where available (Outreachy RSS, MLH page).
    """

    name = "programs"

    def scrape(self) -> List[Opportunity]:
        opps: List[Opportunity] = []
        for prog in PROGRAMS:
            opps.append(Opportunity(
                title=prog["name"],
                company=prog["company"],
                category=prog["category"],
                apply_link=prog["apply_link"],
                source_url=prog["apply_link"],
                source_name="Official Website",
                deadline=prog.get("deadline", ""),
                description=prog.get("description", ""),
                skills_required=prog.get("skills", []),
                location=prog.get("location", "Remote"),
                work_mode=prog.get("work_mode", "remote"),
                salary=prog.get("salary", ""),
                tags=prog.get("tags", []),
                is_india=prog.get("is_india", False),
                batch_eligible=prog.get("batch_eligible", []),
            ))

        # Try to fetch live MLH events
        opps.extend(self._fetch_mlh_events())
        return opps

    def _fetch_mlh_events(self) -> List[Opportunity]:
        """Fetch upcoming MLH hackathons from their public JSON endpoint."""
        url = "https://mlh.io/seasons/2026/events.json"
        data = fetch_json(url)
        if not data or not isinstance(data, list):
            return []
        opps = []
        for event in data:
            if not isinstance(event, dict):
                continue
            name = event.get("name") or ""
            link = event.get("url") or "https://mlh.io"
            start = event.get("start_date") or ""
            end = event.get("end_date") or ""
            location = event.get("location") or "Remote"
            if not name:
                continue
            opps.append(Opportunity(
                title=name,
                company="MLH",
                category="hackathon",
                apply_link=link,
                source_url="https://mlh.io",
                source_name="MLH",
                location=location,
                date_posted=start[:10] if start else "",
                deadline=end[:10] if end else "",
                work_mode="remote" if "online" in location.lower() else "onsite",
                tags=["mlh", "hackathon"],
            ))
        return opps
