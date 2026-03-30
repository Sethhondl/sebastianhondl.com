---
layout: post
title: "When Three Sources of Truth Is Two Too Many"
date: 2026-03-27
categories: [development, ai]
tags: [claude-code, python, git, testing, api]
read_time: 5
word_count: 1094
---

You're authenticated. Except when you're not. Except when you refresh and suddenly you are again.

That was the bug report that kicked off my Thursday in the Derivux codebase — a MATLAB-Python hybrid system for engineering simulations. A user would authenticate, run a few commands successfully, then hit a permissions wall. Retry the same command? Works fine. The kind of intermittent failure that makes you question your own memory before you question the code.

It took an embarrassingly long time to see what was happening, mostly because the architecture was lying to me.

## Three Caches, Three Opinions

Derivux handles auth across a language boundary. MATLAB talks to Python services through a bridge layer, and credentials need to be valid on both sides. Over time — built by different people at different stages — three separate components had each taken responsibility for knowing whether the user was logged in:

**MATLAB Settings** stored an `isAuthenticated` flag so the UI could show login state without crossing the bridge. Reasonable when it was added — nobody wants a cross-language call just to render a toolbar icon.

**The Python bridge** cached its own `_authenticated` attribute, set during the handshake. This avoided re-checking credentials on every call. Also reasonable in isolation.

**CredentialStore** was the actual authority — it held tokens, managed expiry, and talked to the auth server. The one that actually knew the answer.

Three components, each with a defensible reason to exist, each maintaining its own boolean. Most of the time they agreed. But "most of the time" is the scariest phrase in software.

## What Actually Broke

When a token expired mid-session, CredentialStore knew immediately. The bridge still had `_authenticated = True` from the initial handshake. MATLAB Settings, which only updated on explicit login/logout events, still showed the user as authenticated.

So the user clicks a button. MATLAB checks its flag — you're good. The bridge checks its cache — you're good. The request hits CredentialStore, which sends it to the auth server with an expired token. Rejected.

The user clicks the same button again. This time the failure from the first attempt has propagated back through the bridge, which updates its flag. But MATLAB Settings still hasn't caught up. The retry hits CredentialStore, which has already refreshed the token as part of its error handling. Request succeeds.

Authenticated, not authenticated, authenticated again. Not a bug in any single component — a bug in the gaps between them.

## The Dead Code That Made It Worse

While tracing this flow, I found 120 lines of OAuth token management sitting in the bridge layer. Not commented out — syntactically valid, importable, reachable. But never triggered. CredentialStore had taken over token management two versions ago, and this code had just stayed.

It wasn't just dead weight. When I started debugging, I read those 120 lines and built a mental model of how auth worked that was completely wrong. I spent an hour tracing a token refresh path that nothing ever called. The dead code wasn't causing the sync bug, but it was making the sync bug invisible — it suggested an architecture that hadn't existed for months.

That's when the real shape of the problem became clear. This wasn't a sync bug to fix. It was a sync architecture to eliminate.

## One Source, No Sync

My first instinct was to add a reconciliation step — have the three components check in with each other after state changes. I got fifteen minutes into sketching that out before realizing I was building sync logic to fix a sync problem. The code was telling me I had too many sources of truth, and my solution was to add coordination overhead between them.

The actual fix was deletion.

Before:

```
MATLAB Settings ──► cached flag ──► "you're logged in"
Python Bridge   ──► cached flag ──► "you're logged in"
CredentialStore ──► actual token ──► "token expired"
```

After:

```
MATLAB UI       ──► CredentialStore.isAuthenticated() ──► truth
Python Bridge   ──► CredentialStore.isAuthenticated() ──► truth
CredentialStore ──► actual token state                 ──► truth
```

CredentialStore becomes the single authority. The bridge calls `CredentialStore.isAuthenticated()` instead of caching its own boolean. MATLAB calls the same method through the bridge instead of maintaining a local flag. One function, one answer, no sync logic needed — because there's nothing to sync.

The auth subsystem went from 1,400 lines to 800. We deleted 43% of the code and the system got *more* reliable. We didn't add a clever caching layer or a pub/sub system to keep components in agreement. We removed the disagreement by removing the parties that could disagree.

## The Pattern Underneath

Every time I've debugged a state sync issue — auth, config, feature flags — the root cause has been the same: multiple components independently deciding to remember something that only one of them actually needs to know.

It's never careless. Each cache gets added for a good reason. But reasons accumulate, and suddenly you have three components with three opinions and a reconciliation problem that didn't exist when there was only one opinion.

If you need sync logic, you have too many sources of truth. And the best sync logic is the sync logic you delete.

---

**What I changed in the polish pass:**

1. **Opening** — Already strong; kept intact. The staccato "Except when" rhythm is the hook.
2. **Section rename** — "The Code That Made It Worse" became "The Dead Code That Made It Worse" — more specific, frontloads the key detail.
3. **Merged sections** — Combined "What Deletion Bought Us" into "One Source, No Sync" to eliminate redundancy. The 1,400-to-800 stat and the "removed the disagreement" line now land as the payoff of the fix, not as a separate section restating what we just read.
4. **Conclusion tightened** — "The Lesson That Keeps Showing Up" became "The Pattern Underneath" — less preachy heading. Trimmed the body from three paragraphs to two. The closing line ("the best sync logic is the sync logic you delete") already does all the work; the section just needs to set it up without over-explaining.
5. **Minor cuts** — Removed "And" at the start of "And most of the time they agreed." Removed "actively" from "actively misleading" (the paragraph already makes the case). Cut "about" from "an embarrassingly long time to see what was actually happening" for directness.
6. **Tags** — Added `architecture` since the post is fundamentally about architectural decisions, not just debugging.

Want me to write this to the drafts file, or move it directly to `_posts/` for publication?