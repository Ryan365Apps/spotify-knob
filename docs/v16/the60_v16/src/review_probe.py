"""7 Sep review probes against the v15 model: (1) servo frame clearances (design-changes item 5),
(2) horizontal slices of everything above the plate top, saved as polygons for the free-area map (item 6)."""
import sys, os, time, pickle, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import *
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

T0 = time.time()
made = made_parts(knurl=False, engaged=True); bought = bought_parts(True)
allb = {**made, **bought}
print(f"bodies: {len(allb)}  ({time.time()-T0:.0f}s)", flush=True)

# ---------------------------------------------------------------- 1. servo clearances
L = SERVO_L + 1.5
frame_x0, frame_x1 = -1.5, L - 1.5          # local x extent of the frame (end wall to the open end)
frame_y = SERVO_W/2 + 1.0                   # side walls' outer faces
frame_z1 = Z_PLATE_TOP + SERVO_H + 0.5      # frame top
place = polar(MOTOR_AZ, SERVO_R0, 0)
skip = lambda n: n.startswith("servo_") or n == "servo_mount" or n == "base_plate"
def probe_dir(name, mk):
    """mk(s) -> a box in the servo's local frame reaching s beyond the frame's face; report the first hit"""
    for s in [x * 0.25 for x in range(1, 41)]:
        box = place * mk(s)
        hits = []
        for n, b in allb.items():
            if skip(n): continue
            bb = b.bounding_box(); pb = box.bounding_box()
            if bb.max.X < pb.min.X or bb.min.X > pb.max.X or bb.max.Y < pb.min.Y or bb.min.Y > pb.max.Y or bb.max.Z < pb.min.Z or bb.min.Z > pb.max.Z: continue
            try:
                v = (box & b).volume
            except Exception: v = 0
            if v > 1e-6: hits.append(n)
        if hits:
            print(f"  servo frame {name}: first contact at {s:.2f} mm -> {', '.join(sorted(hits))}"); return
    print(f"  servo frame {name}: clear for 10 mm")
print("\n[servo frame clearances beyond its outer faces, 0.25 mm steps]")
probe_dir("+radial (open end, toward the carriage tab)", lambda s: Box(s, 2*frame_y, SERVO_H + 0.5, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((frame_x1, 0, Z_PLATE_TOP))))
probe_dir("-radial (behind the end wall)", lambda s: Box(s, 2*frame_y, SERVO_H + 0.5, align=(Align.MAX, Align.CENTER, Align.MIN)).moved(Location((frame_x0, 0, Z_PLATE_TOP))))
probe_dir("+tangential (side wall)", lambda s: Box(L, s, SERVO_H + 0.5, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((frame_x0, frame_y, Z_PLATE_TOP))))
probe_dir("-tangential (side wall)", lambda s: Box(L, s, SERVO_H + 0.5, align=(Align.MIN, Align.MAX, Align.MIN)).moved(Location((frame_x0, -frame_y, Z_PLATE_TOP))))
probe_dir("up (above the frame top)", lambda s: Box(L, 2*frame_y, s, align=(Align.MIN, Align.CENTER, Align.MIN)).moved(Location((frame_x0, 0, frame_z1))))
# pushrod height vs the carriage tab
for n, b in allb.items():
    if n.startswith("servo_"):
        bb = b.bounding_box(); print(f"  {n}: z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
bb = allb["carriage"].bounding_box(); print(f"  carriage: z {bb.min.Z:.2f}..{bb.max.Z:.2f}")

# ---------------------------------------------------------------- 2. slices above the plate top
def face_polygon(f):
    def ring(w):
        pts = []
        for e in w.edges():
            n = 2 if e.geom_type == "LINE" else 24
            for i in range(n):
                p = e.position_at(i / n); pts.append((p.X, p.Y))
        return pts
    try:
        outer = ring(f.outer_wire()); inner = [ring(w) for w in f.inner_wires()]
        pg = Polygon(outer, inner)
        if not pg.is_valid: pg = pg.buffer(0)
        return pg
    except Exception:
        return None
ZS = [8.6, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 23.5]
slices = {}
print("\n[slices]", flush=True)
for z in ZS:
    slab = Box(400, 400, 0.1, align=(Align.CENTER, Align.CENTER, Align.CENTER)).moved(Location((0, 0, z)))
    polys = []
    for n, b in allb.items():
        if n == "knob_body": continue
        bb = b.bounding_box()
        if bb.max.Z < z - 0.05 or bb.min.Z > z + 0.05: continue
        try:
            i = slab & b
        except Exception: continue
        if i is None: continue
        for f in i.faces():
            if abs(f.normal_at().Z) < 0.9: continue
            if abs(f.center().Z - (z + 0.05)) > 0.02: continue          # top faces of the slab intersection only
            pg = face_polygon(f)
            if pg is not None and pg.area > 0.01: polys.append((n, pg))
    slices[z] = polys
    print(f"  z {z}: {len(polys)} faces from {len(set(n for n,_ in polys))} bodies  ({time.time()-T0:.0f}s)", flush=True)
pickle.dump({"ZS": ZS, "slices": slices, "R_WALL_IN": R_WALL_IN, "R_SEAT_IN": R_SEAT_IN}, open("/home/claude/v9/v15/slices.pkl", "wb"))
print("saved")
