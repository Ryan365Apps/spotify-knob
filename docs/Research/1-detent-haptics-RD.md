# R&D brief — the detent mechanism of the 60

**You are being handed one research strand of a hardware product.** You have no other
context; everything you need is here. Work from this brief, cite sources for
anything factual, and separate what you found from what you recommend.

## The product, in two paragraphs

The 60 is a desk dial made by Cadrane: a Ø135 mm round touchscreen puck with a
heavy knurled metal ring — the knob — around the screen, sitting on a steel base.
It controls audio and the operating system's media transport on a computer over
USB-C. It is positioned as a heavy, expensive watch for the desk that invites idle
handling: the quality of the ring's feel is the product. Anything that improves
the feel of the ring wins; anything competing with it for budget loses. Limited
series; the market is people who buy KEF-LSX-class desk audio. Nothing else about
it — no cloud, no battery, no phone app, no macros — is in scope for you.

The knob rides on three small V-groove wheels sitting in a ridge on its inner
surface (no ball bearing). It is 34 mm tall in total; the knob's skirt is 26 mm of
that. The ring is 3D-printed for prototypes and CNC aluminium in production, with
nothing else changing. **Sixty** is the number of physical detent positions per
turn, and the product is named after it.

## What is already decided — do not re-litigate

These were settled after argument; treat them as constraints unless you find
hard evidence that one is physically impossible, in which case say so plainly.

1. **Three layers of feel.** A *magnet ring* provides the fixed physical scale (60
   positions) and the overall detent weight, and works with no power. A *motor*
   provides everything dynamic: end-stops, resistance ramping toward a limit,
   half-steps between magnet positions, per-context feel. A *vibration actuator*
   (LRA class) provides event confirmations layered on top.
2. **The object must feel like a mechanism with the power off.** Every motorised
   dial on the market is a dead plastic disc unplugged; this one must click like a
   watch bezel. That is why the magnets exist.
3. **Steel on the rotor, magnets on the stator.** Sixty steel poles (currently M2.5
   grub screws, 6.4 mm pitch) are threaded radially into the knob's inner wall at
   Ø122.8. Six N42 magnets (3 × 6 × 3 mm) sit on a stationary carrier ring inside
   the knob, facing outward, radially across a gap of about 0.8 mm. Six, not one:
   evenly spaced magnets cancel each other's side-load. Valid magnet counts for 60
   poles are 3, 4, 5, 6, 10, 12 — eight does not work.
4. **The carrier moves vertically, about 3 mm**, to slide the magnets off the poles'
   height and weaken the detent. It is lifted by a cam ring (three 5.5° helical
   ramps, self-locking) turned by a small gearmotor through a worm — it holds
   position with no power. It moves at gesture cadence (mode changes, a few times
   an hour), **not** per detent. Dynamic detent strength comes from the motor, not
   from moving the magnets.
5. **Motor and magnets are designed together.** A motor has its own natural
   lumpiness (cogging); if its count differs from 60, or matches but is out of
   phase, the two beat and the feel is permanently gritty. Either the motor's
   cogging is near zero or it is locked to the 60 poles in count and phase. The
   current design intent is that the six magnets and sixty poles *are* the motor's
   magnetic circuit: coils around the six magnets turn the detent ring into a
   hybrid-stepper-like machine whose cogging is the detent by construction.
6. **Target detent strength 60–150 mNm peak, adjustable.** Design for the top of the
   range; weakening is easy, exceeding the magnets is impossible.
7. Sensing is a separate optical encoder on the knob's inner wall; it is not your
   problem except where your findings constrain its placement.

Geometry you may need: pole pitch circle Ø122.8; magnet carrier ring r 57.5–61.0;
steel poles Ø2.5 at z = 15 mm above the base; the knob's mass is ~85 g printed and
will be ~180 g in aluminium; the wheels give near-zero rolling friction; the
whole object must stay 34 mm tall.

## What is asked for

**A. State of the art in rotary haptic input devices.** Survey what exists and
how it feels, with the mechanism behind each: SmartKnob (Scott Bezek) and its
derivatives; the Apple Digital Crown; automotive rotary controllers (BMW iDrive,
Audi MMI, Mercedes, Porsche, Genesis) and their detent implementations; Surface
Dial; Nuimo; camera lens rings and the Fuji/Leica aperture click; watch bezels
(dive-bezel ratchets, the Rolex/Omega click mechanisms); Loupedeck, Stream Deck+,
Monogram; pro audio encoders (Elektron, Native Instruments, Ableton Push); the
Griffin PowerMate. For each: detent mechanism, count, torque if published, whether
it works unpowered, what people say it feels like, and what is patented.

**B. Physics of the magnetic detent as designed.** Estimate, with working, the
peak detent torque for six 3 × 6 × 3 N42 magnets facing Ø2.5 steel poles across
0.8 mm at r 60: attraction force per pole, tangential component vs angular offset,
sum over six magnets, torque at the rim. State the sensitivity to gap (0.4, 0.8,
1.2, 2.0 mm) and to magnet grade and size. Say whether the 60–150 mNm target is
reachable, and what the lowered position (magnets 3 mm below the poles) leaves as
residual torque — we suspect a radial-gap detent fades gradually rather than
switching off, and want that quantified. Recommend a magnet size/grade and pole
diameter, and whether the poles should be plain steel, hardened, or something
else.

**C. The motor.** Evaluate the "coils around the six magnets" idea honestly: is a
six-pole, sixty-tooth hybrid/variable-reluctance ring machine at r 60 able to
deliver useful torque (say 30–100 mNm) with coils that fit in a 3.5 × 5 mm annulus
per pole, at 5 V USB power? What is its cogging, and is it really locked to the
detent by construction? Compare against alternatives that keep the 34 mm height:
a custom axial-flux ring stator under the knob; a small BLDC driving the knob's
rim through a friction wheel (rejected once for slip/backlash — say whether that
rejection holds); direct-drive gimbal motors; and voice-coil approaches. For each:
torque, cogging, height, cost, complexity, and what it does to the unpowered
feel. Recommend one, and what to test first.

**D. Control and synchronisation.** How should firmware combine the passive
magnetic detent with the driven layer so they reinforce rather than fight — phase
alignment, position sensing resolution required, control loop rate, how end-stops
and ramps should feel, how half-steps are generated between magnet positions.
Draw on the SmartKnob firmware, haptic-rendering literature (Hayward, MacLean,
Okamura), and automotive haptic-knob papers. Say what sensing resolution and
latency the mechanism demands.

**E. The rig.** Design a bench rig to answer five open questions before any
production drawing: detent strength (light enough for the motor to overpower,
satisfying unpowered); what magnetic pull costs the free spin; whether the
vibration actuator on the base reaches the fingers at all across the wheels;
rollers vs a continuous race at Ø135; wobble at the rim (0.05 mm is felt). For
each: the measurement, the instrument, the pass/fail number.

## Form of the answer

A single document. Findings first, recommendations second, each recommendation
with the evidence behind it and a confidence. Numbers with units and working.
Sources as links. A short table of parameters you would change in the CAD, with
values. Flag anything in "already decided" you believe is wrong, separately, with
the evidence — do not silently design around it.
