---
layout: post
title: "Why Closing a Window Froze MATLAB: A Tale of Git Commands and Missing Timeouts"
date: 2026-01-20
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 3
word_count: 792
---

A user reported that closing my MATLAB Claude integration window froze their entire MATLAB session. Not crashed—frozen. The spinning beach ball of death, requiring a force quit. What started as a simple bug report turned into a lesson about external processes, cross-language coordination, and why every command that touches the filesystem needs a timeout.

## The Setup

I've been building a MATLAB toolbox that lets you interact with Claude directly from the MATLAB environment. It spawns a Python bridge process, displays responses in a custom UI, and integrates with your workspace. The toolbox had been working fine for me, but users on different systems were experiencing complete freezes when they closed the Claude window.

## Tracing the Freeze

The culprit turned out to be the status bar. It displays git information—current branch, additions, deletions—by calling `git diff --numstat HEAD`. On my machine with a small repo on an SSD, this returns instantly. On a user's 50GB monorepo mounted over NFS, it can hang indefinitely.

The sequence of events:

1. User closes the Claude window
2. MATLAB's close callback fires
3. The callback tries to update the status bar one final time
4. `git diff --numstat HEAD` hangs on a slow repository
5. MATLAB's `system()` function blocks, waiting forever for git
6. The entire MATLAB process becomes unresponsive

MATLAB's `system()` function has no built-in timeout. Neither does Python's `subprocess.run()` by default, nor many other standard library process-spawning functions. They trust the child process to finish. That trust is misplaced when network filesystems are involved.

## Adding Timeouts to Git Commands

The fix required wrapping all git calls in a timeout mechanism:

```matlab
function [status, output] = gitWithTimeout(command, timeoutSec)
    if nargin < 2
        timeoutSec = 5;
    end
    
    if isunix
        fullCmd = sprintf('timeout %d %s', timeoutSec, command);
    else
        fullCmd = sprintf('powershell -Command "& {$p = Start-Process -FilePath ''cmd'' -ArgumentList ''/c %s'' -PassThru -NoNewWindow; if (!$p.WaitForExit(%d000)) { $p.Kill(); exit 1 }}"', ...
            strrep(command, '''', ''''''), timeoutSec);
    end
    
    [status, output] = system(fullCmd);
end
```

Now `getGitInfo()` fails gracefully instead of hanging:

```matlab
function info = getGitInfo(obj)
    info = struct('branch', '', 'additions', 0, 'deletions', 0);
    
    [status, branch] = GitUtils.gitWithTimeout('git rev-parse --abbrev-ref HEAD', 2);
    if status ~= 0
        return;  % Not a git repo or timed out—either way, move on
    end
    info.branch = strtrim(branch);
    
    [status, diffStats] = GitUtils.gitWithTimeout('git diff --numstat HEAD', 5);
    if status == 0
        [info.additions, info.deletions] = parseDiffStats(diffStats);
    end
end
```

## Fixing the Shutdown Sequence

The git timeout solved the immediate freeze, but I found a deeper issue: the Python bridge wasn't shutting down cleanly when MATLAB closed the window. The `stop_process()` method set a flag but didn't actually terminate the asyncio event loop.

On the MATLAB side, the fix ensures polling stops before attempting to close the bridge:

```matlab
function closeWindow(obj)
    obj.stopPolling();
    
    if ~isempty(obj.Bridge) && obj.Bridge.isRunning()
        obj.Bridge.shutdown(5.0);
    end
    
    delete(obj.Figure);
end
```

On the Python side, proper shutdown coordination using a lock and explicit loop termination:

```python
def shutdown(self, timeout=5.0):
    with self._shutdown_lock:
        if self._shutdown_requested:
            return
        self._shutdown_requested = True
    
    if self._loop and self._loop.is_running():
        self._loop.call_soon_threadsafe(self._loop.stop)
    
    deadline = time.time() + timeout
    while self._loop and self._loop.is_running():
        if time.time() > deadline:
            break
        time.sleep(0.1)
```

When bridging two languages with different async models, you need explicit shutdown coordination. Python's asyncio event loop doesn't stop just because MATLAB decides to close a window—you have to signal it and wait for acknowledgment.

## A Smaller Fix Along the Way

While debugging, I noticed my Claude Code status line was showing `?t` instead of actual turn counts. The transcript parser was using naive grep:

```bash
TURNS=$(grep -c '"type":"user"' "$TRANSCRIPT_PATH")
```

This produced false positives when a user's message contained that literal string. The fix uses proper JSON parsing:

```bash
TURNS=$(jq '[.[] | select(.type == "user")] | length' "$TRANSCRIPT_PATH" 2>/dev/null)
```

## The Takeaways

**Every external command needs a timeout.** This sounds obvious until you're the developer whose git operations work instantly on a fast SSD. Your users have different environments—network mounts, enormous repos, overloaded CI runners. MATLAB's `system()`, Python's `subprocess`, and similar functions need wrapper code that enforces time limits.

**Cross-language shutdown requires explicit coordination.** When Process A spawns Process B which runs an event loop that makes network calls, closing A doesn't automatically clean up B. You need shutdown signals, acknowledgments, and timeout fallbacks at each boundary.

**Status bars should degrade gracefully.** Dynamic information is valuable, but every piece is a potential freeze if it depends on something slow. Fetch asynchronously when possible, use timeouts always, and show placeholder values when data isn't available.

The freezes are gone. More importantly, I now think differently about external commands. That `git` call that returns in milliseconds on your machine? Someone, somewhere, is waiting five minutes for it to complete. Plan accordingly.