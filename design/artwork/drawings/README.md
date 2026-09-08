# Technical drawing sheets — the 60, v15

Plain engineering drawings: black on white, hatched sections, title block. Nothing here is
styled and nothing is drawn by hand — every line is projected from the v15 CAD, so a sheet
cannot disagree with the model. Dimension and note text is written from the parameter names
too, so a number on a sheet is the number in `params.py`.

| Sheet | What it covers |
|---|---|
| `the60_v15_D01_knob_support` | Knob support. Section A–A on the 30°–210° axis through the wheel at 30°; detail X (V-groove and collar contact, 8:1); detail Y (bush and post, 7:1); plan through the wheels; isometric of the wheel and bush. |
| `the60_v15_D02_light_display_encoder` | The vertical stack. Section B–B on the 310°–130° axis through the encoder, with the whole height ladder; detail P (halo, 7:1); detail Q (encoder and code ring, 4.5:1); plan through the halo; plan under the display's seat face. |
| `the60_v15_D03_drive_clutch` | The drive. Section C–C on the 90°–270° axis with the clutch engaged; detail R showing engaged and released side by side; plan inside the core; plan at the drive band; isometric of the carriage and the servo tray. |
| `the60_v15_D04_core_rim_ports` | The base as three parts: the machined aluminium core, the stainless rim ring and the closing plate. Section D–D through the port face; detail S of the ring's vented outer wall; plan of the core's top face; plan through the vents; isometric of the ring. |
| `the60_v15_D05_cooling` | The cooling circuit. Section E–E through the blower at 51°; detail T of the discharge trench and its hood; plan of the duct and fin channels; plan of the ring alone at the vent height; isometric of the blower, saddle and hood lid. |

Each sheet is A3 landscape (420 × 297) in three formats: `.pdf` to print or send, `.svg` to
edit in Illustrator or Inkscape, `.png` to drop into a document.

## What changed from the v9 set

v15 is a different machine below the knob, so D04 was rebuilt around a different base and D05
is new:

* The **base is now three parts**: a CNC 6082 aluminium core with a cooling duct in it, a
  machined stainless rim ring round it carrying the vent openings, and a 1 mm laser-cut
  aluminium closing plate underneath. v9 had a single Ø124 × 5 steel plate.
* **Active cooling exists.** A Delta blower breathes down through the core's web into a ducted
  space between the web and the closing plate, and air leaves through passages across the
  ring's inner land. That is D05, which v9 never had.
* The **halo moved out onto the wall.** The LED strip now stands vertically on the wall's outer
  face at r 84.0–85.6, firing straight out through a diffuser at r 85.8–87.7. v9 lay a flex
  ring flat on the plate at r 58.8 and fired outward across the gap.
* The **structure is inverted.** There is no ledge: the display's seat flange is the datum face
  and the wheel posts hang below it. The display is bonded to that flat face; the columns and
  M4 seat tabs are gone.
* The **encoder reads from below.** The code ring moved off the bore into the crown's underside,
  so the bore is smooth for the wheels and the encoder gap is set by a shim on a flat face.
* The **device grew**: r 87.7 rather than r 62.5, and 35.9 tall overall.

## Where the geometry comes from

Bodies are read from `docs/v15/the60_v15_assembly.step` (and
`the60_v15_assembly_free_spin.step` for the released clutch), because the vendor STEP files
that `model.py` imports are not all in the repo. Dimension text comes from
`docs/v15/the60_v15/src/params.py`. Sections are Boolean intersections with a half space or a
slab; hidden-line projection is build123d's `Drawing` (OpenCascade hidden-line removal).

The knob is drawn on its turned profile, rebuilt from the parameters. The knurl is on the real
part but is not drawn: in section every diamond would be projected.

## Rebuilding

    pip install build123d cairosvg
    python scripts/build.py

The first run reads the 31 MB assembly (about 25 seconds) and caches every body as a BREP file
under `scripts/.cache`; later runs take seconds. The cache invalidates itself when the STEP is
re-exported.
