#!/usr/bin/env python3
"""
Login Trigger for AutoBlog

Wrapper script that runs on login and generates blog posts for any missed
days in the past 7 days. Uses a marker file to avoid running multiple times
per day.
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


MARKER_FILE = Path.home() / ".autoblog_last_run"
SCRIPT_DIR = Path(__file__).parent
DAILY_BLOG_SCRIPT = SCRIPT_DIR / "daily_blog.py"
POSTS_DIR = SCRIPT_DIR.parent / "_posts"
DRAFTS_DIR = SCRIPT_DIR.parent / "_drafts"
BACKFILL_DAYS = 7


def get_last_run_date() -> Optional[str]:
    """Read the last run date from marker file."""
    if not MARKER_FILE.exists():
        return None
    try:
        return MARKER_FILE.read_text().strip()
    except Exception:
        return None


def set_last_run_date(date: str) -> None:
    """Write today's date to marker file."""
    MARKER_FILE.write_text(date)


def main() -> int:
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if already ran today
    last_run = get_last_run_date()
    if last_run == today:
        print(f"Already ran today ({today}), skipping")
        return 0

    print(f"Running blog generation backfill for past {BACKFILL_DAYS} days")

    # Loop through past 7 days (oldest to newest, excluding today)
    # This ensures posts are generated in chronological order
    any_failures = False
    for days_ago in range(BACKFILL_DAYS, 0, -1):
        target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        print(f"\nProcessing {target_date}...")

        # Skip if post already exists for this date
        if list(POSTS_DIR.glob(f"{target_date}-*.md")) or list(DRAFTS_DIR.glob(f"{target_date}-*.md")):
            print(f"  Post or draft already exists, skipping")
            continue

        result = subprocess.run(
            [sys.executable, str(DAILY_BLOG_SCRIPT), "run", "--date", target_date],
            cwd=SCRIPT_DIR.parent,
        )

        if result.returncode != 0:
            print(f"  Blog generation failed for {target_date} (code {result.returncode})")
            any_failures = True
        else:
            print(f"  Completed {target_date}")

    # Update marker file regardless of success/failure
    # (we don't want to keep retrying on login if there's an error)
    set_last_run_date(today)

    if any_failures:
        print("\nSome days failed to generate. Check logs for details.")
        return 1

    print("\nBlog generation backfill completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
