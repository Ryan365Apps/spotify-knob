"""the 60 v11 - top ring drawing (Ø175.4, plain bore Ø145; RULING 6 Sep: a 20 mm flat rim). Not CAD; numbers from V10-SPECIFICATION.md section 8.1."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

R_KNOB, CH_OUT, CH_IN = 87.7, 2.5, 1.0
R_PIC, R_LIP = 63.5, 64.2
R_LENS, R_GLASS, R_CHIN, R_BORE = 70.0, 66.1, 72.05, 83.2
flat = R_KNOB - CH_OUT - (R_LIP + CH_IN)
metal = R_KNOB - R_LIP
total = R_KNOB - R_PIC

fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
fig.suptitle("the 60 — v11 top face: the metal ring with the 5-inch panel at Ø175.4 — a 20 mm flat rim (drawing, not CAD)", fontsize=16, weight="bold", y=0.975)

ax = fig.add_axes([0.03, 0.08, 0.5, 0.84]); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-105, 105); ax.set_ylim(-105, 105)
ax.add_patch(Circle((0, 0), R_KNOB, fc="#d9d3c5", ec="k", lw=1.2))
ax.add_patch(Circle((0, 0), R_KNOB - CH_OUT, fc="#e9e4d8", ec="k", lw=0.8))
ax.add_patch(Circle((0, 0), R_LIP + CH_IN, fc="#d9d3c5", ec="k", lw=0.8))
ax.add_patch(Circle((0, 0), R_LIP, fc="#0e1a26", ec="k", lw=0.8))
ax.add_patch(Circle((0, 0), R_PIC, fc="#0e1a26", ec="#2f8fe0", lw=1.5))
for r, ls, c, lab in [(R_LENS, "--", "#2f8fe0", "lens Ø140 (ASSUMED)"), (R_GLASS, ":", "#777", "panel glass Ø132.2"), (R_BORE, "-", "#999", "knob bore Ø166.4")]:
    ax.add_patch(Circle((0, 0), r, fc="none", ec=c, lw=0.8, ls=ls))
# chin outline (hidden under the wall)
chin = Polygon([(-38.88, -53.33), (-15.52, -70.36), (15.52, -70.36), (38.88, -53.33)], closed=False, fc="none", ec="#c0392b", lw=1.0, ls=":")
ax.add_patch(chin)
ax.text(0, -60, "driver chin\ncorners r 72.05", color="#c0392b", ha="center", va="center", fontsize=9)
ax.text(0, 4, "picture\nØ127.0", color="w", ha="center", va="center", fontsize=14)
ax.text(0, 98, f"metal ring, picture edge to knob edge: {total:.1f} mm total   (v9: 18.7 mm)", ha="center", fontsize=13, weight="bold")
ax.annotate("outer chamfer 2.5 (bright, diamond-cut)", xy=(R_KNOB - 1.2, 20), xytext=(40, 94), fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.annotate("inner chamfer 1.0 (smooth); lip edge Ø128.4, 0.7 outside the picture", xy=(-64.7, 5), xytext=(-102, 90), fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.annotate(f"flat ring Ø{2*(R_LIP+CH_IN):.1f} – Ø{2*(R_KNOB-CH_OUT):.1f}  =  {flat:.1f} mm wide", xy=(-76, -15), xytext=(-102, -94), fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.annotate("hidden under the lip: lens Ø140 (dashed), panel glass Ø132.2 (dotted), the structure's seat to r 82.8, bore Ø166.4 (grey), chin (red)", xy=(50, -49), xytext=(-40, -102), fontsize=10, arrowprops=dict(arrowstyle="->", lw=0.8))

# section
bx = fig.add_axes([0.56, 0.30, 0.42, 0.55]); bx.set_aspect("equal"); bx.axis("off")
bx.set_title("section through the rim — r outward, z up, mm", fontsize=12, weight="bold")
z_glass0, z_glass1 = 30.9, 32.88; z_lens1 = 35.38; z_lip0 = 35.78; z_top = 38.78; z_seat0, z_seat1 = 28.4, 30.4
bx.set_xlim(60, 92); bx.set_ylim(20.5, 43)
bx.add_patch(Rectangle((R_PIC - 4, z_glass0), R_GLASS - R_PIC + 4, z_glass1 - z_glass0, fc="#0e1a26", ec="k", lw=0.6))
bx.add_patch(Rectangle((R_PIC - 4, z_glass1), R_LENS - R_PIC + 4, z_lens1 - z_glass1, fc="#a8d4f5", ec="k", lw=0.6))
bx.add_patch(Rectangle((62.0, z_seat0), 82.8 - 62.0, z_seat1 - z_seat0, fc="#8a7a5a", ec="k", lw=0.6))  # structure seat flange
bx.add_patch(Rectangle((81.2, 25), 82.8 - 81.2, z_seat0 - 25, fc="#8a7a5a", ec="k", lw=0.6))  # wall
bx.add_patch(Rectangle((62.5, z_seat1), 65.6 - 62.5, z_glass0 - z_seat1, fc="#d0a060", ec="k", lw=0.4))  # bonding tape
bx.add_patch(Polygon([(R_LIP, z_top), (R_KNOB - CH_OUT, z_top), (R_KNOB, z_top - CH_OUT), (R_KNOB, 26.5), (R_BORE, 26.5), (R_BORE, z_lip0), (R_LIP + CH_IN, z_lip0), (R_LIP, z_lip0 + CH_IN)], closed=True, fc="#d9d3c5", ec="k", lw=1.0))
bx.plot([R_PIC, R_PIC], [z_glass0 - 3.5, z_lens1 + 1], color="#2f8fe0", lw=0.8, ls="--")
bx.text(R_PIC + 0.3, z_glass0 - 3.4, "picture edge r 63.5", color="#2f8fe0", fontsize=8, ha="left")
bx.annotate("", xy=(R_LIP + CH_IN, z_top + 1.2), xytext=(R_KNOB - CH_OUT, z_top + 1.2), arrowprops=dict(arrowstyle="<->", lw=0.8)); bx.text((R_LIP + R_KNOB) / 2, z_top + 1.6, f"flat {flat:.1f}", ha="center", fontsize=9)
bx.text(R_KNOB - 1.3, z_top - 1.0, "2.5", fontsize=9); bx.text(R_LIP + 0.1, z_lip0 + 1.6, "1.0", fontsize=9)
bx.annotate("", xy=(R_LIP, z_lens1 - 1.0), xytext=(R_LENS, z_lens1 - 1.0), arrowprops=dict(arrowstyle="<->", lw=0.8)); bx.text((R_LIP + R_LENS) / 2, z_lens1 - 0.8, "lip over lens 5.8", ha="center", fontsize=9)
bx.text(64.5, z_lip0 - 0.05, "rim gap 0.4", fontsize=8, va="bottom", ha="right")
bx.text(66.5, z_seat0 + 1.0, "seat 2.0", fontsize=8, ha="center", va="center", color="w")
bx.text(64.0, z_seat1 + 0.25, "tape 0.5", fontsize=6, ha="center", va="center")
bx.text(85.4, 30, "knob wall 4.5", fontsize=8, ha="center", va="center", rotation=90)
bx.text(60.5, 21.0, "panel glass 1.98 (dark) bonded to the structure's seat on 0.5 tape, lens 2.5 (blue, ASSUMED),\nrim gap 0.4, lip 3.0; z from the v10 stack as built (section 8.3)", fontsize=9, ha="left", va="bottom")

fig.text(0.56, 0.12, f"Read this as: seen from above the ring is {metal:.1f} mm of metal — {flat:.1f} flat, 2.5 bright outer chamfer, 1.0 small inner chamfer — and {total:.1f} mm from the picture edge to the knob edge.\n"
         "The lip overlaps the lens by 5.8 mm and reaches to 0.7 mm outside the picture. v9 had 18.7 mm of metal (picture Ø87.6 in a Ø125 knob); the first v10 build had 9.3 flat at Ø154.\n"
         "RULING 6 Sep: the rim is at least 20 mm flat and the knob keeps its 4.5 wall, so the bore grows to Ø166.4 and everything inside scales out to it; the chin (red) is no longer what sets the bore.",
         fontsize=11, ha="left", va="top", wrap=True)
fig.savefig("v11_top_ring.png")
print("flat", flat, "metal", metal, "total", total)
