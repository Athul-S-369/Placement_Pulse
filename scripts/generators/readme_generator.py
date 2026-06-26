"""
PlacementPulse - README Generator
Auto-updates README.md with today's stats, recent opportunities, and archive links.
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from config.settings import (
    SITE_DESCRIPTION, GITHUB_REPO_URL, SITE_URL,
    ROOT_DIR,
)

log = get_logger("generator.readme")

README_PATH = ROOT_DIR / "README.md"

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


def generate_readme(
    all_opps: List[Opportunity],
    today_opps: List[Opportunity],
    stats: dict,
) -> Path:
    today = date.today()
    cat_counts = Counter(o.category for o in all_opps)
    company_counts = Counter(o.company for o in all_opps)
    top_companies = company_counts.most_common(10)
    recent = sorted(all_opps, key=lambda o: o.date_found or "", reverse=True)[:15]
    active = [o for o in all_opps if not o.is_expired()]

    # Category breakdown for today
    today_cats = Counter(o.category for o in today_opps)

    today_summary_lines = []
    for cat, count in sorted(today_cats.items(), key=lambda x: -x[1]):
        emoji = CATEGORY_EMOJI.get(cat, "•")
        today_summary_lines.append(f"  - {emoji} **{count}** {cat.replace('-', ' ').title()}")
    today_summary = "\n".join(today_summary_lines) or "  - No new opportunities today"

    # Archive links (last 7 days)
    from datetime import timedelta
    archive_links = []
    for i in range(7):
        d = today - timedelta(days=i)
        month_name = d.strftime("%B")
        path = f"daily/{d.year}/{month_name}/{d.isoformat()}.md"
        label = "Today" if i == 0 else d.strftime("%b %d")
        archive_links.append(f"- [{label} ({d.isoformat()})]({path})")
    archive_section = "\n".join(archive_links)

    # Top 15 recent opportunities table
    recent_table_rows = []
    for opp in recent:
        deadline = opp.deadline or "—"
        mode_icon = {"remote": "🌐", "onsite": "🏢", "hybrid": "🔀"}.get(opp.work_mode, "❓")
        recent_table_rows.append(
            f"| [{opp.title[:45]}]({opp.apply_link}) "
            f"| {opp.company[:20]} "
            f"| {CATEGORY_EMOJI.get(opp.category, '•')} {opp.category.replace('-', ' ').title()} "
            f"| {mode_icon} {opp.work_mode.title()} "
            f"| {deadline} |"
        )
    recent_table = "\n".join(recent_table_rows)

    # Category overview
    cat_overview = []
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        emoji = CATEGORY_EMOJI.get(cat, "•")
        cat_link = f"categories/{cat}/README.md"
        cat_overview.append(
            f"| {emoji} [{cat.replace('-', ' ').title()}]({cat_link}) | **{count}** |"
        )
    cat_overview_md = "\n".join(cat_overview)

    # Top companies
    company_rows = "\n".join(
        f"| [{co}](companies/{co.lower().replace(' ', '-')}/README.md) | {cnt} |"
        for co, cnt in top_companies
        if co.strip()
    )

    readme_content = f"""\
<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY -->
<!-- Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC -->

<div align="center">

# 🚀 PlacementPulse

### The Largest Open-Source Collection of Indian Software Opportunities

[![Last Updated](https://img.shields.io/badge/last%20updated-{today.isoformat()}-brightgreen)](#)
[![Total Opportunities](https://img.shields.io/badge/total%20opportunities-{len(all_opps)}-blue)](#)
[![Active](https://img.shields.io/badge/active-{len(active)}-success)](#)
[![GitHub Stars](https://img.shields.io/github/stars/your-username/PlacementPulse?style=social)]({GITHUB_REPO_URL})

**{SITE_DESCRIPTION}**

[📖 Browse Opportunities](#-recent-opportunities) •
[📊 Statistics](#-statistics) •
[🏢 Companies](companies/) •
[📁 Categories](categories/) •
[🌐 Website]({SITE_URL}) •
[🤝 Contribute](CONTRIBUTING.md)

</div>

---

## 📅 Today's Updates — {today.strftime('%B %d, %Y')}

{today_summary}

> 🔄 Auto-updated twice daily via [GitHub Actions](.github/workflows/)

---

## 📋 Recent Opportunities

| Role | Company | Category | Mode | Deadline |
|------|---------|----------|------|----------|
{recent_table}

➡️ **[Browse all {len(all_opps)} opportunities →](categories/)**

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| 📦 Total Opportunities | **{len(all_opps)}** |
| ✅ Active | **{len(active)}** |
| 🏢 Companies Tracked | **{len(company_counts)}** |
| 🆕 Added Today | **{len(today_opps)}** |

### By Category

| Category | Count |
|----------|-------|
{cat_overview_md}

### Top Companies

| Company | Opportunities |
|---------|---------------|
{company_rows}

---

## 📅 Daily Archive

{archive_section}

➡️ **[Browse complete archive →](daily/)**

---

## 🏢 Companies

Browse opportunity history and interview resources for individual companies:

> [Google](companies/google/) •
> [Microsoft](companies/microsoft/) •
> [Apple](companies/apple/) •
> [Amazon](companies/amazon/) •
> [Adobe](companies/adobe/) •
> [NVIDIA](companies/nvidia/) •
> [Atlassian](companies/atlassian/) •
> [Razorpay](companies/razorpay/) •
> [Zoho](companies/zoho/) •
> [Swiggy](companies/swiggy/) •
> [Flipkart](companies/flipkart/)

---

## 📁 Categories

| Category | Description |
|----------|-------------|
| [🎓 Internships](categories/internship/) | Summer and semester-long internships |
| [💼 Fresher Jobs](categories/fresher-job/) | Entry-level positions for recent grads |
| [🚀 Off-Campus Drives](categories/off-campus-drive/) | Mass hiring events |
| [⚡ Hiring Challenges](categories/hiring-challenge/) | Competitive hiring contests |
| [🏆 Hackathons](categories/hackathon/) | Competitive hackathon events |
| [🌟 Fellowships](categories/fellowship/) | Paid fellowship programs |
| [🔓 Open Source Programs](categories/open-source-program/) | GSoC, Outreachy, LFX |
| [📢 Student Ambassadors](categories/student-ambassador/) | Campus ambassador roles |
| [📚 Scholarships](categories/scholarship/) | Tech scholarships |

---

## 📚 Resources

- [Resume Tips & Templates](resources/resume/)
- [Learning Roadmaps](resources/roadmaps/)
- [Interview Preparation](resources/interview-prep.md)

---

## 🤝 Contributing

PlacementPulse thrives on community contributions!

- **Add a scraper:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Report a broken link:** [Open an Issue]({GITHUB_REPO_URL}/issues)
- **Suggest a source:** [Start a Discussion]({GITHUB_REPO_URL}/discussions)

---

## ⚙️ How It Works

```
GitHub Actions (2x daily)
     │
     ▼
Run Scrapers ──── company careers pages
     │           ├── RSS feeds
     │           ├── public JSON APIs
     │           └── curated GitHub lists
     ▼
Normalize & Deduplicate
     ▼
Generate Markdown + Website
     ▼
Commit only if changes exist → Push
```

**100% free to run.** No API keys required. Fork and deploy in minutes.

---

<div align="center">

*Auto-generated by PlacementPulse Bot • {today.isoformat()}*
*[⭐ Star this repo]({GITHUB_REPO_URL}) to help more students discover opportunities*

</div>
"""

    README_PATH.write_text(readme_content, encoding="utf-8")
    log.info("Generated README.md (%d bytes)", len(readme_content))
    return README_PATH
