the 60 - v16 - printable parts (print orientation; they will not assemble as exported)

knob_body            0.16 mm  ONE PIECE. top face down, no supports. bore smooth except the V-RIDGE on its relief band (v16: a 1.2 tall 90 deg ridge at z 19.9-23.1 - printed top-down its lower flank is a 45 deg overhang, fine); the 0.15 code-ring recess is in the crown's underside (the bed face, so it prints as a shallow pocket)
internal_structure   0.20 mm  v16: INVERTED as v15 - the seat flange's top face on the bed, the wall growing up from it (its 50 deg ramp outward at z 13.8-16.2 self-supports), the wall foot at the top. SUPPORTS: the halo ledge + lip (a 6.3-wide ring hanging outward at z 13.2-14.3 - removable, the face it marks is under the knob skirt) and the two Ø8 fixed-post tops (z 19.0). The block channel's roof (8.4 wide) is a bridge; its walls and end wall print up from it. The pillar tops and the LRA clip ribs carry 45 deg cones/webs; the windows are open at the bed; 0.3 chamfers on the bed face's edges
halo_liner           0.16 mm  v16: WHITE PETG, flat on its floor face; the 0.6 wall stands up; no supports. Cut at the two tail notches
wheel_block          0.12 mm  v16: flat on its bottom face; the Ø2.9 pin hole vertical; the spring pocket and the M2 insert hole are side holes (Ø4.2 / Ø3.2 - small, print as drawn); PETG, 4 perimeters
drive_collar         0.12 mm  v16: axis vertical, the lead-in chamfer at the bottom; press over the bell's top 3.5 (ID 35 -0.05); PETG (prototype) / POM (production)
mcu_tray             0.16 mm  v16: flat on its underside; the MCU pocket is a 0.6 recess in the top; four Ø2.2 holes
tray_keeper          0.16 mm  v16: flat; a frame with a window over the MCU's parts; four Ø2.2 holes
board_spacer         0.12 mm  v16: a FAMILY - Ø5 tubes, bore 2.2: 3.0 (x6, under the driver, haptic and level-shifter breakouts), 1.0 (x4, under the audio board), 4.4 (x4, between the audio's nuts and the tray); axis vertical
carriage             0.16 mm  standing on the Ø37 shoe, tab up; 12 mm bridge over the sensor pocket; PETG, 4 perimeters (the tab is loaded across its layers)
servo_mount          0.20 mm  flat; a floorless frame for the AGFRC servo, open toward the tab; two ears screwed to the plate
connect_bracket      0.20 mm  standing on its straight -y edge, the slab vertical (1.5 thick, 28 wide, 50 tall): the feet, ears and bosses stick out sideways and print without support; the M2 insert holes and the csk cones are sideways at Ø3.2 / Ø5.4, fine at that size. (On its feet the slab would hang 1.5 over the bed for 28 mm: supports)
speaker_cradle       0.20 mm  flat; ring under the speaker flange with three snap fingers
blower_saddle        0.16 mm  v15: on its flat top face (the motion board's face) on the bed, the hood's neck walls grow up from it; no supports. Two Ø2.2 through-holes vertical
hood_lid             0.16 mm  v15: flat, 2.5 thick, two Ø2.2 holes; butts against the saddle's neck
encoder_shim         0.10 mm  v15: flat, one per height in ENC_SHIM_FAMILY (0.7 / 0.8 / 0.9 / 1.0 / 1.1) - print the set, fit the one the bench wants
port_face            0.16 mm  lying on its outer face (the socket openings print as vertical holes); the USB-C shelf, the light-sensor foot and the screw rail stand up from it; no supports
base_plate_AL         CNC 6082 aluminium core r < 78.8: 2 web, 5 duct with 3 x 5 fin channels on a 4 pitch, flat top; 12 Ø2.2 stud holes through full-depth islands; external faces black hard anodised, internal faces chromate or bare - no masked pads
rim_ring_STEEL        machined STAINLESS ring r 78.8-92.7 x 8 with the 0.8 shelf to r 94.7: 90 obround openings 2.0 x 4.5 on 3 deg through the 3.7 outer wall into an underside groove the pad closes, 0.8 undercut under the outer wall, 18 intake + 2 exhaust passages across the inner land, the blower trench's notch, the 0.5 rebate for the opal ring, 0.3 polished chamfers; bare, brushed axially
closing_plate_AL      1 mm laser-cut aluminium disc r < 75.8, 9 x M2.5 csk + 12 countersunk Ø2.2 for the boards' studs, flush in the core's recess (unscrew to clean the duct)
halo_diffuser_OPAL    machined opal acrylic ring r 90.8-94.7 x 5.7 (from 6 mm cast sheet), 0.3 chamfers, annealed; Perspex Opal 030 / Satinice 0D010 DF class

Bought: DisplayModule DM-TFTR50-413 panel + cover lens (bonded to the seat); Raspberry Pi 5 + Active Cooler heatsink (fan OFF), powered through its header; 4x M2.5 x 12 standoffs;
DM-ADTTR-014 HDMI-to-DSI adapter kit (driver board on the Pi's standoffs, display connect board on its bracket, 150 mm flat cable); JD-Power MY-3514C gimbal (envelope) with the printed drive collar; AGFRC C1.5CLS PRO servo (envelope);
3x V623ZZ V-groove bearings on Ø3 m6 dowel pins (2x 10, 1x 16) + 2 M3 x 0.5 washers; a Ø4 x 16 compression spring and an M2 x 18 captive screw for the sprung block;
Soberton SP-4005-1; TMC6300-BOB and DRV2605L breakouts on the plate; ESP32-S3-Zero class MCU and a 74AHCT125 breakout on the tray; MT6701 module + D6x2.5 magnet; AEDR-8300 + a 0.15 code ring under the crown; VLV101040A + Mill-Max 867-22-002 spring-pin block; ES9219Q on the audio board;
a panel-mount 3.5 mm jack; GCT USB4520; CUI PJ-063AH barrel jack; Adafruit 4162 VEML7700 breakout; a 4 mm addressable LED strip (~55 LEDs, face down); Pololu D24V90F5 converter; Delta BFB0305HA-C blower; 3x ISO 8734 2 m6 x 8 dowels;
12 x DIN 7991 M2 countersunk studs (audio 4 x M2 x 22, the rest M2 x 16) with DIN 934 M2 nuts; foam gaskets (blower, hood, closing plate, diffuser).

Open the60_v16_assembly.step in Fusion, not the parts: top-level parts (knob, structure, pad, tape, converter, liner...) and the sub-assemblies
(pi5, pi_stack_hardware, display_module, motor_carriage_unit, wheel_30/150/270_sprung, servo_unit, base_plate_unit, speaker_unit, encoder_unit, lra, adapter_unit, connect_board_unit,
audio_unit, mcu_tray_unit, driver_breakout, haptic_breakout, board_fixings, port_module, plugs_external, cables_internal, halo, grounding, lra_contact, blower_unit, locating_pins) - one visibility toggle each.
