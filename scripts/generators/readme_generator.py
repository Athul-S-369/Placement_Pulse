"""
PlacementPulse - README Generator
Generates a professional, elegant README with the latest opportunities snapshot.
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from config.settings import ROOT_DIR

log = get_logger("generator.readme")

README_PATH = ROOT_DIR / "README.md"

CAT_LABEL = {
    "internship": "Internship",
    "fresher-job": "Fresher Job",
    "off-campus-drive": "Off-Campus Drive",
    "hiring-challenge": "Hiring Challenge",
    "hackathon": "Hackathon",
    "fellowship": "Fellowship",
    "open-source-program": "Open Source Program",
    "student-ambassador": "Student Ambassador",
    "scholarship": "Scholarship",
}


def generate_readme(
    all_opps: List[Opportunity],
    today_opps: List[Opportunity],
    stats: dict,
) -> Path:
    today = date.today()
    active = [o for o in all_opps if not o.is_expired()]
    company_counts = Counter(o.company for o in all_opps)
    cat_counts = Counter(o.category for o in all_opps)
    today_cats = Counter(o.category for o in today_opps)

    # ── Category summary for the current run ──────────────────────────────────
    today_lines = []
    for cat, count in sorted(today_cats.items(), key=lambda x: -x[1])[:8]:
        label = CAT_LABEL.get(cat, cat.replace("-", " ").title())
        today_lines.append(f"**{count}** {label}")
    today_snapshot = " &nbsp;·&nbsp; ".join(today_lines) if today_lines else "_No new opportunities found in this run._"

    # ── All opportunities from the current run ────────────────────────────────
    new_opps = sorted(today_opps, key=lambda o: (o.category, o.company, o.title))
    new_rows = []
    for o in new_opps:
        cat_label = CAT_LABEL.get(o.category, o.category.replace("-", " ").title())
        mode = o.work_mode.title() if o.work_mode else "—"
        title = o.title[:60] + ("..." if len(o.title) > 60 else "")
        company = o.company[:28] if o.company else "—"
        location = o.location[:25] if o.location else "—"
        deadline = o.deadline or "—"
        new_rows.append(
            f"| [{title}]({o.apply_link}) | {company} | {location} | {cat_label} | {mode} | {deadline} |"
        )
    if new_rows:
        new_opps_section = (
            f"**{len(new_opps)} opportunities** added or updated in the latest run"
            f" ({today.strftime('%B %d, %Y')}).\n\n"
            "| Role | Company | Location | Category | Mode | Deadline |\n"
            "|------|---------|----------|----------|------|----------|\n"
            + "\n".join(new_rows)
        )
    else:
        new_opps_section = "_No new opportunities were found in this run. Check back at the next scheduled run._"

    # ── All active opportunities (most recent first, up to 50) ────────────────
    recent = sorted(active, key=lambda o: o.date_found or "", reverse=True)[:50]
    recent_rows = []
    for o in recent:
        cat_label = CAT_LABEL.get(o.category, o.category.replace("-", " ").title())
        mode = o.work_mode.title() if o.work_mode else "—"
        title = o.title[:60] + ("..." if len(o.title) > 60 else "")
        company = o.company[:28] if o.company else "—"
        location = o.location[:25] if o.location else "—"
        deadline = o.deadline or "Open"
        recent_rows.append(
            f"| [{title}]({o.apply_link}) | {company} | {location} | {cat_label} | {mode} | {deadline} |"
        )
    recent_table = "\n".join(recent_rows) if recent_rows else "_No active opportunities at the moment._"

    # ── Category breakdown ─────────────────────────────────────────────────────
    cat_rows = []
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        label = CAT_LABEL.get(c, c.replace("-", " ").title())
        cat_rows.append(f"| [{label}](categories/{c}/) | {n} |")
    cat_table = "\n".join(cat_rows)

    # ── Archive (last 7 days) ──────────────────────────────────────────────────
    archive = []
    for i in range(7):
        d = today - timedelta(days=i)
        path = f"daily/{d.year}/{d.strftime('%B')}/{d.isoformat()}.md"
        label = f"{d.strftime('%B %d, %Y')} — Today" if i == 0 else d.strftime("%B %d, %Y")
        archive.append(f"- [{label}]({path})")
    archive_md = "\n".join(archive)

    website_url = "https://athul-s-369.github.io/Placement_Pulse"

    readme_content = f"""\
<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY -->

<div align="center">

# PlacementPulse

**India's open-source aggregator for software internships, fresher jobs,<br>hackathons, fellowships, and placement opportunities.**

[![Opportunities](https://img.shields.io/badge/Opportunities-{len(all_opps)}-0d1117?style=flat-square&labelColor=0d1117&color=c9a84c)](#active-opportunities)
[![Active](https://img.shields.io/badge/Active-{len(active)}-0d1117?style=flat-square&labelColor=0d1117&color=10b981)](#active-opportunities)
[![Companies](https://img.shields.io/badge/Companies-{len(company_counts)}-0d1117?style=flat-square&labelColor=0d1117&color=3b82f6)](#companies)
[![India Only](https://img.shields.io/badge/India-Only-0d1117?style=flat-square&labelColor=FF9933&color=138808)](#)
[![Updated](https://img.shields.io/badge/Updated-{today.strftime("%b %d %Y").replace(" ", "%20")}-0d1117?style=flat-square&labelColor=0d1117&color=64748b)](#)

[Latest Run](#latest-run) &nbsp;·&nbsp;
[Active Opportunities](#active-opportunities) &nbsp;·&nbsp;
[Categories](#categories) &nbsp;·&nbsp;
[Companies](#companies) &nbsp;·&nbsp;
[Archive](#archive) &nbsp;·&nbsp;
[Website]({website_url})

</div>

---

## About

PlacementPulse is a fully automated, open-source platform that discovers and aggregates
software internships, fresher jobs, hackathons, fellowships, and placement opportunities
for students across India. It runs on GitHub Actions with no paid APIs, no manual effort,
and no backend — just Python, public web data, and Markdown.

Data is refreshed **three times daily at 6:00 AM, 2:00 PM, and 10:00 PM IST**
via [GitHub Actions](.github/workflows/daily_update.yml).

---

## Latest Run

**{today.strftime("%B %d, %Y")}** &nbsp;—&nbsp; {today_snapshot}

{new_opps_section}

---

## Active Opportunities

The {min(50, len(active))} most recently added active opportunities across all categories.
[View all {len(all_opps)} on the website.]({website_url})

| Role | Company | Location | Category | Mode | Deadline |
|------|---------|----------|----------|------|----------|
{recent_table}

---

## Categories

| Category | Total |
|----------|-------|
{cat_table}

---

## Companies

[Google](companies/google/) &nbsp;·&nbsp;
[Microsoft](companies/microsoft/) &nbsp;·&nbsp;
[Amazon](companies/amazon/) &nbsp;·&nbsp;
[Apple](companies/apple/) &nbsp;·&nbsp;
[Adobe](companies/adobe/) &nbsp;·&nbsp;
[NVIDIA](companies/nvidia/) &nbsp;·&nbsp;
[Razorpay](companies/razorpay/) &nbsp;·&nbsp;
[Zoho](companies/zoho/) &nbsp;·&nbsp;
[Flipkart](companies/flipkart/) &nbsp;·&nbsp;
[Swiggy](companies/swiggy/) &nbsp;·&nbsp;
[Atlassian](companies/atlassian/)

---

## Archive

{archive_md}

[Full archive](daily/)

---

## Resources

[Resume Templates](resources/resume/) &nbsp;·&nbsp;
[Learning Roadmaps](resources/roadmaps/) &nbsp;·&nbsp;
[Contributing Guide](CONTRIBUTING.md) &nbsp;·&nbsp;
[Setup Guide](SETUP.md)

---

<div align="center">

<sub>Open-source &nbsp;·&nbsp; No paid APIs &nbsp;·&nbsp; 100% free &nbsp;·&nbsp; Built for Indian students</sub>

<sub>Last generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</sub>

</div>
"""

    README_PATH.write_text(readme_content, encoding="utf-8")
    log.info("Generated README.md (%d bytes)", len(readme_content))
    return README_PATH
