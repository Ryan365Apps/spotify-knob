# R&D brief — power budget and power architecture of the 60

**You are being handed one research strand of a hardware product.** You have no other
context; everything you need is here. Work from this brief, cite sources for
anything factual, and separate what you found from what you recommend. Use plain
English: explain every acronym the first time, and give numbers with units.

## The product, in two paragraphs

The 60 is a desk dial made by Cadrane: a Ø135 mm round touchscreen puck with a
heavy knurled metal ring — the knob — around the screen, sitting on a steel base,
34 mm tall. It connects to a computer by one USB-C cable and controls the
computer's audio, media playback, scrolling and calls. It is a heavy, expensive
watch for the desk; the quality of the ring's feel is the product. Limited series
of sixty units. Fixed principles you must respect: no cloud, no phone app, and
**no battery** — a battery gives the object an expiry date and the product is
designed to outlast its maker. Whether a supercapacitor counts as a battery is one
of your questions.

Inside it: a Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C development board (the
production unit will use the same module on a custom board), which carries an
ESP32-P4 processor, an ESP32-C6 Wi-Fi/Bluetooth module, a 3.4-inch 800 × 800
round display at 300 cd/m² with a 10-point touch panel (GT9271 controller), an
ES8311 audio codec, an ES7210 echo-cancellation chip, two microphones and a
connector for an 8 Ω 2 W speaker. Around it, added by us: a halo ring of SK6812
RGBW addressable LEDs under a diffuser at the base's edge (about 320 mm of strip
in a 324° arc; LED count not yet fixed); a vibration actuator (DRV2605L driver,
linear resonant actuator); a small N20 gearmotor turning a cam that lifts a
magnet carrier; a custom ring motor whose coils sit around six magnets and act on
sixty steel poles in the knob (torque target 30–100 mNm, not yet built); an
optical encoder; and, in a later revision, a quality DAC with a headphone/line
output so the device is also the computer's USB audio interface.

## The problem you are solving

The object is powered only by the USB-C cable from the computer. The design
currently assumes a 5 V, 500 mA supply (2.5 W) — the guaranteed minimum from an
ordinary USB 2.0 port — and because of that the halo is capped in firmware at
about 20% brightness. That cap was an assumption, never a measurement, and it has
just been noticed as a real limitation. Two new interaction decisions make the
problem worse:

1. The ring motor must be able to **cancel the magnetic detent completely while
   the ring spins at scrolling speed, for as long as a finger rests on a touch
   hotspot** — a continuous load, not a pulse.
2. The magnet carrier may need to move **fast** (a mode change in roughly 100 ms,
   several times a minute) instead of slowly a few times an hour, which changes
   what actuator drives it and how much current it takes.

On top of that the product must ring like a phone — halo pulsing, vibration
pulsing, speaker playing — while the screen is at full brightness, and a 2 W
speaker alone is most of a 2.5 W budget.

## What is asked for

**A. The load budget, honestly.** Build a table of every consumer with typical
and worst-case current at 5 V: the P4 module with Wi-Fi active and idle; the
display backlight at 100%, 50%, 20%; touch; the audio codec and speaker at 2 W
and at a realistic ringer level; the headphone/line DAC stage; the vibration
actuator; the N20 gearmotor stalled and running; the ring motor cancelling a
60–150 mNm detent continuously (estimate from coil resistance and torque
constant, state your assumptions); the encoder; the halo at 20%, 50%, 100% white
for a stated LED count (use the SK6812 RGBW datasheet — full white is on the order
of 60–80 mA per LED, confirm the figure). Then sum them for four scenarios:
*idle on the desk*, *scrolling with the detent cancelled*, *a call ringing*
(halo pulse + vibration + speaker + full screen), and *everything at once*. Say
which scenarios exceed 2.5 W, 4.5 W, 7.5 W and 15 W.

**B. What a computer's port can actually give.** Lay out the real-world supply
options and how the device can tell which it has: legacy USB 2.0 and 3.x ports
(500 mA / 900 mA); USB Type-C current advertisement over the CC line (1.5 A and
3 A at 5 V, i.e. 7.5 W and 15 W) and how a device detects it; USB Power Delivery
negotiation for 9 V and above and which sink-controller chips do it without
firmware effort (STUSB4500, CYPD3177 or equivalents — verify current parts);
Battery Charging 1.2 ports; what desktop motherboards, front-panel headers,
laptops, docks and Macs typically supply from their Type-C ports. Give the
honest distribution: what fraction of the buyer's likely ports deliver more than
500 mA, more than 1.5 A, PD.

**C. Architecture options, compared.** For each, give the power available, what
it costs in parts, height (the object must stay 34 mm tall), compliance burden,
and what it does to the one-cable promise and the no-battery principle:

1. Live within 5 V / 500 mA and scale the halo, motor and speaker to fit.
2. Detect Type-C 3 A and unlock features only when it is available, with
   graceful degradation on weaker ports.
3. Negotiate USB Power Delivery for a higher voltage for the motors, with a
   sink controller and a buck regulator.
4. A second power input (a second USB-C, or a barrel jack) with the data cable
   staying thin — against the objection that a second cable undermines the object.
5. A powered pass-through: a Y-cable or inline hub, or a Type-C dock in the
   cable, so the desk sees one cable.
6. An energy buffer for peaks: a supercapacitor bank sized for the ringer and
   motor bursts. Size it, cost it, give its lifetime and failure mode, and answer
   directly whether it violates "no battery" in spirit (does it wear out?).
7. Running the device from the audio-interface power class: USB audio devices
   are commonly bus-powered at 500 mA — say what the DAC path itself needs.

**D. The carrier question.** If the magnet carrier must move 3 mm in ~100 ms and
hold position unpowered, what actuator does that (fast gearmotor + cam,
solenoid + latch, voice coil, piezo, shape-memory alloy) and what peak current
and energy per move does each take? Compare the energy cost of *moving the carrier
per gesture* against the energy cost of *the motor cancelling the detent
continuously*; say which is cheaper over a typical hour of use and which is
cheaper at the worst moment.

**E. The halo at lower power.** How to get a halo that reads as generous in a
lit room without the current: LED count vs density, RGBW vs RGB, diffuser and
light-guide efficiency, current-limited peaks vs sustained output, whether the
"20% cap" is a perceptual problem at all once gamma and ambient sensing are done
properly. Give a target LED count and current for a convincing ring.

**F. Heat.** Where the watts go in a sealed 135 mm object with a steel base and an
aluminium ring, and at what continuous power the knob becomes noticeably warm to
the hand (that would be a product failure — the ring is what you touch).

**G. Compliance.** What USB-IF, CE and FCC obligations each architecture creates,
particularly PD negotiation and any energy storage.

## Form of the answer

A single document. Findings first, recommendations second, each with the evidence
behind it and a confidence. Numbers with units and working. Sources as links. A
recommended architecture, a fallback, and the first three bench measurements to
make (with the instrument — a USB power meter on the real board is the obvious
one). Flag anything in "the product" or "the problem" you believe is wrong,
separately, with evidence — do not silently design around it.
