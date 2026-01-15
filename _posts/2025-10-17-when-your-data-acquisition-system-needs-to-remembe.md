---
layout: post
title: "When Your Data Acquisition System Needs to Remember What It's Testing"
date: 2025-10-17
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 4
word_count: 989
---

There's a particular kind of debugging session that every engineer dreads: the one where you're staring at a folder full of files named `data1.txt`, `data2.txt`, and `run_final_v3_FINAL.txt`, trying to remember which test conditions produced which results.

I experienced this firsthand last week. I needed the 5 Hz sweep with 1V amplitude and added mass. I opened `SysID1.txt`—wrong, that was 10 Hz. Opened `SysID2.txt`—closer, but no mass. Opened `SysID1_new.txt`—right frequency, but 0.5V amplitude. Twenty minutes later, I'd found my file, but I'd also found my motivation to fix the naming problem permanently.

## The Problem: Mystery Data Files

The system identification program I inherited was functional but frustrating. It ran frequency sweeps on a motor system, collected data through an ADC, and saved everything to text files. The filenames, however, were basically meaningless. When you're running dozens of tests at different frequencies and amplitudes, with and without added mass, keeping track of what's what becomes a nightmare.

What I wanted: files that tell you exactly what they contain, just from the name. Something like `2.0Hz_0.5V_mass_20251017_140823.txt` instead of `output.txt`. With descriptive names, I could glance at a directory listing and immediately spot the file I needed—no opening required.

## The First Fix: User Input and Timestamps

The original code had a static filename buried in a 30-character buffer:

```cpp
char outfileName[30];
// ... later ...
sprintf(outfileName, "SysID1.txt");
```

My new filename format runs about 40 characters, so the first change was increasing the buffer:

```cpp
char outfileName[64];
```

Next, I added prompts to capture test parameters before starting data collection:

```cpp
double Amp = 0;
double Frequency = 0;
bool hasMass = false;
char massInput;

printf("Enter test frequency (Hz): ");
scanf("%lf", &Frequency);

printf("Enter test amplitude (V): ");
scanf("%lf", &Amp);

printf("Test with mass? (y/n): ");
scanf(" %c", &massInput);
hasMass = (massInput == 'y' || massInput == 'Y');
```

For the timestamp, I used standard C time functions:

```cpp
time_t now = time(NULL);
struct tm* timeinfo = localtime(&now);
char timestamp[20];
strftime(timestamp, sizeof(timestamp), "%Y%m%d_%H%M%S", timeinfo);
```

Then combined everything into the filename:

```cpp
sprintf(outfileName, "%.1fHz_%.1fV_%s_%s.txt", 
        Frequency, Amp, 
        hasMass ? "mass" : "nomass", 
        timestamp);
```

A note on input validation: this lab code trusts that the operator enters sensible values. Production code would need bounds checking, but for a controlled lab environment where the same few people run all the tests, simplicity was worth the trade-off.

## The Twist: Different Frequencies for Different Configurations

Here's where it got more interesting. The system behaves differently with and without added mass. More mass means more inertia, which lowers the natural frequency—the heavier system simply can't respond as quickly to high-frequency inputs. This means different frequency ranges matter for each configuration.

The no-mass frequencies: 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30 Hz

The with-mass frequencies: 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 12 Hz

Notice how the with-mass array tops out at 12 Hz while the no-mass array goes to 30 Hz. Above 12 Hz, the mass-loaded system's response is so attenuated that measurements become noise-dominated.

Rather than making the user remember which frequencies to test, the program now selects the appropriate set automatically:

```cpp
const double freqsNoMass[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30};
const double freqsWithMass[] = {1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 12};

const double* frequencies;
int numFreqs;

if (hasMass) {
    frequencies = freqsWithMass;
    numFreqs = sizeof(freqsWithMass) / sizeof(double);
} else {
    frequencies = freqsNoMass;
    numFreqs = sizeof(freqsNoMass) / sizeof(double);
}
```

## The Downstream Payoff: Batch Processing That Works

Once the data files are collected, a MATLAB script processes them in batch to generate Bode plots. The script uses regex to parse the filename and extract test parameters:

```matlab
freq_amp_match = regexp(baseName, '(\d+\.?\d*)Hz_(\d+\.?\d*)V', 'tokens');
frequency_Hz = str2double(freq_amp_match{1}{1});
amplitude_V = str2double(freq_amp_match{1}{2});
```

With the new naming scheme, the script can also detect the mass condition:

```matlab
hasMass = contains(baseName, '_mass_');
```

This means automated processing can separate with-mass and without-mass data into different Bode plots without any manual sorting.

## What I Learned

**Naming conventions are architecture decisions.** A good filename scheme is essentially a contract between your data collection code and your analysis code. Before I modified anything in the C++ program, I checked how the MATLAB scripts parsed filenames. That context-awareness meant the upstream changes would play nicely with the existing analysis pipeline.

A note on delimiters: I use underscores to separate fields and periods only for decimal values within numeric fields. The regex `(\d+\.?\d*)Hz` handles the decimal point correctly because it looks for digits and optional decimal points before the `Hz` unit marker. The key is consistency—pick a scheme and stick to it.

Encoding experimental conditions in filenames feels hacky compared to using a proper database, but for a lab environment where you need to quickly browse results and share data with teammates who might not have your analysis tools, it's remarkably practical.

## Practical Takeaways

1. **Front-load the metadata**: Ask for test parameters before starting data collection, not after. Future-you will thank present-you.

2. **Use ISO-style timestamps**: `YYYYMMDD_HHMMSS` sorts correctly in any file browser and is unambiguous across locales.

3. **Size your buffers for the actual content**: If your new filename format is longer than the old one, update the buffer size. Off-by-one errors in C string handling are a classic source of bugs.

4. **Think about the analysis pipeline**: Your filename scheme should match what your downstream processing expects. Check the regex patterns in your analysis scripts before committing to a format.

Sometimes the most valuable code changes aren't about algorithms or performance—they're about making your future self's life easier when you're hunting for that one specific test run among dozens. The twenty minutes I spent lost in a maze of `SysID_new_final.txt` files? That's twenty minutes I'll never waste again.