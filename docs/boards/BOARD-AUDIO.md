# the 60 — board 2 of 3: the audio board

**Date: 5 September 2026. Status: design brief, not yet drawn.** Written to be handed to a contract electronics designer with no further conversation needed to start. Everything here is sourced; anything a vendor does not publish is marked **not published**, and anything I concluded rather than read is marked **judgement**.

Companion documents: `the60-board-carrier.md`, `the60-board-motion.md`, `the60-electronics-build-path.md`, `SOURCING-BOM.md`.

> **⚠ One caveat that colours the whole of section 2.** XMOS's website blocks automated access, so the XU316 figures below come from the 2021 datasheet text reproduced verbatim inside a publicly hosted addendum. The current datasheet is **v2.0.0, 13 January 2025**, and the 2021 text labels its operating-conditions and clock tables **"preliminary"**. **The contractor must re-check every rail voltage, current and timing figure against v2.0.0 before layout.** This is the single largest caveat in this document.

---

## 1. What this board is

It presents itself to the computer as a sound card: a stereo output feeding a 3.5 mm **line output** to powered desk speakers, and a stereo input from two microphones for dictation. It also runs the equaliser and the spectrum analysis, because the audio samples are already here, and sends only the resulting numbers to the compute module over a serial link.

It sits behind the internal USB hub, alongside the compute module and the motion board, and it is **self-powered** — it takes 5 V from the product's own supply, not from the computer.

**There is no headphone amplifier and no speaker drive on this board.** The 3.5 mm socket is a line output at consumer level. That ruling simplifies the output stage to almost nothing (section 6).

---

## 2. The processor: XMOS XU316-1024-QF60B-C24

A sixteen-core processor in a 7 x 7 mm 60-pin package that does the USB audio device, the microphone decimation and the signal processing in one part. It is what Topping, SMSL and most of the current converter market ship.

### 2.1 Power rails

| Rail | Min | Typ | Max | Current |
|---|---|---|---|---|
| **VDD** (core) | 0.855 | **0.900** | 0.945 V | 5 mA quiescent, **300 mA typical, 1000 mA maximum** |
| **VDDIOL / VDDIOT / VDDIOR** | 2.97 | 3.30 | 3.63 V | 126 mA absolute maximum per domain |
| **VDDIOB18** | — | **1.8** | 1.98 V | 126 mA maximum |
| **USB_VDD33** | 3.0 | 3.3 | 3.6 V | 0.8-1 mA at high speed |
| **USB_VDD18** | 1.62 | 1.80 | 1.98 V | 30-36 mA at high speed |
| **PLL_AVDD** | 0.855 | 0.90 | 0.945 V | 0.2-5 mA |

**On this package the I/O voltages are not a choice:** *"The left, right, and top IO domains are 3.3V only, the bottom domain is 1.8V only."* Other packages allow programmable domains; this one does not.

**Design the 0.9 V regulator for 1 A** even though typical is 300 mA. XMOS's own schematic checklist item G.1 says so explicitly.

### 2.2 Sequencing is mandatory

Because the package forces 3.3 V on three domains and 1.8 V on the fourth, the "single 1.8 V supply" shortcut in the datasheet is unavailable. XMOS: *"You must ensure that the VDDIOL, VDDIOT, and VDDIOR domains are valid before the device is taken out of reset, as the boot pins are on VDDIOL."* Their own multichannel board does it as: **3.3 V and 1.8 V up first, then 0.9 V last.** Chain the power-good outputs of each regulator into the next one's enable, as their evaluation board does.

Reset pulse minimum 5 µs. Time from reset release to boot start: 295 µs typical, 480 µs maximum.

### 2.3 Decoupling — quoted, because these are requirements not suggestions

- **VDD:** *"Place many (at least eight) 100 nF low inductance multi-layer ceramic capacitors close to the chip."*
- **VDDIO:** one 100 nF 0402 low-inductance capacitor **on each supply pin**.
- **PLL_AVDD:** *"should be separated from the other noisier supplies… a low pass filter (for example, a 1 µF multi-layer ceramic capacitor and a ferrite of 600 ohm at 100MHz and DCR < 1 ohm, eg, **Taiyo Yuden BKH1005LM601-T**) is recommended."*
- **Bulk:** at least 10 µF on VDD and on VDDIO.
- **Vias:** *"Typical designs could use 16 vias in a 4 x 4 grid, equally spaced across the ground paddle. In addition, you should aim to have four VDD vias underneath each of the VDD paddles."* And: other than ground vias, few or no vias under or close around the device.

### 2.4 Clock and boot

**Crystal: 24 MHz ±500 ppm.** With USB the frequency must be 12 or 24 MHz. XMOS recommend 12 pF load, ESR ≤ 60 Ω, fundamental mode, with **Rf = 1 MΩ, Rd = 680 Ω, CL1 = CL2 = 22 pF**. Named parts include Seiko Epson **FA-238 24.0000MD30X-W5** and IQD **LFXTAL032813**. An oscillator may be used instead, but then it must be a **1.8 V** clock into XIN with monotonic edges and jitter under 2 % of the clock period.

**The on-chip memory cannot boot the application.** Boot is from external quad-SPI flash, and **the pinout is hardcoded in the boot ROM and cannot be changed**: X0D01 = select, X0D04-07 = data, X0D10 = clock. The flash must be ready within 300 µs of power-up or the chip must be held in reset. Choose a part already supported by the tools — **Renesas AT25FF321A** is safest because XMOS's own application ships its specification.

**Debug:** the xSYS2 header is 1.27 mm, 2x10, **Amphenol ICC 20021521-00020T4LF**. It is a **1.8 V** interface and needs a 1.8 V debug adapter (**XA-XTAG4**, about $28) — older 3.3 V adapters will not work. Link outputs need 43 Ω series resistors close to the device. A Tag-Connect TC2030 pad set is the smaller alternative. For 60 units, keep one of them: you will reflash.

### 2.5 USB

USB_DP is pin 29, USB_DM pin 28. **No series termination resistors** — the physical layer is compliant on its own. What is specified is the routing: **90 Ω differential, 0.12 mm trace, 0.10 mm gap, 0.10 mm dielectric height, skew under 1 mm**, 0.51 mm to other pairs and 1.27 mm to high-speed signals.

**VBUS detection is mandatory** because this board is self-powered: the device must remove its pull-ups when the host is absent. The circuit is **220 kΩ from VBUS to the pin, 47 kΩ bleeder to ground, 330 kΩ divider for a 3.3 V domain, and 1-10 µF on VBUS** (2.2 µF typical). XMOS explain why a divider rather than a direct pin: *"it avoids any current paths from Vbus to the power supplies on the board which could cause back powering… Back powering the board in this way can cause the supplies not to come up cleanly."*

Their evaluation board also fits a **120 Ω / 2 A ferrite** in the VBUS line and a **Nexperia PUSB2X4Y** protection array. **No common-mode choke is used or required.**

### 2.6 The pin map is already written for us

XMOS's own evaluation board maps exactly the signals this board needs, and every one of these pins is bonded out on this package:

| Signal | Pin | Port |
|---|---|---|
| I²C clock / data | X0D37 / X0D38 | P1N / P1O |
| Master clock | X1D11 | P1D |
| Word clock | X1D01 | P1B |
| Bit clock | X1D10 | P1C |
| Audio data out | X1D00 | P1A |
| Converter reset | X1D09 | P4A3 |
| **Microphone clock** | **X1D22** | P1G |
| **Microphone data** | **X1D13** | P1F |

Copy it. Also copy one detail from their multichannel board: it feeds the master clock to **both tiles** — X1D11 for the audio tile and **X0D11 for the USB clock-synchronisation thread**. That second feed matters.

**⚠ One thing to ask XMOS directly.** Enabling the USB physical layer on a tile consumes ports 8A, 8B, 1E, 1F, 1H, 1I, 1J, 1K on that tile. On this package, tile 0's port 8A overlaps X0D04-07 — the flash pins. XMOS's own application puts USB on tile 0 and does flash-based firmware update on tile 0 and rates it "Release", so it evidently works, but their board uses a different package. **One email, with a layout-sized consequence.**

### 2.7 The module option

**Phaten A316-Mini-V1**: the XU316, its 24 MHz crystal and 16 Mbit of flash in a **13 x 13 x 0.8 mm** 52-pin module, bringing out 25 general-purpose pins including every one in the table above.

**Correction to `the60-electronics-build-path.md`:** that document says the module removes the 0.9 V rail, the crystal and the flash. **It removes the crystal and the flash only.** Pin 48 is a 0.9 V *input* and the module still needs 300 mA typical and 1 A peak at 0.855-0.945 V. The build-path document should be amended.

What it genuinely buys: no crystal circuit to get wrong, no flash compatibility risk, and no 0.4 mm-pitch package with four supply paddles and a via array. Those are precisely the three things that killed a public do-it-yourself XU316 project's first board revision — its author reported *"a 0.9V regulator selection error, oscillator circuit problems, and microcontroller failure."*

**Phaten publish no price, no minimum order and no lead time** — enquiry form only, no Western distributor. Get a written quote before planning around it. For comparison, the bare chip is **$13.05 at 1, $10.81 at 10, $9.21 at 100** at DigiKey with about 1,000 in stock.

---

## 3. Clocking — the decision, and it is not the default

### 3.1 What the converter needs

Minimum master clock is **128 × the sample rate** for normal operation, maximum **50 MHz**. Two legal families:

- **512× (22.5792 / 24.576 MHz)** — works to 192 kHz, exactly at the minimum ratio there.
- **1024× (45.1584 / 49.152 MHz)** — works to 384 kHz, under the ceiling, and divides by 16 to give **3.072 MHz and 2.8224 MHz** — precisely the two microphone clocks the software wants, from an integer divider, with no extra clock source.

**Use the 1024× pair.**

### 3.2 Two oscillators, not the software phase-locked loop

The chip can synthesise the master clock on-chip, and that is the **default** in the software. Fit the oscillators anyway.

XMOS's own hardware manual publishes the comparison and says it themselves: *"The xcore.ai application PLL is obviously the lowest cost and significantly lowest power solution, **however its jitter performance can not match the Si5351A which may be important in demanding applications.**"*

Their published figures for the on-chip route: **7 ps jitter in the 100 Hz-40 kHz baseband, 67-70 ps over 100 Hz-1 MHz, and −4.4 to −11.2 ppm frequency error.** Against the oscillator's **54 fs typical, 75 fs maximum** RMS phase jitter and ±25 ppm.

| | ASDLJ-E-49.152MHZ-L-R-T | ASDLJ-E-45.1584MHZ-L-R-T |
|---|---|---|
| Maker | Abracon | Abracon |
| RMS phase jitter, 12 kHz-20 MHz | **54 fs typ / 75 fs max** | not published for this frequency |
| Supply | 3.3 V ±5 %, 5 mA typ | same |
| Stability | ±25 ppm overall | same |
| Package | **2.5 x 2.0 mm**, 4-pad ceramic | same |
| Pin 1 | **Output enable** — high-impedance when disabled | same |
| Price / stock | **$2.01 at 1**, 7,631 at DigiKey | listed |

**Do not fit a multiplexer.** Use the output-enable pins: two general-purpose pins from the processor, one oscillator enabled at a time, outputs joined through **33 Ω** series resistors. This is what the published Khadas Tone Board does with its two oscillators, and 33 Ω is what XMOS use in their own master-clock path.

The honest counter-argument, so the call is made knowingly: 7 ps in the audio band really is below the noise floor of most converters, XMOS say so, and the software route saves two parts and two pins. If this were a $60 dongle it would be the right answer. It is not, the cost is **$240 across the whole sixty-unit run**, and this audience publishes measurement sweeps.

**Do both on the first board:** lay out the two oscillator footprints *and* route the on-chip output (X1D11) to the same master-clock net through its own 33 Ω resistor and an unfitted link. It costs nothing and allows an A/B on the bench.

---

## 4. The converter: ESS ES9219Q

### 4.1 The package question is closed

**It is a 40-pin quad flat no-lead package, 5 x 5 mm.** Pin 41 is the thermal pad, *"not electrically connected, use for heat dissipation"* — solder it to a ground pour for heat, but it is not a ground.

The "42-ball chip-scale" figure in ESS's launch coverage refers to the **ES9219C**, a different part number, which Mouser lists as **obsolete with restricted availability**. Question resolved.

**⚠ But note:** the datasheet's power and analogue performance tables are labelled *"Measurements taken with ES9219C."* The headline 121 dB dynamic range and −114 dB distortion figures are from the chip-scale part, not the one we are buying. Same die, presumably, but **ask ESS for characterisation data specific to the Q part**, and ask whether a datasheet newer than v1.2 (December 2021) exists.

**Availability:** $13.20 at 1, $11.38 at 5, $10.56 at 25, **$9.91 at 100**; **170 in stock**, two-week factory lead. 170 covers sixty units plus spares with no margin for a second board revision, and its sibling has already gone obsolete. **Buy the whole run's worth now.**

### 4.2 Rails and control

| Pin | Name | Voltage |
|---|---|---|
| 4 | VCCA | **3.3 V** |
| 19 | AVCC18 | 1.8 V ±5 % |
| 20 | AVCC33 | 3.3 V ±5 % |
| 29 | AVDD | **3.3 V** — see below |
| 27, 31, 13, 14 | AVCC_DAC, DVDD, PNEG, PNEG_VC | **internally generated** — decouple only |

**Set AVDD to 3.3 V.** The processor's I/O is 3.3 V only on this package, and the converter's input threshold is AVDD/2 + 0.4 V. At 3.3 V no level shifting is needed; at 1.8 V it would be.

Total consumption in the mode we use is **69 mW**. Digital ground, analogue ground, amplifier ground and charge-pump ground are brought out separately (**four grounds**) precisely so they can be tied at one point under the part rather than letting charge-pump return current flow through the converter's reference.

**Control is I²C only — there is no pin-strap mode.** Address **0x90** (8-bit) with the address pin low. The processor must configure it at start-up. Reset is pin 37, active low, driven from a processor pin.

**Master clock into XIN (pin 3) — do not fit a crystal on the converter.** Feed it the same board master clock, set the clock source register to master-clock input, and power down the crystal oscillator. This also sidesteps three documented crystal hazards in the datasheet.

### 4.3 Charge-pump capacitors — specified, not optional

| Net | Value |
|---|---|
| C1 to C2 (main flying) | **2.2 µF minimum** |
| PNEG to charge-pump ground (main hold) | **22 µF recommended** |
| C1_VC to C2_VC (auxiliary flying) | 1 µF |
| PNEG_VC to charge-pump ground | 1 µF |

*"Use capacitors with an Equivalent Series Resistance of less than 100 mΩ… select capacitors with a minimum X5R dielectric, the X7R dielectric is preferred."* Both pumps switch at 500 kHz, deliberately common so no intermodulation products are produced.

### 4.4 The start-up sequence firmware must walk

This will look like a broken board if it is missed. The analogue volume control's **hardware default is −24 dB**, and *"The AVC is forced to minimum gain until the transition to HiFi mode is complete."* The amplifier mode must be set to **HiFi 2 V** (register 32, value 3), which itself is gated on a general-purpose pin being high and configured as amplifier-mode-select. Then the volume walks up in 1 dB steps to 0 dB.

Power-up order with an external clock: AVDD, VCCA, AVCC33, AVCC18, then the master clock running, then release reset.

---

## 5. Microphones

**Digital, not analogue.** The processor takes them natively, up to eight on one hardware thread, two per pin. The enclosure contains a switching motor bridge, and a one-bit digital stream is immune to it where millivolt analogue signals on wires are not. And the converter is output-only — an analogue microphone would need a second converter chip.

| | **Infineon IM72D128V** | Infineon IM69D130 |
|---|---|---|
| Signal-to-noise | **72 dB(A)** | 69 dB(A) |
| Overload point | 128 dB SPL | 130 dB SPL |
| Sensitivity | −36 dBFS ±1 dB | −36 dBFS ±1 dB |
| Package | **4 x 3 x 1.2 mm**, bottom port | identical |
| Supply | 1.62-3.6 V, 980 µA at 3.072 MHz | same |
| Extra | **IP57 dust and water resistant** | ±2° phase matching at 1 kHz |

**Recommendation: IM72D128V, with the IM69D130 as a drop-in second source.** Signal-to-noise is what dictation at arm's length needs — you are noise-floor limited, not headroom limited. The ±1 dB sensitivity tolerance means a pair matches without trimming.

**Run them from 3.3 V**, as XMOS's evaluation board does, so no level shifting is needed. **A 1 µF bypass capacitor must sit close to each microphone's supply pad.** Clock at **3.072 MHz** for the best signal-to-noise mode.

**The acoustic port is where this goes wrong**, and the rules come from Knowles' design guide:

- Circuit-board hole **0.4-0.9 mm diameter**, gasket cavity **over 1.5 mm**, case hole **1.0-1.5 mm**.
- **"The inside of the PCB acoustic hole must be un-plated so that solder will not wick into the hole and block the hole."** Tell the fabricator explicitly. A plated hole under a bottom-port microphone fills with solder in reflow, and you get sixty dead microphones.
- The gasket must be acoustically opaque and must compress in both worst cases without bulging. Any leak causes echo, noise or response problems.
- A short wide path is fine; a long narrow one creates peaks and sounds tinny.
- Keep the ports as far as possible from the motor and from wherever the desk speakers sit.

**Spacing (judgement — no vendor publishes a figure for a two-microphone dictation array).** A two-element array is unambiguous while spacing is under half a wavelength; at 8 kHz that is 21.4 mm. **Place the pair end-on to the seated user at about 18 mm**, and lay out a second pair of footprints at about 35 mm on the first board so the choice is made by listening. Put both microphones on the same small board or flex with identical acoustic paths — a difference in gasket geometry between the two swamps the part-to-part matching.

**⚠ A scope warning that changes what "dictation must work" means.** The XMOS microphone library decimates and removes offset. **It does no noise reduction, no beamforming, no echo cancellation and no automatic gain.** Two raw channels go to the computer and the noise reduction happens there — Windows' own voice processing, or the dictation application's. On-device noise reduction is XMOS's separate voice product line: a different firmware project and a different licence conversation. **Decide this before committing.** It changes nothing in the hardware.

**One known software issue to test early:** the XMOS library README records that *"Input does not come out of underflow for USB Audio Class 2 when sample rate is 16kHz and channel count is 2"* — which is exactly a two-channel dictation configuration. Run the microphone path at 48 kHz and let the computer resample, or test the issue on an evaluation board before committing.

---

## 6. The line output — remarkably short

With no headphone drive required, this is almost nothing, which is the point of having chosen this converter.

```
OUT_L ──┬── (optional 22-47R) ─────────── TIP
        │
   C0G compensation caps to INB_L, IN_L-GSN_L
                                                    3.5 mm jack
OUT_R ──┬── (optional 22-47R) ─────────── RING
        │
   C0G compensation caps to INB_R, IN_R-GSN_R

GSN_L, GSN_R ──── Kelvin sense, at the jack ─── SLEEVE
                                                  │
                        Littelfuse SP3012-03UTG ──┴── quiet analogue ground
```

**No coupling capacitors.** The amplifier runs from a charge-pump negative rail, so the outputs sit at ground with an offset specified between **−0.5 mV and +0.15 mV**. That is the entire reason to buy this part. Fitting DC-blocking capacitors would add a high-pass corner and distortion and throw the benefit away.

**No buffer.** 2.0 Vrms into 600 Ω, distortion −114 dB into 300 Ω, against powered speakers presenting about 10 kΩ.

**Compensation capacitors are required**, matched, NP0/C0G, between OUT and INB and between IN and the ground-sense pin on each channel. The feedback *resistors* are on-chip. **⚠ The values are in the datasheet's reference schematic, which is a raster image — read them off the figure or ask ESS.**

**Ground sense to the sleeve, at the jack.** GSN_L and GSN_R are the amplifier's load ground sense. Run them as a Kelvin connection to the sleeve so the amplifier senses the actual load return rather than the drop along the ground copper. This is the difference between the datasheet's distortion figure and a mediocre one.

**Protection:** Littelfuse **SP3012-03UTG**, three channels, 0.5 pF line capacitance, ±12 kV contact — the low capacitance matters on an audio line.

### Ground loops — the specific hazard here

The device is mains powered, connected to the computer by USB, and connected to speakers by a cable whose sleeve is mains-referenced through them. That is a classic loop and it will hum. Five rules:

1. **This board is a self-powered USB device.** It takes power from the product's supply, never from the hub's VBUS. Hence the VBUS-detect network in section 2.5.
2. **Do not carry VBUS onto this board as a supply** — one wire, through the divider, no current.
3. Any shield on the internal USB cable bonds to chassis **at the hub end only**.
4. **The jack's sleeve is this board's single ground reference to the outside world.** Nothing else may share that copper — no motor return, no LED return, no regulator return.
5. **Star the whole product's grounds at the power supply**, not here.

If hum persists after all that, the fix is galvanic isolation, not more capacitors. **Judgement: lay out footprints for a pair of small line-level isolation transformers, unfitted, on the first board.** Cheap insurance.

---

## 7. Power

| Rail | Typical | Worst case |
|---|---|---|
| 0.9 V core | 305 mA (≈61 mA at 5 V) | 1005 mA (≈201 mA at 5 V) |
| 1.8 V | ~32 mA | ~40 mA |
| 3.3 V digital | ~50 mA | ~120 mA |
| 3.3 V analogue | ~18 mA | ~25 mA |
| **Total at 5 V** | **≈135 mA, 0.68 W** | **≈340 mA, 1.7 W** |

**Design the 5 V feed for 500 mA continuous**, and make sure it can source the 1 A core transient without sagging — that is about wiring impedance and inlet bulk capacitance, not the number on the supply's label.

| Rail | Part | Why |
|---|---|---|
| 0.9 V at 1 A | **TI TPS62822** buck | The exact part XMOS use for **all three** rails on their evaluation board, with a power-good output. Copying a published working layout |
| 1.8 V at 50 mA | LDO from 3.3 V | XMOS: *"1V8 uses a low drop out linear regulator from the 3V3X supply. This is because 1V8 uses much less current."* |
| 3.3 V digital at 150 mA | TPS62822 buck from 5 V | Keeps 5 V ripple out |
| **3.3 V analogue at 25 mA** | **TI TPS7A20 LDO, its own** | **7 µV RMS noise, 95 dB rejection at 1 kHz.** The single highest-leverage part choice on this board for measured performance. XMOS do exactly this: *"a dedicated analog 3V3 supply… separated and generated by a linear regulator to ensure it is low ripple/noise"* |
| PLL_AVDD | Filtered from 0.9 V | 1 µF plus the specified ferrite, close to the pin |

**Keeping the motion board's noise out**, in descending order of effect:

1. **Separate feeds from the supply, star-connected there.** Two pairs of wires leave the supply — one to each board — never daisy-chained, never sharing a return. If the motor's return current flows through any copper this board uses as a reference, you will hear it. **This is the measure that matters most and it costs one connector.**
2. A **pi filter at this board's inlet**: 10 µF ceramic in parallel with 47 µF bulk, then a ferrite rated over 1 A, then 10 µF and 100 nF. Check the ferrite's DC bias curve — do not read the nominal impedance and assume.
3. Physical separation, and do not mount the boards parallel and facing.
4. **The serial link to the compute module is a noise entry path.** Series resistors of 100-220 Ω, a dedicated ground return in the same connector, and lay out the footprint for a digital isolator in case the shared ground is worse than hoped.
5. No pass-through connectors: the motion board's signals never cross this board.

---

## 8. Board practicalities

**Size (estimate, no vendor figure exists):** with the Phaten module, **45 x 55 mm** is comfortable and 40 x 45 mm is achievable with the jack on a flying lead. Discrete, add about 15 x 15 mm for the crystal, flash and escape routing — call it **55 x 65 mm**. The area is eaten not by the chips but by the jack, the connectors, the debug header, roughly fifty decoupling capacitors, and four regulators with their inductors.

**Six layers.** Four is technically possible and XMOS write their guidance for four, but they simultaneously demand 90 Ω differential USB with a 0.10 mm dielectric height, which on four layers forces a very asymmetric stack.

```
L1  Signal — USB pair, master clock, audio clocks           0.10 mm prepreg to L2
L2  Ground — solid, unbroken under the USB pair and the converter
L3  Signal — control, low speed
L4  Power  — poured islands, one per rail
L5  Ground — solid
L6  Signal — analogue output, microphone lines, connectors
```

**One ground plane. Do not split it.** Partition by placement: the converter, its charge-pump capacitors, the two oscillators and the analogue regulator in one quiet corner; the switching regulators in the opposite corner; the processor between them. Tie the converter's four grounds at a single point directly under it.

**Route the USB pair and the master clock first**, before anything else — XMOS say so. The master clock is the second most important trace on the board, kept short, on one layer, over solid ground, away from the regulators, with its 33 Ω resistor at the source.

The processor is moisture-sensitivity level 3 — 168 hours of floor life. Tell the assembler.

**Connectors**, all latched:

| Link | Part | Ways | Note |
|---|---|---|---|
| USB to the hub | **JST GH 1.25 mm** | 5 | VBUS-detect, D−, D+, ground, ground. **⚠ A crimped connector and loose wire is not a 90 Ω transmission line.** Keep the run under 150 mm and specify a **pre-made twisted-pair assembly**, not a ribbon. Never JST SH |
| Power in, 5 V | **JST VH 3.96 mm** or Molex Micro-Fit | 2 | Its ground pin is this board's **only** power return |
| Microphones | **FPC connector and a small flex** | 4 | **Prefer the flex** — it puts the acoustic ports, gaskets and spacing under mechanical control and lets the spacing change without respinning this board |
| Serial to the computer | JST GH | 4 | 3.3 V, series resistors both ends |
| 3.5 mm jack | Panel mount on a short lead, or board mount | 3 | Metal shell isolated from signal ground; sleeve is the Kelvin point |
| Debug | Amphenol 20021521-00020T4LF, or Tag-Connect pads | 20 / 6 | Keep one |

**No speaker drive on this board.** If an internal speaker is ever added it needs its own class-D amplifier on another board; putting one here would undo sections 6 and 7.

---

## 9. Firmware starting point

Start from **`app_usb_aud_xk_evk_xu316`** in XMOS's `sw_usb_audio` (version 9.2.0, built with XTC Tools 15.3.1) — it is already a two-in, two-out stereo design. Nothing needed is rated below "Release"; the only beta features are DSD playback and HID controls, and neither is wanted.

Changes: a new board description file; **self-powered mode** (which also turns on the VBUS-detect requirement in firmware); explicitly set two input channels and zero I²S input channels, since the input comes from the microphones and not from a converter; enable two microphones in double-data-rate mode; replace the codec initialisation with an ES9219Q I²C sequence; set the master clock family to 1024×; disable the software phase-locked loop if the oscillators are fitted; set the flash device; and get **our own vendor identifier or a licensed product identifier** — the defaults are XMOS's.

No driver is needed on Windows 10/11 or macOS 10.6 and later.

---

## 10. Settled, and still open

**Settled:** the converter's package; no output coupling capacitors; the integrated amplifier used in 2 V mode, not bypassed (it cannot be bypassed for the converter path); digital microphones, Infineon IM72D128V; two oscillators rather than the on-chip clock; the 1024× clock family; a dedicated low-noise regulator for the analogue supplies; external flash is mandatory; sequencing is mandatory; the board is self-powered so VBUS detection is required; six layers; no speaker drive.

**Still open:**

1. **Module or discrete?** Get a written quote, lead time and minimum order from Phaten for 100 pieces, against $9.21 x 60 for the bare chip plus crystal, flash and the extra design hours.
2. **The 16 kHz two-channel input bug.** Bench-test it; most likely the microphones run at 48 kHz and the computer resamples.
3. **Where noise reduction happens** — the computer, or a different XMOS firmware product. No hardware consequence, large product consequence.
4. **Microphone spacing** — lay out two pairs of footprints and choose by listening.
5. **The compensation capacitor values** from the ESS reference figure.
6. **Series resistor and filter at the jack** — fit 0 Ω and pads, measure with two metres of speaker cable attached.
7. **Output isolation transformers** — footprints unfitted on the first board.
8. **Re-verify every XU316 figure against datasheet v2.0.0.**
9. **The USB-versus-flash port overlap question** — one email to XMOS.

## Sources

[XU316-1024-QF60B datasheet text](https://www.pawpaw.cn/media/documents/2022-02/XU316-1024-QF60B-PP24_Datasheet_%E6%9C%A8%E7%93%9C%E7%94%B5%E5%AD%90.pdf) · [XK-EVK-XU316 manual with schematics](https://resources.ampheo.com/static/datasheets/xmos/xk-evk-xu316.pdf) · [xcore.ai Multichannel Audio Board manual with schematics](https://resources.ampheo.com/static/datasheets/xmos/xk-audio-316-mc-ab.pdf) · [sw_usb_audio README](https://raw.githubusercontent.com/xmos/sw_usb_audio/develop/README.rst) · [lib_xua PDM microphone documentation](https://raw.githubusercontent.com/xmos/lib_xua/develop/doc/rst/sw_pdm.rst) · [lib_mic_array README](https://raw.githubusercontent.com/xmos/lib_mic_array/develop/README.rst) · [Phaten A316-Mini-V1 datasheet](https://phaten-audio.com/en/dev_doc/datasheet/modules/a316_mini_v1_datasheet/) · [ES9219 datasheet v1.2](https://www.esstech.com/wp-content/uploads/2022/09/ES9219-Datasheet-v1.2.pdf) · [ES9219Q at Mouser](https://www.mouser.com/ProductDetail/ESS-Technology/ES9219Q) · [Khadas Tone Board v1.3 full schematic](https://dl.khadas.com/products/tone1/schematics/tone-sch-v13.pdf) · [Abracon ASDLJ oscillator datasheet](https://abracon.com/datasheets/ASDLJ.pdf) · [Infineon IM72D128V](https://www.infineon.com/cms/en/product/sensor/mems-microphones/im72d128v/) · [Knowles SiSonic design guide](https://www.knowles.com/docs/default-source/default-document-library/sisonic-design-guide.pdf) · [TI TPS7A20](https://www.ti.com/product/TPS7A20) · [TI TPS62822](https://www.ti.com/product/TPS62822)
