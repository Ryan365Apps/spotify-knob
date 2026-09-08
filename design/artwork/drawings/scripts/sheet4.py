"""D04 - the aluminium core, the stainless rim ring and the port face (v15)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from sheet import Sheet, Port, box_centre, add_balloon, note_list
from meta import META, n, save

s = Sheet("BASE - ALUMINIUM CORE, STAINLESS RIM RING, PORT FACE", "60-15-D04", "AS SHOWN")
s.frame(META)

BASE = ["base_plate", "rim_ring_STEEL", "closing_plate_AL", "closing_gasket_ASSUMED", "pad",
        "port_face", "usbc_board", "jack_board", "barrel_board", "light_board", "veml7700",
        "usbc_receptacle", "jack_3p5", "halo_diffuser", "led_strip_ENVELOPE"]
vD, hD = engine.radial_section(BASE, 0.0, hidden=False, missing_ok=True)

# ---------------------------------------------------------------- SECTION D-D
pD = Port(s, 24, 96, 1.75, ox=0.0, oy=6.0)
clD = pD.clip("clipD", 17, 30, 179, 106)
pD.draw(vD, clip=clD, hidden=False, hatch_paths=hD, wv=0.32)
s.rect(17, 30, 179, 106, 0.3)
s.text(17, 27, "SECTION  D-D     scale 1.75 : 1", 3.4, weight="bold")
s.text(17, 141, "Right half, on the 0 deg - 180 deg axis, through the port face. The base is three parts: the machined "
       "core, the ring round it and the closing plate under it.", 2.2, col="#333")
s.line(pD.px(0), 32, pD.px(0), 134, 0.15, dash="6 2 1 2")
s.text(pD.px(0) + 1.5, 38.5, "CL", 2.2, col="#444")

pD.dim_h(0, P.R_CORE_DUCT, -5.0, "r %s ducted core" % n(P.R_CORE_DUCT), off=5)
pD.dim_h(0, P.RIM_IN, -5.0, "r %s ring bore" % n(P.RIM_IN), off=11)
pD.dim_h(0, P.PLATE_R, -5.0, "r %s edge" % n(P.PLATE_R), off=17)
pD.dim_v(0.0, P.CLOSING_T, P.PLATE_R, n(P.CLOSING_T), off=3)
pD.dim_v(0.0, P.PLATE_T, P.PLATE_R, n(P.PLATE_T), off=9)
pD.dim_v(P.VENT_Z0, P.VENT_Z0 + P.VENT_H, P.PLATE_R, n(P.VENT_H), off=15)

for i, (mx, my, by) in enumerate([
        ((P.RING_WALL_R0 + P.PLATE_R) / 2, P.VENT_Z0 + P.VENT_H / 2, 38),
        ((P.RIM_IN + P.R_CORE_DUCT) / 2, P.PLATE_T - 2.0, 55),
        (40.0, P.CLOSING_T / 2, 72),
        (P.PORT_FACE_R0, 4.0, 89),
        (P.R_CORE_DUCT - 6.0, 2.5, 106)], 1):
    add_balloon(pD, mx, my, 190, by, i)

# ---------------------------------------------------------------- NOTES
s.text(210, 27, "NOTES", 3.4, weight="bold")
note_list(s, 206, 36, [
 (1, "Rim ring, r %s - %s x %s deep, machined stainless. %s. The outer wall r %s - %s carries the vent openings, "
     "%s x %s obround on a %d-position ring, each with a %s x 45 deg polished chamfer at the mouth; the parts list "
     "records 108 open once the ring screws and the port slot have taken their share."
     % (n(P.RIM_IN, 1), n(P.PLATE_R, 1), n(P.PLATE_T, 1), "stainless 304 or 316, bare",
        n(P.RING_WALL_R0, 1), n(P.PLATE_R, 1), n(P.VENT_W, 1), n(P.VENT_H, 1), P.VENT_N, n(P.VENT_CHAMFER, 1))),
 (2, "Core, r under %s, CNC 6082 aluminium: %s web, %s duct, ribs %s tall on the top face."
     % (n(P.RIM_IN, 1), n(P.WEB_T, 1), n(P.PLATE_T - P.CLOSING_T - P.WEB_T, 1), n(6.0, 1))),
 (3, "Closing plate: %s mm laser-cut aluminium, r under %s, %d x M2.5 countersunk from below, flush in the core's "
     "recess on a %s gasket. Unscrew it to clean the duct - it is the only way in."
     % (n(P.CLOSING_T, 0), n(P.R_CORE_DUCT, 1), len(P.CLOSING_SCREW_XY), n(P.GASKET_T, 1))),
 (4, "Port face at r %s, %s thick, carrying USB-C, a 3.5 mm jack, the barrel jack and the ambient-light sensor "
     "looking rearward through a dia %s hole. The port slot through the core is %s wide, from r %s out to the rim."
     % (n(P.PORT_FACE_R0, 1), n(P.PORT_FACE_T, 1), n(P.SENSOR_HOLE_D, 1), n(P.PORT_W, 1), n(P.PORT_NOTCH_R0, 1))),
 (5, "The edge the user sees is the ring, not the core: the ring's outer face is brushed axially and left bare, "
     "and every external face of the core is black hard anodised. No masked pads anywhere - internal faces are "
     "chromate or bare, so the finish line is a whole face, not a patch."),
 (6, "The ring is the mass at the largest radius and the structure the vents pass through, so its section is set "
     "by the openings, not by stiffness. Plate screws from below at %s, into pillars on the wall."
     % " / ".join("%g deg" % a for a in P.PLATE_SCREW_AZ)),
], w=84)

# ---------------------------------------------------------------- DETAIL S - a vent opening
vV, hV = engine.radial_section(["rim_ring_STEEL", "base_plate", "pad"], 200.0, hidden=False, missing_ok=True)
dS = Port(s, 350, 70, 9.0, ox=P.PLATE_R - 3.0, oy=P.VENT_Z0 + P.VENT_H / 2)
clS = dS.clip("clipS", 300, 30, 100, 80)
dS.draw(vV, clip=clS, hidden=False, hatch_paths=hV, wv=0.28)
s.rect(300, 30, 100, 80, 0.3)
s.text(300, 27, "DETAIL S - RIM RING WALL     9 : 1", 3.0, weight="bold")
dS.dim_v(P.VENT_Z0, P.VENT_Z0 + P.VENT_H, P.PLATE_R + 0.6, n(P.VENT_H), off=4)
dS.dim_h(P.RING_WALL_R0, P.PLATE_R, P.VENT_Z0 - 1.2, n(P.PLATE_R - P.RING_WALL_R0), off=6, above=False)
s.text(300, 116, "The openings pass through the %s outer wall on 3 deg, into an underside" % n(P.PLATE_R - P.RING_WALL_R0, 1), 2.2)
s.text(300, 120, "groove that the pad closes. The %s undercut under the wall is what lets" % n(0.8, 1), 2.2)
s.text(300, 124, "the groove be machined without breaking through the visible face.", 2.2)

# ---------------------------------------------------------------- PLAN - THE CORE'S TOP FACE
Z1 = P.PLATE_T - 0.5
PL1 = ["base_plate", "rim_ring_STEEL", "port_face"]
v1, h1 = engine.plan_section(PL1, Z1, missing_ok=True)
p1 = Port(s, 77, 206, 0.55)
cl1 = p1.clip("clip1", 17, 150, 120, 112)
p1.draw(v1, clip=cl1, hidden=False, wv=0.25, hatch_paths=h1)
s.rect(17, 150, 120, 112, 0.3)
s.text(17, 147, "PLAN AT z %s - THE CORE'S TOP FACE     scale %.2f : 1" % (n(Z1, 1), p1.k), 3.0, weight="bold")
s.line(p1.px(-P.PLATE_R), p1.py(0), p1.px(P.PLATE_R), p1.py(0), 0.12, dash="6 2 1 2")
s.line(p1.px(0), p1.py(-P.PLATE_R), p1.px(0), p1.py(P.PLATE_R), 0.12, dash="6 2 1 2")
s.text(p1.px(P.PLATE_R) + 1.0, p1.py(0) + 0.8, "0 deg", 2.3)
s.text(17, 266, "Three through-cuts: the Pi window, the carriage hole at %g deg, the port slot at 0 deg." % P.MOTOR_AZ, 2.2)
s.text(17, 269.5, "Each keeps %s of solid wall so the duct cannot leak into it. Ring bore r %s, duct ends r %s."
       % (n(P.DUCT_MARGIN, 1), n(P.RIM_IN, 1), n(P.R_CORE_DUCT, 1)), 2.2)
s.text(17, 273, "Ribs on this face stand %s tall and carry the boards." % n(6.0, 1), 2.2, col="#555")

# ---------------------------------------------------------------- PLAN - THROUGH THE VENTS
Z2 = P.VENT_Z0 + P.VENT_H / 2
v2, h2 = engine.plan_section(["rim_ring_STEEL", "base_plate", "closing_plate_AL", "port_face"], Z2, missing_ok=True)
p2 = Port(s, 199, 206, 0.55)
cl2 = p2.clip("clip2", 141, 150, 116, 112)
p2.draw(v2, clip=cl2, hidden=False, wv=0.25, hatch_paths=h2)
s.rect(141, 150, 116, 112, 0.3)
s.text(141, 147, "PLAN AT z %s - THROUGH THE VENTS     scale %.2f : 1" % (n(Z2, 1), p2.k), 3.0, weight="bold")
s.line(p2.px(-P.PLATE_R), p2.py(0), p2.px(P.PLATE_R), p2.py(0), 0.12, dash="6 2 1 2")
s.line(p2.px(0), p2.py(-P.PLATE_R), p2.px(0), p2.py(P.PLATE_R), 0.12, dash="6 2 1 2")
s.text(141, 266, "The openings run all the way round except where the port slot and the ring's own", 2.2)
s.text(141, 269.5, "screw bosses interrupt them. Air crosses the inner land through %d intake and" % P.INTAKE_N, 2.2)
s.text(141, 273, "3 exhaust passages - that circuit is D05.", 2.2)

# ---------------------------------------------------------------- ISOMETRIC - THE RING
vI = engine.iso(["rim_ring_STEEL"], direction=(0.9, -1.0, 0.55), hidden=False)
cx, cy = box_centre(vI)
pI = Port(s, 330, 196, 0.50, ox=cx, oy=cy)
clI = pI.clip("clipI", 263, 150, 132, 92)
pI.draw(vI, clip=clI, hidden=False, wv=0.22)
s.rect(263, 150, 132, 92, 0.3)
s.text(263, 147, "RIM RING - ISOMETRIC     0.50 : 1", 3.0, weight="bold")
s.text(263, 246, "The ring on its own, as machined. Every opening in the outer wall is on 3 deg to the radius, so the "
       "eye sees a fine louvre rather than a row of holes.", 2.2)
s.text(263, 249.5, "Finish: bare stainless - edge brushed axially, every opening mouth and both edges polished.", 2.2)

save(s, "the60_v15_D04_core_rim_ports")
