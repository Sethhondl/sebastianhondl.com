---
layout: post
title: "Two Optimization Problems, One Day: From Linkages to CloudFormation"
date: 2025-11-03
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 5
word_count: 1094
---

Today I split my time between two projects that seem completely unrelated—optimizing a mechanical linkage for a greenhouse door and architecting a Minecraft server on AWS. Both required breaking down a complex design space into constraints and letting automation find solutions I couldn't hand-compute. The parallel structure wasn't obvious until I was knee-deep in both.

## The Linkage Problem: Genetic Algorithms Meet Physical Constraints

The first session tackled a challenge for my advanced mechanisms class: finding the optimal ground pivot positions for a six-bar linkage. The goal is a mechanism where a greenhouse door smoothly transitions between open and closed states while keeping all links tucked inside a bounding box when closed.

I asked Claude to help me write a Python optimizer using a genetic algorithm. The core requirements sound straightforward—fit inside the frame when closed, avoid hitting the greenhouse structure while opening—but the devil is in the geometric details:

1. In the closed state, all links and pivots must fit inside the greenhouse frame
2. The path traced by the door's edge must stay outside a "forbidden zone" (shown in pink on the reference diagram)
3. Each dyad and triad must stay on the same kinematic branch throughout the motion
4. The coupler path should hug the boundary between valid and invalid regions as closely as possible

That last requirement is the tricky one. Finding paths that clear the forbidden zone by a mile is easy, but the optimal solution minimizes wasted clearance. The mechanism needs to swing the door open efficiently, not take a scenic route.

The branch consistency constraint deserves special attention. In mechanism synthesis, a linkage can often reach the same position through different "assembly modes." Picture a simple four-bar linkage at a specific crank angle: the coupler link might assemble with the floating pivot above the line connecting the fixed pivots, or below it. Both are geometrically valid, but they're different configurations. If your optimizer accidentally jumps between them mid-motion, you've designed a mechanism that would need to disassemble and reassemble itself to function. The fitness function needs to verify that each configuration along the path is reachable from the previous one without the linkage passing through itself.

By session's end, I had a working optimizer evaluating thousands of candidate geometries per minute. The fitness function penalized forbidden zone violations, rewarded paths that stayed close to the boundary without crossing it, and rejected any configuration requiring branch switching. I kicked off the first optimization run with a population of 200 and let it churn through generations while I switched contexts.

## The Infrastructure Problem: CloudFormation for a Modded Server

The second project started simply: set up a modded Minecraft server on AWS that I could start and stop on demand to keep costs down. My friends and I have been talking about running a modpack together—probably 5-8 players with a moderate mod list, maybe 40-50 mods. Nothing extreme, but enough that hosting on my local machine during game sessions isn't practical.

The requirements evolved through a quick Q&A with Claude:

- Java Edition with Forge/Fabric mod support
- Instance sizing for our specific use case
- EBS volumes for world persistence with S3 backups
- Some way to start and stop the server without SSHing in every time

Claude generated a CloudFormation template covering VPC networking, EC2 compute with parameterized instance types, security groups for the Minecraft port (25565), and IAM roles for S3 access.

Instance sizing gave me the most trouble. Minecraft servers are single-threaded, so raw CPU clock speed matters more than core count—but memory becomes the bottleneck with modpacks. For our 5-8 player, moderate-mod scenario, I landed on t3.large (8 GB RAM, -Xmx6G heap), which should cost around $60-75/month running 24/7, or more like $15-20 if we only spin it up for weekend sessions. I parameterized the instance type so I can scale up to an r5.xlarge later if we go heavier on mods, without redeploying the whole stack.

I pushed back on the initial UserData script. Claude's first version embedded all server setup logic directly in the CloudFormation template—downloading Java, configuring Forge, setting up systemd services, everything. That works, but any change to server setup requires a full stack update. I asked for a revision that pulls a setup script from S3 instead, letting me iterate on server configuration without touching CloudFormation.

I deployed the template to a test VPC. The stack created successfully, and I verified the instance had the right specs via SSH. Actually installing Minecraft and testing with players is tomorrow's task, along with the start/stop automation—probably a simple Lambda function behind API Gateway.

## What Working Both Problems Taught Me

Switching between these projects in a single session surfaced something I wouldn't have noticed working on them separately. The linkage optimizer and the CloudFormation template are both "configuration languages"—you describe constraints and desired properties, and a system figures out the concrete implementation.

But the feedback loops are completely different. The optimizer runs thousands of evaluations per minute; I can watch fitness scores improve in real time. The CloudFormation stack takes 3-4 minutes to deploy, and if something's wrong, I have to read logs, delete the stack, and try again. That difference in iteration speed completely changes my approach. With the linkage, I can be sloppy with initial guesses because the optimizer will find its way. With infrastructure, I have to think carefully upfront because each failed deployment costs real time.

## Practical Takeaways

**For optimization problems:**
- Define hard constraints (must satisfy) separately from soft objectives (want to optimize)
- Branch consistency in mechanisms is non-negotiable—verify it explicitly in your fitness function
- When targeting a boundary, penalize distance from it rather than just checking which side you're on

**For infrastructure:**
- Parameterize instance types so you can scale without redeploying
- Single-threaded workloads benefit from clock speed, not core count
- Keep UserData minimal; pull setup scripts from S3 so you can iterate without stack updates

## The Cliffhanger

When I checked back on the linkage optimizer before wrapping up, every candidate in generations 1 through 100 had returned infinity for its fitness score. All of them. My constraint functions are rejecting every single geometry the algorithm proposes—usually a sign of either impossibly tight constraints or a bug in feasibility evaluation.

Tomorrow I'll add logging to find the culprit. My guess is the bounding box check; I may have set the closed-state envelope too tight for any valid linkage to actually fit. But that's a debugging story for another post.