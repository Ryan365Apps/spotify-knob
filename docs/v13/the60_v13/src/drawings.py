"""v13 general arrangement: plan slices at four heights plus sections through the motor and the back."""
import os, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from model import *

made = made_parts(knurl=False); bought = bought_parts(True)
allp = {**made, **bought}
COL = {"base_plate": "0.45", "rim_ring_STEEL": "0.3", "closing_plate_AL": "0.6", "internal_structure": "#7a6a4a", "halo_diffuser": "#3a9ab0", "knob_body": "0.15", "connect_bracket": "#9a5a1a", "servo_mount": "#9a5a1a",
       "carriage": "#c46a10", "servo_mount": "#5a3a9a", "speaker_cradle": "#c46a10", "port_face": "#1a7a3c", "led_flex": "#c8892a", "pad": "0.7", "bond_tape": "#b07030"}
def colour(n):
    if n in COL: return COL[n]
    if n.endswith("_board"): return "#1a7a3c"
    if n.startswith("collar") or n.startswith("bush") or n.startswith("bearing"): return "#8a4a8a"
    if n.startswith("motor"): return "#8a6d00"
    if n.startswith("servo"): return "#5a3a9a"
    if n.startswith("panel") or n.startswith("lens") or n.startswith("touch"): return "#1f4e9c"
    if n.startswith("pi_") or n.startswith("cooler"): return "#b0294a"
    if n.startswith("led_"): return "#c8892a"
    if "plug" in n or "ribbon" in n or "housing" in n: return "#b02020"
    if n == "speaker": return "#c46a10"
    if n.startswith("adapter") or n.startswith("audio") or n.startswith("motion") or n.startswith("converter"): return "#2a8a6a"
    return "#1a7a3c"
def slice_edges(shape, z):
    slab = Pos(0, 0, z) * Box(300, 300, 0.02)
    try: sec = shape & slab
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        pts = [e.position_at(t) for t in [i/16 for i in range(17)]]
        if abs(pts[0].Z - z) > 0.05: continue
        out.append([(p.X, p.Y) for p in pts])
    return out
def section_edges(shape, az):
    a = D(az)
    plane = Rot(0, 0, az) * Box(300, 0.02, 200, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    try: sec = shape & plane
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        pts = [e.position_at(t) for t in [i/16 for i in range(17)]]
        out.append([(p.X*math.cos(a) + p.Y*math.sin(a), p.Z) for p in pts])
    return out
def plan(ax, z, title, names):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-84, 84); ax.set_ylim(-84, 84)
    ax.set_title(title, fontsize=9.5, weight="bold")
    for n in names:
        if n not in allp: continue
        for seg in slice_edges(allp[n], z):
            xs, ys = zip(*seg); ax.plot(xs, ys, color=colour(n), lw=0.8)
    ax.add_patch(mp.Circle((0, 0), R_BORE, fill=False, ec="0.75", ls=":", lw=0.8))
    ax.annotate("0° = rear, sockets", (77, 0), fontsize=7, color="0.4", rotation=90, va="center")

fig = plt.figure(figsize=(22, 13))
fig.suptitle(f"the 60 — v13 general arrangement.  Pi 5 in the plate window on the closing plate, every board on the plate, adapter on the Pi's standoffs, 5-inch panel bonded to the seat.  "
             f"Ø{2*R_KNOB:.0f} × {HEIGHT:.1f} mm, knob {KNOB_FRACTION*100:.0f} % of the side.", fontsize=12.5, weight="bold", y=0.985)
everything = list(allp)
floor = [n for n in everything if not (n.startswith("panel") or n.startswith("lens") or n.startswith("touch")) and n not in ("knob_body", "halo_diffuser")]
ax = fig.add_axes([0.01, 0.50, 0.32, 0.45]); plan(ax, 4.0, "plan at z = 4 — inside the 8 mm plate: Pi window, carriage hole, port slot with the three plugs", floor)
ax = fig.add_axes([0.34, 0.50, 0.32, 0.45]); plan(ax, 12.0, "plan at z = 12 — motor, Pi + heatsink, servo, converter, speaker, boards", floor + ["knob_body"])
ax = fig.add_axes([0.67, 0.50, 0.32, 0.45]); plan(ax, 18.0, "plan at z = 18 — adapter over the Pi, its sockets; flat cable; touch board", floor + ["knob_body"])
ax = fig.add_axes([0.01, 0.03, 0.32, 0.45]); plan(ax, 27.0, "plan at z = 27 — the panel on its seat, chin at 180°, flex at 0°", floor + ["knob_body", "panel_glass", "panel_components_ENVELOPE"])
def section(ax, az, title):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-84, 84); ax.set_ylim(-4, 44)
    ax.set_title(title, fontsize=9.5, weight="bold")
    for n in everything:
        for seg in section_edges(allp[n], az):
            rs, zs = zip(*seg); ax.plot(rs, zs, color=colour(n), lw=0.8)
    for z, t in ((0, "plate underside z 0"), (Z_PLATE_TOP, "plate top / halo bottom 8.0"), (Z_MOTOR_TOP, "motor top 18.2"),
                 (Z_ADAPTER0, f"adapter {Z_ADAPTER0:.1f}"), (Z_GLASS0, f"glass back {Z_GLASS0:.1f}"), (Z_KNOB_TOP, f"knob top {Z_KNOB_TOP:.1f}")):
        ax.plot([-83, 83], [z, z], color="0.85", lw=0.5, ls=":"); ax.annotate(t, (-83, z + 0.3), fontsize=6.5, color="0.5")
ax = fig.add_axes([0.34, 0.03, 0.32, 0.45]); section(ax, 90, "section through the motor (azimuth 90°, right = motor side; servo on the plate inboard of it)")
ax = fig.add_axes([0.67, 0.03, 0.32, 0.45]); section(ax, 0, "section through the back (azimuth 0°, right = sockets and plugs; left = Pi's micro-SD end)")
fig.text(0.01, 0.005, "Bought parts drawn from their own STEP bodies (panel, Pi 5, motor, servo, bearings, speaker, encoder, LRA, sockets, chips, LEDs).  Envelope-only: cooler heatsink, adapter/audio/motion/converter/touch boards' parts, plugs, ribbon, flex.  "
         "Colours: grey plate, brown structure, orange bracket and frame, black knob, crimson Pi, gold motor, purple servo/wheels, teal boards, blue display, red plugs and cables.", fontsize=7.5, color="0.35")
fig.savefig(os.path.join(OUT, "v13_ga.png"), dpi=110)
print("wrote", os.path.join(OUT, "v13_ga.png"))
