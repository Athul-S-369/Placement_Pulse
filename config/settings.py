"""
PlacementPulse - Global Configuration
Central configuration for all scrapers, pipelines, and generators.
"""

from pathlib import Path
from typing import List

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DAILY_DIR = ROOT_DIR / "daily"
COMPANIES_DIR = ROOT_DIR / "companies"
CATEGORIES_DIR = ROOT_DIR / "categories"
STATS_DIR = ROOT_DIR / "stats"
WEBSITE_DIR = ROOT_DIR / "website"
LOGS_DIR = ROOT_DIR / "logs"

# ─── Scraper Defaults ─────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 20          # seconds
REQUEST_DELAY_MIN = 1.5       # seconds between requests (min)
REQUEST_DELAY_MAX = 3.5       # seconds between requests (max)
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

# ─── Deduplication ────────────────────────────────────────────────────────────
TITLE_SIMILARITY_THRESHOLD = 0.85   # Jaccard / token ratio

# ─── GitHub / Git ─────────────────────────────────────────────────────────────
GIT_COMMIT_PREFIX = "feat(data): "
GIT_AUTHOR_NAME = "PlacementPulse Bot"
GIT_AUTHOR_EMAIL = "bot@placementpulse.dev"

# ─── Website ──────────────────────────────────────────────────────────────────
SITE_TITLE = "PlacementPulse"
SITE_DESCRIPTION = (
    "India's largest open-source collection of software internships, "
    "fresher jobs, hackathons, and placement opportunities — updated daily, 100% free."
)
SITE_URL = "https://athul-s-369.github.io/PlacementPulse"
GITHUB_REPO_URL = "https://github.com/Athul-S-369/PlacementPulse"

# ─── Opportunity Categories ───────────────────────────────────────────────────
CATEGORIES = [
    "internship",
    "fresher-job",
    "off-campus-drive",
    "hiring-challenge",
    "hackathon",
    "fellowship",
    "open-source-program",
    "student-ambassador",
    "scholarship",
]

TECH_DOMAINS = [
    "ai-ml", "software-engineering", "frontend", "backend",
    "fullstack", "devops", "cybersecurity", "data-science",
    "mobile", "embedded", "cloud", "design", "product",
]

# ─── India-only mode ─────────────────────────────────────────────────────────
# When True, any opportunity not linked to India is dropped after normalization.
INDIA_ONLY: bool = True

# ─── India-specific location keywords ────────────────────────────────────────
INDIA_LOCATIONS = [
    "india", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai",
    "delhi", "new delhi", "gurugram", "gurgaon", "noida", "chennai",
    "kolkata", "ahmedabad", "remote india", "pan india", "india remote",
    "india / remote", "remote / india", "anywhere in india",
    "kochi", "coimbatore", "jaipur", "indore", "bhubaneswar",
    "thiruvananthapuram", "trivandrum", "chandigarh", "nagpur", "surat",
]

# Programmes / fellowships that are open worldwide but strongly India-eligible
GLOBAL_PROGRAMS = [
    "gsoc", "google summer of code", "outreachy", "mlh fellowship",
    "linux foundation", "season of docs", "github campus expert",
    "microsoft learn student ambassadors",
]

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
