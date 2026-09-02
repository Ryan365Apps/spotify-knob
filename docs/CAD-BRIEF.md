# CAD brief — decisions that change the model

**Date:** 2026-09-01
**For:** the next modelling session. This is a standalone brief — it assumes no knowledge of the conversation it came from.
**Companion docs:** `PREMIUM-BOM.md` (mechanism reasoning and parts), `VISION.md` (product intent and anti-goals), `../BUILD.md` (firmware and screens).
**Model reviewed:** `desk_dial_assembly.step`, version of 2026-09-01 11:27 — measured directly, figures below are from the file.

---

## 1. The single biggest change: height

**Target overall height is 40 mm. The model is currently ~60 mm.**

### Why 40

The ergonomic model is a mouse, not a thermostat. The heel of your hand rests on the desk; two or three fingers reach the touchscreen; the open hand lies across the bezel to spin it. At 60 mm the wrist has to lift off the desk to reach the top, which turns every interaction into a deliberate reach. At 40 mm the hand stays planted and the object comes to the fingers.

A 50 mm upturned bowl on the desk was used as a physical reference and reads as too tall. 40 mm is the target; treat 45 mm as the failure threshold.

Reducing height while keeping 135 mm diameter also lowers the centre of gravity, which makes the object more stable against the sideways force of spinning the bezel. That is a free win.

### Where the 20 mm comes from

The current stack puts three components in series up the axis when two of them should be side by side.

**Measured stack in the current model:**

| Z (mm) | Part |
|---|---|
| 0 – 4 | `base_plate_STEEL`, 128 mm dia |
| 0 – 1.6 | `REF_main_pcb`, 107 mm dia, carrying the position sensor and haptic driver |
| 0 – 5 | `REF_speaker_40mm` |
| 4 – 10.2 | `halo_diffuser`, 128 mm dia — at the outer skirt |
| 6.6 – 22.2 | `drive_wheel` + `wheel_mount` — **the gear train** |
| 23.1 – 36.1 | `REF_bearing_6817_2RS`, 85 mm bore / 110 mm outside / 13 mm tall |
| 38.8 – 43.8 | `display_carrier` |
| 42.3 – 57.3 | `REF_display_module`, 15 mm tall |
| 17.4 – ~60 | `bezel_knob`, 135 mm dia |

**Two structural changes recover the height:**

**A. Delete the gear train.** `drive_wheel` and `wheel_mount` occupy Z 6.6–22.2 — about 16 mm — in the ring-shaped volume between the board and the bearing. They exist only to drive the rotation sensor, and they are being removed for a separate reason (see §3). That volume is then free, and it is exactly where the magnet system wants to live.

**B. Make the bearing and the display concentric, not stacked.** Today the bearing sits at Z 23–36 and the display sits above it at Z 42–57. A ring bearing has a hole in the middle; the display assembly should pass **through** that hole so the two occupy the same height band. This alone recovers 13 mm.

**Target stack after the change:**

| Z (mm) | Part |
|---|---|
| 0 – 4 | Steel base plate |
| 0 – 5 | Speaker, recessed into the base plate cavity; main board above or around it |
| 4 – 10 | Halo diffuser at the outer skirt — unchanged |
| 5 – 13 | **Magnet carrier ring** plus 2 mm of vertical travel, in the annulus |
| 10 – 25 | Display assembly, **inside** the bearing bore |
| 13 – 26 | Bearing, at large diameter, surrounding the display |
| 25 – 28 | Cover glass and bezel lip |
| ~5 – 38 | Bezel outer wall |

That lands at roughly 38–40 mm.

### The blocker, and two ways round it

The display assembly must fit through the bearing bore. The current 6817 bearing has an 85 mm bore; the round panel is about 86 mm across, and the module in the model measures wider still. **Measure the real part before choosing.**

**Option 1 — a larger thin-section bearing.** Thin-section ring bearings exist with cross-sections down to about 5 mm, so a 100 mm bore inside a 112 mm outside diameter is available. Smoothest option, continuous race, predictable feel. Costs more and needs sourcing.

**Option 2 — three or four small ball bearings running in a V-groove machined into the bezel.** This is how camera lens mounts and some turntables locate a large ring. Near-zero height cost, the diameter is unconstrained, the preload is adjustable by moving the roller posts, and it is cheap. Risk: with only three or four contact points it can feel notchy if the groove is not accurate — on a CNC bezel it would be, on a 3D print it may not be, so **test both on the printed prototype before committing**.

Option 2 also takes the vertical magnetic pull described in §2 in a controllable way, and lets you tune how tight the assembly feels.

---

## 2. The detent mechanism to add

Nothing of this exists in the model yet. Full reasoning is in `PREMIUM-BOM.md`; this is what to draw.

### Three layers

| Layer | What it does | Changes | Works unpowered |
|---|---|---|---|
| **Magnet ring** | The fixed physical scale and overall detent weight | Rarely — mode changes, user preference | **Yes** |
| **Motor** | Everything dynamic: end-stops, resistance ramping toward a limit, half-steps between magnet positions, per-context feel | Continuously, in milliseconds | No |
| **Vibration actuator** | Event confirmations layered on top | Per event | No |

The magnets matter because **the object must still feel like a mechanism with the power off.** Every motorised dial in existence is a dead plastic disc when unplugged; this one clicks like a watch bezel.

### Geometry to draw

- **60 steel poles** embedded near the inner surface of the rotating bezel, evenly spaced (6° apart). These set the detent count.
- **6 magnets** on a flat carrier ring on the stationary part, evenly spaced at 60°. Six, not one: a single magnet pulls the bezel sideways, loading one part of the bearing and producing a tight spot that travels as you turn. Evenly spaced magnets cancel each other's side forces.
- **Magnet counts that work with 60 poles: 3, 4, 5, 6, 10, 12.** Eight does **not** — 45° is seven and a half pole spacings, so half the magnets would pull toward a notch while the rest push away, and the detent half-cancels. Do not change one count without rechecking the other.
- **The carrier moves vertically**, up and down along the spin axis, with about 2 mm of travel. One flat ring lifted by one mechanism so every magnet moves identically. Magnetic force falls away sharply with distance, so 1–2 mm collapses the detent to nothing.
- **The lifting mechanism must hold position with no power.** A fine screw turned by a small motor, or a cam shallow enough that it cannot back-drive. Not a solenoid and not shape-memory wire — both need continuous current to hold a position, which breaks the unpowered-detent requirement.
- Because a screw can stop anywhere, **detent weight becomes continuously adjustable** rather than on or off — a user setting that physically changes the mechanism and survives a power cut, because it is a screw position rather than a stored number.

### Why 60

It divides usefully, so the same physical scale serves every screen: every 10th position (6) for the app selector, every 5th (12) for settings and menus, every position (60) for volume and brightness, and motor-generated half-steps (120) for fine scrubbing. 120 is also a dive-bezel click count. At 135 mm diameter, 60 positions is about 7 mm of travel per click at the rim — comfortably watch-like under a fingertip.

### Motor

A large-diameter ring motor surrounding the display. No catalogue part exists at this bore, so it is a custom item — note that turning force scales with radius, and at ~65 mm radius force is easy to generate. Large diameter makes it hard to *buy* and easy to make *strong*.

**Design the motor and the magnets together.** Any electric motor has natural lumpiness of its own, from its magnets lining up with its steel teeth. If the motor has one count of natural stops and the magnets a different count, or the same count but offset, the two beat against each other and produce a permanent grinding feel. Either specify a stator with almost no natural lumpiness, or lock its count and phase to the 60 poles by design.

---

## 3. Parts to remove

| Part | Why |
|---|---|
| `drive_wheel` | It drives the rotation sensor through a printed gear. Gears have slop, so the same physical position reads differently depending on which way you arrived — the detent then fires at a slightly different angle each direction, which is exactly what makes a dial feel cheap. The document elsewhere rejects gearing a motor for this reason and then accepts it for the sensor. |
| `wheel_mount` | Same assembly. |
| `REF_as5600` | Wrong class of sensor. It reads a magnet on the end of a spinning shaft, on the centre line — and our centre line is occupied by the display, which is why the gear exists. |

**Replace with ring sensing:** a ring of alternating magnetic poles bonded inside the bezel, read by a sensor looking sideways at it. The ams AS5304 / AS5306 / AS5311 family is built for exactly this. Optical or capacitive encoder rings solve it the same way. Nothing touches, nothing has slop, and the resolution is far higher.

**Keep this sensing ring magnetically separate from the detent magnets** — different radius, different height, or a steel shield between them. Two magnetic systems at the same radius will interfere.

---

## 4. Constraints not to break

- **135 mm outside diameter** — established, and the halo diffuser at 128 mm depends on it.
- **~250 g minimum mass**, concentrated low. The steel base plate does this and belongs at the bottom regardless.
- **Add hidden mass in the bezel.** Free-spin feel comes from inertia at the rim; a brass or steel insert concealed inside the aluminium adds it with nothing visible changing.
- **The halo fires downward and outward onto the desk** from the base skirt, never from the rotating part.
- **Captive cable must be replaceable.** The product claims no expiry date; an unreplaceable cable would contradict that. Route it so it can be changed behind a service screw.
- **Bezel is 3D printed for prototyping and CNC aluminium for production, with no other change to the assembly.** Keep the printed part swappable.
- **Wide 45° chamfer between knurl and glass, diamond-cut after anodising.** One bright ring of raw aluminium against matt black. This is the only jewellery on the object and it must survive the height reduction.

---

## 5. Questions the model cannot answer — for the physical rig

Build these before committing CNC drawings.

1. **Detent strength.** Target roughly 60–150 mNm peak, adjustable. Design the magnet ring for the top of that range: weakening it with the air gap is easy, exceeding what the magnets can deliver is impossible.
2. **How much does magnetic pull cost the free spin?** The vertical pull passes through the bearing. It takes up internal slack, so the knob loses any wobble and feels more precisely located — good. It also adds friction, so a free spin dies away sooner — a cost. Measure it, do not argue about it.
3. **Does vibration reach the fingers?** The vibration actuator sits on the base; the bezel spins on a bearing whose job is to isolate the two. Fire it and feel whether anything arrives at a finger on the ring, or whether it just buzzes the desk. This either validates or kills the current haptic plan in an afternoon.
4. **Rollers or a continuous race?** Print both and compare smoothness at 135 mm.
5. **Wobble at the rim.** A 135 mm ring has enough leverage that 0.05 mm of runout is felt. Measure it; it is the difference between expensive and cheap.

---

## 6. Words used here

| Term | Meaning |
|---|---|
| **Detent** | The click you feel as a knob steps from one position to the next. A camera aperture ring has them; most volume knobs do not. |
| **Preload** | Deliberate pressure applied to a bearing to remove its internal slack. Makes a mechanism feel tight and precise, at the cost of a little more friction. |
| **Backlash** | Slop in a gear train — the play you take up before the other side moves, so a position reads differently depending on which direction you approached from. |
| **Ring sensing** | Reading rotation from a ring of magnets bonded around the inside of the knob, with the sensor looking sideways at it. Needed because the centre is occupied by the display, so there is no shaft to put a magnet on. |
| **Cogging** | The lumpy resistance you feel turning an electric motor by hand, from its magnets lining up with its steel teeth. Usually a defect, occasionally deliberate. |
| **Vibration actuator (LRA)** | A tiny vibration motor — a weight on a spring punching back and forth in a straight line, fast enough to start and stop in thousandths of a second. That sharpness is what makes a buzz read as a click. It fakes a detent; nothing physically steps. |
| **Thin-section bearing** | A ring bearing whose walls are unusually thin for its diameter, so it takes up little space. Sold by bore size rather than as a standard series. |
