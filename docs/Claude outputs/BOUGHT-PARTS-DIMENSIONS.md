# the 60 — bought parts, verified dimensions

**Purpose.** Every bought component, with dimensions taken from a manufacturer or distributor page, not assumed. Researched 3 September 2026. Anything still unverified is marked **V** and must not be relied on.

**Rule from Ryan, 3 September 2026:** the part determines the orientation, not the other way round. Nothing gets modelled around an envelope that has not been sourced.

---

## 1. Display module — Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C

**Waveshare publishes full CAD.** `https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-TOUCH-LCD-3_4C.zip` — a 5.2 MB ZIP containing a DXF, a dimensioned 2D PDF, and a **33 MB STEP assembly** (Creo, dated 16 April 2026). This replaces every V on the display.

| Feature | Verified value | Was in the model | Status |
|---|---|---|---|
| Disc OD | **115.00** | 115.00 | ok |
| Disc thickness | **6.00** | 6.00 | ok |
| Lens OD / viewing aperture | 112.50 ±0.10 / 88.20 ±0.20 | — | new |
| LCD active area | **87.60** | 87.60 | ok |
| PCB | **85.50 × 65.00 × 1.60** | 85.50 × 65.00 × 1.60 | ok |
| **PCB centre offset from the disc centre** | **4.50 mm**, toward the 40-pin header edge | 0 (assumed concentric) | **WRONG IN THE MODEL** |
| PCB top face below the front glass | **7.50** → 1.50 air gap under the disc | 1.00 standoff | **WRONG IN THE MODEL** |
| Mounting into the display housing | **4 × M4**, at (±37.50, ±37.50), i.e. **Ø106.07 PCD at 45/135/225/315**, tapped bosses opening rearward, boss OD 6.41, ~5.10 deep | 4 × M2.5 on Ø104 | **WRONG IN THE MODEL** |
| Four free PCB holes | Ø3.00 on a **58.00 × 49.00** rectangle | 58 × 49 | ok |
| Rear stack | PCB bottom −9.10, then 4.00 clear, then a **2.00 mm PMMA backplate** to −15.10 | not modelled | **MISSING FROM THE MODEL** |
| Tallest rear part | **USB-A, 6.40 above the PCB**, overhangs the board edge 0.50 and stands 0.40 proud of the backplate | 6.40 assumed | ok by luck |
| USB-C × 2 | 3.25 tall, overhang 1.04, centres 14.48 apart | — | new |
| RESET / BOOT switches | 3.30 tall, overhang 0.51 | — | new |
| Total assembly thickness | **15.10** (the web images say 15.00 — trust the CAD) | 15.0 | ok |
| Weight | **NOT PUBLISHED** | 60 g assumed | still **V** |

**Consequence of the 4.5 mm offset.** The board is not concentric with the disc. Its worst corner sits at **r 57.35** from the disc centre — 0.15 mm inside the disc edge and 0.65 mm inside the Ø116 bore. Every statement of the form "at azimuth X the board edge is at r 42.75" in earlier work is wrong on one side and must be redone from the STEP.

---

## 2. Drive motor

**Finding: no right-angle gearmotor at Ø10 or under is in production anywhere.** The only one that ever existed, the 45:1 Right Angle Micro Metal Gearmotor, is discontinued at Pimoroni with no other stockist. Every remaining Ø10 right-angle is quote-only (Kegu, ZHAOWEI, Maintex) or a 3–10 rpm stepper. **The bore drive therefore needs a bevel or a belt to turn the corner — that is settled, not a preference.**

| Part | Supplier | Body | Shaft | V | Output rpm | Stall torque | Back-drives | Price |
|---|---|---|---|---|---|---|---|---|
| **NFP-GM10-M20-185** (100:1) | nfpshop.com | **Ø10 × 25 round** (+10 shaft) | Ø2.5 D-cut | 6 | 185 free / 130 loaded | ≥78 mNm | **yes**, steel spur | $10.50 |
| NFP-GM10-M20-74 (250:1) | nfpshop.com | Ø10 × 25 round | Ø2.5 D-cut | 6 | 74 / 52 | ≥88 mNm | yes | $10.50 |
| Pololu #2369 (210:1 MP) | pololu.com | 10 × 12 × 25 | Ø3 D | 6 | 100 free | **167 mNm** | yes, spur | $23.95 |
| Pololu #2368 (150:1 MP) | pololu.com | 10 × 12 × 25 | Ø3 D | 6 | 150 free | 127 mNm | yes | $23.95 |

**Recommendation: NFP-GM10-M20-185.** Round Ø10 × 25 (the "short and fat" the bay rule asks for), in stock, published outline drawing and STEP, back-drives freely, $10.50. Buy a Pololu #2369 alongside as the torque insurance — 167 mNm, precious-metal brushes, same-week UK-reachable stock, at the cost of 2 mm on one axis.

**Rejected:** Pimoroni right-angle (discontinued) · maxon GP 8 A (no longer orderable) · Faulhaber 0816 + 08/1 (31 rpm at 256:1, and £242) · Kegu KG-10P1020R-EN (quote only, two vendor pages disagree on stall torque) · ZHAOWEI ZWSMD010010 (quote only) · PMD 210-102 (53 rpm, 20 mNm, 8-week lead) · NFP-MGB10P-19 (1258 rpm) · NFP-10GP-M10 (25.5 mNm, under the floor).

---

## 3. Ring actuator — the worm is the wrong mechanism

The ring needs **0.77 mm of tangential travel at r 29.5 (1.44 mm at the magnet), held with no current.** A worm-and-wheel plus gearmotor is 27 mm of hardware for that. A miniature leadscrew stepper does it in a can 8.2 mm long.

| Part | Supplier | Body | Screw | V | Step | Force | Holds unpowered | Price |
|---|---|---|---|---|---|---|---|---|
| **VSM0810** PM linear stepper | micro-steppermotor.com | **Ø8 × 8.2 mm** | M2×0.4 or M1.7×0.3 | 5 (3.3 variant) | 18°, **0.015 mm/step** | 0.37 mNm pull-out, ~2 N thrust (est.) | **yes** — 3.6° lead angle, self-locking, plus PM detent | $2–6, MOQ 1, 15–30 day lead |
| TSL-SM08284 | micromotorpro.com | Ø8, screw fitted | M1.7×0.3 | 5 | 0.015 mm/step | 0.37 mNm | yes | not published, "in stock" |
| NFP-609-699 (fallback) | nfpshop.com | Ø6 × 21.05 | — | 3 | 45 rpm | 45 mNm stall | **no** — 699:1 is hard to back-drive but is not a lock | $3.98 |

0.8 mm at 0.015 mm/step is **53 steps**. Open-loop, no encoder, parks dead with the coils off.

**Rejected:** Portescap 20DAM-K (Ø20, quote only) · New Scale M3-LS piezo stage (32 × 32 × 11 and $3,000) · Miga NanoMuscle SMA (does not latch) · Actuonix PQ12/L12 (far outside the envelope) · micro solenoid + ratchet (no off-the-shelf product exists — it would be a bespoke build).

---

## 4. Lift-off solenoid — NOT SOURCEABLE AS SPECIFIED

The model assumes Ø6 × 10 push solenoid. **Nothing at Ø8 × 15 or under exists in any catalogue.**

| Part | Supplier | Body | Stroke | Force | Coil | Price |
|---|---|---|---|---|---|---|
| Olimex PUSH-PULL-SOLENOID-5V | olimex.com / DigiKey | **8 × 10.3 × 16.3** | 5.00 | **NOT PUBLISHED** | 5–6 V, 0.63 A, 6 Ω | €2.50 |
| Adafruit 2776 | adafruit.com | 20 long, **W/H not published** | 3.0 | **0.78 N** | 5 V, 1.1 A | $4.95 |
| Takaha SSAC-0830 | takaha-japan.com | 18 × 22 × 30.4 — out of envelope | 5 | 1.81–2.94 N | 5 V | $14.54 |

No latching or bistable solenoid under Ø10 with published dimensions and force exists. Olimex also warns its part is pulse-only, ≤5 s energised. **The lift-off mechanism needs rethinking, not shopping.**

---

## 5. Supercapacitors — solved, and smaller than assumed

| Part | Supplier | C | V | ESR | Can | Price @100 | Stock |
|---|---|---|---|---|---|---|---|
| **Abracon AHCR-S04R0SA206Q** | Mouser | 20 F (−10/+30 %) | 4.0 (2.5 V floor) | 600 mΩ | **Ø8.0 × 12.0**, 3.5 lead pitch | $1.95 | 726 immediate |
| Abracon AHCR-S04R0SA106Q | Mouser | 10 F | 4.0 | 1000 mΩ | Ø8 × 12 (datasheet) / Ø6.3 × 12 (Mouser listing) — **conflict, verify** | $1.83 | 130 |
| Eaton HV0830-2R7605-R | Eaton | 6 F | 2.7 | 40 mΩ | Ø8.0 × 31.0 | — | — |

**Two AHCR-S04R0SA206Q in series = 10 F at 8.0 V in a 16 × 12 × 8 mm block.** Lying down that is 8 mm tall, inside the 9.8 mm cavity. This replaces the Ø10 × 30 open item. Caveat: lithium-ion hybrids with a 2.5 V lower threshold — they cannot be run to zero, and ESR is ~20× a classic EDLC.

---

## 6. Speaker — the modelled part does not exist in that shape

The model has a **Ø36 round** speaker. The BOM's chosen part, **PUI AS04008CO-R, is 40 × 20 × 5.8 mm — a rectangular frame with an oval cone**, 8 Ω, 2 W, 83 dB, 7.6 g. Not round.

| Part | Supplier | Outline | Z | Power | SPL | Note |
|---|---|---|---|---|---|---|
| PUI AS04008CO-R | DigiKey 3,943 / Mouser 964 | **40 × 20 × 5.8** | 8 Ω | 2 W / 3 W | 83 dB | the BOM's part; oval, not round |
| **Soberton SP-3205-1** | DigiKey 10638231 | **Ø32 × 5.5 round** | 8 Ω | 1.5 W | 90 dB, f₀ 650 Hz | the round option, and 7 dB louder |
| Soberton SP-3020 | DigiKey 9924421 | 30 × 20 × 5.2 oval | 8 Ω | 1.5 / 2.0 W | 85 dB | smallest |

Watch the PUI suffixes: `-R` is 5.8 mm, `-WR-R` and `-2-WR-R` are 8 mm.

**If the speaker stays central and round, it is the Soberton SP-3205-1 at Ø32 × 5.5** — 4 mm smaller than modelled, and louder. If it moves off-centre, the PUI oval becomes viable.

---

## 7. Bearings — confirmed

| Part | Supplier | Dims | Price ex VAT |
|---|---|---|---|
| **623ZZ** | Simply Bearings p170604 | 3 × 10 × 4 | £2.56 / £1.92 at 100 / £1.79 at 999 |
| 623-2RS | Simply Bearings p170605 | 3 × 10 × 4 | same breaks |
| **F623ZZ flanged** | Simply Bearings p155242 | 3 × 10 × 4, **flange Ø11.5 × 1.0 thick** | £3.42 |

Dynamic 0.64 kN, static 0.23 kN, 44,000 rpm in grease. All three in stock, same-day UK.

---

## 8. Magnets — 3 × 3 × 6 IS NOT A CATALOGUE SIZE

Checked first4magnets, Magnet Expert, supermagnete, Magnet Store, e-Magnets UK. **No 3 × 3 × 6 mm block is stocked by any of them**, in either magnetisation.

| Part | Supplier | Size | Grade | Coating | Magnetised | Pull | Price |
|---|---|---|---|---|---|---|---|
| **3 × 3 × 3 cube** | Magnet Expert 19980 / first4magnets p2960 | 3 × 3 × 3, **±0.1** | N42 | Ni-Cu-Ni | through one 3 mm axis | 0.38 kg | 50 for £10.92 inc · **500 for £72.00 inc (£0.14 each)** |
| 3 × 3 × 8 | first4magnets, code MOD8 | 3 × 3 × 8 | 45H | not published | not published | 0.5 kg | product page 404s |
| 8 × 3 × 3 | magnetstore.co.uk | 8 × 3 × 3 | N42 | Ni-Cu-Ni | not published | 0.79 kg | from £6.88 ex |

**Route: two 3 × 3 × 3 N42 cubes stacked north-to-south make one 3 × 3 × 6 magnetised along the 6 mm axis** — which is what the design wants — for £0.28 per magnet position, 12 cubes per unit, in stock now. Verify on the rig that the joint does not weaken the field noticeably. The alternative is a custom 3 × 3 × 6 at 500-off from Magnet Expert or Magnet Store, both of whom do custom blocks routinely.

---

## 9. Still unsourced or unverified

1. **Port board** — 40 × 14 × 1.6 is an **assumed envelope**, not a real board. Its −12 mm tangential offset is legacy (it was placed to clear supercaps that have since moved) and should be deleted and re-derived once the USB-C, jack and DAC are laid out on a real outline.
2. **Lift-off solenoid** — see section 4. No part exists; the mechanism needs rethinking.
3. **Display module weight** — not published by Waveshare anywhere.
4. **Abracon AHCR-S04R0SA106Q can diameter** — datasheet says Ø8, Mouser says Ø6.3. Verify before designing a pocket.
5. **Olimex solenoid force** — not published.
6. **ESR** for the Würth / Vishay / Samwha / CDI 10 F cells — on the manufacturers' datasheets, not the distributor listings.
7. **Magnet joint behaviour** for the stacked-cube route.
