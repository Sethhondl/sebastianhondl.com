---
layout: post
title: "When Your Mechanism Works Until It Doesn't: Debugging Kinematic Limits"
date: 2025-11-08
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 5
word_count: 1071
---

I'm building a six-bar linkage synthesis program for my advanced mechanisms class—a tool that uses differential evolution (a genetic optimization algorithm) to find linkage geometries that trace specific paths. The code was working. The animation looked great. But the coupler point kept stopping short of the endpoint I specified, covering only about 90% of the desired path.

There's a particular frustration that comes with this kind of simulation work: your mechanism moves beautifully through most of its range, then stops dead just before reaching the target position.

## What's a Six-Bar Linkage?

A six-bar linkage is a mechanism with six rigid links connected by rotating joints. Think of a folding chair mechanism or the parallelogram linkage on a desk lamp, but more complex. These mechanisms can produce intricate coupler curves—the path traced by a point on one of the links—useful in everything from car suspensions to robotic grippers.

My optimizer was supposed to find link lengths and pivot locations that would make the coupler point travel through specified start and end positions. The optimizer converged, the links moved smoothly, but the motion kept stopping before reaching the endpoint.

## The Kinematic Chain

The solver computes each joint position in sequence. Given an input angle theta2 (how far we've rotated the driving link), we solve for where each subsequent joint must be:

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

Joint A is fixed. Joint B rotates around A. Joint E is found by intersecting two circles—one centered at B, one at the fixed pivot G. And so on down the chain until we reach D, the coupler point that traces the output path.

The chain looked correct. Each joint fed into the next. But somewhere between my optimization constraints and the actual mechanism behavior, the path was getting truncated.

## Where the Range Finder Failed

The `find_valid_angle_range` function determines which input angles produce valid configurations—angles where all the circle intersections have solutions and no links need to stretch or pass through each other:

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
        except:
            break
```

Working through this with Claude felt like pair programming with someone who has infinite patience for reading kinematic solver code. I started the session with "Can you make sure that it always gets close to the endpoint?" Rather than diving into fixes, Claude first examined `scripts/linkage_solver.py` and `scripts/optimize.py` to understand how the pieces fit together.

Then came the question that reframed everything: "Is the optimizer failing to find solutions, or is it finding solutions in a search space that doesn't include your target?"

That distinction mattered. The optimizer wasn't broken. It was searching over configurations that couldn't physically reach the endpoint—and I hadn't penalized that.

## The Hidden Assumption

Here's what I'd baked in without realizing: I assumed that if a linkage could reach the start point, it could reach any point along the path to the endpoint. But six-bar linkages have lockup positions—angles where the geometry becomes impossible because links would need to stretch or pass through each other.

My cost function checked whether the optimizer's solution could reach the start point. It never checked whether the endpoint was within the valid angular range. So the optimizer happily returned configurations where the endpoint required an angle of, say, 2.8 radians—but the mechanism locked up at 2.5 radians.

```python
def fitness(params, target_points):
    start_pt, end_pt = target_points[0], target_points[-1]

    # Find where the coupler point matches the start
    start_angle = find_angle_for_point(params, start_pt)

    # Calculate path error (how well the path matches targets)
    path_error = calculate_path_deviation(params, target_points, start_angle)

    return path_error  # No check on endpoint reachability!
```

The cost function was minimizing path error without ever asking: "Can this mechanism actually complete the path?"

## The Fix: Validate Before Optimizing

The solution had two parts. First, improve the angle range finder to be more precise near boundaries:

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
        except ValueError:
            # Hit a boundary—back up and search with finer steps
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

The adaptive stepping catches more precise boundaries. And catching `ValueError` specifically, rather than bare `except`, means unexpected errors surface instead of silently truncating the valid range.

Second—the actual fix—add endpoint reachability to the cost function:

```python
def fitness(params, target_points):
    start_pt, end_pt = target_points[0], target_points[-1]
    angle_range = find_valid_angle_range(params)

    # Check if endpoint is reachable
    end_angle = calculate_required_angle(params, end_pt)
    if end_angle > angle_range:
        return float('inf')  # Reject unreachable configurations

    # Don't accept solutions at the edge of validity
    if end_angle > angle_range - 0.1:  # ~6 degrees of margin
        return float('inf')

    path_error = calculate_path_deviation(params, target_points, start_angle)
    return path_error
```

That margin matters. A linkage that can barely reach your target isn't useful in practice—any manufacturing tolerance pushes it into lockup.

## What This Taught Me

**Cost functions encode priorities.** If you don't penalize edge-case solutions, the optimizer will happily find them. Mine was doing exactly what I asked—minimizing path error—but I hadn't told it that unreachable endpoints should be rejected.

**Kinematic limits aren't binary.** A mechanism might solve at a given angle but be practically useless there. The difference between "technically valid" and "robust enough to build" requires thinking about margins.

**Reframing beats staring.** I'd been tweaking mutation rates and population sizes, assuming the optimizer was the problem. The question "is the search space wrong?" shifted focus from the optimizer to the constraints. The fix took twenty minutes once I was looking in the right place.

The code now reaches both endpoints reliably. Configurations that used to stop at 90% now complete the full path—with angular margin to spare.