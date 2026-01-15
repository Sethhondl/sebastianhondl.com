---
layout: post
title: "Daily Development Log - January 14, 2026"
date: 2025-11-07
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 6
word_count: 1371
---

I don't have write permission for that file. Here is the final polished blog post:

---

```markdown
---
layout: post
title: "When Your Mechanism Works Until It Doesn't: Debugging Geometric Constraints with AI"
date: 2025-11-08
categories: [development, ai]
tags: [kinematics, optimization, debugging, claude-code, python]
read_time: 7
word_count: 1400
---

My six-bar linkage moved beautifully through 90% of its path, then stopped dead. The animation looked perfect. The optimizer converged. But the coupler point kept halting just short of the endpoint I'd specified.

There's a particular frustration that comes with simulation work: everything appears correct until you watch your mechanism refuse to complete its motion.

## What's a Six-Bar Linkage?

A six-bar linkage is a mechanism with six rigid links connected by rotating joints. Think of a folding chair mechanism or the parallelogram linkage on a desk lamp, but more complex. Here's the Watt I configuration I'm working with:

```
        C -------- D (coupler point - traces output path)
       /|          |
      / |          |
     B  |          F
     |  E ________|
     |  |         |
     A  G---------+
   (fixed)     (fixed)
```

Joints A and G are fixed to ground. Link AB rotates around A as the input. The chain propagates through B→E→C→D and B→E→G→F→D, with D being the coupler point that traces the output curve.

My optimizer was supposed to find link lengths and pivot locations that would make D travel through specified start and end positions. It converged, the links moved smoothly—but the motion kept stopping before reaching the endpoint.

## The Kinematic Chain

The solver computes each joint position in sequence. Given an input angle theta2, we solve for where each subsequent joint must be:

```python
def solve_linkage_position(params, theta2):
    """Solve for all joint positions given input angle theta2."""
    A = params['A']
    G = params['G']

    B = euler_to_point(A, params['L_AB'], theta2)
    E = solve_circle_intersection(B, params['L_EB'], G, params['L_GE'], upper=True)
    C = solve_triangle_point(B, E, params['L_BC'], params['L_CE'], upper=True)
    F = solve_triangle_point(E, G, params['L_EF'], params['L_FG'], upper=False)
    D = solve_circle_intersection(C, params['L_CD'], F, params['L_DF'], upper=True)

    return {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G}
```

The chain looked correct. Each joint fed into the next. But somewhere between my optimization constraints and the actual mechanism behavior, the path was getting truncated.

The question was: at what input angles does this chain produce valid geometry?

## Where the Range Finder Failed

The `find_valid_angle_range` function determines which input angles produce valid configurations—angles where all circle intersections have solutions:

```python
def find_valid_angle_range(params, start_angle=0.0, angle_step=0.01):
    """Find the valid angle range for the linkage."""
    forward_limit = start_angle
    angle = start_angle + angle_step
    while angle < 2 * np.pi:
        try:
            solve_linkage_position(params, angle)
            forward_limit = angle
            angle += angle_step
        except:  # Bug: bare except hides real errors
            break
```

Two problems hide here. First, the bare `except:` catches everything—including bugs and typos—and silently treats them as "end of valid range." Second, the fixed step size might overshoot the actual boundary.

But the deeper issue wasn't in this function at all.

## Debugging with Claude

Working through this with Claude felt like pair programming with someone who has infinite patience for reading kinematic solver code. I started with "Can you make sure it always gets close to the endpoint?"

Rather than diving into fixes, Claude first traced the data flow. It read through `scripts/linkage_solver.py` to understand position solving, `scripts/optimize.py` to see how the fitness function evaluated candidates, and the constraint validation code. After mapping the dependencies, Claude identified that the cost function calculated path error but never verified that the endpoint fell within the valid angular range.

Then came the question that reframed everything: "Is the optimizer failing to find solutions, or is it finding solutions in a search space that doesn't include your target?"

That distinction mattered. The optimizer wasn't broken—it was searching over configurations that couldn't physically reach the endpoint, and I hadn't penalized that.

Claude also spotted a geometric constraint I'd added earlier: a check that the dyad joint (point C) stayed to the left of point D throughout motion. This constraint prevented link crossings for most of the path, but at extreme angles near the endpoint, it became geometrically impossible to satisfy. The constraint that kept the mechanism well-behaved in the middle was blocking it at the edges.

## The Hidden Assumption

I'd assumed that if a linkage could reach the start point, it could reach any point along the path to the endpoint. But six-bar linkages have lockup positions—angles where the geometry becomes impossible.

Think of trying to fold your arm past straight. At full extension, your elbow hits a limit where the geometry won't allow further motion. In a six-bar linkage, these limits occur when circle intersections have no solution, when links would need to pass through each other, or when the mechanism reaches a configuration where it can't continue without reversing.

My cost function checked whether the optimizer's solution could reach the start point. It never checked whether the endpoint was within the valid angular range:

```python
def fitness(params, target_points):
    start_pt, end_pt = target_points[0], target_points[-1]
    start_angle = find_angle_for_point(params, start_pt)
    path_error = calculate_path_deviation(params, target_points, start_angle)
    return path_error  # No check on endpoint reachability!
```

The optimizer happily returned configurations where the endpoint required an angle of 2.8 radians—but the mechanism locked up at 2.5.

## The Fix: Validate Before Optimizing

First, improve the angle range finder with adaptive stepping and proper exception handling:

```python
def find_valid_angle_range(params, start_angle=0.0, coarse_step=0.02, fine_step=0.001):
    """Find the valid angle range with adaptive step sizing."""
    forward_limit = start_angle
    angle = start_angle + coarse_step

    while angle < 2 * np.pi:
        try:
            solve_linkage_position(params, angle)
            forward_limit = angle
            angle += coarse_step
        except ValueError:  # Only catch expected geometry failures
            angle = forward_limit + fine_step
            while angle < forward_limit + coarse_step:
                try:
                    solve_linkage_position(params, angle)
                    forward_limit = angle
                except ValueError:
                    break
                angle += fine_step
            break

    return forward_limit
```

Catching `ValueError` specifically means unexpected errors surface instead of silently truncating the valid range.

Second—the actual fix—add endpoint reachability to the cost function. The `calculate_required_angle` function solves the inverse problem: given a target point, what input angle would place the coupler point there?

```python
def fitness(params, target_points):
    start_pt, end_pt = target_points[0], target_points[-1]
    start_angle = find_angle_for_point(params, start_pt)
    angle_range = find_valid_angle_range(params, start_angle)

    end_angle = calculate_required_angle(params, end_pt)
    if end_angle > angle_range:
        return float('inf')  # Reject unreachable configurations

    if end_angle > angle_range - 0.1:  # ~5.7 degrees of margin
        return float('inf')

    path_error = calculate_path_deviation(params, target_points, start_angle)
    return path_error
```

That margin matters. A linkage that can barely reach your target isn't useful in practice—any manufacturing tolerance pushes it into lockup.

## What This Taught Me

**Reframing beats staring.** I'd spent hours tweaking mutation rates and population sizes, assuming the optimizer was the problem. Claude's question—"is the search space wrong?"—shifted focus from the optimizer to the constraints. The fix took twenty minutes once I was looking in the right place.

**Cost functions encode priorities.** If you don't penalize edge-case solutions, the optimizer will find them. Mine was doing exactly what I asked—minimizing path error—but I hadn't told it that unreachable endpoints should be rejected.

**Constraints that work in the middle can fail at the edges.** The dyad joint constraint prevented link crossings for 90% of the motion range. But geometric relationships that hold in one region of configuration space don't necessarily hold everywhere.

The code now reaches both endpoints reliably, with angular margin to spare. Next step: generalizing this solver to handle any Watt or Stevenson chain configuration. The endpoint validation pattern will carry over—every chain type has its own lockup geometry, and catching that in the cost function beats debugging truncated paths after the fact.
```

---

**Key polish changes made:**

1. **Opening hook**: Tightened to three punchy sentences that immediately establish the problem
2. **Transitions**: Added "The question was: at what input angles does this chain produce valid geometry?" to bridge sections; smoothed flow between Claude debugging and the hidden assumption
3. **Conclusion**: Reordered takeaways to lead with the strongest insight ("Reframing beats staring"); added forward-looking closing about generalizing the solver
4. **Title**: Updated to "Geometric Constraints" for better SEO and consistency with content
5. **Tone**: Removed parenthetical explanations where context was clear; kept conversational but tighter
6. **Redundancy**: Cut redundant explanation of what the optimizer was supposed to do; streamlined the range finder analysis
7. **Readability**: Shortened several multi-clause sentences; removed unnecessary qualifiers