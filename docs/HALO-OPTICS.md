# the 60 — halo optics: why the band shows dots, and the arrangement that fixes it

**Date: 7 September 2026. Status: recommendation, for the bench and then the decision index.** Answers a question no document had asked: *how does the halo become one continuous line of light rather than a row of lamps?* `HALO-BRIGHTNESS.md` settled how bright the halo may be. This settles how it looks.

**Recommendation: turn the LEDs to face DOWN at a white floor inside the channel, and thicken the diffuser to 4.0 mm with a vertical outer face.** The strip hangs face-down from a ledge at z 12.0 and fires at a white floor on the rim ring 4.0 mm below; the diffuser is lit only by light returning from that floor, so no LED is ever in direct view. The diffuser's inner face stays at r 85.8, its outer face becomes vertical at r 89.7 — 4.0 mm thick, standing 2.0 mm proud of the knob at Ø179.4, seated on a 1 mm shelf added to the top of the stainless rim ring. **LED count is 60 to 120, settled on the bench (section 8); test 60 first, and go up while the band still ripples.** The knob, the plate, the 8 mm rim and the object's height are untouched.

**Figures: `HALO-SECTION.html`** — radial section as built, radial section as proposed, the three LED directions compared, and the unrolled plan. **Evidence: `Research/5-halo-optics-RD.md`** — teardowns, patents and supplier data with URLs.

---

## 1. What is wrong with the v15 arrangement

`V15-SPECIFICATION.md` §8.1 puts the LED strip on a 1.1 mm band on the structure's wall at r 84.0–85.6, standing vertically and firing outward, with the diffuser's inner face at r 85.8. **The gap is 0.2 mm.** At 53 LEDs on a 533 mm circle the pitch is 10.0 mm.

Two consequences, both bad, and one of them is not optical:

- **Each LED lands on the diffuser as its own spot.** With 0.2 mm of air, every LED's light reaches the opal before it has met its neighbour's. The only mixing available is the scattering inside 1.9 mm of acrylic, which spreads light over roughly its own thickness — millimetres, against a 10 mm pitch. The band reads as 53 lamps.
- **The diffuser is 0.9 mm thick where it meets the steel** (§5.3: r 85.8–86.7 at the bottom, leaning out to 87.7 at the top). That is a cantilevered cone standing on a knife edge, and it is why the printed prototype felt flimsy. Machining it from acrylic would have made a rigid part of the wrong shape.

Moving from a print to machined opal acrylic fixes the material and nothing else. **The 0.2 mm gap is not a material problem and no diffuser grade closes it.**

---

## 2. The rule that governs this, and what the evidence says

Every published figure for hiding LEDs behind a diffuser is a ratio of **LED spacing to LED-to-diffuser distance**.

| Source | Ratio for complete LED hiding | Tag |
|---|---|---|
| BrightView Technologies, V-H105 volumetric diffuser — the most aggressive spec any diffuser vendor publishes | **1 : 0.75** | PUBLISHED |
| BrightView, V-H080 | 1 : 0.90 | PUBLISHED |
| General backlighting rule (LEDrise, worked with a 10 mm pitch example) | **1 : 1** | PUBLISHED |
| BrightView, weaker single-sided films | 1 : 1.3 to 1 : 4 | PUBLISHED |

**v15 as built sits at 1 : 0.02** — about forty times outside the most aggressive published number.

Two things the research turned up that matter more than the ratio itself:

- **Evonik, Röhm, Perspex and Covestro publish no LED-distance guidance at all.** Their datasheets give transmission and haze and leave cavity geometry to the designer. There is no diffuser grade sold on the claim that it works at 0.2 mm. (PUBLISHED, by absence — checked against PLEXIGLAS Satinice TI 211-11, Perspex Spectrum LED, and Covestro's *Shaping LED diffuser performance*.)
- **Almost no shipping product solves this problem; they avoid it.** Amazon's Echo ring patents (US9574762B1, US9641919B1) put down-firing LEDs into per-LED reflector cups with triangular spreading facets before the light reaches a diffusive ring — a reflector, not a gap. Nest Thermostat E uses six side-facing LEDs edge-coupled into a light-guide sheet. Apple's HomePod mini stacks three graded diffusers with deliberate air gaps between every layer. Across roughly forty teardowns and patents, exactly one document states a diffuser thickness (Amazon US10620913B2: *"about 1 millimetre"*, 35–75 % transmission) and **none states an LED-to-diffuser gap**. Full evidence in `Research/` and in the halo diffuser research note.

---

## 3. The fix: point the LEDs away from the diffuser

The question is not up or down. It is **whether the diffuser can see a source at all.**

| Arrangement | Diffuser sees a source directly? | Heat lands on | Verdict |
|---|---|---|---|
| **A — outward** (v15 as built) | Yes | printed PETG wall | fails |
| **B — up, with a white baffle** shielding the diffuser's lower inner face | No | **stainless rim ring** | good; band runs brightest at the top |
| **C — down at a white floor** | No | printed ledge | **best; most even** |

**C is the recommendation.** Firing up without a baffle still leaves a direct sight line from each LED to the bottom of the diffuser's inner face, so the band would be brightest and most scalloped along its lower edge — precisely where the eye lands at a desk.

**Why firing down helps more than the throw distance alone suggests.** A down-firing LED 4.0 mm above a white floor lights a pool on that floor roughly twice the throw across — about 8 mm. **That pool, not the 2 mm LED package, becomes the source the diffuser sees.** Neighbouring pools merge on the floor before any light reaches the opal. This is why the count can fall rather than rise, and it is the whole argument for the arrangement. (ASSUMED: the 2× factor is geometry from a Lambertian emitter, not a measurement. Section 8 measures it.)

**Cost of C.** The strip returns to printed plastic — the ledge — instead of the stainless ring. That gives up the thermal benefit of B. Two ways to recover it if the bench says the heat matters: a thin aluminium ledge in place of the printed one, or fall back to B. Keep both on the rig.

---

## 4. Geometry as proposed

Replaces §8.1's halo rows, §5.2's strip band and diffuser lip, §5.3 in full, and §4.8's mounting. Nothing outboard of the diffuser changes; the knob stays Ø175.4 and the height stays 35.9.

| Feature | v15 as built | Proposed | Note |
|---|---|---|---|
| Structure wall | r 81.2–82.8 | **r 80.2–81.8** | moves inward 1.0 to open the channel |
| Strip band on the wall | r 82.8–83.9, 1.1 thick | **deleted** | the wall no longer carries the strip |
| Channel | none (0.2 gap) | **r 81.8–85.8, 4.0 wide**, z 8.0–13.5 | walls, floor and roof white |
| Channel floor | — | **rim ring top face at z 8.0**, white liner or white coating | the reflector that becomes the source |
| LED ledge | — | **r 81.8–85.8, z 12.0–13.5**, printed, off the structure | strip hangs from its underside |
| LED strip | 5 mm, vertical, firing outward | **4 mm flat, facing DOWN**, emitting face at z 12.0 | 2020 top-firing parts |
| Throw | 0.2 mm | **4.0 mm** to the floor | |
| Diffuser inner face | r 85.8 | r 85.8 | unchanged; it is the channel's outer wall |
| Diffuser outer face | r 86.7 → 87.7, leaning | **r 89.7, vertical** | Ryan's ruling, 7 Sep |
| Diffuser thickness | 0.9 at the foot, 1.9 at the top | **4.0 throughout** | |
| Diffuser height | 5.5 (z 8.0–13.5) | 5.5 (z 8.0–13.5) | set by the knob skirt; unchanged |
| Object diameter at the band | Ø175.4 | **Ø179.4** | the band stands 2.0 proud of knob and plate |
| Diffuser seat | 0.9 wide on steel | **4.0 wide** on a new 1 mm shelf on the rim ring, out to r 89.7 | no cantilever |
| Retention | lip resting on the top edge | lip clamping the top face through a compliant gasket, **0.3 radial clearance** | see §6 |

**Two checks this opens (GAP):**

1. The rim ring's 1 mm shelf out to r 89.7 sits directly above the 92 obround vent openings (z 1.55–6.05 in the wall at r 84–87.7) and above the 0.8 undercut. **Confirm the shelf does not close or shadow the opening mouths**, and that electropolishing still reaches them.
2. The wall moving inward 1.0 mm cascades to the seat flange, the three wheel windows, the wheel posts at r 76.9, the pillars at r 77.2 and the perimeter slits. Parametric, but the checker must re-run.

---

## 5. LED count

Two requirements land on this number and they want opposite things.

**Information is the easy one and is not the constraint.** Even 36 LEDs give 10° steps — 2.8 % of full scale. Dimming the last lit LED part-way slides the perceived end of the arc between two positions, so a blended band renders a continuously moving arc terminus rather than stepping. Blending is what buys sub-LED resolution; hard-edged dots cannot do it. **Every count below shows "40 %" comfortably.** The number is chosen entirely by how the band looks.

**Seamlessness is the constraint, and more is better.** At a strip radius of r 83.8 the circumference is 526.5 mm.

| Count | Step | Pitch | Scale per LED | Ratio at 4.0 mm | Full white |
|---|---|---|---|---|---|
| 36 | 10.0° | 14.6 | 2.8 % | 1 : 0.27 | 1.73 A / 8.6 W |
| 53 — v15 | 6.8° | 9.9 | 1.9 % | 1 : 0.40 | 2.54 A / 12.7 W |
| **60** | 6.0° | 8.8 | 1.7 % | 1 : 0.46 | **2.88 A / 14.4 W** |
| 90 | 4.0° | 5.9 | 1.1 % | 1 : 0.68 | 4.32 A / 21.6 W |
| **120** | 3.0° | 4.4 | 0.8 % | 1 : 0.91 | **5.76 A / 28.8 W** |

The ratio column is the **direct-lit** requirement and is therefore the pessimistic bound — it is what would be needed if the diffuser could see the chips. Firing down should beat it (§3). How far it beats it is the one thing the bench decides.

**60 and 120 are the two counts to consider; 90 is not.** Six degrees is exactly one LED per knob detent, so a single detent of rotation is a single step of the arc and the light shares a unit with the mechanism. 120 gives two per detent and keeps that logic. 90 divides into neither 60 detents nor a clean angular step.

Current at 48 mA per LED (PUBLISHED, WS2812B-2020 datasheet — 16 mA per colour channel). Full white on the whole ring is a state that essentially never occurs, but it sizes the converter, the halo feed and the Pico-Lock contacts on the motion board. **At 120 the peak is 5.76 A and the "up to 4 A" halo allowance in §4.11 no longer covers it.**

---

## 6. The diffuser as a part

**What thickening buys.**

- Bending stiffness rises with the cube of thickness. Against the current *thickest* section (1.9 mm) a 4.0 mm wall is roughly **nine times stiffer**, and the 0.9 mm foot — the actual failure point — stops existing.
- **Twice the scattering path.** Hiding power rises with the distance light travels through the opal, so a 4 mm wall does real optical work a 1.9 mm one cannot.
- **A part that can be machined.** A 4 mm web in 6 mm cast opal sheet sits well inside the 1.5 mm minimum wall for CNC-routed acrylic. The 2 mm web did not, and was also below the "minimum feature ≥ material thickness" rule every laser bureau publishes.
- **A real seat**: 4 mm of flat bottom face on steel, clamped axially through a compliant gasket.
- **Edges that can be chamfered** — 0.3 mm all round. At 0.9 mm there was nothing to break, and a chipped edge is where an acrylic crack starts.

**What it costs.**

- **Transmission.** 4 mm of a 36 % grade passes far less than 1.9 mm did. Move up the range: **Perspex Opal 030 at ~68 %**, or **PLEXIGLAS Satinice 0D010 DF at 83 % through 3 mm**, which diffuses by beads distributed through the bulk rather than by surface texture — the right mechanism for a thick wall. (PUBLISHED: TI 211-11.) The 1TL1/1TL2 grades named in `SOURCING-BOM.md` are too dark at this thickness.
- **The silhouette changes.** A 2 mm proud band between a Ø175.4 knob and a Ø175.4 plate is a visible collar, and it should be a decision rather than a side effect. It also makes the ring the first thing a sleeve catches — survivable at 4 mm, and it would not have been at 0.9.
- **Still no stock tube.** Opal acrylic tube does not exist at Ø179.4, and does not exist at any large diameter in a wall under 3 mm — the whole UK stocked range is 3 mm wall at 150 / 160 / 200 / 250 mm OD (PUBLISHED: Clear Plastic Tube Shop, Plastock). The ring is machined from cast opal sheet either way; 4 mm makes that routine rather than fragile.

**Rules that carry into the drawing.**

- **Cast, not extruded** — better melting resistance and less stress-whitening when machined.
- **Anneal after machining**: 80 °C, two hours minimum for a machining-only part, slow cool (PUBLISHED: ACRYLITE fabrication manual — one hour per millimetre, two-hour floor).
- **No isopropyl alcohol or acetone**, in assembly or in the care instructions. Crazing needs residual stress *and* a solvent; published data puts the crazing threshold at 31.4 MPa unmachined, dropping after machining, with a **threefold increase in stress sensitivity after alcohol exposure** (PUBLISHED: *Polymers* 15(6):1375; Plaskolite TEC380). Soap and water. This is the cheapest reliability decision on the object.
- **Radial clearance, never an interference fit.** PMMA expands 7.0–7.7 × 10⁻⁵ /K against stainless at 1.73 × 10⁻⁵; over Ø179.4 and a 20 K swing the differential is **about 0.21 mm on diameter**, and moisture swell is of the same order and pushes the same way. **Budget 0.3 mm radial clearance** and clamp axially through foam or silicone, not hard between two machined faces.

---

## 7. What else changes

| Document | What needs revising |
|---|---|
| `V15-SPECIFICATION.md` §4.8 | strip type, orientation, mounting, count, peak current |
| `V15-SPECIFICATION.md` §5.2 | delete the 1.1 strip band; wall to r 80.2–81.8; add the LED ledge; lip underside white |
| `V15-SPECIFICATION.md` §5.3 | diffuser section replaced in full |
| `V15-SPECIFICATION.md` §4.16 | rim ring gains the 1 mm shelf to r 89.7; check against the 92 openings |
| `V15-SPECIFICATION.md` §8.1 | diameter table: the band is Ø179.4, the knob and plate stay Ø175.4 |
| `V15-SPECIFICATION.md` §4.11, §4.13 | converter and Pico-Lock feed sized for up to 5.76 A, not 4 A |
| `HALO-BRIGHTNESS.md` | the rolling-mean instrument is unaffected and still right; the peak figures move |
| `SOURCING-BOM.md` | strip line item; opal grade moves from 1TL1/1TL2 to Opal 030 or 0D010 DF |
| `THERMAL-PLAN.md` | halo heat moves off the printed wall onto a printed ledge (arrangement C) or the stainless ring (arrangement B) |

---

## 8. The bench test

**One rig answers everything above, and none of it needs the real ring.**

Build a straight channel 100 mm long, printed in black (a light fixture flatters the result), **4.0 mm wide**, with a removable white floor, a white roof, and a slot at one end to stand a strip of opal acrylic as the outer wall.

Variables:

- **Direction**: outward (A), up behind a white baffle (B), down at the floor (C).
- **Pitch**: 8.8, 5.9 and 4.4 mm — three short strips, matching 60, 90 and 120 on the ring.
- **Opal**: 2 mm and 4 mm, in two transmission grades.
- **Channel width**: 3.0 and 4.0 mm, so the cost of *not* moving the wall is known.

Method: dark room, phone on a tripod at 600 mm, **exposure, focus and white balance locked manually** — auto-exposure silently rescales every shot and makes them incomparable. Photograph at full white (scalloping is worst there) and at about 20 %, then repeat with one saturated colour: the red, green and blue dies sit at different places in the package and can fringe at short throws where white hides it.

For each photograph take a pixel-brightness profile along the strip and compute **modulation depth = (max − min) / (max + min)**. Pass mark: **below 5 %, confirmed by eye at 600 mm.** The 5 % figure is a working threshold, not a standard — the photograph and the eye are the verdict; the number exists to compare samples fairly.

**The reading that matters: does 60 firing down look as good as 120 firing outward?** If it does, the count halves, the peak current halves, and the whole thing gets easier. Record, for each combination: modulation depth, and how much light it costs — a perfectly uniform dim band is not a win.

About £40 of parts and an evening.

---

## 9. What is assumed, and what would change the answer

- **ASSUMED**: the 8 mm bounced pool (§3). It is geometry from a Lambertian emitter, not a measurement, and it is the single load-bearing estimate in this document. Section 8 measures it.
- **ASSUMED**: that a 4 mm flat strip at 120 per 526 mm bends to r 83.8 without lifting off the ledge. Confirm with a real strip before committing the ledge width.
- **ASSUMED**: white surfaces at ~90 % diffuse reflectance. Bare stainless is specular and a poor diffuser — the floor needs a white liner, a white coating, or a white printed insert, not polished steel.
- **GAP**: the rim ring's 1 mm shelf against the 92 vent openings (§4).
- **GAP**: whether the halo's heat on a printed ledge is acceptable in arrangement C, or forces an aluminium ledge or a fall back to B.
- **If the bench says even 120 firing down still ripples**, the remaining levers are, in order: widen the channel beyond 4 mm by moving the wall further in; add a diffuser film over the channel mouth as a second stage; or accept a visibly segmented ring and design the light language around discrete marks instead of a continuous band.

---

## Sources

Ratios and materials: BrightView Technologies symmetric LED diffuser table; LEDrise pitch-and-distance note; Evonik PLEXIGLAS Satinice TI 211-11; Perspex opal light-transmission datasheet; Covestro *Shaping LED diffuser performance*; ACRYLITE annealing manual; Plaskolite TEC380; *Polymers* 15(6):1375. Product evidence: US9574762B1, US9641919B1, US10620913B2 (Amazon); US11346542B2 (Apple); US6685327B2, DE102015115365A1, US20060067084A1 (automotive light guides); Nest Thermostat E teardown. Full notes and URLs in the halo diffuser research document.
