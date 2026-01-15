---
layout: post
title: "Why Your Bot Works Fine Until It Restarts: A State Synchronization Bug"
date: 2025-12-20
categories: [development, ai]
tags: [claude-code, python, testing, api, debugging]
read_time: 3
word_count: 714
---

*Debugging villager death message filtering in a Minecraft Discord integration*

My Discord bot's villager filter worked perfectly—until the Minecraft server restarted. Then the channel flooded with death messages again.

## The Setup

I run a Minecraft server with a Discord integration that relays game events to a channel. Players can see when someone joins, makes an advancement, or dies in an amusing way. The architecture involves three components: a log file watcher that monitors the Minecraft server's `latest.log`, a DynamoDB table that tracks which players are currently online, and RCON commands that sync player state when the server starts up.

But villagers dying? That's just noise. The server generates constant death messages whenever villagers crowd together, and nobody wants their Discord channel flooded with those.

The filtering worked fine during normal gameplay. Then the server restarted, and suddenly the channel looked like this:

```
🪦 Villager was squished too much
🪦 Villager was squished too much
🪦 Villager suffocated in a wall
```

## Understanding the Log Formats

Minecraft logs death messages differently for players versus entities. When a player dies:

```
[14:23:45] [Server thread/INFO]: Steve was slain by Zombie
```

Clean and simple—just the player name followed by the death message. But when an entity like a villager dies:

```
[14:23:45] [Server thread/INFO]: Villager class_1646['Villager'/89054, l='ServerLevel[TubaBoneWorld2025]', x=-137.70, y=96.00, z=-399.70] died, message: 'Villager was squished too much'
```

That `class_1646` identifier and coordinate dump are how Minecraft logs non-player entity deaths. This distinction is key to understanding both the bug and the fix.

## The Failed Approach: Player List Checking

The log watcher uses a regex pattern to capture death messages:

```python
DEATH_PATTERN = re.compile(r'\[(\d{2}:\d{2}:\d{2})\] \[(?:Server thread|Async Chat Thread[^\]]*)/INFO\]: (\w+) (.+)')
```

The pattern captures `(\w+)` as the username. For player deaths, "Steve" matches cleanly. For entity deaths, "Villager" also matches as a valid `\w+` sequence, even though the rest of the line is verbose gibberish.

The filtering logic checked if this captured name was a real player:

```python
def handle_death_message(username, message, raw_line):
    if username not in online_players:
        return None
    # ... relay to Discord
```

During normal operation, "Villager" wasn't in the online players list, so the message got filtered. Simple enough.

## The Restart Bug

On server restart, the online players list in DynamoDB gets wiped and rebuilt. The bot queries RCON to get the current player list, then updates the database. But there's a timing window during startup where:

1. The Minecraft server is running and logging events
2. The log watcher is processing those events
3. The DynamoDB sync hasn't completed yet

During this window, the player list check behaved inconsistently. Sometimes the list was empty, sometimes partially populated. The filtering that worked during steady-state operation broke down during state reconstruction.

## The Fix: Filter on Format, Not Content

Rather than fixing the DynamoDB synchronization timing, I added a check that catches entity deaths based on their distinctive log format:

```python
def handle_death_message(username, message, raw_line):
    # Skip entity deaths based on log format
    if 'class_' in raw_line and "died, message:" in raw_line:
        return None
    
    if username not in online_players:
        return None
    # ... relay to Discord
```

This approach is more robust because it doesn't depend on DynamoDB state being synchronized. It catches entity deaths during the startup window, handles edge cases like a player hypothetically named "Villager," and works regardless of which players are online.

The format-based check runs first, so entity deaths never reach the synchronization-dependent code path.

After deploying, a quick server restart confirmed the fix. The log watcher processed the usual flurry of villager deaths during startup, the format check caught them all, and the Discord channel stayed clean.

## The Takeaway

Stateful systems behave differently at startup than during steady-state operation. The villager filter worked perfectly during normal gameplay because the player list was always populated and synchronized. Only the restart scenario—when state was being rebuilt—exposed the gap.

The fix wasn't to make synchronization faster or more reliable. It was to remove the dependency on external state entirely by checking the structural format of the log line itself. When you can filter on intrinsic properties of the data rather than comparing against external state, you eliminate a whole category of timing bugs.