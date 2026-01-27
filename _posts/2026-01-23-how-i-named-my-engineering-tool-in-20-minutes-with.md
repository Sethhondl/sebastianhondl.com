---
layout: post
title: "How I Named My Engineering Tool in 20 Minutes with Claude"
date: 2026-01-23
categories: [development, ai]
tags: [claude-code, git, testing, api, debugging]
read_time: 3
word_count: 731
---

What should you name something that doesn't exist yet?

I've been building an AI assistant that helps engineers run parametric studies—connecting simulation software like MATLAB and Ansys to optimization algorithms without writing custom glue code for each integration. The working title included "MATLAB" directly, which created an obvious problem: I wanted the tool to work with any simulation environment, not just one vendor's ecosystem. A name tied to a single platform would limit perception and positioning from day one.

This is the kind of task that sounds simple but can consume hours of solo brainstorming. So I decided to use Claude as a thinking partner.

## The Collaborative Process

What struck me about this session was how naturally the conversation evolved through constraints. I started with a vague request—"help me name this app"—and Claude responded with a structured exploration across multiple conceptual directions.

Technical metaphors included names like Forge and Anvil, with Claude noting that "Forge" implied building and shaping—fitting for a tool that constructs mathematical models. Connection concepts like Nexus and Conduit emphasized the integration aspect. Abstract options like Flux and Prism aimed for memorability over literal meaning.

Each suggestion came with reasoning I could react to. This wasn't a list dump—it was organized thinking.

## Narrowing Through Iteration

When I said "I like the Nexus and Forge direction," Claude pivoted immediately. Instead of defending other options, it explored that specific territory: Nexforge, Forgex, Forgenix—all blending the concepts I'd responded to.

But I wasn't quite there. I realized I kept gravitating toward terms with mathematical weight, so I asked Claude to focus specifically on that domain. The app is fundamentally about mathematical modeling, and I wanted that identity reflected in the name.

Claude shifted directions entirely, offering options inspired by linear algebra (Eigen, Tensorix), calculus (Derivex, Inflect), and control systems (Laplax, Statespace).

"Gradiant" caught my attention—a deliberate misspelling of "gradient" that creates a portmanteau with "radiant." The altered spelling would help with trademark distinctiveness and domain availability while signaling mathematical sophistication to anyone who noticed the wordplay.

## The Final Refinement

"Gradiant" alone felt incomplete. Claude suggested pairings, including "Gradiant Descent"—a direct reference to the gradient descent optimization algorithm that engineers and ML practitioners would recognize immediately.

I liked the reference, but it felt too on-the-nose, like naming your company "Machine Learning Inc." It was also three words for what should be a single product name.

"Can you find something similar but two syllables?"

The response included compressed alternatives:

| Name | Breakdown | Why It Works |
|------|-----------|--------------|
| Gradive | Grad + dive | Action-oriented, suggests movement |
| Gradix | Gradient + x | Technical, abstract |
| Derivux | Derive + ux | Mathematical root, hints at user experience |

**Derivux** emerged as the winner. "Derive" captures the mathematical essence—derivatives, derivation, deriving solutions from models. The "-ux" suffix subtly suggests user experience without being heavy-handed, and it's more distinctive than "-ive," which appears in countless existing product names.

I checked: derivux.com was available. A quick trademark search showed no conflicts in the software or engineering categories. Sometimes practical validation kills a name you love, but this one survived.

## What I Learned About AI-Assisted Brainstorming

**Start broad, then constrain progressively.** Rather than asking for "the perfect name," I let the conversation reveal my preferences. Each response helped me understand what I actually wanted.

**React honestly to suggestions.** When something didn't land, I said so directly: "I like Gradiant but it needs something else." This gave Claude the signal to iterate rather than defend.

**Use tables for comparison.** Claude's structured tables made it easy to compare options side-by-side. I now ask for this format explicitly in brainstorming sessions.

**Stress-test your favorites.** Once I was leaning toward Derivux, I asked for potential problems: "Too similar to Linux naming conventions?" "Hard to spell from hearing it?" This devil's advocate step caught issues I might have missed.

## The Practical Takeaway

The entire exercise took twenty minutes. I could have spent a full day doing this alone, cycling through the same ideas, second-guessing my instincts. Instead, I had a thinking partner who could generate options faster than I could evaluate them—and who pivoted without ego when I changed direction.

AI assistance isn't just about code. It's about augmenting whatever kind of thinking the moment requires.

**Derivux** it is.