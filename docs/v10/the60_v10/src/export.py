import os, sys, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import *
from build123d import export_step, export_stl, Compound
T0 = time.time()
knurled = None
try:
    from knurl import CACHE
    if os.path.exists(CACHE):
        knurled = import_step(CACHE).solids()[0]
except Exception as e:
    print("knurl not available:", e)
made = made_parts(knurl=False); bought = bought_parts(True)
if knurled is not None:
    made["knob_body"] = knurled; print("knob: knurled body from cache")
else:
    print("knob: SMOOTH body (knurl cache missing)")

from printorient import PRINT
BOARDS = ["adapter_board", "audio_board", "motion_board", "encoder_board", "usbc_board", "jack_board", "barrel_board", "light_board", "commutation_board"]
def centred(s):
    bb = s.bounding_box()
    return Pos(-(bb.min.X + bb.max.X)/2, -(bb.min.Y + bb.max.Y)/2, -bb.min.Z) * s
pd = os.path.join(OUT, "parts"); os.makedirs(pd, exist_ok=True)
bd = os.path.join(OUT, "boards"); os.makedirs(bd, exist_ok=True)
for n, (fn, layer, note) in PRINT.items():
    base = {"collar_0": wheel_collar(), "bush_0": ecc_bush()}.get(n, made[n])
    shape = fn(base)
    if n not in ("knob_body", "internal_structure", "halo_diffuser", "collar_0", "bush_0", "deck"):
        shape = centred(shape)
    export_step(shape, os.path.join(pd, f"{n}.step"), write_pcurves=False)
    export_stl(shape, os.path.join(pd, f"{n}.stl"), tolerance=0.02, angular_tolerance=0.1)
    print(f"  {n:20s} {shape.volume/1000:7.2f} cm3  layer {layer}  {note}", flush=True)
export_step(made["base_plate"], os.path.join(pd, "base_plate_STEEL.step"), write_pcurves=False)
export_stl(made["base_plate"], os.path.join(pd, "base_plate_STEEL.stl"), tolerance=0.02, angular_tolerance=0.1)
print("  base_plate_STEEL      laser/waterjet-cut 8 mm steel (print a stand-in if needed)")
for n in BOARDS:
    export_step(centred(made[n]), os.path.join(bd, f"{n}.step"), write_pcurves=False)
print("  boards: outlines exported to boards/")
GROUPS = [   # (group name, predicate on the body name).  First match wins; unmatched bodies stay top-level.
    ("pi5",                 lambda n: n.startswith("pi_") or n.startswith("pi5") or n.startswith("cooler_")),
    ("display_module",      lambda n: n.startswith("panel_") or n.startswith("lens_") or n.startswith("touch_tail")),
    ("motor_carriage_unit", lambda n: n.startswith("motor") or n.startswith("mt6701") or n in ("carriage", "commutation_board")),
    ("wheel_30",            lambda n: n in ("collar_0", "bush_0", "bearing_30") or n.startswith("bearing30_")),
    ("wheel_150",           lambda n: n in ("collar_1", "bush_1", "bearing_150") or n.startswith("bearing150_")),
    ("wheel_270",           lambda n: n in ("collar_2", "bush_2", "bearing_270") or n.startswith("bearing270_")),
    ("servo_unit",          lambda n: n.startswith("servo")),
    ("speaker_unit",        lambda n: n in ("speaker", "speaker_cradle")),
    ("encoder_unit",        lambda n: n.startswith("encoder") or n == "aedr8300"),
    ("lra",                 lambda n: n.startswith("lra")),
    ("adapter_unit",        lambda n: n.startswith("adapter") or n.startswith("touch_")),
    ("audio_unit",          lambda n: n.startswith("audio") or n.startswith("es9219q")),
    ("motion_unit",         lambda n: n.startswith("motion") or n.startswith("tmc6300") or n.startswith("drv2605l")),
    ("port_module",         lambda n: n in ("port_face", "usbc_board", "jack_board", "barrel_board", "light_board", "barrel_jack_ENVELOPE") or n.startswith("usbc_") and "plug" not in n or n.startswith("jack_") and "plug" not in n or n.startswith("veml7700")),
    ("plugs_external",      lambda n: n in ("usbc_plug_ENVELOPE", "jack_plug_ENVELOPE") or n.startswith("barrel_plug")),
    ("cables_internal",     lambda n: n.startswith("hdmi_") or n in ("usbc_plug_pi_ENVELOPE", "header_housing_ENVELOPE", "usba_plug_ENVELOPE")),
    ("halo",                lambda n: n in ("led_strip_ENVELOPE", "halo_diffuser")),
]
# bought parts whose many small solids (leads, pins, shields, balls) fuse into one body for the tree
FUSE = [("pi5_board", lambda n: n.startswith("pi_")), ("mt6701", lambda n: n.startswith("mt6701")),
        ("bearing_30", lambda n: n.startswith("bearing30_")), ("bearing_150", lambda n: n.startswith("bearing150_")), ("bearing_270", lambda n: n.startswith("bearing270_")),
        ("aedr8300", lambda n: n.startswith("encoder_") and n != "encoder_board"), ("es9219q", lambda n: n.startswith("es9219q")),
        ("tmc6300", lambda n: n.startswith("tmc6300")), ("drv2605l", lambda n: n.startswith("drv2605l")), ("veml7700", lambda n: n.startswith("veml7700")),
        ("usbc_receptacle", lambda n: n.startswith("usbc_") and "plug" not in n and n != "usbc_board"), ("jack_3p5", lambda n: n.startswith("jack_") and "plug" not in n and n != "jack_board"),
        ("lra", lambda n: n.startswith("lra_")), ("servo", lambda n: n.startswith("servo_body")), ("panel_flex", lambda n: n.startswith("panel_flex")),
        ("touch_tail_ASSUMED", lambda n: n.startswith("touch_tail")), ("hdmi_ribbon", lambda n: n.startswith("hdmi_ribbon"))]
def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        try: out = out + s
        except Exception: return None
    try: out = out.clean()
    except Exception: pass
    sol = out.solids()
    return sol[0] if len(sol) == 1 else Compound(sol)
def assembly(engaged, name):
    m = made_parts(knurl=False, engaged=engaged); b = bought_parts(engaged)
    if knurled is not None: m["knob_body"] = knurled
    flat = {**m, **b}
    # 1. fuse the small-solid parts into one body each
    fused = {}
    for fname, pred in FUSE:
        keys = [k for k in flat if pred(k)]
        if not keys: continue
        f = fuse_all([flat[k] for k in keys])
        if f is None: continue
        for k in keys: del flat[k]
        fused[fname] = f
    flat.update(fused)
    # 2. group into sub-assemblies
    groups = {g: [] for g, _ in GROUPS}; top = []
    for n, shp in flat.items():
        try: shp.label = n
        except Exception: pass
        for g, pred in GROUPS:
            if pred(n): groups[g].append(shp); break
        else: top.append(shp)
    kids = list(top)
    for g, members in groups.items():
        if not members: continue
        c = Compound(children=members); c.label = g; kids.append(c)
    asm = Compound(children=kids); asm.label = name
    export_step(asm, os.path.join(OUT, f"{name}.step"), write_pcurves=False)
    nb = sum(len(g) for g in groups.values()) + len(top)
    print(f"  {name}.step: {len(kids)} top-level nodes ({len(top)} parts + {sum(1 for g in groups.values() if g)} sub-assemblies), {nb} bodies", flush=True)
assembly(True, "the60_v10_assembly")
assembly(False, "the60_v10_assembly_free_spin")
with open(os.path.join(pd, "README.txt"), "w") as f:
    f.write("the 60 - v10 - printable parts (print orientation; they will not assemble as exported)\n\n")
    for n, (fn, layer, note) in PRINT.items(): f.write(f"{n:20s} {layer} mm  {note}\n")
    f.write(f"base_plate_STEEL      laser/waterjet-cut 8 mm mild steel (engine-turned edge in plan), then 1.0 chamfers top and bottom on a lathe or CNC; powder-coated or polished; Ø{2*PLATE_R:.0f}; Pi window, carriage hole, port slot\n")
    f.write("\nBought: DisplayModule DM-TFTR50-413 panel + cover lens (bonded to the seat); Raspberry Pi 5 + Active Cooler heatsink (fan OFF);\n"
            "DM-ADTTR-014 HDMI-to-DSI adapter; JD-Power MY-3514C gimbal (envelope); AGFRC C1.5CLS PRO servo (envelope); 3x 623ZZ;\n"
            "Soberton SP-4005-1; TMC6300; MT6701 + D6x2.5 magnet; AEDR-8300 + 0.15 code strip; DRV2605L + VLV101040A; ES9219Q;\n"
            "Switchcraft 35RAPC4BH3; GCT USB4520; CUI PJ-063AH barrel jack; VEML7700; a 5 mm addressable LED strip (~46 LEDs); 12 V -> 5 V 10 A converter module.\n")
    f.write("\nOpen the60_v10_assembly.step in Fusion, not the parts: 6 top-level parts (knob, structure, deck, plate, pad, tape) and 17 sub-assemblies\n(pi5, display_module, motor_carriage_unit, wheel_30/150/270, servo_unit, speaker_unit, encoder_unit, lra, adapter_unit, audio_unit,\nmotion_unit, port_module, plugs_external, cables_internal, halo) - one visibility toggle each.\n")
print(f"done in {time.time()-T0:.0f}s")
