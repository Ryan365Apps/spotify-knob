"""print orientation, layer height and note for every printed part - shared by export.py and printcheck.py"""
from model import *
PRINT = {
    "knob_body":          (lambda s: Pos(0, 0, Z_KNOB_TOP) * Rot(180, 0, 0) * s, "0.16", "ONE PIECE. top face down, no supports. bore smooth except the V-groove; the 0.15 code-ring recess is in the crown's underside (the bed face, so it prints as a shallow pocket)"),
    "internal_structure": (lambda s: Pos(0, 0, Z_SEAT_TOP) * Rot(180, 0, 0) * s, "0.20", "v15: INVERTED - the seat flange's top face (the display's seat) on the bed, the wall growing up from it, the wall foot at the top (Ryan, 6 Sep: fewer supports, a stronger part, a flat seat). Nothing rises above the seat any more: the pins, the encoder shim and the bleed foot all sit on the flat face; the bosses hang under the flange and print upward. SUPPORTS: the diffuser lip (a 3.9 ring at z 11.7, outside the wall - easily removed, the face it marks is under the knob skirt) and the three Ø8 wheel-post tops (the bush seats, z 7.1). The pillar tops and the LRA clip ribs carry 45 deg cones/webs; the windows are open at the bed; 0.3 chamfers on the bed face's edges"),
    "halo_diffuser":      (lambda s: Pos(0, 0, -HALO_Z0) * s, "0.20", "on its underside; natural / translucent PETG; no supports"),
    "carriage":           (lambda s: s, "0.16", "standing on the Ø37 shoe, tab up; 12 mm bridge over the sensor pocket; PETG, 4 perimeters (the tab is loaded across its layers)"),
    "servo_mount":        (lambda s: s, "0.20", "flat; a floorless frame for the AGFRC servo, open toward the tab; two ears screwed to the plate"),
    "connect_bracket":    (lambda s: Rot(90, 0, 0) * s, "0.20", "standing on its straight -y edge, the slab vertical (1.5 thick, 28 wide, 50 tall): the feet, ears and bosses stick out sideways and print without support; the M2 insert holes and the csk cones are sideways at Ø3.2 / Ø5.4, fine at that size. (On its feet the slab would hang 1.5 over the bed for 28 mm: supports)"),
    "speaker_cradle":     (lambda s: s, "0.20", "flat; ring under the speaker flange with three snap fingers"),
    "blower_saddle":      (lambda s: Pos(0, 0, Z_BLOWER1 + SADDLE_T) * Rot(180, 0, 0) * s, "0.16", "v15: on its flat top face (the motion board's face) on the bed, the hood's neck walls grow up from it; no supports. Two Ø2.2 through-holes vertical"),
    "hood_lid":           (lambda s: Pos(0, 0, -(PLATE_T + BLOWER_GASKET_T)) * s, "0.16", "v15: flat, 2.5 thick, two Ø2.2 holes; butts against the saddle's neck"),
    "encoder_shim":       (lambda s: Pos(0, 0, -Z_SEAT_TOP) * s, "0.10", "v15: flat, one per height in ENC_SHIM_FAMILY (0.7 / 0.8 / 0.9 / 1.0 / 1.1) - print the set, fit the one the bench wants"),
    "port_face":          (lambda s: Pos(0, 0, PORT_FACE_R0 + PORT_FACE_T) * Rot(0, 90, 0) * s, "0.16", "lying on its outer face (the socket openings print as vertical holes); the USB-C shelf, the light-sensor foot and the screw rail stand up from it; no supports"),
    "collar_0":           (lambda s: s, "0.12", "x3, axis vertical; press over a 623ZZ"),
    "bush_0":             (lambda s: s, "0.12", "x3, stem down / pin up; the 1 mm flange ledge is the only overhang; brass in production"),
}
