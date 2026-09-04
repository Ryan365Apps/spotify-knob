"""D04 — the steel plate and the floor: cut-outs, fixings, ports, back panel."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

PORTS_CUT = sum(1 for i in range(P.PORT_N)
                if abs(((7.5 + 15.0 * i - P.MOTOR_AZ + 180) % 360) - 180) <= 30)
PORTS_DRILLED = P.PORT_N - PORTS_CUT
# model.carriage_hole() is built from MOTOR_R and CLUTCH_LIFT, not from
# params.CARRIAGE_HOLE_R0/R1 (which nothing in model.py reads), so the numbers
# on the sheet are taken from the shape that is actually cut.
HOLE_D = P.MOTOR_OD + 2 * 1.0 + 1.5
HOLE_R1 = P.MOTOR_R + HOLE_D / 2
HOLE_R0 = P.MOTOR_R - P.CLUTCH_LIFT - HOLE_D / 2
TAB_R0 = P.MOTOR_R - P.MOTOR_OD / 2 - 3.5 - 5.0


s = Sheet("BASE PLATE AND FLOOR — CUT-OUTS, FIXINGS, PORTS", "60-09-D04", "AS SHOWN")
s.frame(META)

# ---------------------------------------------------------------- THE PLATE, 1:1
vP, hP = engine.plan_section(["base_plate"], P.PLATE_T / 2)
pP = Port(s, 87, 100, 1.0)
clP = pP.clip("clipP", 17, 30, 140, 140)
pP.draw(vP, clip=clP, hidden=False, wv=0.3, hatch_paths=hP)
s.rect(17, 30, 140, 140, 0.3)
s.text(17, 27, "THE PLATE — HORIZONTAL SECTION AT z %s     scale 1 : 1" % n(P.PLATE_T / 2, 1), 3.4, weight="bold")
s.line(pP.px(-P.PLATE_R - 4), pP.py(0), pP.px(P.PLATE_R + 4), pP.py(0), 0.12, dash="6 2 1 2")
s.line(pP.px(0), pP.py(-P.PLATE_R - 4), pP.px(0), pP.py(P.PLATE_R + 4), 0.12, dash="6 2 1 2")
for az, lab in ((0, "0° port slot"), (P.MOTOR_AZ, "%g° carriage" % P.MOTOR_AZ), (270, "270°"), (180, "180°")):
    a = math.radians(az)
    # the 0 and 180 labels go inside the rim: at r 65 they would run out of the frame
    r = 65.0 if abs(math.sin(a)) > 0.5 else 44.0
    dy = 2.5 if math.sin(a) < -0.5 else (1.0 if abs(math.sin(a)) > 0.5 else -1.8)
    s.text(pP.px(r * math.cos(a)), pP.py(r * math.sin(a)) + dy, lab, 2.3, anchor="middle")
for az in P.PLATE_SCREW_AZ:
    a = math.radians(az)
    pP.leader(P.PLATE_SCREW_R * math.cos(a), P.PLATE_SCREW_R * math.sin(a),
              pP.px(72 * math.cos(a)), pP.py(72 * math.sin(a)), "M3 %g°" % az,
              anchor="end" if math.cos(a) < 0 else "start", size=2.2)
s.text(17, 175, "Ø%s × %s laser-cut steel, about %s g. Countersinks are on the underside — this view is from above."
       % (n(2 * P.PLATE_R, 0), n(P.PLATE_T, 0), "385"), 2.2)
s.text(17, 178.5, "The plate is the mass, the ground plane and the halo's bottom edge. v8's Ø123 × 3 printed plate is gone.", 2.2)

# ---------------------------------------------------------------- THE FLOOR, 1:1
FZ = 8.0
FLOOR = ["base_plate", "internal_structure", "carriage", "servo_mount", "speaker_cradle", "speaker",
         "driver_board", "port_face", "usbc_board", "jack_board", "light_board", "commutation_board", "led_flex"]
FLOOR += [k for k in engine.parts() if k.startswith(("servo_", "motor_", "supercap", "standoff_",
                                                     "tmc6300_", "drv2605l_", "es9219q_", "jack_", "usbc_",
                                                     "veml7700_", "lra_", "plug_"))]
vF, hF = engine.plan_section(FLOOR, FZ)
pF = Port(s, 233, 100, 1.0)
clF = pF.clip("clipF", 163, 30, 140, 140)
pF.draw(vF, clip=clF, hidden=False, wv=0.25, hatch_paths=hF)
s.rect(163, 30, 140, 140, 0.3)
s.text(163, 27, "THE FLOOR — HORIZONTAL SECTION AT z %s     scale 1 : 1" % n(FZ, 1), 3.4, weight="bold")
s.line(pF.px(-P.PLATE_R - 4), pF.py(0), pF.px(P.PLATE_R + 4), pF.py(0), 0.12, dash="6 2 1 2")
s.line(pF.px(0), pF.py(-P.PLATE_R - 4), pF.px(0), pF.py(P.PLATE_R + 4), 0.12, dash="6 2 1 2")
pF.leader(0, P.MOTOR_R, 250, 40, "motor on its carriage, %g°" % P.MOTOR_AZ, size=2.2)
pF.leader(P.SPEAKER_CENTRE[0], P.SPEAKER_CENTRE[1], 250, 158, "speaker, cone up, on (%g, %g)" % P.SPEAKER_CENTRE, size=2.2)
_a = math.radians(engine.model.DRIVER_AZ)
pF.leader(engine.model.DRIVER_R * math.cos(_a), engine.model.DRIVER_R * math.sin(_a),
          182, 46, "driver board, %g°" % engine.model.DRIVER_AZ, anchor="start", size=2.2)
_a = math.radians(P.LRA_AZ)
pF.leader((P.R_WALL_IN - 1.2) * math.cos(_a), (P.R_WALL_IN - 1.2) * math.sin(_a),
          172, 62, "LRA, %g°" % P.LRA_AZ, anchor="start", size=2.2)
s.text(163, 175, "Perimeter ports Ø%s at z %s on a %g° grid: %d of the %d positions are drilled, %d fall in the "
       "motor cut-out." % (n(P.PORT_D, 1), n(P.PORT_Z, 1), 360.0 / P.PORT_N, PORTS_DRILLED,
                           P.PORT_N, PORTS_CUT), 2.2)
s.text(163, 178.5, "The speaker breathes into the cavity and out through them. Nothing fires down into the plate.", 2.2)

# ---------------------------------------------------------------- NOTES
s.text(313, 27, "NOTES", 3.4, weight="bold")
note_list(s, 309, 36, [
 (1, "Plate: Ø%s × %s steel, the heaviest part of the device and its ground plane. Its rim at r %s is the bottom "
     "edge of the halo." % (n(2 * P.PLATE_R, 0), n(P.PLATE_T, 0), n(P.PLATE_R, 1))),
 (2, "Two big cut-outs: the carriage stadium at %g° (Ø%s over r %s–%s, plus a tab slot inboard) and the port "
     "slot at 0° (%s wide, r %s to the rim)."
     % (P.MOTOR_AZ, n(HOLE_D, 1), n(HOLE_R0, 1), n(HOLE_R1, 1),
        n(P.PORT_W, 0), n(P.PORT_NOTCH_R0, 0))),
 (3, "Fixings, all countersunk or tapped from below: 3 × M3 at %s on r %s into inserts in the structure; 2 × M3 "
     "speaker cradle; 2 × M3 servo tray; 4 × M2 driver board; 2 × M2 port-face ears; 2 × M2 jack board; and one "
     "M3 ground bond beside the slot."
     % (" / ".join("%g°" % a for a in P.PLATE_SCREW_AZ), n(P.PLATE_SCREW_R, 0))),
 (4, "The port slot carries three things on two small boards: USB-C on a horizontal board at z %s; the 3.5 mm jack "
     "hanging UNDER a board at z %s, so its body sits at z −1 to 5, below the halo; and the light sensor on a "
     "small vertical board looking rearward through a Ø%s hole in the face. One board could not put both axes at "
     "z 2." % (n(engine.model.USBC_BOARD_Z0, 1), n(engine.model.JACK_BOARD_Z0, 1), n(P.SENSOR_HOLE_D))),
 (5, "The speaker stands cone-UP on its rear boss at (%g, %g), breathing into the cavity and out through the "
     "perimeter ports. v8's down-firing speaker had nowhere to fire once the plate went solid."
     % P.SPEAKER_CENTRE),
 (6, "Pad: Ø%s at the top tapering to Ø%s, %s thick, notched at the port slot. The carriage stands on the pad "
     "through the plate, so pad thickness is part of the drive geometry, not just a foot."
     % (n(2 * P.PAD_R, 0), n(2 * (P.PAD_R - 0.3), 1), n(P.PAD_T, 1))),
], w=88)

# ---------------------------------------------------------------- SECTION D-D, THE BACK
BACK = ["base_plate", "pad", "port_face", "usbc_board", "jack_board", "light_board", "internal_structure",
        "knob_body", "halo_diffuser", "led_flex"]
BACK += [k for k in engine.parts() if k.startswith(("jack_", "usbc_", "veml7700_", "es9219q_", "plug_"))]
vD, hD = engine.radial_section(BACK, 0.0, hidden=False)
pD = Port(s, 22, 247, 1.5, ox=0.0, oy=0.0)
clD = pD.clip("clipD", 17, 186, 175, 66)
pD.draw(vD, clip=clD, hidden=False, hatch_paths=hD, wv=0.28)
s.rect(17, 186, 175, 66, 0.3)
s.text(17, 183, "SECTION  D–D — THE BACK     1.5 : 1", 3.0, weight="bold")
s.line(pD.px(0), 186, pD.px(0), 252, 0.15, dash="6 2 1 2")
pD.dim_h(P.PORT_NOTCH_R0, P.PLATE_R, -1.5, "port slot, r %s to the rim" % n(P.PORT_NOTCH_R0, 0), off=-7)
pD.leader(P.PORT_FACE_R0, engine.model.USBC_BOARD_Z0 + 1.0, 140, 196, "USB-C, z %s" % n(engine.model.USBC_BOARD_Z0, 1), size=2.2)
pD.leader(P.PORT_FACE_R0, engine.model.JACK_Z, 140, 203, "3.5 mm jack, axis z %s" % n(engine.model.JACK_Z, 1), size=2.2)
pD.leader(P.PORT_FACE_R0, 2.5, 140, 210, "light sensor, Ø%s aperture" % n(P.SENSOR_HOLE_D), size=2.2)
pD.leader(P.R_DIFF_IN + 1.0, (P.HALO_Z0 + P.HALO_Z1) / 2, 140, 217, "halo passes outside the slot", size=2.2)
s.text(17, 256, "Section on the 0°–180° axis, right half. Nothing in the port slot reaches past r 51, and the halo "
       "sits at r %s–%s, so the light band runs over the back unbroken." % (n(P.R_DIFF_IN, 1), n(P.R_DIFF_OUT_TOP, 1)), 2.2)
s.text(17, 259.5, "The plug envelopes are ASSUMED: 12 × 6.5 × 12 for the right-angle cable outside, "
       "10 × 6.5 × 19 for the internal straight plug.", 2.2)

# ---------------------------------------------------------------- DETAIL S — the port face
dS = Port(s, 248, 222, 4.0, ox=49.5, oy=2.0)
clS = dS.clip("clipS", 198, 186, 100, 66)
dS.draw(vD, clip=clS, hidden=False, hatch_paths=hD, wv=0.26)
s.rect(198, 186, 100, 66, 0.3)
s.text(198, 183, "DETAIL S — THE PORT FACE     4 : 1", 3.0, weight="bold")
dS.dim_h(P.PORT_FACE_R0, P.PORT_FACE_R0 + P.PORT_FACE_T, -0.5, n(P.PORT_FACE_T), off=8, above=False)
s.text(198, 256, "Printed face %s thick at r %s, on two M2 ears." % (n(P.PORT_FACE_T), n(P.PORT_FACE_R0, 1)), 2.2)
s.text(198, 259.5, "Face positions: USB-C %g, sensor %g, jack %+g." % (P.PORT_USBC_T, P.PORT_LIGHT_T, P.PORT_JACK_T), 2.2)

save(s, "the60_v9_D04_plate_floor_ports")
