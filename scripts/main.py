"""
PlacementPulse - Main Entry Point
Runs the full pipeline: scrape → normalize → dedup → generate → commit.

Usage:
    python scripts/main.py                 # full run
    python scripts/main.py --scrape-only   # only collect data
    python scripts/main.py --generate-only # only regenerate content from stored data
    python scripts/main.py --dry-run       # full run but skip git commit
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.pipeline import run_pipeline
from scripts.core.storage import load_all, load_today_opps
from scripts.core.logger import get_logger
from scripts.generators.markdown_generator import (
    generate_daily,
    generate_category_pages,
    generate_company_pages,
)
from scripts.generators.readme_generator import generate_readme
from scripts.generators.stats_generator import generate_stats, generate_search_index
from scripts.generators.website_generator import generate_website

log = get_logger("main")


def run_generators(all_opps, today_opps, stats):
    log.info("Running generators…")
    generate_daily(today_opps, all_opps)
    generate_category_pages(all_opps)
    generate_company_pages(all_opps)
    generate_readme(all_opps, today_opps, stats)
    generate_stats(all_opps, today_opps)
    generate_search_index(all_opps)
    generate_website(all_opps)
    log.info("All generators complete.")


def git_commit_if_changed(dry_run: bool = False) -> bool:
    """
    Stages all changed files and creates a commit ONLY if there are actual diffs.
    Returns True if a commit was made.
    """
    root = Path(__file__).parent.parent

    # Check for any changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=root,
    )
    if not result.stdout.strip():
        log.info("No changes detected — skipping commit.")
        return False

    today = date.today().isoformat()
    commit_msg = f"feat(data): update opportunities for {today}"

    if dry_run:
        log.info("[dry-run] Would commit: %s", commit_msg)
        log.info("[dry-run] Changed files:\n%s", result.stdout)
        return False

    # Stage all changes
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)

    # Commit
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=root, check=True,
        env={
            **__import__("os").environ,
            "GIT_AUTHOR_NAME": "PlacementPulse Bot",
            "GIT_AUTHOR_EMAIL": "bot@placementpulse.dev",
            "GIT_COMMITTER_NAME": "PlacementPulse Bot",
            "GIT_COMMITTER_EMAIL": "bot@placementpulse.dev",
        },
    )
    log.info("Committed: %s", commit_msg)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="PlacementPulse pipeline")
    parser.add_argument("--scrape-only", action="store_true", help="Only run scrapers")
    parser.add_argument("--generate-only", action="store_true", help="Only run generators")
    parser.add_argument("--dry-run", action="store_true", help="Skip git commit/push")
    args = parser.parse_args()

    if args.generate_only:
        all_opps = load_all()
        today_opps = load_today_opps()
        stats = {
            "date": date.today().isoformat(),
            "total": len(all_opps),
            "new_today": len(today_opps),
        }
        run_generators(all_opps, today_opps, stats)
    else:
        all_opps, stats = run_pipeline()
        today_opps = load_today_opps()
        if not args.scrape_only:
            run_generators(all_opps, today_opps, stats)

    if not args.scrape_only and not args.dry_run:
        committed = git_commit_if_changed(dry_run=False)
        if committed:
            print("✓ Changes committed.")
        else:
            print("✓ No changes — nothing committed.")
    elif args.dry_run:
        git_commit_if_changed(dry_run=True)

    print(f"\n{'='*50}")
    print(f"  PlacementPulse run complete — {date.today().isoformat()}")
    print(f"  Total opportunities: {stats.get('total', '?')}")
    print(f"  New today:          {stats.get('new_today', '?')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
