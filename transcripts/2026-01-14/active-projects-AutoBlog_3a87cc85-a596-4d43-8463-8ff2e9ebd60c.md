# Claude Conversation Transcript

---

## User [2026-01-14T23:45:41.676Z]

You are doing a final polish pass on a blog post before publication.

## Blog Post to Polish
# Reverse-Engineering Black-Box MATLAB: When Your Flywheel Analysis Hits a Wall

I was staring at a `.p` file when the problem crystallized. The electrical engineering team had sent over their motor analysis code for the flywheel project—compiled MATLAB, no source. I could call their functions, but I couldn't see what they did. This is the kind of constraint that makes AI-assisted engineering genuinely useful: not replacing thought, but accelerating the detective work.

## The Project: Grid-Scale Energy Storage in a Spinning Disk

The assignment is part of my Mechanical Engineering Modeling course: characterize a baseline flywheel energy storage system for grid frequency regulation. If you're not familiar with power grids, here's the key context—the electrical grid must maintain a constant frequency (60 Hz in the US), and any mismatch between power generation and consumption causes frequency drift. Flywheels act as physical batteries: spin them up to store energy, let them slow down to release it. They can respond in milliseconds, making them ideal for smoothing out short-term fluctuations.

The challenge is modeling the losses. A flywheel sitting in a vacuum, spinning on magnetic bearings, still loses energy—through the bearings themselves, through aerodynamic drag (even in partial vacuum), and through electromagnetic effects in the motor/generator. My job was to build a thermal and efficiency model for the rotor losses specifically.

## Working with Black-Box Code

The `.p` files from the EE team included functions for stator current calculations and magnetic field distributions. Compiled MATLAB is common in cross-team projects—it protects IP and prevents accidental modifications—but it means you're working blind.

I asked Claude to help me infer what the functions likely computed based on their signatures and the physics involved. The conversation went something like this:

**Me:** I have a function `calcMagneticField(statorCurrent, rotorPosition, magnetParams)` that returns a struct with `Br`, `Bz`, and `Btheta` fields. Given that this is a surface-mounted permanent magnet machine, what's it probably calculating?

**Claude:** Based on the output structure, this is likely computing the radial, axial, and tangential components of the magnetic flux density in the air gap. For a surface PM machine, `Br` would be dominated by the permanent magnets (relatively constant with position), while the stator current contribution would primarily affect `Btheta` through the armature reaction field. The axial component `Bz` is typically small but matters for eddy current loss calculations in the end regions...

This kind of back-and-forth let me build a mental model of the black-box functions without seeing the source. I could then test my assumptions by calling the functions with known inputs and checking whether the outputs matched expected physics.

## Modeling Rotor Losses

With the black-box functions characterized, I built the loss model. Here's the core function:

```matlab
function losses = rotorLosses(magnetThickness, rotorDiameter, axialLength, statorCurrent, rotorSpeed)
    % Rotor losses include:
    % 1. Eddy current losses in permanent magnets
    % 2. Hysteresis losses in rotor iron (back-iron and laminations)
    %
    % Governing equations from Gieras, "Permanent Magnet Motor Technology" Ch. 11
    
    % Convert rotational speed to electrical frequency
    freq = rotorSpeed / 60;  % [Hz] - for 2-pole machine, elec freq = mech freq
    
    % Rotor surface area (cylindrical approximation)
    A_rotor = pi * rotorDiameter * axialLength;  % [m^2]
    
    % EDDY CURRENT LOSSES: P_eddy ∝ f^2 * B^2 * t^2
    % These dominate at high speeds due to f^2 scaling
    Br = 1.2;  % Magnet remanence for NdFeB at 80°C [T]
    
    % Note: This is a simplified model. In reality, the rotor magnets see 
    % a relatively constant field from themselves; the time-varying component
    % comes from stator slot harmonics and armature reaction. We approximate
    % this as proportional to stator current for the loss calculation.
    B_ripple = 0.15 * (statorCurrent / 100);  % Ripple field amplitude [T]
                                               % 100A = rated current for this design
    
    k_eddy = 2.5e-3;  % Empirical constant, fitted to FEA results
    P_eddy = k_eddy * freq^2 * B_ripple^2 * magnetThickness^2 * A_rotor;
    
    % HYSTERESIS LOSSES: P_hyst ∝ f * B^2
    % Linear with frequency, but still significant at high flux densities
    k_hyst = 0.05;  % For silicon steel laminations
    P_hyst = k_hyst * freq * B_ripple^2 * A_rotor;
    
    losses = P_eddy + P_hyst;
end
```

The physics insight worth highlighting: eddy current losses scale with frequency squared, while hysteresis losses scale linearly. This means at low speeds, the two are comparable, but as the flywheel spins up, eddy currents rapidly dominate. For our design operating at 20,000 RPM (333 Hz electrical), eddy currents account for roughly 85% of the rotor losses. This has direct implications for magnet selection—thinner magnet segments reduce eddy losses quadratically.

For a typical operating point (10mm magnets, 0.5m rotor diameter, 0.3m axial length, 80A stator current, 15,000 RPM):

```
>> losses = rotorLosses(0.010, 0.5, 0.3, 80, 15000)
losses = 847.3  % Watts
```

Compared to the 500 kWh storage capacity of the system, this represents about 0.17% loss per hour from rotor electromagnetic effects alone—significant for a system designed to hold charge for hours.

## Self-Contained Deliverables

One decision that paid off: when consolidating the analysis, I asked Claude to help structure everything so someone could download a single directory and run the full simulation. This meant:

1. Copying the `.p` files into the project directory (with documentation noting they're dependencies from the EE team)
2. Adding a `README.md` with MATLAB version requirements
3. Including sample input files with the exact format expected
4. Adding a `run_analysis.m` script that exercises all functions with default parameters

The forcing function here was documentation. Writing "Deliverable 1, sub-deliverable a" comment blocks with explicit assumptions made me catch two errors in my thermal modeling before they propagated.

## What I'd Do Differently

Looking back at today's session, the most valuable Claude interactions were the ones where I asked for physics reasoning, not code generation. When I said "write me a loss function," the results were generic. When I said "the EE team's function returns these values for these inputs—what physical assumptions would produce this behavior?", the reasoning was sharp and specific.

Tomorrow's work: debugging the Active Magnetic Bearing controller design. The step response is showing unexpected oscillation, which probably means my linearization around the operating point isn't capturing some nonlinearity in the force-current relationship. The flywheel project continues.

---

*For readers interested in flywheel energy storage systems, the [Beacon Power](https://beaconpower.com/resources/) resource page has accessible overviews, and Gieras's "Permanent Magnet Motor Technology" covers the electromagnetic loss modeling in depth.*

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

## Assistant [2026-01-14T23:45:59.957Z]

# Reverse-Engineering Black-Box MATLAB: When Your Flywheel Analysis Hits a Wall

The problem crystallized the moment I opened the file. The electrical engineering team had sent over their motor analysis code for the flywheel project—compiled MATLAB, no source. I could call their functions, but I couldn't see inside them. This is exactly where AI-assisted engineering earns its keep: not replacing thought, but accelerating the detective work when you're flying blind.

## The Project: Grid-Scale Energy Storage in a Spinning Disk

This assignment is part of my Mechanical Engineering Modeling course: characterize a baseline flywheel energy storage system for grid frequency regulation. The core concept is straightforward—the electrical grid must maintain a constant 60 Hz frequency, and any mismatch between generation and consumption causes drift. Flywheels act as physical batteries: spin them up to store energy, let them slow down to release it. With millisecond response times, they're ideal for smoothing short-term fluctuations.

The challenge lies in modeling the losses. Even a flywheel spinning in a vacuum on magnetic bearings bleeds energy—through the bearings, through residual aerodynamic drag, and through electromagnetic effects in the motor/generator. My task was building a thermal and efficiency model for the rotor losses specifically.

## Working with Black-Box Code

The `.p` files from the EE team included functions for stator current calculations and magnetic field distributions. Compiled MATLAB is standard in cross-team projects—it protects IP and prevents accidental modifications—but it means you're essentially reverse-engineering physics from function signatures.

I asked Claude to help infer what the functions likely computed based on their inputs, outputs, and the underlying physics:

**Me:** I have a function `calcMagneticField(statorCurrent, rotorPosition, magnetParams)` that returns a struct with `Br`, `Bz`, and `Btheta` fields. Given that this is a surface-mounted permanent magnet machine, what's it probably calculating?

**Claude:** Based on the output structure, this is likely computing the radial, axial, and tangential components of the magnetic flux density in the air gap. For a surface PM machine, `Br` would be dominated by the permanent magnets (relatively constant with position), while the stator current contribution would primarily affect `Btheta` through the armature reaction field. The axial component `Bz` is typically small but matters for eddy current loss calculations in the end regions...

This back-and-forth let me construct a mental model of the black-box functions without seeing the source. I could then validate my assumptions by calling the functions with known inputs and checking whether the outputs matched expected physics.

## Modeling Rotor Losses

With the black-box functions characterized, I built the loss model:

```matlab
function losses = rotorLosses(magnetThickness, rotorDiameter, axialLength, statorCurrent, rotorSpeed)
    % Rotor losses include:
    % 1. Eddy current losses in permanent magnets
    % 2. Hysteresis losses in rotor iron (back-iron and laminations)
    %
    % Governing equations from Gieras, "Permanent Magnet Motor Technology" Ch. 11
    
    % Convert rotational speed to electrical frequency
    freq = rotorSpeed / 60;  % [Hz] - for 2-pole machine, elec freq = mech freq
    
    % Rotor surface area (cylindrical approximation)
    A_rotor = pi * rotorDiameter * axialLength;  % [m^2]
    
    % EDDY CURRENT LOSSES: P_eddy ∝ f^2 * B^2 * t^2
    % These dominate at high speeds due to f^2 scaling
    Br = 1.2;  % Magnet remanence for NdFeB at 80°C [T]
    
    % Note: This is a simplified model. In reality, the rotor magnets see 
    % a relatively constant field from themselves; the time-varying component
    % comes from stator slot harmonics and armature reaction. We approximate
    % this as proportional to stator current for the loss calculation.
    B_ripple = 0.15 * (statorCurrent / 100);  % Ripple field amplitude [T]
                                               % 100A = rated current for this design
    
    k_eddy = 2.5e-3;  % Empirical constant, fitted to FEA results
    P_eddy = k_eddy * freq^2 * B_ripple^2 * magnetThickness^2 * A_rotor;
    
    % HYSTERESIS LOSSES: P_hyst ∝ f * B^2
    % Linear with frequency, but still significant at high flux densities
    k_hyst = 0.05;  % For silicon steel laminations
    P_hyst = k_hyst * freq * B_ripple^2 * A_rotor;
    
    losses = P_eddy + P_hyst;
end
```

The key physics insight: eddy current losses scale with frequency squared, while hysteresis losses scale linearly. At low speeds, the two are comparable. As the flywheel spins up, eddy currents rapidly dominate. At our design's 20,000 RPM operating point (333 Hz electrical), eddy currents account for roughly 85% of rotor losses. This has direct implications for magnet selection—thinner magnet segments reduce eddy losses quadratically.

For a typical operating point (10mm magnets, 0.5m rotor diameter, 0.3m axial length, 80A stator current, 15,000 RPM):

```
>> losses = rotorLosses(0.010, 0.5, 0.3, 80, 15000)
losses = 847.3  % Watts
```

Against the system's 500 kWh storage capacity, this represents about 0.17% loss per hour from rotor electromagnetic effects alone—significant for hardware designed to hold charge for hours.

## Self-Contained Deliverables

One decision that paid off: structuring everything so someone could download a single directory and run the full simulation. This meant copying the `.p` files into the project directory with proper attribution, adding a README with MATLAB version requirements, including sample input files in the expected format, and writing a `run_analysis.m` script that exercises all functions with default parameters.

The forcing function was documentation. Writing explicit "Deliverable 1, sub-deliverable a" comment blocks with assumptions spelled out made me catch two errors in my thermal modeling before they propagated downstream.

## The Takeaway

Looking back at today's session, the most valuable Claude interactions were the ones where I asked for physics reasoning rather than code generation. When I said "write me a loss function," the results were generic. When I said "the EE team's function returns these values for these inputs—what physical assumptions would produce this behavior?", the reasoning was sharp and specific.

The lesson extends beyond this project: AI assistance works best when you treat it as a physics collaborator, not a code factory. Ask it to reason about why a system behaves the way it does, and the implementation follows naturally.

Tomorrow's challenge: debugging the Active Magnetic Bearing controller. The step response is showing unexpected oscillation, which probably means my linearization isn't capturing some nonlinearity in the force-current relationship. The flywheel keeps spinning.

---

*For readers interested in flywheel energy storage, the [Beacon Power](https://beaconpower.com/resources/) resource page offers accessible overviews, and Gieras's "Permanent Magnet Motor Technology" covers electromagnetic loss modeling in depth.*

