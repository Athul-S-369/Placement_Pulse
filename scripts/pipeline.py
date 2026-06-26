"""
PlacementPulse - Main Pipeline Orchestrator
Runs all scrapers → normalize → deduplicate → merge → persist.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.core.deduplicator import deduplicate
from scripts.core.models import Opportunity
from scripts.core.normalizer import normalize_all
from scripts.core.storage import load_all, merge, save_all, save_today
from scripts.core.logger import get_logger
from config.settings import INDIA_ONLY

# ─── Scraper registry ─────────────────────────────────────────────────────────
from scripts.scrapers.rss_scraper import RssScraper
from scripts.scrapers.github_opportunities import GitHubOpportunitiesScraper
from scripts.scrapers.company_careers import CompanyCareerscraper
from scripts.scrapers.unstop_scraper import UnstopScraper
from scripts.scrapers.hackerearth_scraper import HackerEarthScraper
from scripts.scrapers.devfolio_scraper import DevfolioScraper
from scripts.scrapers.wellfound_scraper import WellfoundScraper
from scripts.scrapers.programs_scraper import ProgramsScraper

SCRAPERS = [
    RssScraper,
    GitHubOpportunitiesScraper,
    CompanyCareerscraper,
    UnstopScraper,
    HackerEarthScraper,
    DevfolioScraper,
    WellfoundScraper,
    ProgramsScraper,
]

log = get_logger("pipeline")


def run_scrapers() -> List[Opportunity]:
    """Execute all enabled scrapers and return merged raw results."""
    all_raw: List[Opportunity] = []
    for ScraperClass in SCRAPERS:
        scraper = ScraperClass()
        results = scraper.run()
        all_raw.extend(results)
        log.info("Scraper %s → %d results", ScraperClass.name, len(results))
    log.info("Total raw opportunities collected: %d", len(all_raw))
    return all_raw


def run_pipeline() -> Tuple[List[Opportunity], dict]:
    """
    Full pipeline:
      1. Scrape
      2. Normalize
      3. Deduplicate
      4. Merge with existing
      5. Persist

    Returns (final_list, stats_dict).
    """
    log.info("=" * 60)
    log.info("PlacementPulse Pipeline — %s", date.today().isoformat())
    log.info("=" * 60)

    # Step 1: Scrape
    raw = run_scrapers()

    # Step 2: Normalize
    normalized = normalize_all(raw)
    log.info("Normalized: %d opportunities", len(normalized))

    # Step 2b: India-only filter
    if INDIA_ONLY:
        before = len(normalized)
        normalized = [o for o in normalized if o.is_india]
        dropped = before - len(normalized)
        log.info("India filter: kept %d, dropped %d non-India opportunities", len(normalized), dropped)

    # Step 3: Deduplicate new batch
    deduped, removed_new = deduplicate(normalized)
    log.info("After dedup (new): %d kept, %d removed", len(deduped), removed_new)

    # Step 4: Load existing + merge
    existing = load_all()
    merged = merge(existing, deduped)

    # Deduplicate the full merged set
    final, removed_total = deduplicate(merged)
    log.info("Final deduplicated set: %d opportunities", len(final))

    # Step 5: Persist
    save_all(final)
    save_today(deduped)  # today's snapshot

    stats = {
        "date": date.today().isoformat(),
        "total": len(final),
        "new_today": len(deduped),
        "duplicates_removed": removed_total,
        "scrapers_run": len(SCRAPERS),
        "raw_collected": len(raw),
    }
    log.info("Pipeline complete: %s", stats)
    return final, stats


if __name__ == "__main__":
    opps, stats = run_pipeline()
    print(f"\n✓ Pipeline complete — {stats['total']} total opportunities ({stats['new_today']} new today)")
