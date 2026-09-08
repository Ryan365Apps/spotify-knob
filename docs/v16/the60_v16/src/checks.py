"""v15 automated checks: solidity, pairwise interference across EVERY body (made and bought)
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
        (lambda: "pad" in s and has("base_plate", "rim_ring_STEEL", "closing_plate_AL", "carriage", "port_face", "barrel_board", "pi_pcb") or ("pad" in s and anyp("pi_")), "stands on the pad"),
        (lambda: has("base_plate", "rim_ring_STEEL", "closing_plate_AL") and has("internal_structure", "speaker_cradle", "port_face", "halo_diffuser", "halo_liner", "converter_gap_pad_ASSUMED", "servo_mount", "connect_bracket", "wheel_block"), "stands on the plate (the block slides on it)"),
        # v16: the wheels
        (lambda: any(x.startswith("wheel") and "_pin_" in x for x in s) and (any(x.startswith("wheel") and "V623ZZ" in x for x in s) or has("internal_structure", "wheel_block") or any("washer" in x for x in s)), "the Ø3 pin: pressed in its post or block, the bearing's inner ring and the washer on it"),
        (lambda: any("washer_M3" in x for x in s) and (has("internal_structure") or any("V623ZZ" in x for x in s)), "the washer between the post's top and the inner ring"),
        (lambda: has("block_spring_ASSUMED") and has("wheel_block", "internal_structure", "block_release_screw_M2x18"), "the spring in the block's pocket, against the channel's end wall, round the release screw"),
        (lambda: has("block_release_screw_M2x18") and has("wheel_block", "internal_structure", "block_nut_M2"), "the captive release screw through the block's hole into its nut; its head on the end wall"),
        (lambda: has("block_nut_M2") and has("wheel_block"), "the nut in the block's slot"),
        (lambda: has("drive_collar") and (any("ENVELOPE" in x and x.startswith("motor") for x in s) or has("motor_band")), "the drive collar pressed on the bell's top; the band on the collar"),
        (lambda: has("mt6701_module_ENVELOPE") and (has("carriage") or anyp("mt6701") or anyp("motor")), "the sensor module in the carriage's pocket, its chip on it, under the magnet"),
        # v16: the boards' studs, spacers and nuts
        (lambda: any("_stud_" in x for x in s) and (any("_nut_" in x for x in s) or has("closing_plate_AL", "converter_D24V90F5_ENVELOPE") or any("_spacer_" in x for x in s)), "the csk stud: its head in the closing plate's countersink, through the spacer, the nut on it; through the converter's envelope (its holes are not drawn)"),
        (lambda: any("_spacer_" in x for x in s) and (has("base_plate", "audio_board", "bob_board", "drv_board", "ls_board", "mcu_tray") or any("_nut_" in x for x in s)), "the printed spacer between the plate (or the audio's nut) and the board (or the tray)"),
        (lambda: any("_nut_" in x for x in s) and has("audio_board", "bob_board", "drv_board", "ls_board", "tray_keeper", "converter_D24V90F5_ENVELOPE"), "the nut on the board / the keeper"),
        (lambda: has("mcu_tray") and (has("tray_keeper") or "ENVELOPE" in a and a.startswith(("mcu_", "level_shifter")) or "ENVELOPE" in b and b.startswith(("mcu_", "level_shifter"))), "the boards in the tray's pockets under the keeper"),
        (lambda: has("tray_keeper") and (a.startswith(("mcu_", "level_shifter")) or b.startswith(("mcu_", "level_shifter"))), "the keeper's rails on the boards' edges"),
        (lambda: a.startswith("mcu_") and b.startswith("mcu_") or a.startswith("level_shifter") and b.startswith("level_shifter"), "parts on their board"),
        (lambda: (anyp("tmc6300") or anyp("bob_")) and (has("bob_board") or has("bob_parts_ENVELOPE")), "on the driver breakout (the chip inside its parts envelope)"),
        (lambda: (anyp("level_shifter") or anyp("ls_")) and (has("ls_board") or anyp("ls_")), "on the level-shifter breakout"),
        (lambda: (anyp("drv2605l") or anyp("drv_parts")) and (has("drv_board") or has("drv_parts_ENVELOPE")), "on the haptic breakout (the chip inside its parts envelope)"),
        (lambda: has("led_strip_ENVELOPE") and has("internal_structure"), "the strip stuck face-down to the ledge's underside"),
        (lambda: has("halo_liner") and has("internal_structure", "halo_diffuser"), "the liner's wall against the structure's wall; its floor to the diffuser's foot"),
        (lambda: has("diffuser_gasket_ASSUMED") and has("halo_diffuser", "internal_structure"), "the gasket between the diffuser's top face and the lip"),
        (lambda: anyp("light_board") and has("port_face") or anyp("light_board") and anyp("light_board") or anyp("veml7700") and anyp("light_board"), "the breakout in the face's slot holder; its parts and sensor on it"),
        (lambda: anyp("jack_panel") and (anyp("jack_panel") or has("port_face")), "the panel jack's bushing through the face's hole, its nut on the face, its body behind"),
        (lambda: anyp("lra_pogo") and anyp("lra_pogo"), "the spring-pin block on its carrier, its pins in it"),
        (lambda: "connect_bracket" in s and "port_face" in s, "the bracket's outer end rests on the port face's rail"),
        (lambda: anyp("servo_body") and has("base_plate"), "the servo lies on the plate inside its frame"),
        (lambda: anyp("pi_washer") and has("closing_plate_AL", "pi_pcb"), "the Pi on its washers on the closing plate's lands"),
        (lambda: anyp("pi_standoff") and has("pi_pcb", "adapter_board"), "standoffs between the Pi and the adapter"),
        (lambda: anyp("touch_standoff") and has("adapter_board", "touch_board_ASSUMED", "adapter_parts_ENVELOPE"), "touch controller's standoffs on the adapter (through its ASSUMED parts envelope)"),
        (lambda: (anyp("cb_") and has("connect_board")) or ("connect_board" in s and "connect_bracket" in s), "connect board's parts on it; the board on the bracket's bosses"),
        (lambda: anyp("cable_") and (anyp("cable_") or has("cb_cn1_cable", "adapter_flex_connector")), "the flat cable's segments; its ends in the two connectors"),
        (lambda: has("panel_flex_6") and has("cb_cn2_panel_flex"), "panel flex into the connect board's CN2"),
        (lambda: a in ("base_plate", "rim_ring_STEEL", "closing_plate_AL") and b in ("base_plate", "rim_ring_STEEL", "closing_plate_AL"), "the plate's three bodies: the ring's flange in the core's rebate, the closing plate in its recess"),
        (lambda: has("converter_gap_pad_ASSUMED") and has("converter_D24V90F5_ENVELOPE"), "converter on its gap pad"),
        (lambda: "halo_diffuser" in s and "internal_structure" in s, "the diffuser's flange under the structure's lip"),
        (lambda: any("ENVELOPE" in x and x.startswith("motor") for x in s) and has("carriage", "motor_band"), "motor on its shoe / band on the bell"),
        (lambda: "speaker" in s and "speaker_cradle" in s, "flange in the cradle"),
        (lambda: any(x.startswith("encoder_") and x != "encoder_board" for x in s) and has("encoder_board"), "encoder and its screw heads on its board"),
        (lambda: has("encoder_board") and has("encoder_shim"), "encoder board on its shim"),
        (lambda: has("encoder_shim") and has("internal_structure"), "the shim on the seat flange"),
        (lambda: anyp("locating_pin") and has("internal_structure"), "dowel pin pressed in the flange's hole and its boss"),
        # v15: the blower unit
        (lambda: has("blower_BFB0305HA-C") and has("blower_inlet_gasket_ASSUMED", "blower_saddle") or anyp("blower_screw") and (has("blower_BFB0305HA-C", "blower_saddle", "base_plate", "blower_inlet_gasket_ASSUMED")), "the blower on its gasket under the saddle, the two M2 through the saddle, blower and gasket into the piers"),
        (lambda: has("blower_inlet_gasket_ASSUMED") and has("base_plate"), "the inlet gasket on the plate top"),
        (lambda: has("hood_gasket_ASSUMED") and has("base_plate", "rim_ring_STEEL", "blower_saddle", "hood_lid"), "the hood's gasket between the saddle / lid and the plate / ring"),
        (lambda: has("hood_lid") and has("rim_ring_STEEL"), "the lid's screws' spot faces on the ring (0.3 gasket)"),
        (lambda: has("fan_lead_housing_JST_SH_4") and has("pi_pcb", "pi_part_13_3x6x4.2"), "the fan lead's housing mated on the Pi's fan connector (pi_part_13 in the vendor STEP)"),
        (lambda: has("fan_lead_5") and has("pi_part_13_3x6x4.2"), "the lead entering its housing on the connector"),
        (lambda: a.startswith("fan_lead") and b.startswith("fan_lead"), "the fan lead's segments join"),
        (lambda: anyp("fan_lead") and has("base_plate", "blower_BFB0305HA-C", "pi_pcb"), "the fan lead: down the blower's corner, along the plate top, onto the Pi"),
        (lambda: anyp("locating_pin") and has("panel_glass"), "the pin's surface 0.15 from the glass disc's edge (the vendor outline is faceted there)"),
        (lambda: anyp("closing_gasket") and has("base_plate", "closing_plate_AL"), "the closing plate's gasket in its groove"),
        (lambda: (anyp("halo_tail") or anyp("halo_feed2")) and (anyp("halo_tail") or anyp("halo_feed2") or has("led_strip_ENVELOPE", "base_plate", "halo_liner", "ls_board", "level_shifter_parts_ENVELOPE", "converter_D24V90F5_ENVELOPE", "internal_structure")), "the halo's tail and far-end feed: from the strip, through the wall's notches and the liner, along the plate, onto the level shifter / to the converter"),
        (lambda: has("encoder_reflective_gap_2mm_typ") and has("knob_body"), "the sensor's 2 mm reflective gap ends at the code ring's face"),
        # v14: grounding features and the two homeless items
        (lambda: has("knob_bleed_leaf_ASSUMED") and has("knob_body", "internal_structure", "knob_bleed_screw"), "the bleed leaf bears on the crown, its foot flat on the flange, under its screw"),
        (lambda: anyp("chassis_bond") and (anyp("chassis_bond") or has("base_plate")), "the chassis bond's washer, terminal and screw stack on the plate"),
        (lambda: anyp("ring_bond") and (anyp("ring_bond") or has("rim_ring_STEEL", "base_plate")), "the rim ring's bond screw through its flange into the core, star washer on the flange"),
        (lambda: anyp("usbc_shell_wire") and (anyp("usbc_shell_wire") or anyp("usbc_") or anyp("chassis_bond") or has("usbc_board")), "the USB-C shell wire: from the receptacle to the chassis bond's terminal"),
        (lambda: anyp("motor_bond_wire") and (anyp("motor_bond_wire") or anyp("motor") or has("carriage", "base_plate")), "the motor frame's bond lead: under a base screw, up out of the tab slot, along the plate (then a harness lead to the driver breakout)"),
        (lambda: anyp("sensor_cable") and (anyp("sensor_cable") or has("carriage", "mt6701_module_ENVELOPE", "servo_mount", "base_plate")), "the rotor sensor lead: out of the carriage's notch, up beside the tab, its loop over the servo frame (then a harness lead to the tray)"),
        (lambda: anyp("lra_pogo") and (anyp("lra_pogo") or anyp("lra_") or has("internal_structure")), "the pogo board in its clip, its pins on the LRA's pads"),
        (lambda: has("audio_usb_plug_ENVELOPE") and has("audio_board"), "USB plug on the audio board's edge"),
        (lambda: anyp("lra_") and "internal_structure" in s, "LRA bonded to its pad"),
        (lambda: any(x.startswith("usbc_") and x != "usbc_board" for x in s) and has("usbc_board", "port_face"), "receptacle in its notch and opening"),
        (lambda: "barrel_jack_ENVELOPE" in s and has("barrel_board", "port_face"), "jack on its vertical board, bushing at the face"),
        (lambda: anyp("es9219q") and "audio_board" in s, "DAC on the audio board"),
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
        (lambda: a.startswith("pi_") and b.startswith("pi_") and not (a.startswith("pi_standoff") or b.startswith("pi_standoff") or a.startswith("pi_washer") or b.startswith("pi_washer")), "vendor assembly internals"),
        (lambda: anyp("cooler_") and (anyp("pi_") or anyp("cooler_")), "cooler on the Pi (heatsink pads on the SoC)"),
        (lambda: has("hdmi_plug_micro_ENVELOPE") and (has("pi_hdmi0_ENVELOPE", "pi_hdmi1_ENVELOPE", "pi_pcb") or has("hdmi_ribbon_1")), "ribbon plug in the micro-HDMI"),
        (lambda: anyp("hdmi_ribbon") and (anyp("hdmi_ribbon") or anyp("hdmi_plug")), "ribbon segments and plugs"),
        (lambda: has("hdmi_plug_A_ENVELOPE") and has("adapter_hdmi_socket"), "HDMI-A plug in the adapter's socket"),
        (lambda: has("header_housing_ENVELOPE") and (has("pi_header", "pi_pcb")), "housing on the header"),
        (lambda: has("usba_plug_ENVELOPE") and anyp("pi_usba"), "plug in the USB-A socket"),
        (lambda: has("converter_D24V90F5_ENVELOPE") and has("base_plate"), "converter on the plate"),
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
moving = lambda k: (k in ("carriage", "drive_collar", "internal_structure", "base_plate", "rim_ring_STEEL", "closing_plate_AL", "servo_mount", "knob_body", "halo_diffuser", "halo_liner", "led_strip_ENVELOPE", "pad", "bob_board", "drv_board", "audio_board", "mcu_tray")
                    or k.startswith("motor") or k.startswith("servo") or k.startswith("mt6701") or k.startswith("pi_") or k.startswith("hdmi") or k.startswith("header") or k.startswith("cooler") or k.startswith("halo_tail") or k.startswith("sensor_cable"))
pairwise({k: v for k, v in {**made_off, **bought_off}.items() if moving(k)}, "released")

sec("clutch")
knob = made["knob_body"]
d_on = knob.distance_to(made["drive_collar"]); d_off = knob.distance_to(made_off["drive_collar"]); d_band_off = knob.distance_to(bought_off["motor_band"])
ok(f"drive collar (Ø{DRIVE_COLLAR_OD} on the bell's top {DRIVE_COLLAR_H}) to the bore, engaged {d_on:.2f} mm (band {MOTOR_BAND_T} thick, so it presses); the bell itself reaches r {MOTOR_R + MOTOR_OD/2:.1f}, inside the wall's outer face ({R_WALL_OUT})")
(ok if d_band_off >= 0.8 else fail)(f"band to bore, released {d_band_off:.2f} mm (>= 0.8); collar {d_off:.2f}")
d_bell_liner = bought_on["motor_motor_ENVELOPE"].distance_to(made["halo_liner"]); d_bell_ledge = bought_on["motor_motor_ENVELOPE"].distance_to(made["internal_structure"])
(ok if d_bell_liner >= 0.3 else fail)(f"the bell passes through the wall's window inside the halo channel's liner: {d_bell_liner:.2f} mm to the liner's wall, {d_bell_ledge:.2f} to the structure (the ledge's inner edge)")
d_tab = made["carriage"].distance_to(bought_on["servo_body_ENVELOPE"] if "servo_body_ENVELOPE" in bought_on else list(v for k, v in bought_on.items() if k.startswith("servo_body"))[0])
ok(f"servo on the plate: body to the tab {d_tab:.2f} mm (the pushrod bridges it); tab to z {CARRIAGE_TAB_TOP} (v11: 28.5 through the deck); lift {CLUTCH_LIFT} mm, {MOTOR_PRELOAD_N} N")

sec("knob rotation")
statics = [(n, s) for n, s in {**made, **bought_on}.items() if n not in ("knob_body", "motor_band") and "V623ZZ" not in n]
for ang in (0.0, 17.0, 45.0, 73.0):
    k = Rot(0, 0, ang) * knob
    for n, s in statics:
        v = inter(k, s)
        if v > 0.05: fail(f"knob at {ang} deg x {n}: {v:.2f} mm3")
if not any("knob at" in f for f in fails): ok("knob clear of every static part at 0/17/45/73 deg")
for n in ("panel_glass", "lens_ASSUMED", "internal_structure", "halo_diffuser", "halo_liner", "diffuser_gasket_ASSUMED", "wheel_block"):
    d = knob.distance_to({**made, **bought_on}[n])
    (ok if d >= GAP_ROTATE - 0.02 else fail)(f"knob to {n}: {d:.2f} mm (>= {GAP_ROTATE})")
sec("the V-ridge in the three V-groove bearings")
for az in WHEEL_AZ:
    w = bought_on[f"wheel{az}_V623ZZ_ASSUMED"]
    v = inter(knob, w); d = knob.distance_to(w)
    (ok if v < 0.05 and d < 0.03 else fail)(f"wheel {az}: the ridge's flanks on the V's flanks - contact {d:.3f} mm, overlap {v:.2f} mm3 (the crest {RIDGE_CLEAR} inside the root; the rims reach r {WHEEL_REACH:.1f}, {R_RELIEF - WHEEL_REACH:.1f} inside the relief band)")
    rmax = max(math.hypot(p.X, p.Y) for p in w.vertices())
    (ok if rmax < R_RELIEF - 0.15 else fail)(f"wheel {az}: rims to r {rmax:.2f} vs the relief band r {R_RELIEF} and the bore r {R_BORE} (the rims never touch the bore)")
ok(f"ridge: crest r {R_CREST} x {RIDGE_CREST_W} flat, base r {R_RELIEF} x {RIDGE_BASE_W}, 90 deg flanks, z {Z_RIDGE0:.1f}-{Z_RIDGE1:.1f}; bearings V623ZZ class {WHEEL_OD} x {WHEEL_W}, V {WHEEL_V_D} deep (ASSUMED) at r {WHEEL_AXIS_R:.1f}, z {Z_WHEEL0}-{Z_WHEEL1}")
(ok if WHEEL_V_D <= 1.5 else warn)(f"the ridge is derived from the bearing's V (depth, root flat): when Ryan's listing is measured, WHEEL_V_D / WHEEL_V_ROOT_FLAT change and everything follows - question 36")

sec("stack and containment")
for n, s in {**made, **bought_on}.items():
    bb = s.bounding_box()
    if bb.max.Z > Z_KNOB_TOP + 0.01: fail(f"{n} above the knob top: {bb.max.Z:.2f}")
    if bb.min.Z < -PAD_T - 0.01: fail(f"{n} below the pad: {bb.min.Z:.2f}")
    r = max(abs(bb.min.X), bb.max.X, abs(bb.min.Y), bb.max.Y)
    lim = R_DIFF_OUT if n in ("rim_ring_STEEL", "halo_diffuser") else R_KNOB
    if r > lim + 0.01 and "plug" not in n: fail(f"{n} outside Ø{2*lim:.0f}: max Ø{2*r:.1f}")
ok(f"height {HEIGHT:.1f} mm incl. pad (no limit; the v10 spec estimated 41.7 before the glue ruling); knob {KNOB_FRACTION*100:.0f} % of the visible side")
(ok if KNOB_FRACTION >= 0.5 else fail)("knob is the majority of the visible side")
display = ("panel_glass", "lens_ASSUMED", "panel_components_ENVELOPE", "bond_tape", "knob_body", "internal_structure", "halo_diffuser", "encoder_board")   # the encoder is above the seat now
tallest = []
for n, s in {**made, **bought_on}.items():
    if n in display or n.startswith("panel_flex") or n.startswith("touch_tail") or n.startswith("wheel") or n.startswith("locating_pin") or n.startswith("encoder_") or n.startswith("knob_bleed"): continue
    z = s.bounding_box().max.Z
    tallest.append((z, n))
    if z > Z_SEAT_BOT - 0.15 + 0.01: fail(f"{n} reaches z {z:.2f}: under the seat's underside {Z_SEAT_BOT} it must stay below {Z_SEAT_BOT - 0.15:.2f}")
tallest.sort(reverse=True)
ok("under the seat (highest first): " + ", ".join(f"{n} {z:.1f}" for z, n in tallest[:6]))
ok(f"seat floor: the bearings over the drive band allow {Z_SEAT_WHEELS:.1f}; the adapter's HDMI socket ({Z_ADAPTER_HDMI_TOP:.2f}) needs {Z_ADAPTER_HDMI_TOP + 0.3 + 2.0:.1f}; seat top {Z_SEAT_TOP}")
ok(f"adapter underside {Z_ADAPTER0:.2f}: {Z_ADAPTER0 - ADAPTER_UNDER_H - Z_HEATSINK_TOP:.1f} mm over the heatsink's fins (with {ADAPTER_UNDER_H} of underside parts), {Z_ADAPTER0 - (Z_PLATE_TOP + SERVO_H + 0.5):.2f} over the servo's frame, {Z_ADAPTER0 - Z_PI_USBA_TOP:.1f} below the USB-A shells' top (it does not reach them: adapter x to {ADAPTER_X0 + ADAPTER_L:.0f}, shells from {PI_X0 + 66.6:.0f})")
ok(f"drive band on the bore z {max(Z_DRIVE0, Z_SKIRT_BOT):.1f}-{Z_DRIVE1:.1f}; ridge {Z_RIDGE0:.1f}-{Z_RIDGE1:.1f}; seat {Z_SEAT_TOP}; glass {Z_GLASS0:.2f}-{Z_GLASS1:.2f}; lens top {Z_LENS1:.2f}; crown underside {Z_CROWN_BOT:.2f} with the code ring's face at {Z_CODE_FACE:.2f}; knob top {Z_KNOB_TOP:.2f} (v12 36.38, v11 39.18)")
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
sec(f"assembly of the knob (v16): the block wound in {BLOCK_TRAVEL_IN} by its release screw, the knob dropped on {KNOB_FIT_OFFSET} off-centre toward az 90 (the fixed wheels' bisector), then slid to centre and the block let go")
made_pk = made_parts(knurl=False, engaged=True, block="parked"); bought_pk = bought_parts(engaged=True, block="parked")
ox, oy = KNOB_FIT_OFFSET * math.cos(math.radians(90.0)), KNOB_FIT_OFFSET * math.sin(math.radians(90.0))
blocked = []
fitted = {k: v for k, v in {**made_pk, **bought_pk}.items() if k not in ("knob_body", "motor_band") and not k.startswith("panel") and not k.startswith("lens") and k != "bond_tape" and not k.startswith("touch_tail") and k != "encoder_board" and not k.startswith("encoder_") and not k.startswith("locating_pin") and not k.startswith("knob_bleed") and k != "encoder_shim"}
for dz in (30.0, 12.0, 4.5, 2.0, 0.0):
    k = Pos(ox, oy, dz) * knob
    for n, sh in fitted.items():
        v = inter(k, sh)
        if v > 0.05: blocked.append(f"at +{dz:.0f}: {n} {v:.1f} mm3")
(ok if not blocked else fail)(f"the knob, offset {KNOB_FIT_OFFSET} toward az 90 with the block parked, descends to its final height clear of everything (the ridge passes outside the fixed wheels' rims; the far side clears the upper wall, the ramp and the parked wheel): " + ("clear" if not blocked else "; ".join(blocked[:8])))
blocked = []
for f in (0.75, 0.5, 0.25):
    k = Pos(ox * f, oy * f, 0) * knob
    for n, sh in fitted.items():
        v = inter(k, sh)
        if v > 0.05: blocked.append(f"at {f*KNOB_FIT_OFFSET:.1f} off: {n} {v:.1f} mm3")
(ok if not blocked else fail)("... and slides back to centre at its final height, the ridge entering the fixed wheels' grooves flank on flank: " + ("clear" if not blocked else "; ".join(blocked[:8])))
w_pk = bought_pk[f"wheel{WHEEL_SPRUNG_AZ}_V623ZZ_ASSUMED"]; rmax_pk = max(math.hypot(p.X, p.Y) for p in w_pk.vertices())
(ok if rmax_pk <= R_CREST - KNOB_FIT_OFFSET - 0.3 else fail)(f"the parked wheel reaches r {rmax_pk:.1f}: {R_CREST - KNOB_FIT_OFFSET - rmax_pk:.1f} inside the offset knob's far-side crest ({R_CREST - KNOB_FIT_OFFSET:.1f})")
v = inter(made_pk["wheel_block"], made_pk["internal_structure"]) + inter(made["wheel_block"], made["internal_structure"])
(ok if v < 0.05 else fail)(f"the block clears its channel's walls and roof in both positions ({v:.2f} mm3); travel {BLOCK_TRAVEL_IN} in / {BLOCK_TRAVEL_OUT} out, the pin's slot in the roof is the stop")
# the release screw's lane: an L-shaped 1.5 mm hex key from the display opening - its short leg on the screw's axis, its long leg rising at r 46 inside the crown's inner edge (64.2)
az = WHEEL_SPRUNG_AZ
lane = rbore(4.0, 44.0, CHANNEL_END_R0 - 1.4, az, RELEASE_SCREW_Z) + zbore(4.0, RELEASE_SCREW_Z - 2.0, Z_KNOB_TOP + 5, az, 44.0)
hit = [f"{n} {inter(lane, sh):.1f}" for n, sh in {**made, **bought_on}.items() if n not in ("knob_body", "panel_glass", "lens_ASSUMED", "panel_components_ENVELOPE", "bond_tape", "block_release_screw_M2x18") and not n.startswith("panel_flex") and not n.startswith("touch_tail") and inter(lane, sh) > 0.05]
(ok if not hit else fail)("the release screw is reached with an L-key through the display opening before the display goes in (a Ø4 lane: radial at z 10.5 from r 44 to the head, vertical at r 44, az 270): " + ("clear" if not hit else "blocked by " + ", ".join(hit)))
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
sec("the boards on countersunk M2 studs from below (v16, Ryan's rule): every stud on a full-depth island, spacer, nut above")
studs = stud_xy()
bad = []
for (x, y) in studs:
    ring = Pos(x, y, CLOSING_T + 0.3) * (Cylinder(3.0, DUCT_H - 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(1.3, 20))   # the island round the hole, through the duct's height (Ø6 of the Ø7)
    if inter(ring, made["base_plate"]) < 0.98 * ring.volume: bad.append(f"({x:.1f}, {y:.1f})")
    if math.hypot(x, y) > R_CORE_DUCT - 1.0: bad.append(f"({x:.1f}, {y:.1f}) beyond the core")
(ok if not bad else fail)(f"{len(studs)} studs (audio 4, driver breakout 2, haptic breakout 2, level shifter 2, converter 2): each rises through a solid Ø7 island in the duct (the channels are cross-linked round them), head Ø{STUD_HEAD_D} flush in the closing plate's underside (0.2 proud), {SPACER_H} printed spacer, nut above" + ("" if not bad else " - NOT at " + ", ".join(bad)))
for n in ("audio_board", "bob_board", "drv_board", "ls_board"):
    hs = [k for k in bought_on if k.startswith(n.split('_')[0] + "_stud")]
    d = min(bought_on[k].distance_to(made[n]) for k in hs)
    ok(f"{n}: {len(hs)} studs pass its Ø{STUD_HOLE_D} holes (nearest {d:.2f} mm), z {made[n].bounding_box().min.Z:.1f}-{made[n].bounding_box().max.Z:.1f}")
for n in ("bob_board", "drv_board", "ls_board", "audio_board", "mcu_tray"):
    others = {k: v for k, v in {**made, **bought_on}.items() if not k.startswith(n.split('_')[0]) and k not in ("base_plate", "internal_structure") and not "_stud_" in k and not "_nut_" in k and not "_spacer_" in k and not k.startswith("halo_tail") and not k.startswith("tray_") and not k.startswith("mcu_") and not k.startswith("level_shifter") and not k.startswith("audio") and not k.startswith("es9219")}
    dd = sorted((made[n].distance_to(v), k) for k, v in others.items())[:3]
    dw = made[n].distance_to(made["internal_structure"])
    ok(f"{n} clearances: " + ", ".join(f"{k} {d:.1f}" for d, k in dd) + f"; to the structure {dw:.1f}")
sec("the printed parts that keep M2.5 screws into the plate's top: blind tapped holes stop in the web + pier")
holes = top_screw_xy()
(ok if BLIND_D <= WEB_T + PIER_H - 1.0 else fail)(f"{len(holes)} x M2.5 (servo frame, connect bracket, speaker cradle) + 2 x M2 (blower) + 1 x M3 (chassis bond) blind holes {BLIND_D} deep from the top face: {WEB_T} of web + {PIER_H} of pier = {WEB_T + PIER_H} of metal, {WEB_T + PIER_H - BLIND_D:.1f} of floor left, {DUCT_H - PIER_H:.1f} of duct under each pier")
holes = holes + blower_screw_xy() + [GND_BOND_XY]
for (x, y) in holes:
    r = math.hypot(x, y)
    if r > R_CORE_DUCT - 1.0: fail(f"top screw at ({x:.1f}, {y:.1f}) r {r:.1f}: beyond the aluminium core ({R_CORE_DUCT})")
hit = []
for (x, y) in holes:
    probe = Pos(x, y, PLATE_T - BLIND_D - 0.2) * Cylinder(1.0, BLIND_D + 0.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    v = inter(probe, made["base_plate"])
    if v < 0.05: hit.append(f"({x:.1f}, {y:.1f})")
(ok if not hit else fail)("every top screw's hole is in the plate (not over a window): " + ("yes" if not hit else "missing at " + ", ".join(hit)))
missing = []
for (x, y) in holes:
    probe = Pos(x, y, PLATE_T - BLIND_D - 0.9) * Cylinder(1.0, 0.8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if inter(probe, made["base_plate"]) < 0.5 * probe.volume: missing.append(f"({x:.1f}, {y:.1f})")
(ok if not missing else fail)("a floor of metal under every blind hole (the pier is there): " + ("yes" if not missing else "missing at " + ", ".join(missing)))
sec("cables against the mechanism, both clutch states")
cables = [n for n in bought_on if n.startswith("hdmi_") or n.startswith("panel_flex") or n.startswith("touch_tail") or n.startswith("header_housing") or n.startswith("usba_plug") or n.startswith("cable_") or n.startswith("halo_")]
mech_on = {k: v for k, v in {**made, **bought_on}.items() if k in ("carriage", "motor_band", "drive_collar", "wheel_block") or k.startswith("motor") or k.startswith("wheel")}
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
ok(f"halo (HALO-OPTICS, v16): the {LED_STRIP_W} mm strip face DOWN under the ledge at r {R_STRIP_IN:.1f}-{R_STRIP_OUT:.1f}, emitting face z {Z_STRIP0}, firing at the white liner's floor {HALO_THROW:.1f} below in a {CHANNEL_W:.1f}-wide channel (r {R_WALL_OUT:.1f}-{R_DIFF_IN:.1f}); the opal ring r {R_DIFF_IN:.1f}-{R_DIFF_OUT:.1f} ({DIFF_T} thick, z {Z_DIFF0}-{Z_DIFF1}) in the ring's 0.5 rebate, clamped by the lip through a {DIFF_GASKET_T} gasket; band Ø{2*R_DIFF_OUT:.1f}, {R_DIFF_OUT - R_KNOB:.1f} proud of the knob")
d_seat = made["halo_diffuser"].distance_to(made["rim_ring_STEEL"]); d_gap = made["halo_diffuser"].distance_to(bought_on["diffuser_gasket_ASSUMED"]); d_lip = made["halo_diffuser"].distance_to(made["internal_structure"])
(ok if d_seat < 0.02 and d_gap < 0.02 and abs(d_lip - 0.3) < 0.05 else fail)(f"the opal ring stands on the shelf ({d_seat:.2f}), under its gasket ({d_gap:.2f}), {d_lip:.2f} radial clearance to the ledge (HALO-OPTICS: 0.3 for PMMA's expansion, never an interference fit)")
d_strip_liner = bought_on["led_strip_ENVELOPE"].distance_to(made["halo_liner"]); d_strip_diff = bought_on["led_strip_ENVELOPE"].distance_to(made["halo_diffuser"])
(ok if d_strip_liner >= 0.5 and d_strip_diff >= 0.15 else fail)(f"the strip: {d_strip_liner:.2f} over the liner's wall, {d_strip_diff:.2f} to the opal ring; no LED in the diffuser's direct view (the ledge is between)")
ok(f"rim edge: {len(vent_azs())} obround openings {VENT_W} x {VENT_H} on 3 deg are the decoration (design-changes items 3 and 5), a plain upper land, {PLATE_CHAMFER} polished chamfers, the 0.8 shelf standing {PLATE_R_SHELF - PLATE_R:.1f} proud at z {Z_SHELF0}-{Z_DIFF0} ({Z_SHELF0 - (VENT_Z0 + VENT_H + VENT_CHAMFER):.2f} above the openings' chamfered tops: it does not shadow them); stainless, bare, brushed axially; plate Ø{2*PLATE_R:.0f} flush with the knob")
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
ok(f"halo: {LED_N} LEDs at {LED_PER_M}/m on the strip at r {(R_STRIP_IN + R_STRIP_OUT)/2:.1f} = {HALO_PEAK_A:.2f} A at full white ({HALO_PEAK_A*5:.1f} W) - the peak that sizes the converter and the halo feed; HALO-OPTICS: 60 or 120 on the bench (120 = 5.76 A); no sustained cap")
sec("mass")
rho = {"base_plate": 2.7, "rim_ring_STEEL": 7.9, "closing_plate_AL": 2.7, "halo_diffuser": 1.19}
tot = 0
for n, s in made.items():
    d = rho.get(n, 1.27); g = s.volume/1000*d; tot += g
    extra = f"  (Al {s.volume/1000*2.7:.0f} g)" if n == "knob_body" else (f"  (in Al {s.volume/1000*2.7:.0f} g)" if n == "rim_ring_STEEL" else "")
    if g > 1: print(f"  {n:20s} {g:7.1f} g{extra}")
core_g = made['base_plate'].volume/1000*2.7; ring_g = made['rim_ring_STEEL'].volume/1000*7.85; cp_g = made['closing_plate_AL'].volume/1000*2.7
ok(f"plate: aluminium core {core_g:.0f} g + stainless rim ring {ring_g:.0f} g + closing plate {cp_g:.0f} g = {core_g + ring_g + cp_g:.0f} g (all-aluminium would be {core_g + cp_g + made['rim_ring_STEEL'].volume/1000*2.7:.0f} g; the v10 Ø154 steel plate was 660 g; v14: core 42 + ring 198 + plate 9)")
ok(f"made parts {tot:.0f} g + panel 70 g, Pi ~45 g, cooler, motor, servo, speaker, boards")

sec("the plate as the heatsink (the60-thermal-plan.md section 14; v15: 2/5/1, the blower fitted, the ring's groove and openings)")
core_air = duct() + core_tunnels() + trench(CLOSING_T, PLATE_T + 1) + zbore(WEB_INLET_D, CLOSING_T + DUCT_H - 1, PLATE_T + 1, BLOWER_AZ, BLOWER_R)
ring_air = ring_groove() + ring_land_grooves()
air = (core_air + ring_air) - made["base_plate"] - made["rim_ring_STEEL"]
air = air & cyl(RING_WALL_R0 + 0.5, -0.5, PLATE_T + 0.5)          # inside the ring's outer wall (the openings are counted separately)
vols = sorted(air.solids(), key=lambda s: -s.volume)
n_air = len([s for s in vols if s.volume > 200])
scraps = [s for s in vols if s.volume <= 200]
ig = intake_grooves(RIM_IN, GROOVE_R0); eg = exhaust_grooves(RIM_IN, GROOVE_R0_EXH); tr = trench(CLOSING_T, PLATE_T)
inlet = zbore(WEB_INLET_D, PLATE_T - 1, PLATE_T + 1, BLOWER_AZ, BLOWER_R)
desc = []
for s in vols:
    if s.volume <= 200: continue
    bb = s.bounding_box()
    desc.append(f"{s.volume/1000:.1f} cm3 (y {bb.min.Y:.0f}..{bb.max.Y:.0f}; intake passages {'yes' if inter(s, ig) > 1 else 'NO'}, blower inlet {'yes' if inter(s, inlet) > 1 else 'NO'}, trench {'yes' if inter(s, tr) > 1 else 'NO'}, -y exhaust passages {'yes' if inter(s, eg) > 1 else 'NO'})")
plus = [s for s in vols if s.volume > 200 and inter(s, inlet) > 1]
disch = [s for s in vols if s.volume > 200 and inter(s, tr) > 1]
complete = (len(plus) == 1 and inter(plus[0], ig) > 1 and inter(plus[0], eg) > 1) and (len(disch) == 1 and inter(disch[0], inlet) < 1) and n_air == 2
(ok if complete and not scraps else fail)(f"the air: {n_air} bodies inside the ring's wall - " + "; ".join(desc) + f"; {len(scraps)} dead scraps. Expected two: the SUCTION network (the whole intake groove 60-300 and its {len(intake_azs())} passages, the collector, all {len(channel_ys())} channels, both plenums, the blower's inlet hole - the -y side's 300-342 openings and passages are pulled in reverse by the blower, so its {sum(1 for y in channel_ys() if y < 0)} channels see forced flow too) and the DISCHARGE (the trench and the 18-60 groove with its openings)")
va = vent_azs(); n_in = sum(1 for a, k in va if k == "intake"); n_ex = sum(1 for a, k in va if k == "exhaust")
a_open = VENT_W * VENT_H - (4 - math.pi) * (VENT_W/2)**2
under_in = sum(2*math.pi*(RING_WALL_R0 + 1.85)*(a1 - a0)/360*INTAKE_UNDERCUT_H for a0, a1, r0 in groove_arcs() if r0 == GROOVE_R0)
under_ex = sum(2*math.pi*(RING_WALL_R0 + 1.85)*(a1 - a0)/360*INTAKE_UNDERCUT_H for a0, a1 in EXHAUST_ARCS)
th_in = len(intake_azs()) * INTAKE_W * INTAKE_H
(ok if n_in * a_open >= 500 and th_in >= 500 else warn)(f"INTAKE: {n_in} openings {VENT_W} x {VENT_H} obround = {n_in * a_open:.0f} mm2 through the edge face over az {INTAKE_AZ0:.0f}-{INTAKE_AZ1:.0f} + the {INTAKE_UNDERCUT_H} undercut {under_in:.0f} mm2; behind them the groove r {GROOVE_R0}-{GROOVE_R1} x {GROOVE_Z1} and {len(intake_azs())} passages {INTAKE_W} x {INTAKE_H} = {th_in:.0f} mm2 of throat (target 500-700)")
th_ex_y = TRENCH_W * (PLATE_T - CLOSING_T); th_ex_my = len(EXHAUST_AZ) * EXHAUST_W * INTAKE_H
(ok if n_ex * a_open >= 200 else warn)(f"EXHAUST: {n_ex} openings = {n_ex * a_open:.0f} mm2 through the edge face on az {EXHAUST_ARCS} (item 4: at least 200 - what a desk mat cannot block) + the undercut {under_ex:.0f} mm2 downward/outward = {n_ex * a_open + under_ex:.0f} total (target about 400); throats: the +y trench {th_ex_y:.0f} mm2, the -y passages {th_ex_my:.0f} mm2; the exhaust groove is r {GROOVE_R0_EXH}-{GROOVE_R1} = {(GROOVE_R1 - GROOVE_R0_EXH) * GROOVE_Z1:.0f} mm2 in section")
ok(f"positions: {VENT_N} on {360/VENT_N:.0f} deg, az 1.5 + 3k, mirrored about 0-180 by construction; {VENT_N - n_in - n_ex} not cut (the port face 342-18, the carriage hole's arc {VENT_SKIP_ARCS[0]} and its mirror {VENT_SKIP_ARCS[1]}, and the 1 deg either side of the groove walls at 60 and 300) - no blind openings: every cut one has the groove behind it")
# nothing from outside reaches the cavity: every opening and the undercut must see ring material or the groove, never the carriage hole / cavity
leak = []
for az, kind in va:
    probe = polar(az, RING_WALL_R0 - 2.5, VENT_Z0 + VENT_H/2) * Box(0.4, 0.8, 0.8)
    if inter(probe, made["rim_ring_STEEL"]) < 0.01 and inter(probe, ring_groove()) < 0.01: leak.append(f"{az:.1f}")
(ok if not leak else fail)("no opening looks through into the carriage hole or the cavity (2.5 behind the wall is ring or groove)" + ("" if not leak else ": " + ", ".join(leak)))
blind = []
for az, kind in va:
    probe = polar(az, RING_WALL_R0 - 0.3, VENT_Z0 + VENT_H/2) * Box(0.4, 0.8, 0.8)
    if inter(probe, made["rim_ring_STEEL"]) > 0.01: blind.append(f"{az:.1f}")
(ok if not blind else fail)("every cut opening breaks into the groove behind it" + ("" if not blind else ": blind at " + ", ".join(blind)))
badf = []
voids = core_tunnels() + trench(CLOSING_T, PLATE_T)
for az in RING_SCREW_AZ:                                # the csk head (Ø6.5 -> 3.4 over 1.6) and the shank, 0.3 of metal round them
    probe = polar(az, RING_SCREW_R, 0.0) * Cone(3.55, 2.0, 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN)) + polar(az, RING_SCREW_R, 1.5) * Cylinder(2.0, RIM_STEP_Z - 1.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if inter(probe, voids) > 0.05: badf.append(f"ring screw {az}")
rvoids = trench(-1, PLATE_T + 1) + ring_groove() + ring_land_grooves()
for az in HOOD_SCREW_AZ:
    probe = polar(az, HOOD_SCREW_R, PLATE_T - 3.2) * Cylinder(1.4, 3.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if inter(probe, rvoids) > 0.05: badf.append(f"hood screw {az}")
probe = polar(RING_BOND_AZ, RING_BOND_R, 0.5) * Cylinder(2.2, RIM_STEP_Z - 0.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
if inter(probe, voids) > 0.05: badf.append("ring bond")
(ok if not badf else fail)(f"every ring fixing on a land: {len(RING_SCREW_AZ)} ring screws, the bond screw at {RING_BOND_AZ}, the hood's two" + ("" if not badf else " - NOT: " + ", ".join(badf)))
ok(f"fins: {len(channel_ys())} channels {FIN_CH_W} x {DUCT_H} on {FIN_PITCH}, finned full length (design-changes item 2 asked for fins over the compute module and converter only - neither sits over a channel: the Pi is in a window through the duct, the converter over the front collector)")
bl = bought_on["blower_BFB0305HA-C"]; bb = bl.bounding_box()
(ok if bb.max.Z <= Z_SEAT_BOT - 2.0 else fail)(f"blower {BLOWER_L} x {BLOWER_W} x {BLOWER_H} at az {BLOWER_AZ}, r {BLOWER_R}, z {bb.min.Z:.1f}-{bb.max.Z:.1f} on its {BLOWER_GASKET_T} gasket; saddle plate to {Z_BLOWER1 + SADDLE_T} (v16: a plain clamp plate, no board on it)")
hole = zbore(WEB_INLET_D, PLATE_T - 0.5, PLATE_T + 0.5, BLOWER_AZ, BLOWER_R)
(ok if inter(hole, made["base_plate"]) < 0.05 else fail)(f"the Ø{WEB_INLET_D} inlet hole through the web is open (inside the blower's Ø{BLOWER_INLET_D} inlet; the gasket ring OD 30 / ID 25 seats on metal all round)")
d_lid = made["hood_lid"].distance_to(made["internal_structure"])
(ok if d_lid >= 0.25 else fail)(f"the hood lid to the structure's wall / post webs: {d_lid:.2f} mm (a loose printed part on its gasket: 0.3 by design)")
ok("blower curve (datasheet P-Q): 0.68 L/s free, 71 Pa at no flow; through this duct (about 8 Pa fins + 3 intake + 7 trench and outlet + 5 groove and openings at 0.5 L/s, ~25 Pa) it lands near 0.5 L/s; air capacity 0.6 W/K, so with the passive 0.5 W/K about 1.0 W/K total: 13 W sustained = 13 K over room, 38 C skin at 25 C. Power 0.65 W, 29 dB(A) free-field")
ok(f"closing plate {CLOSING_T} mm in its recess on a {GASKET_T} gasket, {len(CLOSING_SCREW_XY)} x M2.5 csk + the {len(stud_xy())} board studs through it - free span about 30 mm; no ribs on the plate top (v16: deleted - the plate can be printed / machined flipped)")
ok("no openings through the plate's top face except the two under the hood (the blower's inlet hole and the trench), both sealed by the saddle's gaskets (rule 9: nothing open to the halo's light channel or the cavity)")
ok(f"deflection under knob load: NIL before and after - the knob rides on the wheels on the structure's wall (r {R_WALL_OUT_UP}), the structure stands on the plate at its wall foot and the pillars (r {PILLAR_R}), all inside the solid rim (r >= {RIM_IN}); the web carries the boards and the servo only (item 1's report-back)")
def f1(t, a):
    Dp = 70e9 * (t*1e-3)**3 / (12 * (1 - 0.33**2)); return 10.2 / (2*math.pi*(a*1e-3)**2) * math.sqrt(Dp / (2700 * t*1e-3))
ok(f"first drum mode (plain clamped disc, for the record): 2 mm web Ø{2*R_CORE_DUCT:.0f} about {f1(WEB_T, R_CORE_DUCT):.0f} Hz (the Pi window, fins and piers stiffen it well above that; v14's 4 mm web: {f1(4.0, R_CORE_DUCT):.0f} Hz); the 1 mm closing plate on a 30 mm free span about {f1(1.0, 15):.0f} Hz (on its v14 60 mm span: {f1(1.0, 30):.0f} Hz) - the fins bear on it every 4 mm through the gasket's preload")

print("\n" + "="*62)
print(f"{len(fails)} failures, {len(warns)} warnings, {len(expected)} expected envelope contacts  ({time.time()-T0:.0f}s)")
for f in fails: print("  FAIL", f)
for e in expected: print("  ENV ", e)
