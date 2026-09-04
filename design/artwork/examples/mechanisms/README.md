# Mechanism sections — the 60, v9

Eleven views cut from the v9 geometry, made to answer one question: **where does each bought
component actually sit?** They are the pictures behind `../../MECHANISMS.html` — open that file for
the same images with numbered balloons and a keyed parts list. This README is the plain-text version.

Rebuilt 4 September 2026 from `docs/v9/the60_v9`, which is the current model: 302 named bodies,
0 check failures. Nothing here is carried over from v7.1 or v8.

## How to read them

**z = 0** is the underside of the steel plate. The 1.5 mm pad is below it, and the top of the knob
is at z 38.1, so the device is 39.6 mm tall.

**Azimuth** is measured anticlockwise from the +X axis, which is the USB-C socket at the back. In
the plan views 0 degrees is at the top of the frame, and azimuth increases anticlockwise from there.

**A vertical section at azimuth A** cuts on the plane that holds A and A+180. The camera stands at
A-90 and the half in front of it is removed, so the mechanism at A is cut through the middle and
appears on the right of the frame; A+180 is on the left. `04-ports` is a plan, not a vertical cut,
because the three back-panel parts sit side by side across a 32 mm face and any vertical plane hides
two of them.

**Colour tells you what a thing is:**

| Colour | What |
|---|---|
| orange | the gimbal motor |
| deep orange | the flat drive band |
| amber | the clutch: linear servo |
| light amber | the sliding carriage — the one printed part that moves |
| steel blue | 623ZZ bearings |
| green | encoder |
| violet | haptic LRA |
| blue | speaker |
| teal | supercapacitors |
| yellow-green | USB-C, 3.5 mm jack, light sensor, DAC |
| warm white | halo LEDs, their flex ring, the diffuser |
| slate | the display disc and its board |
| dark green | circuit boards |
| mid grey | the steel plate |
| light grey | printed structure |
| **dark grey** | **a cut face — where the section knife passed** |

If a surface is dark grey it is not a part, it is the inside of something you are looking through.
Bought parts keep their colour where they are cut; printed parts do not.

## The views

| File | Cut | Shows |
|---|---|---|
| `00-plan-floor` | plan z 12 | motor, carriage, servo, speaker, driver board, supercaps, LRA, the three port parts, the perimeter sound ports |
| `00b-plan-board` | plan z 26 | the display board and the three wheels that have to clear its corners |
| `01-drive` | 90 deg | the gimbal motor engaged: band on the bore, carriage on the pad, commutation board underneath |
| `01b-clutch` | 90 deg, retracted | the same with the carriage pulled back 2.4 mm and the knob free |
| `02-encoder` | 330 deg | the AEDR-8300 reading the code band across its 2.00 mm gap |
| `03-wheels` | 30 deg | a 623ZZ in its V-collar on an eccentric bush, running in the groove |
| `04-ports` | plan z 3 | USB-C, jack and light sensor in one 32 mm slot through the plate |
| `05-halo` | 200 deg | 90 LEDs lying flat on the plate firing outward into the diffuser |
| `06-bay` | 152 deg | the whole vertical stack in one full-diameter cut |
| `07-speaker` | 270 deg | the speaker cone-up in its cradle and the perimeter ports |
| `08-display` | 42 deg | a support column, its 1.2 mm seat tab, and the 1.5 mm gap it works in |

## What these views do not settle

1. **Motor base diameter and bell height.** The model assumes the stator base is Ø30 for its lowest
   4.3 mm. At the full Ø35 the LED ring is interrupted at the motor; a lower bell fouls the diffuser
   lip. Nothing published — measure it.
2. **Which end of the shaft carries the magnet.** The commutation board sits under the motor inside
   the carriage. If the magnet is at the top instead, the display rises about 3 mm and the device is
   over its height limit.
3. **Motor bolt pattern.** The carriage has a Ø36 locating rim and nothing else.
4. **Servo lugs and pushrod.** The mount is a tray; the rod-to-tab joint is not drawn.
5. **Band grip at 2.4 N.** If the flat band slips on the bore, add the 2 : 1 bell-crank.
6. **Electrical layout.** The driver, port, encoder and commutation boards are outlines only.

## Regenerating them

`../../scripts/the60_v9_mech_sections.py` builds the scene and renders every view; it runs headless
against the `bpy` module or from inside Blender. It reads `../../blender/v9/*.obj`, which are the
302 named bodies of `docs/v9/the60_v9/the60_v9_assembly.step` tessellated straight out of the STEP —
so the artwork cannot drift from the model.

`../../scripts/build_mechanisms_html.py` then writes `../../MECHANISMS.html`. Balloon positions are
computed, not placed: each keyed item carries a point in model coordinates and the script projects it
through the same camera that rendered the view, using `views.json` written by the renderer. Change a
view's framing and the balloons follow.

Three things will waste your time if you do not know them:

* the section boolean **must use the EXACT solver**. The FLOAT solver silently leaves the model uncut
  and still reports success.
* `material_mode='TRANSFER'` on the printed parts' boolean is what gives the cut faces their dark
  colour. Bought parts use `'INDEX'` so they keep their own colour where they are cut.
* a plan camera must set `rotation_euler` directly, and the render background must come from a world
  datablock — `shading.background_type='VIEWPORT'` renders black in a final render even though the
  viewport shows it correctly.
