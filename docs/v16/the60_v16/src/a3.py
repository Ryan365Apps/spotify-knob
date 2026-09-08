"""A3 technical drawings, one sheet per made part: plan (slices at three heights), front and side
sections through the part's centre, overall dimensions, a title block, notes and the part's key
dimensions from the parameter block.  Sheet 0 lists every ASSUMED number."""
import os, sys, math, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from model import *
from params import ASSUMED_LIST

made = made_parts(knurl=False)
DATE = "2026-09-08"
def slice_edges(shape, z):
    slab = Pos(0, 0, z) * Box(400, 400, 0.02)
    try: sec = shape & slab
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        n = max(8, min(200, int(e.length / 1.5)))
        pts = [e.position_at(t) for t in [i/n for i in range(n + 1)]]
        if abs(pts[0].Z - z) > 0.05: continue
        out.append([(p.X, p.Y) for p in pts])
    return out
def vsection(shape, axis, c):
    """edges of the part cut by the vertical plane x = c (axis 'x') or y = c (axis 'y')"""
    if axis == "x": plane = Pos(c, 0, 0) * Box(0.02, 400, 400)
    else: plane = Pos(0, c, 0) * Box(400, 0.02, 400)
    try: sec = shape & plane
    except Exception: return []
    if sec is None: return []
    out = []
    for e in sec.edges():
        n = max(8, min(200, int(e.length / 1.5)))
        pts = [e.position_at(t) for t in [i/n for i in range(n + 1)]]
        out.append([((p.Y if axis == "x" else p.X), p.Z) for p in pts])
    return out
def dim_h(ax, x0, x1, y, text, off=6):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.plot([x0, x0], [y - off*0.4, y + off*0.4], color="k", lw=0.5); ax.plot([x1, x1], [y - off*0.4, y + off*0.4], color="k", lw=0.5)
    ax.text((x0 + x1)/2, y + 1.0, text, ha="center", va="bottom", fontsize=7.5)
def dim_v(ax, x, y0, y1, text, off=6):
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.plot([x - off*0.4, x + off*0.4], [y0, y0], color="k", lw=0.5); ax.plot([x - off*0.4, x + off*0.4], [y1, y1], color="k", lw=0.5)
    ax.text(x + 1.0, (y0 + y1)/2, text, ha="left", va="center", fontsize=7.5, rotation=90)

SHEETS = [
    ("knob_body", "Knob", "PETG (prototype) / CNC 6082-T6, hard anodised (production)", "print top face down, 0.16 mm; no supports",
     [f"outside Ø{2*R_KNOB:.1f}, bore Ø{2*R_BORE:.1f} (0.45 to the panel's chin corners); wall {SKIRT_WALL:.1f}", f"top rim: lip inner edge Ø{2*R_CROWN_IN:.1f}, {CH_IN} inner chamfer, {RIM_FLAT:.0f} flat, {CH_TOP} outer chamfer (RULING 6 Sep: rim >= 20); lip 3.0 thick, top at z {Z_KNOB_TOP:.2f}", "outer chamfer 2.5 x 45° smooth; inner chamfer 1.0; skirt chamfer 1.2",
      f"v16 V-RIDGE on the bore: relief band r {R_RELIEF} z {Z_RELIEF0:.1f}-{Z_RELIEF1:.1f}; the ridge 90° flanks from its base ({RIDGE_BASE_W} wide, z {Z_RIDGE0:.1f}-{Z_RIDGE1:.1f}) to the crest r {R_CREST} ({RIDGE_CREST_W} flat) - three V623ZZ V-groove bearings straddle it", f"code RING recess 0.15 deep in the crown's underside, r {CODE_R0}-{CODE_R1} (v13: the encoder reads the crown, not the bore - the bore is plain apart from the V-groove)", f"diamond knurl {KNURL_N} starts x 2, {KNURL_DEPTH} deep, helix {KNURL_HELIX_DEG:.1f}°, {KNURL_ROWS} whole rows z {KNURL_Z0:.1f}-{KNURL_Z1:.1f}; skirt bottom z {Z_SKIRT_BOT}", f"wall under the knurl root {SKIRT_WALL - KNURL_DEPTH:.1f}"]),
    ("internal_structure", "Internal structure", "PETG (prototype) / PA12 (production)", "v16: print INVERTED - the seat flange's top face on the bed, 0.20 mm; supports under the halo ledge + lip (outside) and the two Ø8 fixed-post tops; the block channel's roof bridges",
     [f"wall in TWO radii: r {R_WALL_IN}-{R_WALL_OUT} from the plate to z {Z_RAMP0}, a 50° ramp inward to r {R_WALL_IN_UP}-{R_WALL_OUT_UP} at z {Z_RAMP1}, then up to the seat (the knob is fitted {KNOB_FIT_OFFSET} off-centre and its far-side ridge crest comes to r {R_CREST - KNOB_FIT_OFFSET:.1f})", f"seat flange r {R_SEAT_IN}-{R_WALL_OUT_UP}, z {Z_SEAT_BOT}-{Z_SEAT_TOP}: its top face is FLAT with 0.3 chamfers on both edges; three Ø{PIN_D} H7 through-holes (ream) at {NUB_AZ}°, r {PANEL_DISC_R + 1.15:.2f} for the display's dowel pins, each in a Ø{UNDER_BOSS_D} boss {UNDER_BOSS_H} under the flange",
      f"HALO (HALO-OPTICS): the strip's ledge r {R_WALL_OUT_UP + 0.5:.1f}-{R_LEDGE_OUT}, z {Z_LEDGE0}-{Z_LIP1} (the {LED_STRIP_W} mm strip stuck face DOWN under it, r {R_STRIP_IN:.1f}-{R_STRIP_OUT:.1f}, {LED_N} LEDs, {HALO_PEAK_A:.2f} A full white, firing at the white liner {HALO_THROW:.1f} below); the lip r {R_LEDGE_OUT}-{R_LIP_OUT}, z {Z_LIP0}-{Z_LIP1} clamps the opal ring through a {DIFF_GASKET_T} gasket, 0.3 radial clearance",
      f"two FIXED wheel posts Ø{WHEEL_POST_D} at r {WHEEL_AXIS_R:.1f}, az {WHEEL_FIXED_AZ}, to z {Z_POST_TOP:.1f}, Ø2.9 press holes for the Ø3 m6 x 10 pins; the SPRUNG wheel's channel at {WHEEL_SPRUNG_AZ}°: walls {CHANNEL_WALL_T} at t ±{CHANNEL_HALF:.1f}-{CHANNEL_OUT_HALF:.1f} from r {CHANNEL_END_R0} to the wall, z {Z_PLATE_TOP}-{Z_ROOF1}, roof z {Z_ROOF0}-{Z_ROOF1} with a {WHEEL_PIN_D + 0.2} slot for the pin (travel {BLOCK_TRAVEL_IN} in / {BLOCK_TRAVEL_OUT} out), end wall r {CHANNEL_END_R0}-{CHANNEL_END_R0 + 2} with a Ø2.4 hole at z {RELEASE_SCREW_Z} for the release screw; wall windows {WHEEL_OD + 2:.0f} wide open to the top from z {Z_POST_TOP:.1f}; the seat flange cut away above each wheel",
      f"pillars Ø7 at r {PILLAR_R}, az {PILLAR_AZ}, to z {PILLAR_TOP:.1f}; M2.5 inserts (Ø3.5 x 4.0) from below (the plate screws) - nothing screws in from above", f"encoder at {ENC_AZ}°, r {ENC_R:.0f}: two radial slots through the flange at t ±4.75 over M2 inserts in Ø{UNDER_BOSS_D} bosses under it; LRA pad at {LRA_AZ}° (r {LRA_PAD_R_IN:.1f} to the wall) with the contact carrier's clip beside its flex tail at {LRA_CLIP_AZ}° (two ribs from r {LRA_CLIP_R0:.1f}, a 0.4 groove each, 45° tops); the knob-bleed foot's M2 insert in a boss under the flange at {BLEED_AZ}°, r {BLEED_FOOT_R}",
      f"flex slot 32 x 2.5 through the seat at 0°, offset -4; {len(slit_azs())} vent slits {SLIT_W} x {SLIT_Z1 - SLIT_Z0:.1f} at z {SLIT_Z0}-{SLIT_Z1}, 2.5° grid; motor relief at 90° (the bell's window 1.0 clear, the collar's 2.0, open up to the flange); halo tail notch at {HALO_TAIL_AZ}°, the far-end feed's at {HALO_FEED2_AZ}°"]),
    ("halo_diffuser", "Halo ring (opal acrylic)", "cast opal acrylic, 6 mm sheet (Perspex Opal 030 ~68 % / PLEXIGLAS Satinice 0D010 DF 83 % class), CNC routed, annealed 80 °C 2 h; no IPA or acetone ever", "machined, not printed (HALO-OPTICS §6)",
     [f"r {R_DIFF_IN:.1f}-{R_DIFF_OUT:.1f} ({DIFF_T} wall), z {Z_DIFF0}-{Z_DIFF1} ({Z_DIFF1 - Z_DIFF0:.1f} tall); vertical outer face standing {R_DIFF_OUT - R_KNOB:.1f} proud of the knob and plate (Ø{2*R_DIFF_OUT:.1f})", f"{DIFF_CHAMFER} chamfer on all four edges", f"stands in the rim ring's 0.5 rebate (r {R_REBATE} outward, floor z {Z_DIFF0}) on the 0.8 shelf; 0.3 radial clearance to the rebate's wall and the ledge; clamped axially by the lip through a {DIFF_GASKET_T} foam gasket - never hard between two machined faces"]),
    ("halo_liner", "Halo liner (white)", "white PETG", "v16: print flat on its floor, 0.16 mm; no supports",
     [f"L-section ring: floor r {R_WALL_OUT + 0.1:.1f}-{R_LEDGE_OUT} x {LINER_T} on the rim ring's top, wall r {R_WALL_OUT + 0.1:.1f}-{R_WALL_OUT + 0.7:.1f} up to z {Z_PLATE_TOP + LINER_WALL_H} against the structure's wall (0.6 under the strip); cut at the two tail notches", "HALO-OPTICS §9: the floor and walls must be white and diffuse - bare stainless is specular"]),
    ("wheel_block", "Sprung wheel block", "PETG, 4 perimeters", "v16: print flat on its bottom face, 0.12 mm",
     [f"{BLOCK_L} (radial) x {BLOCK_W} x {BLOCK_H} on the plate top at {WHEEL_SPRUNG_AZ}°, r {WHEEL_AXIS_R + BLOCK_PIN_FROM_END - BLOCK_L:.1f}-{WHEEL_AXIS_R + BLOCK_PIN_FROM_END:.1f} nominal; Ø2.9 press hole for the Ø3 m6 x 16 axle pin {BLOCK_PIN_FROM_END} from its outer end (the pin to z {Z_BLOCK0 + 0.2 + BLOCK_PIN_L})", f"Ø2.2 hole from the inner face at z {RELEASE_SCREW_Z} for the M2 x 18 release screw; an M2 nut in a {NUT_M2_AF + 0.2} slot from the top, {BLOCK_NUT_FROM_FACE}-{BLOCK_NUT_FROM_FACE + NUT_M2_T} behind the face", f"spring Ø{SPRING_D} x {SPRING_FREE_L} free, {SPRING_K} N/mm on the screw between the channel's end wall and the block: {SPRING_K * (SPRING_FREE_L - (WHEEL_AXIS_R + BLOCK_PIN_FROM_END - BLOCK_L - CHANNEL_END_R0 - 2)):.1f} N seated, {SPRING_K * (SPRING_FREE_L - (WHEEL_AXIS_R - BLOCK_TRAVEL_IN + BLOCK_PIN_FROM_END - BLOCK_L - CHANNEL_END_R0 - 2)):.1f} N parked", f"{CHANNEL_CLEAR} to the channel's walls and roof; slides on the anodised plate"]),
    ("drive_collar", "Drive collar (on the bell)", "PETG (prototype) / POM (production)", "v16: print axis vertical, 0.12 mm",
     [f"ID {DRIVE_COLLAR_ID} -0.05 (press) x OD {DRIVE_COLLAR_OD} x {DRIVE_COLLAR_H}, on the bell's top (z {Z_COLLAR0}-{Z_COLLAR1}); 0.3 lead-in chamfer", f"the {MOTOR_BAND_T} silicone band on it at z {Z_DRIVE0}-{Z_DRIVE1} reaches the bore (r {R_BORE}); the bell itself stops at r {MOTOR_R + MOTOR_OD/2:.1f}, inside the wall's outer face and 0.5 inside the halo liner", f"bore/collar ratio {2*R_BORE/DRIVE_COLLAR_OD:.2f}"]),
    ("mcu_tray", "MCU tray (over the audio board)", "PETG", "v16: print flat on its underside, 0.16 mm",
     [f"{TRAY_L} x {TRAY_W} x {TRAY_T} at z {Z_TRAY0}-{Z_TRAY1}, centred {TRAY_T0} toward the ports of the audio board's centre; four Ø{STUD_HOLE_D} on the audio's stud pattern ({2*AUDIO_HOLE_L:.0f} x {2*AUDIO_HOLE_W:.0f}); on {TRAY_SPACER_H} tube spacers above the audio's nuts", f"a {TRAY_POCKET_D} pocket: the ESP32-S3-Zero class MCU ({MCU_L} x {MCU_W}) between the four stud nuts, USB-C toward the west end (the level shifter is on the plate at az {LS_AZ}, r {LS_R})", "no screw touches the MCU: the keeper's rails hold it by its edges"]),
    ("tray_keeper", "Tray keeper", "PETG", "v16: print flat, 0.16 mm",
     [f"{TRAY_L} x {TRAY_W} x {KEEPER_T} on the tray (z {Z_TRAY1}-{Z_KEEPER1}), clamped by the audio studs' top nuts; a window over the MCU's parts (1.5 rails); its USB-C end open"]),
    ("board_spacer", "Board spacer (family)", "PETG", "v16: print axis vertical, 0.12 mm; 3.0 x 4, 1.0 x 4, 4.4 x 4",
     [f"Ø{SPACER_D} tube, bore {STUD_HOLE_D}: {SPACER_H} under the driver and haptic breakouts, {AUDIO_SPACER_H} under the audio board, {TRAY_SPACER_H} between the audio's nuts and the tray", "the countersunk M2 stud passes through; the nut above the board clamps the stack"]),
    ("carriage", "Motor carriage", "PETG", "print standing on the shoe, 0.16 mm; no supports (12 mm bridge over the sensor pocket); 4+ perimeters for the tab",
     [f"shoe Ø37 x {CARRIAGE_T}; locating rim Ø35.6/37 x 0.6", f"pocket {CARRIAGE_POCKET_L} x {CARRIAGE_POCKET_W} x 3.3 for the MT6701 module (v16); sight hole Ø9; a 2.4 x 2.2 notch through the shoe's inboard wall for the sensor lead", f"push tab {CARRIAGE_TAB_T} x {CARRIAGE_TAB_W} to z {CARRIAGE_TAB_TOP:.1f} (v11: 28.5 through the deck; the servo is now beside it on the plate)", f"travel {CLUTCH_LIFT} radial in the plate's stadium hole"]),
    ("servo_mount", "Servo frame (on the plate)", "PETG", "print flat, 0.20 mm; no supports",
     [f"floorless frame round the AGFRC envelope {SERVO_L} x {SERVO_W} x {SERVO_H}; walls 1.0, {SERVO_H + 0.5} tall; the servo lies on the plate at r {SERVO_R0:.1f}-{SERVO_R0 + SERVO_L:.1f}, az {MOTOR_AZ:.0f}", "open toward the carriage tab; lead notch in the inner end wall", f"2 ears at t ±{SERVO_EAR_T}, M2.5 x 4 into tapped blind holes in the plate's web"]),
    ("connect_bracket", "Connect-board bracket", "PETG", "print standing on its straight -y edge (slab vertical, feet and bosses sideways), 0.20 mm; no supports",
     [f"slab {CB_BRACKET_T} thick at z {Z_PLATE_TOP + CB_FOOT:.1f}-{Z_PLATE_TOP + CB_FOOT + CB_BRACKET_T:.1f}, r {CB_R - CB_L/2 + 0.5:.0f}-{CB_R + CB_L/2 + 2.5:.0f}, t {CB_T0 - CB_W/2 - 2:.0f}..{CB_T0 + CB_W/2 + 2:.0f}, bridging the port slot; its outer end rests on the port face's rail (z 9.5)", f"foot strip r {CB_R - CB_L/2 + 0.5:.0f}-{CB_R - CB_L/2 + 2.5:.0f} on the plate; two csk ears at {CB_SCREW_XY}, M2.5 into the web", f"four Ø6 bosses {CB_BOSS_H} tall with M2 inserts for the connect board ({CB_L} x {CB_W}, holes 3 in from its inner corners, 5.5 from its outer)", "the -y inner corner cut back to x 45.5 (the audio board's USB plug is there)"]),
    ("blower_saddle", "Blower saddle + hood neck", "PETG", "print on its flat top face, 0.16 mm; no supports",
     [f"plate {BLOWER_L:.0f} x {BLOWER_W:.0f} x {SADDLE_T} on the blower's top (z {Z_BLOWER1}-{Z_BLOWER1 + SADDLE_T}) - v16: a plain clamp plate, no board on it; two Ø2.2 through-holes on the blower's 24 x 24 diagonal: M2 x 16 pan heads through the plate and the blower into the plate's piers",
      f"hood neck: {HOOD_W:.0f} wide, r {BLOWER_R + BLOWER_L/2:.0f}-{R_CORE_DUCT + 1:.1f}, walls {HOOD_T}, open at the bottom over the trench and toward the blower's outlet ({BLOWER_OUTLET_W:.0f} x {BLOWER_OUTLET_H:.0f}); on a {BLOWER_GASKET_T} foam gasket on the plate top", f"blower at az {BLOWER_AZ:.0f}, r {BLOWER_R:.0f} (Delta BFB0305HA-C 30 x 30 x 10, inlet down over the Ø{WEB_INLET_D:.0f} hole in the web)"]),
    ("hood_lid", "Hood lid (over the trench foot)", "PETG", "v15: print flat, 0.16 mm; no supports",
     [f"2.5 thick at z {PLATE_T + BLOWER_GASKET_T}-{PLATE_T + BLOWER_GASKET_T + 2.5}, az {HOOD_LID_AZ[0]:.1f}-{HOOD_LID_AZ[1]:.1f}, r {R_CORE_DUCT:.1f}-{TRENCH_R1 + 1.5:.1f}; butts the saddle's neck (0.15 clear); two Ø2.2 at az {HOOD_SCREW_AZ}, r {HOOD_SCREW_R}: M2 x 5 into the ring's top; on the same {BLOWER_GASKET_T} gasket"]),
    ("encoder_shim", "Encoder shim (family)", "PETG", "v15: print flat, 0.10 mm; one of each height in ENC_SHIM_FAMILY",
     [f"8.4 x 12.4 x {ENC_BOSS_H:.1f} (nominal; family {ENC_SHIM_FAMILY}), two Ø2.2 at ±4.75; sits on the seat flange under the encoder board, sets the {ENC_GAP} optical gap"]),
    ("speaker_cradle", "Speaker cradle", "PETG", "print flat, 0.20 mm; no supports (fingers full height)",
     ["ring r 18.3-20.5 x 4.45 under the Ø40 flange", f"three snap fingers at {SPEAKER_FINGER_AZ}° from the speaker's centre (device azimuths)", f"two ears at r 22.5, {SPEAKER_EAR_AZ}° from the centre; M2.5 x 4 from above into the plate's web (v11: M3 from below)", f"speaker centre ({SPEAKER_CENTRE[0]:.0f}, {SPEAKER_CENTRE[1]:.0f}) - az {math.degrees(math.atan2(SPEAKER_CENTRE[1], SPEAKER_CENTRE[0])):.0f}°, r {math.hypot(*SPEAKER_CENTRE):.1f}"]),
    ("port_face", "Rear port face", "PETG", "print lying on its outer face, 0.16 mm; no supports (the socket holes print vertical)",
     [f"{PORT_W} wide x {PORT_FACE_T} thick at r {PORT_FACE_R0}, z {-PAD_T}-{Z_PLATE_TOP}", f"barrel nose Ø6.2 at t {PORT_BARREL_T}, z {BARREL_AXIS_Z}; USB-C opening at t {PORT_USBC_T}, z {USBC_AXIS_Z}; jack Ø6.3 at t {PORT_JACK_T}, z {JACK_AXIS_Z}; light aperture Ø{SENSOR_HOLE_D} at t {PORT_LIGHT_T}",
      f"shelf for the USB-C board; a 3.0 slot holder for the Adafruit 4162 light-sensor breakout ({LIGHT_BOARD_L} x {LIGHT_BOARD_H}, standing from z {LIGHT_BOARD_Z0} to {LIGHT_BOARD_Z0 + LIGHT_BOARD_H}, sensor at the hole) with a pocket for its sensor package; a {JACK_BOSS_T} boss round the panel jack's Ø{JACK_HOLE_D} hole; rail along the top on the plate (1.5 tall, {2*PORT_TAB_T + 6:.0f} wide, inner edge r {PORT_TAB_R - 2.5:.1f}, flat front in the face's plane, corners cut 45° to stay inside the diffuser) with two Ø2.2 holes at r {PORT_TAB_R:.1f}, t ±{PORT_TAB_T:.0f}: M2 screws into the plate"]),
    ("base_plate", "Base plate - aluminium core (the heatsink)", "6082 aluminium, CNC two-sided; EXTERNAL faces black hard anodised, INTERNAL faces chromate or bare - no masked pads (design-changes item 2)", "machined, not printed (print a PETG stand-in without the duct for the fit check)",
     [f"r < {RIM_IN:.1f} x {PLATE_T}: {WEB_T:.0f} web (z {CLOSING_T + DUCT_H:.0f}-{PLATE_T:.0f}), {DUCT_H:.0f} duct (z {CLOSING_T:.0f}-{CLOSING_T + DUCT_H:.0f}) closed by a 1 mm plate in a recess on a {GASKET_T} gasket in a groove; Ø{PIER_D:.0f} piers {PIER_H} into the duct under every screw from the top; rebate r {R_CORE_DUCT:.1f}-{RIM_IN:.1f}, z {RIM_STEP_Z:.0f}-{PLATE_T:.0f} for the ring's flange on a {RIM_STEP_Z:.0f} shoulder, 7 x M2.5 csk from below at r {RING_SCREW_R}; the ring's bond screw M2.5 tapped 3.0 into the shoulder at az {RING_BOND_AZ}; the CHASSIS bond M2.5 tapped blind at {GND_BOND_XY} (the only chassis bond)",
      f"duct: collector r {COLLECTOR_R0:.0f}-{R_CORE_DUCT - DUCT_WALL:.1f} (front and sides), {len(channel_ys())} straight channels {FIN_CH_W:.0f} x {DUCT_H:.0f} on a {FIN_PITCH:.0f} pitch beside the Pi window, rear plenums r {PLENUM_R0:.0f}+; {DUCT_MARGIN} walls round every through-cut; intake passages as closed tunnels z {CLOSING_T:.0f}-{CLOSING_T + INTAKE_H} through the duct wall and shoulder ({len(intake_azs())} x {INTAKE_W:.0f} wide) + {len(EXHAUST_AZ)} exhaust tunnels {EXHAUST_W:.0f} wide at az {EXHAUST_AZ}",
      f"BLOWER (v15, fitted): Ø{WEB_INLET_D:.0f} inlet hole through the web at az {BLOWER_AZ:.0f}, r {BLOWER_R:.0f}; discharge trench {TRENCH_W:.0f} wide from r {TRENCH_R0} out through the duct wall and the shoulder, widening to az {TRENCH_FOOT_AZ[0]:.0f}-{TRENCH_FOOT_AZ[1]:.0f} (open-topped, the hood seals it); the 2 mm wall at r {TRENCH_R0 - 2:.1f}-{TRENCH_R0} keeps it off the suction side",
      f"Pi window (Pi at ({PI_X0:.0f}, {PI_Y0:.0f}), with the USB-C receptacle, HDMI plug and USB-A plug notches - v16: no plug-head notch, the Pi is powered through its header), carriage hole, port slot {PORT_W} wide; {len(top_screw_xy())} x M2.5 tapped blind {BLIND_D} deep from the top (servo frame, connect bracket, speaker cradle) + 2 x M2 (the blower) + THE chassis bond (M2.5) at {GND_BOND_XY}, each on a pier; {len(CLOSING_SCREW_XY)} x M2.5 tapped from below for the closing plate; {len(stud_xy())} x Ø{STUD_HOLE_D} through full-depth Ø7 islands for the boards' countersunk M2 studs from below (the channels cross-linked round every island)",
      "v16: flat top face - no ribs (the two v15 ribs are deleted)"]),
    ("rim_ring_STEEL", "Rim ring (stainless)", "stainless steel 304/316, machined; BARE: electropolish (the 0.3 chamfers at every opening mouth and both edges), then brush the edge face axially; the bond spot needs no masking", "machined, not printed",
     [f"r {RIM_IN:.1f}-{PLATE_R:.1f} x {PLATE_T}; {len(vent_azs())} obround openings {VENT_W} x {VENT_H} (z {VENT_Z0}-{VENT_Z0 + VENT_H}) on 3° through the {PLATE_R - RING_WALL_R0:.1f} outer wall, az 1.5 + 3k, mirrored about 0-180, none across the port face (342-18): {sum(1 for a, k in vent_azs() if k == 'intake')} intake (60-300) + {sum(1 for a, k in vent_azs() if k == 'exhaust')} exhaust (18-60, 300-342); {VENT_CHAMFER} x 45° polished at every mouth; the upper land plain (no reeding - Ryan, 7 Sep); {PLATE_CHAMFER} chamfers on both outer edges",
      f"underside groove behind the openings: r {GROOVE_R0}-{GROOVE_R1} (intake arc) / r {GROOVE_R0_EXH}-{GROOVE_R1} (exhaust arcs), z 0-{GROOVE_Z1}, walls {GROOVE_WALL_DEG}° at 60 and 300; the pad closes it; the {INTAKE_UNDERCUT_H} undercut under the outer wall (r {RING_WALL_R0}-{PLATE_R:.1f}) opens into it all round both arcs; the blower's trench: flange notched and inner land cut away az {TRENCH_FOOT_AZ[0]:.0f}-{TRENCH_FOOT_AZ[1]:.0f} to r {TRENCH_R1}, the groove's roof open there under the lid; 2 x M2 tapped in the top for the lid at az {HOOD_SCREW_AZ}, r {HOOD_SCREW_R}",
      f"inward flange r {R_CORE_DUCT:.1f}-{RIM_IN:.1f}, z {RIM_STEP_Z:.0f}-{PLATE_T:.0f}, 7 x M2.5 tapped blind from below at r {RING_SCREW_R}, az {RING_SCREW_AZ}; the dedicated BOND screw's Ø2.8 clearance at az {RING_BOND_AZ}, r {RING_BOND_R} (M2.5 from the top into the core, star washer under the head, both faces bare)",
      f"passages across the inner land (r {RIM_IN:.1f} to the groove), {INTAKE_H} deep, the pad closes them: {len(intake_azs())} intake {INTAKE_W:.0f} wide ({len(intake_azs())*INTAKE_W*INTAKE_H:.0f} mm2) on the 11.25° grid, {len(EXHAUST_AZ)} exhaust {EXHAUST_W:.0f} wide at az {EXHAUST_AZ} (the -y circuit; the +y circuit exhausts through the trench)",
      f"3 x M2.5 csk from below at r {PILLAR_R:.1f}, az {PLATE_SCREW_AZ} (the structure's pillars); 2 x Ø1.6 tapped M2 at r {PORT_TAB_R:.1f}, t ±{PORT_TAB_T:.0f} (the port face's rail); port slot {PORT_W} wide", f"v16 (HALO-OPTICS): the opal ring's seat - a 0.5 rebate in the top from r {R_REBATE} outward and a 0.8 shelf r {PLATE_R:.1f}-{PLATE_R_SHELF:.1f} at z {Z_SHELF0}-{Z_DIFF0} standing {PLATE_R_SHELF - PLATE_R:.1f} proud (0.2 polished chamfers on its edges), {Z_SHELF0 - (VENT_Z0 + VENT_H + VENT_CHAMFER):.2f} above the openings' chamfered mouths"]),
    ("closing_plate_AL", "Closing plate (aluminium)", "1 mm aluminium, laser-cut, black anodised (outer face)", "laser-cut, not printed",
     [f"disc r {R_CORE_DUCT - 0.1:.1f} x {CLOSING_T}, flush in the core's recess on a {GASKET_T} die-cut gasket (two pieces); same Pi window, carriage hole and port slot as the core", f"{len(stud_xy())} x Ø{STUD_HOLE_D} countersunk from below (DIN 7991 M2 heads, 0.2 proud) for the boards' studs", f"four 9.5 square lands reaching into the Pi window at the Pi's holes {[(round(x, 1), round(y, 1)) for x, y in pi_holes_xy()]}, Ø2.7 csk from below: the Pi and adapter stack screws to them (M2.5 x 6 into the standoffs)", f"{len(CLOSING_SCREW_XY)} x M2.5 countersunk; unscrew to clean the fin channels"]),
]
def sheet(pdf, i, name, title, material, printnote, dims):
    shape = board_spacer() if name == "board_spacer" else made[name]
    bb = shape.bounding_box()
    cx, cy = (bb.min.X + bb.max.X)/2, (bb.min.Y + bb.max.Y)/2
    s = Pos(-cx, -cy, 0) * shape
    bb = s.bounding_box()
    L, W, H = bb.size.X, bb.size.Y, bb.size.Z
    fig = plt.figure(figsize=(420/25.4, 297/25.4))
    fig.patch.set_facecolor("white")
    # frame
    fr = fig.add_axes([0, 0, 1, 1]); fr.axis("off"); fr.set_xlim(0, 420); fr.set_ylim(0, 297)
    fr.add_patch(plt.Rectangle((10, 10), 400, 277, fill=False, lw=1.2))
    # title block
    fr.add_patch(plt.Rectangle((230, 10), 180, 42, fill=False, lw=1.0))
    fr.plot([230, 410], [38, 38], color="k", lw=0.6); fr.plot([330, 330], [10, 38], color="k", lw=0.6)
    fr.text(233, 46, "the 60 — v16", fontsize=12, weight="bold"); fr.text(300, 46, f"{title}", fontsize=12, weight="bold")
    fr.text(233, 41, f"Cadrane · sheet {i} of {len(SHEETS)} · {DATE} · drawn from src/params.py + model.py (build123d)", fontsize=7)
    fr.text(233, 32, f"Material: {material}", fontsize=7.5); fr.text(233, 26, f"Process: {printnote}", fontsize=7.5)
    fr.text(233, 20, "mm. Tolerance ±0.1 unless stated; clearances: running 0.30,", fontsize=7)
    fr.text(233, 14, "static 0.15, knob 0.40. Printed as-built; CNC knob Ra 0.8 on the chamfers.", fontsize=7)
    fr.text(333, 32, f"Part: {name}", fontsize=8, weight="bold"); fr.text(333, 26, f"Overall {L:.1f} x {W:.1f} x {H:.1f}", fontsize=8)
    fr.text(333, 20, f"Volume {s.volume/1000:.2f} cm³", fontsize=8); fr.text(333, 14, "Scale: see each view (fit)", fontsize=8)
    # notes
    fr.text(14, 48, "Key dimensions (from the parameter block):", fontsize=8, weight="bold")
    import re
    tidy = lambda t: re.sub(r'(\d+\.\d{3,})', lambda m: f"{float(m.group(1)):.2f}", t)
    for k, d in enumerate(dims[:8]): fr.text(14, 43 - 4.4*k, f"{k+1}. {tidy(d)}", fontsize=7)
    # views
    span = max(L, W, H) * 1.35 + 20
    def view(rect, title):
        ax = fig.add_axes(rect); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=8.5, weight="bold"); return ax
    ax = view([0.03, 0.30, 0.44, 0.62], "PLAN (from above): sections at three heights — bottom (light), middle, top (dark)")
    ax.set_xlim(-span/2, span/2); ax.set_ylim(-span/2, span/2)
    for z, col in ((bb.min.Z + 0.4, "0.7"), ((bb.min.Z + bb.max.Z)/2, "0.4"), (bb.max.Z - 0.4, "0.05")):
        for seg in slice_edges(s, z):
            xs, ys = zip(*seg); ax.plot(xs, ys, color=col, lw=0.7)
    dim_h(ax, bb.min.X, bb.max.X, bb.max.Y + span*0.06, f"{L:.1f}")
    dim_v(ax, bb.max.X + span*0.06, bb.min.Y, bb.max.Y, f"{W:.1f}")
    ax.plot([-span/2*0.9, span/2*0.9], [0, 0], color="0.6", lw=0.4, ls="-."); ax.plot([0, 0], [-span/2*0.9, span/2*0.9], color="0.6", lw=0.4, ls="-.")
    ax2 = view([0.50, 0.55, 0.47, 0.40], "SECTION A-A (front, plane y = 0; x across, z up)")
    ax2.set_xlim(-span/2, span/2); ax2.set_ylim(bb.min.Z - span*0.15, bb.max.Z + span*0.15)
    for seg in vsection(s, "y", 0.0):
        xs, zs = zip(*seg); ax2.plot(xs, zs, color="0.05", lw=0.7)
    dim_v(ax2, bb.max.X + span*0.06, bb.min.Z, bb.max.Z, f"{H:.2f}")
    ax3 = view([0.50, 0.20, 0.23, 0.33], "SECTION B-B (side, plane x = 0; y across, z up)")
    ax3.set_xlim(-span/2, span/2); ax3.set_ylim(bb.min.Z - span*0.15, bb.max.Z + span*0.15)
    for seg in vsection(s, "x", 0.0):
        ys, zs = zip(*seg); ax3.plot(ys, zs, color="0.05", lw=0.7)
    # detail: the right-hand end of section A-A, enlarged (the profile that matters on ring-shaped parts)
    dx0, dx1 = bb.max.X - min(L * 0.25, 30.0), bb.max.X + 2.0
    ax4 = view([0.74, 0.20, 0.23, 0.33], f"DETAIL C (section A-A, x {dx0:.0f} to {dx1:.0f}, enlarged)")
    dspan = max(dx1 - dx0, H) * 1.2
    ax4.set_xlim(dx0 - 1, dx0 - 1 + dspan); ax4.set_ylim((bb.min.Z + bb.max.Z)/2 - dspan/2, (bb.min.Z + bb.max.Z)/2 + dspan/2)
    for seg in vsection(s, "y", 0.0):
        xs, zs = zip(*seg); ax4.plot(xs, zs, color="0.05", lw=0.9)
    for zz in sorted(set(round(p, 2) for seg in vsection(s, "y", 0.0) for _, p in seg if abs(seg[0][1] - seg[-1][1]) < 0.01)):
        pass
    pdf.savefig(fig); plt.close(fig)
    print("  sheet", i, name, flush=True)

pdf_path = os.path.join(OUT, "the60_v16_A3_drawings.pdf")
with PdfPages(pdf_path) as pdf:
    # sheet 0: assumptions
    fig = plt.figure(figsize=(420/25.4, 297/25.4)); fr = fig.add_axes([0, 0, 1, 1]); fr.axis("off"); fr.set_xlim(0, 420); fr.set_ylim(0, 297)
    fr.add_patch(plt.Rectangle((10, 10), 400, 277, fill=False, lw=1.2))
    fr.text(14, 278, "the 60 — v16 — sheet 0: the ASSUMED numbers (every one of these must be verified on the real part before the drawing is trusted)", fontsize=12, weight="bold")
    fr.text(14, 270, f"{DATE}.  Stack: plate {PLATE_T}, adapter {Z_ADAPTER0:.2f}-{Z_ADAPTER1:.2f} (socket to {Z_ADAPTER_HDMI_TOP:.2f}), code ring under the crown at {Z_CODE_FACE:.2f}, seat {Z_SEAT_TOP}, glass {Z_GLASS0:.2f}-{Z_GLASS1:.2f}, lens to {Z_LENS1:.2f}, knob top {Z_KNOB_TOP:.2f}, overall {HEIGHT:.2f} with the pad.  Ø{2*R_KNOB:.0f}.", fontsize=8.5)
    for k, (n, v, why) in enumerate(ASSUMED_LIST):
        fr.text(14, 258 - 7*k, f"{k+1:2d}. {n}: {v}", fontsize=8.5, weight="bold"); fr.text(180, 258 - 7*k, why, fontsize=8.5)
    fr.text(14, 60, "Build notes in V16.md.  The sheets that follow: one per made part.", fontsize=8.5)
    pdf.savefig(fig); plt.close(fig)
    for i, (name, title, material, printnote, dims) in enumerate(SHEETS, start=1):
        sheet(pdf, i, name, title, material, printnote, dims)
print("wrote", pdf_path)
