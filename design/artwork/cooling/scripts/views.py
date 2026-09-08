import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import P
from build123d import *

OUT = "/home/claude/dwg/views"
os.makedirs(OUT, exist_ok=True)

def dump(name, objs, direction, hidden=False, look_up=(0,0,1)):
    v = engine.view(objs, direction, look_up=look_up, hidden=hidden)
    d = {"box": v["box"], "vis": v["vis"], "hid": v["hid"]}
    open(os.path.join(OUT, name + ".json"), "w").write(json.dumps(d))
    print(name, "vis", len(v["vis"]), "hid", len(v["hid"]), "box", [round(x,1) for x in v["box"]],
          "%.0f kB" % (os.path.getsize(os.path.join(OUT, name+".json"))/1024))

p = engine.parts()
ring   = p["rim_ring_STEEL"]
core   = p["base_plate"]
close_ = p["closing_plate_AL"]
pad    = p["pad"]
knob   = p["knob_body"]
halo   = p["halo_diffuser"]
struct = p["internal_structure"]

# 1. whole device, front three-quarter (front is az 180 -> -y side toward viewer at az 180)
dump("iso_front", [knob, halo, ring, core, pad], (-0.75, 1.0, 0.62))
# 2. whole device, rear three-quarter (port face at az 0)
dump("iso_rear", [knob, halo, ring, core, pad], (0.95, -0.65, 0.6))
# 3. the base alone, exploded upward: ring, core, closing plate
dump("iso_base_ring", [ring], (0.8, -0.9, 0.75))
dump("iso_base_core", [core], (0.8, -0.9, 0.75))
dump("iso_base_close", [close_], (0.8, -0.9, 0.75))
# 4. bottom view: looking UP from below
dump("bottom_ring", [ring], (0, 0, -1), look_up=(0, 1, 0))
dump("bottom_core", [core], (0, 0, -1), look_up=(0, 1, 0))
dump("bottom_close", [close_], (0, 0, -1), look_up=(0, 1, 0))
# 5. the duct, seen from below with the closing plate off
dump("bottom_duct", [core, ring], (0, 0, -1), look_up=(0, 1, 0))
