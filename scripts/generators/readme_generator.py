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
from config.settings import ROOT_DIR, GITHUB_REPO_URL

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

    # ── Today's category summary ───────────────────────────────────────────────
    today_lines = []
    for cat, count in sorted(today_cats.items(), key=lambda x: -x[1])[:6]:
        label = CAT_LABEL.get(cat, cat.replace("-", " ").title())
        today_lines.append(f"**{count}** {label}")
    today_snapshot = " &nbsp;·&nbsp; ".join(today_lines) or "No new opportunities in this run"

    # ── Newly found opportunities in this run (up to 25) ──────────────────────
    new_opps = sorted(today_opps, key=lambda o: o.date_found or "", reverse=True)[:25]
    new_rows = []
    for o in new_opps:
        cat_label = CAT_LABEL.get(o.category, o.category.replace("-", " ").title())
        mode = o.work_mode.title() if o.work_mode else "—"
        title = o.title[:55] + ("..." if len(o.title) > 55 else "")
        company = o.company[:25] if o.company else "—"
        deadline = o.deadline or "—"
        new_rows.append(
            f"| [{title}]({o.apply_link}) | {company} | {cat_label} | {mode} | {deadline} |"
        )
    new_opps_table = "\n".join(new_rows) if new_rows else "| No new opportunities in this run | — | — | — | — |"

    # ── Recent 15 opportunities across all time ────────────────────────────────
    recent = sorted(all_opps, key=lambda o: o.date_found or "", reverse=True)[:15]
    recent_rows = []
    for o in recent:
        cat_label = CAT_LABEL.get(o.category, o.category.replace("-", " ").title())
        mode = o.work_mode.title() if o.work_mode else "—"
        title = o.title[:55] + ("..." if len(o.title) > 55 else "")
        company = o.company[:25] if o.company else "—"
        recent_rows.append(
            f"| [{title}]({o.apply_link}) | {company} | {cat_label} | {mode} |"
        )
    recent_table = "\n".join(recent_rows)

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
        label = f"{d.strftime('%B %d, %Y')} (Today)" if i == 0 else d.strftime("%B %d, %Y")
        archive.append(f"- [{label}]({path})")
    archive_md = "\n".join(archive)

    readme_content = f"""\
<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY -->

<div align="center">

# PlacementPulse

**India's open-source aggregator for software internships, fresher jobs,<br>hackathons, fellowships and placement opportunities.**

[![Opportunities](https://img.shields.io/badge/Opportunities-{len(all_opps)}-1a1d27?style=flat-square&labelColor=0d1117&color=c9a84c)](#latest-opportunities)
[![Active](https://img.shields.io/badge/Active-{len(active)}-1a1d27?style=flat-square&labelColor=0d1117&color=10b981)](#latest-opportunities)
[![Companies](https://img.shields.io/badge/Companies-{len(company_counts)}-1a1d27?style=flat-square&labelColor=0d1117&color=3b82f6)](#companies)
[![India](https://img.shields.io/badge/India-Only-1a1d27?style=flat-square&labelColor=FF9933&color=138808)](#)
[![Updated](https://img.shields.io/badge/Updated-{today.strftime("%b %d %Y").replace(" ", "%20")}-1a1d27?style=flat-square&labelColor=0d1117&color=64748b)](#)

[Opportunities](#latest-opportunities) &nbsp;·&nbsp;
[New This Run](#new-in-this-run) &nbsp;·&nbsp;
[Categories](#categories) &nbsp;·&nbsp;
[Companies](#companies) &nbsp;·&nbsp;
[Archive](#daily-archive) &nbsp;·&nbsp;
[Website]({GITHUB_REPO_URL.replace("github.com", "athul-s-369.github.io").replace("/Placement_Pulse", "/Placement_Pulse")})

</div>

---

## Run Summary &nbsp;—&nbsp; {today.strftime("%B %d, %Y")}

{today_snapshot}

> Automatically scraped every 8 hours via [GitHub Actions](.github/workflows/daily_update.yml) — 6:00 AM, 2:00 PM and 10:00 PM IST.

---

## New in This Run

The following opportunities were discovered or updated in the most recent automated run.

| Role | Company | Category | Mode | Deadline |
|------|---------|----------|------|----------|
{new_opps_table}

---

## Latest Opportunities

The 15 most recently added opportunities across all categories.

| Role | Company | Category | Mode |
|------|---------|----------|------|
{recent_table}

[Browse all {len(all_opps)} opportunities on the website]({GITHUB_REPO_URL.replace("github.com", "athul-s-369.github.io").replace("/Placement_Pulse", "/Placement_Pulse")})

---

## Categories

| Category | Count |
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

## Daily Archive

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

<sub>Open-source &nbsp;·&nbsp; No API keys &nbsp;·&nbsp; 100% free &nbsp;·&nbsp; Built for Indian students</sub>

<sub>Last generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</sub>

</div>
"""

    README_PATH.write_text(readme_content, encoding="utf-8")
    log.info("Generated README.md (%d bytes)", len(readme_content))
    return README_PATH
