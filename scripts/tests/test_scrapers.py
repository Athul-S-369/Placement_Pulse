"""
Scraper tests — unit tests use mocks; smoke tests hit real URLs.
Mark smoke tests with @pytest.mark.smoke so CI can skip them.
"""

import pytest
from unittest.mock import patch

from scripts.core.models import Opportunity
from scripts.scrapers.base import BaseScraper
from scripts.scrapers.programs_scraper import ProgramsScraper
from scripts.scrapers.rss_scraper import RssScraper, _parse_date
from scripts.scrapers.unstop_scraper import UnstopScraper


# ─── Base class ───────────────────────────────────────────────────────────────

def test_base_scraper_disabled_returns_empty():
    class DisabledScraper(BaseScraper):
        name = "disabled"
        enabled = False

        def scrape(self):
            return [Opportunity(title="should not appear", company="X")]

    s = DisabledScraper()
    assert s.run() == []


def test_base_scraper_exception_returns_empty():
    class BrokenScraper(BaseScraper):
        name = "broken"

        def scrape(self):
            raise RuntimeError("network error")

    s = BrokenScraper()
    result = s.run()
    assert result == []


# ─── RSS scraper ──────────────────────────────────────────────────────────────

def test_rss_parse_date_rss_format():
    assert _parse_date("Fri, 27 Jun 2025 12:00:00 +0000") == "2025-06-27"


def test_rss_parse_date_iso():
    assert _parse_date("2025-06-27T12:00:00Z") == "2025-06-27"


def test_rss_parse_date_invalid():
    assert _parse_date("not a date") == ""


@patch("scripts.scrapers.rss_scraper.fetch_text")
def test_rss_scraper_parses_rss2(mock_fetch):
    mock_fetch.return_value = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item>
    <title>Backend Intern at Google</title>
    <link>https://example.com/job/1</link>
    <description>Join Google as a backend intern</description>
    <pubDate>Fri, 27 Jun 2025 08:00:00 +0000</pubDate>
  </item>
</channel></rss>"""
    scraper = RssScraper()
    feed = {
        "name": "test",
        "url": "https://test.com/rss",
        "company": "Google",
        "category": "internship",
        "source_name": "Test RSS",
    }
    results = scraper._parse_rss(feed)
    assert len(results) == 1
    assert results[0].title == "Backend Intern at Google"
    assert results[0].apply_link == "https://example.com/job/1"


# ─── Programs scraper ─────────────────────────────────────────────────────────

def test_programs_scraper_returns_known_programs():
    scraper = ProgramsScraper()
    with patch("scripts.scrapers.programs_scraper.fetch_json", return_value=None):
        results = scraper.scrape()
    program_names = [r.title for r in results]
    assert any("GSoC" in n or "Google Summer of Code" in n for n in program_names)
    assert any("Outreachy" in n for n in program_names)
    assert any("MLH" in n for n in program_names)


def test_programs_scraper_all_have_apply_link():
    scraper = ProgramsScraper()
    with patch("scripts.scrapers.programs_scraper.fetch_json", return_value=None):
        results = scraper.scrape()
    for opp in results:
        assert opp.apply_link, f"{opp.title} has no apply_link"


# ─── Unstop scraper ───────────────────────────────────────────────────────────

@patch("scripts.scrapers.unstop_scraper.fetch_json")
def test_unstop_scraper_parses_response(mock_fetch):
    mock_fetch.return_value = {
        "data": {
            "data": [
                {
                    "title": "Smart India Hackathon 2025",
                    "organisation": {"name": "AICTE"},
                    "public_url": "hackathons/sih-2025",
                    "end_date": "2025-09-30",
                    "city": "New Delhi",
                    "description": "National hackathon",
                }
            ]
        }
    }
    scraper = UnstopScraper()
    results = scraper._fetch({"oppType": "hackathon"})
    assert len(results) == 1
    assert results[0].title == "Smart India Hackathon 2025"
    assert results[0].company == "AICTE"
    assert results[0].deadline == "2025-09-30"


@patch("scripts.scrapers.unstop_scraper.fetch_json")
def test_unstop_scraper_handles_empty(mock_fetch):
    mock_fetch.return_value = None
    scraper = UnstopScraper()
    assert scraper._fetch({"oppType": "hackathon"}) == []


# ─── Smoke tests (marked, require network) ────────────────────────────────────

@pytest.mark.smoke
def test_smoke_programs_scraper():
    """Actually hits MLH endpoint — needs network."""
    scraper = ProgramsScraper()
    results = scraper.run()
    assert isinstance(results, list)
    # Should always return at least the static programs
    assert len(results) >= 5
