# the 60 — layout study: where every movable part can go, at Ø175.4 and Ø185.4

**8 September 2026. Status: study, for a decision.** Asked for by Ryan after the bought-board sourcing results: reassess every part that has a choice of position, with all physical constraints considered, the ports dictating most of them, and the extra 5 mm of radius as an option. Figures: `layout/layout_study.png` (the two layouts that place every bought board, with cable schematics, and the tray layer), `layout/board_room.png` (the v15 free-room map that started this), `layout/sprung_wheel.png` (the wheel-preload concept decided alongside it).

**Method.** The v15 assembly was sectioned at nine heights above the plate top; every body's footprint in the low layer (z 8–14, parts standing on the plate) is an obstacle. The Pi window — the hole in the plate the Pi sits in, with its three plug notches — is added as an obstacle, because nothing can stand where there is no plate. Cables and wires are left out of the obstacles (they re-route) and drawn back in afterwards as schematic routes. Movable parts are moved as their v15 footprints; the bought boards are placed by a search that maximises clearance, with 1.5 mm of margin all round, largest board first. The +5 mm radius is modelled by pushing every rim-relative part (wall, posts, pillars, motor and carriage with the servo, port face, actuator) out by 5 mm and leaving the centre stack (Pi, adapter, connect board, blower) where it is.

Boards, as the sourcing documents give them: microcontroller either a Pico 2 (51 × 21) or a small ESP32-S3 board (about 25 × 18); TMC6300 motor-driver breakout 25.4 × 20.3 (makes heat, must sit on the plate); DRV2605L haptic breakout and a 74AHCT125 level shifter, both taken as 20 × 15 (sizes not published); the converter as the Pololu D24V90F5, 40.6 × 20.3.

---

## 1. What fixes the geography

| Part | v15 position | Why it is there | Movable? |
|---|---|---|---|
| Port face (barrel, USB-C, jack, light sensor) | az 0 (rear), in the ring's port slot | The ports must face the rear | No — this is the anchor |
| Pi 5 in its window | x −52.75 to 36, y −38.75 to 18.75 (an 88 × 57 hole through the plate) | Its USB ports face the port side; its HDMI ribbon and flat cable go to the adapter above it; it sits in the plate for cooling | Only with the whole centre stack; not in this study |
| Display adapter and touch board | above the Pi on its standoffs | Panel flex reaches them; the adapter's HDMI socket (to z 23.7) is the height-deciding part | With the Pi |
| Connect board and bracket | rear, r 45–78 | Between the adapter and the panel flex at az 0 | No |
| Blower, hood, trench | az 51, r 51, over the +y plenum | Its outlet must reach the exhaust groove at 18–60°; mirroring to 300–342° is possible but only swaps areas | Along the plenum arc; mirror |
| Motor, carriage, servo | motor az 90, r 65.7; servo inboard at r 19 | The bell drives the bore; the servo pushes the carriage radially, so it sits inboard of the motor — at az 90 that puts it just clear of the window's top edge | In azimuth, but the servo must not land over the window, which rules out most of the south |
| Wheel posts | 30°, 150°, 270°, r 76.9 | Clear of the speaker, the port slot and the motor | In azimuth, 120° apart |
| Pillars | 160°, 240°, 320°, r 77.2 | Plate-to-structure screws | In azimuth; they steal a Ø7 spot at the wall wherever they go |
| Converter | az 180, r 65.5, on a gap pad | Needs the plate for heat; the front crescent is the widest free arc | Yes |
| Audio board | az 290, r 55 | Beside the Pi's USB stacks (its USB lead) | Yes, but its 40 × 25 needs a crescent 25 deep, and there are two of those |
| Speaker | az 127.5, r 59 | Boxed in by the adapter's edge, the motor's band, the wall and pillar 160 | Yes, but Ø40 plus its cradle fits only where it is or at the front, and the front is too shallow (the adapter's corner reaches r 50.7 at 167°) |
| Actuator and its contacts | az 257, on the wall | Any azimuth on the wall | Yes |
| Encoder head, bleed contact, locating pins | on the seat flange | Any azimuth | Yes |
| Halo tail notch | az 64 | Beside the strip's joint | Any azimuth; a second notch near the converter for the far-end feed |

The lesson of the table: the three big things — ports at the rear, the Pi window in the middle, the motor and its servo in the north — are coupled to each other and leave the south band (y below −40) and the south-east crescent as the only real room. Moving the converter, the audio board or the speaker does not create room; each has exactly one alternative home, and it is a worse one.

---

## 2. What was tried

| Candidate | Result with 1.5 mm margins |
|---|---|
| Ø175.4 as built, Pico on the plate | Pico: no room. Driver breakout: no room. Only the haptic breakout fits (253°, 3.2 mm) |
| Ø175.4 as built, small ESP32 on the plate | ESP32 fits at 253° with 1.5 mm — and then takes the only spot the driver breakout could have used |
| Ø175.4, audio board to the front (165°), converter to 205°, pillar 160° moved | Fails: the front crescent is bounded by the adapter's corner (r 50.7 at 167°), the 150° post and the speaker, so a 40 × 25 board does not fit there; the converter at 205° hits the Pi's USB-C plug notch |
| Ø175.4 as built, Pi powered through its header (USB-C plug notch deleted) | Driver breakout at 234° with **0.6 mm** — not acceptable; haptic 1.3 mm; level shifter no room |
| **Ø175.4, audio board parked for the prototype** (speaker kept), Pi via header, MCU on the tray | **All three plate boards fit: driver 288° (6.1 mm), haptic 258° (3.6), level shifter 233° (3.2)** |
| Ø185.4 as built, Pico on the plate | Pico: still no room (the constraint runs along the arc, not across it) |
| **Ø185.4 as built, Pi via header, MCU on the tray** | **Everything kept and all three plate boards fit: driver 254° (2.8 mm), haptic 229° (3.6), level shifter 324° (1.0 — or on the tray)** |

In every candidate the microcontroller goes on the tray above the display adapter: a clear 5 mm layer (z 19.5–24.5) between the adapter's tallest parts and the panel's back-side components, carried by the adapter's own four screw posts, 20 mm of clearance in plan for a bare Pico. No plate layout at either radius takes a Pico with margins.

---

## 3. Findings

1. **The plate is out of room at Ø175.4 with everything kept.** The one board that must be on the plate — the motor driver, for its heat — has no place with acceptable clearance. Either the audio board is parked for the prototype (and with it the speaker has no job until audio's turn in the order of work), or the radius grows.
2. **The +5 mm buys the driver's place.** Its 900 mm² of extra area lands mostly in the south band, which deepens by 5 mm, and that is exactly what the driver breakout needed. With it, nothing is parked and every board has 2.8 mm or better except the level shifter at 1.0 — which is a signal part and can go on the tray instead. Costs: the crown's flat bezel goes from 20 to 25 mm (the display is fixed; the radius has nowhere else to go), the object is Ø185.4 (Ø189.4 at the halo band), roughly 100 g heavier, 6 % more halo length and current, and the fin field, trench, connect bracket and window surroundings all get a pass.
3. **Relocating the big parts does not help.** The audio board, the converter and the speaker each have one alternative home and it is worse. The blower's mirror image only swaps the 33–60° area for the 300–345° one. The motor cannot go south because its servo would land over the Pi window. Reassessing every part was worth doing: the answer is that the ports, the window and the motor leave two crescents, and that is what there is.
4. **Powering the Pi through its header** (the small-parts document found the Pi 5's USB-C carries no data anyway) deletes the plug head's 14 × 15 notch in the window and its lead. Small, free, and it is what makes the 234° spot exist at all.
5. **The tray is the microcontroller's place** in every layout. It is a printed part on the adapter's four screw posts with longer screws; bare boards only (no pin headers) because the layer is 5 mm; the flat cable and HDMI ribbon that cross it are routed around it.

---

## 4. Fixings and cables in the two layouts

**Fixings (Ryan's rule: countersunk M2 screws pointing up, nuts above the boards, printed spacers).** Each board takes two M2 studs standing up through the plate — four for the driver breakout, two each for the haptic breakout and the level shifter: eight studs, each on a full-depth pier through the duct so the countersunk head can sit flush in the closing plate's underside and the screw is held by it. Each pier interrupts one fin channel over Ø7; v15's nine closing-plate screws already use the same construction with cross-cuts, and the airflow cost is a few percent per pier on that channel. The converter keeps its two M2.5 into the web (its position does not move). The tray uses the adapter's four posts. The audio board, if kept, keeps its four studs. The speaker cradle is unchanged.

**Cables, as drawn (schematic).** A west trunk runs above the converter at z 17–19 between the tray and the south band: the driver's six PWM lines, the haptic breakout's I²C, and the Pi's 5 V. From the driver breakout the three motor phases go north the same way and over the plate's north-west to the motor (about 150 mm — long for phase leads but fine at 1 A; if the bench objects, the driver moves to the 60–80° crescent at reduced margin). The rotor sensor's flex lead runs from the tray to the carriage. The encoder's two lines run from the tray round the west and south to the flange at 330°. The level shifter takes the LED data from the Pi's header and feeds the halo tail's notch at 64°; the halo's 5 V comes from the converter, once at the notch and once at a second notch near the converter for the far end. The 12 V pair runs from the barrel inlet along the south band to the converter. The external USB-C's lead goes north of the window to the tray (the host link is the microcontroller's). Light sensor and servo go to the Pi's header; the blower to the Pi's fan header. With the audio board kept: its USB lead to the Pi's stack (short), the jack lead from the port face, and the speaker lead round the west trunk. About twenty leads; none longer than 160 mm; pre-made jumper leads and crimped pairs for the prototype, per the sourcing document.

---

## 5. Recommendation

Both layouts work; they differ in what they cost. **Ø175.4 with the audio board parked** keeps the object as designed and costs the prototype its audio until audio's turn in the order of work (when the reduced custom board takes the microcontroller's place and gives the south band back). **Ø185.4 with everything kept** costs 5 mm of bezel and the pass over the plate's features, and buys healthy margins and no parking. I would build Ø185.4 if the 25 mm bezel is acceptable when you see it drawn — it is an aesthetic you have to look at, not a number I can decide — and Ø175.4 with audio parked otherwise. Either way: the Pi powered through its header, the microcontroller on the tray, the driver breakout on the plate on four studs.

**Related decision, same day (`layout/sprung_wheel.png`).** The knob's preload: two fixed wheels at 30° and 150° locate the knob; the 270° wheel sits on a block sliding radially in a printed channel with a roof, pushed out by a spring of about 4 N, retracting 4 mm for assembly and parked by a Ø2 pin while the knob goes on. No eccentric bushes, no lock, no adjustment, no hole through the plate. The wheels become bought V-groove bearings (V623ZZ class), so the knob's bore gets a male V-ridge instead of the groove.
