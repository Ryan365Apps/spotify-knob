"""layout study tool: v15 footprints (from slices.pkl) as fixed obstacles + movable groups + new bought parts;
evaluate a candidate layout (overlaps, clearances, free area) and draw it with a cable schematic."""
import pickle, math, collections
import numpy as np
from shapely.geometry import Point, box, Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = pickle.load(open("/home/claude/v9/v15/slices.pkl", "rb"))
ZS, SL, R_WALL_IN = D["ZS"], D["slices"], D["R_WALL_IN"]
FLEX = ("hdmi_ribbon", "cable_", "cb_cn1_cable", "cb_cn2_panel_flex", "fan_lead", "halo_tail", "motor_bond_wire", "usbc_shell_wire", "sensor_cable", "panel_flex", "lra_fpc_tail", "touch_tail", "usbc_plug_pi_ENVELOPE_cable", "chassis_bond_ring_terminal")
def flexible(n): return any(n.startswith(f) for f in FLEX)

# per-body footprint for the "low layer" (parts standing on the plate, up to z 14) and the "upper layer" (z 16-23.5)
def footprint(names, zmax=14.0, zmin=8.0):
    polys = [p for z in ZS if zmin <= z <= zmax for n, p in SL[z] if n in names and not flexible(n)]
    return unary_union(polys) if polys else None
ALL = sorted(set(n for z in ZS for n, _ in SL[z]))

GROUPS = {   # movable groups: bodies in v15 that move together
    "converter": [n for n in ALL if n.startswith("converter")],
    "audio": [n for n in ALL if n.startswith("audio") or n.startswith("board_washer")],
    "speaker": ["speaker", "speaker_cradle"],
    "blower": [n for n in ALL if n.startswith("blower") or n == "hood_lid"],
    "motion": [n for n in ALL if n.startswith("motion")],          # deleted in every candidate (bought boards replace it)
    "motor": [n for n in ALL if n.startswith("motor_") or n.startswith("servo") or n in ("carriage", "header_housing_ENVELOPE")],
    "lra": [n for n in ALL if n.startswith("lra")],
    "bonds": ["chassis_bond_screw", "ring_bond_screw"],
}
MOVABLE = set(sum(GROUPS.values(), []))
FIXED = [n for n in ALL if n not in MOVABLE and not flexible(n)]

# the structure's posts and pillars are part of one body; carve them out so they can move
POST_AZ, POST_R, PILLAR_AZ, PILLAR_R = [30, 150, 270], 76.93, [160, 240, 320], 77.2
def pol(az, r): return (r * math.cos(math.radians(az)), r * math.sin(math.radians(az)))
def post_shape(az):
    c = Point(pol(az, POST_R)).buffer(4.0)
    web = affinity.rotate(box(POST_R, -3.0, R_WALL_IN + 0.6, 3.0), az, origin=(0, 0))
    return unary_union([c, web])
def pillar_shape(az):
    c = Point(pol(az, PILLAR_R)).buffer(3.5)
    web = affinity.rotate(box(PILLAR_R, -3.5, R_WALL_IN + 0.6, 3.5), az, origin=(0, 0))
    return unary_union([c, web])

PI_X0, PI_Y0, PI_L, PI_W, PI_OVERHANG = -52.0, -38.0, 85.0, 56.0, 3.05
def pi_window():
    c = 0.75
    w = box(PI_X0 - c, PI_Y0 - c, PI_X0 + PI_L + PI_OVERHANG + c, PI_Y0 + PI_W + c)
    w = unary_union([w, box(-40.8 - 7, PI_Y0 - 14, -40.8 + 7, PI_Y0 + 1), box(-12.5 - 7, PI_Y0 - 9.5, -12.5 + 7, PI_Y0 + 1),
                     box(PI_X0 + PI_L + PI_OVERHANG - 1, PI_Y0 + 22, PI_X0 + PI_L + PI_OVERHANG + 10, PI_Y0 + 36)])
    return w
MOTOR_R, MOTOR_OD, CLUTCH_LIFT = 65.704, 35.0, 2.4
def carriage_hole(az=90.0):
    d = MOTOR_OD + 2 + 1.5
    h = unary_union([Point(pol(az, MOTOR_R)).buffer(d/2), Point(pol(az, MOTOR_R - CLUTCH_LIFT)).buffer(d/2),
                     affinity.rotate(box(MOTOR_R - MOTOR_OD/2 - 1 - 9.4, -5.75, MOTOR_R - MOTOR_OD/2 - 1, 5.75), az, origin=(0, 0))])
    return h

def base_fixed(zmax=14.0, grow=0.0):
    """fixed obstacles at Ø175.4 (grow=0) or with the rim-relative parts pushed out by `grow`"""
    polys = []
    for n in FIXED:
        p = footprint([n], zmax)
        if p is None: continue
        if n == "internal_structure":
            for az in POST_AZ: p = p.difference(post_shape(az).buffer(0.3))
            for az in PILLAR_AZ: p = p.difference(pillar_shape(az).buffer(0.3))
            if grow: p = affinity.scale(p, (R_WALL_IN + grow) / R_WALL_IN, (R_WALL_IN + grow) / R_WALL_IN, origin=(0, 0))
        elif n in ("port_face", "halo_diffuser", "led_strip_ENVELOPE") and grow:
            c = p.centroid; r = math.hypot(c.x, c.y)
            p = affinity.translate(p, grow * c.x / r, grow * c.y / r) if n == "port_face" else affinity.scale(p, (R_WALL_IN + grow) / R_WALL_IN, (R_WALL_IN + grow) / R_WALL_IN, origin=(0, 0))
        polys.append((n, p))
    polys.append(("pi_window", pi_window()))
    return polys

def rect(az, r, rot, L, W):
    cx, cy = pol(az, r)
    return affinity.rotate(box(cx - L/2, cy - W/2, cx + L/2, cy + W/2), rot + az, origin=(cx, cy))

class Layout:
    def __init__(self, name, grow=0.0):
        self.name, self.grow = name, grow
        self.R = R_WALL_IN + grow
        self.disc = Point(0, 0).buffer(self.R - 0.3, 256)
        self.items = list(base_fixed(14.0, grow))        # (name, polygon) — obstacles and placed parts alike
        self.movable_names = []
        self.cables = []
        self.notes = []
    def add(self, name, poly):
        self.items.append((name, poly)); self.movable_names.append(name)
    def add_group(self, g, daz=0.0, dr=0.0, mirror=False, zmax=14.0):
        p = footprint(GROUPS[g], zmax)
        if p is None: return
        if g == "motor": p = unary_union([p, carriage_hole(90.0)])
        if mirror: p = affinity.scale(p, 1, -1, origin=(0, 0))
        if daz: p = affinity.rotate(p, daz, origin=(0, 0))
        if dr:
            c = p.centroid; r = math.hypot(c.x, c.y); p = affinity.translate(p, dr * c.x / r, dr * c.y / r)
        self.add(g, p)
    def add_rect(self, name, az, r, rot, L, W): self.add(name, rect(az, r, rot, L, W))
    def add_circle(self, name, az, r, d): self.add(name, Point(pol(az, r)).buffer(d / 2))
    def add_post(self, az): self.add(f"post {az}", post_shape(az))
    def add_pillar(self, az): self.add(f"pillar {az}", pillar_shape(az))
    def cable(self, a, b, label=""): self.cables.append((a, b, label))
    def evaluate(self, margin=1.0):
        probs = []
        for i, (n1, p1) in enumerate(self.items):
            for n2, p2 in self.items[i + 1:]:
                if n1 not in self.movable_names and n2 not in self.movable_names: continue
                if p1.intersects(p2.buffer(margin)):
                    d = p1.distance(p2)
                    probs.append((n1, n2, d))
        for n, p in self.items:
            if n in self.movable_names and not self.disc.contains(p):
                probs.append((n, "wall", 0.0))
        occ = unary_union([p for _, p in self.items])
        free = self.disc.difference(occ)
        return probs, free.area
    def centre(self, name):
        for n, p in self.items:
            if n == name: return p.centroid
        return None
    def draw(self, ax, title):
        occ = unary_union([p for _, p in self.items]); free = self.disc.difference(occ)
        ax.add_patch(plt.Circle((0, 0), self.R, fc="#e6e6e6", ec="none"))
        for g in (free.geoms if hasattr(free, "geoms") else [free]):
            if g.area < 1: continue
            xs, ys = g.exterior.xy; ax.fill(xs, ys, color="#c8e6c9", lw=0)
            for i in g.interiors:
                xs, ys = i.xy; ax.fill(xs, ys, color="#e6e6e6", lw=0)
        for n, p in self.items:
            mv = n in self.movable_names
            for g in (p.geoms if hasattr(p, "geoms") else [p]):
                if g.is_empty or g.area < 0.3: continue
                xs, ys = g.exterior.xy
                if mv: ax.fill(xs, ys, color="#ffe0b2", lw=0.6, ec="#e65100")
                elif n == "pi_window": ax.plot(xs, ys, color="#555", lw=0.8, ls="--")
                else: ax.plot(xs, ys, color="#888", lw=0.3)
            if mv:
                c = p.centroid; ax.text(c.x, c.y, n, fontsize=5.5, ha="center", va="center", color="#7f2f00")
        ax.text(-8, -10, "Pi window\n(no plate here)", fontsize=5.5, ha="center", color="#555")
        for a, b, label in self.cables:
            ca, cb = (self.centre(a) if isinstance(a, str) else Point(a)), (self.centre(b) if isinstance(b, str) else Point(b))
            if ca is None or cb is None: continue
            ax.plot([ca.x, cb.x], [ca.y, cb.y], color="#1565c0", lw=0.7, ls="--", alpha=0.8)
            if label: ax.text((ca.x + cb.x)/2, (ca.y + cb.y)/2, label, fontsize=4.5, color="#1565c0", ha="center")
        ax.add_patch(plt.Circle((0, 0), self.R, fill=False, lw=0.8, color="k"))
        for deg in range(0, 360, 30):
            ax.text((self.R + 5) * math.cos(math.radians(deg)), (self.R + 5) * math.sin(math.radians(deg)), f"{deg}°", fontsize=5.5, ha="center", va="center", color="#444")
        ax.set_aspect("equal"); ax.set_xlim(-self.R - 9, self.R + 9); ax.set_ylim(-self.R - 9, self.R + 9)
        ax.set_title(title, fontsize=8, loc="left"); ax.tick_params(labelsize=5)
        ax.set_xlabel("x, mm (az 0 = rear, ports); grey fixed, orange movable/new, green free", fontsize=6)

def place_rect(L, name, Lg, Wg, margin=1.5, az_range=(0, 360), r_range=(20, 80), prefer=None):
    """greedy: the placement of an Lg x Wg rectangle with the largest clearance to everything placed so far (optionally pulled toward `prefer` (x,y))"""
    from shapely import prepared
    occ = unary_union([p for _, p in L.items]).buffer(margin); best = None
    pb = prepared.prep(occ)
    inner = L.disc.buffer(-margin)
    def trial(az, r, rot):
        rc = rect(az, r, rot, Lg, Wg)
        if not inner.contains(rc) or pb.intersects(rc): return None
        d = occ.distance(rc)
        score = d if prefer is None else d - 0.05 * rc.centroid.distance(Point(prefer))
        return (score, az, r, rot, rc, d)
    # coarse pass, then refine round the best few
    cands = []
    for az in range(int(az_range[0]), int(az_range[1]), 4):
        for r in np.arange(r_range[0], min(r_range[1], L.R), 2.0):
            for rot in range(0, 180, 15):
                t = trial(az, r, rot)
                if t: cands.append(t)
    cands.sort(key=lambda t: -t[0])
    for t in cands[:6]:
        for az in range(t[1] - 3, t[1] + 4, 1):
            for r in np.arange(t[2] - 2, t[2] + 2.1, 0.5):
                for rot in range(t[3] - 12, t[3] + 13, 3):
                    u = trial(az, r, rot)
                    if u and (best is None or u[0] > best[0]): best = u
    if best:
        L.add(name, best[4]); L.notes.append(f"{name}: az {best[1]} r {best[2]:.0f} rot {best[3]}, clearance {best[5]:.1f}")
    else:
        L.notes.append(f"{name}: NO ROOM")
    return best
