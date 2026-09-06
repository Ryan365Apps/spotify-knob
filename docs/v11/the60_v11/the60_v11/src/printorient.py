"""print orientation, layer height and note for every printed part - shared by export.py and printcheck.py"""
from model import *
PRINT = {
    "knob_body":          (lambda s: Pos(0, 0, Z_KNOB_TOP) * Rot(180, 0, 0) * s, "0.16", "ONE PIECE. top face down, no supports. bore smooth except the 0.15 code-band recess and the V-groove"),
    "internal_structure": (lambda s: Pos(0, 0, -Z_PLATE_TOP) * s, "0.20", "upright on the wall foot. SUPPORTS in two places only: under the seat flange (r 62-81.2 at z 20.4 above the bed - a ring inside the wall, hidden face) and under the diffuser lip (r 83.9-86.7 at z 5.5 - a thin ring outside). Everything else self-supporting: open-topped windows, 1 mm slit roofs, 45 deg hole ends"),
    "deck":               (lambda s: Pos(0, 0, Z_DECK1) * Rot(180, 0, 0) * s, "0.20", "upside down: its flat top face on the bed, only the three Pi legs standing up; no supports. 14 x M2.5 nuts press into the pockets in the top face"),
    "halo_diffuser":      (lambda s: Pos(0, 0, -HALO_Z0) * s, "0.20", "on its underside; natural / translucent PETG; no supports"),
    "carriage":           (lambda s: s, "0.16", "standing on the Ø37 shoe, tab up; 12 mm bridge over the sensor pocket; PETG, 4 perimeters (the tab is loaded across its layers)"),
    "servo_mount":        (lambda s: s, "0.20", "flat; tray for the AGFRC servo envelope, open toward the tab; sits on the deck"),
    "speaker_cradle":     (lambda s: s, "0.20", "flat; ring under the speaker flange with three snap fingers"),
    "port_face":          (lambda s: Pos(0, 0, PORT_FACE_R0 + PORT_FACE_T) * Rot(0, 90, 0) * s, "0.16", "lying on its outer face (the socket openings print as vertical holes); the USB-C shelf, the light-sensor foot and the screw rail stand up from it; no supports"),
    "collar_0":           (lambda s: s, "0.12", "x3, axis vertical; press over a 623ZZ"),
    "bush_0":             (lambda s: s, "0.12", "x3, stem down / pin up; the 1 mm flange ledge is the only overhang; brass in production"),
}
