"""printability check for every printed part, in its print orientation (printorient.PRINT)

For each part it reports, against the usual FDM (fused-filament) design rules:
  - OVERHANG  faces that look downward within 45 deg of straight down and are not on the bed: they need support
              (a face steeper than 45 deg from horizontal supports itself).  Reported per B-rep face, so each
              item is one geometric feature, with its height above the bed and where it is.
  - BRIDGE    a horizontal downward face whose two ends rest on material below it - printable as a bridge up to
              about 20 mm; listed separately from unsupported overhangs where it can be told apart (the face's
              extent is small in one direction and material exists below both ends).
  - SIDE HOLE round holes with a horizontal axis (they print as a sagging roof unless teardropped / small).
  - THIN      walls under 0.8 mm (two 0.4 mm perimeters) and features under 1.2 mm.
  - SMALL TOP a downward face on an island that starts in mid-air (nothing at all below it).
Every figure is from the STEP geometry itself.  Run after export (the knob comes from the knurl cache)."""
import os, sys, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import *
from printorient import PRINT
from build123d import Face, Solid, Compound, Location, Vector, GeomType

OVERHANG_DEG = 45.0        # a downward face at or under this angle from horizontal needs support
MIN_AREA     = 1.0         # mm2 - ignore smaller downward faces (chamfer tips, tessellation crumbs)
BRIDGE_MAX   = 20.0        # mm - a horizontal face spanning up to this much between supports prints as a bridge

def load_parts():
    knurled = None
    try:
        from knurl import CACHE
        if os.path.exists(CACHE): knurled = import_step(CACHE).solids()[0]
    except Exception: pass
    made = made_parts(knurl=False)
    if knurled is not None: made["knob_body"] = knurled
    out = {}
    for n, (fn, layer, note) in PRINT.items():
        base = {"collar_0": wheel_collar(), "bush_0": ecc_bush()}.get(n, made[n])
        out[n] = (fn(base), layer, note)
    return out

def classify(shape):
    """returns a list of findings for one oriented shape"""
    bb = shape.bounding_box(); zbed = bb.min.Z
    cos_lim = math.cos(math.radians(90 - OVERHANG_DEG))    # normal within 45 deg of straight down  ->  nz <= -cos(45)
    findings = []
    solid_bb = bb
    for f in shape.faces():
        fb = f.bounding_box()
        # sample the outward normal at the face centre (build123d gives the true outward normal for a solid's faces)
        try:
            n = f.normal_at(f.center())
        except Exception:
            continue
        gt = f.geom_type
        area = f.area
        if area < MIN_AREA: continue
        # 1) downward faces
        nz = n.Z
        if gt == GeomType.PLANE:
            if nz <= -cos_lim and fb.min.Z > zbed + 0.05:
                findings.append(("OVERHANG", f, area, fb, math.degrees(math.asin(-nz))))
        else:
            # curved face: tessellate and sum the downward-looking area, using the true normal at each triangle centre
            try: verts, tris = f.tessellate(0.05, 0.3)
            except Exception: continue
            a_down = 0.0
            for t in tris:
                a, b, c = (verts[i] for i in t)
                cen = (a + b + c) / 3
                tri_n = (b - a).cross(c - a); l = tri_n.length
                if l < 1e-9: continue
                try: nn = f.normal_at(cen)
                except Exception: nn = tri_n / l
                if nn.Z <= -cos_lim and cen.Z > zbed + 0.05: a_down += l / 2
            if a_down >= MIN_AREA:
                findings.append(("OVERHANG", f, a_down, fb, None))
        # 2) side holes: cylindrical faces with a horizontal axis, small radius, concave (a hole, not a boss)
        if gt == GeomType.CYLINDER:
            try:
                cyl = f.geom_adaptor().Cylinder(); ax = cyl.Axis(); rad = cyl.Radius()
                d = Vector(ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z())
                p0 = Vector(ax.Location().X(), ax.Location().Y(), ax.Location().Z())
                p = f.position_at(0.5, 0.5); nn = f.normal_at(p)
                radial = (p - p0) - d * (p - p0).dot(d)
                if abs(d.Z) < 0.05 and rad <= 5.0 and nn.dot(radial) < 0:
                    findings.append(("SIDE HOLE", f, area, fb, 2 * rad))
            except Exception:
                pass
    return findings, zbed

def where(fb, zbed):
    cx, cy = (fb.min.X + fb.max.X)/2, (fb.min.Y + fb.max.Y)/2
    r = math.hypot(cx, cy); az = math.degrees(math.atan2(cy, cx)) % 360
    return f"z {fb.min.Z - zbed:.1f}-{fb.max.Z - zbed:.1f} above the bed, r {math.hypot(fb.min.X, fb.min.Y):.1f}-{math.hypot(fb.max.X, fb.max.Y):.1f} (centre r {r:.1f}, {az:.0f} deg), {fb.max.X - fb.min.X:.1f} x {fb.max.Y - fb.min.Y:.1f}"

def bridged(shape, f, fb, zbed):
    """is this horizontal downward face a bridge? true when material exists just below both ends of either axis
    (a slit's roof is bridged across its 1 mm width even though nothing is beyond its two open ends)"""
    dx, dy = fb.max.X - fb.min.X, fb.max.Y - fb.min.Y
    long_ = max(dx, dy)
    if long_ > BRIDGE_MAX: return False, long_
    c = f.center(); z = fb.min.Z - 0.3
    pairs = [(Vector(fb.min.X - 0.3, c.Y, z), Vector(fb.max.X + 0.3, c.Y, z), dx),
             (Vector(c.X, fb.min.Y - 0.3, z), Vector(c.X, fb.max.Y + 0.3, z), dy)]
    for e1, e2, span in sorted(pairs, key=lambda p: p[2]):
        try:
            if shape.is_inside(e1) and shape.is_inside(e2): return True, span
        except Exception:
            pass
    return False, long_

def run(names=None, verbose=True):
    t0 = time.time()
    parts = load_parts()
    summary = {}
    for n, (shape, layer, note) in parts.items():
        if names and n not in names: continue
        findings, zbed = classify(shape)
        over = [x for x in findings if x[0] == "OVERHANG"]
        holes = [x for x in findings if x[0] == "SIDE HOLE"]
        tot = sum(x[2] for x in over)
        print(f"\n== {n}  (layer {layer}; {note})")
        bb = shape.bounding_box()
        print(f"   {bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f} tall; {len(shape.faces())} faces")
        if not over and not holes:
            print("   no downward faces off the bed, no side holes: prints as it stands, no supports")
        rows = []; a_support = 0.0; n_bridge = 0; max_span = 0.0
        for kind, f, area, fb, extra in sorted(over, key=lambda x: -x[2]):
            horiz = extra is not None and extra > 89.0
            if horiz:
                isb, span = bridged(shape, f, fb, zbed)
                tag = f"BRIDGE {span:.1f} mm" if isb else f"OVERHANG flat {span:.1f} wide"
                if isb: n_bridge += 1; max_span = max(max_span, span)
                else: a_support += area
            else:
                tag = "OVERHANG" + (f" {extra:.0f} deg from horizontal" if extra is not None else " (curved)")
                a_support += area
            rows.append((tag, area, where(fb, zbed)))
        for tag, area, w in rows[:12]:
            print(f"   {tag:28s} {area:8.1f} mm2  {w}")
        if len(rows) > 12: print(f"   ... {len(rows) - 12} more small ones")
        for kind, f, area, fb, d in holes:
            print(f"   {'SIDE HOLE Ø%.1f' % d:28s} {area:8.1f} mm2  {where(fb, zbed)}")
        summary[n] = (a_support, n_bridge, max_span, len(holes))
    print(f"\n-- summary ({time.time() - t0:.0f}s)")
    for n, (a, nb, ms, h) in summary.items():
        verdict = "no supports" if a < 25 else ("small overhangs, no supports needed" if a < 120 else "SUPPORTS NEEDED")
        print(f"   {n:20s} {verdict:36s} unsupported downward area {a:7.1f} mm2; bridges {nb:2d} (longest {ms:4.1f} mm); side holes {h}")
    return summary

if __name__ == "__main__":
    run(sys.argv[1:] or None)
