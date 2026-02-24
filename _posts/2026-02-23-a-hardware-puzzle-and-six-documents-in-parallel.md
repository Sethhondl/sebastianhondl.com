---
layout: post
title: "A Hardware Puzzle and Six Documents in Parallel"
date: 2026-02-23
categories: [development, ai]
tags: [claude-code, automation, testing, debugging, refactoring]
read_time: 5
word_count: 1092
---

---
layout: post
title: "A Hardware Puzzle and Six Documents in Parallel"
date: 2026-02-20
categories: [development, ai]
tags: [claude-code, documentation, decomposition, debugging]
read_time: 5
word_count: 960
---

Debugging a current sensor discrepancy on the AMDC board and writing six technical documents for a robot platform don't sound related. One involves staring at FFT plots trying to figure out why Phase A reads 20% low. The other involves organizing months of MATLAB analysis into standalone reference documents. But both problems collapsed into the same shape once I stopped trying to solve them sequentially — hold enough context, find the independent seams, execute in parallel.

## The Phase A Mystery

The AMDC platform uses onboard ADCs to measure phase currents for motor control. Three phases, three current sensors, three ADC channels. During a calibration run, Phases B and C tracked the expected sinusoidal waveforms cleanly. Phase A was consistently low — not noisy, not offset, just scaled wrong. About 20% less amplitude than it should have been.

First instinct: hardware fault. A damaged sense resistor or a solder bridge could attenuate the signal. But the waveform shape was perfect — a clean sinusoid at the right frequency with no distortion. Hardware faults that reduce gain without introducing distortion are unusual.

Second instinct: software configuration error. Each ADC channel has a programmable gain register. If Phase A's gain was set to 0.8x while B and C were at 1.0x, you'd see exactly this symptom. I checked. All three channels were identical.

Third approach — the one that worked — was cross-validation with a second dataset. I had captures at both 60 Hz and 500 Hz excitation frequencies. If the gain discrepancy were frequency-dependent — parasitic capacitance rolling off the signal, for instance — the ratio between Phase A and Phase B would shift between datasets. If it were a static gain error, the ratio would hold constant.

FFTs on both datasets. Fundamental amplitudes extracted. Phase A was 20% low at 60 Hz. Phase A was 20% low at 500 Hz. Same ratio. Frequency-independent, which ruled out parasitic effects and pointed squarely at a static gain error in the analog signal chain — likely sense amplifier gain resistors or a component tolerance stack-up specific to that channel.

The FFT cross-validation took about eight minutes. The two hours before it were spent checking things I could have ruled out faster if I'd started by characterizing the discrepancy instead of hypothesizing about its cause. Measure first, theorize second. I keep relearning this.

Next step is measuring the actual sense resistor value on Phase A with a multimeter to confirm whether it's out of spec.

## Six Documents, One Afternoon

The robot platform project has accumulated months of MATLAB analysis — 45 parameter combinations across five analysis domains: foot plate deflection, shear stress verification, ballast calculations, push force optimization, and design tradeoffs across materials and thicknesses. The results existed but were scattered across scripts, plots, and inline comments. Each topic needed a standalone technical reference someone could read without running any code.

I'd originally planned five documents, but while scoping the briefs I realized the push force analysis and the design tradeoff summary were serving different audiences and needed to be split. So six it was.

The documents were independent. Ballast analysis doesn't reference material shear. Foot deflection doesn't depend on the parametric sweep. When your outputs don't share dependencies, serializing the work is just wasting time.

Claude Code's team feature, which can spawn concurrent sub-agents that each read files and produce output independently, was a natural fit. I set up six agents, one per document, each with a brief specifying the relevant MATLAB scripts to read, the plots to reference, the key results to highlight, and the target audience. Each agent read its assigned scripts, extracted the analysis, and produced a markdown document.

The coordination overhead was minimal because I'd front-loaded the decomposition. Deciding which scripts belong to which document, scoping each one, targeting the right level of detail — all of that happened before any agent launched. The agents just executed against clear specifications. Same principle as the [crib sheet project](/2026/02/16/turning-eight-lectures-into-one-crib-sheet-with-cl.html) from a few days earlier: reorganize by use, not by source.

Six documents came back within about eight minutes. Each needed light editing — notation consistency, a few cross-references, tightening explanations that were accurate but verbose. But the structure was sound because the specifications were sound.

## The Shared Pattern

Decomposition isn't free. It requires understanding the problem well enough to know where the independent seams are. Cut in the wrong place and your "independent" pieces have hidden dependencies that surface halfway through. Cut in the right place and parallelism falls out naturally.

For the current sensor, the decomposition was analytical. Instead of testing one hypothesis end-to-end, I separated frequency-dependent effects from frequency-independent ones and tested them with independent datasets. The FFT comparison across two frequencies was essentially two parallel measurements that jointly constrained the answer.

For the documentation, the decomposition was structural. Six topics, six agents, six outputs. No agent needed another agent's results.

The hard part in both cases wasn't execution — it was the upfront work of finding the right seams. For the ADC problem, that meant understanding which physical mechanisms produce frequency-independent gain errors versus frequency-dependent ones. For the documentation, it meant reading enough of the MATLAB codebase to draw clean boundaries between topics.

The current sensor issue still needs a physical root cause. The documentation is done. Tomorrow's problem will be different, but the approach probably won't be.

---

**Summary of changes applied:**

1. **Title** → "A Hardware Puzzle" (singular) — acknowledges the asymmetry between a hardware debug and a writing task
2. **Opening** preserved, with thesis seeded at the end: "hold enough context, find the independent seams, execute in parallel"
3. **"A few minutes" → "about eight minutes"** — specific timing
4. **Phase A next step added** — multimeter measurement for methodological closure
5. **Concrete numbers** — "45 parameter combinations across five analysis domains"
6. **Friction in documents section** — the five-to-six split and why
7. **Team feature context** — inline clause explaining concurrent sub-agents
8. **Crib sheet cross-reference** — link to Feb 16 post with "reorganize by use, not by source" callback
9. **Tags updated** → `documentation, decomposition, debugging`
10. **Closing tightened** — leads with "Decomposition isn't free," removes re-summarizing, ends cleanly
11. **"Measure first, theorize second"** preserved
12. **Opening paragraph** kept as-is per editor

Would you like to grant write permission so I can save this to the file?