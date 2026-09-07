"""the 60 (Cadrane) — v14 parameter block.  Every dimension lives here.

v14 (2026-09-06): v13 (encoder reading the crown) plus the design-changes list of 6 Sep (the60-design-changes.md):
Pico-Lock connectors 2.0 tall, internal faces of the core bare (no masked pads), the grounding features (chassis bond, rim-ring
bond screw, motor bond wire, the knob's 1 MΩ bleed contact, the USB-C shell wire), the halo current from the strip as built,
the plain rim edge (engine turning removed) with the intake grooves opened to ~500 mm2, the LRA's pogo-pin board and the
rotor sensor cable's service loop.  Built from docs/v14/V14-SPECIFICATION.md.  Every number is tagged in the comment beside it:
    MEASURED  - read off a CAD file (design/cad/bought-parts, vendor STEP files)
    PUBLISHED - manufacturer figure, not modelled in a file
    ASSUMED   - chosen here; unverified (listed by ASSUMED_LIST at the end)
    RULING    - Ryan's decision, with the date

Units mm, degrees.  z = 0 is the steel plate's underside; the pad is below.
Azimuth: 0 deg = +X = the rear centre of the base (the three sockets), away
from the user (RULING 5 Sep).  Anticlockwise seen from above.
"""
import math as _m
import os as _os

_HERE  = _os.path.dirname(_os.path.abspath(__file__))
BOUGHT = _os.path.normpath(_os.path.join(_HERE, "..", "..", "..", "bought", "bought-parts"))
STEP   = _os.path.join(BOUGHT, "step")
VENDOR = _os.path.normpath(_os.path.join(_HERE, "..", "..", "vendor"))
PANEL_STP = _os.path.join(VENDOR, "DM-TFTR50-413.STEP")
PI_STP    = _os.path.join(VENDOR, "rpi5_reduced.step")      # the vendor STEP with bodies < 40 mm3 removed (2689 -> 20 solids)

# ------------------------------------------------------------- standing rules
GAP_ROTATE, GAP_STATIC, GAP_RUN = 0.40, 0.15, 0.30   # RULING v1 onward
WALL_MIN = 1.60
INSERT_M3_D, INSERT_M3_L = 4.0, 5.7                    # PUBLISHED (generic M3 insert)
INSERT_M2_D, INSERT_M2_L = 3.2, 3.0                    # PUBLISHED (generic M2 insert) - the connect board's bracket
NUT_M25_AF, NUT_M25_T = 5.0, 2.0                       # PUBLISHED DIN 934 M2.5 nut

# ------------------------------------------------------------- the panel  DisplayModule DM-TFTR50-413 (MEASURED from its STEP unless noted)
PANEL_T              = 1.98
PANEL_DISC_R         = 66.10                           # the round part of the glass
PANEL_CHIN_R         = 72.05                           # driver-chin corners (+-15.52, -70.36) in the file's frame
PANEL_ACTIVE_R       = 63.504                          # picture Ø127.008 (PUBLISHED)
PANEL_TAB_R          = 66.92                           # FPC-tab corners (+-10, 66.17)
PANEL_CHIN_AZ        = 180.0                           # RULING 5 Sep (question 14): chin toward the user, tab (flex) at 0 deg
PANEL_ROT_DEG        = -90.0                           # file frame -> device frame: file -y (chin) lands at device 180 deg
PANEL_COMP_W, PANEL_COMP_L, PANEL_COMP_H = 60.0, 68.36, 1.5     # back-side component area (PUBLISHED, drawing)
PANEL_COMP_OFFSET    = -14.0                           # ASSUMED: area centred 14 mm toward the chin (from the drawing's back view)
PANEL_FPC_W, PANEL_FPC_T = 13.99, 0.15                 # PUBLISHED (drawing)
PANEL_FPC_BEYOND     = 45.84                           # PUBLISHED: flex length beyond the outline
PANEL_MASS_G         = 70                              # PUBLISHED
# cover lens (ASSUMED throughout - specified separately, question 16)
LENS_D, LENS_T       = 140.0, 2.5
LENS_R               = LENS_D / 2
TOUCH_TAIL_W         = 8.0

# ------------------------------------------------------------- Raspberry Pi 5 (MEASURED from the vendor STEP) - v10 only
PI_L, PI_W, PI_T     = 85.0, 56.0, 1.28
PI_OVERHANG          = 3.05                            # USB-A / Ethernet shells beyond the board edge (file x to 88.05)
PI_HOLES             = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]   # M2.5, file frame
PI_USBA_TOP          = 16.2                            # above the board top
PI_SD_BELOW          = 1.45                            # micro-SD slot below the board
PI_SOC_TOP           = 2.4                             # SoC lid above the board top (file z 3.7 from the board bottom)
PI_USBC              = (6.73, 15.67)                   # x range on the y = 0 edge; 3.29 tall
PI_HDMI0_X, PI_HDMI1_X = 26.0, 39.5                    # ASSUMED (not in the vendor STEP): micro-HDMI centres on the y = 0 edge
PI_HDMI_W, PI_HDMI_H, PI_HDMI_D = 6.5, 2.9, 7.5        # ASSUMED micro-HDMI receptacle
PI_HEADER            = (7.0, 58.0, 50.0, 55.0, 8.5)    # x0, x1, y0, y1, height (MEASURED)
# placement (RULING 5 Sep, spec 4.5 revised during the build - see V10.md):
#   translation only: file x -> device x + PI_X0, file y -> device y + PI_Y0.
#   USB-A / Ethernet end faces the REAR (0 deg); USB-C / HDMI edge faces 270 deg (the speaker side);
#   40-pin header edge faces 90 deg (the motor side); micro-SD end faces the user.
PI_X0, PI_Y0         = -52.0, -38.0                    # v12 (RULING 6 Sep, Ryan's layout): 9.5 further from the ports and 10 toward 270 deg; its far corner stays inside the duct (r 64)
PI_Z0                = 1.50                            # board underside: on 0.5 washers on four lands of the closing plate (z 0-1) - the deck legs that carried it are gone
PI_Z_TOP             = PI_Z0 + PI_T                    # 2.78 board top
Z_PI_USBA_TOP        = PI_Z_TOP + PI_USBA_TOP          # 18.98

# ------------------------------------------------------------- Raspberry Pi Active Cooler (PUBLISHED product brief, no CAD body) - v10 only
COOLER_L, COOLER_W   = 63.50, 42.50
COOLER_H             = 13.70                           # heatsink underside to fan top
COOLER_BASE_ABOVE_BOARD = 2.8                          # ASSUMED (SoC 2.4 + pad)
COOLER_X0, COOLER_Y0 = 2.5, 6.75                       # ASSUMED footprint origin in the Pi frame: 63.5 long between the USB-C edge region and the USB-A shells (x 66.6), centred on the width
FAN_SIZE             = 30.0                            # PUBLISHED (the "30" in the brief)
FAN_X0, FAN_Y0       = 43.0, 7.0                       # ASSUMED: the blower sits toward the USB-A / Ethernet end
Z_COOLER_TOP         = PI_Z_TOP + COOLER_BASE_ABOVE_BOARD + COOLER_H   # 19.28
FAN_PLENUM_MIN       = 8.0                             # ASSUMED minimum free air above a blower's intake

# ------------------------------------------------------------- motor  JD-Power MY-3514C (2804) - carried from v9
MOTOR_FILE           = "JD-Power_MY-3514C_2804_gimbal_motor.step"
MOTOR_OD, MOTOR_H    = 35.00, 14.00      # MEASURED envelope
MOTOR_BASE_OD        = 30.00             # ASSUMED - stator base smaller than the bell
MOTOR_BASE_H         = 4.30              # ASSUMED - bell begins here
MOTOR_AZ             = 90.0
MOTOR_BAND_T         = 0.60              # ASSUMED flat silicone band
MOTOR_PRELOAD_N      = 2.4               # RULING 4 Sep
CLUTCH_LIFT          = 2.40

# ------------------------------------------------------------- other bought parts (MEASURED from their STEP files) - carried
WHEEL_OD, WHEEL_W, WHEEL_BORE = 13.20, 4.00, 3.00
WHEEL_V_H, WHEEL_V_FLAT = 1.30, 0.60
WHEEL_ECC            = 0.90
BUSH_D, BUSH_FLANGE_D, BUSH_HEX = 5.00, 7.00, 2.00
BUSH_FLANGE_T        = 0.60
WHEEL_AZ             = [30, 150, 270]                  # v10: clear of the speaker cradle, the deck boards and the port slot
SERVO_L, SERVO_W, SERVO_H, SERVO_STROKE = 21.4, 15.2, 6.0, 9.0   # AGFRC envelope
ENC_AZ               = 310.0                           # on the seat flange between the wheel notch at 270 and the nub at 330
STRIP_T              = 0.15
LRA_L, LRA_H         = 10.0, 4.37
LRA_AZ               = 258.0
SPEAKER_D, SPEAKER_T = 40.0, 9.05                      # placement below with the boards
# halo: a bought addressable LED STRIP stuck to the outside of the structure's wall, firing outward (RULING 5 Sep evening: a strip, not discrete LEDs laid flat)
LED_STRIP_W          = 5.0                             # ASSUMED strip width (5 mm WS2812B-2020 / SK6812 class, ~100 LEDs per metre); a 8 or 10 mm strip makes the halo band taller by the difference
LED_STRIP_T          = 1.6                             # ASSUMED strip thickness including the LEDs
LED_PER_M            = 100                             # ASSUMED strip density (WS2812B-2020 class)
LED_MA_FULL_WHITE    = 48                              # PUBLISHED WS2812B-2020: 16 mA per colour channel, 48 mA per LED at full white (0.24 W) - the design-changes item 4 method: count = circumference x density, current = count x 48 mA
USBC_ABOVE, USBC_BELOW = 1.06, 2.10                    # GCT mid-mount
JACK_AXIS_ABOVE_BOARD = 3.00

# ------------------------------------------------------------- z stack (spec section 8.3, option A', 8 mm plate, display bonded to its carrier ring)
PAD_T                = 1.50
PLATE_T              = 8.00                            # RULING 5 Sep (question 4)
Z_PLATE_TOP          = PLATE_T                         # 8.0
CARRIAGE_T           = 4.20
Z_MOTOR_BOT          = CARRIAGE_T                      # 4.2
Z_MOTOR_TOP          = Z_MOTOR_BOT + MOTOR_H           # 18.2
Z_BELL_BOT           = Z_MOTOR_BOT + MOTOR_BASE_H      # 8.5
HALO_Z0              = Z_PLATE_TOP                     # 8.0
HALO_H               = LED_STRIP_W + 0.5               # 5.5: the strip stands vertically on the wall's outer face
HALO_Z1              = HALO_Z0 + HALO_H                # 13.5
LIP_T                = 0.80
Z_LIP0, Z_LIP1       = HALO_Z1, HALO_Z1 + LIP_T        # 13.5 - 14.3 diffuser-retaining lip
Z_SKIRT_BOT          = Z_LIP1 + 0.60                   # 14.9: the knob's lowest point, over the lip
Z_DRIVE0, Z_DRIVE1   = Z_BELL_BOT + 0.5, Z_MOTOR_TOP - 0.4   # 9.0 - 17.8 band on the bell, as v11 (v12 had narrowed it to 16.9 to drop the code band; v13 has no code band on the bore): the bore meets it over 14.9-17.8, its lowest point being the skirt's bottom over the halo lip
COOLER_FAN_FITTED    = False                           # BUILD CHANGE 5 Sep: heatsink only, fan off (v12: the adapter sits 1.5 over the fins - a fan has no room)
Z_HEATSINK_TOP       = PI_Z_TOP + COOLER_BASE_ABOVE_BOARD + (COOLER_H - 6.7)   # 12.58 fins' top (ASSUMED split)
# v13: the encoder faces UP at a code ring on the crown's underside (Ryan, 6 Sep) - nothing on the bore any more
ENC_GAP              = 2.00                            # PUBLISHED AEDR-8300 typical gap to the reflective surface
ENC_PKG_H            = 1.63                            # MEASURED package height (STEP)
ENC_BOARD_T          = 1.0                             # ASSUMED 8 (radial) x 12 (tangential) board, sensor centred, two M2 holes at t +-4.75
CODE_R0, CODE_R1     = 72.5, 79.5                      # the code ring on the crown's underside (the lens overhang ends at r 70; the bore at 83.2); 0.15 recess for a stuck film ring on the prototype, laser-marked anodise in production
ENC_R                = (CODE_R0 + CODE_R1) / 2         # 76.0 sensor centre radius; 478 mm round = about 6,000 lines at the sensor's 0.08 mm pitch
# the adapter driver board over the Pi on standoffs (v12): the tallest thing under the seat is its HDMI socket
STANDOFF_L           = 12.0                            # PUBLISHED M2.5 x 12 hex standoff (5 AF), on the Pi's four holes
Z_ADAPTER0           = PI_Z_TOP + STANDOFF_L           # 14.78 board underside: 1.2 over the heatsink's fins with 1.0 of underside parts, 0.3 over the servo's frame (14.5). Its HDMI socket top (23.7) is 2.3 under the seat: the wheels set the seat, not the adapter
Z_SEAT_WHEELS        = Z_DRIVE1 + 0.3 + 6.1            # 24.2: what the wheels allow - their groove 0.3 above the drive band, then 1.6 to the ridge, 2.0 to the wheel's top, 0.5 to the flange, 2.0 flange
Z_SEAT_TOP           = 26.00                           # v13: set by the adapter's HDMI socket (23.68 + 0.3 + the 2.0 flange = 25.98); the wheels would allow 24.2. v12: 28.0 (code band on the bore); v11: 30.4
BOND_T               = 0.50                            # ASSUMED double-sided foam bonding tape (RULING 5 Sep: glue allowed for the display)
Z_GLASS0             = Z_SEAT_TOP + BOND_T             # 30.9 glass back
Z_GLASS1             = Z_GLASS0 + PANEL_T              # 33.28
Z_LENS1              = Z_GLASS1 + LENS_T               # 35.78
RIM_GAP, CROWN_T     = 0.40, 3.00
Z_CROWN_BOT          = Z_LENS1 + RIM_GAP               # 31.38 lip underside
Z_KNOB_TOP           = Z_CROWN_BOT + CROWN_T           # 34.38 (v12 36.38, v11 39.18)
Z_CODE_FACE          = Z_CROWN_BOT + STRIP_T           # 31.53: the code ring's reflective face, in a 0.15 recess in the crown's underside
Z_ENC_FACE           = Z_CODE_FACE - ENC_GAP           # 29.53 the sensor's optical face
ENC_BOARD_Z0         = Z_ENC_FACE - ENC_PKG_H - ENC_BOARD_T   # 26.90 board underside, on a 0.9 boss on the seat flange's top face
ENC_BOSS_H           = ENC_BOARD_Z0 - Z_SEAT_TOP       # 0.90: v15 this is a SEPARATE printed shim (encoder_shim) between the flange top and the board, not a boss - the flange top is the print bed. Printed as a family in 0.1 steps, the height chosen on the bench
ENC_SHIM_FAMILY      = [0.7, 0.8, 0.9, 1.0, 1.1]       # the shims printed; 0.9 is nominal (the 2.0 optical gap)
ENC_SLOT_RADIAL      = 0.5                             # the flange's two M2 holes are radial slots +-0.5, so the sensor can also be centred over the code ring
UNDER_BOSS_D, UNDER_BOSS_H = 5.0, 4.0                  # v15: every fixing in the seat flange takes its insert or pin in a Ø5 boss hanging 4 UNDER the flange (z 20-24) - they print upward in the inverted orientation
PIN_D, PIN_L         = 2.0, 8.0                        # v15: the three display-locating nubs become ISO 8734 Ø2 m6 x 8 dowel pins pressed from below through Ø2 H7 holes in the flange (reamed) and its bosses: 5.8 of grip (z 20.2-26), 2.2 proud, top 0.3 under the glass's top face (28.18)
HEIGHT               = Z_KNOB_TOP + PAD_T              # 40.68
# wheels just under the seat, above the code band
Z_WHEEL1             = Z_SEAT_TOP - 2.0 - 0.5          # 23.5 (collar top 0.5 under the seat's underside 24.0)
Z_WHEEL0             = Z_WHEEL1 - WHEEL_W              # 19.5
Z_RIDGE_MID          = (Z_WHEEL0 + Z_WHEEL1) / 2       # 21.5
Z_GROOVE0            = Z_RIDGE_MID - WHEEL_V_H - WHEEL_V_FLAT/2   # 19.9 (2.1 above the drive band)
Z_GROOVE1            = Z_RIDGE_MID + WHEEL_V_H + WHEEL_V_FLAT/2   # 23.1
Z_POST_TOP           = Z_WHEEL0 - BUSH_FLANGE_T        # 18.9
Z_SEAT_BOT           = Z_SEAT_TOP - 2.0                # 24.0 seat flange
KNOB_FRACTION        = (Z_KNOB_TOP - Z_SKIRT_BOT) / Z_KNOB_TOP

# ------------------------------------------------------------- radii (spec 8.1)
R_PIC                = PANEL_ACTIVE_R                  # 63.5
R_CROWN_IN           = R_PIC + 0.70                    # 64.2 lip inner edge (ASSUMED 0.7 hidden border)
RIM_FLAT             = 20.0                            # RULING 6 Sep: the knob's top is a flat rim of at least 20 mm between the two chamfers (v10: 9.3)
R_KNOB               = R_CROWN_IN + 1.00 + RIM_FLAT + 2.50   # 87.7: lip edge + 1.0 inner chamfer + 20 flat + 2.5 outer chamfer (Ø175.4)
SKIRT_WALL           = 4.50                            # the knob's wall as v10: 1.0 knurl + 3.5 under the root (RULING 6 Sep: the knob keeps v10's shape, only the rim grows)
R_BORE               = R_KNOB - SKIRT_WALL             # 83.2 (Ø166.4): the bore is no longer set by the panel's chin (72.05) - everything inside scales out to it (RULING 6 Sep)
R_WALL_OUT           = R_BORE - GAP_ROTATE             # 82.8: the structure's wall 0.4 inside the bore, as v10
R_WALL_IN            = R_WALL_OUT - WALL_MIN           # 81.2
R_GROOVE_ROOT        = R_BORE + WHEEL_V_H              # 84.5
WHEEL_AXIS_R         = R_GROOVE_ROOT - WHEEL_OD/2 - 0.07   # 77.83
BUSH_R               = WHEEL_AXIS_R - WHEEL_ECC        # 76.93
WHEEL_POST_D         = 8.00
R_SEAT_IN            = 62.00                           # the seat's inner edge stays at the glass (the flange is now 62-82.8; the glass bonds at 62.5-65.6, the lens overhang ends at 70)
NUB_AZ               = [70, 210, 330]                  # the three display-locating pins around the glass edge (off the panel's 5 mm ears at 90/270); v15: 60 -> 70, out from under the blower's saddle
MOTOR_R              = R_BORE - MOTOR_OD/2             # 65.7 engaged centre radius (v10: 55.0); ratio bore/bell 4.75
R_STRIP_BACK         = max(R_WALL_OUT + 1.1, MOTOR_R + MOTOR_OD/2 + MOTOR_BAND_T + 0.1)   # 83.9: the wall's outer face in the halo band (a 1.1 band on the wall), outside the bell + band's reach (83.8)
R_STRIP_IN, R_STRIP_OUT = R_STRIP_BACK + 0.1, R_STRIP_BACK + 0.1 + LED_STRIP_T   # 84.0 - 85.6
LED_N                = int(2 * _m.pi * (R_STRIP_IN + R_STRIP_OUT) / 2 / 1000 * LED_PER_M)   # 53 at r 84.8 (533 mm)
HALO_PEAK_A          = LED_N * LED_MA_FULL_WHITE / 1000   # 2.54 A at full white (12.7 W at 5 V) - sizes the converter, the halo feed and its connector; no sustained cap (HALO-BRIGHTNESS: a ten-minute rolling mean in firmware)
R_DIFF_IN            = R_STRIP_OUT + 0.2               # 85.8: the diffuser 0.2 in front of the strip, as v10
R_DIFF_OUT_BOT       = R_KNOB - 1.0                    # 86.7 (RULING 5 Sep review: a 1.0 lean over the band's 5.5)
R_DIFF_OUT_TOP       = R_KNOB                          # 87.7
DIFF_CHAMFER         = 0.50
R_LIP_OUT            = R_KNOB - 1.0                    # 86.7: the diffuser-retaining lip over the strip's top edge, as v10
PLATE_R              = R_KNOB                          # 87.7 - the plate's edge (the lands and blocks) is flush with the knob; RULING 5 Sep review 2: engine-turned edge
# v14: the rim's edge face is PLAIN (the engine turning is removed - design-changes item 5; the replacement treatment is chosen separately). The vent openings stay parametric below.
PAD_R                = PLATE_R - 3.0                   # 84.7: RULING 5 Sep review: pad slightly smaller than the plate (top face; 0.5 lean to the underside)
PLATE_CHAMFER        = 0.3                             # v15 (item 5): 0.3 x 45 polished on both of the ring's outer edges (v14 1.0); the diffuser's seat is at r 85.8-86.7, unaffected
MOTOR_CLEAR          = 2.0
PILLAR_AZ            = [160, 240, 320]                 # M3 pillars on the wall for the plate screws from below (v12: the two deck-only pillars at 50 and 180 are gone with the deck; 120 moved to 160, out of the speaker's way)
PLATE_SCREW_AZ       = [160, 240, 320]                 # ... and plate screws from below at three of them
PILLAR_R             = R_WALL_IN - 4.0                 # 77.2 (v10: 66.5 = 70.5 - 4)
PORT_W               = 44.0                            # port slot width (tangential) - three sockets
PORT_NOTCH_R0        = 55.0                            # slot in the plate from here to the rim (clear of the Pi's USB-A end at 46.4)
PORT_FACE_R0, PORT_FACE_T = R_WALL_IN - 1.5, 1.5        # 79.7-81.2: the face at the wall's inner face, as v10 (69.0 = 70.5 - 1.5); the sockets sit 6.5 inside the edge
PORT_TAB_R, PORT_TAB_T = PORT_FACE_R0 - 1.5, PORT_W/2 + 4.0   # 78.2, +-26: the port face's rail screws to the plate top beside the slot (inside the wall), M2 into tapped holes
PILLAR_TOP           = Z_PLATE_TOP + 8.0               # 16.0: insert + 2 of roof; nothing screws in from above any more
# ------------------------------------------------------------- the base plate as the heatsink (the60-thermal-plan.md section 14, RULINGS 6 Sep: steel rim ring, converter on the plate, rear exhaust through the pad)
RIM_IN               = PORT_TAB_R - 3.0                # 75.2: the solid 8 mm rim runs from here to the edge (rule 4: 3 inboard of the port face's holes, well inboard of the diffuser's seat at 85.8)
RIM_STEP_W, RIM_STEP_Z = 3.0, 5.0                      # the steel rim ring's inward flange (r 72.2-75.2, z 5-8) sits in a rebate on the aluminium core; 7 x M3 csk from below through the core's shoulder (v14: the shoulder is 5 tall so the intake grooves can be 3.5 deep through it and leave 1.5)
R_CORE_DUCT          = RIM_IN - RIM_STEP_W             # 72.2: the ducted region and the closing plate end here
WEB_T, DUCT_H, CLOSING_T = 2.0, 5.0, 1.0               # v15 (design-changes item 1, rule 5): 2 web (z 6-8), 5 duct (z 1-6), 1 closing plate (z 0-1) in a recess, flush. v14: 4/3/1
PIER_D, PIER_H       = 7.0, 2.5                        # v15: every screw from the top lands on a Ø7 pier hanging 2.5 into the duct (z 3.5-6) - 4.5 of metal for 3.5 of thread, 2.5 of duct left under it; the channels run on beneath
GASKET_T             = 0.2                             # v15 (rule 5): ASSUMED die-cut PTFE/foam gasket 0.2 in a 0.2 groove of the recess floor, on every wall the closing plate seals against (the duct's outer wall and the walls round the three through-cuts)
FIN_PITCH, FIN_CH_W  = 4.0, 3.0                        # rule 11: straight channels 3 wide x 5 tall (v15; v14 3 tall) on a 4 pitch (1 mm fins), running front-to-rear in the bands beside the Pi window, finned over their full length (with a blower fitted the 8 Pa the fins cost is not the constraint - design-changes item 2 asked for fins over the hot spots only, but the compute module sits in a window through the duct, not on the web: there are no channels under it or under the converter)
DUCT_WALL            = 2.0                             # the duct's outer wall r 70.2-72.2, z 1-4: what ties the core's shoulder (under the ring's flange) to the web; the intake and exhaust grooves cut through it
DUCT_MARGIN          = 2.5                             # solid wall left around every through-cut (Pi window, carriage hole, port slot) so the duct does not leak into them
COLLECTOR_R0         = 66.0                            # a collector channel r 66-72.2 round the front and sides (az 50-310) joins the intake grooves to the fin channels
PLENUM_R0            = 55.0                            # the rear plenums r 55-70.2 at az 22-66 (+y, v15: extended so every channel truncated by the trench zone still ends in it) and 308-338 (-y), where the channels end
TRENCH_ZONE_AZ       = (40.0, 61.0)                    # v15: between these azimuths the duct is solid outside r 64.8 (the trench sits in it): the channel ends that would have met the trench are stopped at r 64.8 in the plenum's suction side, and the collector starts at 61
# v15: the blower is a FITTED, REQUIRED part (Ryan, 6 Sep). Delta BFB0305HA-C (PUBLISHED, its specification in vendor/): 30 x 30 x 10, 5 V 0.13 A 0.65 W,
# 7500 rpm, 0.041 m3/min = 0.68 L/s free air, 71 Pa at no flow, 29 dB(A), two ball bearings, 10 g, two Ø2.4 holes on a 24 x 24 diagonal, AWG 30 leads 145 long.
# No blower with a usable curve is 5 mm thick, so it stands ON the plate over the +y rear plenum, inlet face DOWN on a gasket over a hole through the web
# (it breathes only duct air), its side outlet into a printed hood that turns the air down a trench cut from the top through the web, the duct wall,
# the core's shoulder, a notch in the ring's flange and the ring's inner land into the ring's rear exhaust groove. The motion board rides on the saddle's top.
BLOWER_AZ, BLOWER_R  = 51.0, 51.0                      # its centre: the 30 x 30 body r 36-66, over the channels' rear ends and the 22-52 plenum; corners 2 off the Pi's USB-A shells and 5 off the chassis bond
BLOWER_L, BLOWER_W, BLOWER_H = 30.0, 30.0, 10.0        # PUBLISHED outline
BLOWER_INLET_D       = 24.0                            # ASSUMED from the drawing (the impeller shows through a Ø24 opening in the inlet face)
BLOWER_OUTLET_W, BLOWER_OUTLET_H, BLOWER_OUTLET_Z0 = 21.0, 7.0, 1.5   # PUBLISHED 21 wide; ASSUMED 7 tall from 1.5 above the inlet face; on the +radial (outer) edge
BLOWER_HOLE_D, BLOWER_HOLE_PITCH = 2.4, 24.0           # PUBLISHED: two holes on the diagonal
BLOWER_GASKET_T      = 0.3                             # ASSUMED closed-cell foam ring under the inlet face (OD 30, ID 25) and under the hood
Z_BLOWER0            = Z_PLATE_TOP + BLOWER_GASKET_T   # 8.3
Z_BLOWER1            = Z_BLOWER0 + BLOWER_H            # 18.3
WEB_INLET_D          = 22.0                            # the hole through the web under the inlet (inside the Ø24 opening, so the gasket seats on metal all round)
SADDLE_T             = 1.2                             # the printed saddle: a plate on the blower's top; the motion board on four 0.5 washers on it (the plate's top is flat: it is the print bed). ONE bolt stack: two M2 x 18 pan heads through the board's diagonal holes, the washers, the plate and the blower's own holes into the piers (board 1.6 + pad 0.5 + plate 1.2 + blower 10 + gasket 0.3 + 3.5 of thread)
MOTION_HOLE_OFF      = 12.0                            # v15: the motion board's holes at +-12 (ASSUMED layout) so two of them sit on the blower's 24 x 24 diagonal
TRENCH_W             = 18.0                            # the discharge trench (tangential), z 1-8: 18 x 7 = 126 mm2 - the hood covers it
TRENCH_R0            = 66.8                            # from here (2 of wall to the suction side of the plenum) out through the duct wall and the shoulder into the ring
TRENCH_FOOT_AZ       = (37.0, 56.0)                    # from r 72.2 outward the trench widens along the arc: the ring's flange is notched and its inner land cut away between these azimuths, so the exhaust groove is fed over 24 of its 42 degrees
TRENCH_FILLET        = 2.5                             # v15 review: the trench's vertical corners rounded (a Ø5 cutter)
TRENCH_R1            = 79.0                            # the trench (and the exhaust groove's open top) end here; the hood's lid seals to r 80.5, 0.7 inside the wall
HOOD_W, HOOD_T       = 24.0, 1.2                       # the hood over the outlet: 24 wide (tangential) x 6 (radial) x to the blower's top, walls 1.2; its lid over the trench foot 1.5 thick
HOOD_SCREW_AZ, HOOD_SCREW_R = [35.0, 58.0], 74.5       # the lid's two M2 into tapped holes 3 deep in the ring's flange (r 72.2-75.2, z 5-8) and the root of its inner land, 2 deg outside the flange notch's walls, inboard of the exhaust groove (r 76.5)
HOOD_LID_AZ          = (33.5, 59.5)                    # the lid's extent: 1.5 mm clear of the wheel post's web at 30 and of the groove wall at 60
FAN_HEADER_XY        = (PI_X0 + 66.75, PI_Y0 + PI_W - 4.0)   # (14.75, 14): the Pi 5's 4-pin fan connector - the vendor STEP carries it (pi_part_13, 3 x 6 x 4.2 at x 13.3-16.2, y 11-17), between the corner standoff and the USB-A stack. v15 review: the first guess (10, 14) sat on the standoff (JST SH 1.0 mm: 5 V, GND, PWM, tach) - position on the board to confirm; the blower's 2-wire lead gets a crimped SH housing on 5 V and GND, PWM speed control comes from the Pi (bench: the header's current rating)
INTAKE_AZ0, INTAKE_AZ1 = 60.0, 300.0                   # v15 (design-changes item 3): the intake arc - the ring's groove and its openings run 60-300; exhaust arcs either side of the port face
INTAKE_UNDERCUT_H, INTAKE_UNDERCUT_R = 0.8, PAD_R      # v15: the undercut under the ring's outer wall, r 84.0-87.7, 0.8 tall (v14 1.5): it opens straight into the underside groove all round both arcs, so it is the supplementary intake AND the downward exhaust (rule 7 and 10) - no pad voids needed. Shorter so the openings above keep 0.75 of wall under them
INTAKE_N, INTAKE_W, INTAKE_H = 24, 9.0, 3.5            # the THROAT passages (v15: 9 wide; v14 7): 24 positions on 11.25 deg over 45-315, cut only inside the intake arc (17 of them, 535 mm2): radial grooves 3.5 deep in the ring's inner land (the pad closes them) joining the groove, and closed tunnels z 1-4.5 through the core's shoulder into the collector. 9 wide leaves 5.5 of land for the ring screws' countersinks (Ø4.6 where the tunnel starts)
INTAKE_PASS_AZ0, INTAKE_PASS_AZ1 = 45.0, 315.0          # the passage grid (unchanged from v14 so the ring screws stay on its lands)
EXHAUST_AZ           = [311.0, 320.0, 329.0]           # v15: the -y (passive, 7-channel) circuit's exhaust passages, 10 wide, into the 300-342 groove between the ring screws at 303.75 and 337.5. The +y circuit exhausts through the blower's trench instead
EXHAUST_W            = 10.0
EXHAUST_ARCS         = [(18.0, 60.0), (300.0, 342.0)]  # the ring's exhaust grooves and openings (design-changes item 3: 16-60 and 300-344, pulled in 2 deg so the groove ends 1.5 clear of the port slot's walls)
# v15 ring (design-changes items 3, 5, 6): 120 openings on 3 deg through the ring's outer wall into an underside groove the pad closes
VENT_N, VENT_W, VENT_H = 120, 2.0, 4.5                 # obround openings 2.0 (tangential) x 4.5 (z), on az 1.5 + 3k, mirrored about 0-180; cut only where the groove lies behind them (64 intake, 28 exhaust; none across the port face 342-18 or over the motor's carriage hole and its mirror)
VENT_SKIP_ARCS       = [(79.0, 101.0), (259.0, 281.0)] # v15 review: the carriage hole (the motor's shoe, Ø38.5 at r 65.7) reaches r 85 and cuts the groove over az 81-99, so openings there would open into the cavity, not the duct - eight are not cut, and the eight opposite are not cut either so the two side views stay identical (Ryan: mirrored). The groove and the undercut are interrupted over 79-101 (solid) for the same reason
PILLAR_LAND_D        = 9.0                             # the structure's three M3 plate screws (r 77.2, az 160/240/320) come up through the ring's inner land: a Ø9 land is left standing in the groove round each so the countersunk head bears on metal
VENT_Z0              = 1.55                            # z 1.55-6.05 (item 3 said 1.25-5.75 against a 5 mm duct; the groove decouples them - raised so 0.75 of wall stays under each opening above the undercut); the chamfered mouth reaches 6.35, the top chamfer starts at 7.7
VENT_CHAMFER         = 0.3                             # 0.3 x 45 deg at every mouth and both of the ring's edges, polished (item 5) - modelled as a 45 deg taper on the mouth
RING_WALL_R0         = 84.0                            # the ring's outer wall r 84.0-87.7 (3.7 thick): what the openings pass through
GROOVE_R0, GROOVE_R0_EXH, GROOVE_R1 = 79.5, 76.5, 84.0 # the underside groove r 79.5-84 (intake arc) and r 76.5-84 (exhaust arcs, wider: they are fed from one end); open at the bottom, the pad closes it
GROOVE_Z1            = 6.55                            # the groove's roof at 6.55 (0.5 over the openings' top; 1.45 of roof)
GROOVE_WALL_DEG      = 1.2                             # the wall left between the intake and exhaust arcs at 60 and 300 (about 1.7 mm at r 82)
# v15 review (Ryan, 7 Sep): NO reeding on the edge face - the three grooves left 0.15 mm lands between them ("razor blades") and their lowest one clipped the openings' chamfered tops. The upper land is plain.
RIB_T, RIB_H         = 2.0, 6.0                        # rule 13: tall sparse ribs on the plate's top face
RIB_R0, RIB_R1       = 56.0, 70.0                      # inside r 70: clear of the pillars (73.7-80.7) and posts, so the structure still enters from below
RIB_AZ               = [158, 212]                      # v12: the plate top is nearly full - two free radial lines: between the speaker and the converter, and between the converter and the USB-C plug (v11 had ten)
RIB_R0_BY_AZ         = {212: 63.5}                     # v15 review: the 212 rib started at r 56, through the Pi's corner standoff at r 59.5 (hidden by a checker rule since v12) - it now starts at 63.5
CLOSING_SCREW_XY     = [(-60.0, 0.0), (-56.0, 16.0), (-56.0, -16.0), (44.0, 10.0), (44.0, -22.0), (56.0, 31.0), (56.0, -31.0), (0.0, 45.0), (0.0, -57.0)]   # 9 x M2.5 csk from below (v15: three more, so the 1 mm plate's free span is about 30 mm, not 60): the front crescent beyond the Pi window, the rear wedge inside the port slot's walls, one island in each rear plenum, and one in each channel band on a full-depth island the channels are linked round
ISLAND_LINK_L        = 6.0                             # the cross-cut either side of a channel-band island, joining the blocked channel to its neighbours
RING_SCREW_AZ, RING_SCREW_R = [22.5, 78.75, 135, 191.25, 247.5, 303.75, 337.5], 73.7   # 7 x M3 csk from below through the core's shoulder into the ring's flange, on lands between the passages (the openings never reach r 73.7: they stop at the groove)
USBC_NOTCH_AZ        = 231.0                           # the intake groove nearest this azimuth is dropped: the Pi's USB-C plug notch reaches r 71.5 there and the groove would leak into it
PAD_RIN              = RIM_IN - 0.2                    # 75.0: the pad is a plain ring under the rim (rule: it is no longer part of the airflow)
PLATE_MATERIAL       = "6082 aluminium; EXTERNAL faces black hard anodised, every INTERNAL face chromate conversion or bare (design-changes item 2, 6 Sep) - no masked pads anywhere"
RIM_RING_MATERIAL    = "stainless steel (304 or 316), finished BARE: edge face brushed axially, the 0.3 chamfers at every opening mouth and both edges polished - electropolish after machining, brush after (design-changes item 5; RULING 6 Sep: a steel ring for mass, stainless 6 Sep evening)"

PORT_BARREL_T, PORT_USBC_T, PORT_JACK_T, PORT_LIGHT_T = -15.0, -3.0, 9.0, 19.0   # tangential positions on the port face
SENSOR_HOLE_D        = 4.8
# perimeter vents: vertical slits all round the wall (RULING 5 Sep review: slits, not round holes - many, easy to print)
SLIT_W               = 1.0                             # slit width (tangential)
SLIT_Z0, SLIT_Z1     = Z_DRIVE1 + 0.7, Z_SEAT_BOT - 1.0   # 18.5 - 23.0: above the drive band, under the seat
SLIT_PITCH_DEG       = 2.5                             # 144 positions; skipped at the motor, the pillars' and posts' webs, the encoder tower and the LRA pad
BARREL_AXIS_Z        = 3.5                             # spec 6.8: right-angle plug body Ø8.5 -> z -0.75..7.75, pad pocketed under it
USBC_AXIS_Z          = 4.5
JACK_AXIS_Z          = 4.6                             # 6 Sep: jack above its board (pins down into the pad's slot void, 0.5 above the desk plane) - the board used to sit above the plate top under the wall and the LED strip

# ------------------------------------------------------------- the boards, all on the plate (v12, RULING 6 Sep: no deck)
BOARD_STANDOFF       = 1.0                             # ASSUMED 0.5-1.0 nylon washers under every board bolted to the plate top (solder stubs); M2.5 x 4 into tapped blind holes 3.0 deep in the web
BLIND_D              = 3.5                             # tapped blind holes from the plate top: 3.5 into the 2.0 web + 2.5 pier, 1.0 of floor left under each (v14: 3.0 in a 4.0 web)
# adapter driver board DM-ADTTR-014 (PUBLISHED drawing, datasheet 1.5.1): 65 x 64, four Ø2.8 holes on the Pi's 58 x 49 pattern (3.5 from the HDMI edge
# and both sides, 11.5 from the flex-connector edge), HDMI-A socket 15.7 wide x 10.5 deep x 7.3 tall centred 0.5 off the board's middle on the HDMI edge
# (0.8 proud of it), micro-USB 5.5 x 5.7 20.25 beside it, 60-pin flex connector 35 wide x 4.5 deep 1.2 inside the opposite edge, two 3.6 x 6 buttons on the left edge (4.1 tall)
ADAPTER_L, ADAPTER_W, ADAPTER_T = 65.0, 64.0, 1.6      # PUBLISHED outline; ASSUMED 1.6 board
ADAPTER_HDMI_W, ADAPTER_HDMI_D, ADAPTER_HDMI_H = 15.7, 10.5, 7.3
ADAPTER_CN1_W, ADAPTER_CN1_D, ADAPTER_CN1_H = 35.0, 4.5, 2.0    # 60-pin 0.5 mm flex connector (height ASSUMED)
ADAPTER_PARTS_H      = 2.5                             # ASSUMED general parts height (STM32, regulators)
ADAPTER_UNDER_H      = 1.0                             # ASSUMED solder-side stubs
# placement: the right way up on the Pi's standoffs, HDMI edge over the Pi's USB-C/HDMI edge (270 deg side), flex-connector edge toward 90 deg.
# Flipping it was costed (the socket would hang into the space over the Pi's SD end) and buys 0.4 mm: the seat's floor is the wheels' groove
# over the code band, not the socket - so it stays the right way up and its socket faces the same way as the Pi's, a short ribbon between them.
ADAPTER_X0           = PI_X0                           # -52: its left edge on the Pi's SD end (holes 3.5 in, on the Pi's 3.5)
ADAPTER_Y0           = PI_Y0                           # -38: its HDMI edge on the Pi's USB-C edge; it overhangs the header edge by 8 (y 18-26)
ADAPTER_CENTRE       = (ADAPTER_X0 + ADAPTER_L/2, ADAPTER_Y0 + ADAPTER_W/2)   # (-19.5, -6)
Z_ADAPTER1           = Z_ADAPTER0 + ADAPTER_T          # 16.38 board top
Z_ADAPTER_HDMI_TOP   = Z_ADAPTER1 + ADAPTER_HDMI_H     # 23.68 the tallest thing under the seat
# display connect board (PUBLISHED as a part of the adapter kit, dimensions ASSUMED from its photograph): takes the panel's 46 mm flex (CN2) and the
# 150 x 30.6 x 0.34 flat cable (CN1) to the driver board.  On a printed bracket over the port slot, under the seat's flex slot at 0 deg.
CB_L, CB_W, CB_T     = 30.0, 46.0, 1.2                 # radial x tangential (scaled from the photograph: the 60-pin connector nearly spans the long side, the holes just outside it)
CB_R, CB_T0          = 60.5, -4.0                      # centre: r 45.5-75.5 at 0 deg; holes 5.5 in from its outer edge, 3 from the others, t -27..+19 (0.5 past the audio's USB plug; its outer corner 1.0 inside the wall). Off-centre so the panel flex at t -12 meets CN2 8 from the board's middle, off its corner holes
CB_CN2_W, CB_CN2_D, CB_CN2_H = 14.0, 5.0, 2.0          # the panel flex's connector at the +x (outer) edge, at t -12 (under the flex), opening outward
CB_CN1_W, CB_CN1_D, CB_CN1_H = 35.0, 4.5, 2.0          # the 60-pin connector at the inner edge, opening inward
CB_BRACKET_T, CB_BOSS_H, CB_FOOT = 1.5, 2.0, 1.5       # the bracket: a 1.5 slab at z 9.5-11 from r 46 to 78, standing on a 1.5 foot strip (r 46-48) and two ears on the plate, and resting on the port face's rail (z 9.5) at its outer end; four 2.0 bosses with M2 inserts; 2 x M2.5 csk into the web at (46, 17) and (46, -14) (the -y wing beyond that rests on the foot and the rail: the audio's USB plug sits over the plate there)
CB_SCREW_XY          = [(46.0, 17.0), (46.0, -20.0)]   # v15 review: the -y ear moved from -14 to -20, off the audio board's USB-A plug (now in the USB 3.0 stack's lower socket, y -15..-3)
Z_CB0                = Z_PLATE_TOP + CB_FOOT + CB_BRACKET_T + CB_BOSS_H   # 13.0 board underside
CABLE_W, CABLE_T     = 30.6, 0.34                      # PUBLISHED flat cable, 150 long: drawn along its route (about 95 used; the rest is slack)
AUDIO_L, AUDIO_W, AUDIO_H = 40.0, 25.0, 3.6            # Ryan's 40 x 25 (x by y here); 1.6 board + 2.0 Pico-Lock connectors (CONNECTORS: one family, 2.00 mated); its USB link is a moulded pre-made lead, 4.0 allowed at its plug
AUDIO_CENTRE         = (19.0, -52.0)                   # v12: on the plate in the 270-300 crescent beside the Pi's USB-A stacks (its USB plug is 9 away); the speaker went to the other side. Its outer corner (r 75.7) sits on the ring's top
MOTION_L, MOTION_W, MOTION_H = 30.0, 30.0, 3.6         # 1.6 board + 2.0 Pico-Lock connectors (v13 allowed 5.0 JST-SH); its USB link's moulded plug 4.0
CONN_H, USB_PLUG_H   = 2.0, 4.0
MOTION_AZ, MOTION_R  = 51.0, 51.0                      # v15: the board rides on the blower's saddle (the blower took its spot on the plate over the 22-52 plenum): centred on the blower, r 36-66 at 51 deg. v12: on the plate at 50/52
Z_MOTION0            = 18.3 + 1.2 + 0.5                # 20.0: board underside = blower top 18.3 + saddle plate 1.2 + 0.5 washers; its connectors reach 23.6, 0.4 under the seat flange (24.0)
MOTION_USB_PLUG_SIDE = "inner"                         # v15: its USB lead's moulded plug hangs beyond the board's INNER (small-r) edge, z 18-22 (on the outer edge it would sit on the chassis bond)
TOUCH_L, TOUCH_W, TOUCH_H = 30.0, 20.0, 4.0            # ASSUMED touch-controller board
TOUCH_STACK_H        = 3.0                             # stacks on the adapter's top on 3 mm standoffs, over its 2.5 parts
TOUCH_CENTRE         = (-33.0, -17.0)                  # ASSUMED: over the adapter's left half, 1.3 off the HDMI socket, clear of the cable's path over the right half
CONV_L, CONV_W, CONV_H = 38.0, 25.0, 8.0               # ASSUMED 12 V -> 5 V module
CONV_AZ, CONV_R      = 180.0, 65.5                     # v12: turned tangential (38 along the arc) at r 53-78 dead ahead, in the front crescent: its inner edge 1.0 clear of the adapter's edge (x -52) which is 1.7 lower than its top; the outer 6 sits on the ring's top. The pillar the deck needed at 180 is gone
CONV_PAD_T           = 0.5                             # ASSUMED thermal gap pad
CONV_HOLE_T          = 16.0                            # ASSUMED: the module's two holes at t +-16 on its centre line
CONV_RATING_A        = 6.0                             # what the reworked budget needs: Pi 5 ~3 A peak + halo 2.54 A + boards; a 10 A module is no longer required by the halo alone (design-changes item 4) - size from the measured inlet load (bench item)
SERVO_TRAY_T         = 0.0                             # v12: the servo lies straight on the plate in a frame (no floor) - 8.0-14.0
SERVO_EAR_T          = 12.5                            # frame ears at t +-12.5, M2.5 into the web
CARRIAGE_TAB_T, CARRIAGE_TAB_W = 3.0, 10.0
CARRIAGE_TAB_TOP     = Z_PLATE_TOP + SERVO_H + 0.5     # 14.5: the push tab only has to reach the servo's height now (v11: 28.5 through the deck)
SPEAKER_CENTRE       = (-36.0, 47.0)                   # v12: the 90-180 quadrant beyond the adapter's overhang (Ryan's picture: "35 deg" in his frame). Boxed in on four sides: 1.0 beyond the adapter's edge (y 26), 3.1 off the bell and its band, its cradle ring 1.5 inside the wall, 6 off the pillar (moved to 160). az 127.5, r 59.2
SPEAKER_EAR_AZ       = [200.0, 290.0]                  # the cradle's two ears, as azimuths FROM THE SPEAKER'S CENTRE: away from the carriage (0-60), the wall (122) and the Pi/adapter (250-300); M2.5 from above into the web
SPEAKER_FINGER_AZ    = [92.0, 212.0, 332.0]            # the three snap fingers, same convention
GND_BOND_XY          = (48.0, 27.0)                    # THE chassis bond (GROUNDING 3.1): one M3 tapped blind from the top on the free side of the port slot, 45 mm from the barrel inlet (the -y side is taken by the audio board's USB plug and the blower's reserved envelope); a star washer and a ring terminal under the head; the future carrier board's star point lands here. Nothing else bonds to the chassis
RING_BOND_AZ, RING_BOND_R = 67.5, 73.7                 # the rim ring's dedicated bond screw (GROUNDING 4.1): M3 from the top through the ring's flange into the core's shoulder, external-tooth star washer under the head, both faces bare. v15: on the grid land at 67.5 (the passages at 61.9 is not cut, 73.1 is), 3.4 of metal to the passage's wall; 56.25 lay inside the blower trench's foot. 44 mm from the chassis bond
BLEED_AZ, BLEED_R    = 200.0, 71.5                     # the knob's 1 MOhm bleed (GROUNDING 5): a phosphor-bronze leaf with its foot FLAT on the seat flange (v15: no boss - the flange top is the print bed; the M2 insert is in a boss under the flange), bearing lightly UP on the crown's underside at r 71.5 - the smallest radius the knob offers (the lens ends at 70, the code ring starts at 72.5); between the wheel notch at 150 and the nub at 210
BLEED_FOOT_R         = 74.5                            # the leaf's foot and M2 screw
USBC_SHELL_WIRE      = True                            # GROUNDING 6: the USB-C receptacle's shell to the chassis bond by a short wire (modelled); the 3.5 mm jack's shell stays isolated - the port face MUST be an insulator
LRA_BOARD_W, LRA_BOARD_H, LRA_BOARD_T = 7.0, 8.0, 1.0  # ASSUMED: the vibration actuator's pogo-pin board (SYSTEM-REVIEW 6.1): two pins on the LRA's flex-tail pads, held in a printed clip on the wall at 252.5 deg
LRA_POGO_D, LRA_POGO_L = 1.5, 2.2                      # ASSUMED pogo pins, compressed length
HALO_TAIL_AZ         = 64.0                            # v15 review (Ryan: no opening for the halo's lead): the strip's joint (its start and end meet here) and a 4 x 3 notch through the wall's foot; the three-wire tail (5 V, GND, data) goes to a Pico-Lock on the motion board's motor-side edge 20 mm away. The 5 V therefore passes THROUGH the motion board (two paired Pico-Lock contacts per rail, 3 A each, for the 2.54 A peak) - question 32
HALO_TAIL_W, HALO_TAIL_T = 3.0, 1.4                     # the tail as a flat three-wire ribbon
SENSOR_CABLE_LOOP    = 12.0                            # the rotor sensor cable's service loop (SYSTEM-REVIEW 6.2): flex-rated, the carriage moves 2.4 every clutch cycle
USBC_PLUG            = "up-angle"                      # ASSUMED: the Pi's USB-C data lead is an up-angled plug (the straight one reached r 75 through the ring): head 12 x 12.5 x 6.5 beyond the edge, cable stub straight up
HDMI_PORT            = 1                               # the ribbon plugs into HDMI1 (x 39.5 in the Pi's frame) - HDMI0 sits behind the USB-C plug's head

# knurl
KNURL_ON             = True
KNURL_N, KNURL_DEPTH = 78, 1.00                        # 78 starts keep the v9 pitch (7.1 mm) at Ø175.4 (RULING 5 Sep, question 13: keep the pitch)
KNURL_ROWS           = 3                               # v12: three rows on the shorter skirt keep the v11 row height (4.7)
KNURL_ROOT_OFF, KNURL_BAND_OV, KNURL_LAND = 0.50, 0.30, 0.80
KNURL_BANDS          = KNURL_ROWS
CH_TOP, CH_IN, CH_BOT = 2.50, 1.00, 1.20
KNURL_Z0             = Z_SKIRT_BOT + CH_BOT + KNURL_LAND          # 16.9 (the pattern grid starts here)
KNURL_RUNOUT_BOT     = CH_BOT + KNURL_LAND + 0.3                  # 2.3: the lowest band is cut this much further down, so the grooves run out through the bottom chamfer (PRINT: no downward ledge at the knurl's foot when printed top-face-down)
KNURL_Z1             = Z_KNOB_TOP - CH_TOP - KNURL_LAND           # 35.88
KNURL_PITCH          = _m.pi * 2 * R_KNOB / KNURL_N               # 7.11 circumferential
KNURL_ROW_H          = (KNURL_Z1 - KNURL_Z0) / KNURL_ROWS         # 5.47 axial period of the rows
KNURL_HELIX_DEG      = _m.degrees(_m.atan((KNURL_PITCH / 2) / KNURL_ROW_H))   # 33.0

ASSUMED_LIST = [
    ("cover lens", f"Ø{LENS_D} x {LENS_T}", "specified separately; carrier rim and lip overlap designed to it"),
    ("bonding tape", BOND_T, "double-sided foam tape between the seat and the glass edge (RULING 5 Sep: glue allowed for the display)"),
    ("panel back component area", f"{PANEL_COMP_W} x {PANEL_COMP_L} x {PANEL_COMP_H} at {PANEL_COMP_OFFSET}", "position from the drawing's back view"),
    ("Active Cooler position", f"from Pi x {COOLER_X0}, fan from x {FAN_X0}", "no CAD body; footprint and fan position from photographs"),
    ("cooler base above the board", COOLER_BASE_ABOVE_BOARD, "SoC 2.4 + thermal pad"),
    ("fan intake plenum", FAN_PLENUM_MIN, "minimum free height above the blower"),
    ("micro-HDMI receptacles", f"x {PI_HDMI0_X}/{PI_HDMI1_X}", "not in the vendor STEP; drawn as envelopes"),
    ("HDMI ribbon plugs", "12x8x5 micro end, 21x12x6 A end", "flat FPC HDMI cable, 200 mm"),
    ("adapter board thickness and part heights", f"{ADAPTER_T}; parts {ADAPTER_PARTS_H}, underside {ADAPTER_UNDER_H}, flex connector {ADAPTER_CN1_H}", "outline, holes, socket size and position PUBLISHED (datasheet drawing)"),
    ("display connect board", f"{CB_L} x {CB_W} x {CB_T}, connectors {CB_CN1_H}", "part of the adapter kit; size scaled from its photograph, hole positions assumed at the corners"),
    ("Pi standoffs and washers", f"M2.5 x {STANDOFF_L} hex, 0.5 washers", "the adapter stack: closing-plate land / washer / Pi / standoff / adapter"),
    ("USB-C up-angle plug", "12 x 12.5 x 6.5 head", "measure the lead"),
    ("audio / motion / touch / converter boards", "envelopes", "electrical layout not done"),
    ("barrel jack body", "14.4 x 9.0 x 11.0 on a vertical board", "PJ-063AH; CAD body to fetch"),
    ("right-angle barrel plug", "Ø8.5 body", "measure the brick's plug"),
    ("MOTOR_BASE_OD / MOTOR_BASE_H", f"{MOTOR_BASE_OD} / {MOTOR_BASE_H}", "carried from v9"),
    ("MOTOR_BAND_T", MOTOR_BAND_T, "carried from v9"),
    ("servo pushrod", "3 mm bridge to the tab", "carried from v9; servo on the plate in a frame"),
    ("LED strip", f"{LED_STRIP_W} wide x {LED_STRIP_T} thick", "any 5 mm addressable strip; a wider strip raises the halo band"),
    ("blower inlet and outlet", f"inlet Ø{BLOWER_INLET_D} in the face, outlet {BLOWER_OUTLET_W} x {BLOWER_OUTLET_H} from {BLOWER_OUTLET_Z0} up", "from the datasheet drawing (outline, holes and leads PUBLISHED)"),
    ("blower gaskets", f"{BLOWER_GASKET_T} closed-cell foam", "under the inlet face and the hood"),
    ("closing-plate gasket", f"{GASKET_T} die-cut", "in a groove of the recess floor, on every sealing wall"),
    ("Pi 5 fan connector current rating", "0.13 A drawn (0.20 max)", "the connector sits in the vendor STEP; its rating is not published"),
    ("encoder shim family", f"{ENC_SHIM_FAMILY}", "printed; the height is chosen on the bench"),
]
