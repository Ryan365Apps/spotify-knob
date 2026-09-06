"""the 60 — v10 geometry.  build123d algebra mode.

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
    """the panel's flex from the component area to the adapter, and the touch tail beside it (ASSUMED route,
    bend radius 1.0).  Device frame: the tab is at 0 deg (+x)."""
    out = {}
    t0 = -12.0                                    # tangential centre of the panel flex in the slot (tail beside it)
    zf = Z_GLASS0 - PANEL_FPC_T
    # 1. on the glass back, from the component area edge out to the glass edge
    out["panel_flex_1"] = box_at(PANEL_COMP_OFFSET + PANEL_COMP_L/2 - 2.0, PANEL_TAB_R - 0.75, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, zf, Z_GLASS0)
    # 2. straight out past the edge, then down through the slot
    r_out = 67.9
    out["panel_flex_2"] = box_at(PANEL_TAB_R - 0.75, r_out, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, zf, Z_GLASS0)
    z_low = Z_DECK1 + ADAPTER_T + 2.0            # the adapter's flex connector height (ASSUMED 4 mm connector, entry at its middle)
    out["panel_flex_3"] = box_at(r_out, r_out + PANEL_FPC_T, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, z_low, zf)
    # 3. inward under the seat to the adapter's connector at its +x edge
    x_conn = ADAPTER_CENTRE[0] + ADAPTER_L/2 - 1.0
    out["panel_flex_4"] = box_at(x_conn, r_out + PANEL_FPC_T, t0 - PANEL_FPC_W/2, t0 + PANEL_FPC_W/2, z_low - PANEL_FPC_T, z_low)
    # touch tail (ASSUMED 8 wide) beside it, same route, ending at the touch controller's side via a loop (drawn to the slot only)
    t1 = 6.0
    out["touch_tail_ASSUMED"] = box_at(PANEL_TAB_R - 6.0, r_out - 0.5, t1 - TOUCH_TAIL_W/2, t1 + TOUCH_TAIL_W/2, zf, Z_GLASS0)
    out["touch_tail_ASSUMED_down"] = box_at(r_out - 0.5, r_out - 0.5 + PANEL_FPC_T, t1 - TOUCH_TAIL_W/2, t1 + TOUCH_TAIL_W/2, z_low, zf)
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
def fan_hole_xy():
    """device-frame rectangle of the fan hole in the deck (fan + 2 mm)"""
    return (PI_X0 + FAN_X0 - 2, PI_X0 + FAN_X0 + FAN_SIZE + 2, PI_Y0 + FAN_Y0 - 2, PI_Y0 + FAN_Y0 + FAN_SIZE + 2)
def pi_holes_xy():
    return [(PI_X0 + x, PI_Y0 + y) for x, y in PI_HOLES]
def deck_legs_xy():
    """three of the Pi's four holes: the USB-A corner (61.5, 3.5) is where the speaker sits"""
    return [(PI_X0 + x, PI_Y0 + y) for x, y in PI_HOLES if not (x > 50 and y < 10)]
HDMI0_X = PI_X0 + PI_HDMI0_X           # -16.5 device x of the HDMI0 socket
def pi_plug_bodies():
    out = {}
    # PC data cable: straight USB-C plug in the Pi's USB-C (ASSUMED 8.3 x 6.5 x 25), leaving toward 270 deg
    xc = PI_X0 + (PI_USBC[0] + PI_USBC[1])/2
    zc = PI_Z0 + 0.34 + 4.6/2
    out["usbc_plug_pi_ENVELOPE"] = box_at(xc - 4.15, xc + 4.15, PI_Y0 - 25.0, PI_Y0 + 0.5, zc - 3.25, zc + 3.25)
    # HDMI ribbon: up-angle micro-HDMI plug board at HDMI0 (ASSUMED 12 x 8 x 5), ribbon up through the deck slot, along the deck to the adapter's socket
    zp0 = PI_Z_TOP
    out["hdmi_plug_micro_ENVELOPE"] = box_at(HDMI0_X - 6, HDMI0_X + 6, PI_Y0 - 8.0, PI_Y0 + 0.5, zp0, zp0 + 5.0)
    yr = PI_Y0 - 6.5                                      # ribbon plane (y) where it rises
    out["hdmi_ribbon_1"] = box_at(HDMI0_X - 10, HDMI0_X + 10, yr - 0.3, yr, zp0 + 5.0, Z_DECK1 + 0.3)
    out["hdmi_ribbon_2"] = box_at(HDMI0_X - 10, ADAPTER_CENTRE[0] - 10, yr - 0.3, yr, Z_DECK1 + 0.3, Z_DECK1 + 0.6)   # not used: placeholder removed below
    del out["hdmi_ribbon_2"]
    # on the deck: run along -x at y = yr, under the adapter board, to the HDMI-A plug board at the adapter's -x edge socket
    xw = ADAPTER_CENTRE[0] - ADAPTER_L/2
    out["hdmi_ribbon_2"] = box_at(xw - 21.0, HDMI0_X + 10, yr - 0.3, yr, Z_DECK1 + 0.3, Z_DECK1 + 0.6)
    out["hdmi_plug_A_ENVELOPE"] = box_at(xw - 21.0, xw + 0.5, -44.0, -32.0, Z_DECK1, Z_DECK1 + 6.0)
    # header housing: 2 x 5 crimp housing on pins 1-10 (5 V, GND, UART) - ASSUMED 12.7 x 5.1 x 9 on the header's base
    hx0, hx1, hy0, hy1, hh = PI_HEADER
    out["header_housing_ENVELOPE"] = pi_place() * box_at(hx0, hx0 + 12.7, hy0, hy1, PI_T + 2.5, PI_T + 2.5 + 9.0)
    # audio board's USB: right-angle USB-A plug in the upper socket of the rear stack nearest 270 deg (ASSUMED 9 protrusion x 14 x 8)
    out["usba_plug_ENVELOPE"] = box_at(PI_X0 + PI_L + PI_OVERHANG, PI_X0 + PI_L + PI_OVERHANG + 9.0, PI_Y0 + 4.0, PI_Y0 + 16.5, PI_Z0 + 9.0, PI_Z0 + 16.0)
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
def carriage_hole():
    d = MOTOR_OD + 2 * 1.0 + 1.5
    h = zbore(d, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R)
    h += zbore(d, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R - CLUTCH_LIFT)
    h += blk(CLUTCH_LIFT, d, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R - CLUTCH_LIFT/2)
    h += blk(CARRIAGE_TAB_T + CLUTCH_LIFT + 1.5 + 4.0, CARRIAGE_TAB_W + 1.5, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R - MOTOR_OD/2 - 1.0 - (CARRIAGE_TAB_T + CLUTCH_LIFT + 4.0)/2)   # tab slot
    return h
def port_slot(z0=-3, z1=PLATE_T + 1):
    return xy_slot(PORT_NOTCH_R0, PLATE_R + 2, PORT_W/2, z0, z1, 0.0)
def pi_window():
    c = 0.75
    w = box_at(PI_X0 - c, PI_X0 + PI_L + PI_OVERHANG + c, PI_Y0 - c, PI_Y0 + PI_W + c, -3, PLATE_T + 1)
    xc = PI_X0 + (PI_USBC[0] + PI_USBC[1])/2
    w += box_at(xc - 5.0, xc + 5.0, PI_Y0 - 26.0, PI_Y0 + 1, -3, PLATE_T + 1)                 # USB-C plug notch
    w += box_at(HDMI0_X - 7, HDMI0_X + 7, PI_Y0 - 9.0, PI_Y0 + 1, -3, PLATE_T + 1)               # HDMI plug notch
    w += box_at(PI_X0 + PI_L + PI_OVERHANG - 1, PI_X0 + PI_L + PI_OVERHANG + 10.0, PI_Y0 + 3.0, PI_Y0 + 17.5, -3, PLATE_T + 1)   # USB-A plug notch
    return w
def base_plate():
    p = cyl(PLATE_R, 0, PLATE_T)
    p -= carriage_hole()
    p -= port_slot()
    p -= pi_window()
    for az in PLATE_SCREW_AZ:
        p -= csk_hole(3.4, 0, PLATE_T, az, PILLAR_R)
    for sx in (-22.5, 22.5):                                   # speaker cradle ears
        p -= csk_xy(3.4, SPEAKER_CENTRE[0] + sx, SPEAKER_CENTRE[1], 0, PLATE_T)
    p -= zbore(3.4, -1, PLATE_T + 1, 0.0, 50.0, -20.0)         # ground-bond screw beside the slot
    for t in (-16.0, 16.0):                                    # port-face ears
        p -= zbore(1.6, -1, PLATE_T + 1, 0.0, 65.0, t)
    return p
def pad():
    p = frustum(PAD_R - 0.3, PAD_R, -PAD_T, 0.0)
    p -= port_slot(-3, 1)
    p -= blk(20.0, 15.0, -3, 1, 0.0, 80.0, t=PORT_BARREL_T)     # through-pocket under the barrel plug body
    return p

# ---------------------------------------------------------------- the internal structure
def motor_relief(engaged=True):
    rc = MOTOR_R
    k = zbore(MOTOR_BASE_OD + 2.0, Z_MOTOR_BOT - 0.5, Z_BELL_BOT - 0.01, MOTOR_AZ, rc)
    k += zbore(MOTOR_OD + 2 * MOTOR_CLEAR, Z_BELL_BOT - 0.5, Z_MOTOR_TOP + 0.6, MOTOR_AZ, rc)
    return k
def port_azs():
    out = []
    for i in range(PORT_N):
        az = 7.5 + 15.0 * i
        def near(a, w): return abs(((az - a + 180) % 360) - 180) <= w
        if near(MOTOR_AZ, 20) or near(0.0, 20) or near(ENC_AZ, 8) or near(LRA_AZ, 9): continue
        if any(near(a, 5) for a in PILLAR_AZ): continue
        out.append(az)
    return out
INSERT_M3_SHORT_L = 4.0
def structure():
    s = tube(R_WALL_OUT, R_WALL_IN, Z_PLATE_TOP, Z_SEAT_TOP)                   # the wall
    s += tube(R_WALL_OUT, R_SEAT_IN, Z_SEAT_BOT, Z_SEAT_TOP)                   # the seat flange
    s += tube(R_LIP_OUT, R_WALL_OUT - 0.01, Z_LIP0, Z_LIP1)                    # diffuser-retaining lip
    for az in WHEEL_AZ:                                                        # wheel posts, webbed to the wall
        s += zbore(WHEEL_POST_D, Z_PLATE_TOP - 0.01, Z_POST_TOP, az, BUSH_R)
        s += blk(R_WALL_IN + 0.5 - BUSH_R, 6.0, Z_PLATE_TOP - 0.01, Z_POST_TOP - 2.0, az, (BUSH_R + R_WALL_IN + 0.5)/2)
    # encoder tower against the wall
    s += blk(R_WALL_IN + 0.5 - 66.0, 9.0, Z_PLATE_TOP - 0.01, Z_CODE1 + 0.7, ENC_AZ, (66.0 + R_WALL_IN + 0.5)/2)
    # LRA bonding pad on the inside of the wall
    s += blk(1.3, 11.5, 8.0, 18.0, LRA_AZ, R_WALL_IN - 0.6)
    # six M3 pillars: deck screws from above; three of them also take the plate screws from below
    for az in PILLAR_AZ:
        s += zbore(7.0, Z_PLATE_TOP - 0.01, Z_DECK0, az, PILLAR_R)
        s += blk(R_WALL_IN + 0.5 - PILLAR_R, 7.0, Z_PLATE_TOP - 0.01, Z_DECK0, az, (PILLAR_R + R_WALL_IN + 0.5)/2)
        s -= zbore(INSERT_M3_D, Z_DECK0 - INSERT_M3_SHORT_L - 0.3, Z_DECK0 + 1, az, PILLAR_R)
        if az in PLATE_SCREW_AZ:
            s -= zbore(INSERT_M3_D, Z_PLATE_TOP - 1, Z_PLATE_TOP + INSERT_M3_SHORT_L + 0.3, az, PILLAR_R)
    # cuts
    s -= motor_relief()
    for az in WHEEL_AZ:
        s -= zbore(BUSH_D + 0.1, Z_PLATE_TOP - 1, Z_POST_TOP + 1, az, BUSH_R)
        s -= blk(6.0, WHEEL_OD + 2.0, Z_POST_TOP - 0.3, Z_SEAT_BOT - 0.01, az, R_WALL_OUT)   # window: the wheel reaches through the wall into the groove
    for az in NUB_AZ:                                                          # three locating nubs around the glass edge, under the lens overhang
        s += zbore(2.0, Z_SEAT_TOP - 0.01, Z_GLASS1 - 0.3, az, PANEL_DISC_R + 0.15 + 1.0)
    s -= blk(2.5, 32.0, Z_SEAT_BOT - 1, Z_SEAT_TOP + 1, 0.0, 67.5, t=-4.0)     # flex slot through the seat at 0 deg (panel flex at t -12, touch tail at +6)
    s -= blk(6.0, 32.0, Z_SEAT_TOP - 0.6, Z_SEAT_TOP + 1, 0.0, 65.0, t=-4.0)   # the flex passes over the seat's top face here, 0.6 deep
    # encoder pocket (board + package) looking outward through a window in the wall
    r_face = R_BORE - ENC_GAP - 1.63
    s -= blk(1.2, 8.4, Z_CODE0 - 0.4, Z_CODE1 + 0.4, ENC_AZ, r_face - 0.6)
    s -= blk(ENC_GAP + 1.63 + 0.3 + (R_WALL_OUT - R_BORE) + 1.0, 5.6, Z_CODE0 - 0.4, Z_CODE1 + 0.4, ENC_AZ, R_WALL_OUT + 0.5 - (ENC_GAP + 1.63 + 0.3 + (R_WALL_OUT - R_BORE) + 1.0)/2)
    for az in port_azs():
        s -= rbore(PORT_D, R_WALL_IN - 1, R_WALL_OUT + 1, az, PORT_Z)
    # the port face stands in the plate slot below the wall: relieve the wall's foot over the slot so the face's ears fit
    s -= blk(4.0, PORT_W + 12.0, Z_PLATE_TOP - 1, Z_PLATE_TOP + 1.6, 0.0, R_WALL_IN + 1.0)
    return s
def internal_structure():
    return structure()

# ---------------------------------------------------------------- the display bonds straight onto the seat (double-sided foam tape, ASSUMED 0.5)
def bond_tape():
    return tube(PANEL_DISC_R - 0.5, R_SEAT_IN + 0.5, Z_SEAT_TOP, Z_GLASS0) - blk(6.0, 32.0, Z_SEAT_TOP - 1, Z_GLASS0 + 1, 0.0, 65.0, t=-4.0)

# ---------------------------------------------------------------- diffuser, LED ring
def halo_diffuser():
    c = DIFF_CHAMFER
    lean = (R_DIFF_OUT_TOP - R_DIFF_OUT_BOT) / HALO_H
    return revolve_profile([(R_DIFF_IN, HALO_Z0), (R_DIFF_OUT_BOT, HALO_Z0),
                            (R_DIFF_OUT_TOP - c * lean, HALO_Z1 - c), (R_DIFF_OUT_TOP - c, HALO_Z1), (R_DIFF_IN, HALO_Z1)])
def led_flex():
    return tube(R_LED_FLEX_OUT, R_LED_FLEX_IN, Z_PLATE_TOP, Z_PLATE_TOP + 0.2)
def led_bodies():
    out = {}
    base = bought_solids("OPSCO_SK6812SIDE-A_led_4020.step")
    pk = [s for l, s in base.items() if "package" in l][0]
    for i in range(LED_N):
        az = 360.0 * i / LED_N
        out[f"led_{i:02d}"] = polar(az, LED_R, Z_PLATE_TOP + 0.2) * Rot(0, 0, 90) * pk
    return out

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

# ---------------------------------------------------------------- motor, carriage, clutch (servo on the deck, tall tab)
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
Z_SERVO0 = Z_DECK1 + SERVO_TRAY_T
def servo_place():
    return polar(MOTOR_AZ, SERVO_R0, Z_SERVO0)
def servo_bodies():
    return bodies_of("AGFRC_C1p5CLS_PRO_linear_servo.step", servo_place(), prefix="servo_")
def servo_mount():
    """tray the servo lies in on the deck: floor, two side walls, an inner end wall; open toward the tab"""
    L = SERVO_L + 1.5
    m = Box(L, SERVO_W + 2.0, SERVO_TRAY_T, align=(Align.MIN, Align.CENTER, Align.MIN))
    m += Pos(0, 0, SERVO_TRAY_T) * Box(L, SERVO_W + 2.0, SERVO_H + 0.5, align=(Align.MIN, Align.CENTER, Align.MIN))
    m -= Pos(1.5, 0, SERVO_TRAY_T - 0.01) * Box(L, SERVO_W + 0.4, SERVO_H + 1.0, align=(Align.MIN, Align.CENTER, Align.MIN))
    m -= Pos(-0.1, 0, SERVO_TRAY_T + 1.0) * Box(1.8, 6.0, 4.0, align=(Align.MIN, Align.CENTER, Align.MIN))
    for sy in (-14.0, 14.0):
        m -= Pos(L/2, sy, -1) * Cylinder(1.4, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))      # M2.5 into deck inserts
    m = Pos(-1.5, 0, 0) * m
    return polar(MOTOR_AZ, SERVO_R0, Z_DECK1) * m

# ---------------------------------------------------------------- speaker
def speaker_place():
    return Pos(SPEAKER_CENTRE[0], SPEAKER_CENTRE[1], Z_PLATE_TOP)
def speaker_bodies():
    return bodies_of("Soberton_SP-4005-1_speaker_D40.step", speaker_place(), keep=lambda l: "keepout" not in l, prefix="")
def speaker_cradle():
    """ring under the speaker's flange (flange at 4.45-5.95 above its rear face), three snap fingers over it, ears on the x axis"""
    c = tube(20.5, 18.3, 0, 4.45)
    for a in (80, 200, 320):                                                   # fingers away from the wall side (az ~290 from the speaker) and the encoder tower
        c += Rot(0, 0, a) * (Pos(20.9, 0, 4.44) * Box(2.6, 3.0, 2.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
                             + Pos(19.75, 0, 6.05) * Box(1.0, 3.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for sx in (-22.5, 22.5):
        c += Pos(sx, 0, 0) * Cylinder(3.5, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c += Pos(sx * 20.5/22.5, 0, 0) * Box(5.0, 6.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c -= Pos(sx, 0, -1) * Cylinder(1.7, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return speaker_place() * c

# ---------------------------------------------------------------- mezzanine deck and its boards
def deck():
    d = cyl(70.0, Z_DECK0, Z_DECK1)
    if COOLER_FAN_FITTED:
        x0, x1, y0, y1 = fan_hole_xy()
        d -= box_at(x0, x1, y0, y1, Z_DECK0 - 1, Z_DECK1 + 1)                  # fan hole
    for az in WHEEL_AZ: d -= zbore(WHEEL_POST_D + 1.0, Z_DECK0 - 1, Z_DECK1 + 1, az, BUSH_R)
    d -= blk(6.0, 10.0, Z_DECK0 - 1, Z_DECK1 + 1, ENC_AZ, 68.0)                # encoder tower notch
    d -= blk(CARRIAGE_TAB_T + CLUTCH_LIFT + 0.6, CARRIAGE_TAB_W + 0.6, Z_DECK0 - 1, Z_DECK1 + 1, MOTOR_AZ, TAB_INNER_R + (CARRIAGE_TAB_T - CLUTCH_LIFT)/2)   # tab slot (tab moves inward when released)
    yr = PI_Y0 - 6.5
    d -= box_at(HDMI0_X - 11.0, HDMI0_X + 11.0, yr - 1.8, yr + 1.2, Z_DECK0 - 1, Z_DECK1 + 1)   # HDMI ribbon slot
    for az in PILLAR_AZ: d -= zbore(3.4, Z_DECK0 - 1, Z_DECK1 + 1, az, PILLAR_R)                  # deck screws
    # legs down to the Pi's holes (the Pi hangs from them: M2.5 inserts in the leg ends)
    for (x, y) in deck_legs_xy():
        d += Pos(x, y, PI_Z_TOP) * Cylinder(5.5/2, Z_DECK0 + 0.01 - PI_Z_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))
        d -= Pos(x, y, PI_Z_TOP - 1) * Cylinder(3.2/2, 4.0 + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # inserts for the boards and the servo tray (M2.5 bosses are just holes in the 1.5 deck: inserts go into 3 mm bosses)
    for (x, y) in board_holes():
        d += Pos(x, y, Z_DECK1 - 0.01) * Cylinder(3.0, BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN))
        d -= Pos(x, y, Z_DECK0 - 1) * Cylinder(3.2/2, 5.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return d
def board_holes():
    out = []
    for (cx, cy), L, W in ((ADAPTER_CENTRE, ADAPTER_L, ADAPTER_W),):
        for sx in (-1, 1):
            for sy in (-1, 1): out.append((cx + sx * (L/2 - 3.5), cy + sy * (W/2 - 3.5)))
    for az, r, L, W in ((AUDIO_AZ, AUDIO_R, AUDIO_L, AUDIO_W), (MOTION_AZ, MOTION_R, MOTION_L, MOTION_W)):
        aa = D(az)
        for sx in (-1, 1):
            for sy in (-1, 1):
                lx, ly = r + sx * (L/2 - 3.5), sy * (W/2 - 3.5)
                out.append((lx * math.cos(aa) - ly * math.sin(aa), lx * math.sin(aa) + ly * math.cos(aa)))
    a = D(MOTOR_AZ)
    for sy in (-14.0, 14.0):                                                   # servo tray
        r = SERVO_R0 - 1.5 + (SERVO_L + 1.5)/2
        out.append((r * math.cos(a) - sy * math.sin(a), r * math.sin(a) + sy * math.cos(a)))
    return out
def board_on_deck(centre, L, W, T=1.6, parts_h=0.0, parts_inset=4.0, az=0.0):
    cx, cy = centre
    b = Pos(cx, cy, Z_DECK1 + BOARD_STANDOFF) * Rot(0, 0, az) * Box(L, W, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b
def adapter_board(): return board_on_deck(ADAPTER_CENTRE, ADAPTER_L, ADAPTER_W, ADAPTER_T)
def adapter_parts():
    out = {}
    cx, cy = ADAPTER_CENTRE; zt = Z_DECK1 + BOARD_STANDOFF + ADAPTER_T
    xe = cx + ADAPTER_L/2                                                      # the +x edge faces the flex slot at 0 deg
    xw = cx - ADAPTER_L/2                                                      # the -x edge: HDMI socket (ASSUMED position)
    out["adapter_hdmi_socket_ENVELOPE"] = box_at(xw, xw + 12.0, -44.0, -32.0, zt, zt + ADAPTER_PARTS_H)
    out["adapter_flex_connector_ENVELOPE"] = box_at(xe - 6.0, xe, -12.0 - 9.0, -12.0 + 9.0, zt, zt + 4.0)
    out["adapter_parts_ENVELOPE"] = box_at(cx - 15, cx + 15, cy - 19, cy + 16, zt, zt + 2.0)
    # touch controller stacked on the adapter's low region (BUILD CHANGE, ASSUMED)
    out["touch_board_ASSUMED"] = box_at(cx - 15, cx + 15, cy - 30, cy - 10, zt + TOUCH_STACK_H, zt + TOUCH_STACK_H + 1.6)
    out["touch_parts_ENVELOPE"] = box_at(cx - 12, cx + 12, cy - 27, cy - 13, zt + TOUCH_STACK_H + 1.6, zt + TOUCH_STACK_H + 1.6 + 1.4)
    return out
def audio_board():
    return polar(AUDIO_AZ, AUDIO_R, Z_DECK1 + BOARD_STANDOFF) * Box(AUDIO_L, AUDIO_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
def audio_parts():
    zt = Z_DECK1 + BOARD_STANDOFF + 1.6
    out = {"audio_parts_ENVELOPE": polar(AUDIO_AZ, AUDIO_R, zt) * Pos(0, -6, 0) * Box(AUDIO_L - 6, 20.0, AUDIO_H - 1.6 - BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN))}
    out.update(bodies_of("ESS_ES9219Q_WQFN40_5x5.step", polar(AUDIO_AZ, AUDIO_R, zt) * Pos(0, 12, 0), prefix="es9219q_"))
    return out
def motion_board():
    return polar(MOTION_AZ, MOTION_R, Z_DECK1 + BOARD_STANDOFF) * Box(MOTION_L, MOTION_W, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
def motion_parts():
    zt = Z_DECK1 + BOARD_STANDOFF + 1.6; P = polar(MOTION_AZ, MOTION_R, zt)
    out = {}
    out.update(bodies_of("TMC6300-LA-T_QFN20_3x3.step", P * Pos(6, 5, 0), prefix="tmc6300_"))
    out.update(bodies_of("TI_DRV2605L_VSSOP10_DGS.step", P * Pos(6, -5, 0), prefix="drv2605l_"))
    out["motion_connectors_ENVELOPE"] = P * Pos(-8, 0, 0) * Box(11.0, 24.0, MOTION_H - 1.6 - BOARD_STANDOFF, align=(Align.CENTER, Align.CENTER, Align.MIN))   # connectors on the inner (motor) side
    return out
def converter_body():
    return {"converter_ENVELOPE": polar(CONV_AZ, CONV_R, Z_DECK1) * Box(CONV_W, CONV_L, CONV_H, align=(Align.CENTER, Align.CENTER, Align.MIN))}

# ---------------------------------------------------------------- encoder, LRA
def encoder_board():
    r_face = R_BORE - ENC_GAP - 1.63
    return blk(1.0, 8.0, Z_CODE0, Z_CODE1, ENC_AZ, r_face - 0.5)
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
    for t in (-16.0, 16.0):                                                              # ears on the plate top beside the slot (inside the wall, inboard of the LED ring)
        f += blk(4.0, 4.0, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 1.5, 0.0, 65.0, t=t)
        f += blk(PORT_FACE_R0 - 63.0 + 0.5, 4.0, Z_PLATE_TOP - 1.0, Z_PLATE_TOP - 0.01, 0.0, (63.0 + PORT_FACE_R0 + 0.5)/2, t=t)   # bridge from the face to the ear, under the wall's foot
        f -= zbore(2.2, Z_PLATE_TOP - 1, Z_PLATE_TOP + 3, 0.0, 65.0, t=t)
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
JACK_BOARD_Z0 = JACK_AXIS_Z + JACK_AXIS_ABOVE_BOARD
def jack_board():
    return blk(16.0, 22.0, JACK_BOARD_Z0, JACK_BOARD_Z0 + 1.6, 0.0, PORT_FACE_R0 - 8.0, t=PORT_JACK_T)
def jack_bodies():
    place = polar(0.0, PORT_FACE_R0, JACK_BOARD_Z0) * Pos(0, PORT_JACK_T, 0) * Rot(180, 0, 0) * Rot(0, 0, 180)
    return bodies_of("Switchcraft_35RAPC4BH3_jack_3p5mm.step", place, prefix="jack_")
def barrel_board():
    """vertical board (tangential plane) carrying the right-angle jack, so the barrel axis height is free"""
    return blk(1.6, 14.0, -1.0, 8.0, 0.0, PORT_NOTCH_R0 + 1.0, t=PORT_BARREL_T)
def barrel_bodies():
    """CUI PJ-063AH: 24 V 8 A, 2.0 mm pin (PUBLISHED); body 14.4 x 9.0 x 11.0 ASSUMED, bushing to the face"""
    r1 = PORT_FACE_R0 + PORT_FACE_T
    body = blk(13.2, 11.0, BARREL_AXIS_Z - 4.5, BARREL_AXIS_Z + 4.5, 0.0, PORT_NOTCH_R0 + 1.8 + 13.2/2, t=PORT_BARREL_T)
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
    m = {"base_plate": base_plate(), "internal_structure": internal_structure(),
         "halo_diffuser": halo_diffuser(), "knob_body": knob_body(knurl), "deck": deck(),
         "carriage": carriage(engaged), "servo_mount": servo_mount(),
         "speaker_cradle": speaker_cradle(), "port_face": port_face(),
         "adapter_board": adapter_board(), "audio_board": audio_board(), "motion_board": motion_board(),
         "encoder_board": encoder_board(), "usbc_board": usbc_board(), "jack_board": jack_board(), "barrel_board": barrel_board(),
         "light_board": light_board(), "commutation_board": commutation_board(engaged), "led_flex": led_flex(), "bond_tape": bond_tape()}
    for i, az in enumerate(WHEEL_AZ):
        m[f"collar_{i}"] = wheel_collar(az)
        m[f"bush_{i}"] = ecc_bush(az)
    return m
def bought_parts(engaged=True):
    b = {}
    b.update(panel_bodies()); b.update(flex_bodies())
    b.update(pi_bodies()); b.update(cooler_bodies()); b.update(pi_plug_bodies())
    b.update(motor_bodies(engaged)); b["motor_band"] = band(engaged)
    b.update(magnet_body(engaged)); b.update(mt6701_bodies(engaged))
    b.update(servo_bodies())
    for az in WHEEL_AZ: b.update(bearing_bodies(az))
    b.update(speaker_bodies()); b.update(encoder_bodies()); b.update(lra_bodies())
    b.update(adapter_parts()); b.update(audio_parts()); b.update(motion_parts()); b.update(converter_body())
    b.update(usbc_bodies()); b.update(jack_bodies()); b.update(barrel_bodies()); b.update(light_bodies())
    b.update(led_bodies()); b.update(plug_envelopes())
    b["pad"] = pad()
    return b
