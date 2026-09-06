the 60 - v10 - printable parts (print orientation; they will not assemble as exported)

knob_body            0.16 mm  ONE PIECE. top face down, no supports. bore smooth except the 0.15 code-band recess and the V-groove
internal_structure   0.20 mm  upright on the wall foot. SUPPORTS in two places only: under the seat flange (r 62-70.5 at z 20.4 above the bed - a ring inside the wall, hidden face) and under the diffuser lip (r 73.2-76 at z 5.5 - a thin ring outside). Everything else self-supporting: open-topped windows, 1 mm slit roofs, 45 deg hole ends
deck                 0.20 mm  upside down: its flat top face on the bed, only the three Pi legs standing up; no supports. 14 x M2.5 nuts press into the pockets in the top face
halo_diffuser        0.20 mm  on its underside; natural / translucent PETG
carriage             0.16 mm  standing on the Ø37 shoe, tab up; 12 mm bridge over the sensor pocket; PETG, 4 perimeters (the tab is loaded across its layers)
servo_mount          0.20 mm  flat; tray for the AGFRC servo envelope, open toward the tab; sits on the deck
speaker_cradle       0.20 mm  flat; ring under the speaker flange with three snap fingers
port_face            0.16 mm  lying on its outer face (the socket openings print as vertical holes); the USB-C shelf, the light-sensor foot and the two ear arms stand up from it; no supports
collar_0             0.12 mm  x3, axis vertical; press over a 623ZZ
bush_0               0.12 mm  x3, stem down / pin up; the 1 mm flange ledge is the only overhang; brass in production
base_plate_STEEL      laser/waterjet-cut 8 mm mild steel (engine-turned edge in plan), then 1.0 chamfers top and bottom on a lathe or CNC; powder-coated or polished; Ø154; Pi window, carriage hole, port slot

Bought: DisplayModule DM-TFTR50-413 panel + cover lens (bonded to the seat); Raspberry Pi 5 + Active Cooler heatsink (fan OFF);
DM-ADTTR-014 HDMI-to-DSI adapter; JD-Power MY-3514C gimbal (envelope); AGFRC C1.5CLS PRO servo (envelope); 3x 623ZZ;
Soberton SP-4005-1; TMC6300; MT6701 + D6x2.5 magnet; AEDR-8300 + 0.15 code strip; DRV2605L + VLV101040A; ES9219Q;
Switchcraft 35RAPC4BH3; GCT USB4520; CUI PJ-063AH barrel jack; VEML7700; a 5 mm addressable LED strip (~46 LEDs); 12 V -> 5 V 10 A converter module.

Open the60_v10_assembly.step in Fusion, not the parts: 6 top-level parts (knob, structure, deck, plate, pad, tape) and 17 sub-assemblies
(pi5, display_module, motor_carriage_unit, wheel_30/150/270, servo_unit, speaker_unit, encoder_unit, lra, adapter_unit, audio_unit,
motion_unit, port_module, plugs_external, cables_internal, halo) - one visibility toggle each.
