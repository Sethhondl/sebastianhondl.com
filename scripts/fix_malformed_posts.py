#!/usr/bin/env python3
"""
Fix malformed blog posts that have:
1. Content wrapped in markdown code fences
2. Fallback titles ("Daily Development Log - January 14, 2026")

This script extracts the actual content and regenerates proper filenames.
"""

import re
import sys
from pathlib import Path


def clean_content(content: str) -> tuple:
    """
    Extract actual blog content from Claude's wrapped output.

    Returns: (body_content, title_from_frontmatter_or_None)
    """
    if not content:
        return content, None

    extracted_title = None

    # Try to extract content from markdown code fence that contains frontmatter
    # Pattern matches: ```markdown (newline) ---frontmatter---body ```
    # The closing ``` must be at start of line and followed by newline+--- or end
    code_fence_pattern = r'```(?:markdown)?\s*\n(---\s*\n[\s\S]+?)\n```\s*\n---'
    match = re.search(code_fence_pattern, content, re.DOTALL)
    if not match:
        # Try alternate pattern: closing ``` at end of content
        code_fence_pattern = r'```(?:markdown)?\s*\n(---\s*\n[\s\S]+?)\n```\s*$'
        match = re.search(code_fence_pattern, content, re.DOTALL)
    if match:
        content = match.group(1).strip()
    else:
        # No code fence with frontmatter - check if there's embedded frontmatter
        # Pattern: meta-commentary \n---\nlayout: post\ntitle:...
        embedded_fm_pattern = r'\n---\s*\n(layout:\s*post[\s\S]+?)\n---\s*\n'
        fm_match = re.search(embedded_fm_pattern, content)
        if fm_match:
            # Found embedded frontmatter - extract from there
            start_pos = fm_match.start() + 1  # Include the ---
            content = content[start_pos:].strip()

    # If content has frontmatter, extract the title and body
    if content.startswith('---'):
        lines = content.split('\n')
        body_start = 0
        for i, line in enumerate(lines[1:], 1):  # Skip first ---
            # Look for title in frontmatter
            if line.startswith('title:'):
                # Extract title, handling quotes
                title_match = re.match(r'title:\s*["\']?(.+?)["\']?\s*$', line)
                if title_match:
                    extracted_title = title_match.group(1)
            if line.strip() == '---':
                body_start = i + 1
                break
        if body_start > 0:
            content = '\n'.join(lines[body_start:]).strip()

    # Only look for markdown title heading if we don't have a frontmatter title
    # and the content doesn't start with one
    if not extracted_title:
        lines = content.strip().split('\n')
        first_non_empty = next((l for l in lines if l.strip()), "")
        if not first_non_empty.startswith('# '):
            # Search for a markdown heading (but be careful of code comments)
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Only match ## or # headings, not code comments
                if stripped.startswith('# ') and not stripped.startswith('# ') or stripped.startswith('## '):
                    content = '\n'.join(lines[i:])
                    break

    return content.strip(), extracted_title


def extract_title(content: str, fallback_title: str = None) -> str:
    """Extract the title from markdown content or use fallback."""
    lines = content.strip().split('\n')
    for line in lines[:20]:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return fallback_title


def generate_slug(title: str) -> str:
    """Generate a URL slug from title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')[:50]


def extract_tags(content: str) -> list:
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

    if 'claude-code' not in tags:
        tags.insert(0, 'claude-code')

    return tags[:5]


def fix_post(filepath: Path, dry_run: bool = True) -> dict:
    """Fix a single malformed post."""
    result = {
        'original_file': filepath.name,
        'action': None,
        'new_file': None,
        'title': None,
        'error': None
    }

    try:
        content = filepath.read_text()

        # Extract date from filename
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-', filepath.name)
        if not date_match:
            result['error'] = "Could not extract date from filename"
            return result
        date = date_match.group(1)

        # Split frontmatter and body
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                body = parts[2].strip()
            else:
                body = content
        else:
            body = content

        # Clean the body content
        cleaned_body, frontmatter_title = clean_content(body)

        # Extract the real title (from markdown heading or frontmatter)
        title = extract_title(cleaned_body, fallback_title=frontmatter_title)
        if not title:
            # No embedded title found - content may be clean but with generic title
            result['action'] = 'skipped'
            result['error'] = "No embedded title found (content may be clean)"
            return result

        result['title'] = title

        # Generate new filename
        slug = generate_slug(title)
        new_filename = f"{date}-{slug}.md"
        new_filepath = filepath.parent / new_filename

        result['new_file'] = new_filename

        # Check if this is actually a change
        if filepath.name == new_filename and body == cleaned_body:
            result['action'] = 'no_change'
            return result

        # Remove the title line from cleaned body (it goes in frontmatter)
        body_lines = cleaned_body.strip().split('\n')
        if body_lines and body_lines[0].strip().startswith('# '):
            cleaned_body = '\n'.join(body_lines[1:]).strip()

        # Extract tags
        tags = extract_tags(cleaned_body)

        # Calculate read time
        word_count = len(cleaned_body.split())
        read_time = max(1, word_count // 200)

        # Build new content
        new_content = f'''---
layout: post
title: "{title}"
date: {date}
categories: [development, ai]
tags: [{', '.join(tags)}]
read_time: {read_time}
word_count: {word_count}
---

{cleaned_body}
'''

        if dry_run:
            result['action'] = 'would_fix'
        else:
            # Write new file
            new_filepath.write_text(new_content)

            # Delete old file if different
            if filepath != new_filepath:
                filepath.unlink()

            result['action'] = 'fixed'

        return result

    except Exception as e:
        result['error'] = str(e)
        return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix malformed blog posts")
    parser.add_argument("--apply", action="store_true",
                        help="Actually apply fixes (default is dry-run)")
    parser.add_argument("--file", help="Fix a specific file")
    args = parser.parse_args()

    posts_dir = Path(__file__).parent.parent / "_posts"

    # Find posts with the problematic slug
    if args.file:
        files = [posts_dir / args.file]
    else:
        files = list(posts_dir.glob("*daily-development-log-january-14-2026*.md"))

    if not files:
        print("No malformed posts found")
        return

    print(f"{'DRY RUN - ' if not args.apply else ''}Processing {len(files)} files:\n")

    for filepath in sorted(files):
        result = fix_post(filepath, dry_run=not args.apply)

        print(f"  {result['original_file']}")
        if result['error']:
            print(f"    ERROR: {result['error']}")
        elif result['action'] == 'no_change':
            print(f"    No changes needed")
        else:
            print(f"    Title: {result['title']}")
            print(f"    -> {result['new_file']}")
            print(f"    Action: {result['action']}")
        print()

    if not args.apply:
        print("Run with --apply to make changes")


if __name__ == "__main__":
    main()
