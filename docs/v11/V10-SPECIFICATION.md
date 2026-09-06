# the 60 — version 10 specification

**Status: agreed specification — the baseline for the v10 CAD.** This document describes every component and mechanism the v10 model contains, says which numbers are measured and which are assumed, grades every requirement, and separates what is true of v10 only from what carries to production.

Revision: 5 September 2026, evening — every default in `V10-QUESTIONS.md` approved by Ryan, plus one correction (glue is allowed for securing the display); the v10 CAD was built from this text the same day (`docs/v10/the60_v10.zip`, `V10.md`) and the nine build-time changes recorded in `V10.md` are folded in here. Superseded text has been removed, not struck through. Written from the v10 brief, `V9-SPECIFICATION.md` (the agreed v9 baseline), `CURRENT-MECHANICAL-DESIGN.md`, `CLAUDE.md`, the electronics build-path notes, and the vendor files measured for this revision (section 0).

Tags, as in v9:

- **MEASURED** — taken from a CAD file by measuring it.
- **PUBLISHED** — stated by the manufacturer but not modelled here.
- **ASSUMED** — a number somebody chose. Reasonable or not, it is unverified.
- **GAP** — something the design needs that nothing currently provides.
- **v10-ONLY** — true of the desk prototype, not of the product. **PRODUCTION** — carries to the product.
- **MUST / SHOULD / COULD** — as v9.

---

## 0. What was measured for v10, and the three findings that shape it

New vendor files, now in `design/cad/bought-parts/vendor/`: the DisplayModule DM-TFTR50-413 panel STEP and datasheet, the Raspberry Pi 5 STEP and mechanical drawing, the Raspberry Pi Active Cooler product brief, the Raspberry Pi Compute Module 5 datasheet. Parts still **without a CAD body** (Ryan's rule: nothing is laid out around a part without one): the Active Cooler, the DisplayModule HDMI-to-DSI adapter board, the barrel jack, the internal HDMI ribbon cable and its plugs, the 12 V-to-5 V converter board, the cover lens, and the three boards the 60 makes (audio, motion, power). Each is drawn as a named `_ENVELOPE` body until its file exists.

**Finding 1 — the panel is not a circle, and that sets the diameter.** The DM-TFTR50-413 glass is a Ø132.2 disc with a **driver chin** at one edge: a 31.0 mm wide flat extension whose corners sit at **r 72.05 from the picture centre** (MEASURED from the STEP: the outline's furthest points are (±15.52, −70.36)). The knob rotates around the fixed panel, so the knob's bore must clear r 72.05 at every angle. With 0.45 mm clearance the bore is **Ø145.0**, and with the v9 knob wall of 4.5 mm (1.0 knurl + 3.5 under the root) the knob is **Ø154.0, not Ø150**. The only way to Ø150 is a 2.25 mm wall at the chin's height, which means an internal undercut groove in the knob and a sideways-shift insertion of the panel; it is described in `V10-QUESTIONS.md` question 1 and not recommended. **This specification is written for Ø154.** The top ring (question 2, drawing `v10_top_ring.png`) is 12.8 mm of metal, 13.5 mm from the picture edge to the knob edge (v9: 18.7).

**Finding 2 — the Pi 5 does not fit on the floor with the display adapter.** Inside a Ø145 bore the usable floor is about r 70.5 (15,600 mm²). The Pi 5 is 85 × 56 with a 3.1 mm socket overhang (MEASURED), the DisplayModule adapter is 65 × 64 (PUBLISHED), and the motor's carriage-and-servo sector needs r 27 to r 72.5 at one azimuth. Those three cannot share one floor in a Ø141 circle (worked in section 8.2), so v10 has **two levels**: the Pi, the motor mechanism, the speaker, the power converter and the rear sockets on the floor; the display adapter, the audio board and the motion board on a **mezzanine deck** above them, under the panel. That deck, not the cooler, is what sets the v10 height — and the deck is where the cooler's fan and the adapter collide (finding 3).

**Finding 3 — deleting the cooler does not buy height, standing the Pi on the pad does; and the fan cannot share the deck with the adapter.** The Pi's tallest features are its stacked USB-A sockets at 16.2 mm above the board (MEASURED), and the cooler's top is at 16.5 mm (13.70 PUBLISHED for the cooler on a heatsink base that sits about 2.8 above the board, ASSUMED). Fan up or fan deleted, the Pi is 19 mm thick. What removes height is standing the Pi on the rubber pad **through a window in the steel plate**, exactly as the v9 carriage stands through its hole — the plate has no shape requirement, only heft. With the cooler's heatsink kept and the Pi through the plate (option A″ in section 8.4) v10 is **40.3 mm** tall; with the cooler deleted and the SoC (the system-on-chip — the processor) conducting into the plate through a machined boss (option B) it is about the same. **The cooler's fan is not fitted** (built 5 Sep): its 34 × 34 intake hole in the deck and the 65 × 64 adapter cannot both exist — the fan sits 15 mm from the Pi's centre and the adapter's centre must be within 24 mm of the axis to fit the deck, so every legal adapter position covers the hole. v10 therefore runs the Pi on the cooler's heatsink alone, passively, and the first print measures whether that holds at ~4 W (section 6.9). Production uses B's principle with the Compute Module (section 8.5, **≈ 34 mm**).

---

## 1. What v10 is for

v10 is a printable object that lives on Ryan's desk while the software is written. It must hold the real DM-TFTR50-413 panel, a real Raspberry Pi 5 with its Active Cooler, the real knob mechanism from v9 (MY-3514C motor on its carriage, three 623ZZ wheels, AGFRC servo, AEDR-8300 encoder, LRA (linear resonant actuator, the click motor), speaker, halo), plug into a wall socket and into a PC by cable, and come apart again. It is not the product: the product runs a Compute Module 5 on a custom carrier, and every dimension that exists only to hold a full Pi 5, its cooler, the HDMI adapter and their cables is tagged v10-ONLY.

The first v10 print must prove (Ryan, brief): every part fits; everything can be secured; the knob turns; the Pi's heat has somewhere to go; the cables reach without fouling the mechanism.

---

## 2. Frame of reference and standing rules

**Coordinates.** Millimetres. **z** is height above the underside of the steel base plate; the rubber pad is below zero. **r** is radius from the picture centre. Azimuth is anticlockwise seen from above; **0° is the rear centre of the base, where the three sockets are, facing away from the user.**

**Standing rules carried from v9 unchanged:** the knob clears every static part by at least 0.40; running clearances 0.30; static fits 0.15; minimum printed wall 1.6; no overhang beyond 45° on a functional surface; M3 heat-set inserts; no glue but the pad; everything re-openable; connectors, never solder, between assemblies; every dimension in one parameter block, every number tagged; every check automated; the checker proves the assembly order. The part determines the design: nothing is laid out around a part that has no CAD body.

**Withdrawn by the v10 brief:** the 40 mm height limit (height is derived, section 8); the Ø135 diameter limit; the halo brightness cap.

---

## 3. The object — requirements in force

| Requirement | Value | Grade | Origin |
|---|---|---|---|
| Diameter | derived from the panel and the knob wall: **Ø154** knob, Ø153 plate (section 4.1, finding 1); Ø150 was the nominal and is not reached | MUST (derived) | brief |
| Height | derived: **40.3** v10 with the pad; **≈ 34** production with the CM5; the stack and what each part costs are in section 8 | report | brief |
| Mass | more is better; **8 mm** steel plate proposed (0.70 kg net after its cut-outs; 1.16 kg before) — see 4.16 for why 8 and not 5 | SHOULD | brief; 4.16 |
| Knob | one piece, no seam or screw; the majority of the visible side (v10: 69 % with the 8 mm plate); diamond knurl; wide smooth 45° chamfer at the top outer edge; small smooth chamfer at the lens; touches nothing but its three wheels, never the display | MUST | brief; v9 |
| Top ring | the metal between the picture edge and the knob edge narrows to **13.5 mm** (12.8 of metal: 9.3 flat, 2.5 outer chamfer, 1.0 inner chamfer) at Ø154; shown in `v10_top_ring.png` before commitment | SHOULD (approve the drawing) | brief |
| Display | DM-TFTR50-413 bare panel, picture Ø127.0, behind a round cover lens carrying a bonded 10-point capacitive sensor, specified separately (4.2, 4.3) | MUST | brief |
| Computer | v10: Raspberry Pi 5 + the Active Cooler's heatsink (fan off, finding 3), powered through its 5 V header pins, its USB-C free for the PC. Production: Compute Module 5 on a custom carrier | MUST | brief |
| Sockets | three openings in the base wall at the rear, at plate level, below the halo: **12 V barrel inlet, USB-C data to the PC, 3.5 mm line out**; plug bodies drawn, not just sockets (section 6.8) | MUST | brief |
| Audio | own board (XMOS + converter, ~25 × 40); 3.5 mm is line out to powered speakers, no amplifier; speaker carried from v9 | MUST | brief |
| Motion | motor, encoder, LRA, servo and LED ring on their own microcontroller board (size proposed in 4.13) | MUST | brief |
| Halo | full 360°, on the fixed base, its bottom edge the plate edge; LEDs driven hard — see 4.9 for what that costs in watts | MUST | v9; brief |
| Perimeter port ring | stays; must also vent the computer's heat — adequacy in 6.9 | MUST (acoustic) / SHOULD (vent) | brief |
| Power | dedicated mains supply, external brick; proposal in 6.8 | MUST | brief |
| Assembly | upside down, knob → display → structure → plate → pad; no glue but the pad and the display's bonding tape (Ryan, 5 Sep); re-openable; connectors not solder | MUST | brief |
| Bench display | the Waveshare 5-inch HDMI round touch display (150 × 150 × 7) stays on the bench, not enclosed | — | brief |

---

## 4. Bought components

One entry per part: the body, where it sits, what the made parts must provide, gaps. Parts carried from v9 unchanged are listed with only what changes.

### 4.1 DisplayModule DM-TFTR50-413 — the panel (PRODUCTION)

Body: `vendor/DM-TFTR50-413.STEP`, MEASURED: a 1.98 mm glass, Ø132.2 disc, active picture Ø127.0 centred, borders 2.6 at the sides, 2.67 at the top; **driver chin** at the bottom: 31.0 wide flat at r 70.36, corners at r 72.05; **FPC tab** at the top: the outline is 20.0 wide there, and the flexible printed circuit (13.99 wide, 0.15 thick, PUBLISHED from the drawing) runs from the back-side component area up the back of the glass, over the top edge, and 45.84 mm beyond the outline to a 45-way 0.3 mm pitch gold-finger end with a 4.28 mm stiffener. Small 5 mm locating ears at the two side extremes of the horizontal centreline. Back-side component area 60.0 × 68.4, components up to **1.5 mm** proud of the glass back (PUBLISHED, drawing). Weight 70 g. No mounting holes; no touch. Controller HX8399-C, 4-lane MIPI-DSI (a serial display interface with four data lanes), 1.8 V logic, ±5 V analogue rails, backlight 12 white LEDs in series at 37.2 V, 20 mA (0.75 W) — all PUBLISHED.

Where it sits: glass back at **z 31.3** (section 8), picture centre on the axis, the chin at **180°** (toward the user, under the knob wall — invisible) and the FPC tab at **0°** (rear), ASSUMED, so the flex reaches the adapter over the rear crescent. Picture orientation is software.

What the made parts must provide:

| Provision | So what | Grade |
|---|---|---|
| A **seat** on top of the structure wall (r 62–72.1, top face z 30.4) that the display module **bonds to** with a 0.5 mm double-sided foam tape (ASSUMED) under the glass edge at r 62.5–65.6 — the glass never rests on a hard edge; the module comes off by peeling the tape | the panel has no holes; the knob must not hold it; glue is allowed for the display (Ryan, 5 Sep). A screwed carrier ring was designed and dropped: under the glass it can only be 1.5 mm thick and outside the glass the wall is 0.2 mm away, so it has nowhere for threads | MUST |
| A **32 × 2.5 mm slot** through the seat at 0° (offset 4 mm) for the panel flex and the touch tail, edges radiused 1.0 | the flex runs out past the glass edge and drops through here to the adapter | MUST |
| Centring: three Ø2 nubs on the seat at 60/210/330° locate the Ø132.2 glass to ±0.15, under the lens overhang | the picture must be concentric with the knob within the 0.7 mm the lip hides | MUST |
| The knob's bore clears the chin corners by 0.45 (Ø145.0) | finding 1 | MUST |

**Gaps:** the exact chin outline is the STEP's; the datasheet's 66.10 dimension at the bottom does not match the STEP's 31.04 flat — the STEP is used, verify on the real glass (GAP). Whether the panel can be bought bare in ones (Ryan's question — see 4.4 for the fallback).

### 4.2 Cover lens with bonded touch sensor — specified separately (PRODUCTION)

**No CAD body. ASSUMED throughout:** round, **Ø140.0**, 2.5 mm thick, black-printed border from the picture edge outward, bonded to the panel's front face by its supplier (a perimeter adhesive gasket or full optical bonding — that bonding is part of a bought sub-assembly, not glue in the 60's assembly). The touch sensor's tail is a second FPC, ASSUMED 8 mm wide, exiting at the same edge as the panel's tab. The lens overhangs the Ø132.2 glass by 3.9 all round except at the chin, which stays exposed.

Why Ø140 and not 135: the seat's locating nubs sit under the lens overhang, and The lip hides everything outside Ø128.4, so the lens border (r 64.2 to 70) is invisible. Range acceptable: Ø135 to Ø140.5 (the structure wall's inner face is r 70.5).

**Gaps:** every number above. The lens is a question for its supplier; this specification only fixes what the knob and the structure need from it: outside diameter, thickness, border width, tail position.

### 4.3 DisplayModule HDMI-to-DSI adapter DM-ADTTR-014 (v10-ONLY)

**No CAD body.** PUBLISHED: 65.0 × 64.0 mm board, HDMI type-A socket in, 4-lane DSI out, 4.5–5.5 V supply. ASSUMED: 1.6 board, 6.5 mm socket height, 2 mm of other components, mounting holes M2.5 at the corners, current 0.6 A including the backlight driver. Where: on the mezzanine deck centred at (4, −26) — over the Pi's USB-C half — its +x edge carrying the panel flex connector (30 mm from the seat slot at 0°) and its −x edge the HDMI socket, facing the ribbon that rises from the Pi's HDMI0 (ASSUMED positions; the adapter's drawing decides). Provision: four M2.5 heat-set bosses on the deck; the touch controller board stacks on its outer region on 2 mm standoffs (there is no deck area left for it). **Gap:** the adapter's panel connector must accept this panel's 45-way 0.3 mm flex directly or via a supplied bridge flex — confirm with DisplayModule before ordering (GAP; the brief's 60-pin note does not match a 45-way panel). The adapter route gives no touch; touch in v10 comes from the lens's own USB sensor controller (ASSUMED a small board, 4.12).

### 4.4 If the bare panel cannot be bought

State it plainly rather than enlarge the object: v10 is built with a **dummy display disc** — a printed Ø132.2 × 1.98 plate with the same chin and FPC tab (from the STEP) and a Ø140 × 2.5 clear acrylic lens — so every mechanical proof in section 7 still happens, and software runs on the Waveshare bench display. The dummy is one line in the parameter block. Nothing else changes.

### 4.5 Raspberry Pi 5 (v10-ONLY)

Body: `vendor/rpi5/rpi-5b_no_graphics.step`, MEASURED: board 85 × 56 × 1.28; four Ø2.7 holes at (3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5); two stacked USB-A pairs 16.2 above the board top at x 70–88 (overhanging the board edge by 3.1); Ethernet 13.3; SoC 16.9 × 16.9 at x 24.7–41.6, y 14.3–31.2, top 2.34 above the board; USB-C at x 6.7–15.7 on the y = 0 edge, 3.29 tall; two micro-HDMI on the same edge; 40-pin header along y 50–55, x 7–58, 8.5 tall; micro-SD slot 1.45 below the board. Where: on the floor, long axis along 0°–180°, USB-A/Ethernet end toward **the rear (0°)** — the port slot starts at r 55, 9 mm clear of the socket stacks — USB-C/HDMI edge toward **270°** beside the speaker, header edge toward 90° (the motor side), **standing on the pad through a window in the plate** (4.16), board top at z 2.78. The other orientations put the HDMI and USB-C plugs inside the plate or under the carriage (V10.md change 4).

Provisions: the plate window (with notches for the USB-C plug, the HDMI plug and the rear USB-A plug); three M2.5 heat-set inserts in the underside of the mezzanine deck's legs (4.14) — the Pi hangs from the deck by three of its four holes (the USB-A-corner hole is under the speaker), its underside 1.5 above the pad; a 2 × 3 crimp housing on header pins 2/4 (5 V) and 6 (GND) plus the UART (a plain two-wire serial link) pins for the motion board (4.13); the internal USB-C cable to its USB-C socket (6.8); the HDMI ribbon from its HDMI0 socket (4.15); the audio board's USB in the upper rear USB-A socket through a right-angle plug (ASSUMED 9 mm protrusion). **Gap:** feeding 5 V on the header while the PC's USB-C is plugged in parallels two 5 V sources — see question 6 (VBUS (the USB cable's 5 V wire) cut in the internal cable, or an ideal-diode on the header feed).

### 4.6 Raspberry Pi Active Cooler — heatsink fitted, fan not (v10-ONLY)

**No CAD body.** PUBLISHED (product brief, verified this revision): 63.50 × 42.50 footprint, **13.70 total height** from the heatsink's underside to the fan's top, fan 30 × 30, 1.09 CFM (cubic feet per minute) (0.51 L/s) maximum, 8000 rpm, temperature-controlled from the Pi's fan header, push-pin mounted, not designed for removal. The brief's "30" that read as a height is the fan's footprint. ASSUMED: the heatsink underside sits 2.8 above the board (SoC 2.34 plus pad); the fins' top 7.0 above that (ASSUMED split of the 13.7) = **z 12.6**; the footprint from Pi x 2.5 to 66, between the USB-C edge region and the USB-A shells. **v10 fits the heatsink and leaves the fan off** (finding 3): the deck sits 6.9 mm above the fins with both long sides open; the SoC cools by the fins into the cavity. Adequacy: 6.9 and V10.md bench item 1.

### 4.7 Motor, carriage, servo, wheels, encoder, LRA, speaker — carried from v9

MY-3514C on its 4.2 mm carriage through the plate (stack case B, unchanged: motor z 4.2–18.2, bell from z 8.5 ASSUMED); AGFRC servo pushing the carriage, 2.4 mm lift; three 623ZZ V-collars on eccentric bushes; AEDR-8300 on a 0.15 recessed code strip; Vybronics LRA; Soberton SP-4005-1 cone-up; TMC6300 and MT6701 in the carriage. What changes with the bore at r 72.5:

| Item | v9 | v10 |
|---|---|---|
| Motor centre, engaged | r 40.5 | **r 55.0**; released r 52.6 |
| Drive ratio (bore Ø / bell Ø) | 3.31 : 1 | **4.14 : 1** — 60 knob detents are 14.5 per motor turn, not a whole number, so the detent is rendered from the knob's encoder, as v9 already intends |
| Motor azimuth | 90° | 90°; **the servo lies on the mezzanine deck** at r 8–30 (over the Pi) and pushes a **3 × 10 mm tab that rises 28 mm from the carriage** through a slot in the deck — with the Pi filling the floor there is no floor position for the servo in any azimuth (V10.md change 3); same 2.4 mm lift, same 2.4 N |
| Wheel centres | r 51.7 | **r 67.1**, azimuths **30 / 150 / 270**; the wall gets three 15 × 5.4 windows so the wheels reach through it into the groove |
| Wheels z | 23.4–27.4 | **23.9–27.9**, groove 24.3–27.5, collar tops 0.5 under the seat flange |
| Code band | 18.4–22.6 | **18.5–22.7** on the bore, encoder tower at **310°** |
| Code strip | 364 mm | 455 mm — 5,700 lines per turn at the AEDR-8300's 0.08 mm pitch (PUBLISHED 318 lines per inch) |
| Speaker | floor at 180° | floor at **(17, −46)**, the 270° crescent beside the Pi's USB-C edge, cone-up, cradle carried with its ears on the tangential axis |
| LRA | 258° | 258°, on the structure at the wall |

### 4.8 Halo — 90 × SK6812SIDE-A on a flat flex on the plate top (PRODUCTION)

Carried: side-firing LEDs on a flat flex annulus on the plate, firing outward into the diffuser. v10 radius: LEDs at **r 74.3** (flex r 73.2–75.4), diffuser r 75.5–77.0 (1.5 thick at the bottom), halo z 8.0–10.6 on the 8 mm plate. The ring is 1.0 further out than first drawn because the motor's bell and band reach r 73.1 at the halo's height (V10.md change 6); bench-check that a 1.5 mm opal diffuser still hides the LEDs. At r 74.3 the 90 LEDs are on a 5.2 mm pitch (v9: 4.1); 112 would restore it — 90 ruled (question 12).

**Driven hard, in watts:** the datasheet (PUBLISHED, normandled SK6812 SIDE-A) rates 12 mA per colour, 0.2 W per LED: **90 LEDs at full white = 3.24 A, 16 W; 112 = 4.0 A, 20 W.** That is four times the Pi's heat and it lands on the plate's rim, which is the right place (the flex is taped flat to the steel with thermal tape — the tape is a bought part with its own adhesive, like the pad). Sustained full white is not a realistic duty; a colour at 30 % is 1–2 W. Section 6.9 uses 3 W sustained, 16 W peak.

### 4.9 Perimeter ports, port face, light sensor, USB-C receptacle, 3.5 mm jack, DAC (digital-to-analogue converter) — carried

Ports: 24 positions on a 15° grid through the wall at z 15, **Ø4**, of which 16 are cut (the motor sector, the port slot, the pillars, the encoder tower and the LRA take the rest): 201 mm², passive (6.9). GCT USB4520 mid-mount USB-C receptacle (CAD body exists) on its small board; Switchcraft 35RAPC4BH3 3.5 mm jack (CAD body exists); VEML7700 light sensor on its tiny board behind a Ø4.8 hole. The ES9219Q DAC moves from the jack board to the audio board (4.12); the jack board becomes a plain jack carrier.

### 4.10 Barrel power jack — CUI PJ-063AH (PRODUCTION, part proposed)

**No CAD body yet** (Same Sky offers one — fetch it before CAD). PUBLISHED: 2.0 mm centre pin (5.5 × 2.1 plug), **24 V 8 A** rated, right-angle through-hole. ASSUMED body 14.4 × 9.0 × 11.0, socket axis 6.5 above its board. Where: rear port slot, at 0° −15 mm tangential, on a small **vertical** board (tangential plane) so the barrel's axis height is free — axis at **z 3.5**, the plug body from z −0.75 to 7.75, under the halo's bottom edge (z 8.0) by 0.25 and into a through-pocket in the pad. Why a barrel and why 12 V: section 6.8. Plug body: a **right-angle 5.5 × 2.1 plug, Ø8.5 body** (ASSUMED) — a straight moulded plug on a 12 V brick is Ø10–11 and does not fit under an 8 mm plate's top edge; the cable leaves the object sideways along the rear wall.

### 4.11 12 V → 5 V converter board (PRODUCTION as a function; v10 as a bought module)

**No CAD body.** ASSUMED: a 5 V, 9–10 A step-down module 38 × 25 × **8** (the first draft said 10; 8 is what fits under the seat flange — pick the module to suit), on the mezzanine deck at az 175°, r 33–59. Feeds: the Pi's header (5 A peak), the halo (up to 4 A), the adapter, the audio and motion boards. The motor driver stays on 5 V (the TMC6300's PUBLISHED maximum is 11 V).

### 4.12 Audio board — XMOS USB audio + ES9219Q (PRODUCTION as a function)

**No CAD body.** Ryan's envelope: **25 × 40**; ASSUMED 6 mm tall from the deck including the board and a 4-pin connector, M2.5 corner holes. Where: on the mezzanine deck at az 110°, r 37.5–62.5 (radial 25, tangential 40). Connections: USB to one of the Pi's USB-A sockets (an internal USB-A-to-USB-C cable, ~120 mm, plug body 15 × 6.5 × 20 at the Pi's front end — drawn); line out to the 3.5 mm jack board (3-wire JST-SH); the speaker (2-wire, the XMOS drives a small class-D on this board — the speaker amplifier is the board's, the 3.5 mm output has none). The lens's touch controller board (if the sensor supplier gives one) stacks on the adapter's outer region on 2 mm standoffs, 4.12a: ASSUMED 30 × 20 × 3, USB to the Pi.

### 4.13 Motion board — microcontroller for motor, encoder, LRA, servo, LED ring (PRODUCTION as a function)

**No CAD body.** Envelope as built: **30 × 30 × 7.4** (the TMC6300 driver, a DRV2605L, the microcontroller, low-profile JST-SH connectors 5 mm tall on its motor-facing edge) — the first draft proposed 50 × 40, but the deck's free sector beside the servo is 30 × 30. Where: on the mezzanine deck at az 55°, r 30–60, so the four short cables (motor phases, commutation sensor in the carriage, servo, encoder tower) run a few centimetres. Talks to the Pi over **UART on the 40-pin header** through the same 2 × 5 housing that brings 5 V in — one plug, no internal USB cable for motion (ASSUMED; a USB alternative is question 9). The LED ring's data line comes from here; its 5 V comes from the converter directly (4 A does not go through a signal board).

### 4.14 Mezzanine deck (made part, v10-ONLY) — see 5.4.

### 4.15 Internal HDMI ribbon (v10-ONLY)

**No CAD body.** ASSUMED: a 20-way 0.5 mm pitch flat flexible HDMI cable, 200 mm, with a micro-HDMI **up-angle** plug board at the Pi end (12 × 8 × 5) and an HDMI-A plug board at the adapter end (21 × 12 × 6). Route as built: from the Pi's HDMI0 socket at z 2.8–7.8 on the 270° edge, 6.5 mm outward, a 90° fold upward (bend radius 2.0 — a 0.1 mm flex tolerates 1.0 static), through a 22 × 3 slot in the deck, a 90° fold onto the deck, 33 mm along −x under the adapter board (0.3 mm ribbon under a board on 0.8 mm bosses) to the HDMI-A plug in the adapter's −x-edge socket. A round moulded micro-HDMI cable needs a 25 mm bend radius and 12 mm plug bodies and does not route in this height; the ribbon is the design. Two folds, both static, both ≥ 2 mm radius, both modelled.

### 4.16 Base plate — steel (PRODUCTION)

Laser- or waterjet-cut mild steel, Ø153, **8 mm** (v9: 5), powder-coated, with: the Pi window 89.6 × 57.5 with three plug notches (v10-ONLY); the carriage stadium hole with its tab slot; the 44-wide rear port slot from r 55; three M3 countersunk holes at 120 / 240 / 320°, r 66.5; two M3 for the speaker cradle; a ground-bond hole; two Ø1.6 for the port face's ears. Mass: 1.16 kg solid, **0.66 kg** after the cut-outs (v9 plate 0.39 kg). Why 8: the plug bodies at the rear must sit between the pad's underside (z −1.5) and the halo's bottom edge (z = plate top), so the tallest plug body is plate + pad − 0.5: **6.0 mm on a 5 mm plate, 9.0 on 8 mm**. A USB-C plug is 6.5 tall, a 3.5 mm plug Ø6–8, a right-angle barrel Ø8.5. The 5 mm plate fits none of them cleanly; 8 fits all three, adds 0.4 kg the brief asked for, and halves the plate's spreading resistance for the heat path (6.9). Cost: the halo rises 3 mm (8.0–10.6), the knob's skirt starts at z 12.0 instead of 9.0, so the knob is 69 % of the side instead of 76 %; the overall height is unchanged because everything tall stands on the pad through the plate. Question 4.

### 4.17 Compute Module 5 (PRODUCTION only — not in v10)

PUBLISHED (datasheet, verified): 55 × 40, bare module 4.6 deep, PCB 1.24, SoC 2.2 tall, four M2.5 holes inset 3.5; mounted height 4.94 with the 1.5 mm Amphenol stacking connector or 7.44 with the 4.0 mm one; idle 0.4 A, load 0.9 A at 5 V; "less passive heat-sinking than a Pi 5 — any thermal solution must be designed". Section 8.5 uses it SoC-down on a plate boss with the 4.0 mm stacking.

### 4.18 Rubber pad, screws, inserts, cables, code strip, display bonding tape, LED thermal tape — carried; the pad and the display tape are the only adhesives (Ryan, 5 Sep).

---

## 5. Made components

### 5.1 Knob (PETG prototype; CNC 6082 production)

One piece. **Ø154.0** outside; bore **Ø145.0** straight from the skirt's bottom (z 12.0) to the lens level, with: the 90° V-groove for the wheels (root r 73.8, z 24.3–27.5); the 0.15 code-band recess (z 18.5–22.7); the lip on top: inner edge **Ø128.4** (0.7 outside the picture), 3.0 thick, underside at z 35.78, top at **z 38.78**; outer chamfer 2.5 at 45°, inner chamfer 1.0, skirt chamfer 1.2. Knurl: diamond, 1.0 deep, four whole rows between the lands as v9 (helix 33.0°, derived from the band height 14.0–35.9), **68 starts** at Ø154 to keep the v9 pitch (question 13). Wall under the knurl root 3.5. The knob touches only its three wheels: 0.4 to the lens and the structure, 0.45 to the chin.

### 5.2 Internal structure (printed; PA12 production)

One part, as v9: a wall r 70.5–72.1 from the plate top to the seat; the **seat flange** at the top (r 62–72.1, z 28.4–30.4) with the 32 × 2.5 flex slot at 0° and three Ø2 locating nubs at 60/210/330° — the display module bonds to it; three wheel posts Ø8 at r 66.2, az 30/150/270 (bush sockets open to the plate side), webbed to the wall, with a 15 × 5.4 window through the wall above each for the wheel; the encoder tower at 310° with its window through the wall; the LRA pad at 258°; the diffuser-retaining lip; **five Ø7 pillars at r 66.5, az 50/120/180/240/320**, webbed to the wall, with M3 inserts at the top for the deck's screws and, at 120/240/320, at the bottom for the plate's screws; 16 perimeter ports Ø4 at z 15; the motor relief at 90°; the wall's foot relieved over the port slot for the port face's ears. No ledge, no display columns, no seat tabs, no carrier.

### 5.3 Halo diffuser — carried; r 74.5–77.0, z 8.0–10.6, 0.5 chamfer on the outside top edge.

### 5.4 Mezzanine deck (v10-ONLY)

A flat printed plate Ø140, 1.5 thick, z 19.48–20.98, with: notches around the three wheel posts and the encoder tower; the 6 × 10.6 slot for the carriage's tab at 90°; the 22 × 3 ribbon slot beside the Pi's HDMI0; five Ø3.4 holes at the pillars. On its top: 0.8 mm M2.5 insert bosses for the adapter (4), the audio board (4), the motion board (4) and the servo tray (2). On its underside: three legs Ø5.5 down to the Pi's board top (16.7 tall) with M2.5 inserts — the Pi hangs from them. Print upside down, no supports.

### 5.5 Display seat (PRODUCTION) — the display module's interface to the structure

The seat flange of 5.2, with the bonding tape (4.1). No separate part. The display module (lens bonded to the panel by its supplier) is placed lens-down in the inverted knob and the structure is lowered onto it with the tape on its seat; the three nubs centre the glass. Cost in the stack: 0.5 mm of tape. Replacing the display means peeling it off the seat — acceptable for v10; production can revisit a clamp ring if a tool-free swap is wanted.

### 5.6 Carriage, servo tray, speaker cradle, port face, V-collars ×3, eccentric bushes ×3 — carried from v9 with the new radii. The carriage gains a 3 × 10 × 28 tall push tab (rooted to the shoe); the servo tray sits on the deck and takes 2 × M2.5; the port face grows to 44 wide for three sockets with its ears at t ±16 inside the wall.

### 5.7 SoC boss (option B only, and production)

Aluminium, Ø26, height from the plate top to 0.5 below the SoC's face (v10 option B: 5.4; production: set by the CM5 stack), two M3 countersunk from below the plate, a 0.5 mm thermal pad on top. Not in v10 as built (A″); it is the fallback if the fanless heatsink runs hot (V10.md bench item 1).

### 5.8 Boards — 4.10 (jack carrier), 4.11 (converter, bought), 4.12 (audio), 4.13 (motion), USB-C board, light-sensor board, encoder breakout, commutation board, LED flex — outlines exported as v9.

---

## 6. Mechanisms

### 6.1 Knob suspension, 6.2 detent and drive, 6.3 clutch, 6.4 angle sensing, 6.5 commutation — as v9 with the radii in 4.7. The drive ratio 4.14 : 1 raises the motor's speed for the self-turn and lowers the torque the knob feels by the same factor: a 2.4 N band grip at r 72.5 is 0.17 N·m at the knob (v9: 0.10) — better, not worse.

### 6.6 Display — how the panel is held and driven

Held: bonded to the structure's seat (4.1, 5.5), centred by the seat's nubs; the knob never touches any of it. Driven (v10): Pi HDMI0 → ribbon (4.15) → adapter (4.3) → the panel's 45-way flex, which runs on the glass back to the tab edge at 0°, out 1.8 mm past it, down through the seat slot to z 24.6 and inward 30 mm to the adapter's connector (bend radius 1.0, two static folds, total run 44 of the 45.8 mm available). Touch: the lens's sensor tail → its controller board on the deck → Pi USB. Production: the CM5 carrier's DSI output straight to the flex, ±5 V and the 37 V backlight driver on the carrier, no adapter, no HDMI — that carrier needs a Linux panel driver with the HX8399-C initialisation sequence from DisplayModule (a software task that must happen for production regardless; question 3 asks whether to do it now and skip the adapter, which would take the mezzanine out of v10 and about 2 mm off its height — the fan's intake plenum then sets the height, not the boards).

### 6.7 Audio — speaker on the audio board's amplifier; 3.5 mm line out unamplified; both on the audio board; the jack carrier at the rear is passive.

### 6.8 Power and the three rear openings

**Proposal: a 12 V, 5 A external brick into a 5.5 × 2.1 barrel jack, and a 5 V 10 A step-down inside. Preferred over a USB-C inlet feeding the Pi's 5 V pins.** Why:

1. The 5 V budget. Pi 5 up to 5 A (PUBLISHED supply rating; the board alone ~2.4 A under stress, ASSUMED), halo 3.2–4.0 A at full white (PUBLISHED per-LED), adapter + panel 0.6 A, motor up to 2 A through the TMC6300 (PUBLISHED driver limit), servo 0.5 A, audio 0.3 A: **8–10 A worst case, ~2 A typical**. A 5 V 5 A USB-C brick (the 27 W one Ryan has) cannot cover the worst case, and a barrel pin is rated 5 A at any voltage, so 5 V cannot come in through a barrel either. 12 V in at 5 A is 60 W and covers everything with margin.
2. Two USB-C sockets side by side at the rear invite the wrong cable in the wrong hole; a barrel is unambiguous. A USB-C power inlet at 12–20 V needs a power-delivery negotiator board and still needs the step-down; it saves nothing.
3. A 12 V rail is available for anything that wants it later; the TMC6300 motor driver is not one of them (PUBLISHED maximum 11 V), so the motor stays on 5 V as in v9.

The Pi is fed on header pins 2/4/6 from the converter (v10-ONLY; production feeds the CM5 carrier directly). The Pi's USB-C stays for the PC (USB gadget mode). **Gap:** the PC's 5 V on that USB-C parallels the header feed — question 6.

The three openings, in the 44 × 30 slot through the plate at the rear, left to right seen from behind, all with their plug bodies drawn: **barrel** at −14 mm (right-angle plug, Ø8.5 body, cable leaving sideways along the wall), **USB-C** at 0 (GCT receptacle on its horizontal board; plug body 8.3 wide × 6.5 tall × 25 long, cable straight back), **3.5 mm** at +12 (Switchcraft jack; plug Ø6–8, straight). Plug axes at z 3.5 (barrel), 4.5 (USB-C), 4.0 (jack). Every plug body must lie between the desk (z −1.5) and the halo's bottom edge (z 8.0) where it passes under the diffuser at r 74.5–77: the barrel body spans −0.75 to 7.75 and needs a **15 × 20 through-pocket in the pad** under it (the plug hangs 0.75 above the desk); the USB-C body 1.25–7.75; the jack body 0–8.0 with a Ø8 plug, comfortable with Ø6. On a 5 mm plate none of the three closes without a notch in the halo. Alternatives to the pad pocket: notch the halo over ±8° at the barrel, or a 10 mm plate (1.4 kg). Question 5.

### 6.9 Perimeter ports as the computer's vent — adequate or not

As built: 16 × Ø4 = 201 mm² of ports at z 15, passive; the cooler's fan is not fitted (finding 3), so the through-flow scheme below has no fan to serve and its baffle is not built. The Pi's SoC cools by the cooler's fins into the cavity, the cavity by the skin. The first print measures it (V10.md bench item 1); the fallback is option B.

The heat: Pi ~4 W (Ryan's figure; 12 W stress), adapter and panel ~3 W, halo 3 W sustained (16 W peak), audio and motion ~1 W: **~11 W sustained, ~25 W peak**.

Where it can go: the object's skin — knob side and top, plate rim, lens — is about 0.036 m². At 11 W/m²K (still air plus radiation, ASSUMED) that is **0.40 W/K: +10 K at 4 W, +27 K at 11 W, +60 K at 25 W**. The desk under the pad is a blanket, not a sink (wood, ~20 K/W). The v9 vent — 24 × Ø2 holes (75 mm²) behind a 0.4 mm annular gap (180 mm²) — moves air by buoyancy only and adds perhaps 0.02–0.05 W/K. **So: adequate for the Pi's ~4 W on its own; not adequate for the whole object at 11 W, where the skin runs ~50 °C in a 22 °C room and the knob is unpleasant; and no amount of hole-drilling changes that without a through-flow.** A fan would stir the cavity and drop the SoC-to-plate resistance from ~3.4 to ~1.5 K/W but exhaust into the same cavity it draws from; it would not change the skin figure. Without it (as built) the SoC-to-cavity path is the heatsink's fins in still air, ~3–4 K/W: at 4 W the SoC runs ~15 K above the cavity, the cavity ~10 K above the room — about 50 °C SoC at a 22 °C desk. Credible; measured on the print.

What a real vent would need if a fan is ever fitted (MUST for production if the product keeps a fan): an intake separate from the exhaust so the fan's 0.5 L/s passes through the object once — 0.5 L/s of air carries **0.6 W/K**, more than the whole skin. Path proposed: intake at the **rim gap** (the 0.4 mm ring between the lens and the lip, 176 mm²), down past the panel's edge and the deck's edge into the fan; exhaust through the perimeter ports, enlarged to **24 × Ø4 (300 mm²)** below the deck; a printed baffle so the lower and upper cavities connect only through the fan. Cost: dust at the panel edge; 8000 rpm audible at full speed. Alternative: relieve the pad with four radial channels and cut four Ø8 holes in the plate as the intake, exhaust at the ports — keeps dust off the panel, puts the intake on the desk. Question 10. The passive alternative is to accept the budget: cap the halo's sustained current in software and let the object run warm.

### 6.10 Assembly order (upside down) — every step reachable, proven by the checker

1. Knob upside down, lip down, the code strip already in its recess; a 0.4 shim ring on the lip.
2. Display module (lens + panel, bonded by its supplier) lens-down onto the shim, the chin at 180°, the flex tab at 0°. The Ø140 lens and the r 72.05 chin pass the Ø145 bore with 2.5 and 0.45 to spare — a straight drop, proven by the checker.
3. Internal structure, bonding tape on its seat, lowered over the panel's back with the wheels retracted; the flex and the touch tail led through the seat slot; the three nubs meet the glass edge; the seat pressed onto the glass — the display is now bonded. The structure enters the knob's bore from below on a straight path (checker).
4. Bushes half-turned from the plate side to seat the wheels in the groove; locked; shim out through the rim gap.
5. Encoder breakout into its tower, LRA onto its pad, diffuser into the structure's lip.
6. Mezzanine deck with its boards pre-fitted (adapter with the touch controller stacked on it, audio, motion, converter, servo in its tray); the panel flex plugged into the adapter and the touch tail into its controller; the deck lowered onto the five pillars, 5 × M3 from above (Ø6 driver paths proven clear).
7. Pi with the cooler's heatsink clipped on (fan off), hung from the deck's three legs with 3 × M2.5 driven from below; header housing on; ribbon from HDMI0 folded up through the deck slot and along under the adapter into its HDMI socket; internal USB-C cable into the Pi's USB-C; the audio board's right-angle USB-A plug into the upper rear USB-A socket.
8. Motor on its carriage, band on, carriage into its guide with its tab up through the deck slot to the servo's pushrod; motion-board cables plugged; speaker into its cradle at (17, −46); barrel-jack board, USB-C board, jack carrier and light-sensor board into the port face; port face into the slot; power leads to the converter.
9. Plate on — the LED flex already taped to its top face, its window around the Pi and its plugs, its hole around the carriage, its slot around the port face — 3 × M3 countersunk into the pillars at 120/240/320°, 2 × M3 speaker, ground bond.
10. Pad on (its pocket at the barrel). Turn over.

Nothing is glued but the pad, the display's bonding tape, the code strip and the LED flex's thermal tape (bought parts with their own adhesive). Everything reverses; the display by peeling.

---

## 7. What the first v10 print must prove

Every part fits — the panel (or its dummy), the Pi with the cooler's heatsink on the pad through the plate window, the deck with its four boards and the servo, the motor mechanism at the new radius, the speaker, the converter, the three sockets with their plugs in; everything can be secured — every screw in section 6.10 reachable with the named tool; the knob turns on its three wheels and touches nothing; the Pi's heat has somewhere to go — the SoC temperature is logged for an hour of real work on the fanless heatsink (throttling means option B); the cables reach — ribbon, panel flex, USB-C, USB-A, header housing, motion leads — without touching the carriage, the bell or the wheels at any knob angle. It does not need the knurl, the production diffuser grade, or a working clutch.

---

## 8. Diameter and height — derived, and what each part costs

### 8.1 Diameter

| Layer, from the axis outward | r | Why |
|---|---|---|
| Picture | 63.5 | panel |
| Lip inner edge | 64.2 | 0.7 hidden border, ASSUMED |
| Lens edge | 70.0 | ASSUMED Ø140 (135–140.5 allowed) |
| Structure wall | 70.5–72.1 | 1.6 printed wall |
| Chin corners | 72.05 | MEASURED — the governing number |
| Knob bore | 72.5 | 0.45 clearance |
| Knurl root / outside | 76.0 / 77.0 | 3.5 under the root, 1.0 knurl |
| Plate edge | 76.5 | 0.5 inside the knob |

**Knob Ø154.0, plate Ø153.0, object Ø154.0.** Alternatives: knurl 0.8 deep → Ø153.6; Ø150 by the undercut route, question 1.

### 8.2 Why two levels

Floor inside the wall: r 70.5, 15,600 mm². Pi 88 × 56 = 4,930; adapter 65 × 64 = 4,160; motor sector ~2,000; speaker 1,260; converter 950; three socket boards ~800; motion 2,000; audio 1,000: 17,100 mm² of rectangles in a circle that holds ~11,000 mm² of rectangles. Placing the Pi and the adapter side by side needs a chord of 120 mm where the circle allows 141 only at the centre and 74 at x = ±60. So the floor takes the Pi, the motor sector, the speaker, the converter and the sockets, and the deck takes the three boards. With the adapter gone (question 3) the deck goes too.

### 8.3 v10 stack as built — option A″: cooler heatsink kept, fan off, Pi on the pad through the plate, display bonded to the seat

| z | What | Cost driver |
|---|---|---|
| −1.5–0 | pad | |
| 0–8.0 | plate; halo 8.0–10.6; lip 10.6–11.4; skirt from 12.0 | plate 8 (4.16) |
| 1.5–2.78 | Pi board (SD slot 1.45 below it on the pad) | |
| 4.2–18.2 | motor on its carriage; drive band 9.0–17.8 | v9 case B |
| 12.6 / 18.98 | heatsink fins' top / Pi USB-A tops | the Pi's own thickness |
| 19.48–20.98 | mezzanine deck | +1.5 |
| 20.98–29.3 | boards and plugs on the deck (8.3: 0.8 boss + 1.6 board + parts; the HDMI socket to 30.2 under the bare glass) | the deck's contents |
| 18.5–22.7 code band; 23.9–27.9 wheels; 28.4–30.4 seat flange | | |
| 30.4–30.9 | bonding tape under the glass edge | +0.5 for holding a holeless panel |
| 30.9–32.88 | panel glass 1.98 (its back components hang 1.5 below it inside r 45, over the boards' clearance) | |
| 32.88–35.38 | lens 2.5 (ASSUMED) | |
| 35.78–38.78 | lip 3.0 after the 0.4 rim gap | |
| **40.3** | **overall with the pad** | |

What each part costs against a floor-only object: the deck and its boards **+9.8**; the bonding tape **+0.5**; the cooler's heatsink **0** (the USB-A stacks are as tall); the 8 mm plate **0** in height, −7 % in the knob's share of the side.

### 8.4 Option B — cooler deleted, Pi inverted, SoC on a boss to the plate

Pi inverted with its USB-A and Ethernet stacks standing on the pad through the plate window: component face at z 16.2, board 16.2–17.48, its back-side parts to 18.93; SoC face at 13.86; boss 5.4 tall on the 8 mm plate, 0.5 pad. Deck at 19.48 as built (the motor top and the Pi's back both allow it). Everything above is identical: **40.3 with the pad**, the same as A″.

Thermal credibility at ~4 W (ASSUMED coefficients): pad 0.3 K/W, boss negligible, plate spreading 0.65 K/W (8 mm; 1.0 at 5 mm) → SoC ~4 K above the plate; the plate is ~10 K above the room at 4 W total (6.9) → **SoC ≈ room + 15 K: credible, and silent.** At 12 W stress the Pi throttles at 85 °C long before the object does; acceptable for a desk prototype. Cost: a machined boss, two plate holes, the Pi's sockets facing down (the micro-SD slot is then on the visible back face — convenient), and a thermal-pad thickness that must absorb the boss-to-SoC tolerance (use 1.0 mm, ASSUMED). Gain in height: **none**. A″ (the heatsink without its fan) is built because it needs no new parts; B is the fallback if the first print's temperature log says so, and production's principle.

### 8.5 Production — the same object with a Compute Module 5

CM5 SoC-down on a plate boss (4.17 numbers): plate top 8.0 → pad 0.5 → SoC 2.2 → module PCB 1.24 → 4.0 stacking connector → carrier 1.6 → carrier top-side parts 4.0 (ASSUMED) → carrier top at 21.5. No deck, no adapter, no ribbon, no Pi window (the plate keeps its mass: 1.0 kg). Panel back parts from 22.0 → glass back 23.5 → glass, lens, fingers, gap, lip as v10 → knob top 32.4, **overall 33.9 mm**; 31.4 with the 1.5 mm stacking connector if the carrier's underside allows it. The motor stack (top 18.2) is then 3.3 below the deciding layer — the carrier and the CM5 decide, and a thinner carrier assembly (parts on one side only) would bring the product to ~30.

---

## 9. What is v10-only and what is production

| v10-ONLY | PRODUCTION |
|---|---|
| Raspberry Pi 5, the Active Cooler's heatsink, the plate window, the deck and its legs, the servo on the deck and the tall carriage tab, the HDMI adapter, the HDMI ribbon, the internal USB-C and USB-A cables, the header power housing, the bought converter module, the touch-controller board as a separate item, height 40.3 | Ø154 knob and its lip/chamfers/knurl, bore Ø145, the panel and lens bonded to the seat, the wheel/motor/servo/encoder radii, the halo at r 73.3, the 8 mm plate and its rear slot, the three rear openings and the 12 V barrel choice, the perimeter ports and the vent answer, the audio and motion functions (on the carrier), the CM5 boss principle, height ≈ 34 |

---

## 10. Rules for building the v10 CAD once agreed — v9's ten rules, plus

11. Every plug body (barrel, USB-C, 3.5 mm, micro-HDMI, HDMI-A, USB-A, header housing) is a named `_ENVELOPE` body in the assembly, in its inserted position.
12. Every cable is a swept body along its modelled route with its bend radius as a parameter, and the checker tests it against the carriage sweep, the bell and the wheels at knob angles 0/17/45/73° and both clutch states.
13. The checker proves the display module's insertion path (a straight drop through the bore), the structure's entry from below, and the deck and Pi screws' tool paths.
14. The parameter block carries `PLATE_T` and `COOLER_FAN_FITTED` as switches; the deck layout is five azimuth/radius pairs.
15. Drawings: A3, one sheet per made part, the first sheet listing every ASSUMED number.
