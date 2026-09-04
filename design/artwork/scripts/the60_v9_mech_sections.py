"""
the60_v9_mech_sections.py — section artwork for MECHANISMS.html, v9 geometry.

Runs headless (`python the60_v9_mech_sections.py` with the bpy module) or from
inside Blender (Scripting > Run Script, or the MCP connector).

Input  : the60_v9_assembly.obj / the60_v9_free_spin.obj — the 302 named bodies of
         the v9 STEP assembly, tessellated straight out of docs/v9/the60_v9.
Output : one PNG per view in design/artwork/examples/mechanisms/, plus
         views.json — the exact camera framing of every view, which is what the
         balloon positions in MECHANISMS.html are computed from.

Method, and the three things that waste time if you do not know them:
  * the section is a boolean DIFFERENCE against a big cutter box, solver EXACT.
    The FLOAT solver silently leaves the model uncut and still reports success.
  * material_mode='TRANSFER' is what gives the cut faces their dark colour: the
    faces the cutter creates take the cutter's material.
  * a plan camera must set rotation_euler directly. Building a straight-down
    camera with to_track_quat flips the frame 180 degrees.

Frame: z = 0 is the steel plate's underside, azimuth 0 = +X = the USB-C socket,
anticlockwise from above. Plan views put azimuth 0 at twelve o'clock.
"""
import bpy, bmesh, math, os, json, sys

HERE      = os.path.dirname(os.path.abspath(__file__))
ROOT      = os.path.abspath(os.path.join(HERE, "..", "..", ".."))     # repo root
OBJ_DIR   = os.path.join(ROOT, "design", "artwork", "blender", "v9")
OUT_DIR   = os.path.join(ROOT, "design", "artwork", "examples", "mechanisms")
OBJ_ENGAGED = os.path.join(OBJ_DIR, "the60_v9_assembly.obj")
OBJ_FREE    = os.path.join(OBJ_DIR, "the60_v9_free_spin.obj")

def _h(s):
    """sRGB hex -> scene-linear, so the PNG comes out at exactly this hex"""
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(lin(int(s[i:i+2], 16)) for i in (0, 2, 4))

PAPER_BG = _h("A7A8A9")      # the mid grey the v7.1 sheets used
CUT      = _h("69717A")      # dark grey cut face on printed parts

# printed / structural parts: light grey, and their cut faces go dark.
# everything else is a bought part and keeps its mechanism colour when cut.
PRINTED = {
    "internal_structure": _h("E4E9ED"),
    "knob_body":          _h("E4E9ED"),
    "servo_mount":        _h("D3DAE0"),
    "speaker_cradle":     _h("D3DAE0"),
    "port_face":          _h("D3DAE0"),
    "base_plate":         _h("B4BBC1"),
    "pad":                _h("8A9299"),
}
PRINTED_PREFIX = ("collar_", "bush_", "standoff_")

# bought parts, first matching prefix wins; keep in step with the doc legend
COLOURS = [
    ("motor_band",         _h("E8541F")),
    ("motor_",             _h("FF8948")),
    ("mt6701",             _h("FF8948")),
    ("servo_",             _h("F2A93B")),
    ("carriage",           _h("F7C86B")),
    ("bearing",            _h("7F94A8")),
    ("encoder_",           _h("35C08A")),
    ("lra_",               _h("A96BE0")),
    ("drv2605l",           _h("A96BE0")),
    ("speaker",            _h("3D8BF2")),
    ("supercap",           _h("2FBFB5")),
    ("es9219q",            _h("6E8F1A")),   # DAC
    ("usbc_",              _h("B9CC2F")),   # USB-C
    ("jack_",              _h("8FB01F")),   # 3.5 mm jack
    ("veml7700",           _h("D6E36A")),   # light sensor
    ("plug_envelope",      _h("D9E08A")),
    ("halo_diffuser",      _h("F0E4C4")),
    ("led_flex",           _h("E8C070")),
    ("led_",               _h("FFD9A0")),
    ("display_pcb",        _h("6E7C8A")),
    ("display_case",       _h("93A2B0")),
    ("display_",           _h("AEBAC5")),
    ("tmc6300",            _h("6E7A84")),
    ("driver_board",       _h("3E7D5A")),
    ("commutation_board",  _h("3E7D5A")),
    ("encoder_board",      _h("3E7D5A")),
    ("usbc_board",         _h("3E7D5A")),
    ("jack_board",         _h("3E7D5A")),
    ("light_board",        _h("3E7D5A")),
]
DEFAULT = _h("E4E9ED")

# keep-out volumes and reference bodies: real in the model, noise in a section
HIDE_PREFIX = ("plug_envelope", "servo_stroke_keepout", "encoder_reflective_gap",
               "veml7700_sensitive_area")

def is_printed(name):
    return name in PRINTED or name.startswith(PRINTED_PREFIX)

def colour_for(name):
    if name in PRINTED:
        return PRINTED[name]
    if name.startswith(PRINTED_PREFIX):
        return _h("D3DAE0")
    for pre, c in COLOURS:
        if name.startswith(pre):
            return c
    return DEFAULT

# ---------------------------------------------------------------- views
# plan : cut everything above z, look straight down, azimuth 0 at twelve o'clock
# sect : cut the near half at this azimuth, look inward, image right = +tangential
PLAN_RES, PLAN_S = (1500, 1100), 180.0     # height span 132 mm: the whole Ø125 device
WIDE_RES, WIDE_S = (1500, 620), 140.0      # a full-diameter section, height span 57.9
DET_RES          = (1200, 900)             # a detail: scale is the width span in mm
CV_WIDE = 18.3                             # (-1.5 pad .. 38.1 knob top) / 2

def _plan(vid, z):
    return dict(id=vid, kind="plan", z=z, res=PLAN_RES, scale=PLAN_S, cu=0.0, cv=0.0)

def _sect(vid, az, scale=WIDE_S, cu=0.0, cv=CV_WIDE, res=WIDE_RES, src="engaged", off=0.0):
    """off shifts the cutting plane off the axis, toward the camera, in mm"""
    return dict(id=vid, kind="sect", az=az, src=src, res=res, scale=scale, cu=cu, cv=cv, off=off)

def _det(vid, az, cu, cv, scale, src="engaged", off=0.0):
    return _sect(vid, az, scale=scale, cu=cu, cv=cv, res=DET_RES, src=src, off=off)

VIEWS = [
    _plan("00-plan-floor",  12.0),
    _plan("00b-plan-board", 26.0),
    _sect("01-drive",    90.0, scale=70.0, cu=27.0, cv=10.0),
    _sect("01b-clutch",  90.0, scale=70.0, cu=27.0, cv=10.0, src="free"),
    _det ("02-encoder", 330.0, cu=50.0, cv=21.0, scale=28.0),
    _det ("03-wheels",   30.0, cu=53.0, cv=25.0, scale=28.0),
    dict(id="04-ports", kind="plan", z=3.0, res=DET_RES, scale=48.0, cu=0.0, cv=48.0),
    _det ("05-halo",    200.0, cu=56.0, cv=5.0,  scale=24.0),
    _sect("06-bay",     152.0),
    _det ("07-speaker", 270.0, cu=33.0, cv=11.0, scale=60.0),
    _det ("08-display",  42.0, cu=53.0, cv=28.0, scale=26.0),   # through a support column
]

# ---------------------------------------------------------------- scene helpers
def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_obj(path, coll_name):
    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path, forward_axis='Y', up_axis='Z')
    new = [o for o in bpy.data.objects if o not in before]
    for o in list(new):
        if o.name.startswith(HIDE_PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)
            new.remove(o)
            continue
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        m = bpy.data.materials.new(f"m_{o.name}")
        m.use_nodes = False
        m.diffuse_color = (*colour_for(o.name), 1.0)
        o.data.materials.clear()
        o.data.materials.append(m)
    coll.hide_render = True
    return coll, new

def cut_material():
    m = bpy.data.materials.get("m_cutface")
    if m is None:
        m = bpy.data.materials.new("m_cutface")
        m.use_nodes = False
        m.diffuse_color = (*CUT, 1.0)
    return m

def make_cutter(name, centre, size, rot_z=0.0):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me); bm.free()
    ob.scale = size
    ob.location = centre
    ob.rotation_euler = (0.0, 0.0, rot_z)
    me.materials.append(cut_material())
    bpy.context.scene.collection.objects.link(ob)
    return ob

def bbox_world(o):
    pts = [o.matrix_world @ v.co for v in o.data.vertices]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

# ---------------------------------------------------------------- projection
def cam_az(view):
    """view['az'] is the azimuth the section plane runs through. The plane holds
    azimuths az and az+180, so its normal is at az-90: stand the camera there and
    cut away the half in front of it. The mechanism at az is then cut through the
    middle and lands on the right of the frame; az+180 is on the left."""
    return (view["az"] - 90.0) % 360.0

def uv_of(view, p):
    """world point -> (u, v) in the view's image plane, mm"""
    x, y, z = p
    if view["kind"] == "plan":
        return (-y, x)
    a = math.radians(cam_az(view))
    return (-x * math.sin(a) + y * math.cos(a), z)

def pct_of(view, p):
    """world point -> (left %, top %) on the rendered image"""
    u, v = uv_of(view, p)
    w, h = view["res"]
    sw = view["scale"]
    sh = sw * h / w
    return (50.0 + (u - view["cu"]) / sw * 100.0,
            50.0 - (v - view["cv"]) / sh * 100.0)

def keep_side(view, bb):
    """+1 keep whole, -1 drop whole, 0 straddles the cut plane"""
    x0, x1, y0, y1, z0, z1 = bb
    if view["kind"] == "plan":
        zc = view["z"]
        return 1 if z1 <= zc else (-1 if z0 >= zc else 0)
    a = math.radians(cam_az(view))
    ca, sa = math.cos(a), math.sin(a)
    off = view.get("off", 0.0)
    ss = [x * ca + y * sa for x in (x0, x1) for y in (y0, y1)]
    return 1 if max(ss) <= off else (-1 if min(ss) >= off else 0)

# ---------------------------------------------------------------- render
def setup_render(res):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.film_transparent = False
    d = sc.display.shading
    d.light = 'FLAT'          # flat colour + cavity reads like a printed section
    d.color_type = 'MATERIAL'
    d.show_object_outline = True
    d.object_outline_color = (0.08, 0.09, 0.10)
    d.show_cavity = True
    d.cavity_type = 'BOTH'
    d.curvature_ridge_factor = 1.4
    d.curvature_valley_factor = 1.4
    d.show_shadows = False
    d.show_specular_highlight = False
    w = bpy.data.worlds.get("MECH_BG")
    if w is None:
        w = bpy.data.worlds.new("MECH_BG")
        w.use_nodes = False
    w.color = PAPER_BG
    sc.world = w
    d.background_type = 'WORLD'          # 'VIEWPORT' renders black in a final render
    sc.display.render_aa = '32'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'

def place_camera(view):
    sc = bpy.context.scene
    cam = bpy.data.objects.get("SECT_CAM")
    if cam is None:
        cd = bpy.data.cameras.new("SECT_CAM")
        cam = bpy.data.objects.new("SECT_CAM", cd)
        sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = view["scale"]
    cam.data.clip_start, cam.data.clip_end = 1.0, 800.0
    if view["kind"] == "plan":
        cam.location = (view["cv"], -view["cu"], 300.0)
        cam.rotation_euler = (0.0, 0.0, math.radians(-90.0))
    else:
        a = math.radians(cam_az(view))
        cu, cv = view["cu"], view["cv"]
        cam.location = (300.0 * math.cos(a) - cu * math.sin(a),
                        300.0 * math.sin(a) + cu * math.cos(a), cv)
        cam.rotation_euler = (math.pi / 2, 0.0, math.radians(cam_az(view) + 90.0))
    sc.camera = cam
    return cam

def render_view(view, objects):
    sc = bpy.context.scene
    setup_render(view["res"])
    place_camera(view)
    # cutter
    if view["kind"] == "plan":
        cutter = make_cutter("CUT", (0, 0, view["z"] + 200.0), (400, 400, 400), 0.0)
    else:
        a = math.radians(cam_az(view))
        d = 200.0 + view.get("off", 0.0)
        cutter = make_cutter("CUT", (d * math.cos(a), d * math.sin(a), 0.0),
                             (400, 400, 400), a)
    cutter.hide_render = True
    touched = []
    for o in objects:
        side = keep_side(view, bbox_world(o))
        if side == 1:
            o.hide_render = False
        elif side == -1:
            o.hide_render = True
        else:
            o.hide_render = False
            md = o.modifiers.new("sect", 'BOOLEAN')
            md.operation = 'DIFFERENCE'
            md.solver = 'EXACT'
            md.object = cutter
            md.material_mode = 'TRANSFER' if is_printed(o.name) else 'INDEX'
            touched.append((o, md))
    out = os.path.join(OUT_DIR, view["id"] + ".png")
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    for o, md in touched:
        o.modifiers.remove(md)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return out

def main(only=None):
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = {}
    for src, path in (("engaged", OBJ_ENGAGED), ("free", OBJ_FREE)):
        todo = [v for v in VIEWS if v.get("src", "engaged") == src
                and (only is None or v["id"] in only)]
        if not todo:
            continue
        wipe()
        coll, objs = import_obj(path, "PARTS")
        coll.hide_render = False
        for v in todo:
            print("rendering", v["id"], flush=True)
            render_view(v, objs)
            w, h = v["res"]
            manifest[v["id"]] = dict(kind=v["kind"], az=v.get("az"), z=v.get("z"),
                                     off=v.get("off", 0.0), res=[w, h], scale=v["scale"],
                                     cu=v["cu"], cv=v["cv"], src=src)
    mp = os.path.join(OUT_DIR, "views.json")
    old = {}
    if os.path.exists(mp):
        old = json.load(open(mp))
    old.update(manifest)
    json.dump(old, open(mp, "w"), indent=1)
    print("done", len(manifest), "views")

if __name__ == "__main__":
    only = sys.argv[1:] or None
    main(only)
