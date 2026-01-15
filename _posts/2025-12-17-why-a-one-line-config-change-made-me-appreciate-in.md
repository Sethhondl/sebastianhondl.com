---
layout: post
title: "Why a One-Line Config Change Made Me Appreciate Infrastructure as Code"
date: 2025-12-17
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 4
word_count: 808
---

"Flying is not enabled on this server."

That message appeared in my Discord three times yesterday, each from a different player, each accompanied by growing frustration. They weren't cheating. They weren't using fly hacks. They were just trying to land after an elytra glide, or experiencing a lag spike that made the server briefly lose track of their position. And the server's anti-cheat was kicking them for it.

## The Problem: False Positives Killing the Fun

Minecraft's built-in flight detection is blunt. When the server notices a player's position doesn't match expected physics—feet not touching ground when they should be—it assumes cheating and kicks them. But plenty of legitimate gameplay triggers this:

- **Elytra landings**: The transition from gliding to walking can desync briefly
- **Lag spikes**: Network hiccups cause position updates to arrive late, making it look like you're floating
- **Certain mods**: Some client-side mods (even allowed ones) can cause momentary position mismatches
- **Chunk loading delays**: Sometimes the ground literally isn't loaded yet on the server's end

My players were getting kicked constantly. For a private server where I trust everyone, disabling the check was the right call.

## Finding the Fix with Claude Code

I knew this was a server.properties issue, but I couldn't remember the exact property name or where the template lived in my infrastructure repo. So I described the symptom:

> "Can you modify the minecraft server properties and turn off the player flight check that keeps kicking people."

Claude searched the codebase with a glob pattern for `**/server.properties*` and found three matches: the actual template in `templates/server.properties.template`, an example file in the docs, and a backup. It read the template, identified `allow-flight=false` as the culprit, and proposed the change.

The diff:

```diff
 # Player Settings
 max-players=10
 pvp=true
-allow-flight=false
+allow-flight=true
 player-idle-timeout=0
```

One boolean. That's it.

## Applying the Change

Claude offered two deployment paths:

**Option 1: Direct update on the running server**
```bash
ssh -i minecraft-server-key.pem ec2-user@$(./scripts/get-server-ip.sh) \
  "sudo sed -i 's/allow-flight=false/allow-flight=true/' /minecraft/server.properties && \
   sudo systemctl restart minecraft"
```
Immediate fix, about 30 seconds of downtime for the restart. The `get-server-ip.sh` script queries AWS for the current EC2 instance IP since I use spot instances that change addresses.

**Option 2: Commit the template change and redeploy**
```bash
git add templates/server.properties.template
git commit -m "Enable allow-flight to prevent false kick positives"
./deploy.sh
```
Takes longer (2-3 minutes) but updates the source of truth so future deployments have the correct setting automatically.

I did both: direct update for immediate relief, then committed the template change so it persists.

## Why This Worked So Smoothly

This quick fix worked because of decisions I made when first setting up the project. Having a `server.properties.template` file in version control means:

- **Configuration is searchable**: Claude found it in seconds instead of me SSHing around
- **Changes are reviewable**: Git history shows when this changed and why
- **New deployments inherit the fix**: Spin up a fresh server, it just works
- **Documentation lives next to code**: Comments in the template explain each setting

Without infrastructure-as-code, I'd have needed to remember which instance was running, SSH in, find the right directory, make the change, and probably forget to document it anywhere. That's the difference between infrastructure-as-code and "infrastructure-as-whatever-I-did-last-time."

## Tradeoffs Worth Noting

Setting `allow-flight=true` disables the server's only built-in flight detection. On a private server with trusted players, this is fine. On a public server, you'd want something smarter:

- **Anti-cheat plugins** like NoCheatPlus or Spartan detect actual flight hacks while ignoring false positives
- **Permissions-based flight** can whitelist specific players or ranks
- **Movement monitoring** plugins kick only after sustained impossible movement, not momentary glitches

For my use case—a small server with friends—the simple fix was the right fix.

## Verification

I watched the server logs for the next hour. Previously I'd see 3-5 "kicked for flying" entries per session. After the change: zero. One player specifically tested it with aggressive elytra maneuvers that had gotten them kicked before. No issues.

## The Takeaway

The actual "coding" here was changing one word from `false` to `true`. But the value wasn't in the keystroke—it was in tracing a vague symptom to its root cause, navigating a project with dozens of files to find the right one, understanding deployment options and their tradeoffs, and knowing when a simple fix is the appropriate fix.

That's the pattern I keep seeing with AI-assisted development: it's most valuable for routine tasks with hidden complexity. Not writing thousands of lines of novel code, but confidently handling the small changes that require knowing your codebase, understanding context, and getting the details right.

The players stopped getting kicked. The template is updated for future deployments. And now I have documentation for the next time I forget what `allow-flight` actually does.