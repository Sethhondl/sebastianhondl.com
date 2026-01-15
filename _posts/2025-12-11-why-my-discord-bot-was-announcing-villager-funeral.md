---
layout: post
title: "Why My Discord Bot Was Announcing Villager Funerals"
date: 2025-12-11
categories: [development, ai]
tags: [claude-code, python, testing, debugging]
read_time: 2
word_count: 420
---

Messages started appearing in our Discord channel that nobody asked for:

```
Villager class_1646['Villager'/297305, l='ServerLevel[TubaBoneWorld2025]', 
x=-137.30, y=96.00, z=-399.70] died, message: 'Villager was squished too much'
```

Nobody wants a notification every time a wandering trader's llama meets its end.

## The Setup

My Minecraft server runs a Discord bot that bridges chat between the game and a Discord channel. A log watcher monitors the server log file in real-time, forwarding relevant messages—player joins, achievements, deaths—to Discord. Players love the integration. What they don't love is getting pinged for every villager's unfortunate encounter with a piston.

## The Investigation

My first thought was the new datapack I'd installed for player head drops, but its contents only touch loot tables—no chat logic. The real culprit was hiding in my log watcher:

```python
class MinecraftLogHandler(FileSystemEventHandler):
    DEATH_PATTERN = re.compile(r'\[Server thread/INFO\]: (.+?) (died|was slain|was killed)')
    
    def process_log_line(self, line):
        death_match = self.DEATH_PATTERN.search(line)
        if death_match:
            self.send_to_discord(f"{death_match.group(1)} {death_match.group(2)}")
```

The pattern was too greedy. The regex `(.+?)` captures any characters until it hits a death keyword. When the server logs a villager death, the pattern happily matches `Villager class_1646['Villager'/297305...]` as the "player" name. It doesn't know the difference between `Steve` and an internal mob identifier—it just sees text followed by a death word.

## The Fix

The solution was specificity:

```python
# Player names are 3-16 chars, alphanumeric with underscores only
PLAYER_DEATH_PATTERN = re.compile(
    r'\[Server thread/INFO\]: ([A-Za-z0-9_]{3,16}) (died|was slain by|was killed by|'
    r'drowned|burned to death|fell from|was blown up by|hit the ground too hard|'
    r'was shot by|starved to death|suffocated in|was squished)'
)
```

Minecraft player names follow strict rules: 3-16 characters, alphanumeric with underscores. Mob identifiers contain class names, brackets, coordinates, and quotes. By requiring the simpler pattern, we filter out the noise.

After deploying, the Discord channel went quiet. No more villager obituaries—just the player deaths we actually wanted to see.

## What I Learned

**Regex greed causes bugs.** When parsing logs, be as specific as possible about what you're matching. A broad pattern that "mostly works" will eventually capture something unexpected.

**Data has structure—use it.** The difference between `Steve` and `Villager class_1646['Villager'/297305...]` is obvious to humans but requires explicit rules for code. Identify structural differences and encode them.

**Check your assumptions.** I assumed only player events would match player-focused patterns. The regex wasn't failing on edge cases—it was succeeding on an entirely different category of data I hadn't anticipated.

Sometimes the most valuable debugging sessions are the ones where you fix the thing you didn't know was broken.