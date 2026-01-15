---
layout: post
title: "When Your Lab Report Needs 23 PNG Files by 11 PM"
date: 2025-10-16
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 5
word_count: 1039
---

At 6:14 PM on a Tuesday, I counted the plots my postlab report needed: 23 PNG files, zero generated, and a deadline in less than five hours. What followed was an exercise in academic triage—and an interesting case study in how AI assistants handle the messy reality of engineering coursework.

## The Setup: Digital Filters and Deadline Pressure

I'm taking ME4231 (Motion Control) this semester, and Lab 5 covers digital filtering—specifically, analyzing how different IIR filter implementations affect signal processing on embedded systems. The postlab requires plots showing raw vs. filtered signals, frequency response curves, and comparison tables for multiple test conditions.

The problem? I had MATLAB code scattered across several files, experimental data in text files with cryptic naming conventions like `50_10test.txt`, and a markdown template that was more placeholder than substance.

## What Actually Happened

My first request was straightforward: "can you generate all plots and tables needed for post lab 5 and save them as pngs using matlab"

Claude immediately started exploring the codebase—finding the lab PDF, my existing postlab template, and the various MATLAB scripts I'd accumulated. Before writing any new code, it read through `postlab_report.md`, `postProcess.m`, and the lab instructions to understand what was already there and what was actually required.

Here's where things got interesting. The existing `postProcess.m` script could handle individual files, but I needed batch processing. Claude identified this gap and modified the script to loop through all test files:

```matlab
% Original approach: process one file at a time, manually
postProcess('50_10test.txt', 1.0)
postProcess('50_20test.txt', 1.0)
% ... repeat 20 more times

% Modified approach: automatic batch processing
function results = batchPostProcess(directory)
    files = dir(fullfile(directory, '*.txt'));
    results = struct('filename', {}, 'rms_raw', {}, 'rms_filtered', {}, 'attenuation_dB', {});
    
    for i = 1:length(files)
        baseName = files(i).name;
        filepath = fullfile(directory, baseName);
        
        [raw_signal, filtered_signal, fs] = loadAndFilter(filepath);
        results(i).filename = baseName;
        results(i).rms_raw = rms(raw_signal);
        results(i).rms_filtered = rms(filtered_signal);
        results(i).attenuation_dB = 20 * log10(results(i).rms_filtered / results(i).rms_raw);
        
        % Generate and save plot for this file
        savePlot(raw_signal, filtered_signal, fs, baseName);
    end
end
```

The batch approach meant I could regenerate all plots with a single function call—something that would have taken 20+ minutes of manual execution otherwise.

## Where Things Got Messy

The first version of the batch script ran without errors but produced plots with the transient settling time still visible in the high-pass filter output. The first 0.5 seconds of filtered data showed the filter's initial response rather than steady-state behavior, skewing the RMS calculations.

Claude's fix added a settling time parameter:

```matlab
% Skip initial transient (0.5 seconds at 1000 Hz sampling rate)
settle_samples = round(0.5 * fs);
filtered_signal_steady = filtered_signal(settle_samples:end);
```

This kind of iterative debugging—running the script, spotting the problem in the output, refining—happened three or four times before the plots looked right. The amplitude ratio calculations also needed adjustment because I'd forgotten that the input signal amplitude varied between test cases.

## Handling Two Labs in One Session

With Lab 5's plots saved and verified, I pivoted to Lab 6's prelab requirements. This wasn't a clean switch—it was deadline math. Lab 5 was due at 11 PM, Lab 6's prelab was due the next morning, and I had about two hours of work left on each.

What made the context switch manageable was that Claude had already mapped out my project structure. When I asked about Lab 6, it didn't start from scratch—it found my existing `lab6_prelab_guide.md` and used it as a reference. I could say "set up the batch processing for Lab 6 the same way" and get a script that followed the same patterns.

Lab 6 involves servomotor frequency response and transfer function estimation. The prelab required a script to load multiple frequency sweep files, calculate RMS-to-amplitude conversions, and generate a Bode plot. The key detail from my guide that Claude incorporated:

```matlab
% The guide explicitly warned about this conversion
% Input frequencies are in Hz, but Bode plots use rad/s
angular_freq = all_frequencies * 2 * pi;

% Magnitude calculation: ratio of output to input amplitude
magnitude_dB = 20 * log10(output_amplitude ./ input_amplitude);
```

Getting the Hz-to-rad/s conversion wrong would have shifted the entire Bode plot horizontally—the kind of error that's easy to miss at 10 PM but obvious when your corner frequency doesn't match the design spec.

## The Outcome

By 10:43 PM, I had all 23 Lab 5 plots generated and embedded in my postlab markdown. The batch processing approach paid off when I realized I'd miscalculated one of the filter parameters—regenerating everything took 30 seconds instead of 20 minutes.

The Lab 6 prelab script was ready for the next morning's data, verified against a subset of test files to ensure the Bode plot structure was correct.

## Practical Takeaways

**AI assistants excel at connecting scattered pieces.** I had lab instructions in PDF, code in multiple `.m` files, and data in text files. Claude's value wasn't in writing perfect code from scratch—it was in reading everything and understanding what needed to connect to what.

**Build the loop structure before you need it.** Both labs required processing multiple data files with similar operations. When I found the amplitude ratio error in Lab 5, having batch processing already in place meant the fix propagated across all 23 plots in seconds.

**Unit conversions are where errors hide.** The Lab 6 guide explicitly warns about Hz vs. rad/s conversions. This is exactly the kind of detail that's easy to forget at 11 PM but completely breaks your analysis if you get it wrong.

**Expect iteration.** The settling time issue, the amplitude ratio bug, the file naming confusion—none of these were caught on the first pass. The workflow wasn't "ask Claude, get perfect code." It was "ask Claude, run it, find the problem, fix it, repeat."

## What's Next

The Lab 5 plots showed the expected -20 dB/decade rolloff in the frequency response, and the corner frequency landed within 5% of the design specification. Tomorrow's task is running the Lab 6 prelab script against the actual frequency sweep data and verifying that the transfer function estimate matches the motor's datasheet parameters.

Whether that works will depend on whether the physical measurements match the theory—which is the part of engineering that can't be batch-processed.