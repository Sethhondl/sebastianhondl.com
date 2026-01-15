---
layout: post
title: "Scanning for Secrets: A Security Audit with Claude Code"
date: 2025-12-22
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 5
word_count: 1024
---

Last week I was refactoring my Minecraft server deployment scripts when I noticed something that made my stomach drop: a file called `config.backup.json` that I didn't remember creating. It turned out to be harmless—just some old server settings—but that moment of "wait, what's in there?" stuck with me. How many other files might be lurking in this repository with contents I'd forgotten about?

It was time for a proper audit.

## Why Two Minecraft Servers?

I run a Minecraft server on AWS so friends can connect from anywhere, but I also maintain a local server for testing mods and configuration changes before pushing them to production. Nobody wants to discover that a new mod crashes the server when your friends are mid-build.

Both environments share configuration templates and deployment scripts, which creates an obvious risk: credentials for the production AWS infrastructure living alongside local development files. One careless commit could expose Discord bot tokens, RCON passwords, or AWS access patterns.

My request to Claude was specific: scan the entire codebase for anything that looks like a secret, credential, or sensitive value, and verify that real credentials only exist in the `.env` file where they belong.

## How the Scan Worked

Rather than just asking "are there any secrets?", I prompted Claude to search systematically for common credential patterns. It ran searches for `password`, `passwd`, `pwd`, `secret`, `token`, `api_key`, and `key` across all files, then examined the results in context.

The good news: no actual secrets were hardcoded in version-controlled files. The `.env` file contains all real credentials, and `.gitignore` properly excludes it.

But the scan surfaced findings that deserved closer inspection.

**Template files with placeholder values:**
```properties
# server.properties.template
rcon.password=minecraft123
```

This RCON password placeholder is intentional—RCON lets you run console commands remotely, and the deployment script substitutes the real password from environment variables. But seeing it in plain text prompted me to verify that substitution actually happens (it does) and fails loudly if the environment variable is missing (it didn't—more on that below).

**Documentation examples:**
```markdown
# From README.md
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

Intentional, but a useful reminder that documentation establishes patterns. If your examples look like `YOUR_TOKEN_HERE`, reviewers learn to spot that format. If your examples look like plausible real tokens, pattern-matching becomes harder.

**Default values in code that shouldn't exist:**

```python
# aws_helpers.py (before)
def __init__(self, ssm_client, rcon_password='minecraft123'):
```

This was the real finding. A default password parameter means the code can run without explicit configuration—which means a misconfigured deployment could silently use the placeholder instead of the real credential. Defense in depth says required values should be required.

I changed it to:

```python
# aws_helpers.py (after)
def __init__(self, ssm_client, rcon_password):
    if not rcon_password:
        raise ValueError("rcon_password is required")
```

Now a missing password is a loud failure at initialization, not a silent security gap discovered in production.

## The False Positives

Any pattern-based scan produces noise. Here's what showed up that wasn't actually a problem:

- **`secret_santa.py`**: A module name, not a credential
- **`token_bucket.py`**: A rate-limiting implementation, referring to the algorithm
- **`password_strength_validator`**: A function that checks passwords, doesn't contain them
- **SSH key file paths**: References like `~/.ssh/id_rsa` appeared in documentation, but the actual key files are outside the repository

Recognizing these non-issues matters because it calibrates your response to real findings. If everything looks like a security problem, nothing does.

## What I Changed

Based on the audit, I made three concrete changes:

1. **Removed the default password parameter** (shown above)
2. **Added validation to the deployment script** to fail if `RCON_PASSWORD` isn't set in the environment
3. **Updated `.gitignore`** to explicitly exclude `*.backup.json` and similar recovery file patterns

I also reorganized the directory structure. The audit made me realize how tangled the two server configurations had become:

```
minecraftServer/
├── aws-server/          # Cloud infrastructure
│   ├── cloudformation/
│   ├── lambda/
│   ├── discord-bot/
│   └── deploy.sh
└── local-server/        # Local development
    ├── server.properties
    ├── start.sh
    └── mods/
```

The separation makes it clearer which credentials belong to which environment, reducing the risk of accidentally referencing production secrets in local testing scripts.

## Lessons for Your Own Projects

**Regular secret scans catch drift.** Your `.gitignore` might be perfect today, but you added a config file last month and a debug script last week. Periodic scans catch what initial setup missed.

**Template files need validation, not just substitution.** Having a `.template` file with placeholders is good practice. But verify that your deployment process fails explicitly when substitution doesn't happen, rather than falling back to defaults.

**Search for semantic variations.** Don't just search for `password`—search for `passwd` and `pwd` too. Search for `token` and `api_key` and `apikey`. Think about how different developers name the same concept.

**Evaluate findings in context.** The `minecraft123` placeholder in a template file is obviously not a real password. The same string as a default parameter value is a different risk profile entirely. Context determines severity.

**Document what you changed.** An audit that identifies problems but doesn't fix them is incomplete. I now have a commit that shows exactly what the audit found and how I addressed it—useful for future reference and for anyone reviewing the project's security posture.

## The AI-Assisted Advantage

What made this session effective wasn't raw speed—I could run grep myself. It was the combination of systematic coverage and contextual analysis. Claude searched for multiple credential patterns, then for each match explained whether it was a placeholder, a code reference, or something that warranted action. That's the difference between a list of search results and an actual security review.

The audit also surfaced the default parameter issue, which I might have overlooked in a manual scan. When you're grepping for "password," a function signature doesn't pattern-match the same way as `password=hunter2` in a config file. But it's arguably more dangerous.

Next up: I'm planning to add a pre-commit hook that runs similar pattern checks automatically. Today's audit was valuable, but the real win would be catching these issues before they ever reach the repository.

Sometimes the most valuable AI assistance isn't writing new code—it's asking systematic questions about code you thought you already understood.