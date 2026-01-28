---
layout: post
title: "Building a MATLAB-Claude Bridge (Plus Git Workflow Housekeeping)"
date: 2026-01-16
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 5
word_count: 1105
---

What if your MATLAB IDE could understand natural language? Not through some clunky external tool, but as a native conversation partner that sees your workspace, analyzes your plots, and remembers what you discussed three questions ago. That's what I spent January 16th building—an extension that embeds Claude directly into MATLAB's environment.

I also handled some git workflow setup in the morning, but let me start with the main event.

## The Vision: Claude as a Native MATLAB Companion

Claude Code is an AI coding assistant that works in the terminal, helping developers write, debug, and understand code through natural conversation. My goal is to bring this same experience into MATLAB's IDE—not as a bolt-on tool that feels foreign, but as something that belongs there. Mechanical engineers working in MATLAB should be able to ask Claude for help debugging a matrix operation or understanding a Simulink model without leaving their workflow.

This vision drove all the architectural decisions that followed.

## Deep Dive: Building the Bridge

The integration spans four layers, each translating between different domains:

```
MATLAB UI (JavaScript/HTML in webwindow)
       ↓
ChatUIController.m (MATLAB)
       ↓
MatlabBridge (Python) 
       ↓
MatlabAgent (Claude Agent SDK)
       ↓
Claude API
```

MATLAB handles UI events and workspace context. The Python layer manages the Claude Agent SDK integration and MCP (Model Context Protocol) tools—Anthropic's standard for giving AI assistants access to external capabilities like executing code or reading files. The JavaScript layer renders the chat interface.

### Giving Claude Eyes into MATLAB

A key architectural decision was how to make Claude context-aware. When a user asks Claude to help debug why their plot looks wrong, Claude needs to actually see the plot. When they ask about a matrix operation, Claude should know what variables exist in the workspace.

I built three context providers:

- **Current working directory** via the `matlab_execute` tool
- **Workspace variables** through `WorkspaceContextProvider`  
- **Open Simulink models** via `SimulinkBridge`

The workspace context provider iterates through MATLAB's workspace, extracts each variable's name, type, and dimensions, then formats this as markdown:

```
Current MATLAB Workspace:
- myMatrix (double): 3x3 matrix
- dataTable (table): 100 rows × 5 columns
- results (struct): 4 fields
```

Now when I ask "help me debug this matrix multiplication," Claude can respond with: "I can see you have a 3x3 matrix called `myMatrix` in your workspace. What operation are you trying to perform with it?" That grounding in actual workspace state makes the assistance dramatically more relevant.

### Handling MATLAB Plots

The `matlab_plot` tool returns base64-encoded images that Claude can analyze:

```python
@mcp_server.tool()
async def matlab_plot(code: str, format: str = "png"):
    """Execute MATLAB plotting code and return the figure."""
    result = await matlab_bridge.execute(code)
    temp_path = save_current_figure(format)
    
    with open(temp_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    return {
        "type": "image",
        "media_type": f"image/{format}",
        "data": image_data
    }
```

The tool infrastructure works—what's missing is the JavaScript UI actually rendering those images. The raw base64 data comes back but doesn't display yet. That's on the backlog.

### The Conversation Memory Problem

I noticed something frustrating during testing. I'd ask Claude about a sine wave plot, get a helpful response, then ask a follow-up—and Claude would have no memory of what we'd just discussed. Each message started fresh.

Tracing through the code revealed three culprits:

1. The Python bridge clears all state on each new message
2. The Claude SDK client gets created fresh each time
3. No conversation history gets passed to subsequent queries

This is default SDK behavior—each request is stateless unless you explicitly maintain and pass conversation history. The fix requires maintaining a conversation thread in the `MatlabAgent` class, accumulating messages with each new request. Another backlog item, but now I understand exactly what needs to change.

## Git Workflow Housekeeping

Before diving into MATLAB work, I handled some git-related setup that's worth documenting.

### Severson Group Git Standards

I'm doing a directed study with the Severson Research Group, and they have specific conventions. I created a CLAUDE.md file documenting their workflow:

- **Commit messages**: 72-character max line length, imperative present tense ("make xyzzy do frotz" not "I changed xyzzy")
- **Branch strategy**: `master` for stable releases, `develop` for beta work, topic branches for features
- **Critical rule**: Never rebase, squash, or amend commits already pushed to the server

These standards now live in the project's CLAUDE.md, so Claude follows them automatically.

### Customizing Git Attribution

By default, Claude Code adds a "Co-authored-by" line to commits. For clean commit history in academic contexts, I wanted commits to show only me as the author.

The fix: adding an `attribution` block to `~/.claude/settings.json`:

```json
{
  "attribution": {
    "commit": ""
  }
}
```

Setting the attribution to an empty string removes the co-author line entirely.

### Git Worktrees for Parallel Development

I set up git worktrees to manage multiple features simultaneously:

```bash
git worktree add ../feature-side-panel feature/side-panel
git worktree add ../feature-conversation-memory feature/conversation-memory
```

This creates separate working directories for different branches. I can have one Claude Code session working on the side panel UI while another explores conversation memory in a different directory. No stashing, no branch switching, no merge conflicts from half-finished work.

For a project with multiple exploratory features where I'm not sure which approach will pan out, this isolation is invaluable.

## What I Learned About AI-Assisted Integration Development

Building this bridge surfaced a few patterns worth sharing:

**Context is everything.** Generic coding assistants are helpful. An assistant that sees your actual workspace variables, your current figure, your open files—that's transformative. The effort to build context providers pays off in assistant quality.

**Trace state through every layer.** When the AI "forgets" things, the bug isn't in the AI—it's in how you're managing conversation state. My memory issue wasn't a Claude limitation; it was me not passing history to the SDK.

**AI assistants surface architectural gaps.** Building a Claude integration forced me to think about how MATLAB exposes its internal state, how to serialize that state for an external process, and where sync and async boundaries lie. These questions matter for any integration, but an AI assistant makes you answer them explicitly.

**Document conventions in CLAUDE.md.** Claude follows whatever workflow you document. This is more reliable than hoping the AI infers your preferences.

**Worktrees deserve more attention.** Isolated environments for experimental features mean you can explore aggressively. If an approach doesn't work, delete the worktree and move on.

---

The infrastructure is coming together. Next up: tackling conversation memory and exploring whether MATLAB can host a docked side panel rather than a separate window. The goal remains the same—make Claude feel like it belongs in MATLAB, not like a visitor.