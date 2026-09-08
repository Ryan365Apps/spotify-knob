# the 60 — where each function should live

**Date: 7 September 2026.** An answer to the question "do I actually need the custom motion board?" Written against `the60-board-motion.md`, which this document challenges. Everything here is sourced. Anything a vendor does not publish is marked **not published**; anything I concluded rather than read is marked **judgement**.

---

## 1. The recommendation

**You do not need a custom circuit board to build one working prototype, and you should not commission one yet.** Buy an **ESP32-S3-DevKitC-1** (£28.90, in stock, The Pi Hut) and a **TMC6300-BOB** motor-driver breakout (£19.96 excluding VAT, four in stock, Farnell UK) and wire them together with jumper wires. That pair runs the motor, its rotor sensor, the knob's own encoder, and the vibration actuator — the four functions that genuinely have to be deterministic. Move the ninety LEDs and the clutch servo onto the Raspberry Pi 5, where both are handled by real hardware peripherals rather than by software timing. Keep the keyboard-and-mouse job on the microcontroller: the Pi 5 **can** be a USB keyboard and mouse, I have verified that, but doing it there would put the Linux scheduler inside the one path in the whole product that the hand feels most directly, and the microcontroller's USB stack is a stock example project that costs you nothing. Add about £75 of small breakouts — a level shifter, a haptic driver, a magnetic sensor, a linear servo, and a £3 USB-C splitter that solves a power problem you have not hit yet — and the whole bench setup is **about £150 including VAT, all of it orderable this week from UK suppliers**. Nothing needs to be built. The one thing on your list that nothing off the shelf closes is the reflective code ring for the knob's optical encoder, and that is a lead-time problem, not a circuit-board problem — see §6.

Two consequences worth stating in the same breath. First, **moving the ninety LEDs to the Pi removes the strongest argument in the current motion-board brief for choosing the RP2350** — that document ranks "the ninety-LED string is the hard scheduling problem, not the motor loop" as reason number one for that chip. If the LEDs go to the Pi, that reason evaporates and the choice reopens. Second, if you do eventually build a board for a run of sixty to seventy, **what is left of it is roughly a third of what is drawn now**: a microcontroller, a TMC6300, two level shifters and connectors. No LED driver, no servo drive, no USB device stack of its own if you choose otherwise. That is a much cheaper board to have designed, and a much less risky one.

---

## 2. Glossary, so nothing below is unexplained

| Term | Plain English |
|---|---|
| **FOC** — field-oriented control | The maths that turns "I want this much twisting force at this rotor angle" into the three voltages a brushless motor's coils need. Must run thousands of times a second, on time. |
| **PIO** — programmable input/output | A small block of hardware inside a chip that can be programmed to bit-bang a signal on a pin with exact timing, independently of the main processor. |
| **DMA** — direct memory access | Hardware that moves a block of data from memory to a peripheral without the processor touching it. Once started, it cannot be interrupted by software. |
| **PWM** — pulse-width modulation | A square wave whose on-time carries the message. Hobby servos and motor bridges are both driven this way. |
| **USB gadget mode** | A computer pretending to be a USB accessory (keyboard, network card) rather than being the computer the accessory plugs into. |
| **HID** — human interface device | The USB class every keyboard and mouse uses. Windows and macOS have the driver built in; nothing is installed. |
| **Quadrature** | Two square waves 90° out of step. Counting their edges gives position and direction. |
| **RP1** | The separate chip on a Raspberry Pi 5 that provides all the general-purpose pins, USB ports and low-speed peripherals. It sits at the far end of an internal PCI Express link from the main processor. |
| **cyclictest** | The standard Linux benchmark for "how late can a task be?" |
| **PCNT** | The ESP32's hardware pulse counter, which can decode quadrature in silicon. |

---

## 3. The allocation

**Recommended allocation.** No row needs a custom board.

| | Function | Lives on | Note |
|---|---|---|---|
| **A** | 60 detents, end stops, self-rotation (FOC at a few kHz) | **ESP32-S3-DevKitC-1 + TMC6300-BOB** | The only genuinely hard-real-time job. SimpleFOC supports the ESP32-S3 with all PWM modes ([docs.simplefoc.com/microcontrollers](https://docs.simplefoc.com/microcontrollers)). SmartKnob's own firmware is Apache 2.0 and its motor task lifts almost directly. |
| **B** | Motor rotor angle (MT6701, serial) | **Same microcontroller, hardware SPI** | Inseparable from A, as you said. SimpleFOC has an MT6701 SSI driver in `Arduino-FOC-drivers`. |
| **C** | Knob angle (AEDR-8300 quadrature, ~5,000–15,000 counts/rev) | **Same microcontroller, PCNT hardware counter** | The ESP32-S3 has a hardware pulse counter that "can act as a quadrature decoder", with an official rotary-encoder example ([ESP-IDF PCNT docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/pcnt.html)). This costs **two pins and no processor time**. It has to be here, not on the Pi — see §5. |
| **D** | Clutch servo (1–2 ms pulse, 50 Hz) | **Raspberry Pi 5, hardware PWM** | RP1 contains a genuine hardware PWM peripheral: "Four independent output channels with separate duty-cycle and range registers", "Optional duty-cycle data FIFO with DMA support" ([RP1 peripherals datasheet](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf), §3.4). Exposed via `dtoverlay=pwm-2chan` on GPIO 12/13/18/19 ([overlay README](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README)). Once configured it free-runs — Linux jitter cannot reach it. Free. |
| **E** | Vibration actuator (DRV2605L over I²C) | **Microcontroller** | Not because it is hard, but because **its trigger is computed on the microcontroller** and the two processors are milliseconds apart. See §5 for the number that decides this. Two pins. |
| **F** | Up to 90 addressable LEDs | **Raspberry Pi 5** | Three separate DMA-backed mechanisms exist and are documented (§4.3). The frame content is generated by the interface, which lives on the Pi, so this also deletes a data path. Needs the 74AHCT125 level shifter and its own 5 V feed either way. |
| **G** | Scroll, volume and key events to the host, no driver | **Microcontroller, native USB HID** | The Pi **can** do this — verified, §4.4 — but should not, §5. The ESP32-S3 has native USB and composite HID is a stock example. |
| — | Serial link between the two | **Two wires, UART** | It does not disappear. It carries "use this detent profile", "engage the clutch", "the halo should pulse". None of that is time-critical. It is two wires, not a reason to build anything. |

**Still needs a custom board: nothing, for one prototype.**

---

## 4. The specific things you asked me to check

### 4.1 The Raspberry Pi 5, against D, E, F and G — and why not A

**Why it cannot do A, concretely.** Three independent reasons, each sufficient on its own.

1. **Scheduling.** The best published measurement I could find for a Pi 5 is an academic paper that ran cyclictest for an hour under heavy load on a Pi 5 Model B ([OSPERT 2024, De Wit et al.](https://antonio.paolillo.be/publications/workshops/ecrtsOspert2024_dewit_rtlinux_paper.pdf)): **stock kernel worst case 36,802 µs; hand-patched PREEMPT_RT worst case 124 µs**, average 5.91 µs. A 5 kHz control loop has a 200 µs budget. Even the real-time-patched best case eats most of one period, and the stock kernel is off by two orders of magnitude. The paper's own authors note "it was never the ambition of the real-time Linux community to make the Linux kernel completely hard real-time."
2. **Every pin access crosses a PCI Express link.** RP1 is a separate chip. A September 2026 measurement of GPIO edge-to-timestamp latency on a Pi 5 found **~11–12 µs by default, improving to ~5.2–7.3 µs** only after disabling RP1's PCIe low-power state and pinning the CPU frequency ([satpulse.net](https://satpulse.net/2026/09/06/measuring-systematic-pps-bias-on-the-raspberry-pi-5.html)). The FOC loop must read the MT6701 over SPI *every iteration*; that read alone carries this cost and this jitter.
3. **The PIO cannot be used as a fast co-processor.** Raspberry Pi's own announcement is explicit: "Most PIOLib operations take at least 10 microseconds", and it is unsuitable for "anything that requires close coupling between the state machine and driver software" ([piolib announcement](https://www.raspberrypi.com/news/piolib-a-userspace-library-for-pio-control/)). Register access is proxied through RP1 firmware over the PCIe link — the merged kernel pull request says so in as many words: "Aside from the data FIFOs, the registers are inaccessible over PCIe, so all interactions must be proxied via the RP1 firmware" ([raspberrypi/linux #6470](https://github.com/raspberrypi/linux/pull/6470)).

This is not a "Linux is slow" argument. It is that the parts of the Pi 5 that could be fast are behind a link that is not.

**D — the servo: yes, properly.** Hardware peripheral, quoted above. Not software PWM, not PIO, not shared with anything. A community write-up of the RP1 hardware PWM path reports "much better stability and jitter than any userspace software approaches" ([gist](https://gist.github.com/Gadgetoid/b92ad3db06ff8c264eef2abf0e09d569)). One practical wrinkle: a GitHub issue reports `dtoverlay=pwm-2chan` loading nothing on a stock Pi 5 without getting the pin and function parameters right ([Pioreactor issue #10](https://github.com/Pioreactor/rpi_hardware_pwm/issues/10)) — a configuration hour, not a capability problem.

**E — the haptic driver over I²C: technically yes, but see §5.** RP1 has seven I²C instances; four are exposed on the Pi 5 header via `i2c0-pi5` … `i2c3-pi5` overlays. No Pi-5-specific I²C defects found. The old Broadcom clock-stretching bug is pre-RP1 and does not apply.

**F — the LEDs: yes, by one of three DMA-backed routes.** This one needs care, because the obvious answer is wrong.

- **The library everyone uses on a Pi 4 does not work on a Pi 5 unmodified.** `rpi_ws281x`'s own wiki: "Due to significant changes in the Raspberry Pi hardware, namely the RP1 chipset, a kernel module is now required" ([wiki](https://github.com/jgarff/rpi_ws281x/wiki/Raspberry-Pi-5-Support)). The replacement is an out-of-tree kernel module on a `pi5` branch that drives the string from RP1's PWM duty-cycle FIFO. **Single channel only** — "Concurrent channel support will be added soon."
- **PIO, officially supported.** `piolib` ships `piows2812` ("WS2812 LED example with dynamic state machine allocation") and `piotest` ("WS2812 LED control using DMA"), both defaulting to GPIO 2, requiring `/dev/pio0` ([piolib README](https://github.com/raspberrypi/utils/tree/master/piolib)). Adafruit built a PIO-based NeoPixel path for the Pi 5 too, with an honest caveat of their own: it "is new and it will require a firmware upgrade, which is generally not recommended under normal circumstances as it hasn't been as thoroughly tested" ([Adafruit guide](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/using-neopixels-on-the-pi-5)).
- **Hardware SPI, no kernel module and no PIO at all.** [Pi5Neo](https://github.com/vanshksingh/Pi5Neo) bit-bangs the 800 kHz waveform out of the hardware SPI port with DMA, claims flicker-free operation, and states the default kernel SPI buffer supports about 170 LEDs — comfortably above ninety. **This is the one I would try first**, because it depends on nothing experimental and leaves the PIO block untouched.

The mechanism is sound in all three cases: once the frame is queued, the 2.70 ms burst comes out of hardware, and the processor being busy cannot stretch it. **What I could not find is a field report of anyone running ninety LEDs on a Pi 5 under load and reporting no flicker.** That is the gap. It is an evening on the bench to close, and it is the first thing I would test.

One warning that matters if you run PIO and something else at once: the piolib README states "blocking operations block the whole RP1 firmware interface until they complete." **RP1 contains one PIO block with four state machines** — half what an RP2040 has (confirmed by RP1's designer, quoted in [PiCockpit](https://picockpit.com/raspberry-pi/i-read-the-rp1-documentation-so-you-dont-have-to/) and on [element14](https://community.element14.com/products/raspberry-pi/f/forum/53762/the-raspberry-pi-5-has-a-new-chip---the-rp1-has-a-secret); the RP1 datasheet has no PIO chapter at all and mentions it only in the address map and the pin-function table, so the block is **officially undocumented**). Using SPI for the LEDs sidesteps this entirely.

**G — keyboard and mouse: yes, verified, with two conditions.**

- Raspberry Pi's own announcement of 21 January 2026 lists the supported models and ports: for "Raspberry Pi 5, 500, and 500+" it is "the USB-C port directly on the board"; Compute Module 5 uses "the USB-C port on the Raspberry Pi CM5 IO Board" ([raspberrypi.com news](https://www.raspberrypi.com/news/usb-gadget-mode-in-raspberry-pi-os-ssh-over-usb/)). So the port is genuinely a device port, not power-only.
- **But the shipped package is a network adapter and nothing else.** The same article: the `rpi-usb-gadget` package "configures the `g_ether` USB gadget kernel module", and "CDC-ACM (serial over USB) is not included." There is no HID function in it. Keyboard and mouse means configuring the generic Linux gadget framework by hand — which is well documented in the kernel's own reference ("You can add as many HID functions as you want, only limited by the amount of interrupt endpoints your gadget driver supports", [kernel.org gadget_hid](https://docs.kernel.org/usb/gadget_hid.html)) and has many worked examples, **all of which are written for a Pi Zero**. I found no published example of a composite keyboard-plus-mouse HID gadget running on a Pi 5 specifically. Nothing suggests it fails; nobody has written it down.
- **The condition you have not hit yet: on a Pi 5 the gadget port is also the power inlet.** Raspberry Pi's article says "Once gadget mode is enabled, the selected port will function exclusively as USB networking + power input", and advises connecting directly to a PC port because "some laptop USB ports cannot provide sufficient power". The Pi 5's own documentation asks for a **5 V 5 A supply**, with typical bare-board draw of 800 mA ([power-supplies documentation](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/power-supplies.adoc)). A PC USB port will not do that, and a downstream port on your internal hub certainly will not. Powering through the 40-pin header instead is **not documented by Raspberry Pi as an input path for the Pi 5**, and third-party guidance says it bypasses the board's over-voltage protection and risks back-feeding if USB-C power is also present.
- **The fix costs £3.** A USB-C splitter that separates power-delivery negotiation (the CC pins) from the data pair, so the Pi takes 25 W from your mains supply while its data lines go to the host: [8086 Consultancy USB-C Data/Power Splitter, £3.00, in stock at The Pi Hut](https://thepihut.com/products/usb-c-data-power-splitter). A Raspberry Pi engineer arrived at the same approach on the forums. **This is a genuine finding for the product regardless of what you decide about function G**, because the Pi almost certainly wants a data link to a companion application on the host, and that link is exactly what `rpi-usb-gadget` provides out of the box.

**One thing the Pi 5 has not got, for completeness:** no analogue input on the header. RP1 contains a five-input converter but the datasheet has no chapter for it and no pin carries an ADC function. Irrelevant to A–G as specified; relevant the day you want to read a thermistor.

### 4.2 SmartKnob

**Your four beliefs are all correct**, confirmed from the repository.

| What you believed | Confirmed |
|---|---|
| Eight LEDs, not ninety | Yes — 8 × SK6812-SIDE-A, `-DNUM_LEDS=8` in [platformio.ini](https://github.com/scottbez1/smartknob/blob/master/platformio.ini) |
| No clutch servo | Yes — no servo anywhere in the design |
| No separate optical encoder | Yes — it reads the MT6701 and calls that the knob angle |
| A serial device, not a keyboard and mouse | Yes — "USB-C (2.0) connector for 5V power and serial data/programming (CH340)". The host protocol is COBS-framed, CRC32-checked protobuf over a 921600-baud serial link |

Add a fifth: the author's own status line is **"Not recommended for general use, but may be a fun project for an advanced electronics hobbyist"**, and building one "requires advanced soldering experience... very small-pitch surface-mount soldering". He also states plainly he does not sell them. Licence is **Apache 2.0** for software and electronics, **CC-BY 4.0** for the mechanical design.

The useful part is the pin map, which is published as build flags in `platformio.ini` rather than a header: motor 6 pins, MT6701 serial 3 pins (`PIN_MT_DATA=37, PIN_MT_CLOCK=13, PIN_MT_CSN=14`), LED data 1, display SPI 5, strain gauge 2, ambient light I²C 2 — **20 pins consumed, and no spare-GPIO connector on the original board.**

**What you can actually buy:**

| | Price | Stock | What it is |
|---|---|---|---|
| [SeedLabs SmartKnob DevKit v0.1](https://store.seedlabs.it/products/smartknob-devkit-v0-1) | **£329.00** | "31 in stock" | A **different board from the original**: ESP32-S3-WROOM-1U-N16R8, **72 LEDs** not 8, adds an HX711 load cell amplifier and a VL53L0X proximity sensor. Crucially it **does** break out spare pins: "7 additional GPIOs on the back side" plus three Stemma QT I²C connectors. Assembled, in an enclosure, with motor. |
| [Makerfabs MaTouch SmartKnob Assembled](https://www.makerfabs.com/matouch-smartknob-assembled.html) | **$69.00** | "In stock" | ESP32-S3, round touchscreen, MT6701, gimbal motor, battery. Makerfabs disclaim it is "not a commercial product". A [CNX Software review](https://www.cnx-software.com/2025/02/12/matouch-smartknob-assembled-esp32-based-rotary-knob-touchscreen-display/) notes it adds Bluetooth HID — Bluetooth, not USB. |

Two cautions on the SeedLabs kit. **Its store publishes no shipping policy and no delivery estimate** — the shipping-policy page is an unfilled template, the checkout uses Shopify's deferred-purchase wording, and their own firmware repository says "our goal is not to manufacture this kit at scale, nor to maintain a constant backstock of it. As such, it might take longer to receive it from us." Treat "31 in stock" as a queue position, not a dispatch. And **their licence is not Apache 2.0**: the SeedLabs layer adds a custom licence, free for personal and educational use, with **commercial use requiring a partnership agreement with royalties** ([SeedLabs firmware README](https://github.com/SeedLabs-it/smartknob-firmware)). For a sixty-unit product that is a conversation, not a download.

**Judgement: buy the Makerfabs unit at $69 as a hand-feel benchmark if you want one this month, not the £329 kit.** It is a tenth the price, in stock, and you are buying it to feel what someone else's execution of virtual detents feels like — not to build on. Neither is a platform for the 60, because neither has a clutch, a separate knob encoder, or ninety LEDs in the right place.

**One sourcing note that will bite eventually:** the motor. The project's own wiki spent a year on this. It is now resolved to [SparkFun ROB-20441 at $45.95](https://www.sparkfun.com/products/20441), with the README warning "they've been selling out quickly each time they restock" and that nearly all cheap gimbal motors have "moderate to severe cogging", which fights virtual detents directly.

### 4.3 A bought microcontroller plus a bought motor driver

| Board | UK price | Stock | Size | Verdict |
|---|---|---|---|---|
| **[ESP32-S3-DevKitC-1](https://thepihut.com/products/esp32-s3-devkitc-1-development-board)** | **£28.90** | In stock, Pi Hut | **70 × 28 mm** | **Recommended.** Hardware quadrature counter, native USB, mature SimpleFOC support, and SmartKnob's firmware lineage is ESP32. |
| **[Raspberry Pi Pico 2](https://shop.pimoroni.com/en-us/products/raspberry-pi-pico-2)** | **£3.60** | In stock, Pimoroni | **51 × 21 × 1 mm** | **Buy one anyway at this price.** RP2350 support landed in Arduino-FOC v2.3.5 (July). But `Arduino-FOC-drivers` has **no RP2040 or RP2350 encoder driver of any kind**, so the knob's quadrature means hand-integrating a third-party PIO library. More risk this week; probably the right production core. |
| [Teensy 4.1](https://thepihut.com/products/teensy-4-1) | £30.30 | In stock, Pi Hut | ~61 × 18 mm | SimpleFOC's best-tested board. No native USB-HID advantage over the others, larger. |
| [Nucleo-G431RB](https://uk.farnell.com/stmicroelectronics/nucleo-g431rb/dev-board-32bit-arm-cortex-m4f/dp/3132423) | £14.38 ex VAT | **Farnell quotes delivery from 10 July 2027** | not published | Best silicon for FOC per SimpleFOC's own documentation. Not available this week. |

| Driver board | UK price | Stock | Size | Verdict |
|---|---|---|---|---|
| **[TMC6300-BOB](https://uk.farnell.com/trinamic/tmc6300-bob/breakout-dev-board-3-phase-bldc/dp/3416040)** | **£19.96 ex VAT** | **4 in stock, Farnell UK** | **~25.4 × 20.3 mm** | **Recommended.** The exact chip your design already specifies and the exact chip SmartKnob calls "a perfect match". Two 8-pin 0.1-inch headers: six PWM inputs, VCC_IO/standby, VBAT, three phases, diagnostic, ground. Buy two — four in stock is thin. |
| [SimpleFOC Mini v1.1](https://simplefoc.com/shop) | €12.00 | **Out of stock** | 26 × 21 mm | Official shop is out. Third-party AliExpress listings exist; shipping is 1–3 weeks. |
| [SimpleFOC Shield v3](https://simplefoc.com/shop) | €23.00 | **Out of stock** | not published | — |
| [ST B-G431B-ESC1](https://uk.farnell.com/stmicroelectronics/b-g431b-esc1/discovery-board-32bit-arm-cortex/dp/3247670) | £28.13 ex VAT | **1,720 in stock** | 30 × 41 mm | **Fails your pin test.** Per user manual UM2516 it breaks out **no SPI header**, and its J8 sensor connector is a single Hall-or-encoder input — one sensor, not two. It is a beautiful board for a motor with one sensor, which is exactly not your problem. |

### 4.4 Anything that does the motor and its sensor together on one bought board

**You are right that this is the hardest thing to buy, and the honest answer is that it does not exist in a form you can use.**

| | What it is | Why it fails |
|---|---|---|
| [Dagor Brushless Controller](https://docs.dagor.dev/) | ESP32 + 3-phase driver + **onboard 14-bit magnetic sensor**, 44 × 44 × 6 mm, 7 A continuous | Closest thing that exists. **Price not published, no buy link found, spare-pin availability not documented.** |
| [LILYGO T-Knob](https://lilygo.cc/products/t-knob) | ESP32-C6 + TMC6300 + MT6701 + gimbal motor, $37.28 | **Sold out** at source. UK stockist: none found. Also a finished knob with its own motor, not a board. |
| SeedLabs SmartKnob DevKit | See §4.2 | £329, a finished knob, licence restriction at volume |
| "AS5047 + DRV8313 board", generic AliExpress haptic-knob modules | — | Searched; **no such product found** |

So the microcontroller-plus-driver-breakout pair is not a compromise you are settling for. It is the state of the art of what is purchasable.

---

## 5. The three allocation decisions that are not obvious

These are the places where the answer is not "put it on the cheapest processor that can do it."

**Function C must be on the microcontroller, and this is the point you told me not to gloss over.** The Pi could decode the quadrature — `piolib` ships a `quadenc` example that does exactly this in a PIO state machine, independent of Linux scheduling. But decoding it is not the job. The job is that **the detent-rendering law needs the knob angle as an input, in the loop, every iteration**. SmartKnob does not face this because its motor and knob are one rigid body; yours are joined by a friction band and a clutch, so the number the control law needs is the optical encoder's, not the MT6701's. Reading it on the Pi and posting it over a serial link at gesture cadence puts a Linux scheduler between the sensor and the torque command. That is the same failure as putting the motor loop on the Pi, one hop removed. Two pins on the microcontroller close it for nothing.

If you want the Pi to have the knob angle *as well* — for the interface, or for the alternative in §7 — the AEDR-8300's outputs are **push-pull TTL, not open-collector**, so they will drive two inputs. **Fan the A and B signals out to both processors** through a dual buffer. The microcontroller counts them for the control law; the Pi counts them with `quadenc` for whatever it wants. Neither waits for the other. *(Judgement — I found no prior art doing this, but it is ordinary logic fan-out.)*

**Function E should be on the microcontroller, for a reason that is not "it needs bare metal."** The DRV2605L is two register writes over I²C; the Pi can do that in its sleep. The problem is *when*. The vibration accompanies a mechanical event — a detent edge, an end stop — that is computed on the microcontroller. Firing it from the Pi means the trigger crosses a serial link into a Linux userspace process, and the number from §4.1 applies: **stock-kernel worst-case scheduling latency of 36.8 ms under load.** Most events would be fine; occasionally the buzz would arrive a frame and a half after the click. That is precisely the class of artefact you said you will not accept, and it is the kind that is maddening to diagnose because it is intermittent. Keep the trigger and the actuator on the same processor.

**Function G is the one you suspected, and the answer is the opposite of what you expected.** You are right that the Pi can be the keyboard and mouse — verified in §4.4 above, with the £3 power caveat. But look at what moving it actually buys and costs:

- It does **not** delete the microcontroller. A and B keep it.
- It does **not** delete the serial link. The Pi still has to tell the microcontroller which detent profile to use and when to release the clutch.
- It **does** delete a USB stack from the microcontroller's firmware — but that stack is TinyUSB's composite HID example, which builds unmodified. It is not work.
- And it **inserts Linux into the scroll path.** The knob turn is counted on the microcontroller (function C, above). Under your proposal it would then travel: microcontroller → serial → Linux userspace → gadget driver → USB. Every one of those hops is subject to the 36.8 ms figure. Scroll stutter is the single most perceptible defect this product can have.

So: **the Pi's gadget port should carry the data link to your companion application on the host — which is what the shipped package does out of the box and costs you nothing — and the microcontroller should stay the keyboard and mouse.** You get both, over one cable, through your internal hub. The thing you wanted to delete turns out to be the cheap half.

---

## 6. What nothing covers, and the cheapest honest way to close it

**The reflective code ring for function C. This, not the circuit board, is your long pole.**

- The sensor is fine and in stock: **[AEDR-8300-1W2, £8.10 excluding VAT, 2,016 in stock at Farnell UK](https://uk.farnell.com/broadcom/aedr-8300-1w2/photointerrupter-reflective/dp/1735258)**. This also settles open question 1 in your motion-board brief: the -1W2 is the 212-lines-per-inch, 3.0–5.5 V part, so it gives about **15,200 counts per revolution on a 145 mm ring and removes the level-shifting problem entirely.** The 75-lines-per-inch -1K2 is confirmed "No Longer Stocked" at Farnell. **Buy the -1W2 now** — Farnell's page also warns of a **14-week manufacturer lead time** on reorders.
- **The code ring is not buyable in any form.** No off-the-shelf reflective code ring compatible with the AEDR-8300 exists anywhere I could find. Broadcom's own catalogue code wheels are motor-shaft sized (4–13 mm bore, 20–30 mm discs). Their one catalogue reflective code strip, the AR55-L20S, pairs with a different industrial encoder ASIC.
- **And nothing else measures a 150 mm ring either.** I checked every alternative you would think of. RLS/Renishaw magnetic ring encoders: largest **standard** ring is 100 mm, and their self-serve store [RLS Direct](https://direct.rls.si/) delivers to "EU, Norway, Switzerland, Canada and USA" — the UK is not listed. The ams off-axis parts are worse: the AS5304 evaluation board is marked obsolete at Mouser, the AS5311 adapter board is "Not For New Designs" and shows zero stock at DigiKey. Renishaw AksIM is quote-only. A mouse sensor reading the rim (PMW3360 breakouts are buyable, ~$30 on Tindie) is a real idea but **I found no one who has done it for a knob**, so it is a research project, not a solution.

**The cheapest honest way to close it, in order:**

1. **Get the code ring quoted this week** from the four suppliers already in your sourcing document — MELTEC, PWB Encoders, Laser Lab, Optry Tech. Send them the -1W2 requirements. This is the item with the longest clock and it is currently not started.
2. **Do not let it block the bench.** Prove the two-angle control law with **two magnetic sensors instead**: the MT6701 on the motor shaft and an [AS5600 breakout, £5.40, in stock at The Pi Hut](https://thepihut.com/products/adafruit-as5600-magnetic-angle-sensor) on a second shaft friction-coupled to the knob. That is not the product's sensor, but it produces the same situation — two angles that diverge across a compliant band and a clutch — which is the novel control problem you want to solve. £5.40 and an afternoon of bracketry.
3. Only then, when the real ring arrives, swap the AS5600 for the AEDR-8300 and re-tune.

Two smaller gaps. **The MT6701 has no reputable breakout** — it is not stocked by Mouser, DigiKey, Farnell or RS in any form, and the only modules are unbranded eBay and Amazon UK listings at £5–8. Buy two, expect one to be poor. **The linear servo:** the AGFRC C1.5CLS PRO ships from China. A UK-stocked spec-equivalent (1.5 g digital linear, hobby PWM) is on [eBay UK at £20.99 with three-day delivery](https://www.ebay.co.uk/itm/352981537170) — buy that to prove the pulse range and current draw, which AGFRC do not publish, while the real part is in transit.

---

## 7. Alternatives

### Alternative 1 — everything on the microcontroller, Pi renders only the screen

| Function | Lives on | Note |
|---|---|---|
| A, B, C, E, G | Microcontroller | as recommended |
| **D** | **Microcontroller** | one more pin |
| **F** | **Microcontroller** | 90 LEDs, needs a PIO-class chip → **forces the RP2350 or an ESP32 with RMT** |
| Serial link | Still needed, and now busier — the interface has to stream LED frames to it |

**Trade:** one processor owns everything physical, which is conceptually clean and is what your current brief describes. **Cost:** you are now streaming 270 bytes of LED data per frame across the serial link at 60 Hz, so the link becomes a real interface with a real protocol rather than two wires carrying occasional commands. And you have re-created the 90-LED scheduling problem that drove the RP2350 choice. **This is the current design minus the custom board.** Worth doing only if the Pi's LED path fails on the bench.

### Alternative 2 — maximum Pi: shrink the real-time core as far as it will go

| Function | Lives on | Note |
|---|---|---|
| **A, B** | Microcontroller | the irreducible core |
| **C** | Pi, via `quadenc` in PIO, **fanned out** so the microcontroller also counts it | The microcontroller still needs it for the control law, so this is duplication, not a move |
| **D, E, F, G** | Pi | |

**This answers your question "how small can it be made".** The honest answer: **A and B only, and even then C has to be wired to the microcontroller as well.** So the real-time core is A, B and C's two input pins — a microcontroller, a motor driver, one SPI port and one counter. If you eventually build a board, that is what it is.

**Cost of actually adopting this:** the E jitter problem in §5, and the G scroll-path problem in §5. **Judgement: not recommended, but it is the right mental model of the minimum.**

### Alternative 3 — buy a SmartKnob and bolt the rest on

| Function | Lives on | Note |
|---|---|---|
| A, B | **Makerfabs MaTouch SmartKnob, $69** | Already debugged by someone else |
| C, E | Its ESP32-S3 — **but** you must find spare pins, and the original board publishes none | The SeedLabs board publishes "7 additional GPIOs"; the Makerfabs one does not |
| D, F, G | Pi | |

**Trade:** fastest possible route to a hand-feel benchmark, because it arrives working. **Cost:** its motor is a 3205 gimbal in its own housing, not your 2804 pressing on a friction band, so it tells you nothing about *your* mechanism; its pin availability is undocumented; and it is a finished object you would be dismantling. **Judgement: buy one to feel, do not build on it.**

---

## 8. What to buy this week

| Item | Why | Price | Link |
|---|---|---|---|
| **ESP32-S3-DevKitC-1** | The real-time core. Hardware quadrature counter, native USB, best-trodden SimpleFOC path | **£28.90** | [The Pi Hut](https://thepihut.com/products/esp32-s3-devkitc-1-development-board) |
| **TMC6300-BOB × 2** | The exact motor driver from your design, on headers. Only four in stock | **£19.96 ex VAT ea** | [Farnell UK](https://uk.farnell.com/trinamic/tmc6300-bob/breakout-dev-board-3-phase-bldc/dp/3416040) |
| **Raspberry Pi Pico 2** | The fallback core, and probably the production one. At this price, buy it now | **£3.60** | [Pimoroni](https://shop.pimoroni.com/en-us/products/raspberry-pi-pico-2) |
| **USB-C Data/Power Splitter** | Lets the Pi be mains-powered *and* a USB device at the same time. Solves a problem you have not hit yet | **£3.00** | [The Pi Hut](https://thepihut.com/products/usb-c-data-power-splitter) |
| **74AHCT125 quad level shifter** | Mandatory for the LED string at 5 V. The correct logic family | **£1.30** | [The Pi Hut](https://thepihut.com/products/74ahct125-quad-level-shifter-3v-to-5v) |
| **Pimoroni DRV2605L breakout** | Function E, on headers. Adafruit's own board is sold out at Pi Hut | **£14.10** | [The Pi Hut](https://thepihut.com/products/drv2605l-linear-actuator-haptic-breakout) |
| **AS5600 STEMMA QT** | The stand-in second angle sensor, so the two-angle control law can be proved before the code ring exists | **£5.40** | [The Pi Hut](https://thepihut.com/products/adafruit-as5600-magnetic-angle-sensor) |
| **AEDR-8300-1W2 × 3** | 212 lines/inch, 3.3 V native, in stock now, 14-week lead time on reorder | **£8.10 ex VAT ea** | [Farnell UK](https://uk.farnell.com/broadcom/aedr-8300-1w2/photointerrupter-reflective/dp/1735258) |
| **MT6701 module × 2** | No reputable breakout exists; unbranded is the only option | ~£5–8 ea | [eBay UK](https://www.ebay.co.uk/itm/116603958944) / [Amazon UK](https://www.amazon.co.uk/MT6701-Magnetic-Encoder-Brushless-Replaces-Black/dp/B0DBJ2BN45) |
| **1.5 g linear servo, UK stock** | Proves pulse range and current, which AGFRC do not publish | **£20.99**, 3-day | [eBay UK](https://www.ebay.co.uk/itm/352981537170) |
| *Optional:* Makerfabs MaTouch SmartKnob | A hand-feel benchmark that arrives working | **$69.00** | [Makerfabs](https://www.makerfabs.com/matouch-smartknob-assembled.html) |
| *Already on your list:* SK6812 side-emitting strip, 144/m | The LED bench test | ~£30 | per your existing sourcing document |

**Roughly £150 including VAT without the SmartKnob, £205 with it.** Everything except the MT6701 modules and the SmartKnob is UK next-day.

**And send the code-ring enquiry to MELTEC, PWB Encoders, Laser Lab and Optry Tech on the same day.** It costs nothing and it is the only item with a multi-week clock.

**Then, in this order:**

1. **Ninety LEDs off the Pi, under load.** Pi5Neo over SPI first, `piows2812` second. Run a heavy Godot or Qt scene at the same time and watch for flicker. *One evening. If this fails, function F goes back to the microcontroller and the RP2350 argument returns.*
2. **Pi as a USB keyboard, mains-powered, through the splitter.** `libcomposite` by hand, per the kernel documentation. You want this working even though function G is staying on the microcontroller, because the companion-application data link uses the same port. *One evening.*
3. **Motor spinning under SimpleFOC on the ESP32-S3 with the TMC6300-BOB and the MT6701.** Then detents. *This is the day that matters — everything else is subordinate to whether the feel is right.*
4. **The two-angle problem**, with the AS5600 on a friction-coupled second shaft. *This is the genuinely novel work and no prior art helps.*
5. Servo pulse range and current from the Pi's hardware PWM; DRV2605L from the microcontroller.

---

## 9. What could go wrong

**Pins.** The B-G431B-ESC1 example is the general warning: a board can be excellent at motor control and still be useless to you because it assumes one sensor. Check the pin map before the price on everything. The ESP32-S3-DevKitC-1 is safe on this count; the Pico 2 is safe on pin *count* but not on *software* — `Arduino-FOC-drivers` has no RP2040 or RP2350 encoder driver at all, so the knob's quadrature is a third-party PIO library you integrate yourself.

**Timing, on the Pi's LED path.** This is the largest genuine unknown in the recommendation. The mechanism is documented and there are three implementations, but **nobody has published ninety LEDs on a Pi 5 under load with a report of no flicker.** If it fails, the fallback is Alternative 1 and you are back to a PIO-class microcontroller. Test it first for exactly this reason.

**Timing, on the Pi's HID path — the reason it stays on the microcontroller.** There is **no published measurement of Linux USB gadget HID latency**, on any Pi. That absence is itself the argument: you would be the person who finds out.

**Firmware, on the Pi's gadget path.** The officially-supported package does networking only. HID means hand-written configfs scripts whose every published example targets a Pi Zero. Expect an evening of the mechanism being subtly different, not a week.

**RP1's PIO is undocumented and shallow.** One block, four state machines, no chapter in the datasheet, register access proxied over PCIe, and "blocking operations block the whole RP1 firmware interface until they complete". If you end up with both `piows2812` and `quadenc` running, you are stacking two undocumented things on one shared resource. **Using SPI for the LEDs avoids all of this** and is why I put it first.

**Supply.** Four TMC6300-BOBs at Farnell is not a supply chain — buy two now. The AEDR-8300's 14-week reorder lead time is the number that should worry you at sixty units, not the price. The SmartKnob motor "sells out quickly each time" per its own maintainer. The Nucleo-G431RB, the best FOC silicon on the list, is quoted at July 2027.

**A community that has moved on.** SmartKnob's own maintainer says it is "not recommended for general use". `rpi_ws281x`'s Pi 5 support is a single-channel out-of-tree kernel module with "concurrent channel support will be added soon" as an open promise. SimpleFOC's shop is out of stock on every board it sells and its own page notes the boards are "sold and shipped by individual SimpleFOC team members, not by SimpleFOC as a company". None of this stops you building one; all of it argues against depending on any single one of them for sixty units.

**Licences.** The original SmartKnob is Apache 2.0 and CC-BY 4.0 — copy it freely with attribution. **The SeedLabs derivative is not**: commercial use needs a partnership agreement with royalties. If you buy that kit and lift its firmware, you have inherited a negotiation.

**Space — reported as a finding, as you asked.** Your current model budgets **30 × 30 × 3.6 mm** on top of a blower fan. This recommendation does not fit that.

| | Footprint | Height with headers |
|---|---|---|
| ESP32-S3-DevKitC-1 | 70 × 28 mm | ~13 mm *(judgement — not published)* |
| Raspberry Pi Pico 2 | 51 × 21 × 1 mm | ~9 mm with headers |
| TMC6300-BOB | ~25.4 × 20.3 mm | ~12 mm |
| DRV2605L breakout | not published | — |
| 74AHCT125 breakout | not published | — |

So the microcontroller-plus-driver pair alone is roughly **100 × 30 mm of board area against a 30 × 30 mm budget** on the ESP32 route, or about **80 × 25 mm** on the Pico 2 route. In a 175 mm disc that is findable area but it is not the pocket that is drawn. **The Pico 2 route is the one that could plausibly go inside the current model; the ESP32-S3 route will need the plate re-cut.** You said you would rather re-cut the mechanical design than commission a board, so this is a cost you have already accepted — but it is real and it is not small.

**Volume, as a footnote.** The bought-board stack does not dead-end technically at sixty to seventy units; it dead-ends *ergonomically*, because you would be hand-wiring sixty-five stacks of jumper leads. At that point a small carrier board becomes worth having — but the important finding is what that board would be. With F and D on the Pi and no internal USB device role of its own, it is a microcontroller, a TMC6300, two level shifters and connectors: **a fraction of the twenty-five-component four-layer board now specified, and a much cheaper thing to have designed.** The one item that genuinely dead-ends is the code ring, which is a custom part at any quantity and needs quoting now.

---

## Sources

**Raspberry Pi 5 and RP1** — [USB gadget mode in Raspberry Pi OS, 21 Jan 2026](https://www.raspberrypi.com/news/usb-gadget-mode-in-raspberry-pi-os-ssh-over-usb/) · [rpi-usb-gadget README](https://github.com/raspberrypi/rpi-usb-gadget/blob/pios/trixie/README.md) · [RP1 peripherals datasheet](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf) · [Device-tree overlays README](https://github.com/raspberrypi/linux/blob/rpi-6.12.y/arch/arm/boot/dts/overlays/README) · [RP1 PIO support, kernel PR #6470](https://github.com/raspberrypi/linux/pull/6470) · [piolib README](https://github.com/raspberrypi/utils/tree/master/piolib) · [piolib announcement](https://www.raspberrypi.com/news/piolib-a-userspace-library-for-pio-control/) · [Power supplies documentation](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/power-supplies.adoc) · [USB Power Delivery on Raspberry Pi 5, white paper](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009856-WP-1-USB%20Power%20delivery%20on%20Raspberry%20Pi%205.pdf) · [CM5 IO Board datasheet](https://datasheets.raspberrypi.com/cm5/cm5io-datasheet.pdf)

**Timing evidence** — [OSPERT 2024, real-time Linux on Raspberry Pi 5 (cyclictest)](https://antonio.paolillo.be/publications/workshops/ecrtsOspert2024_dewit_rtlinux_paper.pdf) · [Pi 5 GPIO edge latency measurement, Sept 2026](https://satpulse.net/2026/09/06/measuring-systematic-pps-bias-on-the-raspberry-pi-5.html) · [Linux kernel USB HID gadget documentation](https://docs.kernel.org/usb/gadget_hid.html)

**LEDs on a Pi 5** — [rpi_ws281x Pi 5 support wiki](https://github.com/jgarff/rpi_ws281x/wiki/Raspberry-Pi-5-Support) · [Pi5Neo](https://github.com/vanshksingh/Pi5Neo) · [Adafruit, NeoPixels on the Pi 5](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/using-neopixels-on-the-pi-5) · [RP1 hardware PWM notes](https://gist.github.com/Gadgetoid/b92ad3db06ff8c264eef2abf0e09d569) · [pwm-2chan overlay issue](https://github.com/Pioreactor/rpi_hardware_pwm/issues/10)

**SmartKnob** — [scottbez1/smartknob README](https://github.com/scottbez1/smartknob/blob/master/README.md) · [platformio.ini, the pin map](https://github.com/scottbez1/smartknob/blob/master/platformio.ini) · [Motor status wiki](https://github.com/scottbez1/smartknob/wiki/Motor-Status) · [SparkFun ROB-20441 motor](https://www.sparkfun.com/products/20441) · [SeedLabs DevKit v0.1](https://store.seedlabs.it/products/smartknob-devkit-v0-1) · [SeedLabs firmware README and licence](https://github.com/SeedLabs-it/smartknob-firmware) · [Makerfabs MaTouch SmartKnob](https://www.makerfabs.com/matouch-smartknob-assembled.html) · [CNX Software review](https://www.cnx-software.com/2025/02/12/matouch-smartknob-assembled-esp32-based-rotary-knob-touchscreen-display/)

**Motor control hardware** — [SimpleFOC supported microcontrollers](https://docs.simplefoc.com/microcontrollers) · [Arduino-FOC releases](https://github.com/simplefoc/Arduino-FOC/releases) · [Arduino-FOC-drivers](https://github.com/simplefoc/Arduino-FOC-drivers) · [ESP-IDF PCNT, quadrature decoding](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/pcnt.html) · [TMC6300-BOB, Farnell UK](https://uk.farnell.com/trinamic/tmc6300-bob/breakout-dev-board-3-phase-bldc/dp/3416040) · [B-G431B-ESC1, Farnell UK](https://uk.farnell.com/stmicroelectronics/b-g431b-esc1/discovery-board-32bit-arm-cortex/dp/3247670) · [UM2516, B-G431B-ESC1 user manual](https://www.st.com/resource/en/user_manual/dm00564746-electronic-speed-controller-discovery-kit-for-drones-with-stm32g431cb-stmicroelectronics.pdf) · [SimpleFOC shop](https://simplefoc.com/shop) · [Dagor Brushless Controller documentation](https://docs.dagor.dev/) · [LILYGO T-Knob](https://lilygo.cc/products/t-knob)

**Sensors and small parts** — [AEDR-8300-1W2, Farnell UK](https://uk.farnell.com/broadcom/aedr-8300-1w2/photointerrupter-reflective/dp/1735258) · [AEDR-8300-1K2, no longer stocked](https://uk.farnell.com/broadcom-limited/aedr-8300-1k2/encoder-2channel-smd-75lpi/dp/1161101) · [AS5600 STEMMA QT, The Pi Hut](https://thepihut.com/products/adafruit-as5600-magnetic-angle-sensor) · [RLS ring encoders, standard sizes](https://www.rls.si/eng/ring-encoders) · [RLS Direct store, delivery regions](https://www.rls.si/eng/news/RLS-encoder-online-store-launch/) · [AS5311 adapter board, not for new designs](https://azcus.digikey.com/en/products/detail/ams-osram-usa-inc/AS5311-ADAPTERBOARD/3828353) · [DRV2605L breakout, The Pi Hut](https://thepihut.com/products/drv2605l-linear-actuator-haptic-breakout) · [74AHCT125 level shifter, The Pi Hut](https://thepihut.com/products/74ahct125-quad-level-shifter-3v-to-5v) · [USB-C Data/Power Splitter, The Pi Hut](https://thepihut.com/products/usb-c-data-power-splitter) · [ESP32-S3-DevKitC-1, The Pi Hut](https://thepihut.com/products/esp32-s3-devkitc-1-development-board) · [Raspberry Pi Pico 2, Pimoroni](https://shop.pimoroni.com/en-us/products/raspberry-pi-pico-2) · [Pico 2 datasheet, dimensions](https://pip-assets.raspberrypi.com/categories/1005-raspberry-pi-pico-2/documents/RP-008299-DS-3-pico-2-datasheet.pdf)
