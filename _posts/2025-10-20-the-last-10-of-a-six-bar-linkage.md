---
layout: post
title: "The Last 10% of a Six-Bar Linkage"
date: 2025-10-20
categories: [development, ai]
tags: [claude-code, api, debugging]
read_time: 5
word_count: 1151
---

There's a particular kind of frustration that comes from solving the "interesting" part of a problem and realizing you're only 90% done. Today I hit that wall hard while working on a mechanism synthesis project for my advanced mechanisms class—designing a six-bar linkage to control a folding greenhouse door.

The math was done. The synthesis equations were working. MATLAB was happily spitting out solutions. And yet every single one of them was unusable.

## The Problem That Looked Solved

My team is designing a tabletop greenhouse with a smooth-opening door mechanism. Picture two connected four-bar linkages working together to control a door that folds upward and back, like a laptop screen opening past 90 degrees. We chose a six-bar linkage over simpler alternatives because a basic four-bar can only guarantee three positions along a path, and a cam mechanism would add manufacturing complexity we wanted to avoid. The six-bar gives us enough degrees of freedom to prescribe exactly how the lower right corner of the door travels as it folds open—controlling not just where it ends up, but how it gets there.

I had sample code for dyad synthesis (a method for designing two-link chains that pass through prescribed positions). The equations were implemented. Solutions were generating. Victory, right?

Not quite. The solutions I was getting had a few problems:

1. The door's lower left corner was passing through the greenhouse box
2. The front wall of the door was intersecting with the frame
3. The upper right corner was swinging past the upper left corner (physically impossible for a rigid door)

In mechanism design terms, I had valid kinematic solutions that were geometric nonsense.

## Where Claude Helped (And Where It Couldn't)

I brought this problem to Claude with my sample MATLAB code and project proposal. What followed was a useful exercise in collaborative constraint definition.

The first thing Claude did was ask clarifying questions about the physical setup—which I appreciated because I'd glossed over some details in my own head. Where exactly are the ground pivots allowed? What counts as "inside the box"? How do we define the door's orientation throughout the motion?

This is where AI assistance shines: forcing you to make implicit assumptions explicit. I knew what I meant by "the door shouldn't go inside the box," but I hadn't translated that into mathematical constraints.

We worked through the geometry together. The key variables: `coupler_point` is the position of the lower right corner of the door (the point we're prescribing the path for), `theta_door` is the door's current angle relative to horizontal, and `door_width` and `door_height` are the physical dimensions of the door panel.

```matlab
% Door corner positions as functions of mechanism state
% coupler_point: lower right corner (the path we're controlling)
% theta_door: door angle relative to horizontal
door_LL = coupler_point - door_width * [cos(theta_door); sin(theta_door)];
door_UR = coupler_point + door_height * [cos(theta_door + pi/2); sin(theta_door + pi/2)];

% Constraint 1: Lower left corner must stay outside the box
% (x >= box_front_x OR y >= box_top_y)
constraint_LL = (door_LL(1) >= box_front) | (door_LL(2) >= box_top);

% Constraint 2: Upper right x must not exceed upper left x
% (door isn't "overfolded")
constraint_UR = door_UR(1) <= door_LL(1);
```

The code itself is straightforward. The insight was recognizing that these geometric constraints needed to be checked at every point in the mechanism's motion, not just at the synthesis positions. A solution that works at three prescribed positions can still fail catastrophically between them.

With the constraints formalized, I thought I was ready to solve the problem properly. I wasn't.

## The Real Lesson: Generate, Then Filter

Here's what took most of my time: I kept trying to be clever.

My first instinct was to add the constraints directly to the synthesis equations—solve for mechanisms that inherently satisfy the geometry. Claude and I went down this path for a while before I realized we were overcomplicating things.

The simpler approach: generate solutions using the standard synthesis, then filter them aggressively. Evaluate each candidate mechanism through its full range of motion and reject anything that violates constraints at any point.

```matlab
function valid = check_mechanism_constraints(linkage_params, num_steps)
    valid = true;
    for t = linspace(0, 2*pi, num_steps)
        [door_LL, door_UR] = compute_door_corners(linkage_params, t);
        if ~passes_all_constraints(door_LL, door_UR)
            valid = false;
            return;
        end
    end
end
```

It's not elegant. It's computationally wasteful. But it's correct, and it actually works.

The filtering was aggressive. Out of roughly 400 candidate mechanisms that the synthesis generated, maybe 15 survived all the constraint checks. The survivors shared some common traits: ground pivots tucked behind the hinge line (so the linkage bars didn't collide with the frame), moderate link length ratios (extreme ratios tended to produce jerky motions), and coupler angles that kept the door rotating smoothly rather than whipping through certain portions of the path.

## What I'd Do Differently

This session crystallized something I've been noticing about working with AI on engineering problems: the AI is excellent at helping you formalize what you know and terrible at knowing what you don't know.

Claude helped me translate vague geometric intuition into precise mathematical constraints. It helped me debug MATLAB syntax and suggested efficient ways to structure the filtering loop. What it couldn't do was tell me that I was overengineering the synthesis step when a simple generate-and-filter approach would work better.

That insight came from stepping back and asking myself: "What's the simplest thing that could possibly work?" The AI doesn't ask that question unless you prompt it to.

If I faced a similar problem tomorrow, I'd start with the dumb brute-force approach first. Generate broadly, filter strictly, and only add sophistication to the generation step if filtering isn't finding enough valid candidates. The time I spent trying to embed constraints into the synthesis equations wasn't wasted—I understand the problem better now—but it wasn't the efficient path either.

## Three Lessons from This Session

**1. Separate generation from validation.** It's often easier to generate candidates broadly and filter strictly than to bake all constraints into the generation step. The synthesis math is already complicated enough without adding geometric constraints to the mix.

**2. Check the full motion range.** Discrete synthesis points don't guarantee continuous validity. A mechanism that looks perfect at positions 1, 2, and 3 can still crash through your frame at position 1.5. Sample densely.

**3. Make your constraints explicit early.** If you can't write the constraint as code, you don't understand it well enough. The act of formalizing "the door shouldn't go inside the box" into inequality constraints caught several edge cases I hadn't consciously considered.

Tomorrow I'll be running the filtered solutions through the visualization code to see which ones produce the smoothest motion and have the most reasonable link lengths for fabrication. The "last 10%" has a way of stretching into another full day of work—but at least now I have candidates worth visualizing.