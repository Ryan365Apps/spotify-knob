"""final figure for the layout study: two candidate plate layouts with cable schematics, and the tray layer"""
import pickle, math
from layout_tool import *
from shapely.geometry import LineString

def load(key):
    d = pickle.load(open(f"/home/claude/v9/v15/cand_{key}.pkl", "rb"))
    L = Layout.__new__(Layout); L.name, L.grow, L.items, L.movable_names, L.notes, L.R = d["name"], d["grow"], d["items"], d["movable"], d["notes"], d["R"]
    L.disc = Point(0, 0).buffer(L.R - 0.3, 256); L.cables = []
    return L

def c_of(L, prefix):
    for n, p in L.items:
        if n.startswith(prefix): return (p.centroid.x, p.centroid.y)
    return None

def draw_cables(ax, L, grow):
    g = grow
    PI_HDR = (-20, 16); FAN_HDR = (14.75, 14); PI_USBA = (36, -16)
    PORT = lambda t: (79.7 + g, t)                    # port face: barrel t -15, USB-C t -3, jack t +9, light sensor t +19
    HALO_NOTCH = pol(64, 81 + g); HALO_NOTCH2 = pol(200, 81 + g)
    LRA = c_of(L, "lra"); ENC = pol(330, 70 + g); MOTOR = pol(90, 60 + g); SERVO = (0, 25 + g); BLOWER = c_of(L, "blower")
    CONV = c_of(L, "converter"); BOB = c_of(L, "TMC6300"); DRV = c_of(L, "DRV"); LS = c_of(L, "level"); AUDIO = c_of(L, "audio"); SPK = c_of(L, "speaker")
    TRAY = (-15, 28)                                  # the MCU on the tray above the adapter (z 20-24)
    W = -57 - g                                       # the west trunk, above the converter at z 17-19
    def line(pts, label="", color="#1565c0", lw=0.8):
        xs, ys = zip(*pts); ax.plot(xs, ys, color=color, lw=lw, ls="--", alpha=0.85, zorder=6)
        if label: ax.text(xs[len(xs)//2], ys[len(ys)//2], label, fontsize=4.5, color=color, ha="center", zorder=7, bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.7))
    line([TRAY, PI_HDR], "serial")
    line([TRAY, (W, 24), (W, BOB[1]), BOB], "6 x PWM", "#c62828")
    line([BOB, (W, BOB[1]), (W, 24), (-30, 50), MOTOR], "3 phases", "#c62828")
    line([TRAY, (-35, 45), MOTOR], "rotor sensor (flex)")
    line([TRAY, (-30, 60 + g), pol(150, 60 + g), pol(200, 66 + g), pol(250, 66 + g), pol(300, 68 + g), ENC], "encoder A/B")
    line([TRAY, (W, 24), (W, DRV[1] + 6), DRV], "I2C"); line([DRV, LRA], "")
    line([PI_HDR, (30, 24), (55, 30), LS] if LS[0] > 0 else [PI_HDR, (W, 16), (W, LS[1]), LS], "LED data"); line([LS, pol(40, 60 + g), HALO_NOTCH], "")
    line([CONV, (W, 0), (W, 16), PI_HDR], "5 V Pi", "#2e7d32"); line([CONV, TRAY], "5 V MCU", "#2e7d32")
    line([CONV, HALO_NOTCH2], "5 V halo (far end)", "#2e7d32"); line([CONV, (W, 24), (-30, 50), pol(75, 70 + g), HALO_NOTCH], "5 V halo", "#2e7d32")
    line([PORT(-15), (60, -40), (0, -70 - g), (-45, -62 - g), CONV], "12 V in", "#2e7d32")
    line([PORT(-3), (60, 26), (20, 32), TRAY], "USB-C (host link)")
    line([PORT(19), (45, 30), FAN_HDR, PI_HDR], "light sensor I2C"); line([SERVO, PI_HDR], "servo PWM"); line([BLOWER, FAN_HDR], "fan")
    if AUDIO: line([AUDIO, PI_USBA], "USB audio"); line([PORT(9), (55, -30), AUDIO], "jack"); line([AUDIO, (W, AUDIO[1]), (W, 24), (-45, 40), SPK], "speaker")
    ax.plot(*TRAY, marker="s", ms=9, color="#1f4e79", zorder=8); ax.text(TRAY[0], TRAY[1] + 5, "MCU on the tray\n(z 20–24, above the adapter)", fontsize=5.5, ha="center", color="#1f4e79", zorder=8)
    ax.plot(*PI_HDR, marker="o", ms=4, color="k", zorder=8); ax.text(PI_HDR[0] - 2, PI_HDR[1] - 5, "Pi header", fontsize=5, ha="center")

fig, axes = plt.subplots(1, 3, figsize=(21, 7.6))
for ax, key, title in ((axes[0], "A6", "Ø175.4 — audio board parked for the prototype (speaker kept), Pi powered via its header"), (axes[1], "C3", "Ø185.4 — everything kept, Pi powered via its header")):
    L = load(key); L.draw(ax, title + "\n" + "; ".join(n.split(" (")[0] + ": " + n.split("clearance")[-1].strip() + " mm" for n in L.notes if "clearance" in n))
    draw_cables(ax, L, L.grow)
    ax.set_xlim(-L.R - 12, L.R + 12); ax.set_ylim(-L.R - 12, L.R + 12)
# the tray layer
ax = axes[2]
polys = [p for z in (20.0, 22.0, 23.5) for n, p in SL[z] if not flexible(n) and not n.startswith("motion")]
occ = unary_union(polys); disc = Point(0, 0).buffer(R_WALL_IN, 256); free = disc.difference(occ)
ax.add_patch(plt.Circle((0, 0), R_WALL_IN, fc="#e6e6e6", ec="k", lw=0.8))
for g in (free.geoms if hasattr(free, "geoms") else [free]):
    if g.area < 1: continue
    xs, ys = g.exterior.xy; ax.fill(xs, ys, color="#c8e6c9", lw=0)
    for i in g.interiors:
        xs, ys = i.xy; ax.fill(xs, ys, color="#e6e6e6", lw=0)
for g in (occ.geoms if hasattr(occ, "geoms") else [occ]):
    if g.area < 0.5: continue
    xs, ys = g.exterior.xy; ax.plot(xs, ys, color="#888", lw=0.3)
pico = rect(118, 32, 50, 51, 21); xs, ys = pico.exterior.xy; ax.fill(xs, ys, color="#ffe0b2", ec="#e65100", lw=0.8)
ax.text(pico.centroid.x, pico.centroid.y, "Pico 2 bare\n(or ESP32-S3-Zero)", fontsize=6, ha="center", va="center", color="#7f2f00")
# the adapter's screw posts that carry the tray (from the v15 slices)
for n, p in SL[18.0]:
    if n.startswith("adapter_screw"):
        c = p.centroid; ax.plot(c.x, c.y, marker="o", ms=5, mfc="none", mec="#1f4e79"); ax.text(c.x + 3, c.y, "tray post", fontsize=5, color="#1f4e79")
ad = footprint(["adapter_board"], 16.0, 16.0); xs, ys = ad.exterior.xy; ax.plot(xs, ys, color="#1f4e79", lw=0.6, ls=":"); ax.text(-40, -20, "adapter board\n(below, z 14.8–16.4)", fontsize=5.5, color="#1f4e79")
hd = footprint(["adapter_hdmi_socket"], 23.5, 18.0); xs, ys = hd.exterior.xy; ax.fill(xs, ys, color="#bbb"); ax.text(hd.centroid.x, hd.centroid.y - 6, "HDMI socket\n(to z 23.7)", fontsize=5, ha="center")
ax.set_aspect("equal"); ax.set_xlim(-93, 93); ax.set_ylim(-93, 93); ax.tick_params(labelsize=5)
ax.set_title("The tray layer, z 20–24 (Ø175.4 shown; the same at Ø185.4): free above the adapter, below the seat flange and the panel's back parts", fontsize=8, loc="left")
fig.suptitle("the 60 layout study — the two layouts that place every bought board (green = free plate at z 8–14; orange = movable or new; dashed grey = the Pi window; dashed lines = cables, schematic)", fontsize=9)
plt.tight_layout(); plt.savefig("/home/claude/v9/v15/layout_study.png", dpi=140); print("ok")
