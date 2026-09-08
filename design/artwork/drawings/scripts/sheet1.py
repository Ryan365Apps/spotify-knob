"""D01 - knob support: wheels, collars, eccentric bushes (v15)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

AZ = P.WHEEL_AZ[0]                       # 30 deg: the wheel this sheet sections through
SEC = ["knob_body", "internal_structure", "base_plate", "rim_ring_STEEL", "closing_plate_AL",
       "pad", "halo_diffuser", "collar_0", "bush_0", "bearing_%d" % AZ,
       "panel_glass", "lens_ASSUMED", "panel_components_ENVELOPE"]

s = Sheet("KNOB SUPPORT - WHEELS, COLLARS AND ECCENTRIC BUSHES", "60-15-D01", "AS SHOWN")
s.frame(META)

vA, hA = engine.radial_section(SEC, AZ, hidden=False)

# ---------------------------------------------------------------- SECTION A-A
pA = Port(s, 22, 108, 1.75, ox=0.0, oy=0.0)
clA = pA.clip("clipA", 17, 30, 179, 106)
pA.draw(vA, clip=clA, hidden=False, hatch_paths=hA, wv=0.32)
s.rect(17, 30, 179, 106, 0.3)
s.text(17, 27, "SECTION  A-A     scale 1.75 : 1", 3.4, weight="bold")
s.text(17, 141, "Right half, on the %d deg - %d deg axis, through the wheel at %d deg. Hatching is cut material; plain lines are behind the cut."
       % (AZ, AZ + 180, AZ), 2.2, col="#333")
s.line(pA.px(0), 32, pA.px(0), 134, 0.15, dash="6 2 1 2")
s.text(pA.px(0) + 1.5, 38.5, "CL", 2.2, col="#444")

pA.dim_v(P.Z_GROOVE0, P.Z_GROOVE1, P.R_KNOB, n(P.Z_GROOVE1 - P.Z_GROOVE0), off=4)
pA.dim_v(P.Z_SEAT_BOT, P.Z_SEAT_TOP, P.R_KNOB, n(P.Z_SEAT_TOP - P.Z_SEAT_BOT), off=9)
pA.dim_v(0.0, P.PLATE_T, P.R_KNOB, n(P.PLATE_T), off=14)
pA.dim_v(P.Z_SKIRT_BOT, P.Z_KNOB_TOP, P.R_KNOB, n(P.Z_KNOB_TOP - P.Z_SKIRT_BOT), off=19)
pA.dim_h(0, P.WHEEL_AXIS_R, -1.0, "r %s wheel axis" % n(P.WHEEL_AXIS_R), off=5)
pA.dim_h(0, P.R_BORE, -1.0, "r %s bore" % n(P.R_BORE), off=11)
pA.dim_h(0, P.R_KNOB, -1.0, "r %s knob" % n(P.R_KNOB), off=17)

for i, (mx, my, by) in enumerate([
        (P.R_GROOVE_ROOT, P.Z_RIDGE_MID, 36),
        (P.WHEEL_AXIS_R, P.Z_RIDGE_MID, 52),
        (P.BUSH_R + 2.4, P.Z_POST_TOP + 0.3, 68),
        (P.BUSH_R + 3.6, (P.Z_SEAT_BOT + P.Z_POST_TOP) / 2, 84),
        (P.CODE_R1, P.Z_CODE_FACE, 100)], 1):
    add_balloon(pA, mx, my, 190, by, i)

# ---------------------------------------------------------------- NOTES
s.text(210, 27, "NOTES", 3.4, weight="bold")
note_list(s, 206, 36, [
 (1, "V-groove in the bore: root r %s, 90 deg included, %s deep, %s flat at the root so contact is on the flanks "
     "only. z %s - %s. The bore is dia %s and smooth elsewhere: v15 moved the code ring off the bore into the "
     "crown's underside, so nothing else breaks the turned surface."
     % (n(P.R_GROOVE_ROOT), n(P.WHEEL_V_H), n(P.WHEEL_V_FLAT), n(P.Z_GROOVE0, 1), n(P.Z_GROOVE1, 1),
        n(2 * P.R_BORE, 0))),
 (2, "623ZZ bearing %g x %g x %g pressed into a turned dia %s V-collar. Axis r %s, z %s - %s. Three off, at %s."
     % (P.WHEEL_BORE, 10, P.WHEEL_W, n(P.WHEEL_OD), n(P.WHEEL_AXIS_R), n(P.Z_WHEEL0, 1), n(P.Z_WHEEL1, 1),
        " / ".join("%g deg" % a for a in P.WHEEL_AZ))),
 (3, "Eccentric bush: a dia %s shank in the post carrying a dia %s wheel pin offset %s from it, under a dia %s "
     "flange %s thick, with a %g mm hex socket underneath. Pin inward, the wheel sits at r %s - %s clear inside "
     "the bore - and the knob drops on; half a turn from below seats it and sets the preload."
     % (n(P.BUSH_D), n(P.WHEEL_BORE - 0.04), n(P.WHEEL_ECC), n(P.BUSH_FLANGE_D), n(P.BUSH_FLANGE_T), P.BUSH_HEX,
        n(P.BUSH_R - P.WHEEL_ECC), n(P.R_BORE - (P.BUSH_R - P.WHEEL_ECC) - P.WHEEL_OD / 2))),
 (4, "v15 inverted the structure. There is no ledge: the seat flange (z %s - %s) is the datum face, and the wheel "
     "posts hang below it, dia %s with a dia %s bush bore, top face z %s. The flange's top face is the display's "
     "seat and prints flat on the bed. Plate screws from below at %s."
     % (n(P.Z_SEAT_BOT, 1), n(P.Z_SEAT_TOP, 1), n(P.WHEEL_POST_D), n(P.BUSH_D + 0.1), n(P.Z_POST_TOP, 1),
        " / ".join("%g deg" % a for a in P.PLATE_SCREW_AZ))),
 (5, "The wheels carry the knob's weight and its lift-off load. Nothing else supports it: the drive band is a "
     "friction contact on the same bore, and the halo, the code ring and the display all clear the knob."),
], w=84)
s.text(206, 132, "V-on-V locates the knob radially and axially at once and takes the lift-off", 2.3)
s.text(206, 136, "load, so the knob cannot be pulled off the device.", 2.3)
s.text(206, 143, "Knob %s tall: %.0f %% of the %s body height, %.0f %% of the %s including the pad."
       % (n(P.Z_KNOB_TOP - P.Z_SKIRT_BOT, 1), P.KNOB_FRACTION * 100, n(P.Z_KNOB_TOP, 1),
          100 * (P.Z_KNOB_TOP - P.Z_SKIRT_BOT) / P.HEIGHT, n(P.HEIGHT, 1)), 2.3, col="#333")

# ---------------------------------------------------------------- DETAIL X
WHEEL = ["collar_0", "bush_0", "bearing_%d" % AZ]
vX, hX = engine.radial_section(["knob_body"] + WHEEL, AZ, hidden=False)
dX = Port(s, 350, 68, 8.0, ox=P.R_BORE - 1.5, oy=P.Z_RIDGE_MID)
clX = dX.clip("clipX", 300, 30, 100, 80)
dX.draw(vX, clip=clX, hidden=False, hatch_paths=hX, wv=0.28)
s.rect(300, 30, 100, 80, 0.3)
s.text(300, 27, "DETAIL X - GROOVE AND COLLAR     8 : 1", 3.0, weight="bold")
dX.dim_h(P.R_BORE, P.R_GROOVE_ROOT, P.Z_RIDGE_MID - 2.4, n(P.WHEEL_V_H), off=0)
dX.dim_v(P.Z_RIDGE_MID - P.WHEEL_V_FLAT / 2, P.Z_RIDGE_MID + P.WHEEL_V_FLAT / 2, P.R_GROOVE_ROOT,
         n(P.WHEEL_V_FLAT), off=7)
s.text(300, 116, "Notchiness three times a turn means the collars are bottoming on the", 2.2)
s.text(300, 120, "%s root flat. Bore-to-groove concentricity within 0.05 total: runout" % n(P.WHEEL_V_FLAT), 2.2)
s.text(300, 124, "modulates the wheel preload, and the wheels are what hold the knob.", 2.2)

# ---------------------------------------------------------------- PLAN THROUGH THE WHEELS
PLAN_Z = (P.Z_WHEEL0 + P.Z_WHEEL1) / 2
PLAN = ["internal_structure", "knob_body", "collar_0", "collar_1", "collar_2",
        "bush_0", "bush_1", "bush_2", "encoder_board"]
vP, hP = engine.plan_section(PLAN, PLAN_Z)
pP = Port(s, 82, 206, 0.56)
clP = pP.clip("clipP", 17, 150, 130, 112)
pP.draw(vP, clip=clP, hidden=False, wv=0.28, hatch_paths=hP)
s.rect(17, 150, 130, 112, 0.3)
s.text(17, 147, "PLAN - HORIZONTAL SECTION AT z %.1f     scale %.2f : 1" % (PLAN_Z, pP.k), 3.0, weight="bold")

bb = engine.bbox(["panel_glass"])         # the panel is above the cut: real outline, from the model
s.raw('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#000" stroke-width="0.25" '
      'stroke-dasharray="2.5 1.5"/>'
      % (pP.px(bb.min.X), pP.py(bb.max.Y), (bb.max.X - bb.min.X) * pP.k, (bb.max.Y - bb.min.Y) * pP.k))

def edge_r(az):
    """radius of the panel's edge along an azimuth, from the model's own bounding box"""
    a = math.radians(az); c, si = math.cos(a), math.sin(a); ts = []
    for xv in (bb.min.X, bb.max.X):
        if abs(c) > 1e-9:
            t = xv / c
            if t > 0 and bb.min.Y - 1e-6 <= t * si <= bb.max.Y + 1e-6: ts.append(t)
    for yv in (bb.min.Y, bb.max.Y):
        if abs(si) > 1e-9:
            t = yv / si
            if t > 0 and bb.min.X - 1e-6 <= t * c <= bb.max.X + 1e-6: ts.append(t)
    return min(ts) if ts else 0.0

for az in P.WHEEL_AZ:
    a = math.radians(az)
    s.line(pP.px(0), pP.py(0), pP.px(P.R_BORE * math.cos(a)), pP.py(P.R_BORE * math.sin(a)), 0.15, dash="4 1.5")
    s.text(pP.px(92 * math.cos(a)), pP.py(92 * math.sin(a)) + (2.5 if math.sin(a) < -0.5 else 1.0),
           "%g deg" % az, 2.6, anchor="middle")
s.line(pP.px(-P.R_KNOB), pP.py(0), pP.px(P.R_KNOB), pP.py(0), 0.12, dash="6 2 1 2")
s.line(pP.px(0), pP.py(-P.R_KNOB), pP.px(0), pP.py(P.R_KNOB), 0.12, dash="6 2 1 2")
s.text(pP.px(P.R_KNOB) + 1.0, pP.py(0) + 0.8, "0 deg USB-C", 2.3)

post_in = P.BUSH_R - P.WHEEL_POST_D / 2
s.text(17, 266, "Dashed rectangle: the display panel, %s x %s, centre %s in -x - its real outline from the model, above this cut."
       % (n(bb.max.X - bb.min.X, 1), n(bb.max.Y - bb.min.Y, 1), n(abs((bb.min.X + bb.max.X) / 2), 1)), 2.2)
s.text(17, 269.5, "v15 clears the panel by height, not by azimuth: the panel sits on the seat flange at z %s, above the posts, whose "
       "tops are at z %s. The posts' inner faces are at r %s." % (n(P.Z_SEAT_TOP, 1), n(P.Z_POST_TOP, 1), n(post_in)), 2.2)
s.text(17, 273, "The wheels stay at %s so the encoder tower at %g deg and the port slot at 0 deg have the gaps between them. Encoder on D02."
       % (" / ".join("%g deg" % a for a in P.WHEEL_AZ), P.ENC_AZ), 2.2, col="#555")

# ---------------------------------------------------------------- DETAIL Y
vY, hY = engine.radial_section(["internal_structure"] + WHEEL, AZ, hidden=False)
dY = Port(s, 200, 190, 7.0, ox=P.BUSH_R, oy=(P.Z_POST_TOP + P.Z_WHEEL1) / 2 - 0.5)
clY = dY.clip("clipY", 153, 150, 94, 80)
dY.draw(vY, clip=clY, hidden=False, hatch_paths=hY, wv=0.28)
for r_ax in (P.BUSH_R, P.WHEEL_AXIS_R):                      # bush axis and wheel axis
    dY.s.line(dY.px(r_ax), 152, dY.px(r_ax), 228, 0.15, dash="6 2 1 2")
dY.dim_h(P.BUSH_R, P.WHEEL_AXIS_R, P.Z_WHEEL1 + 1.5, "%s ecc" % n(P.WHEEL_ECC), off=-6)
dY.dim_v(P.Z_POST_TOP, P.Z_POST_TOP + P.BUSH_FLANGE_T, P.BUSH_R + P.BUSH_FLANGE_D / 2, n(P.BUSH_FLANGE_T), off=6)
dY.dim_h(P.BUSH_R - P.WHEEL_POST_D / 2, P.BUSH_R + P.WHEEL_POST_D / 2, P.Z_SEAT_BOT - 1.0,
         "dia %s post" % n(P.WHEEL_POST_D), off=10, above=False)
s.rect(153, 150, 94, 80, 0.3)
s.text(153, 147, "DETAIL Y - BUSH AND POST     7 : 1", 3.0, weight="bold")
s.text(153, 236, "Bush flange %s thick sits on the post's underside at z %s." % (n(P.BUSH_FLANGE_T), n(P.Z_POST_TOP, 1)), 2.2)
s.text(153, 240, "Printed pin is the known weak point - brass with an", 2.2)
s.text(153, 244, "M2 grub screw in production.", 2.2)

# ---------------------------------------------------------------- ISOMETRIC
vI = engine.iso(WHEEL)
cx, cy = box_centre(vI)
pI = Port(s, 300, 195, 3.4, ox=cx, oy=cy)
pI.draw(vI, hidden=True, wv=0.3, wh=0.14)
s.text(253, 147, "WHEEL AND BUSH - ISOMETRIC     3.4 : 1", 3.0, weight="bold")
s.text(253, 236, "V-collar over the 623ZZ, on the eccentric bush,", 2.2)
s.text(253, 240, "as assembled. Hidden edges dashed.", 2.2)

save(s, "the60_v15_D01_knob_support")
