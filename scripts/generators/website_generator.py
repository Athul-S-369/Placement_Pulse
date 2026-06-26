"""
PlacementPulse - Static Website Generator
Generates a complete single-page-application-style static website
in website/ that can be served from GitHub Pages with zero backend.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from config.settings import WEBSITE_DIR, SITE_TITLE, SITE_DESCRIPTION, GITHUB_REPO_URL

log = get_logger("generator.website")

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


def generate_website(all_opps: List[Opportunity]) -> Path:
    """Generate all static HTML files for the website."""
    WEBSITE_DIR.mkdir(parents=True, exist_ok=True)
    (WEBSITE_DIR / "assets").mkdir(parents=True, exist_ok=True)

    _write_css()
    _write_js(all_opps)
    _write_index(all_opps)
    _write_404()

    log.info("Website generated in %s", WEBSITE_DIR)
    return WEBSITE_DIR


def _write_css() -> None:
    css = """\
/* PlacementPulse - Minimal, fast, dark-mode-first CSS */
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface2: #242736;
  --border: #2e3248;
  --text: #e8eaf6;
  --text-muted: #8b90a8;
  --primary: #6c63ff;
  --primary-light: #8b85ff;
  --success: #4caf7d;
  --warning: #f4c542;
  --danger: #f44336;
  --radius: 8px;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #f5f7ff;
    --surface: #ffffff;
    --surface2: #f0f2ff;
    --border: #dde0f0;
    --text: #1a1d27;
    --text-muted: #5c6080;
  }
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  font-size: 15px;
}
a { color: var(--primary-light); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Layout */
.container { max-width: 1100px; margin: 0 auto; padding: 0 1rem; }

/* Header */
header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 100;
  padding: 0.75rem 0;
}
.header-inner { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.logo { font-size: 1.4rem; font-weight: 700; color: var(--primary-light); }
.logo span { color: var(--text); }
nav { display: flex; gap: 1rem; margin-left: auto; }
nav a { color: var(--text-muted); font-size: 0.9rem; }
nav a:hover { color: var(--text); }

/* Hero */
.hero {
  padding: 3rem 0 2rem;
  text-align: center;
}
.hero h1 { font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem; }
.hero p { color: var(--text-muted); font-size: 1.1rem; max-width: 560px; margin: 0 auto 1.5rem; }

/* Stats bar */
.stats-bar {
  display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;
  margin-bottom: 2rem;
}
.stat-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.3rem 1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.stat-chip strong { color: var(--primary-light); }

/* Search */
.search-bar {
  display: flex; gap: 0.5rem; max-width: 600px; margin: 0 auto 2rem;
}
.search-bar input {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  padding: 0.6rem 1rem;
  font-size: 1rem;
  outline: none;
  transition: border 0.2s;
}
.search-bar input:focus { border-color: var(--primary); }

/* Filters */
.filters {
  display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem;
}
.filter-btn {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0.3rem 0.9rem;
  transition: all 0.15s;
}
.filter-btn:hover, .filter-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

/* Cards */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  transition: border-color 0.15s, transform 0.15s;
}
.card:hover { border-color: var(--primary); transform: translateY(-2px); }
.card-company { font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
.card-title { font-weight: 600; margin: 0.2rem 0 0.5rem; font-size: 0.98rem; }
.card-title a { color: var(--text); }
.card-title a:hover { color: var(--primary-light); text-decoration: none; }
.card-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.tag {
  background: var(--surface2);
  border-radius: 4px;
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  color: var(--text-muted);
}
.tag.category { background: rgba(108,99,255,0.15); color: var(--primary-light); }
.tag.remote { background: rgba(76,175,125,0.15); color: var(--success); }
.tag.deadline-soon { background: rgba(244,197,66,0.15); color: var(--warning); }
.apply-btn {
  display: inline-block;
  background: var(--primary);
  color: #fff;
  border-radius: 5px;
  padding: 0.35rem 0.9rem;
  font-size: 0.82rem;
  margin-top: 0.7rem;
  transition: background 0.15s;
}
.apply-btn:hover { background: var(--primary-light); text-decoration: none; }

/* No results */
.no-results { text-align: center; color: var(--text-muted); padding: 3rem; }

/* Footer */
footer {
  border-top: 1px solid var(--border);
  padding: 1.5rem 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 3rem;
}

/* Responsive */
@media (max-width: 600px) {
  .hero h1 { font-size: 1.5rem; }
  .cards { grid-template-columns: 1fr; }
}
"""
    (WEBSITE_DIR / "assets" / "style.css").write_text(css, encoding="utf-8")


def _write_js(all_opps: List[Opportunity]) -> None:
    opps_json = json.dumps(
        [
            {
                "id": o.id,
                "title": o.title,
                "company": o.company,
                "category": o.category,
                "location": o.location,
                "work_mode": o.work_mode,
                "apply_link": o.apply_link,
                "deadline": o.deadline,
                "date_found": o.date_found,
                "skills": o.skills_required[:5],
                "tags": (o.domain_tags + o.tags)[:5],
                "stipend": o.salary or o.stipend,
                "source_name": o.source_name,
            }
            for o in all_opps
            if not o.is_expired() and o.title and o.apply_link
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )

    js = f"""\
// PlacementPulse — client-side search & filter
const ALL_OPPS = {opps_json};

const CAT_EMOJI = {{
  "internship":"🎓","fresher-job":"💼","off-campus-drive":"🚀",
  "hiring-challenge":"⚡","hackathon":"🏆","fellowship":"🌟",
  "open-source-program":"🔓","student-ambassador":"📢","scholarship":"📚"
}};

function renderCard(o) {{
  const emoji = CAT_EMOJI[o.category] || "•";
  const catLabel = o.category.replace(/-/g," ");
  const modeTag = o.work_mode === "remote"
    ? `<span class="tag remote">🌐 Remote</span>`
    : `<span class="tag">${{o.work_mode}}</span>`;
  const deadline = o.deadline
    ? `<span class="tag deadline-soon">📅 ${{o.deadline}}</span>` : "";
  const skills = (o.skills||[]).slice(0,3).map(s=>`<span class="tag">${{s}}</span>`).join("");
  const stipend = o.stipend ? `<span class="tag">💰 ${{o.stipend}}</span>` : "";
  return `
<div class="card" data-category="${{o.category}}" data-mode="${{o.work_mode}}">
  <div class="card-company">${{o.company}} · ${{o.source_name}}</div>
  <div class="card-title"><a href="${{o.apply_link}}" target="_blank" rel="noopener">${{o.title}}</a></div>
  <div class="card-meta">
    <span class="tag category">${{emoji}} ${{catLabel}}</span>
    ${{modeTag}}
    ${{deadline}}
    ${{stipend}}
    ${{skills}}
  </div>
  <a class="apply-btn" href="${{o.apply_link}}" target="_blank" rel="noopener">Apply →</a>
</div>`;
}}

function render(opps) {{
  const container = document.getElementById("cards");
  if (!opps.length) {{
    container.innerHTML = '<div class="no-results">😔 No opportunities match your filters. <br>Try different keywords or check back tomorrow!</div>';
    return;
  }}
  container.innerHTML = opps.map(renderCard).join("");
}}

let activeCategory = "all";
let activeMode = "all";
let searchQuery = "";

function applyFilters() {{
  let filtered = ALL_OPPS;
  if (activeCategory !== "all")
    filtered = filtered.filter(o => o.category === activeCategory);
  if (activeMode !== "all")
    filtered = filtered.filter(o => o.work_mode === activeMode);
  if (searchQuery) {{
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(o =>
      o.title.toLowerCase().includes(q) ||
      o.company.toLowerCase().includes(q) ||
      (o.tags||[]).some(t=>t.toLowerCase().includes(q)) ||
      (o.skills||[]).some(s=>s.toLowerCase().includes(q))
    );
  }}
  render(filtered);
  document.getElementById("result-count").textContent = `${{filtered.length}} opportunities`;
}}

document.addEventListener("DOMContentLoaded", () => {{
  render(ALL_OPPS);
  document.getElementById("result-count").textContent = `${{ALL_OPPS.length}} opportunities`;

  document.getElementById("search-input").addEventListener("input", e => {{
    searchQuery = e.target.value.trim();
    applyFilters();
  }});

  document.querySelectorAll("[data-filter]").forEach(btn => {{
    btn.addEventListener("click", () => {{
      const [type, val] = btn.dataset.filter.split(":");
      if (type === "category") activeCategory = val;
      if (type === "mode") activeMode = val;
      document.querySelectorAll(`[data-filter^="${{type}}:"]`).forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      applyFilters();
    }});
  }});
}});
"""
    (WEBSITE_DIR / "assets" / "app.js").write_text(js, encoding="utf-8")


def _write_index(all_opps: List[Opportunity]) -> None:
    today = date.today()
    active = [o for o in all_opps if not o.is_expired() and o.title and o.apply_link]
    cat_counts = Counter(o.category for o in active)
    total = len(all_opps)
    active_count = len(active)
    company_count = len({o.company for o in all_opps if o.company})

    cat_filter_btns = [
        '<button class="filter-btn active" data-filter="category:all">All</button>'
    ] + [
        f'<button class="filter-btn" data-filter="category:{cat}">'
        f'{CATEGORY_EMOJI.get(cat,"•")} {cat.replace("-"," ").title()} ({cnt})</button>'
        for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1])
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{SITE_DESCRIPTION}">
  <title>{SITE_TITLE} — Indian Software Internships & Jobs</title>
  <link rel="stylesheet" href="assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>">
</head>
<body>

<header>
  <div class="container header-inner">
    <div class="logo">Placement<span>Pulse</span></div>
    <nav>
      <a href="#opportunities">Opportunities</a>
      <a href="stats.json">Stats</a>
      <a href="{GITHUB_REPO_URL}" target="_blank">GitHub</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero container">
    <h1>🚀 PlacementPulse</h1>
    <p>{SITE_DESCRIPTION}</p>

    <div class="stats-bar">
      <div class="stat-chip">📦 <strong>{total}</strong> total</div>
      <div class="stat-chip">✅ <strong>{active_count}</strong> active</div>
      <div class="stat-chip">🏢 <strong>{company_count}</strong> companies</div>
      <div class="stat-chip">🕒 Updated <strong>{today.isoformat()}</strong></div>
    </div>

    <div class="search-bar">
      <input type="search" id="search-input" placeholder="Search by title, company, or skill…" autocomplete="off">
    </div>
  </section>

  <section id="opportunities" class="container">
    <div class="filters">
      {"".join(cat_filter_btns)}
      &nbsp;
      <button class="filter-btn active" data-filter="mode:all">All Modes</button>
      <button class="filter-btn" data-filter="mode:remote">🌐 Remote</button>
      <button class="filter-btn" data-filter="mode:onsite">🏢 Onsite</button>
      <button class="filter-btn" data-filter="mode:hybrid">🔀 Hybrid</button>
    </div>

    <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:1rem;">
      Showing <span id="result-count"></span>
    </p>

    <div id="cards" class="cards">
      <!-- Populated by app.js -->
      <noscript>
        <p>Please enable JavaScript to use the interactive search.</p>
      </noscript>
    </div>
  </section>
</main>

<footer>
  <div class="container">
    <p>
      🚀 <strong>PlacementPulse</strong> — Open-source, updated daily via GitHub Actions.<br>
      <a href="{GITHUB_REPO_URL}" target="_blank">⭐ Star on GitHub</a> •
      <a href="{GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md" target="_blank">Contribute</a> •
      <a href="{GITHUB_REPO_URL}/issues" target="_blank">Report Issue</a>
    </p>
    <p style="margin-top:0.5rem;color:var(--text-muted);font-size:0.78rem;">
      Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC
    </p>
  </div>
</footer>

<script src="assets/app.js"></script>
</body>
</html>
"""
    (WEBSITE_DIR / "index.html").write_text(html, encoding="utf-8")
    log.info("Generated website index.html")


def _write_404() -> None:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>404 — PlacementPulse</title>
  <meta http-equiv="refresh" content="3;url=/">
  <style>body{font-family:sans-serif;text-align:center;padding:3rem;background:#0f1117;color:#e8eaf6}</style>
</head>
<body>
  <h1>🚀 404 — Page Not Found</h1>
  <p>Redirecting to home in 3 seconds…</p>
  <p><a href="/" style="color:#6c63ff">Go Home</a></p>
</body>
</html>"""
    (WEBSITE_DIR / "404.html").write_text(html, encoding="utf-8")
