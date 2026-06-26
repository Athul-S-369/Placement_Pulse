"""
PlacementPulse - Deduplication Engine
Identifies and removes duplicate opportunities using multi-signal comparison.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger

log = get_logger(__name__)


# ─── Token-level Jaccard similarity ───────────────────────────────────────────

def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# ─── URL normalisation ────────────────────────────────────────────────────────

def _normalise_url(url: str) -> str:
    """Strip tracking params, trailing slashes, and protocol for comparison."""
    url = re.sub(r"https?://", "", url.lower()).rstrip("/")
    url = re.sub(r"\?.*$", "", url)  # drop query string
    return url


# ─── Main deduplication logic ─────────────────────────────────────────────────

def _is_duplicate(a: Opportunity, b: Opportunity, threshold: float = 0.85) -> bool:
    """
    Return True if *b* is a duplicate of *a*.
    Uses a voting approach: URL match wins immediately; otherwise two-of-three
    signals must agree.
    """
    # Hard match: same normalised apply URL
    if a.apply_link and b.apply_link:
        if _normalise_url(a.apply_link) == _normalise_url(b.apply_link):
            return True

    # Fingerprint match (same company+title+location hash)
    if a.id == b.id:
        return True

    # Company must match — different companies are never duplicates
    company_match = _jaccard(a.company, b.company) >= 0.8
    if not company_match:
        return False

    # With company confirmed, check title + location
    title_match = _jaccard(a.title, b.title) >= threshold
    loc_match = (
        bool(a.location and b.location)
        and _jaccard(a.location, b.location) >= 0.7
    )

    return title_match or loc_match


def deduplicate(opportunities: List[Opportunity]) -> Tuple[List[Opportunity], int]:
    """
    Remove duplicates from a list.
    Keeps the earliest (lowest index) occurrence as canonical.
    Returns (deduplicated_list, removed_count).
    """
    canonical: List[Opportunity] = []
    removed = 0

    for opp in opportunities:
        found_dup = False
        for canon in canonical:
            if _is_duplicate(canon, opp):
                log.debug(
                    "Duplicate detected: '%s @ %s' matches '%s @ %s'",
                    opp.title, opp.company,
                    canon.title, canon.company,
                )
                opp.is_duplicate = True
                opp.duplicate_of = canon.id
                removed += 1
                found_dup = True
                break
        if not found_dup:
            canonical.append(opp)

    log.info("Deduplication: %d kept, %d removed", len(canonical), removed)
    return canonical, removed
