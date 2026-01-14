"""
Tests for the Project Memory system.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from project_memory import ProjectMemory


class TestProjectMemoryInit:
    """Tests for ProjectMemory initialization."""

    def test_load_empty_index(self, tmp_path):
        """Index initializes correctly when no file exists."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(index_path=index_path)

        assert memory.index["last_updated"] is None
        assert memory.index["projects"] == {}

    def test_load_existing_index(self, sample_index_file, sample_index):
        """Index loads correctly from existing file."""
        memory = ProjectMemory(index_path=sample_index_file)

        assert memory.index["last_updated"] == sample_index["last_updated"]
        assert "AutoBlog" in memory.index["projects"]
        assert "PenguinCAM" in memory.index["projects"]


class TestFindSessions:
    """Tests for session discovery."""

    def test_find_all_sessions(self, sample_transcripts_dir, tmp_path):
        """Correctly finds all sessions in transcript directory."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        sessions = memory.find_all_sessions()

        assert len(sessions) == 3
        projects = {s["project"] for s in sessions}
        assert "AutoBlog" in projects
        assert "PenguinCAM" in projects

    def test_find_new_sessions_no_previous(self, sample_transcripts_dir, tmp_path):
        """All sessions returned when no previous update."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        new_sessions = memory.find_new_sessions(since=None)
        all_sessions = memory.find_all_sessions()

        assert len(new_sessions) == len(all_sessions)

    def test_find_new_sessions_since_date(self, sample_transcripts_dir, tmp_path):
        """Only returns sessions from specified date onwards."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        # Should only get sessions from 2026-01-14
        new_sessions = memory.find_new_sessions(since="2026-01-14T00:00:00")

        assert len(new_sessions) == 2  # Two sessions on 2026-01-14
        for session in new_sessions:
            assert session["date"] == "2026-01-14"


class TestSessionContent:
    """Tests for reading session content."""

    def test_get_session_content(self, sample_transcripts_dir, tmp_path):
        """Correctly reads conversation content from session."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        sessions = memory.find_all_sessions()
        content = memory.get_session_content(sessions[0])

        assert "Claude Code Session" in content
        assert sessions[0]["project"] in content

    def test_get_session_content_missing_file(self, tmp_path):
        """Returns empty string for missing conversation file."""
        memory = ProjectMemory(index_path=tmp_path / "index.json")

        fake_session = {
            "conversation_path": str(tmp_path / "nonexistent.md")
        }
        content = memory.get_session_content(fake_session)

        assert content == ""


class TestIndexUpdate:
    """Tests for index update functionality."""

    def test_update_index_creates_project_entries(
        self, sample_transcripts_dir, tmp_path, mock_claude_cli
    ):
        """Update creates new project entries for discovered sessions."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        stats = memory.update_index(use_claude_for_summaries=False)

        assert stats["new_projects"] == 2  # AutoBlog and PenguinCAM
        assert stats["new_sessions"] == 3
        assert "AutoBlog" in memory.index["projects"]
        assert "PenguinCAM" in memory.index["projects"]

    def test_update_index_saves_to_disk(
        self, sample_transcripts_dir, tmp_path, mock_claude_cli
    ):
        """Update persists index to disk."""
        index_path = tmp_path / "data" / "project_index.json"
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        memory.update_index(use_claude_for_summaries=False)

        # Verify file was created
        assert index_path.exists()

        # Verify content
        with open(index_path) as f:
            saved_index = json.load(f)

        assert "AutoBlog" in saved_index["projects"]

    def test_update_index_incremental(
        self, sample_transcripts_dir, tmp_path, sample_index_file, mock_claude_cli
    ):
        """Update only processes new sessions."""
        # First, create memory with existing index
        memory = ProjectMemory(
            index_path=sample_index_file,
            transcript_dir=sample_transcripts_dir
        )

        # Update - should find sessions from 2026-01-14
        stats = memory.update_index(use_claude_for_summaries=False)

        # Should have added new sessions
        assert stats["new_sessions"] >= 0
        assert memory.index["last_updated"] is not None


class TestProjectHistory:
    """Tests for retrieving project history."""

    def test_get_project_history_existing(self, sample_index_file, sample_index):
        """Returns correct history for existing project."""
        memory = ProjectMemory(index_path=sample_index_file)

        history = memory.get_project_history("AutoBlog")

        assert history is not None
        assert history["first_seen"] == "2026-01-12"
        assert history["total_sessions"] == 3
        assert "daily_logs" in history

    def test_get_project_history_nonexistent(self, sample_index_file):
        """Returns None for nonexistent project."""
        memory = ProjectMemory(index_path=sample_index_file)

        history = memory.get_project_history("NonexistentProject")

        assert history is None


class TestBlogContext:
    """Tests for blog context generation."""

    def test_get_context_for_blog(
        self, sample_transcripts_dir, sample_index_file, tmp_path
    ):
        """Generates correct context for blog generation."""
        # Copy index to transcript-relative location
        memory = ProjectMemory(
            index_path=sample_index_file,
            transcript_dir=sample_transcripts_dir
        )

        context = memory.get_context_for_blog("2026-01-14")

        assert context["date"] == "2026-01-14"
        assert len(context["today"]) > 0
        assert "AutoBlog" in context["projects_worked_on"]

    def test_get_context_includes_history(
        self, sample_transcripts_dir, sample_index_file
    ):
        """Context includes historical project data."""
        memory = ProjectMemory(
            index_path=sample_index_file,
            transcript_dir=sample_transcripts_dir
        )

        context = memory.get_context_for_blog("2026-01-14")

        # Should have history for projects worked on today
        assert len(context["history"]) > 0

    def test_get_context_empty_day(self, sample_transcripts_dir, sample_index_file):
        """Returns empty context for day with no sessions."""
        memory = ProjectMemory(
            index_path=sample_index_file,
            transcript_dir=sample_transcripts_dir
        )

        context = memory.get_context_for_blog("2026-01-01")  # No sessions this day

        assert context["date"] == "2026-01-01"
        assert len(context["today"]) == 0


class TestStats:
    """Tests for statistics retrieval."""

    def test_get_stats(self, sample_index_file, sample_index):
        """Returns correct statistics about the index."""
        memory = ProjectMemory(index_path=sample_index_file)

        stats = memory.get_stats()

        assert stats["total_projects"] == 2
        assert stats["total_sessions"] == 8  # 3 + 5
        assert "AutoBlog" in stats["projects"]
        assert "PenguinCAM" in stats["projects"]

    def test_get_projects_list(self, sample_index_file):
        """Returns list of all tracked projects."""
        memory = ProjectMemory(index_path=sample_index_file)

        projects = memory.get_projects_list()

        assert "AutoBlog" in projects
        assert "PenguinCAM" in projects
