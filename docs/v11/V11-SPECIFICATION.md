# the 60 — version 11 specification

**Status: as-built specification for the v11 CAD.** This document describes every component and mechanism the v11 model contains, says which numbers are measured and which are assumed, grades every requirement, and separates what is true of the v10/v11 prototype only (Raspberry Pi 5) from what carries to production.

Revision: 6 September 2026 — v11 = v10 (5 September, every default in `V10-QUESTIONS.md` approved, glue allowed for the display, the twelve build-time changes and the print review folded in) plus Ryan's rulings of 6 September: **a flat rim of at least 20 mm on the knob's top** (the knob and everything flush with it go from Ø154 to Ø175.4) and **a thin-walled, hollow knob**. Superseded text has been removed, not struck through. The v10 documents stay in `docs/v10/` as delivered.

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

**Finding 1 — the panel is not a circle, and that sets the diameter.** The DM-TFTR50-413 glass is a Ø132.2 disc with a **driver chin** at one edge: a 31.0 mm wide flat extension whose corners sit at **r 72.05 from the picture centre** (MEASURED from the STEP: the outline's furthest points are (±15.52, −70.36)). The knob rotates around the fixed panel, so the knob's bore must clear r 72.05 at every angle. With 0.45 mm clearance the bore is **Ø145.0**, and with the v9 knob wall of 4.5 mm the knob would be Ø154 (not Ø150; Ø150 needs an internal undercut, question 1, not recommended). **Ryan's ruling, 6 Sep: the knob's top must be a flat rim of at least 20 mm**, so the outside is set by the rim, not the wall: lip edge r 64.2 + 1.0 inner chamfer + 20.0 flat + 2.5 outer chamfer = **r 87.7, Ø175.4**, knob wall 15.2 under the knurl. **This specification is written for Ø175.4.** The top ring (drawing `v11_top_ring.png`) is 23.5 mm of metal, 24.2 mm from the picture edge to the knob edge (v9: 18.7; the first v10 build 13.5).

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
| Diameter | **Ø175.4** knob and plate: the bore is set by the panel (Ø145, finding 1) and the outside by the 20 mm top rim (Ryan, 6 Sep); Ø150 was the nominal and is not reached | MUST (ruling) | brief; 6 Sep |
| Height | derived: **40.3** v10 with the pad; **≈ 34** production with the CM5; the stack and what each part costs are in section 8 | report | brief |
| Mass | more is better; **8 mm** steel plate (0.98 kg net after its cut-outs at Ø175.4) — see 4.16 for why 8 and not 5 | SHOULD | brief; 4.16 |
| Knob | one piece, no seam or screw; the majority of the visible side (v10: 62 % — the 5.5 mm halo band and the 8 mm plate both come out of the knob); diamond knurl; wide smooth 45° chamfer at the top outer edge; small smooth chamfer at the lens; touches nothing but its three wheels, never the display | MUST | brief; v9 |
| Top ring | a flat rim of **at least 20 mm** on the knob's top (Ryan, 6 Sep): 23.5 of metal from the lip edge — 1.0 inner chamfer, 20.0 flat, 2.5 outer chamfer — 24.2 from the picture edge to the knob edge; `v11_top_ring.png` | MUST | 6 Sep |
| Display | DM-TFTR50-413 bare panel, picture Ø127.0, behind a round cover lens carrying a bonded 10-point capacitive sensor, specified separately (4.2, 4.3) | MUST | brief |
| Computer | v10: Raspberry Pi 5 + the Active Cooler's heatsink (fan off, finding 3), powered through its 5 V header pins, its USB-C free for the PC. Production: Compute Module 5 on a custom carrier | MUST | brief |
| Sockets | three openings in the base wall at the rear, at plate level, below the halo: **12 V barrel inlet, USB-C data to the PC, 3.5 mm line out**; plug bodies drawn, not just sockets (section 6.8) | MUST | brief |
| Audio | own board (XMOS + converter, ~25 × 40); 3.5 mm is line out to powered speakers, no amplifier; speaker carried from v9 | MUST | brief |
| Motion | motor, encoder, LRA, servo and LED ring on their own microcontroller board (size proposed in 4.13) | MUST | brief |
| Halo | full 360°, on the fixed base, its bottom edge the plate edge; a bought LED strip stuck to the wall (Ryan, 5 Sep evening), its light crossing an 11 mm channel under the knob's skirt to an L-section diffuser at the Ø175.4 edge (5.3); driven hard — see 4.8 for the watts | MUST | v9; brief |
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

### 4.8 Halo — a bought addressable LED strip on the wall (PRODUCTION)

**Ruling (Ryan, 5 Sep evening): the halo is an off-the-shelf addressable LED strip stuck to the wall, not discrete side-firing LEDs laid flat on the plate** — that arrangement was accepted on paper in v9 but is not going to be built. The strip (ASSUMED **5 mm wide, 1.6 thick**, ~100 LEDs per metre → 46 LEDs; any 5 mm WS2812B-2020 / SK6812 strip) stands vertically on a 1.1 mm thick band on the outside of the structure's wall (r 72.1–73.2) from z 8.25 to 13.25, its LED face at r 74.9 firing outward into the diffuser (r 75.1–77.0, 1.9 thick at the bottom). The band keeps the strip 0.2 outside the motor's bell + band (r 73.1); across the motor's relief sector (74–106°) the strip spans 40 mm with no backing, as a hoop. The halo band is z 8.0–13.5, the lip 13.5–14.3, the knob's skirt starts at 14.9. A wider strip raises the band by the difference. The strip's data and 5 V come from the motion board and the converter.

**Driven hard, in watts:** a 5 mm WS2812B-2020 strip at 100 per metre is rated about 0.1 W per LED (PUBLISHED, typical strip data): **46 LEDs at full white ≈ 1.0 A, 5 W** (a 60-per-metre 5050 strip would be ~2.8 A, 14 W). The heat lands on the structure's wall, not the steel — a PETG wall at 5 W over 465 mm of strip is fine; watch it if a 5050 strip is chosen. Sustained full white is not a realistic duty; a colour at 30 % is under 2 W. Section 6.9 uses 2 W sustained, 5 W peak.

### 4.9 Perimeter ports, port face, light sensor, USB-C receptacle, 3.5 mm jack, DAC (digital-to-analogue converter) — carried

Vents: **vertical slits** 1.0 wide × 3.5 tall (z 14.7–18.2, between the halo lip and the code band) on a 2.5° grid all round the wall, 89 of 144 positions cut (the motor's relief, the pillars' and posts' webs, the encoder tower and the LRA pad take the rest): 312 mm², passive (6.9). Ryan's review, 5 Sep: slits, not round holes. GCT USB4520 mid-mount USB-C receptacle (CAD body exists) on its small board; Switchcraft 35RAPC4BH3 3.5 mm jack (CAD body exists); VEML7700 light sensor on its tiny board behind a Ø4.8 hole. The ES9219Q DAC moves from the jack board to the audio board (4.12); the jack board becomes a plain jack carrier.

### 4.10 Barrel power jack — CUI PJ-063AH (PRODUCTION, part proposed)

**No CAD body yet** (Same Sky offers one — fetch it before CAD). PUBLISHED: 2.0 mm centre pin (5.5 × 2.1 plug), **24 V 8 A** rated, right-angle through-hole. ASSUMED body 14.4 × 9.0 × 11.0, socket axis 6.5 above its board. Where: rear port slot, at 0° −15 mm tangential, on a small **vertical** board (tangential plane) so the barrel's axis height is free — axis at **z 3.5**, the plug body from z −0.75 to 7.75, under the halo's bottom edge (z 8.0) by 0.25 and into a through-pocket in the pad. Why a barrel and why 12 V: section 6.8. Plug body: a **right-angle 5.5 × 2.1 plug, Ø8.5 body** (ASSUMED) — a straight moulded plug on a 12 V brick is Ø10–11 and does not fit under an 8 mm plate's top edge; the cable leaves the object sideways along the rear wall.

### 4.11 12 V → 5 V converter board (PRODUCTION as a function; v10 as a bought module)

**No CAD body.** ASSUMED: a 5 V, 9–10 A step-down module 38 × 25 × **8**, **on the plate** (thermal plan rule 15, Ryan 6 Sep) in the front crescent at az 172°, r 47–72, standing on a 0.5 mm thermal gap pad over a masked bare patch of the anodising, two M2.5 screws into the web (the module's holes ASSUMED at ±16 on its centre line). It was on the deck in v10; on the plate its heat goes straight into cooled metal. Feeds: the Pi's header (5 A peak), the halo (up to 4 A), the adapter, the audio and motion boards. The motor driver stays on 5 V (the TMC6300's PUBLISHED maximum is 11 V).

### 4.12 Audio board — XMOS USB audio + ES9219Q (PRODUCTION as a function)

**No CAD body.** Ryan's envelope: **25 × 40**; ASSUMED 6 mm tall from the deck including the board and a 4-pin connector, M2.5 corner holes. Where: on the mezzanine deck at az 110°, r 47.5–72.5 (radial 25, tangential 40; 10 further out than v10, the deck being Ø161). Connections: USB to one of the Pi's USB-A sockets (an internal USB-A-to-USB-C cable, ~120 mm, plug body 15 × 6.5 × 20 at the Pi's front end — drawn); line out to the 3.5 mm jack board (3-wire JST-SH); the speaker (2-wire, the XMOS drives a small class-D on this board — the speaker amplifier is the board's, the 3.5 mm output has none). The lens's touch controller board (if the sensor supplier gives one) stacks on the adapter's outer region on 2 mm standoffs, 4.12a: ASSUMED 30 × 20 × 3, USB to the Pi.

### 4.13 Motion board — microcontroller for motor, encoder, LRA, servo, LED ring (PRODUCTION as a function)

**No CAD body.** Envelope as built: **30 × 30 × 7.4** (the TMC6300 driver, a DRV2605L, the microcontroller, low-profile JST-SH connectors 5 mm tall on its motor-facing edge) — the first draft proposed 50 × 40, but the deck's free sector beside the servo is 30 × 30. Where: on the mezzanine deck at az 45°, r 40–70 (v10: az 55, r 30–60 — the servo tray moved out with the motor), so the four short cables (motor phases, commutation sensor in the carriage, servo, encoder tower) run a few centimetres. Talks to the Pi over **UART on the 40-pin header** through the same 2 × 5 housing that brings 5 V in — one plug, no internal USB cable for motion (ASSUMED; a USB alternative is question 9). The LED ring's data line comes from here; its 5 V comes from the converter directly (4 A does not go through a signal board).

### 4.14 Mezzanine deck (made part, v10-ONLY) — see 5.4.

### 4.15 Internal HDMI ribbon (v10-ONLY)

**No CAD body.** ASSUMED: a 20-way 0.5 mm pitch flat flexible HDMI cable, 200 mm, with a micro-HDMI **up-angle** plug board at the Pi end (12 × 8 × 5) and an HDMI-A plug board at the adapter end (21 × 12 × 6). Route as built: from the Pi's HDMI0 socket at z 2.8–7.8 on the 270° edge, 6.5 mm outward, a 90° fold upward (bend radius 2.0 — a 0.1 mm flex tolerates 1.0 static), through a 22 × 3 slot in the deck, a 90° fold onto the deck, 33 mm along −x under the adapter board (0.3 mm ribbon under a board on 0.8 mm bosses) to the HDMI-A plug in the adapter's −x-edge socket. A round moulded micro-HDMI cable needs a 25 mm bend radius and 12 mm plug bodies and does not route in this height; the ribbon is the design. Two folds, both static, both ≥ 2 mm radius, both modelled.

### 4.16 Base plate — the heatsink: aluminium core, steel rim ring, closing plate (PRODUCTION; `the60-thermal-plan.md` section 14 applied, Ryan's 6 Sep decisions: steel ring, converter on the plate, rear exhaust through the pad)

Three machined pieces, Ø175.4 flush with the knob, 8 mm at the rim, the object's height unchanged (rule 6).

**The aluminium core**, r < 75.2, 6082, **black hard anodised on every face including the internal ones** (rule 1: the cavity's only route to the cold plate is radiation), with two masked bare pads — round the ground-bond screw at (50, −20) and under the converter (rule 2). In section: a **4 mm web** (z 4–8), a **3 mm duct** (z 1–4) and a **1 mm closing plate** flush in a recess (z 0–1), screwed on with six M2.5 countersunk screws that all land in solid web, so it comes off to clean the channels (rule 5). A rebate r 72.2–75.2, z 4–8 takes the ring's flange; seven M3 countersunk screws from below through the core's shoulder hold the ring. Through it: the Pi window (with its plug notches), the carriage hole, the port slot from r 55, the two speaker-cradle screws, the ground bond, two M2.5 tapped holes for the converter — each through-cut with a 2.5 mm solid wall round it so the duct does not leak into it. On its top face, ten **ribs 2 × 6 mm** at r 50–70 in the free crescents (az 30, 40, 135, 145, 200, 210, 220, 235, 245, 255), tall and sparse (rule 13), inside r 70 so the structure still enters from below. Mass ≈ 143 g.

**The duct** (rules 7–12): air enters through a **1.2 mm undercut on the bottom outer edge** outside the pad (r 84.7–87.7) over the front and sides, az 45–315 (496 mm² of mouth; the rear is closed); through **22 radial grooves 6 × 2** in the ring's underside (264 mm²; the pad closes them from below; the two grooves that would land on the motor's through-hole are omitted); into a **collector** r 66–70.2 round the front and sides; through **20 straight fin channels 3 wide × 3 tall on a 4 mm pitch** — ten either side of the Pi window, front to rear; into a **rear plenum** either side of the port slot (r 55–70.2, az 22–52 and 308–338); and out through **six exhaust grooves** at az 27–41 and 319–333 (72 mm²) that open **downward where the pad is cut away** (az 15–46 and 314–345) — rear only, a different arc from the intake, not the socket slot (rule 10). One connected volume, 25 cm³, checked. No opening through the top face or the edge face (rules 8, 9). A **blower envelope 28 × 18 × 5** is reserved in the main duct under the speaker at az 277, r 60 — 3 in the duct, 2 into the web; the part is **not fitted** (rule 12). What the geometry would not give: a 30 × 30 spot — the motor's through-hole and the Pi window rule it out everywhere — so the envelope suits a slim or 20 × 20 blower; and the link between the +y rear quadrant and the front is one 2.25 mm channel between the Pi window's wall and the carriage tab slot's wall, so that quadrant is fed mainly by its own three intake grooves.

**The steel rim ring**, r 75.2–87.7 × 8, mild steel, black (RULING 6 Sep: steel, for mass — ≈ 333 g at the largest radius; in aluminium it would be 115 g): the **engine-turned edge** (twelve smooth blocks 8° wide at 0 / 30 / 60 ... ° and thirteen square-cut grooves 1.2 × 1.0 at 2.4 pitch between each pair, 156 in all, cut in plan) with **1.0 chamfers top and bottom**; the intake undercut and the intake and exhaust grooves in its underside; an inward flange r 72.2–75.2, z 4–8 onto the core with seven M3 tapped holes; the structure's three plate screws at r 77.2 (countersunk from below); two Ø1.6 holes tapped M2 at r 78.2, t ±26 for the port face's rail; the port slot, its mouth trimmed 3 mm each side so no sliver of engine-turning is left. Its inner radius is derived (rule 4): 3 mm inboard of the port face's fixing holes, well inboard of the diffuser's seat at r 85.8; it carries the halo's 8 mm and the plug bodies' 9 mm at the edge, which is the only place the object needs the thickness.

**The closing plate**, 1 mm aluminium, laser-cut, anodised: a disc r 72.1 with the same three windows as the core and six countersunk holes.

Mass (rule 16): core ≈ 143 g + ring ≈ 333 g + closing plate ≈ 24 g ≈ **500 g**; all-aluminium ≈ 282 g; the v10 Ø154 steel plate was 660 g. Why 8 mm at the rim: the plug bodies at the rear must sit between the pad's underside (z −1.5) and the halo's bottom edge (the plate top), so the tallest plug body is plate + pad − 0.5 = 9.0 mm — a USB-C plug is 6.5, a 3.5 mm plug Ø6–8, a right-angle barrel Ø8.5. Why the duct is worth building even unfanned: it is an intake and a defined path, worth ~0.1 W/K passive, and it makes the blower a fitted-or-not decision after measurement rather than a plate respin (the plan's section 8).

### 4.17 Compute Module 5 (PRODUCTION only — not in v10)

PUBLISHED (datasheet, verified): 55 × 40, bare module 4.6 deep, PCB 1.24, SoC 2.2 tall, four M2.5 holes inset 3.5; mounted height 4.94 with the 1.5 mm Amphenol stacking connector or 7.44 with the 4.0 mm one; idle 0.4 A, load 0.9 A at 5 V; "less passive heat-sinking than a Pi 5 — any thermal solution must be designed". Section 8.5 uses it SoC-down on a plate boss with the 4.0 mm stacking.

### 4.18 Rubber pad — now a **plain 1.5 mm ring under the rim ring**, r 75–84.7 (0.5 lean to the desk), cut away at the port slot and at the exhaust arcs (az 15–46 and 314–345) so the exhaust grooves open to the desk; it closes the intake grooves from below and is no longer part of the airflow (thermal plan). The Pi hangs from the deck's legs, not from the pad. Screws, inserts, nuts, cables, code strip, display bonding tape, LED thermal tape, the converter's thermal gap pad — the pad, the display tape and the gap pad are the only adhesives (Ryan, 5 Sep). Hardware as built: 8 × M3 inserts in the structure's pillars, 3 × M2.5 inserts in the deck's legs, **14 × M2.5 DIN 934 nuts pressed into the deck's top-face pockets** (the boards' and the servo tray's fixings — no inserts in the deck), 14 × M2.5 × 4, 2 × M2 × 4 (port face rail into the rim ring), 3 × M2.5 × 6 (Pi), 5 × M3 × 6 (deck), 3 × M3 × 8 csk (plate to the pillars), 2 × M3 × 8 csk (speaker cradle), 7 × M3 × 8 csk (rim ring to the core), 6 × M2.5 × 4 csk (closing plate), 2 × M2.5 × 6 (converter), 3 × 623ZZ.

---

## 5. Made components

### 5.1 Knob (PETG prototype; CNC 6082 production)

One piece, v10's shape scaled to the rim (Ryan, 6 Sep: "relatively similar in shape to the prior version, just with a larger rim"). **Ø175.4** outside, a **4.5 wall** (1.0 knurl + 3.5 under the root), the **3 mm lip** now 19 wide from its edge at r 64.2 to the bore; top rim 1.0 inner chamfer + 20.0 flat + 2.5 outer chamfer. ≈ 72 cm³: ≈ 90 g in PETG, ≈ 195 g in aluminium (v10: 50 cm³); inertia ≈ 1.7× v10's — re-tune the detents on the bench (section 7). Bore **Ø166.4** (the chin at r 72.05 is 11 mm inside it) straight from the skirt's bottom (z 14.9) to the lens level, with: the 90° V-groove for the wheels (root r 73.8, z 24.3–27.5); the 0.15 code-band recess (z 18.5–22.7); the lip on top: inner edge **Ø128.4** (0.7 outside the picture), 3.0 thick, underside at z 35.78, top at **z 38.78**; skirt bottom at z 14.9; outer chamfer 2.5 at 45°, inner chamfer 1.0, skirt chamfer 1.2. Knurl: diamond, 1.0 deep, four whole rows as v9 (helix 37.4°, derived from the band height 16.9–35.5), **78 starts** at Ø175.4 to keep the v9 pitch (question 13); the grooves run out downward through the skirt's 1.2 chamfer (print review, 5 Sep: a flat knurl foot was 68 downward ledges when the knob prints top face down) and stop 0.8 under the top chamfer. Wall under the knurl root 3.5. The knob touches only its three wheels: 0.4 to the lens and the structure, 0.45 to the chin.

### 5.2 Internal structure (printed; PA12 production)

One part, as v9, scaled to the bore: a wall r 81.2–82.8 from the plate top to the seat; the **seat flange** at the top (r 62–82.8, z 28.4–30.4 — a 21 mm shelf now; the glass bonds at r 62.5–65.6 as before) with the 32 × 2.5 flex slot at 0° and three Ø2 locating nubs at 60/210/330° — the display module bonds to it; three wheel posts Ø8 at r 76.9, az 30/150/270 (bush sockets open to the plate side), webbed to the wall, with a 15.2-wide window through the wall above each for the wheel and **the seat flange cut away entirely above each wheel** (print review, 5 Sep: nothing needed it, and it was a shelf hanging over the window — the glass bridges the three notches, the tape ring is unbroken); the encoder tower at 310°, 25.1 tall, its sensor window through the wall open to the top, its board slot open right through the seat with a 0.25 crush rib (the 8 × 11 board is pressed in from the seat side before the display goes on and the lens caps it); the motor's window in the wall open up to the seat flange (no roof to bridge); the LRA pad at 258°; the 1.1 mm band the LED strip sticks to (r 82.8–83.9, z 8–13.5) and the diffuser-retaining lip above it (r to 86.7, 13.5–14.3); **five Ø7 pillars at r 77.2, az 50/120/180/240/320**, webbed to the wall, with M3 inserts at the top for the deck's screws and, at 120/240/320, at the bottom for the plate's screws; 89 vertical vent slits 1.0 × 3.5 at z 14.7–18.2 on a 2.5° grid; the motor relief at 90°; the three blind plate-screw insert holes end in 45° points. No ledge, no display columns, no seat tabs, no carrier, and **no lid** (thermal plan rule 14): the deck's boards reach z 29.4 and the panel's back components start at 29.4, so there is no room for one in v11 — the bonded glass and the seat flange close the cavity; the lid arrives in production with the boards on the plate. **Printing**: upright on the wall's foot; supports only under the seat flange (a hidden ring inside the wall) and under the diffuser lip (a thin ring outside) — everything else is open-topped, a 1 mm bridge or steeper than 45° (`src/printcheck.py`).

### 5.3 Halo diffuser — carried, at the new radius: r 85.8–86.7 at the bottom leaning out to 87.7 at the top (Ryan's review: a more exaggerated taper), z 8.0–13.5, 0.5 chamfer on the outside top edge; sits on the rim ring 0.2 outside the strip, wholly on solid steel (the ring's top chamfer and groove floors start at r 86.7), retained by the structure's lip.

### 5.4 Mezzanine deck (v10-ONLY)

A flat printed plate Ø161, 1.5 thick, z 19.48–20.98, with: notches around the three wheel posts and the encoder tower; the 6 × 10.6 slot for the carriage's tab at 90°; the 22 × 3 ribbon slot beside the Pi's HDMI0; five Ø3.4 holes at the pillars. In its top face: fourteen hex pockets (5.15 across flats, 1.0 deep, Ø2.8 through) holding **M2.5 nuts** for the adapter (4), the audio board (4), the motion board (4) and the servo tray (2); the boards sit on the nuts, 1.0 above the deck, and are held by M2.5 × 4 screws from above (print review, 5 Sep: the 0.8 mm insert bosses that used to stand on the top face left the whole face hanging 0.8 above the bed when printed top face down; inserts in bosses under the deck do not fit — 1.28 mm to the motor bell, 0.5 to the Pi's USB stack). On its underside: three legs Ø5.5 down to the Pi's board top (16.7 tall) with M2.5 inserts — the Pi hangs from them; nothing else. Print upside down, flat top face on the bed, no supports.

### 5.5 Display seat (PRODUCTION) — the display module's interface to the structure

The seat flange of 5.2, with the bonding tape (4.1). No separate part. The display module (lens bonded to the panel by its supplier) is placed lens-down in the inverted knob and the structure is lowered onto it with the tape on its seat; the three nubs centre the glass. Cost in the stack: 0.5 mm of tape. Replacing the display means peeling it off the seat — acceptable for v10; production can revisit a clamp ring if a tool-free swap is wanted.

### 5.6 Carriage, servo tray, speaker cradle, port face, V-collars ×3, eccentric bushes ×3 — carried from v9 with the new radii. The carriage gains a 3 × 10 × 28 tall push tab (rooted to the shoe; printed standing, the tab is loaded across its layers — PETG, 4 perimeters); the servo tray sits on the deck with two ears at ±14 for M2.5 × 4 screws into the deck's captive nuts (round 1.0 pockets in its floor over the nuts); the speaker cradle's three snap fingers stand from the plate (full height, so they print without support and flex more); the port face (44 wide, three sockets) stands at the wall's inner face, r 79.7–81.2 (the sockets 6.5 inside the edge, as v10's proportion), with a 1.5 mm rail along its top (flat-fronted, corners cut at 45°) screwed to the rim ring beside the slot, inside the wall (2 × M2 into tapped holes at r 78.2, t ±26 — v10's ears sat over the slot's void); the 3.5 mm jack stands on its 16 × 12 board with the pins down into the pad's void (in v10 the board sat under the wall and the LED strip); prints lying on its outer face so the socket holes are vertical. The three eccentric bushes print stem down (the 1 mm flange ledge is their only overhang); the collars axis-vertical.

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

### 6.9 Cooling — the base plate is the heatsink; the perimeter slits are acoustic only

Replaces the v10 vent analysis (`the60-thermal-plan.md`). The sustained load is 12–14 W and the object's passive skin is worth about 0.4 W/K; IEC 62368-1 caps a bare-metal knob at 48–51 °C in a 25 °C room; the knob is the largest surface and the one surface that may not be made hot, and it sits close to cavity temperature whatever the structure does (1.6 mm of PA12 plus the 0.4 running gap is ~0.4 W/K of coupling through the bore). So the heat goes down, into the plate, and out under it.

**One forced path, entirely below the plate's web**: room air → the 1.2 mm undercut on the rim's bottom edge (front and sides) → 22 grooves under the rim → the collector → 20 fin channels → the rear plenum → six exhaust grooves opening downward at the rear where the pad is cut away. The web has no holes; the forced stream never enters the cavity, never passes the panel or the encoder. **The 89 perimeter slits stay the speaker's acoustic port and nothing else**; the cavity breathes through them by buoyancy only. What the plate buys: black anodising takes the plate's emissivity from ~0.25 (steel) to 0.88 on both faces — the underside radiating to the desk and the top face to the cavity; aluminium spreads four times better, so the plate runs near-isothermal; the ribs reach 6 mm up into the warmer stratified air; the converter conducts straight into the web through a gap pad. The plan's figures: **0.5 W/K passive** (against 0.4 today) — 48 °C skin at 13 W in a 22 °C room, 51 °C at the standard's 25 °C, exactly at the limit; **1.1 W/K with a blower** at ~1 L/s — 34 °C / 37 °C. Read the other way: for a 40 °C skin in a 22 °C room, 9 W passive or 19.8 W fanned. The blower's envelope is reserved and the part is not fitted; whether it is fitted is decided by measurement (section 7, items 8 and 9), and the passive route is a power budget — cap the halo and underclock the compute module to ~9 W sustained.

What the first print measures: the real load at the 12 V inlet through an hour of use; plate, knob and cavity temperatures on the passive build in a known room; and the ducted case with a bought blower taped into the envelope. The 4 W Pi keeps its heatsink in v11 (fan off, finding 3); in production the compute module's boss goes to the plate through a masked pad (8.5).

### 6.10 Assembly order (upside down) — every step reachable, proven by the checker

1. Knob upside down, lip down, the code strip already in its recess; a 0.4 shim ring on the lip.
2. Display module (lens + panel, bonded by its supplier) lens-down onto the shim, the chin at 180°, the flex tab at 0°. The Ø140 lens and the r 72.05 chin pass the Ø145 bore with 2.5 and 0.45 to spare — a straight drop, proven by the checker.
3. Internal structure, bonding tape on its seat, lowered over the panel's back with the wheels retracted; the flex and the touch tail led through the seat slot; the three nubs meet the glass edge; the seat pressed onto the glass — the display is now bonded. The structure enters the knob's bore from below on a straight path (checker).
4. Bushes half-turned from the plate side to seat the wheels in the groove; locked; shim out through the rim gap.
5. Encoder breakout into its tower, LRA onto its pad, the LED strip stuck round the wall's band (its lead down to the motion board), diffuser into the structure's lip.
6. Mezzanine deck with its boards pre-fitted (adapter with the touch controller stacked on it, audio, motion, converter, servo in its tray); the panel flex plugged into the adapter and the touch tail into its controller; the deck lowered onto the five pillars, 5 × M3 from above (Ø6 driver paths proven clear).
7. Pi with the cooler's heatsink clipped on (fan off), hung from the deck's three legs with 3 × M2.5 driven from below; header housing on; ribbon from HDMI0 folded up through the deck slot and along under the adapter into its HDMI socket; internal USB-C cable into the Pi's USB-C; the audio board's right-angle USB-A plug into the upper rear USB-A socket.
8. Motor on its carriage, band on, carriage into its guide with its tab up through the deck slot to the servo's pushrod; motion-board cables plugged; speaker into its cradle at (17, −46); barrel-jack board, USB-C board, jack carrier and light-sensor board into the port face; port face into the slot; power leads to the converter.
9. Plate on — its window around the Pi and its plugs, its hole around the carriage, its slot around the port face — 3 × M3 countersunk into the pillars at 120/240/320°, 2 × M3 speaker, ground bond.
10. Pad on (its pocket at the barrel). Turn over.

Nothing is glued but the pad, the display's bonding tape, the code strip and the LED strip's own backing (bought parts with their own adhesive). Everything reverses; the display by peeling.

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
| Chin corners | 72.05 | MEASURED — was the governing number in v10; now 11 mm inside the bore |
| Core / ring joint | 72.2–75.2 | the ring's flange on the core's rebate; the duct and closing plate end at 72.2 |
| Rim ring | 75.2–87.7 | 3 inboard of the port face's holes (rule 4) |
| Pillars, wheel posts | 77.2, 76.9 | 4 and 4.3 inside the wall, as v10 |
| Port face | 79.7–81.2 | at the wall's inner face, as v10 |
| Structure wall | 81.2–82.8 | 1.6 printed wall, 0.4 inside the bore, as v10 |
| Knob bore | 83.2 | **R_KNOB − 4.5**: the knob's wall sets it (Ryan, 6 Sep) |
| LED strip on the wall's band | 84.0–85.6 | on a 1.1 band, as v10 |
| Diffuser | 85.8–87.7 | 0.2 outside the strip, leaning to the edge, as v10 |
| Knurl root / outside | 86.7 / 87.7 | 3.5 under the root, 1.0 knurl |
| Top rim | 64.2 → 87.7 | 1.0 chamfer + **20.0 flat** + 2.5 chamfer (Ryan, 6 Sep) |
| Plate edge | 87.7 | flush with the knob; grooves 1.0 deep and 1.0 chamfers top and bottom |

**Knob Ø175.4, plate Ø175.4, object Ø175.4** — set by the 20 mm rim; everything inside is derived from the bore by v10's rules, so the whole object scaled out with it.

### 8.2 Why two levels

Floor inside the wall: r 70.5, 15,600 mm². Pi 88 × 56 = 4,930; adapter 65 × 64 = 4,160; motor sector ~2,000; speaker 1,260; converter 950; three socket boards ~800; motion 2,000; audio 1,000: 17,100 mm² of rectangles in a circle that holds ~11,000 mm² of rectangles. Placing the Pi and the adapter side by side needs a chord of 120 mm where the circle allows 141 only at the centre and 74 at x = ±60. So the floor takes the Pi, the motor sector, the speaker, the converter and the sockets, and the deck takes the three boards. With the adapter gone (question 3) the deck goes too.

### 8.3 v10 stack as built — option A″: cooler heatsink kept, fan off, Pi on the pad through the plate, display bonded to the seat

| z | What | Cost driver |
|---|---|---|
| −1.5–0 | pad | |
| 0–8.0 | plate; halo 8.0–13.5 (5 mm strip); lip 13.5–14.3; skirt from 14.9 | plate 8 (4.16); strip width (4.8) |
| 1.5–2.78 | Pi board (SD slot 1.45 below it on the pad) | |
| 4.2–18.2 | motor on its carriage; band on the bell 9.0–17.8, met by the bore over 14.9–17.8 | v9 case B |
| 12.6 / 18.98 | heatsink fins' top / Pi USB-A tops | the Pi's own thickness |
| 19.48–20.98 | mezzanine deck | +1.5 |
| 20.98–29.3 | boards and plugs on the deck (8.3: 0.8 boss + 1.6 board + parts; the HDMI socket to 30.2 under the bare glass) | the deck's contents |
| 18.5–22.7 code band; 23.9–27.9 wheels; 28.4–30.4 seat flange | | |
| 30.4–30.9 | bonding tape under the glass edge | +0.5 for holding a holeless panel |
| 30.9–32.88 | panel glass 1.98 (its back components hang 1.5 below it inside r 45, over the boards' clearance) | |
| 32.88–35.38 | lens 2.5 (ASSUMED) | |
| 35.78–38.78 | lip 3.0 after the 0.4 rim gap | |
| **40.3** | **overall with the pad** | |

What each part costs against a floor-only object: the deck and its boards **+9.8**; the bonding tape **+0.5**; the cooler's heatsink **0** (the USB-A stacks are as tall); the 8 mm plate **0** in height, −7 % in the knob's share of the side; the 5.5 mm halo band **0** in height, −7 % more of the knob's share.

### 8.4 Option B — cooler deleted, Pi inverted, SoC on a boss to the plate

Pi inverted with its USB-A and Ethernet stacks standing on the pad through the plate window: component face at z 16.2, board 16.2–17.48, its back-side parts to 18.93; SoC face at 13.86; boss 5.4 tall on the 8 mm plate, 0.5 pad. Deck at 19.48 as built (the motor top and the Pi's back both allow it). Everything above is identical: **40.3 with the pad**, the same as A″.

Thermal credibility at ~4 W (ASSUMED coefficients): pad 0.3 K/W, boss negligible, plate spreading 0.65 K/W (8 mm; 1.0 at 5 mm) → SoC ~4 K above the plate; the plate is ~10 K above the room at 4 W total (6.9) → **SoC ≈ room + 15 K: credible, and silent.** At 12 W stress the Pi throttles at 85 °C long before the object does; acceptable for a desk prototype. Cost: a machined boss, two plate holes, the Pi's sockets facing down (the micro-SD slot is then on the visible back face — convenient), and a thermal-pad thickness that must absorb the boss-to-SoC tolerance (use 1.0 mm, ASSUMED). Gain in height: **none**. A″ (the heatsink without its fan) is built because it needs no new parts; B is the fallback if the first print's temperature log says so, and production's principle.

### 8.5 Production — the same object with a Compute Module 5

CM5 SoC-down on a plate boss (4.17 numbers): plate top 8.0 → pad 0.5 → SoC 2.2 → module PCB 1.24 → 4.0 stacking connector → carrier 1.6 → carrier top-side parts 4.0 (ASSUMED) → carrier top at 21.5. No deck, no adapter, no ribbon, no Pi window; the boards mount to the plate (carrier flat to the aluminium with the compute module's boss through a masked pad, the converter and the motor driver on gap pads — thermal plan rule 15), and the structure gains the lid of rule 14. Panel back parts from 22.0 → glass back 23.5 → glass, lens, fingers, gap, lip as v10 → knob top 32.4, **overall 33.9 mm**; 31.4 with the 1.5 mm stacking connector if the carrier's underside allows it. The motor stack (top 18.2) is then 3.3 below the deciding layer — the carrier and the CM5 decide, and a thinner carrier assembly (parts on one side only) would bring the product to ~30.

---

## 9. What is v10-only and what is production

| v10-ONLY | PRODUCTION |
|---|---|
| Raspberry Pi 5, the Active Cooler's heatsink, the plate window, the deck and its legs, the servo on the deck and the tall carriage tab, the HDMI adapter, the HDMI ribbon, the internal USB-C and USB-A cables, the header power housing, the bought converter module, the touch-controller board as a separate item, height 40.3 | Ø175.4 knob and its lip/chamfers/knurl, bore Ø145, the panel and lens bonded to the seat, the wheel/motor/servo/encoder radii, the halo at r 73.3, the 8 mm plate and its rear slot, the three rear openings and the 12 V barrel choice, the perimeter ports and the vent answer, the audio and motion functions (on the carrier), the CM5 boss principle, height ≈ 34 |

---

## 10. Rules for building the v10 CAD once agreed — v9's ten rules, plus

11. Every plug body (barrel, USB-C, 3.5 mm, micro-HDMI, HDMI-A, USB-A, header housing) is a named `_ENVELOPE` body in the assembly, in its inserted position.
12. Every cable is a swept body along its modelled route with its bend radius as a parameter, and the checker tests it against the carriage sweep, the bell and the wheels at knob angles 0/17/45/73° and both clutch states.
13. The checker proves the display module's insertion path (a straight drop through the bore), the structure's entry from below, the encoder board's drop into its slot, the nuts in their pockets, and the deck and Pi screws' tool paths. `printcheck.py` reads every printed part in its print orientation and lists every downward face off the bed, every bridge with its span and every sideways hole — the print list in `V11.md` is its output.
14. The parameter block carries `PLATE_T` and `COOLER_FAN_FITTED` as switches; the deck layout is five azimuth/radius pairs.
15. Drawings: A3, one sheet per made part, the first sheet listing every ASSUMED number.
