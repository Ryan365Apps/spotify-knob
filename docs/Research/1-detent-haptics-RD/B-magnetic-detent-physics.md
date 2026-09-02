# Strand B — Physics of the magnetic detent as designed

Research strand for the 60 by Cadrane. Analyses the sixty-pole / six-magnet radial detent defined in `docs/CAD-BRIEF.md` (the mechanical brief) and decision 19 in `docs/DECISIONS.md` (the decision that the fixed sixty-step scale comes from magnets and dynamic detent strength comes from the motor).

All numbers below come from `calc_detent_torque.py` in this folder (runnable: `python calc_detent_torque.py`, needs `magpylib` — installed successfully, so the numerical route was used, not the analytical fallback) unless marked otherwise. Every model figure is a **central estimate with an error band of roughly −40 % / +65 %** (basis in section 2). Nothing here replaces a bench measurement; the strand-A bench rig is the arbiter.

## Headline findings

1. **The design as drawn lands at ~74 mNm (millinewton-metres) peak detent torque** — inside the 60–150 mNm target band but at the bottom, not the top. Central estimate 74 mNm; error band roughly 45–120 mNm.
2. **The top of the band (150 mNm) is reachable without changing the architecture**: N52 magnets + Ø3 mm poles (M3 grub screws) + gap tightened to 0.6 mm gives ~158 mNm. See section 8.
3. **The 3 mm carrier drop does not switch the detent off — it only halves it** (52 % residual at 3 mm). To get below 10 % residual the carrier must drop ~4.5 mm. Flagged plainly in section 11.
4. **The magnet's 6 mm dimension must be vertical (axial).** Mounted with the 6 mm edge tangential instead, peak torque collapses 4.4× to ~17 mNm. The current spec "3 × 6 × 3 mm" does not pin the orientation. Flagged in section 11.
5. **Standard grub screws are the wrong steel.** ISO 4029 / DIN 916 set screws are hardness class 45H — hardened high-carbon steel with ~10× the coercivity of mild steel, giving ~11 mNm of hysteresis drag (felt as gritty friction) versus ~1–2 mNm for a low-carbon pole. And A2 stainless grub screws are austenitic — essentially non-magnetic — and would kill the detent entirely. Section 10.

---

## 1. Model, coordinate conventions, and sources

Coordinates: **x = radial** (outward, along the magnet's magnetisation), **y = tangential** (direction of knob rotation at the pole), **z = axial** (vertical, the knob's spin axis). Magnet dimensions are quoted **radial × tangential × axial** throughout this document. The brief's "3 × 6 × 3 mm" is taken as 3 mm radial × 3 mm tangential × 6 mm axial (the only orientation that both fits the ~3.5 mm-deep carrier annulus and works — see finding 4).

Geometry as modelled (from the brief, restated with the derivation of the pitch):

- Pole tip pitch circle Ø122.8 mm → radius r = 61.4 mm. Pitch = π × 122.8 mm / 60 = **6.43 mm** (the brief's 6.4 mm, confirmed).
- Pole: cylinder Ø2.5 mm × 4 mm long, axis radial. The 4 mm magnetic length is an **estimate, unverified** (grub screw length and wall engagement not yet fixed) — but the model is insensitive to it: 73.5 / 74.2 / 74.4 mNm at 3 / 4 / 5 mm, because the force is generated in the first ~2 mm behind the tip where the field gradient lives.
- Magnet outer face at r = 60.6 mm (= 61.4 − 0.8 gap); magnet back face at r = 57.6 mm. Consistency check: this sits inside the stated carrier annulus 57.5–61.0 mm with 0.1 mm to spare at the back. A 3.5 mm-radial magnet would reach 61.1 mm and needs the gap opened or the annulus deepened by 0.1 mm.
- Curvature neglected (pole track treated as straight): pitch/radius = 6.43/61.4 ≈ 0.10 rad per pitch, error < 1 %.

**Field model.** The permanent magnet's field is computed with magpylib v5.2.3 (analytical cuboid solution, exact for the magnet alone; Ortner & Coliado Bandeira, *Magpylib: A free Python package for magnetic field computation*, SoftwareX 11, 2020; https://magpylib.readthedocs.io).

**Pole model.** magpylib cannot compute forces on soft iron, so the pole is discretised into 0.25 mm cells, each an induced dipole with a mean-field closure using the whole-cylinder demagnetising factor:

    M_cell = min( B_applied / (μ0 · N_D),  M_sat )

with N_D = 0.25 for a cylinder of length/diameter = 1.6 magnetised axially (**estimate, unverified**; interpolated from the standard cylinder demagnetising-factor tables, Chen, Brug & Goldfarb, *Demagnetizing factors for cylinders*, IEEE Transactions on Magnetics 27(4), 1991) and μ0·M_sat = 2.0 T for low-carbon steel (**estimate**; pure iron 2.15 T, mild steel 2.0–2.1 T, Bozorth, *Ferromagnetism*). Energy is summed over cells (−½·M·B per cell in the linear regime, with a continuous saturated branch), and forces are numerical gradients of that energy. At the nominal 0.8 mm gap the pole runs mostly **unsaturated** (peak applied field ~0.33 T ≪ the ~0.5 T saturation knee of this closure), which is why the grade scaling in section 6 comes out as exactly Br² (remanence squared).

Remanence values Br per grade — K&J Magnetics grade table, https://www.kjmagnetics.com/specs.asp:
N35 → 1.21 T, N42 → 1.30 T, N52 → 1.45 T (mid-range of the published min–max).

**Error band.** Three things dominate model error: (a) the demagnetising-factor closure ignores cell–cell interaction and thread geometry — sweeping N_D over 0.15/0.25/0.35 moves the baseline peak torque over 124 / 74 / 53 mNm; (b) the knob wall material is assumed non-magnetic (aluminium) — a steel wall would add a return path and raise the force; (c) the Maxwell-stress cross-check (below) lands 30 % below the dipole sum. Stated band: **−40 % / +65 %** on any absolute torque; relative comparisons (grade ratios, gap ratios, fade curves) are much tighter because these errors largely cancel.

## 2. Q1 — force of one magnet on one pole across 0.8 mm

Three routes, shown in full:

**(a) Analytical on-axis field of the cuboid** (charge-sheet formula for the field on the axis of a block magnet, as used by the K&J Magnetics field calculator, https://www.kjmagnetics.com/calculator.asp; formula in their "Surface Fields 101" note, https://www.kjmagnetics.com/blog.asp?p=surface-fields-101):

    B(z) = (Br/π) · [ atan( a·b / (2z·√(4z² + a² + b²)) )
                    − atan( a·b / (2(z+L)·√(4(z+L)² + a² + b²)) ) ]

with a = 3 mm, b = 6 mm (face edges), L = 3 mm (magnetised length), Br = 1.30 T, z = 0.8 mm:

    term 1: atan(18 / (1.6·√47.56))  = atan(1.632) = 1.021 rad
    term 2: atan(18 / (7.6·√102.76)) = atan(0.234) = 0.230 rad
    B(0.8 mm) = (1.30/π)(1.021 − 0.230) = 0.327 T   at the face centre

The magpylib model gives the same figure at the centre and **0.298 T averaged over the Ø2.5 mm pole face** — the pole face (area π·1.25² = 4.9 mm²) covers only 27 % of the magnet face (3 × 6 = 18 mm²), but it sits in the strongest, most uniform part of the field, so the average is only 9 % below the centre value. **Flux capture is pole-limited, not magnet-limited** — the single most useful design fact in this strand (it is why bigger magnets barely help in section 6, and why a fatter pole helps a lot).

**(b) Maxwell-stress / flux-capture estimate.** The iron pole roughly doubles the local flux density by the image effect (concentration factor k = 1.8 taken, range 1.6–2.0, **estimate**); the pull is the magnetic pressure over the captured area:

    F ≈ (k·B̄)² · A / (2μ0)
      = (1.8 × 0.298 T)² × 4.91×10⁻⁶ m² / (2 × 4π×10⁻⁷ H/m)
      = 0.287 T² × 4.91×10⁻⁶ m² / 2.513×10⁻⁶ H/m = **0.56 N**

**(c) Numerical dipole-sum (the main model):** **0.81 N** radial pull per magnet at alignment.

**Answer: 0.5–1.0 N per magnet, central ~0.7 N**, model error band as above. Note the check that the pole does not saturate: applied B ≈ 0.33 T → M = B/(μ0·N_D) ≈ 1.05 MA/m, i.e. 65 % of M_sat = 1.6 MA/m. At gaps below ~0.5 mm the tip region starts to saturate and the Br²-type gains flatten.

Side-load: six magnets at 60° spacing cancel the net radial pull by symmetry. With a realistic ±0.1 mm gap asymmetry (force ∝ gap^−1.5, section 5), the residual net side-load is of order 20 % of one magnet's pull ≈ **0.1–0.2 N** — negligible against the V-wheel bearing preload.

## 3. Q2 — tangential force vs offset: the detent profile

Computed by sweeping three consecutive poles (the aligned one and both neighbours, all engaged with the same magnet as they pass) across ±half a pitch and differentiating the energy. Result, N42 3 × 3 × 6 mm, gap 0.8 mm:

| tangential offset (mm) | offset (°) | F_tangential per magnet (N) | torque, 6 magnets (mNm) |
|---:|---:|---:|---:|
| 0.0 | 0.0 | 0.000 | 0 |
| 0.4 | 0.37 | 0.076 | 28 |
| 0.8 | 0.75 | 0.141 | 52 |
| 1.2 | 1.12 | 0.185 | 68 |
| **1.6** | **1.49** | **0.201 (peak)** | **74** |
| 2.0 | 1.87 | 0.187 | 69 |
| 2.4 | 2.24 | 0.143 | 53 |
| 2.8 | 2.61 | 0.077 | 29 |
| 3.2 | 2.99 | 0.010 | 4 |

The profile is a clean, nearly pure sinusoid with period one pitch: peak at exactly quarter-pitch (1.6 mm ≈ 1.5°), zero (unstable equilibrium) at half-pitch. Sanity check on the shape: for a sinusoid the slope at centre should be peak × 2π/period = 74.2 mNm × 2π/6.0° = 78 mNm/°; the model's directly computed centre stiffness is **76 mNm per degree** (4.36 Nm/rad). Match confirms the fundamental dominates — the feel will be a smooth sine detent, not a snap. (A sharper "wall" feel, if wanted, is the ring motor's job per decision 19, the decision that dynamic detent character comes from the motor.)

**Peak tangential force per magnet: 0.20 N** (band 0.12–0.33 N).

Energy barrier per detent (for feel calibration later): for a sinusoidal torque, E = T_peak × step/π = 74.2 mNm × 0.1047 rad / π ≈ **2.5 mJ** per step.

## 4. Q3 — six magnets, total torque

60/6 = 10 poles per magnet sector — integer, so all six magnets sit at identical phase and their tangential forces add directly (this is the design intent; it also means the detent torque is 6× one magnet's with no ripple cancellation).

    T_peak = 6 × 0.201 N × 0.0614 m = 0.0741 Nm = **74 mNm**

(The brief says "torque at r ≈ 60 mm"; the pole tips are at 61.4 mm and the force centroid sits ~1 mm behind the tip, so 61.4 mm is used. Using 60.0 mm flat would read 72 mNm — a 3 % difference, inside noise.)

**Baseline peak detent torque: ~74 mNm, band 45–120 mNm.** In the 60–150 mNm target band, but in its lower third — the design brief asks to design for the top of the range, and the baseline does not reach it.

## 5. Q4 — gap sensitivity

N42, 3 × 3 × 6 mm, Ø2.5 mm pole:

| radial gap (mm) | peak torque (mNm) | peak F_t per magnet (N) |
|---:|---:|---:|
| 0.4 | 138 | 0.375 |
| 0.8 (nominal) | 74 | 0.201 |
| 1.2 | 41 | 0.110 |
| 2.0 | 12.5 | 0.034 |

Fitted scaling over this range: T ∝ gap^−1.5 (ln(138/12.5)/ln(2.0/0.4) = 1.49). **The gap is the strongest single lever** — every 0.1 mm at the nominal point is worth ~15 %. This puts a real tolerance demand on the pole-tip circle and carrier concentricity: ±0.1 mm of runout modulates the detent ±15 % per magnet around the rotation (partially averaged across the six magnets).

## 6. Q5 — grade and size sensitivity

**Grade** (3 × 3 × 6 mm, gap 0.8 mm) — scales as Br² because the pole is unsaturated at this gap:

| grade | Br (T) | peak torque (mNm) |
|---|---:|---:|
| N35 | 1.21 | 64 |
| N42 | 1.30 | 74 |
| N52 | 1.45 | 92 |

N42 → N52 buys +24 %. Cost delta on 3-figure-quantity small blocks is pennies per magnet ("quote required" for the actual run — no supplier price read for this size in `docs/SOURCING-BOM.md` yet).

**Size** (N42, gap 0.8 mm; dims radial × tangential × axial; carrier annulus ≈ 3.5 mm deep radially):

| magnet (mm) | peak torque (mNm) | note |
|---|---:|---|
| 3 × 3 × 6 (baseline) | 74 | |
| 3 × 4 × 6 | 73 | wider tangentially: smears the profile, no gain |
| 4 × 3 × 6 | 87 | +17 %, but 4 mm radial exceeds the 3.5 mm annulus |
| 3 × 3 × 8 | 71 | taller: flux spreads beyond the pole's capture, slight loss |
| 3.5 × 4 × 8 (max that fits) | 75 | ~nothing over baseline |
| 5 × 5 × 5 | 68 | violates annulus and smears across the 6.4 mm pitch |

The brief's candidate sizes map as: "4 × 6 × 3" ≈ the 4 mm-radial row (blocked by the annulus), "3 × 6 × 4" ≈ the wider/taller rows (no gain), "5 × 5 × 5" is worse and doesn't fit. **Conclusion: magnet size is a dead end within the annulus — the Ø2.5 mm pole face is the bottleneck (it captures only 27 % of even the baseline magnet's face).** Money goes into grade, gap, and pole diameter, not magnet volume.

**Pole diameter** (N42 3 × 3 × 6, gap 0.8 mm): Ø2.0 → 53 mNm, Ø2.5 → 74 mNm, Ø3.0 → 94 mNm. Nearly ∝ area (+27 % for M2.5 → M3). The pitch is 6.4 mm, so Ø3.0 mm tips still leave 3.4 mm between tips — profile stays clean.

## 7. Q6 — is 60–150 mNm reachable?

Yes — the bottom of the band is met by the baseline as drawn; the **top of the band needs three cheap changes together** (all central estimates, same error band):

| configuration | peak torque (mNm) |
|---|---:|
| baseline: N42 3 × 3 × 6, Ø2.5 pole, gap 0.8 mm | 74 |
| N52 only | 92 |
| Ø3.0 mm pole only | 94 |
| N52 + Ø3.0 mm pole | 117 |
| N52 + Ø3.0 mm pole + gap 0.6 mm | **158** |
| N52, Ø2.5 pole, gap 0.5 mm | 147 |
| N42, Ø3.0 pole, gap 0.5 mm | 148 |

Recommended route to 150 mNm: **N52, M3 (Ø3 mm) poles, 0.6 mm gap** — it spreads the demand across three levers instead of pushing the gap to 0.5 mm, where tolerance sensitivity (±0.1 mm → ±20 %+) and tip saturation both bite. No architecture change; the carrier annulus, pole circle and six-magnet layout all survive.

## 8. Q7 — residual torque with the carrier dropped

Suspicion confirmed and quantified: a radial-gap detent **fades gradually with vertical offset** — the pole still sees the magnet's fringing field from below. N42 3 × 3 × 6 (6 mm axial), gap 0.8 mm, pole centre at z = 15 mm, magnet lowered by z_off:

| carrier drop (mm) | peak torque (mNm) | % of engaged |
|---:|---:|---:|
| 0 | 74 | 100 |
| 1 | 72 | 97 |
| 2 | 61 | 83 |
| 3 | 39 | **52** |
| 4.5 | 8.5 | 11 |
| 6 | 1.1 | 1.4 |

The fade is slow at first because the magnet is 6 mm tall: for the first ~1.5 mm of travel the pole is still fully inside the magnet's axial extent. The knee sits where the magnet's top edge passes the pole centre.

**The settled 3 mm drop is a 2:1 attenuator, not an off-switch.** Consequences and options are flagged in section 11.

Bonus: the fade curve is smooth and monotonic, so the carrier height is a usable *analogue* strength control over roughly a 2–70 mNm range if the travel is extended to ~5 mm — worth knowing even though decision 19 (dynamic strength from the motor) makes the motor the primary strength control.

## 9. Hysteresis drag and pole material (input to Q8)

Each pole is driven around a minor magnetisation loop once per magnet passage. Loop energy per unit volume ≈ 4·Hc·B_peak (loop-area rule of thumb; Hc = coercivity, B_peak ≈ 1 T in the pole body from the model). Per detent step, six magnets each cycle one pole; drag torque = energy per step / step angle (0.1047 rad). Pole volume = π(1.25 mm)² × 4 mm = 19.6 mm³:

| pole material | coercivity Hc (A/m, estimate; Bozorth, *Ferromagnetism*) | drag torque (mNm) |
|---|---:|---:|
| annealed low-carbon steel / soft iron | ~150 | 0.7 |
| cold-drawn mild steel (as-machined) | ~400 | 1.8 |
| hardened alloy steel — **what a standard 45H grub screw is** | ~2500 | **11** |

11 mNm of always-on drag against a 74 mNm detent is a 15 % gritty background that the motor cannot cancel (it is dissipative, not positional), and hardened poles also acquire remanence — each pole leaves a small stray field signature. Soft poles keep drag under 2 mNm (≈ 2 %).

Saturation: low-carbon steel (μ0·M_sat ≈ 2.0 T) and soft iron (2.15 T) are both fine at the 0.8 mm gap (pole runs at ~65 % of saturation); at the 0.6 mm gap of the 150 mNm configuration the tip region approaches saturation, which slightly favours the higher-saturation material. Free-cutting mild steel (e.g. EN1A / 230M07) machines beautifully and is magnetically close to ideal after use in the as-drawn state; annealing is optional polish, not a requirement.

## 10. Q8 — recommendations

1. **Magnet: N52, 3 mm radial × 3 mm tangential × 6 mm axial block, axially the long way (6 mm vertical), nickel-plated.** Grade upgrade is the cheapest +24 %; size changes inside the annulus buy nothing (section 6). Note `docs/SOURCING-BOM.md` already records that magnets are not UK stock — this size/grade needs the same treatment ("quote required"). **Confidence: high** on orientation and on "size is a dead end"; **medium** on N52 over N42 (only needed if the 150 mNm end of the band survives strand-A feel testing — if 75 mNm feels right, N42 stays).
2. **Pole: Ø3 mm (M3), flat-point, low-carbon steel.** +27 % over M2.5 for the same pitch clearance. Specifically **not** a standard hardened set screw and **not** stainless: ISO 4029 / DIN 916 grub screws are hardness class 45H per ISO 898-5 (hardened, ~11 mNm drag, section 9), and A2/A4 stainless screws are austenitic — essentially non-magnetic, detent gone. Also avoid cup-point tips (DIN 916's cup hollows out the face that does the work); use flat point (DIN 913 pattern) or a turned soft-steel pin, thread-locked or press-fit. Best magnetics for the money: **turned EN1A (230M07) free-cutting mild steel pins or custom-machined M3 flat-point studs**, 60 × 60 units = 3,600 pieces — a trivial turning job, "quote required". **Confidence: high** on avoiding hardened/stainless; **medium-high** on M3 over M2.5 (depends on whether the top of the torque band is actually wanted).
3. **Gap: hold 0.8 mm nominal for the baseline feel; design the carrier so the gap can be shimmed to 0.6 mm.** T ∝ gap^−1.5 makes this the strongest tuning lever and also the tightest tolerance: ±0.1 mm of combined runout is ±15–20 % torque ripple around the rotation. Put a concentricity budget (pole circle + carrier) of ≤ ±0.05 mm on the drawings. **Confidence: high** on the scaling law, **medium** on the absolute numbers.
4. **Pin the magnet orientation on the drawing** (6 mm axis vertical, magnetisation radial-outward, all six same polarity — alternating polarity was not modelled and is not needed since poles are soft). **Confidence: high.**

## 11. Flags — settled constraints under stress

- **The 3 mm carrier drop only halves the detent (52 % residual).** If the settled intent behind the lifting carrier was "weaken", the design works and this section just puts a number on it. If any downstream feature (free-spin scrolling, motor-only haptic modes) assumes the magnetic detent can be *removed*, it cannot at 3 mm: that needs **~4.5 mm of travel for <11 % residual, ~6 mm for <2 %** — or the motor must actively cancel a ~39 mNm sinusoid at 60 cycles/rev, which is exactly the kind of always-on correction decision 19 (dynamic detent strength from the motor) was meant to avoid. This is a physics finding, not a re-litigation: the constraint "3 mm ≈ off", if anyone holds it, is wrong. Needs a ruling on what residual is acceptable before the carrier travel is frozen in CAD.
- **"3 × 6 × 3 magnetised facing outward" is under-specified.** With the 6 mm edge tangential the detent is 17 mNm, not 74 mNm — a 4.4× swing on an orientation the spec currently leaves free. One line on the drawing fixes it.
- **"Plain steel grub screws" as written will probably arrive hardened (45H) or stainless.** Either quietly degrades the detent (grit, or total loss). The sourcing line item must name the steel, not the screw standard.

## 12. What the bench rig must measure (hand-off to strand A)

The model's absolute error band is −40 %/+65 %; these four measurements collapse it: (1) radial pull of one magnet on one pole at 0.4/0.8/1.2 mm (calibrates the whole model with one load cell); (2) peak detent torque of the assembled ring at nominal gap; (3) torque vs carrier drop at 0/1/2/3 mm (validates the fade curve); (4) back-drive drag with a hardened vs soft pole fitted (validates section 9 before 3,600 pins are ordered).
