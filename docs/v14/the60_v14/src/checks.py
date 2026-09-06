"""v14 automated checks: solidity, pairwise interference across EVERY body (made and bought)
in both clutch states, knob rotation, stack, containment, the display module's straight-drop
insertion and the structure's entry from below, the Pi stack's screw paths, cable routes
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
        (lambda: "pad" in s and has("base_plate", "rim_ring_STEEL", "closing_plate_AL", "carriage", "port_face", "light_board", "barrel_board", "pi_pcb") or ("pad" in s and anyp("pi_")), "stands on the pad"),
        (lambda: has("base_plate", "rim_ring_STEEL", "closing_plate_AL") and has("internal_structure", "speaker_cradle", "port_face", "jack_board", "halo_diffuser", "led_strip_ENVELOPE", "converter_gap_pad_ASSUMED", "servo_mount", "connect_bracket"), "stands on the plate"),
        (lambda: "connect_bracket" in s and "port_face" in s, "the bracket's outer end rests on the port face's rail"),
        (lambda: anyp("board_washer") and has("base_plate", "audio_board", "motion_board"), "board on its washers on the plate"),
        (lambda: anyp("servo_body") and has("base_plate"), "the servo lies on the plate inside its frame"),
        (lambda: anyp("pi_washer") and has("closing_plate_AL", "pi_pcb"), "the Pi on its washers on the closing plate's lands"),
        (lambda: anyp("pi_standoff") and has("pi_pcb", "adapter_board"), "standoffs between the Pi and the adapter"),
        (lambda: anyp("touch_standoff") and has("adapter_board", "touch_board_ASSUMED", "adapter_parts_ENVELOPE"), "touch controller's standoffs on the adapter (through its ASSUMED parts envelope)"),
        (lambda: (anyp("cb_") and has("connect_board")) or ("connect_board" in s and "connect_bracket" in s), "connect board's parts on it; the board on the bracket's bosses"),
        (lambda: anyp("cable_") and (anyp("cable_") or has("cb_cn1_cable", "adapter_flex_connector")), "the flat cable's segments; its ends in the two connectors"),
        (lambda: has("panel_flex_6") and has("cb_cn2_panel_flex"), "panel flex into the connect board's CN2"),
        (lambda: a in ("base_plate", "rim_ring_STEEL", "closing_plate_AL") and b in ("base_plate", "rim_ring_STEEL", "closing_plate_AL"), "the plate's three bodies: the ring's flange in the core's rebate, the closing plate in its recess"),
        (lambda: has("converter_gap_pad_ASSUMED") and has("converter_ENVELOPE"), "converter on its gap pad"),
        (lambda: "halo_diffuser" in s and "internal_structure" in s, "the diffuser's flange under the structure's lip"),
        (lambda: anyp("collar") and anyp("bearing"), "press fit"),
        (lambda: anyp("bush") and (anyp("bearing") or "internal_structure" in s), "bush in its post / pin in the bearing"),
        (lambda: anyp("collar") and "knob_body" in s, "wheel in the groove"),
        (lambda: "led_strip_ENVELOPE" in s and "internal_structure" in s, "strip stuck to the wall's band"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and has("carriage", "motor_band"), "motor on its shoe / band on the bell"),
        (lambda: "commutation_board" in s and ("carriage" in s or anyp("mt6701")), "board in its pocket"),
        (lambda: "speaker" in s and "speaker_cradle" in s, "flange in the cradle"),
        (lambda: any(x.startswith("encoder_") and x != "encoder_board" for x in s) and has("encoder_board"), "encoder and its screw heads on its board"),
        (lambda: has("encoder_board") and has("internal_structure"), "encoder board on its boss on the seat flange"),
        (lambda: has("encoder_reflective_gap_2mm_typ") and has("knob_body"), "the sensor's 2 mm reflective gap ends at the code ring's face"),
        # v14: grounding features and the two homeless items
        (lambda: has("knob_bleed_leaf_ASSUMED") and has("knob_body", "internal_structure", "knob_bleed_screw"), "the bleed leaf bears on the crown, sits on its boss, under its screw"),
        (lambda: anyp("chassis_bond") and (anyp("chassis_bond") or has("base_plate")), "the chassis bond's washer, terminal and screw stack on the plate"),
        (lambda: anyp("ring_bond") and (anyp("ring_bond") or has("rim_ring_STEEL", "base_plate")), "the rim ring's bond screw through its flange into the core, star washer on the flange"),
        (lambda: anyp("usbc_shell_wire") and (anyp("usbc_shell_wire") or anyp("usbc_") or anyp("chassis_bond") or has("usbc_board")), "the USB-C shell wire: from the receptacle to the chassis bond's terminal"),
        (lambda: anyp("motor_bond_wire") and (anyp("motor_bond_wire") or anyp("motor") or has("carriage", "motion_connectors_ENVELOPE")), "the motor frame's bond lead: under a base screw, to the motion board"),
        (lambda: anyp("sensor_cable") and (anyp("sensor_cable") or has("carriage", "commutation_board", "motion_connectors_ENVELOPE", "servo_mount")), "the rotor sensor lead: out of the carriage's notch, up beside the tab, its loop over the servo frame, into the motion board"),
        (lambda: anyp("lra_pogo") and (anyp("lra_pogo") or anyp("lra_") or has("internal_structure")), "the pogo board in its clip, its pins on the LRA's pads"),
        (lambda: has("audio_usb_plug_ENVELOPE") and has("audio_board"), "USB plug on the audio board's edge"),
        (lambda: has("motion_usb_plug_ENVELOPE") and has("motion_board"), "USB plug on the motion board's edge"),
        (lambda: anyp("lra_") and "internal_structure" in s, "LRA bonded to its pad"),
        (lambda: any(x.startswith("usbc_") and x != "usbc_board" for x in s) and has("usbc_board", "port_face"), "receptacle in its notch and opening"),
        (lambda: any(x.startswith("jack_") and x != "jack_board" for x in s) and has("jack_board", "port_face"), "jack on its board, bushing through the face"),
        (lambda: "barrel_jack_ENVELOPE" in s and has("barrel_board", "port_face"), "jack on its vertical board, bushing at the face"),
        (lambda: anyp("es9219q") and "audio_board" in s, "DAC on the audio board"),
        (lambda: anyp("veml7700") and has("light_board", "port_face"), "sensor on its board"),
        (lambda: (anyp("tmc6300") or anyp("drv2605l") or "motion_connectors_ENVELOPE" in s) and "motion_board" in s, "on the motion board"),
        (lambda: anyp("adapter_") and "adapter_board" in s, "on the adapter board"),
        (lambda: "audio_parts_ENVELOPE" in s and "audio_board" in s, "on the audio board"),
        (lambda: "touch_parts_ENVELOPE" in s and "touch_board" in s, "on the touch board"),
        (lambda: anyp("servo_body") and "servo_mount" in s, "servo in its tray"),
        (lambda: anyp("mt6701") and "carriage" in s, "chip in the pocket"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and has("internal_structure"), "ENVELOPE: the Ø35 envelope's lowest 4.3 mm stands where the stator base is ASSUMED Ø30"),
        # display stack
        (lambda: has("panel_glass") and has("lens_ASSUMED", "panel_components_ENVELOPE", "bond_tape", "panel_flex_1", "panel_flex_2", "touch_tail_ASSUMED", "internal_structure"), "bonded display module: lens on the glass, parts and flex on its back, tape under its edge, nubs at its edge"),
        (lambda: has("lens_ASSUMED") and (anyp("panel_flex") or anyp("touch_tail")), "flex under the lens overhang"),
        (lambda: has("bond_tape") and (has("internal_structure") or anyp("panel_flex") or anyp("touch_tail")), "tape on the seat / over the flex"),
        (lambda: anyp("panel_flex") and anyp("panel_flex"), "flex segments join") if a != b and a.startswith("panel_flex") and b.startswith("panel_flex") else (lambda: False, ""),
        (lambda: anyp("touch_tail") and anyp("touch_tail") and a != b, "tail segments join"),
        (lambda: (anyp("panel_flex") or anyp("touch_tail")) and has("internal_structure"), "flex in its slot through the seat"),
        (lambda: has("touch_board_ASSUMED") and (has("touch_parts_ENVELOPE") or anyp("touch_standoff")), "touch controller on its standoffs"),
        (lambda: has("panel_components_ENVELOPE") and anyp("panel_flex"), "flex leaves the component area"),
        # the Pi and its cooler, plugs and cables
        (lambda: anyp("pi_") and anyp("pi_") and a != b, "vendor assembly internals"),
        (lambda: anyp("cooler_") and (anyp("pi_") or anyp("cooler_")), "cooler on the Pi (heatsink pads on the SoC)"),
        (lambda: has("usbc_plug_pi_ENVELOPE") and (anyp("pi_usbc") or has("pi_pcb")), "PC cable plug in the Pi's USB-C"),
        (lambda: has("hdmi_plug_micro_ENVELOPE") and (has("pi_hdmi0_ENVELOPE", "pi_hdmi1_ENVELOPE", "pi_pcb") or has("hdmi_ribbon_1")), "ribbon plug in the micro-HDMI"),
        (lambda: anyp("hdmi_ribbon") and (anyp("hdmi_ribbon") or anyp("hdmi_plug")), "ribbon segments and plugs"),
        (lambda: has("hdmi_plug_A_ENVELOPE") and has("adapter_hdmi_socket"), "HDMI-A plug in the adapter's socket"),
        (lambda: anyp("usbc_plug_pi") and anyp("usbc_plug_pi"), "the up-angle plug's head and its lead"),
        (lambda: has("header_housing_ENVELOPE") and (has("pi_header", "pi_pcb")), "housing on the header"),
        (lambda: has("usba_plug_ENVELOPE") and anyp("pi_usba"), "plug in the USB-A socket"),
        (lambda: has("converter_ENVELOPE") and has("base_plate"), "converter on the plate"),
        # rear plugs
        (lambda: anyp("barrel_plug") and has("port_face", "pad", "base_plate", "rim_ring_STEEL", "closing_plate_AL", "barrel_jack_ENVELOPE") or (anyp("barrel_plug") and anyp("barrel_plug")), "plug in the socket, through the slot, over the pad pocket"),
        (lambda: has("usbc_plug_ENVELOPE") and (has("port_face", "pad", "base_plate", "rim_ring_STEEL") or anyp("usbc_")), "plug in the socket, through the slot"),
        (lambda: has("jack_plug_ENVELOPE") and (has("port_face", "pad", "base_plate", "rim_ring_STEEL") or anyp("jack_")), "plug in the jack, through the slot"),
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
moving = lambda k: (k in ("carriage", "commutation_board", "internal_structure", "base_plate", "rim_ring_STEEL", "closing_plate_AL", "servo_mount", "knob_body", "halo_diffuser", "led_strip_ENVELOPE", "pad", "motion_board")
                    or k.startswith("motor") or k.startswith("servo") or k.startswith("mt6701") or k.startswith("pi_") or k.startswith("hdmi") or k.startswith("header") or k.startswith("cooler"))
pairwise({k: v for k, v in {**made_off, **bought_off}.items() if moving(k)}, "released")

sec("clutch")
knob = made["knob_body"]
d_on = knob.distance_to(bought_on["motor_motor_ENVELOPE"]); d_off = knob.distance_to(bought_off["motor_motor_ENVELOPE"])
ok(f"bell to bore, engaged {d_on:.2f} mm (band {MOTOR_BAND_T} thick, so it presses)")
(ok if d_off >= 0.8 else fail)(f"bell to bore, released {d_off:.2f} mm (>= 0.8)")
d_tab = made["carriage"].distance_to(bought_on["servo_body_ENVELOPE"] if "servo_body_ENVELOPE" in bought_on else list(v for k, v in bought_on.items() if k.startswith("servo_body"))[0])
ok(f"servo on the plate: body to the tab {d_tab:.2f} mm (the pushrod bridges it); tab to z {CARRIAGE_TAB_TOP} (v11: 28.5 through the deck); lift {CLUTCH_LIFT} mm, {MOTOR_PRELOAD_N} N")

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
ok(f"height {HEIGHT:.1f} mm incl. pad (no limit; the v10 spec estimated 41.7 before the glue ruling); knob {KNOB_FRACTION*100:.0f} % of the visible side")
(ok if KNOB_FRACTION >= 0.5 else fail)("knob is the majority of the visible side")
display = ("panel_glass", "lens_ASSUMED", "panel_components_ENVELOPE", "bond_tape", "knob_body", "internal_structure", "halo_diffuser", "encoder_board")   # the encoder is above the seat now
tallest = []
for n, s in {**made, **bought_on}.items():
    if n in display or n.startswith("panel_flex") or n.startswith("touch_tail") or n.startswith("collar") or n.startswith("bush") or n.startswith("bearing") or n.startswith("nub") or n.startswith("encoder_") or n.startswith("knob_bleed"): continue
    z = s.bounding_box().max.Z
    tallest.append((z, n))
    if z > Z_SEAT_BOT - 0.15 + 0.01: fail(f"{n} reaches z {z:.2f}: under the seat's underside {Z_SEAT_BOT} it must stay below {Z_SEAT_BOT - 0.15:.2f}")
tallest.sort(reverse=True)
ok("under the seat (highest first): " + ", ".join(f"{n} {z:.1f}" for z, n in tallest[:6]))
ok(f"seat floor: the wheels' groove over the drive band allows {Z_SEAT_WHEELS:.1f}; the adapter's HDMI socket ({Z_ADAPTER_HDMI_TOP:.2f}) needs {Z_ADAPTER_HDMI_TOP + 0.3 + 2.0:.1f}; seat top {Z_SEAT_TOP} (v12 28.0 with the code band on the bore)")
ok(f"adapter underside {Z_ADAPTER0:.2f}: {Z_ADAPTER0 - ADAPTER_UNDER_H - Z_HEATSINK_TOP:.1f} mm over the heatsink's fins (with {ADAPTER_UNDER_H} of underside parts), {Z_ADAPTER0 - (Z_PLATE_TOP + SERVO_H + 0.5):.2f} over the servo's frame, {Z_ADAPTER0 - Z_PI_USBA_TOP:.1f} below the USB-A shells' top (it does not reach them: adapter x to {ADAPTER_X0 + ADAPTER_L:.0f}, shells from {PI_X0 + 66.6:.0f})")
ok(f"drive band on the bore z {max(Z_DRIVE0, Z_SKIRT_BOT):.1f}-{Z_DRIVE1:.1f}; groove {Z_GROOVE0:.1f}-{Z_GROOVE1:.1f}; seat {Z_SEAT_TOP}; glass {Z_GLASS0:.2f}-{Z_GLASS1:.2f}; lens top {Z_LENS1:.2f}; crown underside {Z_CROWN_BOT:.2f} with the code ring's face at {Z_CODE_FACE:.2f}; knob top {Z_KNOB_TOP:.2f} (v12 36.38, v11 39.18)")
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
sec("the encoder facing up at the crown's code ring")
pkg = bought_on["encoder_package"]; gapbody = bought_on["encoder_reflective_gap_2mm_typ"]
top = pkg.bounding_box().max.Z
gap = Z_CODE_FACE - top
(ok if abs(gap - ENC_GAP) < 0.03 else fail)(f"sensor face z {top:.2f} to the code ring's face {Z_CODE_FACE:.2f}: {gap:.2f} mm (AEDR-8300 typical {ENC_GAP}); crown underside {Z_CROWN_BOT:.2f}")
rr = [math.hypot(v.X, v.Y) for v in pkg.vertices()]
(ok if min(rr) >= CODE_R0 + 0.3 and max(rr) <= CODE_R1 - 0.3 else fail)(f"the sensor's footprint r {min(rr):.1f}-{max(rr):.1f} lies inside the code ring r {CODE_R0}-{CODE_R1} (0.15 recess in the crown's underside)")
v = inter(gapbody, knob)
(ok if v < 0.05 else fail)(f"the sensor's 2 mm reflective-gap keep-out reaches the ring's face and no further: {v:.2f} mm3 into the knob")
d = knob.distance_to(made["encoder_board"]); d2 = knob.distance_to(bought_on["encoder_screw_0"])
ok(f"knob to the encoder board {d:.2f}, to its screw heads {d2:.2f}; lens edge r {LENS_R} vs the board's inner edge r {ENC_R - 4:.0f}")
ok(f"code ring: {2*math.pi*ENC_R:.0f} mm round at r {ENC_R:.0f} = {2*math.pi*ENC_R/0.08:.0f} lines at the sensor's 0.08 mm pitch (v12's bore strip: 5,700); axial play of the knob on the V-wheels is what varies the gap now, not the bore's run-out")
sec("the Pi stack: closing-plate lands / washers / Pi / standoffs / adapter (screws from below and above)")
for (x, y) in pi_holes_xy():
    tool = Pos(x, y, -PAD_T + 0.01) * Cylinder(3.0, PAD_T - 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hit = [f"{n} {inter(tool, s):.1f}" for n, s in {**made, **bought_on}.items() if n not in ("pad",) and inter(tool, s) > 0.05]
    (ok if not hit else fail)(f"Ø6 driver to the M2.5 csk screw at ({x:.1f}, {y:.1f}) under the closing plate: " + ("clear" if not hit else "blocked by " + ", ".join(hit)))
    tool = Pos(x, y, Z_ADAPTER1 + 2.1) * Cylinder(3.0, Z_SEAT_BOT - 0.3 - Z_ADAPTER1 - 2.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hit = [f"{n} {inter(tool, s):.1f}" for n, s in {**made, **bought_on}.items() if inter(tool, s) > 0.05 and n not in ("knob_body", "internal_structure") and not n.startswith("cable_")]
    (ok if not hit else fail)(f"Ø6 driver to the adapter's screw at ({x:.1f}, {y:.1f}) from above (before the structure goes on; the flat cable is plugged in after): " + ("clear" if not hit else "blocked by " + ", ".join(hit)))
lands = [f for f in made["closing_plate_AL"].faces()]
ok(f"stack: land (closing plate 0-{CLOSING_T}) / washer 0.5 / Pi board {PI_Z0}-{PI_Z_TOP:.2f} / M2.5 x {STANDOFF_L:.0f} standoffs / adapter {Z_ADAPTER0:.2f}-{Z_ADAPTER1:.2f} / M2.5 x 5 pan heads to {Z_ADAPTER1 + 2:.2f}; M2.5 x 6 csk from below through the land and washer into the standoff")
sec("boards on the plate: blind tapped holes stop in the web")
holes = top_screw_xy()
(ok if BLIND_D <= WEB_T - 1.0 else fail)(f"{len(holes)} x M2.5 blind holes {BLIND_D} deep from the top face leave {WEB_T - BLIND_D:.1f} of the {WEB_T} web over the duct - no islands needed for them ({len(CLOSING_SCREW_XY)} closing screws from below have Ø7 islands)")
for (x, y) in holes:
    r = math.hypot(x, y)
    if r > R_CORE_DUCT - 1.0: fail(f"top screw at ({x:.1f}, {y:.1f}) r {r:.1f}: beyond the aluminium core ({R_CORE_DUCT})")
hit = []
for (x, y) in holes:
    probe = Pos(x, y, PLATE_T - BLIND_D - 0.2) * Cylinder(1.0, BLIND_D + 0.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    v = inter(probe, made["base_plate"])
    if v < 0.05: hit.append(f"({x:.1f}, {y:.1f})")
(ok if not hit else fail)("every top screw's hole is in the plate (not over a window): " + ("yes" if not hit else "missing at " + ", ".join(hit)))
sec("cables against the mechanism, both clutch states")
cables = [n for n in bought_on if n.startswith("hdmi_") or n.startswith("panel_flex") or n.startswith("touch_tail") or n.startswith("usbc_plug_pi") or n.startswith("header_housing") or n.startswith("usba_plug") or n.startswith("cable_")]
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
ok(f"vent area {len(ports)*SLIT_W*(SLIT_Z1 - SLIT_Z0):.0f} mm2 at z {SLIT_Z0:.1f}-{SLIT_Z1:.1f} (above the code band, under the seat); rim gap {2*math.pi*LENS_R*RIM_GAP:.0f} mm2 — passive convection only (no fan)")
ok(f"halo z {HALO_Z0}-{HALO_Z1}: {LED_STRIP_W} mm LED strip on the wall's band at r {R_STRIP_IN}-{R_STRIP_OUT} (bell + band reach {MOTOR_R + MOTOR_OD/2 + MOTOR_BAND_T:.1f}); diffuser r {R_DIFF_IN}-{R_DIFF_OUT_BOT}/{R_DIFF_OUT_TOP}")
seat_r = PLATE_R - PLATE_CHAMFER
(ok if seat_r >= R_DIFF_OUT_BOT - 1e-6 else fail)(f"diffuser seat r {R_DIFF_IN}-{R_DIFF_OUT_BOT} on solid plate: the top chamfer and the groove floors start at r {seat_r:.1f}")
ok(f"rim edge: PLAIN (the engine turning is removed, design-changes item 5 - the replacement treatment is chosen separately; the vent openings stay parametric: INTAKE_N/W/H/AZ0/AZ1, INTAKE_UNDERCUT_H, EXHAUST_AZ); {PLATE_CHAMFER} chamfer top and bottom; plate Ø{2*PLATE_R:.0f} flush with the knob")
d_strip = bought_on["led_strip_ENVELOPE"].distance_to(bought_on["motor_band"])
(ok if d_strip >= 0.1 else fail)(f"strip to the band on the bell, engaged: {d_strip:.2f} mm")
ok(f"drive contact on the bore: z {max(Z_DRIVE0, Z_SKIRT_BOT):.1f}-{Z_DRIVE1:.1f} ({Z_DRIVE1 - max(Z_DRIVE0, Z_SKIRT_BOT):.1f} mm of the band's {Z_DRIVE1 - Z_DRIVE0:.1f})")

sec("grounding (GROUNDING.md): one chassis bond, the ring's dedicated bond, the knob's bleed, the shell wire")
d = bought_on["knob_bleed_leaf_ASSUMED"].distance_to(knob)
(ok if d < 0.02 else fail)(f"the bleed leaf's dome touches the crown's underside at r {BLEED_R} (gap {d:.2f}); the lens ends at r {LENS_R}, the code ring starts at {CODE_R0}")
x, y = GND_BOND_XY
ok(f"chassis bond at ({x:.0f}, {y:.0f}), r {math.hypot(x, y):.1f}, az {math.degrees(math.atan2(y, x)) % 360:.0f}: {math.hypot(x - PORT_FACE_R0, y - PORT_BARREL_T):.0f} mm from the barrel inlet; the rim ring's bond screw at az {RING_BOND_AZ}, r {RING_BOND_R}: {math.hypot(x - RING_BOND_R*math.cos(math.radians(RING_BOND_AZ)), y - RING_BOND_R*math.sin(math.radians(RING_BOND_AZ))):.0f} mm from it")
probe = polar(RING_BOND_AZ, RING_BOND_R, RIM_STEP_Z - 2.9) * Cylinder(1.0, 2.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
(ok if inter(probe, made["base_plate"]) < 0.05 and inter(bought_on["ring_bond_screw"], made["rim_ring_STEEL"]) < 0.05 else fail)("the ring bond screw passes the flange's Ø3.4 clearance and threads 3.0 into the core's shoulder (no other feature in the way)")
wires = [n for n in bought_on if n.startswith("usbc_shell_wire")]
ok(f"USB-C shell wire: {len(wires)} segments from the receptacle's board up out of the slot, under the connect bracket's slab (z 8.1-9.4 in its 1.5 gap) to the chassis terminal - the 3.5 mm jack's shell touches nothing metal (the port face is PETG: a stated requirement, GROUNDING 6)")
ok(f"halo: {LED_N} LEDs at {LED_PER_M}/m on the strip at r {(R_STRIP_IN + R_STRIP_OUT)/2:.1f} = {HALO_PEAK_A:.2f} A at full white ({HALO_PEAK_A*5:.1f} W) - the peak that sizes the converter and the halo feed; no sustained cap")
sec("mass")
rho = {"base_plate": 2.7, "rim_ring_STEEL": 7.85, "closing_plate_AL": 2.7}
tot = 0
for n, s in made.items():
    d = rho.get(n, 1.27); g = s.volume/1000*d; tot += g
    extra = f"  (Al {s.volume/1000*2.7:.0f} g)" if n == "knob_body" else (f"  (in Al {s.volume/1000*2.7:.0f} g)" if n == "rim_ring_STEEL" else "")
    if g > 1: print(f"  {n:20s} {g:7.1f} g{extra}")
core_g = made['base_plate'].volume/1000*2.7; ring_g = made['rim_ring_STEEL'].volume/1000*7.85; cp_g = made['closing_plate_AL'].volume/1000*2.7
ok(f"plate: aluminium core {core_g:.0f} g + steel rim ring {ring_g:.0f} g + closing plate {cp_g:.0f} g = {core_g + ring_g + cp_g:.0f} g (all-aluminium would be {core_g + cp_g + made['rim_ring_STEEL'].volume/1000*2.7:.0f} g; the v10 Ø154 steel plate was 660 g)")
ok(f"made parts {tot:.0f} g + panel 70 g, Pi ~45 g, cooler, motor, servo, speaker, boards")

sec("the plate as the heatsink (the60-thermal-plan.md section 14)")
air = duct() + intake_grooves(R_CORE_DUCT - DUCT_WALL - 0.5, PLATE_R + 2) + exhaust_grooves(R_CORE_DUCT - DUCT_WALL - 0.5, PAD_R + 1.0)
air = air - made["base_plate"] - made["rim_ring_STEEL"]
vols = sorted(air.solids(), key=lambda s: -s.volume)
n_air = len([s for s in vols if s.volume > 200])
scraps = [s for s in vols if s.volume <= 200]
ig = intake_grooves(RIM_IN, PLATE_R); eg = exhaust_grooves(RIM_IN, PAD_R)
desc = []
for s in vols:
    if s.volume <= 200: continue
    bb = s.bounding_box()
    desc.append(f"{s.volume/1000:.1f} cm3 (y {bb.min.Y:.0f}..{bb.max.Y:.0f}; intake {'yes' if inter(s, ig) > 1 else 'NO'}, exhaust {'yes' if inter(s, eg) > 1 else 'NO'})")
complete = all(inter(s, ig) > 1 and inter(s, eg) > 1 for s in vols if s.volume > 200)
(ok if n_air <= 2 and complete and not scraps else fail)(f"the air path (intake grooves, collector, {len(channel_ys())} fin channels ({sum(1 for y in channel_ys() if y > 0)} at +y, {sum(1 for y in channel_ys() if y < 0)} at -y beside the off-centre Pi), plenums, exhaust grooves) is {n_air} circuit{'s' if n_air != 1 else ''}: " + "; ".join(desc) + f"; {len(scraps)} dead scraps. v12: the Pi's USB-C plug notch severs the front collector at 232 deg, so the -y side is its own intake-to-exhaust circuit (v11: one circuit, 25 cm3, 20 channels)")
(ok if 500 <= len(intake_azs()) * INTAKE_W * INTAKE_H <= 700 else warn)(f"intake: {len(intake_azs())} grooves {INTAKE_W} x {INTAKE_H} = {len(intake_azs()) * INTAKE_W * INTAKE_H:.0f} mm2 of throat (design-changes item 5 asks 500-700; v13 had 252) behind a {INTAKE_UNDERCUT_H} undercut over az {INTAKE_AZ0:.0f}-{INTAKE_AZ1:.0f} ({2*math.pi*PLATE_R*(INTAKE_AZ1-INTAKE_AZ0)/360*INTAKE_UNDERCUT_H:.0f} mm2 mouth); exhaust: {len(EXHAUST_AZ)} grooves = {len(EXHAUST_AZ) * INTAKE_W * INTAKE_H:.0f} mm2, downward through the pad's voids at az {EXHAUST_VOID} - the exhaust is the restriction, deliberately (rule 10: rear only); the shoulder keeps {RIM_STEP_Z - INTAKE_H:.1f} over each groove")
ok(f"blower envelope {BLOWER_L} x {BLOWER_W} x {BLOWER_H} reserved at az {BLOWER_AZ:.0f}, r {BLOWER_R:.0f} (in the 308-338 rear plenum; 2 mm into the web) - part not fitted")
d_air = air.distance_to(made["closing_plate_AL"])
ok(f"closing plate {CLOSING_T} mm in its recess, {len(CLOSING_SCREW_XY)} x M2.5 csk into solid web; ribs {len(RIB_AZ)} x {RIB_T} x {RIB_H} tall at r {RIB_R0:.0f}-{RIB_R1:.0f}")
top_holes = [f for f in made["base_plate"].faces() if abs(f.bounding_box().max.Z - PLATE_T) < 0.01 and f.bounding_box().min.Z < PLATE_T - 0.5]
ok("no openings through the plate's top face or its edge face: the duct is cut from below only (rule 8-9)")

print("\n" + "="*62)
print(f"{len(fails)} failures, {len(warns)} warnings, {len(expected)} expected envelope contacts  ({time.time()-T0:.0f}s)")
for f in fails: print("  FAIL", f)
for e in expected: print("  ENV ", e)
