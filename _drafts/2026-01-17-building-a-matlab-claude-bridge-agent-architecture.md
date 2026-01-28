---
layout: post
title: "Building a MATLAB-Claude Bridge: Agent Architecture and Evaluation Foundations"
date: 2026-01-17
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 4
word_count: 913
---

What happens when you give engineers an AI assistant that actually understands their workflow? That's the question driving **matlabClaude**, a toolbox integrating Claude directly into MATLAB and Simulink. Today's work split across three areas: laying groundwork for an evaluation framework, squashing a configuration bug, and designing a system of specialized agents.

## Why an Evaluation Framework Matters

When building an AI assistant for a technical domain, "it usually works" isn't good enough. I needed a systematic way to answer: Does the assistant generate syntactically valid MATLAB? Does it choose idiomatic approaches over technically-correct-but-weird ones? Does it explain its work or just dump code?

Without measurements, I'd be flying blind—unable to tell if prompt changes actually improved responses or just felt better in a few hand-tested examples.

The approach uses two separate Claude instances: one as the system under test, another as the judge scoring responses against specific criteria.

Here's how an evaluation prompt looks:

```
## User Prompt
Create a 5x5 identity matrix in MATLAB and store it in a variable called I

## Evaluation Criteria
1. Uses the eye(5) function or equivalent approach
2. Code is syntactically valid MATLAB
3. The response explains what an identity matrix is or what the code does
```

The evaluator returns structured JSON with pass/fail status, scores, and reasoning. This creates a repeatable way to measure whether the assistant does what users need—not just whether it generates plausible-looking code.

I built initial test cases covering fundamentals: identity matrices, vectors with specific step sizes, bar charts, sine wave plots, and solving linear systems:

```matlab
% Test case: Solving 2x + 3y = 8, 4x + y = 6
% Expected approach: matrix left division
A = [2 3; 4 1];
b = [8; 6];
solution = A \ b  % Should return [1; 2]
```

The evaluation framework scores whether the assistant uses the idiomatic backslash operator versus something clunkier like `inv(A) * b`, and whether it explains why left division is preferred.

This is still early—I haven't run systematic evaluations yet. The next step is building more test cases and establishing baseline scores.

## A Configuration Bug That Blocked Progress

While setting up the test environment, I hit an error that stopped everything:

```
Failed to parse JSON file: File schema must be exactly three 
nonnegative integers separated by '.'s.
```

The culprit was `functionSignatures.json`, which helps MATLAB provide tab completion. The fix was trivial—change line 2 from:

```json
"_schemaVersion": 1,
```

to:

```json
"_schemaVersion": "1.0.0",
```

MATLAB expects semantic versioning as a string, not an integer. I spent more time finding this than fixing it. The lesson: when a tool complains about format, check the exact specification rather than assuming what "version 1" means.

## Designing Specialized Agents

The more ambitious work involved planning specialized agents. Different tasks benefit from different system prompts and capabilities:

- **Git Agent** — handles version control interactions
- **Simulink Agent** — focuses on model manipulation  
- **Code Writer Agent** — generates MATLAB code
- **Code Reviewer Agent** — critiques and improves code

The matlabClaude architecture has a Python backend managing Claude interactions, with MATLAB providing the user-facing API. The agent system uses a base class pattern:

```python
class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "MyCustomAgent"
        self.priority = 50  # Lower = higher priority
    
    def can_handle(self, message: str) -> bool:
        return message.startswith("mycommand")
    
    def handle(self, message: str, context: dict) -> str:
        return "Response"
```

This interceptor pattern with priorities provides flexibility, but I'm still working through routing design. Should "help me commit this code" go to the Git Agent or the general assistant?

My current thinking: use explicit prefixes for now (like `@git commit`) rather than detecting intent from message content. Explicit routing is less magical but more predictable—users know exactly which agent handles their request. I can revisit implicit routing once I have data on how people actually phrase requests.

## Investigating a Ghost Bug

A bug report mentioned that after clicking "Clear" to start a fresh conversation, the system would show "Claude thinking" but never respond. I couldn't reproduce it consistently, but traced through the code to understand the full clear flow:

1. **JavaScript** clears the DOM and resets `window.chatState`
2. **MATLAB** clears `obj.Messages` and calls `obj.PythonBridge.clear_conversation()`
3. **Python** stops the running agent and creates a fresh `MatlabAgent()` instance

The architecture correctly resets state across all three layers. Since the bug isn't reproducing, I documented where to look if it resurfaces: the async event loop handling in `_reset_agent_async()` has a `try/except` that silently catches timeout errors, which might mask connection issues.

Sometimes debugging means building understanding for later rather than shipping a fix today.

## What I Learned

**On evaluation**: Having Claude evaluate responses creates a feedback loop, but only if criteria are specific. "Good code quality" is useless; "uses idiomatic MATLAB functions" is actionable.

**On multi-layer debugging**: When investigating "nothing happens" issues, I traced through JavaScript events, MATLAB callbacks, Python bridge methods, and agent lifecycle separately. Drawing out the flow before diving into code saved time.

**On configuration**: Always check what format a tool expects. "Version 1" and "1.0.0" mean the same thing to humans but not to parsers.

**On agent design**: Explicit routing beats implicit detection—at least until you have real usage data to guide smarter routing.

Next up: running the evaluation framework against the current assistant to establish baseline scores. That will reveal whether the specialized agent prompts I'm designing actually improve responses—or just add complexity.