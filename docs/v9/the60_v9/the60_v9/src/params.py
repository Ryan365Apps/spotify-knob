"""the 60 (Cadrane) — v9 parameter block.  Every dimension lives here.

v9 (2026-09-04).  Built from docs/v9/V9-SPECIFICATION.md, which is the agreed
baseline.  Every number is tagged in the comment beside it:
    MEASURED  - read off a CAD file in design/cad/bought-parts
    PUBLISHED - manufacturer figure, not modelled in a file
    ASSUMED   - chosen here; unverified (listed by ASSUMED_LIST at the end)
    RULING    - Ryan's decision, with the date

Units mm, degrees.  z = 0 is the steel plate's underside; the pad is below.
Azimuth: 0 deg = +X = the device's USB-C socket, twelve o'clock, away from
the user (RULING 4 Sep).  Anticlockwise seen from above.

The Waveshare board is placed with its own USB-C edge toward the back, which
is a rotation of -90 deg about Z from the vendor file's frame: a vendor-frame
point (x, y) lands at device (y, -x).
"""
import math as _m
import os as _os

BOUGHT = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                         "..", "..", "bought", "bought-parts"))
STEP   = _os.path.join(BOUGHT, "step")
WAVESHARE_STP = _os.path.join(BOUGHT, "vendor", "Waveshare_ESP32-P4-WIFI6-Touch-LCD-3.4C",
                              "ESP32-P4-WIFI6-TOUCH-LCD-3_4C.stp")

# ------------------------------------------------------------- standing rules
GAP_ROTATE, GAP_STATIC, GAP_RUN = 0.40, 0.15, 0.30   # RULING v1 onward
WALL_MIN = 1.60
INSERT_M3_D, INSERT_M3_L = 4.0, 5.7                    # PUBLISHED (generic M3 insert)

# ------------------------------------------------------------- display (MEASURED, vendor STEP)
DISC_OD, DISC_T      = 115.00, 6.00
ACTIVE_OD            = 87.60
PCB_L, PCB_W, PCB_T  = 85.50, 65.00, 1.60
PCB_OFFSET           = 4.50       # along the board's short axis, toward the header edge
DISC_TO_PCB_TOP      = 7.50       # glass to board top face  (1.5 air gap under the disc back)
PCB_TO_LOWEST        = 6.40       # board bottom to the USB-A bottom (stays: RULING 4 Sep)
DISPLAY_DEPTH        = DISC_TO_PCB_TOP + PCB_T + PCB_TO_LOWEST        # 15.50
DISC_MOUNT_PCD       = 106.07     # 4 x M4 at (+-37.5, +-37.5) vendor frame
DISC_MOUNT_DEPTH     = 3.50       # tapped hole depth: engagement <= 3.5
VENDOR_ROT_DEG       = -90.0      # vendor frame -> device frame
VENDOR_GLASS_Z       = 3.75       # glass z in the vendor file
DISC_MOUNT_AZ_DEV    = [45, 135, 225, 315]   # unchanged by a 90 deg rotation
PMMA_REMOVED         = True       # RULING 4 Sep

# ------------------------------------------------------------- motor  JD-Power MY-3514C (2804)
MOTOR_FILE           = "JD-Power_MY-3514C_2804_gimbal_motor.step"
MOTOR_OD, MOTOR_H    = 35.00, 14.00      # MEASURED envelope (shop designation "35x14")
MOTOR_BASE_OD        = 30.00             # ASSUMED - stator base smaller than the bell
MOTOR_BASE_H         = 4.30              # ASSUMED - bell begins here; MUST be >= this on the real part
MOTOR_AZ             = 90.0              # design choice: away from the posts and the back
MOTOR_BAND_T         = 0.60              # ASSUMED flat silicone band (RULING 4 Sep: flat band)
MOTOR_PRELOAD_N      = 2.4               # RULING 4 Sep: servo pushes directly
CLUTCH_LIFT          = 2.40              # radial retraction for free-spin (v8, carried)

# ------------------------------------------------------------- other bought parts (MEASURED from their STEP files)
WHEEL_OD, WHEEL_W, WHEEL_BORE = 13.20, 4.00, 3.00     # collar over a 623ZZ (10 x 4, bore 3)
WHEEL_V_H, WHEEL_V_FLAT = 1.30, 0.60
WHEEL_ECC            = 0.90
BUSH_D, BUSH_FLANGE_D, BUSH_HEX = 5.00, 7.00, 2.00
BUSH_FLANGE_T        = 0.60
WHEEL_AZ             = [30, 150, 270]                  # RULING 4 Sep (board-edge rule)
SERVO_L, SERVO_W, SERVO_H, SERVO_STROKE = 21.4, 15.2, 6.0, 9.0   # AGFRC envelope
ENC_GAP              = 2.00                            # AEDR-8300 typical
ENC_AZ               = 330.0                           # design choice (spec 4.7)
STRIP_T              = 0.15                            # RULING 4 Sep: code strip recess
LRA_L, LRA_H         = 10.0, 4.37                      # VLV101040A installed
LRA_AZ               = 165.0                           # RULING: wall beside the post at 150
SPEAKER_D, SPEAKER_T = 40.0, 9.05                      # Soberton, vendor mesh
SPEAKER_CENTRE       = (0.0, -30.0)                    # design choice, clear of the servo mount
SUPERCAP_D, SUPERCAP_L = 8.0, 12.0
LED_N                = 90
LED_T                = 2.0                             # SK6812SIDE-A package height (radial when side-mounted)
JACK_AXIS_ABOVE_BOARD = 3.00
USBC_ABOVE, USBC_BELOW = 1.06, 2.10                    # GCT mid-mount

# ------------------------------------------------------------- z stack (spec section 8, case B)
PAD_T                = 1.50
PLATE_T              = 5.00                            # RULING 4 Sep
Z_PLATE_TOP          = PLATE_T                         # 5.0
CARRIAGE_T           = 4.20                            # sits on the pad through the plate
Z_MOTOR_BOT          = CARRIAGE_T                      # 4.2
Z_MOTOR_TOP          = Z_MOTOR_BOT + MOTOR_H           # 18.2
Z_BELL_BOT           = Z_MOTOR_BOT + MOTOR_BASE_H      # 8.5  (ASSUMED base height)
HALO_Z0              = Z_PLATE_TOP                     # 5.0  halo bottom = plate top edge
HALO_H               = 2.60
HALO_Z1              = HALO_Z0 + HALO_H                # 7.6
LIP_T                = 0.80
Z_LIP0, Z_LIP1       = HALO_Z1, HALO_Z1 + LIP_T        # 7.6 - 8.4  diffuser-retaining lip
Z_SKIRT_BOT          = Z_LIP1 + 0.60                   # 9.0  shadow gap over the lip
Z_DRIVE0, Z_DRIVE1   = Z_BELL_BOT + 0.5, Z_MOTOR_TOP - 0.4   # 9.0 - 17.8 drive band on the bore
Z_COMP_BOT           = Z_MOTOR_TOP + 1.0               # 19.2 display's lowest point (USB-A)
Z_PCB_BOT            = Z_COMP_BOT + PCB_TO_LOWEST      # 25.6
Z_PCB_TOP            = Z_PCB_BOT + PCB_T               # 27.2
Z_DISC_BOT           = Z_PCB_TOP + (DISC_TO_PCB_TOP - DISC_T)   # 28.7
Z_DISC_TOP           = Z_DISC_BOT + DISC_T             # 34.7 the glass
VENDOR_Z_OFFSET      = Z_DISC_TOP - VENDOR_GLASS_Z     # 30.95
RIM_GAP, CROWN_T     = 0.40, 3.00
Z_CROWN_BOT          = Z_DISC_TOP + RIM_GAP            # 35.1
Z_KNOB_TOP           = Z_CROWN_BOT + CROWN_T           # 38.1
HEIGHT               = Z_KNOB_TOP + PAD_T              # 39.6
# wheels under the board, above the code band
Z_WHEEL1             = Z_DISC_BOT - 1.3                # 27.4 (collar top under the disc back)
Z_WHEEL0             = Z_WHEEL1 - WHEEL_W              # 23.4
Z_RIDGE_MID          = (Z_WHEEL0 + Z_WHEEL1) / 2       # 25.4
Z_GROOVE0            = Z_RIDGE_MID - WHEEL_V_H - WHEEL_V_FLAT/2   # 23.8
Z_GROOVE1            = Z_RIDGE_MID + WHEEL_V_H + WHEEL_V_FLAT/2   # 27.0
Z_POST_TOP           = Z_WHEEL0 - BUSH_FLANGE_T        # 22.8  bush flange rests here
Z_CODE0, Z_CODE1     = Z_MOTOR_TOP + 0.2, Z_WHEEL0 - 0.8    # 18.4 - 22.6 code band (AEDR-8300 is 3.96 tall)
# ledge and wall
Z_LEDGE_TOP          = 17.4
Z_LEDGE_BOT          = Z_LEDGE_TOP - 1.8               # 15.6
# display seats (in the 1.5 gap between the board top and the disc back)
SEAT_T               = 1.20
Z_SEAT0, Z_SEAT1     = Z_DISC_BOT - SEAT_T, Z_DISC_BOT # 27.5 - 28.7
COLUMN_AZ            = [42, 138, 222, 318]             # 3 deg off the holes so the far-side columns clear the board edge
COLUMN_R0, COLUMN_R1, COLUMN_W = 51.5, 57.5, 4.0
KNOB_FRACTION        = (Z_KNOB_TOP - Z_SKIRT_BOT) / Z_KNOB_TOP

# ------------------------------------------------------------- radii
R_DISC               = DISC_OD / 2                     # 57.5
R_BORE               = R_DISC + 0.50                   # 58.0 straight bore
R_KNOB               = 62.50
R_CROWN_IN           = ACTIVE_OD / 2 + 0.70            # 44.5
R_GROOVE_ROOT        = R_BORE + WHEEL_V_H              # 59.3
WHEEL_AXIS_R         = R_GROOVE_ROOT - WHEEL_OD/2 - 0.07   # 52.63
BUSH_R               = WHEEL_AXIS_R - WHEEL_ECC        # 51.73
WHEEL_POST_D         = 8.00
R_WALL_IN, R_WALL_OUT = 55.50, 57.60                   # the structure's wall
R_LEDGE_IN           = 49.00
R_LED_OUT            = R_WALL_OUT + 0.60               # 58.2 flex ring outer face (RULING v8 gap kept for the print)
R_DIFF_IN            = 60.00
R_DIFF_OUT_BOT       = 62.00
R_DIFF_OUT_TOP       = R_KNOB                          # 62.5
R_LIP_OUT            = 60.50
PLATE_R              = 62.00
PAD_R                = 61.00
MOTOR_R              = R_BORE - MOTOR_OD/2             # 40.5 engaged centre radius
MOTOR_CLEAR          = 2.0                             # wall/ledge relief around the bell
CARRIAGE_HOLE_W      = MOTOR_OD + 5.0                  # 40 tangential
CARRIAGE_HOLE_R0     = 19.0                            # inner edge (room for the servo tab)
CARRIAGE_HOLE_R1     = 59.5
PLATE_SCREW_AZ       = [125, 245, 332]                 # structure-to-plate M3, countersunk from below
PLATE_SCREW_R        = 53.0
PORT_W               = 32.0                            # port face width (tangential)
PORT_NOTCH_R0        = 35.0                            # slot in the plate from here to the rim
PORT_FACE_R0, PORT_FACE_T = 49.5, 1.5
PORT_LIGHT_T, PORT_USBC_T, PORT_JACK_T = -1.0, -10.0, 9.0   # tangential positions on the port face
SENSOR_HOLE_D        = 4.8                             # 0.5 + 2 * 1.43 * 1.5
PORT_N               = 24                              # perimeter ports on a 15 deg grid (RULING 4 Sep)
PORT_D               = 2.0
PORT_Z               = 12.0

# knurl (carried from v8; the only surface the hand touches)
KNURL_ON             = True
KNURL_N, KNURL_DEPTH, KNURL_HELIX_DEG = 56, 1.00, 30.0
KNURL_ROOT_OFF, KNURL_BAND_OV, KNURL_BANDS, KNURL_LAND = 0.50, -0.03, 8, 0.80
CH_TOP, CH_IN, CH_BOT = 2.50, 1.00, 1.20
KNURL_Z0             = Z_SKIRT_BOT + CH_BOT + KNURL_LAND
KNURL_Z1             = Z_KNOB_TOP - CH_TOP - KNURL_LAND
KNURL_PITCH          = _m.pi * 2 * R_KNOB / KNURL_N
SKIRT_WALL           = R_KNOB - R_BORE                 # 4.5

ASSUMED_LIST = [
    ("MOTOR_BASE_OD", MOTOR_BASE_OD, "stator base narrower than the bell; the bell reaches the bore, the base must clear the LED wall"),
    ("MOTOR_BASE_H", MOTOR_BASE_H, "bell begins 4.3 above the base face; the halo top is at 8.0"),
    ("MOTOR_BAND_T", MOTOR_BAND_T, "0.6 flat silicone band"),
    ("motor bolt pattern", "none", "carriage has a locating recess only"),
    ("servo lugs / pushrod", "none", "servo is an envelope; pushrod assumed on the 21.4 axis"),
    ("code strip thickness", STRIP_T, "recess in the code band"),
    ("display weight", "60 g", "not published"),
    ("internal USB-C plug", "10 x 6.5 x 19", "straight plug + short overmould"),
    ("right-angle USB-C plug body", "12 x 6.5 x 12", "sets the plate notch"),
    ("LED flex ring", "1.2 thick incl. LEDs", "no vendor drawing"),
    ("driver / port / encoder boards", "outlines only", "electrical layout not done"),
]
