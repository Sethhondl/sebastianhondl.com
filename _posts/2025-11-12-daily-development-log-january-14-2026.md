---
layout: post
title: "Daily Development Log - January 14, 2026"
date: 2025-11-12
categories: [development, ai]
tags: [claude-code, python, automation, testing, debugging]
read_time: 5
word_count: 1165
---

I don't have write permissions for that file. Here's the final polished blog post:

---

```markdown
---
layout: post
title: "Five Polling Loops and Zero Communication: An Architecture Archaeology"
date: 2025-11-15
categories: [development, ai]
tags: [claude-code, python, automation, debugging, refactoring]
read_time: 4
word_count: 950
---

I asked Claude why my Discord bot's status updates felt slow. What I discovered: five independent polling loops that don't talk to each other.

## The Problem That Felt Simple

The bot checks player count every 30 seconds. Join the Discord server, glance at the bot, and you'll see something like "Playing: 3 players online." Except sometimes it lies. A player leaves, and for up to 30 seconds, the bot still shows them as online.

This matters more than I initially admitted. A friend checks Discord to see if I'm playing before launching the game. They see "1 player online," boot up Minecraft, connect—and find an empty server because I'd logged off 25 seconds ago. Minor? Sure. But it's the kind of friction that makes a system feel unreliable.

I figured I'd just add an event listener. Flag goes up, bot reacts instantly. Easy, right?

## What Claude Found Instead

Some background: my Minecraft server runs on two components. An EC2 instance hosts the actual game server plus a Discord bot that handles gameplay features—chat bridging, player notifications, status display. A separate Lambda function manages infrastructure—starting and stopping the EC2 instance on demand, tracking costs. They're different bots because they serve different purposes and have different availability requirements.

After crawling through my codebase, Claude mapped out what I'd actually built. I expected one or two polling loops. Instead:

```
Status updater: every 30 seconds (shows player count in Discord)
Performance monitor: every 5 minutes (alerts if TPS drops)
Chat watcher: every 2 seconds (bridges Minecraft chat to Discord)
Player activity check: every 5 minutes (triggers auto-shutdown after idle)
Lambda startup monitor: every 15 seconds (waits for Minecraft to accept connections)
```

Five different polling loops. Five different timing intervals. Some running on EC2, some on Lambda, none talking to each other.

## Technical Debt Doesn't Announce Itself

It accumulates in 30-second intervals and 5-minute cron jobs until someone asks "why is this slow?" and discovers you've built a machine that constantly asks "are we there yet?" instead of waiting to be told.

The architecture made sense when I built each piece individually. The status updater was my first feature—30 seconds seemed responsive enough. The performance monitor came later when I wanted TPS alerts—5 minutes avoided spam. The chat watcher needed to feel real-time, so 2 seconds. Each decision was reasonable in isolation.

Together? Accidental complexity.

## The Hidden Costs

Claude identified four significant limitations, but one stands out: the Lambda bot can't see Minecraft state—only EC2 instance state. It knows the machine is running but not whether Minecraft actually started.

Picture this: you're at work and want to check if the server is ready for your lunch break session. You ask the Discord bot to start the server. Lambda spins up the EC2 instance and tells you "Server starting!" Then... silence. The Lambda startup monitor polls every 15 seconds, but it's checking whether the EC2 instance is running, not whether Minecraft has finished loading. Meanwhile, the EC2 bot isn't running yet because Minecraft hasn't started. You're left refreshing Discord, wondering if it worked.

The other issues compound this:

- **No shared state** between Lambda and EC2 bots. Each maintains its own view of reality, so they sometimes disagree about what's happening.
- **No notifications for auto-shutdown**. The server quietly stops after 60 minutes of inactivity, but Discord users only find out when they try to connect.
- **Redundant checks**. Both bots independently verify server status. Same data, different timing, different results.

The worst part? I already had webhook infrastructure for some features. The backup script sends Discord notifications when backups complete. The whitelist system uses webhooks for approval flows. The pattern existed—I just never connected the dots.

## What Event-Driven Would Actually Look Like

The alternative isn't magic—it's just inverting the responsibility. Instead of the bot asking "what's the player count?" every 30 seconds, the server announces "player joined" when it happens.

```python
# Instead of polling...
@tasks.loop(seconds=30)
async def update_status():
    players = await rcon_client.get_online_players()
    await update_presence(players['count'])

# ...parse server logs for state changes
def on_log_line(line):
    if "joined the game" in line:
        webhook_notify("player_joined", parse_player(line))
    elif "left the game" in line:
        webhook_notify("player_left", parse_player(line))
```

Here's the kicker: my chat watcher already reads the server logs at 2-second intervals to bridge messages to Discord. It sees join/leave events scroll past—and ignores them. The infrastructure for instant status updates exists. I just never wired it up.

## Why I'm Not Fixing It Yet

Here's my honest assessment: polling works. Users rarely notice a 30-second delay in bot status. The system isn't broken—it's just inelegant.

The real question is opportunity cost. Refactoring five polling loops into an event-driven system means touching every bot feature, updating both Lambda and EC2 code, and testing all the edge cases. That's a weekend project. I could spend that weekend adding features users actually request, like better backup management or mod support.

So I'm being strategic. The changes worth making now:

- **Auto-shutdown notifications** (users actually complain about this—moderate effort, clear value)
- **A "server ready" event** instead of polling RCON during startup (removes the "did it work?" uncertainty)

The full consolidation waits until I add a feature that forces it. I'm considering a "server starting" notification so players know when to connect. Building that on top of polling means adding a sixth timer. Building it event-driven means I finally have to fix the architecture.

## Architecture Archaeology

AI assistants are remarkably good at this kind of excavation. I knew I had polling in multiple places. I didn't know I had five polling loops with overlapping concerns and zero communication between them.

Sometimes the most valuable analysis isn't "here's how to fix it"—it's "here's what you actually built." That map of accidental complexity, the list of what each component can and can't see, the inventory of patterns I'd already established but never connected—that's the insight worth preserving.

The bot still polls. But now I have an honest map of the debt and a clear trigger for when to pay it down.
```

---

**Polish notes:**

- **Opening**: Tightened to a single punchy sentence that delivers the hook immediately
- **Transitions**: Each section flows naturally—problem → discovery → debt framing → costs → solution → prioritization → reflection
- **Conclusion**: Ends on the concrete image of "an honest map" rather than abstract lessons, making it memorable
- **Title**: Strong as-is—"Architecture Archaeology" is distinctive and SEO-friendly alongside the concrete "Five Polling Loops"
- **Tone**: Conversational throughout with self-deprecating moments ("I just never connected the dots") balanced against technical substance
- **Redundancy**: Removed any lingering repetition; the "sixth timer" appears once as the decision trigger
- **Readability**: Short paragraphs, concrete examples (the lunch break scenario), and code that illustrates rather than overwhelms