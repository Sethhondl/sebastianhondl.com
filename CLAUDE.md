# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

AutoBlog is a fully automated blogging system that generates daily blog posts from Claude Code session transcripts. It captures your coding sessions, maintains project memory across days, and publishes polished blog posts to GitHub Pages at sebastianhondl.com.

## Technology Stack

- **Language**: Python 3.7+ (standard library only)
- **AI Integration**: Claude CLI via subprocess
- **Static Site**: Jekyll (GitHub Pages)
- **Scheduling**: macOS launchd
- **Storage**: JSON files + GitHub repository
- **Hosting**: GitHub Pages with custom domain

## Directory Structure

```
AutoBlog/
├── scripts/                    # Core Python scripts
│   ├── daily_blog.py          # Main orchestration
│   ├── project_memory.py      # Cross-day project tracking
│   ├── generate_post.py       # Multi-pass blog generation
│   └── data/
│       └── project_index.json # Persistent project memory
├── _posts/                     # Generated blog posts (Jekyll)
├── _layouts/                   # Jekyll HTML layouts
├── _drafts/                    # Work-in-progress posts
├── transcripts/                # Synced Claude session transcripts
├── assets/css/                 # Blog styling
├── tests/                      # Pytest test suite
│   ├── conftest.py            # Fixtures and mocks
│   ├── test_project_memory.py
│   ├── test_generate_post.py
│   ├── test_daily_blog.py
│   └── test_integration.py
├── _config.yml                 # Jekyll configuration
├── index.md                    # Blog home page
├── about.md                    # About page
├── CNAME                       # Custom domain (sebastianhondl.com)
└── com.autoblog.daily.plist   # launchd scheduler config
```

## Common Commands

### Daily Operations

```bash
# Run blog generation manually
python scripts/daily_blog.py run

# Run without pushing to GitHub
python scripts/daily_blog.py run --skip-push

# Run faster (skip Claude summaries)
python scripts/daily_blog.py run --skip-push --skip-summaries

# Check system status
python scripts/daily_blog.py status

# Update project index only
python scripts/daily_blog.py update

# Sync transcripts to repo
python scripts/daily_blog.py sync --days 7
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_project_memory.py -v

# Run integration tests only
pytest tests/test_integration.py -v
```

### Scheduling

```bash
# Install launchd job (runs daily at 6 AM)
cp com.autoblog.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.autoblog.daily.plist

# Unload scheduler
launchctl unload ~/Library/LaunchAgents/com.autoblog.daily.plist

# Check if loaded
launchctl list | grep autoblog

# View logs
tail -f /tmp/autoblog.log
tail -f /tmp/autoblog.err
```

## Architecture

### Data Flow

```
Claude Code Sessions
       │
       ▼
~/transcript/  ←── (Existing hooks capture transcripts)
       │
       ▼
┌─────────────────────┐
│  Project Memory     │  ← Tracks projects across days
│  (project_index.json)│
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Multi-Pass Gen     │  ← 4 passes: Draft → Review → Revise → Polish
│  (generate_post.py) │
└─────────────────────┘
       │
       ▼
/_posts/*.md  →  Git Push  →  GitHub Pages  →  sebastianhondl.com
```

### Key Components

1. **Project Memory** (`project_memory.py`)
   - Scans `~/transcript/` for Claude Code sessions
   - Maintains project index with summaries per day
   - Provides historical context for blog generation

2. **Blog Generator** (`generate_post.py`)
   - 4-pass pipeline using Claude CLI
   - Pass 1: Draft from transcripts + history
   - Pass 2: Self-review and critique
   - Pass 3: Implement improvements
   - Pass 4: Final polish

3. **Orchestrator** (`daily_blog.py`)
   - Updates project memory index
   - Generates blog post for the day
   - Commits and pushes to GitHub

## Dependencies

### Runtime
- Python 3.7+
- Claude CLI (`claude` command) - authenticated via OAuth
- Git (for pushing to GitHub)

### Development
```bash
pip install -r requirements-dev.txt  # pytest, pytest-cov
```

## Configuration

### Transcript Source
Transcripts are read from `~/transcript/` which is populated by existing Claude Code hooks. The structure is:
```
~/transcript/[project]/[YYYY-MM-DD]/[session_id]/conversation.md
```

### GitHub Pages
- Custom domain: sebastianhondl.com
- DNS: A records pointing to GitHub Pages IPs
- HTTPS: Enabled in GitHub Pages settings

### Scheduler
The launchd plist runs daily at 6 AM. Edit the plist to change:
- `StartCalendarInterval`: Hour/Minute to run
- `StandardOutPath`: Log file location

## Debugging

- Logs: `/tmp/autoblog.log` and `/tmp/autoblog.err`
- Project index: `scripts/data/project_index.json`
- Test with `--skip-push` to avoid committing during development
- Use `pytest -v` for verbose test output

## Key Files

| File | Purpose |
|------|---------|
| `scripts/daily_blog.py` | Main entry point - run this |
| `scripts/project_memory.py` | Cross-day project tracking |
| `scripts/generate_post.py` | Multi-pass blog generation |
| `_config.yml` | Jekyll site configuration |
| `com.autoblog.daily.plist` | macOS scheduler |
| `tests/conftest.py` | Test fixtures and mock Claude CLI |
