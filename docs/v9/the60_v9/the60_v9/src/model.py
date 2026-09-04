"""the 60 — v9 geometry.  build123d algebra mode.

Every bought part is placed as its CAD body from design/cad/bought-parts.
Every made part is the simplest shape that holds the bought parts in place.
Names in the assembly are stable and are what the checker and the drawings use.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import *
from params import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
D = math.radians

# ---------------------------------------------------------------- helpers
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
def zbore(d, z0, z1, az=0.0, r=0.0, t=0.0):
    return polar(az, r, z0) * Pos(0, t, 0) * Cylinder(d/2, z1-z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
def rbore(d, r0, r1, az, z, t=0.0):
    """cylinder along the radial direction from r0 to r1 at azimuth az, height z, tangential offset t"""
    return (Pos(0, 0, z) * Rot(0, 0, az) * Pos((r0 + r1) / 2, t, 0) * Rot(0, 90, 0)
            * Cylinder(d/2, r1 - r0, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
def csk_hole(d, z0, z1, az, r, head_d=6.5, head_h=1.6):
    """countersunk from the underside (z0)"""
    h = zbore(d, z0 - 1, z1 + 1, az, r)
    h += polar(az, r, z0 - 0.01) * Cone(head_d/2, d/2, head_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return h
def revolve_profile(pts):
    return revolve(Plane.XZ * Polygon(*pts, align=None), Axis.Z)
def xy_slot(r0, r1, half_w, z0, z1, az=0.0):
    """tangential-width slot along the radial direction"""
    return blk(r1 - r0, 2 * half_w, z0, z1, az, (r0 + r1) / 2)
def label(shape, name):
    try: shape.label = name
    except Exception: pass
    return shape

# ---------------------------------------------------------------- bought bodies (loaded once)
_cache = {}
def bought(name):
    """import a bought-part STEP once; returns a Compound of its solids in the file's own frame"""
    if name not in _cache:
        _cache[name] = import_step(os.path.join(STEP, name))
    return _cache[name]
def bought_solids(name):
    """named solids of a bought STEP: labels live on the child compounds, one solid each"""
    c = bought(name)
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
def bodies_of(name, place, keep=None, prefix=""):
    """place every named solid of a bought STEP; keep = predicate on the body label"""
    out = {}
    for lab, s in bought_solids(name).items():
        if keep and not keep(lab): continue
        out[prefix + lab] = place * s
    return out

# ---------------------------------------------------------------- the display (vendor STEP, trimmed)
_display_cache = {}
def display_bodies():
    """Waveshare assembly rotated into the device frame and lifted so the glass is at Z_DISC_TOP.
    The PMMA back plate and its four screws are removed (RULING 4 Sep); the studs stay."""
    if _display_cache: return dict(_display_cache)
    place = Pos(0, 0, VENDOR_Z_OFFSET) * Rot(0, 0, VENDOR_ROT_DEG)
    ws = import_step(WAVESHARE_STP)
    out = {}
    others = []
    for ch in ws.children:
        lab = (ch.label or "")
        if "CASE" in lab:
            out["display_case"] = ch.solids()[0]
        elif "PMMA" in lab or "SCREW" in lab:
            continue                                   # removed: PMMA plate + its M2.5 x 4 screws
        else:
            for s in ch.solids():
                bb = s.bounding_box()
                if (bb.size.X > 80 and bb.size.Y > 60 and bb.size.Z < 2):
                    out["display_pcb"] = s
                else:
                    others.append(s)
    # name the big components so the checker can say what clashed
    named = 0
    for s in sorted(others, key=lambda q: -q.volume):
        bb = s.bounding_box(); cx, cy = (bb.min.X+bb.max.X)/2, (bb.min.Y+bb.max.Y)/2
        if s.volume > 15:
            n = f"display_part_{named:03d}_{bb.size.X:.0f}x{bb.size.Y:.0f}x{bb.size.Z:.1f}"
            named += 1
        else:
            n = None
        if n: out[n] = s
    # tiny solids (pins, pads) are merged into one compound for the record only
    tiny = [s for s in others if s.volume <= 15]
    placed = {k: label(place * v, k) for k, v in out.items()}
    if tiny:
        placed["display_small_parts"] = label(place * Compound(tiny), "display_small_parts")
    for k, v in placed.items(): label(v, k)
    _display_cache.update(placed)
    return dict(placed)

# ---------------------------------------------------------------- knob
def body_profile():
    rb, rk, ri, rg = R_BORE, R_KNOB, R_CROWN_IN, R_GROOVE_ROOT
    zs, zt, zcb = Z_SKIRT_BOT, Z_KNOB_TOP, Z_CROWN_BOT
    f = WHEEL_V_FLAT / 2
    rc = rb + STRIP_T                                  # code-band recess
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
    """stadium the carriage shoe slides in (engaged r 40.5 .. released r 38.1) plus the tab slot inboard"""
    d = MOTOR_OD + 2 * 1.0 + 1.5                      # shoe Ø37 + 0.75 clearance a side
    h = zbore(d, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R)
    h += zbore(d, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R - CLUTCH_LIFT)
    h += blk(CLUTCH_LIFT, d, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R - CLUTCH_LIFT/2)
    h += blk(10.0, 10.0, -3, PLATE_T + 1, MOTOR_AZ, MOTOR_R - MOTOR_OD/2 - 3.5)   # tab slot
    return h
def port_slot(z0=-3, z1=PLATE_T + 1):
    return xy_slot(PORT_NOTCH_R0, PLATE_R + 2, PORT_W/2, z0, z1, 0.0)
def base_plate():
    p = cyl(PLATE_R, 0, PLATE_T)
    p -= carriage_hole()
    p -= port_slot()
    for az in PLATE_SCREW_AZ:                                  # structure screws, csk from below
        p -= csk_hole(3.4, 0, PLATE_T, az, PLATE_SCREW_R)
    for sx in (-24.0, 24.0):                                   # speaker cradle, csk from below
        p -= Pos(sx + SPEAKER_CENTRE[0], SPEAKER_CENTRE[1], 0) * (cyl(1.7, -1, PLATE_T+1) + Pos(0,0,-0.01)*Cone(3.25, 1.7, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for sx in (-14.0, 14.0):                                   # servo mount, csk from below
        h = polar(MOTOR_AZ, 9.7, 0) * Pos(0, sx, 0)
        p -= h * (cyl(1.7, -1, PLATE_T+1) + Pos(0,0,-0.01)*Cone(3.25, 1.7, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    for (dr, dt) in ((-12, -12), (-12, 12), (12, -12), (12, 12)):   # driver board standoffs, M2 csk
        p -= polar(DRIVER_AZ, DRIVER_R, 0) * Pos(dr, dt, 0) * (cyl(1.1, -1, PLATE_T+1) + Pos(0,0,-0.01)*Cone(2.2, 1.1, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    p -= zbore(3.4, -1, PLATE_T + 1, 0.0, 38.0, -18.5)         # ground-bond screw beside the slot
    for t in (-17.0, 17.0):                                    # jack board M2 (tapped) and port-face ears
        p -= zbore(1.6, -1, PLATE_T + 1, 0.0, 42.0, t)
        p -= zbore(1.6, -1, PLATE_T + 1, 0.0, 49.0, t)
    return p
DRIVER_AZ, DRIVER_R = 152.0, 33.0
def pad():
    p = frustum(PAD_R - 0.3, PAD_R, -PAD_T, 0.0)
    p -= port_slot(-3, 1)
    return p

# ---------------------------------------------------------------- the internal structure
def motor_relief(engaged=True):
    """what the motor and its band need free in the structure: base below the bell, bell above"""
    rc = MOTOR_R
    k = zbore(MOTOR_BASE_OD + 2.0, Z_MOTOR_BOT - 0.5, Z_BELL_BOT - 0.01, MOTOR_AZ, rc)
    k += zbore(MOTOR_OD + 2 * MOTOR_CLEAR, Z_BELL_BOT - 0.5, Z_MOTOR_TOP + 0.6, MOTOR_AZ, rc)
    return k
def structure():
    s = tube(R_WALL_OUT, R_WALL_IN, Z_PLATE_TOP, Z_LEDGE_TOP)                 # the wall
    s += tube(R_WALL_OUT, R_LEDGE_IN, Z_LEDGE_BOT, Z_LEDGE_TOP)               # the ledge
    s += tube(R_LIP_OUT, R_WALL_OUT - 0.01, Z_LIP0, Z_LIP1)                   # diffuser-retaining lip
    for az in WHEEL_AZ:                                                       # wheel posts
        s += zbore(WHEEL_POST_D, Z_LEDGE_TOP - 0.01, Z_POST_TOP, az, BUSH_R)
    for az in COLUMN_AZ:                                                      # display columns + seat tabs
        s += blk(COLUMN_R1 - COLUMN_R0, COLUMN_W, Z_LEDGE_TOP - 0.01, Z_SEAT0 + 0.01, az, (COLUMN_R0 + COLUMN_R1)/2)
    # encoder tower
    s += blk(57.2 - 52.0, 9.0, Z_LEDGE_TOP - 0.01, Z_CODE1 + 0.7, ENC_AZ, (52.0 + 57.2)/2)
    # LRA bonding pad on the inside of the wall
    s += blk(1.3, 11.5, 8.5, 14.5, LRA_AZ, R_WALL_IN - 0.6)
    # M3 insert bosses tying the wall to the plate
    for az in PLATE_SCREW_AZ:
        s += zbore(7.0, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + INSERT_M3_L + 1.5, az, PLATE_SCREW_R)
        s += blk(R_WALL_IN - PLATE_SCREW_R + 1.5, 7.0, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 3.0, az, (PLATE_SCREW_R + R_WALL_IN)/2)
        s -= zbore(INSERT_M3_D, Z_PLATE_TOP - 1, Z_PLATE_TOP + INSERT_M3_L + 0.3, az, PLATE_SCREW_R)
    # cuts
    s -= motor_relief()
    for az in WHEEL_AZ:                                                       # bush bores through the ledge
        s -= zbore(BUSH_D + 0.1, Z_LEDGE_BOT - 1, Z_POST_TOP + 1, az, BUSH_R)
    for az in DISC_MOUNT_AZ_DEV:                                              # M4 clearance through the seat tabs
        s -= zbore(4.3, Z_SEAT0 - 1, Z_SEAT1 + 1, az, DISC_MOUNT_PCD/2)
    # encoder pocket (board + package) looking outward through a window
    s -= blk(1.2, 8.4, Z_CODE0 - 0.4, Z_CODE1 + 0.4, ENC_AZ, R_BORE - ENC_GAP - 1.63 - 0.6)   # board slot
    s -= blk(ENC_GAP + 1.63 + 0.3, 5.6, Z_CODE0 - 0.4, Z_CODE1 + 0.4, ENC_AZ, R_BORE - (ENC_GAP + 1.63 + 0.3)/2)  # window + package
    # light-sensor aperture is in the port face, not the wall; perimeter ports:
    for i in range(PORT_N):
        az = 7.5 + 15.0 * i
        if abs(((az - MOTOR_AZ + 180) % 360) - 180) <= 30: continue             # falls in the motor cut-out
        s -= rbore(PORT_D, R_WALL_IN - 1, R_WALL_OUT + 1, az, PORT_Z)
    return s

def seat_tabs():
    """the four 1.2 mm seat tabs in the gap between the board top and the disc back (part of the structure)"""
    t = None
    for az_col, az_hole in zip(COLUMN_AZ, DISC_MOUNT_AZ_DEV):
        a = D(az_hole); hx, hy = DISC_MOUNT_PCD/2 * math.cos(a), DISC_MOUNT_PCD/2 * math.sin(a)
        tab = Pos(hx, hy, (Z_SEAT0 + Z_SEAT1)/2) * Rot(0, 0, az_hole) * Box(8.0, 8.0, SEAT_T)
        # bridge from the column top to the tab
        ac = D(az_col); cx, cy = (COLUMN_R0 + COLUMN_R1)/2 * math.cos(ac), (COLUMN_R0 + COLUMN_R1)/2 * math.sin(ac)
        mx, my = (hx + cx)/2, (hy + cy)/2
        L = math.hypot(hx - cx, hy - cy) + 6.0
        ang = math.degrees(math.atan2(hy - cy, hx - cx))
        br = Pos(mx, my, (Z_SEAT0 + Z_SEAT1)/2) * Rot(0, 0, ang) * Box(L, 5.0, SEAT_T)
        piece = tab + br
        t = piece if t is None else t + piece
    # keep the seat ring inside the disc and outside the picture
    t = t & tube(R_DISC - 0.3, R_LEDGE_IN, Z_SEAT0 - 1, Z_SEAT1 + 1)
    for az in DISC_MOUNT_AZ_DEV:
        t -= zbore(4.3, Z_SEAT0 - 1, Z_SEAT1 + 1, az, DISC_MOUNT_PCD/2)
    return t

def internal_structure():
    s = structure()
    s += seat_tabs()
    return s

# ---------------------------------------------------------------- diffuser, LED ring
def halo_diffuser():
    return revolve_profile([(R_DIFF_IN, HALO_Z0), (R_DIFF_OUT_BOT, HALO_Z0),
                            (R_DIFF_OUT_TOP, HALO_Z1), (R_DIFF_IN, HALO_Z1)])
def led_flex():
    return tube(R_LED_FLEX_OUT, R_LED_FLEX_IN, Z_PLATE_TOP, Z_PLATE_TOP + 0.2)
R_LED_FLEX_IN, R_LED_FLEX_OUT = 57.7, 60.0
LED_R = 58.8
def led_bodies():
    out = {}
    base = bought_solids("OPSCO_SK6812SIDE-A_led_4020.step")
    pk = [s for l, s in base.items() if "package" in l][0]
    for i in range(LED_N):
        az = 360.0 * i / LED_N
        # file: x 4.0 tangential, y 1.6 radial, z 2.0 up; emitting face = +y face -> point +y outward (radial)
        place = polar(az, LED_R, Z_PLATE_TOP + 0.2) * Rot(0, 0, 90)
        out[f"led_{i:02d}"] = place * pk
    return out

# ---------------------------------------------------------------- wheels
def wheel_collar(az=None):
    h = WHEEL_W
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline((WHEEL_OD/2 - WHEEL_V_H, 0), (WHEEL_OD/2, h/2 - WHEEL_V_FLAT/2),
                         (WHEEL_OD/2, h/2 + WHEEL_V_FLAT/2), (WHEEL_OD/2 - WHEEL_V_H, h),
                         (5.0, h), (5.0, 0), close=True)
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
    place = polar(az, WHEEL_AXIS_R, Z_WHEEL0)
    return bodies_of("623ZZ_bearing_3x10x4.step", place, prefix=f"bearing{az}_")

# ---------------------------------------------------------------- motor, carriage, clutch
def motor_place(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, Z_MOTOR_BOT)
def carriage(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    c = cyl(MOTOR_OD/2 + 1.0, 0, CARRIAGE_T)                                   # Ø37 shoe
    c += tube(MOTOR_OD/2 + 1.0, MOTOR_OD/2 + 0.3, CARRIAGE_T - 0.01, CARRIAGE_T + 0.6)   # locating rim
    c -= Pos(0, 0, -0.01) * Box(12.4, 12.4, 3.3, align=(Align.CENTER, Align.CENTER, Align.MIN))   # commutation board pocket
    c -= cyl(4.5, 3.0, CARRIAGE_T + 2)                                         # sight hole to the shaft magnet
    tab = Pos(-(MOTOR_OD/2 + 0.8 + 0.75), 0, 0) * Box(1.5, 8.0, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN))   # servo push tab (inboard = -x local)
    c += tab
    c += Pos(-(MOTOR_OD/2 + 0.8 + 0.75), 0, 0) * Box(4.0, 8.0, CARRIAGE_T, align=(Align.MIN, Align.CENTER, Align.MIN))   # tab root
    return polar(MOTOR_AZ, MOTOR_R - dr, 0.0) * c
def commutation_board(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    b = Pos(0, 0, 0.0) * Box(12.0, 12.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return polar(MOTOR_AZ, MOTOR_R - dr, 0.0) * b
def mt6701_bodies(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    place = polar(MOTOR_AZ, MOTOR_R - dr, 1.6)
    return bodies_of("MT6701CT-STD_SOP8.step", place, prefix="mt6701_")
def magnet_body(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    place = polar(MOTOR_AZ, MOTOR_R - dr, Z_MOTOR_BOT)         # inside the shaft's bottom end (ASSUMED position)
    return bodies_of("MT6701_diametric_magnet_D6x2p5.step", place, prefix="motor_")
def motor_bodies(engaged=True):
    return bodies_of(MOTOR_FILE, motor_place(engaged), prefix="motor_")
def band(engaged=True):
    dr = 0.0 if engaged else CLUTCH_LIFT
    return polar(MOTOR_AZ, MOTOR_R - dr, 0) * tube(MOTOR_OD/2 + MOTOR_BAND_T, MOTOR_OD/2 + 0.01, Z_DRIVE0, Z_DRIVE1)
SERVO_R0 = MOTOR_R - MOTOR_OD/2 - 0.8 - 1.5 - 1.0 - 3.0 - SERVO_L   # body end 4 mm short of the tab: the pushrod bridges it, and retracts 2.4 for free-spin
def servo_place():
    # file: body x 0..21.4 (stroke axis +x), y +-7.6, z 0..6 ; point +x outward along the radial
    return polar(MOTOR_AZ, SERVO_R0, Z_PLATE_TOP + 1.5)
def servo_bodies():
    return bodies_of("AGFRC_C1p5CLS_PRO_linear_servo.step", servo_place(), prefix="servo_")
def servo_mount():
    """tray the servo lies in: floor, two side walls, an inner end wall; open toward the carriage"""
    L = SERVO_L + 1.5
    m = Box(L, SERVO_W + 3.0, 1.5, align=(Align.MIN, Align.CENTER, Align.MIN))
    m += Pos(0, 0, 1.5) * Box(L, SERVO_W + 3.0, SERVO_H + 0.5, align=(Align.MIN, Align.CENTER, Align.MIN))
    m -= Pos(1.5, 0, 1.49) * Box(L, SERVO_W + 0.4, SERVO_H + 1.0, align=(Align.MIN, Align.CENTER, Align.MIN))   # pocket, open outward
    m -= Pos(-0.1, 0, 1.5 + 1.0) * Box(1.8, 6.0, 4.0, align=(Align.MIN, Align.CENTER, Align.MIN))             # lead exit at the inner end
    for sy in (-14.0, 14.0):
        m -= Pos(L/2, sy, -1) * Cylinder(1.7, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    m = Pos(-1.5, 0, 0) * m
    return polar(MOTOR_AZ, SERVO_R0, Z_PLATE_TOP) * m

# ---------------------------------------------------------------- speaker
def speaker_place():
    return Pos(SPEAKER_CENTRE[0], SPEAKER_CENTRE[1], Z_PLATE_TOP)
def speaker_bodies():
    return bodies_of("Soberton_SP-4005-1_speaker_D40.step", speaker_place(), keep=lambda l: "keepout" not in l, prefix="")
def speaker_cradle():
    """ring under the speaker's Ø40 flange (flange at 4.45-5.95 above its rear face), three snap fingers over it"""
    c = tube(SPEAKER_D/2 + 3.3, 18.3, 0, 4.45)
    for i in range(3):
        f = Rot(0, 0, 120*i + 90) * (Pos(21.75, 0, 4.44) * Box(3.1, 3.0, 2.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
                                     + Pos(19.75, 0, 6.05) * Box(1.0, 3.0, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        c += f
    for sx in (-24.0, 24.0):
        c += Pos(sx, 0, 0) * Cylinder(4.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c += Pos(sx * 22/24, 0, 0) * Box(6.0, 6.0, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c -= Pos(sx, 0, -1) * Cylinder(1.7, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return speaker_place() * c

# ---------------------------------------------------------------- boards
def driver_board():
    return polar(DRIVER_AZ, DRIVER_R, Z_PLATE_TOP + 3.0) * Box(30.0, 22.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
def driver_parts():
    out = {}
    base = polar(DRIVER_AZ, DRIVER_R, Z_PLATE_TOP + 4.6)
    out.update(bodies_of("TMC6300-LA-T_QFN20_3x3.step", base * Pos(8, 6, 0), prefix="tmc6300_"))
    out.update(bodies_of("TI_DRV2605L_VSSOP10_DGS.step", base * Pos(8, -6, 0), prefix="drv2605l_"))
    for i, dy in enumerate((-5.0, 5.0)):                                       # two supercaps lying on the board
        place = base * Pos(-7, dy, SUPERCAP_D/2) * Rot(0, 90, 0)
        out.update(bodies_of("Abracon_AHCR-S04R0SA206Q_supercap_20F.step", place * Pos(0, 0, -SUPERCAP_L/2), keep=lambda l: "can" in l, prefix=f"supercap{i}_"))
    for (dx, dy) in ((-12, -12), (-12, 12), (12, -12), (12, 12)):
        out[f"standoff_{dx}_{dy}"] = polar(DRIVER_AZ, DRIVER_R, Z_PLATE_TOP) * Pos(dx, dy, 0) * Cylinder(2.25, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out
def encoder_board():
    r_face = R_BORE - ENC_GAP - 1.63                                            # package face -> board top face
    return blk(1.0, 8.0, Z_CODE0, Z_CODE1, ENC_AZ, r_face - 0.5)
def encoder_bodies():
    r_face = R_BORE - ENC_GAP - 1.63
    place = polar(ENC_AZ, r_face, (Z_CODE0 + Z_CODE1)/2) * Rot(0, 90, 0) * Rot(0, 0, 90)   # z -> +r
    return bodies_of("Broadcom_AEDR-8300-1K2_encoder.step", place, prefix="encoder_")
def lra_bodies():
    place = polar(LRA_AZ, R_WALL_IN - 1.2 - 0.07, 11.5) * Rot(0, -90, 0) * Rot(0, 0, 0)   # can's -z face onto the pad face
    return bodies_of("Vybronics_VLV101040A_LRA.step", place, prefix="lra_")
# port assembly
def port_face():
    f = blk(PORT_FACE_T, PORT_W, -PAD_T, Z_PLATE_TOP, 0.0, PORT_FACE_R0 + PORT_FACE_T/2)
    f += blk(3.5, 12.0, 0.7, 2.2, 0.0, PORT_FACE_R0 - 1.75, t=PORT_USBC_T)           # shelf under the USB-C board
    f += blk(4.5, 10.0, -PAD_T, 0.0, 0.0, PORT_FACE_R0 - 2.25, t=PORT_LIGHT_T)      # foot holding the light-sensor board
    f -= blk(1.3, 6.4, -PAD_T - 1, 0.6, 0.0, 46.0, t=PORT_LIGHT_T)                    # its slot
    for t in (-17.0, 17.0):                                                           # ears on the plate top beside the slot
        f += blk(4.0, 4.0, Z_PLATE_TOP - 0.01, Z_PLATE_TOP + 1.5, 0.0, 49.0, t=t)
        f -= zbore(2.2, Z_PLATE_TOP - 1, Z_PLATE_TOP + 3, 0.0, 49.0, t=t)
    f -= blk(PORT_FACE_T + 2, 9.6, 2.2 - USBC_BELOW - 0.3, 2.2 + USBC_ABOVE + 0.3 + 1.6, 0.0, PORT_FACE_R0 + PORT_FACE_T/2, t=PORT_USBC_T)   # USB-C opening
    f -= rbore(6.3, PORT_FACE_R0 - 1, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, JACK_Z, t=PORT_JACK_T)         # jack bushing
    f -= rbore(SENSOR_HOLE_D, PORT_FACE_R0 - 1, PORT_FACE_R0 + PORT_FACE_T + 1, 0.0, 2.5, t=PORT_LIGHT_T)  # light sensor aperture
    return f
JACK_Z = 2.0
USBC_BOARD_Z0 = 2.2
def usbc_board():
    b = blk(11.0, 12.0, USBC_BOARD_Z0, USBC_BOARD_Z0 + 1.6, 0.0, PORT_FACE_R0 - 5.5, t=PORT_USBC_T)
    b -= blk(6.3, 9.3, USBC_BOARD_Z0 - 1, USBC_BOARD_Z0 + 3, 0.0, PORT_FACE_R0 - 3.1, t=PORT_USBC_T)   # the required notch
    return b
def usbc_bodies():
    # file: mating face at x=+0.5 (flush with the board edge at x=0), body toward -x; z=0 board top
    place = polar(0.0, PORT_FACE_R0, USBC_BOARD_Z0 + 1.6) * Pos(0, PORT_USBC_T, 0)
    return bodies_of("GCT_USB4520-03-0-A_usbc_midmount.step", place, keep=lambda l: "cutout" not in l, prefix="usbc_")
JACK_BOARD_Z0 = Z_PLATE_TOP
def jack_board():
    return blk(16.0, 36.0, JACK_BOARD_Z0, JACK_BOARD_Z0 + 1.6, 0.0, 42.0)
def jack_bodies():
    # file: axis along x, bushing x -3.5..0, body 0..14, z 0..6 above its board; hang it under the board: flip z
    place = polar(0.0, PORT_FACE_R0, JACK_BOARD_Z0) * Pos(0, PORT_JACK_T, 0) * Rot(180, 0, 0) * Rot(0, 0, 180)
    return bodies_of("Switchcraft_35RAPC4BH3_jack_3p5mm.step", place, prefix="jack_")
def dac_bodies():
    place = polar(0.0, 38.0, JACK_BOARD_Z0 + 1.6) * Pos(0, -8.0, 0)
    return bodies_of("ESS_ES9219Q_WQFN40_5x5.step", place, prefix="es9219q_")
def light_board():
    return blk(1.0, 6.0, -1.4, 5.5, 0.0, 46.0, t=PORT_LIGHT_T)
def light_bodies():
    # sensor's z (its height) points outward (+r): sensitive face toward the aperture
    place = polar(0.0, 46.5, 2.5) * Pos(0, PORT_LIGHT_T, 0) * Rot(0, 90, 0)
    return bodies_of("Vishay_VEML7700-TR_ambient_light_sensor.step", place, prefix="veml7700_")
def plug_envelopes():
    out = {}
    # the boxed cable's right-angle plug in the plate notch (ASSUMED 12 x 6.5 x 12)
    out["plug_envelope_external"] = blk(12.0, 12.0, -1.5, 5.0, 0.0, PORT_FACE_R0 + PORT_FACE_T + 6.0, t=PORT_USBC_T)
    # the internal straight plug on the Waveshare board's back-edge USB-C (ASSUMED 10 x 6.5 x 19)
    # vendor socket at board (-12.4, 25.3) -> device (25.3, 12.4); plug runs outward along +x
    out["plug_envelope_internal"] = Pos(29.0 + 9.5, 12.4, Z_PCB_BOT - 1.17) * Box(19.0, 10.0, 6.5)
    return out

# ---------------------------------------------------------------- assembly
def made_parts(knurl=None, engaged=True):
    m = {"base_plate": base_plate(), "internal_structure": internal_structure(),
         "halo_diffuser": halo_diffuser(), "knob_body": knob_body(knurl),
         "carriage": carriage(engaged), "servo_mount": servo_mount(),
         "speaker_cradle": speaker_cradle(), "port_face": port_face(),
         "driver_board": driver_board(), "encoder_board": encoder_board(),
         "usbc_board": usbc_board(), "jack_board": jack_board(),
         "light_board": light_board(), "commutation_board": commutation_board(engaged),
         "led_flex": led_flex()}
    for i, az in enumerate(WHEEL_AZ):
        m[f"collar_{i}"] = wheel_collar(az)
        m[f"bush_{i}"] = ecc_bush(az)
    return m
def bought_parts(engaged=True):
    b = {}
    b.update(display_bodies())
    b.update(motor_bodies(engaged)); b["motor_band"] = band(engaged)
    b.update(magnet_body(engaged)); b.update(mt6701_bodies(engaged))
    b.update(servo_bodies())
    for az in WHEEL_AZ: b.update(bearing_bodies(az))
    b.update(speaker_bodies()); b.update(driver_parts()); b.update(encoder_bodies())
    b.update(lra_bodies()); b.update(usbc_bodies()); b.update(jack_bodies()); b.update(dac_bodies())
    b.update(light_bodies()); b.update(led_bodies()); b.update(plug_envelopes())
    b["pad"] = pad()
    return b
