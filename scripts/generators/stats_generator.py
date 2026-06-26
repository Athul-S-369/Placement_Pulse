"""
PlacementPulse - Statistics Generator
Produces CSV stats files and a JSON summary for the website.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from config.settings import STATS_DIR, WEBSITE_DIR

log = get_logger("generator.stats")


def _ensure_dirs() -> None:
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    WEBSITE_DIR.mkdir(parents=True, exist_ok=True)


# ─── CSV helpers ──────────────────────────────────────────────────────────────

def _write_csv(path: Path, rows: list, headers: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


# ─── Main generator ───────────────────────────────────────────────────────────

def generate_stats(all_opps: List[Opportunity], today_opps: List[Opportunity]) -> Dict:
    _ensure_dirs()
    today = date.today()

    # ── Per-day stats (append) ─────────────────────────────────────────────────
    daily_csv = STATS_DIR / "daily.csv"
    _append_daily_row(daily_csv, today, today_opps, all_opps)

    # ── Category stats ─────────────────────────────────────────────────────────
    cat_csv = STATS_DIR / "categories.csv"
    cat_counts = Counter(o.category for o in all_opps)
    cat_rows = [
        {"category": cat, "count": count, "as_of": today.isoformat()}
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])
    ]
    _write_csv(cat_csv, cat_rows, ["category", "count", "as_of"])

    # ── Company stats ─────────────────────────────────────────────────────────
    company_csv = STATS_DIR / "companies.csv"
    co_counts = Counter(o.company for o in all_opps if o.company.strip())
    co_rows = [
        {"company": co, "count": cnt, "as_of": today.isoformat()}
        for co, cnt in sorted(co_counts.items(), key=lambda x: -x[1])
    ]
    _write_csv(company_csv, co_rows, ["company", "count", "as_of"])

    # ── JSON summary for website ───────────────────────────────────────────────
    active = [o for o in all_opps if not o.is_expired()]
    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "date": today.isoformat(),
        "total": len(all_opps),
        "active": len(active),
        "new_today": len(today_opps),
        "companies": len(co_counts),
        "categories": dict(cat_counts),
        "top_companies": [{"name": co, "count": cnt} for co, cnt in co_counts.most_common(20)],
        "domain_tags": dict(Counter(
            tag for o in all_opps for tag in o.domain_tags
        )),
        "work_modes": dict(Counter(o.work_mode for o in all_opps)),
    }
    summary_path = WEBSITE_DIR / "stats.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    log.info("Generated stats: %s", summary_path)
    return summary


def _append_daily_row(
    path: Path,
    today: date,
    today_opps: List[Opportunity],
    all_opps: List[Opportunity],
) -> None:
    """Append one row to daily.csv (creates file + header if missing)."""
    headers = [
        "date", "new_opportunities", "total_opportunities",
        "active_opportunities", "internships", "hackathons",
        "fresher_jobs", "fellowships", "open_source",
    ]
    cat = Counter(o.category for o in today_opps)
    row = {
        "date": today.isoformat(),
        "new_opportunities": len(today_opps),
        "total_opportunities": len(all_opps),
        "active_opportunities": sum(1 for o in all_opps if not o.is_expired()),
        "internships": cat.get("internship", 0),
        "hackathons": cat.get("hackathon", 0),
        "fresher_jobs": cat.get("fresher-job", 0),
        "fellowships": cat.get("fellowship", 0),
        "open_source": cat.get("open-source-program", 0),
    }

    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


# ─── Search index for website ─────────────────────────────────────────────────

def generate_search_index(all_opps: List[Opportunity]) -> Path:
    """Generate website/search.json — lightweight search index."""
    index = []
    for opp in all_opps:
        index.append({
            "id": opp.id,
            "title": opp.title,
            "company": opp.company,
            "category": opp.category,
            "location": opp.location,
            "work_mode": opp.work_mode,
            "apply_link": opp.apply_link,
            "deadline": opp.deadline,
            "date_found": opp.date_found,
            "tags": opp.tags + opp.domain_tags,
            "skills": opp.skills_required,
            "is_expired": opp.is_expired(),
        })

    WEBSITE_DIR.mkdir(parents=True, exist_ok=True)
    path = WEBSITE_DIR / "search.json"
    path.write_text(
        json.dumps(index, indent=None, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    log.info("Generated search index: %d entries → %s", len(index), path)
    return path
