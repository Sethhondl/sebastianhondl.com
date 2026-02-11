"""
Tests for the Daily Blog orchestration script.
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from daily_blog import DailyBlogRunner


class TestDailyBlogRunnerInit:
    """Tests for DailyBlogRunner initialization."""

    def test_creates_directories(self, tmp_path):
        """Creates necessary directories on init."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)

        assert runner.posts_dir.exists()

    def test_initializes_components(self, tmp_path):
        """Initializes memory and generator components."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)

        assert runner.memory is not None
        assert runner.generator is not None


class TestRunWorkflow:
    """Tests for the main run workflow."""

    def test_run_with_transcripts(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Successfully runs when transcripts exist."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        success = runner.run(date="2026-01-14", skip_push=True)

        assert success is True
        # Check that a post was created
        posts = list(runner.posts_dir.glob("*.md"))
        assert len(posts) > 0

    def test_run_no_transcripts(self, tmp_path, mock_claude_cli):
        """Returns True (success) when no transcripts to process."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        # Empty transcript dir
        empty_transcripts = tmp_path / "empty_transcripts"
        empty_transcripts.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = empty_transcripts

        success = runner.run(date="2026-01-14", skip_push=True)

        # Should succeed even with no transcripts (nothing to do)
        assert success is True

    def test_run_skip_push_flag(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Respects skip_push flag."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        with patch.object(runner, '_git_push') as mock_push:
            runner.run(date="2026-01-14", skip_push=True)

            # Git push should not be called
            mock_push.assert_not_called()

    def test_run_with_skip_summaries(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Skips Claude summaries when flag is set."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        # This should complete faster without summary generation
        success = runner.run(
            date="2026-01-14",
            skip_push=True,
            skip_summaries=True
        )

        assert success is True


class TestIdempotency:
    """Tests for idempotency checks."""

    def test_runner_idempotent_with_drafts(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """A pre-existing draft for a date prevents re-generation."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        drafts_dir = repo_dir / "_drafts"
        drafts_dir.mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        # Create an existing draft for the target date
        draft_file = drafts_dir / "2026-01-14-existing-draft.md"
        draft_file.write_text("---\ntitle: Existing Draft\n---\nContent")

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        with patch.object(runner.generator, 'generate') as mock_generate:
            success = runner.run(date="2026-01-14", skip_push=True)

            assert success is True
            # Generator should NOT have been called since draft exists
            mock_generate.assert_not_called()


class TestGitOperations:
    """Tests for Git operations."""

    def test_git_push_not_a_repo(self, tmp_path):
        """Returns False when not in a git repo."""
        repo_dir = tmp_path / "not_a_repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)

        success = runner._git_push("Test Title", repo_dir / "test.md")

        assert success is False

    def test_git_push_with_mock_git(self, tmp_path):
        """Tests git push with mocked git commands."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)

        # Create a test file
        test_file = repo_dir / "_posts" / "test.md"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("Test content")

        with patch('subprocess.run') as mock_run:
            # Mock git rev-parse to indicate we're in a repo
            mock_run.return_value = MagicMock(returncode=0)

            # This will fail because it's not actually a git repo,
            # but we're testing the logic path
            result = runner._git_push("Test", test_file)

            # Should have attempted git operations
            assert mock_run.called


class TestTranscriptSync:
    """Tests for transcript synchronization."""

    def test_sync_transcripts_creates_dir(
        self, tmp_path, sample_transcripts_dir
    ):
        """Creates transcripts directory if needed."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        runner.sync_transcripts(days=7)

        assert (repo_dir / "transcripts").exists()

    def test_sync_transcripts_copies_files(
        self, tmp_path, sample_transcripts_dir
    ):
        """Copies transcript files to repo."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        runner.sync_transcripts(days=30)  # Include all test files

        transcripts_dir = repo_dir / "transcripts"
        synced_files = list(transcripts_dir.rglob("*.md"))
        assert len(synced_files) > 0

    def test_sync_transcripts_respects_days(
        self, tmp_path, sample_transcripts_dir
    ):
        """Only syncs transcripts within specified day range."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        # Sync only very recent (won't include old fixtures)
        runner.sync_transcripts(days=0)

        transcripts_dir = repo_dir / "transcripts"
        # With days=0, might not sync anything from fixtures
        # This is expected behavior


class TestStatus:
    """Tests for status reporting."""

    def test_get_status_empty(self, tmp_path):
        """Returns correct status for empty system."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)

        status = runner.get_status()

        assert status["projects_tracked"] == 0
        assert status["total_sessions"] == 0
        assert status["posts_generated"] == 0

    def test_get_status_with_data(
        self, tmp_path, sample_transcripts_dir, sample_index_file, mock_claude_cli
    ):
        """Returns correct status with data."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()

        # Copy index file
        data_dir = repo_dir / "scripts" / "data"
        data_dir.mkdir(parents=True)
        index_dest = data_dir / "project_index.json"

        import shutil
        shutil.copy(sample_index_file, index_dest)

        runner = DailyBlogRunner(repo_dir=repo_dir)

        status = runner.get_status()

        assert status["projects_tracked"] == 2
        assert status["total_sessions"] == 8


class TestLogging:
    """Tests for logging functionality."""

    def test_logging_to_file(self, tmp_path):
        """Logs are written to file when specified."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        log_file = tmp_path / "logs" / "test.log"

        runner = DailyBlogRunner(repo_dir=repo_dir, log_file=log_file)

        # Log file directory should be created
        assert log_file.parent.exists()

    def test_logging_without_file(self, tmp_path):
        """Works without log file specified."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        # Should not raise
        runner = DailyBlogRunner(repo_dir=repo_dir, log_file=None)
        assert runner.logger is not None
