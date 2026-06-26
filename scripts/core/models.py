"""
PlacementPulse - Core Data Models
Canonical dataclass schema for every opportunity in the system.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import List


class Category(str, Enum):
    INTERNSHIP = "internship"
    FRESHER_JOB = "fresher-job"
    OFF_CAMPUS = "off-campus-drive"
    HIRING_CHALLENGE = "hiring-challenge"
    HACKATHON = "hackathon"
    FELLOWSHIP = "fellowship"
    OPEN_SOURCE = "open-source-program"
    AMBASSADOR = "student-ambassador"
    SCHOLARSHIP = "scholarship"


class WorkMode(str, Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class Opportunity:
    """Single placement/internship opportunity - the canonical schema."""

    # ── Identity ──────────────────────────────────────────────────────────────
    id: str = ""                          # SHA-256 fingerprint (auto-generated)
    title: str = ""
    company: str = ""
    company_slug: str = ""               # lowercase-hyphenated

    # ── Classification ────────────────────────────────────────────────────────
    category: str = Category.INTERNSHIP.value
    domain_tags: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # ── Location ──────────────────────────────────────────────────────────────
    location: str = ""
    work_mode: str = WorkMode.UNKNOWN.value
    is_india: bool = True

    # ── Application ───────────────────────────────────────────────────────────
    apply_link: str = ""
    source_url: str = ""
    source_name: str = ""

    # ── Dates ─────────────────────────────────────────────────────────────────
    date_found: str = ""                 # ISO 8601 date string
    date_posted: str = ""
    deadline: str = ""                   # ISO 8601 or human-readable
    last_checked: str = ""

    # ── Eligibility ───────────────────────────────────────────────────────────
    batch_eligible: List[str] = field(default_factory=list)  # ["2024", "2025"]
    experience_required: str = "0"       # years; "0" = fresher
    skills_required: List[str] = field(default_factory=list)

    # ── Compensation ──────────────────────────────────────────────────────────
    salary: str = ""                     # raw string if available
    stipend: str = ""

    # ── Content ───────────────────────────────────────────────────────────────
    description: str = ""
    responsibilities: List[str] = field(default_factory=list)

    # ── Quality ───────────────────────────────────────────────────────────────
    verification_status: str = VerificationStatus.UNVERIFIED.value
    is_duplicate: bool = False
    duplicate_of: str = ""               # id of canonical entry

    def __post_init__(self) -> None:
        now = date.today().isoformat()
        if not self.date_found:
            self.date_found = now
        if not self.last_checked:
            self.last_checked = now
        if not self.company_slug:
            self.company_slug = _slugify(self.company)
        if not self.id:
            self.id = self._fingerprint()

    def _fingerprint(self) -> str:
        """Stable SHA-256 id based on company + title + location."""
        key = f"{self.company.lower().strip()}|{self.title.lower().strip()}|{self.location.lower().strip()}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Opportunity":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def is_expired(self) -> bool:
        if not self.deadline:
            return False
        try:
            deadline_date = date.fromisoformat(self.deadline[:10])
            return deadline_date < date.today()
        except ValueError:
            return False


def _slugify(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
