"""D02 - the light band, the display seat and the encoder (v15)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

ENC_AZ = P.ENC_AZ                                  # 310: the encoder axis, and section B-B
LED_R = (P.R_STRIP_IN + P.R_STRIP_OUT) / 2         # 84.8: the strip's mid-thickness
Z_STRIP0 = P.HALO_Z0 + 0.25                        # the 5.0 strip inside the 5.5 band
Z_STRIP1 = Z_STRIP0 + P.LED_STRIP_W

s = Sheet("LIGHT BAND, DISPLAY SEAT AND ENCODER", "60-15-D02", "AS SHOWN")
s.frame(META)

STACK = ["knob_body", "internal_structure", "base_plate", "rim_ring_STEEL", "closing_plate_AL", "pad",
         "halo_diffuser", "led_strip_ENVELOPE", "encoder_board", "encoder_shim",
         "panel_glass", "panel_components_ENVELOPE", "lens_ASSUMED", "bond_tape"]
vB, hB = engine.radial_section(STACK, ENC_AZ, hidden=False, missing_ok=True)

# ---------------------------------------------------------------- SECTION B-B
pB = Port(s, 22, 100, 1.05, ox=0.0, oy=0.0)
clB = pB.clip("clipB", 17, 30, 179, 106)
pB.draw(vB, clip=clB, hidden=False, hatch_paths=hB, wv=0.32)
s.rect(17, 30, 179, 106, 0.3)
s.text(17, 27, "SECTION  B-B     scale 1.05 : 1", 3.4, weight="bold")
s.text(17, 141, "Right half, on the %g deg - %g deg axis, through the encoder at %g deg. The whole vertical stack, pad to lens."
       % (ENC_AZ, ENC_AZ - 180, ENC_AZ), 2.2, col="#333")
s.line(pB.px(0), 32, pB.px(0), 134, 0.15, dash="6 2 1 2")
s.text(pB.px(0) + 1.5, 38.5, "CL", 2.2, col="#444")

# the v15 height stack, as a ladder of levels read straight from params.py
LEVELS = [(0.0, "core underside, z 0"),
          (P.CLOSING_T, "closing plate top"),
          (P.Z_PLATE_TOP, "core top, halo bottom"),
          (P.HALO_Z1, "halo top"),
          (P.Z_LIP1, "diffuser lip top"),
          (P.Z_SKIRT_BOT, "knob skirt bottom"),
          (P.Z_POST_TOP, "wheel post underside"),
          (P.Z_SEAT_BOT, "seat flange under"),
          (P.Z_SEAT_TOP, "seat face, display sits here"),
          (P.Z_GLASS1, "panel glass top"),
          (P.Z_LENS1, "cover lens top"),
          (P.Z_CODE_FACE, "code ring face"),
          (P.Z_KNOB_TOP, "knob top")]
_lab_y, _prev = [], None
for z, lab in sorted(LEVELS, key=lambda t: -t[0]):
    y = pB.py(z)
    if _prev is not None and y < _prev + 3.1:
        y = _prev + 3.1
    _lab_y.append((z, lab, y)); _prev = y
for z, lab, y in _lab_y:
    s.line(pB.px(P.R_KNOB) + 2, pB.py(z), 121, pB.py(z), 0.12, dash="2 1.5", col="#666")
    s.line(121, pB.py(z), 125, y, 0.12, col="#666")
    s.text(127, y + 0.8, "z %s   %s" % (n(z, 1), lab), 2.0, col="#333")
_y0, _y1 = pB.py(P.Z_KNOB_TOP), pB.py(-P.PAD_T)
s.raw('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#000" stroke-width="0.25" fill="none" '
      'marker-start="url(#ar)" marker-end="url(#ar)"/>' % (117, _y0, 117, _y1))
s.text(115, (_y0 + _y1) / 2, "%s overall, pad to knob top" % n(P.HEIGHT, 1), 2.4, anchor="middle", rot=-90)
pB.dim_h(0, P.R_BORE, -3.5, "r %s bore" % n(P.R_BORE), off=7)
pB.dim_h(0, P.R_KNOB, -3.5, "r %s knob and rim" % n(P.R_KNOB), off=13)

for i, (mx, my, by) in enumerate([
        (LED_R, (Z_STRIP0 + Z_STRIP1) / 2, 40),
        (P.R_DIFF_IN + 1.0, (P.HALO_Z0 + P.HALO_Z1) / 2, 56),
        (P.ENC_R, P.Z_CODE_FACE - 1.0, 72),
        ((P.R_WALL_IN + P.R_WALL_OUT) / 2, (P.Z_SEAT_BOT + P.Z_SEAT_TOP) / 2, 88),
        (P.R_LIP_OUT - 0.5, (P.Z_LIP0 + P.Z_LIP1) / 2, 104)], 1):
    add_balloon(pB, mx, my, 190, by, i)

# ---------------------------------------------------------------- NOTES
s.text(210, 27, "NOTES", 3.4, weight="bold")
note_list(s, 206, 36, [
 (1, "About %d LEDs on a %g per metre strip, %s wide and %s thick, standing VERTICALLY on the wall's outer face at "
     "r %s - %s, z %s - %s. v15 stood the strip up on the wall; v9 lay a flex ring flat on the plate at r 58.8 and "
     "fired outward across the gap."
     % (P.LED_N, P.LED_PER_M, n(P.LED_STRIP_W, 1), n(P.LED_STRIP_T, 1),
        n(P.R_STRIP_IN, 1), n(P.R_STRIP_OUT, 1), n(Z_STRIP0, 2), n(Z_STRIP1, 2))),
 (2, "Diffuser r %s inside, %s - %s outside (bottom to top, flush with the knob and the rim at r %s), so it leans "
     "%s over the band's %s height. Retained by a lip at r %s, z %s - %s, with a %s shadow gap under the knob skirt."
     % (n(P.R_DIFF_IN, 1), n(P.R_DIFF_OUT_BOT, 1), n(P.R_DIFF_OUT_TOP, 1), n(P.R_KNOB, 1),
        n(P.R_DIFF_OUT_TOP - P.R_DIFF_OUT_BOT, 1), n(P.HALO_H, 1),
        n(P.R_LIP_OUT, 1), n(P.Z_LIP0, 1), n(P.Z_LIP1, 1), n(P.Z_SKIRT_BOT - P.Z_LIP1, 1))),
 (3, "Continuous through 360 deg. Standing the strip on the wall takes it clear of everything inside: the motor at "
     "%g deg reaches r %s with its band, and the strip's back face is at r %s. Nothing now breaks the ring."
     % (P.MOTOR_AZ, n(P.MOTOR_R + P.MOTOR_OD / 2 + P.MOTOR_BAND_T, 1), n(P.R_STRIP_BACK, 1))),
 (4, "Peak draw %s A at full white (%s W at 5 V) for %d LEDs at %g mA each. That is what sizes the converter, the "
     "halo feed and its connector; the sustained level is a firmware limit, not a fuse."
     % (n(P.HALO_PEAK_A), n(P.HALO_PEAK_A * 5, 1), P.LED_N, P.LED_MA_FULL_WHITE)),
 (5, "AEDR-8300 at %g deg on a board at z %s, looking UP at a %s code ring on the crown's underside: ring face z %s, "
     "r %s - %s, in a %s recess so the printed crown and the stuck-on ring finish flush. Nominal %s gap, set by the "
     "shim - print the family %s and fit the one the bench wants."
     % (ENC_AZ, n(P.ENC_BOARD_Z0, 1), n(P.STRIP_T), n(P.Z_CODE_FACE, 2), n(P.CODE_R0, 1), n(P.CODE_R1, 1),
        n(P.STRIP_T), n(P.ENC_GAP), " / ".join("%g" % v for v in P.ENC_SHIM_FAMILY))),
 (6, "Reading from below rather than across the bore leaves the bore smooth for the wheels and sets the gap by a "
     "shim on a flat face, not by the knob's radial runout."),
 (7, "Display: the panel sits on the seat flange's top face at z %s, bonded with %s tape; glass z %s - %s, cover "
     "lens r %s x %s thick on top, to z %s. There are no columns and no M4 seat tabs - the inverted structure "
     "prints the seat as one flat face."
     % (n(P.Z_SEAT_TOP, 1), n(P.BOND_T), n(P.Z_GLASS0, 1), n(P.Z_GLASS1, 2), n(P.LENS_R, 1), n(P.LENS_T, 1),
        n(P.Z_LENS1, 2))),
 (8, "The ambient-light sensor is not in this wall: it is in the port face, looking rearward - see D04."),
], w=84)

# ---------------------------------------------------------------- DETAIL P - the halo
HALO = ["base_plate", "rim_ring_STEEL", "internal_structure", "halo_diffuser", "led_strip_ENVELOPE", "knob_body"]
vP_, hP_ = engine.radial_section(HALO, 48.0, hidden=False, missing_ok=True)
dP = Port(s, 320, 78, 7.0, ox=85.0, oy=11.0)
clP = dP.clip("clipP", 300, 30, 100, 80)
dP.draw(vP_, clip=clP, hidden=False, hatch_paths=hP_, wv=0.28)
s.rect(300, 30, 100, 80, 0.3)
s.text(300, 27, "DETAIL P - HALO     7 : 1", 3.0, weight="bold")
dP.dim_v(P.HALO_Z0, P.HALO_Z1, P.R_DIFF_OUT_TOP, n(P.HALO_H), off=4)
dP.dim_h(P.R_DIFF_IN, P.R_DIFF_OUT_BOT, P.HALO_Z0 - 1.2, n(P.R_DIFF_OUT_BOT - P.R_DIFF_IN), off=6, above=False)
dP.leader(LED_R, (Z_STRIP0 + Z_STRIP1) / 2, 318, 40, "strip at r %s" % n(LED_R), size=2.2)
s.text(300, 116, "The strip stands on the wall's outer face and fires straight out through the", 2.2)
s.text(300, 120, "diffuser: r %s to r %s is %s of acrylic in front of the LEDs." % (n(P.R_STRIP_OUT,1), n(P.R_DIFF_OUT_BOT,1), n(P.R_DIFF_OUT_BOT-P.R_STRIP_OUT,1)), 2.2)
s.text(300, 124, "Bench test the diffuser before committing: see docs HALO-BENCH-TEST.", 2.2)

# ---------------------------------------------------------------- PLAN THROUGH THE HALO
HZ = (P.HALO_Z0 + P.HALO_Z1) / 2
PL = ["base_plate", "rim_ring_STEEL", "internal_structure", "halo_diffuser", "led_strip_ENVELOPE",
      "knob_body", "carriage", "motor_motor_ENVELOPE", "motor_band"]
vH, hH = engine.plan_section(PL, HZ, missing_ok=True)
pH = Port(s, 82, 206, 0.56)
clH = pH.clip("clipH", 17, 150, 130, 112)
pH.draw(vH, clip=clH, hidden=False, wv=0.25, hatch_paths=hH)
s.rect(17, 150, 130, 112, 0.3)
s.text(17, 147, "PLAN - HORIZONTAL SECTION AT z %s     scale %.2f : 1" % (n(HZ, 1), pH.k), 3.0, weight="bold")
s.line(pH.px(-P.R_KNOB), pH.py(0), pH.px(P.R_KNOB), pH.py(0), 0.12, dash="6 2 1 2")
s.line(pH.px(0), pH.py(-P.R_KNOB), pH.px(0), pH.py(P.R_KNOB), 0.12, dash="6 2 1 2")
for az, lab in ((0, "0 deg USB-C"), (P.MOTOR_AZ, "%g deg motor" % P.MOTOR_AZ), (ENC_AZ, "%g deg encoder" % ENC_AZ),
                (P.BLOWER_AZ, "%g deg blower" % P.BLOWER_AZ)):
    a = math.radians(az)
    s.text(pH.px(96 * math.cos(a)), pH.py(96 * math.sin(a)) + (2.5 if math.sin(a) < -0.5 else 1.0),
           lab, 2.3, anchor="middle")
s.text(17, 266, "About %d LEDs on a %s deg pitch at r %s, unbroken all the way round: on the wall's outer face nothing "
       "inside can interrupt it." % (P.LED_N, n(360.0 / P.LED_N, 1), n(LED_R)), 2.2)
s.text(17, 269.5, "The rim ring below carries the vents; this cut is above it, in the halo band. The port slot at 0 deg "
       "passes under the halo, through the core.", 2.2)

# ---------------------------------------------------------------- DETAIL Q - encoder and code ring
dQ = Port(s, 200, 192, 4.5, ox=P.ENC_R - 1.0, oy=(P.ENC_BOARD_Z0 + P.Z_CODE_FACE) / 2)
clQ = dQ.clip("clipQ", 153, 150, 94, 80)
dQ.draw(vB, clip=clQ, hidden=False, hatch_paths=hB, wv=0.28)
s.rect(153, 150, 94, 80, 0.3)
s.text(153, 147, "DETAIL Q - ENCODER AND CODE RING     4.5 : 1", 3.0, weight="bold")
dQ.dim_v(P.ENC_BOARD_Z0 + P.ENC_BOARD_T + P.ENC_PKG_H, P.Z_CODE_FACE, P.ENC_R + 4.0, n(P.ENC_GAP), off=5)
dQ.dim_h(P.CODE_R0, P.CODE_R1, P.Z_CODE_FACE + 1.4, n(P.CODE_R1 - P.CODE_R0), off=4)
s.text(153, 236, "Package top to ring face: %s nominal, set by the shim under the" % n(P.ENC_GAP), 2.2)
s.text(153, 240, "board, not by the knob's radial runout. The ring is a %s recess" % n(P.STRIP_T), 2.2)
s.text(153, 244, "in the crown's underside, so the stuck-on ring finishes flush.", 2.2)

# ---------------------------------------------------------------- PLAN ON THE SEAT FACE
SZ = P.Z_SEAT_TOP - 0.5
vS, hS = engine.plan_section(["internal_structure", "knob_body", "panel_glass"], SZ, missing_ok=True)
pS = Port(s, 324, 196, 0.56)
clS = pS.clip("clipS", 253, 150, 142, 92)
pS.draw(vS, clip=clS, hidden=False, wv=0.25, hatch_paths=hS)
s.rect(253, 150, 142, 92, 0.3)
s.text(253, 147, "PLAN - HORIZONTAL SECTION AT z %s, UNDER THE SEAT FACE     scale %.2f : 1" % (n(SZ, 1), pS.k),
       3.0, weight="bold")
bb = engine.bbox(["panel_glass"])
s.raw('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#000" stroke-width="0.25" '
      'stroke-dasharray="2.5 1.5"/>'
      % (pS.px(bb.min.X), pS.py(bb.max.Y), (bb.max.X - bb.min.X) * pS.k, (bb.max.Y - bb.min.Y) * pS.k))
s.raw('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="#000" stroke-width="0.2" stroke-dasharray="2 1.5"/>'
      % (pS.px(0), pS.py(0), P.LENS_R * pS.k))
s.text(253, 246, "Dashed rectangle: the panel, %s x %s, on the seat face above this cut. Dashed circle: the cover lens, r %s."
       % (n(bb.max.X - bb.min.X, 1), n(bb.max.Y - bb.min.Y, 1), n(P.LENS_R, 1)), 2.2)
s.text(253, 249.5, "The seat is one flat face at z %s. Panel mass %g g is carried on the bond, so the tape's area and its "
       "peel strength are the fixing." % (n(P.Z_SEAT_TOP, 1), P.PANEL_MASS_G), 2.2)

save(s, "the60_v15_D02_light_display_encoder")
