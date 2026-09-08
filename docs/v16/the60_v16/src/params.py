"""the 60 (Cadrane) — v16 parameter block.  Every dimension lives here.

v16 (2026-09-08): v15 plus the layout study and the decisions of 8 Sep (docs/LAYOUT-STUDY.md, docs/HALO-OPTICS.md,
docs/FUNCTION-ALLOCATION.md, docs/SMALL-PARTS-SOURCING.md): the knob's rim 25 flat (Ø185.4); the wheels are bought V-groove
bearings on fixed pins and the bore carries a male V-ridge; the third wheel is on a spring-loaded block in a channel (no eccentric
bushes, no adjustment); the halo strip faces DOWN under a ledge at a white floor with a 4 mm machined opal ring standing 2 proud;
the motion board and its saddle seat are gone - bought breakouts on the plate (motor driver, haptic driver) on countersunk M2 studs
from below with nuts above and printed spacers; the microcontroller and the level shifter on a printed tray over the audio board;
the Pi powered through its header (its USB-C plug and notch deleted); the panel jack, the light-sensor breakout, the Mill-Max pogo
block and the MT6701 module replace the four tiny custom boards; the plate's two ribs deleted.  Every number is tagged:
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
# v16: the bell does NOT reach the bore. At Ø176.4 a Ø35 bell touching the bore would reach r 88.8 and pass straight through the halo's channel
# (r 86.4-90.8, z 8-13.5) - v15's strip sat inside the bell's reach, the face-down channel cannot. So a printed DRIVE COLLAR (ID 35 pressed on the
# bell's top 3.5, OD 39.4) carries the band and reaches the bore over z 14.9-17.8 only, above the ledge; the bell itself stops at r 86.0, inside the
# wall's outer face, 0.5 inside the liner. Ratio bore/collar 4.48 (v15 4.75)
DRIVE_COLLAR_OD, DRIVE_COLLAR_ID, DRIVE_COLLAR_H = 39.4, 35.0, 3.5
MOTOR_PRELOAD_N      = 2.4               # RULING 4 Sep
CLUTCH_LIFT          = 2.40

# ------------------------------------------------------------- other bought parts (MEASURED from their STEP files) - carried
# v16 wheels (RULING 8 Sep: bought V-groove bearings, no custom collar, no eccentric bush): V623ZZ class, 3 x 12 x 4, a 90 deg V in the
# outer ring. The V's depth and root flat are ASSUMED until Ryan's listing is measured (the ridge below is derived from them - a drop-in)
WHEEL_OD, WHEEL_W, WHEEL_BORE = 12.00, 4.00, 3.00      # PUBLISHED class figures (V623ZZ)
WHEEL_V_D, WHEEL_V_ROOT_FLAT, WHEEL_V_ANGLE = 1.20, 0.40, 90.0   # ASSUMED: V 1.2 deep, 0.4 flat at the root, 90 deg included
WHEEL_V_MOUTH        = WHEEL_V_ROOT_FLAT + 2 * WHEEL_V_D          # 2.8 wide at the outer face
WHEEL_AZ             = [30, 150, 270]                  # two FIXED wheels at 30 and 150 locate the knob; the 270 wheel is on the sprung block
WHEEL_FIXED_AZ, WHEEL_SPRUNG_AZ = [30, 150], 270
# the knob's bore carries a male V-ridge that the bearings' grooves straddle (v15: a groove in the bore and printed V-collars). The ridge
# stands on a shallow relief band so the bearings' rims never touch the bore; its crest is narrower than the V's root by 2 x the clearance,
# so the flanks meet with 0.2 between crest and root (the same 90 deg flanks slide into each other on assembly)
RIDGE_CLEAR          = 0.20                            # crest to the V's root, radial
RIDGE_H              = WHEEL_V_D                       # 1.2 tall (from the relief band)
RIDGE_CREST_W        = WHEEL_V_ROOT_FLAT + 2 * RIDGE_CLEAR         # 0.8 flat at the crest
RIDGE_BASE_W         = RIDGE_CREST_W + 2 * RIDGE_H                 # 3.2 at the base (90 deg flanks)
BORE_RELIEF          = 0.30                            # the relief band cut into the bore behind the ridge: the bearings' Ø12 rims sit 0.2 inside it
WHEEL_PIN_D          = 3.0                             # ISO 8734 Ø3 m6 dowel pins as the axles (fixed posts x 10, block x 16), M3 x 0.5 washers (DIN 433) under the inner rings
WHEEL_WASHER_D, WHEEL_WASHER_T = 6.0, 0.5
# the sprung block (RULING 8 Sep, sketch docs/layout/sprung_wheel.png revised: the block slides RADIALLY in a printed channel on the structure, a
# roof with a pin slot stops it tipping; a spring behind it; a captive M2 release screw from the centre winds it in for assembly and is
# backed off to let it go - the crown covers r > 64.2, so the release has to be reached from the display opening, not from above the wheel)
BLOCK_L, BLOCK_W, BLOCK_H = 13.0, 8.0, 5.0             # radial x tangential x tall, on the plate top (z 8-13)
BLOCK_TRAVEL_IN, BLOCK_TRAVEL_OUT = 4.0, 0.5           # from the nominal (knob centred) position: 4.0 in for assembly, 0.5 out (the stop the spring rests on with no knob)
BLOCK_PIN_FROM_END   = 1.7                             # the axle pin this far from the block's outer end (the block's outer face 84.0 nominal, 84.5 at its outer stop: 0.3 inside the wall)
BLOCK_NUT_FROM_FACE  = 3.0                             # an M2 nut in a slot from the block's top, 3.0-4.6 behind its inner face: the release screw's thread
CHANNEL_WALL_T, CHANNEL_CLEAR = 2.0, 0.2               # the channel's side walls, and the block's clearance to them and the roof
CHANNEL_ROOF_T       = 0.8                             # roof over the block (the pin's slot through it)
CHANNEL_END_R0       = 58.0                            # the channel's inner end wall r 58-60: the spring's abutment, the release screw through it (its head on the centre side)
SPRING_D, SPRING_FREE_L, SPRING_K = 4.0, 16.0, 0.80    # ASSUMED compression spring Ø4 x 16 free (ID 3.2: it runs on the release screw), 0.8 N/mm: 4.0 N seated (11 long), 7.2 N parked (7 long), 3.6 N at the outer stop
RELEASE_SCREW        = "M2 x 18 pan head, captive: through the end wall (Ø2.4), inside the spring, into the nut in the block. Wound in it pulls the block 4.0 toward the centre against the spring; backed off, the spring pushes the block out and the thread stays in the nut at every position (tip 5.0-9.0 behind the block's face; the pin hole starts at 9.8)"
RELEASE_SCREW_Z      = 10.5                            # its axis: the block's mid-height
SERVO_L, SERVO_W, SERVO_H, SERVO_STROKE = 21.4, 15.2, 6.0, 9.0   # AGFRC envelope
ENC_AZ               = 335.0                           # on the seat flange between the nub at 330 (r 67, inboard of the encoder's r 72-80) and the flex slot at 0 (v16: 310 sat over the MCU tray's east studs)
STRIP_T              = 0.15
LRA_L, LRA_H         = 10.0, 4.37
LRA_AZ               = 258.0
SPEAKER_D, SPEAKER_T = 40.0, 9.05                      # placement below with the boards
# halo (v16, HALO-OPTICS.md accepted 8 Sep): a bought addressable LED STRIP stuck FACE DOWN to the underside of a ledge on the structure, firing at
# a white floor in a channel between the wall and the diffuser; the diffuser is lit only by light returning from the floor (no LED in direct view)
LED_STRIP_W          = 4.0                             # ASSUMED 4 mm flat strip of 2020 top-firing parts (HALO-OPTICS §4); the channel is 0.4 wider than it
LED_STRIP_T          = 1.2                             # ASSUMED strip thickness including the LEDs
LED_PER_M            = 100                             # ASSUMED strip density (WS2812B-2020 class); HALO-OPTICS §5: 60 or 120 on the ring, settled on the bench (question 34)
LINER_T, LINER_WALL_H = 0.4, 3.4                       # the white printed L-liner in the channel: a 0.4 floor on the ring's top and a 0.6 wall up the structure's wall to z 11.4 (HALO-OPTICS: floor, walls and roof white; bare stainless is specular)
HALO_THROW           = 12.0 - 8.0 - LINER_T            # 3.6 from the strip's emitting face (z 12.0) to the liner's floor (HALO-OPTICS §4 asked for 4.0 to a coated ring top; a white coating instead of the liner gives 4.0 - bench item, question 34)
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
HALO_Z0              = Z_PLATE_TOP                     # 8.0 the channel's floor (the ring's top; the liner on it)
HALO_H               = 5.5                             # the channel z 8.0-13.5 as v15 (set by the knob's skirt)
HALO_Z1              = HALO_Z0 + HALO_H                # 13.5
LIP_T                = 0.80
Z_LIP0, Z_LIP1       = HALO_Z1, HALO_Z1 + LIP_T        # 13.5 - 14.3: the lip that clamps the diffuser's top face through its gasket (v16: out to the knob's radius)
Z_LEDGE0             = Z_LIP1 - 1.1                    # 13.2: the strip's ledge (r wall to 90.5) is the lip's inner part, 1.1 thick; the strip hangs under it z 12.0-13.2, emitting face at 12.0
Z_STRIP0, Z_STRIP1   = Z_LEDGE0 - LED_STRIP_T, Z_LEDGE0     # 12.0 - 13.2
DIFF_GASKET_T        = 0.30                            # ASSUMED closed-cell foam ring between the diffuser's top face and the lip (HALO-OPTICS §6: clamp axially through something compliant, never hard)
Z_DIFF1              = Z_LIP0 - DIFF_GASKET_T          # 13.2 the diffuser's top face
Z_DIFF0              = Z_PLATE_TOP - 0.5               # 7.5: it stands in a 0.5 rebate in the ring's top (radial location on the rebate's inner wall, 0.3 clearance)
Z_SKIRT_BOT          = Z_LIP1 + 0.60                   # 14.9: the knob's lowest point, over the lip
Z_COLLAR0, Z_COLLAR1 = Z_MOTOR_TOP - DRIVE_COLLAR_H, Z_MOTOR_TOP   # 14.7 - 18.2 the drive collar on the bell's top
Z_DRIVE0, Z_DRIVE1   = Z_COLLAR0 + 0.2, Z_MOTOR_TOP - 0.4    # 14.9 - 17.8 the band on the collar: the bore meets all of it (the skirt's bottom is at 14.9)
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
Z_SEAT_WHEELS        = Z_DRIVE1 + 0.3 + 0.6 + 4.0 + 0.5 + 2.0   # 25.2: what the wheels allow - the relief band 0.3 above the drive band, 0.6 of band under the bearing, the 4.0 bearing, 0.5 to the flange, 2.0 flange
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
# wheels just under the seat
Z_WHEEL1             = Z_SEAT_TOP - 2.0 - 0.5          # 23.5 (bearing top 0.5 under the seat's underside 24.0)
Z_WHEEL0             = Z_WHEEL1 - WHEEL_W              # 19.5
Z_RIDGE_MID          = (Z_WHEEL0 + Z_WHEEL1) / 2       # 21.5: the ridge's crest and the bearings' V root
Z_RIDGE0, Z_RIDGE1   = Z_RIDGE_MID - RIDGE_BASE_W/2, Z_RIDGE_MID + RIDGE_BASE_W/2   # 19.9 - 23.1 the ridge's base on the relief band
Z_RELIEF0, Z_RELIEF1 = Z_WHEEL0 - 0.2, Z_WHEEL1 + 0.2  # 19.3 - 23.7 the relief band (the bearings' rims run inside it)
Z_POST_TOP           = Z_WHEEL0 - WHEEL_WASHER_T       # 19.0: the fixed posts' top faces; a 0.5 washer between the post and the inner ring
Z_SEAT_BOT           = Z_SEAT_TOP - 2.0                # 24.0 seat flange
# the sprung block's channel (z from the plate top): block 8-13, 0.2 clearance, roof 13.2-14.0; the block's Ø3 x 16 pin from 8.2 to 24.2
Z_BLOCK0, Z_BLOCK1   = Z_PLATE_TOP, Z_PLATE_TOP + BLOCK_H            # 8.0 - 13.0
Z_ROOF0              = Z_BLOCK1 + CHANNEL_CLEAR                     # 13.2
Z_ROOF1              = Z_ROOF0 + CHANNEL_ROOF_T                     # 14.0
BLOCK_PIN_L          = 16.0                                          # ISO 8734 3 m6 x 16: z 8.2 - 24.2 (4.8 pressed in the block, the bearing on it 19.5-23.5)
POST_PIN_L           = 10.0                                          # ISO 8734 3 m6 x 10 in the fixed posts: z 13.5 - 23.5 (5.5 pressed)
KNOB_FRACTION        = (Z_KNOB_TOP - Z_SKIRT_BOT) / Z_KNOB_TOP

# ------------------------------------------------------------- radii (spec 8.1)
R_PIC                = PANEL_ACTIVE_R                  # 63.5
R_CROWN_IN           = R_PIC + 0.70                    # 64.2 lip inner edge (ASSUMED 0.7 hidden border)
RIM_FLAT             = 25.0                            # RULING 8 Sep (Ryan: 'add the extra 5mm'): the flat rim between the two chamfers is 25 (v15 20; RULING 6 Sep: at least 20). The display is fixed, so the whole 5 goes into the bezel
R_KNOB               = R_CROWN_IN + 1.00 + RIM_FLAT + 2.50   # 92.7: lip edge + 1.0 inner chamfer + 25 flat + 2.5 outer chamfer (Ø185.4; v15 87.7)
SKIRT_WALL           = 4.50                            # the knob's wall as v10: 1.0 knurl + 3.5 under the root (RULING 6 Sep: the knob keeps v10's shape, only the rim grows)
R_BORE               = R_KNOB - SKIRT_WALL             # 88.2 (Ø176.4; v15 83.2): everything inside scales out to it (RULING 6 Sep)
# v16 wall: TWO radii. Its lower part (the plate to the halo ledge) sits 4.4 inside the diffuser so the strip's channel is 4.4 wide; above the
# ledge it steps INWARD 2.0 on a 50 deg ramp (printable inverted) so that the knob, dropped on with a 2.4 offset toward the two fixed wheels
# (the way the ridge passes them - see V16.md), clears it on the far side: the far-side ridge crest comes to 84.9 and the bore to 85.8
R_DIFF_OUT           = R_KNOB + 2.0                    # 94.7: the opal ring's outer face, vertical, standing 2.0 proud of the knob and the plate (HALO-OPTICS §4; Ø189.4 at the band)
DIFF_T               = 3.9                             # 4 mm class machined opal (HALO-OPTICS §6: Perspex Opal 030 / Satinice 0D010 DF, cast, annealed)
R_DIFF_IN            = R_DIFF_OUT - DIFF_T             # 90.8: the channel's outer wall
CHANNEL_W            = LED_STRIP_W + 0.4               # 4.4: 0.2 either side of the strip
R_WALL_OUT           = R_DIFF_IN - CHANNEL_W           # 86.4: the wall's outer face below the ledge (v15 82.8)
R_WALL_IN            = R_WALL_OUT - WALL_MIN           # 84.8 (v15 81.2: +3.6 - the layout study assumed +5 for the wall; the halo channel takes 1.4 of it)
WALL_STEP            = 2.0                             # the inward step above the ledge
R_WALL_OUT_UP        = R_WALL_OUT - WALL_STEP          # 84.4 above the ramp
R_WALL_IN_UP         = R_WALL_IN - WALL_STEP           # 82.8
Z_RAMP0              = Z_LIP1 - 0.5                    # 13.8: the ramp starts just under the ledge's top and rises 45 deg to
Z_RAMP1              = Z_RAMP0 + WALL_STEP * 1.2       # 16.2: the ramp is 50 deg from horizontal (a 45 deg face is the printer's limit; 5 deg in hand)
R_RELIEF             = R_BORE + BORE_RELIEF            # 88.5: the relief band's radius (the bore behind the ridge)
R_CREST              = R_RELIEF - RIDGE_H              # 87.3: the ridge's crest
WHEEL_AXIS_R         = R_CREST - RIDGE_CLEAR - (WHEEL_OD/2 - WHEEL_V_D)   # 82.3: root 0.2 outside the crest; the rims reach 88.3, 0.2 inside the relief band
WHEEL_REACH          = WHEEL_AXIS_R + WHEEL_OD/2       # 88.3
KNOB_FIT_OFFSET      = 2 * (WHEEL_REACH - R_CREST + 0.2)  # 2.4: the knob is dropped on this far toward az 90 (the fixed wheels' bisector, cos 60 = 0.5 per wheel) so its ridge passes outside their rims, then slid back to centre
R_LIP_OUT            = R_KNOB                          # 92.7: the lip clamps the diffuser's inner 1.9 through the gasket (its outer 2.0 stands proud, uncovered)
R_LEDGE_OUT          = R_DIFF_IN - 0.3                 # 90.5: the strip's ledge ends 0.3 inside the diffuser (the radial clearance HALO-OPTICS budgets for PMMA's expansion)
R_STRIP_IN, R_STRIP_OUT = R_WALL_OUT + 0.2, R_WALL_OUT + 0.2 + LED_STRIP_W   # 86.6 - 90.6 the strip's envelope, face down under the ledge
LED_N                = int(2 * _m.pi * (R_STRIP_IN + R_STRIP_OUT) / 2 / 1000 * LED_PER_M)   # 55 at r 88.6 (557 mm)
HALO_PEAK_A          = LED_N * LED_MA_FULL_WHITE / 1000   # 2.64 A at full white (13.2 W at 5 V) - sizes the converter and the halo feed; no sustained cap (HALO-BRIGHTNESS: a ten-minute rolling mean in firmware); 120 LEDs would be 5.76 A
DIFF_CHAMFER         = 0.30                            # HALO-OPTICS §6: 0.3 on every edge of the acrylic ring
WHEEL_POST_D         = 8.00
R_SEAT_IN            = 62.00                           # the seat's inner edge stays at the glass (the flange is 62-84.4; the glass bonds at 62.5-65.6, the lens overhang ends at 70)
NUB_AZ               = [70, 210, 330]                  # the three display-locating pins around the glass edge (off the panel's 5 mm ears at 90/270)
MOTOR_R              = R_BORE - DRIVE_COLLAR_OD/2      # 68.5 engaged centre radius (v15 65.7): the collar touches the bore, the bell reaches 86.0
PLATE_R              = R_KNOB                          # 92.7 - the ring's outer wall is flush with the knob
PLATE_R_SHELF        = R_DIFF_OUT                      # 94.7: the ring carries a thin flange out under the diffuser (z 6.7-7.5) - the 1 mm shelf HALO-OPTICS asked for, 2.0 proud, the acrylic's seat
Z_SHELF0             = Z_DIFF0 - 0.8                   # 6.7 - 7.5: 0.35 above the openings' chamfered tops (6.35): the shelf does not shadow them (HALO-OPTICS GAP 1)
R_REBATE             = R_LEDGE_OUT                     # 90.5: the ring's top is rebated 0.5 from here outward; the diffuser's inner face (90.8) has 0.3 to the rebate's wall
PAD_R                = PLATE_R - 3.0                   # 89.7: pad slightly smaller than the plate (top face; 0.5 lean to the underside)
PLATE_CHAMFER        = 0.3                             # 0.3 x 45 polished on the ring's outer edges (item 5); 0.2 on the thin shelf's edges
MOTOR_CLEAR          = 1.0                             # v16: the bell's window in the wall is 1.0 clear of the bell (2.0 for the collar and band)
PILLAR_AZ            = [160, 240, 328]                 # M3 pillars on the wall for the plate screws from below (v16: 320 -> 328, out of the level shifter's way; v12: 120 moved to 160, out of the speaker's way)
PLATE_SCREW_AZ       = [160, 240, 328]                 # ... and plate screws from below at three of them
PILLAR_R             = R_WALL_IN - 4.0                 # 80.8 (v15 77.2); the Ø7 pillar reaches 84.3, 0.1 inside the upper wall's outer face
PORT_W               = 56.0                            # port slot width (tangential) - v16: 56 (v15 44) so the 16.5 mm light-sensor breakout stands beside the jack; the ring's un-vented arc 342-18 is +-28.6 at the edge
PORT_NOTCH_R0        = 55.0                            # slot in the plate from here to the rim (clear of the Pi's USB-A end at 46.4)
PORT_FACE_R0, PORT_FACE_T = R_WALL_IN - 1.5, 1.5        # 83.3-84.8: the face at the wall's inner face; the sockets sit 9.4 inside the edge
PORT_TAB_R, PORT_TAB_T = PORT_FACE_R0 - 1.5, PORT_W/2 + 4.0   # 81.8, +-32: the port face's rail screws to the plate top beside the slot (inside the wall), M2 into tapped holes
PILLAR_TOP           = Z_PLATE_TOP + 8.0               # 16.0: insert + 2 of roof; nothing screws in from above any more
# ------------------------------------------------------------- the base plate as the heatsink (the60-thermal-plan.md section 14, RULINGS 6 Sep: steel rim ring, converter on the plate, rear exhaust through the pad)
RIM_IN               = PORT_TAB_R - 3.0                # 78.8: the solid 8 mm rim runs from here to the edge (rule 4: 3 inboard of the port face's holes, well inboard of the diffuser's seat at 90.8)
RIM_STEP_W, RIM_STEP_Z = 3.0, 5.0                      # the steel rim ring's inward flange (r 72.2-75.2, z 5-8) sits in a rebate on the aluminium core; 7 x M3 csk from below through the core's shoulder (v14: the shoulder is 5 tall so the intake grooves can be 3.5 deep through it and leave 1.5)
R_CORE_DUCT          = RIM_IN - RIM_STEP_W             # 75.8: the ducted region and the closing plate end here
WEB_T, DUCT_H, CLOSING_T = 2.0, 5.0, 1.0               # v15 (design-changes item 1, rule 5): 2 web (z 6-8), 5 duct (z 1-6), 1 closing plate (z 0-1) in a recess, flush. v14: 4/3/1
PIER_D, PIER_H       = 7.0, 2.5                        # v15: every screw from the top lands on a Ø7 pier hanging 2.5 into the duct (z 3.5-6) - 4.5 of metal for 3.5 of thread, 2.5 of duct left under it; the channels run on beneath
GASKET_T             = 0.2                             # v15 (rule 5): ASSUMED die-cut PTFE/foam gasket 0.2 in a 0.2 groove of the recess floor, on every wall the closing plate seals against (the duct's outer wall and the walls round the three through-cuts)
FIN_PITCH, FIN_CH_W  = 4.0, 3.0                        # rule 11: straight channels 3 wide x 5 tall (v15; v14 3 tall) on a 4 pitch (1 mm fins), running front-to-rear in the bands beside the Pi window, finned over their full length (with a blower fitted the 8 Pa the fins cost is not the constraint - design-changes item 2 asked for fins over the hot spots only, but the compute module sits in a window through the duct, not on the web: there are no channels under it or under the converter)
DUCT_WALL            = 2.0                             # the duct's outer wall r 70.2-72.2, z 1-4: what ties the core's shoulder (under the ring's flange) to the web; the intake and exhaust grooves cut through it
DUCT_MARGIN          = 2.5                             # solid wall left around every through-cut (Pi window, carriage hole, port slot) so the duct does not leak into them
COLLECTOR_R0         = 69.6                            # a collector channel r 69.6-73.8 round the front and sides (az 61-310) joins the intake grooves to the fin channels (v15 66-70.2: +3.6 with the rim)
PLENUM_R0            = 58.6                            # the rear plenums r 58.6-73.8 at az 22-66 (+y) and 308-338 (-y), where the channels end (v15 55-70.2)
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
TRENCH_R0            = 70.4                            # from here (2 of wall to the suction side of the plenum) out through the duct wall and the shoulder into the ring (v15 66.8)
TRENCH_FOOT_AZ       = (37.0, 56.0)                    # from r 72.2 outward the trench widens along the arc: the ring's flange is notched and its inner land cut away between these azimuths, so the exhaust groove is fed over 24 of its 42 degrees
TRENCH_FILLET        = 2.5                             # v15 review: the trench's vertical corners rounded (a Ø5 cutter)
TRENCH_R1            = R_WALL_IN - 1.8                 # 83.0: the trench (and the exhaust groove's open top) end here, 0.5 into the exhaust groove (from 82.5); the hood's lid seals to r 84.5, 0.3 inside the wall's foot (v15 79.0 / 80.5)
HOOD_W, HOOD_T       = 24.0, 1.2                       # the hood over the outlet: 24 wide (tangential) x 6 (radial) x to the blower's top, walls 1.2; its lid over the trench foot 1.5 thick
HOOD_SCREW_AZ, HOOD_SCREW_R = [35.0, 58.0], 78.1       # the lid's two M2 into tapped holes 3 deep in the ring's flange (r 75.8-78.8, z 5-8) and the root of its inner land, 2 deg outside the flange notch's walls, inboard of the exhaust groove (r 80.1)
HOOD_LID_AZ          = (33.5, 59.5)                    # the lid's extent: 1.5 mm clear of the wheel post's web at 30 and of the groove wall at 60
FAN_HEADER_XY        = (PI_X0 + 66.75, PI_Y0 + PI_W - 4.0)   # (14.75, 14): the Pi 5's 4-pin fan connector - the vendor STEP carries it (pi_part_13, 3 x 6 x 4.2 at x 13.3-16.2, y 11-17), between the corner standoff and the USB-A stack. v15 review: the first guess (10, 14) sat on the standoff (JST SH 1.0 mm: 5 V, GND, PWM, tach) - position on the board to confirm; the blower's 2-wire lead gets a crimped SH housing on 5 V and GND, PWM speed control comes from the Pi (bench: the header's current rating)
INTAKE_AZ0, INTAKE_AZ1 = 60.0, 300.0                   # v15 (design-changes item 3): the intake arc - the ring's groove and its openings run 60-300; exhaust arcs either side of the port face
INTAKE_UNDERCUT_H, INTAKE_UNDERCUT_R = 0.8, PAD_R      # v15: the undercut under the ring's outer wall, r 84.0-87.7, 0.8 tall (v14 1.5): it opens straight into the underside groove all round both arcs, so it is the supplementary intake AND the downward exhaust (rule 7 and 10) - no pad voids needed. Shorter so the openings above keep 0.75 of wall under them
INTAKE_N, INTAKE_W, INTAKE_H = 24, 9.0, 3.5            # the THROAT passages (v15: 9 wide; v14 7): 24 positions on 11.25 deg over 45-315, cut only inside the intake arc (17 of them, 535 mm2): radial grooves 3.5 deep in the ring's inner land (the pad closes them) joining the groove, and closed tunnels z 1-4.5 through the core's shoulder into the collector. 9 wide leaves 5.5 of land for the ring screws' countersinks (Ø4.6 where the tunnel starts)
INTAKE_PASS_AZ0, INTAKE_PASS_AZ1 = 45.0, 315.0          # the passage grid (unchanged from v14 so the ring screws stay on its lands)
INTAKE_SKIP_AZ       = []                              # (none skipped: every stud island stays inside r 73.3, where the tunnels start)
EXHAUST_AZ           = [310.0, 318.0]                  # the -y (passive) circuit's two exhaust passages, 10 wide, into the 300-339 groove between the ring screw at 303.75 and the pillar screw at 328 (v15 had three at 311/320/329: the 56-wide port slot moved the end ring screw to 334 and the level shifter moved the pillar to 328). The +y circuit exhausts through the blower's trench instead
EXHAUST_W            = 10.0
EXHAUST_ARCS         = [(21.0, 60.0), (300.0, 339.0)]  # the ring's exhaust grooves and openings (design-changes item 3: 16-60 and 300-344; v16: pulled in to 21 and 339 so the groove (r from 82.5) ends 1.6 clear of the 56-wide port slot's walls; 26 openings, 212 mm2)
# v15 ring (design-changes items 3, 5, 6): 120 openings on 3 deg through the ring's outer wall into an underside groove the pad closes
VENT_N, VENT_W, VENT_H = 120, 2.0, 4.5                 # obround openings 2.0 (tangential) x 4.5 (z), on az 1.5 + 3k, mirrored about 0-180; cut only where the groove lies behind them (64 intake, 28 exhaust; none across the port face 342-18 or over the motor's carriage hole and its mirror)
VENT_SKIP_ARCS       = [(79.0, 101.0), (259.0, 281.0)] # the carriage hole (the motor's shoe, Ø38.5 at r 70.7) reaches r 90 and cuts the groove over az 80-100, so openings there would open into the cavity, not the duct - eight are not cut, and the eight opposite are not cut either so the two side views stay identical (Ryan: mirrored). The groove and the undercut are interrupted over 79-101 (solid) for the same reason
PILLAR_LAND_D        = 9.0                             # the structure's three M3 plate screws (r 77.2, az 160/240/320) come up through the ring's inner land: a Ø9 land is left standing in the groove round each so the countersunk head bears on metal
VENT_Z0              = 1.55                            # z 1.55-6.05 (item 3 said 1.25-5.75 against a 5 mm duct; the groove decouples them - raised so 0.75 of wall stays under each opening above the undercut); the chamfered mouth reaches 6.35, the top chamfer starts at 7.7
VENT_CHAMFER         = 0.3                             # 0.3 x 45 deg at every mouth and both of the ring's edges, polished (item 5) - modelled as a 45 deg taper on the mouth
RING_WALL_R0         = PLATE_R - 3.7                   # 89.0: the ring's outer wall r 89.0-92.7 (3.7 thick): what the openings pass through
GROOVE_R0, GROOVE_R0_EXH, GROOVE_R1 = RING_WALL_R0 - 4.5, RING_WALL_R0 - 6.5, RING_WALL_R0   # 84.5 / 82.5 / 89.0: the underside groove (intake arc 4.5 wide, exhaust arcs 6.5: fed from one end; v15 7.5 - narrower so its end clears the wider port slot by 1.6); open at the bottom, the pad closes it
GROOVE_Z1            = 6.55                            # the groove's roof at 6.55 (0.5 over the openings' top; 1.45 of roof)
GROOVE_WALL_DEG      = 1.2                             # the wall left between the intake and exhaust arcs at 60 and 300 (about 1.7 mm at r 82)
# v15 review (Ryan, 7 Sep): NO reeding on the edge face - the three grooves left 0.15 mm lands between them ("razor blades") and their lowest one clipped the openings' chamfered tops. The upper land is plain.
# v16: the plate's two upstanding ribs are deleted (Ryan, 8 Sep: negligible stiffness for a part that then cannot be printed flipped)
CLOSING_SCREW_XY     = [(-60.0, 0.0), (-56.0, 16.0), (-56.0, -16.0), (44.0, 10.0), (44.0, -22.0), (56.0, 31.0), (56.0, -31.0), (0.0, 45.0), (0.0, -57.0)]   # 9 x M2.5 csk from below (v15: three more, so the 1 mm plate's free span is about 30 mm, not 60): the front crescent beyond the Pi window, the rear wedge inside the port slot's walls, one island in each rear plenum, and one in each channel band on a full-depth island the channels are linked round
ISLAND_LINK_L        = 6.0                             # the cross-cut either side of a channel-band island, joining the blocked channel to its neighbours
RING_SCREW_AZ, RING_SCREW_R = [26.0, 78.75, 135, 191.25, 247.5, 303.75, 334.0], R_CORE_DUCT + 1.5   # 77.3: 7 x M3 csk from below through the core's shoulder into the ring's flange, on lands between the passages; the two beside the port slot at 26 / 334 (v15 22.5 / 337.5: the 56-wide slot's walls are at t +-28, the head Ø6.5 broke into them)
PAD_RIN              = RIM_IN - 0.2                    # 78.6: the pad is a plain ring under the rim (rule: it is no longer part of the airflow)
PLATE_MATERIAL       = "6082 aluminium; EXTERNAL faces black hard anodised, every INTERNAL face chromate conversion or bare (design-changes item 2, 6 Sep) - no masked pads anywhere"
RIM_RING_MATERIAL    = "stainless steel (304 or 316), finished BARE: edge face brushed axially, the 0.3 chamfers at every opening mouth and both edges polished - electropolish after machining, brush after (design-changes item 5; RULING 6 Sep: a steel ring for mass, stainless 6 Sep evening)"

PORT_BARREL_T, PORT_USBC_T, PORT_JACK_T, PORT_LIGHT_T = -18.0, -6.0, 6.5, 19.5   # tangential positions on the port face (v16: spread over the 56 slot; the light sensor's 16.5 board at t 11.25-27.75)
SENSOR_HOLE_D        = 4.8
# v16 port module: the panel-mount 3.5 mm jack (SMALL-PARTS-SOURCING: 6.3 mm hole in a 3 mm boss; its body behind the face ASSUMED Ø9 x 14 with solder tags),
# the Adafruit 4162 VEML7700 breakout standing vertically in a slot behind the face (PUBLISHED 16.6 x 16.5 x 4 max; the sensor ASSUMED 3.0 from one edge, on the
# board's centre line, from Ryan's photograph), the GCT USB-C receptacle on its little board as v15, the barrel jack on its vertical board as v15. No jack board, no light board
LIGHT_BOARD_L, LIGHT_BOARD_H, LIGHT_BOARD_T = 16.6, 16.5, 1.6   # tangential x tall x thick
LIGHT_SENSOR_FROM_EDGE = 3.0                           # the sensor's centre this far from the board's bottom edge -> the board stands from z 1.0 to 17.5 with the sensor at the face's hole (z 4.0)
LIGHT_BOARD_Z0       = 4.0 - LIGHT_SENSOR_FROM_EDGE    # 1.0
LIGHT_SLOT_R         = PORT_FACE_R0 - 4.0              # 79.3: the slot's centre plane (the board 78.5-80.1; the VEML7700 package stands 3.0 off the board's outer face, 0.2 short of the face); a 5.3 holder on the face's inner side from the pad to the plate top
JACK_BOSS_T, JACK_HOLE_D = 3.0, 6.3                    # the face is locally 3.0 thick round the jack's bushing (a boss on the inner side), Ø6.3 hole
JACK_BODY_D, JACK_BODY_L = 9.0, 14.0                   # ASSUMED body behind the face
MT_MOD_L, MT_MOD_W, MT_MOD_T = 17.0, 15.0, 1.6         # the MT6701 module (SMALL-PARTS-SOURCING: 15 x 17 breakout with the chip centred) in the carriage's pocket, replacing the 12 x 12 custom commutation board
CARRIAGE_POCKET_L, CARRIAGE_POCKET_W = MT_MOD_L + 0.4, MT_MOD_W + 0.4   # 17.4 x 15.4
# perimeter vents: vertical slits all round the wall (RULING 5 Sep review: slits, not round holes - many, easy to print)
SLIT_W               = 1.0                             # slit width (tangential)
SLIT_Z0, SLIT_Z1     = Z_DRIVE1 + 0.7, Z_SEAT_BOT - 1.0   # 18.5 - 23.0: above the drive band, under the seat
SLIT_PITCH_DEG       = 2.5                             # 144 positions; skipped at the motor, the pillars' and posts' webs, the encoder tower and the LRA pad
BARREL_AXIS_Z        = 3.5                             # spec 6.8: right-angle plug body Ø8.5 -> z -0.75..7.75, pad pocketed under it
USBC_AXIS_Z          = 4.5
JACK_AXIS_Z          = 4.6                             # 6 Sep: jack above its board (pins down into the pad's slot void, 0.5 above the desk plane) - the board used to sit above the plate top under the wall and the LED strip

# ------------------------------------------------------------- the boards, all on the plate (v12, RULING 6 Sep: no deck)
# v16 fixings (RULING 8 Sep, Ryan): every BOARD is held by countersunk M2 screws pointing UP - the head flush in the closing plate's underside, the
# shank up through a full-depth Ø7 island in the duct and the web, a printed spacer on the plate top, the board, an M2 nut above it. Nothing
# threads into the plate for a board. The printed parts that are not boards (servo frame, speaker cradle, connect bracket) keep their M2.5 into
# tapped blind holes in the web (v15), as does the chassis bond.
STUD_D, STUD_HEAD_D, STUD_HEAD_H = 2.0, 3.8, 1.2       # DIN 7991 M2 csk: head Ø3.8 x 1.2 (0.2 proud under the 1 mm closing plate - the core stands 1.5 off the desk on its pad)
STUD_HOLE_D          = 2.2                             # clearance through the core, the spacer and the board
NUT_M2_AF, NUT_M2_T  = 4.0, 1.6                        # DIN 934 M2
SPACER_H, SPACER_D   = 3.0, 5.0                        # printed spacer under every plate board (solder stubs, the odd tall part on the underside); Ø5, bore 2.2
BOARD_STANDOFF       = SPACER_H                        # (kept for the older code paths)
BLIND_D              = 3.5                             # tapped blind holes from the plate top for the M2.5 screws that remain: 3.5 into the 2.0 web + 2.5 pier, 1.0 of floor left under each
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
CB_R, CB_T0          = 64.1, -4.0                      # centre: r 49.1-79.1 at 0 deg (v15 60.5: +3.6 with the wall); holes 5.5 in from its outer edge, 3 from the others, t -27..+19. Off-centre so the panel flex at t -12 meets CN2 8 from the board's middle, off its corner holes
CB_CN2_W, CB_CN2_D, CB_CN2_H = 14.0, 5.0, 2.0          # the panel flex's connector at the +x (outer) edge, at t -12 (under the flex), opening outward
CB_CN1_W, CB_CN1_D, CB_CN1_H = 35.0, 4.5, 2.0          # the 60-pin connector at the inner edge, opening inward
CB_BRACKET_T, CB_BOSS_H, CB_FOOT = 1.5, 2.0, 1.5       # the bracket: a 1.5 slab at z 9.5-11 from r 46 to 78, standing on a 1.5 foot strip (r 46-48) and two ears on the plate, and resting on the port face's rail (z 9.5) at its outer end; four 2.0 bosses with M2 inserts; 2 x M2.5 csk into the web at (46, 17) and (46, -14) (the -y wing beyond that rests on the foot and the rail: the audio's USB plug sits over the plate there)
CB_SCREW_XY          = [(49.6, 17.0), (49.6, -20.0)]   # the bracket's two ears on its foot strip (v16: +3.6 with the board); the -y one off the audio's USB-A plug (in the USB 3.0 stack's lower socket, y -15..-3)
Z_CB0                = Z_PLATE_TOP + CB_FOOT + CB_BRACKET_T + CB_BOSS_H   # 13.0 board underside
CABLE_W, CABLE_T     = 30.6, 0.34                      # PUBLISHED flat cable, 150 long: drawn along its route (about 95 used; the rest is slack)
AUDIO_L, AUDIO_W, AUDIO_H = 40.0, 25.0, 3.6            # Ryan's 40 x 25 (long x short); 1.6 board + 2.0 Pico-Lock connectors (CONNECTORS: one family, 2.00 mated); its USB link is a moulded pre-made lead, 4.0 allowed at its plug
AUDIO_AZ, AUDIO_R    = 297.0, 62.0                     # v16 (layout study C3 said 300 / 64): squeezed between the block channel's wall at 270 (its west edge 1.9 clear) and the Pi's Ethernet shell corner (its inner edge, r 49.5, 1.5 clear); the holes pulled in so its outer studs sit at r 69.5 and their islands stay inside r 73.3, where the intake tunnels start (the lands between the tunnels are too narrow for an island): tangential (40 along the arc) in the south-east crescent; its four M2 studs at (+-16.5, +-9) carry the MCU tray above it
AUDIO_HOLE_L, AUDIO_HOLE_W = 12.0, 6.5                 # (ASSUMED hole pattern: 8 in from the short edges, 6 from the long ones - the board's layout is not done; the pattern is what keeps the outer studs inside r 69.8)
AUDIO_SPACER_H       = 1.0                             # the audio board sits on 1.0 spacers (v15's washers), so the tray over it stays low
CONN_H, USB_PLUG_H   = 2.0, 4.0
# v16: the motion board is GONE (FUNCTION-ALLOCATION.md, 8 Sep). Its jobs go to bought breakouts: the TMC6300 motor-driver breakout (on the plate: it is the
# heat part), the DRV2605L haptic breakout (on the plate), a 74AHCT125 level shifter for the halo's data (on the tray), and the microcontroller (on the tray)
BOB_L, BOB_W, BOB_T  = 25.4, 20.3, 1.6                 # TMC6300-BOB (PUBLISHED outline); ASSUMED two M2 holes on its long axis 2.5 in from the short ends, 2.0 of parts in the middle, right-angle header strips 6.0 tall along BOTH long edges (the BOB's pins are on its long edges) - question 37: if the real board has no holes it goes in a pocket under a keeper like the tray's boards
BOB_AZ, BOB_R, BOB_ROT = 246.5, 58.9, 23.5             # layout study: az 255 r 64.5 with 2.2 mm; v16 as built: its long axis along y, centred (-23.5, -54), 7 from the block channel's wall at 270 (which the study did not know), 1.4 from the haptic breakout, its inner stud 5 clear of the HDMI plug's notch
BOB_PARTS_H, BOB_HEADER_H = 2.0, 3.0                   # right-angle headers with the housings lying flat (a vertical header + housing would be 14 and meet the HDMI ribbon over the board)
DRV_L, DRV_W, DRV_T  = 20.0, 15.0, 1.6                 # DRV2605L breakout (Adafruit 2305 class; outline ASSUMED 20 x 15 - not published to the mm); two M2 holes ASSUMED at (+-7.5, 0)
DRV_AZ, DRV_R, DRV_ROT = 226.6, 65.4, 133.4            # centre (-45, -47.5), long axis along x: 2.0 south of the adapter's edge, 2.6 off the Pi's corner standoff; its studs (holes at +-6) at r 60.5 / 69.7 (islands inside 73.3)
DRV_PARTS_H          = 3.0                             # the chip and a right-angle header lying flat
LS_L, LS_W, LS_T     = 20.0, 15.0, 1.6                 # 74AHCT125 breakout (Adafruit 1787 class; outline ASSUMED); two M2 holes ASSUMED at (-3, +-4) - across the board near its inner end, which is what keeps both studs inside r 69.8
LS_AZ, LS_R, LS_ROT  = 322.0, 69.5, 333.0              # v16: ON THE PLATE east of the audio board's end, long axis along az 297 (parallel to the audio's edge), between the connect bracket's foot and the port slot's wall, between the connect bracket's foot and the pillar at 320 (the layout study's tray had no room for it beside the MCU, and every lobe of the tray reached the sprung wheel's window or the pillar)
LS_PARTS_H           = 3.0
MCU_L, MCU_W, MCU_T, MCU_USB_H = 25.0, 18.0, 1.0, 3.2  # ESP32-S3-Zero class (PUBLISHED 25 x 18; no mounting holes - castellated); its USB-C ASSUMED 3.2 tall at one short end. RULING pending (question 33): Ryan has a Pico 2 with headers; a bare Pico 2 (51 x 21, USB and debug connectors 3.2 / 2.9 tall) does not fit this tray under the seat flange, and over the adapter it collides with the flat cable's fold
# the MCU tray (printed, v16): a 54 x 25 x 1.2 plate on the audio board's four studs, 4.4 tube spacers above the audio's nuts; the MCU and the level shifter
# lie in pockets in its top and a printed KEEPER frame (1.2) clamped by the same nuts holds them down - no screw touches either board (the Zero has no holes)
TRAY_L, TRAY_W, TRAY_T = 40.0, 28.0, 1.2                # 28 across (the audio board is 25), set 1.5 outboard of the audio's centre line: the MCU lies ACROSS the tray between the four stud nuts, and the tray's inner corner keeps 1.6 from the Pi's Ethernet shell
TRAY_Y0              = -1.5                            # the tray's (and the MCU's) centre this far OUTBOARD of the audio board's centre line (audio frame: +y is inboard)
TRAY_SPACER_H        = 4.4                             # nut top (12.2) to the tray's underside (16.6): clears the audio's connectors (12.6) and its USB plug (14.6)
Z_TRAY0              = Z_PLATE_TOP + AUDIO_SPACER_H + 1.6 + NUT_M2_T + TRAY_SPACER_H   # 16.6
Z_TRAY1              = Z_TRAY0 + TRAY_T                # 17.8
TRAY_POCKET_D        = 0.6                             # the boards sit 0.6 into the tray (the pocket floors are the tray's bottom 0.6)
KEEPER_T             = 1.2                             # the keeper frame over the tray: rails 1.5 wide on every board edge
Z_KEEPER1            = Z_TRAY1 + KEEPER_T              # 19.0; the audio studs' top nuts on it to 20.6; the MCU's USB-C to 21.3 (the seat flange is at 24)
AUDIO_STUD_L         = 22.0                            # M2 x 22 csk: from the closing plate's underside up through 1 + 7 + 1.0 + 1.6 + 1.6 (nut) + 4.4 + 1.2 + 1.2 + 1.6 (nut) = 20.6, 1.2 proud
TRAY_T0              = 0.0                             # the tray covers the audio board (t -20..+20), the MCU between the four stud nuts (a tangential board's ends run out to large radii: a 62-long tray reached the pillar at 320 and the sprung wheel's window at 270)
MCU_ON_TRAY          = (0.0, -1.5)                     # the Zero's centre over the audio board's centre (1.5 outboard), turned 90 deg: its 25 lies across the tray (radial), its 18 between the two stud columns (24 apart, nuts 4.6 across); its USB-C at the inboard end, open in the keeper
# the tray's mass and the audio's connectors: the tray is 40 x 25, so nothing of it lies beyond the audio board's outline
LS_ON_TRAY           = None                            # (v16: the level shifter is on the plate, LS_AZ / LS_R; the tray carries the MCU only)
TOUCH_L, TOUCH_W, TOUCH_H = 30.0, 20.0, 4.0            # ASSUMED touch-controller board
TOUCH_STACK_H        = 3.0                             # stacks on the adapter's top on 3 mm standoffs, over its 2.5 parts
TOUCH_CENTRE         = (-33.0, -17.0)                  # ASSUMED: over the adapter's left half, 1.3 off the HDMI socket, clear of the cable's path over the right half
CONV_L, CONV_W, CONV_H = 40.6, 20.3, 7.6               # Pololu D24V90F5 (PUBLISHED 40.6 x 20.3; height ASSUMED 7.6 - its inductor) - SMALL-PARTS-SOURCING
CONV_AZ, CONV_R      = 180.0, 67.5                     # tangential (40.6 along the arc) at r 57.35-77.65 dead ahead: its inner edge 5.3 clear of the adapter's edge (x -52), its outer edge 7.2 inside the wall; its studs at r 69.4 so their islands (to 72.9) stay clear of the intake tunnels (from r 73.3)
CONV_PAD_T           = 0.5                             # ASSUMED thermal gap pad (the one bonded thing besides the display tape and the pad)
CONV_HOLE_T          = 16.0                            # ASSUMED: the module's two holes at t +-16 on its centre line; M2 studs from below, nuts above (the gap pad is its spacer)
CONV_RATING_A        = 6.0                             # what the reworked budget needs: Pi 5 ~3 A peak + halo 2.64 A + boards; size from the measured inlet load (bench item)
SERVO_TRAY_T         = 0.0                             # v12: the servo lies straight on the plate in a frame (no floor) - 8.0-14.0
SERVO_EAR_T          = 12.5                            # frame ears at t +-12.5, M2.5 into the web
CARRIAGE_TAB_T, CARRIAGE_TAB_W = 3.0, 10.0
CARRIAGE_TAB_TOP     = Z_PLATE_TOP + SERVO_H + 0.5     # 14.5: the push tab only has to reach the servo's height now (v11: 28.5 through the deck)
SPEAKER_CENTRE       = (-36.0, 47.0)                   # v12: the 90-180 quadrant beyond the adapter's overhang (Ryan's picture: "35 deg" in his frame). Boxed in on four sides: 1.0 beyond the adapter's edge (y 26), 3.1 off the bell and its band, its cradle ring 1.5 inside the wall, 6 off the pillar (moved to 160). az 127.5, r 59.2
SPEAKER_EAR_AZ       = [200.0, 290.0]                  # the cradle's two ears, as azimuths FROM THE SPEAKER'S CENTRE: away from the carriage (0-60), the wall (122) and the Pi/adapter (250-300); M2.5 from above into the web
SPEAKER_FINGER_AZ    = [92.0, 212.0, 332.0]            # the three snap fingers, same convention
GND_BOND_XY          = (48.0, 27.0)                    # THE chassis bond (GROUNDING 3.1): one M3 tapped blind from the top on the free side of the port slot, 45 mm from the barrel inlet (the -y side is taken by the audio board's USB plug and the blower's reserved envelope); a star washer and a ring terminal under the head; the future carrier board's star point lands here. Nothing else bonds to the chassis
RING_BOND_AZ, RING_BOND_R = 67.5, R_CORE_DUCT + 1.5    # 77.3: the rim ring's dedicated bond screw (GROUNDING 4.1): M3 from the top through the ring's flange into the core's shoulder, external-tooth star washer under the head, both faces bare. v15: on the grid land at 67.5 (the passages at 61.9 is not cut, 73.1 is), 3.4 of metal to the passage's wall; 56.25 lay inside the blower trench's foot. 44 mm from the chassis bond
BLEED_AZ, BLEED_R    = 200.0, 71.5                     # the knob's 1 MOhm bleed (GROUNDING 5): a phosphor-bronze leaf with its foot FLAT on the seat flange (v15: no boss - the flange top is the print bed; the M2 insert is in a boss under the flange), bearing lightly UP on the crown's underside at r 71.5 - the smallest radius the knob offers (the lens ends at 70, the code ring starts at 72.5); between the wheel notch at 150 and the nub at 210
BLEED_FOOT_R         = 74.5                            # the leaf's foot and M2 screw
USBC_SHELL_WIRE      = True                            # GROUNDING 6: the USB-C receptacle's shell to the chassis bond by a short wire (modelled); the 3.5 mm jack's shell stays isolated - the port face MUST be an insulator
LRA_BOARD_W, LRA_BOARD_H, LRA_BOARD_T = 7.0, 8.0, 1.0  # the vibration actuator's contact carrier (SYSTEM-REVIEW 6.1): a 7 x 8 x 1 carrier board in a printed clip on the wall at 252.5 deg with a Mill-Max 867-22-002-70-501010 two-position spring-pin block soldered to it (SMALL-PARTS-SOURCING), its pins on the LRA's flex-tail pads
LRA_POGO_D, LRA_POGO_L = 1.5, 2.2                      # the block's two pins ASSUMED Ø1.5, 2.2 compressed; the block's body ASSUMED 5.1 x 2.6 x 3.0 on the carrier
HALO_TAIL_AZ         = 325.0                           # v16: the strip's joint (its start and end meet here) and a notch through the wall's foot, 1.2 deg clear of the pillar's web at 320; the three-wire tail (5 V, GND, data) runs inward along the plate to the level shifter beside it. The far end's 5 V feed enters at a second notch near the converter (HALO_FEED2_AZ) - question 32 closed
HALO_FEED2_AZ        = 190.0                           # the second feed notch: 5 V and GND to the strip's far end from the converter 10 deg away
HALO_TAIL_W, HALO_TAIL_T = 3.0, 1.4                     # the tail as a flat three-wire ribbon
SENSOR_CABLE_LOOP    = 12.0                            # the rotor sensor cable's service loop (SYSTEM-REVIEW 6.2): flex-rated, the carriage moves 2.4 every clutch cycle
# v16: the Pi's USB-C plug is GONE - the Pi 5's USB-C carries no data (SMALL-PARTS-SOURCING), so it is powered through its header (5 V pins 2/4, GND 6) from the converter; the window's notch for the plug head goes with it. The external USB-C on the port face is the microcontroller's host link
HDMI_PORT            = 1                               # the ribbon plugs into HDMI1 (x 39.5 in the Pi's frame) - HDMI0 sits behind the USB-C plug's head

# knurl
KNURL_ON             = True
KNURL_N, KNURL_DEPTH = 82, 1.00                        # 82 starts keep the v9 pitch (7.1 mm) at Ø185.4 (RULING 5 Sep, question 13: keep the pitch; v15 78 at Ø175.4)
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
    ("audio / touch boards", "envelopes", "electrical layout not done"),
    ("bought breakouts", f"TMC6300-BOB {BOB_L} x {BOB_W}; DRV2605L {DRV_L} x {DRV_W}; 74AHCT125 {LS_L} x {LS_W}; hole patterns", "outlines from the vendors' pages where published; hole positions and part heights assumed"),
    ("microcontroller", f"ESP32-S3-Zero class {MCU_L} x {MCU_W}, USB-C {MCU_USB_H} tall", "RULING pending (question 33): a Pico 2 does not fit the tray"),
    ("converter height", CONV_H, "Pololu D24V90F5: outline published, the inductor's height not"),
    ("V-groove bearing", f"V623ZZ: V {WHEEL_V_D} deep, {WHEEL_V_ROOT_FLAT} root flat, {WHEEL_V_ANGLE} deg", "the ridge is derived from these - measure Ryan's listing and re-run"),
    ("block spring", f"Ø{SPRING_D} x {SPRING_FREE_L} free, {SPRING_K} N/mm", "about 4 N seated; the bench sets it (the band slip limit is 120-160 mN.m at 4 N)"),
    ("light-sensor breakout", f"sensor {LIGHT_SENSOR_FROM_EDGE} from the edge", "Adafruit 4162, from Ryan's photograph"),
    ("panel jack body", f"Ø{JACK_BODY_D} x {JACK_BODY_L}", "the listing's drawing to fetch"),
    ("Mill-Max spring-pin block", "5.1 x 2.6 x 3.0, pins Ø1.5 x 2.2 compressed", "867-22-002-70-501010; datasheet to fetch"),
    ("diffuser gasket", DIFF_GASKET_T, "closed-cell foam ring under the lip"),
    ("halo liner", f"{LINER_T} floor, {LINER_WALL_H} wall", "white PETG; a white coating on the ring is the alternative (throw 4.0 instead of 3.6)"),
    ("barrel jack body", "14.4 x 9.0 x 11.0 on a vertical board", "PJ-063AH; CAD body to fetch"),
    ("right-angle barrel plug", "Ø8.5 body", "measure the brick's plug"),
    ("MOTOR_BASE_OD / MOTOR_BASE_H", f"{MOTOR_BASE_OD} / {MOTOR_BASE_H}", "carried from v9"),
    ("MOTOR_BAND_T", MOTOR_BAND_T, "carried from v9"),
    ("servo pushrod", "3 mm bridge to the tab", "carried from v9; servo on the plate in a frame"),
    ("LED strip", f"{LED_STRIP_W} wide x {LED_STRIP_T} thick, face down", "a 4 mm 2020 strip (HALO-OPTICS); the channel is 4.4 wide - a 5 mm strip needs the wall 1.0 further in"),
    ("blower inlet and outlet", f"inlet Ø{BLOWER_INLET_D} in the face, outlet {BLOWER_OUTLET_W} x {BLOWER_OUTLET_H} from {BLOWER_OUTLET_Z0} up", "from the datasheet drawing (outline, holes and leads PUBLISHED)"),
    ("blower gaskets", f"{BLOWER_GASKET_T} closed-cell foam", "under the inlet face and the hood"),
    ("closing-plate gasket", f"{GASKET_T} die-cut", "in a groove of the recess floor, on every sealing wall"),
    ("Pi 5 fan connector current rating", "0.13 A drawn (0.20 max)", "the connector sits in the vendor STEP; its rating is not published"),
    ("encoder shim family", f"{ENC_SHIM_FAMILY}", "printed; the height is chosen on the bench"),
]
