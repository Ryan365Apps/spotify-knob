"""section through the halo band at one azimuth (away from the motor): v15 as built vs the machined-acrylic proposal"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

R_WALL_IN, R_WALL_OUT, R_BAND = 81.2, 82.8, 83.9
R_STRIP0, R_STRIP1 = 84.0, 85.6
R_KNOB = 87.7
Z_PLATE = 8.0
Z_LIP0, Z_LIP1, Z_SKIRT = 13.5, 14.3, 14.9

def poly(ax, pts, fc, ec="k", lw=0.6, hatch=None, alpha=1.0, z=1):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, hatch=hatch, alpha=alpha, zorder=z))

def common(ax, title, ring_top_pts, diff_pts, foam_pts=None):
    ax.set_title(title, fontsize=10, loc="left")
    # stainless ring: outer wall r 84-87.7 up to the plate top (with a 0.3 chamfer) - only the top 3 mm shown
    poly(ax, ring_top_pts, "#c9ced4", hatch="//")
    ax.text(85.85, 6.2, "stainless ring\n(outer wall r 84–87.7)", fontsize=6.5, ha="center", va="center")
    # plate core top face (r < 75.2 is far left; the ring's flange region is under the wall foot) - draw the ring's inner land as part of the ring
    # structure wall with its 1.1 band over the halo band, and the lip
    poly(ax, [(R_WALL_IN, Z_PLATE), (R_WALL_OUT, Z_PLATE), (R_WALL_OUT, Z_PLATE), (R_BAND, Z_PLATE), (R_BAND, Z_LIP0),
              (86.7, Z_LIP0), (86.7, Z_LIP1), (R_WALL_IN, Z_LIP1)], "#f2d9b8", hatch="..")
    ax.text(82.0, 11.0, "structure\nwall", fontsize=6.5, ha="center", va="center")
    ax.text(84.7, 13.9, "lip 0.8", fontsize=6, ha="center", va="center")
    # LED strip 1.6 thick (ASSUMED), 5 wide, on the band
    poly(ax, [(R_STRIP0, Z_PLATE + 0.25), (R_STRIP1, Z_PLATE + 0.25), (R_STRIP1, Z_PLATE + 5.25), (R_STRIP0, Z_PLATE + 5.25)], "#2f6f3e", ec="k")
    ax.text(84.8, 10.75, "LED\nstrip\n1.6", fontsize=6, ha="center", va="center", color="w")
    # knob skirt above z 14.9, bore at 83.2, 1.2 bottom chamfer
    poly(ax, [(83.2, Z_SKIRT), (R_KNOB - 1.2, Z_SKIRT), (R_KNOB, Z_SKIRT + 1.2), (R_KNOB, 17.5), (83.2, 17.5)], "#9aa3ad", hatch="\\\\")
    ax.text(85.6, 16.6, "knob skirt", fontsize=6.5, ha="center", va="center")
    if foam_pts: poly(ax, foam_pts, "#444", ec="k", z=2)
    poly(ax, diff_pts, "#dbe9f7", ec="#1f4e79", lw=1.0, z=3)
    ax.set_xlim(80.5, 89.0); ax.set_ylim(5.5, 17.5)
    ax.set_aspect("equal"); ax.set_xlabel("radius, mm", fontsize=7); ax.set_ylabel("height above the desk plane, mm", fontsize=7)
    ax.tick_params(labelsize=6); ax.grid(True, lw=0.2, alpha=0.5)
    ax.axvline(R_KNOB, color="#1f4e79", lw=0.4, ls=":"); ax.text(R_KNOB + 0.1, 5.7, "r 87.7\nobject edge", fontsize=5.5, va="bottom")

fig, (a, b) = plt.subplots(1, 2, figsize=(11, 6.2))

# ---- v15 as built
ring15 = [(84.0, 5.5), (R_KNOB, 5.5), (R_KNOB, Z_PLATE - 0.3), (R_KNOB - 0.3, Z_PLATE), (84.0, Z_PLATE)]
diff15 = [(85.8, Z_PLATE), (86.7, Z_PLATE), (87.7 - 0.5 * (1.0/5.5), Z_LIP0 - 0.5), (87.2, Z_LIP0), (85.8, Z_LIP0)]
common(a, "v15 as built — printed PETG: 0.9 thick at the bottom, 1.9 at the top", ring15, diff15)
a.annotate("0.9", xy=(86.25, 8.15), fontsize=6.5, ha="center", color="#1f4e79")
a.annotate("1.9", xy=(86.6, 13.0), fontsize=6.5, ha="center", color="#1f4e79")
a.annotate("1.0 lean over 5.5\n(RULING 5 Sep)", xy=(87.5, 10.8), xytext=(88.2, 11.5), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
a.annotate("sits on the ring's top face,\nclamped under the lip — 0 clearance", xy=(86.2, 8.0), xytext=(80.7, 6.4), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
a.text(85.9, 9.2, "0.2 gap\nto the strip", fontsize=5.5, ha="left", va="center", color="#1f4e79")

# ---- proposal: machined opal acrylic, straight 1.9 wall, seated in a 0.5 rebate on a foam ring, 0.3 chamfers
RB_R, RB_Z = 85.65, Z_PLATE - 0.5          # rebate: inner wall r 85.65, floor z 7.5
ring16 = [(84.0, 5.5), (R_KNOB, 5.5), (R_KNOB, RB_Z - 0.3), (R_KNOB - 0.3, RB_Z), (RB_R, RB_Z), (RB_R, Z_PLATE), (84.0, Z_PLATE)]
foam = [(RB_R + 0.05, RB_Z), (R_KNOB - 0.4, RB_Z), (R_KNOB - 0.4, RB_Z + 0.25), (RB_R + 0.05, RB_Z + 0.25)]
d0 = RB_Z + 0.25                            # diffuser bottom on the compressed foam
H = Z_LIP0 - d0                             # 5.75 tall
diff16 = [(85.8 + 0.4, d0), (R_KNOB - 0.3, d0), (R_KNOB, d0 + 0.3), (R_KNOB, Z_LIP0 - 0.3), (R_KNOB - 0.3, Z_LIP0), (85.8, Z_LIP0), (85.8, d0 + 0.4)]
common(b, "proposal — machined opal acrylic: straight 1.9 wall, in a 0.5 rebate, on foam", ring16, diff16, foam)
b.annotate("1.9 (2.1–2.3 if the real strip\nmeasures 1.2–1.4 thick)", xy=(86.75, 12.6), xytext=(80.7, 16.2), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
b.annotate("0.5 rebate in the ring's top outer corner:\nlocates the ring radially (0.15 clearance\nat r 85.65), hides the joint", xy=(RB_R, RB_Z + 0.2), xytext=(80.7, 5.9), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
b.annotate("closed-cell foam ring 0.5 free,\ncompressed to 0.25 under the lip\n(takes the height tolerance; not glued)", xy=(86.6, RB_Z + 0.12), xytext=(88.05, 9.2), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
b.annotate("0.3 × 45° chamfers, both outer\nedges — a V-line at each joint", xy=(R_KNOB - 0.15, d0 + 0.15), xytext=(88.05, 7.2), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
b.annotate("0.4 chamfer inside,\nclears the rebate's corner radius", xy=(86.0, d0 + 0.2), xytext=(88.05, 11.3), fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))
b.text(85.9, 9.6, "0.2 gap", fontsize=5.5, ha="left", va="center", color="#1f4e79")
b.text(86.75, 10.8, f"H {H:.2f}", fontsize=6.5, ha="center", color="#1f4e79")

fig.suptitle("the 60 — halo diffuser section (one azimuth, away from the motor); the strip's 1.6 thickness is ASSUMED, everything else as v15", fontsize=9)
plt.tight_layout()
plt.savefig("/home/claude/v9/v15/halo_section.png", dpi=170)
print("ok", H)
