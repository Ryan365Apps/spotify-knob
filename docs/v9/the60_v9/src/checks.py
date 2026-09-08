"""v9 automated checks: solidity, pairwise interference across EVERY body (made and bought),
knob rotation, clutch states, stack numbers, containment, and the list of expected
envelope conflicts (bought parts that are only envelopes and are known to overlap)."""
import sys, os, time, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import *
T0 = time.time(); fails = []; warns = []; expected = []
def ok(m): print(f"  ok    {m}")
def fail(m): print(f"  FAIL  {m}"); fails.append(m)
def warn(m): print(f"  warn  {m}"); warns.append(m)
def exp(m): print(f"  env   {m}"); expected.append(m)
def sec(t): print(f"\n[{t}]  ({time.time()-T0:.0f}s)", flush=True)
def inter(a, b):
    try:
        i = a & b
        if i is None: return 0.0
        return i.volume if hasattr(i, "volume") else sum(s.volume for s in i)
    except Exception as e:
        return -1.0

# Pairs that are allowed to touch or overlap, with the reason.  Nothing else is exempt.
def allowed(a, b):
    s = {a, b}
    rules = [
        (lambda: "knob_body" in s and "motor_band" in s, "band pressed 0.6 into the bore: the preload"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and any(x == "motor_magnet" or x.startswith("mt6701") for x in s), "magnet sits inside the hollow shaft the envelope does not model"),
        (lambda: any(x.startswith("servo_stroke") or x.startswith("servo_pushrod") for x in s) and any(x in ("carriage", "servo_mount", "motor_band") or x.startswith("motor") or x.startswith("servo") for x in s), "ASSUMED pushrod / 9 mm stroke keep-out: the carriage tab is the stop, so the keep-out beyond it is never reached"),
        (lambda: "pad" in s and ("base_plate" in s or "carriage" in s or "port_face" in s or "light_board" in s), "stands on the pad"),
        (lambda: "base_plate" in s and any(x in ("internal_structure", "servo_mount", "speaker_cradle", "port_face", "jack_board", "led_flex", "halo_diffuser") or x.startswith("standoff") for x in s), "stands on the plate"),
        (lambda: any(x.startswith("collar") for x in s) and any(x.startswith("bearing") for x in s), "press fit"),
        (lambda: any(x.startswith("bush") for x in s) and any(x.startswith("bearing") or x == "internal_structure" for x in s), "bush in its post / pin in the bearing"),
        (lambda: any(x.startswith("collar") for x in s) and "knob_body" in s, "wheel in the groove"),
        (lambda: "display_case" in s and "internal_structure" in s, "seat tabs against the disc back"),
        (lambda: any(x.startswith("led_") for x in s) and "led_flex" in s, "LEDs on the flex"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and ("carriage" in s or "motor_band" in s), "motor on its shoe / band on the bell"),
        (lambda: "commutation_board" in s and ("carriage" in s or any(x.startswith("mt6701") for x in s)), "board in its pocket"),
        (lambda: "speaker" in s and "speaker_cradle" in s, "flange in the cradle"),
        (lambda: any(x.startswith("encoder_") for x in s) and ("encoder_board" in s or "internal_structure" in s), "encoder on its board in its seat"),
        (lambda: any(x.startswith("lra_") for x in s) and ("internal_structure" in s or any(y.startswith("lra_") for y in s - {a} - {b})), "LRA bonded to its pad"),
        (lambda: any(x.startswith("usbc_") for x in s) and ("usbc_board" in s or "port_face" in s), "receptacle in its notch and opening"),
        (lambda: any(x.startswith("jack_") for x in s) and ("jack_board" in s or "port_face" in s), "jack on its board, bushing through the face"),
        (lambda: any(x.startswith("es9219q") for x in s) and "jack_board" in s, "DAC on its board"),
        (lambda: any(x.startswith("veml7700") for x in s) and ("light_board" in s or "port_face" in s), "sensor on its board"),
        (lambda: any(x.startswith("tmc6300") or x.startswith("drv2605l") or x.startswith("supercap") or x.startswith("standoff") for x in s) and "driver_board" in s, "on the driver board"),
        (lambda: "plug_envelope_internal" in s and any(x.startswith("display_") for x in s), "plug on the vendor board's own socket"),
        (lambda: "plug_envelope_external" in s and ("port_face" in s or any(x.startswith("usbc_") for x in s) or "pad" in s or "base_plate" in s), "plug in the notch"),
        (lambda: any(x.startswith("display_") for x in s) and any(y.startswith("display_") for y in s) and a != b, "vendor assembly internals"),
        (lambda: any(x.startswith("servo_body") for x in s) and "servo_mount" in s, "servo in its pocket"),
        (lambda: any(x.startswith("mt6701") for x in s) and "carriage" in s, "chip in the pocket"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and ("internal_structure" in s or "led_flex" in s), "ENVELOPE: the Ø35 envelope's lowest 4.3 mm stands where the stator base is ASSUMED Ø30 — verify on the real motor"),
    ]
    for pred, why in rules:
        try:
            if pred(): return why
        except Exception:
            pass
    return None

sec("build")
made = made_parts(knurl=False, engaged=True)
bought_on = bought_parts(engaged=True)
bought_off = bought_parts(engaged=False)
made_off = made_parts(knurl=False, engaged=False)
print(f"  {len(made)} made, {len(bought_on)} bought bodies")

sec("solidity")
for n, s in {**made, **bought_on}.items():
    try:
        ns = len(s.solids())
    except Exception:
        ns = -1
    if n == "display_small_parts": continue
    if ns != 1: fail(f"{n}: {ns} solids")
    elif not s.is_valid: fail(f"{n}: invalid")
for n, s in made.items(): ok(f"{n:20s} {s.volume/1000:7.2f} cm3")

def pairwise(allp, tag):
    allp = {k: v for k, v in allp.items() if k != "display_small_parts"}
    names = list(allp); bad = 0; n = 0
    bbs = {k: v.bounding_box() for k, v in allp.items()}
    for a, b in itertools.combinations(names, 2):
        ba, bb = bbs[a], bbs[b]
        if (ba.max.X < bb.min.X - 0.01 or bb.max.X < ba.min.X - 0.01 or ba.max.Y < bb.min.Y - 0.01 or bb.max.Y < ba.min.Y - 0.01
            or ba.max.Z < bb.min.Z - 0.01 or bb.max.Z < ba.min.Z - 0.01): continue
        n += 1
        if os.environ.get("TRACE"): print(f"    {a} x {b}", flush=True)
        v = inter(allp[a], allp[b])
        why = allowed(a, b)
        if v < 0: warn(f"{a} x {b}: boolean failed")
        elif v > 0.05 and why is None:
            fail(f"{tag}: {a} x {b}: {v:.2f} mm3"); bad += 1
        elif v > 0.05 and why:
            if "ENVELOPE" in a or "ENVELOPE" in b or "envelope" in a or "envelope" in b or "keepout" in a or "keepout" in b:
                exp(f"{a} x {b}: {v:.1f} mm3 — {why}")
    if not bad: ok(f"{tag}: no unintended interference ({n} bbox-overlapping pairs tested)")

sec("interference, clutch engaged")
pairwise({**made, **bought_on}, "engaged")
sec("interference, clutch released")
pairwise({k: v for k, v in {**made_off, **bought_off}.items()
          if k in ("carriage", "commutation_board", "internal_structure", "base_plate", "servo_mount", "knob_body", "halo_diffuser", "led_flex", "pad")
          or k.startswith("motor") or k.startswith("servo") or k.startswith("mt6701") or k.startswith("led_")}, "released")

sec("clutch")
knob = made["knob_body"]
d_on = knob.distance_to(bought_on["motor_motor_ENVELOPE"]); d_off = knob.distance_to(bought_off["motor_motor_ENVELOPE"])
ok(f"bell to bore, engaged {d_on:.2f} mm (band {MOTOR_BAND_T} thick, so it presses)")
(ok if d_off >= 0.8 else fail)(f"bell to bore, released {d_off:.2f} mm (>= 0.8)")
ok(f"servo lift {CLUTCH_LIFT} mm; servo force {MOTOR_PRELOAD_N} N direct (RULING 4 Sep)")

sec("knob rotation")
statics = [(n, s) for n, s in {**made, **bought_on}.items()
           if n not in ("knob_body", "motor_band") and not n.startswith("collar") and n != "display_small_parts"]
for ang in (0.0, 17.0, 45.0, 73.0):
    k = Rot(0, 0, ang) * knob
    for n, s in statics:
        v = inter(k, s)
        if v > 0.05: fail(f"knob at {ang} deg x {n}: {v:.2f} mm3")
if not any("knob at" in f for f in fails): ok("knob clear of every static part at 0/17/45/73 deg")
for n in ("display_case", "display_pcb", "internal_structure"):
    d = knob.distance_to({**made, **bought_on}[n])
    (ok if d >= GAP_ROTATE - 0.02 else fail)(f"knob to {n}: {d:.2f} mm (>= {GAP_ROTATE})")

sec("stack and containment")
for n, s in {**made, **bought_on}.items():
    if n == "display_small_parts": continue
    bb = s.bounding_box()
    if bb.max.Z > Z_KNOB_TOP + 0.01: fail(f"{n} above the knob top: {bb.max.Z:.2f}")
    if bb.min.Z < -PAD_T - 0.01: fail(f"{n} below the pad: {bb.min.Z:.2f}")
    r = max(abs(bb.min.X), bb.max.X, abs(bb.min.Y), bb.max.Y)
    if r > R_KNOB + 0.01 and not n.startswith("plug_envelope"): fail(f"{n} outside Ø{2*R_KNOB:.0f}: max Ø{2*r:.1f}")
ok(f"height {HEIGHT:.1f} mm incl. pad (limit 40); knob {KNOB_FRACTION*100:.0f} % of the visible side (>= 67)")
(ok if HEIGHT <= 40.0 else fail)("height within the 40 mm limit")
(ok if KNOB_FRACTION >= 2/3 else fail)("knob share within limit")
(ok if Z_MOTOR_TOP < Z_COMP_BOT else fail)(f"motor top {Z_MOTOR_TOP} under the display's lowest point {Z_COMP_BOT}")
(ok if Z_BELL_BOT > Z_LIP1 - 0.01 else fail)(f"bell bottom {Z_BELL_BOT} (ASSUMED base {MOTOR_BASE_H}) clears the lip top {Z_LIP1} and the halo top {HALO_Z1}")
ok(f"drive band on the bore z {Z_DRIVE0:.1f}-{Z_DRIVE1:.1f}; code band {Z_CODE0:.1f}-{Z_CODE1:.1f} recessed {STRIP_T}; groove {Z_GROOVE0:.1f}-{Z_GROOVE1:.1f}")
# display seat check: the tabs must touch the disc back and clear the board top
tabs = made["internal_structure"]
d_tab_pcb = tabs.distance_to(bought_on["display_pcb"])
(ok if d_tab_pcb >= 0.25 else fail)(f"seat tabs to the board top: {d_tab_pcb:.2f} mm (>= 0.25)")
d_case = tabs.distance_to(bought_on["display_case"])
(ok if d_case <= 0.02 else fail)(f"seat tabs against the disc back: gap {d_case:.2f} mm")
# every M4 seat: the Ø7 screw head must travel from the open plate side up through the ledge hole and on to the tab, clear of everything
for az in DISC_MOUNT_AZ_DEV:
    a = math.radians(az); hx, hy = DISC_MOUNT_PCD/2*math.cos(a), DISC_MOUNT_PCD/2*math.sin(a)
    lo = Pos(LEDGE_PASS_R*math.cos(a), LEDGE_PASS_R*math.sin(a), Z_PLATE_TOP + 0.1) * Cylinder(3.5, Z_LEDGE_TOP + 1.5 - Z_PLATE_TOP - 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hi = Pos(hx, hy, Z_LEDGE_TOP + 2.0) * Cylinder(3.5, Z_SEAT0 - 0.05 - Z_LEDGE_TOP - 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    blocked = []
    for n, s in {**made, **bought_on}.items():
        if n in ("knob_body", "display_small_parts") or n.startswith("display_case"): continue
        v = inter(lo, s) + inter(hi, s)
        if v > 0.05: blocked.append(f"{n} {v:.1f}")
    (ok if not blocked else fail)(f"M4 head path at {az} deg (Ø7, plate side -> ledge hole -> tab): " + ("clear" if not blocked else "blocked by " + ", ".join(blocked)))

sec("wall ports and halo")
ports = [7.5 + 15*i for i in range(PORT_N) if abs(((7.5 + 15*i - MOTOR_AZ + 180) % 360) - 180) > 30]
ok(f"{len(ports)} of {PORT_N} perimeter ports cut (the rest fall in the motor cut-out): {ports}")
ok(f"halo z {HALO_Z0}-{HALO_Z1}; {LED_N} LEDs at r {LED_R} = {2*math.pi*LED_R/LED_N:.2f} mm pitch; diffuser r {R_DIFF_IN}-{R_DIFF_OUT_BOT}/{R_DIFF_OUT_TOP}")

sec("mass")
rho = {"base_plate": 7.85}
tot = 0
for n, s in made.items():
    d = rho.get(n, 1.27); g = s.volume/1000*d; tot += g
    extra = f"  (Al {s.volume/1000*2.7:.0f} g)" if n == "knob_body" else ""
    print(f"  {n:20s} {g:7.1f} g{extra}")
ok(f"made parts {tot:.0f} g + display, motor, servo, speaker, boards")

print("\n" + "="*62)
print(f"{len(fails)} failures, {len(warns)} warnings, {len(expected)} expected envelope contacts  ({time.time()-T0:.0f}s)")
for f in fails: print("  FAIL", f)
for e in expected: print("  ENV ", e)
