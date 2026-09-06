# the 60 — design changes for the CAD session

**Working list, edited in place.** Changes decided outside the CAD session that the model has to absorb. **Delete an item once it is built.** This file is not a history — if it is empty, the model is current.

Last edited 6 September 2026, against **v14** as the current mechanical authority; the next build is **v15**. Source documents: `docs/THERMAL-PLAN.md`, `docs/GROUNDING.md`, `docs/CONNECTORS.md`, `docs/HALO-BRIGHTNESS.md`, `docs/SYSTEM-REVIEW.md`.

Where this file names a section number it means **the current specification**, whichever version that is — the numbering has been stable across v10 to v14.

**What v15 is about.** One theme: the plate's cooling path was measured properly for the first time and it does not work. At the airflow needed to carry the sustained load, the object needs about **70 Pascals** of pressure across it, and the small radial blower reserved in the rear plenum can push perhaps ten to twenty. Two thirds of that loss is in two places — the fin channels, which are too shallow, and the exhaust, which is a quarter the size of the intake and points down at the desk. Items 1 to 4 fix both, without changing the overall height and without enlarging the blower's envelope. Item 5 is the rim edge treatment that has been held since v13, now settled and made compatible with the new openings.

Two drawings in `Claude outputs/` carry the reasoning: **`v15-plate-reproportion.svg`** (item 1) and **`v15-fins-and-exhaust.svg`** (items 2 and 4).

**A Pascal (Pa) is a unit of pressure**; the figures below are all quoted at 1.0 litre of air per second, which is what carries the 12.7 W sustained load in air that has warmed by about 10 degrees.

---

## 1. Re-proportion the plate: 2 mm web, 5 mm duct, 1 mm closing plate

Section 4.16 currently reads **4 mm web (z 4–8), 3 mm duct (z 1–4), 1 mm closing plate (z 0–1)**. Change it to:

| | v14 | v15 |
|---|---|---|
| Web | 4.0 (z 4–8) | **2.0 nominal (z 6–8)** |
| Duct | 3.0 (z 1–4) | **5.0 (z 1–6)** |
| Closing plate | 1.0 (z 0–1) | 1.0 (z 0–1), unchanged |
| Total | 8.0 | **8.0 — unchanged** |

**Nothing is given up in height.** The 4 mm web was a round number in `THERMAL-PLAN.md` rule 5, chosen for stiffness and screw threads; it was never derived, and it has never been tested against the airflow it costs.

What it buys, with the fin change in item 2: the channel cross-section goes from 3 × 3 = 9 mm² to **3 × 5 = 15 mm²**, the fin surface area rises by about 44 percent, and the resistance across the plate falls from about **41 Pa to about 16 Pa**. A 5 mm tall, 1 mm thick aluminium fin is still essentially fully effective, so all of the added surface works.

**Screw threads — less of a problem than it first appears.** An M2.5 thread in 2 mm of 6082 has a pull-out strength of roughly 1.9 kN, which is orders of magnitude more than any of the sixteen light board fixings will ever see. Leave them at 2 mm. Keep a local 4 mm thickening only for:

- the M3 chassis bond at (48, 27) — a bond screw that backs off is worse than one that is absent, so give it full thread;
- the six closing-plate screws, which already have Ø7 islands through the duct;
- anything the checker finds carrying a real load.

Where a local thickening falls inside the ducted region it goes **downward as an island with the fin channels routed round it**, exactly as the closing screws already do. It must not stand up into the cavity — that would raise every board sitting on the web and cost the height this change is protecting.

**Stiffness.** A 2 mm web is eight times less stiff in bending than 4 mm. Three things recover it and none of them are new parts: the **nineteen fins at 5 mm tall are themselves stiffening ribs** running front to rear; the **stainless rim ring is a stiff hoop** bolted to the plate's rim by seven M3; and the two top-face ribs stay. The weak direction is side to side, across the fins. **Report the plate's centre deflection under a stated knob load, before and after** — do not assert it is adequate, measure it in the model.

Expected mass change: the core falls from about 137 g to about 112 g, so the plate goes from about 463 g to about 438 g.

**Cost, accepted:** the web is what spreads heat sideways from the compute module's footprint out to the fins, and halving it roughly doubles that spreading resistance — about **1.4 K more on the compute module**. Acceptable. Place one top-face rib deliberately over the compute module's footprint; it acts as a local spreader and recovers part of it. If the compute module sits where the web is thinned and no rib runs over it, the penalty is larger than 1.4 K — check this specifically.

## 2. Fin channels: 5 mm tall, and only where the heat is

**The direction is already right and does not change.** Section 4.16 has nineteen straight channels running front to rear, and that is correct: air enters at the rim and leaves at the rim, so it travels front to back, and fins must follow the flow. Radial fins would sit across it. The gap is already 3.0 mm with 1.0 mm fins, which is also right.

Two changes:

1. **Fin height 3.0 → 5.0 mm**, on the same 4 mm pitch, filling the new duct. This is `THERMAL-PLAN.md` rule 11 and it must be changed there too (item 10).
2. **Fin only where the heat is.** Aluminium spreads heat sideways very well, so fins across the whole run mostly cost pressure without earning anything. Fin the **compute module and converter footprints** and leave the rest of each channel as open 5 mm cavity. An unfinned stretch has roughly a seventh of the resistance of a finned one. On a 110 mm run, finning about 50 mm of it takes the plate from about 16 Pa to about **8 Pa** at no cost in surface area that matters.

Keep the two-circuit arrangement and the checker rule that each circuit has both an intake and an exhaust.

## 3. Rim openings: one uniform pattern, mirrored, all the way round

The current 21 intake grooves of 7 × 3.5 mm sit on an odd count over a 270° arc, so the pattern cannot mirror about the front-to-back centreline — which is why the left and right side views of the render disagree. Replace the whole arrangement:

- **One pitch everywhere: 120 divisions at 3°**, a 4.59 mm pitch at r 87.7.
- **Openings 1.8 mm wide × 4.5 mm tall**, in the ring's **edge face**, at z 1.25–5.75 so they line up with the new 5 mm duct. Land 2.79 mm between openings, 1.25 mm below and 2.25 mm above.
- **Mirrored about the 0°–180° centreline**, so the two side views are identical by construction.
- **No openings across the port face.** That arc is plain, and plainly deliberate.
- **No blind openings anywhere.** Every opening in the band is a real one.

Arcs, in the model's frame (0° at the ports):

| Arc | Azimuth | Openings | Free area |
|---|---|---|---|
| Port face — plain | 344–16 | none | — |
| **Exhaust** | 16–60 and 300–344 | 29 | **235 mm²** |
| **Intake** | 60–300 | 80 | **648 mm²** |

The openings stay parametric (`VENT_N`, `VENT_W`, `VENT_H`, and the arc limits) so the counts can be trimmed once the ring's screw positions are final.

**The ring's fixings must land on the pitch, in the solid land between two openings** — the seven M3 ring screws, the two M2 port-face rail holes, and the bond screw. The bond screw is currently at az 56.25, which now falls on the intake/exhaust boundary; move it to the nearest land that still keeps it close to the chassis bond and hidden. If a fixing cannot be moved onto the pitch, move the pitch's phase rather than interrupting the pattern.

**Openings are no longer forbidden in the edge face.** `THERMAL-PLAN.md` rules 7 and 8 forbid them, on the grounds that the edge face carried the engine turning. The engine turning was deleted in v14, so that reason is gone (item 10). **Rule 9 still stands: no openings through the top face** — that is the halo's light channel.

**Keep the 1.5 mm bottom-edge undercut** as a supplementary intake. It costs nothing and it is invisible. It is no longer the primary path, because a bottom-edge undercut is blocked by a desk mat and edge-face openings are not.

## 4. Rebalance the exhaust — it is the single biggest loss in the object

At 1.0 litre per second the current 147 mm² exhaust throws away about **28 Pa**, more than a third of the whole budget, because the air leaves a small hole at nearly 7 metres per second and then meets the desk a few millimetres below.

The rear cannot supply an exhaust equal to the intake — measured against the real geometry, the port face and the two rear plenums leave about 88° of usable arc, not enough. It does not need to. **Target about 400 mm² of total rear exhaust**, which brings the loss down to about 4 Pa:

- **235 mm² through the rear edge-face openings** (item 3), which work whatever the object is standing on;
- **at least 165 mm² through the existing downward grooves into the pad voids**, up from 147 mm², as a supplement.

**Hard requirement: the edge-face part alone must be at least 200 mm².** The downward path is blocked when the dial sits on a soft mat or cloth, and the object must still work in that case. With the edge-face exhaust alone the system comes to about 20 Pa; with both paths open, about 12 Pa. Both are inside what the reserved 28 × 18 × 5 mm blower can deliver, which is the whole point of items 1 to 4 — **the blower envelope does not have to grow, and there is no plate respin to fit one later.**

Separation between the nearest intake opening and the nearest exhaust opening is about 46 mm, which is enough at a 10 to 15 K air temperature rise for the object not to re-breathe its own exhaust.

## 5. Rim edge treatment — settled

The edge face has been plain since the engine turning was removed in v13. This closes it.

**Material: stainless steel**, replacing the mild steel of section 4.16. Mass is effectively unchanged (7.9 against 7.85 g/cm³, so still about 300 g). Stainless is finished bare, which also closes the ring's open finish question — there is no plating, so no drawing note about masking, and the bond screw's star washer cuts through the passive layer directly.

**One note on the bond:** stainless against aluminium is a slightly worse galvanic pair than mild steel against aluminium, so the star washer and the thread-lock at that joint matter more, not less. Keep both faces bare and the joint dry and hidden. Nothing else changes in `GROUNDING.md` 4.1.

**The treatment:**

1. **The band is brushed axially** — the abrasive grain runs up and down, the same direction as the openings, so it reinforces their rhythm instead of cutting across it. Not circular brushing: the grain would run across every opening and leave the edges looking ragged, and it reads as rotation, which is wrong on a part that does not turn.
2. **A 0.3 mm × 45° polished chamfer at every opening mouth**, and along the ring's top and bottom edges. This is the whole decorative idea: a matte surface meeting a polished bevel is the move that reads as machined rather than moulded, and it makes the openings read as precise bright-edged apertures rather than dark holes. **The venting becomes the decoration**, which is what was asked for. It is also functionally right — it removes the burr from the sharpest feature on a hand-touched part and slightly improves the airflow entry.
3. **Optional, and cheap: three horizontal reeded grooves**, 0.55 mm deep on 1.2 mm centres, in the **upper land at z 6.2–8.0**. That zone is above the duct and structurally free, so the reeding costs nothing and gives a second, quieter rhythm above the openings without competing with them. Build it as a parametric switch (`REED_N`, default on) so it can be turned off after a render.

**Do not** re-introduce an all-over decorative texture across the band. Two competing rhythms on one small face is exactly what was rejected in v13.

## 6. The ring's internal plenum — optional, build it if it is cheap

Boring an annular groove into the ring's inner face behind the openings — roughly 4.5 mm radial × 5.6 mm tall — was the original enabler for taller openings. **The 5 mm duct in item 1 has made it unnecessary for that purpose**: the openings now line up with the duct directly. It retains two smaller benefits:

- every opening shares one air space, so the openings far from the blower actually flow instead of the near ones taking all the air;
- each opening shortens from a tunnel through solid steel to a 2 mm one, which is easier to cut and to deburr.

It is one extra boring operation on the same lathe setup and it takes about 80 g off the ring. **Build it if the ring's geometry takes it without a fight; drop it if it complicates the flange or the bond screw.** The openings stay 4.5 mm tall either way.

## 7. Converter rating

The 10 A figure came from the old halo number. Size the module from the measured inlet load (bench item) — the halo's 2.54 A no longer justifies 10 A on its own. The envelope (38 × 25 × 8) stays until a part is chosen; if the chosen part is larger, the front crescent at az 180 has r 53–78 and t ±19 to give.

## 8. Assumptions the model made that a real part must confirm

Not decisions — things the model had to guess, each tagged ASSUMED in the parameter block:

- The bleed leaf: 4 wide, 0.2 thick phosphor bronze, bearing at r 71.5; its drag must not be felt.
- The vibration actuator's pogo-pin board (7 × 8 × 1) and pins (Ø1.5, 2.2 compressed) against the flex tail's pads at z 11.75 and 14.35.
- The rotor sensor lead: flex-rated for 10⁵ cycles at 2.4 mm; its notch in the carriage shoe (2.4 × 2.2) and beside the plate's tab slot (2.5 × 4).
- The USB-C shell wire's route under the connect bracket's slab (a 1.5 mm gap).

---

## What does not change

So the model is not over-corrected:

- **The internal structure's vent slits are the speaker's acoustic port and nothing else.** They are not an intake and they were never part of the forced path. The cavity above the web breathes by buoyancy only, through them, and the web has no holes — the forced stream never enters the cavity, never passes the panel and never passes the optical encoder. **Do not open them up for airflow.** Drawing forced air past the encoder's optical gap and the panel is how this object collects dust in the one place it must not.
- The two-circuit duct arrangement, the collector, the rear plenums, and the blower envelope reserved and unfitted.
- The boards mounting to the plate; the plate as the chassis.
- The pad as a ring, with the rear voids the downward exhaust drops into.
- Everything in `THERMAL-PLAN.md` section 14 except rules 5, 7, 8, 10 and 11, which item 10 changes.

## 9. Report back

On top of the existing rule 17 (intake and exhaust free areas achieved, and the fin count):

- the plate's **centre deflection under a stated knob load**, with the 4 mm web and with the 2 mm web, so the stiffness loss is a number rather than an assurance;
- the **total system pressure at 1.0 litre per second** — intake, fin channels and exhaust separately — with the downward exhaust open and with it blocked;
- the **finned and unfinned lengths** of each channel, and which components they cover;
- confirmation that every ring fixing lands on a land between two openings.

## 10. Rules to change in THERMAL-PLAN.md section 14

Done in the same edit as this file — listed here so the change is visible to anyone reading only this document. Rules 5, 7, 8, 10 and 11 have been rewritten; if any of them still reads as it did in v14, the edit did not land.
