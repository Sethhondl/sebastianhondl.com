"""
Tests for the Blog Post Generator.
"""

import json
from pathlib import Path

import pytest

from generate_post import BlogGenerator, GenerationResult


class TestBlogGeneratorInit:
    """Tests for BlogGenerator initialization."""

    def test_creates_posts_directory(self, tmp_path):
        """Posts directory is created if it doesn't exist."""
        posts_dir = tmp_path / "_posts"
        generator = BlogGenerator(posts_dir=posts_dir)

        assert posts_dir.exists()

    def test_uses_existing_directory(self, temp_posts_dir):
        """Uses existing posts directory without error."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        assert generator.posts_dir == temp_posts_dir


class TestGeneration:
    """Tests for blog post generation."""

    def test_generate_success(self, mock_claude_cli, sample_context, temp_posts_dir):
        """Successfully generates a blog post through all passes."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        result = generator.generate(sample_context)

        assert result.success is True
        assert result.title != ""
        assert result.content != ""
        assert result.filename.endswith(".md")
        assert "draft" in result.passes
        assert "review" in result.passes
        assert "revised" in result.passes
        assert "final" in result.passes

    def test_generate_empty_transcripts(self, mock_claude_cli, temp_posts_dir):
        """Returns failure when no transcripts provided."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        context = {
            "date": "2026-01-14",
            "today": [],
            "history": [],
            "projects_worked_on": []
        }
        result = generator.generate(context)

        assert result.success is False
        assert "No transcripts" in result.error

    def test_generate_includes_all_passes(
        self, mock_claude_cli, sample_context, temp_posts_dir
    ):
        """All four passes are executed and stored."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        result = generator.generate(sample_context)

        assert "draft" in result.passes
        assert "review" in result.passes
        assert "revised" in result.passes
        assert "final" in result.passes

        # Each pass should have content
        for pass_name, content in result.passes.items():
            assert len(content) > 0, f"Pass '{pass_name}' is empty"


class TestTitleExtraction:
    """Tests for title extraction from content."""

    def test_extract_title_from_heading(self, temp_posts_dir):
        """Extracts title from markdown heading."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "# My Amazing Blog Post\n\nSome content here."
        title = generator._extract_title(content)

        assert title == "My Amazing Blog Post"

    def test_extract_title_with_whitespace(self, temp_posts_dir):
        """Handles extra whitespace in title."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "#   Spaced Out Title   \n\nContent"
        title = generator._extract_title(content)

        assert title == "Spaced Out Title"

    def test_extract_title_fallback(self, temp_posts_dir):
        """Returns fallback title when no heading found."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "No heading here, just content."
        title = generator._extract_title(content)

        assert "Daily Development Log" in title


class TestFilenameGeneration:
    """Tests for filename generation."""

    def test_generate_filename_basic(self, temp_posts_dir):
        """Generates correct Jekyll filename."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        filename = generator._generate_filename("2026-01-14", "My Blog Post")

        assert filename == "2026-01-14-my-blog-post.md"

    def test_generate_filename_special_chars(self, temp_posts_dir):
        """Handles special characters in title."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        filename = generator._generate_filename(
            "2026-01-14",
            "Building AI-Powered Apps: A Guide!"
        )

        assert filename == "2026-01-14-building-ai-powered-apps-a-guide.md"
        assert "!" not in filename
        assert ":" not in filename

    def test_generate_filename_long_title(self, temp_posts_dir):
        """Truncates very long titles."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        long_title = "This is a very long title that goes on and on and on " * 5
        filename = generator._generate_filename("2026-01-14", long_title)

        # Should be truncated to 50 chars for slug
        slug_part = filename.replace("2026-01-14-", "").replace(".md", "")
        assert len(slug_part) <= 50

    def test_generate_filename_default_date(self, temp_posts_dir):
        """Uses today's date when none provided."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        filename = generator._generate_filename(None, "Test Post")

        # Should start with a date
        assert filename[0:4].isdigit()  # Year
        assert filename[4] == "-"


class TestJekyllFormatting:
    """Tests for Jekyll post formatting."""

    def test_format_jekyll_frontmatter(self, temp_posts_dir):
        """Correctly formats Jekyll front matter."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "# Test Post\n\nSome content here."
        formatted = generator._format_jekyll_post(content, "2026-01-14", "Test Post")

        assert formatted.startswith("---")
        assert "layout: post" in formatted
        assert 'title: "Test Post"' in formatted
        assert "date: 2026-01-14" in formatted
        assert "---" in formatted[4:]  # Closing front matter

    def test_format_removes_duplicate_title(self, temp_posts_dir):
        """Removes title heading when it matches front matter title."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "# My Post Title\n\nThe actual content."
        formatted = generator._format_jekyll_post(
            content, "2026-01-14", "My Post Title"
        )

        # Title should not appear twice (once in front matter, once in content)
        title_count = formatted.count("My Post Title")
        assert title_count == 1  # Only in front matter

    def test_format_includes_tags(self, temp_posts_dir):
        """Includes extracted tags in front matter."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "# Test\n\nWorking with Claude Code and Python automation."
        formatted = generator._format_jekyll_post(content, "2026-01-14", "Test")

        assert "tags:" in formatted
        assert "claude-code" in formatted

    def test_format_includes_read_time(self, temp_posts_dir):
        """Includes read time in front matter."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "# Test\n\n" + ("word " * 400)  # ~400 words = 2 min read
        formatted = generator._format_jekyll_post(content, "2026-01-14", "Test")

        assert "read_time:" in formatted


class TestTagExtraction:
    """Tests for tag extraction from content."""

    def test_extract_tags_claude(self, temp_posts_dir):
        """Extracts claude-code tag from relevant content."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "Working with Claude Code today on automation."
        tags = generator._extract_tags(content)

        assert "claude-code" in tags

    def test_extract_tags_multiple(self, temp_posts_dir):
        """Extracts multiple relevant tags."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "Using Python and Git to automate testing with pytest."
        tags = generator._extract_tags(content)

        assert "python" in tags
        assert "git" in tags
        assert "testing" in tags

    def test_extract_tags_limits_count(self, temp_posts_dir):
        """Limits tags to 5 maximum."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        # Content with many potential tags
        content = """
        Claude Code helped with Python, JavaScript, Git, automation,
        testing, API development, debugging, refactoring, and more.
        """
        tags = generator._extract_tags(content)

        assert len(tags) <= 5

    def test_extract_tags_always_includes_claude(self, temp_posts_dir):
        """Always includes claude-code tag even if not in content."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        content = "Just some random content about programming."
        tags = generator._extract_tags(content)

        assert "claude-code" in tags


class TestSavePost:
    """Tests for saving posts to disk."""

    def test_save_post_creates_file(
        self, mock_claude_cli, sample_context, temp_posts_dir
    ):
        """Successfully saves generated post to disk."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        result = generator.generate(sample_context)
        filepath = generator.save_post(result)

        assert filepath is not None
        assert filepath.exists()
        assert filepath.suffix == ".md"

    def test_save_post_content_matches(
        self, mock_claude_cli, sample_context, temp_posts_dir
    ):
        """Saved file content matches result content."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        result = generator.generate(sample_context)
        filepath = generator.save_post(result)

        saved_content = filepath.read_text()
        assert saved_content == result.content

    def test_save_post_failed_result(self, temp_posts_dir):
        """Returns None when trying to save failed result."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        result = GenerationResult(
            success=False,
            title="",
            content="",
            filename="",
            passes={},
            error="Test error"
        )
        filepath = generator.save_post(result)

        assert filepath is None


class TestTranscriptFormatting:
    """Tests for transcript formatting."""

    def test_format_transcripts_basic(self, temp_posts_dir):
        """Correctly formats transcripts for prompt."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        transcripts = [
            {"project": "TestProject", "content": "Session content here."}
        ]
        formatted = generator._format_transcripts(transcripts)

        assert "TestProject" in formatted
        assert "Session content here" in formatted

    def test_format_transcripts_multiple(self, temp_posts_dir):
        """Formats multiple transcripts with separators."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        transcripts = [
            {"project": "Project1", "content": "Content 1"},
            {"project": "Project2", "content": "Content 2"},
        ]
        formatted = generator._format_transcripts(transcripts)

        assert "Project1" in formatted
        assert "Project2" in formatted
        assert "---" in formatted  # Separator

    def test_format_transcripts_empty(self, temp_posts_dir):
        """Returns empty string for empty transcripts."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        formatted = generator._format_transcripts([])

        assert formatted == ""

    def test_format_transcripts_truncates_long(self, temp_posts_dir):
        """Truncates very long transcript content."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        long_content = "x" * 10000
        transcripts = [{"project": "Test", "content": long_content}]
        formatted = generator._format_transcripts(transcripts)

        assert "truncated" in formatted.lower()


class TestHistoryFormatting:
    """Tests for history formatting."""

    def test_format_history_basic(self, temp_posts_dir):
        """Correctly formats project history."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        history = [
            {
                "project": "TestProject",
                "first_worked": "2026-01-10",
                "total_sessions": 5,
                "summary": "Test project summary",
                "recent_sessions": {}
            }
        ]
        formatted = generator._format_history(history)

        assert "TestProject" in formatted
        assert "2026-01-10" in formatted
        assert "5" in formatted

    def test_format_history_empty(self, temp_posts_dir):
        """Returns appropriate message for empty history."""
        generator = BlogGenerator(posts_dir=temp_posts_dir)

        formatted = generator._format_history([])

        assert "No previous work" in formatted
