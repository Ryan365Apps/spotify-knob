"""Diamond knurl on the v14 knob body's side.

Built one band per subprocess with a BREP checkpoint.  The lessons that made
this work in v5/v6/v7 and are kept here:
  - bands must NOT overlap (KNURL_BAND_OV is negative)
  - both helices go in as ONE cutter per band
  - every cutter is volume-guarded against a silently failed boolean
  - the result must be a single valid solid or the band is retried

v8 difference: there are no peg holes to cut afterwards.  The bore is smooth;
the knurl is the only thing that breaks the turned surface.

  python knurl.py            -> builds out/.knob_body_<hash>.step
  python knurl.py step N     -> one step (used by the runner)
model.knob_body(knurl=True) loads the cached STEP or raises with instructions.
"""
import sys, os, math, hashlib, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import *
from params import *
import model as M

OUT = M.OUT
KEY = (KNURL_N, KNURL_DEPTH, round(KNURL_HELIX_DEG, 3), KNURL_ROWS, KNURL_ROOT_OFF, KNURL_BANDS, KNURL_BAND_OV,
       KNURL_Z0, KNURL_Z1, R_KNOB, R_BORE, R_CROWN_IN, Z_SKIRT_BOT, Z_KNOB_TOP,
       Z_CROWN_BOT, CH_BOT, CH_TOP, CH_IN, R_GROOVE_ROOT, Z_GROOVE0, Z_GROOVE1,
       WHEEL_V_FLAT, Z_RIDGE_MID, KNURL_RUNOUT_BOT, SKIRT_WALL, "v14", 1)
HASH = hashlib.md5(json.dumps(KEY).encode()).hexdigest()[:10]
CACHE = os.path.join(OUT, f".knob_body_{HASH}.step")
TMP = os.path.join(OUT, f".kb_{HASH}")
os.makedirs(TMP, exist_ok=True)

def _star(n, r_root, r_tip, z, phase):
    p = []
    for i in range(n):
        a1 = 2 * math.pi * i / n + phase
        a2 = 2 * math.pi * (i + 0.5) / n + phase
        p += [(r_tip * math.cos(a1), r_tip * math.sin(a1), z),
              (r_root * math.cos(a2), r_root * math.sin(a2), z)]
    return Face(Wire.make_polygon([Vector(*q) for q in p], close=True))

def _band_shell(r, za, zb, d, out):
    return M.revolve_profile([(r - d, za), (r - d, zb), (r + out, zb), (r + out, za)])

def _knurl_star(r, za, zb, z_ref, phase_ref, sign, ext=1.0, dx=0.0):
    d, tip = KNURL_DEPTH + dx, 0.5
    kk = sign * math.tan(math.radians(KNURL_HELIX_DEG)) / r
    sz, h = za - ext, zb - za + 2 * ext
    sec = _star(KNURL_N, r - d - KNURL_ROOT_OFF, r + tip, sz, phase_ref + kk * (sz - z_ref))
    return Solid.extrude_linear_with_rotation(sec, (0, 0, sz), (0, 0, h), math.degrees(kk * h))

def _guard(cut, shell, what):
    f = cut.volume / shell.volume
    assert 0.30 < f < 0.98, f"{what}: cutter is {f:.3f} of the band shell - boolean failed"
    return cut

def knurl_band(r, z0, z1, z_ref, ov, dx=0.0, ov_bot=None):
    """dx: extra depth for alternate bands, so the flanks of an overlapping band are never
    coincident with the flanks already cut (a 0.02 step at the root, invisible)
    ov_bot: a larger overlap below the lowest band, so the grooves run out through the skirt's bottom chamfer
    instead of ending on a flat ledge (which would be a 1 mm overhang when the knob prints top-face-down)"""
    d, out = KNURL_DEPTH + dx, 1.5
    za, zb = z0 - (ov if ov_bot is None else ov_bot), z1 + ov
    shell = _band_shell(r, za, zb, d, out)
    sp = _knurl_star(r, za, zb, z_ref, 0.0, +1, dx=dx)
    sm = _knurl_star(r, za, zb, z_ref, math.pi / KNURL_N, -1, dx=dx)
    return _guard((shell - sp) + (shell - sm), shell, f"band {z0:.1f}-{z1:.1f}")

def band_z(b):
    nb = KNURL_BANDS
    return (KNURL_Z0 + (KNURL_Z1 - KNURL_Z0) * b / nb,
            KNURL_Z0 + (KNURL_Z1 - KNURL_Z0) * (b + 1) / nb)

def step_path(i):
    return os.path.join(TMP, f"s{i}.brep")

def run_step(i):
    nb = KNURL_BANDS
    if i == 0:
        p = M.knob_body_smooth()
    else:
        p = import_brep(step_path(i - 1))
        if 1 <= i <= nb:
            za, zb = band_z(i - 1)
            ov = KNURL_BAND_OV
            for attempt in range(4):
                cut = knurl_band(R_KNOB, za, zb, KNURL_Z0, ov, dx=0.02 * ((i - 1) % 2), ov_bot=(KNURL_RUNOUT_BOT if i == 1 else None))
                expect = (p & cut).volume            # what the band should remove from this body
                q = p - cut
                removed = p.volume - q.volume
                if q.is_valid and len(q.solids()) == 1 and removed > 0.5 * expect and expect > 100:
                    print(f"  band {i}: removed {removed/1000:.2f} cm3 (expected {expect/1000:.2f})", flush=True)
                    p = q; break
                print(f"  band {i} attempt {attempt}: valid {q.is_valid} solids {len(q.solids())} removed {removed/1000:.2f} of {expect/1000:.2f} cm3 - retrying", flush=True)
                ov += 0.011
            else:
                raise RuntimeError(f"band {i} never produced a valid single solid that actually removed the band")
        elif i == nb + 1:
            try: p = p.clean()
            except Exception: pass
            solids = sorted(p.solids(), key=lambda s: -s.volume)
            assert len(solids) == 1, f"knob fragmented into {len(solids)} solids"
            p = solids[0]
            export_step(p, CACHE, write_pcurves=False)
            print("cached", CACHE)
    export_brep(p, step_path(i))
    print(f"step {i}: vol {p.volume/1000:.2f} cm3, faces {len(p.faces())}, valid {p.is_valid}", flush=True)

def build_all():
    for i in range(KNURL_BANDS + 2):
        r = subprocess.run([sys.executable, __file__, "step", str(i)], capture_output=True, text=True)
        out = [l for l in (r.stdout + r.stderr).splitlines() if "Warning" not in l]
        print("\n".join(out[-3:]), flush=True)
        if r.returncode != 0:
            raise SystemExit(f"step {i} failed")

def apply_knurl(_unused):
    if os.path.exists(CACHE):
        return import_step(CACHE).solids()[0]
    if os.environ.get("KN_INPROCESS") == "1":
        build_all()
        return import_step(CACHE).solids()[0]
    raise RuntimeError(f"knurled body not cached: run  python knurl.py  first ({CACHE})")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "step":
        run_step(int(sys.argv[2]))
    else:
        build_all()
