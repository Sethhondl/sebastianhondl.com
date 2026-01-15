---
layout: post
title: "When File-Based Detection Lies: Switching to RCON for Minecraft Server Status"
date: 2025-11-20
categories: [development, ai]
tags: [claude-code, python, git, testing, api]
read_time: 5
word_count: 1099
---

My Minecraft server was running. The PID file proved it. And yet, the server wasn't running at all.

This paradox cost me a week of intermittent debugging before I understood what was actually happening: I'd been asking the wrong question entirely.

## The Symptom: A Silent Status Bar

I run a Minecraft server on AWS with a Discord bot that displays player count in its status line—that little "Playing: 2 players online" text beneath the bot's name. One day I noticed it had gone blank. The bot was online, the chat bridge worked fine, but the status showed nothing.

My first instinct was to check git history. The status had worked before, so something must have changed. A quick search found it: a cleanup commit had removed the `status_updater` task along with 270 other lines of "outdated" code. Classic over-aggressive refactoring.

I restored the code. The status stayed blank.

This is when the real debugging began.

## The Original Detection: Trusting a File

The status update logic depended on knowing whether the server was running. Here's what that check looked like:

```python
def is_server_running(self):
    """Check if server is running via PID file"""
    pid_file = Path("/var/run/minecraft/server.pid")
    if not pid_file.exists():
        return False

    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, 0)  # Signal 0 just checks if process exists
        return True
    except OSError:
        return False
```

This seemed bulletproof. The PID file gets created when the server starts and contains the process ID. The `os.kill(pid, 0)` trick verifies the process is still alive without actually killing it. If both checks pass, the server is running.

Except "the process is alive" and "the server is accepting players" are fundamentally different things.

## The Zombie State: When Java Lives But Minecraft Dies

Minecraft servers are Java applications, and Java processes can enter a zombie state where the JVM is technically running but the game server inside has crashed or hung. This happens more often than you'd expect:

- **Plugin crashes**: A badly-written mod throws an unhandled exception in the main tick loop
- **Memory exhaustion**: The heap fills up, GC thrashes endlessly, but the process never exits
- **Network stack failures**: The server socket dies but the main thread keeps spinning
- **Deadlocks**: Two threads waiting on each other indefinitely

In all these cases, the PID file exists, `os.kill(pid, 0)` succeeds, and my detection logic reports "server running." But try to connect as a player and you'll timeout.

The status updater would call `is_server_running()`, get `True`, then try to query player count via RCON—which would fail silently because the RCON subsystem was part of the crashed server. The code handled RCON failures by simply not updating the status, leaving the Discord status bar empty.

I had a detection method that perfectly detected the wrong thing.

## The Fix: Ask the Server Directly

The insight seems obvious in retrospect: if you want to know whether a Minecraft server can serve players, ask it to serve something.

```python
def is_server_running(self):
    """Check if server is running by attempting RCON connection"""
    try:
        with MCRcon(self.host, self.password, port=self.port) as mcr:
            mcr.command("list")
            return True
    except Exception:
        return False
```

RCON (Remote Console) lets you send commands to a running server. If the server responds to a `list` command, it's genuinely operational—not just a living process, but an actual functioning game server. If RCON fails, we know the server can't handle players either.

This changes the question from "is the process alive?" to "is the server healthy?"

## Verifying the Fix

I didn't want to just deploy and hope. To confirm RCON-based detection would catch zombie states, I simulated one:

```bash
# Find the Minecraft server process
$ pgrep -f "minecraft_server"
12345

# Pause it (simulates a hung server)
$ kill -STOP 12345

# Test detection
$ python -c "from rcon_client import RconClient; print(RconClient().is_server_running())"
False

# Resume the server
$ kill -CONT 12345
```

The PID file check would have said "running." The RCON check correctly identified the frozen server as non-functional.

## The Implementation

With the core detection fixed, I updated the status updater:

```python
@tasks.loop(seconds=30)
async def status_updater():
    """Update Discord status with player count from RCON"""
    if not rcon_client.is_server_running():
        await client.change_presence(
            activity=discord.Game(name="Server offline"),
            status=discord.Status.idle
        )
        return

    player_info = rcon_client.get_online_players()
    if player_info['success']:
        count = player_info['count']
        status_text = f"{count} player{'s' if count != 1 else ''} online"
        await client.change_presence(
            activity=discord.Game(name=status_text),
            status=discord.Status.online
        )
    else:
        logger.warning(f"RCON player query failed: {player_info.get('error')}")
        await client.change_presence(
            activity=discord.Game(name="Status unavailable"),
            status=discord.Status.dnd
        )
```

Three states now, each with appropriate Discord status colors:
- **Green (online)**: Server running, show player count
- **Yellow (idle)**: Server offline
- **Red (do not disturb)**: Server running but RCON failed

The logging matters. The original code failed silently. Now failures get logged with context.

## The Broader Lesson: Presence Isn't Health

This session crystallized a principle I keep relearning: **presence isn't health**.

A process existing doesn't mean it's functioning. A file being present doesn't mean it contains valid data. A network connection being open doesn't mean messages are being processed. A service responding to health checks doesn't mean it can handle real requests.

The PID file approach took ten lines of code and worked for months. But it encoded an assumption—"process alive equals server working"—that failed exactly when it mattered most: when the server was in trouble.

## Practical Takeaways

**For Minecraft server operators**: Use RCON for health checking. The `list` command is lightweight and definitively answers "is the server accepting commands?" File-based checks can supplement but shouldn't be primary.

**For anyone building monitoring**: Test your detection methods against failure modes, not just happy paths. My PID file check worked when the server was healthy or completely dead. It failed on partial failures—exactly when good detection matters most.

**For debugging silent failures**: When restored code doesn't work, the bug is in your assumptions. I spent an hour re-reading the status updater looking for bugs. The actual bug was in a different file entirely, in a function that appeared to work but answered the wrong question.

## Conclusion

The status bar works now. More importantly, it fails loudly—if something goes wrong, I'll see it in logs and in the Discord status itself, not as mysterious blankness.

The irony: I thought I was debugging a Discord bot issue. I was actually debugging a philosophy-of-detection issue that happened to manifest in a Discord bot. The same flawed thinking—trusting presence over health—could appear in database connections, API clients, or any system where "the thing exists" differs from "the thing works."

Now I know to ask: what am I actually detecting? And is that what I actually need to know?