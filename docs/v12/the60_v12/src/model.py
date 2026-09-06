"""the 60 — v12 geometry.  build123d algebra mode.

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
    # audio board's USB: right-angle USB-A plug in the upper socket of the rear stack nearest 270 deg (ASSUMED 9 protrusion x 14 x 8)
    out["usba_plug_ENVELOPE"] = box_at(PI_X0 + PI_L + PI_OVERHANG, PI_X0 + PI_L + PI_OVERHANG + 9.0, PI_Y0 + 4.0, PI_Y0 + 16.5, PI_Z0 + 9.0, PI_Z0 + 16.0)
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
    rc = rb + STRIP_T
    return [(rb, zs), (rk - CH_BOT, zs), (rk, zs + CH_BOT),
            (rk, zt - CH_TOP), (rk - CH_TOP, zt),
            (ri + CH_IN, zt), (ri, zt - CH_IN),
            (ri, zcb), (rb, zcb),
            (rb, Z_GROOVE1), (rg, Z_RIDGE_MID + f), (rg, Z_RIDGE_MID - f), (rb, Z_GROOVE0),
            (rb, Z_CODE1), (rc, Z_CODE1), (rc, Z_CODE0), (rb, Z_CODE0)]
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
    return h
def port_slot(z0=-3, z1=PLATE_T + 1, m=0.0):
    return xy_slot(PORT_NOTCH_R0 - m, PLATE_R + 2, PORT_W/2 + m, z0, z1, 0.0)
def pi_window(m=0.0, z0=-3, z1=PLATE_T + 1):
    c = 0.75 + m
    w = box_at(PI_X0 - c, PI_X0 + PI_L + PI_OVERHANG + c, PI_Y0 - c, PI_Y0 + PI_W + c, z0, z1)
    w += box_at(USBC_XC - 7.0 - m, USBC_XC + 7.0 + m, PI_Y0 - 14.0 - m, PI_Y0 + 1, z0, z1)             # USB-C up-angle plug's head
    w += box_at(HDMI_X - 7 - m, HDMI_X + 7 + m, PI_Y0 - 9.5 - m, PI_Y0 + 1, z0, z1)                     # HDMI plug notch
    w += box_at(PI_X0 + PI_L + PI_OVERHANG - 1, PI_X0 + PI_L + PI_OVERHANG + 10.0 + m, PI_Y0 + 3.0 - m, PI_Y0 + 17.5 + m, z0, z1)   # USB-A plug notch
    return w
def sector(az0, az1, r_out, z0, z1):
    """a pie wedge from az0 to az1 (deg, anticlockwise) out to r_out"""
    n = max(2, int(math.ceil((az1 - az0) / 5.0)))
    pts = [(0.0, 0.0)] + [(r_out * math.cos(math.radians(az0 + (az1 - az0) * i / n)), r_out * math.sin(math.radians(az0 + (az1 - az0) * i / n))) for i in range(n + 1)]
    return Pos(0, 0, z0) * extrude(Polygon(*pts, align=None), z1 - z0)
def et_groove_azs():
    """centre azimuths (deg) of every engine-turned groove: fields of square grooves between the plain blocks"""
    out = []
    field = 360.0 / ET_BLOCKS - ET_BLOCK_DEG                        # angular width of one grooved field
    field_arc = math.radians(field) * PLATE_R                       # ... as an arc length at the edge
    n_g = int((field_arc - ET_GROOVE_W - 2 * ET_LAND_MIN) // ET_PITCH) + 1
    for k in range(ET_BLOCKS):
        c = 360.0 * k / ET_BLOCKS + 180.0 / ET_BLOCKS               # centre of the field after block k
        for j in range(n_g):
            s = (j - (n_g - 1) / 2) * ET_PITCH                      # arc offset from the field's centre
            out.append(c + math.degrees(s / PLATE_R))
    return out
def engine_turned_outline(z0, z1):
    """the plate's plan outline: a disc with square-cut vertical grooves in fields between twelve plain blocks,
    cut through the full thickness - laser/waterjet friendly (the grooves run out through the top chamfer)"""
    r_in = PLATE_R - ET_GROOVE_D
    hw = math.degrees(ET_GROOVE_W / 2 / PLATE_R)                    # half the groove's angular width
    events = []                                                     # (az, r) corners in angular order
    for g in sorted(et_groove_azs()):                               # corners in angular order (do not sort the corners themselves)
        events += [(g - hw, PLATE_R), (g - hw, r_in), (g + hw, r_in), (g + hw, PLATE_R)]
    pts = []
    def arc(a0, a1, r):                                             # fill an arc at r with points every <= 1 deg
        n = max(1, int(math.ceil((a1 - a0) / 1.0)))
        for i in range(1, n):
            a = a0 + (a1 - a0) * i / n
            pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
    for i, (a, r) in enumerate(events):
        pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
        a_next = events[(i + 1) % len(events)][0] + (360.0 if i + 1 == len(events) else 0.0)
        if events[(i + 1) % len(events)][1] == r and r == PLATE_R:
            arc(a, a_next, r)
    return Pos(0, 0, z0) * extrude(Polygon(*pts, align=None), z1 - z0)
# ---------------------------------------------------------------- the base plate as the heatsink (the60-thermal-plan.md, section 14)
#   three bodies: the aluminium CORE (web, duct, ribs, r < 75.2), the steel RIM RING (r 75.2-87.7, engine-turned edge,
#   intake and exhaust grooves in its underside, an inward flange on a rebate of the core), and the 1 mm CLOSING PLATE
#   screwed flush into the core's underside.  The pad is a ring under the rim ring.
def rear_wedge(az_half, r_out, z0, z1):
    return sector(-az_half, az_half, r_out, z0, z1)
def speaker_ear_xy():
    """the cradle's two ear screws"""
    cx, cy = SPEAKER_CENTRE
    return [(cx + 22.5 * math.cos(D(a)), cy + 22.5 * math.sin(D(a))) for a in SPEAKER_EAR_AZ]
def duct_islands():
    """solid spots left in the duct under every screw that comes from BELOW (the closing plate's).
    Screws from above stop in the web (BLIND_D 3.0 of the 4.0) and need none."""
    k = None
    for (x, y) in CLOSING_SCREW_XY:
        b = Pos(x, y, 0) * Cylinder(3.5, PLATE_T, align=(Align.CENTER, Align.CENTER, Align.MIN)); k = b if k is None else k + b
    k += box_at(USBC_XC + 9.5 - 0.5, HDMI_X - 9.5 + 0.5, PI_Y0 - 12.0, PI_Y0 - 3.0, 0, PLATE_T)   # fills two dead scraps of channel between the USB-C notch's wall and the HDMI notch's wall
    return k
def channel_ys():
    """centre y of every fin channel: both bands beside the Pi window, from its margin wall outward (v12: the Pi is off-centre)"""
    ys = []
    y = PI_Y0 + PI_W + 0.75 + DUCT_MARGIN + FIN_CH_W/2 + 0.5
    while y + FIN_CH_W/2 <= R_CORE_DUCT - 1.0: ys.append(y); y += FIN_PITCH
    y = PI_Y0 - 0.75 - DUCT_MARGIN - FIN_CH_W/2 - 0.5
    while -y + FIN_CH_W/2 <= R_CORE_DUCT - 1.0: ys.append(y); y -= FIN_PITCH
    return ys
def duct():
    """everything hollow between the web (z 4) and the closing plate (z 1) inside r 72.2"""
    z0, z1 = CLOSING_T, CLOSING_T + DUCT_H
    ro = R_CORE_DUCT - DUCT_WALL                                                        # the duct's outer wall (r 70.2-72.2) ties the core's shoulder to the web
    d = tube(ro, COLLECTOR_R0, z0, z1) - rear_wedge(50.0, 100, z0 - 1, z1 + 1)          # the collector, front and sides
    for yk in channel_ys():                                                             # straight channels either side of the Pi window, front to rear
        d += box_at(-R_CORE_DUCT, R_CORE_DUCT, yk - FIN_CH_W/2, yk + FIN_CH_W/2, z0, z1)
    d += sector(22.0, 52.0, ro, z0, z1) - cyl(PLENUM_R0, z0 - 1, z1 + 1)                # the rear plenum, both sides of the port slot
    d += sector(308.0, 338.0, ro, z0, z1) - cyl(PLENUM_R0, z0 - 1, z1 + 1)
    d += blk(BLOWER_L, BLOWER_W, z0, z0 + BLOWER_H, BLOWER_AZ, BLOWER_R)                  # the blower's envelope, 2 into the web (part not fitted)
    d &= cyl(ro, z0 - 1, z0 + BLOWER_H + 1)
    d -= pi_window(DUCT_MARGIN, z0 - 1, z1 + BLOWER_H)                                  # walls round every through-cut
    d -= carriage_hole(DUCT_MARGIN, z0 - 1, z1 + BLOWER_H)
    d -= port_slot(z0 - 1, z1 + BLOWER_H, DUCT_MARGIN)
    d -= duct_islands()
    return d
def intake_azs():
    """the intake grooves' azimuths: the front and sides, less those that would land on the motor's through-hole or the USB-C plug's notch"""
    out = []
    for i in range(INTAKE_N):
        az = INTAKE_AZ0 + (INTAKE_AZ1 - INTAKE_AZ0) * (i + 0.5) / INTAKE_N
        if abs(az - MOTOR_AZ) <= 14.0: continue
        if abs(az - USBC_NOTCH_AZ) <= 5.0: continue
        out.append(az)
    return out
def intake_grooves(r0, r1):
    """radial grooves in the underside, z 0-2, between r0 and r1, on the intake arc"""
    g = None
    for az in intake_azs():
        b = blk(r1 - r0, INTAKE_W, -1, INTAKE_H, az, (r0 + r1)/2); g = b if g is None else g + b
    return g
def exhaust_grooves(r0, r1):
    g = None
    for az in EXHAUST_AZ:
        b = blk(r1 - r0, INTAKE_W, -1, INTAKE_H, az, (r0 + r1)/2); g = b if g is None else g + b
    return g
def rot_xy(cx, cy, lx, ly, az):
    a = D(az); return (cx + lx * math.cos(a) - ly * math.sin(a), cy + lx * math.sin(a) + ly * math.cos(a))
def top_screw_xy():
    """every M2.5 screw into the plate's top face: converter (2), audio (4), motion (4), servo frame (2), connect bracket (2), speaker cradle (2)"""
    out = []
    for t in (-CONV_HOLE_T, CONV_HOLE_T): out.append(rot_xy(0, 0, CONV_R, t, CONV_AZ))
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append((AUDIO_CENTRE[0] + sx * (AUDIO_L/2 - 3.5), AUDIO_CENTRE[1] + sy * (AUDIO_W/2 - 3.5)))
            out.append(rot_xy(0, 0, MOTION_R + sx * (MOTION_L/2 - 3.5), sy * (MOTION_W/2 - 3.5), MOTION_AZ))
    for sy in (-SERVO_EAR_T, SERVO_EAR_T): out.append(rot_xy(0, 0, SERVO_R0 - 1.5 + (SERVO_L + 1.5)/2, sy, MOTOR_AZ))
    out += speaker_ear_xy()
    out += CB_SCREW_XY
    return out
def base_plate():
    """the aluminium core: r < 75.2, 8 tall; rebate for the ring's flange; recess for the closing plate; the duct; ribs on top"""
    p = cyl(RIM_IN, 0, PLATE_T)
    p -= tube(RIM_IN + 1, R_CORE_DUCT, RIM_STEP_Z, PLATE_T + 1)                          # rebate the ring's flange sits in (r 72.2-75.2, z 4-8)
    p -= cyl(R_CORE_DUCT, -1, CLOSING_T)                                                 # recess for the closing plate (z 0-1)
    p -= duct()
    p -= intake_grooves(R_CORE_DUCT - DUCT_WALL - 0.5, RIM_IN + 0.5)                     # the grooves continue through the shoulder and the duct wall into the collector
    p -= exhaust_grooves(R_CORE_DUCT - DUCT_WALL - 0.5, RIM_IN + 0.5)
    p -= carriage_hole(); p -= port_slot(); p -= pi_window()
    for (x, y) in CLOSING_SCREW_XY:                                                     # M2.5 tapped for the closing plate's countersunk screws
        p -= Pos(x, y, -1) * Cylinder(1.0, CLOSING_T + 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for az in RING_SCREW_AZ:                                                            # M3 csk from below through the shoulder into the ring's flange
        p -= csk_hole(3.4, 0, RIM_STEP_Z, az, RING_SCREW_R)
    for (x, y) in top_screw_xy():                                                       # everything bolted to the plate top: M2.5 tapped, blind, 3.0 into the 4.0 web
        p -= Pos(x, y, PLATE_T - BLIND_D) * Cylinder(1.0, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(GND_BOND_XY[0], GND_BOND_XY[1], PLATE_T - BLIND_D) * Cylinder(1.25, BLIND_D + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))   # chassis ground: M3 tapped blind, masked bare pad round it
    for az in RIB_AZ:                                                                   # ribs on the top face
        p += blk(RIB_R1 - RIB_R0, RIB_T, PLATE_T - 0.01, PLATE_T + RIB_H, az, (RIB_R0 + RIB_R1)/2)
    return p
def rim_ring():
    """the steel ring: engine-turned edge, chamfers, the flange onto the core, intake undercut and grooves, exhaust grooves, the fixing holes"""
    p = engine_turned_outline(0, PLATE_T)
    c = PLATE_CHAMFER
    p -= revolve_profile([(PLATE_R - c, -0.01), (PLATE_R + 1, -0.01), (PLATE_R + 1, c + 0.01), (PLATE_R, c)])                                  # 1.0 chamfer, bottom outer edge
    p -= revolve_profile([(PLATE_R, PLATE_T - c), (PLATE_R + 1, PLATE_T - c - 0.01), (PLATE_R + 1, PLATE_T + 0.01), (PLATE_R - c, PLATE_T + 0.01)])   # 1.0 chamfer, top outer edge
    p -= cyl(RIM_IN, -1, PLATE_T + 1)
    p += tube(RIM_IN + 0.01, R_CORE_DUCT, RIM_STEP_Z, PLATE_T)                             # the inward flange, in the core's rebate
    p -= tube(PLATE_R + 2, INTAKE_UNDERCUT_R, -1, INTAKE_UNDERCUT_H) - rear_wedge(360 - INTAKE_AZ1, 100, -2, INTAKE_UNDERCUT_H + 1)   # the intake undercut, front and sides
    p -= intake_grooves(RIM_IN - 0.5, PLATE_R + 2)
    p -= exhaust_grooves(RIM_IN - 0.5, PAD_R + 1.0)                                       # the exhaust grooves stop under the pad's void, not at the edge
    p -= port_slot(); p -= carriage_hole()                                            # the carriage's shoe drops through the ring at 90 deg too (r 46-85.5)
    for t in (-1, 1):                                                                   # clean the slot's mouth: no sliver of engine-turning within 3 of the slot's edge
        x0 = math.sqrt(PLATE_R**2 - (PORT_W/2 + 3.0)**2) - ET_GROOVE_D - 0.3
        p -= box_at(x0, PLATE_R + 2, t * (PORT_W/2), t * (PORT_W/2 + 3.0), -1, PLATE_T + 1) if t > 0 else box_at(x0, PLATE_R + 2, -(PORT_W/2 + 3.0), -PORT_W/2, -1, PLATE_T + 1)
    for az in PLATE_SCREW_AZ:                                                           # the structure's plate screws, csk from below
        p -= csk_hole(3.4, 0, PLATE_T, az, PILLAR_R)
    for t in (-PORT_TAB_T, PORT_TAB_T):                                                 # port-face rail: Ø1.6, tapped M2
        p -= zbore(1.6, -1, PLATE_T + 1, 0.0, PORT_TAB_R, t)
    for az in RING_SCREW_AZ:                                                            # M3 tapped in the flange, blind from below
        p -= zbore(2.5, RIM_STEP_Z - 0.1, PLATE_T - 0.6, az, RING_SCREW_R)
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
    """a plain ring under the rim ring (thermal plan: the pad is no longer part of the airflow), cut away at the exhaust"""
    p = frustum(PAD_R - 0.5, PAD_R, -PAD_T, 0.0) - cyl(PAD_RIN, -3, 1)
    p -= port_slot(-3, 1)
    p -= blk(20.0, 15.0, -3, 1, 0.0, PLATE_R + 3.0, t=PORT_BARREL_T)     # through-pocket under the barrel plug body
    for az0, az1 in EXHAUST_VOID:
        p -= sector(az0, az1, 100, -3, 1) - cyl(74.0, -4, 2)             # the exhaust void: the grooves open to the desk here
    return p

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
    wheel posts' webs, the encoder tower or the LRA pad"""
    out = []
    n = int(round(360.0 / SLIT_PITCH_DEG))
    for i in range(n):
        az = SLIT_PITCH_DEG / 2 + SLIT_PITCH_DEG * i
        def near(a, w): return abs(((az - a + 180) % 360) - 180) <= w
        if near(MOTOR_AZ, 17) or near(ENC_AZ, 5) or near(LRA_AZ, 6): continue
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
    # encoder tower against the wall
    s += blk(5.0, 9.0, Z_PLATE_TOP - 0.01, ENC_TOWER_TOP, ENC_AZ, R_WALL_IN + 0.5 - 2.5)                  # 5 thick tower against the wall
    # LRA bonding pad on the inside of the wall
    s += blk(1.3, 11.5, 8.0, 18.0, LRA_AZ, R_WALL_IN - 0.6)
    # three M3 pillars on the wall for the plate screws from below (v12: the deck and its two extra pillars are gone)
    for az in PILLAR_AZ:
        s += zbore(7.0, Z_PLATE_TOP - 0.01, PILLAR_TOP, az, PILLAR_R)
        s += blk(R_WALL_IN + 0.5 - PILLAR_R, 7.0, Z_PLATE_TOP - 0.01, PILLAR_TOP, az, (PILLAR_R + R_WALL_IN + 0.5)/2)
        s -= zbore(INSERT_M3_D, Z_PLATE_TOP - 1, Z_PLATE_TOP + INSERT_M3_SHORT_L + 0.3, az, PILLAR_R)
        s -= polar(az, PILLAR_R, Z_PLATE_TOP + INSERT_M3_SHORT_L + 0.29) * Cone(INSERT_M3_D/2, 0.01, INSERT_M3_D/2, align=(Align.CENTER, Align.CENTER, Align.MIN))   # PRINT: 45 deg roof on the blind hole
    # cuts
    s -= motor_relief()
    for az in WHEEL_AZ:
        s -= zbore(BUSH_D + 0.1, Z_PLATE_TOP - 1, Z_POST_TOP + 1, az, BUSH_R)
        s -= blk(6.0, WHEEL_OD + 2.0, Z_POST_TOP - 0.3, Z_SEAT_TOP + 1, az, R_WALL_OUT)   # open-topped window: the wheel reaches through the wall into the groove; no bridge to print
        s -= blk(R_WALL_IN + 1.0 - (R_SEAT_IN - 1.0), WHEEL_OD + 2.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, az, (R_SEAT_IN - 1.0 + R_WALL_IN + 1.0)/2)   # PRINT (Ryan, 5 Sep): the seat flange above the wheel is removed entirely - nothing needs it, and it was a shelf hanging over the window
    for az in NUB_AZ:                                                          # three locating nubs around the glass edge, under the lens overhang
        s += zbore(2.0, Z_SEAT_TOP - 0.01, Z_GLASS1 - 0.3, az, PANEL_DISC_R + 0.15 + 1.0)
    s -= blk(2.5, 32.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, 0.0, 67.5, t=-4.0)     # flex slot through the seat at 0 deg (panel flex at t -12, touch tail at +6)
    s -= blk(6.0, 32.0, Z_SEAT_TOP - 0.6, Z_SEAT_TOP + 1, 0.0, 65.0, t=-4.0)   # the flex passes over the seat's top face here, 0.6 deep
    # encoder pocket (board + package) looking outward through a window in the wall
    r_face = R_BORE - ENC_GAP - 1.63
    s -= blk(1.2, 8.4, ENC_BOARD_Z0 - 0.4, Z_SEAT_TOP + 1, ENC_AZ, r_face - 0.6)             # the board's slot, open right through the seat (PRINT: no roof; the board drops in from above before the display goes on; the lens caps it)
    s += blk(ENC_RIB_H, ENC_RIB_W, ENC_BOARD_Z0 + 2.0, ENC_TOWER_TOP - 0.5, ENC_AZ, r_face - 0.6 - 0.6 + ENC_RIB_H/2)   # crush rib on the slot's inner face: the board is a friction fit, so it stays put while the assembly is upside down
    s -= blk(4.0, 8.4, ENC_BOARD_Z0 - 0.4, Z_CODE0 - 0.6, ENC_AZ, r_face - 0.6 - 2.0)         # v12: notch through the tower's inner face under the sensor - the board's leads leave at its bottom
    s -= blk(ENC_GAP + 1.63 + 0.3 + (R_WALL_OUT - R_BORE) + 1.0, 5.6, Z_CODE0 - 0.4, Z_CODE1 + 0.4, ENC_AZ, R_WALL_OUT + 0.5 - (ENC_GAP + 1.63 + 0.3 + (R_WALL_OUT - R_BORE) + 1.0)/2)
    s -= blk(R_WALL_OUT - R_WALL_IN + 2.0, 5.6, Z_CODE1 + 0.3, Z_SEAT_TOP + 1, ENC_AZ, (R_WALL_IN + R_WALL_OUT)/2)   # the wall above the encoder window opened to the top: no bridge to print
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
        b += box_at(x - 3.5, x + 3.5, min(y, CB_T0), max(y, CB_T0), Z_PLATE_TOP, z1) & clip & cyl(CB_R - CB_L/2 + 2.5, 0, 20)
        b -= Pos(x, y, Z_PLATE_TOP - 1) * Cylinder(1.4, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
        b -= Pos(x, y, z1 - 1.0) * Cone(1.4, 2.7, 1.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b -= blk(3.0, 6.0, Z_PLATE_TOP - 1, z1 + 1, 0.0, PORT_TAB_R, t=-PORT_TAB_T)                            # clear of the rail's M2 screw head at t -26
    b -= box_at(0, 45.5, -40, -21.0, 0, 20)                                                                # the -y inner corner is cut back to x 45.5: the audio's USB-A plug (to x 45, from z 10.5) sits there
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
    out = {"audio_parts_ENVELOPE": P * Pos(-6, 0, 0) * Box(20.0, AUDIO_W - 6, AUDIO_H - 1.6 - BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN))}
    out.update(bodies_of("ESS_ES9219Q_WQFN40_5x5.step", P * Pos(12, 0, 0), prefix="es9219q_"))
    return out
def motion_board():
    return polar(MOTION_AZ, MOTION_R, Z_PLATE_TOP + BOARD_STANDOFF) * Box(MOTION_L, MOTION_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
def motion_parts():
    zt = Z_PLATE_TOP + BOARD_STANDOFF + 1.6; P = polar(MOTION_AZ, MOTION_R, zt)
    out = {}
    out.update(bodies_of("TMC6300-LA-T_QFN20_3x3.step", P * Pos(6, 5, 0), prefix="tmc6300_"))
    out.update(bodies_of("TI_DRV2605L_VSSOP10_DGS.step", P * Pos(6, -5, 0), prefix="drv2605l_"))
    out["motion_connectors_ENVELOPE"] = P * Pos(-8, 0, 0) * Box(11.0, 24.0, MOTION_H - 1.6 - BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN))   # connectors on the inner (motor) side
    return out
def converter_body():
    """the 12 V -> 5 V module on the PLATE (thermal plan rule 15), on a 0.5 gap pad, tangential in the front crescent"""
    return {"converter_ENVELOPE": polar(CONV_AZ, CONV_R, Z_PLATE_TOP + CONV_PAD_T) * Box(CONV_W, CONV_L, CONV_H, align=(Align.CENTER, Align.CENTER, Align.MIN)),
            "converter_gap_pad_ASSUMED": polar(CONV_AZ, CONV_R, Z_PLATE_TOP) * Box(CONV_W, CONV_L, CONV_PAD_T, align=(Align.CENTER, Align.CENTER, Align.MIN))}
def washer_bodies():
    """the 1.0 washers under the audio and motion boards (ASSUMED nylon)"""
    out = {}
    pts = [(AUDIO_CENTRE[0] + sx * (AUDIO_L/2 - 3.5), AUDIO_CENTRE[1] + sy * (AUDIO_W/2 - 3.5)) for sx in (-1, 1) for sy in (-1, 1)]
    pts += [rot_xy(0, 0, MOTION_R + sx * (MOTION_L/2 - 3.5), sy * (MOTION_W/2 - 3.5), MOTION_AZ) for sx in (-1, 1) for sy in (-1, 1)]
    for i, (x, y) in enumerate(pts):
        out[f"board_washer_{i}"] = Pos(x, y, Z_PLATE_TOP) * (Cylinder(2.5, BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.35, 5))
    return out

# ---------------------------------------------------------------- encoder, LRA
def encoder_board():
    r_face = R_BORE - ENC_GAP - 1.63
    return blk(1.0, 8.0, ENC_BOARD_Z0, ENC_BOARD_Z0 + ENC_BOARD_H, ENC_AZ, r_face - 0.5)   # 8 x 10 from 13.5 to 23.5: through the seat's slot, 2.5 under the seat's top face; the lens caps it; leads at the bottom
def encoder_bodies():
    r_face = R_BORE - ENC_GAP - 1.63
    place = polar(ENC_AZ, r_face, (Z_CODE0 + Z_CODE1)/2) * Rot(0, 90, 0) * Rot(0, 0, 90)
    return bodies_of("Broadcom_AEDR-8300-1K2_encoder.step", place, prefix="encoder_")
def lra_bodies():
    place = polar(LRA_AZ, R_WALL_IN - 1.2 - 0.07, 13.0) * Rot(0, -90, 0)
    return bodies_of("Vybronics_VLV101040A_LRA.step", place, prefix="lra_")

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
         "encoder_board": encoder_board(), "usbc_board": usbc_board(), "jack_board": jack_board(), "barrel_board": barrel_board(),
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
    b["pad"] = pad()
    return b
