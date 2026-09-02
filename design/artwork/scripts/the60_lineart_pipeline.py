"""
the60_lineart_pipeline.py  -  Blender 5.2 line-art artwork pipeline for the 60 (Cadrane)

Verified live on Blender 5.2.1 LTS, 2026-09-02, against the v7.1 part exports.

What it does (each step is a function, so you can run them one at a time from the
Scripting workspace or from the Claude connector):

    build_scene(parts_dir)      import STL/OBJ parts, weld, smooth, ghost material,
                                PARTS collection, CTR helper, isometric camera
    build_lineart()             LineArt object with heavy / light / hidden / glow layers
    build_explode(plan)         one 'explode' slider on CTR driving every part
    build_backdrop(style)       generated blueprint / neon-hex backdrop behind the model
    set_style('paper'|'blueprint'|'neon')
    render_frames(folder)       renders the frame range ONE FRAME PER TIMER TICK
                                (a single long blocking render drops the connector link)
    encode_mp4(folder, out)     PNG frames -> H.264 MP4 via a second scene + sequencer

Quick start in Blender:  Scripting tab > New > paste > edit PARTS_DIR > Run Script,
then in the Python console:   build_all()

Units: the scene is set to millimetres with unit scale 0.001, so every number below
is in mm. Grease Pencil stroke radius is in scene units too (0.7 = a 1.4 mm line).
"""
import bpy, os, math, glob
import numpy as np

# ------------------------------------------------------------------ settings
PARTS_DIR   = r"D:\Projects\PROD\spotify-knob\docs\v7.1\parts"   # <- edit
OUT_DIR     = r"D:\Projects\PROD\spotify-knob\design\artwork\renders"   # <- edit
DEVICE_H    = 34.0            # mm, CTR sits at half height
PAPER, INK  = "E7E8E9", "141618"
BLUE_BASE, BLUE_DARK, BLUE_LINE = "1B4FA3", "0E3272", "DCE6FF"
NEON_BG, NEON_EDGE, NEON_BRIGHT = "07080C", "0F5C66", "19B8CC"

# large components and how they explode: name -> (delay 0..1, distance mm on Z)
EXPLODE_PLAN = {
    "knob_body_smooth": (0.00,  75),
    "ring_b":           (0.12,  44),
    "ring_a":           (0.22,  30),
    "halo_diffuser":    (0.28, -30),
    "base_plate":       (0.38, -52),
    # base_shell stays: it is the anchor
}
HIDE_PARTS = ("rocker", "drive_plate", "tyre_hub", "collar_0", "bush_0", "knob_body")

# ------------------------------------------------------------------ helpers
def hex_lin(h, a=1.0):
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)

def srgb(h):
    return np.array([int(h[i:i+2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)

def scene():
    return bpy.data.scenes["Scene"]

def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        scene().collection.children.link(col)
    return col

def move_to(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def refresh_lineart():
    """5.2 quirk: after importing geometry, Line Art does not redraw until its
    modifiers are toggled. Call this whenever lines are missing."""
    la = bpy.data.objects.get("LineArt")
    if not la:
        return
    for m in la.modifiers: m.show_viewport = False
    for m in la.modifiers: m.show_viewport = True
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D': a.tag_redraw()

# ------------------------------------------------------------------ 1. scene
def build_scene(parts_dir=PARTS_DIR):
    sc = scene()
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.length_unit = 'MILLIMETERS'
    sc.unit_settings.scale_length = 0.001
    sc.render.engine = 'BLENDER_EEVEE'
    sc.view_settings.view_transform = 'Standard'   # AgX would grey the flat colours
    sc.render.fps = 30
    sc.render.resolution_x, sc.render.resolution_y = 2400, 1600
    sc.frame_start, sc.frame_end = 1, 210
    w = sc.world or bpy.data.worlds.new("World"); sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = hex_lin(PAPER)
    for n in ("Cube", "Light"):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)

    # ghost material: fully transparent, but the mesh still occludes lines
    ghost = bpy.data.materials.get("MAT_ghost") or bpy.data.materials.new("MAT_ghost")
    ghost.use_nodes = True
    nt = ghost.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    nt.links.new(tr.outputs[0], out.inputs[0])
    try: ghost.surface_render_method = 'BLENDED'
    except Exception: pass

    parts = collection("PARTS")
    files = sorted(glob.glob(os.path.join(parts_dir, "*.stl")) + glob.glob(os.path.join(parts_dir, "*.obj")))
    imported = []
    for fp in files:
        name = os.path.splitext(os.path.basename(fp))[0]
        if name in [o.name for o in parts.objects]:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        if fp.lower().endswith(".stl"):
            bpy.ops.wm.stl_import(filepath=fp)
        else:
            bpy.ops.wm.obj_import(filepath=fp, use_split_objects=True, validate_meshes=True)
        for o in [o for o in bpy.context.selected_objects if o.type == 'MESH']:
            o.name = name
            move_to(o, parts)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)      # weld (STL is unwelded)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
            o.data.materials.clear(); o.data.materials.append(ghost)
            imported.append(o)
    for n in HIDE_PARTS:
        o = bpy.data.objects.get(n)
        if o: o.hide_viewport = True; o.hide_render = True

    ctr = bpy.data.objects.get("CTR")
    if ctr is None:
        ctr = bpy.data.objects.new("CTR", None); sc.collection.objects.link(ctr)
    ctr.location = (0, 0, DEVICE_H / 2)
    ctr["explode"] = 0.0
    ctr.id_properties_ui("explode").update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)

    cam = sc.camera
    if cam is None:
        cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
        sc.collection.objects.link(cam); sc.camera = cam
    cam.parent = None
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 340; cam.data.clip_end = 5000
    cam.rotation_euler = (math.radians(54.7), 0, math.radians(45))   # true isometric
    D = 320
    cam.location = (0.577 * D, -0.577 * D, DEVICE_H / 2 + 0.577 * D)
    cam.parent = ctr; cam.matrix_parent_inverse = ctr.matrix_world.inverted()
    return [o.name for o in imported]

# ------------------------------------------------------------------ 2. line art
LAYERS = {
    # name : (radius mm, opacity, contour, crease, intersection, material-border, occlusion range)
    "heavy":  (0.70, 1.00, True,  False, False, False, None),
    "light":  (0.25, 1.00, False, True,  True,  True,  None),
    "hidden": (0.18, 0.40, True,  True,  False, False, (1, 4)),
    "glow":   (2.20, 0.18, True,  False, False, False, None),
}

def gp_material(name, color):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if not m.is_grease_pencil:
        bpy.data.materials.create_gpencil_data(m)
    m.grease_pencil.color = color
    return m

def build_lineart():
    if "LineArt" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["LineArt"], do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.grease_pencil_add(type='LINEART_COLLECTION')
    la = bpy.context.active_object; la.name = "LineArt"
    move_to(la, collection("LINES"))
    gpd = la.data
    gpd.layers[0].name = "heavy"
    for n in LAYERS:
        if n not in gpd.layers: gpd.layers.new(n)
    for l in gpd.layers:
        l.use_lights = False          # otherwise scene lights darken the strokes
    for m in list(la.modifiers): la.modifiers.remove(m)
    for n, (rad, opa, con, cre, inter, matb, occ) in LAYERS.items():
        mat = gp_material("LINE_" + n, hex_lin(INK))
        if mat.name not in gpd.materials: gpd.materials.append(mat)
        m = la.modifiers.new("LA_" + n, 'LINEART')
        m.source_type = 'COLLECTION'; m.source_collection = collection("PARTS")
        m.target_layer = n; m.target_material = mat
        m.radius = rad; m.opacity = opa
        m.use_contour = con; m.use_crease = cre; m.use_intersection = inter; m.use_material = matb
        m.use_edge_overlap = True            # "Overlapping Edges as Contour" for CAD meshes
        if occ:
            m.use_multiple_levels = True; m.level_start, m.level_end = occ
        if n != "heavy":
            m.use_cache = True
    d = la.modifiers.new("Dash_hidden", 'GREASE_PENCIL_DASH')
    d.segments[0].dash, d.segments[0].gap = 6, 4
    d.tree_node_filter = "hidden"
    refresh_lineart()
    return la

# ------------------------------------------------------------------ 3. explode
def build_explode(plan=EXPLODE_PLAN, frames=((1, 0.0), (75, 1.0), (150, 1.0), (195, 0.0)), spin_deg=360):
    sc = scene(); ctr = bpy.data.objects["CTR"]
    sc.frame_set(1)
    for name, (delay, dist) in plan.items():
        o = bpy.data.objects.get(name)
        if not o: continue
        rest = o.location.z
        fc = o.animation_data.drivers.find("location", index=2) if o.animation_data else None
        if fc:  # keep the rest value already baked into an existing driver
            rest = float(fc.driver.expression.split("+")[0].strip())
        o.driver_remove("location", 2)
        fc = o.driver_add("location", 2); dr = fc.driver; dr.type = 'SCRIPTED'
        v = dr.variables.new(); v.name = "var"; v.type = 'SINGLE_PROP'
        v.targets[0].id = ctr; v.targets[0].data_path = '["explode"]'
        # simple-expression subset only (no Python permission needed)
        dr.expression = f"{rest:.4f} + max(0, min(1, (var - {delay}) / {1 - delay:.2f})) * {dist}"
    for f, val in frames:
        ctr["explode"] = val; ctr.keyframe_insert(data_path='["explode"]', frame=f)
    # camera drift: one full turn, linear, last key one frame past the end = seamless loop
    for f in (1, sc.frame_end, sc.frame_end + 1):
        try: ctr.keyframe_delete("rotation_euler", index=2, frame=f)
        except Exception: pass
    prefs = bpy.context.preferences.edit; old = prefs.keyframe_new_interpolation_type
    prefs.keyframe_new_interpolation_type = 'LINEAR'
    ctr.rotation_euler = (0, 0, 0); ctr.keyframe_insert("rotation_euler", index=2, frame=1)
    ctr.rotation_euler = (0, 0, math.radians(spin_deg))
    ctr.keyframe_insert("rotation_euler", index=2, frame=sc.frame_end + 1)
    prefs.keyframe_new_interpolation_type = old
    # hidden lines fade in while open
    hid = bpy.data.objects["LineArt"].data.layers["hidden"]
    for f, val in ((1, 0.0), (55, 0.0), (95, 1.0), (160, 1.0), (200, 0.0)):
        hid.opacity = val; hid.keyframe_insert("opacity", frame=f)
    sc.frame_set(100)

# ------------------------------------------------------------------ 4. backdrops
def make_blueprint(W, H, mm_per_px):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    v = (0.35 * np.clip(r - 0.35, 0, 1))[..., None]
    img = srgb(BLUE_BASE) * (1 - v) + srgb(BLUE_DARK) * v
    img = img + np.random.default_rng(7).normal(0, 0.018, (H, W, 1)).astype(np.float32)
    p5, p25 = 5 / mm_per_px, 25 / mm_per_px
    minor = ((xx % p5) < 1) | ((yy % p5) < 1)
    major = ((xx % p25) < 1.6) | ((yy % p25) < 1.6)
    img = np.where(minor[..., None], img * 0.75 + srgb(BLUE_LINE) * 0.25, img)
    img = np.where(major[..., None], img * 0.5 + srgb(BLUE_LINE) * 0.5, img)
    return np.clip(img, 0, 1)

def make_neon_hex(W, H, s=54.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    q = (np.sqrt(3) / 3 * xx - 1 / 3 * yy) / s; z = (2 / 3 * yy) / s; x = q; y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    m1 = (dx > dy) & (dx > dz); m2 = (~m1) & (dy > dz)
    rx = np.where(m1, -ry - rz, rx); rz = np.where(~m1 & ~m2, -rx - ry, rz)
    px, py = xx - s * np.sqrt(3) * (rx + rz / 2), yy - s * 1.5 * rz
    d = np.maximum(np.abs(px), np.abs(px) / 2 + np.abs(py) * np.sqrt(3) / 2)   # pointy-top hex
    edge = (s * np.sqrt(3) / 2 - d) < 1.3
    ih = ((rx.astype(np.int64) * 73856093) ^ (rz.astype(np.int64) * 19349663)) % 97 / 97.0
    img = np.ones((H, W, 3), np.float32) * srgb(NEON_BG) + (0.06 * np.clip(1 - r, 0, 1))[..., None] * srgb("15303A")
    img = np.where((ih < 0.05)[..., None], img + 0.3 * srgb(NEON_EDGE), img)
    img = np.where(edge[..., None], img * 0.35 + srgb(NEON_EDGE) * 0.65, img)
    img = np.where((edge & (ih > 0.94))[..., None], srgb(NEON_BRIGHT), img)
    fade = np.clip(1.15 - r, 0.15, 1)[..., None]
    return np.clip(srgb(NEON_BG) * (1 - fade) + img * fade, 0, 1)

def image_from_array(name, arr, path=None):
    H, W = arr.shape[:2]
    im = bpy.data.images.get(name)
    if im: bpy.data.images.remove(im)
    im = bpy.data.images.new(name, W, H, alpha=True)
    im.pixels.foreach_set(np.dstack([arr[::-1], np.ones((H, W, 1), np.float32)]).astype(np.float32).ravel())
    if path:
        im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    im.pack()
    return im

def build_backdrop(style="blueprint"):
    """Backdrop plane parented to the camera, sized to the orthographic frame."""
    sc = scene(); cam = sc.camera
    W, H = sc.render.resolution_x, sc.render.resolution_y
    long_side = max(W, H)
    mm_per_px = cam.data.ortho_scale / long_side
    os.makedirs(OUT_DIR, exist_ok=True)
    if style == "blueprint":
        im = image_from_array("bg_blueprint", make_blueprint(W, H, mm_per_px), os.path.join(OUT_DIR, "bg_blueprint.png"))
    else:
        im = image_from_array("bg_neonhex", make_neon_hex(W, H), os.path.join(OUT_DIR, "bg_neonhex.png"))
    mat = bpy.data.materials.get("MAT_bg_" + style) or bpy.data.materials.new("MAT_bg_" + style)
    mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = im
    nt.links.new(tex.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs[0])
    bd = bpy.data.objects.get("BACKDROP")
    if bd is None:
        me = bpy.data.meshes.new("BACKDROP")
        me.from_pydata([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], [], [(0, 1, 2, 3)]); me.update()
        uv = me.uv_layers.new(name="UVMap")
        for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = (u, v)
        bd = bpy.data.objects.new("BACKDROP", me); sc.collection.objects.link(bd)
    bd.parent = cam; bd.matrix_parent_inverse.identity()
    bd.location = (0, 0, -700); bd.rotation_euler = (0, 0, 0)
    s = cam.data.ortho_scale
    bd.scale = (s * (W / long_side) * 1.02, s * (H / long_side) * 1.02, 1)
    bd.data.materials.clear(); bd.data.materials.append(mat)
    bd.hide_viewport = False; bd.hide_render = False
    return bd

def set_style(name):
    la = bpy.data.objects["LineArt"]; bd = bpy.data.objects.get("BACKDROP")
    M = {n: bpy.data.materials["LINE_" + n] for n in LAYERS}
    def show(mod, on):
        la.modifiers[mod].show_viewport = on; la.modifiers[mod].show_render = on
    if name == "paper":
        for m in M.values(): m.grease_pencil.color = hex_lin(INK)
        show("LA_hidden", False); show("LA_glow", False)
        if bd: bd.hide_viewport = True; bd.hide_render = True
    elif name == "blueprint":
        for m in M.values(): m.grease_pencil.color = hex_lin("EEF3FF")
        show("LA_hidden", True); show("LA_glow", False)
        build_backdrop("blueprint")
    elif name == "neon":
        M["heavy"].grease_pencil.color = hex_lin("3DF4FF"); M["glow"].grease_pencil.color = hex_lin("3DF4FF")
        M["light"].grease_pencil.color = hex_lin("FF3FB4"); M["hidden"].grease_pencil.color = hex_lin("1FA3B0")
        la.modifiers["LA_light"].radius = 0.32
        show("LA_hidden", True); show("LA_glow", True)
        build_backdrop("neon")
    refresh_lineart()

# ------------------------------------------------------------------ 5. render
def render_frames(folder, start=None, end=None):
    """Render one frame per timer tick so the UI (and the Claude connector) stay alive.
    Progress: bpy.app.driver_namespace['the60_render_state']"""
    sc = scene(); os.makedirs(folder, exist_ok=True)
    sc.render.image_settings.media_type = 'IMAGE'
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    st = {"next": start or sc.frame_start, "end": end or sc.frame_end, "folder": folder, "done": False, "errors": []}
    bpy.app.driver_namespace["the60_render_state"] = st
    def step():
        st = bpy.app.driver_namespace["the60_render_state"]
        if st["done"]: return None
        f = st["next"]
        try:
            s = scene(); s.frame_set(f)
            s.render.filepath = os.path.join(st["folder"], f"frame_{f:04d}.png")
            bpy.ops.render.render(write_still=True, scene="Scene")
        except Exception as e:
            st["errors"].append((f, str(e)))
        st["next"] = f + 1
        if st["next"] > st["end"]:
            st["done"] = True; return None
        return 0.05
    bpy.app.timers.register(step, first_interval=0.5)

def encode_mp4(folder, out_path, fps=30):
    """Blender 5.2: video output is Output > Media Type = Video, then FFmpeg/MPEG-4/H.264."""
    files = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
    enc = bpy.data.scenes.get("ENCODE") or bpy.data.scenes.new("ENCODE")
    src = scene()
    enc.render.resolution_x, enc.render.resolution_y = src.render.resolution_x, src.render.resolution_y
    enc.render.resolution_percentage = 100; enc.render.fps = fps
    enc.frame_start, enc.frame_end = 1, len(files)
    if enc.sequence_editor is None: enc.sequence_editor_create()
    se = enc.sequence_editor
    coll = se.strips if hasattr(se, "strips") else se.sequences
    for s in list(coll): coll.remove(s)
    strip = coll.new_image(name="frames", filepath=os.path.join(folder, files[0]), channel=1, frame_start=1)
    for f in files[1:]: strip.elements.append(f)
    enc.render.image_settings.media_type = 'VIDEO'
    enc.render.image_settings.file_format = 'FFMPEG'
    enc.render.ffmpeg.format = 'MPEG4'; enc.render.ffmpeg.codec = 'H264'
    enc.render.ffmpeg.constant_rate_factor = 'HIGH'; enc.render.ffmpeg.gopsize = 15
    enc.view_settings.view_transform = 'Standard'
    enc.render.filepath = out_path
    bpy.ops.render.render(animation=True, scene="ENCODE")
    return out_path

def reel_format():
    """Portrait reel: 1080x1920, orthographic scale applies to the longer (vertical) side."""
    sc = scene()
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.camera.data.ortho_scale = 330

# ------------------------------------------------------------------ all
def build_all(style="blueprint"):
    build_scene(); build_lineart(); build_explode(); reel_format(); set_style(style)
    if bpy.data.filepath: bpy.ops.wm.save_mainfile()
    print("Scene built. Next: render_frames(r'...frames') then encode_mp4(...)")
