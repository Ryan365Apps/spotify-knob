# the 60 — bench prototype enclosure (P1) — brief for the CAD session

## What this is

Build a NEW, SEPARATE model called **P1**. It is not v17 and it is not part of the v16 line. Do not modify, renumber or supersede any v16 file. v16 remains the mechanical authority for the product; P1 is a disposable test fixture that exists so software, touchpad work and bezel mechanics can proceed on real hardware while the production display and carrier decisions are still open.

P1 will be thrown away. Judge every decision by "does this let Ryan develop and feel the bezel, and run the display and touch software" — not by whether it could be manufactured.

## What changed

The production design assumes a bare DisplayModule DM-TFTR50-413 panel driven by the DisplayModule HDMI-to-DSI adapter kit. The prototype instead uses hardware that has arrived and is working:

- **Waveshare 5 inch round 1080x1080 HDMI touch display.** Module 150 x 150 x 7 mm, active circle 127.6 mm, 10-point capacitive touch on toughened glass. Its driver board is bolted to the back of the panel and carries a full-size HDMI socket, a 5 V power input, a touch port, an earphone jack, a backlight on/off button and a speaker header.
- **Raspberry Pi 5 (2 GB)** with the official Active Cooler fitted, powered by the official 27 W USB-C supply.
- **The Pi bolts directly to the Waveshare driver board** — the board's hole pattern aligns with the Pi's own mounting points.
- The kit's two small USB-to-Type-C adapter boards connect the display's power and touch straight into the Pi's USB-A ports, and an HDMI adapter joins the Pi's micro-HDMI to the board's HDMI socket.

Measured **33.3 mm** from the front face of the glass to the rearmost point, with the Pi mounted to the driver board. Verify it against the parts in hand before building.

Treat panel + driver board + Pi + adapters as **one bought sub-assembly with a single measured envelope**. Model it as one block. Do not separate or reposition its parts.

## How the extra height is absorbed — this is the governing rule

The stack is far deeper than the production layout, and **all of that extra height is taken in the base plate**. Everything from the seat upward is v16 geometry, unchanged.

- The base plate becomes a deep printed tub that carries the whole electronics stack.
- Its height is a **single named parameter**, and there are **printed riser rings** so the height can be changed without reprinting the plate. Ryan wants to adjust the seat height relative to the bezel during bring-up.
- The bezel, the knob and the V-wheel mechanism must not move, change or be re-derived to save height. If something does not fit, make the plate deeper.

## Carry over unchanged

Everything the bezel's feel depends on must be identical to v16, or the prototype teaches nothing that transfers:

- Knob Ø185.4, 25 mm flat rim, one piece, knurled, wide top chamfer, fitted 2.4 mm off-centre toward az 90 and slid home, wall stepping inward 2.0 above the halo ledge on a 50 degree ramp
- Bore male V-ridge and the V623ZZ-class V-groove bearings on Ø3 dowels; two fixed posts at 30 and 150 degrees; the sprung block at 270 in its printed channel with the Ø4 x 16 spring at 4 N, roof and pin slot as stops, and the captive M2 x 18 release screw wound from the centre and reached with an L-key through the display opening
- The KIMISS 2204 260KV gimbal motor with the printed drive collar, ID 35 / OD 39.4 on the bell's top 3.5 mm, bell stopping at r 86.0
- The AEDR-8300 encoder facing up at the code ring recess in the crown's underside at r 72.5-79.5 across a 2.0 mm gap, on a separate spacer that sets its height
- The FH-1502 linear servo clutch and its carriage
- The halo channel geometry at r 84.8-86.4 and the diffuser's vertical outer face at r 89.7 — **keep the geometry** even though no strip or diffuser need be fitted, so the knob and wall profile stay identical to v16

## Delete in the prototype

- **All audio:** audio board, speaker, speaker pillar and box, microphone, 3.5 mm jack, and the structure's acoustic port slits. The Waveshare board's own earphone jack and speaker header are not to be used or brought out.
- **All product power:** the 12 V barrel inlet, the Pololu D24V90F5 converter and the internal 5 V distribution. P1 is powered solely by the Pi's own 27 W USB-C supply, and the display takes its 5 V from a Pi USB port.
- The DisplayModule panel, its HDMI-to-DSI adapter kit, the flat cable, the display connect board and its bracket.
- The carrier board, the USB hub, the light sensor and any compute-module provision.

## Delete if you need too or alter as much as needed

- **All thermal machinery:** the aluminium base plate section, fin channels, duct, blower and its hood, the stainless rim ring, every intake and exhaust opening, the gasket and the rubber pad ring.

## Make room for, but do not optimise

The motion electronics are needed later for bezel feel work, so provide simple space and printed mounts in the deep plate, placed wherever is easy:

- A Raspberry Pi Pico with headers fitted
- The TMC6300 motor driver breakout
- The DRV2605L haptic driver breakout
- The 74AHCT125 level shifter
- The encoder and its spacer

A flat printed shelf with generic slots or clips is fine. They should be reachable and removable by hand. Do not spend effort on their arrangement.

## Constraints

- **Height is unconstrained**, and is absorbed in the plate per the rule above. Report the resulting height but never trade bezel fidelity for it.
- **Radial clearance:** the Waveshare module is Ø150, so the structure must clear r 75 — about 3 mm more than the DisplayModule panel's r 72.05. Check this against the halo channel at r 84.8 and report the margin.
- **Everything printed.** PETG, 0.4 mm nozzle, 0.2 mm layer, minimum wall 1.6 mm, no-support geometry where possible, chamfered mating edges, M2.5 heat-set inserts where threads are needed.
- **The Active Cooler stays fitted and its fan must breathe.** Leave the rear and underside substantially open. This is not thermal design — just don't suffocate it.
- **The Pi's ports must be reachable from outside:** USB-C power, both micro-HDMI, all four USB-A and Ethernet. A single large rear opening is the expected answer.
- **Room for the cabling as assembled:** the HDMI loop between the Pi's micro-HDMI and the driver board's HDMI socket, and the two USB adapter boards. Measure these as fitted rather than assuming.
- **Assembly must be reversible by hand** with common tools. It will be taken apart repeatedly.

## Explicit non-goals

Do not optimise for height, mass, thermal performance, acoustics, dust ingress, electromagnetic shielding, grounding, rear appearance or manufacturability. Do not carry over the grounding scheme, the connector standard or the design-changes working list — none of them apply to P1.

## Deliverables

- The model built the same way as the v16 line: parametric source, STEP assembly and parts, and a checker run reporting zero failures
- A short `P1.md` describing what was built and how it goes together
- A `P1-QUESTIONS.md` listing every assumption made and every dimension guessed rather than measured
- Delivered to `docs/proto1`, leaving all v16 files untouched

## Report back

1. The stack envelope as measured against the parts, and whether 33.3 mm held
2. The finished overall height, what the plate parameter is set to, and the range the riser rings give
3. The radial margin between the Ø150 module and the halo channel
4. Anything in the carry-over list that could not be built as written against this stack — said plainly rather than worked around
5. What in P1 would **not** transfer to the production design, so nothing learned here is trusted further than it should be
