---
layout: post
title: "From Napkin Math to Full Simulation: Building a Supersonic Trebuchet Optimizer"
date: 2025-10-13
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 5
word_count: 1197
---

There's something delightfully medieval about using AI to design a trebuchet—and something thoroughly modern about wanting it to launch ball bearings at Mach 1.2. The siege engineers of old perfected their craft through decades of physical prototypes and battlefield iteration. I wanted to know in an afternoon whether their design could ever reach supersonic speeds, or whether physics would say "no" before I bent a single piece of metal.

Physics had opinions. Strong ones.

## The Goal That Might Be Impossible

Here's the punchline: achieving 400 m/s with a purely gravitational trebuchet appears to be physically unrealistic at any buildable scale. The optimization framework I built exists precisely to quantify *why*—and to find out what speeds are actually achievable.

For context, the trebuchets at Punkin Chunkin competitions—purpose-built machines with counterweights exceeding 10,000 pounds—launch pumpkins at roughly 50-70 m/s. I'm asking for six times that velocity with a backyard-scale machine. Since energy requirements scale with velocity squared, I need 36 times the energy transfer efficiency of competition machines.

That's the question worth answering: where exactly does the physics break down?

## Starting with the Napkin

I'd already done preliminary energy calculations. The physics are straightforward—kinetic energy of a 3.544 gram projectile at 400 m/s works out to roughly 284 Joules. Working backwards through gravitational potential energy, accounting for roughly 15% losses to friction, air resistance, and sling dynamics, you need a counterweight around 32 kg dropping 1.5 meters.

Simple enough. But here's where trebuchets get interesting: the *geometry* matters enormously. Arm length, sling length, pivot position, counterweight drop path—these all interact in ways that are surprisingly hard to intuit. Two trebuchets with identical energy inputs can differ by a factor of three in release velocity depending on their proportions.

## The Architecture That Emerged

When I described the problem to Claude, it immediately grasped that this wasn't a trivial optimization. The response laid out a multi-file MATLAB architecture: a core dynamics simulator using Lagrangian mechanics, an optimization script with parameter sweeps, visualization tools for validation, and energy tracking to verify efficiency assumptions.

Claude didn't offer to write a quick script. It recognized that simulating a trebuchet properly requires modeling it as a multi-body dynamical system—the counterweight, the arm, and the sling all have coupled equations of motion.

The Lagrangian approach tracks total energy in the system and derives motion from how that energy flows between components. For a trebuchet, this is cleaner than applying Newton's laws to each part because you're fundamentally interested in energy transfer: gravitational potential energy becoming rotational kinetic energy becoming projectile velocity.

## The Physics That Actually Matters

The core insight for trebuchet design is that you're not just dropping a weight. You're orchestrating a carefully timed energy transfer:

1. **Counterweight drops**, converting potential energy to rotational kinetic energy
2. **Arm accelerates**, with the sling initially trailing behind  
3. **Sling whips forward**, adding effective arm length at exactly the right moment
4. **Release occurs** when tangential velocity peaks

Get the geometry wrong and the release angle sends your projectile into the ground—or straight up. The dynamics simulator tracks both the arm angle and sling angle with their own coupled equations of motion, derived from the system Lagrangian:

```matlab
% Kinetic energy terms
T_arm = 0.5 * I_arm * theta_dot^2;
T_cw = 0.5 * m_cw * v_cw^2;
T_proj = 0.5 * m_proj * (v_arm_tip + v_sling_relative)^2;

% Potential energy terms  
V = m_cw * g * y_cw + m_proj * g * y_proj;

% Lagrangian: L = T - V
% Equations of motion: d/dt(dL/d(q_dot)) - dL/dq = 0
```

The sling isn't passively attached—its angular acceleration depends on the arm's motion, and its inertia feeds back into the arm dynamics. This coupling is what makes trebuchet optimization non-trivial.

## What the Simulations Showed

Here's where I have to be honest: I built the framework but haven't completed the full parameter sweeps yet. Preliminary runs with reasonable parameters (3m pivot height, 2m arm, 1.5m sling, 50kg counterweight) produced release velocities around 45-60 m/s—solidly in the competition trebuchet range, nowhere near supersonic.

Scaling analysis suggests that reaching 400 m/s would require either a counterweight exceeding 2,000 kg with a 10+ meter drop height, mechanical advantage tricks that introduce their own losses, or supplementary energy storage like springs or pneumatics.

The framework now lets me ask precise questions: "What's the maximum velocity achievable with a 3-meter structure and 100 kg counterweight?" The next session will sweep arm ratio, sling length, and counterweight mass to map the feasible design space.

## Where AI Helped—and Where It Didn't

The collaboration wasn't frictionless. Claude's initial implementation assumed a fixed-pivot counterweight, but real trebuchets often use a hanging counterweight on a hinge—this changes the dynamics significantly. I had to point out that energy transfer efficiency depends on the counterweight's path, not just its drop height.

There was also a moment where Claude generated event detection code for sling release that would have triggered at maximum arm angular velocity rather than maximum projectile tangential velocity. These aren't the same thing because the sling adds its own velocity contribution. Catching that required me to actually understand the physics, not just trust the output.

**What worked well**: Claude handled the tedious parts—setting up the ODE solver options, managing event detection callbacks, structuring the parameter sweep loops. It also correctly derived the coupled equations of motion from the Lagrangian I specified, saving considerable algebra.

**What required my input**: Physical intuition about acceptable simplifications, catching dynamics errors, and knowing which results to sanity-check against the napkin math.

## Practical Takeaways

If you're tackling a physics simulation project with AI assistance:

1. **Start with napkin math.** Having preliminary calculations gave Claude concrete numbers to sanity-check against. When the simulation produced 55 m/s with parameters that napkin math predicted should yield 60 m/s, we knew we were in the right ballpark.

2. **Let the architecture emerge from the problem.** Don't force a structure. Describe what you need to learn, and let the tool organization follow from the physics.

3. **Validate against known cases.** Before trusting the trebuchet simulation, I ran it with the sling length set to zero—reducing it to a simple catapult—and verified the release velocity matched the analytical solution.

4. **Know when physics says "no."** Sometimes the most valuable output is learning that your goal requires rethinking the approach entirely.

## What's Next

The next session will run systematic parameter sweeps across three dimensions: arm pivot ratio (0.2 to 0.4), sling length as a multiple of arm length (0.5 to 2.0), and counterweight mass (20 to 200 kg). The output will be a surface plot showing maximum achievable velocity, plus identification of any practical designs that break 100 m/s.

If nothing in the parameter space gets close to supersonic, I'll have quantified exactly why—and can start exploring hybrid designs that add spring pre-tension or pneumatic assist.

The medieval engineers had to iterate through physical prototypes, learning from each collapsed frame and misfired projectile. I get to iterate through equations first, finding the walls before I hit them. That's the real luxury of simulation—failing fast and cheap, in service of eventually building something that works.