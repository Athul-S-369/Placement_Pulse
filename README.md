<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY -->

<div align="center">

# 🚀 PlacementPulse

### The Largest Open-Source Collection of Indian Software Opportunities

[![Last Updated](https://img.shields.io/badge/last%20updated-2026--06--27-brightgreen)](#)
[![Total Opportunities](https://img.shields.io/badge/total%20opportunities-0-blue)](#)
[![GitHub Stars](https://img.shields.io/github/stars/your-username/PlacementPulse?style=social)](#)

**The largest open-source collection of Indian software internship and placement opportunities, updated daily.**

[📖 Browse Opportunities](#-recent-opportunities) •
[⚙️ Setup](SETUP.md) •
[🤝 Contribute](CONTRIBUTING.md) •
[📊 How It Works](#️-how-it-works)

</div>

---

> **First run pending.** This repository was just initialized.  
> Run `python scripts/main.py` locally or trigger the GitHub Action to populate with live data.

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

## 🚀 Quick Start (Fork & Deploy)

1. **Fork** this repository
2. Enable **GitHub Actions** (Actions tab → enable)
3. Enable **GitHub Pages** (Settings → Pages → Source: GitHub Actions)
4. Trigger the workflow manually or wait for the scheduled run

See [SETUP.md](SETUP.md) for detailed instructions.

---

## 📁 Repository Structure

```
PlacementPulse/
├── .github/workflows/     # GitHub Actions (daily update, CI, PR validation)
├── config/                # Settings and configuration
├── scripts/
│   ├── core/              # Models, HTTP client, storage, dedup, normalizer
│   ├── scrapers/          # One scraper per source (easy to add new ones)
│   ├── generators/        # Markdown, README, stats, website generators
│   ├── tests/             # 39 unit tests, all passing
│   ├── pipeline.py        # Orchestrator
│   └── main.py            # CLI entry point
├── data/processed/        # Normalized opportunity JSON
├── daily/                 # Daily digest Markdown (auto-generated)
├── companies/             # Per-company pages (auto-generated)
├── categories/            # Per-category pages (auto-generated)
├── stats/                 # CSV statistics (auto-generated)
├── website/               # Static website for GitHub Pages (auto-generated)
└── resources/             # Resume tips, learning roadmaps
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) to add a new scraper in under 30 minutes.

---

## 📜 License

MIT — free to fork, use, and build on.
