"""the 60 (Cadrane) — v10 parameter block.  Every dimension lives here.

v10 (2026-09-05).  Built from docs/v10/V10-SPECIFICATION.md with every default in
V10-QUESTIONS.md approved (Ryan, 5 Sep) and one correction: glue is allowed for
securing the display.  Every number is tagged in the comment beside it:
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
INSERT_M25_D, INSERT_M25_L = 3.5, 4.0                  # PUBLISHED (generic M2.5 insert)

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
LED_N                = 90                              # RULING 5 Sep (question 12)
LED_T                = 2.0
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
HALO_H               = 2.60
HALO_Z1              = HALO_Z0 + HALO_H                # 10.6
LIP_T                = 0.80
Z_LIP0, Z_LIP1       = HALO_Z1, HALO_Z1 + LIP_T        # 10.6 - 11.4 diffuser-retaining lip
Z_SKIRT_BOT          = Z_LIP1 + 0.60                   # 12.0
Z_DRIVE0, Z_DRIVE1   = Z_BELL_BOT + 0.5, Z_MOTOR_TOP - 0.4   # 9.0 - 17.8 drive band on the bore
DECK_T               = 1.50
COOLER_FAN_FITTED    = False                           # BUILD CHANGE 5 Sep: the fan's 34 x 34 intake hole and the 65 x 64 adapter cannot share the deck (V10.md); heatsink stays, fan off
Z_HEATSINK_TOP       = PI_Z_TOP + COOLER_BASE_ABOVE_BOARD + (COOLER_H - 6.7)   # 12.58 fins' top (ASSUMED split)
Z_DECK0              = max(Z_PI_USBA_TOP, Z_COOLER_TOP if COOLER_FAN_FITTED else Z_HEATSINK_TOP, Z_MOTOR_TOP) + 0.5   # 19.48 mezzanine deck underside
Z_DECK1              = Z_DECK0 + DECK_T                # 21.28
DECK_BOARDS_H        = 8.0                             # ASSUMED: tallest board + plug on the deck
BOARD_STANDOFF       = 0.8                             # boards sit on 0.8 mm insert bosses on the deck
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
Z_SEAT_BOT           = Z_SEAT_TOP - 2.0                # 28.4 seat flange
KNOB_FRACTION        = (Z_KNOB_TOP - Z_SKIRT_BOT) / Z_KNOB_TOP

# ------------------------------------------------------------- radii (spec 8.1)
R_PIC                = PANEL_ACTIVE_R                  # 63.5
R_CROWN_IN           = R_PIC + 0.70                    # 64.2 lip inner edge (ASSUMED 0.7 hidden border)
R_WALL_IN, R_WALL_OUT = 70.50, 72.10
R_BORE               = PANEL_CHIN_R + 0.45             # 72.5 (0.45 to the chin corners)
R_KNOB               = R_BORE + 4.50                   # 77.0 (1.0 knurl + 3.5 under the root)
R_GROOVE_ROOT        = R_BORE + WHEEL_V_H              # 73.8
WHEEL_AXIS_R         = R_GROOVE_ROOT - WHEEL_OD/2 - 0.07   # 67.13
BUSH_R               = WHEEL_AXIS_R - WHEEL_ECC        # 66.23
WHEEL_POST_D         = 8.00
R_SEAT_IN            = 62.00
NUB_AZ               = [60, 210, 330]                  # three locating nubs on the seat around the glass edge (off the panel's 5 mm ears at 90/270)
LED_R                = 74.3                            # BUILD CHANGE: 1.0 further out than the spec's 73.3 - the bell + band reach r 73.1 at the halo's height on the 8 mm plate
R_LED_FLEX_IN, R_LED_FLEX_OUT = 73.2, 75.4
R_DIFF_IN            = 75.5
R_DIFF_OUT_BOT       = 76.6
R_DIFF_OUT_TOP       = R_KNOB                          # 77.0
DIFF_CHAMFER         = 0.50
R_LIP_OUT            = 76.0
PLATE_R              = 76.5
PAD_R                = 75.5
MOTOR_R              = R_BORE - MOTOR_OD/2             # 55.0 engaged centre radius
MOTOR_CLEAR          = 2.0
PILLAR_AZ            = [50, 120, 180, 240, 320]        # M3 pillars on the wall: deck screws from above at all five; 7.5 deg off the port grid so the ports clear their webs
PLATE_SCREW_AZ       = [120, 240, 320]                 # ... and plate screws from below at three of them
PILLAR_R             = 66.5
PORT_W               = 44.0                            # port slot width (tangential) - three sockets
PORT_NOTCH_R0        = 55.0                            # slot in the plate from here to the rim (clear of the Pi's USB-A end at 46.4)
PORT_FACE_R0, PORT_FACE_T = 69.0, 1.5
PORT_BARREL_T, PORT_USBC_T, PORT_JACK_T, PORT_LIGHT_T = -15.0, -3.0, 8.5, 19.0   # tangential positions on the port face
SENSOR_HOLE_D        = 4.8
PORT_N               = 24                              # perimeter ports on a 15 deg grid
PORT_D               = 4.0                             # RULING 5 Sep (question 10): 24 x Ø4 exhaust
PORT_Z               = 15.0
BARREL_AXIS_Z        = 3.5                             # spec 6.8: right-angle plug body Ø8.5 -> z -0.75..7.75, pad pocketed under it
USBC_AXIS_Z          = 4.5
JACK_AXIS_Z          = 4.0

# ------------------------------------------------------------- deck (mezzanine) layout, device frame (ASSUMED placements, proven by the checker)
ADAPTER_L, ADAPTER_W, ADAPTER_T = 65.0, 64.0, 1.6      # PUBLISHED outline; ASSUMED 1.6 board
ADAPTER_CENTRE       = (4.0, -26.0)                    # BUILD CHANGE: over the Pi's USB-C half of the deck, its +x edge carrying the flex connector and the HDMI socket
ADAPTER_PARTS_H      = 6.5                             # ASSUMED HDMI-A receptacle height
AUDIO_L, AUDIO_W, AUDIO_H = 25.0, 40.0, 6.0            # Ryan's 25 x 40 (radial x tangential); ASSUMED height from the deck top incl. the board
AUDIO_AZ, AUDIO_R    = 110.0, 50.0                     # between the motion board (55) and the converter (150); its 6 mm height fits under the seat flange
MOTION_L, MOTION_W, MOTION_H = 30.0, 30.0, 7.4         # revised from the proposed 50 x 40: the deck's 90 deg sector allows 30 x 30 (V10.md); connectors 5.0 tall
MOTION_AZ, MOTION_R  = 55.0, 45.0                      # between the servo strip and the pillar at 55 (V10.md)
TOUCH_L, TOUCH_W, TOUCH_H = 30.0, 20.0, 4.0            # ASSUMED touch-controller board
TOUCH_STACK_H        = 2.0                             # BUILD CHANGE: the touch controller stacks on the adapter's outer region on 2 mm standoffs (no deck area left)
CONV_L, CONV_W, CONV_H = 38.0, 25.0, 8.0               # ASSUMED 12 V -> 5 V module (spec said 10 tall; 8 fits the deck zone - question 18 revised)
CONV_AZ, CONV_R      = 175.0, 46.0
SERVO_TRAY_T         = 1.5
CARRIAGE_TAB_T, CARRIAGE_TAB_W = 3.0, 10.0              # the tall push tab (rises through the deck to the servo)
CARRIAGE_TAB_TOP     = Z_DECK1 + SERVO_TRAY_T + SERVO_H   # 28.48: the tab top level with the servo's stroke axis zone

# knurl
KNURL_ON             = True
KNURL_N, KNURL_DEPTH = 68, 1.00                        # RULING 5 Sep (question 13): 68 starts keep the v9 pitch at Ø154
KNURL_ROWS           = 4
KNURL_ROOT_OFF, KNURL_BAND_OV, KNURL_LAND = 0.50, 0.30, 0.80
KNURL_BANDS          = KNURL_ROWS
CH_TOP, CH_IN, CH_BOT = 2.50, 1.00, 1.20
KNURL_Z0             = Z_SKIRT_BOT + CH_BOT + KNURL_LAND          # 14.0
KNURL_Z1             = Z_KNOB_TOP - CH_TOP - KNURL_LAND           # 35.88
KNURL_PITCH          = _m.pi * 2 * R_KNOB / KNURL_N               # 7.11 circumferential
KNURL_ROW_H          = (KNURL_Z1 - KNURL_Z0) / KNURL_ROWS         # 5.47 axial period of the rows
KNURL_HELIX_DEG      = _m.degrees(_m.atan((KNURL_PITCH / 2) / KNURL_ROW_H))   # 33.0
SKIRT_WALL           = R_KNOB - R_BORE                 # 4.5

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
    ("servo pushrod", "4 mm bridge to the tab", "carried from v9; servo now on the deck"),
]
