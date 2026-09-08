"""free-area map above the v15 plate top and a placement search for the bought boards named in FUNCTION-ALLOCATION.md"""
import pickle, math
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity, prepared
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = pickle.load(open("/home/claude/v9/v15/slices.pkl", "rb"))
ZS, slices, R_WALL_IN = d["ZS"], d["slices"], d["R_WALL_IN"]
disc = Point(0, 0).buffer(R_WALL_IN - 0.3, 256)
FLEX = ("hdmi_ribbon", "cable_", "cb_cn1_cable", "cb_cn2_panel_flex", "fan_lead", "halo_tail", "motor_bond_wire", "usbc_shell_wire", "sensor_cable", "panel_flex", "lra_fpc_tail", "touch_tail", "usbc_plug_pi_ENVELOPE_cable", "chassis_bond_ring_terminal")
def flexible(n): return any(n.startswith(f) for f in FLEX)

def occupied(z_top):
    """everything cut by any slice from the plate top up to z_top (the next slice above is included, conservatively)"""
    polys = []
    for z in ZS:
        if z <= z_top + 1.4:
            polys += [p for n, p in slices[z] if not flexible(n)]
    u = unary_union(polys)
    return u

boards = [  # name, L, W, height with headers, height bare
    ("ESP32-S3-DevKitC-1", 70.0, 28.0, 13.0, 8.0),
    ("Raspberry Pi Pico 2", 51.0, 21.0, 9.0, 4.5),
    ("TMC6300-BOB", 25.4, 20.3, 12.0, 5.0),
]
MARGIN = 1.0   # clearance all round
results = {}
for name, L, W, h_hdr, h_bare in boards:
    for tag, h in (("with headers", h_hdr), ("bare (wires soldered)", h_bare)):
        occ = occupied(8.0 + h)
        free = disc.difference(occ)
        pocc = prepared.prep(occ.buffer(MARGIN))
        found = []
        for az in range(0, 360, 4):
            for r in np.arange(20, 78, 2.0):
                cx, cy = r * math.cos(math.radians(az)), r * math.sin(math.radians(az))
                for rot in range(0, 180, 10):
                    rect = affinity.rotate(box(cx - L/2, cy - W/2, cx + L/2, cy + W/2), rot + az, origin=(cx, cy))
                    if not disc.contains(rect): continue
                    if pocc.intersects(rect): continue
                    found.append((az, r, rot, rect))
        results[(name, tag)] = (free, found)
        if found:
            # summarise as distinct clusters by azimuth
            azs = sorted(set(f[0] for f in found))
            # cluster the azimuths
            cl = []; 
            for a in azs:
                if cl and a - cl[-1][-1] <= 4: cl[-1].append(a)
                else: cl.append([a])
            print(f"{name} {L}x{W}, {h} tall ({tag}): {len(found)} placements; centre azimuths " + ", ".join(f"{c[0]}-{c[-1]}" for c in cl))
            best = max(found, key=lambda f: occ.distance(f[3]))
            print(f"    e.g. centre az {best[0]} r {best[1]:.0f}, long side at {best[2]} deg to the radial, clearance {occ.distance(best[3]):.1f} mm")
        else:
            print(f"{name} {L}x{W}, {h} tall ({tag}): NO placement inside r {R_WALL_IN-0.3:.1f} with {MARGIN} mm clearance")

# ---- picture: free area at two heights, with the best placements
fig, axes = plt.subplots(1, 2, figsize=(13, 6.6))
for ax, (ztop, title) in zip(axes, [(13.0, "free above the plate top, bodies up to z 13 (5 mm tall parts)"), (21.0, "free up to z 21 (13 mm tall parts)")]):
    occ = occupied(ztop)
    free = disc.difference(occ)
    geoms = free.geoms if hasattr(free, "geoms") else [free]
    for g in geoms:
        if g.area < 1: continue
        xs, ys = g.exterior.xy; ax.fill(xs, ys, color="#bfe3bf", lw=0)
        for i in g.interiors:
            xs, ys = i.xy; ax.fill(xs, ys, color="white", lw=0)
    ogeoms = occ.geoms if hasattr(occ, "geoms") else [occ]
    for g in ogeoms:
        if g.area < 0.5: continue
        xs, ys = g.exterior.xy; ax.plot(xs, ys, color="#666", lw=0.3)
    ax.add_patch(plt.Circle((0, 0), R_WALL_IN, fill=False, lw=0.8, color="k"))
    ax.set_aspect("equal"); ax.set_xlim(-90, 90); ax.set_ylim(-90, 90); ax.set_title(title, fontsize=9)
    ax.set_xlabel("x, mm (az 0 = rear/ports)", fontsize=7); ax.tick_params(labelsize=6)
    for deg in range(0, 360, 30):
        ax.text(86 * math.cos(math.radians(deg)), 86 * math.sin(math.radians(deg)), f"{deg}°", fontsize=5.5, ha="center", va="center", color="#444")
    print(f"free area up to z {ztop}: {free.area:.0f} mm2 of {disc.area:.0f}")
# best placements overlaid on the right-hand map (with headers) and left (bare)
colors = {"ESP32-S3-DevKitC-1": "#c0392b", "Raspberry Pi Pico 2": "#1f4e79", "TMC6300-BOB": "#7d3c98"}
for (name, tag), (free, found) in results.items():
    if not found: continue
    ax = axes[1] if tag == "with headers" else axes[0]
    occ = occupied(8.0 + [b for b in boards if b[0] == name][0][3 if tag == "with headers" else 4])
    best = max(found, key=lambda f: occ.distance(f[3]))
    xs, ys = best[3].exterior.xy
    ax.plot(xs, ys, color=colors[name], lw=1.4); ax.text(best[3].centroid.x, best[3].centroid.y, name.split()[0], fontsize=6, ha="center", va="center", color=colors[name])
fig.suptitle("the 60 v15 — free room above the plate top (green) with cables and wires ignored (they re-route); best-clearance placements for the bought boards, 1 mm margin", fontsize=9)
plt.tight_layout(); plt.savefig("/home/claude/v9/v15/board_room.png", dpi=160)
print("saved board_room.png")
