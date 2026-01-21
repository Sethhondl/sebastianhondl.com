#!/usr/bin/env python3
"""
Sanitize transcripts by removing secrets before committing.

Scans transcript files for common secret patterns and redacts them.
Run this after syncing transcripts but before committing.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class RedactionResult:
    """Result of sanitizing a single file."""
    file_path: Path
    redactions: List[Tuple[str, str]]  # (pattern_name, matched_text_preview)
    modified: bool


# Secret patterns to detect and redact
# Each tuple: (name, pattern, replacement)
SECRET_PATTERNS = [
    # API Keys
    ("Anthropic API Key", r'sk-ant-[a-zA-Z0-9_-]{20,}', '[REDACTED_ANTHROPIC_KEY]'),
    ("OpenAI API Key", r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_OPENAI_KEY]'),
    ("Generic API Key", r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?(?!\[REDACTED)([a-zA-Z0-9_-]{16,})["\']?', r'\1=[REDACTED_API_KEY]'),

    # AWS Credentials
    ("AWS Access Key", r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),
    ("AWS Secret Key", r'(?i)(aws[_-]?secret[_-]?access[_-]?key|aws[_-]?secret)\s*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', r'\1=[REDACTED_AWS_SECRET]'),

    # Tokens
    ("Bearer Token", r'(?i)(bearer\s+)[a-zA-Z0-9_-]{20,}', r'\1[REDACTED_TOKEN]'),
    ("GitHub Token", r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'),
    ("GitHub Token (old)", r'github_pat_[a-zA-Z0-9_]{22,}', '[REDACTED_GITHUB_TOKEN]'),
    ("GitLab Token", r'glpat-[a-zA-Z0-9_-]{20,}', '[REDACTED_GITLAB_TOKEN]'),
    ("Slack Token", r'xox[baprs]-[a-zA-Z0-9-]+', '[REDACTED_SLACK_TOKEN]'),
    ("Discord Token", r'[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27}', '[REDACTED_DISCORD_TOKEN]'),

    # Private Keys
    ("Private Key", r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----', '[REDACTED_PRIVATE_KEY]'),
    ("SSH Private Key", r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----[\s\S]*?-----END\s+OPENSSH\s+PRIVATE\s+KEY-----', '[REDACTED_SSH_KEY]'),

    # Database Connection Strings
    ("Database URL", r'(?i)(postgres|mysql|mongodb|redis)://[^\s"\'<>]+:[^\s"\'<>]+@[^\s"\'<>]+', r'[REDACTED_DB_URL]'),

    # Environment Variables with sensitive names (exclude already-redacted values)
    ("Password Env", r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?(?!\[REDACTED)([^\s"\']{4,})["\']?', r'\1=[REDACTED_PASSWORD]'),
    ("Secret Env", r'(?i)(secret|private[_-]?key)\s*[=:]\s*["\']?(?!\[REDACTED)([^\s"\']{8,})["\']?', r'\1=[REDACTED_SECRET]'),
    ("Token Env", r'(?i)([a-z_]*token)\s*[=:]\s*["\']?(?!\[REDACTED)([a-zA-Z0-9_-]{16,})["\']?', r'\1=[REDACTED_TOKEN]'),

    # JWT Tokens (three base64 parts separated by dots)
    ("JWT Token", r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', '[REDACTED_JWT]'),

    # Webhook URLs
    ("Webhook URL", r'https://hooks\.(slack|discord)\.com/[^\s"\'<>]+', '[REDACTED_WEBHOOK_URL]'),

    # Email addresses (optional - uncomment if desired)
    # ("Email", r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]'),

    # IP addresses with ports that might be internal
    ("Internal IP", r'(?:192\.168|10\.|172\.(?:1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3}(?::\d+)?', '[REDACTED_INTERNAL_IP]'),

    # Base64-encoded secrets (long base64 strings that look like secrets)
    ("Base64 Secret", r'(?i)(key|secret|password|token|credential)\s*[=:]\s*["\']?(?!\[REDACTED)([A-Za-z0-9+/]{40,}={0,2})["\']?', r'\1=[REDACTED_BASE64]'),
]


def sanitize_content(content: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Sanitize content by redacting secrets.

    Returns:
        Tuple of (sanitized_content, list of (pattern_name, preview))
    """
    redactions = []
    sanitized = content

    for name, pattern, replacement in SECRET_PATTERNS:
        matches = list(re.finditer(pattern, sanitized))
        for match in matches:
            matched_text = match.group(0)
            # Create a preview (first 20 chars + ... if longer)
            preview = matched_text[:20] + '...' if len(matched_text) > 20 else matched_text
            redactions.append((name, preview))

        sanitized = re.sub(pattern, replacement, sanitized)

    return sanitized, redactions


def sanitize_file(file_path: Path, dry_run: bool = False) -> RedactionResult:
    """
    Sanitize a single file.

    Args:
        file_path: Path to the file to sanitize
        dry_run: If True, don't modify the file, just report what would be redacted

    Returns:
        RedactionResult with details of what was found/redacted
    """
    content = file_path.read_text(encoding='utf-8', errors='replace')
    sanitized, redactions = sanitize_content(content)

    modified = content != sanitized

    if modified and not dry_run:
        file_path.write_text(sanitized, encoding='utf-8')

    return RedactionResult(
        file_path=file_path,
        redactions=redactions,
        modified=modified
    )


def sanitize_directory(directory: Path, dry_run: bool = False) -> Dict[str, any]:
    """
    Sanitize all markdown files in a directory.

    Args:
        directory: Path to the directory to sanitize
        dry_run: If True, don't modify files, just report what would be redacted

    Returns:
        Dictionary with summary statistics and detailed results
    """
    results = []
    total_files = 0
    files_with_secrets = 0
    total_redactions = 0

    # Find all markdown files
    for md_file in directory.rglob('*.md'):
        total_files += 1
        result = sanitize_file(md_file, dry_run=dry_run)

        if result.redactions:
            files_with_secrets += 1
            total_redactions += len(result.redactions)
            results.append(result)

    return {
        'total_files': total_files,
        'files_with_secrets': files_with_secrets,
        'total_redactions': total_redactions,
        'results': results,
        'dry_run': dry_run
    }


def print_report(summary: Dict[str, any]) -> None:
    """Print a human-readable report of the sanitization results."""
    print("\n" + "=" * 60)
    print("TRANSCRIPT SANITIZATION REPORT")
    print("=" * 60)

    if summary['dry_run']:
        print("MODE: DRY RUN (no files modified)")
    else:
        print("MODE: LIVE (files were modified)")

    print(f"\nFiles scanned: {summary['total_files']}")
    print(f"Files with secrets: {summary['files_with_secrets']}")
    print(f"Total redactions: {summary['total_redactions']}")

    if summary['results']:
        print("\n" + "-" * 60)
        print("DETAILED FINDINGS:")
        print("-" * 60)

        for result in summary['results']:
            rel_path = result.file_path.name
            print(f"\n📄 {rel_path}")
            for pattern_name, preview in result.redactions:
                # Mask the preview further for display
                masked_preview = preview[:10] + '***' if len(preview) > 10 else preview[:5] + '***'
                print(f"   • {pattern_name}: {masked_preview}")

    print("\n" + "=" * 60)

    if summary['dry_run'] and summary['total_redactions'] > 0:
        print("⚠️  Run without --dry-run to apply redactions")
    elif summary['total_redactions'] > 0:
        print("✅ Redactions applied successfully")
    else:
        print("✅ No secrets found")

    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Sanitize transcripts by removing secrets before committing.'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='transcripts',
        help='Directory to sanitize (default: transcripts)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Don't modify files, just report what would be redacted"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Only output if secrets were found"
    )

    args = parser.parse_args()

    # Resolve directory path
    directory = Path(args.directory)
    if not directory.is_absolute():
        # If relative, assume it's relative to the repo root
        script_dir = Path(__file__).parent
        repo_dir = script_dir.parent
        directory = repo_dir / directory

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        sys.exit(1)

    summary = sanitize_directory(directory, dry_run=args.dry_run)

    if not args.quiet or summary['total_redactions'] > 0:
        print_report(summary)

    # Exit with code 1 if secrets were found in dry-run mode (useful for CI)
    if args.dry_run and summary['total_redactions'] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
