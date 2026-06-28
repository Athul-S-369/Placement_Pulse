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
from config.settings import WEBSITE_DIR, SITE_DESCRIPTION, GITHUB_REPO_URL

log = get_logger("generator.website")

CATEGORY_LABEL = {
    "internship": "Internship",
    "fresher-job": "Fresher Job",
    "off-campus-drive": "Off-Campus Drive",
    "hiring-challenge": "Hiring Challenge",
    "hackathon": "Hackathon",
    "fellowship": "Fellowship",
    "open-source-program": "Open Source",
    "student-ambassador": "Ambassador",
    "scholarship": "Scholarship",
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
/* PlacementPulse — Luxury Dark UI */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
  --bg:          #080c12;
  --bg2:         #0d1117;
  --surface:     #111820;
  --surface2:    #18222e;
  --border:      #1e2d3d;
  --border2:     #243548;
  --text:        #e2e8f0;
  --text-muted:  #64748b;
  --text-dim:    #94a3b8;
  --gold:        #c9a84c;
  --gold-light:  #e4c46e;
  --gold-dim:    rgba(201,168,76,0.12);
  --accent:      #3b82f6;
  --accent-dim:  rgba(59,130,246,0.12);
  --green:       #10b981;
  --green-dim:   rgba(16,185,129,0.1);
  --radius:      10px;
  --radius-lg:   16px;
  --font-sans:   'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif:  'Playfair Display', Georgia, serif;
  --shadow:      0 4px 24px rgba(0,0,0,0.4);
  --shadow-card: 0 2px 12px rgba(0,0,0,0.3);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }

body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  font-size: 14.5px;
}

a { color: var(--gold-light); text-decoration: none; transition: color 0.2s; }
a:hover { color: #fff; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── Layout ── */
.container { max-width: 1160px; margin: 0 auto; padding: 0 1.5rem; }

/* ── Header ── */
header {
  background: rgba(8,12,18,0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 100;
  padding: 1rem 0;
}
.header-inner {
  display: flex; align-items: center; gap: 1.5rem;
}
.logo {
  font-family: var(--font-serif);
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--gold-light);
  letter-spacing: 0.01em;
}
.logo span { color: var(--text-dim); font-weight: 300; }
.header-badge {
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  border: 1px solid var(--border2);
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
}
nav { display: flex; gap: 1.5rem; margin-left: auto; }
nav a {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.03em;
}
nav a:hover { color: var(--text); }

/* ── Hero ── */
.hero {
  padding: 4.5rem 0 3rem;
  text-align: center;
  position: relative;
}
.hero::before {
  content: '';
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 300px;
  background: radial-gradient(ellipse at center, rgba(201,168,76,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--gold);
  border: 1px solid rgba(201,168,76,0.3);
  border-radius: 4px;
  padding: 0.3rem 0.8rem;
  margin-bottom: 1.5rem;
}
.hero h1 {
  font-family: var(--font-serif);
  font-size: 3rem;
  font-weight: 700;
  line-height: 1.15;
  color: var(--text);
  margin-bottom: 1rem;
  letter-spacing: -0.01em;
}
.hero h1 em {
  font-style: normal;
  color: var(--gold-light);
}
.hero p {
  color: var(--text-muted);
  font-size: 1rem;
  max-width: 500px;
  margin: 0 auto 2.5rem;
  font-weight: 400;
  line-height: 1.7;
}

/* ── Stats ── */
.stats-bar {
  display: flex; gap: 0; flex-wrap: wrap; justify-content: center;
  margin-bottom: 2.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  max-width: 640px;
  margin-left: auto; margin-right: auto;
  background: var(--surface);
}
.stat-chip {
  flex: 1; min-width: 120px;
  padding: 1rem 1.25rem;
  text-align: center;
  border-right: 1px solid var(--border);
  position: relative;
}
.stat-chip:last-child { border-right: none; }
.stat-chip .stat-val {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--gold-light);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}
.stat-chip .stat-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-top: 0.2rem;
}

/* ── Search ── */
.search-wrap {
  max-width: 560px; margin: 0 auto 2.5rem;
  position: relative;
}
.search-icon {
  position: absolute; left: 1rem; top: 50%; transform: translateY(-50%);
  color: var(--text-muted); font-size: 0.9rem; pointer-events: none;
}
.search-wrap input {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: var(--radius);
  color: var(--text);
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  font-size: 0.95rem;
  font-family: var(--font-sans);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-wrap input::placeholder { color: var(--text-muted); }
.search-wrap input:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(201,168,76,0.1);
}

/* ── Filters ── */
.filter-section { margin-bottom: 2rem; }
.filter-group {
  display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center;
  margin-bottom: 0.75rem;
}
.filter-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  min-width: 60px;
}
.filter-btn {
  background: transparent;
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.78rem;
  font-family: var(--font-sans);
  font-weight: 500;
  padding: 0.35rem 0.85rem;
  transition: all 0.15s;
  letter-spacing: 0.01em;
}
.filter-btn:hover {
  border-color: var(--gold);
  color: var(--gold-light);
  background: var(--gold-dim);
}
.filter-btn.active {
  background: var(--gold-dim);
  border-color: var(--gold);
  color: var(--gold-light);
}
.results-meta {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
.results-meta span { color: var(--text-dim); font-weight: 600; }

/* ── Cards ── */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.card {
  background: var(--surface);
  padding: 1.4rem 1.5rem;
  transition: background 0.15s;
  display: flex; flex-direction: column; gap: 0.6rem;
  position: relative;
}
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: transparent;
  transition: background 0.2s;
}
.card:hover { background: var(--surface2); }
.card:hover::before { background: var(--gold); }

.card-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem; }
.card-company {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text);
}
.card-title a { color: inherit; }
.card-title a:hover { color: var(--gold-light); }

.card-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag {
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.03em;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  background: var(--surface2);
  color: var(--text-muted);
  border: 1px solid var(--border);
}
.tag.cat  { background: var(--accent-dim); color: #60a5fa; border-color: rgba(59,130,246,0.2); }
.tag.loc  { background: var(--green-dim);  color: #34d399; border-color: rgba(16,185,129,0.2); }
.tag.date { background: var(--gold-dim);   color: var(--gold-light); border-color: rgba(201,168,76,0.2); }

.card-footer { margin-top: auto; padding-top: 0.75rem; border-top: 1px solid var(--border); }
.apply-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: transparent;
  border: 1px solid var(--gold);
  color: var(--gold-light);
  border-radius: 6px;
  padding: 0.45rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  font-family: var(--font-sans);
  letter-spacing: 0.04em;
  transition: all 0.15s;
}
.apply-btn:hover {
  background: var(--gold);
  color: var(--bg);
  text-decoration: none;
}
.apply-btn::after { content: '→'; }

/* ── No results ── */
.no-results {
  text-align: center;
  color: var(--text-muted);
  padding: 4rem 2rem;
  font-size: 0.95rem;
  line-height: 1.8;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.no-results strong { color: var(--text-dim); display: block; font-size: 1.1rem; margin-bottom: 0.5rem; }

/* ── Footer ── */
footer {
  margin-top: 5rem;
  padding: 2.5rem 0;
  border-top: 1px solid var(--border);
  text-align: center;
}
.footer-logo {
  font-family: var(--font-serif);
  font-size: 1.2rem;
  color: var(--gold-light);
  margin-bottom: 0.75rem;
}
.footer-links { display: flex; gap: 1.5rem; justify-content: center; margin-bottom: 1rem; flex-wrap: wrap; }
.footer-links a { font-size: 0.82rem; color: var(--text-muted); }
.footer-links a:hover { color: var(--text); }
.footer-meta { font-size: 0.75rem; color: var(--text-muted); }

/* ── Divider ── */
.section-divider {
  height: 1px; background: var(--border);
  margin: 2.5rem 0;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero h1 { font-size: 2rem; }
  .stat-chip { min-width: 90px; }
  .cards { grid-template-columns: 1fr; }
  .header-badge { display: none; }
}
@media (max-width: 480px) {
  .hero { padding: 3rem 0 2rem; }
  .hero h1 { font-size: 1.65rem; }
  .stats-bar { border-radius: var(--radius); }
  .stat-chip { padding: 0.75rem; }
  .stat-chip .stat-val { font-size: 1.2rem; }
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

const CAT_LABEL = {{
  "internship":"Internship","fresher-job":"Fresher Job","off-campus-drive":"Off-Campus",
  "hiring-challenge":"Hiring Challenge","hackathon":"Hackathon","fellowship":"Fellowship",
  "open-source-program":"Open Source","student-ambassador":"Ambassador","scholarship":"Scholarship"
}};

function cap(s) {{ return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }}

function renderCard(o) {{
  const catLabel = CAT_LABEL[o.category] || cap(o.category.replace(/-/g," "));
  const mode = cap(o.work_mode || "");
  const modeTag = mode ? `<span class="tag loc">${{mode}}</span>` : "";
  const deadline = o.deadline ? `<span class="tag date">Closes ${{o.deadline}}</span>` : "";
  const skills = (o.skills||[]).slice(0,2).map(s=>`<span class="tag">${{s}}</span>`).join("");
  const stipend = o.stipend ? `<span class="tag">${{o.stipend}}</span>` : "";
  return `
<div class="card" data-category="${{o.category}}" data-mode="${{o.work_mode}}">
  <div class="card-company">${{o.company}}</div>
  <div class="card-title"><a href="${{o.apply_link}}" target="_blank" rel="noopener">${{o.title}}</a></div>
  <div class="card-tags">
    <span class="tag cat">${{catLabel}}</span>
    ${{modeTag}}
    ${{deadline}}
    ${{stipend}}
    ${{skills}}
  </div>
  <div class="card-footer">
    <a class="apply-btn" href="${{o.apply_link}}" target="_blank" rel="noopener">Apply</a>
  </div>
</div>`;
}}

function render(opps) {{
  const container = document.getElementById("cards");
  if (!opps.length) {{
    container.innerHTML = '<div class="no-results"><strong>No results found</strong>Try different keywords or adjust your filters.</div>';
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
        '<button class="filter-btn active" data-filter="category:all">All Categories</button>'
    ] + [
        f'<button class="filter-btn" data-filter="category:{cat}">'
        f'{CATEGORY_LABEL.get(cat, cat.replace("-"," ").title())} ({cnt})</button>'
        for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1])
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{SITE_DESCRIPTION}">
  <title>PlacementPulse — India Tech Careers</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111820'/><text x='6' y='24' font-size='20' font-family='serif' fill='%23c9a84c'>P</text></svg>">
</head>
<body>

<header>
  <div class="container header-inner">
    <div class="logo">Placement<span>Pulse</span></div>
    <div class="header-badge">India &middot; Tech Careers</div>
    <nav>
      <a href="#opportunities">Opportunities</a>
      <a href="{GITHUB_REPO_URL}" target="_blank">GitHub</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero container">
    <div class="hero-eyebrow">India &middot; Software &middot; Updated Daily</div>
    <h1>Find Your Next<br><em>Tech Opportunity</em></h1>
    <p>Internships, fresher jobs, hackathons and fellowships across India — curated daily from the best sources.</p>

    <div class="stats-bar">
      <div class="stat-chip">
        <span class="stat-val">{total}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-chip">
        <span class="stat-val">{active_count}</span>
        <span class="stat-label">Active</span>
      </div>
      <div class="stat-chip">
        <span class="stat-val">{company_count}</span>
        <span class="stat-label">Companies</span>
      </div>
      <div class="stat-chip">
        <span class="stat-val">{today.strftime("%b %d")}</span>
        <span class="stat-label">Updated</span>
      </div>
    </div>

    <div class="search-wrap">
      <span class="search-icon">&#9906;</span>
      <input type="search" id="search-input" placeholder="Search roles, companies, skills..." autocomplete="off">
    </div>
  </section>

  <section id="opportunities" class="container">
    <div class="filter-section">
      <div class="filter-group">
        <span class="filter-label">Category</span>
        {"".join(cat_filter_btns)}
      </div>
      <div class="filter-group">
        <span class="filter-label">Mode</span>
        <button class="filter-btn active" data-filter="mode:all">All</button>
        <button class="filter-btn" data-filter="mode:remote">Remote</button>
        <button class="filter-btn" data-filter="mode:onsite">Onsite</button>
        <button class="filter-btn" data-filter="mode:hybrid">Hybrid</button>
      </div>
    </div>

    <div class="results-meta">Showing <span id="result-count"></span></div>

    <div id="cards" class="cards">
      <noscript><p style="padding:2rem;color:var(--text-muted)">Enable JavaScript to use the interactive search.</p></noscript>
    </div>
  </section>
</main>

<footer>
  <div class="container">
    <div class="footer-logo">PlacementPulse</div>
    <div class="footer-links">
      <a href="{GITHUB_REPO_URL}" target="_blank">GitHub</a>
      <a href="{GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md" target="_blank">Contribute</a>
      <a href="{GITHUB_REPO_URL}/issues" target="_blank">Report Issue</a>
    </div>
    <div class="footer-meta">
      Open-source &middot; No API keys &middot; Updated 3&times; daily &middot;
      Last run {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC
    </div>
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
  <meta http-equiv="refresh" content="4;url=/">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@400;500&display=swap');
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Inter',sans-serif;text-align:center;padding:5rem 1.5rem;
         background:#080c12;color:#64748b;min-height:100vh;
         display:flex;flex-direction:column;align-items:center;justify-content:center}
    .code{font-family:'Playfair Display',serif;font-size:5rem;color:#1e2d3d;line-height:1;margin-bottom:1.5rem}
    h1{font-family:'Playfair Display',serif;font-size:1.5rem;color:#e2e8f0;margin-bottom:0.75rem}
    p{font-size:0.9rem;margin-bottom:2rem}
    a{display:inline-block;border:1px solid #c9a84c;color:#e4c46e;border-radius:6px;
      padding:0.5rem 1.25rem;font-size:0.85rem;font-weight:500;transition:all .15s}
    a:hover{background:#c9a84c;color:#080c12;text-decoration:none}
  </style>
</head>
<body>
  <div class="code">404</div>
  <h1>Page Not Found</h1>
  <p>Redirecting to home in a moment...</p>
  <a href="/">Go Home</a>
</body>
</html>"""
    (WEBSITE_DIR / "404.html").write_text(html, encoding="utf-8")
