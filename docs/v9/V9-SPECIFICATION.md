# the 60 — version 9 specification

**Status: agreed specification — the baseline for the v9 CAD.** This document describes every component and mechanism the v9 model must contain, says which numbers are measured and which are assumed, grades every requirement as must / should / could, and lists the gaps that only the bench can close.

Revision: 4 September 2026, evening — every question answered and folded in; **no open questions remain**. v9 CAD built from this text the same evening (`docs/v9/the60_v9.zip`, `V9.md`); the five build-time changes are recorded in `V9.md` and folded in here. Superseded text has been removed, not struck through.

Sources measured directly: all 18 STEP files in `design/cad/bought-parts/step/` and Waveshare's vendor STEP; the v8 model source in `docs/Claude outputs/the60_v8.zip`. Documents read: `CURRENT-MECHANICAL-DESIGN.md`, `BOUGHT-PARTS-DIMENSIONS-2.md`, `MECHANICAL-REQUIREMENTS.md`, `DECISIONS.md`, `CLAUDE.md`, `design/cad/bought-parts/README.md`.

Tags used throughout:

- **MEASURED** — taken from a CAD file in the repo by measuring it.
- **PUBLISHED** — stated by the manufacturer but not modelled here.
- **ASSUMED** — a number somebody chose. Reasonable or not, it is unverified.
- **GAP** — something the design needs that nothing currently provides.
- **MUST / SHOULD / COULD** — must: the device does not work or cannot be built without it; should: the device is worse without it and the cost of having it is small; could: nice to have, decide on the bench.

---

## 1. What v9 is for

v9 is the version built around the parts as they actually are, in a base that is designed from scratch rather than patched from v8. Two things went wrong in v8 that v9 must not repeat:

1. **Parts were described but never modelled** — motor carriage, clutch eccentric, preload spring, port board with its USB-C socket and jack, encoder seat, light-sensor aperture, cable path. None exists as geometry in the v8 model.
2. **Structure was made complicated where it should have stayed simple.** The v8 base shell is one 44 cm³ solid built from twenty-odd booleans, and that complexity hid the defects in section 8.

v9 therefore starts from a component list in which every bought part is placed as its own CAD body, and every made part is the simplest shape that holds the bought parts in the right places and can be assembled in the order in section 7.

---

## 2. Frame of reference and standing rules

**Coordinates.** Millimetres. **z** is height above the underside of the steel base plate; the rubber pad is below zero. **r** is radius from the display disc's centre. Azimuth is anticlockwise seen from above.

**Azimuth datum (Ryan, 4 September).** **0° is the device's USB-C socket, at twelve o'clock, facing away from the user.** No other component has a fixed azimuth; everything else is placed to suit the design. The Waveshare board's own orientation is therefore a design choice, and the sensible one is its USB-C edge toward the back so the internal power lead is short (section 6.8). In that orientation, board-frame azimuths convert to device azimuths by subtracting 90°.

**Standing rules carried over unchanged (Ryan, v1 onward):** the knob clears every static part by at least 0.40 mm; running clearances 0.30; static fits 0.15; minimum printed wall 1.6; no overhang beyond 45° on a functional surface; M3 heat-set inserts; no glue; everything re-openable; every dimension in one parameter block; every check automated; anything unverified is a named parameter marked V.

**The part determines the design (Ryan, 3 September).** Nothing is laid out around a part that does not have a CAD body in `design/cad/bought-parts/`.

---

## 3. The object — requirements in force

| Requirement | Value | Grade | Origin |
|---|---|---|---|
| Height | at most 40 mm including the pad; 45 is failure | MUST | Ryan, decision 37 |
| Diameter | not a requirement; smaller preferred while staying chunky; working value Ø125; the halo bench test decides the final figure (Ø127–136) | SHOULD | Ryan 2 Sep; `HALO-BENCH-TEST.md` |
| Knob share of the visible side | at least two thirds | MUST | Ryan |
| Visible picture | Ø87.6; the knob's lip reaches in over the dead border as close to 87.6 as possible | SHOULD | Ryan |
| Mass | at least 250 g, low; steel plate; the plate has **no shape requirement, only heft** — it may be cut, notched or thickened as the design needs | MUST | decision 42; Ryan 4 Sep |
| Knob | one piece, no seam or screw; diamond knurl on the side; wide smooth 45° chamfer at the top outer edge; small smooth chamfer at the glass; small chamfer at the skirt's lower edge; **solid — more mass is better** | MUST | Ryan; decisions 45/46; Ryan 4 Sep |
| The knob touches nothing but its three wheels — never the display | | MUST | Ryan 4 Sep |
| Sixty positions per turn by default, any pattern in software; the detent is rendered by the motor | | MUST | v8 architecture |
| Free-spin is real: the motor is lifted physically clear; the servo is proportional and **sets the preload in software** — no spring, no hard stops | | MUST | Ryan 4 Sep |
| The knob turns itself, slowly | | MUST | Ryan 2 Sep |
| Halo: full 360°, on the fixed base, firing down and outward; its bottom edge is the plate edge (no plinth band) | | MUST | Ryan; decision 43; Ryan 4 Sep |
| Sockets: one USB-C in, one 3.5 mm jack; at the back; **below the halo**, at plate level, the plug body sitting in a notch in the plate; no permanent cable | | MUST | Ryan 4 Sep |
| Perimeter ports in the base wall under the knob's skirt: acoustic paths for the speaker and the two microphones, and the heat vent; may read as an aesthetic feature | | MUST (acoustic) / SHOULD (vent) | Ryan 4 Sep |
| Microphones work in this enclosure (dictation) | | MUST | Ryan 4 Sep; decision 14 |
| Sits flat on a rubber pad, no feet | | MUST | Ryan |
| Display is a replaceable module on a defined interface | | SHOULD | decision 65 |
| Assembly is upside down, in the order knob → display → internal structure → base plate → pad; the internal structure may be modular; the structure that holds the display connects to the base plate | | MUST | Ryan 4 Sep |
| First print must prove: every component fits the cavity, everything can be secured, the knob turns | | MUST | Ryan 4 Sep |

---

## 4. Bought components

One entry per part: the body as it exists in the CAD folder, where it sits, what the made parts must provide for it, and its gaps. Inside a part, coordinates follow its file: board-mounted parts have z = 0 at the top of the board they sit on; round parts have their axis on Z; everything else has z = 0 at the seating face.

### 4.1 Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C — display and main controller

File: `vendor/Waveshare_ESP32-P4-WIFI6-Touch-LCD-3.4C/ESP32-P4-WIFI6-TOUCH-LCD-3_4C.stp`. Everything below is **MEASURED** from it unless marked. Vendor frame: disc centred on the origin, front glass at z +3.75.

| Feature | Value |
|---|---|
| Disc | Ø115.00, z −2.25 to +3.75 = **6.00 thick**. Front face Ø114 with a 0.5 chamfer; back edge rounded to Ø113 at the back face |
| Glass | lens Ø112.5; viewing aperture Ø88.2; active picture Ø87.6 |
| Rear mounting holes | **4 × M4** (drawing: "4×M4.00") at (±37.50, ±37.50) = **Ø106.07 pitch circle**, 45° apart from the board axes. Modelled Ø3.3, **3.5 mm deep** from the back face. Back face is flat around each hole |
| Main board | 85.50 × 65.00 × 1.60, centred **4.50 mm off the disc centre along the board's short axis** (toward the 40-pin-header edge), top face 1.50 below the disc back, bottom face 7.10 below the disc back |
| Board corners | far corners at **r 56.54**; near corners r 51.10 |
| Tallest rear part | USB-A socket 12.2 × 13.1 × 7.0 at the board's +X end → bottom **15.50 below the glass**. **Stays** (Ryan, question 9) |
| Vendor back plate | 2 mm PMMA on four M2.5 × 4 screws — **removed for the 60** (Ryan, question 8); the four M2.5 hex studs stay, reaching 13.1 below the glass. Stiffening added by the 60's structure if the board proves floppy without the plate — COULD |
| Disc features below its back face | four Ø4.5 stud bosses 1.5 mm proud; one bracket 15.5 × 6.2 at the header-edge side, **3.6 mm proud**, r 33.5–39.7 |
| Rear-side component map (board frame; convert by −90° for the device) | 40-pin header 51.3 × 6.6 × 5.1 along the −Y edge · USB-A at +X end · microSD at −X end · **two USB-C sockets on the +Y edge** at x −12.4 and −26.9, 4.2 tall, overhanging the edge 1.04 · speaker JST 8.5 × 7.9 × 5.6 near (37.5, −20.6) · RESET/BOOT switches on the −X edge · two small connectors on the −Y edge · **two microphone cans 4 × 4.4 × 2.0 at (−20.5, −8.2) and (−19.1, 8.3), facing down** |
| Top side of the board | no components |
| Weight | NOT PUBLISHED; 60 g ASSUMED |

**What the made parts must provide for the display — scrutinised.** Each line says what, why, its grade, and whether it is a leftover from v8.

| # | Provision | Why | Grade | Verdict |
|---|---|---|---|---|
| 1 | **Four fixing points on Ø106.07** that bear on the disc's back face and take an M4 screw each | The disc has exactly four M4 holes and no other fixing. The screws are the only way to hold a 115 mm glass disc without clamping its edge (the knob must not touch it) | MUST | Real. But "bosses on the shell" was v8's shape, not a requirement — and it cannot work anyway: two of the four holes are 0.5 mm from the board's edge, so no post can stand under them. v9: four 4 × 6 columns at 42/138/222/318° (three degrees off the holes) carrying 1.2 mm seat tabs that reach the holes inside the 1.5 mm gap above the board |
| 2 | **M4 thread engagement ≤ 3.5 mm** (and ≥ 2.5 mm) | The tapped hole is 3.5 deep; a longer screw bottoms and splits the housing. So the screw length is the seat thickness + 3.0 ± 0.5 | MUST | Real, measured. v8's "M4 × 5 deep" and "M4 × 6" were wrong |
| 3 | Screw heads face the plate side and are driven **before the plate goes on** | Follows from the assembly order (knob → display → structure → plate). No long driver, no through-holes in a wall | MUST | Real, and now trivially met by the order. v8's 25 mm through-hole idea is deleted |
| 4 | Clearance for the disc's own rear features: four Ø4.5 stud bosses (1.5 proud) and the bracket 3.6 proud at r 33.5–39.7 on the header side | They are moulded into the case; anything touching them loads the disc off its four seats | MUST | Real, measured. v8 did not model them |
| 5 | A cavity under the board at least **15.5 deep** over the board's footprint plus the USB-A overhang | 15.5 is the USB-A bottom and the USB-A stays | MUST | Real |
| 6 | **+1.0 mm** clearance below the tallest part | Working clearance to a static part; the board is not a precision datum | SHOULD | v8 assumption, kept; 0.5 would do if height is desperate |
| 7 | Nothing under the display within the wheel band except the three wheels | The knob's V-groove is level with the board; the wheel collars sweep r 46–59 there | MUST | Real; it is why wheel azimuths are restricted (section 6.1) |
| 8 | **Microphone acoustic path** from the two cans (facing down at r ≈ 21) to the outside | Dictation is a must; the cans face into a closed cavity | MUST | Real gap; v8 had nothing. How it is met is section 6.9 |
| 9 | **Power lead** from the device's USB-C to one of the board's two USB-C sockets: a short USB-C-to-USB-C cable (Ryan, question 26) and the **plug body it needs under the disc at the back** — about 10 wide × 7 tall × 28 long from the board edge for a straight plug, or 10 × 7 × 12 for a right-angle plug turning down | The board has no other power input the 60 will use | MUST | Real gap; v8 had nothing |
| 10 | A path for the **speaker JST lead** from the board's socket to the speaker | The speaker is driven from the vendor board | MUST | Real; trivial but must be drawn |
| 11 | Access to the microSD, RESET and BOOT | Development convenience | COULD | v8 never mentioned it; not a v9 requirement |

**Gaps:** the board's stiffness with the PMMA off; weight. (Resolved: the Waveshare wiki says **both** USB-C sockets accept power — one is "USB 2.0 full speed, for power supply, program flashing and debugging", the other "USB to UART, for power supply, program flashing, debugging". Either can be the 60's power input; using the USB 2.0 one leaves the UART one free for the debug cable.)

### 4.2 JD-Power gimbal motor — the haptic engine and the self-turn drive

**Settled (Ryan, 4 September): the motor is the JD-Power MY-3514C, 2804 frame.**

File: **MEASURED** a single body `motor_ENVELOPE`, Ø35.00 × 14.00, nothing else. **Not modelled because JD-Power publishes nothing:** hollow bore, base-to-bell split height, mounting bolt pattern, wire exit, locating boss. The README warns the real body is probably nearer Ø34.5 (the sister part's "28×13" is Ø27.5 × 13 on its drawing). **Torque, resistance, pole count: NOT PUBLISHED.**

**How it is used:** axis vertical; the bell, in a friction band, presses radially on the knob's smooth drive band on the bore (r 58.0). With a Ø35 bell the ratio is **58 / 17.5 = 3.31 : 1** in the knob's favour (from an unpublished motor torque). The motor centre sits at r 40.5. Where the motor's circle crosses the base wall band (r 55.5–57) it does so over **±11°** — the wall, the ledge and the LED ring are interrupted there unless they sit below the bell.

**What the made parts must provide:** a **carriage** (section 5.6) that holds the motor by its bolt pattern, slides 2.4 mm radially, carries the servo's push and pass the phase leads; the commutation sensor on the shaft axis at whichever end JD-Power fits the magnet (section 4.4); the bell above the halo's top or the halo notched (section 6.6).

**Gaps:** bolt pattern, bore, bell split, wire exit, torque — all bench measurements on the real motor.

### 4.3 TMC6300-LA-T three-phase driver

File `TMC6300-LA-T_QFN20_3x3.step`. **MEASURED** 3.0 × 3.0 × 0.85. **PUBLISHED** in full. Sits on the **motor-driver board** beside the motor (section 5.9).

### 4.4 MT6701CT-STD angle sensor and Ø6 × 2.5 diametric magnet — motor commutation

Files `MT6701CT-STD_SOP8.step` (**MEASURED** 4.9 × 3.9, 6.0 across leads, 1.62 tall) and `MT6701_diametric_magnet_D6x2p5.step`. **PUBLISHED**.

**How it is used:** magnet in one end of the motor's hollow shaft, sensor 0.5–2.0 mm (1.0 typical) off the magnet face, on the axis. The stack it needs beyond the shaft end is about **4 mm**: 1.0 gap + 1.6 chip + 1.6 board.

**Where it goes is set by the motor, not by us:** JD-Power ships the MY-series "with encoder magnet fitted" — at whichever shaft end they chose. The conventional gimbal arrangement is magnet at the bottom, sensor board under the motor base. Until the motor is in hand this is unknown, and it decides the height stack (section 8). **GAP.**

### 4.5 623ZZ bearing ×3 — the knob's wheels

File `623ZZ_bearing_3x10x4.step`. **MEASURED** Ø10 × 4, bore Ø3, inner shoulder Ø4.8. **PUBLISHED** in full. Pressed into a V-collar (5.4) on an eccentric bush pin (5.5). **Provide:** collar bore Ø9.9 press (ASSUMED, tune on the print); Ø3 pin running fit; a shoulder so the inner ring is not the part that spins (COULD — v8 had none).

### 4.6 AGFRC C1.5CLS PRO linear servo — the clutch actuator

File `AGFRC_C1p5CLS_PRO_linear_servo.step`. **MEASURED** body 21.4 × 15.2 × 6.0 as `_ENVELOPE`; pushrod and 9 mm stroke keep-out `_ASSUMED`; stroke along the 21.4 axis ASSUMED. **PUBLISHED:** 9 mm stroke, 2.4 N at 6 V, 1.5 g. **GAP:** no drawing — lugs, holes, pushrod, output geometry, lead exit all unknown until bought.

**How it is used (Ryan, question 4):** **proportional**. The pushrod drives the carriage directly; the servo's position sets the bell's contact force, and full retraction is free-spin. No spring, no hard stops, no over-centre eccentric. The servo holds position with current while engaged — its holding current is a bench measurement.

**Provide:** a pocket 21.4 × 15.2 × 6.0 plus 9 mm stroke clearance in line with the carriage's slide axis; a retention feature (unknown); a pushrod-to-carriage joint that takes 5 N in both directions. The stroke axis is radial through the motor centre, so the servo lies radially inboard or tangentially beside the motor with a bell-crank — decide in CAD; radial inboard is simpler.

### 4.7 Broadcom AEDR-8300-1K2 reflective encoder — the knob's angle

File `Broadcom_AEDR-8300-1K2_encoder.step`. **MEASURED** 5.12 × 3.96 × 1.63 plus a 2.0 mm `reflective_gap` body. **PUBLISHED** in full.

**How it is used:** on its own small board on a **seat** on the internal structure (Ryan, question 5), optical face 2.0 mm from a bonded reflective code strip on the bore's code band. Azimuth **75° in the board frame** (Ryan, question 16) = between a wheel post and the back; in the device frame this is a free choice away from any post and the motor sector. ~10,300 counts per turn with index; this closes the haptic loop.

**Provide:** a rigid seat; a slot for board and flex; a code band on the bore recessed by the strip thickness (Ryan, question 17: **0.15 mm recess**, joint at the index). **Gaps:** strip supplier and exact thickness; the 6 × 8 carrier board is ASSUMED.

### 4.8 Vishay VEML7700-TR ambient light sensor

File `Vishay_VEML7700-TR_ambient_light_sensor.step`. **MEASURED** 6.8 × 2.35 × 3.0; sensitive area 1.95 above the seating plane on one long face. **PUBLISHED** in full.

**Placement (Ryan, question 19):** **at the back beside the sockets, looking rearward**, on the port board. **Provide:** an aperture aligned with the sensitive area, width 0.5 + 2 × 1.43 × wall thickness (Ø4.8 through 1.5 mm), through the base wall below the halo. MUST (if the sensor is kept); the sensor itself is SHOULD — the halo and screen can run at fixed brightness.

### 4.9 Vybronics VLV101040A linear resonant actuator — event feedback

File `Vybronics_VLV101040A_LRA.step`. **MEASURED** can 10 × 10 × 4.05, installed stack **4.37** with tape and cushion, 13.9 long with the flex tail. **PUBLISHED** in full.

**Placement (Ryan, question 18):** bonded by its tape to the **internal structure's wall next to a wheel post**, so the pulse reaches the knob through that bearing. Unproven — decision-list question C. **Provide:** a flat 10.2 × 10.2 bonding face with 4.4 mm of height, tail channel to the driver board. SHOULD (the product works without it; the detent is the motor's job).

### 4.10 TI DRV2605L haptic driver

Files `TI_DRV2605L_VSSOP10_DGS.step` (3 × 3, 1.10 tall, hand-solderable) and `TI_DRV2605L_DSBGA9_YZF.step`. **PUBLISHED** in full. On the motor-driver board or the port board — CAD choice.

### 4.11 Soberton SP-4005-1 speaker

Files `Soberton_SP-4005-1_speaker_D40.step` and the vendor mesh. **Height is 9.05** (the vendor mesh measures z −1.50 to +7.55 over Ø40.00); the datasheet's 8.5 is not the overall height. Flange Ø40, front ring Ø38 / Ø35.5 opening, rear boss Ø16.2, lead exit `_ASSUMED`.

**How it is used (v9 build):** stands cone-up on its rear boss at (0, −30), breathing into the cavity, which vents through the **perimeter ports** (section 6.9). No plate aperture. **Provide:** a cradle ring under the Ø40 flange (flange 4.45–5.95 above the rear face) with three snap fingers over it, two M3 into the plate, lead path to the vendor board's JST. MUST.

### 4.12 ESS ES9219Q DAC with headphone amplifier

File `ESS_ES9219Q_WQFN40_5x5.step`. **MEASURED** 5 × 5 × 0.75. **PUBLISHED** in full. On the port board.

### 4.13 Switchcraft 35RAPC4BH3 3.5 mm jack

File `Switchcraft_35RAPC4BH3_jack_3p5mm.step`. **MEASURED** body 14.0 × 11.5 × 6.0 above its board, M6 × 0.5 bushing 3.5 long, axis **3.0 above the board**, pins 2.5 below. **PUBLISHED.**

**Placement (Ryan, questions 12/13):** at the back beside the USB-C, **below the halo**, on the vertical port board (4.14). **Provide:** Ø6.2 hole in a wall ≤ 2.5 thick, flat outside face for the nut, plug keep-out (Ø8 × 15 outside).

### 4.14 GCT USB4520-03-0-A mid-mount USB-C receptacle

File `GCT_USB4520-03-0-A_usbc_midmount.step`. **MEASURED** 6.5 × 8.94 × 3.16; hangs 2.10 below the board top, stands 1.06 above; needs a 9.24 × 6.20 board notch; mating face flush with the board edge.

**Placement (Ryan, question 12, option b):** at the back, below the halo, the plug body sitting in a **notch through the plate and the pad**. The plate has no shape requirement, so the notch is free.

**Settled (Ryan, 4 September): the plate is 5 mm thick** so that the halo's bottom edge (the plate top) is 6.5 mm above the desk (pad 1.5 + plate 5.0) and a 6.5 mm right-angle plug body sits wholly below it, in a notch cut through the plate and the pad, its underside at desk level. The **port board stands vertically** against the back wall inside the notch region so that the USB-C axis and the jack axis (3.0 above the board face) sit at about z 2.5, and the jack's M6 bushing passes through the back wall below the halo. **As built in v9:** a 32 mm slot through plate and pad from r 35 to the rim; a printed **port face** at r 49.5–51 carrying the USB-C opening, the Ø6.3 jack hole and the Ø4.8 light-sensor aperture; the USB-C on a horizontal board at z 2.2 in the slot (receptacle z 0.1–3.3); the jack hanging under a board at z 5.0 so its body sits at z −1..5 and its axis at z 2.0; the light sensor on a tiny vertical board at r 46 looking rearward. One board could not hold both sockets at z ≈ 2, which is why there are two.

### 4.15 Abracon AHCR-S04R0SA206Q supercapacitor ×2

File `Abracon_AHCR-S04R0SA206Q_supercap_20F.step`. **MEASURED** can Ø8 × 12, leads Ø0.6 at 3.5 pitch. Two in series, lying down, on the motor-driver board (their job is the motor's current spikes). MUST for the motor; placement is a CAD choice.

### 4.16 OPSCO SK6812SIDE-A side-emitting LED ×90

File `OPSCO_SK6812SIDE-A_led_4020.step`. **MEASURED** 4.0 × 1.6 × 2.0 tall. **PUBLISHED**; window position not published. **90 is the maximum** at 4.21 mm pitch on the ring (`HALO-BENCH-TEST.md`).

**How it is used (v9 build):** on a **flat annular flex lying on the plate top** (r 57.7–60.0), the LEDs at r 58.8 with their emitting face outward into the diffuser; continuous 360°. (A side-view LED on a flex wrapped round the wall would fire up or down, not outward — so the ring lies flat.) **Provide:** the annular seat on the plate top under the diffuser lip, clear of the motor's base (assumed Ø30); a slot for the ring's connector; retention by the lip and the diffuser (adhesive backing — ASSUMED). **Gaps:** the flexible board itself (width, thickness, connector, join); the LED-to-diffuser gap (bench test not run; v9 prints at Ø125 with the v8 gap and accepts a dotted halo — Ryan, question 7).

### 4.17 Friction band on the bell

Not a CAD file. **Ryan, question 20:** flat silicone band, about 0.6 × 8 mm, stretched onto the bell, held by friction. Shore ASSUMED 40–70, to be chosen on the bench. The band's torsional compliance is the likely limit on click sharpness. **Provide:** nothing on the made parts; a retention lip on the bell is COULD once the real bell is measured.

### 4.18 Rubber pad, screws, inserts, cable

Pad Ø122 × 1.5 full-face, bonded (ASSUMED). Fasteners: M3 countersunk plate-to-structure with heat-set inserts; 4 × M4 display (length per 4.1 line 2); M2 grubs for the bush locks in production. Braided right-angle USB-C cable, 1 m — its plug body sets the plate notch (4.14).

### 4.19 Boards the 60 must make — **defined by Ryan, question 5**

Individual boards, each near the part it serves, with the wiring harness between them a first-class design consideration that should steer placement but stay flexible:

| Board | Carries | Where |
|---|---|---|
| **Port board** | USB-C receptacle, 3.5 mm jack, ES9219Q DAC, VEML7700 light sensor, ground-bond tag | back, at plate level, below the halo |
| **Motor-driver board** | TMC6300, two supercapacitors, DRV2605L (or on the port board) | beside the motor, on or near the carriage |
| **Commutation board** | MT6701 | on the motor's shaft axis at the magnet end |
| **Encoder board** | AEDR-8300 | on its seat, 2 mm from the code band |
| **LED ring** | 90 × SK6812SIDE-A | outside the base wall |

All are made parts in v9 with outline, thickness (1.6 FR4, 0.2 flex for the ring) and mounting holes drawn; the electrical design is not part of this spec. Harness routes: motor phases (3) carriage → driver board; driver board → vendor board (I²C/PWM; the vendor board's small connectors are on its header edge); encoder → vendor board; LED data + power; USB-C power cable; speaker JST; LRA tail. **Provide:** a harness channel around the floor and a grommet or slot into the display cavity. MUST.

---

## 5. Made components

Simplest shape that does the job. The v8 base shell is **not carried over** (Ryan, question 3: "the shell is to be completely redesigned; the options are not to be assumed").

### 5.1 Base plate (steel)

Ø123 × **5 mm** mild steel (Ryan, 4 September), laser-cut, powder-coated, about **340 g**. It is ballast, the floor, and the bottom edge of the halo. Cut into it: three fixing holes to the internal structure; the plug notch at the back; the **carriage hole** for the motor carriage (the carriage stands on the pad through it and slides in it — stack case B); a ground-bond hole beside the port board. Pad Ø122 × 1.5 bonded below, cut to match the plug notch, with a PTFE slide sheet under the carriage (SHOULD).

### 5.2 Internal structure (printed; PA12 in production) — replaces the v8 shell

What it must do, in order of importance: (1) hold the display by its four M4 seats, rigidly, connected to the plate; (2) carry the three wheel posts so the knob runs on the display's axis; (3) carry the encoder seat, the LRA bonding face beside one wheel post, the carriage's slide and the servo pocket; (4) form the base wall that the LED ring wraps and the perimeter ports pierce; (5) screw to the plate with three M3.

**Shape rule for v9:** a **spider or ring with four legs to the plate**, not a closed cup — the display seats, wheel posts and encoder seat on a ring at the display's level; legs down to the plate carrying the wall segments and the LED seat; the motor carriage and servo on the plate, not on the structure. Modular is allowed (Ryan): e.g. a display ring + three identical wheel-post legs + a back wall segment carrying the ports. Every screw and bush faces the open (plate) side during assembly.

### 5.3 Halo diffuser (opal PMMA production; natural PETG prototype)

A ring, v9 build: r 60.0 inside, r 62.0 outside at the bottom leaning out to 62.5 at the top, z 5.0–7.6 (2.6 tall). Its bottom edge sits on the plate top at the rim; **retained by being trapped between the plate and a 0.8 mm lip on the structure at z 7.6–8.4** (Ryan, question 28). No openings for the sockets, which are below it.

### 5.4 Knob (PETG prototype; CNC 6082 production)

As v8 in principle, solid: Ø125; 3 mm lip to Ø89; chamfers 2.5 / 1.0 / 1.2; diamond knurl 56 starts, 1.0 deep, 30° helix; straight bore Ø116; on the bore from the bottom: smooth **drive band**, **code band** recessed 0.15 for the strip, **90° V-groove** 1.3 deep with a 0.6 flat root. Nothing else. The band heights follow the motor stack (section 8).

### 5.5 Wheel V-collar ×3 and eccentric bush ×3

As v8: Ø13.2 convex-V collar over a 623ZZ; bush with Ø5 stem, Ø7 flange, Ø3 pin offset 0.9, 2 mm hex in the stem end. **Access:** the hex faces the plate side and is turned during upside-down assembly after the structure is on the display and before the plate goes on. Production lock: M2 grub through the post — hole to be drawn.

### 5.6 Motor carriage — new in v9

A flat plate or shoe carrying the motor on its bolt pattern (unknown), sliding 2.4 mm radially on the steel plate (or on the pad through a plate hole — question 2) in a straight guide formed by the structure's legs or by two pins in slots; the servo's pushrod attaches to it. Carries the commutation board if the magnet is at the bottom, with a pocket for it. The phase leads exit on the side away from the bore. Cannot be finished until the motor is measured; drawn in v9 as a generic plate with a Ø36 locating recess and three radial slots.

### 5.7 Servo mount — new in v9

A pocket on the plate or a leg, in line with the carriage's slide axis; drawn as an envelope until the servo is measured.

### 5.8 Perimeter port ring

Not a separate part: a pattern of small holes (e.g. Ø2–2.5, 12–24 of them) through the base wall in the band hidden by the knob's skirt, above the halo. Section 6.9.

### 5.9 Boards — section 4.19.

---

## 6. Mechanisms

### 6.1 Knob suspension — three V-wheels in a bore groove

Three 623ZZ in convex-V collars on eccentric bushes in posts on the structure, running in the bore's concave V-groove level with the display board. Wheel axis r 52.63, retracted 0.57 inside the bore for the drop-on, half a turn seats them.

**Wheel azimuths are restricted by the board's edge** (the collars sweep r 46–59 at the board's height). In the device frame with the board's USB-C edge at the back (0°), the clear arcs are **270–291°, 308–52°, 69–111°, 144–216°**. **Settled (Ryan, 4 September): wheels at 30°, 150°, 270°** (board edge at r 32.3, 42.7, 42.8 on those rays — the best-margin set, leaving the back open from 270° to 30° for the ports and the internal USB-C plug). The motor sector must not coincide with a post.

**Assumed:** 0.9 eccentric throw covers print tolerance; three wheels suffice. **Gaps:** production bush lock; groove-to-bore concentricity 0.05 on a print.

### 6.2 Detent and drive — motor bell on the bore

The bell, in its silicone band, presses on the bore's drive band; ratio 3.31 : 1 (Ø35 bell) from an unpublished motor torque. One loop on the encoder renders every click pattern and turns the knob. **Assumed:** ~5 N preload (now a servo setting), μ 0.5, band 0.6. **Gaps:** motor torque, bolt pattern, bell split, driver-board placement, heat (vented through the perimeter ports).

### 6.3 Clutch — proportional servo, direct push

The servo's pushrod moves the carriage radially: fully in = free-spin (bell ≥ 0.8 mm clear of the bore after the band), fully out = maximum preload; anything between is a software preload. No spring, no over-centre, no stops other than the servo's own travel limits. Holding current while engaged is a bench number. **Settled (Ryan, 4 September): direct push, 2.4 N** at the bell for the first print; whether the band grips at that force is a bench finding. A 2 : 1 bell-crank (4.8 N, 4.5 mm of carriage travel) is the fallback and is a small added part. **Gaps:** servo mount and pushrod joint until the servo is measured.

### 6.4 Angle sensing — reflective encoder on a bore strip

AEDR-8300 at 2.0 mm from a 0.15 mm strip recessed into the code band; ~10,300 counts with index. Seat on the structure away from posts and the motor sector. **Gaps:** strip source; latency budget.

### 6.5 Motor commutation — MT6701 on the shaft axis

At the magnet end JD-Power chose. Board on the carriage (bottom) or on a bridge over the shaft (top). Decides the stack — section 8.

### 6.6 Halo

90 LEDs on a flat flex annulus on the plate top at r 58.8 (4.11 mm pitch), opal diffuser outside them at r 60–62.5, 360°, z 5.0–7.6, retaining lip 7.6–8.4, knob skirt bottom 9.0 leaving the 0.6 shadow gap. **The ring must sit below the motor's bell** wherever the motor reaches the wall band (±11° at the motor azimuth), or the ring is interrupted there. With the lip top at 8.4 the bell's bottom must be at z ≥ 8.5 — 4.3 above the motor's base face at z 4.2 (stack case B, section 8) — and the motor's base must be ≤ Ø31 to pass inside the flex annulus. Verify both on the real motor. **Gaps:** LED-to-diffuser gap (bench test deferred); flex ring details; diffuser thickness and grade.

### 6.7 Audio out — speaker and headphones

Speaker down-firing into the cavity, breathing through the perimeter ports; ES9219Q on the port board driving the jack. **Gaps:** back volume (the cavity is shared with everything else — accept for the prototype, SHOULD improve later); gasket; JST lead route.

### 6.8 Power and cable

Device USB-C at the back at plate level → short USB-C-to-USB-C cable inside the base → one of the vendor board's two USB-C sockets at the board's back edge (plug body under the disc at the back, section 4.1 line 9) and a tap to the port board and motor-driver board. Ground bond: one M3 with a solder tag from the port board to a plate hole beside it (Ryan, question 27). **Gaps:** which vendor socket; the plug envelope under the disc; where the 5 V splits.

### 6.9 Perimeter ports — acoustic paths and vent (Ryan, questions 10, 11, 25)

A ring of small holes through the base wall in the band above the halo and below the ledge, hidden under the knob's skirt. Air path: cavity → holes → the 0.4 mm annular gap between the wall and the knob's bore → the 0.6 mm shadow gap → the room. Serves the speaker, the microphones and heat.

**Ryan's question — can the vent and the acoustic paths be the same holes? Yes, with these caveats:**

- The annular gap is the bottleneck, not the holes: 0.4 mm × 360° is about 145 mm² total, which is generous for sound (a phone's speaker port is ~10 mm²) but weak for convection. As a vent it works by letting warm air out around the whole rim; do not expect it to cool a stalled motor. SHOULD, measured.
- The holes must avoid the motor sector (the bell fills the wall band there), the three wheel posts and the encoder seat. That still leaves ~250° of wall. MUST.
- The **speaker** will sound like what it is: a driver in a leaky box. Fine for notifications (decision 15). MUST.
- The **microphones** are at r ≈ 21 on the board's underside, 35 mm from the wall. A duct that long has a quarter-wave resonance near 2.4 kHz — bad for speech. **Settled (Ryan, 4 September): no ducts on the prototype** — the cans hear the cavity, which is open through the ports; dictation is tested on the print. If it is poor, the fix is a short duct down through the structure to a plate hole (~20 mm), not a long one to the wall. Production: MUST work.
- **Settled (Ryan, 4 September): 24 × Ø2 holes**, evenly spaced over the free arcs; revisited when the print is in hand. At Ø2 they are invisible under the skirt.

### 6.10 Assembly order (Ryan, questions 14/15) — every step must be physically reachable

1. Knob upside down on the bench, lip down. A 0.4 mm shim ring on the lip (jig) sets the rim gap.
2. Display placed in the knob, glass down onto the shim; disc centred by the bore (0.5 mm clearance all round — a centring jig is SHOULD).
3. Internal structure lowered over the display with the three wheels retracted; four M4 screws into the disc from above (which is the underside when upright).
4. Bushes half-turned from above to seat the wheels in the groove; locked. Shim removed later through the rim gap — or the shim is three thin tabs pulled out sideways (jig design).
5. Encoder board on its seat; LRA bonded; LED ring wrapped on the wall; diffuser placed in its lip.
6. Motor on its carriage with the band on; carriage into its guide; servo into its pocket, pushrod attached; driver board and commutation board fitted; harness dressed into its channel.
7. Speaker into its cradle; port board fitted at the back; internal USB-C cable plugged into the vendor board and dressed to the port board.
8. Base plate on — it captures the diffuser edge, the carriage and the port board — three M3 into the structure's inserts; ground-bond screw.
9. Pad bonded. Turn over.

Nothing is glued but the pad; everything reverses.

---

## 7. What the first v9 print must prove (Ryan, question 23)

Every component fits the cavity; everything can be secured in place; the knob turns. So the first print needs the real display, the three wheels, the motor (as its envelope if not yet in hand), the servo envelope, the speaker, the boards as blank outlines, and the LED ring as a blank strip. It does not need the knurl, the diffuser grade or a working clutch.

---

## 8. Height stack — worked for the Ø35 × 14 motor

Fixed: pad 1.5; plate 5.0 (the carriage stands on the pad through it, so the plate thickness does not enter the motor stack); display module 15.5 from the USB-A bottom to the glass; +1.0 clearance under the USB-A; 0.4 rim gap; 3.0 lip. So **knob top = (display's lowest point) + 15.5 + 0.4 + 3.0**, and overall = knob top + 1.5. To meet 40.0 the display's lowest point must be at **z ≤ 20.1**.

| Case | Motor stands on | Commutation board | Motor top | Display lowest | Overall | Halo clear of the bell? |
|---|---|---|---|---|---|---|
| A | the pad, through a plate hole (z 0) | above the shaft, in a 4 mm bridge | 14.0 | 19.0 | 39.4 | only if the bell starts ≥ 8.5 — needs an 8.5 mm base on a 14 mm motor: **no** → ring notched ±11° |
| **B — chosen** | a 4.2 mm carriage on the pad, through a plate hole (motor base at z 4.2) | below, inside the carriage (board 1.6 + chip 1.6 + gap 1.0) | 18.2 | 19.2 | **39.6** | bell must start ≥ 4.3 above the motor base (halo top 8.0 on the 5 mm plate): **plausible, verify** |
| C | the plate top (z 5) | above the shaft | 19.0 | 24.0 | 44.4 | yes |
| D | the plate top (z 5) | below, in the carriage (4 mm) | 23.0 | 24.0 | 44.4 | yes |
| E | the plate top (z 5), no commutation sensor | — | 19.0 | 20.0 | 40.4 | fails the limit anyway |

**So what:** the shorter motor buys the space for the commutation sensor, not a lower device. Cases C and D fail the 40 mm limit; case E fails whenever the band slips. **Settled (Ryan, 4 September): case B.** The carriage is 4.2 mm tall, stands on the pad through a hole in the 5 mm plate (its top 0.8 below the plate top), holds the commutation board in a pocket under the shaft, and the motor is bolted on top at z 4.2. Resulting stack as built: motor 4.2–18.2 · drive band 9.0–17.8 · ledge 15.6–17.4 · code band 18.4–22.6 (the AEDR-8300 is 3.96 tall, so the band is 4.2) · display's lowest point 19.2 · wheels 23.4–27.4, groove 23.8–27.0 · board 25.6–27.2 · seat tabs 27.5–28.7 · glass 34.7 · knob top 38.1 · **overall 39.6** with the pad. Halo 5.0–7.6, lip to 8.4, knob skirt bottom 9.0, knob 76 % of the visible side. **Conditions to verify on the real motor:** the bell must begin at least 4.3 mm above the motor's base face (z ≥ 8.5) and the base must be no wider than Ø31, or the LED ring is interrupted over ±11° at the motor. If the bench shows a shorter base, the fallback is to drop the halo to the plate's *underside* edge by rebating the plate rim — the plate has no shape requirement.

Radial budget at the halo: outside radius = 57.5 + 0.75 clearance + 1.5 wall + 1.2 LED board + gap + diffuser; v9 prints at Ø125 with the v8 gap (Ryan, question 7).

---

## 9. Defects found in v8 that v9 must not repeat

Found by measuring the v8 model source and the bought-parts CAD. Kept as the checklist for the v9 checker.

1. Eccentric bushes unreachable — bores dead-ended inside an 8 mm wall. *v9: bushes face the open side during assembly.*
2. Display screws unreachable, and the screw length wrong for a 3.5 mm tapped hole. *v9: screws driven before the plate goes on; length = seat + 3.0 ± 0.5.*
3. Halo not 360° — LED wall cut away ±13° at the motor. *v9: ring below the bell (stack case B), or the case is chosen knowing the cost.*
4. Motor carriage, clutch parts, servo linkage absent. *v9: 5.6, 5.7, drawn as envelopes until measured.*
5. Encoder buried in a wheel post, masked by a checker exemption. *v9: no exemptions except pad–plate, plate–structure, press fits.*
6. Motor both "on the pad" and "sliding on the clutch". *v9: the carriage is the thing that slides; the motor is bolted to it.*
7. No commutation-sensor location. *v9: section 8.*
8. Cable tunnel 3.5 mm high; receptacle straddling the plate. *v9: plate notch; height conflict flagged in 4.14.*
9. Board offset on the wrong axis. *v9: measured; wheel azimuths re-derived in 6.1.*
10. Speaker fired into a solid pad. *v9: perimeter ports.*
11. No boards for ten bought parts. *v9: 4.19.*
12. Envelope numbers wrong: speaker 9.05 not 8.5; LRA 4.37 not 3.6; light-sensor hole 4.8 not 2.5.
13. No socket holes or plug keep-outs. *v9: 4.13, 4.14, 4.1 line 9.*
14. Microphones face a closed base. *v9: 6.9.*
15. Multi-piece references exported as one body (two supercaps). *v9: separate named bodies always.*

---

## 10. Rules for building the v9 CAD, once the remaining questions are answered

1. Every bought part is placed as its CAD body from `design/cad/bought-parts/`, by file — never as a cylinder or box drawn in the model.
2. `_ENVELOPE`, `_ASSUMED` and `_keepout` bodies stay in the assembly as named bodies until the real part is measured; they are never mounting geometry.
3. Every made part is one revolve or one extrude plus holes wherever possible. A feature that exists only to join two other features means the part should be two parts or a different shape.
4. Every screw, insert, bush socket and connector has a straight tool path in the assembly order of section 6.10, and the order names the tool.
5. No interference exemptions except pad–plate, plate–structure and press fits.
6. Multi-piece references are separate named bodies.
7. The parameter block tags every number MEASURED, PUBLISHED or ASSUMED; the first drawing sheet prints the ASSUMED list.
8. The checker proves the assembly order: for each step, the part being added must be insertable along a straight line without passing through anything already placed.
