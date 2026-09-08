"""concept sketch: two fixed wheels + one sprung wheel on a pivot arm (the wheel at 270 deg), against v15 geometry"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle, Arc, FancyArrowPatch

# v15 numbers (radial x, tangential y in the local frame at az 270)
R_BORE, R_ROOT, R_KNOB = 83.2, 84.5, 87.7
R_WALL_IN, R_WALL_OUT = 81.2, 82.8
WHEEL_OD, WHEEL_W = 13.2, 4.0
R_AX = 77.83                       # wheel axis radius (engaged)
Z_W0, Z_W1 = 19.5, 23.5            # wheel
Z_G0, Z_G1, Z_GM = 19.9, 23.1, 21.5  # the knob's V-groove
Z_PLATE, Z_SEAT_BOT, Z_SEAT_TOP, Z_SKIRT = 8.0, 24.0, 26.0, 14.9
# the concept
PIV = (76.5, -13.5)                # pivot pin (radial, tangential)
ARM_Z0, ARM_Z1 = 15.0, 19.3        # arm below the wheel
ARM_W = 5.0
SPRING_X0, SPRING_X1 = 67.0, 73.5  # spring from the abutment on the structure to the arm's inner face
TRAVEL_IN, TRAVEL_OUT = 0.15, 0.50

def poly(ax, pts, fc, ec="k", lw=0.6, hatch=None, z=1, alpha=1):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, hatch=hatch, zorder=z, alpha=alpha))
def spring(ax, x0, x1, y, n=7, amp=1.4, z=4, vertical=False):
    xs = [x0]; ys = [y]
    for i in range(1, n * 2):
        xs.append(x0 + (x1 - x0) * i / (2 * n)); ys.append(y + (amp if i % 2 else -amp))
    xs.append(x1); ys.append(y)
    if vertical: ax.plot(ys, xs, color="#8b0000", lw=1.2, zorder=z)
    else: ax.plot(xs, ys, color="#8b0000", lw=1.2, zorder=z)

fig, (a, b) = plt.subplots(1, 2, figsize=(13, 6.8), gridspec_kw={"width_ratios": [1.15, 1]})

# ------------------------------------------------------------ PLAN (looking down, local frame: x radial outward, y tangential)
ax = a
ax.set_title("PLAN at the 270° wheel — x radial (outward →), y tangential; the block's layer z 13–18.3", fontsize=9, loc="left")
# knob skirt bore and groove root (arcs approximated as straight over this width)
ax.axvline(R_BORE, color="#666", lw=0.8); ax.text(R_BORE + 0.2, 20, "knob bore r 83.2", fontsize=6, rotation=90, va="bottom")
ax.axvline(R_ROOT, color="#666", lw=0.5, ls="--"); ax.text(R_ROOT + 0.2, 20, "groove root r 84.5", fontsize=6, rotation=90, va="bottom")
poly(ax, [(R_KNOB, -26), (R_KNOB + 3, -26), (R_KNOB + 3, 26), (R_KNOB, 26)], "#9aa3ad", hatch="\\\\")
ax.text(R_KNOB + 1.5, 0, "knob", fontsize=6.5, rotation=90, ha="center", va="center")
# structure wall with the wheel window (WHEEL_OD + 2 wide)
win = WHEEL_OD / 2 + 1.0
for y0, y1 in ((-26, -win), (win, 26)):
    poly(ax, [(R_WALL_IN, y0), (R_WALL_OUT, y0), (R_WALL_OUT, y1), (R_WALL_IN, y1)], "#f2d9b8", hatch="..")
ax.text(82.0, 20, "wall", fontsize=6.5, rotation=90, ha="center", va="center")
ax.text(82.0, 0, "window\n(as v15)", fontsize=5.5, ha="center", va="center", rotation=90)
# the channel in the structure: floor pad on the plate top, two side walls 2 thick, closed inner end (the spring abutment), roof under the wheel
CH_X0, CH_X1, CH_W = 57.0, 81.0, 8.0          # channel inside width 8, from r 61 to the wall
BLK_L, BLK_W = 14.0, 8.0                      # the block: 14 radial x 8 tangential (guide ratio 1.75 : 1)
BLK_X1 = R_AX + 4.0                           # the block's outer end (the wheel pin sits 4 in from it)
for y0, y1 in ((-CH_W/2 - 2.0, -CH_W/2), (CH_W/2, CH_W/2 + 2.0)):
    poly(ax, [(CH_X0 - 2.0, y0), (CH_X1, y0), (CH_X1, y1), (CH_X0 - 2.0, y1)], "#f2d9b8", hatch="..")
poly(ax, [(CH_X0 - 2.0, -CH_W/2), (CH_X0, -CH_W/2), (CH_X0, CH_W/2), (CH_X0 - 2.0, CH_W/2)], "#f2d9b8", hatch="..")   # closed inner end
ax.text(69.0, -12.5, "channel in the structure (printed):\nfloor, two walls, closed inner end, roof", fontsize=5.5, ha="center", va="top")
# the block (printed, or POM) with the wheel pin
poly(ax, [(BLK_X1 - BLK_L, -BLK_W/2 + 0.15), (BLK_X1, -BLK_W/2 + 0.15), (BLK_X1, BLK_W/2 - 0.15), (BLK_X1 - BLK_L, BLK_W/2 - 0.15)], "#cfe2f3", ec="#1f4e79", lw=1.0, z=3)
ax.text(BLK_X1 - BLK_L + 3.0, 0, "block", fontsize=6, color="#1f4e79", ha="center", va="center", zorder=5)
# retracted position (dashed) 4 mm inward
poly(ax, [(BLK_X1 - BLK_L - 4.0, -BLK_W/2 + 0.15), (BLK_X1 - 4.0, -BLK_W/2 + 0.15), (BLK_X1 - 4.0, BLK_W/2 - 0.15), (BLK_X1 - BLK_L - 4.0, BLK_W/2 - 0.15)], "none", ec="#1f4e79", lw=0.7, z=3)
ax.add_patch(Circle((R_AX - 4.0, 0), WHEEL_OD/2, fc="none", ec="k", lw=0.6, ls="--", zorder=4))
ax.annotate("retracted 4 mm for assembly (dashed):\nthe wheel is then inside the bore and the knob\ndrops on, offset 2.5 mm toward the fixed wheels;\nlet go and the spring seats it", xy=(R_AX - 4.0 - 6.6, 0), xytext=(53.0, 16.0), fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.5))
# parking pin hole (holds the block retracted while the knob goes on)
ax.add_patch(Circle((BLK_X1 - BLK_L - 4.0 + 2.0, 0), 1.0, fc="white", ec="k", lw=0.6, zorder=6))
ax.annotate("Ø2 parking pin: pushed up through the\nfoot into the block to hold it back;\npulled before the plate goes on", xy=(BLK_X1 - BLK_L - 2.0, -1.0), xytext=(53.0, -18.0), fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.5))
# wheel (bought V-wheel) on its pin
ax.add_patch(Circle((R_AX, 0), WHEEL_OD/2, fc="#dddddd", ec="k", lw=0.8, zorder=4, alpha=0.55))
ax.add_patch(Circle((R_AX, 0), 1.5, fc="#777", ec="k", lw=0.6, zorder=6))
ax.text(R_AX, 0, "V-wheel\nØ13.2 × 4\n(bought)", fontsize=5.5, ha="center", va="center", zorder=7)
# spring
spring(ax, CH_X0, BLK_X1 - BLK_L, 0)
ax.text((CH_X0 + BLK_X1 - BLK_L)/2, -7.2, "compression spring Ø4, free ~16:\n~4 N seated (10.8 long), ~7 N retracted (6.8 long)", fontsize=5.5, ha="center", va="top", color="#8b0000")
# stops = the ends of the roof's pin slot
ax.annotate("stops: the pin's slot in the roof ends 0.5 out\n(knob off: the wheel stays put) and 4.0 in", xy=(R_AX + 0.5, 1.6), xytext=(53.0, 22.5), fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.5))
ax.add_patch(FancyArrowPatch((R_AX - 4.0, 9.5), (R_AX + 0.5, 9.5), arrowstyle="<->", mutation_scale=8, lw=0.8, color="#1f4e79"))
ax.text(R_AX - 1.75, 10.2, "4.5 travel, radial", fontsize=5.5, ha="center", va="bottom", color="#1f4e79")
# arm swing arc
ax.add_patch(Arc(PIV, 2 * 13.0, 2 * 13.0, theta1=80, theta2=100, color="#1f4e79", lw=0.5, ls=":"))
ax.set_xlim(52, 92); ax.set_ylim(-28, 28); ax.set_aspect("equal"); ax.grid(True, lw=0.2, alpha=0.5); ax.tick_params(labelsize=6)
ax.set_xlabel("radius, mm", fontsize=7); ax.set_ylabel("tangential, mm", fontsize=7)

# ------------------------------------------------------------ SECTION (radial, through the wheel axis at y = 0)
ax = b
ax.set_title("SECTION through the wheel axis (y = 0) — the sprung wheel; the fixed ones differ only below z 18.9", fontsize=9, loc="left")
# knob: skirt from z 14.9 up, bore at 83.2 with the V-groove 19.9-23.1 to root 84.5
poly(ax, [(R_BORE, Z_SKIRT), (R_KNOB - 1.2, Z_SKIRT), (R_KNOB, Z_SKIRT + 1.2), (R_KNOB, 31), (R_BORE, 31), (R_BORE, Z_G1), (R_ROOT, Z_GM + 0.3), (R_ROOT, Z_GM - 0.3), (R_BORE, Z_G0)], "#9aa3ad", hatch="\\\\")
ax.text(86.0, 27.5, "knob\nskirt", fontsize=6.5, ha="center")
ax.annotate("V-groove in the bore\n(mates the bought wheel's profile —\ncut to suit the part chosen)", xy=(R_ROOT - 0.3, Z_GM), xytext=(88.6, 17.5), fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.5))
# structure: wall (r 81.2-82.8) below the window (window is open-topped from z 18.6 up in v15) and the seat flange r 62-82.8 z 24-26 (removed above the window)
poly(ax, [(R_WALL_IN, Z_PLATE), (R_WALL_OUT, Z_PLATE), (R_WALL_OUT, 18.6), (R_WALL_IN, 18.6)], "#f2d9b8", hatch="..")
ax.text(82.0, 12.5, "wall", fontsize=6.5, rotation=90, ha="center", va="center")
poly(ax, [(62.0, Z_SEAT_BOT), (R_AX - win, Z_SEAT_BOT), (R_AX - win, Z_SEAT_TOP), (62.0, Z_SEAT_TOP)], "#f2d9b8", hatch="..")
ax.text(66.5, 25.0, "seat flange", fontsize=6.5, va="center")
# plate top
poly(ax, [(60, 5.5), (R_KNOB + 3, 5.5), (R_KNOB + 3, Z_PLATE), (60, Z_PLATE)], "#c9ced4", hatch="//")
ax.text(66, 6.7, "plate / ring", fontsize=6.5, va="center")
# wheel (section: rectangle with a V on the outer face) on a Ø3 pin standing from the arm
poly(ax, [(R_AX - WHEEL_OD/2, Z_W0), (R_AX + WHEEL_OD/2 - 1.3, Z_W0), (R_AX + WHEEL_OD/2, Z_GM - 0.3), (R_AX + WHEEL_OD/2, Z_GM + 0.3), (R_AX + WHEEL_OD/2 - 1.3, Z_W1), (R_AX - WHEEL_OD/2, Z_W1)], "#dddddd", ec="k", lw=0.8, z=3)
ax.text(R_AX - 2.0, (Z_W0 + Z_W1)/2, "V-wheel (bought)\nØ13.2 × 4, bore 3", fontsize=5.5, ha="center", va="center", zorder=5)
ax.add_patch(Rectangle((R_AX - 1.5, ARM_Z0 + 1.0), 3.0, Z_W1 - ARM_Z0 - 0.5, fc="#777", ec="k", lw=0.6, zorder=4))
ax.text(R_AX + 2.0, 17.0, "Ø3 pin, pressed\nin the arm", fontsize=5.5, va="center")
# the channel section: floor pad z 8-13, block z 13-18.3, roof z 18.3-19.4 with the pin slot; the block's inner end and the spring
poly(ax, [(CH_X0 - 2.0, Z_PLATE - 0.01), (CH_X1, Z_PLATE - 0.01), (CH_X1, 13.0), (CH_X0 - 2.0, 13.0)], "#f2d9b8", hatch="..")      # floor pad (structure)
poly(ax, [(CH_X0 - 2.0, 13.0), (CH_X0, 13.0), (CH_X0, 19.4), (CH_X0 - 2.0, 19.4)], "#f2d9b8", hatch="..")                       # closed inner end
poly(ax, [(CH_X0 - 2.0, 18.3), (R_AX - 4.5, 18.3), (R_AX - 4.5, 19.4), (CH_X0 - 2.0, 19.4)], "#f2d9b8", hatch="..")               # roof, up to the pin slot
poly(ax, [(R_AX + 1.0, 18.3), (CH_X1, 18.3), (CH_X1, 19.4), (R_AX + 1.0, 19.4)], "#f2d9b8", hatch="..")                          # roof beyond the pin slot
ax.text(62.0, 18.85, "roof", fontsize=5.5, ha="center", va="center")
ax.text(64.0, 10.5, "floor pad (structure)", fontsize=5.5, ha="center", va="center")
poly(ax, [(BLK_X1 - BLK_L, 13.15), (BLK_X1, 13.15), (BLK_X1, 18.15), (BLK_X1 - BLK_L, 18.15)], "#cfe2f3", ec="#1f4e79", lw=1.0, z=2)
ax.text(BLK_X1 - BLK_L + 3.5, 15.65, "block", fontsize=6.5, color="#1f4e79", ha="center", va="center", zorder=5)
spring(ax, CH_X0, BLK_X1 - BLK_L, 15.65)
ax.annotate("the pin passes up through a 3.2 x 4.5 slot in the roof;\nthe roof keeps the block from tilting under the knob's weight", xy=(R_AX - 2.0, 18.85), xytext=(53.5, 21.5), fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.5))
# fixed-wheel note: post Ø8 in v15 up to 18.9 — for the two fixed wheels the pin stands in a plain post, no bush
ax.annotate("fixed wheels (30°, 150°): the same pin\nin a plain Ø8 post, no eccentric bush,\npost top at 18.9 as v15", xy=(R_AX, 13.15), xytext=(54.0, 28.0), fontsize=5.5, arrowprops=dict(arrowstyle="->", lw=0.5))
# load path arrows
ax.add_patch(FancyArrowPatch((R_AX + WHEEL_OD/2 + 0.3, Z_GM), (R_AX + WHEEL_OD/2 + 3.0, Z_GM), arrowstyle="<-", mutation_scale=8, lw=0.9, color="#8b0000"))
ax.text(R_AX + WHEEL_OD/2 + 3.3, Z_GM, "spring\npreload", fontsize=5.5, va="center", color="#8b0000")
ax.set_xlim(52, 92); ax.set_ylim(5, 31.5); ax.set_aspect("equal"); ax.grid(True, lw=0.2, alpha=0.5); ax.tick_params(labelsize=6)
ax.set_xlabel("radius, mm", fontsize=7); ax.set_ylabel("height above the desk plane, mm", fontsize=7)

fig.suptitle("the 60 — wheel preload concept: two FIXED wheels (30°, 150°) locate the knob; the 270° wheel is SPRUNG in a radial slot — no eccentric, no lock, no adjustment, no access hole", fontsize=9)
plt.tight_layout(); plt.savefig("/home/claude/v9/v15/sprung_wheel.png", dpi=170); print("ok")
