# Answer — the detent mechanism of the 60

Response to the R&D brief `docs/Research/1-detent-haptics-RD.md`. This is the single
synthesis document the brief asks for. Full working, sources and instrument listings
live in the five strand documents in this folder, referenced throughout:

- `A-state-of-the-art.md` — survey of rotary haptic input devices
- `B-magnetic-detent-physics.md` — the magnetic detent modelled (runnable model:
  `calc_detent_torque.py`, magpylib)
- `C-motor-options.md` — the motor layer evaluated
- `D-control-sync.md` — control and synchronisation
- `E-bench-rig.md` — the bench rig, instruments and pass/fail numbers

Every number below has units; its working is in the named strand. Model torques carry
strand B's error band of roughly −40 %/+65 % — the bench rig, not this document, is
the arbiter of absolutes. Relative comparisons (ratios, scalings, fade curves) are much
tighter because the model errors cancel.

---

## Verdict in one paragraph

The passive magnetic detent works as designed and needs only detail changes (pole
steel, magnet orientation, a pinned gap tolerance). The layered architecture — magnets
for the fixed scale, motor for dynamics, vibration actuator for events — is validated
by the survey: it is the corrected version of two documented commercial failures, and
no surveyed device does all three. But one piece of design intent fails by arithmetic:
the coils-around-the-six-magnets machine is not a motor and never will be — it is a
detent-strength modulator. The motor layer should instead be a custom ironless
axial-flux ring stator (printed-circuit-board stator) under the knob, which is the
only evaluated topology that reaches useful torque at 5 V with zero cogging by
construction. Separately, the 3 mm carrier drop only halves the detent rather than
switching it off, which collides with the half-step feature unless the travel grows to
about 4.5 mm. Both flags are detailed in the "already decided under stress" section.

---

## Findings

### 1. The detent as drawn lands at ~74 mNm — in the target band, but its lower third

Central estimate 74 mNm peak (band 45–120 mNm), from six N42 magnets each pulling
~0.7 N radially on an aligned Ø2.5 mm pole across 0.8 mm, peak tangential force
0.20 N per magnet at quarter-pitch, times six magnets (all in phase, since 60/6 is an
integer) at radius 61.4 mm. The profile is a clean sinusoid — a smooth watch-bezel
click, not a snap; the energy barrier is ~2.5 mJ per step. (Strand B §2–4.)

The single most useful physical fact: **flux capture is pole-limited, not
magnet-limited.** The Ø2.5 mm pole face covers only 27 % of the magnet face, so
bigger magnets buy nothing (every size tried inside the carrier annulus lands within
±5 % of baseline), while a fatter pole and a smaller gap buy a lot. (Strand B §6.)

The top of the band is reachable without architecture change: N52 grade (+24 %,
remanence-squared scaling), Ø3 mm poles (+27 %, area scaling), gap tightened
0.8 → 0.6 mm → **~158 mNm combined**. Torque scales as gap^−1.5, so the gap is both
the strongest tuning lever and the tightest tolerance: ±0.1 mm of runout is ±15–20 %
torque ripple. (Strand B §5–7.)

Whether the top of the band is *wanted* is a feel question the survey softens: the
only published detent torque in the entire device landscape is the Alps EC11 encoder
class at 12±5 mNm on a ~6 mm shaft ([Alps datasheet](https://www.mouser.com/datasheet/2/15/EC11-1370808.pdf)),
and at the 60's ~10× lever arm the baseline ~74 mNm already lands near a firm encoder
click in fingertip terms (arithmetic, not a source — strand A, pattern 4). Build
shimmable, decide by hand.

### 2. The survey validates the three-layer architecture — and says consistency beats strength

Rotary devices split into passive energy wells (aperture rings, watch bezels,
detented encoders), motor-simulated torque (SmartKnob, BMW iDrive generation 1), and
vibration substitutes (Surface Dial, Apple Digital Crown). Motor-only detents failed
commercially — BMW shipped force-feedback detents in 2001 and retreated to fixed
mechanical ones ([BimmerFest](https://www.bimmerfest.com/threads/idrive-changes-haptic-feedback-gone.204398/));
SmartKnob's detents die unpowered and its motor cogs parasitically when off
([SmartKnob README](https://github.com/scottbez1/smartknob/blob/master/README.md?plain=1)).
No surveyed device layers all three feels. (Strand A, patterns 1–2.)

The sharpest commercial lesson: **the worst reviews in the survey are all variance
findings** — dials differing on one unit (Stream Deck+), encoders varying in tightness
(Push 2), clicks changing with wear (Fuji) — while the premium benchmark, the Rolex
bezel, is judged on sub-0.3 mm rim back-play. Detent-to-detent uniformity and rim
backlash are the measurable quality targets, and a non-contact magnetic detent's
freedom from wear is an advantage nothing ball-and-spring in the survey has.
(Strand A, pattern 3.) Passive magnet-pole detent prior art dates to
[US3934216A (1976)](https://patents.google.com/patent/US3934216A/en) — the base
mechanism is long public. Sixty clicks per revolution is proven watch-bezel territory
on the "chunky, tactile" side, with ~7 mm of rim travel per click at Ø135. Audio is
part of the detent illusion (Apple's crown patent
[US11016587B2](https://patents.google.com/patent/US11016587) synchronises click sounds
deliberately); the acoustic signature of the magnet-pole engagement deserves tuning on
the rig, not accident. (Strand A, patterns 5, 8.)

### 3. The coils-around-the-magnets machine is a modulator, not a motor — by arithmetic

Three independent facts kill it as the motor (strand C §1, full working there):

1. **Single-phase by construction.** All six magnets align with poles simultaneously
   (that is exactly what makes the detent strong), so every coil sees the same
   electrical phase. A hybrid stepper needs pole groups offset by fractions of a tooth
   pitch; there is no offset anywhere.
2. **The coil fights its own magnet.** Coil flux must pass through the neodymium block
   (magnetically air, ~2,900 ampere-turns of its own), while the 3.5 × 5 mm window
   thermally sustains ~40–50 ampere-turns (~240 turns of AWG 32 at ~0.19 A). Result:
   ±3 % continuous modulation of detent strength, ±10–20 % in multi-second pulses.
3. **Equilibria cannot move.** Steel-pole attraction is polarity-independent, so
   reversing current only scales the torque profile — zero crossings stay at the sixty
   aligned positions. No half-steps, no end-stop walls, ever.

Against the 30–100 mNm dynamic band: an order-of-magnitude miss continuously. What
survives is real and cheap: a perfectly phase-locked, zero-unpowered-penalty
**detent-strength modulation layer** ("heavier clicks" per context), worth keeping only
if the carrier design gets the winding space for free. The offset variable-reluctance
fix (six plain iron poles at half-pitch) repairs the topology but not the physics at a
0.8 mm gap: ~1–2 mNm continuous, ~30 mNm in pulses.

### 4. The motor that works: an ironless axial-flux ring stator under the knob

A ring of alternating-polarity magnets set into the knob's underside (back iron
rotating with them), over a stationary ironless 6-layer printed-circuit-board
three-phase stator in the annulus Ø118–135 — clear of the main board's 107.4 mm
diagonal. First-order estimate: torque constant ~130 mNm/A, **~65 mNm at ~5 W,
~110 mNm approaching 15 W** (transient; sustained realistically 30–60 mNm — all
estimates, unverified until wound). It is the only evaluated topology in the
30–100 mNm band at 5 V USB. Zero cogging because there is no stator iron — it
physically cannot beat against the sixty detents, which also dissolves strand D's
warning about motor ripple at a foreign spatial period. The one unpowered-feel risk is
eddy-current drag from magnets sweeping stator copper: velocity-proportional, felt as
viscous never gritty, suppressed by keeping copper as narrow radial spokes only under
the magnet track — and measured before anything else (see the rig gates). Height:
~5–6 mm under the knob rim — **needs a check against the CAD stack** (the parametric
model is outside this repo; ask for the path). Cost ~£20–45/unit at sixty units
(estimates; board quote required). (Strand C §2a, comparison table §3.)

Rim friction drive stays rejected, harder than before: a Ø10 mm wheel's 13.5:1 ratio
reflects the drive motor's cogging into the knob ×13.5 at a spatial frequency
incommensurate with sixty — precisely the forbidden beat — whenever the wheel touches,
powered or not. Catalogue hollow motors are dead by geometry (largest bore found:
30 mm, on a motor taller than the whole product). (Strand C §2b–2c.)

### 5. Control: the motor renders desired-minus-passive, and is silent by default

The passive magnet field is, to the controller, known cogging: capture torque-vs-angle
once on the rig (the Swindells/MacLean "haptic camera" pattern), store it as a lookup
table, and drive the motor with the *difference* between desired and passive torque.
In magnet-defined contexts the motor idles at exactly zero across the well floor — no
power, no hunt, no noise; the passive well holds position. All rendered features are
defined in angle, never time (torque perception keys on spatial profile — Tan et al.,
IEEE Transactions on Haptics 2008), phase-locked to the magnet frame through a
per-well 60-entry calibration table that also absorbs encoder eccentricity. A phase
error does not make two detents; it makes one mushy detent that disagrees with the
screen. (Strand D §1, recommendations 1–2.)

Numbers the mechanism demands (strand D §2–3): position sensing **12-bit/rev minimum,
14-bit-equivalent target (≥16,384 counts/rev, ≤0.022°)**, judged on velocity-estimate
noise rather than absolute accuracy — SmartKnob's move to the 14-bit MT6701 was for
loop stability, not display. Torque loop **≥1 kHz, ≤1 ms encoder-to-torque, headroom
to 5 kHz** (a 20 rev/s flick crosses a 6° detent in 0.8 ms). Vibration events
**≤10 ms trigger-to-vibration, 30 ms hard ceiling, jitter the enemy** (Kaaresoja).
Parasitic torque ripple budget **≤1 % of local peak** (human detection floor 1–3 %,
spatial-frequency thresholds down to 0.37 %). End-stops: passivity-bounded spring plus
in-wall damping plus a vibration transient at contact — never stiffness alone; the
near-frictionless V-wheels make the stability envelope unusually tight (Colgate &
Brown), and parking the magnet carrier *up* behind a wall lends the wall real physical
ratcheting. (Strand D §4, recommendations 3–6, 9–10.)

The inner-wall optical encoder constraint is favourable for resolution (a 20 µm scale
at Ø110 is ~17,300 lines/rev raw) but demands two things: a sub-divisional
(interpolation) error spec from the readhead vendor, evaluated as velocity noise at
the loop rate, and an index or absolute reference so the encoder frame binds to the
magnet frame at power-up without a felt homing wiggle. (Strand D §5.)

### 6. The three flags physics raises against the drawings

1. **The 3 mm carrier drop is a 2:1 attenuator, not an off-switch.** Residual detent
   at 3 mm drop: 52 %. The fade is slow at first because the magnet is 6 mm tall — the
   pole stays inside the magnet's axial extent for the first ~1.5 mm of travel.
   Getting below ~11 % residual needs ~4.5 mm of travel; below 2 % needs ~6 mm.
   (Strand B §8.) The collision this causes with half-steps is in the next section.
2. **Magnet orientation is unpinned and worth a factor of 4.4.** "3 × 6 × 3 mm facing
   outward" allows mounting the 6 mm edge tangentially, which collapses peak torque
   from 74 to 17 mNm. The 6 mm axis must be vertical, magnetisation radial-outward,
   all six the same polarity — one line on the drawing. (Strand B §11.)
3. **"Plain steel grub screws" will arrive wrong.** Standard ISO 4029 / DIN 916 set
   screws are hardness class 45H — hardened steel with ~10× the coercivity of mild
   steel, adding ~11 mNm of always-on hysteresis grit (15 % of the detent, dissipative,
   uncancellable by the motor). A2/A4 stainless is austenitic — essentially
   non-magnetic, detent gone. Cup-point tips hollow out the working face. The part is
   a turned free-cutting mild-steel (EN1A / 230M07) flat-point M3 stud, 3,600 pieces,
   quote required. (Strand B §9–10.)

### 7. The cross-strand collision: detent strength × carrier travel × motor headroom

These three numbers must be chosen together, and as currently drawn they conflict:

- Half-steps require the motor to overpower the *residual* passive field (the midpoint
  between wells is an unstable equilibrium — strand D §1.3).
- At 3 mm drop the residual is 52 % of peak: **39 mNm** on the ~74 mNm baseline,
  **~78 mNm** on a 150 mNm top-of-band build.
- The recommended motor sustains an estimated 30–60 mNm continuous.

So on a top-of-band detent with 3 mm travel, half-steps and motor-masked smooth modes
fail; even at baseline it is marginal. The rig's gate (strand E, question 1) is
residual ≤ 30 mNm — below the weakest credible motor. Two coherent resolutions:

- **Extend carrier travel to ~4.5 mm** → residual ~11 % (8 mNm at baseline, 17 mNm at
  top-of-band) — comfortably maskable. Costs cam redesign (longer or steeper ramps;
  at gesture cadence more cam rotation is free) and must respect the 34 mm height.
- **Hold the detent near baseline (~75–90 mNm)** rather than the top of the band, and
  keep 3 mm travel — viable only if feel testing says ~75 mNm is enough, which the
  survey's lever-arm arithmetic suggests it may be.

Preferred: design the carrier for 4.5 mm now (travel is cheap on paper, impossible
after the height budget is spent) and let the rig pick the detent strength.

---

## Recommendations

Each with evidence and confidence. Numbers 1–4 change drawings; 5–8 set the plan.

1. **Motor layer = custom ironless axial-flux printed-stator ring under the knob;
   demote the six-magnet coils to an optional modulation layer.** Evidence: strand C's
   ampere-turn arithmetic (the primary idea misses by ~10× continuously and cannot
   move equilibria) and topology comparison (only option in the 30–100 mNm band at
   5 V, zero cogging by construction). Confidence: high (~90 %) on the ranking;
   medium (~65 %) that the stator reaches ≥30 mNm continuous in the real stack —
   which is why its bench test is first.
2. **Pole: turned EN1A free-cutting mild-steel flat-point M3 stud — explicitly not a
   standard hardened grub screw, not stainless, not cup-point.** Evidence: strand B §9
   hysteresis working (45H ≈ 11 mNm grit vs ≤2 mNm soft); Ø3 mm buys +27 % torque.
   Confidence: high on the material exclusions; medium-high on M3 over M2.5 (couples
   to the strength decision).
3. **Magnet: N52, 3 mm radial × 3 mm tangential × 6 mm axial, 6 mm axis vertical,
   magnetisation radial-outward, same polarity ×6, orientation pinned on the drawing.**
   Evidence: strand B §6 (grade is the only magnet lever that works; size is a dead
   end — the pole face is the bottleneck) and §11 (4.4× orientation swing).
   Confidence: high on orientation and "size is dead"; medium on N52 over N42 (only
   needed if feel testing wants the top of the band). Not UK stock — quote required,
   same as the existing magnet line in `docs/SOURCING-BOM.md`.
4. **Gap: 0.8 mm nominal, carrier shimmable to 0.6 mm, combined concentricity budget
   ≤ ±0.05 mm on pole circle + carrier.** Evidence: strand B §5 — torque ∝ gap^−1.5;
   ±0.1 mm runout is ±15–20 % per-magnet torque ripple against a ≤10 % detent-spread
   quality bar (strand E question 1) and a 1–3 % human ripple-detection floor
   (strand D §6). Confidence: high on the scaling, medium on absolutes.
5. **Design the carrier for ~4.5 mm travel; let the rig set the shipped detent
   strength between ~75 and ~150 mNm.** Evidence: section 7 above. Confidence:
   high that 3 mm is insufficient *if* half-steps/smooth modes are wanted at
   top-of-band strength; the preference for more travel over less strength is
   judgment, flagged as such.
6. **Firmware architecture: passive-profile lookup table feed-forward, motor renders
   desired-minus-passive, zero torque across well floors by default, per-well 60-entry
   phase calibration, features defined in angle; ≥1 kHz torque loop;
   14-bit-equivalent sensing judged on velocity noise; vibration events ≤10 ms.**
   Evidence: strand D throughout (SmartKnob source, Colgate & Brown, Tan et al.,
   Kaaresoja). Confidence: high.
7. **Build the bench rig before any production drawing; ~£120–150 in instruments
   (~£300–360 with the Mitutoyo indicator) — estimates.** Evidence: strand E's full
   design: reaction-torque measurement on a floating stator (TAL221 500 g load cell at
   a 50 mm arm, NAU7802 analogue-to-digital converter at 320 samples/s → 160 samples
   per detent at a 12°/s sweep), coast-down drag extraction against a derived ring
   inertia of ~7×10⁻⁴ kg·m², accelerometer-on-rim vibration transmission, FFT
   separation of 3/rev wobble vs ~10/rev wheel order vs 60/rev detents, and dial-test
   runout at ≤0.05 mm total indicated. Confidence: high — it is standard metrology
   from purchasable parts.
8. **Tune the sound on the rig, not by accident.** Evidence: strand A pattern 8 —
   Apple patents the audio half of the detent illusion; encoder "zipping" is a real
   user complaint; the 60 is a desk object in a quiet room. Confidence: high that it
   matters; the tuning itself is future work.

### Rig gates, in run order (what unblocks what)

1. **Eddy-drag coast-down** over a dummy stator board — gates the motor topology
   (go/no-go: drag imperceptible against the detent, indicatively <2–3 mNm).
2. **One-magnet pull at 0.4/0.8/1.2 mm** — collapses strand B's −40 %/+65 % band with
   one load cell.
3. **Full-ring torque profile + residual vs carrier drop at 0/1/2/3(/4.5) mm** — gates
   the strength choice and recommendation 5 (pass: residual ≤30 mNm).
4. **Soft vs hardened pole back-drive drag** — validates recommendation 2 before 3,600
   pins are ordered.
5. **Static torque vs current on the energised stator** — verifies the ~130 mNm/A
   constant within ~2×; gates the motor spec.
6. **Vibration transmission base→rim** (pass ≥1.0 m/s² RMS at the rim), **wheel-order
   ripple** (≤5 mNm), **runout** (≤0.05 mm) — per strand E.

---

## Parameters to change in the CAD

All pending the named gate; V = unverified until measured, per the repo's rule that
unverified dimensions are named parameters marked V.

| Parameter | Current | Change to | Why | Gate |
|---|---|---|---|---|
| Pole thread/diameter | M2.5, Ø2.5 mm | **M3, Ø3.0 mm flat-point** | +27 % torque, same pitch clearance | rig gate 3 |
| Pole material (spec line) | "steel grub screw" | **turned EN1A / 230M07 mild steel stud** | avoids ~11 mNm hysteresis grit / non-magnetic stainless | rig gate 4 |
| Magnet grade | N42 | **N52** (V — only if top-of-band wanted) | +24 %, pennies | rig gate 3 + feel |
| Magnet orientation | unpinned | **6 mm axis vertical, radial-out, ×6 same polarity** | 4.4× torque swing | drawing note, no gate |
| Radial gap | 0.8 mm | **0.8 mm nominal, shim seats to 0.6 mm** | strongest tuning lever, T ∝ gap^−1.5 | rig gate 2 |
| Concentricity budget (pole circle + carrier) | unstated | **≤ ±0.05 mm combined** | ±0.1 mm = ±15–20 % torque ripple vs 1–3 % detection floor | rig gate 3 |
| Carrier vertical travel | 3 mm | **~4.5 mm** (V) | 3 mm leaves 52 % residual; half-steps need ≤ motor torque | rig gate 3 |
| Height reservation under knob rim | none | **5–6 mm annulus Ø118–135 for magnet ring + stator board** (V) | the motor layer | rig gates 1, 5 + CAD stack check |
| Stator copper rule | n/a | **no pours/planes under the magnet track; radial spokes only** | eddy drag suppression | rig gate 1 |
| Encoder scale | "optical, inner wall" | **add index/absolute reference; require sub-divisional-error spec** | power-up frame binding; velocity noise at 1 kHz | firmware bring-up |

The parametric CAD lives outside this repo; these are requested changes, not applied
ones.

---

## Already decided, under stress

Flagged separately as the brief requires — with evidence, not silently designed
around. Nothing settled is physically impossible; two items carry wrong quantitative
expectations and two are under-specified.

1. **Decided item 5 in the brief — "the six magnets and sixty poles *are* the motor's
   magnetic circuit" — is wrong as a motor and right as a lock.** The machine is
   single-phase by construction, its coils are outmatched ~60:1 in ampere-turns by the
   magnets they wrap, and polarity-independent pole attraction pins every equilibrium
   to the sixty detent positions. It can modulate detent strength ±3 % continuously
   (±10–20 % pulsed) and nothing else. The *requirement* behind the decision — cogging
   near zero or locked to sixty in count and phase — stands and is satisfied better by
   the ironless axial-flux stator, whose cogging is zero because it has no iron.
   Evidence: strand C §1, arithmetic shown. This needs a ruling before the carrier is
   drawn (winding space) and before `docs/DECISIONS.md` items describing the ring
   motor are treated as build instructions.
2. **Decided item 4 — the 3 mm lifting carrier — under-delivers if "weaken" ever meant
   "remove".** 52 % residual at 3 mm; ~4.5 mm for ~11 %, ~6 mm for ~2 %. The
   cam-at-gesture-cadence architecture itself is untouched and validated (firmware
   treats carrier height as part of the haptic state machine — strand D §1.3).
   Evidence: strand B §8 fade curve. Needs a ruling on acceptable residual before the
   cam is frozen.
3. **Decided item 3 — pole and magnet spec — is under-specified in two ways that
   silently destroy the detent:** magnet orientation (worth 4.4×) and pole steel
   (hardened = grit, stainless = dead). Evidence: strand B §9–11. Two drawing lines
   fix both.
4. **Decided item 6 — "design for the top of the range" — conflicts with half-steps at
   3 mm travel** (section 7 above). Design for the top *and* extend the travel, or
   accept the baseline strength. Evidence: strands B §8, C §2a, D §1.3 combined.
5. **Decided item 7 — optical encoder on the inner wall — one real friction:** an
   incremental optical scale has no absolute reference, so binding the encoder frame
   to the magnet frame at power-up needs an index mark or a felt homing move; and
   readhead interpolation error acts as velocity noise that destabilises damping
   terms. Constraint stands; the scale choice must include an index and a
   sub-divisional-error spec. Evidence: strand D §5 (Renishaw application notes).

---

## What was not answered

- Absolute torque to better than the −40 %/+65 % model band — rig gates 2–3 close it.
- Whether the axial-flux stator's estimated torque constant survives contact with a
  real wound board (±2× uncertainty) — rig gate 5.
- Rolex/Omega bezel-mechanism patents (not found in this pass; an Espacenet assignee
  search is the follow-up if bezel prior art matters commercially).
- Anything about sound beyond "tune it deliberately" — needs the rig.
- Interaction between the new underside magnet ring and the detent circuit — needs a
  finite-element pass or a bench check (strand C §2a flags it).
