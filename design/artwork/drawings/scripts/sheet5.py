"""D05 - cooling: the duct, the fin channels, the ring's passages, the blower (v15)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

AZ = P.BLOWER_AZ                                   # 51 deg: the blower, and section E-E
DUCT_H = P.PLATE_T - P.CLOSING_T - P.WEB_T         # 5.0

s = Sheet("COOLING - DUCT, FIN CHANNELS, RING PASSAGES, BLOWER", "60-15-D05", "AS SHOWN")
s.frame(META)

AIR = ["base_plate", "rim_ring_STEEL", "closing_plate_AL", "closing_gasket_ASSUMED", "pad",
       "blower_BFB0305HA-C", "blower_saddle", "hood_lid", "hood_gasket_ASSUMED",
       "blower_inlet_gasket_ASSUMED", "blower_screw_0", "blower_screw_1",
       "internal_structure", "motion_board", "halo_diffuser"]
vE, hE = engine.radial_section(AIR, AZ, hidden=False, missing_ok=True)

# ---------------------------------------------------------------- SECTION E-E
pE = Port(s, 24, 92, 1.55, ox=0.0, oy=7.0)
clE = pE.clip("clipE", 17, 30, 179, 106)
pE.draw(vE, clip=clE, hidden=False, hatch_paths=hE, wv=0.32)
s.rect(17, 30, 179, 106, 0.3)
s.text(17, 27, "SECTION  E-E     scale 1.55 : 1", 3.4, weight="bold")
s.text(17, 141, "Right half, on the %g deg - %g deg axis, through the blower. Air is drawn down through the web, across "
       "the duct and out through the ring." % (AZ, AZ + 180), 2.2, col="#333")
s.line(pE.px(0), 32, pE.px(0), 134, 0.15, dash="6 2 1 2")
s.text(pE.px(0) + 1.5, 38.5, "CL", 2.2, col="#444")

pE.dim_v(P.CLOSING_T, P.CLOSING_T + DUCT_H, P.PLATE_R, "%s duct" % n(DUCT_H, 1), off=3)
pE.dim_v(0.0, P.PLATE_T, P.PLATE_R, n(P.PLATE_T), off=12)
pE.dim_h(0, P.PLENUM_R0, -6.0, "r %s plenum starts" % n(P.PLENUM_R0, 1), off=5)
pE.dim_h(0, P.R_CORE_DUCT, -6.0, "r %s duct ends" % n(P.R_CORE_DUCT, 1), off=11)
pE.dim_h(0, P.PLATE_R, -6.0, "r %s edge" % n(P.PLATE_R, 1), off=17)

for i, (mx, my, by) in enumerate([
        (P.MOTOR_R - 20.0, P.PLATE_T + 4.0, 38),
        (25.0, P.CLOSING_T + DUCT_H / 2, 55),
        ((P.TRENCH_R0 + P.TRENCH_R1) / 2, P.CLOSING_T + 3.0, 72),
        ((P.RING_WALL_R0 + P.PLATE_R) / 2, P.VENT_Z0 + P.VENT_H / 2, 89),
        (40.0, P.CLOSING_T / 2, 106)], 1):
    add_balloon(pE, mx, my, 190, by, i)

# ---------------------------------------------------------------- NOTES
s.text(210, 27, "NOTES", 3.4, weight="bold")
note_list(s, 206, 36, [
 (1, "One Delta BFB0305HA-C blower at %g deg, sitting on a printed saddle on the motion board's face and breathing "
     "DOWN through a dia %s hole in the core's web (the dia %s inlet opening seats on metal all round, on a %s foam "
     "ring). The Pi's own fan is off; this is the only moving air in the device."
     % (AZ, n(P.WEB_INLET_D, 1), n(P.BLOWER_INLET_D, 1), n(P.BLOWER_GASKET_T, 1))),
 (2, "The duct is the space between the web and the closing plate: %s tall, r under %s, divided into channels by "
     "fins. The rear plenums at r %s - %s (az 22-66 and 308-338) are where the channels end."
     % (n(DUCT_H, 1), n(P.R_CORE_DUCT, 1), n(P.PLENUM_R0, 1), n(P.R_CORE_DUCT, 1))),
 (3, "Two circuits. The +y side is driven: the blower discharges into a trench %s wide x %s tall, r %s - %s, roofed "
     "by the hood lid over az %g - %g, and out through the ring's exhaust groove. The -y side is passive, with "
     "%d exhaust passages %s wide at %s into the groove over az %g - %g."
     % (n(P.TRENCH_W, 1), n(P.PLATE_T - P.CLOSING_T, 1), n(P.TRENCH_R0, 1), n(P.TRENCH_R1, 1),
        P.HOOD_LID_AZ[0], P.HOOD_LID_AZ[1], len(P.EXHAUST_AZ), n(P.EXHAUST_W, 1),
        " / ".join("%g deg" % a for a in P.EXHAUST_AZ), P.EXHAUST_ARCS[1][0], P.EXHAUST_ARCS[1][1])
     + " Between az %g and %g the duct is solid outside r 64.8, because the trench sits in it." % (P.TRENCH_ZONE_AZ[0], P.TRENCH_ZONE_AZ[1])),
 (4, "Air enters through the ring's own openings and crosses its inner land through %d intake passages %s wide, "
     "into the duct. Intake and exhaust are separated by the arcs the exhaust grooves occupy: %s."
     % (P.INTAKE_N, n(P.INTAKE_W, 1),
        " and ".join("%g - %g deg" % (a, b) for a, b in P.EXHAUST_ARCS))),
 (5, "Every through-cut in the core - the Pi window, the carriage hole, the port slot - keeps %s of solid wall "
     "around it, so the duct cannot leak into the dry side of the device."
     % n(P.DUCT_MARGIN, 1)),
 (6, "The closing plate is the service access: %d M2.5 countersunk screws from below on a %s gasket. Nothing else "
     "opens the duct, and nothing inside it can be reached from above."
     % (len(P.CLOSING_SCREW_XY), n(P.GASKET_T, 1))),
], w=84)

# ---------------------------------------------------------------- DETAIL T - the trench and hood
dT = Port(s, 316, 74, 4.4, ox=(P.TRENCH_R0 + P.TRENCH_R1) / 2, oy=P.PLATE_T / 2)
clT = dT.clip("clipT", 300, 30, 100, 80)
dT.draw(vE, clip=clT, hidden=False, hatch_paths=hE, wv=0.28)
s.rect(300, 30, 100, 80, 0.3)
s.text(300, 27, "DETAIL T - TRENCH AND HOOD     4.4 : 1", 3.0, weight="bold")
dT.dim_h(P.TRENCH_R0, P.TRENCH_R1, P.CLOSING_T + 0.4, n(P.TRENCH_R1 - P.TRENCH_R0), off=3, above=False)
s.text(300, 116, "The trench runs from r %s, two millimetres of wall inside the plenum's" % n(P.TRENCH_R0, 1), 2.2)
s.text(300, 120, "suction side, out through the duct wall and the core's shoulder into the", 2.2)
s.text(300, 124, "ring. The lid seals to r %s, %s inside the wall." % (n(80.5, 1), n(0.7, 1)), 2.2)

# ---------------------------------------------------------------- PLAN - THE DUCT
Z1 = P.CLOSING_T + DUCT_H / 2
v1, h1 = engine.plan_section(["base_plate", "closing_plate_AL", "rim_ring_STEEL"], Z1, missing_ok=True)
p1 = Port(s, 77, 206, 0.55)
cl1 = p1.clip("clip1", 17, 150, 120, 112)
p1.draw(v1, clip=cl1, hidden=False, wv=0.25, hatch_paths=h1)
s.rect(17, 150, 120, 112, 0.3)
s.text(17, 147, "PLAN AT z %s - THE DUCT     scale %.2f : 1" % (n(Z1, 1), p1.k), 3.0, weight="bold")
s.line(p1.px(-P.PLATE_R), p1.py(0), p1.px(P.PLATE_R), p1.py(0), 0.12, dash="6 2 1 2")
s.line(p1.px(0), p1.py(-P.PLATE_R), p1.px(0), p1.py(P.PLATE_R), 0.12, dash="6 2 1 2")
for az, lab in ((AZ, "%g deg blower" % AZ), (0, "0 deg port"), (P.MOTOR_AZ, "%g deg carriage" % P.MOTOR_AZ)):
    a = math.radians(az)
    s.text(p1.px(96 * math.cos(a)), p1.py(96 * math.sin(a)) + (2.5 if math.sin(a) < -0.5 else 1.0),
           lab, 2.3, anchor="middle")
s.text(17, 266, "The fin channels and the two rear plenums. Air comes in at the rim all", 2.2)
s.text(17, 269.5, "the way round, runs inward along the channels and leaves through the", 2.2)
s.text(17, 273, "trench at %g deg and the passive groove at %g - %g deg."
       % (AZ, P.EXHAUST_ARCS[1][0], P.EXHAUST_ARCS[1][1]), 2.2)

# ---------------------------------------------------------------- PLAN - THE RING'S LAND
Z2 = P.VENT_Z0 + P.VENT_H / 2
v2, h2 = engine.plan_section(["rim_ring_STEEL"], Z2, missing_ok=True)
p2 = Port(s, 199, 206, 0.55)
cl2 = p2.clip("clip2", 141, 150, 116, 112)
p2.draw(v2, clip=cl2, hidden=False, wv=0.25, hatch_paths=h2)
s.rect(141, 150, 116, 112, 0.3)
s.text(141, 147, "PLAN AT z %s - THE RING ALONE     scale %.2f : 1" % (n(Z2, 1), p2.k), 3.0, weight="bold")
s.line(p2.px(-P.PLATE_R), p2.py(0), p2.px(P.PLATE_R), p2.py(0), 0.12, dash="6 2 1 2")
s.line(p2.px(0), p2.py(-P.PLATE_R), p2.px(0), p2.py(P.PLATE_R), 0.12, dash="6 2 1 2")
for a0, a1 in P.EXHAUST_ARCS:
    am = math.radians((a0 + a1) / 2)
    s.text(p2.px(64 * math.cos(am)), p2.py(64 * math.sin(am)) + 1.0, "exhaust %g-%g deg" % (a0, a1), 2.2, anchor="middle")
s.text(141, 266, "The ring on its own at the vent height: the outer wall's openings, the inner", 2.2)
s.text(141, 269.5, "land, and the passages that cross it. Everything the air does inside the", 2.2)
s.text(141, 273, "device happens between this land and the closing plate.", 2.2)

# ---------------------------------------------------------------- ISOMETRIC - BLOWER, SADDLE, HOOD
ISO = ["blower_saddle", "hood_lid", "blower_BFB0305HA-C"]
vI = engine.iso(ISO, direction=(0.9, -1.0, 0.7), hidden=True, missing_ok=True)
cx, cy = box_centre(vI)
pI = Port(s, 330, 196, 1.5, ox=cx, oy=cy)
clI = pI.clip("clipI", 263, 150, 132, 92)
pI.draw(vI, clip=clI, hidden=True, wv=0.28, wh=0.13)
s.rect(263, 150, 132, 92, 0.3)
s.text(263, 147, "BLOWER, SADDLE AND HOOD LID - ISOMETRIC     1.5 : 1", 3.0, weight="bold")
s.text(263, 246, "The saddle prints on its flat top face - the face the motion board sits against - with the hood's neck "
       "walls growing up from it, so it needs no supports. Two dia 2.2 holes pass straight through.", 2.2)
s.text(263, 249.5, "The lid is flat, %s thick, and butts against the saddle's neck." % n(2.5, 1), 2.2)

save(s, "the60_v15_D05_cooling")
