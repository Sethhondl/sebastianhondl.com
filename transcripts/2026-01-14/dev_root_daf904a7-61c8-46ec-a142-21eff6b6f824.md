# Claude Conversation Transcript

---

## User [2026-01-14T17:30:14.886Z]

I would like to have my default tmux window to be 2x2 open to the same direcotry location

## Assistant [2026-01-14T17:30:20.100Z]

I'll help you set up tmux to open with a 2x2 pane layout. Let me first check if you have an existing tmux configuration.

## User [2026-01-14T17:30:22.854Z]

[Tool Result:      1→set -g mode-keys vi
     2→set -g mouse on
     3→
     4→

]

## Assistant [2026-01-14T17:30:34.050Z]

You have an existing tmux config. There are two main approaches to get a 2x2 layout by default:

**Option 1: Add a hook to your tmux.conf** (automatic for every new session)

**Option 2: Create a shell alias/function** (run when you want the layout)

Which would you prefer? The hook makes every new tmux session start with 2x2 panes automatically, while the alias gives you more control over when to use it.

Here's what the hook approach would look like added to your config:

```bash
# Create 2x2 layout on new session
set-hook -g after-new-session 'split-window -h; split-window -v; select-pane -t 0; split-window -v; select-pane -t 0'
```

Want me to add this to your `~/.tmux.conf`?

## User [2026-01-14T17:31:31.102Z]

Let's add a hook to tmux.conf.

## User [2026-01-14T17:31:38.933Z]

[Tool Result: The file /Users/sethhondl/.tmux.conf has been updated. Here's the result of running `cat -n` on a snippet of the edited file:
     1→set -g mode-keys vi
     2→set -g mouse on
     3→
     4→# Create 2x2 layout on new session
     5→set-hook -g after-new-session 'split-window -h; split-window -v; select-pane -t 0; split-window -v; select-pane -t 0'
     6→
     7→]

## Assistant [2026-01-14T17:31:43.391Z]

Done. The hook is now in your config. To apply it:

- **New tmux sessions** will automatically use the 2x2 layout
- **Existing sessions**: run `tmux source-file ~/.tmux.conf` to reload, but the hook only triggers on *new* sessions

Start a new tmux session with `tmux new` to see the 2x2 grid.

## User [2026-01-14T17:31:56.468Z]

Can you run T-MUX to reload existing sessions?

## User [2026-01-14T17:32:03.959Z]

[Tool Result: ]

## Assistant [2026-01-14T17:32:08.649Z]

Done. The config is reloaded. Note that the `after-new-session` hook will only create the 2x2 layout when you start a **new** tmux session - it won't change your current windows. Start a new session with `tmux new -s <name>` to see it in action.

