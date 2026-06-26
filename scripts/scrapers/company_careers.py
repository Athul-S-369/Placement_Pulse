"""
PlacementPulse - Company Careers Page Scraper
Scrapes official careers pages of top tech companies that allow indexing.
Each company definition is a dict — adding a new company needs zero code changes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import date

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import fetch_json, fetch_text, get

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# ─── Company definitions ──────────────────────────────────────────────────────
# Each entry specifies how to reach and parse the public careers API / page.
# `parser` key determines which parsing strategy to use.

COMPANIES: List[Dict] = [
    # ── Companies with JSON APIs ───────────────────────────────────────────────
    {
        "company": "Microsoft",
        "slug": "microsoft",
        "url": "https://jobs.careers.microsoft.com/global/en/search?q=intern&lc=India&exp=Students+and+graduates&rt=Individual+Contributor&format=json&start=0&rows=20",
        "parser": "microsoft_json",
        "category": "internship",
        "location": "India",
    },
    {
        "company": "Atlassian",
        "slug": "atlassian",
        "url": "https://www.atlassian.com/company/careers/all-jobs?team=&location=India&search=intern",
        "parser": "atlassian_html",
        "category": "internship",
        "location": "India",
    },
    {
        "company": "Razorpay",
        "slug": "razorpay",
        "url": "https://razorpay.com/jobs/",
        "parser": "razorpay_html",
        "category": "internship",
        "location": "Bengaluru, India",
    },
    {
        "company": "Zoho",
        "slug": "zoho",
        "url": "https://careers.zohocorp.com/jobs/Careers",
        "parser": "zoho_html",
        "category": "fresher-job",
        "location": "India",
    },
    {
        "company": "Adobe",
        "slug": "adobe",
        "url": "https://careers.adobe.com/us/en/search-results?keywords=intern&country=India",
        "parser": "adobe_html",
        "category": "internship",
        "location": "India",
    },
    {
        "company": "NVIDIA",
        "slug": "nvidia",
        "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?locationCountry=in&workerSubType=0c40f6bd1d8f10adf6dae042e1117353&workerSubType=ab40a98049581037a3ada55b087049b7",
        "parser": "workday_html",
        "category": "internship",
        "location": "India",
    },
    {
        "company": "Swiggy",
        "slug": "swiggy",
        "url": "https://careers.swiggy.com/#careers",
        "parser": "lever_html",
        "category": "fresher-job",
        "location": "Bengaluru, India",
    },
    {
        "company": "Flipkart",
        "slug": "flipkart",
        "url": "https://www.flipkartcareers.com/#!/joblist",
        "parser": "flipkart_html",
        "category": "fresher-job",
        "location": "Bengaluru, India",
    },
]


class CompanyCareerscraper(BaseScraper):
    """Scrapes official company careers pages."""

    name = "company-careers"

    def scrape(self) -> List[Opportunity]:
        all_opps: List[Opportunity] = []
        for company in COMPANIES:
            try:
                opps = self._scrape_company(company)
                all_opps.extend(opps)
                self.log.info("  %s → %d jobs", company["company"], len(opps))
            except Exception as exc:
                self.log.warning("Company '%s' error: %s", company["company"], exc)
        return all_opps

    def _scrape_company(self, company: Dict) -> List[Opportunity]:
        parser = company.get("parser", "generic_html")
        dispatch = {
            "microsoft_json": self._microsoft,
            "atlassian_html": self._atlassian,
            "razorpay_html": self._razorpay,
            "zoho_html": self._zoho,
            "adobe_html": self._adobe,
            "workday_html": self._workday,
            "lever_html": self._lever,
            "flipkart_html": self._flipkart,
            "generic_html": self._generic_html,
        }
        fn = dispatch.get(parser, self._generic_html)
        return fn(company)

    # ── Microsoft ─────────────────────────────────────────────────────────────

    def _microsoft(self, c: Dict) -> List[Opportunity]:
        data = fetch_json(c["url"])
        if not data:
            return []
        jobs = data.get("operationResult", {}).get("result", {}).get("jobs", [])
        opps = []
        for job in jobs:
            opps.append(Opportunity(
                title=job.get("title", ""),
                company="Microsoft",
                category=c["category"],
                apply_link=f"https://jobs.careers.microsoft.com/global/en/job/{job.get('jobId', '')}",
                source_url=c["url"],
                source_name="Microsoft Careers",
                location=job.get("location", c["location"]),
                description=job.get("properties", {}).get("description", "")[:400],
            ))
        return opps

    # ── Atlassian ─────────────────────────────────────────────────────────────

    def _atlassian(self, c: Dict) -> List[Opportunity]:
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        for card in soup.select("[class*='JobCard'], [class*='job-card'], article"):
            title_el = card.select_one("h2, h3, [class*='title']")
            link_el = card.select_one("a[href]")
            loc_el = card.select_one("[class*='location']")
            if not title_el or not link_el:
                continue
            href = link_el["href"]
            if not href.startswith("http"):
                href = "https://www.atlassian.com" + href
            opps.append(Opportunity(
                title=title_el.get_text(strip=True),
                company="Atlassian",
                category=c["category"],
                apply_link=href,
                source_url=c["url"],
                source_name="Atlassian Careers",
                location=loc_el.get_text(strip=True) if loc_el else c["location"],
            ))
        return opps

    # ── Razorpay ──────────────────────────────────────────────────────────────

    def _razorpay(self, c: Dict) -> List[Opportunity]:
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        for card in soup.select(".job-listing, .position, [class*='job']"):
            title_el = card.select_one("h2, h3, .title, [class*='title']")
            link_el = card.select_one("a[href]")
            if not title_el or not link_el:
                continue
            href = link_el["href"]
            if not href.startswith("http"):
                href = "https://razorpay.com" + href
            opps.append(Opportunity(
                title=title_el.get_text(strip=True),
                company="Razorpay",
                category=c["category"],
                apply_link=href,
                source_url=c["url"],
                source_name="Razorpay Careers",
                location=c["location"],
            ))
        return opps

    # ── Zoho ──────────────────────────────────────────────────────────────────

    def _zoho(self, c: Dict) -> List[Opportunity]:
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        for row in soup.select("tr, .job-row, [class*='career']"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            title = cells[0].get_text(strip=True)
            location = cells[1].get_text(strip=True) if len(cells) > 1 else c["location"]
            link_el = row.find("a", href=True)
            if not title or not link_el:
                continue
            href = link_el["href"]
            if not href.startswith("http"):
                href = "https://careers.zohocorp.com" + href
            opps.append(Opportunity(
                title=title,
                company="Zoho",
                category=c["category"],
                apply_link=href,
                source_url=c["url"],
                source_name="Zoho Careers",
                location=location,
            ))
        return opps

    # ── Adobe ─────────────────────────────────────────────────────────────────

    def _adobe(self, c: Dict) -> List[Opportunity]:
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        for card in soup.select(".job-listing-item, [class*='job-list'], [data-ph-id]"):
            title_el = card.select_one("h3, h4, .job-title, [class*='title']")
            link_el = card.select_one("a[href]")
            loc_el = card.select_one("[class*='location']")
            if not title_el or not link_el:
                continue
            href = link_el["href"]
            if not href.startswith("http"):
                href = "https://careers.adobe.com" + href
            opps.append(Opportunity(
                title=title_el.get_text(strip=True),
                company="Adobe",
                category=c["category"],
                apply_link=href,
                source_url=c["url"],
                source_name="Adobe Careers",
                location=loc_el.get_text(strip=True) if loc_el else c["location"],
            ))
        return opps

    # ── Workday (NVIDIA etc.) ──────────────────────────────────────────────────

    def _workday(self, c: Dict) -> List[Opportunity]:
        """Generic Workday scraper - extracts jobs from Workday-based career pages."""
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        for card in soup.select("[data-automation-id='jobTitle'], .css-1q2dra3, li[class*='css']"):
            title = card.get_text(strip=True)
            link_el = card.find_parent("a") or card.find("a")
            href = link_el["href"] if link_el else c["url"]
            if href and not href.startswith("http"):
                base = re.match(r"https?://[^/]+", c["url"])
                href = (base.group() if base else "") + href
            opps.append(Opportunity(
                title=title,
                company=c["company"],
                category=c["category"],
                apply_link=href,
                source_url=c["url"],
                source_name=f"{c['company']} Careers",
                location=c["location"],
            ))
        return opps

    # ── Lever (Swiggy etc.) ───────────────────────────────────────────────────

    def _lever(self, c: Dict) -> List[Opportunity]:
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        for posting in soup.select(".posting, [class*='posting']"):
            title_el = posting.select_one("h5, .posting-name, [class*='title']")
            link_el = posting.select_one("a[href]")
            if not title_el or not link_el:
                continue
            opps.append(Opportunity(
                title=title_el.get_text(strip=True),
                company=c["company"],
                category=c["category"],
                apply_link=link_el["href"],
                source_url=c["url"],
                source_name=f"{c['company']} Careers",
                location=c["location"],
            ))
        return opps

    # ── Flipkart ──────────────────────────────────────────────────────────────

    def _flipkart(self, c: Dict) -> List[Opportunity]:
        data = fetch_json("https://www.flipkartcareers.com/api/joblist?limit=50&skip=0")
        if not data:
            return []
        jobs = data.get("data") or data if isinstance(data, list) else []
        opps = []
        for job in jobs:
            if not isinstance(job, dict):
                continue
            opps.append(Opportunity(
                title=job.get("jobTitle") or job.get("title") or "",
                company="Flipkart",
                category=c["category"],
                apply_link=f"https://www.flipkartcareers.com/#!/jobdetail/{job.get('id', '')}",
                source_url=c["url"],
                source_name="Flipkart Careers",
                location=job.get("location") or c["location"],
                description=(job.get("jobDescription") or "")[:400],
            ))
        return opps

    # ── Generic fallback ──────────────────────────────────────────────────────

    def _generic_html(self, c: Dict) -> List[Opportunity]:
        """Heuristic scraper for any page with job-like content."""
        if not BS4_AVAILABLE:
            return []
        resp = get(c["url"])
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        opps = []
        job_keywords = re.compile(
            r"intern|engineer|developer|analyst|scientist|designer|manager",
            re.I,
        )
        for a_tag in soup.find_all("a", href=True):
            text = a_tag.get_text(strip=True)
            if not text or not job_keywords.search(text):
                continue
            href = a_tag["href"]
            if not href.startswith("http"):
                base = re.match(r"https?://[^/]+", c["url"])
                href = (base.group() if base else "") + href
            opps.append(Opportunity(
                title=text,
                company=c["company"],
                category=c["category"],
                apply_link=href,
                source_url=c["url"],
                source_name=f"{c['company']} Careers",
                location=c["location"],
            ))
        return opps[:30]   # cap to avoid noise
