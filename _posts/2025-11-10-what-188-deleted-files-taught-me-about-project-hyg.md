---
layout: post
title: "What 188 Deleted Files Taught Me About Project Hygiene in Linkage Synthesis"
date: 2025-11-10
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 5
word_count: 1182
---

I nearly pushed a working Stephenson I linkage synthesizer buried under so much organizational debris that my teammate would have needed archaeological tools to find it. The revelation came when I ran `git status` and watched 188 lines of deleted files scroll past—a monument to every experimental branch, failed optimization run, and "just in case" backup I'd accumulated while wrestling with six-bar linkage synthesis for my Advanced Mechanisms class.

## The Technical Problem: Making Mechanisms That Actually Work

Six-bar linkages convert rotary motion into complex paths. Turn a crank, and the output traces a specific curve—the motion that makes mechanical toys walk, industrial machines stamp precise patterns, or automotive suspensions articulate correctly. Synthesizing these linkages means finding the exact link lengths, pivot positions, and joint connections that produce a desired output path.

The math is beautiful and brutal. You're solving systems of circle-circle intersections where two links of known length must meet, applying triangle constraints to determine rigid body positions, and feeding it all into an optimizer hunting through a high-dimensional parameter space. Most configurations don't work. Links collide. Joints lock up. The mechanism exists mathematically but violates physical reality.

My Python synthesis code had been through dozens of iterations. Each optimization run produced artifacts: animation GIFs showing the mechanism in motion, JSON files storing parameter sets, PNG images of complete path traces. And because I was never quite sure which version of the code produced which results, I kept backup copies of scripts alongside their outputs.

## The Mess Becomes Visible

When I cloned my team's shared repository to integrate my working synthesizer, I finally saw the scope of what I'd created. Nested folders with names like `CouldWorkrun_20251107_142251`—named optimistically when I thought that particular parameter search might converge, now just another directory of artifacts from a run that produced physically impossible mechanisms. Output directories from fifty-plus test runs. Multiple versions of the same script with suffixes like `_backup`, `_old`, `_working`. Documentation files I'd started but never finished.

I deleted the cruft, reorganized the structure, and ran the commit:

```
Changes not staged for commit:
  deleted:    Python6BarLinkage/basic_animation/sixbar_animation.py
  deleted:    Python6BarLinkage/basic_animation/test_sixbar.py
  deleted:    Python6BarLinkage/documentation/README_GENERALIZED.md
  ...
```

One hundred eighty-eight lines. The commit message practically wrote itself: "Clean up experimental artifacts and reorganize project structure."

But here's what bothered me: somewhere in that mess was a working Stephenson I synthesizer that had taken me a week to debug. If I'd tried to share my code before this cleanup, my teammate would have had to dig through directories named with timestamps and optimism to find the actual deliverable. The mess wasn't just aesthetically displeasing—it would have cost someone else hours of confusion.

## Why Linkage Optimizers Return Infinity

The constraint system I'd built helps explain why so many output directories accumulated. When an optimizer searches for valid linkage parameters, it evaluates candidate solutions against multiple constraints. Invalid configurations need penalties heavy enough that the optimizer abandons them, but not so heavy that numerical precision breaks down.

Here's the box constraint checker:

```python
def check_start_position_in_box(self, params, theta_start):
    """Check that all joints are in [box_min, box_max] box at starting position."""
    try:
        positions = solve_linkage_position(params, theta_start)
        for joint_name in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            x, y = positions[joint_name]
            if x < self.box_min or x > self.box_max or y < self.box_min or y > self.box_max:
                return False
        return True
    except:
        return False
```

Seven joints, each with x and y coordinates, all needing to stay within a unit box throughout the mechanism's motion. A typical path-following error for a reasonable mechanism might be 0.01 to 0.1. My penalty weights are scaled accordingly:

- **10,000** for box constraint violations—about 100,000x a good path error
- **500,000** for negative x-coordinates during motion—mechanisms that swing through negative space are physically building through walls

These numbers emerged from watching optimization runs fail in specific ways. Too-small penalties let the optimizer produce "solutions" that clip through physical boundaries. Too-large penalties cause numerical overflow—the optimizer sees infinity and gives up. Each timestamped directory represented another calibration attempt.

## The Stephenson I Adaptation

The Stephenson I synthesizer was what I was actually trying to share with my team. I'd successfully adapted my Watt I synthesis code to a different linkage topology, and the working version was buried in the organizational chaos.

Both linkage types have six bars and one degree of freedom. Both produce complex output paths from simple rotary input. But their topology differs in how the ternary links attach to ground.

**Watt I solving order:**
1. Calculate joint B from ground pivot A using crank angle and link length
2. Find joint E at the intersection of circles centered at B and G
3. Solve triangle BCE to locate joint C
4. Solve triangle EFG to locate joint F
5. Find joint D at the intersection of circles from C and F

**Stephenson I solving order:**
1. Calculate joint B from ground pivot A (same as Watt I)
2. Find joint C at the intersection of circles centered at B and ground pivot G
3. Solve triangle BCD to locate joint D
4. Find joint E at the intersection of circles from D and G
5. Solve triangle DEF to locate joint F

The framework stays identical—same optimization loop, same constraint checking, same visualization pipeline. But `solve_linkage_position()` needed complete rewriting because you're propagating positions through a different kinematic chain. Getting this working required many failed runs, each generating its own output directory, each teaching me something about where the math could go wrong.

## What I'm Actually Changing

Here's what I'm doing differently going forward:

**For `.gitignore`:**
```
output_*/
*_backup.py
*_old.py
*.gif
solutions_*/
```

The pattern `output_*/` catches my timestamped run directories. The backup file patterns catch my uncertainty-driven copies. GIFs are easily regenerated from working code—they don't belong in version control.

**For naming conventions:**
- `possibleSolutions/watt_i_working_2024-11-07.json` for parameter sets worth keeping
- Descriptive names that say what makes a solution notable, not when I ran it

**On iteration speed:**
Working with Claude accelerated my progress dramatically. I could describe a constraint violation, get a fix, test it, and move to the next problem in minutes. But that same speed meant I generated output directories faster than I cleaned them up. The mess wasn't despite AI assistance—it was partly because of it. The tool that helped me solve the kinematic problems also helped me create organizational debt faster than I'd have managed alone.

## The Mechanism Works

After the cleanup, the Stephenson I synthesizer still produces valid results. The optimizer converges on mechanisms where all seven joints stay within the unit box throughout their motion, the output path follows target points within acceptable error, and no link passes through negative x-coordinates.

The 188 deleted files are now properly committed. The repository structure makes sense. My teammate can find the working synthesizer without spelunking through timestamped directories.

And I have a concrete reminder: iteration speed without organizational discipline just moves the mess to a larger pile—one that eventually blocks the actual goal of sharing working code with the people who need it.