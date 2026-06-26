"""
PlacementPulse - Storage Layer
JSON-based persistence for opportunities with atomic writes.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.models import Opportunity
from scripts.core.logger import get_logger
from config.settings import DATA_PROCESSED_DIR, DATA_RAW_DIR

log = get_logger(__name__)

MASTER_FILE = DATA_PROCESSED_DIR / "opportunities.json"
TODAY_FILE = DATA_PROCESSED_DIR / f"today_{date.today().isoformat()}.json"


def _atomic_write(path: Path, data: str) -> None:
    """Write to a temp file then rename — prevents partial writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise


def load_all() -> List[Opportunity]:
    """Load all opportunities from the master JSON file."""
    if not MASTER_FILE.exists():
        return []
    with open(MASTER_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    opps = [Opportunity.from_dict(o) for o in raw]
    log.info("Loaded %d opportunities from storage", len(opps))
    return opps


def save_all(opportunities: List[Opportunity]) -> None:
    """Persist the full list atomically."""
    data = json.dumps(
        [o.to_dict() for o in opportunities],
        indent=2,
        ensure_ascii=False,
    )
    _atomic_write(MASTER_FILE, data)
    log.info("Saved %d opportunities to %s", len(opportunities), MASTER_FILE)


def save_today(opportunities: List[Opportunity]) -> None:
    """Write today's snapshot (raw + processed)."""
    data = json.dumps(
        [o.to_dict() for o in opportunities],
        indent=2,
        ensure_ascii=False,
    )
    _atomic_write(TODAY_FILE, data)
    log.info("Saved %d today-opportunities to %s", len(opportunities), TODAY_FILE)


def save_raw(source_name: str, data: list | dict) -> Path:
    """Dump raw scraper output for auditing/debugging."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    path = DATA_RAW_DIR / f"{source_name}_{ts}.json"
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))
    return path


def load_today_opps() -> List[Opportunity]:
    """Load today's snapshot if it exists, else return empty list."""
    if not TODAY_FILE.exists():
        return []
    with open(TODAY_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return [Opportunity.from_dict(o) for o in raw]


def merge(existing: List[Opportunity], new: List[Opportunity]) -> List[Opportunity]:
    """
    Merge new opportunities into the existing list.
    Existing entries with the same id are updated (last-write wins for
    metadata fields, but apply_link is preserved).
    """
    index: Dict[str, Opportunity] = {o.id: o for o in existing}
    added = 0
    updated = 0

    for opp in new:
        if opp.id in index:
            # Update last_checked and potentially refresh fields
            old = index[opp.id]
            old.last_checked = opp.last_checked or old.last_checked
            old.verification_status = opp.verification_status
            updated += 1
        else:
            index[opp.id] = opp
            added += 1

    log.info("Merge: %d added, %d updated, %d total", added, updated, len(index))
    return list(index.values())
