"""Hidden-line view generation for the 60 v15, from the exported assembly.

Nothing here is drawn by hand: every line on a sheet is projected from
docs/v9/the60_v9/src/model.py.  The only hand work is where a view sits on the
sheet and which parts it contains.

Set SRC (or the THE60_SRC environment variable) to the unzipped v9 src folder.
The bought-part STEP files must sit where params.py expects them: two levels
above src, in bought/bought-parts.
"""
import os, sys, tempfile, math
import xml.etree.ElementTree as ET

_REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
SRC = os.environ.get("THE60_SRC", os.path.join(_REPO, "docs", "v15", "the60_v15", "src"))
sys.path.insert(0, SRC)
from build123d import *                      # noqa
from build123d import export_brep, import_brep, import_step
from build123d.exporters import Drawing, ExportSVG, LineType
import params as P                           # noqa

SVGNS = "{http://www.w3.org/2000/svg}"

# ---------------------------------------------------------------- the model, built once
# v15: bodies come from the exported assembly STEP rather than from a rebuild of
# model.py, because the vendor STEP files model.py needs are not all in the repo.
# Names are the assembly's own labels, flattened, so they match the Fusion tree.
# The two clutch states are two exported files.
ASM = {True:  os.environ.get("THE60_ASM",  os.path.join(_REPO, "docs", "v15", "the60_v15_assembly.step")),
       False: os.environ.get("THE60_ASMF", os.path.join(_REPO, "docs", "v15", "the60_v15_assembly_free_spin.step"))}
CACHE = os.environ.get("THE60_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache"))

_parts = {}
def _flatten(c):
    out = {}
    def walk(n):
        kids = list(getattr(n, "children", []) or [])
        if kids:
            for k in kids: walk(k)
            return
        lab = n.label or "body"
        for i, s in enumerate(n.solids()):
            k = lab if i == 0 else "%s_%d" % (lab, i)
            while k in out: k += "_x"
            out[k] = s
    for k in (getattr(c, "children", []) or []): walk(k)
    return out

def parts(engaged=True):
    """{name: solid} for every body in the assembly, cached per clutch state."""
    if engaged in _parts:
        return _parts[engaged]
    src = ASM[engaged]
    d = os.path.join(CACHE, "engaged" if engaged else "released")
    stamp = os.path.join(d, "_ok")
    fresh = os.path.isfile(stamp) and os.path.getmtime(stamp) > os.path.getmtime(src)
    if fresh:
        _parts[engaged] = {f[:-5]: import_brep(os.path.join(d, f))
                           for f in os.listdir(d) if f.endswith(".brep")}
    else:
        p = _flatten(import_step(src))
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.unlink(os.path.join(d, f))
        for k, v in p.items():
            export_brep(v, os.path.join(d, k + ".brep"))
        open(stamp, "w").write("ok")
        _parts[engaged] = p
    d2 = _parts[engaged]
    if "knob_body" in d2 and len(d2["knob_body"].faces()) > 100:
        d2["knob_body_knurled"] = d2["knob_body"]
        d2["knob_body"] = _smooth_knob()
    return d2


def _smooth_knob():
    """The knob without its knurl, rebuilt from params.

    The exported assembly carries the knurled body (2286 faces); in section and
    in hidden-line projection every diamond would be drawn. Drawings use the
    turned profile, as the v9 sheets did (model.knob_body(knurl=False)).
    """
    rb, rk, ri, rg = P.R_BORE, P.R_KNOB, P.R_CROWN_IN, P.R_GROOVE_ROOT
    zs, zt, zcb = P.Z_SKIRT_BOT, P.Z_KNOB_TOP, P.Z_CROWN_BOT
    f = P.WHEEL_V_FLAT / 2
    zr = zcb + P.STRIP_T
    pts = [(rb, zs), (rk - P.CH_BOT, zs), (rk, zs + P.CH_BOT),
           (rk, zt - P.CH_TOP), (rk - P.CH_TOP, zt),
           (ri + P.CH_IN, zt), (ri, zt - P.CH_IN),
           (ri, zcb), (P.CODE_R0, zcb), (P.CODE_R0, zr), (P.CODE_R1, zr), (P.CODE_R1, zcb), (rb, zcb),
           (rb, P.Z_GROOVE1), (rg, P.Z_RIDGE_MID + f), (rg, P.Z_RIDGE_MID - f), (rb, P.Z_GROOVE0)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ) as sk:
            with BuildLine():
                Polyline([(x, z) for x, z in pts], close=True)
            make_face()
        revolve(axis=Axis.Z)
    return bp.part.solids()[0]

def scene(names=(), engaged=True, missing_ok=False):
    """Bodies by name, in order, with repeats dropped (a name may match twice
    when a list mixes explicit names with a startswith group)."""
    p = parts(engaged)
    out, seen = [], set()
    for n in names:
        if n in seen:
            continue
        seen.add(n)
        if n in p:
            out.append(p[n])
        elif not missing_ok:
            raise KeyError("no body called %r" % n)
    return out

def group(prefix, engaged=True):
    """Every body whose name starts with `prefix` (led_, display_part_, bearing30_ ...)."""
    return [v for k, v in parts(engaged).items() if k.startswith(prefix)]

# ---------------------------------------------------------------- sectioning
def spin(objs, az):
    """Rotate a list of solids about Z. Used to bring any azimuth onto the 0-180 axis."""
    return [Rot(0, 0, az) * o for o in objs]

def cut(objs, keep):
    """keep: a solid; every part is intersected with it."""
    out = []
    for p in objs:
        try:
            q = p & keep
        except Exception:
            q = None
        if q is not None and getattr(q, "volume", 0) > 1e-6:
            out.append(q)
    return out

def halfspace(size=400):
    """Solid filling y > 0: the half kept by a section on the 0-180 axis."""
    return Box(size, size, size, align=(Align.CENTER, Align.MIN, Align.CENTER))

def slab(z, size=400, above=True):
    """Everything above (or below) a horizontal cut at z."""
    a = Align.MIN if above else Align.MAX
    return Pos(0, 0, z) * Box(size, size, size, align=(Align.CENTER, Align.CENTER, a))

def view(objs, look_from, look_up=(0, 0, 1), hidden=True, look_at=(0, 0, 0)):
    """{'vis':[path d], 'hid':[...], 'box':(x0,y0,w,h)} in model mm, y-up."""
    # moved(Location()) hands the compound a fresh shape: a body can appear in
    # more than one view without being re-parented out of an earlier one
    shape = Compound(label="s", children=[o.moved(Location()) for o in objs])
    d = Drawing(shape, look_from=look_from, look_up=look_up, look_at=look_at, with_hidden=hidden)
    e = ExportSVG(scale=1, fit_to_stroke=False, margin=0)
    e.add_layer("v", line_weight=0.35)
    e.add_layer("h", line_weight=0.18, line_type=LineType.DASHED)
    e.add_shape(d.visible_lines, "v")
    if hidden:
        e.add_shape(d.hidden_lines, "h")
    fn = tempfile.mktemp(suffix=".svg")
    e.write(fn)
    tree = ET.parse(fn); root = tree.getroot()
    vb = [float(x) for x in root.get("viewBox").split()]
    out = {"vis": [], "hid": [], "box": (vb[0], vb[1], vb[2], vb[3])}
    for g in root.iter(SVGNS + "g"):
        gid = g.get("id")
        if gid in ("v", "h"):
            key = "vis" if gid == "v" else "hid"
            for el in g:
                d = _as_path(el)
                if d:
                    out[key].append(d)
    os.unlink(fn)
    return out

def _as_path(el):
    """ExportSVG writes straight edges as <line> and full circles as <circle>;
    only curved-but-not-closed edges come out as <path>. A view made entirely of
    flat faces has no <path> at all, so every element type is converted here."""
    tag = el.tag.replace(SVGNS, "")
    g = lambda k: float(el.get(k))
    if tag == "path":
        return el.get("d")
    if tag == "line":
        return "M %s,%s L %s,%s" % (el.get("x1"), el.get("y1"), el.get("x2"), el.get("y2"))
    if tag == "circle":
        cx, cy, r = g("cx"), g("cy"), g("r")
        return ("M %.6f,%.6f A %.6f,%.6f 0 1 0 %.6f,%.6f A %.6f,%.6f 0 1 0 %.6f,%.6f"
                % (cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy))
    if tag == "ellipse":
        cx, cy, rx, ry = g("cx"), g("cy"), g("rx"), g("ry")
        return ("M %.6f,%.6f A %.6f,%.6f 0 1 0 %.6f,%.6f A %.6f,%.6f 0 1 0 %.6f,%.6f"
                % (cx - rx, cy, rx, ry, cx + rx, cy, rx, ry, cx - rx, cy))
    if tag in ("polyline", "polygon"):
        pts = el.get("points", "").replace(",", " ").split()
        if len(pts) < 4:
            return None
        d = "M %s,%s " % (pts[0], pts[1])
        d += " ".join("L %s,%s" % (pts[i], pts[i + 1]) for i in range(2, len(pts) - 1, 2))
        return d + (" Z" if tag == "polygon" else "")
    return None

def section_faces(cut_parts, axis="Y", at=0.0, per_part=False):
    """Faces lying in the cutting plane (normal along `axis`, through `at`).

    per_part keeps one list per body, so each part can be hatched its own way.
    """
    idx = {"X": 0, "Y": 1, "Z": 2}[axis]
    out = []
    for p in cut_parts:
        here = []
        for f in p.faces():
            try:
                n = f.normal_at(None)
            except Exception:
                continue
            c = f.center()
            if abs(abs(n.to_tuple()[idx]) - 1.0) < 1e-6 and abs(c.to_tuple()[idx] - at) < 1e-4:
                here.append(f)
        if per_part:
            if here:
                out.append(here)
        else:
            out.extend(here)
    return out

def wire_pts(w, sag=0.05):
    """Points along a wire. Curved edges get enough points that the chord error
    stays under `sag` mm, so a hatched Ø125 face is not drawn as a 24-gon."""
    pts = []
    for e in w.edges():
        if e.geom_type == GeomType.LINE:
            n = 2
        else:
            n = min(720, max(24, int(e.length / max(sag, 1e-3)) + 1))
        for i in range(n):
            pts.append(e @ (i / (n - 1)))
    return pts

def face_paths(faces, sx, sy):
    """SVG path strings for section faces. sx/sy map a 3D point to screen (x,y)."""
    out = []
    for f in faces:
        d = ""
        for w in [f.outer_wire()] + list(f.inner_wires()):
            pts = wire_pts(w)
            d += "M " + " L ".join("%.3f,%.3f" % (sx(p), sy(p)) for p in pts) + " Z "
        out.append(d.strip())
    return out

X = (lambda p: p.X)
Y = (lambda p: p.Y)
Z = (lambda p: p.Z)

# ---------------------------------------------------------------- the shapes of view a sheet uses
def radial_section(names, az, engaged=True, hidden=False, missing_ok=False, extra=()):
    """Section on the az-(az+180) axis, seen from outside the kept half.

    The scene is spun by -az so the cut always lands on the 0-180 axis and the
    projection is the one case that is known to work.  Screen x is the radius at
    azimuth az (positive to the right), screen y is z.
    """
    objs = spin(list(scene(names, engaged, missing_ok)) + list(extra), -az)
    c = cut(objs, halfspace())
    v = view(c, (0, -1, 0), hidden=hidden)
    h = [face_paths(g, X, Z) for g in section_faces(c, "Y", 0.0, per_part=True)]
    return v, h

def plan_section(names, z, engaged=True, hidden=False, missing_ok=False, above=False, extra=()):
    """Horizontal section at z: material below the cut, seen from above.

    Screen x is +X, screen y is +Y. above=True instead keeps what is over the cut.
    """
    objs = list(scene(names, engaged, missing_ok)) + list(extra)
    c = cut(objs, slab(z, above=above))
    v = view(c, (0, 0, 1), look_up=(0, 1, 0), hidden=hidden)
    h = [face_paths(g, X, Y) for g in section_faces(c, "Z", z, per_part=True)]
    return v, h

def elevation(names, az=0.0, engaged=True, hidden=True, missing_ok=False, extra=()):
    """Uncut outside view looking at the az face."""
    objs = spin(list(scene(names, engaged, missing_ok)) + list(extra), -az)
    return view(objs, (0, -1, 0), hidden=hidden)

def iso(names, engaged=True, hidden=True, direction=(1, -1, 0.8), missing_ok=False, extra=()):
    objs = list(scene(names, engaged, missing_ok)) + list(extra)
    return view(objs, direction, hidden=hidden)

def bbox(names, engaged=True, missing_ok=False):
    """Bounding box of a set of bodies, for driving annotation off the real model."""
    objs = scene(names, engaged, missing_ok)
    bb = objs[0].bounding_box()
    for o in objs[1:]:
        bb = bb.add(o.bounding_box())
    return bb
