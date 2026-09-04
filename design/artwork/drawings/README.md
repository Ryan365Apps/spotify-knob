# Technical drawing sheets — the 60, v9

Plain engineering drawings: black on white, hatched sections, title block. Nothing here is
styled and nothing is drawn by hand — every line is projected from the v9 CAD source, so a
sheet cannot disagree with the model. Dimension and note text is written from the parameter
names too, so a number on a sheet is the number in `params.py`.

| Sheet | What it covers |
|---|---|
| `the60_v9_D01_knob_support` | Knob support. Section A–A on the 30°–210° axis through the wheel at 30°; detail X (V-groove and collar contact, 8:1); detail Y (bush and post, 7:1); plan section at z 20 showing why the wheels are at 30/150/270; isometric of the wheel and bush. |
| `the60_v9_D02_light_display_encoder` | The vertical stack. Section B–B on the 330°–150° axis through the encoder, with the whole height ladder; detail P (halo, 8:1, on an LED pitch); detail Q (encoder and code band, 8:1); plan through the halo at z 6.3; plan through the display seat tabs at z 28.1. |
| `the60_v9_D03_drive_clutch` | The drive. Section C–C on the 90°–270° axis with the clutch engaged; detail R showing engaged and released side by side; plan inside the plate at z 2.5; plan at the drive band; isometric of the carriage and the servo tray. |
| `the60_v9_D04_plate_floor_ports` | The steel plate at 1:1 and the floor at 1:1; section D–D through the back at 0°; detail S of the port face. Cut-outs, fixings, perimeter ports, USB-C, jack and light sensor. |

Each sheet is A3 landscape (420 × 297) in three formats: `.pdf` to print or send, `.svg` to
edit in Illustrator or Inkscape, `.png` to drop into a document.

## What changed from the v8 set

v9 is a different machine below the knob, so two of the v8 sheets were rebuilt and two are new:

* The **gimbal drive and over-centre clutch are gone**. The motor is a JD-Power MY-3514C on a
  carriage that slides radially through the plate, and the clutch is a linear servo pushing the
  carriage. That is D03, which v8 never had.
* The **halo moved**. It is 90 LEDs lying flat on the plate at r 58.8, firing outward into a
  diffuser at r 60–62.5, continuous through 360°. v8 stood the ring on the outside of the wall.
* The **wheels moved** from 60/180/300 to 30/150/270 and up to z 23.4–27.4, and the plate screws
  no longer share structure with the posts.
* The **plate is Ø124 × 5 steel**, not Ø123 × 3 printed, and it now carries a port slot with
  USB-C, a 3.5 mm jack and the ambient-light sensor. That is D04, which v8 never had.
* The **port board is no longer an invented envelope**: the port assembly is modelled, and its
  boards have outlines in `boards/`.

## Where the geometry comes from

`docs/v9/the60_v9/the60_v9/src/params.py` and `model.py`, built with build123d, with every
bought part placed from its own STEP body in `design/cad/bought-parts/step`. Sections are
Boolean intersections with a half space or a slab; hidden-line projection is build123d's
`Drawing` (OpenCascade HLR).

## Regenerating

Needs Python with `build123d` and `cairosvg`. It does not need Blender.

    pip install build123d cairosvg
    export THE60_SRC=.../docs/v9/the60_v9/the60_v9/src
    export THE60_OUT=.../design/artwork/drawings
    python scripts/build.py

`params.py` expects the bought-part STEP files two levels above `src`, in `bought/bought-parts`.
If they live in `design/cad/bought-parts` instead, either copy that folder into place or point
`params.BOUGHT` at it.

`scripts/` holds:

* `engine.py` — the model (cached to BREP so a rerun takes seconds, not two minutes), Boolean
  sectioning, hidden-line views, per-part section hatching.
* `sheet.py` — the A3 sheet, frame, title block, view ports, dimensions, balloons, notes.
* `sheet1.py` … `sheet4.py` — the four sheets.
* `build.py` — runs all four and writes PDF and PNG.

## Two things to know before trusting a sheet

1. **MODELLED, NOT PRINTED.** No v9 part has been made. Every dimension is a model value, not a
   measurement.
2. Bodies the model tags **ENVELOPE** or **ASSUMED** are drawn as envelopes, not as the real
   part: the motor (Ø35 × 14 with no base/bell split), the servo, the pushrod, the plug bodies,
   and the LED flex. The five bench items in `docs/v9/V9.md` are the ones that decide whether the
   drawn geometry survives contact with the real parts — the motor base diameter above all,
   because it is what keeps the LED ring unbroken.

## Not drawn

Electrical layout. The board outlines in `boards/` are shapes, not schematics, and no sheet
here shows a track, a connector pinout or a wiring route.
