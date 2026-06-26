"""
PlacementPulse - Data Normalizer
Cleans, standardises, and enriches raw opportunity data.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity, WorkMode, Category
from scripts.core.logger import get_logger
from config.settings import CATEGORIES, GLOBAL_PROGRAMS, INDIA_LOCATIONS

log = get_logger(__name__)

# ─── Location ─────────────────────────────────────────────────────────────────

_REMOTE_KEYWORDS = ["remote", "work from home", "wfh", "anywhere"]
_HYBRID_KEYWORDS = ["hybrid", "partial remote"]
_INDIA_KEYWORDS = set(INDIA_LOCATIONS)

def _infer_work_mode(location: str) -> str:
    loc = location.lower()
    if any(k in loc for k in _REMOTE_KEYWORDS):
        return WorkMode.REMOTE.value
    if any(k in loc for k in _HYBRID_KEYWORDS):
        return WorkMode.HYBRID.value
    return WorkMode.ONSITE.value

_GLOBAL_PROGRAMS_LOWER = [p.lower() for p in GLOBAL_PROGRAMS]


def _is_india_opportunity(title: str, company: str, location: str) -> bool:
    """
    Return True if this opportunity is relevant for Indian students.
    Covers:
      - Any location mentioning India or an Indian city
      - Known global programmes (GSoC, Outreachy, MLH, etc.) — always India-eligible
      - Generic 'Remote' with no country qualifier (benefit of the doubt)
    """
    loc = location.lower()
    title_co = (title + " " + company).lower()

    if any(k in loc for k in _INDIA_KEYWORDS):
        return True
    if any(prog in title_co for prog in _GLOBAL_PROGRAMS_LOWER):
        return True
    # Pure remote / blank — keep; scraper already targeted India or it's a global programme
    if loc in ("remote", "work from home", "wfh", "anywhere", "remote / various", ""):
        return True
    return False

# ─── Category inference ───────────────────────────────────────────────────────

_CAT_PATTERNS = {
    Category.INTERNSHIP.value: [r"\bintern(ship)?\b", r"\btraineeship\b"],
    Category.HACKATHON.value: [r"\bhackathon\b", r"\bcode ?jam\b", r"\bcontest\b"],
    Category.HIRING_CHALLENGE.value: [r"\bhiring\s+challenge\b", r"\bchallenge\b.*\bhire\b"],
    Category.FELLOWSHIP.value: [r"\bfellow(ship)?\b"],
    Category.OPEN_SOURCE.value: [r"\bgsoc\b", r"\boutreachy\b", r"\bopen.source\b"],
    Category.AMBASSADOR.value: [r"\bambassador\b", r"\bstudent\s+partner\b"],
    Category.SCHOLARSHIP.value: [r"\bscholarship\b", r"\bgrant\b"],
    Category.OFF_CAMPUS.value: [r"\boff.campus\b", r"\bdrive\b"],
    Category.FRESHER_JOB.value: [r"\bfresher\b", r"\bentry.level\b", r"\bgraduate\b"],
}

def _infer_category(title: str, description: str, existing: str) -> str:
    if existing and existing in CATEGORIES:
        return existing
    combined = (title + " " + description).lower()
    for cat, patterns in _CAT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined):
                return cat
    return Category.INTERNSHIP.value

# ─── Domain tags ──────────────────────────────────────────────────────────────

_DOMAIN_PATTERNS = {
    "ai-ml": [r"\b(machine\s+learning|ml|artificial\s+intelligence|ai|nlp|deep\s+learning|llm)\b"],
    "software-engineering": [r"\b(software\s+engineer|swe|sde|backend|frontend|fullstack|full.stack)\b"],
    "frontend": [r"\b(react|vue|angular|frontend|front.end|ui|ux)\b"],
    "backend": [r"\b(backend|back.end|api|server|django|flask|node\.?js|spring)\b"],
    "devops": [r"\b(devops|kubernetes|docker|ci/cd|cloud|aws|gcp|azure)\b"],
    "data-science": [r"\b(data\s+science|data\s+analyst|analytics|spark|pandas|sql)\b"],
    "cybersecurity": [r"\b(security|pentest|ethical\s+hack|ctf|infosec|soc)\b"],
    "mobile": [r"\b(android|ios|flutter|react\s+native|swift|kotlin)\b"],
    "cloud": [r"\b(cloud|aws|gcp|azure|serverless|infrastructure)\b"],
    "design": [r"\b(ui/ux|product\s+design|figma|sketch|interaction)\b"],
    "embedded": [r"\b(embedded|firmware|rtos|iot|fpga|arduino|raspberry)\b"],
}

def _infer_domains(title: str, description: str) -> List[str]:
    combined = (title + " " + description).lower()
    found = []
    for domain, patterns in _DOMAIN_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined):
                found.append(domain)
                break
    return found

# ─── Batch / experience ───────────────────────────────────────────────────────

_BATCH_PATTERN = re.compile(r"\b(20[2-9]\d)\b")

def _extract_batches(text: str) -> List[str]:
    return list(set(_BATCH_PATTERN.findall(text)))

_EXP_PATTERN = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?", re.I)

def _extract_experience(text: str) -> str:
    m = _EXP_PATTERN.search(text)
    return m.group(1) if m else "0"

# ─── Text cleaning ────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ─── Public API ───────────────────────────────────────────────────────────────

def normalize(opp: Opportunity) -> Opportunity:
    """In-place normalization — returns the same object for chaining."""
    opp.title = _clean(opp.title)
    opp.company = _clean(opp.company)
    opp.description = _clean(opp.description)
    opp.location = _clean(opp.location)

    if not opp.work_mode or opp.work_mode == WorkMode.UNKNOWN.value:
        opp.work_mode = _infer_work_mode(opp.location)

    opp.is_india = _is_india_opportunity(opp.title, opp.company, opp.location) or opp.is_india

    opp.category = _infer_category(opp.title, opp.description, opp.category)

    if not opp.domain_tags:
        opp.domain_tags = _infer_domains(opp.title, opp.description)

    if not opp.batch_eligible:
        combined = opp.title + " " + opp.description
        opp.batch_eligible = _extract_batches(combined)

    if opp.experience_required == "0":
        opp.experience_required = _extract_experience(opp.description)

    # Rebuild fingerprint after normalization
    opp.id = opp._fingerprint()
    return opp


def normalize_all(opportunities: List[Opportunity]) -> List[Opportunity]:
    return [normalize(o) for o in opportunities]
