---
layout: post
title: "When Your Script Declares Victory Before the Server's Ready"
date: 2025-11-26
categories: [development, ai]
tags: [claude-code, python, javascript, automation, testing]
read_time: 3
word_count: 723
---

There's a particular flavor of debugging frustration that comes from scripts that technically work but don't quite *finish* the job. Today I spent time with my Minecraft server's backup restore script, which was proudly declaring success while the server was still warming up in the background.

## The Problem: Premature Victory Laps

The restore script had a straightforward job: download a backup from S3, stop the server, extract files, restart, and verify everything's working. The logs showed it completing each step, but then it would hang at "Waiting for server to become joinable..." indefinitely. I expected a final "✓ Server is joinable" message. Instead, just a blinking cursor:

```
✓ Minecraft service started
ℹ Waiting for server to become joinable...
[2025-11-26 17:30:54] Using RCON password from environment: Wil***
█
```

No success message. No failure message. Just silence.

## The Detection Gap

The issue was in how the script checked server readiness. Minecraft servers have a peculiar startup behavior—systemd reports "active" while the Java process is still loading worlds and initializing. The script was checking `systemctl is-active`, which returns true the moment the service starts, not when the server is actually accepting connections.

This is a common pattern in service management: the process manager's view of "running" doesn't match the application's view of "ready."

The fix involved health checks using RCON (Remote Console), a protocol for sending administrative commands to a running Minecraft server. RCON only responds once the server is truly ready, making it a reliable indicator of actual readiness:

```bash
wait_for_server() {
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if mcrcon -H localhost -p "$RCON_PASSWORD" "list" 2>/dev/null | grep -q "players"; then
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    return 1
}
```

## A Second Bug Lurking Nearby

While testing the fix, I ran through the full server lifecycle a few times: backup, restore, verify. During one verification pass, I checked the Discord bot that tracks player statistics—and noticed the leaderboard wasn't updating. Deaths and playtime were stuck at zero for everyone.

Different bug, but I was already in debugging mode.

The stats tracking code was looking for Minecraft's statistics files in `/minecraft/world/stats/`, and the files existed. Permissions looked fine. File contents were valid JSON. Everything checked out—except the path itself.

A quick comparison revealed the problem:

```bash
echo "Parser looking in: $STATS_PATH"
echo "server.properties world-name: $(grep 'level-name' /minecraft/server.properties)"
```

The parser was looking in `/minecraft/world/stats/` while the server's `level-name` was set to `survival`—meaning the real stats lived in `/minecraft/survival/stats/`. The parser had been initialized at module load time with a hardcoded default, before the configuration that would have told it the correct world name.

The fix: lazy initialization.

```python
_stats_parser = None

def get_stats_parser():
    global _stats_parser
    if _stats_parser is None:
        world_name = config.get('world_name', 'world')
        _stats_parser = StatsParser(f"/minecraft/{world_name}/stats/")
    return _stats_parser
```

## The Pattern: Initialization Order Matters

Both bugs shared a theme: timing assumptions. The restore script assumed "service active" meant "server ready." The stats parser assumed configuration would be available at import time.

These bugs are particularly tricky because they work fine in most scenarios. The restore script succeeds if you happen to wait long enough. The stats parser works if the world is named "world" (the default). It's only when conditions deviate slightly that things break—which is exactly when you need them most.

## Practical Takeaways

**Distinguish "started" from "ready."** Process managers tell you when something launched, not when it's functional. For any service with a startup phase, add application-level health checks.

**Lazy-initialize configuration-dependent objects.** If a component needs runtime configuration, don't create it at import time. Use lazy initialization or explicit setup methods.

**Test the unhappy paths.** The restore script worked fine during manual testing because humans are slow. Automated scripts running in sequence expose these timing issues that patience accidentally hides.

Throughout this session, I leaned on Claude Code to generate diagnostic scripts—describing symptoms and having it suggest which assumptions to verify. That systematic approach caught the world name mismatch. When I said "stats aren't updating but the files exist," the first suggestion was to verify the path the parser was *actually using* versus where the files *actually lived*.

The Minecraft server now properly detects when it's ready, and the leaderboard is finally tracking everyone's deaths. Sorry, frequent respawners—your secrets are out.