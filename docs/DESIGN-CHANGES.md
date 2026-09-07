# the 60 — design changes for the CAD session

**Working list, edited in place.** Changes decided outside the CAD session that the model has to absorb. **Delete an item once it is built.** This file is not a history — if it is empty, the model is current.

Last edited 7 September 2026, against **v15** as the current mechanical authority. Source documents: `docs/GROUNDING.md`, `docs/CONNECTORS.md`, `docs/HALO-BRIGHTNESS.md`, `docs/THERMAL-PLAN.md`, `docs/SYSTEM-REVIEW.md`.

Where this file names a section number it means **the current specification**, whichever version that is — the numbering has been stable across v10 to v15.

Built in v15 and removed from this list: the plate re-proportioned to 2 web / 5 duct / 1 closing plate with the thickening downward as piers under every top screw (item 1); the fins 5 tall (item 2 — finned full length, because neither the compute module nor the converter sits over a channel: the Pi is in a window through the duct, the converter over the front collector); the ring's 120 positions on 3° with 92 obround openings into an underside groove, mirrored, plain across the port face and over the motor's carriage hole, every fixing on a land (item 3); the exhaust at 228 mm² through the edge face plus 101 through the undercut, with a 126 mm² trench from the blower (item 4); the stainless ring, bare, brushed axially, 0.3 polished chamfers, no reeding (item 5 — Ryan's review); the groove that item 6 called optional (item 6 — it is what makes the openings machinable); the report-back (item 9 — in `docs/v15/V15.md` and `checks.txt`: deflection under knob load nil because the knob's load never crosses the web; the ring fixings on lands; the areas; the mass); and, from Ryan's rulings of 6 September: the blower fitted as a required part with its saddle, hood, trench, gaskets and lead; the internal structure printed inverted on its flat seat; dowel pins in through-holes; the separate encoder shim family; the bleed foot flat.

---

## 1. Converter rating

The 10 A figure came from the old halo number. Size the module from the measured inlet load (bench item) — the halo's 2.54 A no longer justifies 10 A on its own, and the blower adds 0.13 A at 5 V. The envelope (38 × 25 × 8) stays until a part is chosen; if the chosen part is larger, the front crescent at az 180 has r 53–78 and t ±19 to give.

## 2. Assumptions the v15 model made that a real part must confirm

Not decisions — things the model had to guess to build the items above, each tagged ASSUMED in the parameter block:

- The blower's inlet opening (Ø24 in the face) and outlet (21 × 7 from 1.5 up, on one edge) — from the datasheet drawing; its outline, holes and leads are PUBLISHED.
- The Pi 5's fan connector's current rating (its position is in the vendor STEP).
- The three foam gaskets (0.3 under the blower's inlet face and the hood, 0.2 under the closing plate) and the groove for the last.
- The motion board's holes at ±12 (so two of them are the blower's through-bolts).
- The audio board's USB-A plug overmould (9 × 12 × 6.8) in the lower socket of the Pi's USB 3.0 stack; the halo strip's tail as a 3 × 1.4 ribbon to the motion board (its 5 V now through that board — question 32 in the questions file).
- The encoder shim's fitted height (the family 0.7–1.1 is printed; 0.9 is nominal).
- The bleed leaf: 4 wide, 0.2 thick phosphor bronze, bearing at r 71.5; its drag must not be felt.
- The LRA's pogo-pin board (7 × 8 × 1) and pins (Ø1.5, 2.2 compressed) against the flex tail's pads at z 11.75 and 14.35.
- The rotor sensor lead: flex-rated for 10⁵ cycles at 2.4 mm; its notch in the carriage shoe (2.4 × 2.2) and beside the plate's tab slot (2.5 × 4).
- The USB-C shell wire's route under the connect bracket's slab (a 1.5 mm gap).

---

## 3. The eccentric bushes are not reachable with a driver (Ryan, 7 September)

**Reported against the v15 model: the three bush sockets cannot be got at from the plate side — the internal structure is in the way.** The specification says they can. Section 5.2: *"three wheel posts Ø8 at r 76.9, az 30/150/270 (bush sockets open to the plate side)"*, and assembly step 4: *"Bushes half-turned from the plate side to seat the wheels; locked; shim out through the rim gap."* If a 2 mm hex key on a straight shaft cannot reach all three sockets and turn a full half-revolution, the model and the specification disagree and the model is what gets built.

This is not a preference. The bushes are the only adjustment in the machine: they set the knob's preload against the V-groove, and they are the thing to reach for when the knob feels loose or notchy. Losing access to them means the knob's fit is fixed at the moment the structure is printed.

**What the CAD session should do:**

1. **Prove it, don't assume it.** Add a check that puts a Ø4 cylinder (a 2 mm hex key's shaft plus clearance) on each bush's axis, running from the socket face down through the plate side, and reports the first thing it hits. A pass is a clear path to outside the assembly; anything else is a fail with the blocking body named.
2. **Say at which step it must be clear.** Two different requirements are hiding in one sentence. *Seating* the wheels happens at step 4, knob-side, before the plate exists — the driver only has to clear the structure itself. *Re-adjusting* preload later, on a built object, means the path must also clear the base plate, its ducting, the closing plate and the foot. Decide which one is required. If it is only the first, the specification's wording should stop implying the second.
3. **If the path is blocked, move the obstruction rather than the bush.** The wheels are at 30/150/270° and their radius sets the knob's geometry; the webs, the pillars at 160/240/320° and the wall's local thickness are free to move. A clearance bore straight through whatever sits below each socket is acceptable — it is a printed part.
4. **If later adjustment is wanted, it costs three holes in the base plate** on the bush axes, plugged or left open under the foot. Note the cost and let Ryan choose; do not add them unilaterally.

Report back which of the three sockets pass today, and what blocks the ones that do not.

---

## What does not change

So the model is not over-corrected: the plate's ducted construction with the blower on its +y side, the fin channels' direction, the ring's groove and openings, the boards mounting to the plate (the motion board on the blower's saddle), the stainless ring, the pad as a plain ring, the structure's inverted print, and every dimension in `THERMAL-PLAN.md` section 14 as rewritten for v15 all stand as built.
