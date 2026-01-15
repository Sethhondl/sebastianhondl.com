---
layout: post
title: "Why Custom AMIs Beat Containers for My Minecraft Server"
date: 2025-11-28
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 2
word_count: 499
---

Not every infrastructure decision needs to be complicated. I've been running a Minecraft server on EC2 with an EBS volume, and recently wondered whether containers could simplify my deployment workflow. The answer was a clear "no"—and understanding why taught me more about containers than any tutorial ever has.

## The Mismatch

Containers are optimized for stateless, horizontally scalable microservices. A Minecraft server is none of those things.

| Container Assumption | Game Server Reality |
|---------------------|---------------------|
| Ephemeral storage | Worlds need persistent, durable storage |
| Horizontal scaling | A single world runs on one instance |
| Quick task termination | Servers run continuously for days or weeks |
| Microservice resource limits | Fargate caps at 30GB RAM; my `r8a.xlarge` provides 32GB |

My Discord bot also runs on the same EC2 instance, watching Minecraft logs via RCON. Containerizing would mean rearchitecting something that already works.

## The Better Path: Custom AMIs

Instead of containers, I'm moving to custom AMIs built with Packer. Here's the difference in boot sequences:

**Current process:**
```
EC2 starts → Download Java → Download Minecraft JAR → Download Fabric 
→ Download mods → Install Discord bot deps → Configure everything → Start
```

**With a custom AMI:**
```
EC2 starts → Mount EBS → Start services
```

That's 3-5 minutes reduced to roughly 30 seconds. More importantly, it eliminates external download failures during boot—no more outages because a mod CDN is temporarily down.

### The Tradeoff

Custom AMIs shift complexity to update time. When Java or mods need updates, I rebuild the AMI rather than just restarting. For now, I'll do this manually since updates happen maybe monthly. If it becomes tedious, a GitHub Actions workflow could handle scheduled rebuilds.

## The Storage Question

I'd also wondered: can you attach EBS directly to a container? No. EBS volumes attach at the hypervisor level, not to containers. If you're running containers on EC2, the host mounts the volume, then you bind-mount directories into containers.

For shared storage across containers, you'd need EFS—which introduces latency that matters for real-time game servers. This reinforced why my current architecture makes sense.

## The Real Lesson

I came in asking "how do I containerize this?" when I should have been asking "what problem am I trying to solve?"

My actual problems were boot reliability and startup time. Containers would have addressed neither while adding orchestration complexity. Custom AMIs solve both directly.

## Takeaways

1. **Identify your actual problem before choosing a solution.** Stateful, memory-intensive workloads often don't benefit from containers.

2. **Consider custom AMIs for any EC2 workload that downloads dependencies at boot.** The reliability gains usually outweigh rebuild overhead.

3. **Understand your storage layer first.** EBS vs. EFS vs. S3 choices cascade into compute decisions.

The next step is finishing the Packer configuration and testing my first custom AMI build. The architecture decision is made—and for this workload, the boring solution is the right one.