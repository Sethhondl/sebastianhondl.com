---
layout: post
title: "When Everything Lies About Its State: GIF Frames, Exam Deadlines, and a Discord Bot That Couldn't Accept Reality"
date: 2025-12-10
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 4
word_count: 951
---

At 2:47 PM, I was staring at a Discord embed showing a cheerful green dot next to "Server Online" while simultaneously SSH'd into the Minecraft server watching it sit completely stopped. Somewhere between extracting animation frames for a controls engineering report due at midnight and debugging why a bot couldn't tell the difference between "running" and "not running," I realized every problem I'd touched that day was fundamentally the same: something's actual state didn't match its representation.

## Racing the Clock: Animation Frames for a LaTeX Deadline

The morning started with an email reminder: final report for ME 451 due at 11:59 PM. The six-bar linkage synthesis project was complete, but the documentation wasn't. I had five GIF animations showing different mechanism solutions, but LaTeX's `animate` package needs numbered PNG frames, not GIFs.

My usual tools weren't an option. The university computing environment didn't have ImageMagick installed, and I didn't have admin rights to add it. ffmpeg was similarly absent. But Python with Pillow was available:

```python
from PIL import Image

def extract_gif_frames(gif_path, output_dir):
    img = Image.open(gif_path)
    frame_num = 0
    while True:
        try:
            img.seek(frame_num)
            frame = img.copy()
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            frame.save(output_dir / f'frame_{frame_num:04d}.png')
            frame_num += 1
        except EOFError:
            break
    return frame_num
```

Writing the script took fifteen minutes. Running it across all five solution folders took ten seconds. When I noticed one animation had a timing issue and needed regeneration, I just ran the script again instead of repeating a manual process. Deadline pressure forced the better solution.

## The Controls Final: AI as Study Partner

That same afternoon, I needed to complete a take-home controls final. Before anyone reaches for the academic integrity pitchfork: this was explicitly an open-book, open-notes, open-tools exam. The professor's policy permitted any resources except collaboration with other students, reflecting the reality that actual engineering work involves looking things up.

My approach with Claude wasn't "solve this problem for me" but "help me work through this systematically while showing all steps." The difference matters.

What made this effective was context. I fed Claude the relevant lecture notes, homework solutions showing the professor's expected notation, and Simulink models from class. Without that context, asking about linearizing a chemostat system would produce a generic textbook approach. With it, the output matched the specific formulation we'd used all semester—the same variable names, the same matrix conventions, the same equilibrium expressions.

The broader lesson: AI assistance quality scales with context quality. Vague prompts get vague answers.

## The Green Dot That Wouldn't Die

Back to that Discord status embed mocking me at 2:47 PM.

The Minecraft server runs on EC2, with a Discord bot showing server status in a dedicated channel. Lambda functions handle slash commands like `/start`, the EC2 instance runs both the Minecraft server and a Python bot for live status updates, and DynamoDB stores persistent data.

The status logic looked correct:

```python
if restoring:
    embed_color = discord.Color.gold()
elif is_running:
    embed_color = discord.Color.green()
else:
    embed_color = discord.Color.red()
```

Green if running, red if stopped, gold if restoring. So why was it green when the server was definitely stopped?

The bug was in how `is_running` got its value. The bot determined server state by checking whether the Minecraft process was running locally. But if the server crashed or was stopped via SSH rather than through the bot's shutdown command, the bot never received a signal to update. It just kept displaying whatever it last knew.

Worse, if the bot itself wasn't running after an EC2 reboot, the Discord message would sit there showing green indefinitely.

The fix had two parts. First, a watchdog that polls actual process state and corrects drift:

```python
@tasks.loop(seconds=30)
async def verify_status():
    actual_running = is_minecraft_process_running()
    if self.displayed_status != actual_running:
        await update_status_embed(actual_running)
        self.displayed_status = actual_running
```

Second, Lambda functions now check EC2 instance state directly rather than trusting cached data when responding to `/status` commands.

The satisfying moment came around 4 PM when I stopped the Minecraft server via SSH, watched the status embed, and saw it flip from green to red without manual intervention. State finally matched representation.

## The Thread Connecting Everything

Every problem that day was a variation on the same theme: ensuring appearance matches reality.

The GIF conversion transformed one representation into another that a different system could use. The controls exam involved linearization—approximating nonlinear behavior around an operating point, where a wrong representation means your controller fails when reality diverges from the model. The Discord bot was lying because its representation had disconnected from actual state.

This pattern appears everywhere in software: stale caches, UIs that don't reflect backend state, monitoring dashboards that miss failures. The solution is always some combination of proper invalidation, polling as a fallback, and acknowledging that any representation can drift from reality.

## What Actually Surprised Me

I expected the controls exam to be the hard part. Linearizing nonlinear systems, designing observers, proving stability—that's the stuff that should be difficult.

Instead, the Discord bot ate more of my afternoon. The controls problems had clear methodology: follow the steps, apply the formulas, check your work. The bot bug required tracing through distributed components to find where synchronization broke down. There wasn't a formula for that.

The day ended with frames ready for LaTeX, exam solutions documented in MATLAB, and a Minecraft server that accurately reports when it's offline. Three different domains, one underlying problem: keeping representations honest about the state they claim to show.

The next time you see a green status indicator, maybe give it a skeptical glance. It might just be telling you what it last believed rather than what's actually true.