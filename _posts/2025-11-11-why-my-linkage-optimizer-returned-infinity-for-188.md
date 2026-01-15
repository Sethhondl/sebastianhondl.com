---
layout: post
title: "Why My Linkage Optimizer Returned Infinity for 188 Generations"
date: 2025-11-11
categories: [development, ai]
tags: [claude-code, python, testing, api, debugging]
read_time: 4
word_count: 993
---

Generation 47: best: inf. Generation 48: best: inf. Generation 49: best: inf. I watched the terminal scroll for ten minutes, each line identical to the last, before accepting that something was fundamentally wrong. The genetic algorithm wasn't slowly converging or getting stuck in local minima—it was finding *zero* valid solutions out of thousands of candidates.

## The Context: Six-Bar Linkage Synthesis

I'm working on a final project for my advanced mechanisms class that involves synthesizing six-bar linkages. Think of the mechanism that makes windshield wipers sweep in an arc, or how a folding chair collapses—these are linkages that convert rotation into specific motion paths. A six-bar linkage has six rigid links connected by joints, and by carefully choosing the link lengths and pivot positions, you can make a point on the mechanism trace almost any path you need.

My goal: find link lengths and pivot positions that make a coupler point travel between two specific target positions. This "two-position synthesis" specifies where I want the mechanism to be at two key moments, and the optimizer searches for geometry that achieves both.

Here's a rough sketch of the linkage topology:

```
    Ground (fixed)
    A-----------G
    |           |
   AB          GH
    |           |
    B-----C-----H
          |
         CD
          |
          D  ← coupler point (must hit target positions)
```

The optimization uses `scipy.optimize.differential_evolution`, a genetic algorithm exploring a 13-dimensional parameter space: two ground pivot locations and nine link lengths. With so many variables and hard geometric constraints, the algorithm can easily wander through regions where no valid configurations exist.

## The Symptom: Every Solution Returns Infinity

After adding an early stopping feature to halt optimization when the error converged, I ran the synthesis and watched 188 generations pass with "best: inf" on every line. Over 4,000 total evaluations—every single one returning infinity.

My fitness function used large penalty values to enforce constraints:

```python
# Hard constraint: Start position must be within 0.01 units
if dist_start > 0.01:
    error += 1000000.0 * (dist_start - 0.01)**2

# Hard constraint: All joints must stay in the [0,1] box
if any_joint_outside_box:
    error += 500000.0

# Critical: No joint can have negative X coordinate
if any_negative_x:
    error += 5000000.0
```

These penalties might seem arbitrary, but their purpose is to make constraint-violating solutions effectively infinitely worse than valid ones. A valid solution might have an error of 0.001 to 0.1, so adding millions ensures the optimizer always prefers valid geometry. When scipy reports "best: inf," every solution is violating something.

## The Debugging Process

Claude helped me systematically investigate, ruling out several hypotheses before finding the real issue.

**First hypothesis: bounds too restrictive.** The parameter bounds looked reasonable—all positions in the unit square, all link lengths between 0.1 and 1.0. But this didn't explain why *every* combination failed.

**Second hypothesis: numerical precision issues.** Maybe the circle-circle intersection code was failing due to floating point errors? We added epsilon tolerances, but the problem persisted.

**Third hypothesis: the target positions themselves.** This is where things got interesting. I had specified a start position at (1, 0) and an end position at (0.1, 1)—opposite corners of the workspace. We added diagnostic counters to track exactly which constraints were failing:

```python
def objective(self, x):
    self.eval_count += 1
    params = self.params_dict(x)
    
    if not self.check_triangle_inequalities(params):
        self.triangle_failures += 1
        return 1e8
    
    try:
        theta_start, dist_start = self.find_angle_for_target(params, self.target_start)
    except ValueError:
        self.geometry_failures += 1
        return 1e8  # Circles don't intersect—linkage can't close
```

The results were illuminating:

```
Triangle inequality failures: 847
Circle intersection failures: 1203  
Box constraint violations: 2156
Successful geometry evaluations: 0
```

The triangle inequality check catches a physical impossibility: for any three connected links forming a loop, the sum of any two lengths must exceed the third. If link AB is 0.2, BC is 0.3, and CA is 0.8, there's no way to connect them—0.2 + 0.3 = 0.5 < 0.8.

But the real culprit was the combination of tight target positions and the box constraint. Reaching from (1, 0) to (0.1, 1) required the linkage to sweep through a large arc, inevitably pushing joints outside the [0, 1] box during motion.

## The Fix: Graduated Penalties and Wider Bounds

The solution involved three concrete changes:

1. **Increased population size** from 10 to 25. More diverse initial candidates meant better coverage of the feasible region.

2. **Widened link length bounds** for connecting links—`L_AB` from (0.1, 1.0) to (0.1, 1.5), `L_CD` to (0.1, 1.2). Longer links allow the mechanism to reach further without pushing intermediate joints outside the workspace.

3. **Graduated penalties** instead of hard cutoffs:

```python
# Old: hard cutoff
if any_joint_outside_box:
    error += 500000.0

# New: graduated penalty based on violation magnitude
for joint in joints:
    if joint.x < 0:
        error += 100000.0 * abs(joint.x)
    if joint.x > 1:
        error += 50000.0 * (joint.x - 1)
```

After these changes, valid solutions appeared within 12 generations, with errors dropping from infinity to 0.0034.

## The Key Insight

When every solution returns infinity, the algorithm has no gradient to follow. It's randomly jumping between equally invalid candidates with no way to tell which direction leads toward feasibility. Graduated penalties create a slope that guides the search toward valid regions.

Hard constraints should be reserved for true impossibilities—configurations that violate physics or break the simulation. Geometric preferences work better as graduated penalties proportional to the violation magnitude. A joint at x=-0.001 shouldn't be treated the same as one at x=-0.5.

## Practical Takeaway

If your optimization is stuck returning infinity, add instrumentation to track *which* constraints are failing:

```python
class ConstraintTracker:
    def __init__(self):
        self.failures = defaultdict(int)
    
    def check(self, name, condition):
        if not condition:
            self.failures[name] += 1
        return condition

# After running:
print(dict(tracker.failures))
# {'triangle_ineq': 847, 'circle_intersect': 1203, 'box_constraint': 2156}
```

This immediately tells you where to focus. In my case, seeing that box constraint violations outnumbered everything else pointed directly at the relationship between target positions and workspace limits—and suggested that softening those constraints would let the optimizer find its footing.