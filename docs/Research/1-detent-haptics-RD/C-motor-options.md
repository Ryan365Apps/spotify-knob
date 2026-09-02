# Strand C — Motor options for the dynamic-feel layer

Research strand C of the detent/haptics R&D brief for the 60 by Cadrane. This document evaluates the motor layer: the machine that adds software-defined effects (end-stops, resistance ramps, half-steps, per-context feel) on top of the passive 60-position magnetic detent. Findings first, recommendation at the end.

Settled context this strand builds on (not re-litigated here): sixty Ø2.5 mm steel poles (M2.5 grub screws) in the knob's inner wall at pitch circle Ø122.8 mm; six N42-grade neodymium magnets, 3×6×3 mm, on a stationary carrier facing the poles across ~0.8 mm radially; passive detent target 60–150 mNm peak; total height 34 mm; centre occupied by the Ø115 mm display, so annular or rim solutions only; 5 V USB power, ≤15 W; knob on three V-groove wheels; motor cogging must be near zero or locked to the sixty poles in count and phase.

---

## 0. Findings summary

1. **The primary idea — coils wound around the six detent magnets — is not a motor. It is a detent-strength modulator.** By construction it is a single-phase machine whose coils must drive flux through the magnets themselves; the working below shows ±3 % continuous and ±10–20 % transient modulation of detent torque, i.e. ±2–5 mNm continuous on a 100 mNm detent. It cannot produce directional torque on demand, half-steps, or end-stop walls. Its two virtues are real: it is perfectly phase-locked to the sixty detents, and unpowered it does nothing at all.
2. **A variable-reluctance phase added at half-pitch offset fixes the topology but not the physics.** With the available coil window and a 0.8 mm gap it delivers roughly 1–2 mNm continuous and ~30 mNm in pulses of a few seconds. Good for event haptics and brief end-stop bumps; useless for sustained resistance ramps. Reluctance torque scales with flux density squared, and flux density scales with ampere-turns over gap — real steppers get their torque from ~0.05 mm gaps, not 0.8 mm.
3. **An ironless axial-flux ring stator (option a) is the only topology found that reaches the 30–100 mNm band within 5 V / 15 W, keeps zero cogging by construction, and leaves the unpowered feel essentially untouched.** First-order estimate: torque constant ~130 mNm/A, ~65 mNm at ~5 W. It needs its own magnet ring added to the knob's underside and ~5–6 mm of vertical space.
4. **Rim drive (option b) is worse than its original rejection.** The 13.5:1 friction ratio reflects the drive motor's cogging into the knob multiplied by the ratio, at a spatial frequency incommensurate with sixty — the beat the constraint forbids — and the always-engaged wheel drags the unpowered feel. The rejection holds and strengthens.
5. **Direct-drive catalogue hollow motors (option c) are dead by geometry.** The largest common catalogue bore found is 30 mm (CubeMars GL100, itself 34.2 mm tall — taller than the whole object). This confirms the prior sourcing finding (no bore over 84 mm at Ø135 outside diameter) rather than contradicting it.
6. **Tangential voice coils (option d) degenerate into option a for continuous rotation.** As true limited-angle devices they belong to the event-haptics actuator layer, not the motor layer.

No settled constraint was found to be physically impossible. One settled *expectation* is quantitatively unfounded — see section 6.

---

## 1. Primary idea: coils around the six detent magnets

### 1.1 What the topology actually is

Six stator poles at 60° spacing; sixty rotor teeth at 6° pitch. Since 60° is exactly ten tooth pitches, **all six magnets align with rotor teeth simultaneously** — necessarily, because that is what makes all six magnets add up into one strong 60-per-revolution detent. The consequence: every coil sees the same electrical phase. This is a **single-phase machine**, not a hybrid stepper. A hybrid stepper gets bidirectional controlled torque from stator pole groups offset by fractions of a tooth pitch; here there is no offset anywhere.

A second structural problem: the coil's flux must pass through the magnet it is wound around. Sintered neodymium has a recoil permeability of ~1.05 — magnetically it is air. So the coil works into an effective gap of at least 3.8 mm (3 mm magnet + 0.8 mm working gap), while the magnet's own magnetomotive force dominates the circuit. This is exactly the layout real hybrid steppers avoid: they place the permanent magnet in a shared axial path and let the coils act on toothed soft-iron poles across a tiny gap ([hybrid stepper detent vs holding torque](https://www.motioncontroltips.com/faq-whats-the-difference-between-detent-torque-and-holding-torque/) — detent torque is typically 5–20 % of holding torque precisely because the coils, properly placed, command 5–20× the magnet's unpowered effect; here the ratio inverts).

### 1.2 Ampere-turns achievable in the window (working)

Coil window: 3.5 mm radial × 5 mm axial = 17.5 mm² per pole.

- Wire: AWG 32 (0.20 mm bare, ~0.24 mm insulated, 0.032 mm² copper area).
- Turns: (3.5/0.24) × (5/0.24) ≈ 14 × 20 ≈ **~240 turns** (geometric; ~0.85 practical fill already included in the rounding — estimate, unverified until a coil is wound).
- Mean turn length around a 3×6 mm magnet plus buildup: ~30 mm → wire length ≈ 7.2 m → resistance ≈ **3.9 Ω per coil** (ρ_Cu = 1.72×10⁻⁸ Ω·m).
- Continuous current at a conservative 5–6 A/mm² for a potted fine-wire coil: 0.16–0.19 A → **~40–50 ampere-turns continuous** per pole (~0.15 W per coil, trivial heat).
- Pulse: one coil directly across 5 V draws 1.28 A → **~307 ampere-turns**, 6.4 W, ~40 A/mm². Copper self-heats at roughly 6–7 °C/s at that density, so pulses of a few seconds are fine. Driving six coils as three parallel pairs at 5 V gives ~154 ampere-turns each at ~10 W total.

### 1.3 Torque achievable (working)

The magnet's magnetomotive force: N42 coercivity ≈ 950 kA/m × 3 mm thickness ≈ **2,900 ampere-turns**. The coil and magnet drive the same magnetic circuit, so fractional flux change = coil ampere-turns / magnet ampere-turns, and force goes with flux squared (fractional force change ≈ 2× the flux change):

| Drive | Ampere-turns/pole | Detent-torque modulation | On a 100 mNm detent |
|---|---|---|---|
| Continuous (all six, ~1 W) | ~46 | ±3 % | ±3 mNm |
| Pulse, all six (~10 W, seconds) | ~154 | ±11 % | ±11 mNm |
| Pulse, two coils (~13 W, seconds) | ~307 | ±21 % on 2 of 6 poles | ~±7 mNm net |

**Against the 30–100 mNm dynamic target: a miss by an order of magnitude in continuous operation.** And the modulation is not directional torque. Attraction of a steel pole is polarity-independent — reversing coil current cannot move the equilibrium positions, only scale the torque profile whose zero crossings stay fixed at the sixty aligned positions. Therefore, by construction: **no half-steps, no end-stop wall, no free-spin flywheel feel.** What it *can* do, with the position encoder the design already needs: strengthen the detent while the user climbs out of it and weaken it as they fall into the next — an asymmetric ratchet whose average resistance is a few mNm continuous, tens of mNm in bursts. That is "heavier clicks", genuinely useful for per-context feel, and nothing more.

### 1.4 Cogging and phase lock

Perfect on both counts, trivially: the powered machine's equilibria *are* the sixty detent positions, because it is the same magnetic circuit. Sixty positions, zero phase error, guaranteed by construction, forever. And unpowered, dead coils change nothing — the passive watch-bezel click is untouched. This is the honest appeal of the idea, and why it survives as a *layer* even though it fails as *the motor*.

### 1.5 Drive electronics

Six half-bridge or three full-bridge channels; a dual DRV8833-class brushed driver or one three-phase driver misused as three half-bridges suffices (single-phase, bidirectional current, PWM amplitude control keyed to encoder position). No field-oriented control needed. Estimate £2–4 in parts (estimate, unverified).

### 1.6 The two-phase fix: offset variable-reluctance poles

Add six plain soft-iron wound poles (no magnets) at a 3° offset — half a tooth pitch — from the magnet alignment grid. Now there are two phases sharing the sixty-tooth rotor: the machine becomes controllable like a stepper, half-step equilibria appear, and the extra poles contribute **zero unpowered force** (no magnet, no flux). Cogging stays locked to sixty by construction.

But the torque physics at a 0.8 mm gap is unforgiving. Flux from the coil alone: B = μ₀·NI/g. With a U-yoke pole (two 3×5 mm faces, ~1.6 mm total series gap):

- Continuous (~46 A-t): B ≈ 0.036 T → normal force ≈ 0.02 N/pole → tangential ≈ 25 % of normal (tooth-geometry factor, estimate) → **~1–2 mNm total for six poles**.
- Pulse (307 A-t, one coil at 5 V): B ≈ 0.24 T → ~0.7 N normal, ~0.18 N tangential per pole → ~11 mNm/pole; three poles pulsed at ~15 W → **~30 mNm for a few seconds**.

To hold 30 mNm *continuously* this way needs ~500 ampere-turns per pole → ~65 A/mm² — more than 10× the thermal limit of the window. Closing the gap to 0.3 mm (torque ∝ 1/gap²) still leaves continuous torque near 10–20 mNm with a crowded carrier. General variable-reluctance references confirm the scaling: torque comes from air-gap permeance change and collapses with gap ([reluctance torque overview, ScienceDirect](https://www.sciencedirect.com/topics/engineering/reluctance-torque); [axial air-gap variable-reluctance motor tests, Electric Machines & Power Systems](https://www.tandfonline.com/doi/abs/10.1080/03616968108960076)).

**Verdict on the primary idea and its fix:** keep the six coils (or a subset) as a cheap, perfectly-locked *detent modulation layer* if the carrier design can afford the winding; do not ask it to be the motor. The offset-pole variant buys event haptics the actuator layer already owns (per the premium bill-of-materials layering: magnets own the fixed scale, motor owns dynamics, actuator owns event haptics) and is probably not worth its complexity.

---

## 2. Alternatives

### 2a. Custom ironless axial-flux ring stator under the knob

Topology: a ring of alternating-polarity magnets (e.g. ~40 poles of ~5×2.5×2 mm N42 blocks, or a printed multipole ring) set into the knob's underside with a thin steel back-iron ring behind them (back iron rotates with the magnets, so it costs nothing unpowered); beneath it, a stationary **ironless** three-phase winding — either a multilayer printed-circuit-board stator or a potted wound-coil ring — at mean radius ~62 mm. The main board's 85.5×65 mm footprint has a diagonal of ~107.4 mm, so everything beyond Ø108 is clear of it: a stator annulus spanning roughly Ø118–135 fits beside the board, not under the display. This is a Lorentz-force (voice-coil-principle) machine: torque linear in current, **zero cogging because there is no iron in the stator** — it physically cannot beat against the sixty detents.

First-order torque estimate (marked estimate, unverified until wound): 6-layer 2 oz printed stator, radial spokes at ~0.7 mm pitch at r = 62 mm → ~3,300 conductors, ~1,400 torque-effective after phase and winding factors; air-gap flux density ~0.25 T from a single-sided array with back iron at ~1–1.5 mm gap (estimate; multilayer printed stators of this class are established — a recent 19 mm, 48-layer example achieves 45 % copper fill, [High Torque Density PCB Axial Flux Permanent Magnet Motor, arXiv 2509.23561](https://arxiv.org/abs/2509.23561); topology comparison in [IET Electric Power Applications](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-epa.2020.0622)); active radial length 6 mm. Torque constant K_t ≈ 1,400 × 0.25 T × 6 mm × 62 mm ≈ **130 mNm/A**. Phase resistance ~9 Ω → **~65 mNm at ~0.5 A / ~5 W; ~110 mNm approaching the 15 W ceiling** (transient; continuous limit set by board heating, realistically 30–60 mNm sustained with the base as heatsink — estimate, unverified). **This is the only option that lands in the 30–100 mNm band at 5 V.**

Unpowered feel: no iron → no cogging, no magnetic drag. The one real risk is **eddy-current drag** from magnets sweeping the stator copper — velocity-proportional, so it feels viscous, never gritty, and it cannot beat with the detents. Mitigation by design: no copper pours or planes under the magnet track, narrow radial spokes only (eddy loops are then confined to trace width and suppressed quadratically). Must be measured, not assumed. Second risk: the new magnet ring interacting with the six detent magnets and sixty steel poles — separated radially/axially but needs a finite-element or bench check.

Height consumed: magnets ~2 mm + gap ~1 mm + board 1.6 mm + clearance ≈ **5–6 mm** under the knob rim, in the base — needs a CAD check against the V-wheel and carrier stack, ask for the CAD path before committing geometry.

Drive: standard three-phase field-oriented control (FOC) driver — e.g. TMC6300 (2–11 V) or DRV8311 class, ~£2–3 (estimate, unverified) — plus the high-resolution ring encoder the design already requires.

Cost per unit at quantity 60: printed stator £10–25, magnet ring £5–15, driver £2–3, back iron £1–3 — **~£20–45 (all estimates, unverified; board quote required)**.

Complexity/risk: medium. It is a custom machine, but a *planar, tolerance-friendly* one — the printed stator is a commodity board order, and the magnet ring is glued into a machined pocket. Torque estimate is first-order only.

### 2b. Small brushless motor driving the rim through a friction wheel

Torque arithmetic is seductive: a Ø10 mm wheel on the Ø135 rim gives 13.5:1, so 100 mNm at the knob needs only ~7.4 mNm at the motor — comfortably inside a £10–20 2804-class gimbal motor. That is why it keeps coming back.

It stays rejected, for a stronger reason than the original slip/backlash finding. **The ratio works in reverse on cogging.** The drive motor's unpowered cogging (a few mNm for a cheap gimbal motor) is reflected to the knob multiplied by 13.5, as lumps at (motor cogging count × 13.5) events per knob revolution — hundreds per revolution, incommensurate with sixty. That is precisely the beat the settled constraint forbids, present *whenever the wheel touches the rim, powered or not*, plus always-engaged friction drag on the near-zero-friction V-wheel ride. The SmartKnob community documents exactly this failure mode at 1:1 — cheap gimbal motor cogging visibly corrupts weak virtual detents ([SmartKnob wiki, Motor Status](https://github.com/scottbez1/smartknob/wiki/Motor-Status)); a ratio makes it 13.5× worse. Salvageable only with an actuated engage/disengage clutch: added mechanism, audible clunk, wear marks on a cosmetic rim. Rejection holds and strengthens. Cost would have been ~£15–30 (estimate); irrelevant.

### 2c. Direct-drive hollow/ring catalogue motors

The requirement is a bore clearing the Ø115 display within Ø135 outside diameter and a few-mm height slice. What is actually purchasable:

- **CubeMars GL100 KV10** — the largest-bore common catalogue gimbal motor found: bore 30 mm, outside diameter 106.8 mm, height **34.2 mm** (taller than the entire object), 3 N·m rated, 24 V, 698 g, **$272.99** ([CubeMars listing](https://www.cubemars.com/product/gl100-kv10-gimbal-motor.html)).
- Typical hollow-shaft gimbal motors (T-Motor GB4106, GB54-1, EMAX GB4114, RCtimer GBM4114) have bores of 10–20 mm ([overview via GetFPV and vendor listings](https://www.getfpv.com/tiger-gb4106-brushless-gimbal-motor-hollow-shaft.html)).
- Frameless torque-motor kits (e.g. [Kollmorgen TBM2G series, seven frame sizes](https://www.kollmorgen.com/en-us/products/motors/direct-drive/tbm2g-series-frameless)) go larger, but no frame offers a >Ø115 bore inside Ø135 — consistent with the prior sourcing finding of an 84 mm maximum bore at this outside diameter. Price: quote required.

**Dead by geometry.** Even ignoring the bore, height alone disqualifies everything found. This option's real value is negative confirmation: the ring machine must be custom, exactly as decision-level sourcing already concluded. Note SmartKnob itself ([scottbez1/smartknob](https://github.com/scottbez1/smartknob)) is the display-in-centre prior art — but its display is 39.5 mm and rides *through* a hollow-shaft brushless motor under it; that topology does not scale to a Ø115 display disc with a board on its back.

### 2d. Voice-coil / moving-coil tangential actuators on the ring

Rotary voice coils ("arc segment actuators", "limited-angle torque motors") are cog-free and torque-linear ([how rotary voice coil actuators work, Motion Control Tips](https://www.motioncontroltips.com/how-do-rotary-voice-coil-actuators-work/); [H2W Technologies rotary voice coils](https://www.h2wtech.com/category/rotary-voicecoil-actuators) — e.g. 1.29 N·m continuous units exist, but at sizes and power far beyond this envelope; price: quote required). Two ways to apply them here:

1. **Continuous rotation with stationary coils and rotor magnets** — this *is* option 2a: an ironless ring motor is exactly a circle of commutated voice coils. Not a distinct option.
2. **True limited-angle actuation** — a small arc actuator shaking or biasing the magnet carrier ring (which is already on a lifting mechanism) to render clicks and bumps. Legitimate, but that is the event-haptics actuator layer's job in the settled three-layer model, not the motor layer's. It cannot do sustained ramps or end-stops on a continuously rotating knob.

---

## 3. Comparison table

All torques at 5 V within ≤15 W. "Unpowered feel" is the pass/fail column.

| Option | Continuous torque | Transient torque | Cogging character | Height used | Unit cost (est.) | Risk | Unpowered feel |
|---|---|---|---|---|---|---|---|
| 1. Coils on the six magnets | ±3 mNm modulation only, no directional torque | ±10–30 mNm modulation, seconds | Locked to 60, by construction | ~0 (inside carrier) | £5–10 (estimate) | Low | **Perfect** — dead coils = pure passive detent |
| 1.6 + offset VR poles | ~1–2 mNm | ~30 mNm, seconds | Locked to 60 | ~0 | £10–20 (estimate) | Medium | Perfect (unmagnetized poles inert) |
| 2a. Ironless axial-flux ring | ~30–60 mNm (est.) | ~100+ mNm (est.) | **Zero** (no stator iron) | 5–6 mm | £20–45 (estimate, quote required for boards) | Medium | Near-perfect; eddy drag = smooth viscous, must measure |
| 2b. Friction rim drive | 100+ mNm easily | ditto | Motor cogging ×13.5, incommensurate with 60 — **beats** | ~0 vertical, radial pocket | £15–30 (estimate) | Medium | **Fails** — reflected cogging + drag whenever engaged |
| 2c. Catalogue hollow motor | n/a | n/a | n/a | ≥34 mm found | $272.99 for the largest bore found (30 mm) | n/a | n/a — no purchasable geometry fits |
| 2d. Limited-angle voice coil | n/a for rotation | event pulses | Zero | small | quote required | Low | Perfect, but wrong layer |

---

## 4. What each does to the unpowered watch-bezel click

- **Coils on magnets / offset poles:** nothing. The strongest property of the primary idea.
- **Axial-flux ring:** no added lumpiness of any spatial frequency (no stator iron → no preferred positions). Adds rotor magnet mass (slightly more inertia — arguably nicer) and a small velocity-proportional eddy drag through the stator copper; drag is smooth and cannot beat, but if measurable at hand speeds it dilutes the "free ring between clicks" feel — hence the bench test below, and the no-copper-under-track layout rule.
- **Rim drive:** permanent gritty beat plus friction drag. Disqualifying.

---

## 5. Recommendation

**Build option 2a, the custom ironless axial-flux ring stator (printed-circuit-board stator first, wound-coil fallback), as the motor layer.** It is the only evaluated topology that reaches the 30–100 mNm dynamic band within 5 V / 15 W, and it is the only *powered* topology whose cogging is zero by construction rather than by locking discipline. Treat the primary idea's six coils as an optional, separate *detent-strength modulation layer* — decide after the carrier is designed whether the winding space is free; it is cheap and perfectly locked, but it is not the motor and must not be sized as one.

**First bench test:** a static-and-drag rig before any full motor build.

1. Glue the candidate magnet ring into a dummy knob ring on the existing V-wheel ride; spin it by hand over (i) a blank FR-4 disc and (ii) a dummy 6-layer stator board with the real copper layout, measuring coast-down / drag torque at 0.5–2 rev/s. **Go/no-go: eddy drag at hand speed must be imperceptible against the passive detent (indicatively <2–3 mNm — threshold to be set against strand A's detent measurements; estimate, unverified).**
2. Same rig, stator energized DC through two phases: measure static torque vs current → verify the ~130 mNm/A torque-constant estimate within a factor of ~2, and confirm no positional preference (no cogging) with power off.

**Confidence: medium (~65 %)** that option 2a reaches ≥30 mNm continuous in the real stack. The torque model is first-order (flux density and winding factor are the soft numbers); eddy drag and interaction with the detent magnet ring are unmeasured. Confidence that the *ranking* is right — ring Lorentz machine over reluctance, rim, or catalogue options — is high (~90 %): the reluctance shortfall and the geometry exclusions are arithmetic, not judgment.

---

## 6. Settled-constraint check

Nothing settled is physically impossible. One quantified correction to expectations:

- **If any settled text assumes the coils-around-the-six-magnets machine can itself deliver 30–100 mNm of continuous dynamic torque, that assumption is wrong by roughly an order of magnitude.** The binding facts: the coil window caps continuous excitation at ~40–50 ampere-turns per pole (thermal), the magnet it must push through is ~2,900 ampere-turns and magnetically air, and steel-pole attraction is polarity-independent so equilibria cannot be moved. Working in section 1. The constraint that cogging be zero or locked to sixty is sound and is exactly what the recommended ironless topology satisfies.

---

## Sources

- [SmartKnob — haptic knob with software-defined detents (scottbez1, GitHub)](https://github.com/scottbez1/smartknob)
- [SmartKnob wiki — Motor Status (cogging of cheap gimbal motors vs virtual detents)](https://github.com/scottbez1/smartknob/wiki/Motor-Status)
- [Hackaday — An In-Depth Look At The Haptic Smart Knob](https://hackaday.com/2022/06/24/an-in-depth-look-at-the-haptic-smart-knob/)
- [Detent torque vs holding torque (Motion Control Tips)](https://www.motioncontroltips.com/faq-whats-the-difference-between-detent-torque-and-holding-torque/)
- [Reluctance torque overview (ScienceDirect Topics)](https://www.sciencedirect.com/topics/engineering/reluctance-torque)
- [Tests of an axial air-gap variable reluctance motor (Electric Machines & Power Systems)](https://www.tandfonline.com/doi/abs/10.1080/03616968108960076)
- [High Torque Density PCB Axial Flux Permanent Magnet Motor for Micro Robots (arXiv 2509.23561)](https://arxiv.org/abs/2509.23561)
- [Comparison of PCB winding topologies for axial-flux machines (IET Electric Power Applications)](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-epa.2020.0622)
- [CubeMars GL100 KV10 gimbal motor listing](https://www.cubemars.com/product/gl100-kv10-gimbal-motor.html)
- [Tiger GB4106 hollow-shaft gimbal motor (GetFPV)](https://www.getfpv.com/tiger-gb4106-brushless-gimbal-motor-hollow-shaft.html)
- [Kollmorgen TBM2G frameless torque motors](https://www.kollmorgen.com/en-us/products/motors/direct-drive/tbm2g-series-frameless)
- [How rotary voice coil actuators work (Motion Control Tips)](https://www.motioncontroltips.com/how-do-rotary-voice-coil-actuators-work/)
- [H2W Technologies rotary voice coil actuators](https://www.h2wtech.com/category/rotary-voicecoil-actuators)
- [Alps Alpine haptic cockpit components, CES 2026 (heise online)](https://www.heise.de/en/news/Alps-Alpine-Vehicle-cockpit-with-haptic-feedback-11132159.html)
