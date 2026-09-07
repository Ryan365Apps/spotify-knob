"""the 60 — v14 geometry.  build123d algebra mode.

Every bought part is placed as its CAD body (design/cad/bought-parts, or the vendor
STEP files for the panel and the Pi 5); parts without a body are named _ENVELOPE
bodies.  Every made part is the simplest shape that holds the bought parts in place.
Names in the assembly are stable and are what the checker and the drawings use.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import *
from params import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
D = math.radians

# ---------------------------------------------------------------- helpers (carried from v9)
def cyl(r, z0, z1):
    return Pos(0, 0, z0) * Cylinder(r, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
def tube(ro, ri, z0, z1, eps=0.01):
    return cyl(ro, z0, z1) - cyl(ri, z0 - eps, z1 + eps)
def frustum(r0, r1, z0, z1):
    return Pos(0, 0, z0) * Cone(r0, r1, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
def polar(az, r, z=0.0):
    a = D(az); return Pos(r * math.cos(a), r * math.sin(a), z) * Rot(0, 0, az)
def blk(radial, tangential, z0, z1, az, r, t=0.0):
    """box whose local x is radial (outward), y tangential, centred at (az, r), offset t tangentially"""
    return polar(az, r, (z0 + z1) / 2) * Pos(0, t, 0) * Box(radial, tangential, z1 - z0)
def box_at(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1)/2, (y0 + y1)/2, (z0 + z1)/2) * Box(x1 - x0, y1 - y0, z1 - z0)
def zbore(d, z0, z1, az=0.0, r=0.0, t=0.0):
    return polar(az, r, z0) * Pos(0, t, 0) * Cylinder(d/2, z1-z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
def rbore(d, r0, r1, az, z, t=0.0):
    return (Pos(0, 0, z) * Rot(0, 0, az) * Pos((r0 + r1) / 2, t, 0) * Rot(0, 90, 0)
            * Cylinder(d/2, r1 - r0, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
def csk_hole(d, z0, z1, az, r, head_d=6.5, head_h=1.6):
    """countersunk from the underside (z0)"""
    h = zbore(d, z0 - 1, z1 + 1, az, r)
    h += polar(az, r, z0 - 0.01) * Cone(head_d/2, d/2, head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return h
def csk_xy(d, x, y, z0, z1, head_d=6.5, head_h=1.6):
    return Pos(x, y, 0) * (cyl(d/2, z0 - 1, z1 + 1) + Pos(0, 0, z0 - 0.01) * Cone(head_d/2, d/2, head_h, align=(Align.CENTER, Align.CENTER, Align.MIN)))
def revolve_profile(pts):
    return revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z)
def xy_slot(r0, r1, half_w, z0, z1, az=0.0):
    return blk(r1 - r0, 2 * half_w, z0, z1, az, (r0 + r1) / 2)
def label(shape, name):
    try: shape.label = name
    except Exception: pass
    return shape

# ---------------------------------------------------------------- bought bodies (loaded once)
_cache = {}
def bought(name, path=None):
    key = path or os.path.join(STEP, name)
    if key not in _cache:
        _cache[key] = import_step(key)
    return _cache[key]
def bought_solids(name, path=None):
    c = bought(name, path)
    out = {}
    def walk(node):
        kids = getattr(node, "children", None) or []
        if kids:
            for k in kids: walk(k)
        else:
            for i, s in enumerate(node.solids()):
                lab = node.label or f"solid{len(out)}"
                out[lab if i == 0 else f"{lab}_{i}"] = s
    walk(c)
    if not out:
        out = {f"solid{i}": s for i, s in enumerate(c.solids())}
    return out
def bodies_of(name, place, keep=None, prefix="", path=None):
    out = {}
    for lab, s in bought_solids(name, path).items():
        if keep and not keep(lab): continue
        out[prefix + lab] = place * s
    return out

# ---------------------------------------------------------------- the panel, lens, flex (vendor STEP + ASSUMED parts)
def panel_place():
    return Pos(0, 0, Z_GLASS0) * Rot(0, 0, PANEL_ROT_DEG)
def panel_bodies():
    out = {}
    s = import_step(PANEL_STP).solids()[0]
    out["panel_glass"] = panel_place() * s
    # back-side component area (PUBLISHED 60 x 68.36, max 1.5) - centred toward the chin (ASSUMED)
    out["panel_components_ENVELOPE"] = panel_place() * Pos(0, PANEL_COMP_OFFSET, -PANEL_COMP_H/2) * Box(PANEL_COMP_W, PANEL_COMP_L, PANEL_COMP_H)
    out["lens_ASSUMED"] = cyl(LENS_R, Z_GLASS1, Z_LENS1)
    return out
def flex_bodies():
    """the panel's flex from the component area, out over the seat, down through the slot to the display CONNECT BOARD's CN2
    (v12: the adapter kit's connect board takes the panel flex; a 150 mm flat cable goes on to the driver board - v10/v11
    had the flex reaching the driver board directly, which it cannot).  Bend radius 1.0, ASSUMED route.  Tab at 0 deg (+x)."""
    out = {}
    t0 = -12.0                                    # tangential centre of the panel flex (touch tail beside it at +6)
    zf = Z_GLASS0 - PANEL_FPC_T
    out["panel_flex_1"] = box_at(PANEL_COMP_OFFSET + PANEL_COMP_L/2 - 2.0, PANEL_TAB_R - 0.75, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, zf, Z_GLASS0)
    r_out = 67.9
    out["panel_flex_2"] = box_at(PANEL_TAB_R - 0.75, r_out, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, zf, Z_GLASS0)
    z_over = Z_CB0 + CB_T + CB_CN2_H + 1.0        # 15.7: passes 1.0 over CN2, out to the wall side, and comes back into it
    out["panel_flex_3"] = box_at(r_out, r_out + PANEL_FPC_T, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, z_over, zf)          # down
    x_cn2 = CB_R + CB_L/2                         # 77: the connect board's outer edge; CN2 opens outward
    out["panel_flex_4"] = box_at(r_out, x_cn2 + 1.5, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, z_over, z_over + PANEL_FPC_T)   # outward over CN2
    out["panel_flex_5"] = box_at(x_cn2 + 1.5, x_cn2 + 1.5 + PANEL_FPC_T, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, Z_CB0 + CB_T + CB_CN2_H/2, z_over)   # down again
    out["panel_flex_6"] = box_at(x_cn2 - 2.0, x_cn2 + 1.5, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, Z_CB0 + CB_T + CB_CN2_H/2 - PANEL_FPC_T, Z_CB0 + CB_T + CB_CN2_H/2)   # into CN2
    t1 = 6.0                                      # touch tail (ASSUMED 8 wide), drawn to the slot only
    out["touch_tail_ASSUMED"] = box_at(PANEL_TAB_R - 6.0, r_out - 0.5, t1 - TOUCH_TAIL_W/2, t1 + TOUCH_TAIL_W/2, zf, Z_GLASS0)
    out["touch_tail_ASSUMED_down"] = box_at(r_out - 0.5, r_out - 0.5 + PANEL_FPC_T, t1 - TOUCH_TAIL_W/2, t1 + TOUCH_TAIL_W/2, z_over + 2.0, zf)
    return out

# ---------------------------------------------------------------- the Pi 5, cooler, its plugs (vendor STEP reduced + envelopes)
def pi_place():
    return Pos(PI_X0, PI_Y0, PI_Z0)
def pi_bodies():
    out = {}
    sol = import_step(PI_STP).solids()
    named = 0
    for s in sorted(sol, key=lambda q: -q.volume):
        bb = s.bounding_box()
        if bb.size.X > 80 and bb.size.Y > 50: n = "pi_pcb"
        elif bb.min.X > 66 and bb.size.Z > 13: n = f"pi_usba_eth_{named:02d}"; named += 1
        elif 24 < bb.min.X < 25 and 14 < bb.min.Y < 15: n = "pi_soc" if bb.min.Z < 2 else "pi_soc_lid"
        elif bb.min.Y > 49 and bb.size.X > 40: n = "pi_header"
        elif bb.min.X < 7 and bb.min.Y < 0 and bb.size.X > 8: n = "pi_usbc" if "pi_usbc" not in out else "pi_usbc_2"
        else: n = f"pi_part_{named:02d}_{bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.1f}"; named += 1
        out[n] = pi_place() * s
    # micro-HDMI receptacles are not in the vendor STEP: envelopes on the y = 0 edge (ASSUMED)
    for i, xc in enumerate((PI_HDMI0_X, PI_HDMI1_X)):
        out[f"pi_hdmi{i}_ENVELOPE"] = pi_place() * box_at(xc - PI_HDMI_W/2, xc + PI_HDMI_W/2, -0.4, PI_HDMI_D - 0.4, PI_T, PI_T + PI_HDMI_H)
    return out
def cooler_bodies():
    """Active Cooler: heatsink block + blower on top (PUBLISHED 63.5 x 42.5 x 13.7 total; split ASSUMED)"""
    out = {}
    z0 = PI_T + COOLER_BASE_ABOVE_BOARD
    hs_h = COOLER_H - 6.7
    out["cooler_heatsink_ENVELOPE"] = pi_place() * box_at(COOLER_X0, COOLER_X0 + COOLER_L, COOLER_Y0, COOLER_Y0 + COOLER_W, z0, z0 + hs_h)
    if COOLER_FAN_FITTED:
        out["cooler_fan_ENVELOPE"] = pi_place() * box_at(FAN_X0, FAN_X0 + FAN_SIZE, FAN_Y0, FAN_Y0 + FAN_SIZE, z0 + hs_h, z0 + COOLER_H)
    return out
def pi_holes_xy():
    return [(PI_X0 + x, PI_Y0 + y) for x, y in PI_HOLES]
HDMI_X = PI_X0 + (PI_HDMI1_X if HDMI_PORT == 1 else PI_HDMI0_X)      # device x of the micro-HDMI in use
USBC_XC = PI_X0 + (PI_USBC[0] + PI_USBC[1])/2                         # device x of the Pi's USB-C
def pi_plug_bodies():
    out = {}
    # PC data lead: UP-ANGLE USB-C plug in the Pi's USB-C (ASSUMED head 12 x 12.5 x 6.5 beyond the edge, cable stub straight up)
    zc = PI_Z0 + 0.34 + 4.6/2
    out["usbc_plug_pi_ENVELOPE"] = box_at(USBC_XC - 6.0, USBC_XC + 6.0, PI_Y0 - 12.5, PI_Y0 + 0.5, zc - 3.25, zc + 3.25)
    out["usbc_plug_pi_ENVELOPE_cable"] = box_at(USBC_XC - 3.0, USBC_XC + 3.0, PI_Y0 - 13.0, PI_Y0 - 7.0, zc + 3.25, Z_SEAT_BOT - 0.5)   # the lead leaves the head's far end straight up
    # HDMI ribbon: up-angle micro-HDMI plug (ASSUMED 12 x 8 x 5) in HDMI1; the ribbon rises beside it, loops outward and comes back
    # into the adapter's HDMI-A socket, which faces the same way (270 deg) 9 mm above.  A end plug ASSUMED 21 x 12 x 6.
    zp0 = PI_Z_TOP
    out["hdmi_plug_micro_ENVELOPE"] = box_at(HDMI_X - 6, HDMI_X + 6, PI_Y0 - 8.0, PI_Y0 + 0.5, zp0, zp0 + 5.0)
    yr = PI_Y0 - 8.3                                      # where it rises, just outside the micro plug
    xa = ADAPTER_X0 + ADAPTER_L/2 + 0.5                   # the HDMI-A socket's centre x (0.5 off the board's middle)
    z_a = Z_ADAPTER1 + ADAPTER_HDMI_H/2                   # the socket's axis height
    y_far = PI_Y0 - 0.8 - 21.0 - 3.5                      # 3.5 beyond the A plug's tail
    out["hdmi_ribbon_1"] = box_at(HDMI_X - 10, HDMI_X + 10, yr - 0.3, yr, zp0 + 5.0, Z_PLATE_TOP + 1.3)              # up out of the micro plug
    out["hdmi_ribbon_2"] = box_at(HDMI_X - 10, HDMI_X + 10, y_far, yr, Z_PLATE_TOP + 1.0, Z_PLATE_TOP + 1.3)          # outward along the plate top, 1.0 over it
    out["hdmi_ribbon_3"] = box_at(xa - 10, HDMI_X + 10, y_far - 0.3, y_far, Z_PLATE_TOP + 1.0, z_a + 0.3)              # up beyond the A plug's tail, shifting across to it
    out["hdmi_ribbon_4"] = box_at(xa - 10, xa + 10, y_far, y_far + 3.5 + 0.5, z_a, z_a + 0.3)                           # into the A plug's tail
    out["hdmi_plug_A_ENVELOPE"] = box_at(xa - 6.0, xa + 6.0, PI_Y0 - 0.8 - 21.0, PI_Y0 - 0.8, z_a - 3.0, z_a + 3.0)   # in the socket, body outward
    # header housing: 2 x 5 crimp housing on pins 1-10 (5 V, GND, UART) - ASSUMED 12.7 x 5.1 x 9 on the header's base
    hx0, hx1, hy0, hy1, hh = PI_HEADER
    out["header_housing_ENVELOPE"] = pi_place() * box_at(hx0, hx0 + 12.7, hy0, hy1, PI_T + 2.5, PI_T + 2.5 + 9.0)
    # audio board's USB: right-angle USB-A plug in the LOWER socket of the USB 3.0 stack (the middle stack; v15 review - it was drawn in the
    # Ethernet jack, the stack nearest the HDMI edge). ASSUMED 9 protrusion x 12 x 6.8, under the flat cable's leg (z 14.9) and the bracket's slab (z 9.5)
    out["usba_plug_ENVELOPE"] = box_at(PI_X0 + PI_L + PI_OVERHANG, PI_X0 + PI_L + PI_OVERHANG + 9.0, PI_Y0 + 23.0, PI_Y0 + 35.0, PI_Z0 + 1.0, PI_Z0 + 7.8)
    return out
def pi_stack_bodies():
    """the four M2.5 x 12 hex standoffs on the Pi (PUBLISHED 5 AF) and the 0.5 washers under it"""
    out = {}
    r = 5.0 / 2 / math.cos(math.radians(30))
    for i, (x, y) in enumerate(pi_holes_xy()):
        out[f"pi_standoff_{i}"] = Pos(x, y, PI_Z_TOP) * (extrude(RegularPolygon(r, 6), STANDOFF_L) - Cylinder(2.05/2, 30))
        out[f"pi_washer_{i}"] = Pos(x, y, CLOSING_T) * (Cylinder(5.0/2, PI_Z0 - CLOSING_T, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(2.7/2, 5))
    return out

# ---------------------------------------------------------------- knob
def body_profile():
    rb, rk, ri, rg = R_BORE, R_KNOB, R_CROWN_IN, R_GROOVE_ROOT
    zs, zt, zcb = Z_SKIRT_BOT, Z_KNOB_TOP, Z_CROWN_BOT
    f = WHEEL_V_FLAT / 2
    zr = zcb + STRIP_T                                                     # v13: the code ring's recess in the crown's underside (nothing on the bore)
    return [(rb, zs), (rk - CH_BOT, zs), (rk, zs + CH_BOT),
            (rk, zt - CH_TOP), (rk - CH_TOP, zt),
            (ri + CH_IN, zt), (ri, zt - CH_IN),
            (ri, zcb), (CODE_R0, zcb), (CODE_R0, zr), (CODE_R1, zr), (CODE_R1, zcb), (rb, zcb),
            (rb, Z_GROOVE1), (rg, Z_RIDGE_MID + f), (rg, Z_RIDGE_MID - f), (rb, Z_GROOVE0)]
def knob_body_smooth():
    return revolve_profile(body_profile())
def knob_body(knurl=None):
    if (KNURL_ON if knurl is None else knurl):
        from knurl import apply_knurl
        return apply_knurl(None)
    return knob_body_smooth()

# ---------------------------------------------------------------- plate, pad
def carriage_hole(m=0.0, z0=-3, z1=PLATE_T + 1):
    """m: extra margin all round (used to keep the duct clear of the hole)"""
    d = MOTOR_OD + 2 * 1.0 + 1.5 + 2 * m
    h = zbore(d, z0, z1, MOTOR_AZ, MOTOR_R)
    h += zbore(d, z0, z1, MOTOR_AZ, MOTOR_R - CLUTCH_LIFT)
    h += blk(CLUTCH_LIFT, d, z0, z1, MOTOR_AZ, MOTOR_R - CLUTCH_LIFT/2)
    h += blk(CARRIAGE_TAB_T + CLUTCH_LIFT + 1.5 + 4.0 + 2 * m, CARRIAGE_TAB_W + 1.5 + 2 * m, z0, z1, MOTOR_AZ, MOTOR_R - MOTOR_OD/2 - 1.0 - (CARRIAGE_TAB_T + CLUTCH_LIFT + 4.0)/2)   # tab slot
    h += blk(4.0 + 2 * m, 2.5 + 2 * m, z0, z1, MOTOR_AZ, 39.5, t=6.0)                                     # v14: the sensor lead's notch beside the tab slot
    return h
def port_slot(z0=-3, z1=PLATE_T + 1, m=0.0):
    return xy_slot(PORT_NOTCH_R0 - m, PLATE_R + 2, PORT_W/2 + m, z0, z1, 0.0)
def pi_window(m=0.0, z0=-3, z1=PLATE_T + 1):
    c = 0.75 + m
    w = box_at(PI_X0 - c, PI_X0 + PI_L + PI_OVERHANG + c, PI_Y0 - c, PI_Y0 + PI_W + c, z0, z1)
    w += box_at(USBC_XC - 7.0 - m, USBC_XC + 7.0 + m, PI_Y0 - 14.0 - m, PI_Y0 + 1, z0, z1)             # USB-C up-angle plug's head
    w += box_at(HDMI_X - 7 - m, HDMI_X + 7 + m, PI_Y0 - 9.5 - m, PI_Y0 + 1, z0, z1)                     # HDMI plug notch
    w += box_at(PI_X0 + PI_L + PI_OVERHANG - 1, PI_X0 + PI_L + PI_OVERHANG + 10.0 + m, PI_Y0 + 22.0 - m, PI_Y0 + 36.0 + m, z0, z1)   # USB-A plug notch (v15: at the USB 3.0 stack)
    return w
def sector(az0, az1, r_out, z0, z1):
    """a pie wedge from az0 to az1 (deg, anticlockwise) out to r_out"""
    n = max(2, int(math.ceil((az1 - az0) / 5.0)))
    pts = [(0.0, 0.0)] + [(r_out * math.cos(math.radians(az0 + (az1 - az0) * i / n)), r_out * math.sin(math.radians(az0 + (az1 - az0) * i / n))) for i in range(n + 1)]
    return Pos(0, 0, z0) * extrude(Polygon(*pts, align=None), z1 - z0)
# ---------------------------------------------------------------- the base plate as the heatsink (the60-thermal-plan.md, section 14)
#   three bodies: the aluminium CORE (web, duct, ribs, r < 75.2), the steel RIM RING (r 75.2-87.7, plain edge,
#   intake and exhaust grooves in its underside, an inward flange on a rebate of the core), and the 1 mm CLOSING PLATE
#   screwed flush into the core's underside.  The pad is a ring under the rim ring.
def rear_wedge(az_half, r_out, z0, z1):
    return sector(-az_half, az_half, r_out, z0, z1)
def speaker_ear_xy():
    """the cradle's two ear screws"""
    cx, cy = SPEAKER_CENTRE
    return [(cx + 22.5 * math.cos(D(a)), cy + 22.5 * math.sin(D(a))) for a in SPEAKER_EAR_AZ]
def duct_islands():
    """solid spots left in the duct: a full-depth Ø7 island under every closing-plate screw (from below), and the fill of two dead scraps"""
    k = None
    for (x, y) in CLOSING_SCREW_XY:
        b = Pos(x, y, 0) * Cylinder(3.5, PLATE_T, align=(Align.CENTER, Align.CENTER, Align.MIN)); k = b if k is None else k + b
    k += box_at(USBC_XC + 9.5 - 0.5, HDMI_X - 9.5 + 0.5, PI_Y0 - 12.0, PI_Y0 - 3.0, 0, PLATE_T)   # fills two dead scraps of channel between the USB-C notch's wall and the HDMI notch's wall
    return k
def island_links():
    """v15: where a closing-screw island sits in a channel band it blocks the channel(s) under it - a cross-cut either side
    (ISLAND_LINK_L from the island's edge, the width of three channels) joins the blocked channel to its neighbours"""
    ys = channel_ys(); k = None
    for (x, y) in CLOSING_SCREW_XY:
        blocked = [yk for yk in ys if abs(yk - y) < 3.5 + FIN_CH_W/2]
        if not blocked: continue
        y0 = min(blocked) - FIN_PITCH - FIN_CH_W/2; y1 = max(blocked) + FIN_PITCH + FIN_CH_W/2
        for sx in (-1, 1):
            b = box_at(x + sx * 3.5 + (0 if sx > 0 else -ISLAND_LINK_L), x + sx * 3.5 + (ISLAND_LINK_L if sx > 0 else 0), y0, y1, CLOSING_T, CLOSING_T + DUCT_H)
            k = b if k is None else k + b
    return k
def piers():
    """v15: a Ø7 pier hanging PIER_H into the duct under every screw from the top (rule 5: the thickening goes down, never up)"""
    k = None
    for (x, y) in top_screw_xy() + [GND_BOND_XY] + blower_screw_xy():
        b = Pos(x, y, CLOSING_T + DUCT_H - PIER_H - 0.01) * Cylinder(PIER_D/2 + (0.5 if (x, y) == GND_BOND_XY else 0), PIER_H + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
        k = b if k is None else k + b
    return k
def channel_ys():
    """centre y of every fin channel: both bands beside the Pi window, from its margin wall outward (v12: the Pi is off-centre)"""
    ys = []
    y = PI_Y0 + PI_W + 0.75 + DUCT_MARGIN + FIN_CH_W/2 + 0.5
    while y + FIN_CH_W/2 <= R_CORE_DUCT - 1.0: ys.append(y); y += FIN_PITCH
    y = PI_Y0 - 0.75 - DUCT_MARGIN - FIN_CH_W/2 - 0.5
    while -y + FIN_CH_W/2 <= R_CORE_DUCT - 1.0: ys.append(y); y -= FIN_PITCH
    return ys
def trench(z0=CLOSING_T, z1=PLATE_T + 1):
    """v15: the blower's discharge trench, cut from the top: TRENCH_W wide from TRENCH_R0 out through the duct wall; from the
    rebate (r 72.2) outward it widens along the arc to TRENCH_FOOT_AZ, to TRENCH_R1. Used on the core, the ring and the hood."""
    t = blk(R_CORE_DUCT + 0.02 - TRENCH_R0, TRENCH_W, z0, z1, BLOWER_AZ, (TRENCH_R0 + R_CORE_DUCT + 0.02)/2)
    t += sector(TRENCH_FOOT_AZ[0], TRENCH_FOOT_AZ[1], TRENCH_R1, z0, z1) - cyl(R_CORE_DUCT - 0.02, z0 - 1, z1 + 1)
    try:                                                                                 # v15 review: every vertical corner of the trench rounded R2.5 (a Ø5 cutter's natural corner; the turns cost less)
        t = t.fillet(TRENCH_FILLET, t.edges().filter_by(Axis.Z))
    except Exception:
        pass
    return t
def suction_wall():
    """the 2 mm wall between the plenum's suction side and the trench (the trench's inner end): left solid in the duct"""
    return blk(2.0, TRENCH_W + 4.0, CLOSING_T - 1, CLOSING_T + DUCT_H + 1, BLOWER_AZ, TRENCH_R0 - 1.0)
def duct():
    """everything hollow between the web (z 6) and the closing plate (z 1) inside r 72.2"""
    z0, z1 = CLOSING_T, CLOSING_T + DUCT_H
    ro = R_CORE_DUCT - DUCT_WALL                                                        # the duct's outer wall (r 70.2-72.2) ties the core's shoulder to the web
    d = tube(ro, COLLECTOR_R0, z0, z1) - sector(-50.0, TRENCH_ZONE_AZ[1], 100, z0 - 1, z1 + 1)   # the collector, front and sides (az 61-310; v14 50-310)
    for yk in channel_ys():                                                             # straight channels either side of the Pi window, front to rear
        d += box_at(-R_CORE_DUCT, R_CORE_DUCT, yk - FIN_CH_W/2, yk + FIN_CH_W/2, z0, z1)
    d += sector(22.0, 66.0, ro, z0, z1) - cyl(PLENUM_R0, z0 - 1, z1 + 1)                # the rear plenums, both sides of the port slot
    d += sector(308.0, 338.0, ro, z0, z1) - cyl(PLENUM_R0, z0 - 1, z1 + 1)
    d += island_links()
    d &= cyl(ro, z0 - 1, z1 + 1)
    d -= sector(TRENCH_ZONE_AZ[0], TRENCH_ZONE_AZ[1], ro + 1, z0 - 1, z1 + 1) - cyl(TRENCH_R0 - 2.0, z0 - 2, z1 + 2)   # v15: the trench zone - solid outside r 64.8, so no channel end or collector meets the trench
    d -= pi_window(DUCT_MARGIN, z0 - 1, z1 + 1)                                         # walls round every through-cut
    d -= carriage_hole(DUCT_MARGIN, z0 - 1, z1 + 1)
    d -= port_slot(z0 - 1, z1 + 1, DUCT_MARGIN)
    d -= duct_islands()
    d -= suction_wall()                                                                 # v15: the trench is walled off from the suction side
    d -= trench(z0 - 1, z1 + 1)                                                         # (the trench itself is cut separately, from the top)
    d += zbore(WEB_INLET_D + 4.0, z0, z1, BLOWER_AZ, BLOWER_R)                            # v15 review: a clear Ø26 pocket under the blower's inlet - no fins across it (they earned ~5% of the surface and throttled the inlet)
    d -= piers()
    return d
def intake_azs():
    """the intake passages' azimuths: the 11.25 deg grid over 45-315 (v14), cut only inside the intake arc and away from the motor's
    through-hole, the USB-C plug's notch and the exhaust arcs' walls"""
    out = []
    for i in range(INTAKE_N):
        az = INTAKE_PASS_AZ0 + (INTAKE_PASS_AZ1 - INTAKE_PASS_AZ0) * (i + 0.5) / INTAKE_N
        if az < INTAKE_AZ0 + 4.5 or az > INTAKE_AZ1 - 4.5: continue
        if abs(az - MOTOR_AZ) <= 14.0: continue
        if abs(az - USBC_NOTCH_AZ) <= 5.0: continue
        out.append(az)
    return out
def passage(az, w, r0, r1, z0, z1):
    return blk(r1 - r0, w, z0, z1, az, (r0 + r1)/2)
def core_tunnels():
    """v15: the passages through the core's shoulder and duct wall are CLOSED tunnels z 1-4.5 (v14 cut them open to the underside,
    which joined the intake to the space under the plate); intake ones on the intake grid, the -y exhaust ones on EXHAUST_AZ"""
    g = None
    for az in intake_azs():
        b = passage(az, INTAKE_W, R_CORE_DUCT - DUCT_WALL - 0.5, RIM_IN + 0.5, CLOSING_T, CLOSING_T + INTAKE_H); g = b if g is None else g + b
    for az in EXHAUST_AZ:
        g += passage(az, EXHAUST_W, R_CORE_DUCT - DUCT_WALL - 0.5, RIM_IN + 0.5, CLOSING_T, CLOSING_T + INTAKE_H)
    return g
def ring_land_grooves():
    """the same passages continued as open grooves in the ring's inner land (r 75.2 to the groove), the pad closes them"""
    g = None
    for az in intake_azs():
        b = passage(az, INTAKE_W, RIM_IN - 0.5, GROOVE_R0 + 0.5, -1, INTAKE_H); g = b if g is None else g + b
    for az in EXHAUST_AZ:
        g += passage(az, EXHAUST_W, RIM_IN - 0.5, GROOVE_R0_EXH + 0.5, -1, INTAKE_H)
    return g
def intake_grooves(r0, r1):
    """(kept for the checker) the intake throat: every intake passage as one body between r0 and r1"""
    g = None
    for az in intake_azs():
        b = passage(az, INTAKE_W, r0, r1, CLOSING_T if r1 <= RIM_IN + 0.5 else -1, CLOSING_T + INTAKE_H); g = b if g is None else g + b
    return g
def exhaust_grooves(r0, r1):
    g = None
    for az in EXHAUST_AZ:
        b = passage(az, EXHAUST_W, r0, r1, CLOSING_T, CLOSING_T + INTAKE_H); g = b if g is None else g + b
    return g
def rot_xy(cx, cy, lx, ly, az):
    a = D(az); return (cx + lx * math.cos(a) - ly * math.sin(a), cy + lx * math.sin(a) + ly * math.cos(a))
def top_screw_xy():
    """every M2.5 screw into the plate's top face: converter (2), audio (4), servo frame (2), connect bracket (2), speaker cradle (2).
    v15: the motion board's four are in the blower's saddle now"""
    out = []
    for t in (-CONV_HOLE_T, CONV_HOLE_T): out.append(rot_xy(0, 0, CONV_R, t, CONV_AZ))
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append((AUDIO_CENTRE[0] + sx * (AUDIO_L/2 - 3.5), AUDIO_CENTRE[1] + sy * (AUDIO_W/2 - 3.5)))
    for sy in (-SERVO_EAR_T, SERVO_EAR_T): out.append(rot_xy(0, 0, SERVO_R0 - 1.5 + (SERVO_L + 1.5)/2, sy, MOTOR_AZ))
    out += speaker_ear_xy()
    out += CB_SCREW_XY
    return out
def blower_screw_xy():
    """the blower's two Ø2.4 holes on its 24 x 24 diagonal: M2 x 16 through the saddle and the blower into piers"""
    h = BLOWER_HOLE_PITCH/2
    return [rot_xy(0, 0, BLOWER_R + h, h, BLOWER_AZ), rot_xy(0, 0, BLOWER_R - h, -h, BLOWER_AZ)]
def gasket_groove(depth=GASKET_T):
    """v15 (rule 5): the closing plate seals on a die-cut gasket in a groove of the recess floor: a ring on the duct's outer wall and
    bands on the walls round the three through-cuts"""
    z0, z1 = CLOSING_T, CLOSING_T + depth
    g = tube(R_CORE_DUCT - 0.3, R_CORE_DUCT - DUCT_WALL + 0.3, z0, z1)
    g += pi_window(DUCT_MARGIN - 0.3, z0, z1) - pi_window(0.3, z0 - 1, z1 + 1)
    g += carriage_hole(DUCT_MARGIN - 0.3, z0, z1) - carriage_hole(0.3, z0 - 1, z1 + 1)
    g += port_slot(z0, z1, DUCT_MARGIN - 0.3) - port_slot(z0 - 1, z1 + 1, 0.3)
    g &= cyl(R_CORE_DUCT - 0.2, z0 - 1, z1 + 1)
    g -= duct()
    g -= pi_window(0.3, z0 - 1, z1 + 1) + carriage_hole(0.3, z0 - 1, z1 + 1) + port_slot(z0 - 1, z1 + 1, 0.3)   # the through-cuts themselves
    return g
def closing_gasket():
    return {"closing_gasket_ASSUMED": gasket_groove()}
def base_plate():
    """the aluminium core: r < 75.2, 8 tall; rebate for the ring's flange; recess for the closing plate; the duct (2 web / 5 duct / 1 plate);
    the passages as closed tunnels; the blower's inlet hole and discharge trench; piers; the gasket groove; ribs on top"""
    p = cyl(RIM_IN, 0, PLATE_T)
    p -= tube(RIM_IN + 1, R_CORE_DUCT, RIM_STEP_Z, PLATE_T + 1)                          # rebate the ring's flange sits in (r 72.2-75.2, z 5-8)
    p -= cyl(R_CORE_DUCT, -1, CLOSING_T)                                                 # recess for the closing plate (z 0-1)
    p -= duct()
    p -= core_tunnels()                                                                  # the passages through the duct wall and the shoulder into the collector / plenum, closed top and bottom
    p -= carriage_hole(); p -= port_slot(); p -= pi_window()
    p -= zbore(WEB_INLET_D, CLOSING_T + DUCT_H - 1, PLATE_T + 1, BLOWER_AZ, BLOWER_R)     # v15: the blower's inlet hole through the web
    p -= trench(CLOSING_T, PLATE_T + 1)                                                  # v15: the discharge trench, open-topped under the hood
    p -= gasket_groove()
    for (x, y) in CLOSING_SCREW_XY:                                                     # M2.5 tapped for the closing plate's countersunk screws
        p -= Pos(x, y, -1) * Cylinder(1.0, CLOSING_T + 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for az in RING_SCREW_AZ:                                                            # M3 csk from below through the shoulder into the ring's flange
        p -= csk_hole(3.4, 0, RIM_STEP_Z, az, RING_SCREW_R)
    p -= zbore(2.5, RIM_STEP_Z - 3.0, RIM_STEP_Z + 0.1, RING_BOND_AZ, RING_BOND_R)         # the ring's bond screw, M3 tapped 3.0 into the shoulder from its top face (GROUNDING 4.1)
    for (x, y) in top_screw_xy():                                                       # everything bolted to the plate top: M2.5 tapped, blind, 3.5 into web + pier
        p -= Pos(x, y, PLATE_T - BLIND_D) * Cylinder(1.0, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in blower_screw_xy():                                                    # the blower's two M2 into piers
        p -= Pos(x, y, PLATE_T - BLIND_D) * Cylinder(0.8, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(GND_BOND_XY[0], GND_BOND_XY[1], PLATE_T - BLIND_D) * Cylinder(1.25, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))   # chassis ground: M3 tapped blind into its pier
    for az in RIB_AZ:                                                                   # ribs on the top face
        r0 = RIB_R0_BY_AZ.get(az, RIB_R0)
        p += blk(RIB_R1 - r0, RIB_T, PLATE_T - 0.01, PLATE_T + RIB_H, az, (r0 + RIB_R1)/2)
    return p
def vent_azs():
    """the 120 positions az 1.5 + 3k; returns (az, kind) for those with the groove behind them (not the port face, not the
    carriage hole's arc, not its mirror)"""
    out = []
    for k in range(VENT_N):
        az = (360.0 / VENT_N) * (k + 0.5)
        if any(a0 < az < a1 for a0, a1 in VENT_SKIP_ARCS): continue
        if INTAKE_AZ0 + 1.0 < az < INTAKE_AZ1 - 1.0: out.append((az, "intake"))
        elif any(a0 + 1.0 < az < a1 - 1.0 for a0, a1 in EXHAUST_ARCS): out.append((az, "exhaust"))
    return out
def groove_arcs():
    """the underside groove's arcs: the intake arc split round the carriage hole, plus the two exhaust arcs; (az0, az1, r_inner)"""
    w = GROOVE_WALL_DEG / 2
    m0, m1 = VENT_SKIP_ARCS[0]
    arcs = [(INTAKE_AZ0 + w, m0, GROOVE_R0), (m1, INTAKE_AZ1 - w, GROOVE_R0)]
    arcs += [(a0, a1, GROOVE_R0_EXH) for a0, a1 in EXHAUST_ARCS]
    return arcs
def vent_cutter(az):
    """one obround opening through the outer wall (r 83 to beyond the edge), with its 0.3 x 45 mouth chamfer as a taper on the outer face"""
    zc = VENT_Z0 + VENT_H/2
    body = Pos(PLATE_R + 0.5, 0, 0) * extrude(Plane.YZ * SlotOverall(VENT_H, VENT_W, rotation=90), -(PLATE_R + 0.5 - (RING_WALL_R0 - 1.0)))
    mouth = Pos(PLATE_R + 0.01, 0, 0) * extrude(Plane.YZ * SlotOverall(VENT_H + 2*VENT_CHAMFER, VENT_W + 2*VENT_CHAMFER, rotation=90), -VENT_CHAMFER, taper=45)
    return Pos(0, 0, zc) * Rot(0, 0, az) * (body + mouth)
def ring_groove():
    """the underside groove behind the openings: the intake arcs r 79.5-84 (interrupted over the carriage hole), the exhaust arcs
    r 76.5-84, z 0-6.55, walls between; a Ø9 land left standing round each of the structure's three plate screws"""
    g = None
    for a0, a1, r0 in groove_arcs():
        s = sector(a0, a1, GROOVE_R1, -1, GROOVE_Z1) - cyl(r0, -2, GROOVE_Z1 + 1)
        g = s if g is None else g + s
    for az in PLATE_SCREW_AZ:
        g -= zbore(PILLAR_LAND_D, -2, GROOVE_Z1 + 1, az, PILLAR_R)
    return g
def rim_ring():
    """the stainless ring (v15): 120 obround openings through its outer wall into an underside groove (the pad closes it), the
    undercut under the outer wall into the same groove, the passages in its inner land, the notch and open groove top under the
    blower's hood, 0.3 chamfers (no reeding: Ryan, 7 Sep), the flange onto the core, the fixing holes, the bond screw's hole, the hood's two taps"""
    p = cyl(PLATE_R, 0, PLATE_T)
    c = PLATE_CHAMFER
    p -= revolve_profile([(PLATE_R, PLATE_T - c), (PLATE_R + 1, PLATE_T - c - 0.01), (PLATE_R + 1, PLATE_T + 0.01), (PLATE_R - c, PLATE_T + 0.01)])   # top outer edge
    p -= cyl(RIM_IN, -1, PLATE_T + 1)
    p += tube(RIM_IN + 0.01, R_CORE_DUCT, RIM_STEP_Z, PLATE_T)                             # the inward flange, in the core's rebate
    p -= ring_groove()
    arcs = [(a0, a1) for a0, a1, r0 in groove_arcs()]
    for a0, a1 in arcs:                                                                  # the undercut: under the outer wall, straight into the groove, over every groove arc
        p -= sector(a0, a1, PLATE_R + 2, -1, INTAKE_UNDERCUT_H) - cyl(RING_WALL_R0 - 0.01, -2, INTAKE_UNDERCUT_H + 1)
        u = INTAKE_UNDERCUT_H
        p -= (revolve_profile([(PLATE_R - c, u - 0.01), (PLATE_R + 1, u - 0.01), (PLATE_R + 1, u + c + 0.01), (PLATE_R, u + c)])
              & sector(a0, a1, PLATE_R + 2, -1, PLATE_T))                                # bottom outer edge chamfer, on the wall's foot
    plain = revolve_profile([(PLATE_R - c, -0.01), (PLATE_R + 1, -0.01), (PLATE_R + 1, c + 0.01), (PLATE_R, c)])
    for a0, a1 in arcs: plain -= sector(a0, a1, 100, -2, 9)
    p -= plain                                                                           # ... and on the plain arcs at z 0
    vents = None
    for az, kind in vent_azs():
        v = vent_cutter(az); vents = v if vents is None else vents + v
    p -= vents
    p -= ring_land_grooves()                                                             # the passages across the inner land
    p -= trench(-1, PLATE_T + 1) & cyl(TRENCH_R1, -2, PLATE_T + 2)                        # v15: the blower's trench: flange notch, inner land cut away, groove top open, between TRENCH_FOOT_AZ out to TRENCH_R1
    p -= port_slot(); p -= carriage_hole()                                            # the carriage's shoe drops through the ring at 90 deg too (r 46-85.5)
    for az in PLATE_SCREW_AZ:                                                           # the structure's plate screws, csk from below (through the Ø9 lands in the groove)
        p -= csk_hole(3.4, 0, PLATE_T, az, PILLAR_R)
    for az in RING_SCREW_AZ:                                                            # the ring screws' countersinks (in the core's shoulder) reach 1.7 past the core's edge into the ring's inner land: the same cone here
        p -= polar(az, RING_SCREW_R, -0.01) * Cone(6.5/2, 3.4/2, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for t in (-PORT_TAB_T, PORT_TAB_T):                                                 # port-face rail: Ø1.6, tapped M2
        p -= zbore(1.6, -1, PLATE_T + 1, 0.0, PORT_TAB_R, t)
    for az in RING_SCREW_AZ:                                                            # M3 tapped in the flange, blind from below
        p -= zbore(2.5, RIM_STEP_Z - 0.1, PLATE_T - 0.6, az, RING_SCREW_R)
    p -= zbore(3.4, RIM_STEP_Z - 1, PLATE_T + 1, RING_BOND_AZ, RING_BOND_R)                # the dedicated bond screw's clearance hole through the flange (GROUNDING 4.1)
    for az in HOOD_SCREW_AZ:                                                            # v15: the hood lid's M2 taps 3 deep in the ring's flange
        p -= zbore(1.6, PLATE_T - 3.0, PLATE_T + 1, az, HOOD_SCREW_R)
    return p
def closing_plate():
    """1 mm aluminium disc closing the duct from below, flush in the core's recess; laser-cut with the same windows.
    v12: four Ø8 lands reach into the Pi window at its holes - the Pi (and the adapter stack on it) is screwed to them from below, M2.5 csk"""
    p = cyl(R_CORE_DUCT - 0.1, 0, CLOSING_T)
    p -= pi_window(); p -= carriage_hole(); p -= port_slot()
    for (x, y) in pi_holes_xy():
        p += box_at(x - 4.75, x + 4.75, y - 4.75, y + 4.75, 0, CLOSING_T)                  # a 9.5 square land: the hole is 3.5 in from the Pi's corner, the window's edge 4.25, so it joins the plate on two sides
        p -= Pos(x, y, -1) * Cylinder(1.35, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        p -= Pos(x, y, -0.01) * Cone(4.7/2, 2.7/2, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))   # csk (DIN 7991 M2.5 head Ø4.7, 0.5 proud below)
    for (x, y) in CLOSING_SCREW_XY: p -= Pos(x, y, -1) * Cylinder(1.4, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return p
def pad():
    """a plain ring under the rim ring (thermal plan: the pad is no longer part of the airflow); v15: no exhaust voids - the exhaust
    leaves through the undercut under the ring's outer wall"""
    p = frustum(PAD_R - 0.5, PAD_R, -PAD_T, 0.0) - cyl(PAD_RIN, -3, 1)
    p -= port_slot(-3, 1)
    p -= blk(20.0, 15.0, -3, 1, 0.0, PLATE_R + 3.0, t=PORT_BARREL_T)     # through-pocket under the barrel plug body
    return p
# ---------------------------------------------------------------- v15: the blower, its saddle and hood, its gaskets and lead
def blower_place():
    return polar(BLOWER_AZ, BLOWER_R, Z_BLOWER0)
def blower_bodies():
    """Delta BFB0305HA-C from its drawing: 30 x 30 x 10, inlet face DOWN (Ø24 opening 1.5 deep drawn as a recess), the outlet on
    the +radial edge (21 x 7 from 1.5 up), two Ø2.4 holes on the diagonal; the impeller is not modelled"""
    P = blower_place()
    b = Box(BLOWER_L, BLOWER_W, BLOWER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= Pos(0, 0, -0.01) * Cylinder(BLOWER_INLET_D/2, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= Pos(BLOWER_L/2 - 1.0, 0, BLOWER_OUTLET_Z0) * Box(2.0, BLOWER_OUTLET_W, BLOWER_OUTLET_H, align=(Align.MIN, Align.CENTER, Align.MIN))
    h = BLOWER_HOLE_PITCH/2
    for (x, y) in ((h, h), (-h, -h)):
        b -= Pos(x, y, -1) * Cylinder(BLOWER_HOLE_D/2, BLOWER_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out = {"blower_BFB0305HA-C": P * b}
    out["blower_inlet_gasket_ASSUMED"] = polar(BLOWER_AZ, BLOWER_R, Z_PLATE_TOP) * (Cylinder(15.0, BLOWER_GASKET_T, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(12.5, 3))
    for i, (x, y) in enumerate(blower_screw_xy()):                                       # M2 x 16 pan heads on the saddle, shanks through the blower into the piers
        out[f"blower_screw_{i}"] = Pos(x, y, Z_BLOWER1 + SADDLE_T) * Cylinder(1.9, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) + Pos(x, y, PLATE_T - BLIND_D + 0.5) * Cylinder(0.95, Z_BLOWER1 + SADDLE_T - (PLATE_T - BLIND_D + 0.5), align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def hood_neck(z0, z1, shrink=0.0):
    """the hood's neck over the blower's outlet: from the blower's outer face (r 66) to r 73.2, HOOD_W wide"""
    r0 = BLOWER_R + BLOWER_L/2 + shrink; r1 = R_CORE_DUCT + 1.0 - shrink
    return blk(r1 - r0, HOOD_W - 2*shrink, z0, z1, BLOWER_AZ, (r0 + r1)/2)
def hood_lid_shape(z0, z1):
    """the lid over the trench's foot: HOOD_LID_AZ, from the rebate (r 72.2) to 1.5 past the trench's end"""
    return sector(HOOD_LID_AZ[0], HOOD_LID_AZ[1], TRENCH_R1 + 1.5, z0, z1) - cyl(R_CORE_DUCT - 0.01, z0 - 1, z1 + 1)
def blower_saddle():
    """printed, one part: the flat plate on the blower's top carrying the motion board on four 0.5 washers (the board's two diagonal screws
    are the blower's own through-bolts), and the hood's neck over the outlet turning the air down into the trench. The lid over the trench's
    foot is a separate flat part (hood_lid) so both print without support"""
    z_top = Z_BLOWER1 + SADDLE_T
    s = polar(BLOWER_AZ, BLOWER_R, Z_BLOWER1) * Box(BLOWER_L, BLOWER_W, SADDLE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))   # flat top: the board sits on four 0.5 washers (PRINT: the flat top is the bed face)
    for (x, y) in blower_screw_xy(): s -= Pos(x, y, Z_BLOWER1 - 1) * Cylinder(1.1, SADDLE_T + 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hood = hood_neck(PLATE_T + BLOWER_GASKET_T, z_top) - hood_neck(PLATE_T - 1, z_top - HOOD_T, HOOD_T)   # the neck's shell (open at the bottom, over the trench, and toward the blower)
    hood -= blower_place() * Box(BLOWER_L + 0.2, BLOWER_W + 0.2, BLOWER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))   # the blower's outlet face opens into it
    # v15 review: a turning vane in the neck's top outer corner - a concave R5.9 sweep from the roof at the blower's face down to the outer wall, so the
    # outlet's horizontal jet is turned downward into the trench instead of hitting a square corner (about 10 Pa saved at 0.5 L/s)
    r_face = BLOWER_R + BLOWER_L/2 + 0.1; r_wall = R_CORE_DUCT + 1.0 - HOOD_T; zc = PLATE_T + 4.3
    vane = blk(r_wall - r_face, HOOD_W - 2*HOOD_T, zc, z_top - HOOD_T + 0.01, BLOWER_AZ, (r_face + r_wall)/2)
    vane -= polar(BLOWER_AZ, r_face, zc) * Rot(90, 0, 0) * Cylinder(z_top - HOOD_T - zc, HOOD_W, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    hood += vane
    return s + hood
def hood_lid():
    """printed, flat: the 2.5 lid over the trench's foot, butting against the neck's outer wall, two M2 into the ring's top; on a gasket"""
    lid = hood_lid_shape(PLATE_T + BLOWER_GASKET_T, PLATE_T + BLOWER_GASKET_T + 2.5)
    lid -= hood_neck(PLATE_T - 1, PLATE_T + 20, -0.15)                                   # clear of the neck's outer wall by 0.15
    for az in HOOD_SCREW_AZ: lid -= zbore(2.2, PLATE_T - 1, PLATE_T + 20, az, HOOD_SCREW_R)
    return lid
def hood_gasket():
    """the foam under the hood's walls and the lid (not over the trench or the neck's cavity)"""
    g = hood_neck(PLATE_T, PLATE_T + BLOWER_GASKET_T) - hood_neck(PLATE_T - 1, PLATE_T + 1, HOOD_T) + hood_lid_shape(PLATE_T, PLATE_T + BLOWER_GASKET_T)
    g -= trench(PLATE_T - 1, PLATE_T + 1)
    for az in HOOD_SCREW_AZ: g -= zbore(2.2, PLATE_T - 1, PLATE_T + 1, az, HOOD_SCREW_R)
    return {"hood_gasket_ASSUMED": g}
def halo_tail_bodies():
    """v15: the LED strip's three-wire tail (5 V, GND, data) at its joint (HALO_TAIL_AZ): out of the strip's back, through the notch in
    the wall's foot, along the plate top just inside the wall to az 71 (round the ring bond screw's head), inward along az 71 to the
    motion board's +t side, up beside the board, and over its edge into the Pico-Lock on its motor-side edge"""
    out = {}
    z0, z1 = Z_PLATE_TOP + 0.9, Z_PLATE_TOP + 0.9 + HALO_TAIL_T
    az2 = 71.0; r_in = 62.0; r_lane = 79.3
    out["halo_tail_1"] = blk(R_STRIP_IN + 0.3 - (r_lane - 1.5), HALO_TAIL_W, z0, z1, HALO_TAIL_AZ, (r_lane - 1.5 + R_STRIP_IN + 0.3)/2)   # from the strip's back through the notch
    out["halo_tail_2"] = blk(HALO_TAIL_W, 2 * r_lane * math.sin(D((az2 - HALO_TAIL_AZ)/2)) + HALO_TAIL_W, z0, z1, (HALO_TAIL_AZ + az2)/2, r_lane)   # along the wall's foot, outside the bond screw's head
    out["halo_tail_3"] = blk(r_lane + 1.5 - r_in, HALO_TAIL_W, z0, z1, az2, (r_in + r_lane + 1.5)/2)                   # inward along az 71
    z_top = Z_MOTION0 + 1.6 + CONN_H
    out["halo_tail_4"] = polar(az2, r_in, z1 - 0.01) * Box(HALO_TAIL_W, HALO_TAIL_T, z_top - z1 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))   # up beside the board's +t side
    x, y = polar(az2, r_in).position.X, polar(az2, r_in).position.Y
    xp = (x - MOTION_R * math.cos(D(MOTION_AZ))) * math.cos(D(MOTION_AZ)) + (y - MOTION_R * math.sin(D(MOTION_AZ))) * math.sin(D(MOTION_AZ))
    tp = -(x - MOTION_R * math.cos(D(MOTION_AZ))) * math.sin(D(MOTION_AZ)) + (y - MOTION_R * math.sin(D(MOTION_AZ))) * math.cos(D(MOTION_AZ))
    out["halo_tail_5"] = polar(MOTION_AZ, MOTION_R, z_top - HALO_TAIL_T) * Pos(xp, (tp + 12.5)/2, 0) * Box(HALO_TAIL_W, tp - 12.5 + 0.7, HALO_TAIL_T, align=(Align.CENTER, Align.CENTER, Align.MIN))   # over the board's edge onto the connector
    return out
def fan_lead_bodies():
    """the blower's two AWG 30 leads, 145 long, drawn as their route to the Pi 5's fan connector (in the vendor STEP: pi_part_13 at the
    board's +y edge between the corner standoff and the USB-A stack): out beside the outlet at the blower's -t corner, down to the plate,
    along the blower's -t face, west over the Pi window's edge, then down onto the connector; a crimped JST SH housing on the end.
    1.4 x 1.4 for the pair. Pi's fan header: JST SH 1.0 mm, 4-way (5 V, GND, PWM, tach); the pair connects 5 V and GND"""
    out = {}
    x0, y0 = rot_xy(0, 0, BLOWER_R + BLOWER_L/2 - 2.0, -BLOWER_W/2 - 1.2, BLOWER_AZ)       # beside the outlet, just off the -t face
    fx, fy = FAN_HEADER_XY
    out["fan_lead_1"] = box_at(x0 - 0.7, x0 + 0.7, y0 - 0.7, y0 + 0.7, Z_PLATE_TOP + 1.5, Z_BLOWER0 + BLOWER_OUTLET_Z0 + 1.0)   # down the blower's corner to the plate
    out["fan_lead_2"] = blk(29.5, 1.4, Z_PLATE_TOP + 1.5, Z_PLATE_TOP + 2.9, BLOWER_AZ, BLOWER_R - 1.25, t=-BLOWER_W/2 - 1.2)   # along the blower's -t face, 1.2 off it, to its inner corner
    xe, ye = rot_xy(0, 0, BLOWER_R - 16.0, -BLOWER_W/2 - 1.2, BLOWER_AZ)                 # (34.6, 17.0)
    out["fan_lead_3"] = box_at(fx - 0.7, xe + 0.7, ye - 0.4, ye + 1.0, Z_PLATE_TOP + 1.5, Z_PLATE_TOP + 2.9)                     # west over the Pi window's +y edge (0.4 off the USB-A stack's top face region, under the window's edge at 18.75)
    out["fan_lead_4"] = box_at(fx - 0.7, fx + 0.7, fy + 3.0, ye + 1.0, Z_PLATE_TOP + 1.5, Z_PLATE_TOP + 2.9)                     # in to the connector, between the corner standoff and the USB-A stack
    out["fan_lead_5"] = box_at(fx - 0.7, fx + 0.7, fy + 3.0, fy + 4.4, PI_Z_TOP + 4.5, Z_PLATE_TOP + 2.9)                        # down to the housing's top
    out["fan_lead_housing_JST_SH_4"] = box_at(fx - 1.5, fx + 1.5, fy - 2.8, fy + 3.0, PI_Z_TOP, PI_Z_TOP + 5.0)   # mated on the Pi's connector (pi_part_13, 3 x 6 with its pin row along y), 0.8 off the corner standoff
    return out
# ---------------------------------------------------------------- the internal structure
def motor_relief(engaged=True):
    rc = MOTOR_R
    k = zbore(MOTOR_BASE_OD + 2.0, Z_MOTOR_BOT - 0.5, Z_BELL_BOT - 0.01, MOTOR_AZ, rc)
    k += zbore(MOTOR_OD + 2 * MOTOR_CLEAR, Z_BELL_BOT - 0.5, Z_MOTOR_TOP + 0.6, MOTOR_AZ, rc)
    # PRINT: the wall and the strip band above the bell's window are opened up to the seat flange, so the window has
    # no roof to bridge (the flange above it is printed on the same support ring as the rest of the flange)
    half = math.sqrt((MOTOR_OD/2 + MOTOR_CLEAR)**2 - (R_WALL_IN - rc)**2)          # half the window's width at the wall's inner face
    k += blk(R_STRIP_BACK + 1.0 - (R_WALL_IN - 1.0), 2 * half, Z_MOTOR_TOP + 0.5, Z_SEAT_BOT + 0.01, MOTOR_AZ, (R_WALL_IN - 1.0 + R_STRIP_BACK + 1.0)/2)
    return k
def slit_azs():
    """vertical vent slits on a 2.5 deg grid, everywhere the wall is plain: not at the motor's relief, the pillars' and
    wheel posts' webs or the LRA pad"""
    out = []
    n = int(round(360.0 / SLIT_PITCH_DEG))
    for i in range(n):
        az = SLIT_PITCH_DEG / 2 + SLIT_PITCH_DEG * i
        def near(a, w): return abs(((az - a + 180) % 360) - 180) <= w
        if near(MOTOR_AZ, 17) or near(LRA_AZ, 6): continue
        if any(near(a, 4) for a in PILLAR_AZ) or any(near(a, 4.5) for a in WHEEL_AZ): continue
        out.append(az)
    return out
port_azs = slit_azs
INSERT_M3_SHORT_L = 4.0
def structure():
    s = tube(R_WALL_OUT, R_WALL_IN, Z_PLATE_TOP, Z_SEAT_TOP)                   # the wall
    s += tube(R_STRIP_BACK, R_WALL_OUT - 0.01, Z_PLATE_TOP, HALO_Z1)           # the band the LED strip is stuck to
    s += tube(R_WALL_OUT, R_SEAT_IN, Z_SEAT_BOT, Z_SEAT_TOP)                   # the seat flange
    s += tube(R_LIP_OUT, R_WALL_OUT - 0.01, Z_LIP0, Z_LIP1)                    # diffuser-retaining lip (over the strip's top edge)
    for az in WHEEL_AZ:                                                        # wheel posts, webbed to the wall
        s += zbore(WHEEL_POST_D, Z_PLATE_TOP - 0.01, Z_POST_TOP, az, BUSH_R)
        s += blk(R_WALL_IN + 0.5 - BUSH_R, 6.0, Z_PLATE_TOP - 0.01, Z_POST_TOP - 2.0, az, (BUSH_R + R_WALL_IN + 0.5)/2)
        # PRINT (v15, inverted): the post's top face (the bush's seat) is the one downward-facing flat left - a Ø8 face 7 mm up, on a small support
    # v15: NOTHING rises above the seat flange's top face - it is the print bed (Ryan, 6 Sep). The encoder's platform is a separate shim;
    # its two M2 inserts sit in Ø5 bosses hanging UNDER the flange, the flange's holes are radial slots +-0.5 for centring over the code ring
    for t in (-4.75, 4.75):
        s += zbore(UNDER_BOSS_D, Z_SEAT_BOT - UNDER_BOSS_H, Z_SEAT_BOT + 0.01, ENC_AZ, ENC_R, t=t)
        s -= zbore(INSERT_M2_D, Z_SEAT_BOT - UNDER_BOSS_H - 1, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L, ENC_AZ, ENC_R, t=t)   # the insert, pressed from below
        s -= blk(2 * ENC_SLOT_RADIAL + 2.2, 2.2, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L - 0.5, Z_SEAT_TOP + 1, ENC_AZ, ENC_R, t=t)   # the slot through the flange above the insert (drawn square-ended)
    # LRA bonding pad on the inside of the wall, and (v14) the clip for its pogo-pin board beside its flex tail
    s += blk(1.3, 11.5, 8.0, 18.0, LRA_AZ, R_WALL_IN - 0.6)
    for t in (-LRA_BOARD_W/2 - 0.75 - 0.4, LRA_BOARD_W/2 + 0.75 + 0.4):                     # two ribs from r 76 to the wall, the board's edges in 0.4 grooves between them
        s += blk(R_WALL_IN + 0.5 - 76.0, 1.5, Z_PLATE_TOP - 0.01, 17.0, LRA_CLIP_AZ, (76.0 + R_WALL_IN + 0.5)/2, t=t)
        s += polar(LRA_CLIP_AZ, 76.0, 17.0 - 0.01) * Pos(0, t, 0) * extrude(Plane.XZ * Polygon((0, 0), (R_WALL_IN + 0.5 - 76.0, 0), (R_WALL_IN + 0.5 - 76.0, R_WALL_IN + 0.5 - 76.0), align=None), 0.75, both=True)   # PRINT (v15): 45 deg on the rib's top
    s -= blk(LRA_BOARD_T + 0.2, LRA_BOARD_W + 0.8, 9.0, 18.0, LRA_CLIP_AZ, LRA_BOARD_R)     # the board's slot (open-topped: it drops in from above)
    # v14/v15: the knob's bleed contact - its foot flat on the flange top, the M2 insert in a boss under the flange (GROUNDING 5)
    s += zbore(UNDER_BOSS_D, Z_SEAT_BOT - UNDER_BOSS_H, Z_SEAT_BOT + 0.01, BLEED_AZ, BLEED_FOOT_R)
    s -= zbore(INSERT_M2_D, Z_SEAT_BOT - UNDER_BOSS_H - 1, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L, BLEED_AZ, BLEED_FOOT_R)
    s -= zbore(2.2, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L - 0.5, Z_SEAT_TOP + 1, BLEED_AZ, BLEED_FOOT_R)
    # three M3 pillars on the wall for the plate screws from below (v12: the deck and its two extra pillars are gone)
    for az in PILLAR_AZ:
        s += zbore(7.0, Z_PLATE_TOP - 0.01, PILLAR_TOP, az, PILLAR_R)
        s += blk(R_WALL_IN + 0.5 - PILLAR_R, 7.0, Z_PLATE_TOP - 0.01, PILLAR_TOP, az, (PILLAR_R + R_WALL_IN + 0.5)/2)
        s += polar(az, PILLAR_R, PILLAR_TOP - 0.01) * Cone(3.5, 0.01, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))   # PRINT (v15, inverted): 45 deg cone on the pillar's top - it prints downward-pointing, no support
        s += polar(az, (PILLAR_R + R_WALL_IN + 0.5)/2, PILLAR_TOP - 0.01) * Rot(0, 0, 0) * extrude(Plane.XZ * Polygon((-(R_WALL_IN + 0.5 - PILLAR_R)/2, 0), ((R_WALL_IN + 0.5 - PILLAR_R)/2, 0), ((R_WALL_IN + 0.5 - PILLAR_R)/2, 3.5), align=None), 3.5, both=True)   # ... and a 45 deg web up the wall side
        s -= zbore(INSERT_M3_D, Z_PLATE_TOP - 1, Z_PLATE_TOP + INSERT_M3_SHORT_L + 0.3, az, PILLAR_R)
        s -= polar(az, PILLAR_R, Z_PLATE_TOP + INSERT_M3_SHORT_L + 0.29) * Cone(INSERT_M3_D/2, 0.01, INSERT_M3_D/2, align=(Align.CENTER, Align.CENTER, Align.MIN))   # PRINT: 45 deg roof on the blind hole
    # cuts
    s -= motor_relief()
    for az in WHEEL_AZ:
        s -= zbore(BUSH_D + 0.1, Z_PLATE_TOP - 1, Z_POST_TOP + 1, az, BUSH_R)
        s -= blk(6.0, WHEEL_OD + 2.0, Z_POST_TOP - 0.3, Z_SEAT_TOP + 1, az, R_WALL_OUT)   # open-topped window: the wheel reaches through the wall into the groove; no bridge to print
        s -= blk(R_WALL_IN + 1.0 - (R_SEAT_IN - 1.0), WHEEL_OD + 2.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, az, (R_SEAT_IN - 1.0 + R_WALL_IN + 1.0)/2)   # PRINT (Ryan, 5 Sep): the seat flange above the wheel is removed entirely - nothing needs it, and it was a shelf hanging over the window
    for az in NUB_AZ:                                                          # v15: three Ø2 H7 through-holes (reamed) for the dowel pins that locate the glass edge, in Ø5 bosses under the flange
        s += zbore(UNDER_BOSS_D, Z_SEAT_BOT - UNDER_BOSS_H, Z_SEAT_BOT + 0.01, az, PANEL_DISC_R + 0.15 + 1.0)
        s -= zbore(PIN_D, Z_SEAT_BOT - UNDER_BOSS_H - 1, Z_SEAT_TOP + 1, az, PANEL_DISC_R + 0.15 + 1.0)
    s -= blk(2.5, 32.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, 0.0, 67.5, t=-4.0)     # flex slot through the seat at 0 deg (panel flex at t -12, touch tail at +6)
    s -= blk(R_STRIP_BACK + 0.5 - (R_WALL_IN - 0.5), HALO_TAIL_W + 1.0, Z_PLATE_TOP - 0.1, Z_PLATE_TOP + 3.0, HALO_TAIL_AZ, (R_WALL_IN - 0.5 + R_STRIP_BACK + 0.5)/2)   # v15: the halo tail's notch through the wall's foot and the strip band at the strip's joint
    # PRINT (v15, inverted): 0.3 chamfers on the bed face's two circular edges against elephant's foot
    s -= revolve_profile([(R_SEAT_IN - 0.01, Z_SEAT_TOP + 0.01), (R_SEAT_IN + 0.3, Z_SEAT_TOP + 0.01), (R_SEAT_IN - 0.01, Z_SEAT_TOP - 0.3)])
    s -= revolve_profile([(R_WALL_OUT + 0.01, Z_SEAT_TOP + 0.01), (R_WALL_OUT - 0.3, Z_SEAT_TOP + 0.01), (R_WALL_OUT + 0.01, Z_SEAT_TOP - 0.3)])
    s -= blk(6.0, 32.0, Z_SEAT_TOP - 0.6, Z_SEAT_TOP + 1, 0.0, 65.0, t=-4.0)   # the flex passes over the seat's top face here, 0.6 deep
    slits = None
    for az in slit_azs():
        b = blk(R_WALL_OUT - R_WALL_IN + 2.0, SLIT_W, SLIT_Z0, SLIT_Z1, az, (R_WALL_IN + R_WALL_OUT)/2)
        slits = b if slits is None else slits + b
    s -= slits
    # (the wall's foot used to be relieved 1.6 over the port slot for an older port face; the face and its ear arms now stay
    #  at or below the plate top and inboard of the wall, so the foot is continuous - PRINT: no 56 mm bridge at the first layers)
    return s
def internal_structure():
    return structure()
def locating_pins():
    """v15: three ISO 8734 Ø2 m6 x 12 dowel pins pressed from below, top 0.3 under the glass's top face, under the lens overhang"""
    out = {}
    for i, az in enumerate(NUB_AZ):
        out[f"locating_pin_{i}"] = zbore(PIN_D, Z_GLASS1 - 0.3 - PIN_L, Z_GLASS1 - 0.3, az, PANEL_DISC_R + 0.15 + 1.0)
    return out
def encoder_shim():
    """v15: the encoder's platform as a separate printed shim, 8.4 x 12.4 x ENC_BOSS_H, two M2 clearance holes; printed as a family
    (ENC_SHIM_FAMILY) so the optical gap is set on the bench"""
    b = blk(8.4, 12.4, Z_SEAT_TOP, ENC_BOARD_Z0, ENC_AZ, ENC_R)
    for t in (-4.75, 4.75): b -= zbore(2.2, Z_SEAT_TOP - 1, ENC_BOARD_Z0 + 1, ENC_AZ, ENC_R, t=t)
    return b

# ---------------------------------------------------------------- the display bonds straight onto the seat (double-sided foam tape, ASSUMED 0.5)
def bond_tape():
    return tube(PANEL_DISC_R - 0.5, R_SEAT_IN + 0.5, Z_SEAT_TOP, Z_GLASS0) - blk(6.0, 32.0, Z_SEAT_TOP - 1, Z_GLASS0 + 1, 0.0, 65.0, t=-4.0)   # one ring; it simply spans the three wheel notches in the seat

# ---------------------------------------------------------------- diffuser, LED ring
def halo_diffuser():
    c = DIFF_CHAMFER
    lean = (R_DIFF_OUT_TOP - R_DIFF_OUT_BOT) / HALO_H
    return revolve_profile([(R_DIFF_IN, HALO_Z0), (R_DIFF_OUT_BOT, HALO_Z0),
                            (R_DIFF_OUT_TOP - c * lean, HALO_Z1 - c), (R_DIFF_OUT_TOP - c, HALO_Z1), (R_DIFF_IN, HALO_Z1)])
def led_strip():
    """the bought strip as one envelope: a ring r 73.3-74.9, 5 wide, stuck to the wall's band, firing outward"""
    return {"led_strip_ENVELOPE": tube(R_STRIP_OUT, R_STRIP_IN, Z_PLATE_TOP + 0.25, Z_PLATE_TOP + 0.25 + LED_STRIP_W)}

# ---------------------------------------------------------------- wheels
def wheel_collar(az=None):
    h = WHEEL_W
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline((WHEEL_OD/2 - WHEEL_V_H, 0), (WHEEL_OD/2, h/2 - WHEEL_V_FLAT/2),
                         (WHEEL_OD/2, h/2 + WHEEL_V_FLAT/2), (WHEEL_OD/2 - WHEEL_V_H, h), (5.0, h), (5.0, 0), close=True)
            make_face()
        revolve(axis=Axis.Z)
    p = bp.part
    if az is None: return p
    return polar(az, WHEEL_AXIS_R, Z_WHEEL0) * p
def ecc_bush(az=None, retracted=False):
    e = -WHEEL_ECC if retracted else WHEEL_ECC
    b = Cylinder(BUSH_FLANGE_D/2, BUSH_FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b += Pos(0, 0, -6.0) * Cylinder(BUSH_D/2, 6.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b += Pos(e, 0, BUSH_FLANGE_T) * Cylinder(WHEEL_BORE/2 - 0.02, WHEEL_W, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= Pos(0, 0, -6.1) * Cylinder(BUSH_HEX/2 * 1.1, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if az is None: return b
    return polar(az, BUSH_R, Z_POST_TOP) * b
def bearing_bodies(az):
    return bodies_of("623ZZ_bearing_3x10x4.step", polar(az, WHEEL_AXIS_R, Z_WHEEL0), prefix=f"bearing{az}_")

# ---------------------------------------------------------------- motor, carriage, clutch (servo on the plate, short tab)
def motor_place(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, Z_MOTOR_BOT)
TAB_X = -(MOTOR_OD/2 + 1.0 + 0.8 + CARRIAGE_TAB_T/2)           # tab centre, carriage frame (inboard = -x local)
def carriage(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    c = cyl(MOTOR_OD/2 + 1.0, 0, CARRIAGE_T)
    c += tube(MOTOR_OD/2 + 1.0, MOTOR_OD/2 + 0.3, CARRIAGE_T - 0.01, CARRIAGE_T + 0.6)
    c -= Pos(0, 0, -0.01) * Box(12.4, 12.4, 3.3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= cyl(4.5, 3.0, CARRIAGE_T + 2)
    c += Pos(TAB_X, 0, 0) * Box(CARRIAGE_TAB_T, CARRIAGE_TAB_W, CARRIAGE_TAB_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))   # the tall push tab
    c += Pos(TAB_X - CARRIAGE_TAB_T/2, 0, 0) * Box(CARRIAGE_TAB_T/2 + 3.5, CARRIAGE_TAB_W, CARRIAGE_T, align=(Align.MIN, Align.CENTER, Align.MIN))   # tab root (reaches the shoe)
    c -= Pos(-(MOTOR_OD/2 + 1.0) - 1, 0, 0.8) * Box(8.0, 2.4, 2.2, align=(Align.MIN, Align.CENTER, Align.MIN))   # v14: notch through the shoe's inboard wall for the sensor board's lead (SYSTEM-REVIEW 6.2)
    return polar(MOTOR_AZ, MOTOR_R - dr, 0.0) * c
def commutation_board(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, 0.0) * Box(12.0, 12.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
def mt6701_bodies(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return bodies_of("MT6701CT-STD_SOP8.step", polar(MOTOR_AZ, MOTOR_R - dr, 1.6), prefix="mt6701_")
def magnet_body(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return bodies_of("MT6701_diametric_magnet_D6x2p5.step", polar(MOTOR_AZ, MOTOR_R - dr, Z_MOTOR_BOT), prefix="motor_")
def motor_bodies(engaged=True):
    return bodies_of(MOTOR_FILE, motor_place(engaged), prefix="motor_")
def band(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, 0) * tube(MOTOR_OD/2 + MOTOR_BAND_T, MOTOR_OD/2 + 0.01, Z_DRIVE0, Z_DRIVE1)
TAB_INNER_R = MOTOR_R + TAB_X - CARRIAGE_TAB_T/2            # 32.7 the tab's inner face, engaged
SERVO_R0 = TAB_INNER_R - 3.0 - SERVO_L                      # body end 3 mm short of the tab: the pushrod bridges it
Z_SERVO0 = Z_PLATE_TOP + SERVO_TRAY_T                       # 8.0: the servo lies straight on the plate (v12)
def servo_place():
    return polar(MOTOR_AZ, SERVO_R0, Z_SERVO0)
def servo_bodies():
    return bodies_of("AGFRC_C1p5CLS_PRO_linear_servo.step", servo_place(), prefix="servo_")
def servo_mount():
    """v12: a FRAME round the servo on the plate top - no floor; two side walls, an inner end wall, open toward the tab; two ears
    with M2.5 screws into the web.  The servo sits on the plate (8.0-14.0), the frame to 14.5."""
    L = SERVO_L + 1.5
    m = Box(L, SERVO_W + 2.0, SERVO_H + 0.5, align=(Align.MIN, Align.CENTER, Align.MIN))
    m -= Pos(1.5, 0, -0.01) * Box(L, SERVO_W + 0.4, SERVO_H + 1.0, align=(Align.MIN, Align.CENTER, Align.MIN))
    m -= Pos(-0.1, 0, 1.0) * Box(1.8, 6.0, 4.0, align=(Align.MIN, Align.CENTER, Align.MIN))          # lead notch in the end wall
    for sy in (-SERVO_EAR_T, SERVO_EAR_T):
        m += Pos(L/2, sy, 0) * Cylinder(3.5, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        m += Pos(L/2, sy/2, 0) * Box(7.0, abs(sy), 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        m -= Pos(L/2, sy, -1) * Cylinder(1.4, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    m = Pos(-1.5, 0, 0) * m
    return polar(MOTOR_AZ, SERVO_R0, Z_PLATE_TOP) * m

# ---------------------------------------------------------------- speaker
def speaker_place():
    return Pos(SPEAKER_CENTRE[0], SPEAKER_CENTRE[1], Z_PLATE_TOP)
def speaker_bodies():
    return bodies_of("Soberton_SP-4005-1_speaker_D40.step", speaker_place(), keep=lambda l: "keepout" not in l, prefix="")
def speaker_cradle():
    """ring under the speaker's flange (flange at 4.45-5.95 above its rear face), three snap fingers over it, two ears (M2.5 from
    above into the web).  Fingers and ears at device azimuths from the speaker's centre (SPEAKER_FINGER_AZ / SPEAKER_EAR_AZ)."""
    c = tube(20.5, 18.3, 0, 4.45)
    for a in SPEAKER_FINGER_AZ:
        c += Rot(0, 0, a) * (Pos(20.9, 0, 0) * Box(2.6, 3.0, 7.24, align=(Align.CENTER, Align.CENTER, Align.MIN))
                             + Pos(19.75, 0, 6.05) * Box(1.0, 3.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for a in SPEAKER_EAR_AZ:
        c += Rot(0, 0, a) * (Pos(22.5, 0, 0) * Cylinder(3.5, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
                             + Pos(20.5, 0, 0) * Box(5.0, 6.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        c -= Rot(0, 0, a) * Pos(22.5, 0, -1) * Cylinder(1.4, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return speaker_place() * c

# ---------------------------------------------------------------- the boards (v12: all on the plate; the adapter on the Pi's standoffs)
def board_on_plate(x, y, L, W, T=1.6, az=0.0):
    return Pos(x, y, Z_PLATE_TOP + BOARD_STANDOFF) * Rot(0, 0, az) * Box(L, W, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
def adapter_board():
    b = Pos(ADAPTER_CENTRE[0], ADAPTER_CENTRE[1], Z_ADAPTER0) * Box(ADAPTER_L, ADAPTER_W, ADAPTER_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in pi_holes_xy(): b -= Pos(x, y, Z_ADAPTER0 - 1) * Cylinder(1.4, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b
def adapter_parts():
    """DM-ADTTR-014 parts from its drawing (heights: HDMI PUBLISHED 7.3, the rest ASSUMED)"""
    out = {}
    x0, y0 = ADAPTER_X0, ADAPTER_Y0; zt = Z_ADAPTER1; xm = x0 + ADAPTER_L/2
    out["adapter_hdmi_socket"] = box_at(xm + 0.5 - ADAPTER_HDMI_W/2, xm + 0.5 + ADAPTER_HDMI_W/2, y0 - 0.8, y0 - 0.8 + ADAPTER_HDMI_D, zt, zt + ADAPTER_HDMI_H)
    out["adapter_microusb"] = box_at(xm + 0.5 + 20.25 - 2.75, xm + 0.5 + 20.25 + 2.75, y0, y0 + 5.7, zt, zt + 3.0)
    xc1 = xm + 1.8
    out["adapter_flex_connector"] = box_at(xc1 - ADAPTER_CN1_W/2, xc1 + ADAPTER_CN1_W/2, y0 + ADAPTER_W - 1.2 - ADAPTER_CN1_D, y0 + ADAPTER_W - 1.2, zt, zt + ADAPTER_CN1_H)
    for i, yb in enumerate((y0 + 24.0, y0 + 32.0)):
        out[f"adapter_button_{i}"] = box_at(x0 + 0.2, x0 + 3.8, yb, yb + 6.0, zt, zt + 4.1)
    out["adapter_parts_ENVELOPE"] = box_at(x0 + 8, x0 + ADAPTER_L - 8, y0 + 13, y0 + ADAPTER_W - 12, zt, zt + ADAPTER_PARTS_H)   # keeps 3 clear of the four corner screws
    out["adapter_underside_ENVELOPE"] = box_at(x0 + 6, x0 + ADAPTER_L - 6, y0 + 6, y0 + 48.0, Z_ADAPTER0 - ADAPTER_UNDER_H, Z_ADAPTER0)   # stops short of the Pi header strip (the crimp housing there reaches 14.3)
    for i, (x, y) in enumerate(pi_holes_xy()):                                 # M2.5 x 5 pan-head screws into the standoffs' tops (heads 2.0)
        out[f"adapter_screw_{i}"] = Pos(x, y, zt) * Cylinder(2.25, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # touch controller stacked on the adapter's top (ASSUMED)
    cx, cy = TOUCH_CENTRE; zs = zt + TOUCH_STACK_H
    out["touch_board_ASSUMED"] = box_at(cx - TOUCH_L/2, cx + TOUCH_L/2, cy - TOUCH_W/2, cy + TOUCH_W/2, zs, zs + 1.6)
    out["touch_parts_ENVELOPE"] = box_at(cx - 12, cx + 12, cy - 7, cy + 7, zs + 1.6, zs + 1.6 + 1.4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            out[f"touch_standoff_{sx}{sy}"] = Pos(cx + sx * (TOUCH_L/2 - 3), cy + sy * (TOUCH_W/2 - 3), zt) * Cylinder(2.0, TOUCH_STACK_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def connect_board():
    """the display connect board on its bracket (r 47-77 at 0 deg)"""
    b = Pos(CB_R, CB_T0, Z_CB0) * Box(CB_L, CB_W, CB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in cb_holes_xy(): b -= Pos(x, y, Z_CB0 - 1) * Cylinder(1.2, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b
def cb_holes_xy():
    return [(CB_R - CB_L/2 + 3.0, CB_T0 + sy * (CB_W/2 - 3.0)) for sy in (-1, 1)] + [(CB_R + CB_L/2 - 5.5, CB_T0 + sy * (CB_W/2 - 3.0)) for sy in (-1, 1)]
def connect_board_parts():
    out = {}
    zt = Z_CB0 + CB_T; xo = CB_R + CB_L/2; xi = CB_R - CB_L/2
    out["cb_cn2_panel_flex"] = box_at(xo - CB_CN2_D, xo, -12.0 - CB_CN2_W/2, -12.0 + CB_CN2_W/2, zt, zt + CB_CN2_H)
    out["cb_cn1_cable"] = box_at(xi, xi + CB_CN1_D, CB_T0 - CB_CN1_W/2, CB_T0 + CB_CN1_W/2, zt, zt + CB_CN1_H)
    for i, (x, y) in enumerate(cb_holes_xy()):
        out[f"cb_screw_{i}"] = Pos(x, y, zt) * Cylinder(1.9, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))   # M2 x 4 pan heads
    return out
def connect_bracket():
    """printed: a 1.5 slab at z 9.5-11 from r 46 to 78 over the port slot, resting on the port face's rail (z 9.5, r 75.7+) at its
    outer end and on a 1.5 foot strip (r 46-48) plus two csk ears at its inner end; four 2.0 bosses with M2 inserts for the board"""
    z0 = Z_PLATE_TOP + CB_FOOT; z1 = z0 + CB_BRACKET_T
    clip = box_at(40, 90, CB_T0 - CB_W/2 - 2.0, CB_T0 + CB_W/2 + 2.0, 0, 20)
    b = tube(CB_R + CB_L/2 + 2.5, CB_R - CB_L/2 + 0.5, z0, z1) & clip                                     # the slab, r 46-78
    b += tube(CB_R - CB_L/2 + 2.5, CB_R - CB_L/2 + 0.5, Z_PLATE_TOP, z0 + 0.01) & clip                    # the foot strip on the plate, r 46-48
    for (x, y) in cb_holes_xy():
        b += Pos(x, y, z1 - 0.01) * Cylinder(3.0, CB_BOSS_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
        b -= Pos(x, y, z1 + CB_BOSS_H - INSERT_M2_L) * Cylinder(INSERT_M2_D/2, INSERT_M2_L + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in CB_SCREW_XY:                                                                            # ears on the plate, csk from above
        b += Pos(x, y, Z_PLATE_TOP) * Cylinder(3.5, z1 - Z_PLATE_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))
        b -= Pos(x, y, Z_PLATE_TOP - 1) * Cylinder(1.4, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
        b -= Pos(x, y, z1 - 1.0) * Cone(1.4, 2.7, 1.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= blk(3.0, 6.0, Z_PLATE_TOP - 1, z1 + 1, 0.0, PORT_TAB_R, t=-PORT_TAB_T)                            # clear of the rail's M2 screw head at t -26
    b -= box_at(0, 46.0, PI_Y0 + 22.0, PI_Y0 + 36.0, 0, Z_PLATE_TOP + CB_FOOT + 0.01)                       # v15: the foot strip is notched over the audio's USB-A plug (x to 45, z to 9.3); the slab above it stands clear
    return b
def cable_bodies():
    """the 150 x 30.6 flat cable from the connect board's CN1 to the adapter's flex connector (ASSUMED route, about 95 mm of it;
    the rest is slack).  Legs: inward at the bracket level; up beside the Pi's USB-A stacks; over them at 19.5; a 45 deg fold to
    run toward 90 deg over the servo; a double 45 deg fold (Z-fold) that brings it back toward 270, sideways by its width, down onto the connector."""
    out = {}
    hw = CABLE_W/2; T = CABLE_T
    xi = CB_R - CB_L/2                                    # 47: CN1's inner face
    z1 = Z_CB0 + CB_T + CB_CN1_H/2                        # 13.7 leaving CN1
    x_up = PI_X0 + PI_L + PI_OVERHANG + 3.5               # 39.5: rises here, beside the USB-A shells (the audio's USB plug is 0.2 to its side)
    z2 = Z_PI_USBA_TOP + 0.5                              # 19.5 over the shells
    out["cable_1"] = box_at(x_up, xi, CB_T0 - hw, CB_T0 + hw, z1 - T, z1)
    out["cable_2"] = box_at(x_up - T, x_up, CB_T0 - hw, CB_T0 + hw, z1 - T, z2 + T)
    xf = ADAPTER_X0 + ADAPTER_L/2 + 1.8 + hw              # 13.6: the 45 deg fold's centre so the next leg is centred on the adapter's connector + one width
    out["cable_3"] = box_at(xf, x_up, CB_T0 - hw, CB_T0 + hw, z2, z2 + T)
    yc = PI_Y0 + ADAPTER_W - 1.2 - ADAPTER_CN1_D/2        # 22.55: the connector's centre y
    y_top = 43.0
    out["cable_4"] = box_at(xf - hw, xf + hw, CB_T0 - hw, y_top, z2 + T, z2 + 2*T)          # toward 90 deg, one width to the right of the connector
    out["cable_5"] = box_at(xf - hw - CABLE_W, xf + hw, y_top - 3.0, y_top, z2 + 2*T, z2 + 4*T)   # the Z-fold's three layers
    xc = xf - CABLE_W                                     # -17: over the connector (its centre -17.7)
    out["cable_6"] = box_at(xc - hw, xc + hw, yc + 4.0, y_top - 3.0, z2 + 3*T, z2 + 4*T)   # back toward 270
    zc = Z_ADAPTER1 + ADAPTER_CN1_H/2
    out["cable_7"] = box_at(xc - hw, xc + hw, yc + 4.0 - T, yc + 4.0, zc, z2 + 4*T)         # down to the connector
    out["cable_8"] = box_at(xc - hw, xc + hw, yc - 1.0, yc + 4.0, zc - T, zc)              # into it
    return out
def audio_board():
    return board_on_plate(AUDIO_CENTRE[0], AUDIO_CENTRE[1], AUDIO_L, AUDIO_W)
def audio_parts():
    zt = Z_PLATE_TOP + BOARD_STANDOFF + 1.6; P = Pos(AUDIO_CENTRE[0], AUDIO_CENTRE[1], zt)
    out = {"audio_parts_ENVELOPE": P * Pos(-6, 0, 0) * Box(20.0, AUDIO_W - 6, CONN_H, align=(Align.CENTER, Align.CENTER, Align.MIN)),            # Pico-Lock right-angle connectors on its edges, 2.0 mated
           "audio_usb_plug_ENVELOPE": P * Pos(AUDIO_L/2 - 5.0, -6.0, 0) * Box(10.0, 8.0, USB_PLUG_H, align=(Align.CENTER, Align.CENTER, Align.MIN))}   # the moulded plug of its pre-made USB lead, 4.0
    out.update(bodies_of("ESS_ES9219Q_WQFN40_5x5.step", P * Pos(12, 6, 0), prefix="es9219q_"))
    return out
def motion_board():
    """v15: on the blower's saddle (z 20.0-21.6), holes at +-12 (two of them on the blower's through-bolts)"""
    b = polar(MOTION_AZ, MOTION_R, Z_MOTION0) * Box(MOTION_L, MOTION_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):
        for sy in (-1, 1):
            b -= polar(MOTION_AZ, MOTION_R, Z_MOTION0 - 1) * Pos(sx * MOTION_HOLE_OFF, sy * MOTION_HOLE_OFF, 0) * Cylinder(1.1, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b
def motion_parts():
    zt = Z_MOTION0 + 1.6; P = polar(MOTION_AZ, MOTION_R, zt)
    out = {}
    out.update(bodies_of("TMC6300-LA-T_QFN20_3x3.step", P * Pos(6, 5, 0), prefix="tmc6300_"))
    out.update(bodies_of("TI_DRV2605L_VSSOP10_DGS.step", P * Pos(6, -5, 0), prefix="drv2605l_"))
    out["motion_connectors_ENVELOPE"] = P * Pos(0, 11, 0) * Box(24.0, 5.0, CONN_H, align=(Align.CENTER, Align.CENTER, Align.MIN))   # v15: Pico-Lock right-angle on the +t edge (the motor's side now), 2.0 mated
    out["motion_usb_plug_ENVELOPE"] = polar(MOTION_AZ, MOTION_R, Z_MOTION0 - 2.0) * Pos(-MOTION_L/2 - 4.0, 0, 0) * Box(8.0, 10.0, USB_PLUG_H, align=(Align.CENTER, Align.CENTER, Align.MIN))   # v15: its pre-made USB lead's moulded plug beyond the INNER edge, straddling the board's plane (z 18-22)
    return out
def converter_body():
    """the 12 V -> 5 V module on the PLATE (thermal plan rule 15), on a 0.5 gap pad, tangential in the front crescent"""
    return {"converter_ENVELOPE": polar(CONV_AZ, CONV_R, Z_PLATE_TOP + CONV_PAD_T) * Box(CONV_W, CONV_L, CONV_H, align=(Align.CENTER, Align.CENTER, Align.MIN)),
            "converter_gap_pad_ASSUMED": polar(CONV_AZ, CONV_R, Z_PLATE_TOP) * Box(CONV_W, CONV_L, CONV_PAD_T, align=(Align.CENTER, Align.CENTER, Align.MIN))}
def washer_bodies():
    """the 1.0 washers under the audio board and (v15) the 0.5 washers under the motion board on the saddle (ASSUMED nylon)"""
    out = {}
    pts = [(AUDIO_CENTRE[0] + sx * (AUDIO_L/2 - 3.5), AUDIO_CENTRE[1] + sy * (AUDIO_W/2 - 3.5)) for sx in (-1, 1) for sy in (-1, 1)]
    for i, (x, y) in enumerate(pts):
        out[f"board_washer_{i}"] = Pos(x, y, Z_PLATE_TOP) * (Cylinder(2.5, BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.35, 5))
    for i, (sx, sy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
        x, y = rot_xy(0, 0, MOTION_R + sx * MOTION_HOLE_OFF, sy * MOTION_HOLE_OFF, MOTION_AZ)
        out[f"motion_washer_{i}"] = Pos(x, y, Z_BLOWER1 + SADDLE_T) * (Cylinder(2.5, 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.1, 5))
    return out

# ---------------------------------------------------------------- encoder, LRA
def encoder_board():
    """8 (radial) x 12 (tangential) x 1.0, flat on its boss on the seat flange, sensor centred, two M2 holes at t +-4.75"""
    b = blk(8.0, 12.0, ENC_BOARD_Z0, ENC_BOARD_Z0 + ENC_BOARD_T, ENC_AZ, ENC_R)
    for t in (-4.75, 4.75): b -= zbore(2.2, ENC_BOARD_Z0 - 1, ENC_BOARD_Z0 + 2, ENC_AZ, ENC_R, t=t)
    return b
def encoder_bodies():
    """AEDR-8300 face UP (its optical axis +z), long axis tangential = the direction the code ring moves; plus its two M2 x 4 pan heads"""
    place = polar(ENC_AZ, ENC_R, ENC_BOARD_Z0 + ENC_BOARD_T) * Rot(0, 0, 90)
    out = bodies_of("Broadcom_AEDR-8300-1K2_encoder.step", place, prefix="encoder_")
    for i, t in enumerate((-4.75, 4.75)):
        out[f"encoder_screw_{i}"] = polar(ENC_AZ, ENC_R, ENC_BOARD_Z0 + ENC_BOARD_T) * Pos(0, t, 0) * Cylinder(1.9, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
LRA_CLIP_AZ = 252.5                                  # the LRA's flex tail (pads at r 79.6-80, x -25.3..-21.4) sits at this azimuth
LRA_BOARD_R = 77.0                                   # the pogo board's centre radius: pins from 77.5 to 79.7, on the pads
def lra_bodies():
    place = polar(LRA_AZ, R_WALL_IN - 1.2 - 0.07, 13.0) * Rot(0, -90, 0)
    return bodies_of("Vybronics_VLV101040A_LRA.step", place, prefix="lra_")


# ---------------------------------------------------------------- v14: grounding features and the two homeless items
def lra_contact_bodies():
    """SYSTEM-REVIEW 6.1: the vibration actuator must not be soldered - a 7 x 8 x 1 board (ASSUMED) in a printed clip beside the
    LRA's flex tail, two pogo pins (ASSUMED Ø1.5, 2.2 compressed) on the tail's two pads at z 11.75 and 14.35"""
    out = {}
    out["lra_pogo_board_ASSUMED"] = blk(LRA_BOARD_T, LRA_BOARD_W, 9.0, 9.0 + LRA_BOARD_H, LRA_CLIP_AZ, LRA_BOARD_R)
    for i, z in enumerate((11.75, 14.35)):
        out[f"lra_pogo_pin_{i}"] = rbore(LRA_POGO_D, LRA_BOARD_R + LRA_BOARD_T/2 - 0.01, LRA_BOARD_R + LRA_BOARD_T/2 + LRA_POGO_L, LRA_CLIP_AZ, z)
    return out
def bleed_bodies():
    """GROUNDING 5: a phosphor-bronze leaf (ASSUMED 4 wide, 0.2 thick) screwed to its boss on the seat flange at 200 deg, rising to bear
    on the crown's underside at r 71.5 with a small dome; wired to the chassis bond through 1 MOhm (the resistor is in the lead)"""
    out = {}
    z0 = Z_SEAT_TOP                                                                                  # v15: the foot flat on the flange top (no boss)
    out["knob_bleed_leaf_ASSUMED"] = (blk(4.0, 4.0, z0, z0 + 0.2, BLEED_AZ, BLEED_FOOT_R)                                     # the foot under the screw
                                     + blk(1.2, 4.0, z0 + 0.2, Z_CROWN_BOT - 0.2, BLEED_AZ, BLEED_R + 0.6)                       # the arm (drawn upright; really inclined)
                                     + polar(BLEED_AZ, BLEED_R, Z_CROWN_BOT - 0.2) * Cylinder(0.75, 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))   # the dome, touching the crown
    out["knob_bleed_screw"] = polar(BLEED_AZ, BLEED_FOOT_R, z0 + 0.2) * Cylinder(1.9, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))   # M2 x 4 pan head over a ring terminal
    return out
def bond_bodies():
    """GROUNDING 3.1 and 4.1: the chassis bond (M3 pan head, external-tooth star washer, ring terminal) on the plate top beside the
    power inlet; the rim ring's dedicated bond screw through its flange into the core's shoulder, star washer under the head"""
    out = {}
    x, y = GND_BOND_XY
    out["chassis_bond_star_washer"] = Pos(x, y, Z_PLATE_TOP) * (Cylinder(3.5, 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.7, 3))
    out["chassis_bond_ring_terminal"] = Pos(x, y, Z_PLATE_TOP + 0.6) * (Cylinder(3.5, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.7, 3)) + box_at(x + 3.0, x + 11.0, y - 2.0, y + 2.0, Z_PLATE_TOP + 0.6, Z_PLATE_TOP + 1.4)
    out["chassis_bond_screw"] = Pos(x, y, Z_PLATE_TOP + 1.4) * Cylinder(2.75, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out["ring_bond_star_washer"] = polar(RING_BOND_AZ, RING_BOND_R, PLATE_T) * (Cylinder(3.5, 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.7, 3))
    out["ring_bond_screw"] = polar(RING_BOND_AZ, RING_BOND_R, PLATE_T + 0.6) * Cylinder(2.75, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)) + polar(RING_BOND_AZ, RING_BOND_R, RIM_STEP_Z - 2.8) * Cylinder(1.45, PLATE_T + 0.6 - RIM_STEP_Z + 2.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def wire_bodies():
    """GROUNDING 6 and 5: the USB-C receptacle's shell wire to the chassis bond (Ø1.3, drawn as its route: up out of the port slot
    beside the USB-C board, along under the connect bracket's slab to the slot's edge, to the terminal); the motor frame's bond
    wire to the motion board's ground (SYSTEM-REVIEW: a floating frame switching at 20 ns edges beside the encoder)"""
    out = {}
    x, y = GND_BOND_XY
    out["usbc_shell_wire_1"] = box_at(67.35, 68.65, -4.65, -3.35, 3.4, 9.4)                        # up beside the USB-C board, in the slot
    out["usbc_shell_wire_2"] = box_at(67.35, 68.65, -4.65, 22.0, 8.1, 9.4)                          # along under the bracket's slab to its edge
    out["usbc_shell_wire_3"] = box_at(x + 11.0, 68.65, 22.0, 23.3, 8.1, 9.4)                        # across to the terminal's tab
    out["usbc_shell_wire_4"] = box_at(x + 11.0, x + 12.3, 22.0, y - 1.0, 8.1, 9.4)
    # motor frame bond: a ring terminal under the motor's inboard base screw, the lead inward over the carriage, up, and across to the motion board
    out["motor_bond_wire_1"] = box_at(-0.65, 0.65, 45.5, 50.8, Z_MOTOR_BOT + 0.8, Z_MOTOR_BOT + 2.1)
    out["motor_bond_wire_2"] = box_at(-0.65, 0.65, 45.5, 46.8, Z_MOTOR_BOT + 0.8, Z_PLATE_TOP + 4.6)
    out["motor_bond_wire_3"] = box_at(-0.65, 9.3, 45.5, 46.8, Z_PLATE_TOP + 3.3, Z_PLATE_TOP + 4.6)      # across to x 8 (short of the blower's corner at x 11)
    out["motor_bond_wire_4"] = box_at(8.0, 9.3, 45.5, 46.8, Z_PLATE_TOP + 3.3, Z_MOTION0 + 3.0)       # v15: up beside the blower to the raised motion board
    out["motor_bond_wire_5"] = box_at(8.0, 16.5, 43.5, 44.8, Z_MOTION0 + 1.7, Z_MOTION0 + 3.0)        # across onto the board's +t edge connector
    return out
def sensor_cable_bodies():
    """SYSTEM-REVIEW 6.2: the rotor sensor's lead leaves the carriage's pocket through a notch beside the tab, rises through the plate's
    tab slot, and makes a 12 mm service loop over the servo's frame before dropping to the motion board - flex-rated, 2.4 mm of travel"""
    out = {}
    xc = -6.0                                                                                            # t +6.0: beside the tab (t +-5), inside the servo frame's wall (t 7.6)
    out["sensor_cable_1"] = box_at(xc - 0.75, xc + 0.75, 38.75, 40.25, 1.0, Z_PLATE_TOP + 7.5)                 # up through the notch beside the tab slot
    out["sensor_cable_2"] = box_at(xc - 0.75, xc + 0.75, 38.75, 40.25 + SENSOR_CABLE_LOOP/2, Z_PLATE_TOP + 7.5, Z_PLATE_TOP + 9.5)   # the loop's outward leg over the servo frame (14.5)
    out["sensor_cable_3"] = box_at(xc - 0.75, 10.0, 32.0, 46.5, Z_PLATE_TOP + 8.5, Z_PLATE_TOP + 9.5)             # over toward the motion board (drawn as a slab: the loop and the run), stopping short of the blower's corner (x 11)
    out["sensor_cable_4"] = box_at(8.5, 10.0, 40.0, 41.5, Z_PLATE_TOP + 9.5, Z_MOTION0 + 3.0)                     # v15: up beside the blower to the raised board
    out["sensor_cable_5"] = box_at(8.5, 16.0, 40.0, 41.5, Z_MOTION0 + 1.6, Z_MOTION0 + 3.0)                       # onto the board's +t edge connector
    return out

# ---------------------------------------------------------------- rear port module: face + barrel + USB-C + jack + light sensor
def port_face():
    f = blk(PORT_FACE_T, PORT_W, -PAD_T, Z_PLATE_TOP, 0.0, PORT_FACE_R0 + PORT_FACE_T/2)
    f += blk(3.5, 12.0, USBC_AXIS_Z - 1.1 - 1.6 - 1.5, USBC_AXIS_Z - 1.1 - 1.6, 0.0, PORT_FACE_R0 - 1.75, t=PORT_USBC_T)   # shelf under the USB-C board
    f += blk(4.5, 10.0, -PAD_T, 0.0, 0.0, PORT_FACE_R0 - 2.25, t=PORT_LIGHT_T)          # foot for the light-sensor board
    f -= blk(1.3, 6.4, -PAD_T - 1, 0.6, 0.0, PORT_FACE_R0 - 3.5, t=PORT_LIGHT_T)
    # a rail along the face's top, 1.5 tall on the plate top, reaching 4 mm past the slot on each side: two M2 screws into the plate
    rail_w = 2 * PORT_TAB_T + 6.0
    xo = PORT_FACE_R0 + PORT_FACE_T                                                  # the face's outer plane (at the wall's inner face)
    ri = R_WALL_IN - 0.3                                                             # nothing above z 8 may reach the wall
    rail = tube(ri, PORT_TAB_R - 2.5, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 1.5) & box_at(60.0, 90.0, -rail_w/2, rail_w/2, Z_PLATE_TOP - 1, Z_PLATE_TOP + 2)
    rail += box_at(PORT_FACE_R0, xo, -PORT_W/2, PORT_W/2, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 1.5) & cyl(ri, Z_PLATE_TOP - 1, Z_PLATE_TOP + 2)   # joins the rail to the face's top
    f += rail                                                                          # PRINT: face-down, the rail's curved front is a 1.5 mm ledge 0.3-5.7 above the bed (small overhang, accepted)
    for t in (-PORT_TAB_T, PORT_TAB_T):
        f -= zbore(2.2, Z_PLATE_TOP - 1, Z_PLATE_TOP + 3, 0.0, PORT_TAB_R, t=t)
    f -= blk(PORT_FACE_T + 2, 9.6, USBC_AXIS_Z - USBC_BELOW - 0.3, USBC_AXIS_Z + USBC_ABOVE + 0.3 + 1.6, 0.0, PORT_FACE_R0 + PORT_FACE_T/2, t=PORT_USBC_T)
    f -= rbore(6.3, PORT_FACE_R0 - 1, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, JACK_AXIS_Z, t=PORT_JACK_T)
    f -= rbore(6.2, PORT_FACE_R0 - 1, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, BARREL_AXIS_Z, t=PORT_BARREL_T)   # barrel nose Ø5.5
    f -= rbore(SENSOR_HOLE_D, PORT_FACE_R0 - 1, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, 4.0, t=PORT_LIGHT_T)
    return f
USBC_BOARD_Z0 = USBC_AXIS_Z - 1.1 - 1.6
def usbc_board():
    b = blk(11.0, 12.0, USBC_BOARD_Z0, USBC_BOARD_Z0 + 1.6, 0.0, PORT_FACE_R0 - 5.5, t=PORT_USBC_T)
    b -= blk(6.3, 9.3, USBC_BOARD_Z0 - 1, USBC_BOARD_Z0 + 3, 0.0, PORT_FACE_R0 - 3.1, t=PORT_USBC_T)
    return b
def usbc_bodies():
    place = polar(0.0, PORT_FACE_R0, USBC_BOARD_Z0 + 1.6) * Pos(0, PORT_USBC_T, 0)
    return bodies_of("GCT_USB4520-03-0-A_usbc_midmount.step", place, keep=lambda l: "cutout" not in l, prefix="usbc_")
JACK_BOARD_Z0 = JACK_AXIS_Z - JACK_AXIS_ABOVE_BOARD - 1.6        # board under the jack: -0.1 to 1.5
def jack_board():
    return blk(16.0, 12.0, JACK_BOARD_Z0, JACK_BOARD_Z0 + 1.6, 0.0, PORT_FACE_R0 - 8.0, t=PORT_JACK_T + 0.5)   # 16 x 12, just the jack's footprint: between the USB-C shelf and the light-sensor foot
def jack_bodies():
    place = polar(0.0, PORT_FACE_R0, JACK_BOARD_Z0 + 1.6) * Pos(0, PORT_JACK_T, 0) * Rot(0, 0, 180)
    return bodies_of("Switchcraft_35RAPC4BH3_jack_3p5mm.step", place, prefix="jack_")
def barrel_board():
    """vertical board (tangential plane) carrying the right-angle jack, so the barrel axis height is free"""
    return blk(1.6, 14.0, -1.0, 8.0, 0.0, PORT_FACE_R0 + 1.0 - 13.2 - 0.8, t=PORT_BARREL_T)          # its outer face against the jack body's inner end
def barrel_bodies():
    """CUI PJ-063AH: 24 V 8 A, 2.0 mm pin (PUBLISHED); body 14.4 x 9.0 x 11.0 ASSUMED, bushing to the face"""
    r1 = PORT_FACE_R0 + PORT_FACE_T
    body = blk(13.2, 11.0, BARREL_AXIS_Z - 4.5, BARREL_AXIS_Z + 4.5, 0.0, PORT_FACE_R0 + 1.0 - 13.2/2, t=PORT_BARREL_T)   # body ends 1.0 into the face (the bushing sits in the face's hole)
    return {"barrel_jack_ENVELOPE": body}
def light_board():
    return blk(1.0, 6.0, -1.4, 6.5, 0.0, PORT_FACE_R0 - 3.5, t=PORT_LIGHT_T)
def light_bodies():
    place = polar(0.0, PORT_FACE_R0 - 3.0, 4.0) * Pos(0, PORT_LIGHT_T, 0) * Rot(0, 90, 0)
    return bodies_of("Vishay_VEML7700-TR_ambient_light_sensor.step", place, prefix="veml7700_")
def plug_envelopes():
    out = {}
    r0 = PORT_FACE_R0 + PORT_FACE_T
    out["barrel_plug_ENVELOPE"] = rbore(8.5, r0 + 0.5, r0 + 14.0, 0.0, BARREL_AXIS_Z, t=PORT_BARREL_T)     # right-angle plug body, then the cable turns sideways
    out["barrel_plug_ENVELOPE_cable"] = blk(8.5, 22.0, BARREL_AXIS_Z - 4.25, BARREL_AXIS_Z + 4.25, 0.0, r0 + 14.0 - 4.25, t=PORT_BARREL_T - 11.0)
    out["usbc_plug_ENVELOPE"] = blk(25.0, 8.3, USBC_AXIS_Z - 3.25, USBC_AXIS_Z + 3.25, 0.0, r0 + 0.5 + 12.5, t=PORT_USBC_T)
    out["jack_plug_ENVELOPE"] = rbore(6.0, r0 + 0.5, r0 + 30.0, 0.0, JACK_AXIS_Z, t=PORT_JACK_T)
    return out

# ---------------------------------------------------------------- assembly
def made_parts(knurl=None, engaged=True):
    m = {"base_plate": base_plate(), "rim_ring_STEEL": rim_ring(), "closing_plate_AL": closing_plate(), "internal_structure": internal_structure(),
         "halo_diffuser": halo_diffuser(), "knob_body": knob_body(knurl),
         "carriage": carriage(engaged), "servo_mount": servo_mount(), "connect_bracket": connect_bracket(),
         "speaker_cradle": speaker_cradle(), "port_face": port_face(),
         "adapter_board": adapter_board(), "connect_board": connect_board(), "audio_board": audio_board(), "motion_board": motion_board(),
         "encoder_board": encoder_board(), "encoder_shim": encoder_shim(), "blower_saddle": blower_saddle(), "hood_lid": hood_lid(), "usbc_board": usbc_board(), "jack_board": jack_board(), "barrel_board": barrel_board(),
         "light_board": light_board(), "commutation_board": commutation_board(engaged), "bond_tape": bond_tape()}
    for i, az in enumerate(WHEEL_AZ):
        m[f"collar_{i}"] = wheel_collar(az)
        m[f"bush_{i}"] = ecc_bush(az)
    return m
def bought_parts(engaged=True):
    b = {}
    b.update(panel_bodies()); b.update(flex_bodies())
    b.update(pi_bodies()); b.update(cooler_bodies()); b.update(pi_plug_bodies()); b.update(pi_stack_bodies())
    b.update(motor_bodies(engaged)); b["motor_band"] = band(engaged)
    b.update(magnet_body(engaged)); b.update(mt6701_bodies(engaged))
    b.update(servo_bodies())
    for az in WHEEL_AZ: b.update(bearing_bodies(az))
    b.update(speaker_bodies()); b.update(encoder_bodies()); b.update(lra_bodies())
    b.update(adapter_parts()); b.update(connect_board_parts()); b.update(cable_bodies()); b.update(audio_parts()); b.update(motion_parts()); b.update(converter_body()); b.update(washer_bodies())
    b.update(usbc_bodies()); b.update(jack_bodies()); b.update(barrel_bodies()); b.update(light_bodies())
    b.update(led_strip()); b.update(plug_envelopes())
    b.update(lra_contact_bodies()); b.update(bleed_bodies()); b.update(bond_bodies()); b.update(wire_bodies()); b.update(sensor_cable_bodies())
    b.update(blower_bodies()); b.update(hood_gasket()); b.update(fan_lead_bodies()); b.update(halo_tail_bodies()); b.update(locating_pins()); b.update(closing_gasket())
    b["pad"] = pad()
    return b
