# the 60 — board 3 of 3: the motion board

**Date: 5 September 2026. Status: design brief, not yet drawn.** Written to be handed to a contract electronics designer with no further conversation needed to start. Everything here is sourced; anything a vendor does not publish is marked **not published**, and anything I concluded rather than read is marked **judgement**.

Companion documents: `the60-board-carrier.md`, `the60-board-audio.md`, `the60-electronics-build-path.md`, `SOURCING-BOM.md`.

---

## 0. Four findings that change the parts list — read these first

| | Finding | Severity |
|---|---|---|
| **A** | **The two Abracon supercapacitors in the sourcing document cannot do the job and must be replaced.** They are lithium-ion hybrid cells rated **80 mA continuous, 420 mA peak, 600 mΩ each**. The motor driver pulls up to 2 A. Two in series is 1.2 Ω of resistance — at 1 A the resistance alone drops 1.2 V. It is a backup-energy cell, not a pulse cell, and asking it to do this shortens its life | **Blocking** |
| **B** | **The chosen encoder gives 4,300-5,400 counts per revolution, not "well over ten thousand"** as the sourcing document states. It is a 75-lines-per-inch part. It is also **5 V only** and its outputs will destroy a 3.3 V microcontroller pin without a buffer. A better part in the same family may fix both | **Correction** |
| **C** | **The motor driver's sense pins cannot be used for current feedback.** One of them is the shared footpoint of two bridges. SimpleFOC's maintainer: *"we support 2 or 3 shunts, but not just one, and not with 2 phases combined on one shunt"* | **Design-defining** |
| **D** | **The recommended microcontroller's analogue converter is unsuitable for current sensing** — but per finding C we were never going to get current sensing from this driver anyway, so it costs nothing we had | **Design-defining** |

---

## 1. What this board is

Everything that must happen on time, every time, so that the feel of the knob is never disturbed by the graphics. It runs one loop, forever, with no operating system.

It drives the gimbal motor with field-oriented control at a few kilohertz to render sixty detents per revolution, end stops, and slow self-rotation. It reads the knob's angle from the optical encoder and the motor's rotor angle from a magnetic sensor. It drives the clutch servo that sets how hard the motor presses. It drives the vibration actuator. It drives up to ninety addressable LEDs. It presents itself to the computer as **a keyboard and a mouse with a scroll wheel**, so a knob turn becomes a scroll event with nothing in between. And it talks to the compute module over a serial link at gesture cadence.

It sits behind the internal USB hub as a third downstream device.

---

## 2. The microcontroller: Raspberry Pi RP2350

**Recommendation: RP2350B** (80-pin, 10 x 10 mm, 48 general-purpose pins) with external flash, or the RP2350A (60-pin, 30 pins) if the pin count closes. **$0.90 at reel.**

**The reasons, in order of weight:**

1. **The ninety-LED string is the hard scheduling problem, not the motor loop.** Ninety LEDs at 24 bits and 1.25 µs a bit is **2.70 ms of continuous, jitter-intolerant bit-stream** every refresh — 17 % duty on one pin, forever. On a microcontroller without programmable input/output blocks you solve this with direct-memory-access tricks that eat a timer, several channels and 2.2 kB of memory. Here it is **one state machine and one channel**, genuinely free of the processor, and there are twelve state machines.
2. **Two cores.** One runs the motor loop and sensors on a hard timer; the other runs USB, the serial link and LED frame composition. That is real isolation, which is the entire architectural premise of this board.
3. **Quadrature decoding costs nothing** — another state machine, no interrupts.
4. **Price and supply**, direct from Raspberry Pi with no allocation history. The obvious alternative, an STM32G431, is four to eight times the price with a worse supply record.
5. **The software is first-party.** The Pico software development kit plus TinyUSB, whose composite keyboard-and-mouse example builds for this chip out of the box. And SimpleFOC has supported it in the main release since August 2025.

**The cost of the choice: no on-chip current sensing.** The analogue converter is 500 ksamples/s with no timer-triggered injected mode, and SimpleFOC say directly that it *"is not sufficient for low-side current sensing."* Per finding C we lose nothing, because the driver cannot present independent shunts anyway.

**If current-sensed control later proves non-negotiable**, the answer is not a different microcontroller — it is in-line sense amplifiers, after which either chip works. At that point the **STM32G431CB** becomes attractive because its three internal amplifiers can take the shunts with no external parts. That is a coherent alternative architecture; it costs the programmable blocks and the second core.

**⚠ Two things the contractor must be told.**

**Erratum E9.** Every general-purpose pin, when configured as an input sitting at an intermediate voltage, leaks up to **120 µA** and overwhelms the internal pull-downs. The official workaround is an **external pull of 8.2 kΩ or less** on every input pin. No fixed silicon has shipped. This is a bill-of-materials line, not a blocker.

**The stock quadrature decoder example did not work on this chip** when the issue was opened in September 2024, and I could not verify it is fixed. **Prove it on day one.**

**Pin budget on the smaller package (30 pins):** motor 6, driver enable and diagnostic 2, motor sensor 3, knob encoder 2, servo 1, haptic driver 3, LED data 1, buffer enable 1, serial link 2, current-sense spares 2, status and spare 2 — **25 of 30**. It fits, with five spare. **Take the larger package anyway** for a sixty-unit run, where a board respin costs more than twenty pence of package.

---

## 3. The motor driver: TMC6300-LA-T

| Parameter | Value |
|---|---|
| Bridge supply | **2 V (1.8 V min) to 11 V** |
| Peak output current | **2 A** |
| Maximum continuous per bridge below 110 °C | **1.0 A** |
| Design guideline | 1.0 A at 2.1 V, 1.2 A at 2.2 V, **1.4 A at 2.5 V** |
| On-resistance | 170 mΩ each side, typical |
| Standby current | under 50 nA |
| Short-circuit detection | 1 µs, three retries then latch |
| Switching | 20 ns rise, 7 ns fall, 250-500 ns input to output |

**Control is six logic pins, one per transistor. No serial bus, no registers, no configuration.** Internal break-before-make logic prevents shoot-through. SimpleFOC's `BLDCDriver6PWM` drives it with no driver-specific code.

**There is no separate enable pin.** Pin 11 is both the digital supply and the enable: pull it to ground and the part goes to standby and resets. **Do not tie it hard to 3.3 V** — drive it from a microcontroller pin or a load switch, because the diagnostic output only clears on a supply cycle.

**Decoupling, exactly as specified:**

| Node | Value |
|---|---|
| VS (pin 18) | **≥10 µF ceramic**, or 100 µF electrolytic, near the pin |
| 1.8VOUT (pin 13) | **100 nF ceramic**, near the pin |
| VIO (pin 11) | 100 nF |
| VCP (pin 2) | 1-100 nF to VS — the datasheet recommends it when several bridges switch together, **which is exactly what this control scheme does. Fit it** |

**Thermal — the 3 x 3 mm problem.** Datasheet, verbatim: *"thermal properties of the PCB design become critical for the tiny QFN 3 mm x 3 mm package at or above 1.4 A motor current… For currents above 1.4 A, a 4-layer PCB layout with 5 via contact of the die attach pad to the GND plane is required."* At 1.0 A the conduction loss is about 0.34 W, a 14 °C rise on four layers — comfortable. **Specify four layers and at least five thermal vias in the pad.** This is the most common way this part gets ruined.

**Can it drive the motor? Yes, comfortably** — a 2804-frame gimbal motor is a high-resistance, low-current part, and the open-source SmartKnob drives an almost identical motor with this exact chip and calls it *"a perfect match."*

**What torque? Cannot be calculated.** JD-Power publish nothing for the MY-3514C beyond its size, a hollow shaft, an included magnet and a price. No speed constant, no phase resistance, no inductance, no pole count. **This must be measured on the bench** — SimpleFOC has estimation routines, plus a lever arm and a scale. Budget a day.

**A lever worth knowing about:** the driver accepts up to 11 V. Raising the motor rail above 5 V is the cheapest torque available — the current limit stays but the voltage available against back-EMF roughly doubles, and with it the sharpness of a detent edge. **Consider a small boost converter for the motor rail alone, and decide it on the bench.**

---

## 4. Current sensing — the decision

**Option 1, for the first board: voltage-mode control, no current sensing.** Tie both sense footpoints directly to the ground plane. This is what SmartKnob does, and SmartKnob is the acknowledged benchmark for hand feel. Zero extra parts, zero calibration.

**The reasoning that matters:** the silicone friction band's torsional compliance is almost certainly the dominant limit on how sharp a click can be, not whether the current is measured. **Prove that on the bench before spending board area.**

**Option 2, the upgrade path — lay the footprints out and leave them unfitted.** Two shunts in the **phase output lines**, not at the driver's sense pins, with the third phase derived by arithmetic.

| Part | Value | Notes |
|---|---|---|
| Shunt | **50 mΩ, 1 %, ≥1 W, 2512** | At 1.2 A that is 60 mV and 72 mW. Kelvin footprint mandatory. Susumu KRL6432E-C-R050-F-T1, or Vishay WSLP2512R0500FEA |
| Amplifier | **TI INA240A1** (20 V/V) | ±1.6 A maps to ±1.6 V on a 1.65 V mid-rail — a good fit for a 3.3 V converter. Its **enhanced rejection of pulse-width-modulation transients** is the reason to choose this family |

**Instruction to the contractor:** route the phase lines through 2512 Kelvin pads with 0 Ω links fitted, so a shunt can be swapped in on the bench without a board respin.

---

## 5. Sensors

### 5.1 Motor rotor angle — MT6701CT-STD, in serial mode

**Use the serial interface, not I²C.** Three reasons: it is **absolute**, so the control loop knows the electrical angle at power-on with no alignment sweep — a visible, audible twitch on a premium object; it carries **six bits of error check on every reading**, which matters a few millimetres from a switching bridge; and SimpleFOC supports it directly and rates it *"fully functional and tested."* SmartKnob chose this part for exactly these reasons. The library's own README says the I²C output *"is probably too slow for high performance motor control."*

14-bit absolute, 24-bit frame, clock period at least 64 ns. At 10 MHz a frame takes 2.4 µs — 1.2 % of a 200 µs control budget.

| Parameter | Spec |
|---|---|
| Magnet | **Ø6 x 2.5 mm, diametrically magnetised** — matches the chosen part exactly |
| Field at the sensor | 200-1,000 Gauss |
| Air gap | **0.5-2.0 mm** |
| **Lateral misalignment** | **0.3 mm maximum** |
| Supply | 3.3-5.0 V, 10-14 mA |
| Application circuit | 0.1 µF on the supply; the datasheet recommends 6 V transient suppressors on the signal pins |

**The 0.3 mm lateral tolerance is the tight one.** The sensor die must sit on the shaft axis within 0.3 mm. **Give the contractor a dimensioned datum, not "centre it."**

**Two caveats from the library:** the serial implementation *"reportedly struggles when sharing an SPI bus with other devices"* — **give it its own peripheral**; and programming its memory requires 5 V, so **put a 5 V-capable programming jumper or test pads on the board** for factory calibration, even though normal use never writes to it.

**⚠ Which shaft end carries the magnet is not published.** It decides the height stack and whether the sensor board sits above or below the motor. **Buy three motors now and measure.** Two mitigations for the layout: put the sensor on a small satellite board on a flying lead so its position is a mechanical decision, or put the footprint on the underside of this board with a clearance window, which is what SmartKnob does.

### 5.2 Knob angle — the AEDR-8300 family, and a part swap to consider

The chosen `-1K2` is **75 lines per inch**, which on our ring gives:

| Strip diameter | Counts per revolution | Counts per detent |
|---|---|---|
| 116 mm | 4,304 | 71.7 |
| 135 mm | 5,009 | 83.5 |
| 145 mm | 5,381 | 89.7 |

**Is 72-90 counts per detent enough? Yes, comfortably** — far finer than the hand can resolve. **But it is two to three times coarser than the sourcing document assumed**, so any haptic modelling that relied on the higher figure should be re-read.

**Electrical:**

| Parameter | Value |
|---|---|
| Supply | **4.5-5.5 V. This is a 5 V part** |
| **Light-emitting diode resistor** | **220 Ω ±10 %** from the 5 V rail to pin 3. The only external component the datasheet specifies |
| Outputs | **TTL push-pull**, not open-collector. 2.4 V high, 0.4 V low |
| Maximum count frequency | 30 kHz — about 1,670 rpm on our ring. No constraint on a hand |
| Working gap | **1.0 min, 2.0 typical, 2.5 max mm** |
| Alignment | ±0.38 mm radial and tangential, ±1.5° angular |

**The 5 V outputs must be level-shifted.** The recommendation is **SN74LVC2G17DBVR** — a dual Schmitt buffer running from 3.3 V with 5 V-tolerant inputs. One part, adds hysteresis, costs pennies, and it also satisfies the erratum requirement because it drives the pin actively rather than leaving it near mid-rail. **Put the buffer at the microcontroller end**, so the higher-noise-margin 5 V signal travels the long distance and the fragile 3.3 V one travels a few millimetres.

**⚠ Two reasons to revisit the part choice before the bill of materials is locked.** Farnell UK list the `-1K2` as **"No Longer Stocked."** And the **`-1W2` variant is 212 lines per inch with a 3.0-5.5 V supply** — 2.8 times the resolution *and* it removes the level-shifting problem entirely, in the same package with the same 1.0-2.5 mm gap. **Read its datasheet and check stock at 70 pieces before committing.**

**The code strip is a custom part.** Broadcom's own code wheels are transmissive metal discs and will not work. Requirements: reflective areas 60-85 % reflectance, non-reflective under 10 %, window-to-bar ratio 0.9-1.1, bar radial extent 1.80-2.31 mm, pitch 0.3387 mm at 75 lines per inch. Real suppliers: **MELTEC** (Japan), **PWB Encoders** (Germany), **Laser Lab** (USA), **Optry Tech** (China, low minimum). **Thickness and substrate are unsourced**; chrome on polyester bonded into a recess is the standard answer and 0.15 mm is our assumption, not a vendor's.

---

## 6. The halo — ninety LEDs

**Timing:** 800 kHz, 1.25 µs per bit, 24 bits per LED, latch over 80 µs. Ninety LEDs is **2.70 ms per frame**.

**Level shifting is required, not optional.** The LED's high-input threshold is **0.7 × supply** — at 5 V that is **3.50 V**, above what a 3.3 V pin can output. A 3.3 V signal into a 5 V-powered string is **out of specification**. It often works on the bench and fails in the field over temperature and batch spread. **Do not ship it.**

Use **SN74AHCT1G125DBVR** — a single buffer at 5 V with TTL input thresholds, so a 3.3 V input is unambiguously high and the output swings to 5 V. **It must be an HCT or AHCT part**; an AHC or HC part has the same threshold problem you are trying to solve.

**Current, which dominates this board:**

| Condition | At 5 V | Power |
|---|---|---|
| One LED, full white | 36.7 mA | 0.18 W |
| **Ninety, full white** | **3.30 A** | **16.5 W** |
| Ninety, off | 59 mA | 0.29 W |
| Ninety, white at 25 % | 0.87 A | 4.4 W |

**16.5 W of LEDs is several times the motor.** Two consequences. The supply must be sized for it — which is why the product moved to mains power. And a **global brightness cap must be stated as a design parameter, not discovered**: cap at 40 % white and it is 1.3 A. Full-white test patterns must still be *possible* without browning out, so either size for 3.3 A or compute a per-frame current estimate in firmware and limit — standard practice is to sum the byte values and scale.

**At the string:**

- **470 Ω in series with the data input, physically on the flexible ring at the first LED**, not on this board. Both the datasheet and Adafruit are explicit that the resistor belongs at the LED end.
- **100 nF per LED** — what SmartKnob does on all of its.
- **1000 µF at each power injection point.**

**Feed the ring at three points, 120° apart.** Fed from one point the entire 3.3 A flows through the first millimetre of trace and the far side sees roughly 0.33 V of drop on 1 oz copper. Three feeds cut the worst case by about nine times. Use 2 oz copper on the flex if the fabricator offers it.

**Keep the data as one continuous chain** — each LED regenerates the signal. Or split it into three chains of thirty, which costs nothing here (twelve state machines are available), triples the refresh headroom, and means one dead LED kills a third of the ring rather than all of it. **The flex layout decides.**

---

## 7. Servo, vibration actuator, and the energy buffer

### 7.1 Clutch servo — AGFRC C1.5CLS PRO

| Published | Value |
|---|---|
| Voltage | 3.7-6 V |
| Stroke | 9 mm |
| Force | 120 gf at 3.7 V, 170 at 4.2 V, **240 at 6.0 V** |
| Speed | 0.108 s per 9 mm at 6 V |
| Weight | 1.5 g |
| Connector | JST 1.25 mm or a servo plug |

**Not published: current draw of any kind, pulse-width range, frame rate, dead band, or a mechanical drawing.** The convention is a 1.0-2.0 ms pulse at 50 Hz, but that is a convention and not a specification for this part. **Buy two and test with a servo tester before layout.**

**Give it its own supply rail, always.** A coreless micro-servo's stall current is many times its running current and its noise is broadband. A separate regulator from 5 V with its own 100 µF and 100 nF, star-grounded back at the supply inlet.

**A design note worth acting on:** this is a proportional clutch. If the servo holds a mid-stroke position continuously it draws current continuously and will hunt audibly. **Consider whether the mechanism can be made over-centre or detented so the servo is unpowered in both end states** — then its supply can be cut between transitions with a load switch, killing both the noise and the current.

### 7.2 Vibration actuator — DRV2605L and VLV101040A

**I²C address 0x5A, fixed.** No conflict with anything else on the board. No external clock or resistor. Startup 0.7 ms.

Connections: 1 µF on the supply and 1 µF on the internal regulator pin, both close; the trigger pin to ground for I²C-triggered operation; **the enable pin to a microcontroller pin — do not tie it high**, because holding it low removes the driver from the noise floor entirely when nothing is playing, which matters with an audio board next door. The two outputs as a **tight differential pair**, away from the encoder and away from the audio board.

**⚠ Two mechanical requirements that are easy to miss.** The actuator is **wideband** (170 Hz resonance, usable 140-300 Hz), and a shallow broad resonance can make closed-loop resonance tracking hunt — **plan to test both open-loop and automatic modes**. And Vybronics warn that *"if soldering thin wires… adhesion may separate"*: **do not solder wires to this part. Use spring contacts or pogo pins.** That is an enclosure requirement, not a board one.

### 7.3 The energy buffer — replace the part, and question whether it is needed

**Sizing.** To hold the 5 V rail within 200 mV while supplying 2 A for 10 ms needs **C = 2 × 0.010 / 0.2 = 0.1 F**. So the instinct is right — a 1000 µF electrolytic would sag badly. You need farads that can deliver amps, which is exactly what the chosen part cannot do.

**Replacement: two Eaton HB-series 2.5 V cells in series.**

| Part | Capacitance | Resistance | Continuous current | Size |
|---|---|---|---|---|
| **HB1030-2R5106-R** | **10 F** | **60 mΩ** | **2.5 A** | Ø10 x 31.5 mm |
| HB1020-2R5505-R | 5 F | 100 mΩ | 1.4 A | Ø10 x 22.3 mm |

Two of the first in series gives **5 F at 5.0 V, 120 mΩ, 2.5 A** — fifty times the capacitance needed and only 240 mV of drop at 2 A. **The height is the trade**: 31.5 mm may dominate this board's envelope in a flat object, and the shorter part is still ample.

**Series arrangement** (standard practice; neither datasheet publishes guidance): a **2.4 kΩ 1 % balancing resistor across each cell** — bleed current at least fifty times the leakage — costing 2 mA continuous, negligible on a mains-powered device.

**Inrush limiting is essential.** An empty bank looks like a short circuit and will trip the supply's fold-back. Use a **current-limited load switch with a programmable limit set at 0.5-1 A**; the bank then charges in about 50 ms and nothing notices. A thermistor is cheaper but stays lossy and does not reset quickly.

**No charger is needed** — with 5 V-rated cells across a 5 V rail the bank simply sits behind the limiter. That is much simpler than the lithium-hybrid case, which would have needed voltage-limited charging. One more reason to switch.

**At power-off the bank holds 62.5 J and keeps the rail up well after the mains is removed.** Two consequences worth designing in: **the microcontroller must sense the loss of input power upstream of the limiter and shut down deliberately** — park the clutch, fade the halo, tell the computer. That is what makes the object feel considered rather than just cutting out. And **warn the assembler and the service technician that this board stays live after unplugging.**

**⚠ But question whether the bank is needed at all.** With an adequate mains supply, the motor's 2 A transient may simply not matter. **Instrument the 5 V rail on the bench with the motor rendering detents at full effort and look at the droop. If it is under 100 mV, delete the bank, the balancing resistors and the load switch, and save two cylinders of height.** One measurement closes it.

---

## 8. USB — keyboard and mouse

**This is a solved problem with public examples.** The chip has a full-speed device controller with an integrated physical layer, and TinyUSB's composite example — which enumerates keyboard, mouse, consumer control, and more — builds for it out of the box. You delete descriptors; you do not add any.

**Keep consumer control.** Volume up, down and mute as consumer-control usages is the correct driver-free way for a volume knob to talk to Windows and macOS, better than synthesising keystrokes. And the mouse report carries a signed **wheel** byte plus a horizontal pan byte, which is the scroll path.

**Latency.** A full-speed interrupt endpoint has a **1 ms floor** and that is what to request. There is no way below it without high-speed USB, which this chip does not do — and 1 ms is well under the perceptual threshold. **The interesting engineering is not the bus rate but making sure the encoder-to-report path never queues: compute the delta and post the report from the timer side, not from a task that can be delayed.**

**Use two separate interfaces**, one keyboard and one mouse, rather than one interface with report identifiers. It costs one more endpoint and a few descriptor lines, and it gives the mouse its own 1 ms slot so keyboard traffic can never delay a scroll report.

**Electrically:** **27 Ω series resistors on both data lines** close to the chip, **90 Ω differential**, solid ground directly underneath. Pull-ups are built in. Add **USBLC6-2SC6** protection **between the connector and the series resistors**. Route VBUS through a divider to a pin so firmware knows a host is attached. Expose the boot-select and reset points as **test pads rather than buttons** so a sealed unit can be recovered.

Also from Raspberry Pi's hardware design guide: a 12 MHz crystal with a **1 kΩ series resistor** on the drive side and 15 pF loading; a **3.3 µH inductor** for the core regulator with 4.7 µF either side; **33 Ω and 4.7 µF filtering the analogue supply** even if the converter is unused; and 100 nF per power pin.

---

## 9. Prior art — what can and cannot be copied

**scottbez1/smartknob** is the closest thing that exists, and its electronics are **Apache 2.0** — permissive, attribution the only obligation.

| Element | SmartKnob | This board |
|---|---|---|
| Driver | **TMC6300-LA** — *"a perfect match"* | **Same part** |
| Sensor | **MT6701**, for *"CRC to validate data"* and *"lower noise versus alternatives"* | **Same part** |
| Motor | 32 mm hollow-shaft gimbal | Very close relative |
| LEDs | **8 x SK6812SIDE-A**, 0.1 µF each | **Same part**, ninety of them |
| USB | Serial bridge, **not native keyboard/mouse** | Native |

**Copy:** the whole driver-plus-sensor-plus-gimbal topology, the driver's application circuit as built (its schematic shows **no sense resistors fitted**, confirming that voltage-mode control is what it actually does), the serial sensor wiring, the per-LED capacitor, and the firmware architecture on top of SimpleFOC.

**Cannot copy:** everything specific to its processor; anything about a clutch, which it does not have; the LED ring, because eight is not ninety; and — importantly — **the knob encoder**. SmartKnob reads the *motor's* sensor and treats it as the knob angle, because its motor is rigidly coupled to the knob. **Ours has a friction band and a clutch, so the motor angle and the knob angle can diverge.** That is why this design has a separate optical encoder and SmartKnob does not, and **nothing in the prior art addresses it. It is the genuinely novel control problem in this product.**

**Also useful:** SimpleFOC's `Arduino-FOC` and `Arduino-FOC-drivers` (both MIT), which contain the sensor driver and need no driver-specific code for the motor driver; a public thread confirming **this exact driver working with this microcontroller family**; and the Twisted Fields motor controller, which is the closest published board — read it, but it carries a "work in progress, do not use" warning.

**Buy a SmartKnob development kit from SeedLabs.** It is the fastest route to a hand-feel benchmark without building anything, and it shows what someone else's execution of this idea feels like.

---

## 10. Board practicalities

**Four layers, non-negotiable.** The driver's datasheet requires it with thermal vias; the USB pair needs a solid plane; and a motor bridge is switching within a few centimetres of an optical encoder and a haptic amplifier. Stack: signal, ground, power, signal, with the motor phases and the driver on the top layer directly over the ground plane.

**Size: 50 x 45 mm to 60 x 50 mm.** Give the contractor a 60 x 50 mm budget and an instruction to come in under it. The energy-buffer cells, if retained, may dominate the envelope on height alone.

**Noise, in priority order:**

1. **Physically partition.** Motor zone in one corner, sensor and haptic zone in the opposite corner, digital and USB between. Do not interleave.
2. **Keep the phase current loop tiny** — bulk capacitor, driver, motor connector, back to the capacitor's ground. That loop is the antenna. The 10 µF must be within a few millimetres of the supply pin.
3. **One unbroken ground plane.** Do **not** split it into analogue and digital islands — that is the classic mistake and it forces return currents to detour. Control where currents flow by controlling where components sit.
4. **Star the power entry** — separate feeds to the motor, the LED ring, the servo, and the logic regulator. The ring at 3.3 A and the servo at stall are as dirty as the motor.
5. **Route the encoder pair away from the motor zone**, with ground either side.
6. **The motor sensor's cable is the most exposed signal in the system** — a short serial link running past a switching bridge. Keep it short, twisted or shielded, run the clock at 2-5 MHz rather than 15, **and rely on the error check**: read, verify, and on failure reuse the previous sample rather than acting on garbage.
7. **Give the audio board its own feed from the supply**, never a daisy-chain from here, and fit a filter on this board's own inlet so its switching does not propagate back up the shared rail.

**Connectors — one rule above all: no friction-fit.** JST SH at 1.0 mm **has no latch** and is unsuitable for something that gets picked up. It is the connector everyone reaches for because it is small.

| Link | Recommended | Ways |
|---|---|---|
| Motor phases | **JST PH 2.0 mm** (2 A, latched) — or match whatever the motor ships with, **which is not published; measure a real one** | 3 |
| Motor sensor | JST GH 1.25 mm | 5 |
| Knob encoder | JST GH — and put the 220 Ω resistor **on the encoder's own board**, so the cable carries no high-current node | 5 |
| Clutch servo | JST GH, or the mating part the servo comes with. **Confirm on a real servo** | 3 |
| Vibration actuator | **Spring contacts or pogo pins. Do not solder** | 2 |
| LED ring power | JST PH per feed, three feeds at 1.1 A each | 2 x 3 |
| LED ring data | JST GH, co-located with a power feed | 2 |
| Serial to the computer | JST GH | 4 |
| 5 V in | Molex Micro-Fit 3.0 or JST VH, sized for 5 A | 2-3 |
| Debug | Tag-Connect pads, no connector fitted | 6 |

**At sixty units, buy pre-crimped leads or have the harness made.** Hand-crimping 1.25 mm contacts is where solo builds go wrong — a marginal crimp on the motor sensor's line produces an intermittent haptic fault that takes a week to find.

---

## 11. Settled, and still open

**Settled:** RP2350B; the motor driver with six pulse-width lines and its supply pin as the enable; four layers with thermal vias; the decoupling set; both sense footpoints to ground for the first board; the motor sensor in serial mode; the encoder's 220 Ω resistor and 1.0-2.5 mm gap; both the encoder outputs and the LED data must be level-shifted, and with different part families; the LED string's series resistor at the ring, per-LED capacitor, bulk at three injection points; the haptic driver at 0x5A with its enable on a pin; the actuator must be spring-contacted; USB series resistors, protection and a 1 ms interval; **the supercapacitors must be replaced**; latched connectors only; an external pull on every input pin for the erratum.

**Still open:**

1. **75 or 212 lines per inch on the encoder?** The better part gives 2.8 times the resolution *and* removes the level-shifting problem. **Close this before the bill of materials is locked** — check its datasheet, stock and price at 70 pieces.
2. **Current sensing at all?** Bench-test voltage mode first. If detent quality is limited by torque accuracy rather than band compliance, add the in-line amplifiers — and revisit the microcontroller.
3. **Motor rail at 5 V or boosted to 8-10 V?** Bench-measure detent sharpness at both.
4. **Energy buffer at all?** One measurement of rail droop closes it.
5. **One ninety-LED chain or three of thirty?** The flex layout decides; three costs nothing here.
6. **The global brightness cap** — an artistic decision with an electrical consequence. State the number.
7. **Which shaft end carries the sensor magnet.** Buy three motors and measure.
8. **Servo pulse range, frame rate, and whether 3.3 V drives it.** Buy two and test.
9. **Code strip supplier, thickness, substrate.** Quote the four named suppliers.
10. **Which board owns the external USB socket** and its attach resistors — architecture, not layout. Currently the carrier.
11. **The shield grounding scheme**, settled jointly with the audio board.
12. **Whether the stock quadrature example now works on this chip.** Prove on day one.

## Sources

[RP2350 datasheet](https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008373-DS-2-rp2350-datasheet.pdf) · [Hardware design with RP2350](https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008280-DS-2-hardware-design-with-rp2350.pdf) · [Erratum E9 explained](https://hackaday.com/2024/09/20/raspberry-pi-rp2350-e9-erratum-redefined-as-input-mode-leakage-current/) · [TMC6300 datasheet v1.04](https://www.mouser.com/datasheet/2/256/TMC6300_Datasheet_V104-2066968.pdf) · [TMC6300-BOB datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/tmc6300-bob_datasheet_rev1.00.pdf) · [MT6701 datasheet Rev 1.8](https://www.magntek.com.cn/upload/pdf/202407/MT6701_Rev.1.8.pdf) · [AEDR-8300 series datasheet](https://www.farnell.com/datasheets/20531.pdf) · [AEDR-8300-1Wx datasheet](https://www.mouser.com/datasheet/2/678/AVGOS05599_1-2574607.pdf) · [SK6812 SIDE-A datasheet](https://www.normandled.com/upload/201810/SK6812%20SIDE-A%20LED%20Datasheet.pdf) · [Adafruit NeoPixel best practices](https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices) · [DRV2605L datasheet](https://www.ti.com/lit/ds/symlink/drv2605l.pdf) · [Vybronics VLV101040A](https://www.vybronics.com/linear-lra-vibration-motors/v-lv101040a) · [AGFRC C1.5CLS PRO](https://www.agfrc.com/index.php?id=2438) · [Abracon AHCR-S04R0S datasheet](https://abracon.com/datasheets/AHCR-S04R0S.pdf) · [Eaton HB supercapacitor datasheet](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-hb-supercapacitor-data-sheet.pdf) · [TI INA240 datasheet](https://www.ti.com/lit/ds/symlink/ina240.pdf) · [SimpleFOC current sensing](https://docs.simplefoc.com/current_sense) · [SimpleFOC and the TMC6300](https://community.simplefoc.com/t/current-sensing-with-tmc6300/2062) · [scottbez1/smartknob](https://github.com/scottbez1/smartknob) · [Arduino-FOC-drivers MT6701 driver](https://github.com/simplefoc/Arduino-FOC-drivers/blob/master/src/encoders/mt6701/README.md) · [TinyUSB composite HID example](https://docs.tinyusb.org/en/latest/examples/device/hid_composite.html) · [USBLC6-2](https://www.st.com/en/protections-and-emi-filters/usblc6-2.html)
