"""v9 general arrangement: real plan slices at four heights plus a section through the motor."""
import os, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from model import *

made = made_parts(knurl=False); bought = bought_parts(True)
allp = {**made, **bought}
COL = {"base_plate": "0.45", "internal_structure": "#7a6a4a", "halo_diffuser": "#3a9ab0", "knob_body": "0.15",
       "carriage": "#c46a10", "servo_mount": "#5a3a9a", "speaker_cradle": "#c46a10", "port_face": "#1a7a3c",
       "driver_board": "#1a7a3c", "encoder_board": "#1a7a3c", "usbc_board": "#1a7a3c", "jack_board": "#1a7a3c",
       "light_board": "#1a7a3c", "commutation_board": "#1a7a3c", "led_flex": "#c8892a", "pad": "0.7"}
def colour(n):
    if n in COL: return COL[n]
    if n.startswith("collar") or n.startswith("bush") or n.startswith("bearing"): return "#8a4a8a"
    if n.startswith("motor"): return "#8a6d00"
    if n.startswith("servo"): return "#5a3a9a"
    if n.startswith("display"): return "#1f4e9c"
    if n.startswith("led_"): return "#c8892a"
    if n.startswith("plug"): return "#b02020"
    if n == "speaker": return "#c46a10"
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
    """edges of the part cut by the vertical half-plane at azimuth az (and az+180), returned as (r, z) with sign"""
    a = D(az)
    plane = Rot(0, 0, az) * Box(300, 0.02, 200, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    try: sec = shape & plane
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        pts = [e.position_at(t) for t in [i/16 for i in range(17)]]
        rr = [(p.X*math.cos(a) + p.Y*math.sin(a), p.Z) for p in pts]
        out.append(rr)
    return out

def plan(ax, z, title, names):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-70, 70); ax.set_ylim(-70, 70)
    ax.set_title(title, fontsize=9.5, weight="bold")
    for n in names:
        if n not in allp: continue
        for seg in slice_edges(allp[n], z):
            xs, ys = zip(*seg); ax.plot(xs, ys, color=colour(n), lw=0.8)
    ax.add_patch(mp.Circle((0, 0), R_BORE, fill=False, ec="0.75", ls=":", lw=0.8))
    ax.annotate("0° = USB-C, back", (63, 0), fontsize=7, color="0.4", rotation=90, va="center")

fig = plt.figure(figsize=(22, 13))
fig.suptitle(f"the 60 — v9 general arrangement.  MY-3514C on a sliding carriage, proportional clutch, 5 mm plate, halo on the plate edge.  "
             f"Ø{2*R_KNOB:.0f} × {HEIGHT:.1f} mm, knob {KNOB_FRACTION*100:.0f} % of the side.", fontsize=12.5, weight="bold", y=0.985)

everything = list(allp)
floor = [n for n in everything if not n.startswith("display") and n not in ("knob_body", "halo_diffuser")]
ax = fig.add_axes([0.01, 0.50, 0.32, 0.45]); plan(ax, 3.0, "plan at z = 3 — inside the 5 mm plate: carriage hole, port slot, plug, jack, USB-C", floor)
ax = fig.add_axes([0.34, 0.50, 0.32, 0.45]); plan(ax, 10.0, "plan at z = 10 — motor on its carriage, servo, speaker, driver board, wall ports", floor + ["knob_body"])
ax = fig.add_axes([0.67, 0.50, 0.32, 0.45]); plan(ax, 20.0, "plan at z = 20 — wheel posts, columns, encoder seat, display components", floor + ["knob_body"] + [n for n in everything if n.startswith("display_part")])
ax = fig.add_axes([0.01, 0.03, 0.32, 0.45]); plan(ax, 27.0, "plan at z = 27 — wheels in the groove, board edge, seat tabs", floor + ["knob_body", "display_pcb"])

# section through the motor (az 90) and the back (az 0)
def section(ax, az, title):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-70, 70); ax.set_ylim(-4, 44)
    ax.set_title(title, fontsize=9.5, weight="bold")
    for n in everything:
        if n == "display_small_parts": continue
        for seg in section_edges(allp[n], az):
            rs, zs = zip(*seg); ax.plot(rs, zs, color=colour(n), lw=0.8)
    for z, t in ((0, "plate underside z 0"), (Z_PLATE_TOP, "plate top / halo bottom 5.0"), (Z_MOTOR_TOP, "motor top 18.2"),
                 (Z_COMP_BOT, "display lowest 19.2"), (Z_DISC_TOP, "glass 34.7"), (Z_KNOB_TOP, "knob top 38.1")):
        ax.plot([-69, 69], [z, z], color="0.85", lw=0.5, ls=":"); ax.annotate(t, (-69, z + 0.3), fontsize=6.5, color="0.5")
ax = fig.add_axes([0.34, 0.03, 0.32, 0.45]); section(ax, 90, "section through the motor (azimuth 90°, right = motor side)")
ax = fig.add_axes([0.67, 0.03, 0.32, 0.45]); section(ax, 0, "section through the back (azimuth 0°, right = USB-C, jack, port face)")

fig.text(0.01, 0.005, "Bought parts drawn from their own STEP bodies.  Envelope-only parts: motor (Ø35 × 14, no base/bell split), servo (21.4 × 15.2 × 6 + stroke), plugs.  "
         "Colours: grey plate, brown structure, black knob, gold motor, purple servo/wheels, orange carriage/speaker, green boards, amber LEDs, blue display, red plug envelopes.",
         fontsize=7.5, color="0.35")
fig.savefig(os.path.join(OUT, "v9_ga.png"), dpi=110)
print("wrote", os.path.join(OUT, "v9_ga.png"))
