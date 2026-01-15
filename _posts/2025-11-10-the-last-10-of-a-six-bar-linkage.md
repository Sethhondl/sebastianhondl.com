---
layout: post
title: "The Last 10% of a Six-Bar Linkage"
date: 2025-11-10
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 6
word_count: 1293
---

At 2 PM, I had a six-bar linkage optimizer that could find solutions. By 6 PM, I had the same optimizer—plus forty pages of documentation, a cleaned-up repository, and the uncomfortable realization that I'd been enforcing a constraint I'd forgotten existed.

## The Project: Synthesizing Six-Bar Linkages

I'm building a Python tool to synthesize six-bar linkages—mechanisms with six rigid bars connected by rotating joints that can trace specific paths. If you've seen a desk lamp with a parallelogram arm that stays level as you move it, that's a four-bar linkage. Six-bar linkages add two more bars and two more joints, enabling more complex curves—figure-eights, loops with cusps, paths that reverse direction—but the math to design them grows exponentially harder.

The optimizer was already finding solutions. The visualizations were already rendering. But today I needed to:

1. Document all the constraints on the mechanism's "box" workspace
2. Adapt the code from a Watt I topology to a Stephenson I topology
3. Write progress report documentation for an academic deadline

This is the work that doesn't feel like progress until you try to skip it.

## When AI Becomes Your Engineering Notebook

The most useful thing Claude did today wasn't writing code—it was reading my code back to me in a structured way.

I asked Claude to list all the constraints currently implemented for the box workspace. What came back was essentially a comprehensive audit:

```
## BOX CONSTRAINT DEFINITIONS

### 1. Box Bounds Initialization
- Default: (0, 1) - unit square workspace
- Storage: self.box_min = 0, self.box_max = 1

### 2. Ground Pivot Constraints (A and G)
- Both x and y coordinates within [0, 1]
- Penalty: Applied during optimization bounds setup

### 3. All Joints in Box at Start Position
- ALL joints (A, B, C, D, E, F, G) must be within box
- Penalty: 10,000 error units if violated

### 4. No Negative X-Coordinates During Motion
- Checked at 30 points during motion
- Penalty: 500,000 error units - CRITICAL CONSTRAINT
```

That fourth constraint stopped me cold. I'd added it months ago when solutions kept placing joints to the left of the workspace origin, making the mechanism impossible to mount on a physical test rig. Then I'd forgotten about it entirely. The penalty weight (500,000 units, dwarfing everything else) meant it was silently dominating my optimization, potentially rejecting good solutions that only briefly dipped past x=0.

Without this audit, I would have spent tomorrow debugging why certain promising configurations kept getting discarded. Instead, I now have a decision to make: keep the constraint and document why, or relax it and see what new solutions emerge.

## Adapting Kinematic Equations for Different Topologies

The more interesting technical challenge was adapting the solver for Stephenson I linkages. Both Watt I and Stephenson I are six-bar mechanisms with the same number of links and joints, but the connections differ in a way that changes everything about solving them.

In both topologies, you have joints that connect two bars (binary joints) and joints that connect three (ternary joints). In a Watt I linkage, the two ternary joints are connected through intermediate links—like two hubs in a bicycle wheel connected by spokes. In a Stephenson I linkage, one ternary joint is bolted directly to the ground frame. This changes which joints you can solve for first, because you can only calculate a joint's position once you know the positions of the joints constraining it.

Here's the Watt I solving sequence:

```python
def solve_watt_i_position(params, theta2):
    # Start from ground pivot A
    B = euler_to_point(A, L_AB, theta2)              # Input angle determines B
    E = solve_circle_intersection(B, L_EB, G, L_GE)  # E constrained by B and ground
    C = solve_triangle_point(B, E, L_BC, L_CE)       # C fixed relative to B and E
    F = solve_triangle_point(E, G, L_EF, L_FG)       # F fixed relative to E and G
    D = solve_circle_intersection(C, L_CD, F, L_DF)  # D is where the coupler links meet
    return [A, B, C, D, E, F, G]
```

For Stephenson I, the grounded ternary link means the solving order changes completely:

```python
def solve_stephenson_i_position(params, theta2):
    # Ground pivot A drives the input
    B = euler_to_point(A, L_AB, theta2)              # Same as Watt I
    # But now E is part of the grounded ternary link
    C = solve_circle_intersection(B, L_BC, E, L_CE)  # C before F (different order)
    D = euler_to_point(E, L_ED, theta_ternary)       # D constrained by ternary link
    F = solve_circle_intersection(D, L_DF, G, L_GF)  # F comes last
    return [A, B, C, D, E, F, G]
```

Claude's contribution here was systematic: after I explained the difference and sketched diagrams in comments, it identified exactly which functions would need modification and which could remain unchanged. The triangle inequality checks, the visualization loops, the parameter dictionaries—all catalogued with specific line numbers and notes on whether each depended on solving order.

## The Unglamorous Work: Git Hygiene

Half my conversation with Claude today was about repository management—not algorithms.

I'd reorganized directories, deleted old outputs, added new solution folders. The result was a git status with dozens of changes. Claude helped me commit these changes not by writing clever code, but by acting as a sanity check. When I asked it to review the staged changes, it flagged that I was deleting `test_sixbar.py` but not the import statements that referenced it elsewhere. This caught a broken import that would have failed silently until someone tried to run the test suite.

## What Actually Went Wrong

When I first asked Claude to explain the difference between Watt I and Stephenson I topologies, it confidently described Stephenson I as having "both ternary links grounded"—which is actually Stephenson III. I caught this because I had the textbook open, but it's a reminder that AI assistance works best when you're checking its work against authoritative sources, not trusting it as the authority itself.

The error was instructive. It forced me to articulate the topology differences precisely enough that I could correct Claude's description, and that articulation ended up in my progress report almost verbatim.

## What "Done" Means for This Project

The title claims I'm in the "last 10%," which deserves quantification:

- Position analysis for Watt I ✓
- Optimization pipeline for Watt I ✓
- Position analysis for Stephenson I (documented, not implemented)
- Optimization pipeline for Stephenson I (not started)
- Velocity and acceleration analysis (not started)
- Physical prototype validation (not started)

By that measure, I'm maybe 40% done with the full project. But for the deliverable due this week—a progress report demonstrating working Watt I synthesis plus a documented plan for Stephenson I—today's work completed the gap between "code that runs" and "submission I can defend."

## Practical Takeaways

**Code audits surface forgotten assumptions.** I knew I had box constraints. I didn't know I had a 500,000-penalty constraint silently shaping every optimization run. Asking an AI to enumerate what your code actually does—not what you think it does—can reveal these buried decisions.

**Topology isn't just labeling—it's solving order.** When you change which link connects to what in a mechanism, you're not swapping variable names. You're redefining the dependency graph that determines which joints you can solve for at each step.

**Use AI as a sanity check, not an oracle.** Claude caught my orphaned import but hallucinated a topology classification. The pattern is consistent: good at structural analysis of code you show it, unreliable for domain facts you don't verify.

**The last 10% is whatever sits between "works" and "shareable."** Today I wrote zero lines of new algorithmic code. I documented constraints, cleaned up the repository, caught a broken import, and prepared a submission. Tomorrow's Stephenson I implementation will go faster because today's groundwork made the problem legible—to my collaborators, and to future me.