---
layout: post
title: "Why Your Bot Works Fine Until It Restarts: A State Synchronization Bug"
date: 2025-12-18
categories: [development, ai]
tags: [claude-code, python, testing, api, debugging]
read_time: 2
word_count: 521
---

My Minecraft-Discord bot was flooding the channel with villager death notifications every time the server restarted. During normal gameplay, filtering worked perfectly—only real player deaths made it to Discord. But restart the server? Every mob death poured through.

## The Initial Investigation

The death notification showed up in my terminal with a distinctive format:

```
Villager class_1646['Villager'/89054, l='ServerLevel[TubaBoneWorld2025]', x=-137.70, y=96.00, z=-399.70] died, message: 'Villager was squished too much'
```

I traced the issue to `minecraft_integration.py` and its regex patterns for parsing log events:

```python
DEATH_PATTERN = re.compile(r'\[(\d{2}:\d{2}:\d{2})\] \[(?:Server thread|Async Chat Thread[^\]]*)/INFO\]: (\w+) (.+)')
```

The pattern uses `(\w+)` as the first capture group—"one or more word characters." This means "Villager" matches just as readily as "Steve" would. The pattern is intentionally permissive because Minecraft has dozens of death message variants, and maintaining an exhaustive list would be fragile. Better to catch everything and filter downstream.

## The State Synchronization Problem

The bot maintains an online players list in DynamoDB. The filtering logic seemed simple: if the "username" from the death message isn't in the online players list, ignore it. Villagers aren't players, so they'd never appear in that list.

But server restarts expose a timing gap:

```
6:00:00 - Minecraft server process starts
6:00:02 - Server begins writing to log file
6:00:03 - Log watcher detects activity, starts processing
6:00:03 - Villager gets crushed by falling block, death logged
6:00:15 - DynamoDB sync completes, player list populated
```

During that 12-second window, the player list is empty. The filtering logic checks if "Villager" is in an empty list, gets `False`, and then what? The original code didn't handle this case:

```python
def should_forward_death(username, death_message):
    online_players = get_online_players()  # Returns [] during startup
    if username in online_players:
        return True
    # No explicit handling for empty player list
    # Falls through to return True by default
```

With an empty player list, the code couldn't distinguish "this is a mob death" from "this player might be online but we don't know yet."

## The Fix: Intrinsic Checks Over Stateful Lookups

Instead of depending on synchronized state, the fix examines the log line itself:

```python
if 'class_' in raw_line and "died, message:" in raw_line:
    return None
```

Minecraft logs entity deaths with a distinctive format that includes `class_XXXX` identifiers and coordinate data. Player deaths never include this metadata—they're logged as simple messages like `Steve was slain by Zombie`. This format check is intrinsic to the data; it doesn't depend on any external state being synchronized.

## Takeaways

**Test your restart scenarios.** Steady-state behavior can hide timing bugs that only appear during initialization.

**Prefer intrinsic checks over stateful lookups.** If you can identify data by its format rather than comparing against external state, you eliminate timing dependencies entirely.

**Show AI assistants the actual error.** The raw log line contained all the clues—the `class_1646` identifier and coordinate tuple immediately revealed the distinguishing characteristic.

The villager filter now works regardless of timing. The `class_` identifier is baked into Minecraft's logging format. It doesn't care whether DynamoDB has finished syncing, and neither does my bot.