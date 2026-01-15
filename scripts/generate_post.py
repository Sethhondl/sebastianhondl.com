#!/usr/bin/env python3
"""
Multi-Pass Blog Post Generator for AutoBlog

Generates polished blog posts using a 4-pass Claude CLI pipeline:
1. Draft - Initial blog post from transcripts
2. Review - Critique and identify improvements
3. Revise - Implement improvements
4. Polish - Final readability pass
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Try to import anthropic for API fallback
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class GenerationResult:
    """Result of the blog generation pipeline."""
    success: bool
    title: str
    content: str
    filename: str
    passes: Dict[str, str]
    error: Optional[str] = None


# Prompt templates for each pass
DRAFT_PROMPT = """You are writing a blog post about my day coding with Claude Code.

## Today's Claude Code Sessions
{transcripts}

## Historical Context (previous work on these projects)
{history}

## Task
Write an engaging blog post (600-1000 words) that:
- Highlights the most interesting work done today
- Shares insights about AI-assisted development
- Includes relevant code snippets if appropriate
- Has a conversational, personal tone
- Would be valuable to other developers learning Claude Code

Format the post as markdown with a clear title (# heading).
Include practical takeaways that readers can apply.

Write the blog post now:"""

REVIEW_PROMPT = """You are a professional editor reviewing a blog post about AI-assisted development.

## Blog Post to Review
{draft}

## Task
Critically review this blog post and identify specific improvements. Consider:

1. **Clarity**: Are there sections that are unclear or need more explanation?
2. **Context**: Is there missing context that would help readers understand?
3. **Flow**: Does the post flow well from one section to the next?
4. **Engagement**: Are there opportunities to make it more engaging?
5. **Technical Accuracy**: Any technical concerns or inaccuracies?
6. **Structure**: Is the organization logical and easy to follow?

Provide a numbered list of specific, actionable improvements.
Be constructive but thorough - this will be used to revise the post.

Your review:"""

REVISE_PROMPT = """You are revising a blog post based on editor feedback.

## Original Blog Post
{draft}

## Editor Feedback
{feedback}

## Task
Revise the blog post to address each piece of feedback from the editor.
Make sure to:
- Implement all suggested improvements
- Maintain the original voice and style
- Keep the post focused and well-structured
- Ensure all technical details are accurate

Write the revised blog post in full (don't summarize or abbreviate):"""

POLISH_PROMPT = """You are doing a final polish pass on a blog post before publication.

## Blog Post to Polish
{post}

## Task
Apply a final polish for publication. Focus on:

1. **Opening Hook**: Ensure the first paragraph grabs attention
2. **Transitions**: Smooth transitions between sections
3. **Conclusion**: Strong, memorable ending with clear takeaway
4. **Title**: Make sure the title is engaging and SEO-friendly
5. **Tone**: Consistent, conversational voice throughout
6. **Redundancy**: Remove any repetitive content
7. **Readability**: Clear, concise sentences

Write the final polished blog post in full:"""


class BlogGenerator:
    """Generates polished blog posts using multi-pass Claude CLI pipeline."""

    def __init__(self, posts_dir: Optional[Path] = None):
        self.posts_dir = posts_dir or Path(__file__).parent.parent / "_posts"
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, context: Dict[str, Any]) -> GenerationResult:
        """
        Generate a blog post using the 4-pass pipeline.

        Args:
            context: Blog context from ProjectMemory.get_context_for_blog()

        Returns:
            GenerationResult with the final post and intermediate outputs
        """
        passes = {}

        try:
            # Format context for prompts
            transcripts_text = self._format_transcripts(context.get("today", []))
            history_text = self._format_history(context.get("history", []))

            if not transcripts_text.strip():
                return GenerationResult(
                    success=False,
                    title="",
                    content="",
                    filename="",
                    passes={},
                    error="No transcripts found for today"
                )

            # Pass 1: Draft
            print("Pass 1/4: Generating draft...")
            draft = self._call_claude(DRAFT_PROMPT.format(
                transcripts=transcripts_text,
                history=history_text
            ))
            passes["draft"] = draft

            if not draft:
                return GenerationResult(
                    success=False,
                    title="",
                    content="",
                    filename="",
                    passes=passes,
                    error="Failed to generate draft"
                )

            # Pass 2: Review
            print("Pass 2/4: Reviewing draft...")
            review = self._call_claude(REVIEW_PROMPT.format(draft=draft))
            passes["review"] = review

            if not review:
                # Continue with draft if review fails
                print("Warning: Review failed, continuing with draft")
                review = "No specific improvements identified."

            # Pass 3: Revise
            print("Pass 3/4: Revising based on feedback...")
            revised = self._call_claude(REVISE_PROMPT.format(
                draft=draft,
                feedback=review
            ))
            passes["revised"] = revised

            if not revised:
                # Fall back to draft if revision fails
                print("Warning: Revision failed, using draft")
                revised = draft

            # Pass 4: Polish
            print("Pass 4/4: Final polish...")
            final = self._call_claude(POLISH_PROMPT.format(post=revised))
            passes["final"] = final

            if not final:
                # Fall back to revised if polish fails
                print("Warning: Polish failed, using revised version")
                final = revised

            # Extract title and format
            title = self._extract_title(final)
            filename = self._generate_filename(context.get("date"), title)
            content = self._format_jekyll_post(final, context.get("date"), title)

            return GenerationResult(
                success=True,
                title=title,
                content=content,
                filename=filename,
                passes=passes
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                title="",
                content="",
                filename="",
                passes=passes,
                error=str(e)
            )

    def _call_claude(self, prompt: str, timeout: int = 300) -> str:
        """
        Call Claude with a prompt, trying CLI first, then API fallback.

        The API fallback is used when ANTHROPIC_API_KEY is set (e.g., in GitHub Actions).
        """
        # Check if we should use API directly (e.g., in CI environment)
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        use_api = os.environ.get('USE_ANTHROPIC_API', '').lower() == 'true'

        if use_api and api_key and ANTHROPIC_AVAILABLE:
            return self._call_claude_api(prompt, api_key, timeout)

        # Try CLI first
        cli_result = self._call_claude_cli(prompt, timeout)
        if cli_result:
            return cli_result

        # Fall back to API if CLI fails and API is available
        if api_key and ANTHROPIC_AVAILABLE:
            print("CLI failed, falling back to Anthropic API...")
            return self._call_claude_api(prompt, api_key, timeout)

        return ""

    def _call_claude_cli(self, prompt: str, timeout: int = 300) -> str:
        """Call Claude via CLI."""
        try:
            result = subprocess.run(
                ['claude', '--print', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Claude CLI error: {result.stderr}")
                return ""

        except subprocess.TimeoutExpired:
            print(f"Claude CLI timed out after {timeout}s")
            return ""
        except FileNotFoundError:
            print("Claude CLI not found")
            return ""
        except Exception as e:
            print(f"Claude CLI exception: {e}")
            return ""

    def _call_claude_api(self, prompt: str, api_key: str, timeout: int = 300) -> str:
        """Call Claude via Anthropic API directly."""
        try:
            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            if message.content and len(message.content) > 0:
                return message.content[0].text
            return ""

        except Exception as e:
            print(f"Anthropic API error: {e}")
            return ""

    def _format_transcripts(self, transcripts: List[Dict[str, Any]]) -> str:
        """Format today's transcripts for the prompt."""
        if not transcripts:
            return ""

        sections = []
        for t in transcripts:
            project = t.get("project", "Unknown Project")
            content = t.get("content", "")

            # Truncate very long transcripts
            if len(content) > 8000:
                content = content[:8000] + "\n\n[... transcript truncated ...]"

            sections.append(f"### Project: {project}\n\n{content}")

        return "\n\n---\n\n".join(sections)

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format historical context for the prompt."""
        if not history:
            return "No previous work on these projects."

        sections = []
        for h in history:
            project = h.get("project", "Unknown")
            first = h.get("first_worked", "unknown")
            summary = h.get("summary", "No summary available")
            total = h.get("total_sessions", 0)

            section = f"""### {project}
- First worked on: {first}
- Total sessions: {total}
- Summary: {summary}"""

            # Add recent session summaries
            recent = h.get("recent_sessions", {})
            if recent:
                section += "\n- Recent work:"
                for date, log in sorted(recent.items())[-3:]:
                    log_summary = log.get("summary", "")
                    if log_summary:
                        section += f"\n  - {date}: {log_summary}"

            sections.append(section)

        return "\n\n".join(sections)

    def _extract_title(self, content: str) -> str:
        """Extract the title from the blog post content."""
        # Look for # Title at the start
        lines = content.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()

        # Fallback title
        return f"Daily Development Log - {datetime.now().strftime('%B %d, %Y')}"

    def _generate_filename(self, date: Optional[str], title: str) -> str:
        """Generate a Jekyll-compatible filename."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Convert title to slug
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')[:50]

        return f"{date}-{slug}.md"

    def _format_jekyll_post(self, content: str, date: Optional[str], title: str) -> str:
        """Format the content as a Jekyll post with front matter."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Extract tags from content
        tags = self._extract_tags(content)

        # Calculate read time (roughly 200 words per minute)
        word_count = len(content.split())
        read_time = max(1, word_count // 200)

        # Build front matter
        front_matter = f"""---
layout: post
title: "{title}"
date: {date}
categories: [development, ai]
tags: [{', '.join(tags)}]
read_time: {read_time}
word_count: {word_count}
---

"""

        # Remove the title from content if it starts with it
        content_lines = content.strip().split('\n')
        if content_lines and content_lines[0].strip().startswith('# '):
            content = '\n'.join(content_lines[1:]).strip()

        return front_matter + content

    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from the content."""
        content_lower = content.lower()
        tags = []

        tag_keywords = {
            'claude-code': ['claude code', 'claude', 'ai assistant'],
            'python': ['python', 'pip', 'pytest'],
            'javascript': ['javascript', 'js', 'typescript', 'node'],
            'git': ['git', 'commit', 'branch', 'merge'],
            'automation': ['automat', 'script', 'cron', 'schedule'],
            'testing': ['test', 'pytest', 'unittest', 'spec'],
            'api': ['api', 'endpoint', 'rest', 'graphql'],
            'debugging': ['debug', 'error', 'fix', 'bug'],
            'refactoring': ['refactor', 'cleanup', 'reorganiz'],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(tag)

        # Always include claude-code tag
        if 'claude-code' not in tags:
            tags.insert(0, 'claude-code')

        return tags[:5]  # Limit to 5 tags

    def save_post(self, result: GenerationResult) -> Optional[Path]:
        """Save the generated post to the _posts directory."""
        if not result.success or not result.content:
            return None

        filepath = self.posts_dir / result.filename
        filepath.write_text(result.content)
        return filepath


def main():
    """CLI interface for blog generation."""
    import argparse
    from project_memory import ProjectMemory

    parser = argparse.ArgumentParser(description="Generate blog post from transcripts")
    parser.add_argument("--date", help="Date to generate post for (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't save the post, just print it")
    parser.add_argument("--single-pass", action="store_true",
                        help="Only run the draft pass (faster, less polished)")

    args = parser.parse_args()

    # Get context from project memory
    memory = ProjectMemory()
    context = memory.get_context_for_blog(args.date)

    if not context.get("today"):
        print(f"No transcripts found for {context['date']}")
        return

    print(f"Generating blog post for {context['date']}")
    print(f"Projects: {', '.join(context['projects_worked_on'])}")
    print(f"Sessions: {len(context['today'])}")
    print()

    # Generate post
    generator = BlogGenerator()
    result = generator.generate(context)

    if result.success:
        print(f"\nGenerated: {result.title}")
        print(f"Filename: {result.filename}")

        if args.dry_run:
            print("\n--- POST CONTENT ---\n")
            print(result.content)
        else:
            filepath = generator.save_post(result)
            print(f"Saved to: {filepath}")
    else:
        print(f"\nGeneration failed: {result.error}")


if __name__ == "__main__":
    main()
