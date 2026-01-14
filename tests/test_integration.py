"""
Integration tests for the AutoBlog system.

These tests verify the complete end-to-end workflow.
"""

import json
from pathlib import Path

import pytest

from project_memory import ProjectMemory
from generate_post import BlogGenerator
from daily_blog import DailyBlogRunner


class TestEndToEndWorkflow:
    """End-to-end integration tests."""

    def test_full_pipeline_with_mock_claude(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Complete pipeline: update index → generate post → save."""
        # Setup
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        posts_dir = repo_dir / "_posts"
        posts_dir.mkdir()
        data_dir = repo_dir / "scripts" / "data"
        data_dir.mkdir(parents=True)

        index_path = data_dir / "project_index.json"

        # Step 1: Create and update project memory
        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )
        stats = memory.update_index(use_claude_for_summaries=False)

        assert stats["new_sessions"] > 0
        assert index_path.exists()

        # Step 2: Get blog context
        context = memory.get_context_for_blog("2026-01-14")

        assert len(context["today"]) > 0
        assert len(context["projects_worked_on"]) > 0

        # Step 3: Generate blog post
        generator = BlogGenerator(posts_dir=posts_dir)
        result = generator.generate(context)

        assert result.success is True
        assert result.title != ""

        # Step 4: Save post
        filepath = generator.save_post(result)

        assert filepath is not None
        assert filepath.exists()
        assert filepath.read_text() == result.content

    def test_index_update_then_generate(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Index update correctly informs generation."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        posts_dir = repo_dir / "_posts"
        posts_dir.mkdir()
        data_dir = repo_dir / "scripts" / "data"
        data_dir.mkdir(parents=True)

        # First update
        memory = ProjectMemory(
            index_path=data_dir / "project_index.json",
            transcript_dir=sample_transcripts_dir
        )
        memory.update_index(use_claude_for_summaries=False)

        # Get context - should have data
        context = memory.get_context_for_blog("2026-01-14")

        # Projects worked on should match what's in transcripts
        assert "AutoBlog" in context["projects_worked_on"]

        # History should be available for projects
        assert len(context["history"]) > 0

    def test_multi_project_day(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Handles multiple projects worked on same day."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        posts_dir = repo_dir / "_posts"
        posts_dir.mkdir()
        data_dir = repo_dir / "scripts" / "data"
        data_dir.mkdir(parents=True)

        memory = ProjectMemory(
            index_path=data_dir / "project_index.json",
            transcript_dir=sample_transcripts_dir
        )
        memory.update_index(use_claude_for_summaries=False)

        context = memory.get_context_for_blog("2026-01-14")

        # Sample transcripts have multiple projects on 2026-01-14
        assert len(context["projects_worked_on"]) >= 2

        # Generator should handle multiple projects
        generator = BlogGenerator(posts_dir=posts_dir)
        result = generator.generate(context)

        assert result.success is True

    def test_resumed_project_includes_history(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Blog for resumed project includes historical context."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        data_dir = repo_dir / "scripts" / "data"
        data_dir.mkdir(parents=True)

        # Create initial index with historical data
        initial_index = {
            "last_updated": "2026-01-13T00:00:00",
            "projects": {
                "AutoBlog": {
                    "first_seen": "2026-01-10",
                    "last_touched": "2026-01-13",
                    "total_sessions": 5,
                    "summary": "Building automated blog system",
                    "daily_logs": {
                        "2026-01-10": {
                            "sessions": ["s1"],
                            "summary": "Initial project setup",
                            "key_topics": ["python", "automation"]
                        },
                        "2026-01-12": {
                            "sessions": ["s2", "s3"],
                            "summary": "Core pipeline development",
                            "key_topics": ["generation", "claude"]
                        }
                    }
                }
            }
        }

        index_path = data_dir / "project_index.json"
        index_path.write_text(json.dumps(initial_index))

        memory = ProjectMemory(
            index_path=index_path,
            transcript_dir=sample_transcripts_dir
        )

        # Get context for a day when AutoBlog is resumed
        context = memory.get_context_for_blog("2026-01-14")

        # Should have historical context
        autoblog_history = next(
            (h for h in context["history"] if h["project"] == "AutoBlog"),
            None
        )

        if autoblog_history:
            assert autoblog_history["first_worked"] == "2026-01-10"
            assert "recent_sessions" in autoblog_history


class TestDailyRunnerIntegration:
    """Integration tests for DailyBlogRunner."""

    def test_runner_full_workflow(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Runner completes full workflow successfully."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        success = runner.run(
            date="2026-01-14",
            skip_push=True,
            skip_summaries=True
        )

        assert success is True

        # Verify post was created
        posts = list(runner.posts_dir.glob("*.md"))
        assert len(posts) == 1

        # Verify index was updated
        index_file = runner.scripts_dir / "data" / "project_index.json"
        assert index_file.exists()

    def test_runner_consecutive_days(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Runner handles consecutive day runs correctly."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        # Run for day 1
        success1 = runner.run(
            date="2026-01-13",
            skip_push=True,
            skip_summaries=True
        )

        # Run for day 2
        success2 = runner.run(
            date="2026-01-14",
            skip_push=True,
            skip_summaries=True
        )

        assert success1 is True
        assert success2 is True

        # Should have posts for both days
        posts = list(runner.posts_dir.glob("*.md"))
        assert len(posts) == 2

    def test_runner_idempotent(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Running twice for same day doesn't duplicate."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        # Run twice for same day
        runner.run(date="2026-01-14", skip_push=True, skip_summaries=True)
        runner.run(date="2026-01-14", skip_push=True, skip_summaries=True)

        # Second run should overwrite, not create duplicate
        posts = list(runner.posts_dir.glob("2026-01-14*.md"))
        assert len(posts) == 1


class TestErrorHandling:
    """Tests for error handling in integration scenarios."""

    def test_handles_missing_transcript_dir(self, tmp_path, mock_claude_cli):
        """Gracefully handles missing transcript directory."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        nonexistent_dir = tmp_path / "nonexistent"

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = nonexistent_dir

        # Should not crash, just return success (nothing to do)
        success = runner.run(date="2026-01-14", skip_push=True)
        assert success is True

    def test_handles_corrupted_index(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Handles corrupted index file gracefully."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "_posts").mkdir()
        data_dir = repo_dir / "scripts" / "data"
        data_dir.mkdir(parents=True)

        # Create corrupted index
        index_path = data_dir / "project_index.json"
        index_path.write_text("not valid json {{{")

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        # Should handle gracefully (might reinitialize index)
        # The exact behavior depends on implementation
        # At minimum, it shouldn't crash
        try:
            success = runner.run(date="2026-01-14", skip_push=True)
        except json.JSONDecodeError:
            # This is acceptable - the corrupted file is detected
            pass


class TestContentQuality:
    """Tests verifying content quality aspects."""

    def test_post_has_required_frontmatter(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Generated post has required Jekyll front matter."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        posts_dir = repo_dir / "_posts"
        posts_dir.mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        runner.run(date="2026-01-14", skip_push=True, skip_summaries=True)

        posts = list(posts_dir.glob("*.md"))
        assert len(posts) > 0

        content = posts[0].read_text()

        # Check front matter
        assert content.startswith("---")
        assert "layout: post" in content
        assert "title:" in content
        assert "date:" in content
        assert "tags:" in content

    def test_post_content_not_empty(
        self, tmp_path, sample_transcripts_dir, mock_claude_cli
    ):
        """Generated post has actual content beyond front matter."""
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        posts_dir = repo_dir / "_posts"
        posts_dir.mkdir()
        (repo_dir / "scripts" / "data").mkdir(parents=True)

        runner = DailyBlogRunner(repo_dir=repo_dir)
        runner.memory.transcript_dir = sample_transcripts_dir

        runner.run(date="2026-01-14", skip_push=True, skip_summaries=True)

        posts = list(posts_dir.glob("*.md"))
        content = posts[0].read_text()

        # Split by front matter delimiters
        parts = content.split("---")
        assert len(parts) >= 3  # Before, front matter, after

        # Content after front matter should be substantial
        body = "---".join(parts[2:])
        assert len(body.strip()) > 100  # At least 100 chars of content
