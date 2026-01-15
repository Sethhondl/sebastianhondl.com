---
layout: post
title: "NaN: Three Characters That Mean Your Script Ran Successfully and Told You Nothing"
date: 2025-10-10
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 5
word_count: 1008
---

NaN. The most frustrating output in numerical computing. Your MATLAB script executes without errors, produces a result, and that result is "not a number." Today's debugging session involved a post-processing script for a digital filtering lab, and the culprit was hiding in plain sight.

## The Setup

I'm working through a motion control lab where the goal is to design a 2nd-order IIR high-pass Butterworth filter for processing motor encoder velocity data. The filter removes low-frequency drift from the encoder signal, leaving only the oscillatory component we care about for frequency response analysis.

The workflow: collect data from a motor encoder, filter it in real-time with C++ code running on hardware, then analyze the results in MATLAB to verify the filter's frequency response matches theory. The `postProcess.m` script loads a data file, calculates the RMS amplitude of the filtered signal, and computes the gain in decibels.

Simple enough. But when I ran it on my actual lab data:

```
Gain Analysis:
Output/Input Amplitude Ratio: NaN
Gain in dB: NaN dB
```

## Finding the First Bug

When I plotted the raw and filtered data, something felt off. The script had a 2-second delay to let the filter settle, but I couldn't tell whether that delay was actually being applied correctly. Was the filter broken, or was I analyzing the wrong portion of the data?

The plot showed everything from t=0 onward with no indication of where the "good" data started. The early transient garbage was visually dominating, and I couldn't confirm where the calculations actually began.

The fix was a single line:

```matlab
xline(Tdelay, 'k--', 'LineWidth', 2, 'Label', sprintf('Delay = %.1fs', Tdelay), 'LabelVerticalAlignment', 'bottom')
```

A vertical dashed line at t=2 seconds. Now I could immediately see that the delay *was* being applied correctly—the RMS calculation started well after the transient had settled. The filter was fine. The problem was elsewhere.

## The Real Culprit: Filename Parsing Gone Wrong

My actual lab data file was named `1s50Hz20251010094305rawdata.txt`—a timestamp-based naming convention from the data acquisition system.

The script expected something very different. It was trying to extract the input frequency and amplitude from the filename itself. The original test file was named `50_10test.txt`, which the script parsed as:

- First part before underscore: `50` → frequency = 5.0 Hz (divide by 10)
- Second part: `10` → amplitude = 1.0 V (divide by 10)

Here's what that parsing looked like:

```matlab
parts = strsplit(filename, '_');
Fsig = str2double(parts{1}) / 10;
Vampin = str2double(parts{2}(1:2)) / 10;
```

When `strsplit` tried to parse `1s50Hz20251010094305rawdata.txt`, it couldn't find an underscore. The extraction failed, and `str2double` on garbage strings returns NaN.

NaN then propagated through every downstream calculation. Any arithmetic operation involving NaN returns NaN. So `Camp / NaN` gives NaN, and `20*log10(NaN)` gives NaN. One bad input at the top, garbage all the way down.

## The Fix

The solution was to switch from parsing filenames (fragile) to prompting the user for the actual values (robust):

```matlab
% Prompt user for input parameters
Fsig = input('Enter the input signal frequency (Hz): ');
Vampin = input('Enter the input signal amplitude (V): ');

if ~isempty(Fsig) && ~isempty(Vampin) && Vampin > 0
    gain_ratio = Camp / Vampin;
    gain_dB = 20*log10(gain_ratio);
    
    fprintf('\nGain Analysis:\n');
    fprintf('Output/Input Amplitude Ratio: %.4f\n', gain_ratio);
    fprintf('Gain in dB: %.2f dB\n', gain_dB);
end
```

Is it less automatic? Sure. But it trades a silent failure mode (NaN with no indication why) for an obvious one (wrong numbers that don't match expectations). The person running the script knows what frequency and amplitude they just configured on the hardware.

After fixing the script, I got actual results: the filter showed -3.1 dB attenuation at 5 Hz, close to the expected -3 dB at the cutoff frequency. The math was working all along; it just needed valid inputs.

## The Lesson About Implicit Assumptions

This debugging session crystallized a pattern I've noticed repeatedly: code encodes assumptions that seem obvious at write-time but become invisible mines later. The original author assumed filenames would follow a specific format. That assumption was documented nowhere and embedded in parsing logic that silently produced nonsense when violated.

Here's a heuristic: any time you see string parsing in analysis code, ask "what happens when the format changes?" Filenames are almost never under your complete control. Data acquisition systems have their own conventions. Collaborators rename things. Future you forgets the naming scheme.

## Working With Claude Code

What made this session efficient was the rapid hypothesis-testing cycle. I described the symptom ("the delay doesn't seem to remove data from the plot"), and Claude identified that the plot showed all data while calculations used trimmed data—a subtle distinction I was conflating.

For the NaN issue, having the script and the actual filename visible in the same context made the mismatch obvious. I might have missed this flipping between terminal tabs, mentally holding the filename format while reading parsing code. Seeing both together, the problem was immediate.

## Takeaways

1. **Visual feedback in analysis scripts matters.** A single `xline` showing where your calculations actually start can prevent you from debugging the wrong problem entirely.

2. **Filename parsing is technical debt waiting to happen.** Unless you control the naming convention end-to-end, interactive prompts or config files are more reliable.

3. **NaN is usually a type mismatch or missing data problem.** When you see NaN, trace backward to find the first operation that produced it. Everything after is just propagation.

4. **Describe symptoms, not diagnoses.** "The delay doesn't seem to work" led to a better investigation than "I think the index calculation is wrong" would have. Symptoms let the investigation stay fresh instead of confirming your bias.

5. **RMS-based gain calculations assume steady-state sinusoidal input.** The gain I computed equals the filter's frequency response magnitude only because I was feeding it a pure sine wave and waiting for transients to settle. For arbitrary signals, this shortcut doesn't hold.

Tomorrow I implement the C++ filter. Today I built the tools to know whether it's working.