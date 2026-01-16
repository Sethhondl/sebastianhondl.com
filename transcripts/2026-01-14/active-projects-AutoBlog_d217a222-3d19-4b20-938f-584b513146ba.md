# Claude Conversation Transcript

---

## User [2026-01-14T23:41:20.255Z]

You are doing a final polish pass on a blog post before publication.

## Blog Post to Polish
# Why I Chose Custom AMIs Over Containers for My Minecraft Server

Some coding days are about deep debugging sessions. Others are about implementing complex features. And then there are days like today—where exploring a seemingly straightforward infrastructure question reveals why the "boring" solution is often correct.

## The Question That Started It

I've been running a Minecraft server on EC2 with an EBS volume, and I started wondering whether containers could simplify my deployment workflow. Specifically, I wanted to know: could I get easier updates and more reproducible builds by containerizing the server?

So I asked Claude directly: would containers fit my server's architecture?

The answer was a well-reasoned "no," and understanding *why* taught me more about containers than any tutorial.

## Why Containers Don't Fit Game Servers

The key insight is that containers are optimized for **stateless, scalable microservices**—essentially the opposite of a Minecraft server. Here's what stood out:

| Container Assumption | Why It Conflicts With Game Servers |
|---------------------|-----------------------------------|
| **Ephemeral storage** | Minecraft worlds require persistent, durable storage across restarts |
| **Horizontal scaling** | A single world can only run on one server instance |
| **Quick task termination** | Game servers are long-running processes, often up for days or weeks |
| **Resource limits designed for microservices** | Fargate caps at 30GB RAM (as of early 2025—verify current limits); my `r8a.xlarge` provides 32GB |

My Discord bot also runs on the same EC2 instance, watching Minecraft logs via RCON (the remote console protocol for sending server commands). Containerizing would mean significant rearchitecting for something that already works well.

## The Better Path: Custom AMIs with Packer

Instead, Claude suggested custom AMIs—and this approach actually *improved* my architecture rather than complicating it.

Packer is HashiCorp's tool for automating AMI creation through declarative configuration. Instead of downloading dependencies every time the server boots, you bake everything into a machine image once.

My current boot process looks like:
```
EC2 starts → Download Java → Download Minecraft JAR → Download Fabric 
→ Download mods → Install Discord bot deps → Configure everything → Start
```

With a custom AMI, it becomes:
```
EC2 starts → Mount EBS → Start services
```

That's a 3-5 minute startup reduced to roughly 30 seconds. More importantly, it eliminates external download failures during boot—no more server outages because a mod CDN is temporarily down.

### The Tradeoff: Update Complexity

Custom AMIs do shift complexity somewhere. When Java, Minecraft, or mods need updates, I'll need to rebuild the AMI rather than just restarting the server. For now, I'm planning manual rebuilds since updates happen infrequently (maybe monthly). If this becomes tedious, I could add a GitHub Actions workflow that rebuilds on a schedule or when I push changes to a configuration repo.

## Setting Up Packer

Here's the core Packer configuration:

```hcl
source "amazon-ebs" "minecraft" {
  source_ami_filter {
    filters = {
      name                = "al2023-ami-*-x86_64"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    owners      = ["amazon"]
    most_recent = true
  }
  instance_type = "t3.small"
  ssh_username  = "ec2-user"
  ami_name      = "minecraft-server-{{timestamp}}"
}
```

The provisioners then install Java, pre-download the Minecraft JAR, configure systemd services, and set up the Discord bot. The result is an AMI where user-data just mounts storage and starts services.

## Why You Can't Attach EBS Directly to Containers

I also got a clarifying answer on a question I'd been wondering about: can you attach an EBS volume directly to a container?

The short answer: no. EBS volumes attach to EC2 instances at the hypervisor level, not to containers. If you're running containers on EC2, the host mounts the volume, then you bind-mount directories into containers.

The key limitation for game servers: EBS volumes are availability-zone-specific and can only attach to one instance at a time. For shared storage across containers, you'd need EFS—which introduces latency that matters for real-time game servers.

This reinforced why my current architecture makes sense. I don't need the complexity of container orchestration when a single EC2 instance with attached EBS handles my requirements cleanly.

## What This Changed About My Approach

The real lesson wasn't about containers or AMIs specifically—it was about asking the right question. I came in asking "how do I containerize this?" when I should have been asking "what problem am I trying to solve?"

My actual problems were boot reliability and startup time. Containers would have addressed neither while adding orchestration complexity. Custom AMIs solve both directly.

## Practical Takeaways

1. **Before containerizing, identify your actual problem.** If your workload is stateful and memory-intensive, containers may add complexity without addressing what's actually wrong.

2. **Consider custom AMIs for any EC2 workload that downloads dependencies at boot.** Packer makes this maintainable, and the reliability gains often outweigh the rebuild overhead.

3. **Understand the storage layer before choosing compute.** EBS vs. EFS vs. S3 choices cascade into architectural decisions about where your workloads can run and how they handle state.

## What's Next

The next step is finishing the Packer configuration and testing the first custom AMI build. I expect some iteration on the provisioner scripts, but the architecture decision is made—and I'm confident it's the right one for this workload.

## Task
Apply a final polish for publication. Focus on:

1. **Opening Hook**: Ensure the first paragraph grabs attention
2. **Transitions**: Smooth transitions between sections
3. **Conclusion**: Strong, memorable ending with clear takeaway
4. **Title**: Make sure the title is engaging and SEO-friendly
5. **Tone**: Consistent, conversational voice throughout
6. **Redundancy**: Remove any repetitive content
7. **Readability**: Clear, concise sentences

Write the final polished blog post in full:

## Assistant [2026-01-14T23:41:31.653Z]

# Why Custom AMIs Beat Containers for My Minecraft Server

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

