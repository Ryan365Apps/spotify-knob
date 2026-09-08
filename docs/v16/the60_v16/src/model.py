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
def csk_hole(d, z0, z1, az, r, head_d=CSK_M25_HEAD_D, head_h=CSK_M25_HEAD_H):
    """countersunk from the underside (z0)"""
    h = zbore(d, z0 - 1, z1 + 1, az, r)
    h += polar(az, r, z0 - 0.01) * Cone(head_d/2, d/2, head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return h
def csk_xy(d, x, y, z0, z1, head_d=CSK_M25_HEAD_D, head_h=CSK_M25_HEAD_H):
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
    # v16: no USB-C plug on the Pi (it is powered through its header; its USB-C carries no data)
    # HDMI ribbon: up-angle micro-HDMI plug (ASSUMED 12 x 8 x 5) in HDMI1; the ribbon rises beside it to z 16.4 (over the plate boards, under the
    # A plug's body), runs outward, rises again and comes back into the adapter's HDMI-A socket, which faces the same way (270 deg). A end plug ASSUMED 21 x 12 x 6.
    zp0 = PI_Z_TOP
    out["hdmi_plug_micro_ENVELOPE"] = box_at(HDMI_X - 6, HDMI_X + 6, PI_Y0 - 8.0, PI_Y0 + 0.5, zp0, zp0 + 5.0)
    yr = PI_Y0 - 8.3                                      # where it rises, just outside the micro plug
    xa = ADAPTER_X0 + ADAPTER_L/2 + 0.5                   # the HDMI-A socket's centre x (0.5 off the board's middle)
    z_a = Z_ADAPTER1 + ADAPTER_HDMI_H/2                   # the socket's axis height
    y_far = PI_Y0 - 0.8 - 21.0 - 3.5                      # 3.5 beyond the A plug's tail
    z_run = z_a - 3.0 - 0.6                               # 16.4: the outward run, 0.3 under the A plug's body (v15 ran on the plate top at z 9; the boards are there now)
    out["hdmi_ribbon_1"] = box_at(HDMI_X - 10, HDMI_X + 10, yr - 0.3, yr, zp0 + 5.0, z_run + 0.3)                     # up out of the micro plug
    out["hdmi_ribbon_2"] = box_at(HDMI_X - 10, HDMI_X + 10, y_far, yr, z_run, z_run + 0.3)                              # outward over the boards
    out["hdmi_ribbon_3"] = box_at(xa - 10, HDMI_X + 10, y_far - 0.3, y_far, z_run, z_a + 0.3)                            # up beyond the A plug's tail, shifting across to it
    out["hdmi_ribbon_4"] = box_at(xa - 10, xa + 10, y_far, y_far + 3.5 + 0.5, z_a, z_a + 0.3)                           # into the A plug's tail
    out["hdmi_plug_A_ENVELOPE"] = box_at(xa - 6.0, xa + 6.0, PI_Y0 - 0.8 - 21.0, PI_Y0 - 0.8, z_a - 3.0, z_a + 3.0)   # in the socket, body outward
    # header housing: 2 x 5 crimp housing on pins 1-10 (5 V, GND, UART) - ASSUMED 12.7 x 5.1 x 9 on the header's base. v16: the Pi's 5 V comes in here
    hx0, hx1, hy0, hy1, hh = PI_HEADER
    out["header_housing_ENVELOPE"] = pi_place() * box_at(hx0, hx0 + 12.7, hy0, hy1, PI_T + 2.5, PI_T + 2.5 + 9.0)
    # audio board's USB: right-angle USB-A plug in the LOWER socket of the USB 3.0 stack. ASSUMED 9 protrusion x 12 x 6.8
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
    """v16: the bore carries a male V-ridge (90 deg flanks, RIDGE_CREST_W flat) standing on a BORE_RELIEF band, where the three V-groove bearings run"""
    rb, rk, ri = R_BORE, R_KNOB, R_CROWN_IN
    zs, zt, zcb = Z_SKIRT_BOT, Z_KNOB_TOP, Z_CROWN_BOT
    zr = zcb + STRIP_T                                                     # v13: the code ring's recess in the crown's underside (nothing on the bore)
    rr, rc, hc = R_RELIEF, R_CREST, RIDGE_CREST_W / 2
    return [(rb, zs), (rk - CH_BOT, zs), (rk, zs + CH_BOT),
            (rk, zt - CH_TOP), (rk - CH_TOP, zt),
            (ri + CH_IN, zt), (ri, zt - CH_IN),
            (ri, zcb), (CODE_R0, zcb), (CODE_R0, zr), (CODE_R1, zr), (CODE_R1, zcb), (rb, zcb),
            (rb, Z_RELIEF1), (rr, Z_RELIEF1), (rr, Z_RIDGE1), (rc, Z_RIDGE_MID + hc), (rc, Z_RIDGE_MID - hc), (rr, Z_RIDGE0), (rr, Z_RELIEF0), (rb, Z_RELIEF0)]
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
    # v16: no notch for a USB-C plug head - the Pi is powered through its header and its USB-C carries no data; only the receptacle's own body (1.6 beyond the board edge)
    w += box_at(USBC_XC - 5.5 - m, USBC_XC + 5.5 + m, PI_Y0 - 2.5 - m, PI_Y0 + 1, z0, z1)
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
    for (x, y) in CLOSING_SCREW_XY + stud_xy():
        b = Pos(x, y, 0) * Cylinder(3.5, PLATE_T, align=(Align.CENTER, Align.CENTER, Align.MIN)); k = b if k is None else k + b
    return k
def island_links():
    """v15: where a closing-screw island sits in a channel band it blocks the channel(s) under it - a cross-cut either side
    (ISLAND_LINK_L from the island's edge, the width of three channels) joins the blocked channel to its neighbours"""
    ys = channel_ys(); k = None
    for (x, y) in CLOSING_SCREW_XY + stud_xy():
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
        if any(abs(az - k) < 0.1 for k in INTAKE_SKIP_AZ): continue
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
    """every M2.5 screw into the plate's top face (v16: the printed parts only - servo frame (2), connect bracket (2), speaker cradle (2);
    every BOARD is on countersunk M2 studs from below, stud_xy())"""
    out = []
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
    """v16: the die-cut gasket is two pieces - the ring round the duct's outer wall with the bands round the port slot and the carriage hole, and the band round the Pi window"""
    sol = sorted(gasket_groove().solids(), key=lambda q: -q.volume)
    out = {"closing_gasket_ASSUMED": sol[0]}
    for i, q in enumerate(sol[1:]): out[f"closing_gasket_window_ASSUMED_{i}"] = q
    return out
def base_plate():
    """the aluminium core: r < 75.2, 8 tall; rebate for the ring's flange; recess for the closing plate; the duct (2 web / 5 duct / 1 plate);
    the passages as closed tunnels; the blower's inlet hole and discharge trench; piers; the gasket groove; the boards' stud holes (v16: no ribs)"""
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
    for az in RING_SCREW_AZ:                                                            # M2.5 csk from below through the shoulder into the ring's flange
        p -= csk_hole(CSK_M25_D, 0, RIM_STEP_Z, az, RING_SCREW_R)
    p -= zbore(TAP_M25_D, RIM_STEP_Z - 3.0, RIM_STEP_Z + 0.1, RING_BOND_AZ, RING_BOND_R)   # the ring's bond screw, M2.5 tapped 3.0 into the shoulder from its top face (GROUNDING 4.1)
    for (x, y) in top_screw_xy():                                                       # everything bolted to the plate top: M2.5 tapped, blind, 3.5 into web + pier
        p -= Pos(x, y, PLATE_T - BLIND_D) * Cylinder(1.0, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in blower_screw_xy():                                                    # the blower's two M2 into piers
        p -= Pos(x, y, PLATE_T - BLIND_D) * Cylinder(0.8, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(GND_BOND_XY[0], GND_BOND_XY[1], PLATE_T - BLIND_D) * Cylinder(TAP_M25_D/2, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))   # chassis ground: M2.5 tapped blind into its pier
    for (x, y) in stud_xy():                                                            # v16: the boards' M2 studs pass up through full-depth islands (Ø2.2 clearance)
        p -= Pos(x, y, -1) * Cylinder(STUD_HOLE_D/2, PLATE_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return p                                                                            # (v16: no ribs)
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
    blower's hood, 0.3 chamfers (no reeding: Ryan, 7 Sep), the flange onto the core, the fixing holes, the bond screw's hole, the hood's two taps;
    v16: the diffuser's rebate and the 2.0-proud shelf under it (HALO-OPTICS)"""
    p = cyl(PLATE_R, 0, PLATE_T)
    c = PLATE_CHAMFER
    # v16 (HALO-OPTICS): the opal ring's seat - a 0.5 rebate in the top from R_REBATE outward, and a thin shelf standing 2.0 proud of the wall (r to 94.7, z 6.7-7.5)
    p -= tube(PLATE_R + 1, R_REBATE, Z_DIFF0, PLATE_T + 1)
    p += tube(PLATE_R_SHELF, PLATE_R - 0.01, Z_SHELF0, Z_DIFF0)
    cs = 0.2
    p -= revolve_profile([(PLATE_R_SHELF, Z_DIFF0 - cs), (PLATE_R_SHELF + 1, Z_DIFF0 - cs - 0.01), (PLATE_R_SHELF + 1, Z_DIFF0 + 0.01), (PLATE_R_SHELF - cs, Z_DIFF0 + 0.01)])   # the shelf's top outer edge, 0.2 polished
    p -= revolve_profile([(PLATE_R_SHELF - cs, Z_SHELF0 - 0.01), (PLATE_R_SHELF + 1, Z_SHELF0 - 0.01), (PLATE_R_SHELF + 1, Z_SHELF0 + cs + 0.01), (PLATE_R_SHELF, Z_SHELF0 + cs)])   # ... and its bottom outer edge
    p -= revolve_profile([(R_REBATE - c, PLATE_T + 0.01), (R_REBATE + 0.01, PLATE_T + 0.01), (R_REBATE + 0.01, PLATE_T - c)])   # the rebate's top inner edge, 0.3 polished (the edge the liner meets)
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
        p -= csk_hole(CSK_M25_D, 0, PLATE_T, az, PILLAR_R)
    for az in RING_SCREW_AZ:                                                            # the ring screws' countersinks (in the core's shoulder) reach 0.85 past the core's edge into the ring's inner land: the same cone here
        p -= polar(az, RING_SCREW_R, -0.01) * Cone(CSK_M25_HEAD_D/2, CSK_M25_D/2, CSK_M25_HEAD_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for t in (-PORT_TAB_T, PORT_TAB_T):                                                 # port-face rail: Ø1.6, tapped M2
        p -= zbore(1.6, -1, PLATE_T + 1, 0.0, PORT_TAB_R, t)
    for az in RING_SCREW_AZ:                                                            # M2.5 tapped in the flange, blind from below
        p -= zbore(TAP_M25_D, RIM_STEP_Z - 0.1, PLATE_T - 0.6, az, RING_SCREW_R)
    p -= zbore(2.8, RIM_STEP_Z - 1, PLATE_T + 1, RING_BOND_AZ, RING_BOND_R)                # the dedicated bond screw's Ø2.8 clearance hole through the flange (GROUNDING 4.1)
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
    for (x, y) in stud_xy():                                                                  # v16: the boards' M2 csk studs: Ø2.2 through, the countersink in the underside (head 0.2 proud)
        p -= Pos(x, y, -1) * Cylinder(STUD_HOLE_D/2, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
        p -= Pos(x, y, -0.01) * Cone(1.76, STUD_D/2, CLOSING_T + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
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
    s = polar(BLOWER_AZ, BLOWER_R, Z_BLOWER1) * Box(BLOWER_L, BLOWER_W, SADDLE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))   # flat top: the board sits on four 0.5 washers (v16: no board on it - the saddle is a plain clamp plate over the blower with the hood; PRINT: the flat top is the bed face)
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
    """v16: the strip's three-wire tail (5 V, GND, data) at its joint (HALO_TAIL_AZ 325): out of the strip's back through the notch in the wall's foot,
    inward along the plate top, then across onto the level shifter's edge beside it. A second two-wire feed (5 V, GND from the converter) enters
    the channel at HALO_FEED2_AZ for the strip's far end"""
    out = {}
    z0, z1 = Z_PLATE_TOP + 0.9, Z_PLATE_TOP + 0.9 + HALO_TAIL_T
    az = HALO_TAIL_AZ
    lx, ly = LS_R * math.cos(D(LS_AZ)), LS_R * math.sin(D(LS_AZ))
    r_turn = LS_R + LS_W/2 + 2.5
    out["halo_tail_1"] = blk(R_STRIP_IN + 0.3 - r_turn, HALO_TAIL_W, z0, z1, az, (r_turn + R_STRIP_IN + 0.3)/2)      # through the notch, inward along the plate
    x0, y0 = r_turn * math.cos(D(az)), r_turn * math.sin(D(az))
    zt = Z_PLATE_TOP + SPACER_H + LS_T
    L = math.hypot(lx - x0, ly - y0); a = math.degrees(math.atan2(ly - y0, lx - x0))
    out["halo_tail_2"] = Pos(x0, y0, z0) * Cylinder(HALO_TAIL_W/2, zt + 1.0 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))   # up beside the board's edge
    out["halo_tail_3"] = Pos((x0 + lx)/2, (y0 + ly)/2, zt + 1.0 - HALO_TAIL_T/2) * Rot(0, 0, a) * Box(L, HALO_TAIL_W, HALO_TAIL_T)   # across onto the level shifter's header
    z2 = Z_PLATE_TOP + 0.9 + HALO_TAIL_T
    r_lane = R_WALL_IN - 2.0
    out["halo_feed2_1"] = blk(R_STRIP_IN + 0.3 - (r_lane - 1.5), 2.0, z0, z2, HALO_FEED2_AZ, (r_lane - 1.5 + R_STRIP_IN + 0.3)/2)   # the far-end 5 V feed: through its notch
    out["halo_feed2_2"] = blk(2.0, 2 * r_lane * math.sin(D((HALO_FEED2_AZ - CONV_AZ)/2)) + 2.0, z0, z2, (HALO_FEED2_AZ + CONV_AZ)/2, r_lane)   # along the wall's foot to the converter's azimuth
    out["halo_feed2_3"] = blk(r_lane + 1.0 - (CONV_R + CONV_W/2 + 0.5), 2.0, z0, z2, CONV_AZ, (CONV_R + CONV_W/2 + 0.5 + r_lane + 1.0)/2)   # in to the converter's outer edge
    return out
def halo_tail_az():
    return HALO_TAIL_AZ
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
def wall_solid():
    """v16: the wall as a solid of revolution - r 84.8-86.4 from the plate to z 13.8, a 50 deg ramp inward to r 82.8-84.4 at 16.2, then up to the seat top"""
    return revolve_profile([(R_WALL_IN, Z_PLATE_TOP), (R_WALL_OUT, Z_PLATE_TOP), (R_WALL_OUT, Z_RAMP0), (R_WALL_OUT_UP, Z_RAMP1), (R_WALL_OUT_UP, Z_SEAT_TOP),
                            (R_WALL_IN_UP, Z_SEAT_TOP), (R_WALL_IN_UP, Z_RAMP1), (R_WALL_IN, Z_RAMP0)])
def wall_inside(eps=0.02):
    """everything inside the wall's outer face: webs, pads and ribs that reach the wall are trimmed with it so nothing pokes out through the ramp"""
    return revolve_profile([(1.0, Z_PLATE_TOP - 1), (R_WALL_OUT - eps, Z_PLATE_TOP - 1), (R_WALL_OUT - eps, Z_RAMP0), (R_WALL_OUT_UP - eps, Z_RAMP1),
                            (R_WALL_OUT_UP - eps, Z_SEAT_TOP + 1), (1.0, Z_SEAT_TOP + 1)])
def motor_relief(engaged=True):
    rc = MOTOR_R
    k = zbore(MOTOR_BASE_OD + 2.0, Z_MOTOR_BOT - 0.5, Z_BELL_BOT - 0.01, MOTOR_AZ, rc)
    k += zbore(MOTOR_OD + 2 * MOTOR_CLEAR, Z_BELL_BOT - 0.5, Z_COLLAR0 - 0.3, MOTOR_AZ, rc)                        # the bell's window, 1.0 clear
    k += zbore(DRIVE_COLLAR_OD + 2 * MOTOR_BAND_T + 2 * 2.0, Z_COLLAR0 - 0.3, Z_MOTOR_TOP + 0.6, MOTOR_AZ, rc)       # the collar and band's window, 2.0 clear
    # PRINT: the wall above the collar's window is opened up to the seat flange, so the window has no roof to bridge (the flange above it
    # is printed on the same bed as the rest of the flange)
    half = math.sqrt((DRIVE_COLLAR_OD/2 + MOTOR_BAND_T + 2.0)**2 - (R_WALL_IN_UP - rc)**2)          # half the window's width at the upper wall's inner face
    k += blk(R_WALL_OUT + 1.0 - (R_WALL_IN_UP - 1.0), 2 * half, Z_MOTOR_TOP + 0.5, Z_SEAT_BOT + 0.01, MOTOR_AZ, (R_WALL_IN_UP - 1.0 + R_WALL_OUT + 1.0)/2)
    k &= cyl(R_WALL_OUT + 0.01, 0, 40)                                                                     # nothing outside the wall's outer face: the ledge and lip stay whole
    return k
def slit_azs():
    """vertical vent slits on a 2.5 deg grid, everywhere the wall is plain: not at the motor's relief, the pillars' and
    wheel posts' webs, the block's channel or the LRA pad"""
    out = []
    n = int(round(360.0 / SLIT_PITCH_DEG))
    for i in range(n):
        az = SLIT_PITCH_DEG / 2 + SLIT_PITCH_DEG * i
        def near(a, w): return abs(((az - a + 180) % 360) - 180) <= w
        if near(MOTOR_AZ, 17) or near(LRA_AZ, 6): continue
        if any(near(a, 4) for a in PILLAR_AZ) or any(near(a, 6.0) for a in WHEEL_AZ): continue
        out.append(az)
    return out
port_azs = slit_azs
CHANNEL_HALF = BLOCK_W/2 + CHANNEL_CLEAR                       # 4.2: half the channel's clear width
CHANNEL_OUT_HALF = CHANNEL_HALF + CHANNEL_WALL_T                # 6.2: to the outside of its walls
def block_channel():
    """v16: the sprung wheel's channel at 270 deg, part of the structure: two side walls and an inner end wall standing on the plate, a roof
    with the axle pin's slot; open at the outer end into the wall's window. Printed inverted: the roof is a downward face in print - it is
    only 8.4 wide (a bridge); the walls print up from it"""
    az = WHEEL_SPRUNG_AZ
    r0, r1 = CHANNEL_END_R0, R_WALL_IN + 0.4
    c = None
    for t in (-CHANNEL_HALF - CHANNEL_WALL_T/2, CHANNEL_HALF + CHANNEL_WALL_T/2):
        b = blk(r1 - r0, CHANNEL_WALL_T, Z_PLATE_TOP - 0.01, Z_ROOF1, az, (r0 + r1)/2, t=t); c = b if c is None else c + b
    c += blk(r1 - r0, 2 * CHANNEL_OUT_HALF, Z_ROOF0, Z_ROOF1, az, (r0 + r1)/2)                          # the roof
    c += blk(2.0, 2 * CHANNEL_OUT_HALF, Z_PLATE_TOP - 0.01, Z_ROOF1, az, r0 + 1.0)                        # the inner end wall (the spring's abutment)
    c -= rbore(2.4, r0 - 1, r0 + 3.1, az, RELEASE_SCREW_Z)                                                # the release screw through it
    slot_r0 = WHEEL_AXIS_R - BLOCK_TRAVEL_IN - WHEEL_PIN_D/2 - 0.1; slot_r1 = WHEEL_AXIS_R + BLOCK_TRAVEL_OUT + WHEEL_PIN_D/2 + 0.1
    c -= blk(slot_r1 - slot_r0, WHEEL_PIN_D + 0.2, Z_ROOF0 - 1, Z_ROOF1 + 1, az, (slot_r0 + slot_r1)/2)   # the pin's slot in the roof (also cuts the wall's ramp above it)
    return c
def structure():
    s = wall_solid()                                                                    # the wall (two radii, ramp between)
    s += tube(R_WALL_OUT_UP, R_SEAT_IN, Z_SEAT_BOT, Z_SEAT_TOP)                        # the seat flange
    # v16 halo (HALO-OPTICS): the strip's ledge under the lip - the strip hangs face down from its underside (z 12.0-13.2), the lip clamps the
    # diffuser's top face through a 0.3 gasket. PRINT (inverted): the ledge and lip are one 6.3-wide ring hanging outward at z 13.2-14.3 - SUPPORTS
    s += tube(R_LEDGE_OUT, R_WALL_OUT_UP + 0.5, Z_LEDGE0, Z_LIP1)
    s += tube(R_LIP_OUT, R_LEDGE_OUT - 0.01, Z_LIP0, Z_LIP1)
    for az in WHEEL_FIXED_AZ:                                                          # the two fixed wheel posts, Ø8 to z 19.0, webbed to the wall
        s += zbore(WHEEL_POST_D, Z_PLATE_TOP - 0.01, Z_POST_TOP, az, WHEEL_AXIS_R)
        s += blk(R_WALL_IN + 0.5 - WHEEL_AXIS_R, 6.0, Z_PLATE_TOP - 0.01, Z_POST_TOP - 2.0, az, (WHEEL_AXIS_R + R_WALL_IN + 0.5)/2) & wall_inside()
        # PRINT (inverted): the post's top face (the washer's seat) is a downward-facing Ø8 flat 7 mm up, on a small support (as v15)
    s += block_channel()                                                               # the sprung wheel's channel at 270
    # v15: NOTHING rises above the seat flange's top face - it is the print bed (Ryan, 6 Sep). The encoder's platform is a separate shim;
    # its two M2 inserts sit in Ø5 bosses hanging UNDER the flange, the flange's holes are radial slots +-0.5 for centring over the code ring
    for t in (-4.75, 4.75):
        s += zbore(UNDER_BOSS_D, Z_SEAT_BOT - UNDER_BOSS_H, Z_SEAT_BOT + 0.01, ENC_AZ, ENC_R, t=t)
        s -= zbore(INSERT_M2_D, Z_SEAT_BOT - UNDER_BOSS_H - 1, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L, ENC_AZ, ENC_R, t=t)   # the insert, pressed from below
        s -= blk(2 * ENC_SLOT_RADIAL + 2.2, 2.2, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L - 0.5, Z_SEAT_TOP + 1, ENC_AZ, ENC_R, t=t)   # the slot through the flange above the insert (drawn square-ended)
    # LRA bonding pad on the inside of the wall (v16: a block from the upper wall's inner face down to the plate, fused into the ramp), and the clip for its contact carrier
    s += blk(R_WALL_IN + 0.5 - LRA_PAD_R_IN, 11.5, Z_PLATE_TOP - 0.01, 18.0, LRA_AZ, (LRA_PAD_R_IN + R_WALL_IN + 0.5)/2) & wall_inside()
    for t in (-LRA_BOARD_W/2 - 0.75 - 0.4, LRA_BOARD_W/2 + 0.75 + 0.4):                     # two ribs from the clip's root to the wall, the carrier's edges in 0.4 grooves between them
        s += blk(R_WALL_IN + 0.5 - LRA_CLIP_R0, 1.5, Z_PLATE_TOP - 0.01, 17.0, LRA_CLIP_AZ, (LRA_CLIP_R0 + R_WALL_IN + 0.5)/2, t=t) & wall_inside()
        L = R_WALL_IN + 0.5 - LRA_CLIP_R0; h = Z_SEAT_BOT - 17.0
        s += (polar(LRA_CLIP_AZ, LRA_CLIP_R0, 17.0 - 0.01) * Pos(0, t, 0) * extrude(Plane.XZ * Polygon((0, 0), (L, 0), (L, h), (h, h), align=None), 0.75, both=True)) & wall_inside()   # PRINT: 45 deg on the rib's top, up to the flange's underside (v16: the rib is 10.8 long, so the wedge is cut off at z 24)
    s -= blk(LRA_BOARD_T + 0.2, LRA_BOARD_W + 0.8, 9.0, 18.0, LRA_CLIP_AZ, LRA_BOARD_R)     # the carrier's slot (open-topped: it drops in from above)
    # v14/v15: the knob's bleed contact - its foot flat on the flange top, the M2 insert in a boss under the flange (GROUNDING 5)
    s += zbore(UNDER_BOSS_D, Z_SEAT_BOT - UNDER_BOSS_H, Z_SEAT_BOT + 0.01, BLEED_AZ, BLEED_FOOT_R)
    s -= zbore(INSERT_M2_D, Z_SEAT_BOT - UNDER_BOSS_H - 1, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L, BLEED_AZ, BLEED_FOOT_R)
    s -= zbore(2.2, Z_SEAT_BOT - UNDER_BOSS_H + INSERT_M2_L - 0.5, Z_SEAT_TOP + 1, BLEED_AZ, BLEED_FOOT_R)
    # three M2.5 pillars on the wall for the plate screws from below (v16b: M3 -> M2.5; the Ø7 pillar keeps 1.75 of wall round the Ø3.5 insert)
    for az in PILLAR_AZ:
        s += zbore(7.0, Z_PLATE_TOP - 0.01, PILLAR_TOP, az, PILLAR_R)
        s += blk(R_WALL_IN + 0.5 - PILLAR_R, 7.0, Z_PLATE_TOP - 0.01, PILLAR_TOP, az, (PILLAR_R + R_WALL_IN + 0.5)/2) & wall_inside()
        s += polar(az, PILLAR_R, PILLAR_TOP - 0.01) * Cone(3.5, 0.01, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))   # PRINT (inverted): 45 deg cone on the pillar's top - it prints downward-pointing, no support
        s += (polar(az, (PILLAR_R + R_WALL_IN + 0.5)/2, PILLAR_TOP - 0.01) * extrude(Plane.XZ * Polygon((-(R_WALL_IN + 0.5 - PILLAR_R)/2, 0), ((R_WALL_IN + 0.5 - PILLAR_R)/2, 0), ((R_WALL_IN + 0.5 - PILLAR_R)/2, 3.5), align=None), 3.5, both=True)) & wall_inside()   # ... and a 45 deg web up the wall side
        s -= zbore(INSERT_M25_D, Z_PLATE_TOP - 1, Z_PLATE_TOP + INSERT_M25_L + 0.3, az, PILLAR_R)
        s -= polar(az, PILLAR_R, Z_PLATE_TOP + INSERT_M25_L + 0.29) * Cone(INSERT_M25_D/2, 0.01, INSERT_M25_D/2, align=(Align.CENTER, Align.CENTER, Align.MIN))   # PRINT: 45 deg roof on the blind hole
    # cuts
    s -= motor_relief()
    for az in WHEEL_FIXED_AZ:
        s -= zbore(WHEEL_PIN_D - 0.1, Z_POST_TOP - (POST_PIN_L - WHEEL_WASHER_T - WHEEL_W), Z_POST_TOP + 1, az, WHEEL_AXIS_R)   # Ø2.9 press hole for the Ø3 m6 x 10 pin, 5.5 deep
    for az in WHEEL_AZ:
        r_in = WHEEL_AXIS_R - (BLOCK_TRAVEL_IN if az == WHEEL_SPRUNG_AZ else 0.0) - WHEEL_OD/2 - 1.0
        s -= blk(R_WALL_OUT + 1.0 - r_in, WHEEL_OD + 2.0, Z_POST_TOP + 0.01, Z_SEAT_TOP + 1, az, (r_in + R_WALL_OUT + 1.0)/2)   # open-topped window: the bearing reaches through the wall to the ridge; no bridge to print
        s -= blk(R_WALL_IN_UP + 1.0 - (R_SEAT_IN - 1.0), WHEEL_OD + 2.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, az, (R_SEAT_IN - 1.0 + R_WALL_IN_UP + 1.0)/2)   # PRINT (Ryan, 5 Sep): the seat flange above the wheel is removed entirely
    s -= blk(R_WALL_IN + 0.01 - (CHANNEL_END_R0 + 2.0), 2 * CHANNEL_HALF, Z_PLATE_TOP - 1, Z_ROOF0, WHEEL_SPRUNG_AZ, (CHANNEL_END_R0 + 2.0 + R_WALL_IN + 0.01)/2)   # the channel's clear interior (from the end wall to the wall's inner face)
    for az in NUB_AZ:                                                          # v15: three Ø2 H7 through-holes (reamed) for the dowel pins that locate the glass edge, in Ø5 bosses under the flange
        s += zbore(UNDER_BOSS_D, Z_SEAT_BOT - UNDER_BOSS_H, Z_SEAT_BOT + 0.01, az, PANEL_DISC_R + 0.15 + 1.0)
        s -= zbore(PIN_D, Z_SEAT_BOT - UNDER_BOSS_H - 1, Z_SEAT_TOP + 1, az, PANEL_DISC_R + 0.15 + 1.0)
    s -= blk(2.5, 32.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, 0.0, 67.5, t=-4.0)     # flex slot through the seat at 0 deg (panel flex at t -12, touch tail at +6)
    s -= blk(R_WALL_OUT + 0.5 - (R_WALL_IN - 0.5), HALO_TAIL_W + 1.0, Z_PLATE_TOP - 0.1, Z_PLATE_TOP + 3.0, halo_tail_az(), (R_WALL_IN - 0.5 + R_WALL_OUT + 0.5)/2)   # the halo tail's notch through the wall's foot at the strip's joint
    s -= blk(R_WALL_OUT + 0.5 - (R_WALL_IN - 0.5), 3.0, Z_PLATE_TOP - 0.1, Z_PLATE_TOP + 3.0, HALO_FEED2_AZ, (R_WALL_IN - 0.5 + R_WALL_OUT + 0.5)/2)   # ... and the far-end feed's notch near the converter
    # PRINT (v15, inverted): 0.3 chamfers on the bed face's two circular edges against elephant's foot
    s -= revolve_profile([(R_SEAT_IN - 0.01, Z_SEAT_TOP + 0.01), (R_SEAT_IN + 0.3, Z_SEAT_TOP + 0.01), (R_SEAT_IN - 0.01, Z_SEAT_TOP - 0.3)])
    s -= revolve_profile([(R_WALL_OUT_UP + 0.01, Z_SEAT_TOP + 0.01), (R_WALL_OUT_UP - 0.3, Z_SEAT_TOP + 0.01), (R_WALL_OUT_UP + 0.01, Z_SEAT_TOP - 0.3)])
    s -= blk(6.0, 32.0, Z_SEAT_TOP - 0.6, Z_SEAT_TOP + 1, 0.0, 65.0, t=-4.0)   # the flex passes over the seat's top face here, 0.6 deep
    slits = None
    for az in slit_azs():
        b = blk(R_WALL_OUT_UP - R_WALL_IN_UP + 2.0, SLIT_W, SLIT_Z0, SLIT_Z1, az, (R_WALL_IN_UP + R_WALL_OUT_UP)/2)
        slits = b if slits is None else slits + b
    s -= slits
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

# ---------------------------------------------------------------- v16 halo: machined opal ring, face-down strip, white liner, gasket (HALO-OPTICS)
def halo_diffuser():
    """the opal acrylic ring: r 90.8-94.7, z 7.5-13.2, standing in the ring's rebate, 0.3 chamfers on all four edges (machined from cast opal sheet, annealed)"""
    c = DIFF_CHAMFER
    return revolve_profile([(R_DIFF_IN + c, Z_DIFF0), (R_DIFF_OUT - c, Z_DIFF0), (R_DIFF_OUT, Z_DIFF0 + c), (R_DIFF_OUT, Z_DIFF1 - c), (R_DIFF_OUT - c, Z_DIFF1),
                            (R_DIFF_IN + c, Z_DIFF1), (R_DIFF_IN, Z_DIFF1 - c), (R_DIFF_IN, Z_DIFF0 + c)])
def led_strip():
    """the bought strip as one envelope: a ring r 86.6-90.6, 4 wide, 1.2 thick, stuck face DOWN to the ledge's underside, emitting face at z 12.0"""
    return {"led_strip_ENVELOPE": tube(R_STRIP_OUT, R_STRIP_IN, Z_STRIP0, Z_STRIP1)}
def halo_liner():
    """printed, white: an L-section ring lying in the channel - a 0.4 floor on the ring's top (r 86.5-90.5) and a 0.6 wall up the structure's wall
    to z 11.4 (0.6 under the strip). The channel's floor and inner wall are then white; the ledge's underside is the strip. Split at the two tail notches"""
    l = tube(R_LEDGE_OUT, R_WALL_OUT + 0.1, Z_PLATE_TOP, Z_PLATE_TOP + LINER_T)
    l += tube(R_WALL_OUT + 0.1 + 0.6, R_WALL_OUT + 0.1, Z_PLATE_TOP + LINER_T - 0.01, Z_PLATE_TOP + LINER_WALL_H)
    l -= blk(4.0, HALO_TAIL_W + 1.4, Z_PLATE_TOP - 1, Z_PLATE_TOP + 4, halo_tail_az(), R_WALL_OUT + 1.0)      # the tail passes through it
    l -= blk(4.0, 3.4, Z_PLATE_TOP - 1, Z_PLATE_TOP + 4, HALO_FEED2_AZ, R_WALL_OUT + 1.0)
    return l
def diffuser_gasket():
    """ASSUMED 0.3 closed-cell foam ring between the diffuser's top face and the lip (r 90.8-92.7)"""
    return {"diffuser_gasket_ASSUMED": tube(R_LIP_OUT, R_DIFF_IN, Z_DIFF1, Z_LIP0)}

# ---------------------------------------------------------------- v16 wheels: bought V-groove bearings on pins; two fixed, one on the sprung block
def vgroove_bearing():
    """V623ZZ class (3 x 12 x 4) drawn from its class figures: outer ring with the 90 deg V (depth WHEEL_V_D, root flat WHEEL_V_ROOT_FLAT), inner ring Ø3 bore, shields"""
    ro, ri, h = WHEEL_OD/2, WHEEL_BORE/2, WHEEL_W
    m, f = WHEEL_V_MOUTH/2, WHEEL_V_ROOT_FLAT/2
    pts = [(ri, 0), (ro, 0), (ro, h/2 - m), (ro - WHEEL_V_D, h/2 - f), (ro - WHEEL_V_D, h/2 + f), (ro, h/2 + m), (ro, h), (ri, h)]
    return revolve_profile(pts)
def block_dr(state="nominal"):
    """the block's radial position relative to nominal: 'nominal' (knob centred, the spring pressing it home), 'parked' (wound in for assembly), 'free' (no knob: at its outer stop)"""
    return {"nominal": 0.0, "parked": -BLOCK_TRAVEL_IN, "free": BLOCK_TRAVEL_OUT}[state]
def wheel_bodies(az, state="nominal"):
    """the bearing, its pin and (fixed posts) the washer under its inner ring"""
    out = {}
    dr = block_dr(state) if az == WHEEL_SPRUNG_AZ else 0.0
    r = WHEEL_AXIS_R + dr
    out[f"wheel{az}_V623ZZ_ASSUMED"] = polar(az, r, Z_WHEEL0) * vgroove_bearing()
    if az == WHEEL_SPRUNG_AZ:
        out[f"wheel{az}_pin_3m6x16"] = zbore(WHEEL_PIN_D, Z_BLOCK0 + 0.2, Z_BLOCK0 + 0.2 + BLOCK_PIN_L, az, r)
    else:
        out[f"wheel{az}_pin_3m6x10"] = zbore(WHEEL_PIN_D, Z_WHEEL1 - POST_PIN_L, Z_WHEEL1, az, r)
        out[f"wheel{az}_washer_M3x0.5"] = polar(az, r, Z_POST_TOP) * (Cylinder(WHEEL_WASHER_D/2, WHEEL_WASHER_T, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(WHEEL_PIN_D/2 + 0.1, 3))
    return out
def wheel_block(state="nominal"):
    """printed: the sliding block - BLOCK_L x BLOCK_W x BLOCK_H on the plate top, the Ø2.9 press hole for the axle pin, the Ø2.2 hole for the release
    screw from its inner face and the M2 nut's slot from its top"""
    az = WHEEL_SPRUNG_AZ; dr = block_dr(state)
    r_out = WHEEL_AXIS_R + dr + BLOCK_PIN_FROM_END; r_in = r_out - BLOCK_L
    b = blk(BLOCK_L, BLOCK_W, Z_BLOCK0, Z_BLOCK1, az, (r_in + r_out)/2)
    b -= zbore(WHEEL_PIN_D - 0.1, Z_BLOCK0 - 1, Z_BLOCK1 + 1, az, WHEEL_AXIS_R + dr)
    b -= rbore(2.2, r_in - 1, r_in + BLOCK_NUT_FROM_FACE + NUT_M2_T + 4.5, az, RELEASE_SCREW_Z)                          # the screw's hole, to 0.8 short of the pin's hole
    b -= blk(NUT_M2_T + 0.2, NUT_M2_AF + 0.2, RELEASE_SCREW_Z - NUT_M2_AF/2/math.cos(math.radians(30)) - 0.1, Z_BLOCK1 + 1, az, r_in + BLOCK_NUT_FROM_FACE + NUT_M2_T/2)   # the nut's slot from the top
    return b
def block_parts(state="nominal"):
    """the nut in the block, the spring (drawn at its length in this state) and the captive release screw"""
    out = {}
    az = WHEEL_SPRUNG_AZ; dr = block_dr(state)
    r_in = WHEEL_AXIS_R + dr + BLOCK_PIN_FROM_END - BLOCK_L                                            # the block's inner face
    r_seat = CHANNEL_END_R0 + 2.0                                                                        # the end wall's inner face
    out["block_nut_M2"] = polar(az, r_in + BLOCK_NUT_FROM_FACE + NUT_M2_T/2, RELEASE_SCREW_Z) * Rot(0, 90, 0) * (extrude(RegularPolygon(NUT_M2_AF/2/math.cos(math.radians(30)), 6), NUT_M2_T/2, both=True) - Cylinder(1.05, 5))
    out["block_spring_ASSUMED"] = rbore(SPRING_D, r_seat, r_in, az, RELEASE_SCREW_Z) - rbore(SPRING_D - 0.9, r_seat - 1, r_in + 1, az, RELEASE_SCREW_Z)
    r_head = CHANNEL_END_R0 - 1.3                                                                          # the head on the end wall's centre-side face in every state
    out["block_release_screw_M2x18"] = rbore(3.8, r_head, r_head + 1.3, az, RELEASE_SCREW_Z) + rbore(2.0, r_head + 1.3 - 0.01, r_head + 1.3 + 18.0, az, RELEASE_SCREW_Z)
    return out

# ---------------------------------------------------------------- motor, carriage, clutch (servo on the plate, short tab)
def motor_place(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, Z_MOTOR_BOT)
TAB_X = -(MOTOR_OD/2 + 1.0 + 0.8 + CARRIAGE_TAB_T/2)           # tab centre, carriage frame (inboard = -x local)
def carriage(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    c = cyl(MOTOR_OD/2 + 1.0, 0, CARRIAGE_T)
    c += tube(MOTOR_OD/2 + 1.0, MOTOR_OD/2 + 0.3, CARRIAGE_T - 0.01, CARRIAGE_T + 0.6)
    c -= Pos(0, 0, -0.01) * Box(CARRIAGE_POCKET_L, CARRIAGE_POCKET_W, 3.3, align=(Align.CENTER, Align.CENTER, Align.MIN))   # v16: the pocket takes the 17 x 15 MT6701 module
    c -= cyl(4.5, 3.0, CARRIAGE_T + 2)
    c += Pos(TAB_X, 0, 0) * Box(CARRIAGE_TAB_T, CARRIAGE_TAB_W, CARRIAGE_TAB_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))   # the tall push tab
    c += Pos(TAB_X - CARRIAGE_TAB_T/2, 0, 0) * Box(CARRIAGE_TAB_T/2 + 3.5, CARRIAGE_TAB_W, CARRIAGE_T, align=(Align.MIN, Align.CENTER, Align.MIN))   # tab root (reaches the shoe)
    c -= Pos(-(MOTOR_OD/2 + 1.0) - 1, 0, 0.8) * Box(8.0, 2.4, 2.2, align=(Align.MIN, Align.CENTER, Align.MIN))   # v14: notch through the shoe's inboard wall for the sensor board's lead (SYSTEM-REVIEW 6.2)
    return polar(MOTOR_AZ, MOTOR_R - dr, 0.0) * c
def mt6701_module(engaged=True):
    """v16: the bought MT6701 module (SMALL-PARTS-SOURCING: a 15 x 17 breakout, the chip centred) lying in the carriage's pocket; its chip from its own STEP"""
    dr = 0.0 if engaged else CLUTCH_LIFT
    return {"mt6701_module_ENVELOPE": polar(MOTOR_AZ, MOTOR_R - dr, 0.0) * Box(MT_MOD_L, MT_MOD_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))}
def mt6701_bodies(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return bodies_of("MT6701CT-STD_SOP8.step", polar(MOTOR_AZ, MOTOR_R - dr, 1.6), prefix="mt6701_")
def magnet_body(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return bodies_of("MT6701_diametric_magnet_D6x2p5.step", polar(MOTOR_AZ, MOTOR_R - dr, Z_MOTOR_BOT), prefix="motor_")
def motor_bodies(engaged=True):
    return bodies_of(MOTOR_FILE, motor_place(engaged), prefix="motor_")
def drive_collar(engaged=True):
    """v16 (printed, PETG; POM turned in production): a ring pressed over the bell's top 3.5 - ID 35, OD 39.4 - that carries the band and reaches the
    bore; the bell itself stops at r 86.0, inside the wall and the liner. A 0.3 lead-in chamfer at its lower inner edge for the press"""
    dr = 0.0 if engaged else CLUTCH_LIFT
    c = tube(DRIVE_COLLAR_OD/2, DRIVE_COLLAR_ID/2 - 0.05, Z_COLLAR0, Z_COLLAR1)
    c -= revolve_profile([(DRIVE_COLLAR_ID/2 - 0.06, Z_COLLAR0 - 0.01), (DRIVE_COLLAR_ID/2 + 0.3, Z_COLLAR0 - 0.01), (DRIVE_COLLAR_ID/2 - 0.06, Z_COLLAR0 + 0.3)])
    return polar(MOTOR_AZ, MOTOR_R - dr, 0) * c
def band(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, 0) * tube(DRIVE_COLLAR_OD/2 + MOTOR_BAND_T, DRIVE_COLLAR_OD/2 + 0.01, Z_DRIVE0, Z_DRIVE1)
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
# ---------------------------------------------------------------- v16: the plate boards on countersunk M2 studs from below, spacers, nuts above; the MCU tray over the audio board
def board_place(az, r, rot, z):
    """a board's frame: centre at (az, r), its long axis turned `rot` from the radial direction (the layout study's convention), bottom face at z"""
    return polar(az, r, z) * Rot(0, 0, rot)
def stud_xy():
    """every countersunk M2 stud from below: the audio board (4), the driver breakout (2), the haptic breakout (2), the level shifter (2), the converter (2)"""
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append(rot_xy(0, 0, AUDIO_R + sy * AUDIO_HOLE_W, sx * AUDIO_HOLE_L, AUDIO_AZ))
    for (lx, ly) in BOB_HOLES: out.append(frame_xy(BOB_AZ, BOB_R, BOB_ROT, lx, ly))
    for (lx, ly) in DRV_HOLES: out.append(frame_xy(DRV_AZ, DRV_R, DRV_ROT, lx, ly))
    for (lx, ly) in LS_HOLES: out.append(frame_xy(LS_AZ, LS_R, LS_ROT, lx, ly))
    for t in (-CONV_HOLE_T, CONV_HOLE_T): out.append(rot_xy(0, 0, CONV_R, t, CONV_AZ))
    return out
BOB_HOLES = [(-BOB_L/2 + 2.5, 0.0), (BOB_L/2 - 2.5, 0.0)]                         # ASSUMED: two on the long axis at the short ends
DRV_HOLES = [(-6.0, 0.0), (6.0, 0.0)]                                              # ASSUMED: two on the long axis, 4 in from the short ends
def frame_xy(az, r, rot, lx, ly):
    """device xy of a point (lx, ly) in a board frame placed by board_place"""
    a = D(az + rot); cx, cy = r * math.cos(D(az)), r * math.sin(D(az))
    return (cx + lx * math.cos(a) - ly * math.sin(a), cy + lx * math.sin(a) + ly * math.cos(a))
def stud_stack(x, y, z_board0, board_t, spacer_h, top_nut_z=None, length=None):
    """one fixing: the csk M2 stud (head in the closing plate's underside), the printed spacer under the board, the nut above it"""
    out = {}
    L = length or (CLOSING_T + (PLATE_T - CLOSING_T) + spacer_h + board_t + NUT_M2_T + 0.8)
    head = Pos(x, y, -0.2) * Cone(STUD_HEAD_D/2, STUD_D/2, STUD_HEAD_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shank = Pos(x, y, STUD_HEAD_H - 0.2 - 0.01) * Cylinder(STUD_D/2, L - STUD_HEAD_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out["stud"] = head + shank
    if spacer_h > 0:
        out["spacer"] = Pos(x, y, Z_PLATE_TOP) * (Cylinder(SPACER_D/2, spacer_h, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(STUD_HOLE_D/2, 10))
    zn = top_nut_z if top_nut_z is not None else z_board0 + board_t
    out["nut"] = Pos(x, y, zn) * (extrude(RegularPolygon(NUT_M2_AF/2/math.cos(math.radians(30)), 6), NUT_M2_T) - Cylinder(STUD_D/2 + 0.05, 5))
    return out
def audio_board():
    b = board_place(AUDIO_AZ, AUDIO_R, 90.0, Z_PLATE_TOP + AUDIO_SPACER_H) * Box(AUDIO_L, AUDIO_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = rot_xy(0, 0, AUDIO_R + sy * AUDIO_HOLE_W, sx * AUDIO_HOLE_L, AUDIO_AZ)
            b -= Pos(x, y, 0) * Cylinder(STUD_HOLE_D/2, 30)
    return b
def audio_parts():
    zt = Z_PLATE_TOP + AUDIO_SPACER_H + 1.6; P = board_place(AUDIO_AZ, AUDIO_R, 90.0, zt)
    out = {"audio_parts_ENVELOPE": P * Pos(-3, 0, 0) * Box(10.0, 12.0, CONN_H, align=(Align.CENTER, Align.CENTER, Align.MIN)),            # its Pico-Lock connectors etc, 2.0 mated (between the four stud nuts - the layout is not done)
           "audio_usb_plug_ENVELOPE": P * Pos(-AUDIO_L/2 + 5.5, 0.0, 0) * Box(10.0, 8.0, USB_PLUG_H, align=(Align.CENTER, Align.CENTER, Align.MIN))}   # the moulded plug of its pre-made USB lead, 4.0, on the board's middle line at its west end
    out.update(bodies_of("ESS_ES9219Q_WQFN40_5x5.step", P * Pos(7, 0, 0), prefix="es9219q_"))
    return out
def bob_board():
    b = board_place(BOB_AZ, BOB_R, BOB_ROT, Z_PLATE_TOP + SPACER_H) * Box(BOB_L, BOB_W, BOB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (lx, ly) in BOB_HOLES:
        x, y = frame_xy(BOB_AZ, BOB_R, BOB_ROT, lx, ly); b -= Pos(x, y, 0) * Cylinder(STUD_HOLE_D/2, 30)
    return b
def bob_parts():
    """TMC6300-BOB: the driver chip from its STEP, a 2.0 parts envelope, and the right-angle header strip along its -y long edge (6.0 tall: header + housings)"""
    zt = Z_PLATE_TOP + SPACER_H + BOB_T; P = board_place(BOB_AZ, BOB_R, BOB_ROT, zt)
    out = bodies_of("TMC6300-LA-T_QFN20_3x3.step", P * Pos(2, 0, 0), prefix="tmc6300_")
    out["bob_parts_ENVELOPE"] = P * Box(BOB_L - 10, BOB_W - 11, BOB_PARTS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for i, sy in enumerate((-1, 1)):
        out[f"bob_header_ENVELOPE_{i}"] = P * Pos(0, sy * (BOB_W/2 - 1.5), 0) * Box(BOB_L - 10, 3.0, BOB_HEADER_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def drv_board():
    b = board_place(DRV_AZ, DRV_R, DRV_ROT, Z_PLATE_TOP + SPACER_H) * Box(DRV_L, DRV_W, DRV_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (lx, ly) in DRV_HOLES:
        x, y = frame_xy(DRV_AZ, DRV_R, DRV_ROT, lx, ly); b -= Pos(x, y, 0) * Cylinder(STUD_HOLE_D/2, 30)
    return b
def drv_parts():
    zt = Z_PLATE_TOP + SPACER_H + DRV_T; P = board_place(DRV_AZ, DRV_R, DRV_ROT, zt)
    out = bodies_of("TI_DRV2605L_VSSOP10_DGS.step", P * Pos(0, 2, 0), prefix="drv2605l_")
    out["drv_parts_ENVELOPE"] = P * Pos(0, -2.0, 0) * Box(DRV_L - 11, DRV_W - 8, DRV_PARTS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def board_fixings():
    """every stud, spacer and nut on the plate boards (the audio's studs carry on up through the tray: see tray_fixings)"""
    out = {}
    for i, (lx, ly) in enumerate(BOB_HOLES):
        x, y = frame_xy(BOB_AZ, BOB_R, BOB_ROT, lx, ly)
        for k, v in stud_stack(x, y, Z_PLATE_TOP + SPACER_H, BOB_T, SPACER_H).items(): out[f"bob_{k}_{i}"] = v
    for i, (lx, ly) in enumerate(DRV_HOLES):
        x, y = frame_xy(DRV_AZ, DRV_R, DRV_ROT, lx, ly)
        for k, v in stud_stack(x, y, Z_PLATE_TOP + SPACER_H, DRV_T, SPACER_H).items(): out[f"drv_{k}_{i}"] = v
    for i, (lx, ly) in enumerate(LS_HOLES):
        x, y = frame_xy(LS_AZ, LS_R, LS_ROT, lx, ly)
        for k, v in stud_stack(x, y, Z_PLATE_TOP + SPACER_H, LS_T, SPACER_H).items(): out[f"ls_{k}_{i}"] = v
    for i, t in enumerate((-CONV_HOLE_T, CONV_HOLE_T)):
        x, y = rot_xy(0, 0, CONV_R, t, CONV_AZ)
        for k, v in stud_stack(x, y, Z_PLATE_TOP + CONV_PAD_T, 1.6, 0.0).items(): out[f"conv_{k}_{i}"] = v      # the gap pad is its spacer; the module's board 1.6 at its holes
    i = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = rot_xy(0, 0, AUDIO_R + sy * AUDIO_HOLE_W, sx * AUDIO_HOLE_L, AUDIO_AZ)
            st = stud_stack(x, y, Z_PLATE_TOP + AUDIO_SPACER_H, 1.6, AUDIO_SPACER_H, length=AUDIO_STUD_L)
            out[f"audio_stud_{i}"] = st["stud"]; out[f"audio_spacer_{i}"] = st["spacer"]; out[f"audio_nut_{i}"] = st["nut"]
            z_nut1 = Z_PLATE_TOP + AUDIO_SPACER_H + 1.6 + NUT_M2_T
            out[f"tray_spacer_{i}"] = Pos(x, y, z_nut1) * (Cylinder(SPACER_D/2, TRAY_SPACER_H, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(STUD_HOLE_D/2, 10))   # the 4.4 tube to the tray
            out[f"tray_nut_{i}"] = Pos(x, y, Z_KEEPER1) * (extrude(RegularPolygon(NUT_M2_AF/2/math.cos(math.radians(30)), 6), NUT_M2_T) - Cylinder(STUD_D/2 + 0.05, 5))   # the top nut on the keeper
            i += 1
    return out
def board_spacer(h=SPACER_H):
    """the printed spacer as a part (the family: 3.0 under the plate boards, 1.0 under the audio board, 4.4 tubes under the tray)"""
    return Cylinder(SPACER_D/2, h, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(STUD_HOLE_D/2, 10)
def tray_place(z):
    return board_place(AUDIO_AZ, AUDIO_R, 90.0, z)
def tray_outline(z0, t):
    """the tray's outline: the plate over the audio board (audio frame)"""
    return tray_place(z0) * Pos(TRAY_T0, TRAY_Y0, 0) * Box(TRAY_L, TRAY_W, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
def mcu_tray():
    """printed: a 40 x 25 x 1.2 plate on the audio board's four studs, with a 0.6 pocket that locates the microcontroller"""
    t = tray_outline(Z_TRAY0, TRAY_T)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = rot_xy(0, 0, AUDIO_R + sy * AUDIO_HOLE_W, sx * AUDIO_HOLE_L, AUDIO_AZ); t -= Pos(x, y, 0) * Cylinder(STUD_HOLE_D/2, 80)
    t -= tray_place(Z_TRAY1 - TRAY_POCKET_D) * Pos(MCU_ON_TRAY[0], MCU_ON_TRAY[1], 0) * Rot(0, 0, -90) * Box(MCU_L + 0.4, MCU_W + 0.4, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t
def tray_keeper():
    """printed: a 1.2 frame over the tray, clamped by the audio studs' top nuts, whose rails hold the two boards down by their edges (1.5 wide; the boards
    carry no screw). Windows over the boards' parts; the microcontroller's USB-C end is open"""
    k = tray_outline(Z_TRAY1, KEEPER_T)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = rot_xy(0, 0, AUDIO_R + sy * AUDIO_HOLE_W, sx * AUDIO_HOLE_L, AUDIO_AZ); k -= Pos(x, y, 0) * Cylinder(STUD_HOLE_D/2, 80)
    k -= tray_place(Z_TRAY1 - 1) * Pos(MCU_ON_TRAY[0], MCU_ON_TRAY[1], 0) * Rot(0, 0, -90) * Box(MCU_L - 3.0, MCU_W - 3.0, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    k -= tray_place(Z_TRAY1 - 1) * Pos(MCU_ON_TRAY[0], MCU_ON_TRAY[1], 0) * Rot(0, 0, -90) * Pos(-MCU_L/2, 0, 0) * Box(6.0, 10.0, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))   # the USB-C end open (inboard)
    return k
def tray_boards():
    """the microcontroller (ESP32-S3-Zero class envelope, its USB-C at the -x end) lying in the tray's pocket under the keeper"""
    out = {}
    z0 = Z_TRAY1 - TRAY_POCKET_D
    P = tray_place(z0) * Pos(MCU_ON_TRAY[0], MCU_ON_TRAY[1], 0) * Rot(0, 0, -90)
    out["mcu_ESP32-S3-Zero_ENVELOPE"] = P * Box(MCU_L, MCU_W, MCU_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out["mcu_usbc_ENVELOPE"] = P * Pos(-MCU_L/2 + 3.5, 0, MCU_T) * Box(7.0, 9.0, MCU_USB_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out["mcu_parts_ENVELOPE"] = P * Pos(2.0, 0, MCU_T) * Box(MCU_L - 10, MCU_W - 4, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
LS_HOLES  = [(-3.0, -4.0), (-3.0, 4.0)]
def ls_board():
    b = board_place(LS_AZ, LS_R, LS_ROT, Z_PLATE_TOP + SPACER_H) * Box(LS_L, LS_W, LS_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (lx, ly) in LS_HOLES:
        x, y = frame_xy(LS_AZ, LS_R, LS_ROT, lx, ly); b -= Pos(x, y, 0) * Cylinder(STUD_HOLE_D/2, 30)
    return b
def ls_parts():
    zt = Z_PLATE_TOP + SPACER_H + LS_T; Q = board_place(LS_AZ, LS_R, LS_ROT, zt)
    return {"level_shifter_parts_ENVELOPE": Q * Pos(3.5, 0, 0) * Box(LS_L - 11, LS_W - 6, LS_PARTS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))}
def converter_body():
    """the Pololu D24V90F5 on the PLATE (thermal plan rule 15), on a 0.5 gap pad, tangential in the front crescent; two M2 studs through its holes"""
    return {"converter_D24V90F5_ENVELOPE": polar(CONV_AZ, CONV_R, Z_PLATE_TOP + CONV_PAD_T) * Box(CONV_W, CONV_L, CONV_H, align=(Align.CENTER, Align.CENTER, Align.MIN)),
            "converter_gap_pad_ASSUMED": polar(CONV_AZ, CONV_R, Z_PLATE_TOP) * (Box(CONV_W, CONV_L, CONV_PAD_T, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Pos(0, -CONV_HOLE_T, 0) * Cylinder(1.5, 5) - Pos(0, CONV_HOLE_T, 0) * Cylinder(1.5, 5))}

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
LRA_CLIP_AZ = 252.5                                  # the LRA's flex tail (pads at r 81.2-81.6) sits at this azimuth
LRA_PAD_R_IN = R_WALL_IN_UP - 1.25                    # 81.55: the pad's inner face (the LRA bonds to it), 1.25 inside the UPPER wall's inner face
LRA_BOARD_R = LRA_PAD_R_IN - 0.35 - LRA_POGO_L - 3.0 - LRA_BOARD_T/2   # 75.5: the contact carrier's centre radius: the 3.0 block on its outer face, the pins' tips at 81.2 on the LRA tail's pads (0.35 inboard of the pad's face)
LRA_CLIP_R0 = LRA_BOARD_R - 1.0                       # the clip's ribs start here
def lra_bodies():
    place = polar(LRA_AZ, LRA_PAD_R_IN - 0.02, 13.0) * Rot(0, -90, 0)
    return bodies_of("Vybronics_VLV101040A_LRA.step", place, prefix="lra_")


# ---------------------------------------------------------------- v14: grounding features and the two homeless items
def lra_contact_bodies():
    """SYSTEM-REVIEW 6.1: the vibration actuator must not be soldered - a 7 x 8 x 1 board (ASSUMED) in a printed clip beside the
    LRA's flex tail, two pogo pins (ASSUMED Ø1.5, 2.2 compressed) on the tail's two pads at z 11.75 and 14.35"""
    out = {}
    out["lra_pogo_carrier_ASSUMED"] = blk(LRA_BOARD_T, LRA_BOARD_W, 9.0, 9.0 + LRA_BOARD_H, LRA_CLIP_AZ, LRA_BOARD_R)
    out["lra_pogo_block_MillMax_867-22-002_ENVELOPE"] = blk(3.0, 5.1, 11.75 - 1.3, 14.35 + 1.3, LRA_CLIP_AZ, LRA_BOARD_R + LRA_BOARD_T/2 + 1.5)   # the two-position spring-pin block (2.54 pitch) on the carrier's outer face
    for i, z in enumerate((11.75, 14.35)):
        out[f"lra_pogo_pin_{i}"] = rbore(LRA_POGO_D, LRA_BOARD_R + LRA_BOARD_T/2 + 3.0 - 0.01, LRA_BOARD_R + LRA_BOARD_T/2 + 3.0 + LRA_POGO_L, LRA_CLIP_AZ, z)
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
    """GROUNDING 3.1 and 4.1: the chassis bond (M2.5 pan head, external-tooth star washer, ring terminal) on the plate top beside the
    power inlet; the rim ring's dedicated bond screw through its flange into the core's shoulder, star washer under the head"""
    out = {}
    x, y = GND_BOND_XY
    out["chassis_bond_star_washer"] = Pos(x, y, Z_PLATE_TOP) * (Cylinder(STAR_M25_OD/2, 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(STAR_M25_ID/2, 3))
    out["chassis_bond_ring_terminal"] = Pos(x, y, Z_PLATE_TOP + 0.6) * (Cylinder(3.0, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(STAR_M25_ID/2, 3)) + box_at(x + 2.5, x + 11.0, y - 2.0, y + 2.0, Z_PLATE_TOP + 0.6, Z_PLATE_TOP + 1.4)
    out["chassis_bond_screw"] = Pos(x, y, Z_PLATE_TOP + 1.4) * Cylinder(PAN_M25_HEAD_D/2, PAN_M25_HEAD_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out["ring_bond_star_washer"] = polar(RING_BOND_AZ, RING_BOND_R, PLATE_T) * (Cylinder(STAR_M25_OD/2, 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(STAR_M25_ID/2, 3))
    out["ring_bond_screw"] = polar(RING_BOND_AZ, RING_BOND_R, PLATE_T + 0.6) * Cylinder(PAN_M25_HEAD_D/2, PAN_M25_HEAD_H, align=(Align.CENTER, Align.CENTER, Align.MIN)) + polar(RING_BOND_AZ, RING_BOND_R, RIM_STEP_Z - 2.8) * Cylinder(1.25, PLATE_T + 0.6 - RIM_STEP_Z + 2.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def wire_bodies():
    """GROUNDING 6 and 5: the USB-C receptacle's shell wire to the chassis bond (Ø1.3, drawn as its route: up out of the port slot
    beside the USB-C board, along under the connect bracket's slab to the slot's edge, to the terminal); the motor frame's bond
    wire to the motion board's ground (SYSTEM-REVIEW: a floating frame switching at 20 ns edges beside the encoder)"""
    out = {}
    x, y = GND_BOND_XY
    xw = PORT_FACE_R0 - 12.35                                                                  # 71.0: beside the USB-C board's inner end
    out["usbc_shell_wire_1"] = box_at(xw - 0.65, xw + 0.65, PORT_USBC_T - 1.65, PORT_USBC_T - 0.35, 3.4, 9.4)   # up beside the USB-C board, in the slot
    out["usbc_shell_wire_2"] = box_at(xw - 0.65, xw + 0.65, PORT_USBC_T - 1.65, 22.0, 8.1, 9.4)                 # along under the bracket's slab to its edge
    out["usbc_shell_wire_3"] = box_at(x + 11.0, xw + 0.65, 22.0, 23.3, 8.1, 9.4)                                 # across to the terminal's tab
    out["usbc_shell_wire_4"] = box_at(x + 11.0, x + 12.3, 22.0, y - 1.0, 8.1, 9.4)
    # motor frame bond: a ring terminal under the motor's inboard base screw, the lead inward over the carriage, up, and across to the motion board
    dm = MOTOR_R - 65.704                                                                            # the motor sits this much further out than v15
    out["motor_bond_wire_1"] = box_at(-0.65, 0.65, 45.5 + dm, 50.8 + dm, Z_MOTOR_BOT + 0.8, Z_MOTOR_BOT + 2.1)
    out["motor_bond_wire_2"] = box_at(-0.65, 0.65, 45.5 + dm, 46.8 + dm, Z_MOTOR_BOT + 0.8, Z_PLATE_TOP + 4.6)
    out["motor_bond_wire_3"] = box_at(-0.65, 0.65, 43.0 + dm, 46.8 + dm, Z_PLATE_TOP + 3.3, Z_PLATE_TOP + 4.6)      # v16: along the plate top toward the centre; it joins the motor's phase leads to the driver breakout (its ground) - drawn to the tab slot's edge, then it is a lead in the harness
    return out
def sensor_cable_bodies():
    """SYSTEM-REVIEW 6.2: the rotor sensor's lead leaves the carriage's pocket through a notch beside the tab, rises through the plate's
    tab slot, and makes a 12 mm service loop over the servo's frame before dropping to the motion board - flex-rated, 2.4 mm of travel"""
    out = {}
    xc = -6.0                                                                                            # t +6.0: beside the tab (t +-5), inside the servo frame's wall (t 7.6)
    dm = MOTOR_R - 65.704
    out["sensor_cable_1"] = box_at(xc - 0.75, xc + 0.75, 38.75 + dm, 40.25 + dm, 1.0, Z_PLATE_TOP + 7.5)                 # up through the notch beside the tab slot
    out["sensor_cable_2"] = box_at(xc - 0.75, xc + 0.75, 38.75 + dm, 40.25 + dm + SENSOR_CABLE_LOOP/2, Z_PLATE_TOP + 7.5, Z_PLATE_TOP + 9.5)   # the loop's outward leg over the servo frame (14.5)
    out["sensor_cable_3"] = box_at(xc - 0.75, 10.0, 32.0 + dm, 46.5 + dm, Z_PLATE_TOP + 8.5, Z_PLATE_TOP + 9.5)             # over toward the blower's corner (drawn as a slab: the loop and the run) - from here it is a lead in the harness to the tray (v16: the motion board is gone)
    return out

# ---------------------------------------------------------------- rear port module: face + barrel + USB-C + panel jack + light-sensor breakout (v16)
def port_face():
    f = blk(PORT_FACE_T, PORT_W, -PAD_T, Z_PLATE_TOP, 0.0, PORT_FACE_R0 + PORT_FACE_T/2)
    f += blk(3.5, 12.0, USBC_AXIS_Z - 1.1 - 1.6 - 1.5, USBC_AXIS_Z - 1.1 - 1.6, 0.0, PORT_FACE_R0 - 1.75, t=PORT_USBC_T)   # shelf under the USB-C board
    # v16: the light-sensor breakout (Adafruit 4162, 16.6 x 16.5) stands in a slot holder on the face's inner side: a 3.0 block from the pad to the plate top, the
    # slot 1.8 wide x 17.0, the board rises free above the plate top to z 17.5 with its sensor at the face's hole (z 4.0)
    f += blk(5.3, LIGHT_BOARD_L + 3.0, -PAD_T, Z_PLATE_TOP, 0.0, PORT_FACE_R0 - 2.65, t=PORT_LIGHT_T)
    f -= blk(LIGHT_BOARD_T + 0.2, LIGHT_BOARD_L + 0.4, LIGHT_BOARD_Z0 - 0.01, Z_PLATE_TOP + 1, 0.0, LIGHT_SLOT_R, t=PORT_LIGHT_T)
    f -= blk(5.5, LIGHT_BOARD_L - 4.0, -PAD_T - 1, LIGHT_BOARD_Z0 - 0.01, 0.0, PORT_FACE_R0 - 2.65, t=PORT_LIGHT_T)   # the holder is open under the board's middle (its two rows of pins hang there)
    # v16: the panel-mount 3.5 mm jack's bushing needs 3.0 of face: a boss on the inner side round the Ø6.3 hole
    f += blk(JACK_BOSS_T - PORT_FACE_T, 11.0, JACK_AXIS_Z - 5.5, JACK_AXIS_Z + 5.5, 0.0, PORT_FACE_R0 - (JACK_BOSS_T - PORT_FACE_T)/2, t=PORT_JACK_T)
    # a rail along the face's top, 1.5 tall on the plate top, reaching 4 mm past the slot on each side: two M2 screws into the plate
    rail_w = 2 * PORT_TAB_T + 6.0
    xo = PORT_FACE_R0 + PORT_FACE_T                                                  # the face's outer plane (at the wall's inner face)
    ri = R_WALL_IN - 0.3                                                             # nothing above z 8 may reach the wall
    rail = tube(ri, PORT_TAB_R - 2.5, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 1.5) & box_at(60.0, 95.0, -rail_w/2, rail_w/2, Z_PLATE_TOP - 1, Z_PLATE_TOP + 2)
    rail += box_at(PORT_FACE_R0, xo, -PORT_W/2, PORT_W/2, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 1.5) & cyl(ri, Z_PLATE_TOP - 1, Z_PLATE_TOP + 2)   # joins the rail to the face's top
    rail -= blk(8.0, LIGHT_BOARD_L + 2.0, Z_PLATE_TOP - 1, Z_PLATE_TOP + 2, 0.0, PORT_FACE_R0 - 2.65, t=PORT_LIGHT_T)   # the rail is cut away round the sensor board's slot
    f += rail                                                                          # PRINT: face-down, the rail's curved front is a 1.5 mm ledge 0.3-5.7 above the bed (small overhang, accepted)
    for t in (-PORT_TAB_T, PORT_TAB_T):
        f -= zbore(2.2, Z_PLATE_TOP - 1, Z_PLATE_TOP + 3, 0.0, PORT_TAB_R, t=t)
    f -= blk(PORT_FACE_T + 2, 9.6, USBC_AXIS_Z - USBC_BELOW - 0.3, USBC_AXIS_Z + USBC_ABOVE + 0.3 + 1.6, 0.0, PORT_FACE_R0 + PORT_FACE_T/2, t=PORT_USBC_T)
    f -= rbore(JACK_HOLE_D, PORT_FACE_R0 - JACK_BOSS_T, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, JACK_AXIS_Z, t=PORT_JACK_T)
    f -= rbore(6.2, PORT_FACE_R0 - 1, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, BARREL_AXIS_Z, t=PORT_BARREL_T)   # barrel nose Ø5.5
    f -= rbore(SENSOR_HOLE_D, PORT_FACE_R0 - 0.5, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, 4.0, t=PORT_LIGHT_T)   # the light hole through the face
    f -= blk(PORT_FACE_R0 + 0.01 - (LIGHT_SLOT_R + LIGHT_BOARD_T/2 + 0.09), 8.5, 4.0 - 2.5, 4.0 + 2.5, 0.0, (PORT_FACE_R0 + 0.01 + LIGHT_SLOT_R + LIGHT_BOARD_T/2 + 0.09)/2, t=PORT_LIGHT_T)   # a pocket through the holder, from the slot to the face's inner surface, for the 6.8 x 2.4 x 3.0 sensor package on the board's outer face
    return f
USBC_BOARD_Z0 = USBC_AXIS_Z - 1.1 - 1.6
def usbc_board():
    b = blk(11.0, 12.0, USBC_BOARD_Z0, USBC_BOARD_Z0 + 1.6, 0.0, PORT_FACE_R0 - 5.5, t=PORT_USBC_T)
    b -= blk(6.3, 9.3, USBC_BOARD_Z0 - 1, USBC_BOARD_Z0 + 3, 0.0, PORT_FACE_R0 - 3.1, t=PORT_USBC_T)
    return b
def usbc_bodies():
    place = polar(0.0, PORT_FACE_R0, USBC_BOARD_Z0 + 1.6) * Pos(0, PORT_USBC_T, 0)
    return bodies_of("GCT_USB4520-03-0-A_usbc_midmount.step", place, keep=lambda l: "cutout" not in l, prefix="usbc_")
def jack_bodies():
    """v16: a panel-mount 3.5 mm jack (SMALL-PARTS-SOURCING): its bushing through the face's Ø6.3 hole (nut on the outside), the body behind it ASSUMED Ø9 x 14 with
    solder tags; no board (its three leads go to the audio board)"""
    r_face = PORT_FACE_R0 + PORT_FACE_T
    out = {"jack_panel_bushing_ENVELOPE": rbore(6.0, PORT_FACE_R0 - JACK_BOSS_T + PORT_FACE_T - 0.5, r_face + 2.5, 0.0, JACK_AXIS_Z, t=PORT_JACK_T),
           "jack_panel_nut_ENVELOPE": rbore(8.0, r_face, r_face + 2.0, 0.0, JACK_AXIS_Z, t=PORT_JACK_T) - rbore(6.1, r_face - 1, r_face + 3, 0.0, JACK_AXIS_Z, t=PORT_JACK_T),
           "jack_panel_body_ENVELOPE": rbore(JACK_BODY_D, PORT_FACE_R0 - JACK_BOSS_T + PORT_FACE_T - 0.5 - JACK_BODY_L, PORT_FACE_R0 - JACK_BOSS_T + PORT_FACE_T - 0.5, 0.0, JACK_AXIS_Z, t=PORT_JACK_T)}
    return out
def barrel_board():
    """vertical board (tangential plane) carrying the right-angle jack, so the barrel axis height is free"""
    return blk(1.6, 14.0, -1.0, 8.0, 0.0, PORT_FACE_R0 + 1.0 - 13.2 - 0.8, t=PORT_BARREL_T)          # its outer face against the jack body's inner end
def barrel_bodies():
    """CUI PJ-063AH: 24 V 8 A, 2.0 mm pin (PUBLISHED); body 14.4 x 9.0 x 11.0 ASSUMED, bushing to the face"""
    body = blk(13.2, 11.0, BARREL_AXIS_Z - 4.5, BARREL_AXIS_Z + 4.5, 0.0, PORT_FACE_R0 + 1.0 - 13.2/2, t=PORT_BARREL_T)   # body ends 1.0 into the face (the bushing sits in the face's hole)
    return {"barrel_jack_ENVELOPE": body}
def light_bodies():
    """v16: the Adafruit 4162 VEML7700 breakout (PUBLISHED 16.6 x 16.5) standing in the face's slot holder, its sensor (from its STEP) on the outer face at the hole"""
    out = {"light_board_Adafruit4162_ENVELOPE": blk(LIGHT_BOARD_T, LIGHT_BOARD_L, LIGHT_BOARD_Z0, LIGHT_BOARD_Z0 + LIGHT_BOARD_H, 0.0, LIGHT_SLOT_R, t=PORT_LIGHT_T)}
    out["light_board_parts_ENVELOPE"] = blk(1.5, LIGHT_BOARD_L - 4.0, Z_PLATE_TOP + 1.0, LIGHT_BOARD_Z0 + LIGHT_BOARD_H - 1.0, 0.0, LIGHT_SLOT_R - LIGHT_BOARD_T/2 - 0.75, t=PORT_LIGHT_T)   # its parts on the inner face, above the holder
    place = polar(0.0, LIGHT_SLOT_R + LIGHT_BOARD_T/2, 4.0) * Pos(0, PORT_LIGHT_T, 0) * Rot(0, 90, 0) * Rot(0, 0, 90)   # the package's 6.8 tangential, its 3.0 outward
    out.update(bodies_of("Vishay_VEML7700-TR_ambient_light_sensor.step", place, prefix="veml7700_"))
    return out
def plug_envelopes():
    out = {}
    r0 = PORT_FACE_R0 + PORT_FACE_T
    out["barrel_plug_ENVELOPE"] = rbore(8.5, r0 + 0.5, r0 + 14.0, 0.0, BARREL_AXIS_Z, t=PORT_BARREL_T)     # right-angle plug body, then the cable turns sideways
    out["barrel_plug_ENVELOPE_cable"] = blk(8.5, 22.0, BARREL_AXIS_Z - 4.25, BARREL_AXIS_Z + 4.25, 0.0, r0 + 14.0 - 4.25, t=PORT_BARREL_T - 11.0)
    out["usbc_plug_ENVELOPE"] = blk(25.0, 8.3, USBC_AXIS_Z - 3.25, USBC_AXIS_Z + 3.25, 0.0, r0 + 0.5 + 12.5, t=PORT_USBC_T)
    out["jack_plug_ENVELOPE"] = rbore(6.0, r0 + 0.5, r0 + 30.0, 0.0, JACK_AXIS_Z, t=PORT_JACK_T)
    return out

# ---------------------------------------------------------------- assembly
def made_parts(knurl=None, engaged=True, block="nominal"):
    m = {"base_plate": base_plate(), "rim_ring_STEEL": rim_ring(), "closing_plate_AL": closing_plate(), "internal_structure": internal_structure(),
         "halo_diffuser": halo_diffuser(), "halo_liner": halo_liner(), "knob_body": knob_body(knurl),
         "carriage": carriage(engaged), "drive_collar": drive_collar(engaged), "servo_mount": servo_mount(), "connect_bracket": connect_bracket(),
         "speaker_cradle": speaker_cradle(), "port_face": port_face(), "wheel_block": wheel_block(block),
         "adapter_board": adapter_board(), "connect_board": connect_board(), "audio_board": audio_board(), "bob_board": bob_board(), "drv_board": drv_board(),
         "ls_board": ls_board(), "mcu_tray": mcu_tray(), "tray_keeper": tray_keeper(),
         "encoder_board": encoder_board(), "encoder_shim": encoder_shim(), "blower_saddle": blower_saddle(), "hood_lid": hood_lid(), "usbc_board": usbc_board(), "barrel_board": barrel_board(),
         "bond_tape": bond_tape()}
    return m
def bought_parts(engaged=True, block="nominal"):
    b = {}
    b.update(panel_bodies()); b.update(flex_bodies())
    b.update(pi_bodies()); b.update(cooler_bodies()); b.update(pi_plug_bodies()); b.update(pi_stack_bodies())
    b.update(motor_bodies(engaged)); b["motor_band"] = band(engaged)
    b.update(magnet_body(engaged)); b.update(mt6701_bodies(engaged)); b.update(mt6701_module(engaged))
    b.update(servo_bodies())
    for az in WHEEL_AZ: b.update(wheel_bodies(az, block))
    b.update(block_parts(block))
    b.update(speaker_bodies()); b.update(encoder_bodies()); b.update(lra_bodies())
    b.update(adapter_parts()); b.update(connect_board_parts()); b.update(cable_bodies()); b.update(audio_parts()); b.update(bob_parts()); b.update(drv_parts()); b.update(tray_boards()); b.update(ls_parts()); b.update(converter_body()); b.update(board_fixings())
    b.update(usbc_bodies()); b.update(jack_bodies()); b.update(barrel_bodies()); b.update(light_bodies())
    b.update(led_strip()); b.update(diffuser_gasket()); b.update(plug_envelopes())
    b.update(lra_contact_bodies()); b.update(bleed_bodies()); b.update(bond_bodies()); b.update(wire_bodies()); b.update(sensor_cable_bodies())
    b.update(blower_bodies()); b.update(hood_gasket()); b.update(fan_lead_bodies()); b.update(halo_tail_bodies()); b.update(locating_pins()); b.update(closing_gasket())
    b["pad"] = pad()
    return b
