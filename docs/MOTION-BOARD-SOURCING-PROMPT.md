# Handoff prompt — how should the device's motion, haptic and lighting functions be built?

Copy everything below the line into a new session.

---

## The premise

I am building **one working prototype** of a premium haptic desk dial. A production run of sixty to seventy units exists as a plan, but it is not what this exercise is about. Treat volume sourcing as a secondary check — a "does this dead-end later" flag on your recommendation — not as a constraint that rules anything out. **A single hand-built development board that I can buy one of, this week, is a perfectly good answer.** Minimum order quantities, unit price at volume, and certification are all secondary.

## Your job

Below is a list of **things the device has to do**. Not a list of things a board has to do — there is a difference, and it matters.

The current design answers all of them with **one custom four-layer circuit board**, designed by a contractor, with about twenty-five bought components on it. That board does not exist yet. It is the most complex and hardest-to-source item in the whole project, and I want to know whether I actually need it.

**Tell me where each function should live, in this order of preference:**

1. **On something already in the device.** There is a Raspberry Pi 5 in it already, running the display and the application software, and already connected to the host computer by USB. If it can do a job properly, that job costs nothing.
2. **On something I can buy.** A development board, a module, a kit — any combination of two or three of them wired together. I would take an ugly stack of three bought boards on short cables over one elegant custom board without hesitating.
3. **On a custom board, and only what genuinely cannot go anywhere else.** If the answer is that some small hard-real-time core still needs building, tell me — but tell me how small it can be made once everything else has been moved off it.

**Do not design a circuit board.** No schematic, no layout, no parts list for a custom board. If your honest conclusion is that a custom board is unavoidable, say so in your first paragraph and spend the rest explaining what it is left doing and why nothing else can do it.

## What the device has to do

Six functions. **How they are grouped onto boards is your output, not my input** — the grouping in the current design is exactly what I am asking you to challenge.

**A. Render sixty detents per revolution, plus end stops and slow self-rotation.** A 2804-frame gimbal brushless motor pressing against the inside of the knob through a silicone friction band. Field-oriented control at a few kilohertz. The open-source SmartKnob project is the reference implementation of this exact idea and uses a TMC6300 driver with the SimpleFOC library. **This is the one function with a hard real-time requirement** — the feel of the knob must never be disturbed by anything else happening in the object.

**B. Know the motor's rotor angle.** An MT6701 absolute magnetic sensor on the motor shaft, serial interface. Inseparable from A in practice — it is what the control loop reads.

**C. Know the knob's angle, independently of the motor.** A Broadcom AEDR-8300 reflective optical encoder reading a code ring on the underside of the knob. Quadrature, about 5,000 counts per revolution. **See the note below — this is the awkward one.**

**D. Engage and release the clutch.** A 1.5 gram linear servo on a standard hobby pulse signal, moving 2.4 mm to lift the motor clear of the knob for free-spin. This happens occasionally, not continuously — it is not a real-time job by any reasonable definition.

**E. Fire a vibration actuator.** A linear resonant actuator through a TI DRV2605L haptic driver over I²C. Event-driven.

**F. Light up to ninety addressable LEDs.** WS2812B/SK6812 type, single-wire at 800 kHz — a continuous 2.7 millisecond bit-stream per frame that cannot tolerate jitter. Needs a 3.3 V to 5 V level shifter of the HCT family. Up to 3.3 A at 5 V, fed separately from any signal board.

**G. Send scroll, volume and key events to the host computer with no driver installed.** A knob turn should become a scroll event, and volume changes should use the standard consumer-control usages that Windows and macOS already understand. Today this is done by a microcontroller enumerating as a USB keyboard and mouse.

## Two functions I have deliberately left off that list

Both are in the current design, and both exist **only because of the architecture, not because the device needs them**:

- **A serial link between the motion board and the Pi.** That link exists to join two boards. If the functions land differently, it may not need to exist at all.
- **"Run with no operating system, on a hard timer."** That is a property required by function A, not a function in its own right. Do not let it drag functions D, E, F and G onto a bare-metal microcontroller by association — ask separately, for each one, whether it actually needs that.

**Function G is the one I most suspect is misplaced.** The Pi 5 is already plugged into the host computer by USB and can be put into USB gadget mode, where it presents itself as whatever kind of device it declares. If the Pi can be the keyboard and mouse, then function G costs nothing and the microcontroller stops needing a USB stack. **Check this properly** — what Linux's USB gadget framework actually supports on a Pi 5, whether both a keyboard-and-mouse composite device and the existing USB roles can coexist, and what the latency looks like from a knob event to a scroll event on the host.

**Function F is the second one.** The Pi 5 has programmable input/output hardware that has been used to drive addressable LED strings. Find out whether it does it reliably under Linux with other things running, or whether the timing falls apart in practice.

## The awkward bit you must not gloss over

**Functions B and C are separate on purpose, and nothing you find will expect that.** SmartKnob reads the motor's own sensor and calls it the knob angle, because its motor is rigidly coupled to the knob. Mine is not — there is a friction band and a clutch, so the motor angle and the knob angle can diverge, and the knob's own optical encoder is the one that tells the truth. This is the genuinely novel control problem in the product and no prior art addresses it.

So when you assess any board: **does it have a spare quadrature input, or spare pins on a peripheral that can decode quadrature, on top of whatever it uses for the motor's own sensor?** A board that consumes every pin driving the motor is not a candidate however good its motor control is.

## Specific things to check

Named starting points, so you are not beginning from nothing. Check each, say what it covers and what it does not, and link your sources.

1. **The Raspberry Pi 5 itself** — against functions D, E, F and G, and say explicitly why it cannot do A. Be concrete about real-time behaviour, its programmable input/output hardware, its pulse-width and serial peripherals, and its USB gadget capability. I want to know which jobs it does *properly* — no visible or audible artefacts — not which ones "mostly work".
2. **SmartKnob.** Apache 2.0 open source, and **SeedLabs sells a development kit**. Find out what is actually purchasable as a single item, at what price, shipped to the UK, and how soon. A board designed for exactly this application and already debugged by someone else is worth a great deal. Say what it does not do — I believe eight LEDs rather than ninety, no clutch servo, no separate optical encoder, and a serial device rather than a keyboard and mouse.
3. **A bought microcontroller board plus a bought motor driver board.** Raspberry Pi Pico 2, Arduino Nano, Teensy, an ESP32 board — paired with **SimpleFOC Mini**, **SimpleFOC Shield**, **ST B-G431B-ESC1**, **MKS ESP32 FOC**, or anything else you find. Give me the specific combination with part numbers and prices.
4. **Anything that does the motor and its sensor together on one bought board**, which is the hardest part to buy.

## Constraints, in order of how much they matter

- **It has to work, once, on a bench, soon.** That is the whole test.
- **Space.** The object is 175 mm across and 36 mm tall and it is full. The current custom board is budgeted at 30 × 30 × 3.6 mm sitting on top of a blower fan. **Anything you recommend will probably be bigger.** Do not quietly ignore that — give me actual dimensions, and treat "this needs more room than the model currently has" as a finding to report. For a prototype I will make room. I would far rather re-cut the mechanical design than commission a circuit board.
- **UK sourcing, one of each.** Prices in pounds where you can, and whether it ships here and roughly how fast.
- **Volume, as a footnote only.** For each recommendation, one line on whether it dead-ends at sixty to seventy units.

## What to give me back

1. **The recommendation in one paragraph at the top.** What to buy, what it costs, and what — if anything — still has to be built.
2. **An allocation table**: functions A to G down the side; for each one, where it lives in your recommendation, and a note. Make the "still needs a custom board" rows obvious.
3. **Two or three alternative allocations** with the same table, so I can see the trade.
4. **Anything left over** that nothing covers, and the cheapest honest way to close it.
5. **What to buy this week**, with links and prices, to test the recommendation on a bench.
6. **What could go wrong** — where a bought board or a Pi-side implementation would let me down later: pins, timing, firmware, supply, or a community that has moved on.

Every claim about a specific board or chip's capability must come from a datasheet, a schematic, a vendor page, or a repository, with the source linked. Where a vendor does not publish something, write **not published** rather than estimating. Do not tell me a board "should be able to" do something.

## Style

Plain English. Explain any acronym or abbreviation the first time you use it. Critical thinking rather than enthusiasm — if the honest answer is that I have to build a board after all, say so in the first paragraph.
