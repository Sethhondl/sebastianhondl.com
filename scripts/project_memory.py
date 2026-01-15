#!/usr/bin/env python3
"""
Project Memory System for AutoBlog

Maintains a persistent index of all projects worked on with Claude Code,
enabling cross-day context for blog generation.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


# Default paths
TRANSCRIPT_DIR = Path.home() / "transcript"
REPO_TRANSCRIPT_DIR = Path(__file__).parent.parent / "transcripts"
DEFAULT_INDEX_PATH = Path(__file__).parent / "data" / "project_index.json"


def get_transcript_dir() -> Path:
    """
    Get the transcript directory, preferring local ~/transcript if available,
    falling back to repo transcripts/ for GitHub Actions.
    """
    if TRANSCRIPT_DIR.exists() and any(TRANSCRIPT_DIR.iterdir()):
        return TRANSCRIPT_DIR
    return REPO_TRANSCRIPT_DIR


class ProjectMemory:
    """Manages the project memory index for cross-day context."""

    def __init__(self, index_path: Optional[Path] = None, transcript_dir: Optional[Path] = None):
        self.index_path = index_path or DEFAULT_INDEX_PATH
        self.transcript_dir = transcript_dir or get_transcript_dir()
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load the project index from disk, or create empty if doesn't exist."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Corrupted or unreadable file - start fresh
                pass
        return {
            "last_updated": None,
            "projects": {}
        }

    def _save_index(self) -> None:
        """Save the project index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2, default=str)

    def find_all_sessions(self) -> List[Dict[str, Any]]:
        """Find all transcript sessions in the transcript directory."""
        sessions = []

        if not self.transcript_dir.exists():
            return sessions

        # Check if this is the local structure or repo structure
        # Local: ~/transcript/[project]/[date]/[session_id]/conversation.md
        # Repo:  transcripts/[date]/[project]_[session_id].md

        first_level_items = list(self.transcript_dir.iterdir())
        if not first_level_items:
            return sessions

        # Detect structure by checking if first-level dirs are dates or projects
        sample_dir = next((d for d in first_level_items if d.is_dir() and not d.name.startswith('.')), None)
        if sample_dir is None:
            return sessions

        is_repo_structure = self._is_date_format(sample_dir.name)

        if is_repo_structure:
            sessions = self._find_sessions_repo_structure()
        else:
            sessions = self._find_sessions_local_structure()

        return sessions

    def _is_date_format(self, name: str) -> bool:
        """Check if a directory name is in YYYY-MM-DD format."""
        try:
            datetime.strptime(name, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _find_sessions_repo_structure(self) -> List[Dict[str, Any]]:
        """Find sessions in repo structure: transcripts/[date]/[project]_[session_id].md"""
        sessions = []

        for date_dir in self.transcript_dir.iterdir():
            if not date_dir.is_dir() or date_dir.name.startswith('.'):
                continue

            if not self._is_date_format(date_dir.name):
                continue

            date_str = date_dir.name

            for transcript_file in date_dir.iterdir():
                if not transcript_file.is_file() or not transcript_file.name.endswith('.md'):
                    continue

                # Parse filename: [project]_[session_id].md
                filename = transcript_file.stem
                parts = filename.rsplit('_', 1)

                if len(parts) == 2:
                    project_name, session_id = parts
                else:
                    project_name = filename
                    session_id = filename

                session_info = {
                    "project": project_name,
                    "date": date_str,
                    "session_id": session_id,
                    "path": str(date_dir),
                    "conversation_path": str(transcript_file),
                    "has_metadata": False
                }
                sessions.append(session_info)

        return sessions

    def _find_sessions_local_structure(self) -> List[Dict[str, Any]]:
        """Find sessions in local structure: ~/transcript/[project]/[date]/[session_id]/"""
        sessions = []

        for project_dir in self.transcript_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name.startswith('.'):
                continue

            project_name = project_dir.name

            for date_dir in project_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                # Validate date format (YYYY-MM-DD)
                if not self._is_date_format(date_dir.name):
                    continue

                date_str = date_dir.name

                for session_dir in date_dir.iterdir():
                    if not session_dir.is_dir():
                        continue

                    session_id = session_dir.name
                    conversation_file = session_dir / "conversation.md"
                    metadata_file = session_dir / "metadata.json"

                    if conversation_file.exists():
                        session_info = {
                            "project": project_name,
                            "date": date_str,
                            "session_id": session_id,
                            "path": str(session_dir),
                            "conversation_path": str(conversation_file),
                            "has_metadata": metadata_file.exists()
                        }

                        # Load metadata if available
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    session_info["metadata"] = json.load(f)
                            except json.JSONDecodeError:
                                pass

                        sessions.append(session_info)

        return sessions

    def find_new_sessions(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find sessions added since the last update."""
        all_sessions = self.find_all_sessions()

        if since is None:
            return all_sessions

        since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
        new_sessions = []

        for session in all_sessions:
            # Check if session is from a date on or after 'since'
            session_date = datetime.strptime(session["date"], '%Y-%m-%d')
            if session_date.date() >= since_date.date():
                new_sessions.append(session)

        return new_sessions

    def get_session_content(self, session: Dict[str, Any]) -> str:
        """Read the conversation content from a session."""
        conversation_path = Path(session["conversation_path"])
        if conversation_path.exists():
            return conversation_path.read_text()
        return ""

    def update_index(self, use_claude_for_summaries: bool = True) -> Dict[str, int]:
        """
        Update the project index with new sessions.

        Returns stats about what was updated.
        """
        stats = {
            "new_sessions": 0,
            "new_projects": 0,
            "updated_projects": 0
        }

        # Get sessions since last update
        since = self.index.get("last_updated")
        new_sessions = self.find_new_sessions(since)

        for session in new_sessions:
            project = session["project"]
            date = session["date"]
            session_id = session["session_id"]

            # Create project entry if new
            if project not in self.index["projects"]:
                self.index["projects"][project] = {
                    "first_seen": date,
                    "last_touched": date,
                    "total_sessions": 0,
                    "summary": "",
                    "daily_logs": {}
                }
                stats["new_projects"] += 1

            project_data = self.index["projects"][project]

            # Update last_touched
            if date > project_data["last_touched"]:
                project_data["last_touched"] = date

            # Initialize daily log if needed
            if date not in project_data["daily_logs"]:
                project_data["daily_logs"][date] = {
                    "sessions": [],
                    "summary": "",
                    "key_topics": []
                }

            daily_log = project_data["daily_logs"][date]

            # Add session if not already tracked
            if session_id not in daily_log["sessions"]:
                daily_log["sessions"].append(session_id)
                project_data["total_sessions"] += 1
                stats["new_sessions"] += 1
                stats["updated_projects"] += 1

        # Generate summaries for updated projects
        if use_claude_for_summaries and stats["new_sessions"] > 0:
            self._update_summaries(new_sessions)

        # Update timestamp
        self.index["last_updated"] = datetime.now().isoformat()

        # Save index
        self._save_index()

        return stats

    def _update_summaries(self, sessions: List[Dict[str, Any]]) -> None:
        """Update summaries for projects with new sessions using Claude."""
        # Group sessions by project and date
        project_dates = {}
        for session in sessions:
            key = (session["project"], session["date"])
            if key not in project_dates:
                project_dates[key] = []
            project_dates[key].append(session)

        for (project, date), date_sessions in project_dates.items():
            # Read conversation content
            content_snippets = []
            for session in date_sessions[:3]:  # Limit to 3 sessions for summary
                content = self.get_session_content(session)
                # Take first 2000 chars of each session
                if content:
                    content_snippets.append(content[:2000])

            if not content_snippets:
                continue

            # Generate summary using Claude CLI
            combined_content = "\n\n---\n\n".join(content_snippets)
            summary = self._generate_summary(project, date, combined_content)

            if summary and project in self.index["projects"]:
                daily_log = self.index["projects"][project]["daily_logs"].get(date, {})
                daily_log["summary"] = summary.get("summary", "")
                daily_log["key_topics"] = summary.get("key_topics", [])

                # Update overall project summary
                self.index["projects"][project]["summary"] = self._generate_project_summary(project)

    def _generate_summary(self, project: str, date: str, content: str) -> Optional[Dict[str, Any]]:
        """Generate a summary of the day's work using Claude CLI."""
        prompt = f"""Summarize this Claude Code session for the project "{project}" on {date}.

Provide a JSON response with:
- "summary": A 1-2 sentence summary of what was done
- "key_topics": A list of 3-5 key topics/technologies discussed

Session content:
{content[:4000]}

Respond with only valid JSON, no other text."""

        try:
            result = subprocess.run(
                ['claude', '--print', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                # Try to parse JSON from response
                response = result.stdout.strip()
                # Find JSON in response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            pass

        return None

    def _generate_project_summary(self, project: str) -> str:
        """Generate an overall summary for a project based on daily logs."""
        if project not in self.index["projects"]:
            return ""

        project_data = self.index["projects"][project]
        daily_summaries = []

        for date, log in sorted(project_data["daily_logs"].items())[-5:]:
            if log.get("summary"):
                daily_summaries.append(f"- {date}: {log['summary']}")

        if not daily_summaries:
            return f"Project worked on {project_data['total_sessions']} times"

        return "\n".join(daily_summaries)

    def get_project_history(self, project: str) -> Optional[Dict[str, Any]]:
        """Get the full history for a specific project."""
        return self.index["projects"].get(project)

    def get_context_for_blog(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get context for blog generation including today's transcripts and historical context.

        Args:
            date: Date to generate context for (defaults to today)

        Returns:
            Dictionary with 'today' (list of sessions) and 'history' (project summaries)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Get today's sessions
        all_sessions = self.find_all_sessions()
        today_sessions = [s for s in all_sessions if s["date"] == date]

        # Get today's transcript content
        today_transcripts = []
        for session in today_sessions:
            content = self.get_session_content(session)
            if content:
                today_transcripts.append({
                    "project": session["project"],
                    "session_id": session["session_id"],
                    "content": content
                })

        # Get historical context for each project worked on today
        projects_today = set(s["project"] for s in today_sessions)
        historical_context = []

        for project in projects_today:
            history = self.get_project_history(project)
            if history:
                # Get recent daily logs (excluding today)
                recent_logs = {}
                for log_date, log in sorted(history["daily_logs"].items()):
                    if log_date < date:
                        recent_logs[log_date] = log

                # Take last 5 days
                recent_logs = dict(list(recent_logs.items())[-5:])

                historical_context.append({
                    "project": project,
                    "first_worked": history["first_seen"],
                    "total_sessions": history["total_sessions"],
                    "summary": history["summary"],
                    "recent_sessions": recent_logs
                })

        return {
            "date": date,
            "today": today_transcripts,
            "history": historical_context,
            "projects_worked_on": list(projects_today)
        }

    def get_projects_list(self) -> List[str]:
        """Get a list of all tracked projects."""
        return list(self.index["projects"].keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the project index."""
        total_sessions = sum(
            p["total_sessions"] for p in self.index["projects"].values()
        )

        return {
            "total_projects": len(self.index["projects"]),
            "total_sessions": total_sessions,
            "last_updated": self.index["last_updated"],
            "projects": list(self.index["projects"].keys())
        }


def main():
    """CLI interface for project memory management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage AutoBlog project memory")
    parser.add_argument("command", choices=["update", "stats", "context", "history"],
                        help="Command to run")
    parser.add_argument("--project", help="Project name (for history command)")
    parser.add_argument("--date", help="Date for context (YYYY-MM-DD)")
    parser.add_argument("--no-summaries", action="store_true",
                        help="Skip Claude summary generation")

    args = parser.parse_args()

    memory = ProjectMemory()

    if args.command == "update":
        print("Updating project index...")
        stats = memory.update_index(use_claude_for_summaries=not args.no_summaries)
        print(f"Found {stats['new_sessions']} new sessions")
        print(f"New projects: {stats['new_projects']}")
        print(f"Updated projects: {stats['updated_projects']}")

    elif args.command == "stats":
        stats = memory.get_stats()
        print(f"Total projects: {stats['total_projects']}")
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Last updated: {stats['last_updated']}")
        print(f"Projects: {', '.join(stats['projects'])}")

    elif args.command == "context":
        context = memory.get_context_for_blog(args.date)
        print(f"Date: {context['date']}")
        print(f"Projects worked on: {', '.join(context['projects_worked_on'])}")
        print(f"Today's sessions: {len(context['today'])}")
        print(f"Historical context for {len(context['history'])} projects")

    elif args.command == "history":
        if not args.project:
            print("Error: --project required for history command")
            return
        history = memory.get_project_history(args.project)
        if history:
            print(json.dumps(history, indent=2))
        else:
            print(f"No history found for project: {args.project}")


if __name__ == "__main__":
    main()
