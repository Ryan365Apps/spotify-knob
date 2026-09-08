# the 60 — design changes for the CAD session

**Working list, edited in place.** Changes decided outside the CAD session that the model has to absorb. **Delete an item once it is built.** This file is not a history — if it is empty, the model is current.

Last edited 8 September 2026, against **v16** as the current mechanical authority. Source documents: `docs/LAYOUT-STUDY.md`, `docs/HALO-OPTICS.md`, `docs/FUNCTION-ALLOCATION.md`, `docs/SMALL-PARTS-SOURCING.md`, `docs/GROUNDING.md`, `docs/CONNECTORS.md`, `docs/HALO-BRIGHTNESS.md`, `docs/THERMAL-PLAN.md`, `docs/SYSTEM-REVIEW.md`.

Where this file names a section number it means **the current specification**, whichever version that is — the numbering has been stable across v10 to v16.

Built in v16 and removed from this list: the converter as the Pololu D24V90F5 on two M2 studs (the old item 1 — its 9 A covers the Pi, the halo at 120 LEDs and the boards); the eccentric bushes and their driver access (the old item 3 — there are no bushes: bought V-groove bearings on fixed pins ride a ridge on the bore, the third on a spring-loaded block whose captive release screw the checker proves reachable with an L-key from the display opening); the extra 5 mm of radius; the halo as HALO-OPTICS (strip face down, the opal ring, the shelf, the liner, two feeds); the drive collar on the bell; the breakouts on the plate and the MCU tray on countersunk M2 studs with nuts above; the Pi powered through its header; the panel jack, the Adafruit light-sensor breakout, the Mill-Max block and the MT6701 module; the ribs deleted. From the old items 4 and 5, the parameter part: the motor's bell (`MOTOR_OD`), its centre radius (`MOTOR_R`, now derived from the collar) and the servo's envelope (`SERVO_L/W/H`) are parameters, not constants. The open questions that came out of the build are in `V16-QUESTIONS.md` (33–40): the microcontroller (a Pico 2 does not fit the tray), the bearings' V to measure, the breakouts' outlines and holes, the block's spring, the halo count, the Pi's power lead, boards on edge.

---

## 1. Assumptions the v16 model made that a real part must confirm

Not decisions — things the model had to guess to build v16, each tagged ASSUMED in the parameter block (`ASSUMED_LIST` prints them; sheet 0 of the drawings lists them):

- The V-groove bearing's V: 1.2 deep, 0.4 root flat, 90° (V623ZZ class). The ridge on the bore and the knob-fitting offset are derived from these two numbers.
- The block's spring: Ø4 × 16 free, 0.8 N/mm (4.0 N seated); its ID runs on the M2 release screw.
- The strip: 4 mm wide, 1.2 thick, 100 LEDs/m (55 on the ring); the diffuser gasket 0.3 foam; the liner 0.4 / 0.6 white PETG.
- The breakouts: TMC6300-BOB holes at its short ends (none? then a pocket and keeper), DRV2605L and 74AHCT125 breakouts 20 × 15 with two holes each (the level shifter's across the board near one end); their parts 2–3 tall with right-angle headers lying flat.
- The microcontroller: ESP32-S3-Zero class 25 × 18, USB-C 3.2 tall (question 33).
- The audio board's hole pattern 24 × 13 (the board is not laid out): it keeps the outer studs inside the intake tunnels' radius.
- The Pololu converter's height 7.6 and its two holes at ±16.
- The Adafruit 4162's sensor 3.0 from its bottom edge; the panel jack's body Ø9 × 14; the Mill-Max block 5.1 × 2.6 × 3.0 with Ø1.5 pins 2.2 compressed.
- The audio board's USB-A plug overmould; the bleed leaf; the rotor sensor lead's flex rating; the blower's gaskets and the Pi's fan header rating (from v15).

---

## 2. The gimbal motor: three generic 2804/2805 motors are being measured (Ryan, 7 September)

The hollow shaft is out of the requirement (nothing passes through the motor). What is still owed from the model is the **report-back**: with the bell as a parameter, how much lateral room in the motor sector is freed per millimetre of bell diameter, and what the drive ratio becomes across a plausible range.

**v16 changed the shape of the question.** The bell no longer touches the bore — a printed drive collar (ID 35 pressed over the bell's top 3.5 mm, OD 39.4) does, above the halo ledge, because a Ø35 bell touching the bore would cross the halo channel. So the drive ratio is set by the **collar's** OD (4.48 : 1 today, `R_BORE / (DRIVE_COLLAR_OD / 2)`) and the motor centre by `MOTOR_R = R_BORE − DRIVE_COLLAR_OD / 2`; a different bell changes the collar's ID and wall, and only through the collar's OD the ratio and the motor centre. A smaller bell can keep the same collar (a thicker collar wall) and change nothing else, or take a smaller collar for a higher ratio and a motor centre further out. When the three motors are measured, give the model each bell's OD and the height at which the bell starts (`MOTOR_OD`, `MOTOR_BASE_H`); the collar is redrawn from them. Report back then: the collar's wall, the ratio and the motor centre for each, and the lateral room in the motor sector (the bell must stay 1.0 inside the wall's window and 0.5 inside the liner).

## 3. The clutch servo: three generic 1.5 g linear servos are being measured (Ryan, 7 September)

The AGFRC C1.5CLS PRO is not the chosen part. The servo's envelope is a parameter (`SERVO_L/W/H`, 21.4 × 15.2 × 6.0) and its frame on the plate follows it, but the **report-back is still owed**: the clearance the frame has in each direction today, and the pushrod height the carriage's push tab (3 × 10 × 14.5) is built to. A part 2 mm longer or 1 mm taller should be a number change, not a redraw. The 2.4 N figure has never been measured — it is the AGFRC's published output, not a requirement; nothing in the model should be built as though 2.4 N is a specification.

## 4. The carrier-board sourcing prompt is parked (7 September)

Of the three sourcing exercises, two have landed and are built (the motion board became bought breakouts on the plate and a microcontroller on the tray; the small parts as `SMALL-PARTS-SOURCING.md`). `CARRIER-BOARD-SOURCING-PROMPT.md` is production-only and parked: nothing to do, but do not tighten the rear sector or the port face around today's numbers, and report how much room could be freed there if asked.

---

## What does not change

So the model is not over-corrected: the plate's ducted construction with the blower on its +y side, the fin channels' direction, the ring's groove and openings, the stainless ring, the pad as a plain ring, the structure's inverted print, the seat at 26.0 and the height at 35.9, and every dimension in `THERMAL-PLAN.md` section 14 as rewritten for v15 all stand as built.
