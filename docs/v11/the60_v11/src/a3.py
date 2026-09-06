"""A3 technical drawings, one sheet per made part: plan (slices at three heights), front and side
sections through the part's centre, overall dimensions, a title block, notes and the part's key
dimensions from the parameter block.  Sheet 0 lists every ASSUMED number."""
import os, sys, math, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from model import *
from params import ASSUMED_LIST

made = made_parts(knurl=False)
DATE = "2026-09-05"
def slice_edges(shape, z):
    slab = Pos(0, 0, z) * Box(400, 400, 0.02)
    try: sec = shape & slab
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        n = max(8, min(200, int(e.length / 1.5)))
        pts = [e.position_at(t) for t in [i/n for i in range(n + 1)]]
        if abs(pts[0].Z - z) > 0.05: continue
        out.append([(p.X, p.Y) for p in pts])
    return out
def vsection(shape, axis, c):
    """edges of the part cut by the vertical plane x = c (axis 'x') or y = c (axis 'y')"""
    if axis == "x": plane = Pos(c, 0, 0) * Box(0.02, 400, 400)
    else: plane = Pos(0, c, 0) * Box(400, 0.02, 400)
    try: sec = shape & plane
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        n = max(8, min(200, int(e.length / 1.5)))
        pts = [e.position_at(t) for t in [i/n for i in range(n + 1)]]
        out.append([((p.Y if axis == "x" else p.X), p.Z) for p in pts])
    return out
def dim_h(ax, x0, x1, y, text, off=6):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.plot([x0, x0], [y - off*0.4, y + off*0.4], color="k", lw=0.5); ax.plot([x1, x1], [y - off*0.4, y + off*0.4], color="k", lw=0.5)
    ax.text((x0 + x1)/2, y + 1.0, text, ha="center", va="bottom", fontsize=7.5)
def dim_v(ax, x, y0, y1, text, off=6):
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.plot([x - off*0.4, x + off*0.4], [y0, y0], color="k", lw=0.5); ax.plot([x - off*0.4, x + off*0.4], [y1, y1], color="k", lw=0.5)
    ax.text(x + 1.0, (y0 + y1)/2, text, ha="left", va="center", fontsize=7.5, rotation=90)

SHEETS = [
    ("knob_body", "Knob", "PETG (prototype) / CNC 6082-T6, hard anodised (production)", "print top face down, 0.16 mm; no supports",
     [f"outside Ø{2*R_KNOB:.1f}, bore Ø{2*R_BORE:.1f} (0.45 to the panel's chin corners); wall {SKIRT_WALL:.1f}", f"top rim: lip inner edge Ø{2*R_CROWN_IN:.1f}, {CH_IN} inner chamfer, {RIM_FLAT:.0f} flat, {CH_TOP} outer chamfer (RULING 6 Sep: rim >= 20); lip 3.0 thick, top at z {Z_KNOB_TOP:.2f}", "outer chamfer 2.5 x 45° smooth; inner chamfer 1.0; skirt chamfer 1.2",
      f"V-groove 90°, root r {R_GROOVE_ROOT}, z {Z_GROOVE0:.1f}-{Z_GROOVE1:.1f}", f"code-band recess 0.15 deep, z {Z_CODE0:.1f}-{Z_CODE1:.1f}", f"diamond knurl {KNURL_N} starts x 2, {KNURL_DEPTH} deep, helix {KNURL_HELIX_DEG:.1f}°, 4 whole rows z {KNURL_Z0:.1f}-{KNURL_Z1:.1f}; skirt bottom z {Z_SKIRT_BOT}", f"wall under the knurl root {SKIRT_WALL - KNURL_DEPTH:.1f}"]),
    ("internal_structure", "Internal structure", "PETG (prototype) / PA12 (production)", "print upright on the wall foot, 0.20 mm; supports ONLY under the seat flange (inside) and the diffuser lip (outside)",
     [f"wall r {R_WALL_IN}-{R_WALL_OUT}, z {Z_PLATE_TOP}-{Z_SEAT_TOP}", f"seat flange r {R_SEAT_IN}-{R_WALL_OUT}, z {Z_SEAT_BOT}-{Z_SEAT_TOP}; three Ø2 locating nubs at {NUB_AZ}°", f"LED-strip band r {R_WALL_OUT}-{R_STRIP_BACK}, z {Z_PLATE_TOP}-{HALO_Z1} (strip r {R_STRIP_IN}-{R_STRIP_OUT}); diffuser lip r {R_WALL_OUT}-{R_LIP_OUT}, z {Z_LIP0}-{Z_LIP1}",
      f"wheel posts Ø{WHEEL_POST_D} at r {BUSH_R:.2f}, az {WHEEL_AZ}, to z {Z_POST_TOP:.1f}; bush bores Ø{BUSH_D + 0.1}; wall windows 15.2 wide, open to the top from z {Z_POST_TOP - 0.3:.1f}; the seat flange is cut away above each wheel", f"pillars Ø7 at r {PILLAR_R}, az {PILLAR_AZ}, to z {Z_DECK0:.2f}; M3 inserts top (all) and bottom ({PLATE_SCREW_AZ})",
      f"encoder tower at {ENC_AZ}° to z {ENC_TOWER_TOP:.1f}, board slot open to the top, window through the wall at the code band; motor window open to the seat; LRA pad at {LRA_AZ}°", f"flex slot 32 x 2.5 through the seat at 0°, offset -4; {len(slit_azs())} vent slits {SLIT_W} x {SLIT_Z1 - SLIT_Z0:.1f} at z {SLIT_Z0}-{SLIT_Z1}, 2.5° grid", "motor relief at 90°"]),
    ("deck", "Mezzanine deck", "PETG", "print upside down (flat top face on the bed, legs up), 0.20 mm; no supports; 14 x M2.5 nuts pressed into the top pockets",
     [f"disc Ø{2*DECK_R:.0f} x {DECK_T:.1f}, z {Z_DECK0:.2f}-{Z_DECK1:.2f}; 14 hex pockets {NUT_POCKET_AF} across flats x {NUT_POCKET_D} deep in the top face for M2.5 nuts (the boards sit on the nuts, 1.0 proud)", f"three legs Ø5.5 down to the Pi's board top (z {PI_Z_TOP}), M2.5 inserts", f"tab slot 6.0 x 10.6 at 90°; ribbon slot 22 x 3 at ({HDMI0_X:.1f}, {PI_Y0 - 6.5:.1f})",
      f"Ø3.4 holes at the pillars; notches at the wheel posts and the encoder tower", "M2.5 insert bosses for the adapter, audio, motion boards and the servo tray"]),
    ("halo_diffuser", "Halo diffuser", "opal PMMA (production) / natural PETG (prototype)", "print on its underside, 0.20 mm; no supports",
     [f"r {R_DIFF_IN:.1f}-{R_DIFF_OUT_BOT:.1f} at the bottom, to r {R_DIFF_OUT_TOP:.1f} at the top; z {HALO_Z0}-{HALO_Z1}", f"{DIFF_CHAMFER} chamfer on the outside top edge", f"retained by the structure's lip (r to {R_LIP_OUT:.1f}); sits on the rim ring 0.2 outside the LED strip"]),
    ("carriage", "Motor carriage", "PETG", "print standing on the shoe, 0.16 mm; no supports (12 mm bridge over the sensor pocket); 4+ perimeters for the tab",
     [f"shoe Ø37 x {CARRIAGE_T}; locating rim Ø35.6/37 x 0.6", "commutation-board pocket 12.4 x 12.4 x 3.3; sight hole Ø9", f"push tab {CARRIAGE_TAB_T} x {CARRIAGE_TAB_W} to z {CARRIAGE_TAB_TOP:.2f} (through the deck to the servo)", f"travel {CLUTCH_LIFT} radial in the plate's stadium hole"]),
    ("servo_mount", "Servo tray (on the deck)", "PETG", "print flat, 0.20 mm; no supports (6 mm bridges over the nut pockets)",
     [f"tray for the AGFRC envelope {SERVO_L} x {SERVO_W} x {SERVO_H}; walls 1.0, floor {SERVO_TRAY_T}", "open toward the carriage tab; lead exit at the inner end", "2 ears, M2.5 x 4 screws into the deck's captive nuts (round 1.0 pockets over the nuts)"]),
    ("speaker_cradle", "Speaker cradle", "PETG", "print flat, 0.20 mm; no supports (fingers full height)",
     ["ring r 18.3-20.5 x 4.45 under the Ø40 flange", "three snap fingers at 80/200/320° (local)", "two ears at ±22.5 on the local x axis, M3 countersunk from below the plate"]),
    ("port_face", "Rear port face", "PETG", "print lying on its outer face, 0.16 mm; no supports (the socket holes print vertical)",
     [f"{PORT_W} wide x {PORT_FACE_T} thick at r {PORT_FACE_R0}, z {-PAD_T}-{Z_PLATE_TOP}", f"barrel nose Ø6.2 at t {PORT_BARREL_T}, z {BARREL_AXIS_Z}; USB-C opening at t {PORT_USBC_T}, z {USBC_AXIS_Z}; jack Ø6.3 at t {PORT_JACK_T}, z {JACK_AXIS_Z}; light aperture Ø{SENSOR_HOLE_D} at t {PORT_LIGHT_T}",
      f"shelf for the USB-C board; foot for the light-sensor board; rail along the top on the plate (1.5 tall, {2*PORT_TAB_T + 6:.0f} wide, inner edge r {PORT_TAB_R - 2.5:.1f}, flat front in the face's plane, corners cut 45° to stay inside the diffuser) with two Ø2.2 holes at r {PORT_TAB_R:.1f}, t ±{PORT_TAB_T:.0f}: M2 screws into the plate"]),
    ("collar_0", "Wheel V-collar (x3)", "PETG (prototype) / POM (production)", "print axis vertical, 0.12 mm",
     [f"Ø{WHEEL_OD} x {WHEEL_W}, 90° V {WHEEL_V_H} deep with a {WHEEL_V_FLAT} flat; bore Ø10 press over a 623ZZ"]),
    ("bush_0", "Eccentric bush (x3)", "PETG (prototype) / brass (production)", "print stem down / pin up, 0.12 mm; the 1 mm flange ledge is the only overhang",
     [f"Ø{BUSH_D} shank x 6, Ø{BUSH_FLANGE_D} x {BUSH_FLANGE_T} flange, Ø{WHEEL_BORE} pin x {WHEEL_W} offset {WHEEL_ECC}; 2 mm hex socket"]),
    ("base_plate", "Base plate - aluminium core (the heatsink)", "6082 aluminium, CNC two-sided, black hard anodised on every face (masked bare pads at the ground bond and under the converter)", "machined, not printed (print a PETG stand-in without the duct for the fit check)",
     [f"r < {RIM_IN:.1f} x {PLATE_T}: {WEB_T:.0f} web (z {WEB_T:.0f}-{PLATE_T:.0f}), {DUCT_H:.0f} duct (z {CLOSING_T:.0f}-{CLOSING_T + DUCT_H:.0f}) closed by a 1 mm plate in a recess; rebate r {R_CORE_DUCT:.1f}-{RIM_IN:.1f}, z {RIM_STEP_Z:.0f}-{PLATE_T:.0f} for the ring's flange, 7 x M3 csk from below at r {RING_SCREW_R}",
      f"duct: collector r {COLLECTOR_R0:.0f}-{R_CORE_DUCT - DUCT_WALL:.1f} (front and sides), straight channels {FIN_CH_W:.0f} wide on a {FIN_PITCH:.0f} pitch beside the Pi window, rear plenum r {PLENUM_R0:.0f}+, blower envelope {BLOWER_W:.0f} x {BLOWER_L:.0f} x {BLOWER_H:.0f} at az {BLOWER_AZ:.0f} (not fitted); {DUCT_MARGIN} walls round every through-cut",
      f"Pi window, carriage hole, port slot; 2 x M3 csk for the speaker cradle; ground-bond hole; 2 x M2.5 tapped for the converter at az {CONV_AZ:.0f}, r {CONV_R}, t ±{CONV_HOLE_T:.0f}; {len(CLOSING_SCREW_XY)} x M2.5 tapped for the closing plate",
      f"{len(RIB_AZ)} ribs {RIB_T} x {RIB_H} tall on the top face at r {RIB_R0:.0f}-{RIB_R1:.0f}, az {RIB_AZ}"]),
    ("rim_ring_STEEL", "Rim ring (steel)", "mild steel, machined, black (RULING 6 Sep: steel for mass)", "machined, not printed",
     [f"r {RIM_IN:.1f}-{PLATE_R:.1f} x {PLATE_T}; engine-turned edge: {ET_BLOCKS} plain blocks {ET_BLOCK_DEG:.0f}° wide at 0/30/60..., {len(et_groove_azs())} square grooves {ET_GROOVE_W} x {ET_GROOVE_D} at {ET_PITCH} pitch between them; {PLATE_CHAMFER} chamfer top and bottom outer edges",
      f"inward flange r {R_CORE_DUCT:.1f}-{RIM_IN:.1f}, z {RIM_STEP_Z:.0f}-{PLATE_T:.0f}, 7 x M3 tapped blind from below at r {RING_SCREW_R}, az {RING_SCREW_AZ}",
      f"intake: {INTAKE_UNDERCUT_H} undercut on the bottom outer edge outside r {INTAKE_UNDERCUT_R:.1f} over az {INTAKE_AZ0:.0f}-{INTAKE_AZ1:.0f}, feeding {len(intake_azs())} radial grooves {INTAKE_W} x {INTAKE_H} in the underside (the pad closes them); exhaust: {len(EXHAUST_AZ)} grooves at az {EXHAUST_AZ}, opening downward where the pad is cut away",
      f"3 x M3 csk from below at r {PILLAR_R:.1f}, az {PLATE_SCREW_AZ} (the structure's pillars); 2 x Ø1.6 tapped M2 at r {PORT_TAB_R:.1f}, t ±{PORT_TAB_T:.0f} (the port face's rail); port slot {PORT_W} wide"]),
    ("closing_plate_AL", "Closing plate (aluminium)", "1 mm aluminium, laser-cut, black anodised", "laser-cut, not printed",
     [f"disc r {R_CORE_DUCT - 0.1:.1f} x {CLOSING_T}, flush in the core's recess; same Pi window, carriage hole and port slot as the core", f"{len(CLOSING_SCREW_XY)} x M2.5 countersunk; unscrew to clean the fin channels"]),
]
def sheet(pdf, i, name, title, material, printnote, dims):
    shape = {"collar_0": wheel_collar(), "bush_0": ecc_bush()}.get(name, made[name])
    bb = shape.bounding_box()
    cx, cy = (bb.min.X + bb.max.X)/2, (bb.min.Y + bb.max.Y)/2
    s = Pos(-cx, -cy, 0) * shape
    bb = s.bounding_box()
    L, W, H = bb.size.X, bb.size.Y, bb.size.Z
    fig = plt.figure(figsize=(420/25.4, 297/25.4))
    fig.patch.set_facecolor("white")
    # frame
    fr = fig.add_axes([0, 0, 1, 1]); fr.axis("off"); fr.set_xlim(0, 420); fr.set_ylim(0, 297)
    fr.add_patch(plt.Rectangle((10, 10), 400, 277, fill=False, lw=1.2))
    # title block
    fr.add_patch(plt.Rectangle((230, 10), 180, 42, fill=False, lw=1.0))
    fr.plot([230, 410], [38, 38], color="k", lw=0.6); fr.plot([330, 330], [10, 38], color="k", lw=0.6)
    fr.text(233, 46, "the 60 — v11", fontsize=12, weight="bold"); fr.text(300, 46, f"{title}", fontsize=12, weight="bold")
    fr.text(233, 41, f"Cadrane · sheet {i} of {len(SHEETS)} · {DATE} · drawn from src/params.py + model.py (build123d)", fontsize=7)
    fr.text(233, 32, f"Material: {material}", fontsize=7.5); fr.text(233, 26, f"Process: {printnote}", fontsize=7.5)
    fr.text(233, 20, "mm. Tolerance ±0.1 unless stated; clearances: running 0.30,", fontsize=7)
    fr.text(233, 14, "static 0.15, knob 0.40. Printed as-built; CNC knob Ra 0.8 on the chamfers.", fontsize=7)
    fr.text(333, 32, f"Part: {name}", fontsize=8, weight="bold"); fr.text(333, 26, f"Overall {L:.1f} x {W:.1f} x {H:.1f}", fontsize=8)
    fr.text(333, 20, f"Volume {s.volume/1000:.2f} cm³", fontsize=8); fr.text(333, 14, "Scale: see each view (fit)", fontsize=8)
    # notes
    fr.text(14, 48, "Key dimensions (from the parameter block):", fontsize=8, weight="bold")
    for k, d in enumerate(dims[:8]): fr.text(14, 43 - 4.4*k, f"{k+1}. {d}", fontsize=7)
    # views
    span = max(L, W, H) * 1.35 + 20
    def view(rect, title):
        ax = fig.add_axes(rect); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=8.5, weight="bold"); return ax
    ax = view([0.03, 0.30, 0.44, 0.62], "PLAN (from above): sections at three heights — bottom (light), middle, top (dark)")
    ax.set_xlim(-span/2, span/2); ax.set_ylim(-span/2, span/2)
    for z, col in ((bb.min.Z + 0.4, "0.7"), ((bb.min.Z + bb.max.Z)/2, "0.4"), (bb.max.Z - 0.4, "0.05")):
        for seg in slice_edges(s, z):
            xs, ys = zip(*seg); ax.plot(xs, ys, color=col, lw=0.7)
    dim_h(ax, bb.min.X, bb.max.X, bb.max.Y + span*0.06, f"{L:.1f}")
    dim_v(ax, bb.max.X + span*0.06, bb.min.Y, bb.max.Y, f"{W:.1f}")
    ax.plot([-span/2*0.9, span/2*0.9], [0, 0], color="0.6", lw=0.4, ls="-."); ax.plot([0, 0], [-span/2*0.9, span/2*0.9], color="0.6", lw=0.4, ls="-.")
    ax2 = view([0.50, 0.55, 0.47, 0.40], "SECTION A-A (front, plane y = 0; x across, z up)")
    ax2.set_xlim(-span/2, span/2); ax2.set_ylim(bb.min.Z - span*0.15, bb.max.Z + span*0.15)
    for seg in vsection(s, "y", 0.0):
        xs, zs = zip(*seg); ax2.plot(xs, zs, color="0.05", lw=0.7)
    dim_v(ax2, bb.max.X + span*0.06, bb.min.Z, bb.max.Z, f"{H:.2f}")
    ax3 = view([0.50, 0.20, 0.23, 0.33], "SECTION B-B (side, plane x = 0; y across, z up)")
    ax3.set_xlim(-span/2, span/2); ax3.set_ylim(bb.min.Z - span*0.15, bb.max.Z + span*0.15)
    for seg in vsection(s, "x", 0.0):
        ys, zs = zip(*seg); ax3.plot(ys, zs, color="0.05", lw=0.7)
    # detail: the right-hand end of section A-A, enlarged (the profile that matters on ring-shaped parts)
    dx0, dx1 = bb.max.X - min(L * 0.25, 30.0), bb.max.X + 2.0
    ax4 = view([0.74, 0.20, 0.23, 0.33], f"DETAIL C (section A-A, x {dx0:.0f} to {dx1:.0f}, enlarged)")
    dspan = max(dx1 - dx0, H) * 1.2
    ax4.set_xlim(dx0 - 1, dx0 - 1 + dspan); ax4.set_ylim((bb.min.Z + bb.max.Z)/2 - dspan/2, (bb.min.Z + bb.max.Z)/2 + dspan/2)
    for seg in vsection(s, "y", 0.0):
        xs, zs = zip(*seg); ax4.plot(xs, zs, color="0.05", lw=0.9)
    for zz in sorted(set(round(p, 2) for seg in vsection(s, "y", 0.0) for _, p in seg if abs(seg[0][1] - seg[-1][1]) < 0.01)):
        pass
    pdf.savefig(fig); plt.close(fig)
    print("  sheet", i, name, flush=True)

pdf_path = os.path.join(OUT, "the60_v11_A3_drawings.pdf")
with PdfPages(pdf_path) as pdf:
    # sheet 0: assumptions
    fig = plt.figure(figsize=(420/25.4, 297/25.4)); fr = fig.add_axes([0, 0, 1, 1]); fr.axis("off"); fr.set_xlim(0, 420); fr.set_ylim(0, 297)
    fr.add_patch(plt.Rectangle((10, 10), 400, 277, fill=False, lw=1.2))
    fr.text(14, 278, "the 60 — v11 — sheet 0: the ASSUMED numbers (every one of these must be verified on the real part before the drawing is trusted)", fontsize=12, weight="bold")
    fr.text(14, 270, f"{DATE}.  Stack: plate {PLATE_T}, deck {Z_DECK0:.2f}-{Z_DECK1:.2f}, seat {Z_SEAT_TOP}, glass {Z_GLASS0:.2f}-{Z_GLASS1:.2f}, lens to {Z_LENS1:.2f}, knob top {Z_KNOB_TOP:.2f}, overall {HEIGHT:.2f} with the pad.  Ø{2*R_KNOB:.0f}.", fontsize=8.5)
    for k, (n, v, why) in enumerate(ASSUMED_LIST):
        fr.text(14, 258 - 7*k, f"{k+1:2d}. {n}: {v}", fontsize=8.5, weight="bold"); fr.text(180, 258 - 7*k, why, fontsize=8.5)
    fr.text(14, 60, "Build-time changes against V11-SPECIFICATION.md are listed in V11.md.  Sheets 1-11 follow: one per made part.", fontsize=8.5)
    pdf.savefig(fig); plt.close(fig)
    for i, (name, title, material, printnote, dims) in enumerate(SHEETS, start=1):
        sheet(pdf, i, name, title, material, printnote, dims)
print("wrote", pdf_path)
