"""
Pytest configuration and fixtures for AutoBlog tests.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@dataclass
class MockCompletedProcess:
    """Mock subprocess.CompletedProcess for testing Claude CLI calls."""
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


# Sample Claude CLI responses for different passes
MOCK_RESPONSES = {
    "draft": """# Building an Automated Blog System

Today I worked on creating an automated blogging system that captures my Claude Code sessions and turns them into daily blog posts.

## The Challenge

I wanted a way to document my AI-assisted development journey without the manual effort of writing blog posts every day.

## The Solution

The system works in several phases:
1. Capture transcripts from Claude Code sessions
2. Maintain a project memory index across days
3. Generate polished blog posts using a multi-pass pipeline
4. Automatically publish to GitHub Pages

## Key Learnings

Working with Claude Code, I discovered that breaking down complex tasks into smaller, well-defined steps leads to better results. The AI excels at implementation when given clear context and constraints.

## Next Steps

Tomorrow I'll focus on testing the system and setting up the scheduling automation.
""",

    "review": """Here are my suggestions for improving this blog post:

1. **Add a more engaging hook**: The opening could be more compelling to draw readers in.

2. **Include code examples**: The post mentions technical implementation but doesn't show any code snippets.

3. **Expand on 'Key Learnings'**: This section feels brief - could benefit from more specific examples.

4. **Add transition sentences**: The flow between sections could be smoother.

5. **Clarify the audience**: Make it clearer who this post is for (developers? AI enthusiasts?).

6. **Strengthen the conclusion**: The 'Next Steps' section could tie back to the main theme better.
""",

    "revised": """# Building an Automated Blog System: My Journey into AI-Powered Content

Have you ever wished you could document your coding journey without the overhead of writing blog posts? Today, I built a system that does exactly that.

## The Challenge

As a developer who codes daily with Claude Code, I generate hours of valuable conversation transcripts. But these insights were going to waste - I simply didn't have time to manually write blog posts about my experiences.

## The Solution

I created an automated pipeline that transforms my Claude Code sessions into polished blog posts:

```python
# The core generation pipeline
def generate_blog_post(context):
    draft = claude_cli(DRAFT_PROMPT.format(transcripts=context))
    review = claude_cli(REVIEW_PROMPT.format(draft=draft))
    revised = claude_cli(REVISE_PROMPT.format(draft=draft, feedback=review))
    return claude_cli(POLISH_PROMPT.format(post=revised))
```

The system maintains a "project memory" that tracks work across multiple days, so when I return to a project, the blog can provide context about previous sessions.

## Key Learnings

Working with Claude Code taught me several valuable lessons:

1. **Context is king**: The more context you provide, the better the AI's output. My project memory system ensures Claude always has relevant history.

2. **Iteration improves quality**: The 4-pass generation pipeline (draft → review → revise → polish) produces noticeably better content than single-pass generation.

3. **Automation requires good architecture**: Spending time on a clean, modular design pays dividends when debugging and extending the system.

## Looking Forward

This blog itself is proof that the system works. Every post you read here is generated automatically from real Claude Code sessions - it's AI writing about AI-assisted development.

What automation challenges are you tackling? I'd love to hear about them.
""",

    "final": """# Building an Automated Blog System: My Journey into AI-Powered Content

Have you ever wished you could document your coding journey without the overhead of writing blog posts? Today, I built a system that does exactly that - and you're reading the result.

## The Challenge

As a developer who codes daily with Claude Code, I generate hours of valuable conversation transcripts. These sessions contain insights, solutions, and learnings that could help other developers. But the insights were going to waste - I simply didn't have time to manually distill them into blog posts.

## The Solution

I created an automated pipeline that transforms my Claude Code sessions into polished blog posts:

```python
# The core generation pipeline
def generate_blog_post(context):
    draft = claude_cli(DRAFT_PROMPT.format(transcripts=context))
    review = claude_cli(REVIEW_PROMPT.format(draft=draft))
    revised = claude_cli(REVISE_PROMPT.format(draft=draft, feedback=review))
    return claude_cli(POLISH_PROMPT.format(post=revised))
```

The system maintains a "project memory" that tracks work across multiple days. When I return to a project after a break, the blog generation has full context about what I did previously - enabling more coherent storytelling.

## Key Learnings

Building this system with Claude Code taught me several valuable lessons:

1. **Context is king**: The more context you provide, the better the AI's output. My project memory system ensures Claude always has relevant history when generating posts.

2. **Iteration dramatically improves quality**: The 4-pass generation pipeline (draft → review → revise → polish) produces noticeably better content than single-pass generation. The self-review step catches issues I wouldn't have thought to address.

3. **Automation requires good architecture**: Spending time on a clean, modular design pays dividends when debugging and extending the system later.

## What's Next

This blog itself is proof that the system works. Every post you read here is generated automatically from real Claude Code sessions - it's AI writing about AI-assisted development, and I think that's pretty cool.

What automation challenges are you tackling in your own workflow? I'd love to hear about them.
"""
}


@pytest.fixture
def mock_claude_cli(monkeypatch):
    """Mock the Claude CLI subprocess calls."""

    def mock_run(cmd, *args, **kwargs):
        # Extract the prompt from the command
        prompt = ""
        if isinstance(cmd, list) and '-p' in cmd:
            idx = cmd.index('-p')
            if idx + 1 < len(cmd):
                prompt = cmd[idx + 1].lower()

        # Determine which response to return based on prompt content
        if 'draft' in prompt or 'transcripts' in prompt:
            return MockCompletedProcess(stdout=MOCK_RESPONSES["draft"])
        elif 'review' in prompt or 'critique' in prompt:
            return MockCompletedProcess(stdout=MOCK_RESPONSES["review"])
        elif 'revise' in prompt or 'feedback' in prompt:
            return MockCompletedProcess(stdout=MOCK_RESPONSES["revised"])
        elif 'polish' in prompt or 'final' in prompt:
            return MockCompletedProcess(stdout=MOCK_RESPONSES["final"])
        else:
            # Default response for summaries, etc.
            return MockCompletedProcess(stdout=json.dumps({
                "summary": "Test summary of the session",
                "key_topics": ["python", "automation", "testing"]
            }))

    monkeypatch.setattr(subprocess, "run", mock_run)
    return mock_run


@pytest.fixture
def fixtures_dir():
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_transcripts_dir(fixtures_dir, tmp_path):
    """Create a temporary directory with sample transcripts."""
    transcripts_dir = tmp_path / "transcript"

    # Create sample transcript structure
    projects = [
        ("AutoBlog", "2026-01-14", "session_abc123"),
        ("AutoBlog", "2026-01-13", "session_def456"),
        ("PenguinCAM", "2026-01-14", "session_ghi789"),
    ]

    for project, date, session_id in projects:
        session_dir = transcripts_dir / project / date / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create conversation.md
        conversation = session_dir / "conversation.md"
        conversation.write_text(f"""# Claude Code Session
**Project**: {project}
**Date**: {date}
**Session ID**: {session_id}

## Conversation

**User**: Help me with {project}

**Assistant**: I'll help you with {project}. Let me analyze the requirements...

## Statistics
- Messages: 10
- Tools used: Read, Edit, Write
- Duration: 30 minutes
""")

        # Create metadata.json
        metadata = session_dir / "metadata.json"
        metadata.write_text(json.dumps({
            "project": project,
            "date": date,
            "session_id": session_id,
            "start_time": f"{date}T10:00:00",
            "end_time": f"{date}T10:30:00"
        }))

    return transcripts_dir


@pytest.fixture
def sample_index():
    """Return a sample project index for testing."""
    return {
        "last_updated": "2026-01-13T23:00:00",
        "projects": {
            "AutoBlog": {
                "first_seen": "2026-01-12",
                "last_touched": "2026-01-13",
                "total_sessions": 3,
                "summary": "Automated blogging system for Claude Code sessions",
                "daily_logs": {
                    "2026-01-12": {
                        "sessions": ["session_001"],
                        "summary": "Initial project setup and planning",
                        "key_topics": ["python", "automation"]
                    },
                    "2026-01-13": {
                        "sessions": ["session_002", "session_003"],
                        "summary": "Implemented core generation pipeline",
                        "key_topics": ["claude-cli", "subprocess"]
                    }
                }
            },
            "PenguinCAM": {
                "first_seen": "2026-01-10",
                "last_touched": "2026-01-12",
                "total_sessions": 5,
                "summary": "Computer vision project for penguin monitoring",
                "daily_logs": {
                    "2026-01-10": {
                        "sessions": ["session_a1"],
                        "summary": "Camera setup and initial calibration",
                        "key_topics": ["opencv", "camera"]
                    }
                }
            }
        }
    }


@pytest.fixture
def sample_index_file(tmp_path, sample_index):
    """Create a sample index file for testing."""
    index_path = tmp_path / "data" / "project_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(sample_index, indent=2))
    return index_path


@pytest.fixture
def sample_context():
    """Return sample blog generation context."""
    return {
        "date": "2026-01-14",
        "today": [
            {
                "project": "AutoBlog",
                "session_id": "session_abc123",
                "content": """# Claude Code Session
**Project**: AutoBlog
**Date**: 2026-01-14

## Conversation

**User**: Help me create the test suite for AutoBlog

**Assistant**: I'll help you create a comprehensive test suite. Let me start with the fixtures...
"""
            }
        ],
        "history": [
            {
                "project": "AutoBlog",
                "first_worked": "2026-01-12",
                "total_sessions": 3,
                "summary": "Automated blogging system",
                "recent_sessions": {
                    "2026-01-13": {
                        "summary": "Implemented generation pipeline",
                        "key_topics": ["python", "claude-cli"]
                    }
                }
            }
        ],
        "projects_worked_on": ["AutoBlog"]
    }


@pytest.fixture
def temp_posts_dir(tmp_path):
    """Create a temporary posts directory."""
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    return posts_dir
