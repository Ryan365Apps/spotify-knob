"""D03 - the drive and the clutch: sliding carriage, MY-3514C, band, servo (v15)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

AZ = P.MOTOR_AZ                                     # 90: the motor axis, and section C-C
RATIO = (2 * P.R_BORE) / P.MOTOR_OD
BAND_OUT = P.MOTOR_R + P.MOTOR_OD / 2 + P.MOTOR_BAND_T
# model.carriage_hole() is built from MOTOR_R and CLUTCH_LIFT, not from
# params.CARRIAGE_HOLE_R0/R1 (which nothing in model.py reads), so the numbers
# on the sheet are taken from the shape that is actually cut.
HOLE_D = P.MOTOR_OD + 2 * 1.0 + 1.5
HOLE_R1 = P.MOTOR_R + HOLE_D / 2
HOLE_R0 = P.MOTOR_R - P.CLUTCH_LIFT - HOLE_D / 2
TAB_R0 = P.MOTOR_R - P.MOTOR_OD / 2 - 3.5 - 5.0


s = Sheet("DRIVE AND CLUTCH - CARRIAGE, MOTOR, BAND, SERVO", "60-15-D03", "AS SHOWN")
s.frame(META)

DRIVE = ["knob_body", "internal_structure", "base_plate", "rim_ring_STEEL", "closing_plate_AL", "pad",
         "halo_diffuser", "led_strip_ENVELOPE", "carriage", "commutation_board", "servo_mount", "mt6701",
         "collar_2", "bush_2"]
DRIVE += [k for k in engine.parts() if k.startswith(("motor_", "servo"))]

vC, hC = engine.radial_section(DRIVE, AZ, hidden=False, missing_ok=True)

# ---------------------------------------------------------------- SECTION C-C
pC = Port(s, 40.0, 108, 1.35, ox=0.0, oy=0.0)
clC = pC.clip("clipC", 17, 30, 179, 106)
pC.draw(vC, clip=clC, hidden=False, hatch_paths=hC, wv=0.30)
s.rect(17, 30, 179, 106, 0.3)
s.text(17, 27, "SECTION  C-C     scale 1.35 : 1", 3.4, weight="bold")
s.text(17, 141, "On the %g deg - %g deg axis, clutch ENGAGED. Right of the centreline is the motor at %g deg; the servo's inboard "
       "end crosses the centreline." % (AZ, AZ + 180, AZ), 2.2, col="#333")
s.line(pC.px(0), 32, pC.px(0), 134, 0.15, dash="6 2 1 2")
s.text(pC.px(0) + 1.5, 38.5, "CL", 2.2, col="#444")

pC.dim_h(0, P.MOTOR_R, -3.0, "r %s motor axis" % n(P.MOTOR_R), off=5)
pC.dim_h(0, P.R_BORE, -3.0, "r %s bore" % n(P.R_BORE), off=10)
pC.dim_v(P.Z_MOTOR_BOT, P.Z_MOTOR_TOP, P.R_BORE, "%s motor" % n(P.MOTOR_H), off=5)
pC.dim_v(0.0, P.CARRIAGE_T, P.R_BORE, "%s carriage" % n(P.CARRIAGE_T), off=13)
pC.dim_v(P.Z_DRIVE0, P.Z_DRIVE1, P.R_BORE, "%s band" % n(P.Z_DRIVE1 - P.Z_DRIVE0), off=21)

# balloons run along the empty band under the pad rather than in a right-hand
# column, which on this sheet is taken by the height dimensions
for i, (mx, my, bx) in enumerate([
        (BAND_OUT - 0.3, (P.Z_DRIVE0 + P.Z_DRIVE1) / 2, 36),
        (P.MOTOR_R, (P.Z_MOTOR_BOT + P.Z_MOTOR_TOP) / 2, 64),
        (P.MOTOR_R - P.MOTOR_OD / 2 - 3.0, 9.5, 92),
        (P.MOTOR_R, 0.8, 120),
        (P.MOTOR_R, P.CARRIAGE_T - 1.0, 148)], 1):
    add_balloon(pC, mx, my, bx, 131.5, i)

# ---------------------------------------------------------------- NOTES
s.text(210, 27, "NOTES", 3.4, weight="bold")
note_list(s, 206, 36, [
 (1, "The drive is friction, not gears: a Ø%s motor bell running on the Ø%s bore through a %s flat silicone band. "
     "Ratio %.2f : 1. The gimbal drive and its over-centre clutch went at v9 and have not come back."
     % (n(P.MOTOR_OD, 0), n(2 * P.R_BORE, 0), n(P.MOTOR_BAND_T), RATIO)),
 (2, "JD-Power MY-3514C (2804), dia %s x %s, on a carriage that slides radially in a stadium hole through the "
     "aluminium core. "
     "The carriage shoe is dia %s on the pad, so the motor's base face is at z %s and its top at z %s."
     % (n(P.MOTOR_OD, 0), n(P.MOTOR_H, 0), n(P.MOTOR_OD + 2.0, 0), n(P.Z_MOTOR_BOT, 1), n(P.Z_MOTOR_TOP, 1))),
 (3, "The clutch IS the servo. An AGFRC C1.5CLS PRO linear servo (%g × %g × %g envelope) pushes the carriage tab "
     "directly; %s of travel takes the bell from contact to %s clear. Preload — %s N nominal — is a servo "
     "position set in software, not a spring."
     % (P.SERVO_L, P.SERVO_W, P.SERVO_H, n(P.CLUTCH_LIFT), n(P.CLUTCH_LIFT), n(P.MOTOR_PRELOAD_N, 1))),
 (4, "Commutation: an MT6701 on a %g x %g board inside the carriage, under the motor, reading a Ø6 × 2.5 diametric "
     "magnet in the shaft's lower end through a dia %s sight hole. Which end of the shaft carries the magnet is "
     "ASSUMED. If it is the top, this board moves and the display rises about 3 mm, against %s as modelled." % (12, 12, n(9.0, 0), n(P.HEIGHT, 1))),
 (5, "Not drawn, because nothing published says: the motor's bolt pattern (the carriage has a Ø%s locating rim "
     "only), the servo's mounting lugs, and the pushrod-to-tab joint. Measure all three on the real parts before "
     "printing the carriage or the servo mount." % n(P.MOTOR_OD + 0.6, 1)),
 (6, "Band grip at %s N is untested. If it slips under a firm hand, the fallback is a 2 : 1 bell-crank between the "
     "servo and the tab — that doubles the force and halves the travel, so the stadium hole would grow."
     % n(P.MOTOR_PRELOAD_N, 1)),
], w=84)

# ---------------------------------------------------------------- DETAIL R — the clutch, both states
CONTACT = ["knob_body", "internal_structure", "carriage"] + [k for k in engine.parts() if k.startswith("motor_")]
for i, (eng, lab, x0) in enumerate([(True, "ENGAGED", 300), (False, "RELEASED", 351)]):
    v, h = engine.radial_section(CONTACT, AZ, engaged=eng, hidden=False, missing_ok=True)
    d = Port(s, x0 + 24, 74, 4.0, ox=P.R_BORE - 2.5, oy=(P.Z_DRIVE0 + P.Z_DRIVE1) / 2)
    cl = d.clip("clipR%d" % i, x0, 30, 48, 80)
    d.draw(v, clip=cl, hidden=False, hatch_paths=h, wv=0.26)
    s.rect(x0, 30, 48, 80, 0.3)
    s.text(x0, 27, lab, 2.8, weight="bold")
    if eng:
        d.dim_h(P.R_BORE, BAND_OUT, P.Z_DRIVE0 + 1.0, "%s band" % n(P.MOTOR_BAND_T), off=-14)
    else:
        d.dim_h(P.MOTOR_R - P.CLUTCH_LIFT + P.MOTOR_OD / 2, P.R_BORE, P.Z_DRIVE0 + 1.0, n(P.CLUTCH_LIFT), off=-14)
s.text(300, 22, "DETAIL R - THE CLUTCH     4 : 1", 3.0, weight="bold")
s.text(300, 116, "Same section, same scale, %s apart. Engaged, the band is squeezed %s between" % (n(P.CLUTCH_LIFT), n(P.MOTOR_BAND_T)), 2.2)
s.text(300, 120, "bell and bore. Released, the bell stands %s clear and the knob free-spins." % n(P.CLUTCH_LIFT), 2.2)
s.text(300, 124, "The knob is never released by the wheels — only by the drive.", 2.2)

# ---------------------------------------------------------------- PLAN THROUGH THE PLATE
Z1 = 2.5
PL1 = ["base_plate", "closing_plate_AL", "rim_ring_STEEL", "carriage", "commutation_board", "mt6701",
       "port_face", "usbc_board", "light_board"]
v1, h1 = engine.plan_section(PL1, Z1, missing_ok=True)
p1 = Port(s, 77, 206, 0.55)
cl1 = p1.clip("clip1", 17, 150, 120, 112)
p1.draw(v1, clip=cl1, hidden=False, wv=0.25, hatch_paths=h1)
s.rect(17, 150, 120, 112, 0.3)
s.text(17, 147, "PLAN AT z %s - INSIDE THE CORE     scale %.2f : 1" % (n(Z1, 1), p1.k), 3.0, weight="bold")
s.line(p1.px(-P.R_KNOB), p1.py(0), p1.px(P.R_KNOB), p1.py(0), 0.12, dash="6 2 1 2")
s.line(p1.px(0), p1.py(-P.R_KNOB), p1.px(0), p1.py(P.R_KNOB), 0.12, dash="6 2 1 2")
p1.leader(0, P.MOTOR_R, 104, 168, "carriage shoe on the pad", size=2.2)
p1.leader(-14.0, 9.7, 104, 200, "servo tray screws", size=2.2)
p1.leader(P.PORT_FACE_R0, 0.0, 104, 214, "port face", size=2.2)
s.text(17, 266, "The stadium hole is the two carriage positions plus the slot", 2.2)
s.text(17, 269.5, "between them: dia %s wide, r %s - %s at %g deg, with a 10 x 10 tab slot reaching in to r %s."
       % (n(HOLE_D, 1), n(HOLE_R0, 1), n(HOLE_R1, 1), P.MOTOR_AZ, n(TAB_R0, 1)), 2.2)
s.text(17, 273, "The carriage rides on the pad, not on the core. This cut is inside the cooling duct - see D05.", 2.2)

# ---------------------------------------------------------------- PLAN AT THE DRIVE BAND
Z2 = (P.Z_DRIVE0 + P.Z_DRIVE1) / 2
PL2 = ["knob_body", "internal_structure", "carriage", "servo_mount", "motion_board", "speaker_cradle", "speaker",
       "halo_diffuser", "led_strip_ENVELOPE"]
PL2 += [k for k in engine.parts() if k.startswith(("motor_", "servo"))]
v2, h2 = engine.plan_section(PL2, Z2, missing_ok=True)
p2 = Port(s, 199, 206, 0.55)
cl2 = p2.clip("clip2", 141, 150, 116, 112)
p2.draw(v2, clip=cl2, hidden=False, wv=0.25, hatch_paths=h2)
s.rect(141, 150, 116, 112, 0.3)
s.text(141, 147, "PLAN AT z %s - THE DRIVE BAND     scale %.2f : 1" % (n(Z2, 1), p2.k), 3.0, weight="bold")
s.line(p2.px(-P.R_KNOB), p2.py(0), p2.px(P.R_KNOB), p2.py(0), 0.12, dash="6 2 1 2")
s.line(p2.px(0), p2.py(-P.R_KNOB), p2.px(0), p2.py(P.R_KNOB), 0.12, dash="6 2 1 2")
s.text(141, 266, "Contact is a line at %g deg, at r %s. Everything else on this level -" % (P.MOTOR_AZ, n(P.R_BORE)), 2.2)
s.text(141, 269.5, "motion board at %g deg, speaker, servo tray - stays outside the bell." % P.MOTION_AZ, 2.2)
s.text(141, 273, "The wall relief is cut for the bell, %s a side; the base below z %s is narrower."
       % (n(P.MOTOR_CLEAR, 1), n(P.Z_BELL_BOT, 1)), 2.2)

# ---------------------------------------------------------------- ISOMETRIC
# the two printed parts on their own: with the motor envelope on top the carriage
# is completely hidden, and the motor is not what anyone has to make
ISO = ["carriage", "servo_mount", "commutation_board"]
vI = engine.iso(ISO, direction=(0.9, -1.0, 0.7), hidden=True, missing_ok=True)
cx, cy = box_centre(vI)
pI = Port(s, 330, 196, 1.9, ox=cx, oy=cy)
clI = pI.clip("clipI", 263, 150, 132, 92)
pI.draw(vI, clip=clI, hidden=True, wv=0.28, wh=0.13)
s.rect(263, 150, 132, 92, 0.3)
s.text(263, 147, "CARRIAGE AND SERVO TRAY - ISOMETRIC     1.9 : 1", 3.0, weight="bold")
s.text(263, 246, "The two printed parts of the drive, with the commutation board in its pocket. Motor and servo are "
       "left off: their envelopes hide everything that has to be made.", 2.2)
s.text(263, 249.5, "Assembly: board into the carriage, motor on top, band over the bell, servo into the tray, tray on "
       "the plate, then set the preload in software.", 2.2)

save(s, "the60_v15_D03_drive_clutch")
