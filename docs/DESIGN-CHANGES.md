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

## 4. The gimbal motor's hollow shaft is no longer required (Ryan, 7 September)

**Decision: the hollow shaft comes out of the requirement.** The JD-Power MY-3514C is £56 and its hollow shaft was inherited from the old centre-mounted layout, where something passed through the motor. Nothing does now — the motor is off-axis at azimuth 90°, r 55.0, driving the bore through a silicone band, with nothing passing through it at all. Dropping that one requirement opens the field to generic 2804/2805 gimbal motors at a fraction of the price. Three are being bought and measured.

**Do not expect height from this, and here is why.** The as-built stack (section 8.3) already says it: the seat sits at 26.0 because **the display adapter's HDMI socket reaches 23.68**, and that is *"the deciding part"*. The wheels alone would allow 24.2. The motor's own stack allows 23.4–24.2. So the motor is **1.8 mm below the binding constraint**, and a shorter motor buys nothing until the adapter's socket is dealt with — which is question 19, flipping the adapter, worth +0.6 rather than +1.8. Height comes from the adapter first and the wheels second. The motor is third in that queue.

**What a different motor genuinely changes, and what the model should be ready for:**

1. **The bell diameter, and with it the drive ratio.** Today it is 4.14 : 1 from the bore at r 72.5 to the bell. A generic motor with a different bell changes that ratio and may change the motor centre from r 55.0. **Carry the bell diameter and the motor centre as parameters** rather than constants, so a measured motor drops in without a rebuild.
2. **Plate area in the motor sector**, if the frame or the bell is smaller. That is lateral room, not vertical.
3. **The carriage and its 2.4 mm travel**, if the mounting pattern differs. The carriage is a printed part and can follow.

**What the model should report back:** with the bell as a parameter, how much lateral room in the motor sector is freed per millimetre of bell diameter, and what the drive ratio becomes across a plausible range. That tells us what to look for when the three motors are measured, rather than measuring first and asking afterwards.

## 5. The clutch servo is not committed to the AGFRC part (Ryan, 7 September)

**Decision: the AGFRC C1.5CLS PRO is not the chosen part.** It is £47 and is a premium badge on a commodity class of 1.5 gram linear servos — the Spektrum SPMAS2000 is £11.95 and Hobbypower and Flash Hobby generics go lower again. Three are being bought and measured.

**This matters to the model because the servo frame is dimensioned to one specific part.** The floorless frame on the plate — walls 1.0, 6.5 tall, two ears at t ±12.5 for M2.5 into the web, a lead notch in its end wall — was drawn around the AGFRC's 21.4 × 15.2 × 6.0 envelope, and the carriage's 3 × 10 × 14.5 push tab meets its pushrod at one particular height.

**What the CAD session should do:** carry the servo's envelope and its pushrod height as parameters, and report the clearance the frame currently has in each direction. A part 2 mm longer or 1 mm taller should be a number change, not a redraw. The mechanism needs **2.4 mm of travel** and every servo in this class delivers 7–9 mm, so travel is not the risk; envelope and pushrod position are.

Also note for the record: the **2.4 N force figure has never been measured** — it is the AGFRC's published output, not a requirement the clutch was ever tested against. Nothing in the model should be built as though 2.4 N is a specification.

## 6. Three sourcing exercises are running that may change board envelopes (7 September)

**Not a change to make — a reason not to tighten around the current numbers.** Three handoff prompts have gone out asking whether bought boards can replace the custom ones: `MOTION-BOARD-SOURCING-PROMPT.md`, `SMALL-PARTS-SOURCING-PROMPT.md`, and `CARRIER-BOARD-SOURCING-PROMPT.md` (that last one is parked — it is production-only). The premise across all three is **one working prototype, and buy convenience over elegance**.

The likely consequence for the model is that **some board envelopes grow**. The motion board is budgeted at 30 × 30 × 3.6 on the blower's saddle; almost any bought development board is bigger than that. The six small boards — light sensor, USB-C carrier, jack carrier, actuator contacts, rotor sensor, knob encoder — may each become a bought breakout with its own dimensions rather than a board drawn to fit.

**What the CAD session should do now:** nothing structural. But when a choice arises between two arrangements, prefer the one with slack in the rear sector and on the port face, and **report how much room could be freed in each if asked** — how far the motion board's envelope could grow before something collides, and what the port face could hold. When the sourcing answers land, that number is what decides whether a bought board is acceptable or whether the mechanical design has to move. Ryan's stated position is that he would sooner re-cut the mechanical design than commission a circuit board.

---

## What does not change

So the model is not over-corrected: the plate's ducted construction with the blower on its +y side, the fin channels' direction, the ring's groove and openings, the boards mounting to the plate (the motion board on the blower's saddle), the stainless ring, the pad as a plain ring, the structure's inverted print, and every dimension in `THERMAL-PLAN.md` section 14 as rewritten for v15 all stand as built.
