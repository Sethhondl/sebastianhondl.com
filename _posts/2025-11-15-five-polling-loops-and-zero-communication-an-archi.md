---
layout: post
title: "Five Polling Loops and Zero Communication: An Architecture Archaeology"
date: 2025-11-15
categories: [development, ai]
tags: [claude-code, python, automation, debugging, refactoring]
read_time: 3
word_count: 799
---

My Discord bot updates its presence status to show how many players are on my Minecraft server. Simple feature, simple implementation—or so I thought until I asked Claude about making it faster and discovered I'd accidentally built five independent timers all doing versions of the same work.

## The Problem That Felt Simple

The bot checks player count every 30 seconds. Join the Discord server, glance at the bot, and you'll see something like "Playing: 3 players online." Except sometimes it lies. A player leaves, and for up to 30 seconds, the bot still shows them as online.

This matters more than I initially admitted. A friend checks Discord to see if I'm playing before launching the game. They see "1 player online," boot up Minecraft, connect—and find an empty server because I'd logged off 25 seconds ago. Minor? Sure. But it's the kind of friction that makes a system feel unreliable.

I figured I'd just add an event listener. Flag goes up, bot reacts instantly. Easy, right?

## What Claude Found Instead

After crawling through my codebase, Claude mapped out what I'd actually built. I expected one or two polling loops. Instead:

```
Status updater: every 30 seconds
Performance monitor: every 5 minutes  
Chat watcher: every 2 seconds
Player activity check: every 5 minutes
Lambda startup monitor: every 15 seconds (during boot only)
```

Five different polling loops. Five different timing intervals. Some running on EC2, some on Lambda, none talking to each other.

Technical debt doesn't announce itself. It accumulates in 30-second intervals and 5-minute cron jobs until someone asks "why is this slow?" and discovers you've built a machine that constantly asks "are we there yet?" instead of waiting to be told.

The architecture made sense when I built each piece individually. The status updater was my first feature—30 seconds seemed responsive enough. The performance monitor came later when I wanted TPS alerts—5 minutes avoided spam. The chat watcher needed to feel real-time, so 2 seconds. Each decision was reasonable in isolation.

Together? Accidental complexity.

## The Hidden Costs

Claude identified four significant limitations:

1. **The Lambda bot can't see Minecraft state**—only EC2 instance state. It knows the machine is running but not whether Minecraft actually started.

2. **No shared state** between Lambda and EC2 bots. Each maintains its own view of reality.

3. **No notifications for auto-shutdown**. The server quietly stops after 60 minutes of inactivity, but Discord users only find out when they try to connect.

4. **Redundant checks**. Both bots independently verify server status. Same data, different timing, different results.

The worst part? I already had webhook infrastructure for some features. The backup script sends Discord notifications when backups complete. The whitelist system uses webhooks for approval flows. The pattern existed—I just never connected the dots.

## What Event-Driven Would Actually Look Like

The alternative isn't magic—it's just inverting the responsibility:

```python
# Instead of polling...
@tasks.loop(seconds=30)
async def update_status():
    players = await rcon_client.get_online_players()
    await update_presence(players['count'])

# ...push state changes
def on_player_join(player_name):
    webhook_notify("player_joined", player_name)
    
def on_player_leave(player_name):  
    webhook_notify("player_left", player_name)
```

Minecraft server logs already emit join/leave events. The chat watcher reads them at 2-second intervals. I could trigger status updates from those same events instead of running a separate polling loop.

## Prioritizing the Fix

Here's my honest assessment: polling works. Users rarely notice a 30-second delay in bot status. The system isn't broken—it's just inelegant.

But Claude's analysis gave me a clear prioritization framework:

**High value, low effort:**
- Add webhook notifications for auto-shutdown (users actually complain about this)
- Emit a "server ready" event instead of polling RCON during startup

**High value, moderate effort:**
- Share state between Lambda and EC2 through DynamoDB so they stop maintaining separate views of reality

**Lower priority:**
- Consolidate the five polling loops into event-driven reactions (significant refactor, marginal user benefit)

The trigger for actually making these changes? When I add the next feature that needs real-time state. Right now I'm considering a "server starting" notification so players know when to connect. Building that on top of polling would mean adding a sixth timer. Building it event-driven means I finally have to fix the architecture.

## The Real Lesson

AI assistants are remarkably good at architecture archaeology. I knew I had polling in multiple places. I didn't know I had five polling loops with overlapping concerns and zero communication between them.

Sometimes the most valuable analysis isn't "here's how to fix it"—it's "here's what you actually built." That map of accidental complexity is worth the conversation alone.

The bot still polls. But now I know exactly where the debt lives, I have a prioritized plan, and I know what will finally force me to pay it down: the next feature that makes six timers feel absurd.