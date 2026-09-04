"""
Radial / "the 60" — bought-component CAD models.

Every dimension carries a tag in DIMS below:
    P = published by the manufacturer (datasheet or dimensioned drawing)
    D = derived arithmetically from published values
    A = ASSUMED — not published anywhere; measure the part before trusting it

Convention for every model:
    units mm, Z up
    circular parts: axis = Z through (0,0)
    board-mounted parts: z = 0 is the PCB top surface, leads/pads at z = 0
    through-hole leads run below z = 0
    other parts: z = 0 is the seating / mounting face
"""
from build123d import *
import os, json
import math as _math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step")
os.makedirs(OUT, exist_ok=True)
REPORT = []


# ------------------------------------------------------------------ helpers
def cyl(d, h, z0=0.0):
    return Pos(0, 0, z0) * Cylinder(d / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))


def tube(od, id_, h, z0=0.0):
    return cyl(od, h, z0) - cyl(id_, h + 0.2, z0 - 0.1)


def box(l, w, h, x=0.0, y=0.0, z=0.0):
    return Pos(x, y, z) * Box(l, w, h, align=(Align.CENTER, Align.CENTER, Align.MIN))


VIRTUAL = ("keepout", "cutout", "gap", "REQUIRED", "sensitive_area", "ENVELOPE")


def _virtual(label):
    return any(v in label for v in VIRTUAL)


def save(name, bodies, note=""):
    """bodies: list of (label, shape). Earlier bodies are carved by later ones so
    no two real solids interfere; reference volumes are left alone."""
    real = [i for i, (l, _) in enumerate(bodies) if not _virtual(l)]
    for a in real:
        for b in real:
            if b > a:
                try:
                    bodies[a] = (bodies[a][0], bodies[a][1] - bodies[b][1])
                except Exception:
                    pass
    kids = []
    for label, s in bodies:
        s.label = label
        kids.append(s)
    asm = Compound(children=kids)
    asm.label = name
    path = os.path.join(OUT, name + ".step")
    export_step(asm, path, write_pcurves=False)
    bb = asm.bounding_box()
    REPORT.append(dict(
        name=name, note=note,
        bbox=[round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3)],
        zmin=round(bb.min.Z, 3), zmax=round(bb.max.Z, 3),
        bodies=[b[0] for b in bodies],
        kb=round(os.path.getsize(path) / 1024, 1)))
    print(f"  {name:44s} {bb.size.X:7.2f} x {bb.size.Y:7.2f} x {bb.size.Z:7.2f}")


print("building...")

# =================================================================== 1. 623ZZ
# SKF 623-2Z: d 3, D 10, B 4, r min 0.15, d1 4.8 (inner shoulder),
# D2 8.2 (outer ring recess = shield seat).  All P.
B_D, B_OD, B_W = 3.0, 10.0, 4.0
B_D1, B_D2, B_CH = 4.8, 8.2, 0.15
_outer = tube(B_OD, B_D2, B_W)
_outer = chamfer(_outer.edges().filter_by(GeomType.CIRCLE).group_by(SortBy.RADIUS)[-1], B_CH)
_inner = tube(B_D1, B_D, B_W)
_inner = chamfer(_inner.edges().filter_by(GeomType.CIRCLE).group_by(SortBy.RADIUS)[0], B_CH)
_sh_t = tube(B_D2, B_D1, 0.20, B_W - 0.35)
_sh_b = tube(B_D2, B_D1, 0.20, 0.15)
save("623ZZ_bearing_3x10x4",
     [("outer_ring", _outer), ("inner_ring", _inner),
      ("shield_top", _sh_t), ("shield_bottom", _sh_b)],
     "SKF 623-2Z geometry. Inner ring rotates relative to outer ring + shields.")

# ===================================== 2. JD-Power MY-3514C (2804) gimbal
# ENVELOPE ONLY, as requested.  The only dimension published anywhere for this
# part is the reseller/shop size designation "35x14mm":
#   jdpowershop.com/?product=jd-power-my-3514c-2804-outer-rotor-hollow-shaft-gimbal-brushless-motor
# JD-Power's shop page states all parameters are customisable and gives no
# specification table.  No dimensioned drawing has been retrieved for this part.
#
# CAUTION: on the sister part DC-2813C, the marketing designation "28x13" turned
# out to be Ø27.5 +/-0.1 x 13 +/-0.2 on JD-Power's own drawing.  So "35x14" is
# very likely a rounded-up designation and the real body may be ~Ø34.5.  Treat
# this solid as a keepout, not as the part.
#
# Not modelled, because nothing is published for this part: the hollow bore, the
# locating boss, the mounting bolt patterns, the base/bell split, the solder pads.
N_OD, N_H = 35.00, 14.00
_nmotor = cyl(N_OD, N_H)
save("JD-Power_MY-3514C_2804_gimbal_motor",
     [("motor_ENVELOPE", _nmotor)],
     "ENVELOPE ONLY. 35 x 14 is the shop size designation, not a toleranced "
     "dimension — the sister DC-2813C's '28x13' is Ø27.5 x 13 on the real "
     "drawing. No bore, boss, bolt patterns or rotor/stator split are modelled "
     "because JD-Power publishes none for this part.")

# ====================================================== 3. AGFRC C1.5CLS PRO
# P: 21.4 x 15.2 x 6.0 overall, 9 mm stroke.
# A: everything else.  AGFRC publishes no drawing — no lug positions, no hole
#    sizes, no pushrod diameter or position, no axis assignment.
S_L, S_W, S_H = 21.40, 15.20, 6.00
S_STROKE = 9.00
_sbody = box(S_L, S_W, S_H, x=S_L / 2)
_srod = Rot(0, 90, 0) * Cylinder(1.5 / 2, S_L + S_STROKE / 2,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
_srod = Pos(0, 0, S_H / 2) * _srod
_srod = _srod - box(S_L, S_W + 1, S_H, x=S_L / 2)
_ssweep = Rot(0, 90, 0) * Cylinder(3.0 / 2, S_STROKE, align=(Align.CENTER, Align.CENTER, Align.MIN))
_ssweep = Pos(S_L, 0, S_H / 2) * _ssweep
save("AGFRC_C1p5CLS_PRO_linear_servo",
     [("body_ENVELOPE", _sbody), ("pushrod_ASSUMED", _srod),
      ("stroke_keepout_9mm_ASSUMED", _ssweep)],
     "Only the 21.4 x 15.2 x 6.0 envelope and the 9 mm stroke are published. "
     "Axis assignment, pushrod and all mounting features are assumed.")

# ================================================== 4. Soberton SP-4005-1
# From Soberton 2D drawing SP-4005-1.pdf.  Ordinate ladder (P): 0, 1.20, 3.20,
# 4.45, 5.95, 6.95, 9.05.  Diameters (P): 40.00, 38.00, 36.25, 35.50, 16.20.
# NOTE: the drawing totals 9.05; the datasheet and product page say 8.5.
# Modelled at 9.05 — the larger of the two, so the cavity is never short.
# z = 0 is the REAR face.  Leads are 2 x AWG26 flying leads, 150 mm, exiting
# radially at the rim; modelled only as a small exit keepout.
_sp = (cyl(16.20, 3.20, 0.00)
       + cyl(36.25, 1.25, 3.20)
       + cyl(40.00, 1.50, 4.45)
       + cyl(38.00, 1.00, 5.95)
       + tube(38.00, 35.50, 2.10, 6.95))
_sp_lead = box(4.0, 3.0, 2.0, x=0, y=-20.0, z=4.45) - _sp
save("Soberton_SP-4005-1_speaker_D40",
     [("speaker", _sp), ("lead_exit_keepout_ASSUMED", _sp_lead)],
     "Height 9.05 per the 2D drawing (datasheet says 8.5 — conflict). "
     "Front sealing face is the 38.00/35.50 ring at z 6.95-9.05. "
     "Lead exit angular position is not published.")

# ================================================= 5. Vybronics VLV101040A
# P: can 10 +/-0.1 x 10 +/-0.1 x 4.05 +/-0.05; overall 13.9 incl. FPC;
#    tape 8.5 x 8.5 x 0.07 (bottom); Poron 9 x 9 x 0.25 (top);
#    pad block 5.70 x 2.80; 2 pads 1.9 wide, 4.5 outer span;
#    tail thickness 0.62 inner / 0.45 at the terminal end.
# z = 0 is the ADHESIVE (bottom) mounting face; vibration axis is Z.
L_S, L_H = 10.00, 4.05
_lcan = box(L_S, L_S, L_H)
_ltape = box(8.5, 8.5, 0.07, z=-0.07)
_lporon = box(9.0, 9.0, 0.25, z=L_H)
_ltail = box(5.70, 3.90, 0.62, y=-(L_S / 2 + 3.90 / 2))
_lpad1 = box(1.9, 2.80, 0.05, x=-4.5 / 2 + 1.9 / 2, y=-(L_S / 2 + 3.90 - 2.80 / 2), z=0.62)
_lpad2 = box(1.9, 2.80, 0.05, x=+4.5 / 2 - 1.9 / 2, y=-(L_S / 2 + 3.90 - 2.80 / 2), z=0.62)
save("Vybronics_VLV101040A_LRA",
     [("can", _lcan), ("adhesive_tape", _ltape), ("poron_top", _lporon),
      ("fpc_tail", _ltail), ("pad_1", _lpad1), ("pad_2", _lpad2)],
     "Vibration axis is Z, normal to the adhesive face. Top face is marked "
     "'Don't Push' max 0.5 kgf. FPC pads suit pogo pins.")

# =============================================== 6. Switchcraft 35RAPC4BH3
# From Switchcraft customer drawing 35RAPC__H3 Rev J.  All P except axis height.
# x = 0 is the PANEL MOUNTING SURFACE (bushing-side body face), +x rearward.
# y = 0 is the bushing centreline. z = 0 is the PCB seating plane.
J_BODY_L, J_H = 14.00, 6.00
J_Y_LEFT, J_Y_RIGHT = 6.00, 5.50           # +y and -y half widths
J_BUSH_D, J_BUSH_PROJ, J_BORE = 6.00, 3.50, 3.60
J_AXIS_Z = 3.00                             # D: body height 6.00, axis centred
_jbody = Pos(J_BODY_L / 2, (J_Y_LEFT - J_Y_RIGHT) / 2, 0) * Box(
    J_BODY_L, J_Y_LEFT + J_Y_RIGHT, J_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
_jbush = Pos(-J_BUSH_PROJ, 0, J_AXIS_Z) * (Rot(0, 90, 0) * Cylinder(
    J_BUSH_D / 2, J_BUSH_PROJ, align=(Align.CENTER, Align.CENTER, Align.MIN)))
_jbore = Pos(-J_BUSH_PROJ - 0.1, 0, J_AXIS_Z) * (Rot(0, 90, 0) * Cylinder(
    J_BORE / 2, J_BUSH_PROJ + 8.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
_jbody = _jbody - _jbore
_jbush = _jbush - _jbore
# pin: (x, y, orientation of the 1.20 dim, thickness)
J_PINS = [(2.00, 0.00, "perp", 0.40), (9.80, 5.20, "par", 0.30),
          (8.40, 2.50, "par", 0.30), (13.00, -4.00, "perp", 0.30),
          (5.40, -4.50, "par", 0.30)]
_jpins = None
for px, py, orient, th in J_PINS:
    lx, ly = (th, 1.20) if orient == "perp" else (1.20, th)
    p = Pos(px, py, -2.50) * Box(lx, ly, 2.50, align=(Align.CENTER, Align.CENTER, Align.MIN))
    _jpins = p if _jpins is None else _jpins + p
save("Switchcraft_35RAPC4BH3_jack_3p5mm",
     [("body", _jbody), ("bushing_M6x0p5", _jbush), ("pins_5x", _jpins)],
     "Bushing thread M6 x 0.5, projects 3.50 from the panel face. Axis at "
     "z 3.00 (derived, not dimensioned). PCB holes are 1.75 x 0.75 slots.")

# ============================================== 7. Broadcom AEDR-8300-1K2
# P: body 5.12 x 3.96 x 1.63 (+/-0.15); 6 terminals 0.95 (inward) x 0.60,
#    row pitch 1.96; reflective gap G 1.0 / 2.0 typ / 2.5 to the code strip.
# x = along the 3 terminal rows, y = across the two columns.
E_L, E_W, E_H = 5.12, 3.96, 1.63
E_T_IN, E_T_W, E_ROW = 0.95, 0.60, 1.96
_ebody = box(E_L, E_W, E_H)
_eterm = None
for xi in (-E_ROW, 0.0, E_ROW):
    for sy in (-1, 1):
        t = box(E_T_IN, E_T_W, 0.12, x=xi, y=sy * (E_W / 2 - E_T_IN / 2), z=-0.12)
        # terminals are leadless pads flush with the package underside
        t = Pos(0, 0, 0.12) * t
        _eterm = t if _eterm is None else _eterm + t
_egap = box(E_L, E_W, 2.00, z=E_H)          # typ reflective gap to the code strip
save("Broadcom_AEDR-8300-1K2_encoder",
     [("package", _ebody), ("terminals_6x", _eterm), ("reflective_gap_2mm_typ", _egap)],
     "75 LPI variant (0.3387 mm line pitch, derived). Optical centre is the "
     "package geometric centre (derived from land-pattern symmetry). "
     "Gap range 1.0-2.5 mm; 2.0 typ shown.")

# ================================================== 8. Vishay VEML7700-TR
# P: 6.8 (over mould) x 2.35 x 3.0; 4 leads width 0.5, pitch 1.27, span 3.81,
#    offset 0.635 from centreline; sensitive area 0.336 sq, its centre 1.95
#    above the seating plane on the longitudinal centreline.
V_L, V_W, V_H = 6.80, 2.35, 3.00
_vbody = box(V_L, V_W, V_H)
_vleads = None
for x in (-1.905, -0.635, 0.635, 1.905):
    l = box(0.50, 1.20, 0.20, x=x, y=-(V_W / 2 + 1.20 / 2 - 0.4), z=0.0)
    _vleads = l if _vleads is None else _vleads + l
_vsens = box(0.336, 0.10, 0.336, y=V_W / 2, z=1.95 - 0.336 / 2)
save("Vishay_VEML7700-TR_ambient_light_sensor",
     [("package", _vbody), ("leads_4x", _vleads), ("sensitive_area_0p336sq", _vsens)],
     "Sensitive area centre is 1.95 above the seating plane, NOT at mid-height. "
     "Aperture width w = 0.5 + 2 x (1.43 x d), d = sensor face to window outer face.")

# ============================================== 9. GCT USB4520-03-0-A USB-C
# P: body 6.5 long x 8.94 wide x 3.16 high; legs span 11.24; mid-mount offset
#    2.10 below the PCB top; shell 8.34 x 2.56; cavity opening 6.69;
#    board cutout 9.24 wide.  D: cutout depth 6.20, protrusion 0.50 past the
#    board edge, 1.06 standing above the PCB top.
U_L, U_W, U_H = 6.50, 8.94, 3.16
U_OFFSET = 2.10
U_LEG_W = 11.24
U_CUT_W, U_CUT_D = 9.24, 6.20
U_PROTRUDE = 0.50                            # board edge is x = 0, +x outward
_ubody = Pos(U_PROTRUDE - U_L / 2, 0, -U_OFFSET) * Box(
    U_L, U_W, U_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
_ushell = Pos(U_PROTRUDE - 0.6 / 2, 0, -U_OFFSET + (U_H - 2.56) / 2) * Box(
    0.6, 8.34, 2.56, align=(Align.CENTER, Align.CENTER, Align.MIN))
_umouth = Pos(U_PROTRUDE - 2.05 / 2, 0, -U_OFFSET + (U_H - 2.56) / 2 + 0.2) * Box(
    2.2, 6.69, 2.16, align=(Align.CENTER, Align.CENTER, Align.MIN))
_ubody = _ubody - _umouth
_ushell = _ushell - _umouth
_ulegs = None
for sy in (-1, 1):
    for lx in (-1.60, -5.60):
        l = Pos(lx, sy * (U_LEG_W / 2 - 1.00 / 2), -U_OFFSET) * Box(
            0.60, 1.00, U_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        _ulegs = l if _ulegs is None else _ulegs + l
# the notch to cut in the PCB itself: GCT's layout assumes a 0.80 mm board,
# so the cutout is drawn through z -0.80 to 0 (the board).  Scale to your stackup.
_ucut = Pos(-U_CUT_D / 2, 0, -0.80) * Box(
    U_CUT_D, U_CUT_W, 0.80, align=(Align.CENTER, Align.CENTER, Align.MIN))
save("GCT_USB4520-03-0-A_usbc_midmount",
     [("body", _ubody), ("shell_mating_face", _ushell), ("solder_legs_4x", _ulegs),
      ("board_cutout_REQUIRED", _ucut)],
     "z 0 = PCB top surface; board edge at x 0, connector protrudes 0.50 past it. "
     "Body hangs 2.10 below the PCB. 'board_cutout_REQUIRED' is the 9.24 x 6.20 "
     "notch to cut in the PCB, not part of the connector. GCT spec PDF says "
     "2.0 offset, the Rev A1 drawing says 2.10 — 2.10 used.")

# ========================================= 10. Abracon AHCR-S04R0SA206Q
# P: can/sleeve OD 8.0, body L 12.0, lead pitch 3.5 +/-0.5, lead dia 0.6,
#    short lead 8.00 min, long lead 12.00 min beyond the body.
# Radial through-hole. z = 0 is the PCB top; body sits above, leads below.
C_D, C_L, C_P, C_LD = 8.0, 12.0, 3.5, 0.6
_ccan = cyl(C_D, C_L, 0.0)
_clead_s = Pos(-C_P / 2, 0, -8.00) * Cylinder(C_LD / 2, 8.00, align=(Align.CENTER, Align.CENTER, Align.MIN))
_clead_l = Pos(+C_P / 2, 0, -12.00) * Cylinder(C_LD / 2, 12.00, align=(Align.CENTER, Align.CENTER, Align.MIN))
save("Abracon_AHCR-S04R0SA206Q_supercap_20F",
     [("can_with_sleeve", _ccan), ("lead_short_cathode_side", _clead_s),
      ("lead_long_anode_side", _clead_l),],
     "Lead lengths are published as MINIMA only — total height with leads is "
     "not published. Sleeve OD 8.0 +/-1.0; bare can OD not published. "
     "Negative bar is printed on the sleeve on the cathode side.")

# ============================================= 11. OPSCO SK6812SIDE-A (4020)
# P: 4.00 x 1.60 footprint, 2.00 tall, C0.6 chamfer at the GND (pin 4) corner.
#    Terminal widths along the 4.00 length: 0.75 / 0.60 / 0.35 / 0.65,
#    gaps 0.55, terminal depth 0.30.  Emits from the 4.00 x 2.00 face.
K_L, K_W, K_H = 4.00, 1.60, 2.00
_kbody = box(K_L, K_W, K_H)
_kch = Pos(K_L / 2, -K_W / 2, 0) * (Rot(0, 0, 45) * Box(
    0.6 * 1.42, 0.6 * 1.42, K_H + 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
_kbody = _kbody - _kch
_kterm = None
_x = -K_L / 2
for w in (0.75, 0.60, 0.35, 0.65):
    t = box(w, 0.30, 0.10, x=_x + w / 2, y=-K_W / 2 + 0.15, z=0.0)
    _kterm = t if _kterm is None else _kterm + t
    _x += w + 0.55
save("OPSCO_SK6812SIDE-A_led_4020",
     [("package", _kbody), ("terminals_4x", _kterm)],
     "Side emitter: light leaves the 4.00 x 2.00 face. Chamfered corner marks "
     "pin 4 (GND). Pad pitch is non-uniform. Window size not published.")

# ===================================================== 12-16. IC packages
def qfn(name, body, height, npin_side, pitch, lead_w, lead_l, pad, standoff, note):
    b = box(body, body, height - standoff, z=standoff)
    leads = None
    n = npin_side
    start = -(n - 1) * pitch / 2
    for i in range(n):
        c = start + i * pitch
        for (lx, ly, w, h) in ((body / 2 - lead_l / 2, c, lead_l, lead_w),
                               (-(body / 2 - lead_l / 2), c, lead_l, lead_w),
                               (c, body / 2 - lead_l / 2, lead_w, lead_l),
                               (c, -(body / 2 - lead_l / 2), lead_w, lead_l)):
            l = box(w, h, standoff + 0.05, x=lx, y=ly, z=0)
            leads = l if leads is None else leads + l
    tp = box(pad, pad, standoff + 0.05, z=0)
    save(name, [("body", b), (f"leads_{n*4}x", leads), ("thermal_pad", tp)], note)


# TMC6300-LA-T : QFN20 3x3, A 0.85 nom, A1 0.035, b 0.20, L 0.40, pad 1.7
qfn("TMC6300-LA-T_QFN20_3x3", 3.00, 0.85, 5, 0.40, 0.20, 0.40, 1.70, 0.035,
    "Analog Devices/Trinamic TMC6300 datasheet Rev 1.04 s9.1.")

# ESS ES9219Q : WQFN40 5x5, A 0.75 nom, A1 0.02, b 0.20, L 0.30, pad 3.79
qfn("ESS_ES9219Q_WQFN40_5x5", 5.00, 0.75, 10, 0.40, 0.20, 0.30, 3.79, 0.02,
    "ESS ES9219 datasheet v1.2 Fig 23. 40-pin WQFN, JEDEC MO-220, pad = pin 41.")


def soic(name, body_l, body_w, span, body_h, standoff, npin, pitch, lead_w, foot, note):
    b = box(body_l, body_w, body_h, z=standoff)
    leads = None
    n = npin // 2
    start = -(n - 1) * pitch / 2
    for i in range(n):
        c = start + i * pitch
        for sy in (-1, 1):
            y = sy * (span / 2 - foot / 2)
            l = box(lead_w, foot, 0.20, x=c, y=y, z=0)
            r = box(lead_w, 0.25, body_h, x=c, y=sy * (body_w / 2 + 0.125), z=standoff)
            leads = l + r if leads is None else leads + l + r
    save(name, [("body", b), (f"leads_{npin}x", leads)], note)


# MT6701CT-STD : SOP-8, D 4.9 nom, E1 3.9 nom, E 6.0 span, A2 1.45, A1 0.175
soic("MT6701CT-STD_SOP8", 4.90, 3.90, 6.00, 1.45, 0.175, 8, 1.27, 0.42, 0.85,
     "MT6701 datasheet Rev 1.8 s10.1. Sensing centre is the package geometric "
     "centre. Pair with a 6 x 2.5 diametric magnet at 1.0 mm typ air gap.")

# DRV2605L VSSOP-10 (DGS) : D 3.0, E1 3.0, E 4.90, A 1.10, A1 0.10
soic("TI_DRV2605L_VSSOP10_DGS", 3.00, 3.00, 4.90, 1.00, 0.10, 10, 0.50, 0.22, 0.55,
     "TI drawing DGS0010A, JEDEC MO-187 BA. The hand-solderable package.")

# DRV2605L DSBGA-9 (YZF) : 1.44 x 1.44, 0.625 max height, 9 balls 0.30 dia, 0.5 pitch
_dbody = box(1.44, 1.44, 0.625 - 0.30, z=0.30)
_dballs = None
for bx in (-0.5, 0.0, 0.5):
    for by in (-0.5, 0.0, 0.5):
        s = Pos(bx, by, 0.15) * Sphere(0.30 / 2)
        _dballs = s if _dballs is None else _dballs + s
save("TI_DRV2605L_DSBGA9_YZF", [("die", _dbody), ("balls_9x", _dballs)],
     "TI drawing YZF0009. 1.41-1.47 sq, 0.625 max height, 0.5 mm ball pitch.")

# MT6701 companion magnet
_mag = cyl(6.0, 2.5)
save("MT6701_diametric_magnet_D6x2p5", [("magnet", _mag)],
     "NdFeB, DIAMETRICALLY magnetised. Face-to-package-top air gap "
     "0.5 min / 1.0 typ / 2.0 max. Field at the sensor 200-1000 Gauss.")

with open(os.path.join(OUT, "_report.json"), "w") as f:
    json.dump(REPORT, f, indent=1)
print(f"\n{len(REPORT)} models written to {OUT}")
