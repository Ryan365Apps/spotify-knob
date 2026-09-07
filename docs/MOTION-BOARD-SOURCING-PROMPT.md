# Handoff prompt — source a ready-made board for the motion functions

Copy everything below the line into a new session.

---

## Your job

I am building a premium haptic desk dial in a run of about 60 units. One custom circuit board in it — the **motion board** — has become the most complex and hardest-to-source part of the project, and I do not want to have it designed and manufactured if I can avoid it.

**Find me something I can buy.** A development board, a module, a kit, or a small stack of two or three bought boards wired together, that covers as much of the motion board's job as possible. I would take a board that does 80 per cent without hesitation. I would seriously consider one that does 50 per cent if the remaining 50 per cent is something simple I can bolt on.

**The mantra is buy convenience.** I am one person. Sourcing 25 line items, having a four-layer board laid out by a contractor, and debugging it is a cost measured in months, not pounds. A bought board that is twice the unit price and half as elegant but exists today and has a community behind it is the better answer, and you should say so if you find one.

**Do not design a circuit board.** Do not produce a schematic, a parts list for a custom board, or a layout. If your honest conclusion is that nothing suitable exists, say that plainly and say what the closest thing is and what it is missing — that is a useful answer too.

## What the motion board has to do

Nine jobs. They are listed roughly in order of how hard they are to buy.

1. **Drive a gimbal brushless motor with field-oriented control** at a few kilohertz, to render sixty detents per revolution, end stops, and slow self-rotation. The motor is a 2804-frame gimbal motor — high resistance, low current, about 1 A. It presses against the inside of the knob through a silicone friction band. The reference implementation for this whole idea is the open-source SmartKnob, which uses a TMC6300 driver and the SimpleFOC library.
2. **Read the motor's rotor angle** from a magnetic sensor (MT6701, absolute, serial interface) mounted on the motor shaft.
3. **Read the knob's angle separately**, from a reflective optical encoder (Broadcom AEDR-8300 family) looking at a code ring on the underside of the knob. Quadrature, about 5,000 counts per revolution. *See the note below — this is the one thing no bought board will have thought about.*
4. **Drive up to 90 addressable LEDs** (WS2812B/SK6812 type, 800 kHz single-wire). This is a continuous 2.7 ms jitter-intolerant bit-stream per frame. Needs a 3.3 V → 5 V level shifter of the HCT family.
5. **Drive a 1.5 gram linear servo** — a hobby-style servo on a standard pulse signal. It moves a clutch 2.4 mm to lift the motor clear of the knob for free-spin.
6. **Drive a linear resonant vibration actuator** (TI DRV2605L haptic driver over I²C, 170 Hz actuator).
7. **Present itself to the host computer as a USB keyboard and mouse** so that a knob turn becomes a scroll event with nothing in between — no driver, no software layer. Consumer-control usages for volume.
8. **Talk to a Raspberry Pi 5** over a plain serial link at gesture cadence. The Pi runs the display and the application software.
9. **Run all of the above with no operating system**, on a hard timer, so the feel of the knob is never disturbed by anything else.

## The questions I actually want answered

**Answer these directly. Do not give me a survey of the market.**

1. **Can the Raspberry Pi 5 do any of this itself?** It is already in the product. My instinct is that the motor loop cannot live on Linux, but the servo, the LEDs, and the vibration actuator all look like things a Pi might handle. Tell me which of the nine jobs a Pi 5 can do properly — meaning without visible or audible artefacts, not "it mostly works" — and which it cannot, and why. Be specific about real-time behaviour and jitter, and about what Pi hardware (its programmable input/output, its PWM peripherals, its SPI and I²C) actually gives you.

2. **Can a bought microcontroller board — a Raspberry Pi Pico 2, an Arduino Nano, a Teensy, an ESP32 board — plus a bought motor driver board do the job?** This is my leading hypothesis. Two or three cheap boards on a short cable beats one custom board. Tell me the specific combination, with part numbers and prices, and what it costs me in board area and cable count.

3. **Is there a single board that does the motor and the sensor together?** Named starting points, not an exhaustive list — check each and tell me what it does and does not cover: **SimpleFOC Mini**, **SimpleFOC Shield**, **ST B-G431B-ESC1**, **MKS ESP32 FOC**, **Mechaduino / SimpleFOC-compatible boards**, and anything else you find. For each: does it fit, does it drive a gimbal motor at low current, does it take an absolute magnetic sensor, does it do USB HID.

4. **Can I buy SmartKnob's board?** SmartKnob is Apache 2.0 open source, and **SeedLabs sells a development kit**. Find out what is actually purchasable — a bare board, an assembled board, a whole kit — at what price, in what quantity, and to the UK. A board designed for exactly this application, already debugged by someone else, is worth a lot even if I have to change its firmware. Tell me what it does not do: I believe it has only eight LEDs, no clutch servo, no separate optical encoder, and it presents itself as a serial device rather than a keyboard and mouse.

5. **What is the split that minimises the amount I have to build?** I am completely open to the answer being three bought boards in a stack rather than one. Give me a concrete recommendation, with what goes on each board and what wires between them.

## The awkward bit you must not gloss over

**Jobs 2 and 3 are separate on purpose, and no bought board will expect that.** SmartKnob reads the motor's own sensor and calls it the knob angle, because its motor is rigidly coupled to the knob. Mine is not — there is a friction band and a clutch, so the motor angle and the knob angle can diverge, and the knob's own optical encoder is the one that tells the truth. This is the genuinely novel control problem in the product.

So when you assess a board, check specifically: **does it have a spare quadrature input, or spare pins with a peripheral that can decode quadrature, on top of whatever it uses for the motor's own sensor?** A board that consumes every pin driving the motor is not a candidate no matter how good the motor control is.

## Hard constraints

- **Quantity: about 60 to 70 units.** Not one prototype, and not ten thousand. This kills anything with a minimum order of hundreds, and it kills anything only available as a single hand-built development board.
- **Space is very tight.** The current custom design is budgeted at **30 × 30 × 3.6 mm** sitting on top of a blower fan inside a 175 mm diameter, 36 mm tall object. **A bought board will almost certainly be bigger than this.** Do not silently ignore that. Tell me the actual dimensions of anything you recommend, and treat "this needs more room than the model currently has" as a finding to report, not a disqualification. I would rather re-cut the mechanical design than commission a circuit board.
- **The 90-LED string draws up to 3.3 A at 5 V.** That current does not want to go through a small development board's traces. Assume the LED power is fed separately and only the data line comes from the board — but confirm that whatever you recommend can generate that signal cleanly.
- **UK sourcing.** Prices in pounds where you can, and say whether it ships to the UK and roughly how fast.
- **No FCC/CE certification carries over** from a development board to my product, so do not weigh that either way.

## What to give me back

A single document, in this shape:

1. **The recommendation, in one paragraph, at the top.** What to buy, what it costs, what it covers, and what I still have to build.
2. **A coverage table**: the nine jobs down the side, your recommended option across the top, and for each cell "covered / partly covered / not covered", with a note.
3. **Two or three alternatives**, each with the same coverage table, so I can see the trade.
4. **What is left over** — the jobs nothing covers — and the cheapest honest way to close each one.
5. **What I should buy this week to test the recommendation**, with links and prices. Bench samples, not production quantities.
6. **What could go wrong.** Where a bought board would let me down later: pins, timing, firmware, supply, or a community that has moved on.

Every claim about a specific board's capability must come from its datasheet, its schematic, its vendor page, or its repository, and you must link the source. Where a vendor does not publish something, say **not published** rather than estimating. Do not tell me a board "should be able to" do something.

## Style

Plain English. Explain any acronym or abbreviation the first time you use it. I want critical thinking, not enthusiasm — if the honest answer is that I have to build the board after all, tell me that in the first paragraph and spend the rest of the document explaining why nothing else works.
