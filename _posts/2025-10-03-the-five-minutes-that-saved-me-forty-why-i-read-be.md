---
layout: post
title: "The Five Minutes That Saved Me Forty: Why I Read Before I Copy"
date: 2025-10-03
categories: [development, ai]
tags: [claude-code, automation, testing, api, debugging]
read_time: 4
word_count: 944
---

I was about to copy `sineIO.cpp` twice and rename the files when I stopped. The lab instructions said "create 3 files using sineIO as a starting point," but this was a Visual Studio solution, not a folder of loose scripts. Copying just the source file would leave me with three `.cpp` files that couldn't build—no project references, no link to the 826 board API, no connection to the shared timing utilities. The five minutes I spent understanding the structure saved me from a debugging session that would have produced nothing but cryptic linker errors.

## The Codebase I Inherited

The starter code was a Visual Studio solution for an S826 I/O board used in motion control labs:

```
AdcDacSinIo/
├── 826api.h          # Hardware API definitions
├── myWin826.cpp/h    # Windows-specific 826 board wrapper
├── RealTime.cpp/h    # Timing utilities
├── SINEIO/           # The example project to clone
│   └── sineIO.cpp    # Main sine wave I/O demo
├── ADC/              # ADC-specific project (empty)
└── DAC/              # DAC-specific project (empty)
```

The `sineIO.cpp` file demonstrated real-time analog I/O with these configuration constants:

```cpp
#define SAMPLE_RATE  1000    // 1kHz sampling
#define DAC_CONFIG_GAIN S826_DAC_SPAN_10_10   // -10 to 10V
#define DAC_VRANGE    20.0                    // 20V total span
#define DAC_CNT_RANGE 0xFFFF                  // 16-bit resolution
#define DAC_OFFSET_COUNTS 0x8000              // Signed→unsigned mapping
```

That `DAC_OFFSET_COUNTS` constant caught my attention. The DAC takes a 16-bit unsigned integer (0 to 65535), but the output voltage range is -10V to +10V. If you want zero volts, you can't send 0—that would output -10V. You send 32768 (0x8000), the midpoint. Skip this offset and your "zero" signal slams the output to the negative rail. In a motion control lab, that's how you get a motor jumping to full reverse the moment you power on.

## What Exploration Revealed

Before creating anything, I traced through the existing project structure. This surfaced details I would have missed otherwise.

The header includes used relative paths (`../826api.h`, `../myWin826.h`), meaning each project folder expected to sit one level below the shared headers. A flat copy would break these references immediately.

The initialization code had layered error checking:

```cpp
int boardflags = S826_SystemOpen();
if (boardflags < 0)
    errcode = boardflags;
```

I'd seen similar patterns fail silently in a previous lab when I'd copied code without understanding the error handling. The board would fail to initialize, the error code would get set, but nothing would stop execution. The program would run, output garbage to disconnected channels, and I'd spend an hour wondering why my oscilloscope showed nothing.

The configuration constants at the top weren't just tidy organization—they were the lab's adjustable parameters. Change `SAMPLE_RATE` from 1000 to 500 and every timing calculation adapts. Bury that number inside a function and you're hunting through code during the lab while your TA waits.

## The Three Projects

The exploration clarified what each lab project actually needed:

**SINEIO (the template):** Generates a sine wave on the DAC, reads it back on the ADC, demonstrates the full I/O loop. Both input and output channels active.

**DAC project:** Strips out the ADC reading code. Outputs a waveform for measurement on an external oscilloscope. The core change was removing the `S826_AdcRead()` calls and the input processing loop—maybe 40 lines of code, but I needed to understand which 40.

**ADC project:** Removes the sine generation. Reads an external signal and logs or processes it. Here the DAC initialization and output writes get cut, and the ADC configuration becomes the focus.

Without reading the template first, I might have kept the DAC output active in the ADC project, creating an unintended feedback loop, or forgotten to initialize the ADC subsystem because I copied from code that prioritized DAC setup.

## The Pattern Worth Remembering

Engineering labs hand you working examples for a reason: you're supposed to focus on concepts, not boilerplate. But there's a trap in this efficiency. Copy without understanding and you inherit assumptions you don't know about.

A classmate in a previous lab copied a data acquisition script, changed the filename, and spent forty minutes debugging why his readings were nonsense. The original script had a channel offset hardcoded for a different sensor configuration. Five minutes of reading would have surfaced the assumption; forty minutes of trial-and-error didn't.

The five-minute exploration rule applies whether you're using AI assistance or working manually:

1. Find and read the reference implementation
2. Map the file dependencies and build relationships
3. Identify what's configuration versus what's structural
4. Then create new files with actual context

## Questions for the Hardware

The exploration answered my immediate questions—how to structure the projects, what code to keep or cut—but raised others I'll investigate when I run the actual hardware.

The template configures a 1kHz sample rate and a 16-bit DAC. That's a clean configuration on paper, but what does quantization actually look like when I output a sine wave and read it back? The code handles the signed-to-unsigned voltage mapping, but I don't yet know how much noise the board introduces, or whether the timing utilities maintain precise intervals under Windows' non-real-time scheduler.

Those questions require the oscilloscope and the running hardware, not more code reading. But I'll be looking for them specifically because the exploration told me where the assumptions live.

## The Real Deliverable

The three project files exist now, structured correctly and ready to build. But the more useful outcome is knowing which constants to adjust when experiments require different configurations, and understanding what silence from the error handling actually means.

The lab will have enough real problems to debug. Linker errors from a careless copy shouldn't be one of them.