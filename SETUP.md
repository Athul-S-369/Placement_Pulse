# ⚙️ Setup & Deployment Guide

This guide walks you through forking and deploying your own PlacementPulse instance
in under 10 minutes — completely free.

---

## Prerequisites

- A GitHub account (free)
- Python 3.10+ (for local development only)
- Git

---

## 1. Fork the Repository

1. Click **Fork** on GitHub
2. Name it `PlacementPulse` (or anything you like)
3. Ensure the repository is **public** (required for free GitHub Pages)

---

## 2. Enable GitHub Pages

1. Go to your fork's **Settings → Pages**
2. Under **Source**, select **GitHub Actions**
3. Save

---

## 3. Enable GitHub Actions

1. Go to **Actions** tab in your fork
2. Click **"I understand my workflows, go ahead and enable them"**

That's it! The workflow will run automatically every morning and evening.

---

## 4. Customize (Optional)

Edit `config/settings.py` to change:

```python
SITE_TITLE = "PlacementPulse"           # Your site name
SITE_URL = "https://your-username.github.io/PlacementPulse"
GITHUB_REPO_URL = "https://github.com/your-username/PlacementPulse"
```

---

## 5. Run Manually

Trigger a run anytime from **Actions → Daily Opportunity Update → Run workflow**.

---

## 6. Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/PlacementPulse.git
cd PlacementPulse

# Create virtual environment
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (dry run — no git commit)
python scripts/main.py --dry-run

# Run only scrapers
python scripts/main.py --scrape-only

# Regenerate all content from stored data (no scraping)
python scripts/main.py --generate-only

# Run tests
pip install -r requirements-dev.txt
pytest scripts/tests/ -v
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Ensure you're in the repo root and ran `pip install -r requirements.txt` |
| Scrapers returning 0 results | Some sites may be down or have changed their HTML. Check logs in `logs/`. |
| GitHub Actions failing | Check the **Actions** tab. Most failures are transient network issues — re-run the workflow. |
| Pages not updating | Ensure Pages source is set to **GitHub Actions** (not a branch). |

---

## Architecture Overview

```
PlacementPulse/
├── config/            # Global settings
├── scripts/
│   ├── core/          # Data models, HTTP client, storage, dedup, normalizer
│   ├── scrapers/      # One file per data source
│   ├── generators/    # Markdown, README, stats, website generators
│   ├── tests/         # Unit tests
│   ├── pipeline.py    # Orchestrator
│   └── main.py        # CLI entry point
├── data/
│   ├── raw/           # Raw scraper output (gitignored)
│   └── processed/     # Normalized, deduplicated JSON
├── daily/             # Daily digest Markdown files
├── companies/         # Per-company README files
├── categories/        # Per-category README files
├── stats/             # CSV statistics
├── website/           # Static website (deployed to GitHub Pages)
└── .github/workflows/ # GitHub Actions
```
