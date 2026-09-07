the 60 - v15 - printable parts (print orientation; they will not assemble as exported)

knob_body            0.16 mm  ONE PIECE. top face down, no supports. bore smooth except the V-groove; the 0.15 code-ring recess is in the crown's underside (the bed face, so it prints as a shallow pocket)
internal_structure   0.20 mm  v15: INVERTED - the seat flange's top face (the display's seat) on the bed, the wall growing up from it, the wall foot at the top (Ryan, 6 Sep: fewer supports, a stronger part, a flat seat). Nothing rises above the seat any more: the pins, the encoder shim and the bleed foot all sit on the flat face; the bosses hang under the flange and print upward. SUPPORTS: the diffuser lip (a 3.9 ring at z 11.7, outside the wall - easily removed, the face it marks is under the knob skirt) and the three Ø8 wheel-post tops (the bush seats, z 7.1). The pillar tops and the LRA clip ribs carry 45 deg cones/webs; the windows are open at the bed; 0.3 chamfers on the bed face's edges
halo_diffuser        0.20 mm  on its underside; natural / translucent PETG; no supports
carriage             0.16 mm  standing on the Ø37 shoe, tab up; 12 mm bridge over the sensor pocket; PETG, 4 perimeters (the tab is loaded across its layers)
servo_mount          0.20 mm  flat; a floorless frame for the AGFRC servo, open toward the tab; two ears screwed to the plate
connect_bracket      0.20 mm  standing on its straight -y edge, the slab vertical (1.5 thick, 28 wide, 50 tall): the feet, ears and bosses stick out sideways and print without support; the M2 insert holes and the csk cones are sideways at Ø3.2 / Ø5.4, fine at that size. (On its feet the slab would hang 1.5 over the bed for 28 mm: supports)
speaker_cradle       0.20 mm  flat; ring under the speaker flange with three snap fingers
blower_saddle        0.16 mm  v15: on its flat top face (the motion board's face) on the bed, the hood's neck walls grow up from it; no supports. Two Ø2.2 through-holes vertical
hood_lid             0.16 mm  v15: flat, 2.5 thick, two Ø2.2 holes; butts against the saddle's neck
encoder_shim         0.10 mm  v15: flat, one per height in ENC_SHIM_FAMILY (0.7 / 0.8 / 0.9 / 1.0 / 1.1) - print the set, fit the one the bench wants
port_face            0.16 mm  lying on its outer face (the socket openings print as vertical holes); the USB-C shelf, the light-sensor foot and the screw rail stand up from it; no supports
collar_0             0.12 mm  x3, axis vertical; press over a 623ZZ
bush_0               0.12 mm  x3, stem down / pin up; the 1 mm flange ledge is the only overhang; brass in production
base_plate_AL         CNC 6082 aluminium core r < 75.2: 2 web, 5 duct with 3 x 5 fin channels on a 4 pitch, ribs 6 tall on top; external faces black hard anodised, internal faces chromate or bare - no masked pads
rim_ring_STEEL        machined STAINLESS ring r 75.2-87.7 x 8: 92 obround openings 2.0 x 4.5 on 3 deg through the 3.7 outer wall into an underside groove the pad closes, 0.8 undercut under the outer wall, 17 intake + 3 exhaust passages across the inner land, the blower trench's notch, 0.3 polished chamfers; bare, brushed axially
closing_plate_AL      1 mm laser-cut aluminium disc r < 72.2, 9 x M2.5 csk, flush in the core's recess (unscrew to clean the duct)

Bought: DisplayModule DM-TFTR50-413 panel + cover lens (bonded to the seat); Raspberry Pi 5 + Active Cooler heatsink (fan OFF); 4x M2.5 x 12 standoffs;
DM-ADTTR-014 HDMI-to-DSI adapter kit (driver board on the Pi's standoffs, display connect board on its bracket, 150 mm flat cable); JD-Power MY-3514C gimbal (envelope); AGFRC C1.5CLS PRO servo (envelope); 3x 623ZZ;
Soberton SP-4005-1; TMC6300; MT6701 + D6x2.5 magnet; AEDR-8300 + a 0.15 code ring under the crown; DRV2605L + VLV101040A; ES9219Q;
Switchcraft 35RAPC4BH3; GCT USB4520; CUI PJ-063AH barrel jack; VEML7700; a 5 mm addressable LED strip (~46 LEDs); 12 V -> 5 V converter module (rating from the measured inlet load); Delta BFB0305HA-C blower; 3x ISO 8734 2 m6 x 12 dowels; foam gaskets.

Open the60_v15_assembly.step in Fusion, not the parts: 5 top-level parts (knob, structure, pad, tape, converter) and 20 sub-assemblies
(pi5, pi_stack_hardware, display_module, motor_carriage_unit, wheel_30/150/270, servo_unit, base_plate_unit, speaker_unit, encoder_unit, lra, adapter_unit, connect_board_unit,
audio_unit, motion_unit, board_washers, port_module, plugs_external, cables_internal, halo) - one visibility toggle each.
