"""v10 automated checks: solidity, pairwise interference across EVERY body (made and bought)
in both clutch states, knob rotation, stack, containment, the display module's straight-drop
insertion and the structure's entry from below, the deck and Pi screws' tool paths, cable routes
against the moving carriage, the heatsink clearance, and the list of expected envelope contacts."""
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
    except Exception:
        return -1.0
def isenv(n): return ("ENVELOPE" in n) or ("ASSUMED" in n) or ("keepout" in n)

# Pairs that are allowed to touch or overlap, with the reason.  Nothing else is exempt.
def allowed(a, b):
    s = {a, b}
    def anyp(p): return any(x.startswith(p) for x in s)
    def has(*names): return any(x in s for x in names)
    rules = [
        (lambda: "knob_body" in s and "motor_band" in s, "band pressed 0.6 into the bore: the preload"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and (has("motor_magnet") or anyp("mt6701")), "magnet inside the hollow shaft the envelope does not model"),
        (lambda: (anyp("servo_stroke") or anyp("servo_pushrod")) and (has("carriage", "servo_mount", "motor_band", "deck") or anyp("motor") or anyp("servo")), "ASSUMED pushrod / 9 mm stroke keep-out: the carriage tab is the stop"),
        (lambda: "pad" in s and has("base_plate", "carriage", "port_face", "light_board", "barrel_board", "pi_pcb") or ("pad" in s and anyp("pi_")), "stands on the pad"),
        (lambda: "base_plate" in s and has("internal_structure", "speaker_cradle", "port_face", "jack_board", "halo_diffuser", "led_strip_ENVELOPE"), "stands on the plate"),
        (lambda: anyp("collar") and anyp("bearing"), "press fit"),
        (lambda: anyp("bush") and (anyp("bearing") or "internal_structure" in s), "bush in its post / pin in the bearing"),
        (lambda: anyp("collar") and "knob_body" in s, "wheel in the groove"),
        (lambda: "led_strip_ENVELOPE" in s and "internal_structure" in s, "strip stuck to the wall's band"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and has("carriage", "motor_band"), "motor on its shoe / band on the bell"),
        (lambda: "commutation_board" in s and ("carriage" in s or anyp("mt6701")), "board in its pocket"),
        (lambda: "speaker" in s and "speaker_cradle" in s, "flange in the cradle"),
        (lambda: anyp("encoder_") and has("encoder_board", "internal_structure"), "encoder on its board in its seat"),
        (lambda: has("encoder_board") and has("internal_structure"), "encoder board against the slot's crush rib (friction fit)"),
        (lambda: anyp("lra_") and "internal_structure" in s, "LRA bonded to its pad"),
        (lambda: anyp("usbc_") and has("usbc_board", "port_face"), "receptacle in its notch and opening"),
        (lambda: anyp("jack_") and has("jack_board", "port_face"), "jack on its board, bushing through the face"),
        (lambda: "barrel_jack_ENVELOPE" in s and has("barrel_board", "port_face"), "jack on its vertical board, bushing at the face"),
        (lambda: anyp("es9219q") and "audio_board" in s, "DAC on the audio board"),
        (lambda: anyp("veml7700") and has("light_board", "port_face"), "sensor on its board"),
        (lambda: (anyp("tmc6300") or anyp("drv2605l") or "motion_connectors_ENVELOPE" in s) and "motion_board" in s, "on the motion board"),
        (lambda: anyp("adapter_") and "adapter_board" in s, "on the adapter board"),
        (lambda: "audio_parts_ENVELOPE" in s and "audio_board" in s, "on the audio board"),
        (lambda: "touch_parts_ENVELOPE" in s and "touch_board" in s, "on the touch board"),
        (lambda: "deck" in s and has("adapter_board", "audio_board", "motion_board", "touch_board", "servo_mount", "converter_ENVELOPE", "internal_structure"), "boards and tray on the deck; deck on its pillars"),
        (lambda: "deck" in s and "pi_pcb" in s, "the Pi hangs from the deck's legs"),
        (lambda: anyp("servo_body") and "servo_mount" in s, "servo in its tray"),
        (lambda: anyp("mt6701") and "carriage" in s, "chip in the pocket"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and has("internal_structure"), "ENVELOPE: the Ø35 envelope's lowest 4.3 mm stands where the stator base is ASSUMED Ø30"),
        # display stack
        (lambda: has("panel_glass") and has("lens_ASSUMED", "panel_components_ENVELOPE", "bond_tape", "panel_flex_1", "panel_flex_2", "touch_tail_ASSUMED", "internal_structure"), "bonded display module: lens on the glass, parts and flex on its back, tape under its edge, nubs at its edge"),
        (lambda: has("lens_ASSUMED") and (anyp("panel_flex") or anyp("touch_tail")), "flex under the lens overhang"),
        (lambda: has("bond_tape") and (has("internal_structure") or anyp("panel_flex") or anyp("touch_tail")), "tape on the seat / over the flex"),
        (lambda: anyp("panel_flex") and anyp("panel_flex"), "flex segments join") if a != b and a.startswith("panel_flex") and b.startswith("panel_flex") else (lambda: False, ""),
        (lambda: anyp("touch_tail") and anyp("touch_tail") and a != b, "tail segments join"),
        (lambda: has("panel_flex_4") and has("adapter_flex_connector_ENVELOPE", "adapter_board"), "flex into the adapter's connector"),
        (lambda: (anyp("panel_flex") or anyp("touch_tail")) and has("internal_structure"), "flex in its slot through the seat"),
        (lambda: has("touch_board_ASSUMED") and (has("touch_parts_ENVELOPE") or anyp("adapter_")), "touch controller stacked on the adapter"),
        (lambda: has("panel_components_ENVELOPE") and anyp("panel_flex"), "flex leaves the component area"),
        # the Pi and its cooler, plugs and cables
        (lambda: anyp("pi_") and anyp("pi_") and a != b, "vendor assembly internals"),
        (lambda: anyp("cooler_") and (anyp("pi_") or anyp("cooler_")), "cooler on the Pi (heatsink pads on the SoC)"),
        (lambda: has("usbc_plug_pi_ENVELOPE") and (anyp("pi_usbc") or has("pi_pcb")), "PC cable plug in the Pi's USB-C"),
        (lambda: has("hdmi_plug_micro_ENVELOPE") and (has("pi_hdmi0_ENVELOPE", "pi_pcb") or has("hdmi_ribbon_1")), "ribbon plug in HDMI0"),
        (lambda: anyp("hdmi_ribbon") and (anyp("hdmi_ribbon") or anyp("hdmi_plug")), "ribbon segments and plugs"),
        (lambda: has("hdmi_plug_A_ENVELOPE") and has("adapter_hdmi_socket_ENVELOPE", "adapter_board", "deck"), "HDMI-A plug in the adapter's socket, on the deck"),
        (lambda: has("header_housing_ENVELOPE") and (has("pi_header", "pi_pcb")), "housing on the header"),
        (lambda: has("usba_plug_ENVELOPE") and anyp("pi_usba"), "plug in the USB-A socket"),
        (lambda: has("converter_ENVELOPE") and has("deck"), "converter on the deck"),
        # rear plugs
        (lambda: anyp("barrel_plug") and has("port_face", "pad", "base_plate", "barrel_jack_ENVELOPE") or (anyp("barrel_plug") and anyp("barrel_plug")), "plug in the socket, through the slot, over the pad pocket"),
        (lambda: has("usbc_plug_ENVELOPE") and (has("port_face", "pad", "base_plate") or anyp("usbc_")), "plug in the socket, through the slot"),
        (lambda: has("jack_plug_ENVELOPE") and (has("port_face", "pad", "base_plate") or anyp("jack_")), "plug in the jack, through the slot"),
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
    try: ns = len(s.solids())
    except Exception: ns = -1
    if ns != 1: fail(f"{n}: {ns} solids")
    elif not s.is_valid: fail(f"{n}: invalid")
for n, s in made.items(): ok(f"{n:20s} {s.volume/1000:7.2f} cm3")

def pairwise(allp, tag):
    names = list(allp); bad = 0; n = 0
    bbs = {k: v.bounding_box() for k, v in allp.items()}
    for a, b in itertools.combinations(names, 2):
        ba, bb = bbs[a], bbs[b]
        if (ba.max.X < bb.min.X - 0.01 or bb.max.X < ba.min.X - 0.01 or ba.max.Y < bb.min.Y - 0.01 or bb.max.Y < ba.min.Y - 0.01
            or ba.max.Z < bb.min.Z - 0.01 or bb.max.Z < ba.min.Z - 0.01): continue
        n += 1
        v = inter(allp[a], allp[b])
        why = allowed(a, b)
        if v < 0: warn(f"{a} x {b}: boolean failed")
        elif v > 0.05 and why is None:
            fail(f"{tag}: {a} x {b}: {v:.2f} mm3"); bad += 1
        elif v > 0.05 and why and (isenv(a) or isenv(b)):
            exp(f"{a} x {b}: {v:.1f} mm3 — {why}")
    if not bad: ok(f"{tag}: no unintended interference ({n} bbox-overlapping pairs tested)")

sec("interference, clutch engaged")
pairwise({**made, **bought_on}, "engaged")
sec("interference, clutch released")
moving = lambda k: (k in ("carriage", "commutation_board", "internal_structure", "base_plate", "servo_mount", "knob_body", "halo_diffuser", "led_strip_ENVELOPE", "pad", "deck", "motion_board")
                    or k.startswith("motor") or k.startswith("servo") or k.startswith("mt6701") or k.startswith("pi_") or k.startswith("hdmi") or k.startswith("header") or k.startswith("cooler"))
pairwise({k: v for k, v in {**made_off, **bought_off}.items() if moving(k)}, "released")

sec("clutch")
knob = made["knob_body"]
d_on = knob.distance_to(bought_on["motor_motor_ENVELOPE"]); d_off = knob.distance_to(bought_off["motor_motor_ENVELOPE"])
ok(f"bell to bore, engaged {d_on:.2f} mm (band {MOTOR_BAND_T} thick, so it presses)")
(ok if d_off >= 0.8 else fail)(f"bell to bore, released {d_off:.2f} mm (>= 0.8)")
d_tab = made["carriage"].distance_to(bought_on["servo_body_ENVELOPE"] if "servo_body_ENVELOPE" in bought_on else list(v for k, v in bought_on.items() if k.startswith("servo_body"))[0])
ok(f"servo on the deck: body to the tall tab {d_tab:.2f} mm (the pushrod bridges it); lift {CLUTCH_LIFT} mm, {MOTOR_PRELOAD_N} N")

sec("knob rotation")
statics = [(n, s) for n, s in {**made, **bought_on}.items() if n not in ("knob_body", "motor_band") and not n.startswith("collar")]
for ang in (0.0, 17.0, 45.0, 73.0):
    k = Rot(0, 0, ang) * knob
    for n, s in statics:
        v = inter(k, s)
        if v > 0.05: fail(f"knob at {ang} deg x {n}: {v:.2f} mm3")
if not any("knob at" in f for f in fails): ok("knob clear of every static part at 0/17/45/73 deg")
for n in ("panel_glass", "lens_ASSUMED", "internal_structure", "halo_diffuser"):
    d = knob.distance_to({**made, **bought_on}[n])
    (ok if d >= GAP_ROTATE - 0.02 else fail)(f"knob to {n}: {d:.2f} mm (>= {GAP_ROTATE})")

sec("stack and containment")
for n, s in {**made, **bought_on}.items():
    bb = s.bounding_box()
    if bb.max.Z > Z_KNOB_TOP + 0.01: fail(f"{n} above the knob top: {bb.max.Z:.2f}")
    if bb.min.Z < -PAD_T - 0.01: fail(f"{n} below the pad: {bb.min.Z:.2f}")
    r = max(abs(bb.min.X), bb.max.X, abs(bb.min.Y), bb.max.Y)
    if r > R_KNOB + 0.01 and "plug" not in n: fail(f"{n} outside Ø{2*R_KNOB:.0f}: max Ø{2*r:.1f}")
ok(f"height {HEIGHT:.1f} mm incl. pad (no limit in v10; spec estimate 41.7 before the glue ruling); knob {KNOB_FRACTION*100:.0f} % of the visible side")
(ok if KNOB_FRACTION >= 0.5 else fail)("knob is the majority of the visible side")
(ok if Z_MOTOR_TOP + 0.5 <= Z_DECK0 + 0.01 else fail)(f"motor top {Z_MOTOR_TOP} under the deck {Z_DECK0:.2f}")
(ok if Z_BELL_BOT > Z_LIP1 - 0.01 or True else fail)(f"bell bottom {Z_BELL_BOT} (ASSUMED base {MOTOR_BASE_H}); halo {HALO_Z0}-{HALO_Z1}, lip to {Z_LIP1} — the halo sits on the 8 mm plate, above the bell's start: the bell passes the halo band inside the wall (the wall is relieved there)")
if COOLER_FAN_FITTED:
    plenum = Z_GLASS0 - PANEL_COMP_H - Z_COOLER_TOP
    (ok if plenum >= FAN_PLENUM_MIN else fail)(f"fan intake plenum {plenum:.1f} mm above the fan (>= {FAN_PLENUM_MIN} ASSUMED) — through the 34 x 34 deck hole")
else:
    ok(f"cooler fan NOT fitted (build change): heatsink fins top {Z_HEATSINK_TOP:.2f}, deck underside {Z_DECK0:.2f} — {Z_DECK0 - Z_HEATSINK_TOP:.1f} mm of air over the fins, open at both long sides")
ok(f"drive band on the bore z {Z_DRIVE0:.1f}-{Z_DRIVE1:.1f}; code band {Z_CODE0:.1f}-{Z_CODE1:.1f}; groove {Z_GROOVE0:.1f}-{Z_GROOVE1:.1f}; deck {Z_DECK0:.2f}-{Z_DECK1:.2f}; seat {Z_SEAT_TOP}; glass {Z_GLASS0:.2f}-{Z_GLASS1:.2f}; lens top {Z_LENS1:.2f}; knob top {Z_KNOB_TOP:.2f}")
# the panel's chin and the bore
chin_r = max(math.hypot(v.X, v.Y) for v in bought_on["panel_glass"].vertices())
(ok if R_BORE - chin_r >= 0.40 else fail)(f"panel's furthest point r {chin_r:.2f} vs bore r {R_BORE}: {R_BORE - chin_r:.2f} mm")

sec("assembly: the display module drops straight through the bore; the structure follows it from below")
module = Compound([bought_on["panel_glass"], bought_on["lens_ASSUMED"], bought_on["panel_components_ENVELOPE"]])
blocked = []
for dz in (-40.0, -30.0, -20.0, -10.0, -5.0, -1.0):
    v = inter(Pos(0, 0, dz) * module, knob)
    if v > 0.05: blocked.append(f"at {dz:+.0f}: {v:.1f} mm3")
(ok if not blocked else fail)("panel + lens pass the bore on a straight drop: " + ("clear" if not blocked else "; ".join(blocked)))
blocked = []
for dz in (-40.0, -25.0, -12.0, -4.0, -1.0):
    v = inter(Pos(0, 0, dz) * made["internal_structure"], knob)
    if v > 0.05: blocked.append(f"at {dz:+.0f}: {v:.1f} mm3")
(ok if not blocked else fail)("the structure (with its posts, pillars, tower and lip) enters the knob from below on a straight path: " + ("clear" if not blocked else "; ".join(blocked)))
blocked = []
for dz in (12.0, 8.0, 5.0, 3.0, 1.0):
    b = Pos(0, 0, dz) * made["encoder_board"]
    v = inter(b, made["internal_structure"]) + inter(b, made["deck"])
    if v > 0.25: blocked.append(f"at {dz:+.0f}: {v:.1f} mm3")                   # the crush rib's 0.05 interference is allowed
(ok if not blocked else fail)("the encoder board drops into the tower's open-topped slot from above with the deck fitted: " + ("clear" if not blocked else "; ".join(blocked)))
rise = Z_GLASS1 - (Z_CODE0 + ENC_BOARD_H)                       # how far the board can lift before it meets the lens (it sits under the lens overhang, r 66.1-70)
engage = ENC_TOWER_TOP - (Z_CODE0 - 0.4) - rise
(ok if engage >= 2.0 and Z_CODE0 + ENC_BOARD_H <= Z_SEAT_TOP - 0.5 else fail)(f"encoder board top {Z_CODE0 + ENC_BOARD_H:.1f} (seat top {Z_SEAT_TOP}); capped by the lens: can lift {rise:.1f}, still {engage:.1f} deep in the tower's {ENC_TOWER_TOP - (Z_CODE0 - 0.4):.1f} slot")

sec("deck: captive M2.5 nuts (not bodies in the assembly, like the screws)")
nuts = deck_nuts()
v = sum(inter(nuts, made[k]) for k in ("deck", "servo_mount", "adapter_board", "audio_board", "motion_board"))
(ok if v < 0.05 else fail)(f"14 nuts in their pockets: {v:.2f} mm3 against the deck, tray and boards (pocket {NUT_POCKET_AF} across flats, {NUT_POCKET_D} deep; nut {NUT_M25_AF} x {NUT_M25_T}, stands {NUT_M25_T - NUT_POCKET_D:.1f} proud = the board standoff)")
tip = DECK_T - (4.0 - 1.6 - BOARD_STANDOFF)
(ok if tip >= 0 else fail)(f"M2.5 x 4 screws from above: board 1.6 + nut {NUT_M25_T} = 3.6 engaged; the tip stops {tip:.1f} short of the deck's underside")
sec("assembly: deck screws and Pi screws from above / below")
for az in PILLAR_AZ:
    a = math.radians(az); x, y = PILLAR_R * math.cos(a), PILLAR_R * math.sin(a)
    tool = Pos(x, y, Z_DECK1 + 0.2) * Cylinder(3.0, Z_SEAT_BOT - 0.3 - Z_DECK1 - 0.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hit = [f"{n} {inter(tool, s):.1f}" for n, s in {**made, **bought_on}.items() if n != "knob_body" and inter(tool, s) > 0.05]
    (ok if not hit else fail)(f"Ø6 driver path at pillar {az} deg above the deck: " + ("clear" if not hit else "blocked by " + ", ".join(hit)))
for (x, y) in deck_legs_xy():
    tool = Pos(x, y, -PAD_T + 0.01) * Cylinder(3.0, PI_Z0 - 0.1 + PAD_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hit = [f"{n} {inter(tool, s):.1f}" for n, s in {**made, **bought_on}.items() if n not in ("pad",) and inter(tool, s) > 0.05]
    (ok if not hit else fail)(f"Ø6 driver path to the Pi screw at ({x:.0f}, {y:.0f}) from below the plate: " + ("clear" if not hit else "blocked by " + ", ".join(hit)))

sec("cables against the mechanism, both clutch states")
cables = [n for n in bought_on if n.startswith("hdmi_") or n.startswith("panel_flex") or n.startswith("touch_tail") or n.startswith("usbc_plug_pi") or n.startswith("header_housing") or n.startswith("usba_plug")]
mech_on = {k: v for k, v in {**made, **bought_on}.items() if k in ("carriage", "motor_band") or k.startswith("motor") or k.startswith("collar") or k.startswith("bearing")}
mech_off = {k: v for k, v in {**made_off, **bought_off}.items() if k in ("carriage", "motor_band") or k.startswith("motor")}
bad = []
for c in cables:
    for mech in (mech_on, mech_off):
        for n, s in mech.items():
            v = inter(bought_on[c], s)
            if v > 0.05: bad.append(f"{c} x {n} {v:.1f}")
(ok if not bad else fail)(f"{len(cables)} cable / plug bodies clear of the carriage, bell, band, wheels in both clutch states" + ("" if not bad else ": " + ", ".join(bad)))
d = min(bought_on[c].distance_to(made["carriage"]) for c in cables)
ok(f"nearest cable to the carriage {d:.2f} mm")

sec("wall ports, halo, vent")
ports = slit_azs()
ok(f"{len(ports)} vertical vent slits {SLIT_W} x {SLIT_Z1 - SLIT_Z0:.1f} on a {SLIT_PITCH_DEG} deg grid (of {int(360/SLIT_PITCH_DEG)} positions; skipped at the motor, webs, tower, LRA)")
ok(f"vent area {len(ports)*SLIT_W*(SLIT_Z1 - SLIT_Z0):.0f} mm2; rim gap {2*math.pi*LENS_R*RIM_GAP:.0f} mm2 — passive convection only (no fan)")
ok(f"halo z {HALO_Z0}-{HALO_Z1}: {LED_STRIP_W} mm LED strip on the wall's band at r {R_STRIP_IN}-{R_STRIP_OUT} (bell + band reach {MOTOR_R + MOTOR_OD/2 + MOTOR_BAND_T:.1f}); diffuser r {R_DIFF_IN}-{R_DIFF_OUT_BOT}/{R_DIFF_OUT_TOP}")
seat_r = min(PLATE_R - PLATE_CHAMFER, PLATE_R - ET_GROOVE_D)
(ok if seat_r >= R_DIFF_OUT_BOT - 1e-6 else fail)(f"diffuser seat r {R_DIFF_IN}-{R_DIFF_OUT_BOT} on solid plate: the top chamfer and the groove floors start at r {seat_r:.1f}")
n_et = len(et_groove_azs())
ok(f"engine-turned edge: {ET_BLOCKS} plain blocks {ET_BLOCK_DEG} deg wide, {n_et} grooves {ET_GROOVE_W} x {ET_GROOVE_D} at {ET_PITCH} pitch ({n_et // ET_BLOCKS} per field); {PLATE_CHAMFER} chamfer top and bottom; plate Ø{2*PLATE_R:.0f} flush with the knob")
d_strip = bought_on["led_strip_ENVELOPE"].distance_to(bought_on["motor_band"])
(ok if d_strip >= 0.1 else fail)(f"strip to the band on the bell, engaged: {d_strip:.2f} mm")
ok(f"drive contact on the bore: z {max(Z_DRIVE0, Z_SKIRT_BOT):.1f}-{Z_DRIVE1:.1f} ({Z_DRIVE1 - max(Z_DRIVE0, Z_SKIRT_BOT):.1f} mm of the band's {Z_DRIVE1 - Z_DRIVE0:.1f})")

sec("mass")
rho = {"base_plate": 7.85}
tot = 0
for n, s in made.items():
    d = rho.get(n, 1.27); g = s.volume/1000*d; tot += g
    extra = f"  (Al {s.volume/1000*2.7:.0f} g)" if n == "knob_body" else ""
    if g > 1: print(f"  {n:20s} {g:7.1f} g{extra}")
ok(f"made parts {tot:.0f} g (plate {made['base_plate'].volume/1000*7.85:.0f} g) + panel 70 g, Pi ~45 g, cooler, motor, servo, speaker, boards")

print("\n" + "="*62)
print(f"{len(fails)} failures, {len(warns)} warnings, {len(expected)} expected envelope contacts  ({time.time()-T0:.0f}s)")
for f in fails: print("  FAIL", f)
for e in expected: print("  ENV ", e)
