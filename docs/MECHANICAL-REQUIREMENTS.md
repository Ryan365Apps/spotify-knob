# the 60 — mechanical requirements as they stand, with where each one came from

**Date:** 2 September 2026, revised the same day with Ryan's rulings (marked **RULING**). Every mechanical requirement currently in force, in plain words. The origin column matters: **you** means Ryan stated it; **session** means an earlier session derived it and it hardened into a decision or a rule; **research** means one of the four R&D answers added it. Anything marked *session* is a candidate for the question "was this ever actually a requirement?"

## The object

| Requirement | Origin | Where it is written |
|---|---|---|
| ~~135 mm across~~ **RULING: not a requirement.** Smaller is preferred while staying chunky. The visible screen is 87.6 mm; the knob only has to sit outside that. At the display's 115 mm the knob can be thin-walled and its rim can reach inward over the display's dead border toward 87.6 mm, as close as possible — a rim up to ~13.7 mm wide per side | you | today |
| 40 mm tall at most; 45 mm is failure | you (via the CAD brief) | decision 37 |
| The knob is at least two thirds of the visible side | you | this session, v6a onward |
| **RULING:** the top rim surface does not have to be tall | you | today |
| Ergonomic model is a mouse, not a thermostat: heel of the hand on the desk, fingers to the screen, palm across the knob | session | decision 38 |
| The knob must spin effortlessly from a thumb on the side, a hand resting alongside, an outstretched finger, or a fingertip on the top rim, leaving two fingers free to touch | you | software contexts document, interaction model |
| At least 250 g, concentrated low; steel base plate | session | decision 42 |
| Hidden mass ring in the knob for free-spin inertia — **RULING: optional; keep only if it helps the flywheel feel** | session | decision 32 |
| Sits flat on a desk, not secured; rubber pad, not feet | you | memory, v6a.2 |
| No permanent cable; sockets face away from the user at twelve o'clock | you | v6a.2 |
| No visible screws, no logo on the face, fully re-openable, heat-set inserts, no glue | you | build rules from v1 |
| Printed for prototypes, CNC aluminium for production — **RULING: the "nothing else in the assembly changing" clause is removed** (it meant the printed and machined knobs must have identical interfaces so the swap needs no other redesign) | session | decision 46 |
| Wide 45° chamfer on the knob's top outer edge, diamond-cut after anodising; smaller smooth chamfer at the glass; flat coin-edged rim; knurl on the side; small chamfer on the skirt's lower edge; both crown chamfers smooth, as if lathe-turned | you | decision 45 and this session |
| Chunky diamond knurl | you (twice) | memory; the industrial design research would make it finer on the machined unit |
| Type III hardcoat anodising; the bright chamfer must be sealed | research | industrial design answer |

## The knob's bearing

| Requirement | Origin | Where |
|---|---|---|
| Bearing and display must not be stacked; recover height | you (via the CAD brief) | decision 39 |
| Route B: three V-groove wheels under the display, rail on the knob's skirt | you ("YES route b") | this session |
| Wheels or a continuous race is still open; print both and compare | session | decision 41 |
| Rim runout 0.05 mm is felt; it is the difference between expensive and cheap | session | open question E |
| The knob must clear everything static by at least 0.4 mm; 0.3 mm running clearance, 0.15 mm static fits | you (standing build rule) | v1 onward |
| Low off-detent friction and high inertia for free spin | research | industrial design answer; now load-bearing because scrolling needs free spin |

## The clicks (detent)

| Requirement | Origin | Where |
|---|---|---|
| Sixty positions per turn | you | the product's name |
| ~~The object still clicks like a watch bezel with no power~~ **RULING: "no power" meant unplugged, and unplugged behaviour is not a requirement. What matters is idle with the PC on — the device is powered then (USB gives at least 2.5 W; idle draw is about 0.84 W). The requirement is: at idle the clicks are present and cost no power and no heat, which magnets give and a motor cannot** | you | today; decision 18 stands down |
| Three layers: magnets = fixed scale and weight; motor = everything dynamic; vibration actuator = event confirmations | session | decision 17 |
| Sixty steel pegs on the rotating knob, six magnets on the fixed part; a ring of magnets, never one | session | decisions 21, 24, 25 |
| Magnet counts that work with sixty pegs: 3, 4, 5, 6, 10, 12 — never 8 | session (arithmetic) | decision 22 |
| Click strength 60–150 mNm peak, adjustable; design for the top of the range | session | decision 29 (decided in principle) |
| Click strength is adjustable in use; the mechanism that adjusts it moves at "gesture cadence", a few times an hour | session | decision 20 — **now contradicted by your ask for a fast-acting carrier** |
| The carrier moves vertically, about 2 mm | session | decision 26 — **replaced by sideways groups in the v6c proposal** |
| ~~The adjusting mechanism must hold position with no power; not a solenoid, not shape-memory wire~~ **RULING: not a requirement.** Derived by a session from decision 18, which has itself stood down. Solenoids, latching solenoids and spring returns are back on the table; the power research's fast gearmotor-and-cam with dwell flats still holds by geometry for free | session | decisions 27, 28 |
| Dynamic click strength comes from the motor because a screw cannot move in a tenth of a second | session | decision 19 — premise removed by a fast carrier |
| Magnets stand on their 6 mm edge, magnetised outward, all six the same way, pinned on the drawing | research | detent answer (a factor of 4.4) |
| Pegs are soft mild steel, not hardened grub screws, not stainless; M3 flat-point studs or 3 mm steel balls | research | detent answer, sourcing document |
| Magnet-to-peg gap 0.8 mm, shimmable to 0.6; combined concentricity within ±0.05 mm | research | detent answer |
| Click-to-click uniformity within 10 %; rim back-play a fraction of a millimetre | research | detent answer (Rolex bezel benchmark) |
| The clicks can be fully cancelled while the knob spins, for as long as a finger rests on the "feel" hotspot | you (via the scroll-wheel decision) | software contexts document — met by moving the magnets, not by the motor; the power research reaches the same conclusion |
| The carrier should be fast-acting so software contexts change the clicks | you | today |

## The motor

| Requirement | Origin | Where |
|---|---|---|
| The motor is a torque motor acting directly on the knob — it pushes and pulls against the hand for end-stops, ramps, half-clicks, per-context feel | session | decision 17, CAD brief layer table |
| The motor's own lumpiness must be near zero, or locked to the sixty pegs in count and phase, or the two beat | session | decision 30 |
| Custom large-diameter ring motor; no catalogue part exists | session | decision 31 (decided in principle); confirmed by the sourcing document |
| Printed-circuit-board ironless ring stator under the knob, 30–100 mNm, zero cogging by construction; reserve 5–6 mm of height | research | detent answer, recommendation 1 |
| Eddy-current drag from the stator must be imperceptible against the clicks (under 2–3 mNm) | research | detent answer, rig gate 1 |
| ~~Motor cancels the clicks continuously while scrolling~~ **RULING: no longer a firm decision.** The power research finds it costs 1.4–25 W continuously and puts the heat in the ring | you | software contexts document |
| Whether the ring motor is needed at all once the magnets are adjustable in 100 ms | **open — pros and cons in `RING-MOTOR.md`** | today |

## Sensing and touch

| Requirement | Origin | Where |
|---|---|---|
| Delete the gear train and on-axis sensor; read the knob's angle from a ring | session | decisions 33, 34 |
| Keep the sensing magnetically separate from the click magnets | session | decision 35 |
| Continuous position between clicks, for smooth scrolling and the light tick | you (via scroll) and research | software contexts; screen/light answer |
| About 0.02° resolution for a stable motor loop; an index mark so the sensor frame binds to the magnet frame at power-up | research | detent answer |
| ~~Touch must reject a resting palm while the ring moves under other fingers~~ **RULING: removed.** Derived from the "hand resting alongside" grip in the software document, not stated; the rim's width means no palm rests on it | session | — |

## Light, sound, vibration

| Requirement | Origin | Where |
|---|---|---|
| The light fires down and outward from the fixed base, never from the rotating part | session | decision 43 |
| Full 360° ring that still accommodates the sockets | you | today |
| Brighter than the 20 % cap — **RULING: depends on the bench test; more light is better.** The power research finds 20 % duty reads as about 52 % perceived brightness, so the cap is not the limitation; count, diffusion and gamma are | you | today; power research |
| The light is not mechanically coupled to the magnet carrier; software leads the clunk by 80 ms | session | decision 47 — **contradicted by your ask today**; three options in the v6c proposal |
| **RULING, extended:** the lights should convey scrolling — radiating in time with the knob as it spins, thrown further out radially with speed and more acute (pointing down) at low speed | you | today |
| Diffuser at least 4 mm from the LEDs; 83 % opal; outward lean of 8° at most | research | industrial design answer |
| The shadow gap under the knob stays dark | research | industrial design answer |
| Speaker for notifications only; never music; never doubles the click | you and research | decisions 11, 15; sound answer |
| Vibration reaches the fingers through the bearing — to be proven on the rig | session | open question C |

## Connections and power

| Requirement | Origin | Where |
|---|---|---|
| One USB-C cable, no battery, no cloud | you | decisions 6, 7 |
| USB-C and 3.5 mm headphone socket; the jack is core, it serves the DAC | you | v6a.2 |
| Sockets cost as little height as possible — "a slim phone on its back" | you | v6a |
| The cable must be replaceable | session | decision 44 — met by "no permanent cable" |
| The steel plate bonded to ground at one point only, at the USB-C | research | audio answer |

## Display

| Requirement | Origin | Where |
|---|---|---|
| Display designed as a replaceable module on a defined interface | session | decision 65 |
| Optical bonding kept | session | decision 67 |
| Display disc 115 mm, 6 mm thick; board hangs below on 1 mm standoffs, components down | you (from the drawings) | this session |

## Standing prototype rules (yours, from v1)

Printed in PETG; minimum wall 1.6 mm; no overhangs over 45° on functional surfaces; M3 heat-set inserts; no glue; every part re-openable; every dimension in one parameter block; every check automated; anything unverified is a named parameter marked V.
