---
layout: post
title: "The Last 10% of a Six-Bar Linkage"
date: 2025-11-09
categories: [development, ai]
tags: [claude-code, python, git, testing, api]
read_time: 5
word_count: 1003
---

The moment I realized something was wrong came when I zoomed in on my animation. The mechanism's output link was tracing a beautiful curve through five waypoints, then stopping just short of the sixth—the one that actually mattered. After three days of work, my linkage solver was 95% of the way there, which in mechanism design means it didn't work at all.

## What's a Six-Bar Linkage, Anyway?

A six-bar linkage is a mechanism made of six rigid links connected by rotating joints. Think of it as a more sophisticated cousin of the four-bar linkages you see in car suspensions or folding chairs. The extra links give you more control over the output motion—you can design paths that would be impossible with simpler mechanisms. In my case, I needed the output link (the "coupler") to pass through six specific positions in space as part of a class project on advanced mechanism synthesis.

The challenge is that these six positions aren't independent wishes—they're geometric constraints that the mechanism either satisfies or doesn't. There's no partial credit in kinematics.

## When "Close Enough" Isn't

The problem was deceptively simple. My optimization code would find solutions that hit all five intermediate waypoints with impressive precision. But the sixth position—the endpoint where the mechanism needed to finish its motion—would get tantalizingly close and then just stop short.

Mechanical linkages don't care about your optimization algorithm's feelings. If the geometry says the mechanism can't physically reach a position, it won't. At certain configurations, the circles that define joint positions simply don't intersect. The math constrains what's possible, and no amount of clever coding can violate trigonometry.

The core solver looked clean enough:

```python
def solve_linkage_position(params, theta2):
    """Solve for all joint positions given input angle theta2."""
    A = params['A']  # Fixed ground pivot
    G = params['G']  # Second fixed ground pivot
    
    # Calculate each joint position in sequence
    B = euler_to_point(A, params['L_AB'], theta2)  # Input crank tip
    E = solve_circle_intersection(B, params['L_EB'], G, params['L_GE'])
    C = solve_triangle_point(B, E, params['L_BC'], params['L_CE'])
    F = solve_triangle_point(E, G, params['L_EF'], params['L_FG'])
    D = solve_circle_intersection(C, params['L_CD'], F, params['L_DF'])  # Output point
    
    return {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G}
```

Each function call solves for where two circles intersect or where a triangle's third vertex must be given two sides and two known vertices. When any of these geometric constructions become impossible—circles too far apart to intersect, triangles that can't close—the solver fails for that input angle. Point D is the output I care about; it needs to reach all six target positions as the input angle theta2 sweeps through its range.

## The Range-Finding Problem

The real issue lived in how I was determining the valid angle range for the input crank:

```python
def find_valid_angle_range(params, start_angle=0.0, angle_step=0.01):
    """Find the valid angle range by stepping until geometry fails."""
    forward_limit = start_angle
    angle = start_angle + angle_step
    while angle < 2 * np.pi:
        try:
            solve_linkage_position(params, angle)
            forward_limit = angle
            angle += angle_step
        except:  # Geometry became impossible
            break
    return forward_limit
```

This brute-force approach steps through angles until the geometry fails. It's not sophisticated, but it finds where the mechanism locks up. The problem was that my optimization wasn't penalizing solutions that had their valid range end *before* reaching the target endpoint.

The optimizer was finding linkages that looked great on paper—low error at positions one through five—but couldn't physically complete their intended motion to position six.

## What Claude Code Actually Helped With

I asked Claude to help ensure the solution "always gets close to the endpoint," and the response was to first understand the problem space before proposing fixes. This is the pattern I've noticed in effective AI-assisted debugging: don't jump to solutions, map the territory first.

The conversation started with Claude examining the kinematic solver, the angle range finder, and the optimization objective function. Only after understanding how all three pieces interacted did we discuss modifications.

The fix involved adding endpoint proximity as a hard constraint rather than a soft penalty:

```python
def is_valid_candidate(params, target_positions):
    """Reject candidates that can't reach the final target position."""
    final_target = target_positions[-1]
    valid_range = find_valid_angle_range(params)
    
    # Check if mechanism can get within tolerance of endpoint
    for angle in np.linspace(0, valid_range, 100):
        try:
            positions = solve_linkage_position(params, angle)
            if distance(positions['D'], final_target) < ENDPOINT_TOLERANCE:
                return True
        except:
            continue
    return False  # Can't reach endpoint; reject entirely
```

If a candidate linkage can't reach within a specified tolerance of the endpoint, it gets rejected entirely rather than scored poorly.

**Sometimes the best optimization tweak isn't adjusting weights—it's changing what's even allowed to compete.**

This reframing turned a frustrating near-miss problem into a clean filter. Bad candidates get eliminated early, and the optimizer only spends cycles on geometries that can actually complete the required motion.

## Shipping the Project

The session ended with getting the project onto GitHub—242 files changed, 16,788 insertions. My collaborator needed to review the synthesis code before our project deadline, and the animations weren't going to share themselves.

```
[main 773ce35] Add Python6BarLinkage project folder
 242 files changed, 16788 insertions(+)
```

There's always a temptation to spend another week "perfecting" code before sharing it. But done beats perfect, especially when someone else is waiting to build on your work.

## Takeaways

1. **Describe the symptom, not the diagnosis.** I said "doesn't seem to be going all the way to the endpoint" rather than prescribing a fix. This let Claude explore the actual problem space.

2. **Hard constraints need hard enforcement.** When physics says something is impossible, don't try to optimize your way around it. Filter impossible candidates out entirely.

3. **The optimization objective isn't always the problem.** Sometimes valid ranges, constraint handling, or the search space definition is where the bug lives.

4. **Ship it.** 242 files sitting on your local machine help nobody.

The linkage solver isn't perfect—I already have a list of edge cases to handle. But today, it reaches its endpoint. And in mechanism design, reaching your endpoint is the whole point.