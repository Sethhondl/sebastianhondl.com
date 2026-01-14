#!/usr/bin/env python3
"""
Daily Blog Orchestration Script for AutoBlog

Main entry point for the automated blog generation system.
Coordinates project memory updates, blog generation, and Git operations.
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import argparse
import logging

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from project_memory import ProjectMemory
from generate_post import BlogGenerator


# Setup logging
def setup_logging(log_file: Optional[Path] = None) -> logging.Logger:
    """Configure logging for the daily blog script."""
    logger = logging.getLogger("autoblog")
    logger.setLevel(logging.INFO)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)

    return logger


class DailyBlogRunner:
    """Orchestrates the daily blog generation process."""

    def __init__(self, repo_dir: Optional[Path] = None, log_file: Optional[Path] = None):
        self.repo_dir = repo_dir or Path(__file__).parent.parent
        self.posts_dir = self.repo_dir / "_posts"
        self.scripts_dir = self.repo_dir / "scripts"
        self.log_file = log_file
        self.logger = setup_logging(log_file)

        self.memory = ProjectMemory(
            index_path=self.scripts_dir / "data" / "project_index.json"
        )
        self.generator = BlogGenerator(posts_dir=self.posts_dir)

    def run(self, date: Optional[str] = None, skip_push: bool = False,
            skip_summaries: bool = False) -> bool:
        """
        Run the full daily blog generation process.

        Args:
            date: Date to generate for (defaults to today)
            skip_push: Don't push to GitHub
            skip_summaries: Don't generate Claude summaries (faster)

        Returns:
            True if successful, False otherwise
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.logger.info(f"Starting daily blog generation for {date}")

        try:
            # Step 1: Update project memory index
            self.logger.info("Step 1/4: Updating project memory index...")
            stats = self.memory.update_index(use_claude_for_summaries=not skip_summaries)
            self.logger.info(f"  Found {stats['new_sessions']} new sessions")
            self.logger.info(f"  New projects: {stats['new_projects']}")

            # Step 2: Get context for blog generation
            self.logger.info("Step 2/4: Gathering context...")
            context = self.memory.get_context_for_blog(date)

            if not context.get("today"):
                self.logger.info(f"  No transcripts found for {date}")
                self.logger.info("  Checking for transcripts from yesterday...")

                # Try yesterday if today is empty (for early morning runs)
                yesterday = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                context = self.memory.get_context_for_blog(yesterday)

                if not context.get("today"):
                    self.logger.info("  No transcripts found. Skipping generation.")
                    return True  # Not an error, just nothing to do

                self.logger.info(f"  Using transcripts from {yesterday}")

            self.logger.info(f"  Projects: {', '.join(context['projects_worked_on'])}")
            self.logger.info(f"  Sessions: {len(context['today'])}")

            # Step 3: Generate blog post
            self.logger.info("Step 3/4: Generating blog post...")
            result = self.generator.generate(context)

            if not result.success:
                self.logger.error(f"  Generation failed: {result.error}")
                return False

            self.logger.info(f"  Title: {result.title}")

            # Save the post
            filepath = self.generator.save_post(result)
            self.logger.info(f"  Saved to: {filepath}")

            # Step 4: Git commit and push
            if not skip_push:
                self.logger.info("Step 4/4: Pushing to GitHub...")
                push_success = self._git_push(result.title, filepath)
                if not push_success:
                    self.logger.warning("  Git push failed, but post was saved locally")
            else:
                self.logger.info("Step 4/4: Skipping Git push (--skip-push)")

            self.logger.info("Daily blog generation completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Error during blog generation: {e}", exc_info=True)
            return False

    def _git_push(self, title: str, filepath: Path) -> bool:
        """Commit and push changes to GitHub."""
        try:
            os.chdir(self.repo_dir)

            # Check if we're in a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.logger.warning("Not a git repository, skipping push")
                return False

            # Add the new post
            subprocess.run(['git', 'add', str(filepath)], check=True)

            # Also add updated project index
            index_file = self.scripts_dir / "data" / "project_index.json"
            if index_file.exists():
                subprocess.run(['git', 'add', str(index_file)], check=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'diff', '--cached', '--quiet'],
                capture_output=True
            )
            if result.returncode == 0:
                self.logger.info("  No changes to commit")
                return True

            # Commit
            commit_msg = f"Add blog post: {title}\n\nAutomatically generated by AutoBlog"
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                check=True
            )

            # Push
            subprocess.run(['git', 'push'], check=True)
            self.logger.info("  Successfully pushed to GitHub")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"  Git operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"  Unexpected error during git push: {e}")
            return False

    def sync_transcripts(self, days: int = 7) -> bool:
        """
        Sync recent transcripts to the repo's transcripts directory.

        Args:
            days: Number of days of transcripts to sync

        Returns:
            True if successful
        """
        import shutil

        transcripts_dir = self.repo_dir / "transcripts"
        transcripts_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Syncing transcripts from last {days} days...")

        source_dir = Path.home() / "transcript"
        if not source_dir.exists():
            self.logger.warning(f"Transcript directory not found: {source_dir}")
            return False

        # Calculate date threshold
        threshold = datetime.now() - timedelta(days=days)
        synced_count = 0

        for project_dir in source_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name.startswith('.'):
                continue

            for date_dir in project_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                try:
                    date = datetime.strptime(date_dir.name, '%Y-%m-%d')
                    if date < threshold:
                        continue
                except ValueError:
                    continue

                # Sync this date's transcripts
                for session_dir in date_dir.iterdir():
                    if not session_dir.is_dir():
                        continue

                    conversation = session_dir / "conversation.md"
                    if not conversation.exists():
                        continue

                    # Create destination path
                    dest_dir = transcripts_dir / date_dir.name
                    dest_dir.mkdir(parents=True, exist_ok=True)

                    dest_file = dest_dir / f"{project_dir.name}_{session_dir.name}.md"
                    shutil.copy2(conversation, dest_file)
                    synced_count += 1

        self.logger.info(f"  Synced {synced_count} transcript files")
        return True

    def get_status(self) -> dict:
        """Get the current status of the blog system."""
        stats = self.memory.get_stats()

        # Count posts
        posts = list(self.posts_dir.glob("*.md")) if self.posts_dir.exists() else []

        return {
            "projects_tracked": stats["total_projects"],
            "total_sessions": stats["total_sessions"],
            "last_index_update": stats["last_updated"],
            "posts_generated": len(posts),
            "repo_dir": str(self.repo_dir),
            "posts_dir": str(self.posts_dir)
        }


def main():
    """CLI entry point for daily blog generation."""
    parser = argparse.ArgumentParser(
        description="AutoBlog - Automated blog generation from Claude Code transcripts"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run daily blog generation")
    run_parser.add_argument("--date", help="Date to generate for (YYYY-MM-DD)")
    run_parser.add_argument("--skip-push", action="store_true",
                            help="Don't push to GitHub")
    run_parser.add_argument("--skip-summaries", action="store_true",
                            help="Skip Claude summary generation (faster)")
    run_parser.add_argument("--log-file", type=Path,
                            help="Log file path")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync transcripts to repo")
    sync_parser.add_argument("--days", type=int, default=7,
                             help="Days of transcripts to sync (default: 7)")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update project index only")
    update_parser.add_argument("--skip-summaries", action="store_true",
                               help="Skip Claude summary generation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    runner = DailyBlogRunner(
        log_file=getattr(args, 'log_file', None)
    )

    if args.command == "run":
        success = runner.run(
            date=args.date,
            skip_push=args.skip_push,
            skip_summaries=args.skip_summaries
        )
        sys.exit(0 if success else 1)

    elif args.command == "status":
        status = runner.get_status()
        print("AutoBlog Status")
        print("=" * 40)
        print(f"Projects tracked: {status['projects_tracked']}")
        print(f"Total sessions: {status['total_sessions']}")
        print(f"Last index update: {status['last_index_update']}")
        print(f"Posts generated: {status['posts_generated']}")
        print(f"Repository: {status['repo_dir']}")

    elif args.command == "sync":
        success = runner.sync_transcripts(days=args.days)
        sys.exit(0 if success else 1)

    elif args.command == "update":
        stats = runner.memory.update_index(
            use_claude_for_summaries=not args.skip_summaries
        )
        print(f"New sessions: {stats['new_sessions']}")
        print(f"New projects: {stats['new_projects']}")
        print(f"Updated projects: {stats['updated_projects']}")


if __name__ == "__main__":
    main()
