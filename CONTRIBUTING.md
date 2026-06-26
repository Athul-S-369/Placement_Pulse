# 🤝 Contributing to PlacementPulse

Thank you for helping make PlacementPulse better! This guide explains how to add
scrapers, fix bugs, improve docs, or suggest new data sources.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Adding a New Scraper](#adding-a-new-scraper)
3. [Coding Standards](#coding-standards)
4. [Running Tests](#running-tests)
5. [Pull Request Checklist](#pull-request-checklist)
6. [Suggesting a Data Source](#suggesting-a-data-source)

---

## Quick Start

```bash
# 1. Fork & clone
git clone https://github.com/your-username/PlacementPulse.git
cd PlacementPulse

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 4. Run existing tests
pytest scripts/tests/

# 5. Run the pipeline locally (dry run — no commit)
python scripts/main.py --dry-run
```

---

## Adding a New Scraper

### 1. Create the scraper file

Create `scripts/scrapers/<source_name>.py`:

```python
"""
PlacementPulse - <Source Name> Scraper
Scrapes <description of what this scrapes>.
Only uses public, freely accessible endpoints.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scrapers.base import BaseScraper
from scripts.core.models import Opportunity
from scripts.core.http_client import fetch_json, get   # use these, not requests directly


class MySourceScraper(BaseScraper):
    name = "my-source"          # unique slug, used in logs and filenames
    base_url = "https://example.com"

    def scrape(self) -> List[Opportunity]:
        data = fetch_json("https://example.com/api/jobs")
        if not data:
            return []

        opps = []
        for item in data.get("jobs", []):
            opps.append(Opportunity(
                title=item["title"],
                company=item["company"],
                category="internship",         # see Category enum in models.py
                apply_link=item["url"],
                source_url=self.base_url,
                source_name="My Source",
                location=item.get("location", "India"),
                description=item.get("description", "")[:500],
            ))
        return opps
```

### 2. Register the scraper

Add it to `scripts/pipeline.py`:

```python
from scripts.scrapers.my_source import MySourceScraper

SCRAPERS = [
    ...
    MySourceScraper,    # ← add here
]
```

### 3. Write a test

Add to `scripts/tests/test_scrapers.py`:

```python
from unittest.mock import patch
from scripts.scrapers.my_source import MySourceScraper

@patch("scripts.scrapers.my_source.fetch_json")
def test_my_source_scraper(mock_fetch):
    mock_fetch.return_value = {"jobs": [
        {"title": "Intern", "company": "Acme", "url": "https://example.com/1"}
    ]}
    scraper = MySourceScraper()
    results = scraper.scrape()
    assert len(results) == 1
    assert results[0].title == "Intern"
```

### 4. Submit a PR

Open a pull request with:
- The new scraper file
- Registration in `pipeline.py`
- At least one unit test
- A brief description of the source

---

## Coding Standards

- **Python 3.10+** with type hints
- Use `scripts.core.http_client.get()` / `fetch_json()` — never `requests` directly
- Respect rate limits: the HTTP client adds delays automatically
- Keep `scrape()` focused — one responsibility per scraper
- Truncate descriptions to ≤ 500 characters
- Cap results per scraper at ≤ 200 to avoid memory issues
- Log meaningful info: `self.log.info(...)` / `self.log.warning(...)`

### Robots.txt Policy

Before adding a scraper, check the site's `robots.txt`. If scraping is disallowed for
career data / job listings, use an alternative (RSS feed, public JSON API, GitHub list).
Flag any uncertain cases in your PR.

---

## Running Tests

```bash
# All unit tests (no network required)
pytest scripts/tests/ -v

# With smoke tests (requires network)
pytest scripts/tests/ -v -m smoke

# Lint
ruff check scripts/ config/

# Type check
mypy scripts/core/ config/ --ignore-missing-imports
```

---

## Pull Request Checklist

- [ ] Scraper only uses free, public endpoints (no API keys)
- [ ] `BaseScraper` is the parent class
- [ ] `name` attribute is set and unique
- [ ] Returns `List[Opportunity]` with all required fields
- [ ] Unit test added and passing
- [ ] `ruff` lint passes
- [ ] PR description explains the source and why it's valuable

---

## Suggesting a Data Source

Open a [GitHub Issue](https://github.com/your-username/PlacementPulse/issues/new)
with the label `new-source` and include:

- Source URL
- What type of opportunities it lists
- Whether it's publicly accessible (no login required)
- Whether it has an API, RSS feed, or is HTML only
- Why it's valuable for Indian students
