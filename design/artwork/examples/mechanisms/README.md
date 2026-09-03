# Mechanism sections — the 60, v7.1

Nine views cut from the real v7.1 geometry, made to answer one question: **where does each bought
component actually sit?** They are the pictures behind `../../MECHANISMS.html` — open that file for the
same images with numbered balloons and a keyed parts list. This README is the plain-text version.

## How to read them

**Azimuth** is measured anticlockwise from the +X axis. The ports are at **90 deg**, which is the far
side from you when the device is on the desk. In the two plan views, 90 deg is at the top of the image,
+X is to the right.

**Colour tells you what a thing is:**

| Colour | What |
|---|---|
| orange | self-turning drive: motor, shaft, tyre, solenoid |
| amber | carrier gearmotor and worm |
| red | the six detent magnets |
| pale steel | the sixty Ø3 balls, and the 623ZZ wheel bearings |
| green | encoder |
| violet | haptic LRA |
| blue | speaker |
| teal | supercapacitors |
| yellow-green | port board, USB-C, 3.5 mm jack |
| warm white | halo LED ring board |
| slate blue | display disc and main PCB |
| light grey | printed structure |
| **dark grey** | **a cut face — where the section knife passed** |

If a surface is dark grey it is not a part, it is the inside of something you are looking through.

## The views

### 00-plan-floor.png — the floor
Horizontal section at **z 12**, looking down. Cut just below the inner roof (z 12.8) so the whole
electronics bay is open. Everything visible here sits on the pad and is installed when the steel plate
goes on, which is the last assembly step.

Drive motor at 180 deg, solenoid at 205 deg, carrier gearmotor at 350 deg with its worm, speaker on the
axis, two supercapacitors at 105 and 119 deg, the port board and its two sockets at 90 deg. The LRA at
105 deg is the odd one out — it hangs from the inner roof at z 9.2 to 12.8, above everything else on
this level, so it appears here but lives higher.

### 00b-plan-ring.png — the detent ring
Horizontal section at **z 21**, looking down: the level where the knob meets the base. This is the view
that shows the detent principle at a glance — six magnets at 60 deg spacing against sixty balls at 6 deg
spacing.

Magnets alternate between the two carrier rings: A holds 30/150/270 deg, B holds 90/210/330 deg. Also
visible: the encoder at 60 deg, the three 623ZZ wheels at 0/120/240 deg, and the drive tyre at 180 deg
pressing into the bore.

### 01-drive.png — self-turning drive
Vertical section at **180 deg**. The motor sits in a Ø19 hole in the steel plate, on the pad; its shaft
runs up to a hub carrying an O-ring tyre that presses 0.15 mm into the knob's Ø116 bore. The printed
drive arm pivots 14 mm along the tangent, so swinging it moves the tyre almost purely radially — 1.0 mm
of lift is enough to disengage and let the knob spin free.

The solenoid at 205 deg is not on this section plane; see the floor plan for it.

### 02-detent.png — adaptive detent
Vertical section at **30 deg**, through one magnet tower. The knob wall is on the left. The magnet face
sits at r 57.0 and the ball tips at r 57.8, giving the 0.8 mm gap (0.4 mm lip plus 0.4 mm air) that the
detent research is based on.

### 02b-carrier.png — carrier drive
Vertical section at **350 deg**, through the gearmotor. This is the mechanism that makes the detent
adjustable: the Ø8 gearmotor lies flat on the pad, its worm drives a toothed tab under carrier ring A,
and a rocker at 255 deg turns ring B the opposite way. Ring A goes +1.5 deg and ring B goes -1.5 deg,
which puts the two groups of three magnets half a peg pitch apart so their clicks cancel. Strength runs
0 to 100 per cent in about 50 ms, and because it is a worm it holds position without power.

### 03-wheels.png — knob support wheels
Vertical section at **0 deg**, through one of the three wheels. The 623ZZ runs in a V-groove cut into
the knob bore rather than on a ridge — that change is the whole reason v7.1 can have a one-piece knob,
because a groove lets the Ø115 display pass down through the Ø116 bore during assembly.

**Caveat:** the bearing is placed from the model, but the printed V-collar and eccentric bush are drawn
from their print-orientation exports, so their position in this one section is indicative rather than
exact. Treat the bearing as accurate and the two printed parts as a sketch.

### 04-ports.png — ports and cable tunnel
Vertical section at **90 deg**, the rear. Both sockets are on one 40 x 14 board on 1 mm standoffs, in a
tunnel that runs beneath the full-360 halo. The jack is the tightest clearance in the device: its body
top is at z 4.7 and carrier ring A sits at z 4.8.

### 05-halo.png — halo light ring
Vertical section at **225 deg**. The LED board is on the outer face of the LED wall at r 57 to 58.2,
behind the translucent diffuser at r 58.5 to 62.5, firing down and outward at the desk. It is on the
static base and never on the rotating knob.

### 06-bay.png — electronics bay
Vertical section at **112 deg**, through the supercapacitors. Shows the whole vertical stack in one
picture: plate, supercaps and speaker on the floor, LRA under the inner roof, then the main PCB and the
display disc above. The inner roof clears the board's components by 0.6 mm.

## Open items these views make visible

1. **Supercapacitor pocket.** The Ø8 x 16 pair drawn here is an assumed envelope. The real 10 F bank is
   Ø10 x 30 and has no pocket yet. This is the largest unresolved item on the floor.
2. **Drive motor.** Envelope only. Neither the motor nor its torque against the knob's inertia has been
   chosen or checked.
3. **Carrier torque.** The gearmotor's ability to turn ring A against the magnets is not sized — measure
   it on the printed rings.
4. **Display assumptions.** Standoff height, component height and hole PCD are carried over from v7 and
   still unverified.

## Regenerating them

Blender scene `MECH` in `../../blender/the60_lineart.blend`. The bought components are rebuilt as
primitives from the model's own `ref_*` placements in `src/params.py`, so no build123d install is
needed. Three things will waste your time if you do not know them:

* The Boolean section **must use the EXACT solver.** The FLOAT solver silently fails on these meshes and
  leaves the model uncut while still reporting success.
* `material_mode='TRANSFER'` on the printed parts' Boolean is what gives the cut faces their dark
  colour. Without it a section is unreadable.
* Plan views must set `camera.rotation_euler=(0,0,0)` directly. Building a straight-down camera with
  `to_track_quat` flips the frame 180 deg, which puts the ports at the bottom.

An interactive version of the same data — spin, isolate a mechanism, cut a wedge, pull the layers
apart — is published as the **Mechanism Explorer** artifact.
