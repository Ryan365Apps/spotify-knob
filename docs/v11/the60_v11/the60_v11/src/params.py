"""the 60 (Cadrane) — v11 parameter block.  Every dimension lives here.

v11 (2026-09-06): v10 with Ryan's 6 Sep rulings - a 20 mm flat rim on the knob (Ø175.4) and a
thin-walled, hollow knob.  Built from docs/v11/V11-SPECIFICATION.md.  Every number is tagged in the comment beside it:
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
INSERT_M25_D, INSERT_M25_L = 3.5, 4.0                  # PUBLISHED (generic M2.5 insert) - used in the deck legs only
NUT_M25_AF, NUT_M25_T = 5.0, 2.0                       # PUBLISHED DIN 934 M2.5 nut: 5.0 across flats, 2.0 thick
NUT_POCKET_AF, NUT_POCKET_D = 5.15, 1.0                # ASSUMED: hex pocket in the deck's top (light press fit), 1.0 deep; the nut stands 1.0 proud and the board sits on it

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
#   translation only: file x -> device x - 42.5, file y -> device y - 28.
#   USB-A / Ethernet end faces the REAR (0 deg); USB-C / HDMI edge faces 270 deg (the speaker side);
#   40-pin header edge faces 90 deg (the motor side); micro-SD end faces the user.
PI_X0, PI_Y0         = -42.5, -28.0
PI_Z0                = 1.50                            # board underside: micro-SD slot 1.45 above the pad (stands on the pad through the plate window)
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
ENC_GAP              = 2.00
ENC_AZ               = 310.0                           # v10: moved from 330 - clear of the port slot, the pillar at 320 and the speaker's crescent
STRIP_T              = 0.15
LRA_L, LRA_H         = 10.0, 4.37
LRA_AZ               = 258.0
SPEAKER_D, SPEAKER_T = 40.0, 9.05
SPEAKER_CENTRE       = (17.0, -46.0)                   # 270 deg crescent beside the Pi's USB-C edge, clear of the HDMI0 plug (spec 4.7); the deck leg at the Pi's USB-A corner is dropped for it
# halo: a bought addressable LED STRIP stuck to the outside of the structure's wall, firing outward (RULING 5 Sep evening: a strip, not discrete LEDs laid flat)
LED_STRIP_W          = 5.0                             # ASSUMED strip width (5 mm WS2812B-2020 / SK6812 class, ~100 LEDs per metre); a 8 or 10 mm strip makes the halo band taller by the difference
LED_STRIP_T          = 1.6                             # ASSUMED strip thickness including the LEDs
LED_N                = 46                              # informational: 100 per metre at r 74.1
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
HALO_Z1              = HALO_Z0 + HALO_H                # 10.6
LIP_T                = 0.80
Z_LIP0, Z_LIP1       = HALO_Z1, HALO_Z1 + LIP_T        # 10.6 - 11.4 diffuser-retaining lip
Z_SKIRT_BOT          = Z_LIP1 + 0.60                   # 12.0
Z_DRIVE0, Z_DRIVE1   = Z_BELL_BOT + 0.5, Z_MOTOR_TOP - 0.4   # 9.0 - 17.8 band on the bell; the bore meets it only above the skirt's bottom (14.9-17.8)
DECK_T               = 1.50
COOLER_FAN_FITTED    = False                           # BUILD CHANGE 5 Sep: the fan's 34 x 34 intake hole and the 65 x 64 adapter cannot share the deck (V10.md); heatsink stays, fan off
Z_HEATSINK_TOP       = PI_Z_TOP + COOLER_BASE_ABOVE_BOARD + (COOLER_H - 6.7)   # 12.58 fins' top (ASSUMED split)
Z_DECK0              = max(Z_PI_USBA_TOP, Z_COOLER_TOP if COOLER_FAN_FITTED else Z_HEATSINK_TOP, Z_MOTOR_TOP) + 0.5   # 19.48 mezzanine deck underside
Z_DECK1              = Z_DECK0 + DECK_T                # 20.98
DECK_BOARDS_H        = 8.0                             # ASSUMED: tallest board + plug on the deck
BOARD_STANDOFF       = NUT_M25_T - NUT_POCKET_D        # 1.0: the boards sit on the captive nuts (PRINT 5 Sep: no insert bosses on the deck - its top prints on the bed; M2.5 x 4 screws from above into M2.5 nuts held in hex pockets in the deck's top face; nothing under the deck but the three Pi legs)
Z_DECK_BOARDS_TOP    = Z_DECK1 + DECK_BOARDS_H         # 29.28
Z_SEAT_TOP           = 30.40                           # the structure's seat: the display module bonds straight onto it (BUILD CHANGE: no carrier ring - a screwed ring has no room for threads under the glass, and glue is allowed)
BOND_T               = 0.50                            # ASSUMED double-sided foam bonding tape (RULING 5 Sep: glue allowed for the display)
Z_GLASS0             = Z_SEAT_TOP + BOND_T             # 30.9 glass back
Z_GLASS1             = Z_GLASS0 + PANEL_T              # 33.28
Z_LENS1              = Z_GLASS1 + LENS_T               # 35.78
RIM_GAP, CROWN_T     = 0.40, 3.00
Z_CROWN_BOT          = Z_LENS1 + RIM_GAP               # 36.18 lip underside
Z_KNOB_TOP           = Z_CROWN_BOT + CROWN_T           # 39.18
HEIGHT               = Z_KNOB_TOP + PAD_T              # 40.68
# wheels just under the seat, above the code band
Z_WHEEL1             = Z_SEAT_TOP - 2.0 - 0.5          # 27.9 (collar top 0.5 under the seat's underside 28.4)
Z_WHEEL0             = Z_WHEEL1 - WHEEL_W              # 22.8
Z_RIDGE_MID          = (Z_WHEEL0 + Z_WHEEL1) / 2       # 24.8
Z_GROOVE0            = Z_RIDGE_MID - WHEEL_V_H - WHEEL_V_FLAT/2   # 23.2
Z_GROOVE1            = Z_RIDGE_MID + WHEEL_V_H + WHEEL_V_FLAT/2   # 26.4
Z_POST_TOP           = Z_WHEEL0 - BUSH_FLANGE_T        # 22.2
Z_CODE0, Z_CODE1     = Z_MOTOR_TOP + 0.3, Z_MOTOR_TOP + 0.3 + 4.2    # 18.5 - 22.7 code band (AEDR-8300 is 3.96 tall)
ENC_TOWER_TOP        = Z_CODE1 + 2.4                   # 25.1: the tower's top (PRINT: 2.0 of material over the sensor pocket, a 6 mm bridge, instead of 0.3)
ENC_RIB_H, ENC_RIB_W = 0.25, 0.6                       # ASSUMED crush rib in the board slot (slot 1.2, board 1.0: 0.05 interference at the rib)
ENC_BOARD_H          = 11.0                            # ASSUMED 8 x 11 board: dropped through a slot in the seat into the tower's open-topped slot (before the display goes on); the lens above caps it. Its leads go on the exposed part between the tower top and the seat flange
Z_SEAT_BOT           = Z_SEAT_TOP - 2.0                # 28.4 seat flange
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
NUB_AZ               = [60, 210, 330]                  # three locating nubs on the seat around the glass edge (off the panel's 5 mm ears at 90/270)
MOTOR_R              = R_BORE - MOTOR_OD/2             # 65.7 engaged centre radius (v10: 55.0); ratio bore/bell 4.75
R_STRIP_BACK         = max(R_WALL_OUT + 1.1, MOTOR_R + MOTOR_OD/2 + MOTOR_BAND_T + 0.1)   # 83.9: the wall's outer face in the halo band (a 1.1 band on the wall), outside the bell + band's reach (83.8)
R_STRIP_IN, R_STRIP_OUT = R_STRIP_BACK + 0.1, R_STRIP_BACK + 0.1 + LED_STRIP_T   # 84.0 - 85.6
R_DIFF_IN            = R_STRIP_OUT + 0.2               # 85.8: the diffuser 0.2 in front of the strip, as v10
R_DIFF_OUT_BOT       = R_KNOB - 1.0                    # 86.7 (RULING 5 Sep review: a 1.0 lean over the band's 5.5)
R_DIFF_OUT_TOP       = R_KNOB                          # 87.7
DIFF_CHAMFER         = 0.50
R_LIP_OUT            = R_KNOB - 1.0                    # 86.7: the diffuser-retaining lip over the strip's top edge, as v10
PLATE_R              = R_KNOB                          # 87.7 - the plate's edge (the lands and blocks) is flush with the knob; RULING 5 Sep review 2: engine-turned edge
ET_BLOCKS, ET_BLOCK_DEG = 12, 8.0                      # ASSUMED: twelve smooth (polished) blocks 8 deg wide at 0/30/60..., the grooved fields between them
ET_GROOVE_W, ET_GROOVE_D, ET_PITCH = 1.2, 1.0, 2.4     # ASSUMED: square-cut vertical grooves in plan, 1.2 wide x 1.0 deep at 2.4 pitch (laser/waterjet-cuttable in 8 mm)
ET_LAND_MIN          = 0.8                             # ASSUMED: smallest land left at each end of a grooved field
PAD_R                = PLATE_R - 3.0                   # 84.7: RULING 5 Sep review: pad slightly smaller than the plate (top face; 0.5 lean to the underside)
PLATE_CHAMFER        = 1.0                             # top and bottom outer edges (RULING 5 Sep review 2); the top one runs r 86.7-87.7, outside the diffuser's seat (r 85.8-86.7)
MOTOR_CLEAR          = 2.0
PILLAR_AZ            = [50, 120, 180, 240, 320]        # M3 pillars on the wall: deck screws from above at all five; 7.5 deg off the port grid so the ports clear their webs
PLATE_SCREW_AZ       = [120, 240, 320]                 # ... and plate screws from below at three of them
PILLAR_R             = R_WALL_IN - 4.0                 # 77.2 (v10: 66.5 = 70.5 - 4)
PORT_W               = 44.0                            # port slot width (tangential) - three sockets
PORT_NOTCH_R0        = 55.0                            # slot in the plate from here to the rim (clear of the Pi's USB-A end at 46.4)
PORT_FACE_R0, PORT_FACE_T = R_WALL_IN - 1.5, 1.5        # 79.7-81.2: the face at the wall's inner face, as v10 (69.0 = 70.5 - 1.5); the sockets sit 6.5 inside the edge
PORT_TAB_R, PORT_TAB_T = PORT_FACE_R0 - 1.5, PORT_W/2 + 4.0   # 78.2, +-26: the port face's rail screws to the plate top beside the slot (inside the wall), M2 into tapped holes
DECK_R               = R_WALL_IN - 0.5                 # 80.7 (v10: 70.0)
# ------------------------------------------------------------- the base plate as the heatsink (the60-thermal-plan.md section 14, RULINGS 6 Sep: steel rim ring, converter on the plate, rear exhaust through the pad)
RIM_IN               = PORT_TAB_R - 3.0                # 75.2: the solid 8 mm rim runs from here to the edge (rule 4: 3 inboard of the port face's holes, well inboard of the diffuser's seat at 85.8)
RIM_STEP_W, RIM_STEP_Z = 3.0, 4.0                      # the steel rim ring's inward flange (r 72.2-75.2, z 4-8) sits in a rebate on the aluminium core; 7 x M3 csk from below through the core's shoulder
R_CORE_DUCT          = RIM_IN - RIM_STEP_W             # 72.2: the ducted region and the closing plate end here
WEB_T, DUCT_H, CLOSING_T = 4.0, 3.0, 1.0               # rule 5: 4 web (z 4-8), 3 duct (z 1-4), 1 closing plate (z 0-1) in a recess, flush
FIN_PITCH, FIN_CH_W  = 4.0, 3.0                        # rule 11: straight channels 3 wide x 3 tall on a 4 pitch (1 mm fins), running front-to-rear in the bands beside the Pi window
DUCT_WALL            = 2.0                             # the duct's outer wall r 70.2-72.2, z 1-4: what ties the core's shoulder (under the ring's flange) to the web; the intake and exhaust grooves cut through it
DUCT_MARGIN          = 2.5                             # solid wall left around every through-cut (Pi window, carriage hole, port slot) so the duct does not leak into them
COLLECTOR_R0         = 66.0                            # a collector channel r 66-72.2 round the front and sides (az 50-310) joins the intake grooves to the fin channels
PLENUM_R0            = 55.0                            # the rear plenum r 55-72.2 at az 22-50 and 310-338 (either side of the port slot) where the channels end and the exhaust starts
BLOWER_AZ, BLOWER_R, BLOWER_L, BLOWER_W, BLOWER_H = 277.0, 60.0, 18.0, 28.0, 5.0   # rule 12: envelope for a radial blower, part NOT fitted; 3 in the duct + 2 into the web. Under the speaker, in the main duct: the motor's through-hole and the Pi window leave no 30 x 30 spot anywhere in the duct - 28 (tangential) x 18 (radial) is what fits
INTAKE_AZ0, INTAKE_AZ1 = 45.0, 315.0                   # rule 7: intake over the front and sides, not the rear
INTAKE_UNDERCUT_H, INTAKE_UNDERCUT_R = 1.2, PAD_R      # a 1.2 undercut on the bottom outer edge outside the pad, r 84.7-87.7
INTAKE_N, INTAKE_W, INTAKE_H = 24, 6.0, 2.0            # 24 radial grooves 6 wide x 2 deep in the rim's underside (the pad closes them), from the undercut to the duct
EXHAUST_AZ           = [27.0, 34.0, 41.0, 319.0, 326.0, 333.0]   # rule 10: rear only, downward, through a void in the pad, on a different arc from the intake
EXHAUST_VOID         = [(15.0, 46.0), (314.0, 345.0)]  # the pad is cut away over these arcs (from the port slot's edge), r 74-86, so the exhaust grooves open to the desk
RIB_T, RIB_H         = 2.0, 6.0                        # rule 13: tall sparse ribs on the plate's top face
RIB_R0, RIB_R1       = 50.0, 70.0                      # inside r 70: clear of the pillars (73.7-80.7) and posts, so the structure still enters from below
RIB_AZ               = [135, 145, 200, 210, 220, 235, 245, 255, 30, 40]   # the free crescents: front either side of the converter, the 240 sector, the 30-40 sector
CLOSING_SCREW_XY     = [(-52.0, 30.0), (-60.0, 0.0), (-52.0, -30.0), (0.0, 42.0), (-16.5, -35.5), (-31.0, -50.0)]   # 6 x M2.5 csk from below, each in solid web: the front crescent (no channels there) and the walls round the tab slot, HDMI and USB-C notches
RING_SCREW_AZ, RING_SCREW_R = [22.5, 78.75, 135, 191.25, 247.5, 303.75, 337.5], 73.7   # 7 x M3 csk from below through the core's shoulder into the ring's flange, on lands between intake grooves
PAD_RIN              = RIM_IN - 0.2                    # 75.0: the pad is a plain ring under the rim (rule: it is no longer part of the airflow)
PLATE_MATERIAL       = "6082 aluminium, black hard anodised on every face incl. internal; masked bare pads at the ground bond and under the converter"   # rule 1-2
RIM_RING_MATERIAL    = "mild steel, black (RULING 6 Sep: steel ring for mass)"

PORT_BARREL_T, PORT_USBC_T, PORT_JACK_T, PORT_LIGHT_T = -15.0, -3.0, 9.0, 19.0   # tangential positions on the port face
SENSOR_HOLE_D        = 4.8
# perimeter vents: vertical slits all round the wall (RULING 5 Sep review: slits, not round holes - many, easy to print)
SLIT_W               = 1.0                             # slit width (tangential)
SLIT_Z0, SLIT_Z1     = 14.7, 18.2                      # between the halo lip (14.3) and the code band (18.5)
SLIT_PITCH_DEG       = 2.5                             # 144 positions; skipped at the motor, the pillars' and posts' webs, the encoder tower and the LRA pad
BARREL_AXIS_Z        = 3.5                             # spec 6.8: right-angle plug body Ø8.5 -> z -0.75..7.75, pad pocketed under it
USBC_AXIS_Z          = 4.5
JACK_AXIS_Z          = 4.6                             # 6 Sep: jack above its board (pins down into the pad's slot void, 0.5 above the desk plane) - the board used to sit above the plate top under the wall and the LED strip

# ------------------------------------------------------------- deck (mezzanine) layout, device frame (ASSUMED placements, proven by the checker)
ADAPTER_L, ADAPTER_W, ADAPTER_T = 65.0, 64.0, 1.6      # PUBLISHED outline; ASSUMED 1.6 board
ADAPTER_CENTRE       = (4.0, -26.0)                    # BUILD CHANGE: over the Pi's USB-C half of the deck, its +x edge carrying the flex connector and the HDMI socket
ADAPTER_PARTS_H      = 6.5                             # ASSUMED HDMI-A receptacle height
AUDIO_L, AUDIO_W, AUDIO_H = 25.0, 40.0, 6.0            # Ryan's 25 x 40 (radial x tangential); ASSUMED height from the deck top incl. the board
AUDIO_AZ, AUDIO_R    = 110.0, 60.0                     # v11: 10 further out on the Ø161 deck (r 47.5-72.5), clear of the carriage tab and servo tray, which moved out with the motor
MOTION_L, MOTION_W, MOTION_H = 30.0, 30.0, 7.4         # revised from the proposed 50 x 40: the deck's 90 deg sector allows 30 x 30 (V10.md); connectors 5.0 tall
MOTION_AZ, MOTION_R  = 45.0, 55.0                      # v11: r 40-70 at az 45, clear of the servo tray (now at r 19-41) and inside the pillar at 50 and the wheel post at 30
TOUCH_L, TOUCH_W, TOUCH_H = 30.0, 20.0, 4.0            # ASSUMED touch-controller board
TOUCH_STACK_H        = 2.0                             # BUILD CHANGE: the touch controller stacks on the adapter's outer region on 2 mm standoffs (no deck area left)
CONV_L, CONV_W, CONV_H = 38.0, 25.0, 8.0               # ASSUMED 12 V -> 5 V module (spec said 10 tall; 8 fits the deck zone - question 18 revised)
CONV_AZ, CONV_R      = 172.0, 59.5                     # v11: ON THE PLATE (thermal plan rule 15), r 47-72 in the front crescent, on a 0.5 gap pad; 2 x M2.5 into the web
CONV_PAD_T           = 0.5                             # ASSUMED thermal gap pad
CONV_HOLE_T          = 16.0                            # ASSUMED: the module's two holes at t +-16 on its centre line
SERVO_TRAY_T         = 1.5
CARRIAGE_TAB_T, CARRIAGE_TAB_W = 3.0, 10.0              # the tall push tab (rises through the deck to the servo)
CARRIAGE_TAB_TOP     = Z_DECK1 + SERVO_TRAY_T + SERVO_H   # 28.48: the tab top level with the servo's stroke axis zone

# knurl
KNURL_ON             = True
KNURL_N, KNURL_DEPTH = 78, 1.00                        # 78 starts keep the v9 pitch (7.1 mm) at Ø175.4 (RULING 5 Sep, question 13: keep the pitch)
KNURL_ROWS           = 4
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
    ("adapter board", f"{ADAPTER_L} x {ADAPTER_W} x {ADAPTER_T}, parts {ADAPTER_PARTS_H}", "DM-ADTTR-014 outline PUBLISHED; socket position and height assumed"),
    ("audio / motion / touch / converter boards", "envelopes", "electrical layout not done"),
    ("barrel jack body", "14.4 x 9.0 x 11.0 on a vertical board", "PJ-063AH; CAD body to fetch"),
    ("right-angle barrel plug", "Ø8.5 body", "measure the brick's plug"),
    ("MOTOR_BASE_OD / MOTOR_BASE_H", f"{MOTOR_BASE_OD} / {MOTOR_BASE_H}", "carried from v9"),
    ("MOTOR_BAND_T", MOTOR_BAND_T, "carried from v9"),
    ("servo pushrod", "3 mm bridge to the tab", "carried from v9; servo now on the deck"),
    ("LED strip", f"{LED_STRIP_W} wide x {LED_STRIP_T} thick", "any 5 mm addressable strip; a wider strip raises the halo band"),
]
