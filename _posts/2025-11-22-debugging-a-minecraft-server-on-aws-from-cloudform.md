---
layout: post
title: "Debugging a Minecraft Server on AWS: From CloudFormation Limits to RCON Credentials"
date: 2025-11-22
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 4
word_count: 957
---

Today's coding session turned into a masterclass on hidden constraints—the kind of debugging that makes you appreciate just how many invisible boundaries exist between cloud services and the applications running on them. I maintain a Minecraft server on EC2 with Discord integration for player management, and today both layers demanded attention.

## The Cryptic Error That Started Everything

The day began with a CloudFormation deployment failure. The error message was characteristically unhelpful:

```
Waiter StackCreateComplete failed: Waiter encountered a terminal failure state: 
For expression "Stacks[].StackStatus" we matched expected path: "ROLLBACK_COMPLETE"
```

Stack rolled back. Great. But *why*? The first diagnostic step was querying stack events:

```bash
aws cloudformation describe-stack-events \
  --stack-name minecraft-server \
  --query "StackEvents[?ResourceStatus=='CREATE_FAILED'].[LogicalResourceId,ResourceStatusReason]" \
  --output table
```

The actual culprit emerged:

```
MinecraftInstance: Resource handler returned message: "Encoded User data is 
limited to 25600 bytes (Service: Ec2, Status Code: 400)"
```

My EC2 UserData script had grown past AWS's 25,600 byte limit for base64-encoded initialization scripts. The raw script was around 19KB, and base64 encoding adds roughly 33% overhead, pushing it to approximately 25.3KB—just over the limit.

## The Fix: Breaking Up Monolithic Scripts

The solution was architectural rather than cosmetic. Instead of cramming everything into UserData, I refactored to upload initialization scripts to S3 during deployment, then have the instance download them at boot.

First, the deploy script uploads the scripts before creating the stack:

```bash
# Upload initialization scripts to S3
TEMPLATE_BUCKET="cf-templates-${AWS_ACCOUNT_ID}-${AWS_REGION}"
aws s3 cp scripts/ec2-init-system.sh "s3://$TEMPLATE_BUCKET/scripts/"
aws s3 cp scripts/ec2-init-minecraft.sh "s3://$TEMPLATE_BUCKET/scripts/"
aws s3 cp scripts/ec2-init-services.sh "s3://$TEMPLATE_BUCKET/scripts/"
```

Then the UserData becomes a thin bootstrap that fetches and executes these scripts:

```yaml
UserData:
  Fn::Base64: !Sub |
    #!/bin/bash
    set -e
    
    TEMPLATE_BUCKET="cf-templates-${AWS::AccountId}-${AWS::Region}"
    
    aws s3 cp "s3://$TEMPLATE_BUCKET/scripts/ec2-init-system.sh" /tmp/
    aws s3 cp "s3://$TEMPLATE_BUCKET/scripts/ec2-init-minecraft.sh" /tmp/
    aws s3 cp "s3://$TEMPLATE_BUCKET/scripts/ec2-init-services.sh" /tmp/
    
    chmod +x /tmp/ec2-init-*.sh
    /tmp/ec2-init-system.sh
    /tmp/ec2-init-minecraft.sh
    /tmp/ec2-init-services.sh
```

This pattern is cleaner anyway—modular scripts are easier to test and update independently, and there's no practical size limit on what S3 can store.

## Tracing Bugs Across System Boundaries

With the infrastructure stable, the session shifted to application-level issues. What looked like four unrelated bugs turned out to share a common theme: data failing to cross system boundaries correctly.

### The Missing Whitelist Entry

A user had linked their Discord account but wasn't whitelisted. Rather than diving into sync script code, I checked timestamps first:

```bash
aws dynamodb get-item \
  --table-name minecraft-players \
  --key '{"discord_id": {"S": "123456789"}}' \
  --query "Item.linked_at.S"
```

The user linked at 11:42 PM. The server had shut down at 10:30 PM. The whitelist sync only runs when Minecraft is active, so their entry sat in DynamoDB without being applied. Not a code bug—just an edge case where the offline-to-online transition didn't trigger a sync.

### The Restore Script That Wouldn't Finish

This one took longer. The backup restore appeared to work—files downloaded, extracted, permissions fixed—but the server readiness check never completed. The script hung indefinitely waiting for an RCON response.

The issue was how credentials crossed process boundaries. The restore script runs as a subprocess, and the RCON password lived in the parent's environment:

```python
# Before: environment variable not exported to subprocess
subprocess.run(["./check_server_ready.sh"], check=True)
```

The fix was explicit about passing the environment:

```python
# After: pass RCON credentials to the subprocess
env = os.environ.copy()
env["RCON_PASSWORD"] = self.rcon_password
subprocess.run(["./check_server_ready.sh"], env=env, check=True)
```

Tracing this required connecting three files across two process boundaries: restore script → subprocess call → health check script → RCON connection → missing password. Having full codebase context made that chain visible immediately.

### RCON Command Feedback Spam

The final issue was cosmetic but annoying: every automated `save-all` command appeared in players' game chat. The fix was adding a filter to skip automated command responses before relaying to Discord. Minecraft's `gamerule sendCommandFeedback` would also work, but I wanted players to see feedback from their own commands—just not the server's scheduled ones.

## Configuration Sprawl: The Root Cause

Debugging these issues revealed a deeper problem: the same configuration values were defined in multiple places with slight variations. The whitelist sync needed the server port. The restore script needed RCON credentials. The Discord bot needed to know which commands to filter.

Each component sourced these values differently—some from environment variables, some hardcoded, some from CloudFormation parameters. This made debugging frustrating because fixing a value in one place didn't fix it everywhere.

The solution was creating a single `.env.example` as the source of truth:

```bash
SERVER_PORT=25565
RCON_PASSWORD=changeme
RCON_PORT=25575
MAX_PLAYERS=10
SPAWN_PROTECTION=0
```

Then updating the deploy script and CloudFormation template to read from this file consistently. Not glamorous, but it prevents the "but I already changed that setting" debugging loop.

## Diagnostic Commands Worth Keeping

For anyone debugging similar AWS infrastructure issues:

```bash
# Get failed resource details from CloudFormation
aws cloudformation describe-stack-events \
  --stack-name YOUR_STACK \
  --query "StackEvents[?ResourceStatus=='CREATE_FAILED']"

# Check encoded UserData size before deploying
cat userdata.sh | base64 | wc -c

# Verify S3 script uploads
aws s3 ls s3://YOUR_BUCKET/scripts/

# Test RCON connectivity manually
mcrcon -H localhost -P 25575 -p "$RCON_PASSWORD" "list"
```

The UserData size check is now part of my pre-deployment validation. Catching the limit before CloudFormation fails saves a 10-minute rollback cycle.

## What Got Fixed

By session's end: deployments work reliably with S3-based script loading, the whitelist syncs correctly on server startup, restore operations complete with proper credential passing, and command feedback no longer spams player chat.

The real lesson wasn't any single fix—it was recognizing that cloud debugging is often about finding which boundary the data didn't cross. Environment variables that don't propagate. Process state that doesn't inherit. Service assumptions that don't hold when components restart. Today's bugs all lived in those gaps, and understanding that pattern will make the next round of debugging faster.