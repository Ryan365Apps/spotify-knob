# the 60 — version 14 specification

**Status: as-built specification for the v14 CAD.** This document describes every component and mechanism the v14 model contains, says which numbers are measured and which are assumed, grades every requirement, and separates what is true of the v10/v11 prototype only (Raspberry Pi 5) from what carries to production.

Revision: 6 September 2026 (late) — v14 = v13 plus **the design-changes list** (`the60-design-changes.md`): Pico-Lock connectors at 2.0 mm, the core's internal faces bare, the grounding features (chassis bond, rim-ring bond screw, motor bond lead, the knob's 1 MΩ bleed, the USB-C shell wire, the port face stated as an insulator), the halo current from the strip as built, the plain rim edge with the intake grooves opened to 514 mm², the vibration actuator's pogo-pin board and the rotor sensor lead's service loop. v13 was v12 plus **the encoder facing up at a code ring on the crown's underside** (Ryan, 6 Sep): no code band on the bore, no tower, the bell band back to its full contact, the wheels straight above it, the seat set by the adapter's HDMI socket at 26.0, height 35.9. v12 was v11 plus Ryan's deck-less layout: no mezzanine deck, every board on the plate, the display adapter's driver board on the Pi's standoffs, the code band and the wheels dropped to the bell band's limit, the seat 2.4 lower. Two facts from the adapter's datasheet (fetched this revision) are folded in: its holes are the Pi's 58 × 49 pattern, and the adapter is three parts (driver board, 150 mm flat cable, display connect board) — v10 and v11 wrongly had the panel flex reaching the driver board. Superseded text has been removed, not struck through. The v11, v12 and v13 documents stay in `docs/v11/`, `docs/v12/` and `docs/v13/` as delivered.

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

**Finding 2 (v10) — superseded in v12.** v10 found that the Pi 5, the display adapter and the motor sector could not share one floor inside a Ø145 bore and built a mezzanine deck. Two things changed: the bore is Ø166.4 (finding 1), and the adapter's datasheet shows its mounting holes are the Pi's own 58 × 49 pattern, so **the driver board stands on the Pi on standoffs** and needs no floor of its own. v12 is **one level** (Ryan, 6 Sep): everything bolts to the plate; the adapter is the one part off that plane, on the Pi.

**Finding 3 (v10) — what still holds.** The Pi's tallest features are its stacked USB-A sockets at 16.2 above the board (MEASURED) and standing the Pi through a window in the plate is what removes height. **The cooler's fan is not fitted**; in v12 the adapter's underside is 1.2 mm over the heatsink's fins, so a fan has no room at all — the first print measures the passive Pi (section 6.9). **What sets v13's height is the adapter's HDMI socket** (23.68 + 0.3 + the 2.0 seat flange = 26.0). In v12 it was the wheels: their groove had to sit above the code band on the bore, and the code band above the bell band's contact zone, which starts at the knob skirt's bottom (14.9, over the halo's lip) — seat 28.0. With the code ring on the crown's underside the groove only has to clear the band, which would allow 24.2. Seat 26.0, knob top 34.4 — 4.8 below v11 (section 8.3).

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
| Height | derived: **35.9** v13 with the pad (knob top 34.4; v12 37.9, v11 40.7); **34.1** production with the CM5 (the wheels' floor); the stack and what decides it are in section 8 | report | brief |
| Mass | more is better; the three-piece plate ≈ 498 g (steel rim ring 334 g at the largest radius) — see 4.16 | SHOULD | brief; 4.16 |
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
| A **seat** on top of the structure wall (r 62–82.8, top face z 26.0) that the display module **bonds to** with a 0.5 mm double-sided foam tape (ASSUMED) under the glass edge at r 62.5–65.6 — the glass never rests on a hard edge; the module comes off by peeling the tape | the panel has no holes; the knob must not hold it; glue is allowed for the display (Ryan, 5 Sep). A screwed carrier ring was designed and dropped: under the glass it can only be 1.5 mm thick and outside the glass the wall is 0.2 mm away, so it has nowhere for threads | MUST |
| A **32 × 2.5 mm slot** through the seat at 0° (offset 4 mm) for the panel flex and the touch tail, edges radiused 1.0 | the flex runs out past the glass edge and drops through here to the display connect board under it | MUST |
| Centring: three Ø2 nubs on the seat at 60/210/330° locate the Ø132.2 glass to ±0.15, under the lens overhang | the picture must be concentric with the knob within the 0.7 mm the lip hides | MUST |
| The knob's bore clears the chin corners by 0.45 (Ø145.0) | finding 1 | MUST |

**Gaps:** the exact chin outline is the STEP's; the datasheet's 66.10 dimension at the bottom does not match the STEP's 31.04 flat — the STEP is used, verify on the real glass (GAP). Whether the panel can be bought bare in ones (Ryan's question — see 4.4 for the fallback).

### 4.2 Cover lens with bonded touch sensor — specified separately (PRODUCTION)

**No CAD body. ASSUMED throughout:** round, **Ø140.0**, 2.5 mm thick, black-printed border from the picture edge outward, bonded to the panel's front face by its supplier (a perimeter adhesive gasket or full optical bonding — that bonding is part of a bought sub-assembly, not glue in the 60's assembly). The touch sensor's tail is a second FPC, ASSUMED 8 mm wide, exiting at the same edge as the panel's tab. The lens overhangs the Ø132.2 glass by 3.9 all round except at the chin, which stays exposed.

Why Ø140 and not 135: the seat's locating nubs sit under the lens overhang, and The lip hides everything outside Ø128.4, so the lens border (r 64.2 to 70) is invisible. Range acceptable: Ø135 to Ø140.5 (the structure wall's inner face is r 70.5).

**Gaps:** every number above. The lens is a question for its supplier; this specification only fixes what the knob and the structure need from it: outside diameter, thickness, border width, tail position.

### 4.3 DisplayModule HDMI-to-DSI adapter DM-ADTTR-014 (v10-ONLY)

**No CAD body; drawn from its datasheet** (`DM-ADTTR-014_datasheet.pdf`, section 1.5.1, fetched 6 Sep). PUBLISHED: a **kit of three parts** — "one driver board, one FPC cable, one display connect board". Driver board 65.0 × 64.0; four Ø2.8 holes 3.5 from the HDMI edge and from both sides, 11.5 from the flex-connector edge — **the Raspberry Pi's 58 × 49 pattern**; HDMI-A socket 15.7 wide × 10.5 deep, centred 0.5 off the board's middle on the HDMI edge, 0.8 proud of it, **7.3 tall**; micro-USB 5.5 × 5.7 beside it (20.25 over); 60-pin 0.5 mm flex connector 35 wide × 4.5 deep, 1.2 inside the opposite edge; two 3.6 × 6 buttons on the left edge (4.1 tall); 4.5–5.5 V supply. Flat cable 150 × 30.6 × 0.34. Connect board: photographed, not dimensioned — ASSUMED 30 × 46 × 1.2 with corner holes, CN2 for the panel's flex on one long edge, CN1 for the 60-pin cable on the other. ASSUMED on the driver board: 1.6 board, 2.5 of general parts, 1.0 of underside parts, the connector 2.0 tall.

Where: **the driver board on four M2.5 × 12 hex standoffs on the Pi's holes**, its left edge on the Pi's SD end (x −52..13), its HDMI edge over the Pi's HDMI edge (y −38, both sockets facing 270°), its flex-connector edge toward 90° overhanging the Pi's header edge by 8 (y 18–26, 0.28 above the servo's frame). Board 14.78–16.38; underside 1.2 over the heatsink's fins; HDMI socket top 23.68 — the tallest thing under the seat and, in v13, what sets it (26.0). The touch controller stacks on it at (−33, −17) on 3 mm standoffs. **The connect board** lies on a printed bracket over the port slot at (60.5, −4), r 45.5–75.5, z 13.0–14.2, its CN2 opening outward 8 mm from the panel flex's drop line at t −12 (the flex comes down at r 67.9, passes 1 mm over CN2, folds down at r 77 and enters it) and its CN1 opening inward; the flat cable runs inward at 15.2, up beside the Pi's USB-A shells, over them at 19.5, folds 45° toward 90° over the servo, Z-folds back toward 270° one width across and drops onto the driver board's connector — about 95 of the 150 mm used, the rest slack. **Why not flipped** (Ryan's suggestion): the socket would hang into the space over the Pi's SD end and the cable would have to enter a downward-facing connector. In v13 the socket does set the seat, so a flip would now buy 1.2 mm (the touch board on the adapter becomes the ceiling at 22.4, seat 24.8) — question 19, not built. **Gap:** measure the connect board and confirm its CN2 mates with this panel's 45-way 0.3 mm flex (GAP; the bracket's bosses move to its real holes).

### 4.4 If the bare panel cannot be bought

State it plainly rather than enlarge the object: v10 is built with a **dummy display disc** — a printed Ø132.2 × 1.98 plate with the same chin and FPC tab (from the STEP) and a Ø140 × 2.5 clear acrylic lens — so every mechanical proof in section 7 still happens, and software runs on the Waveshare bench display. The dummy is one line in the parameter block. Nothing else changes.

### 4.5 Raspberry Pi 5 (v10-ONLY)

Body: `vendor/rpi5/rpi-5b_no_graphics.step`, MEASURED: board 85 × 56 × 1.28; four Ø2.7 holes at (3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5); two stacked USB-A pairs 16.2 above the board top at x 70–88 (overhanging the board edge by 3.1); Ethernet 13.3; SoC 16.9 × 16.9 at x 24.7–41.6, y 14.3–31.2, top 2.34 above the board; USB-C at x 6.7–15.7 on the y = 0 edge, 3.29 tall; two micro-HDMI on the same edge; 40-pin header along y 50–55, x 7–58, 8.5 tall; micro-SD slot 1.45 below the board. Where: in the plate window, long axis along 0°–180°, USB-A/Ethernet end toward **the rear (0°)**, USB-C/HDMI edge toward **270°**, header edge toward 90° (the motor side); **at (−52, −38)** — v12: 9.5 further from the ports and 10 toward 270° (Ryan's layout; his picture had it ~35 over, which puts its corner outside the wall), its far corner at r 64 inside the duct; board 1.5–2.78, **carried by four lands of the closing plate** (4.16) on 0.5 washers, M2.5 × 6 countersunk from below into the standoffs that carry the adapter (4.3).

Provisions: the plate window (with notches for the USB-C plug's head, the HDMI plug and the rear USB-A plug); the closing plate's four lands; four M2.5 × 12 standoffs (PUBLISHED, 5 across flats); a 2 × 5 crimp housing on header pins 1–10 (5 V, GND, UART — a plain two-wire serial link) for the motion board (4.13), 9 tall on the header — the adapter's underside is 0.5 above it; the internal USB-C lead to its USB-C socket (6.8) — **an up-angled plug** (ASSUMED head 12 × 12.5 × 6.5 beyond the edge, lead straight up): a straight plug reaches r 75 through the ring at the new position and a right-angled one collides with the HDMI plug; the HDMI ribbon from its **HDMI1** socket (4.15; HDMI0 sits behind the USB-C plug's head); the audio board's USB in the upper rear USB-A socket through a right-angle plug (ASSUMED 9 mm protrusion). **Gap:** feeding 5 V on the header while the PC's USB-C is plugged in parallels two 5 V sources — see question 6 (VBUS (the USB cable's 5 V wire) cut in the internal cable, or an ideal-diode on the header feed).

### 4.6 Raspberry Pi Active Cooler — heatsink fitted, fan not (v10-ONLY)

**No CAD body.** PUBLISHED (product brief, verified this revision): 63.50 × 42.50 footprint, **13.70 total height** from the heatsink's underside to the fan's top, fan 30 × 30, 1.09 CFM (cubic feet per minute) (0.51 L/s) maximum, 8000 rpm, temperature-controlled from the Pi's fan header, push-pin mounted, not designed for removal. The brief's "30" that read as a height is the fan's footprint. ASSUMED: the heatsink underside sits 2.8 above the board (SoC 2.34 plus pad); the fins' top 7.0 above that (ASSUMED split of the 13.7) = **z 12.6**; the footprint from Pi x 2.5 to 66, between the USB-C edge region and the USB-A shells. **The heatsink is fitted and the fan is not** (finding 3): in v12 the adapter's underside is 1.2 mm above the fins (with 1.0 of underside parts assumed), so the fins' air leaves sideways under the board; the SoC cools by the fins into the cavity. Adequacy: V12.md bench item 1 — if it throttles, 15 mm standoffs (the seat allows 2.3 more) or option B (8.4).

### 4.7 Motor, carriage, servo, wheels, encoder, LRA, speaker — carried from v9

MY-3514C on its 4.2 mm carriage through the plate (stack case B, unchanged: motor z 4.2–18.2, bell from z 8.5 ASSUMED); AGFRC servo pushing the carriage, 2.4 mm lift; three 623ZZ V-collars on eccentric bushes; AEDR-8300 on a 0.15 recessed code strip; Vybronics LRA; Soberton SP-4005-1 cone-up; TMC6300 and MT6701 in the carriage. What changes with the bore at r 72.5:

| Item | v9 | v10 |
|---|---|---|
| Motor centre, engaged | r 40.5 | **r 55.0**; released r 52.6 |
| Drive ratio (bore Ø / bell Ø) | 3.31 : 1 | **4.14 : 1** — 60 knob detents are 14.5 per motor turn, not a whole number, so the detent is rendered from the knob's encoder, as v9 already intends |
| Motor azimuth | 90° | 90°; **the servo lies on the plate** at r 19–40.4 inboard of the carriage, in a floorless printed frame (two ears, M2.5 into the web), and pushes a **3 × 10 tab 14.5 tall** on the carriage (v11: 28.5, through the deck); same 2.4 mm lift, same 2.4 N |
| Wheel centres | r 51.7 | **r 67.1**, azimuths **30 / 150 / 270**; the wall gets three 15 × 5.4 windows so the wheels reach through it into the groove |
| Wheels z | 23.4–27.4 | **19.5–23.5**, groove 19.9–23.1 (2.1 above the drive band — v13: nothing else on the bore), collar tops 0.5 under the seat flange |
| Code band | 18.4–22.6 on the bore | **none on the bore.** v13: a code RING in a 0.15 recess in the crown's underside, r 72.5–79.5 (a stuck film ring on the prototype; laser-ablated stripes in the anodise on the machined knob), read by the AEDR-8300 lying on a 0.9 boss on the seat flange at **310°**, r 76, facing up at its 2.0 mm gap — the sensor's native codewheel arrangement. The bell band is back to 9.0–17.8, met by the bore over 14.9–17.8 |
| Code pattern | 364 mm strip | a 478 mm ring at r 76 — about 6,000 lines per turn at the AEDR-8300's 0.08 mm pitch (PUBLISHED 318 lines per inch) |
| Speaker | floor at 180° | plate at **(−36, 47)** — az 127.5, r 59.2, the quadrant beyond the adapter's edge (Ryan's "35°"), cone-up; boxed in: 1.0 beyond the adapter's edge, 3.1 off the bell and its band, its cradle ring 1.5 inside the wall, 6 off the pillar at 160; the cradle's fingers at 92/212/332° and ears at 200/290° from its centre, M2.5 from above |
| LRA | 258° | 258°, on the structure at the wall. **Its vendor warns against soldering to it** (`SYSTEM-REVIEW.md` 6.1): v14 gives it a **pogo-pin board** — 7 × 8 × 1 (ASSUMED) in a printed clip on the wall's inside at 252.5°, two ribs with a 0.4 groove each, open-topped, the board dropping in from above; two pins (ASSUMED Ø1.5, 2.2 compressed) on the pads of its flex tail at z 11.75 and 14.35 |
| Rotor sensor lead | — | the MT6701 rides in the carriage, which moves 2.4 every clutch cycle (`SYSTEM-REVIEW.md` 6.2): **a flex-rated lead** (a life requirement: 10⁵ cycles at 2.4 mm, ASSUMED) leaving the shoe through a 2.4 × 2.2 notch in its inboard wall, up through a notch beside the plate's tab slot (t +6, between the tab and the servo frame's wall), a **12 mm service loop** over the servo's frame, into the motion board — modelled |

### 4.8 Halo — a bought addressable LED strip on the wall (PRODUCTION)

**Ruling (Ryan, 5 Sep evening): the halo is an off-the-shelf addressable LED strip stuck to the wall, not discrete side-firing LEDs laid flat on the plate** — that arrangement was accepted on paper in v9 but is not going to be built. The strip (ASSUMED **5 mm wide, 1.6 thick**, ~100 LEDs per metre → 46 LEDs; any 5 mm WS2812B-2020 / SK6812 strip) stands vertically on a 1.1 mm thick band on the outside of the structure's wall (r 72.1–73.2) from z 8.25 to 13.25, its LED face at r 74.9 firing outward into the diffuser (r 75.1–77.0, 1.9 thick at the bottom). The band keeps the strip 0.2 outside the motor's bell + band (r 73.1); across the motor's relief sector (74–106°) the strip spans 40 mm with no backing, as a hoop. The halo band is z 8.0–13.5, the lip 13.5–14.3, the knob's skirt starts at 14.9. A wider strip raises the band by the difference. The strip's data and 5 V come from the motion board and the converter.

**Driven hard, in watts** (`HALO-BRIGHTNESS.md`, design-changes item 4): the WS2812B-2020 datasheet gives **16 mA per colour channel — 48 mA, 0.24 W per LED at full white**. The count follows the strip's radius as built and is computed in the parameter block (`LED_N = circumference × LEDs per metre`, `HALO_PEAK_A = LED_N × 48 mA`): at r 84.8 the strip is 533 mm, **53 LEDs, 2.54 A / 12.7 W at full white**. That peak sizes the converter, the halo's power feed and its connector. **There is no sustained brightness cap**: firmware limits a ten-minute rolling mean (2.0 W provisional), so full white is available whenever the user is interacting and nothing mechanical depends on the cap. The heat lands on the structure's wall — a PETG wall at 12.7 W for a minute is fine, sustained it is not, which is what the rolling mean is for.

### 4.9 Perimeter ports, port face, light sensor, USB-C receptacle, 3.5 mm jack, DAC (digital-to-analogue converter) — carried

Vents: **vertical slits** 1.0 wide × 4.5 tall (z 18.5–23.0, between the drive band and the seat) on a 2.5° grid all round the wall, 101 of 144 positions cut (the motor's relief, the pillars' and posts' webs and the LRA pad take the rest): 455 mm², passive (6.9). Ryan's review, 5 Sep: slits, not round holes. GCT USB4520 mid-mount USB-C receptacle (CAD body exists) on its small board — **its shell goes to the chassis bond by a short wire** (modelled: up out of the slot, under the connect bracket's slab, to the bond's ring terminal; `GROUNDING.md` 6); Switchcraft 35RAPC4BH3 3.5 mm jack (CAD body exists) — **its shell MUST stay isolated from the chassis** (it is the audio board's only outside-world ground reference; if it reaches the plate the object hums), which is why **the port face is, and must remain, an insulator — a printed plastic part; a metal port face is not permitted** (`GROUNDING.md` 6, a stated requirement, not an accident of the print); VEML7700 light sensor on its tiny board behind a Ø4.8 hole. The ES9219Q DAC moves from the jack board to the audio board (4.12); the jack board becomes a plain jack carrier.

### 4.10 Barrel power jack — CUI PJ-063AH (PRODUCTION, part proposed)

**No CAD body yet** (Same Sky offers one — fetch it before CAD). PUBLISHED: 2.0 mm centre pin (5.5 × 2.1 plug), **24 V 8 A** rated, right-angle through-hole. ASSUMED body 14.4 × 9.0 × 11.0, socket axis 6.5 above its board. Where: rear port slot, at 0° −15 mm tangential, on a small **vertical** board (tangential plane) so the barrel's axis height is free — axis at **z 3.5**, the plug body from z −0.75 to 7.75, under the halo's bottom edge (z 8.0) by 0.25 and into a through-pocket in the pad. Why a barrel and why 12 V: section 6.8. Plug body: a **right-angle 5.5 × 2.1 plug, Ø8.5 body** (ASSUMED) — a straight moulded plug on a 12 V brick is Ø10–11 and does not fit under an 8 mm plate's top edge; the cable leaves the object sideways along the rear wall.

### 4.11 12 V → 5 V converter board (PRODUCTION as a function; v10 as a bought module)

**No CAD body.** ASSUMED: a 5 V step-down module 38 × 25 × **8** — its rating is set by the whole reworked budget, not by the halo (design-changes item 4: the halo's 2.54 A no longer justifies a 10 A part on its own; size it from the measured inlet load, bench item), about 6 A — **on the plate** (thermal plan rule 15) in the front crescent at az 180°, **tangential** (38 along the arc), r 53–78 — its inner edge 1.0 clear of the adapter's edge at x −52 (the module's top is 1.7 above the adapter's underside), its outer 6 mm on the ring's flat top — standing on a 0.5 mm thermal gap pad over a masked bare patch of the anodising, two M2.5 × 4 into tapped blind holes in the web (the module's holes ASSUMED at ±16 on its centre line). Feeds: the Pi's header (5 A peak), the halo (up to 4 A), the adapter, the audio and motion boards. The motor driver stays on 5 V (the TMC6300's PUBLISHED maximum is 11 V).

### 4.12 Audio board — XMOS USB audio + ES9219Q (PRODUCTION as a function)

**No CAD body.** Ryan's envelope: **25 × 40**; 1.6 board + **2.0 mm Molex Pico-Lock 1.50 right-angle connectors on its edges** (`CONNECTORS.md`: one family for every crimped link, 2.00 mated, 30 cycles) and the 4.0 mm moulded plug of its pre-made USB lead, M2.5 corner holes. Where: **on the plate at (19, −52)** (40 along x, 25 along y), the 270–300° crescent beside the Pi's USB-A end, on 1.0 washers with M2.5 × 4 into tapped blind holes; its outer corner (r 75.7) sits on the ring's top. Ryan drew it central beside the speaker; that spot is the Pi's board at the new position, and beside the USB-A end its USB plug is 9 mm away. Connections: USB to one of the Pi's USB-A sockets (an internal USB-A-to-USB-C cable, ~120 mm, plug body 15 × 6.5 × 20 at the Pi's front end — drawn); line out to the 3.5 mm jack board (3-wire JST-SH); the speaker (2-wire, the XMOS drives a small class-D on this board — the speaker amplifier is the board's, the 3.5 mm output has none). The lens's touch controller board (if the sensor supplier gives one) stacks on the adapter at (−33, −17) on 3 mm standoffs, 4.12a: ASSUMED 30 × 20 × 3, USB to the Pi.

### 4.13 Motion board — microcontroller for motor, encoder, LRA, servo, LED ring (PRODUCTION as a function)

**No CAD body.** Envelope as built: **30 × 30 × 3.6** (the TMC6300 driver, a DRV2605L, the microcontroller, **2.0 mm Pico-Lock right-angle connectors on its motor-facing edge** — v13 allowed 5 mm JST-SH, and the JST VH / Micro-Fit named elsewhere at 10–18 mm were never going to fit) plus the 4.0 mm moulded plug of its pre-made USB lead on its rear-facing edge. It also lands the **motor frame's bond lead** (a ring terminal under the motor's inboard base screw, modelled) and the knob's 1 MΩ bleed lead — the first draft proposed 50 × 40; 30 × 30 is what the plate's rear sector holds. Where: **on the plate at az 50°, r 37–67** (Ryan's "140°" is the model's 40; 50 clears the Pi's USB-A shells by 0.7 and the connect bracket's ear by 2), over the 22–52 rear plenum, on 1.0 washers with M2.5 × 4 into tapped blind holes, so the four short cables (motor phases, commutation sensor in the carriage, servo, encoder on the seat flange) run a few centimetres. Talks to the Pi over **UART on the 40-pin header** through the same 2 × 5 housing that brings 5 V in — one plug, no internal USB cable for motion (ASSUMED; a USB alternative is question 9). The LED ring's data line comes from here; its 5 V comes from the converter directly (4 A does not go through a signal board).

### 4.14 Mezzanine deck — gone in v12 (Ryan, 6 Sep). See 5.4 for what replaced it.

### 4.15 Internal HDMI ribbon (v10-ONLY)

**No CAD body.** ASSUMED: a 20-way 0.5 mm pitch flat flexible HDMI cable, 200 mm, with a micro-HDMI **up-angle** plug board at the Pi end (12 × 8 × 5) and an HDMI-A plug board at the adapter end (21 × 12 × 6). Route as built (v12): from the Pi's **HDMI1** socket at z 2.8–7.8 on the 270° edge, up out of the micro plug, outward along 1 mm over the plate top to 3.5 beyond the A plug's tail, up to the adapter's socket height (20.0), and back into the A plug's tail — the two sockets face the same way 9 mm apart, so the ribbon is a loop of about 60 mm; three folds, all static, all modelled. A round moulded micro-HDMI cable needs a 25 mm bend radius and 12 mm plug bodies and does not route in this height; the ribbon is the design.

### 4.16 Base plate — the heatsink: aluminium core, steel rim ring, closing plate (PRODUCTION; `the60-thermal-plan.md` section 14 applied, Ryan's 6 Sep decisions: steel ring, converter on the plate, rear exhaust through the pad)

Three machined pieces, Ø175.4 flush with the knob, 8 mm at the rim, the object's height unchanged (rule 6).

**The aluminium core**, r < 75.2, 6082, **external faces black hard anodised; every internal face chromate-conversion coated or bare — no masked pads anywhere** (Ryan, 6 Sep, `GROUNDING.md` 4: masking five pads on sixty parts is fiddly and a pad that comes back coated is an invisible fault in the ground path; cost 0.048 W/K, 2.8 K passive). The closing plate's outer face stays black — it is the visible underside and radiates to the desk. In section: a **4 mm web** (z 4–8), a **3 mm duct** (z 1–4) and a **1 mm closing plate** flush in a recess (z 0–1), screwed on with six M2.5 countersunk screws that all land in solid web, so it comes off to clean the channels (rule 5). A rebate r 72.2–75.2, z 5–8 takes the ring's flange on a **5 mm shoulder** (v13: 4 — raised so the intake grooves can be 3.5 deep through it and leave 1.5); seven M3 countersunk screws from below through the shoulder hold the ring. **THE chassis bond** (`GROUNDING.md` 3, one and only one): an M3 tapped blind hole at (48, 27) on the free side of the port slot, with an external-tooth star washer and a ring terminal under the head; the production carrier's star point lands on it. **The rim ring's dedicated bond screw** (`GROUNDING.md` 4.1): M3 tapped 3.0 into the shoulder's top face at az 56.25, r 73.7. Through it: the Pi window (with notches for the USB-C plug's head, the HDMI plug and the USB-A plug), the carriage hole, the port slot from r 55 — each through-cut with a 2.5 mm solid wall round it so the duct does not leak into it. Into its top face: **16 M2.5 tapped blind holes 3.0 deep** (converter 2, audio 4, motion 4, servo frame 2, connect bracket 2, speaker cradle 2) and the chassis bond's M3 at (48, 27) — they stop 1.0 above the duct, so nothing above the web needs an island; only the six closing screws from below have Ø7 islands. On its top face, **two ribs 2 × 6 mm** at r 56–70 (az 158 and 212 — the plate top is nearly full; v11 had ten), inside r 70 so the structure still enters from below. Mass ≈ 139 g.

**The duct** (rules 7–12; the openings are parametric — `INTAKE_N/W/H/AZ0/AZ1`, `INTAKE_UNDERCUT_H`, `EXHAUST_AZ` — so the edge treatment chosen later swaps in without a rebuild): air enters through a **1.5 mm undercut on the bottom outer edge** outside the pad (r 84.7–87.7) over the front and sides, az 45–315 (620 mm² of mouth; the rear is closed); through **21 radial grooves 7 × 3.5** in the ring's underside and the core's shoulder (514 mm² of throat, inside the 500–700 mm² the design-changes list asks for; the pad closes them from below; the two grooves that would land on the motor's through-hole and the one at the USB-C plug's notch are omitted); into a **collector** r 66–70.2 round the front and sides; through **19 straight fin channels 3 wide × 3 tall on a 4 mm pitch** — twelve on the +y side and seven on the −y side of the off-centre Pi window, front to rear; into a **rear plenum** either side of the port slot (r 55–70.2, az 22–52 and 308–338); and out through **six exhaust grooves** of the same 7 × 3.5 section at az 28–44 and 316–332 (147 mm² — the exhaust is the restriction now, deliberately: rule 10 keeps it to the rear arcs) that open **downward where the pad is cut away** (az 15–46 and 314–345) — rear only, a different arc from the intake, not the socket slot (rule 10). **Two circuits in v12**: the Pi's USB-C plug notch reaches r 70.6 at az 231 and its wall severs the front collector, so the −y side (7 channels, 6 intake grooves at 242–298°, the 308–338 plenum, the exhaust at 319–333) is its own intake-to-exhaust circuit of 11.8 cm³ and the +y side (12 channels, 14 grooves, the 22–52 plenum, the exhaust at 28–44) is 19.8 cm³ — the checker requires each to have both. No opening through the top face or the edge face (rules 8, 9). A **blower envelope 28 × 18 × 5** is reserved in the 308–338 plenum at az 328, r 63 (where the air leaves) — 3 in the duct, 2 into the web; the part is **not fitted** (rule 12). What the geometry would not give: a 30 × 30 spot — the motor's through-hole and the Pi window rule it out everywhere — so the envelope suits a slim or 20 × 20 blower; and a single circuit, because the plug notch is fed mainly by its own three intake grooves.

**The steel rim ring**, r 75.2–87.7 × 8, mild steel (RULING 6 Sep: steel, for mass — ≈ 301 g at the largest radius; in aluminium it would be 104 g; **its finish is open**, and decides whether its bond spot is masked or the star washer cuts through): a **plain edge face** (design-changes item 5: the engine turning is removed — the vent grooves and the turning were two rhythms on one face; the replacement treatment is chosen separately) with **1.0 chamfers top and bottom**; the intake undercut and the intake and exhaust grooves in its underside; an inward flange r 72.2–75.2, z 5–8 onto the core with seven M3 tapped holes and, at az 56.25, r 73.7, **the Ø3.4 clearance for its dedicated bond screw** — an M3 from the top into the core's shoulder with an external-tooth star washer under its head and both faces bare, hidden under the structure, thread-locked (`GROUNDING.md` 4.1: bare steel on bare aluminium is a galvanic pair; the star washer's gas-tight point contact survives it; on the land between two intake grooves because the rear arc's lands round the slot are all taken by the exhaust grooves and the ring screws; 35 mm from the chassis bond); the structure's three plate screws at r 77.2 (countersunk from below); two Ø1.6 holes tapped M2 at r 78.2, t ±26 for the port face's rail; the port slot. Its inner radius is derived (rule 4): 3 mm inboard of the port face's fixing holes, well inboard of the diffuser's seat at r 85.8; it carries the halo's 8 mm and the plug bodies' 9 mm at the edge, which is the only place the object needs the thickness.

**The closing plate**, 1 mm aluminium, laser-cut, anodised: a disc r 72.1 with the same three windows as the core, six countersunk holes — and, v12, **four 9.5 mm square lands** reaching into the Pi window at the Pi's holes with Ø2.7 countersunk holes: the Pi and the adapter stack on it screw to these from below (the deck's legs that carried the Pi are gone).

Mass (rule 16): core ≈ 137 g + ring ≈ 301 g + closing plate ≈ 25 g ≈ **463 g**; all-aluminium ≈ 266 g; the v10 Ø154 steel plate was 660 g. Why 8 mm at the rim: the plug bodies at the rear must sit between the pad's underside (z −1.5) and the halo's bottom edge (the plate top), so the tallest plug body is plate + pad − 0.5 = 9.0 mm — a USB-C plug is 6.5, a 3.5 mm plug Ø6–8, a right-angle barrel Ø8.5. Why the duct is worth building even unfanned: it is an intake and a defined path, worth ~0.1 W/K passive, and it makes the blower a fitted-or-not decision after measurement rather than a plate respin (the plan's section 8).

### 4.17 Compute Module 5 (PRODUCTION only — not in v10)

PUBLISHED (datasheet, verified): 55 × 40, bare module 4.6 deep, PCB 1.24, SoC 2.2 tall, four M2.5 holes inset 3.5; mounted height 4.94 with the 1.5 mm Amphenol stacking connector or 7.44 with the 4.0 mm one; idle 0.4 A, load 0.9 A at 5 V; "less passive heat-sinking than a Pi 5 — any thermal solution must be designed". Section 8.5 uses it SoC-down on a plate boss with the 4.0 mm stacking.

### 4.18 Rubber pad — now a **plain 1.5 mm ring under the rim ring**, r 75–84.7 (0.5 lean to the desk), cut away at the port slot and at the exhaust arcs (az 15–46 and 314–345) so the exhaust grooves open to the desk; it closes the intake grooves from below and is no longer part of the airflow (thermal plan). The Pi is carried by the closing plate's lands, not by the pad. Screws, inserts, washers, standoffs, cables, code strip, display bonding tape, LED thermal tape, the converter's thermal gap pad — the pad, the display tape and the gap pad are the only adhesives (Ryan, 5 Sep). Hardware as built (v12): 4 × M2.5 × 12 hex standoffs and 4 × 0.5 washers (the Pi stack), 4 × M2.5 × 6 csk from below (Pi), 4 × M2.5 × 5 (adapter), 4 × 3 mm standoffs (touch board), 4 × M2 inserts + 4 × M2 × 4 (connect board on its bracket), **16 × M2.5 × 4 into tapped blind holes in the plate** (converter 2, audio 4, motion 4, servo frame 2, connect bracket 2 csk, speaker cradle 2), 8 × 1.0 washers (audio, motion), 2 × M2 × 4 (port face rail into the rim ring), 3 × M3 inserts in the structure's pillars + 3 × M3 × 8 csk (plate to the pillars), 7 × M3 × 8 csk (rim ring to the core), 6 × M2.5 × 4 csk (closing plate), 3 × 623ZZ.

---

## 5. Made components

### 5.1 Knob (PETG prototype; CNC 6082 production)

One piece, v10's shape scaled to the rim (Ryan, 6 Sep: "relatively similar in shape to the prior version, just with a larger rim"). **Ø175.4** outside, a **4.5 wall** (1.0 knurl + 3.5 under the root), the **3 mm lip** now 19 wide from its edge at r 64.2 to the bore; top rim 1.0 inner chamfer + 20.0 flat + 2.5 outer chamfer. ≈ 72 cm³: ≈ 90 g in PETG, ≈ 195 g in aluminium (v10: 50 cm³); inertia ≈ 1.7× v10's — re-tune the detents on the bench (section 7). Bore **Ø166.4** (the chin at r 72.05 is 11 mm inside it) straight from the skirt's bottom (z 14.9) to the lens level, with: the 90° V-groove for the wheels (root r 73.8, z 24.3–27.5); the 0.15 code ring's 0.15 recess in the crown's underside at r 72.5–79.5 (the bore is plain apart from the V-groove).5–22.7); the lip on top: inner edge **Ø128.4** (0.7 outside the picture), 3.0 thick, underside at z 35.78, top at **z 38.78**; skirt bottom at z 14.9; outer chamfer 2.5 at 45°, inner chamfer 1.0, skirt chamfer 1.2. Knurl: diamond, 1.0 deep, four whole rows as v9 (helix 37.4°, derived from the band height 16.9–35.5), **78 starts** at Ø175.4 to keep the v9 pitch (question 13); the grooves run out downward through the skirt's 1.2 chamfer (print review, 5 Sep: a flat knurl foot was 68 downward ledges when the knob prints top face down) and stop 0.8 under the top chamfer. Wall under the knurl root 3.5. The knob touches only its three wheels: 0.4 to the lens and the structure, 0.45 to the chin.

### 5.2 Internal structure (printed; PA12 production)

One part, as v9, scaled to the bore: a wall r 81.2–82.8 from the plate top to the seat; the **seat flange** at the top (r 62–82.8, z 24.0–26.0 — a 21 mm shelf; the glass bonds at r 62.5–65.6 as before) with the 32 × 2.5 flex slot at 0° and three Ø2 locating nubs at 60/210/330° — the display module bonds to it; three wheel posts Ø8 at r 76.9, az 30/150/270 (bush sockets open to the plate side), webbed to the wall, with a 15.2-wide window through the wall above each for the wheel and **the seat flange cut away entirely above each wheel** (print review, 5 Sep: nothing needed it, and it was a shelf hanging over the window — the glass bridges the three notches, the tape ring is unbroken); no encoder tower (v13): an 8.4 × 12.4 × 0.9 boss on the seat flange's top face at 310°, r 76, with two M2 inserts, on which the 8 × 12 encoder board lies sensor-up, 2.0 under the crown's code ring — the board is screwed on before the display goes on, its leads run inward over the flange; **the knob's bleed contact** (v14, `GROUNDING.md` 5): a 5 × 8 × 1 boss on the flange's top at 200°, r 74.5, with an M2 insert, carrying a phosphor-bronze leaf (ASSUMED 4 wide, 0.2 thick) that rises to bear lightly on the crown's underside at **r 71.5 — the smallest radius the knob offers** (the lens ends at 70, the code ring starts at 72.5), hidden, intermittent contact being fine for a bleed, wired to the chassis bond through 1 MΩ in the lead; the leaf's drag must not be felt (bench); **the LRA's pogo-board clip** at 252.5° (4.7); the motor's window in the wall open up to the seat flange (no roof to bridge); the LRA pad at 258°; the 1.1 mm band the LED strip sticks to (r 82.8–83.9, z 8–13.5) and the diffuser-retaining lip above it (r to 86.7, 13.5–14.3); **five Ø7 pillars at r 77.2, az 50/120/180/240/320**, webbed to the wall, with M3 inserts at the top for the deck's screws and, at 120/240/320, at the bottom for the plate's screws; 89 vertical vent slits 1.0 × 3.5 at z 14.7–18.2 on a 2.5° grid; the motor relief at 90°; the three blind plate-screw insert holes end in 45° points. No ledge, no display columns, no seat tabs, no carrier, and **no lid** (thermal plan rule 14): the deck's boards reach z 29.4 and the panel's back components start at 29.4, so there is no room for one in v11 — the bonded glass and the seat flange close the cavity; the lid arrives in production with the boards on the plate. **Printing**: upright on the wall's foot; supports only under the seat flange (a hidden ring inside the wall) and under the diffuser lip (a thin ring outside) — everything else is open-topped, a 1 mm bridge or steeper than 45° (`src/printcheck.py`).

### 5.3 Halo diffuser — carried, at the new radius: r 85.8–86.7 at the bottom leaning out to 87.7 at the top (Ryan's review: a more exaggerated taper), z 8.0–13.5, 0.5 chamfer on the outside top edge; sits on the rim ring 0.2 outside the strip, wholly on solid steel (the ring's top chamfer and groove floors start at r 86.7), retained by the structure's lip.

### 5.4 Connect-board bracket, and the Pi stack that replaced the deck (v10-ONLY)

The deck is gone (Ryan, 6 Sep). Two things do its jobs. **The Pi stack**: four lands of the closing plate (4.16) → 0.5 washers → the Pi → four M2.5 × 12 hex standoffs on its holes → the adapter driver board (4.3) → M2.5 × 5 pan heads; M2.5 × 6 countersunk screws from below through the lands into the standoffs. Every other board bolts to the plate's top face on 1.0 washers (4.11–4.13). **The connect-board bracket** (printed): a 1.5 mm slab at z 9.5–11 from r 46 to 78, t −29..+21, bridging the port slot; it rests on the port face's rail (z 9.5) at its outer end and stands on a 1.5 mm foot strip (r 46–48) and two countersunk ears (46, 17) and (46, −14) at its inner end (M2.5 × 4 into the web); four Ø6 bosses 2 mm tall with M2 inserts carry the connect board; its −y inner corner is cut back to x 45.5 because the audio board's USB-A plug sits there. Prints standing on its straight −y edge (slab vertical, feet and bosses sideways), no supports.

### 5.5 Display seat (PRODUCTION) — the display module's interface to the structure

The seat flange of 5.2, with the bonding tape (4.1). No separate part. The display module (lens bonded to the panel by its supplier) is placed lens-down in the inverted knob and the structure is lowered onto it with the tape on its seat; the three nubs centre the glass. Cost in the stack: 0.5 mm of tape. Replacing the display means peeling it off the seat — acceptable for v10; production can revisit a clamp ring if a tool-free swap is wanted.

### 5.6 Carriage, servo tray, speaker cradle, port face, V-collars ×3, eccentric bushes ×3 — carried from v9 with the new radii. The carriage's push tab is 3 × 10 × 14.5 tall (v11: 28.5 — the servo is beside it on the plate now; rooted to the shoe; printed standing, the tab is loaded across its layers — PETG, 4 perimeters); the servo lies on the plate inside a **floorless frame** (walls 1.0, 6.5 tall, open toward the tab, a lead notch in its end wall, two ears at t ±12.5 for M2.5 × 4 into the web); the speaker cradle's three snap fingers stand from the plate (full height, so they print without support and flex more), its two ears are placed by azimuth from the speaker's centre (200° and 290°) and take M2.5 × 4 from above; the port face (44 wide, three sockets) stands at the wall's inner face, r 79.7–81.2 (the sockets 6.5 inside the edge, as v10's proportion), with a 1.5 mm rail along its top (flat-fronted, corners cut at 45°) screwed to the rim ring beside the slot, inside the wall (2 × M2 into tapped holes at r 78.2, t ±26 — v10's ears sat over the slot's void); the 3.5 mm jack stands on its 16 × 12 board with the pins down into the pad's void (in v10 the board sat under the wall and the LED strip); prints lying on its outer face so the socket holes are vertical. The three eccentric bushes print stem down (the 1 mm flange ledge is their only overhang); the collars axis-vertical.

### 5.7 SoC boss (option B only, and production)

Aluminium, Ø26, height from the plate top to 0.5 below the SoC's face (v10 option B: 5.4; production: set by the CM5 stack), two M3 countersunk from below the plate, a 0.5 mm thermal pad on top. Not in v10 as built (A″); it is the fallback if the fanless heatsink runs hot (V10.md bench item 1).

### 5.8 Boards — 4.10 (jack carrier), 4.11 (converter, bought), 4.12 (audio), 4.13 (motion), USB-C board, light-sensor board, encoder breakout, commutation board, LED flex — outlines exported as v9.

---

## 6. Mechanisms

### 6.1 Knob suspension, 6.2 detent and drive, 6.3 clutch, 6.4 angle sensing, 6.5 commutation — as v9 with the radii in 4.7. The drive ratio 4.14 : 1 raises the motor's speed for the self-turn and lowers the torque the knob feels by the same factor: a 2.4 N band grip at r 72.5 is 0.17 N·m at the knob (v9: 0.10) — better, not worse.

### 6.6 Display — how the panel is held and driven

Held: bonded to the structure's seat (4.1, 5.5), centred by the seat's nubs; the knob never touches any of it. Driven (v10): Pi HDMI1 → ribbon (4.15) → adapter driver board (4.3) → 150 mm flat cable → display connect board → the panel's 45-way flex, which runs on the glass back to the tab edge at 0°, out 1 mm past it, down through the seat slot to z 15.7, 1 mm over the connect board's CN2 to r 77, down and back into it (bend radius 1.0, four static folds, total run about 27 of the 45.8 mm available; the slack loops in the cavity). Touch: the lens's sensor tail → its controller board on the adapter → Pi USB. Production: the CM5 carrier's DSI output straight to the flex, ±5 V and the 37 V backlight driver on the carrier, no adapter, no HDMI — that carrier needs a Linux panel driver with the HX8399-C initialisation sequence from DisplayModule (a software task that must happen for production regardless; question 3 asks whether to do it now and skip the adapter, which would take the mezzanine out of v10 and about 2 mm off its height — the fan's intake plenum then sets the height, not the boards).

### 6.7 Audio — speaker on the audio board's amplifier; 3.5 mm line out unamplified; both on the audio board; the jack carrier at the rear is passive.

### 6.8 Power and the three rear openings

**Proposal: a 12 V, 5 A external brick (**Class II, two-pin, double insulated**, with a stated leakage figure — `GROUNDING.md` 3: an earthed brick would give the object a second earth reference through the audio cable) into a 5.5 × 2.1 barrel jack, and a 5 V step-down inside sized from the measured budget. Preferred over a USB-C inlet feeding the Pi's 5 V pins.** Why:

1. The 5 V budget. Pi 5 up to 5 A (PUBLISHED supply rating; the board alone ~2.4 A under stress, ASSUMED), halo 2.54 A at full white (4.8, computed from the strip as built), adapter + panel 0.6 A, motor up to 2 A through the TMC6300 (PUBLISHED driver limit), servo 0.5 A, audio 0.3 A: **8–10 A worst case, ~2 A typical**. A 5 V 5 A USB-C brick (the 27 W one Ryan has) cannot cover the worst case, and a barrel pin is rated 5 A at any voltage, so 5 V cannot come in through a barrel either. 12 V in at 5 A is 60 W and covers everything with margin.
2. Two USB-C sockets side by side at the rear invite the wrong cable in the wrong hole; a barrel is unambiguous. A USB-C power inlet at 12–20 V needs a power-delivery negotiator board and still needs the step-down; it saves nothing.
3. A 12 V rail is available for anything that wants it later; the TMC6300 motor driver is not one of them (PUBLISHED maximum 11 V), so the motor stays on 5 V as in v9.

The Pi is fed on header pins 2/4/6 from the converter (v10-ONLY; production feeds the CM5 carrier directly). The Pi's USB-C stays for the PC (USB gadget mode). **Gap:** the PC's 5 V on that USB-C parallels the header feed — question 6.

The three openings, in the 44 × 30 slot through the plate at the rear, left to right seen from behind, all with their plug bodies drawn: **barrel** at −14 mm (right-angle plug, Ø8.5 body, cable leaving sideways along the wall), **USB-C** at 0 (GCT receptacle on its horizontal board; plug body 8.3 wide × 6.5 tall × 25 long, cable straight back), **3.5 mm** at +12 (Switchcraft jack; plug Ø6–8, straight). Plug axes at z 3.5 (barrel), 4.5 (USB-C), 4.0 (jack). Every plug body must lie between the desk (z −1.5) and the halo's bottom edge (z 8.0) where it passes under the diffuser at r 74.5–77: the barrel body spans −0.75 to 7.75 and needs a **15 × 20 through-pocket in the pad** under it (the plug hangs 0.75 above the desk); the USB-C body 1.25–7.75; the jack body 0–8.0 with a Ø8 plug, comfortable with Ø6. On a 5 mm plate none of the three closes without a notch in the halo. Alternatives to the pad pocket: notch the halo over ±8° at the barrel, or a 10 mm plate (1.4 kg). Question 5.

### 6.9 Cooling — the base plate is the heatsink; the perimeter slits are acoustic only

Replaces the v10 vent analysis (`the60-thermal-plan.md`). The sustained load is 12–14 W and the object's passive skin is worth about 0.4 W/K; IEC 62368-1 caps a bare-metal knob at 48–51 °C in a 25 °C room; the knob is the largest surface and the one surface that may not be made hot, and it sits close to cavity temperature whatever the structure does (1.6 mm of PA12 plus the 0.4 running gap is ~0.4 W/K of coupling through the bore). So the heat goes down, into the plate, and out under it.

**Two forced paths, entirely below the plate's web** (one each side of the off-centre Pi window, severed from each other by the USB-C plug's notch): room air → the 1.2 mm undercut on the rim's bottom edge (front and sides) → 21 grooves under the rim → the collector → 19 fin channels → the rear plenums → six exhaust grooves opening downward at the rear where the pad is cut away. The web has no holes; the forced stream never enters the cavity, never passes the panel or the encoder. **The 101 perimeter slits (z 18.5–23.0, above the drive band) stay the speaker's acoustic port and nothing else**; the cavity breathes through them by buoyancy only. What the plate buys: black anodising takes the plate's emissivity from ~0.25 (steel) to 0.88 on both faces — the underside radiating to the desk and the top face to the cavity; aluminium spreads four times better, so the plate runs near-isothermal; the ribs reach 6 mm up into the warmer stratified air; the converter conducts straight into the web through a gap pad. The plan's figures: **0.5 W/K passive** (against 0.4 today) — 48 °C skin at 13 W in a 22 °C room, 51 °C at the standard's 25 °C, exactly at the limit; **1.1 W/K with a blower** at ~1 L/s — 34 °C / 37 °C. Read the other way: for a 40 °C skin in a 22 °C room, 9 W passive or 19.8 W fanned. The blower's envelope is reserved and the part is not fitted; whether it is fitted is decided by measurement (section 7, items 8 and 9), and the passive route is a power budget — cap the halo and underclock the compute module to ~9 W sustained.

What the first print measures: the real load at the 12 V inlet through an hour of use; plate, knob and cavity temperatures on the passive build in a known room; and the ducted case with a bought blower taped into the envelope. The 4 W Pi keeps its heatsink in v12 (fan off, finding 3; the adapter 1.2 mm over its fins is bench item 1); in production the compute module's boss goes to the plate through a masked pad (8.5).

### 6.10 Assembly order — every step reachable, proven by the checker

The knob side, upside down: 1. Knob upside down, lip down, the code ring stuck into the recess in its crown's underside; a 0.4 shim ring on the lip. 2. Display module (lens + panel, bonded by its supplier) lens-down onto the shim, chin at 180°, flex tab at 0° — a straight drop through the bore (checker). 3. Internal structure, bonding tape on its seat, the encoder board screwed to its boss on the flange (sensor up, 2 × M2), **the bleed leaf screwed to its boss at 200° with its lead**, **the LRA's pogo board dropped into its clip**, lowered over the panel's back with the wheels retracted; the flex and the touch tail led through the seat slot; the seat pressed onto the glass — the display is now bonded. 4. Bushes half-turned from the plate side to seat the wheels; locked; shim out through the rim gap. 5. LRA onto its pad, the LED strip round the wall's band, the diffuser under the lip.

The plate side, the right way up: 6. Rim ring to the core (7 × M3 csk), **its bond screw from the top with its star washer, thread-locked**; closing plate into its recess (6 × M2.5 csk); **the chassis bond screw with its star washer and ring terminal** at (48, 27). 7. Pi with its heatsink onto the four lands on 0.5 washers, standoffs on, 4 × M2.5 csk driven from below (Ø6 paths clear). 8. Adapter driver board with the touch board stacked on it onto the standoffs, 4 × M2.5 × 5 (Ø6 paths from above clear); header housing; the ribbon from HDMI1 looped into the adapter's socket; the up-angled USB-C lead; the audio board's right-angle USB-A plug. 9. Converter on its gap pad, audio and motion boards on their washers, speaker into its cradle, servo into its frame with the carriage + motor + band through the plate and the tab at its pushrod; the port face with its four boards into the slot, its rail screwed (2 × M2); the connect bracket over the slot (2 × M2.5 csk) with the connect board on it (4 × M2); the flat cable from the connect board's CN1 over the USB-A shells and the servo to the adapter's connector.

Together: 10. The plate assembly lowered onto the structure, the panel flex into the connect board's CN2 (it passes over the connector and folds back in); 3 × M3 countersunk into the pillars at 160/240/320°; ground bond. 11. Pad ring on (its pocket at the barrel). Turn over.

Nothing is glued but the pad, the display's bonding tape, the converter's gap pad, the code strip and the LED strip's own backing. Everything reverses; the display by peeling.

---

## 7. What the first v10 print must prove

Every part fits — the panel (or its dummy), the Pi on the closing plate's lands through the plate window with the adapter on its standoffs, the boards on the plate, the servo in its frame beside the carriage, the connect board on its bracket over the port slot, the motor mechanism, the three sockets — with nothing touching that should not (checker); the display module and the structure go in on straight paths; the Pi's screws from below and the adapter's from above are reachable; the flat cable and the ribbon route as drawn.

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

### 8.2 Why one level now

v10's deck existed because the Pi, the adapter and the motor sector could not share a Ø141 floor. In v12 the floor inside the wall is r 81.2 (20,700 mm²), the adapter stands on the Pi (its holes are the Pi's), and the plate takes the Pi, the motor sector with the servo inboard of it, the speaker, the converter, the audio and motion boards, the connect board over the port slot and the sockets. The plate top is nearly full — two ribs survive of v11's ten — but nothing overlaps (checker) and nothing is above anything else except the adapter on the Pi and the touch board on the adapter.

### 8.3 v13 stack as built — one level, adapter on the Pi, encoder reading the crown, display bonded to the seat

| z | What | Cost driver |
|---|---|---|
| −1.5–0 | pad ring | |
| 0–8.0 | plate (closing plate 0–1 with the Pi's lands, duct 1–4, web 4–8); halo 8.0–13.5 (5 mm strip); lip 13.5–14.3; skirt from 14.9 | plate 8 (4.16); strip width (4.8) |
| 1.5–2.78 | Pi board on 0.5 washers on the lands | |
| 4.2–18.2 | motor on its carriage; band on the bell 9.0–17.8, met by the bore over 14.9–17.8 | v9 case B |
| 8–17.05 | boards on the plate: servo 8–14 (frame 14.5), audio to 14, motion to 16.4, converter to 16.5, speaker to 17.05, connect board 13.0–14.7 on its bracket | |
| 14.78–16.38 | adapter on 12 mm standoffs; its parts to 18.9, flex connector 18.4, buttons 20.5, **HDMI socket to 23.68**; touch board on it to 22.4; flat cable to 20.8 | **the deciding part**: 23.68 + 0.3 + the 2.0 flange = 26.0 |
| 19.5–23.5 wheels, groove 19.9–23.1; **24.0–26.0 seat flange** | the wheels alone would allow 24.2 | |
| 26.0–26.5 | bonding tape under the glass edge; the encoder's boss, board and sensor on the flange outside the lens (26.0–29.53, 2.0 under the crown's code ring) | +0.5 |
| 26.5–28.48 | panel glass 1.98 (its back components hang 1.5 below it inside r 34) | |
| 28.48–30.98 | lens 2.5 (ASSUMED) | |
| 31.38–34.38 | lip 3.0 after the 0.4 rim gap; the code ring's face 0.15 up in its underside | |
| **35.9** | **overall with the pad** (v12 37.9, v11 40.7) | |

What each part costs against the wheels' floor of 24.2: the adapter's HDMI socket **+1.8** (flipping it would leave the touch board at 22.4 as the ceiling, +0.6 — question 19); the bonding tape **+0.5**; the 8 mm plate and the 5.5 halo band **0** in height. Below the wheels' floor the limit is the motor stack: the drive band's contact zone starts at the knob skirt's bottom (14.9, over the halo's lip) and 2–3 mm of contact puts the band's top at 17–17.8 and the seat at 23.4–24.2 — a narrower halo strip or a lower motor would be needed to go under about 33.3 overall.

### 8.4 Option B — cooler deleted, Pi inverted, SoC on a boss to the plate

Pi inverted with its USB-A and Ethernet stacks standing on the pad through the plate window: component face at z 16.2, board 16.2–17.48, its back-side parts to 18.93; SoC face at 13.86; boss 5.4 tall on the 8 mm plate, 0.5 pad. Everything above is as built: **35.9 with the pad**, the same as v13 (the adapter sets the seat either way).

Thermal credibility at ~4 W (ASSUMED coefficients): pad 0.3 K/W, boss negligible, plate spreading 0.65 K/W (8 mm; 1.0 at 5 mm) → SoC ~4 K above the plate; the plate is ~10 K above the room at 4 W total (6.9) → **SoC ≈ room + 15 K: credible, and silent.** At 12 W stress the Pi throttles at 85 °C long before the object does; acceptable for a desk prototype. Cost: a machined boss, two plate holes, the Pi's sockets facing down (the micro-SD slot is then on the visible back face — convenient), and a thermal-pad thickness that must absorb the boss-to-SoC tolerance (use 1.0 mm, ASSUMED). Gain in height: **none**. A″ (the heatsink without its fan) is built because it needs no new parts; B is the fallback if the first print's temperature log says so, and production's principle.

### 8.5 Production — the same object with a Compute Module 5

CM5 SoC-down on a plate boss (4.17 numbers): plate top 8.0 → pad 0.5 → SoC 2.2 → module PCB 1.24 → 4.0 stacking connector → carrier 1.6 → carrier top-side parts 4.0 (ASSUMED) → carrier top at 21.5. No adapter, no ribbon, no Pi window; the boards mount to the plate as they already do in v12 (carrier flat to the aluminium with the compute module's boss through a masked pad, the converter and the motor driver on gap pads — thermal plan rule 15), and the structure gains the lid of rule 14. The carrier top at 21.5 would allow a seat at 23.8, but **the wheels set the floor at 24.2** (their groove over the drive band, 8.3): seat 24.2 → knob top 32.6, **overall 34.1 mm** — 1.8 below the Pi 5 prototype, which is the adapter's socket. A thinner carrier does not lower it; going under about 33.3 needs a narrower halo strip or the motor lower in the plate.

---

## 9. What is v10-only and what is production

| v10-ONLY | PRODUCTION |
|---|---|
| Raspberry Pi 5, the Active Cooler's heatsink, the plate window, the closing plate's lands and the Pi's standoffs, the HDMI adapter kit (driver board, flat cable, connect board and its bracket), the HDMI ribbon, the internal USB-C and USB-A cables, the header power housing, the bought converter module, the touch-controller board as a separate item, height 40.3 | Ø175.4 knob and its lip/chamfers/knurl, bore Ø145, the panel and lens bonded to the seat, the wheel/motor/servo/encoder radii, the halo at r 73.3, the 8 mm plate and its rear slot, the three rear openings and the 12 V barrel choice, the perimeter ports and the vent answer, the audio and motion functions (on the carrier), the CM5 boss principle, height ≈ 34 |

---

## 10. Rules for building the v10 CAD once agreed — v9's ten rules, plus

11. Every plug body (barrel, USB-C, 3.5 mm, micro-HDMI, HDMI-A, USB-A, header housing) is a named `_ENVELOPE` body in the assembly, in its inserted position.
12. Every cable is a swept body along its modelled route with its bend radius as a parameter, and the checker tests it against the carriage sweep, the bell and the wheels at knob angles 0/17/45/73° and both clutch states.
13. The checker proves the display module's insertion path (a straight drop through the bore), the structure's entry from below, the encoder board's drop into its slot, the Ø6 driver paths to the Pi's screws from below and the adapter's from above, every top-face screw hole landing in the plate, every body under the seat below its underside, and both air circuits having an intake and an exhaust.
14. The parameter block carries `PLATE_T` and `COOLER_FAN_FITTED` as switches; the boards' placements are azimuth/radius pairs or (x, y) centres; the adapter follows the Pi (`ADAPTER_X0 = PI_X0`).
15. Drawings: A3, one sheet per made part, the first sheet listing every ASSUMED number.
