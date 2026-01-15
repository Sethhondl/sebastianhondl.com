---
layout: post
title: "When File-Based Detection Lies: Switching to RCON for Minecraft Server Auto-Shutdown"
date: 2025-11-21
categories: [development, ai]
tags: [claude-code, automation, testing, debugging]
read_time: 3
word_count: 640
---

There's a particular kind of bug that makes you question your assumptions about "simple" solutions. My Minecraft server's auto-shutdown system was kicking players off while they were actively playing—three complaints over two weeks before I finally tracked it down. The culprit? A file-based player detection system that seemed clever but had a fundamental flaw.

## The Problem: Players Getting Booted Mid-Game

My AWS-hosted Minecraft server has an auto-shutdown feature to save costs. When no players are online for 30 minutes, the server gracefully shuts down. But players were reporting something frustrating: the server was shutting down while they were still playing.

## The Investigation

The auto-shutdown logic lived in `check-players.sh`, running every 5 minutes via cron:

```bash
get_player_count() {
  if ! pgrep -f "fabric-server-launch.jar|minecraft_server|forge.*jar" > /dev/null; then
    echo "0"
    return
  fi

  PLAYER_DATA_DIR="/minecraft/world/playerdata"

  if [ ! -d "$PLAYER_DATA_DIR" ]; then
    echo "0"
    return
  fi

  # Count recently modified player data files (modified in last 10 minutes)
  COUNT=$(find "$PLAYER_DATA_DIR" -name "*.dat" -mmin -10 2>/dev/null | wc -l)
  echo "$COUNT"
}
```

The logic seemed sound: count player data files modified in the last 10 minutes. The 10-minute window provided a buffer beyond the 5-minute cron interval. If a player is actively playing, their `.dat` file should be getting updated, right?

Wrong.

## Where It Broke Down

Minecraft doesn't continuously save player data while someone is playing. The server autosaves at configurable intervals (typically every 5-6 minutes for world data), but player `.dat` files specifically get written when a player's inventory or position changes significantly—or when they disconnect. A player standing around chatting, AFK, or mining steadily in one area might not trigger a save for much longer than 10 minutes.

The file-based approach had appealing properties—no network overhead, no dependency on RCON being responsive—but those advantages meant nothing if it couldn't actually detect players.

My initial hypothesis was that the RCON password wasn't being passed correctly from my `.env` file through the CloudFormation deployment. But tracing the code path showed the password flowing correctly. The problem wasn't configurational—it was architectural.

## The Fix: RCON-Based Detection

The solution was switching to RCON (Remote Console), which queries the server directly:

```bash
get_player_count() {
  if ! pgrep -f "fabric-server-launch.jar|minecraft_server|forge.*jar" > /dev/null; then
    echo "0"
    return
  fi

  RESULT=$(mcrcon -H localhost -P 25575 -p "$RCON_PASSWORD" "list" 2>/dev/null)
  
  if [ $? -ne 0 ]; then
    # RCON failed - assume players might be online to be safe
    echo "1"
    return
  fi

  COUNT=$(echo "$RESULT" | grep -oP 'There are \K\d+')
  echo "${COUNT:-0}"
}
```

Two key decisions shaped this implementation:

1. **Fail open when RCON is unreachable.** If we can't confirm the server is empty, assume someone might be playing. This trades potential cost (empty server stays running longer) for guaranteed player experience (no surprise disconnects).

2. **Use the `list` command** for the authoritative player count straight from the server itself.

## Lessons Learned

**"Simple" solutions carry hidden assumptions.** The file-based detection assumed file modification time correlates with player presence. A reasonable assumption that happened to be wrong.

**Fail open when the failure mode matters.** When you can't determine state with certainty, err on the side that protects user experience over cost optimization.

**Test the edge cases you don't think about.** This bug only appeared when players were relatively idle—not a scenario I'd explicitly tested.

**Check assumptions before chasing configuration bugs.** My initial RCON password hypothesis was a red herring. Systematic exploration ruled it out quickly and pointed to the real architectural issue.

## Wrapping Up

Sometimes the most important bugs aren't the flashy ones—they're the quiet failures that erode trust one frustrated disconnect at a time. Now players can actually finish their builds without getting unexpectedly booted. And I've learned to be more skeptical of "simple" solutions that make assumptions about systems I don't fully control.