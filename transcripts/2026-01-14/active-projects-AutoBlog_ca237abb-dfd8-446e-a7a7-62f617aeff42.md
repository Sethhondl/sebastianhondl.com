# Claude Conversation Transcript

---

## User [2026-01-14T23:55:52.989Z]

You are doing a final polish pass on a blog post before publication.

## Blog Post to Polish
Let me now write the revised blog post addressing all the editor's feedback:

---

# Feedback Loops: How Verifying Against Solutions Changed My AI Workflow

My control systems homework came with partial solutions. I had a choice: peek first, or use them to verify my AI-assisted work after the fact.

I chose verification. The workflow was simple: ask Claude to solve each problem independently using transfer function analysis and root locus methods, compare the results against the provided solutions, identify where they differed, then apply those learnings to the remaining problems. This turned a homework assignment into something more valuable—a feedback loop where mistakes became teaching moments.

## The Verification Workflow in Practice

The key instruction was explicit:

> "Please complete the homework first without looking at the partial solutions, then compare where the partial solutions and my solutions differ and come up with a plan to fix it for that problem."

This forced Claude into a learning posture rather than a copying posture. When the AI discovers its own mistakes, it produces better explanations of *why* something went wrong—which is exactly what I needed to actually learn the material.

For example, one problem asked for the steady-state error of a unity feedback system with a Type 1 plant. Claude's initial solution applied the final value theorem correctly but used the wrong error constant formula, treating the system as Type 0. Comparing against the solution revealed the gap: the number of free integrators in the loop determines the system type, which then determines which error constant (position, velocity, or acceleration) governs steady-state behavior.

That distinction—something I'd glossed over in lecture notes—stuck after seeing it fail in practice.

The output format mattered too. I had Claude generate HTML that gets printed to PDF via Chrome's headless mode:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --print-to-pdf="hw8.pdf" \
  --no-margins solutions.html
```

This avoided the LaTeX rabbit hole while producing clean, submission-ready documents. Sometimes the simplest approach is the right one.

## Debugging a Ghost Instance on AWS

The same verification pattern surfaced later that day while debugging my Minecraft server's auto-shutdown feature. The symptom: the server should have been running, but SSH connections timed out.

Checking the CloudFormation outputs gave me an instance ID:

```bash
aws cloudformation describe-stacks --stack-name minecraft-server \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" \
  --output text
# Returns: i-0be2a78206b22947e
```

But querying EC2 directly told a different story:

```bash
aws ec2 describe-instances --instance-ids i-0be2a78206b22947e
# An error occurred (InvalidInstanceID.NotFound): 
# The instance ID 'i-0be2a78206b22947e' does not exist
```

The CloudFormation stack showed `CREATE_COMPLETE`. Expected state: instance exists. Actual state: instance gone. The same verification pattern from the homework—compare expected against actual, investigate the difference.

Digging into the CloudFormation template revealed the shutdown mechanism: a Lambda function triggered by CloudWatch alarms when player count drops to zero. The function was supposed to *stop* the instance (preserving it for later restart), but I found the bug—an earlier refactor had changed `stop_instances` to `terminate_instances` without updating the surrounding logic.

The auto-shutdown *had* worked. It just worked too well. Instead of a stoppable instance waiting for the next play session, I had a terminated instance and a CloudFormation stack pointing at nothing.

The fix was straightforward once identified: revert to `stop_instances` and add a check preventing termination of instances that are already stopped. But finding it required the same discipline as the homework—don't assume the system matches its declared state, verify against reality.

## What Connects These Tasks

Both situations involved the same core pattern: forming an expectation, checking it against ground truth, and learning from the delta.

For homework, the expectation was "Claude's solution is correct" and the ground truth was the partial solutions. For the infrastructure bug, the expectation was "CloudFormation says the instance exists" and the ground truth was the EC2 API.

The learning happens in the gap. Claude's wrong error constant formula taught me more about system types than the lecture did. The terminated-instead-of-stopped bug taught me to audit Lambda function changes more carefully.

## What I'll Do Differently

Next time I have reference solutions available—for homework, for debugging, for anything—I'll build verification into the workflow from the start rather than reaching for it as a fallback. The extra structure creates the feedback loops where actual understanding develops.

The homework took longer this way. I could have copied the solutions and finished in twenty minutes. Instead, I spent an hour and a half working through problems, comparing, fixing, and re-solving. But I'll remember the steady-state error formulas now. That's the trade-off worth making.

---

This revised version addresses all the editor's feedback:

1. **New title** that matches the actual content (feedback loops/verification)
2. **Unified theme** threaded throughout—the verification pattern appears in both stories
3. **Cut to two projects** (homework and ghost instance), removing RCON and webhook sections
4. **Added concrete homework example** (Type 1 system, steady-state error)
5. **Explained what caused the termination** (Lambda function bug)
6. **Removed "state drift" terminology**—described what actually happened instead
7. **Opening is concrete**, not abstract
8. **Transitions connect the stories** through the shared verification pattern
9. **Removed vague praise** about Claude's investigative patterns
10. **Conclusion offers something new**—what to do differently, not a restatement
11. **Consistent code formatting** (full blocks where appropriate)
12. **Takeaways emerge from the stories** rather than being bolted on

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

## Assistant [2026-01-14T23:56:03.703Z]

# Feedback Loops: How Verifying Against Solutions Changed My AI Workflow

My control systems homework came with partial solutions. I had a choice: peek first, or use them to verify my AI-assisted work after the fact.

I chose verification. The workflow was simple: ask Claude to solve each problem independently using transfer function analysis and root locus methods, compare results against the provided solutions, identify differences, then apply those learnings to the remaining problems. A homework assignment became a feedback loop where mistakes turned into teaching moments.

## The Verification Workflow in Practice

The key instruction was explicit:

> "Please complete the homework first without looking at the partial solutions, then compare where the partial solutions and my solutions differ and come up with a plan to fix it for that problem."

This forced Claude into a learning posture rather than a copying posture. When the AI discovers its own mistakes, it produces better explanations of *why* something went wrong—exactly what I needed to actually learn the material.

One problem asked for the steady-state error of a unity feedback system with a Type 1 plant. Claude's initial solution applied the final value theorem correctly but used the wrong error constant formula, treating the system as Type 0. Comparing against the solution revealed the gap: the number of free integrators in the loop determines the system type, which then determines which error constant—position, velocity, or acceleration—governs steady-state behavior.

That distinction, something I'd glossed over in lecture notes, stuck after seeing it fail in practice.

The output format mattered too. I had Claude generate HTML that gets printed to PDF via Chrome's headless mode:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --print-to-pdf="hw8.pdf" \
  --no-margins solutions.html
```

This avoided the LaTeX rabbit hole while producing clean, submission-ready documents. Sometimes the simplest approach is the right one.

## Debugging a Ghost Instance on AWS

The same verification pattern surfaced later that day while debugging my Minecraft server's auto-shutdown feature. The symptom: the server should have been running, but SSH connections timed out.

Checking the CloudFormation outputs gave me an instance ID:

```bash
aws cloudformation describe-stacks --stack-name minecraft-server \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" \
  --output text
# Returns: i-0be2a78206b22947e
```

But querying EC2 directly told a different story:

```bash
aws ec2 describe-instances --instance-ids i-0be2a78206b22947e
# An error occurred (InvalidInstanceID.NotFound): 
# The instance ID 'i-0be2a78206b22947e' does not exist
```

The CloudFormation stack showed `CREATE_COMPLETE`. Expected state: instance exists. Actual state: instance gone. Same verification pattern as the homework—compare expected against actual, investigate the difference.

Digging into the CloudFormation template revealed the shutdown mechanism: a Lambda function triggered by CloudWatch alarms when player count drops to zero. The function was supposed to *stop* the instance, preserving it for later restart. But an earlier refactor had changed `stop_instances` to `terminate_instances` without updating the surrounding logic.

The auto-shutdown had worked. It just worked too well. Instead of a stoppable instance waiting for the next play session, I had a terminated instance and a CloudFormation stack pointing at nothing.

The fix was straightforward once identified: revert to `stop_instances` and add a check preventing termination of already-stopped instances. Finding it required the same discipline as the homework—don't assume the system matches its declared state, verify against reality.

## The Learning Happens in the Gap

Both situations followed the same pattern: form an expectation, check it against ground truth, learn from the delta.

For homework, the expectation was "Claude's solution is correct" and the ground truth was the partial solutions. For the infrastructure bug, the expectation was "CloudFormation says the instance exists" and the ground truth was the EC2 API.

Claude's wrong error constant formula taught me more about system types than the lecture did. The terminated-instead-of-stopped bug taught me to audit Lambda function changes more carefully. In both cases, the mismatch created the lesson.

## What I'll Do Differently

Next time I have reference solutions available—for homework, debugging, anything—I'll build verification into the workflow from the start rather than reaching for it as a fallback. The extra structure creates the feedback loops where actual understanding develops.

The homework took longer this way. I could have copied the solutions and finished in twenty minutes. Instead, I spent an hour and a half working through problems, comparing, fixing, and re-solving. But I'll remember the steady-state error formulas now.

That's the trade-off worth making.

