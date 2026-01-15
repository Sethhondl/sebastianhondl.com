---
layout: post
title: "When Two Player Counts Are Both Right"
date: 2025-12-16
categories: [development, ai]
tags: [claude-code, python, debugging]
read_time: 2
word_count: 514
---

"Your bot's broken—it says 2 players but only shows 1 in the embed."

My friend's message sent me down a debugging rabbit hole. I run a Discord bot for my Minecraft server that displays player counts in two places: the bot's presence status ("Playing: 2 players online") and a detailed embed in a dedicated channel. They were showing different numbers. Classic data inconsistency bug, right?

Not exactly.

## The Two Displays

The bot tracks players in two ways because Discord integration requires it. When someone joins my server, they can use the `/link` command to connect their Discord account to their Minecraft username. This unlocks features: their Discord profile shows in the status embed, they get pinged for server events, and their playtime syncs to a leaderboard.

But not everyone links. Some players just want to mine blocks without Discord integration. The server still knows they're online—it just can't show their Discord identity.

Here's how the code handles each display:

```python
# bot/presence.py
player_info = rcon_client.get_online_players()  # All players from DynamoDB
player_count = player_info['count']
status_text = f"{player_count} players online"
```

```python
# bot/embed.py
players = dynamodb_helper.get_all_linked_players()
online_count = sum(1 for p in players if p['is_online'])
```

The presence counts everyone. The embed counts only linked players. Two people were playing, but only one had linked their account. Both numbers were correct.

## Finding the Culprit

A quick database check revealed the issue: a player named "Buzz" was whitelisted but hadn't linked their Minecraft username to their Discord account. A DynamoDB update fixed the immediate problem:

```bash
aws dynamodb put-item --table-name minecraft-server-whitelist --item '{
    "pk": {"S": "USER#543646641140400138"},
    "sk": {"S": "MAPPING"},
    "discord_username": {"S": "buzz6432"},
    "minecraft_name": {"S": "happy6432"},
    "minecraft_uuid": {"S": "ded12816-206d-4350-b69c-817d1c2def5f"}
}'
```

But manual data entry isn't a real fix—better communication is.

## A Second Problem Lurking

While investigating, I noticed something else in the logs: players occasionally getting kicked during whitelist reloads. The whitelist synchronization between DynamoDB and the Minecraft server has timing windows where connected players can briefly appear unauthorized. That's a problem for another day, but it's now on my list.

## What I Actually Learned

**Distinguish between "accurate" and "useful."** Both player counts were accurate. Neither was useful to someone who didn't understand the linking system. The bot should show "2 online (1 on Discord)" rather than making users puzzle out the discrepancy. More work to implement, less work to explain.

**AI assistants excel at code archaeology.** Claude traced through multiple files and compared both player count implementations faster than I could have found the first relevant function manually. Having a tool that holds the entire codebase in context while you talk through a problem is genuinely useful for this kind of investigation.

## The Takeaway

When you're building systems with multiple views of the same data, document why they might differ. A comment like `# Only counts linked players, use get_all_online() for total` would have saved twenty minutes of investigation.

Sometimes the most valuable debugging sessions end with discovering the code was right all along—you just forgot what you told it to do.