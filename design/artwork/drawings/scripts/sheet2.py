"""D02 — the light band, the display fixing and the encoder."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

ENC_AZ = P.ENC_AZ                                  # 330: the encoder axis, and section B-B
LED_AZ = 48.0                                      # a whole LED pitch, clear of the columns and the motor
LED_I = int(round(LED_AZ * P.LED_N / 360.0))
LED_R = engine.model.LED_R
FLEX_T = 0.2                                       # led_flex is z 5.0-5.2 in the model

def base_arc(od, limit):
    """Half-angle over which a motor base of diameter od, centred at r MOTOR_R,
    reaches past `limit`. Used for the note about breaking the LED ring."""
    rb, c = od / 2.0, P.MOTOR_R
    best = 0.0
    for i in range(1401):
        phi = i * 0.001
        disc = rb * rb - (c * math.sin(phi)) ** 2
        if disc < 0:
            break
        if c * math.cos(phi) + math.sqrt(disc) > limit:
            best = phi
    return math.degrees(best)

s = Sheet("LIGHT BAND, DISPLAY FIXING AND ENCODER", "60-09-D02", "AS SHOWN")
s.frame(META)

STACK = ["knob_body", "internal_structure", "base_plate", "pad", "halo_diffuser", "led_flex",
         "encoder_board", "display_case", "display_pcb"]
STACK += [k for k in engine.parts() if k.startswith("encoder_")]
vB, hB = engine.radial_section(STACK, ENC_AZ, hidden=False)

# ---------------------------------------------------------------- SECTION B-B
pB = Port(s, 22, 105, 1.75, ox=0.0, oy=0.0)
clB = pB.clip("clipB", 17, 30, 179, 106)
pB.draw(vB, clip=clB, hidden=False, hatch_paths=hB, wv=0.32)
s.rect(17, 30, 179, 106, 0.3)
s.text(17, 27, "SECTION  B–B     scale 1.75 : 1", 3.4, weight="bold")
s.text(17, 141, "Right half, on the %g°–%g° axis, through the encoder at %g°. The whole vertical stack, plate underside to knob top."
       % (ENC_AZ, ENC_AZ - 180, ENC_AZ), 2.2, col="#333")
s.line(pB.px(0), 30, pB.px(0), 136, 0.15, dash="6 2 1 2")
s.text(pB.px(0) + 1.5, 36.5, "CL", 2.2, col="#444")

# the v9 height stack, as a ladder of levels read straight from params.py
LEVELS = [(0.0, "plate underside, z 0"),
          (P.Z_PLATE_TOP, "plate top, halo bottom"),
          (P.HALO_Z1, "halo top"),
          (P.Z_LIP1, "diffuser lip top"),
          (P.Z_SKIRT_BOT, "knob skirt bottom"),
          (P.Z_CODE0, "code band bottom"),
          (P.Z_CODE1, "code band top"),
          (P.Z_PCB_BOT, "display board under"),
          (P.Z_SEAT0, "seat tabs"),
          (P.Z_DISC_BOT, "glass bottom"),
          (P.Z_DISC_TOP, "glass top"),
          (P.Z_KNOB_TOP, "knob top")]
# the labels are pushed apart where two levels are closer than the text is tall,
# with a kink in the leader, so the crowded 5.0-9.0 band stays readable
_lab_y, _prev = [], None
for z, lab in sorted(LEVELS, key=lambda t: -t[0]):
    y = pB.py(z)
    if _prev is not None and y < _prev + 3.1:
        y = _prev + 3.1
    _lab_y.append((z, lab, y)); _prev = y
for z, lab, y in _lab_y:
    s.line(pB.px(P.R_KNOB) + 2, pB.py(z), 131, pB.py(z), 0.12, dash="2 1.5", col="#666")
    s.line(131, pB.py(z), 135, y, 0.12, col="#666")
    s.text(137, y + 0.8, "z %s   %s" % (n(z, 1), lab), 2.0, col="#333")
_y0, _y1 = pB.py(P.Z_KNOB_TOP), pB.py(-P.PAD_T)
s.raw('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#000" stroke-width="0.25" fill="none" '
      'marker-start="url(#ar)" marker-end="url(#ar)"/>' % (192, _y0, 192, _y1))
s.text(190, (_y0 + _y1) / 2, "%s overall, pad to knob top" % n(P.HEIGHT, 1), 2.4, anchor="middle", rot=-90)
pB.dim_h(0, P.R_BORE, -3.5, "r %s bore" % n(P.R_BORE), off=7)
pB.dim_h(0, P.R_KNOB, -3.5, "r %s knob" % n(P.R_KNOB), off=13)
pB.dim_h(0, P.PLATE_R, -3.5, "r %s plate" % n(P.PLATE_R), off=19)

for i, (mx, my, by) in enumerate([
        (LED_R, (P.HALO_Z0 + P.HALO_Z1) / 2, 40),
        (P.R_DIFF_IN + 1.0, (P.HALO_Z0 + P.HALO_Z1) / 2, 56),
        (P.R_BORE - P.ENC_GAP / 2, (P.Z_CODE0 + P.Z_CODE1) / 2, 72),
        (P.DISC_MOUNT_PCD / 2, (P.Z_SEAT0 + P.Z_SEAT1) / 2, 88),
        (P.R_LIP_OUT - 0.5, (P.Z_LIP0 + P.Z_LIP1) / 2, 104)], 1):
    add_balloon(pB, mx, my, 181, by, i)

# ---------------------------------------------------------------- NOTES
s.text(205, 27, "NOTES", 3.4, weight="bold")
note_list(s, 201, 36, [
 (1, "%d SK6812SIDE-A at r %s on a %s flex ring on the plate top (z %s–%s); packages z %s–%s, lit band z %s–%s. "
     "v8 stood the ring on the wall, where a side-view LED fires up or down."
     % (P.LED_N, n(LED_R), n(FLEX_T, 1), n(P.Z_PLATE_TOP, 1), n(P.Z_PLATE_TOP + FLEX_T, 1),
        n(P.Z_PLATE_TOP + FLEX_T, 1), n(P.Z_PLATE_TOP + FLEX_T + P.LED_T, 1), n(P.HALO_Z0, 1), n(P.HALO_Z1, 1))),
 (2, "Diffuser r %s inside, %s–%s outside (bottom to top, flush with the knob at r %s), %s–%s thick. Retained by "
     "a lip at r %s, z %s–%s, with a %s shadow gap under the knob skirt."
     % (n(P.R_DIFF_IN, 1), n(P.R_DIFF_OUT_BOT, 1), n(P.R_DIFF_OUT_TOP, 1), n(P.R_KNOB, 1),
        n(P.R_DIFF_OUT_BOT - P.R_DIFF_IN, 1), n(P.R_DIFF_OUT_TOP - P.R_DIFF_IN, 1),
        n(P.R_LIP_OUT, 1), n(P.Z_LIP0, 1), n(P.Z_LIP1, 1), n(P.Z_SKIRT_BOT - P.Z_LIP1, 1))),
 (3, "Continuous through 360°, motor at %g° included, only while the stator base is Ø%s or less: base centred at "
     "r %s, flex inner edge r %s. params ASSUMES Ø%g — measure it. At Ø%g the base cuts the ring over ±%.1f°; the "
     "bell relief (Ø%g) would cut it over ±%.1f°."
     % (P.MOTOR_AZ, n(2 * (engine.model.R_LED_FLEX_IN - P.MOTOR_R), 1), n(P.MOTOR_R, 1),
        n(engine.model.R_LED_FLEX_IN, 1), P.MOTOR_BASE_OD, P.MOTOR_OD,
        base_arc(P.MOTOR_OD, engine.model.R_LED_FLEX_IN), P.MOTOR_OD + 2 * P.MOTOR_CLEAR,
        base_arc(P.MOTOR_OD + 2 * P.MOTOR_CLEAR, engine.model.R_LED_FLEX_IN))),
 (4, "AEDR-8300 at %g°, package face at r %s, nominal %s gap to the code band. The band is the bore recessed "
     "%s to r %s over z %s–%s. It is %s tall because the package measures 3.96 across the strip."
     % (ENC_AZ, n(P.R_BORE - P.ENC_GAP - 1.63), n(P.ENC_GAP), n(P.STRIP_T), n(P.R_BORE + P.STRIP_T),
        n(P.Z_CODE0, 1), n(P.Z_CODE1, 1), n(P.Z_CODE1 - P.Z_CODE0, 1))),
 (5, "Display fixing: four columns at %s carrying %s seat tabs that reach the M4 holes at %s on a Ø%s PCD, in the "
     "%s gap above the board. Columns sit 3° off the holes because two of the four are 0.5 from the board edge. "
     "M4 × 4 driven before the plate goes on."
     % (" / ".join("%g°" % a for a in P.COLUMN_AZ), n(P.SEAT_T), " / ".join("%g°" % a for a in P.DISC_MOUNT_AZ_DEV),
        n(P.DISC_MOUNT_PCD), n(P.Z_DISC_BOT - P.Z_PCB_TOP, 1))),
 (6, "The ambient-light sensor is NOT in this wall. v9 moved it into the port face at the back, looking rearward "
     "through a Ø%s hole below the halo — see D04." % n(P.SENSOR_HOLE_D)),
 (7, "OPEN — settle this before the flex is ordered. As modelled the package faces INWARD, at the wall, with its "
     "terminals outward: at 0° it spans r %s–%s. The intent is the opposite; either the placement rotation in "
     "model.py or this note is wrong." % (n(LED_R - 0.8, 1), n(LED_R + 0.8, 1))),
], w=88)

# ---------------------------------------------------------------- DETAIL P — the halo
HALO = ["base_plate", "internal_structure", "halo_diffuser", "led_flex", "knob_body", "led_%02d" % LED_I]
vP_, hP_ = engine.radial_section(HALO, LED_AZ, hidden=False)
dP = Port(s, 350, 68, 8.0, ox=59.0, oy=7.0)
clP = dP.clip("clipP", 300, 30, 100, 80)
dP.draw(vP_, clip=clP, hidden=False, hatch_paths=hP_, wv=0.28)
s.rect(300, 30, 100, 80, 0.3)
s.text(300, 27, "DETAIL P — HALO     8 : 1", 3.0, weight="bold")
dP.dim_v(P.HALO_Z0, P.HALO_Z1, P.R_DIFF_OUT_TOP, n(P.HALO_Z1 - P.HALO_Z0), off=4)
dP.dim_h(P.R_DIFF_IN, P.R_DIFF_OUT_BOT, P.HALO_Z0 - 1.0, n(P.R_DIFF_OUT_BOT - P.R_DIFF_IN), off=6, above=False)
dP.leader(LED_R, P.Z_PLATE_TOP + 1.2, 306, 45, "LED at r %s" % n(LED_R), size=2.2)
s.text(300, 116, "The section is on the %g° LED pitch. The flex ring is r %s–%s and %s thick on the plate"
       % (LED_AZ, n(engine.model.R_LED_FLEX_IN, 1), n(engine.model.R_LED_FLEX_OUT, 1), n(FLEX_T, 1)), 2.2)
s.text(300, 120, "top; the package stands %s tall on it. Which way it faces is note 7, still open." % n(P.LED_T, 1), 2.2)
s.text(300, 124, "Bench test the diffuser before committing: see docs HALO-BENCH-TEST.", 2.2)

# ---------------------------------------------------------------- PLAN THROUGH THE HALO
HZ = (P.HALO_Z0 + P.HALO_Z1) / 2
PL = ["base_plate", "internal_structure", "halo_diffuser", "led_flex", "knob_body", "carriage"]
PL += [k for k in engine.parts() if k.startswith("led_") or k.startswith("motor_")]
vH, hH = engine.plan_section(PL, HZ)
pH = Port(s, 82, 206, 0.78)
clH = pH.clip("clipH", 17, 150, 130, 112)
pH.draw(vH, clip=clH, hidden=False, wv=0.25, hatch_paths=hH)
s.rect(17, 150, 130, 112, 0.3)
s.text(17, 147, "PLAN — HORIZONTAL SECTION AT z %s     scale %.2f : 1" % (n(HZ, 1), pH.k), 3.0, weight="bold")
s.line(pH.px(-P.R_KNOB), pH.py(0), pH.px(P.R_KNOB), pH.py(0), 0.12, dash="6 2 1 2")
s.line(pH.px(0), pH.py(-P.R_KNOB), pH.px(0), pH.py(P.R_KNOB), 0.12, dash="6 2 1 2")
for az, lab in ((0, "0° USB-C"), (P.MOTOR_AZ, "%g° motor" % P.MOTOR_AZ), (ENC_AZ, "%g° encoder" % ENC_AZ)):
    a = math.radians(az)
    s.text(pH.px(68.5 * math.cos(a)), pH.py(68.5 * math.sin(a)) + (2.5 if math.sin(a) < -0.5 else 1.0),
           lab, 2.4, anchor="middle")
s.text(17, 266, "%d LEDs on a %s° pitch at r %s, unbroken all the way round. The port slot at 0° passes UNDER the "
       "halo, through the plate." % (P.LED_N, n(360.0 / P.LED_N, 1), n(LED_R)), 2.2)
s.text(17, 269.5, "The only interruption to the ring's outer wall is the motor relief at %g°, and the ring itself "
       "runs on behind it." % P.MOTOR_AZ, 2.2)

# ---------------------------------------------------------------- DETAIL Q — encoder and code band
dQ = Port(s, 200, 190, 8.0, ox=56.0, oy=(P.Z_CODE0 + P.Z_CODE1) / 2)
clQ = dQ.clip("clipQ", 153, 150, 94, 80)
dQ.draw(vB, clip=clQ, hidden=False, hatch_paths=hB, wv=0.28)
s.rect(153, 150, 94, 80, 0.3)
s.text(153, 147, "DETAIL Q — ENCODER AND CODE BAND     8 : 1", 3.0, weight="bold")
dQ.dim_v(P.Z_CODE0, P.Z_CODE1, P.R_BORE + P.STRIP_T, n(P.Z_CODE1 - P.Z_CODE0), off=7)
dQ.dim_h(P.R_BORE - P.ENC_GAP - 1.63, P.R_BORE, P.Z_CODE0 - 0.8, n(P.ENC_GAP + 1.63), off=6, above=False)
s.text(153, 236, "Package face to bore: %s, of which %s is the AEDR-8300's" % (n(P.ENC_GAP + 1.63), n(P.ENC_GAP)), 2.2)
s.text(153, 240, "nominal working gap. The strip is a %s recess in the bore, so a" % n(P.STRIP_T), 2.2)
s.text(153, 244, "printed knob and a stuck-on strip finish flush at r %s." % n(P.R_BORE), 2.2)

# ---------------------------------------------------------------- PLAN THROUGH THE SEAT TABS
SZ = (P.Z_SEAT0 + P.Z_SEAT1) / 2
vS, hS = engine.plan_section(["internal_structure", "knob_body", "display_pcb"], SZ)
pS = Port(s, 302, 196, 0.78)
clS = pS.clip("clipS", 253, 150, 142, 92)
pS.draw(vS, clip=clS, hidden=False, wv=0.25, hatch_paths=hS)
s.rect(253, 150, 142, 92, 0.3)
s.text(253, 147, "PLAN — HORIZONTAL SECTION AT z %s, THROUGH THE SEAT TABS     scale %.2f : 1" % (n(SZ, 1), pS.k),
       3.0, weight="bold")
for az in P.DISC_MOUNT_AZ_DEV:
    a = math.radians(az); r = P.DISC_MOUNT_PCD / 2
    s.raw('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="#000" stroke-width="0.2"/>'
          % (pS.px(r * math.cos(a)), pS.py(r * math.sin(a)), 4.3 / 2 * pS.k))
    s.text(pS.px(68 * math.cos(a)), pS.py(68 * math.sin(a)) + 1.0, "M4 %g°" % az, 2.2, anchor="middle")
for az in P.COLUMN_AZ:
    a = math.radians(az)
    s.text(pS.px(43 * math.cos(a)), pS.py(43 * math.sin(a)) + 1.0, "%g°" % az, 2.2, anchor="middle", col="#555")
bb = engine.bbox(["display_pcb"])
s.raw('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#000" stroke-width="0.25" '
      'stroke-dasharray="2.5 1.5"/>'
      % (pS.px(bb.min.X), pS.py(bb.max.Y), (bb.max.X - bb.min.X) * pS.k, (bb.max.Y - bb.min.Y) * pS.k))
s.text(253, 246, "Columns (grey azimuths) sit 3° off the M4 holes; the tabs bridge across. Dashed rectangle: the board, below this cut.", 2.2)
s.text(253, 249.5, "The tabs stand %s above the board and touch the glass back — they set the display's height, not the columns."
       % n(P.Z_SEAT0 - P.Z_PCB_TOP), 2.2)

save(s, "the60_v9_D02_light_display_encoder")
