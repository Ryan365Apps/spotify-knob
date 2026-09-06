# the 60 — design changes for the CAD session

**Working list, edited in place.** Changes decided outside the CAD session that the model has to absorb. **Delete an item once it is built.** This file is not a history — if it is empty, the model is current.

Last edited 6 September 2026, against **v14** as the current mechanical authority. Source documents: `docs/GROUNDING.md`, `docs/CONNECTORS.md`, `docs/HALO-BRIGHTNESS.md`, `docs/THERMAL-PLAN.md`, `docs/SYSTEM-REVIEW.md`.

Where this file names a section number it means **the current specification**, whichever version that is — the numbering has been stable across v10 to v14.

Built in v14 and removed from this list: the Pico-Lock connector allowance (2.0 mm on every board, 4.0 at the two moulded USB plugs); anodising of external faces only, no masked pads; the chassis bond, the rim ring's dedicated bond screw, the motor frame's bond lead, the knob's 1 MΩ bleed contact and its mounting, the USB-C shell wire, the port face stated as an insulator; the halo current computed from the strip as built (2.54 A) with section 4.8 and the bench item corrected; the engine turning removed and the intake opened to 514 mm² with the vent openings parametric; the vibration actuator's pogo-pin board and clip; the rotor sensor lead's notch, route and service loop.

---

## 1. Rim edge decoration — choose the treatment, then build it

The edge face is **plain** in v14 and stays plain until the replacement for the engine turning is chosen. The vent openings are parametric (`INTAKE_N`, `INTAKE_W`, `INTAKE_H`, `INTAKE_AZ0/AZ1`, `INTAKE_UNDERCUT_H`, `EXHAUST_AZ`) so the treatment can be swapped in without a rebuild. The intake requirement (500–700 mm² over the front and sides, exhaust at the rear downward through the pad voids) is met as built and must survive the treatment.

## 2. The steel rim ring's finish

Open (`docs/GROUNDING.md` 4.1). It decides whether the ring's bond-screw spot at az 56.25 is masked or the star washer is relied on to cut through. Once decided, add the drawing note to the rim ring's sheet.

## 3. Converter rating

The 10 A figure came from the old halo number. Size the module from the measured inlet load (bench item) — the halo's 2.54 A no longer justifies 10 A on its own. The envelope (38 × 25 × 8) stays until a part is chosen; if the chosen part is larger, the front crescent at az 180 has r 53–78 and t ±19 to give.

## 4. Assumptions the v14 model made that a real part must confirm

Not decisions — things the model had to guess to build the items above, each tagged ASSUMED in the parameter block:

- The bleed leaf: 4 wide, 0.2 thick phosphor bronze, bearing at r 71.5; its drag must not be felt.
- The LRA's pogo-pin board (7 × 8 × 1) and pins (Ø1.5, 2.2 compressed) against the flex tail's pads at z 11.75 and 14.35.
- The rotor sensor lead: flex-rated for 10⁵ cycles at 2.4 mm; its notch in the carriage shoe (2.4 × 2.2) and beside the plate's tab slot (2.5 × 4).
- The USB-C shell wire's route under the connect bracket's slab (a 1.5 mm gap).

---

## What does not change

So the model is not over-corrected: the plate's ducted construction, the fin channels, the intake undercut principle, the blower envelope reserved and unfitted, the boards mounting to the plate, the steel rim ring, the pad as a ring, and every dimension in `THERMAL-PLAN.md` section 14 all stand as built.
