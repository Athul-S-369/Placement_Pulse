"""
PlacementPulse - Markdown Generator
Generates:
  - daily/YYYY/Month/YYYY-MM-DD.md
  - categories/<category>/README.md
  - companies/<company>/README.md
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from config.settings import (
    DAILY_DIR, COMPANIES_DIR, CATEGORIES_DIR,
    GITHUB_REPO_URL,
)

log = get_logger("generator.markdown")

_MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

CATEGORY_EMOJI = {
    "internship": "🎓",
    "fresher-job": "💼",
    "off-campus-drive": "🚀",
    "hiring-challenge": "⚡",
    "hackathon": "🏆",
    "fellowship": "🌟",
    "open-source-program": "🔓",
    "student-ambassador": "📢",
    "scholarship": "📚",
}

WORK_MODE_BADGE = {
    "remote": "🌐 Remote",
    "onsite": "🏢 Onsite",
    "hybrid": "🔀 Hybrid",
    "unknown": "❓",
}


def _opp_to_row(opp: Opportunity) -> str:
    deadline = opp.deadline or "—"
    mode = WORK_MODE_BADGE.get(opp.work_mode, "❓")
    stipend = opp.salary or opp.stipend or "—"
    return (
        f"| [{opp.title}]({opp.apply_link}) "
        f"| {opp.company} "
        f"| {opp.location} "
        f"| {mode} "
        f"| {stipend} "
        f"| {deadline} "
        f"| {opp.source_name} |"
    )


def _table_header() -> str:
    return (
        "| Role | Company | Location | Mode | Stipend/Salary | Deadline | Source |\n"
        "|------|---------|----------|------|----------------|----------|--------|"
    )


# ─── Daily digest ─────────────────────────────────────────────────────────────

def generate_daily(today_opps: List[Opportunity], all_opps: List[Opportunity]) -> Path:
    today = date.today()
    month_name = _MONTH_NAMES[today.month]
    year = today.year
    out_dir = DAILY_DIR / str(year) / month_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{today.isoformat()}.md"

    by_category: Dict[str, List[Opportunity]] = defaultdict(list)
    for opp in today_opps:
        by_category[opp.category].append(opp)

    lines = [
        f"# 📅 {today.strftime('%B %d, %Y')} — PlacementPulse Daily Digest",
        "",
        f"> Auto-generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC  ",
        f"> [{len(today_opps)} new opportunities]({GITHUB_REPO_URL}) discovered today",
        "",
        "## 📊 Today's Summary",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]
    for cat, opps in sorted(by_category.items(), key=lambda x: -len(x[1])):
        emoji = CATEGORY_EMOJI.get(cat, "•")
        lines.append(f"| {emoji} {cat.replace('-', ' ').title()} | **{len(opps)}** |")

    lines += [
        "",
        f"**Total repository:** {len(all_opps)} opportunities",
        "",
        "---",
        "",
    ]

    for cat, opps in sorted(by_category.items(), key=lambda x: -len(x[1])):
        emoji = CATEGORY_EMOJI.get(cat, "•")
        lines.append(f"## {emoji} {cat.replace('-', ' ').title()}")
        lines.append("")
        lines.append(_table_header())
        for opp in opps:
            lines.append(_opp_to_row(opp))
        lines.append("")

    lines += [
        "---",
        "",
        f"*[← Back to README]({GITHUB_REPO_URL}/blob/main/README.md)*  ",
        f"*[← Browse all daily digests]({GITHUB_REPO_URL}/tree/main/daily)*",
        "",
    ]

    out_file.write_text("\n".join(lines), encoding="utf-8")
    log.info("Generated daily digest: %s", out_file)
    return out_file


# ─── Category pages ───────────────────────────────────────────────────────────

def generate_category_pages(all_opps: List[Opportunity]) -> List[Path]:
    by_category: Dict[str, List[Opportunity]] = defaultdict(list)
    for opp in all_opps:
        by_category[opp.category].append(opp)

    generated = []
    for cat, opps in by_category.items():
        out_dir = CATEGORIES_DIR / cat.replace("-", "-")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "README.md"

        emoji = CATEGORY_EMOJI.get(cat, "•")
        active = [o for o in opps if not o.is_expired()]
        expired = [o for o in opps if o.is_expired()]

        lines = [
            f"# {emoji} {cat.replace('-', ' ').title()}",
            "",
            f"**{len(active)} active** | **{len(expired)} expired** | "
            f"**{len(opps)} total**",
            "",
            f"*Last updated: {date.today().isoformat()}*",
            "",
            "## Active Opportunities",
            "",
            _table_header(),
        ]
        for opp in sorted(active, key=lambda o: o.date_found or "", reverse=True)[:100]:
            lines.append(_opp_to_row(opp))

        if expired:
            lines += ["", "## Recently Expired", "", _table_header()]
            for opp in sorted(expired, key=lambda o: o.deadline or "", reverse=True)[:20]:
                lines.append(_opp_to_row(opp))

        lines.append("")
        out_file.write_text("\n".join(lines), encoding="utf-8")
        generated.append(out_file)

    log.info("Generated %d category pages", len(generated))
    return generated


# ─── Company pages ────────────────────────────────────────────────────────────

def generate_company_pages(all_opps: List[Opportunity]) -> List[Path]:
    by_company: Dict[str, List[Opportunity]] = defaultdict(list)
    for opp in all_opps:
        by_company[opp.company].append(opp)

    generated = []
    for company, opps in by_company.items():
        if not company.strip():
            continue
        slug = opps[0].company_slug or company.lower().replace(" ", "-")
        out_dir = COMPANIES_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "README.md"

        active = [o for o in opps if not o.is_expired()]
        categories = list({o.category for o in opps})
        locations = list({o.location for o in opps if o.location})

        lines = [
            f"# 🏢 {company}",
            "",
            f"**{len(active)} active opportunities** | "
            f"**{len(opps)} total tracked** | "
            f"*Last updated: {date.today().isoformat()}*",
            "",
            "## Overview",
            "",
            f"- **Categories:** {', '.join(c.replace('-', ' ').title() for c in categories)}",
            f"- **Locations:** {', '.join(locations[:5])}",
            "",
            "## Current Opportunities",
            "",
            _table_header(),
        ]
        for opp in sorted(active, key=lambda o: o.date_found or "", reverse=True):
            lines.append(_opp_to_row(opp))

        # Apply prep section
        lines += [
            "",
            "## 📖 Interview Preparation",
            "",
            "| Resource | Link |",
            "|----------|------|",
            f"| GeeksForGeeks – {company} | "
            f"[Search](https://www.geeksforgeeks.org/search/?q={company.replace(' ', '+')}) |",
            f"| LeetCode – {company} | "
            f"[Problems](https://leetcode.com/company/{slug}/) |",
            f"| Glassdoor – {company} | "
            f"[Reviews](https://www.glassdoor.com/Reviews/{company.replace(' ', '-')}-Reviews-E.htm) |",
            "",
        ]

        out_file.write_text("\n".join(lines), encoding="utf-8")
        generated.append(out_file)

    log.info("Generated %d company pages", len(generated))
    return generated
