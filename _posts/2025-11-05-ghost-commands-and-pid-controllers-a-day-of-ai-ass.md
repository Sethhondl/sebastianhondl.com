---
layout: post
title: "Ghost Commands and PID Controllers: A Day of AI-Assisted Debugging"
date: 2025-11-05
categories: [development, ai]
tags: [claude-code, python, javascript, git, testing]
read_time: 3
word_count: 788
---

The Discord slash commands wouldn't go away. I'd removed the bot from my Minecraft server days ago, but every time someone typed `/` in the chat, the phantom commands appeared—mocking me, refusing to die. This turned into the most interesting debugging puzzle of the day, sandwiched between motion control prelabs and exam prep.

## The Ghost Command Hunt

Here's what tripped me up: I assumed Discord slash commands were tied to bot presence. Remove the bot, commands disappear. Reasonable assumption, completely wrong.

Discord registers slash commands at the application level, stored on their servers independently of whether your bot is connected to a guild. When you kick a bot, Discord doesn't clean up after it. The commands persist like digital graffiti.

Claude helped me trace the architecture. Commands live at this endpoint:

```
https://discord.com/api/v10/applications/{APP_ID}/guilds/{GUILD_ID}/commands
```

The fix required explicitly deleting each registered command via the API:

```python
import requests

def purge_ghost_commands(app_id, guild_id, bot_token):
    headers = {"Authorization": f"Bot {bot_token}"}
    base_url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
    
    # Get all registered commands
    commands = requests.get(base_url, headers=headers).json()
    
    # Delete each one
    for cmd in commands:
        requests.delete(f"{base_url}/{cmd['id']}", headers=headers)
        print(f"Deleted: {cmd['name']}")
```

Why does Discord separate command registration from bot presence? I suspect it's for production reliability—keeping commands available during brief disconnections—but I couldn't find official documentation confirming this. Whatever the reason, the behavior creates cleanup headaches during development that aren't obvious until you hit them.

## The PID Controller Prelab

Earlier that morning, I'd been working through a prelab for Lab 8 on PID control. The assignment: implement proportional, PI, and PID controllers for a DC servomotor using a Sensoray 826 data acquisition board.

The interesting part wasn't the control theory—it was watching Claude navigate my existing codebase. When I mentioned needing Ziegler-Nichols tuning parameters, Claude first explored my Lab 7 files to find the experimentally determined values: Kcr (critical gain) and Pcr (critical period). These measurements from previous experiments were prerequisites for calculating the new controller gains.

Rather than generating generic PID code, Claude built on my existing `myWin826.h` wrapper functions:

```cpp
void runPIDController(double Kp, double Ki, double Kd, double Ts) {
    double error, previous_error = 0;
    double integrated_error = 0;
    double error_derivative;
    double control_voltage;
    
    while (running) {
        double actual = readEncoderPosition();
        double reference = getReferenceSignal();
        
        error = reference - actual;
        integrated_error += error * Ts;
        error_derivative = (error - previous_error) / Ts;
        
        control_voltage = Kp * error + Ki * integrated_error + Kd * error_derivative;
        
        writeDAC(0, control_voltage);
        logData(error, control_voltage);
        
        previous_error = error;
        waitForNextSample(Ts);
    }
}
```

One limitation worth noting: this implementation lacks anti-windup protection. In a real system, the integral term can accumulate to absurd values when the actuator saturates, causing massive overshoot when the error finally reverses. For a prelab demonstration this works, but any production PID controller needs integral clamping to handle saturation gracefully.

## Context-Aware Formatting

A smaller task rounded out the day: adding material specifications to an HTML exam reference sheet for a wind turbine analysis course. I needed to explain what "Steel (ASTM A572 Grade 50)" means in about 20 words, formatted to match the existing document.

The cheat sheet was already dense—three-column layout, 6pt font, consistent styling throughout:

```html
<div class="formula-box">
  <strong>ASTM A572 Grade 50:</strong> Structural steel, 
  Fy = 50 ksi yield, Fu = 65 ksi ultimate, 
  commonly used for wind turbine towers and frames.
</div>
```

Not technically complex, but it demonstrated something useful: Claude read the entire file structure before editing, matching the existing CSS classes and formatting patterns exactly. No style drift, no reformatting of adjacent sections.

## The Common Thread

Looking at ghost commands, motor control, and document formatting together, one pattern emerges: investigation before implementation.

For the Discord problem, jumping straight to "how do I delete slash commands" would have given me the API call. But understanding *why* commands persist explained the behavior and will prevent confusion on future projects.

For the PID prelab, Claude could have generated textbook controller code immediately. Instead, it explored Lab 7 first, found my critical gain measurements, and matched my existing function signatures. The result compiled without modification.

Even the exam sheet addition reinforced the same lesson: reading existing structure before adding new content prevents the small inconsistencies that accumulate into messy codebases.

## The Takeaway

Tomorrow I'll probably hit another debugging puzzle where the obvious assumption is wrong. The ghost command hunt was a reminder to question those assumptions earlier. When something doesn't behave as expected, the first question should be "what am I assuming about how this system works?" rather than "what code fixes the symptom?"

That's the real value of AI-assisted debugging: not the code generation, but the collaborative investigation that surfaces the actual cause before you've committed to the wrong solution.