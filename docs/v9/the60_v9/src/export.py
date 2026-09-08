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
    made["knob_body"] = knurled
    print("knob: knurled body from cache")
else:
    print("knob: SMOOTH body (knurl cache missing)")

PRINT = {  # part -> (orientation transform, layer, note)
    "knob_body":          (lambda s: Pos(0, 0, Z_KNOB_TOP) * Rot(180, 0, 0) * s, "0.16", "ONE PIECE. top face down, no supports. bore smooth except the 0.15 code-band recess and the V-groove"),
    "internal_structure": (lambda s: Pos(0, 0, -Z_PLATE_TOP) * s, "0.20", "upright on the wall foot; SUPPORT the ledge underside, the lip and the four 1.2 mm seat tabs"),
    "halo_diffuser":      (lambda s: Pos(0, 0, -HALO_Z0) * s, "0.20", "on its underside; natural / translucent PETG"),
    "carriage":           (lambda s: s, "0.16", "flat; Ø37 shoe, sensor pocket underneath, push tab; slides in the plate hole"),
    "servo_mount":        (lambda s: s, "0.20", "flat; tray for the AGFRC servo envelope, open toward the carriage"),
    "speaker_cradle":     (lambda s: s, "0.20", "flat; ring under the speaker flange with three snap fingers"),
    "port_face":          (lambda s: s, "0.16", "standing as modelled; USB-C opening, jack hole, light-sensor aperture"),
    "collar_0":           (lambda s: s, "0.12", "x3, axis vertical; press over a 623ZZ"),
    "bush_0":             (lambda s: s, "0.12", "x3, pin up; brass in production"),
}
BOARDS = ["driver_board", "encoder_board", "usbc_board", "jack_board", "light_board", "commutation_board", "led_flex"]

def centred(s):
    bb = s.bounding_box()
    return Pos(-(bb.min.X + bb.max.X)/2, -(bb.min.Y + bb.max.Y)/2, -bb.min.Z) * s

pd = os.path.join(OUT, "parts"); os.makedirs(pd, exist_ok=True)
bd = os.path.join(OUT, "boards"); os.makedirs(bd, exist_ok=True)
for n, (fn, layer, note) in PRINT.items():
    base = {"collar_0": wheel_collar(), "bush_0": ecc_bush()}.get(n, made[n])
    shape = fn(base)
    if n not in ("knob_body", "internal_structure", "halo_diffuser", "collar_0", "bush_0"):
        shape = centred(shape)
    export_step(shape, os.path.join(pd, f"{n}.step"), write_pcurves=False)
    export_stl(shape, os.path.join(pd, f"{n}.stl"), tolerance=0.02, angular_tolerance=0.1)
    print(f"  {n:20s} {shape.volume/1000:7.2f} cm3  layer {layer}  {note}", flush=True)
export_step(made["base_plate"], os.path.join(pd, "base_plate_STEEL.step"), write_pcurves=False)
export_stl(made["base_plate"], os.path.join(pd, "base_plate_STEEL.stl"), tolerance=0.02, angular_tolerance=0.1)
print("  base_plate_STEEL      laser-cut 5 mm steel (print a stand-in if needed)")
for n in BOARDS:
    export_step(centred(made[n]), os.path.join(bd, f"{n}.step"), write_pcurves=False)
print("  boards: outlines exported to boards/")

def assembly(engaged, name):
    m = made_parts(knurl=False, engaged=engaged); b = bought_parts(engaged)
    if knurled is not None: m["knob_body"] = knurled
    kids = []
    for n, s in {**m, **b}.items():
        if n == "display_small_parts": continue          # 1,000+ pins and pads: 140 MB of STEP for nothing
        try: s.label = n
        except Exception: pass
        kids.append(s)
    asm = Compound(children=kids); asm.label = name
    export_step(asm, os.path.join(OUT, f"{name}.step"), write_pcurves=False)
    print(f"  {name}.step: {len(kids)} named bodies", flush=True)
assembly(True, "the60_v9_assembly")
assembly(False, "the60_v9_assembly_free_spin")

with open(os.path.join(pd, "README.txt"), "w") as f:
    f.write("the 60 - v9 - printable parts (print orientation; they will not assemble as exported)\n\n")
    for n, (fn, layer, note) in PRINT.items(): f.write(f"{n:20s} {layer} mm  {note}\n")
    f.write("base_plate_STEEL      laser-cut 5 mm mild steel, powder-coated; Ø124\n")
    f.write("\nBought: JD-Power MY-3514C gimbal (envelope only); AGFRC C1.5CLS PRO servo (envelope);\n"
            "3x 623ZZ; Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C (PMMA back plate off); Soberton SP-4005-1;\n"
            "2x Abracon AHCR-S04R0SA206Q; TMC6300; MT6701 + D6x2.5 magnet; AEDR-8300 + 0.15 code strip;\n"
            "DRV2605L + VLV101040A; ES9219Q; Switchcraft 35RAPC4BH3; GCT USB4520; VEML7700; 90x SK6812SIDE-A.\n")
    f.write("\nOpen the60_v9_assembly.step (every body named, assembled position) in Fusion, not the parts.\n")
print(f"done in {time.time()-T0:.0f}s")
