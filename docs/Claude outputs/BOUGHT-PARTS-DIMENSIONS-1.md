# the 60 — bought parts: what exists, what we pick, what the device does about it

**Method (Ryan's rule, 3 September 2026): the part determines the design.** This document starts from what is actually stocked, then says what the device changes to suit it. It does not start from a specification. Every row links to the page the numbers came from.

Researched 3 September 2026. **NOT PUBLISHED** means the supplier does not state it — never an estimate.

---

## 1. Detent magnets

### What exists

The European metric catalogues stock small blocks magnetised **through the thinnest dimension**. A metric 3 × 3 × 6 magnetised along the 6 mm axis is a custom order here. Two suppliers break that pattern.

| Part | Size (mm) | Grade | Magnetised | Tol. | Pull | Price 1 / 500 | Stock | Link |
|---|---|---|---|---|---|---|---|---|
| **K&J b224** | 3.17 × 3.17 × **6.35** | N42 Ni-Cu-Ni | **through the 6.35 length** | ±0.1 | 0.52 kg, 6353 G | $0.35 / $0.31 | in stock | [kjmagnetics.com/b224](https://www.kjmagnetics.com/b224-neodymium-block-magnet) |
| **supermagnete S-03-06-N** | **Ø3 × 6 rod** | N48 Ni-Cu-Ni | **axial** | ±0.1 | 400 g (3.92 N), shear 81 g | €0.25 / €0.18 @360 | **251,820** | [supermagnete S-03-06-N](https://www.supermagnete.de/eng/rod-magnets-neodymium/rod-magnet-3mm-6mm_S-03-06-N) |
| supermagnete S-03-10-N | Ø3 × 10 rod | N45 | axial | ±0.1 | 390 g | €0.33 / €0.24 @360 | in stock | [link](https://www.supermagnete.de/eng/rod-magnets-neodymium/rod-magnet-3mm-10mm_S-03-10-N) |
| K&J b228 | 3.17 × 3.17 × 12.7 | N42 | through length | ±0.1 | 0.54 kg, 6535 G | $0.62 / $0.56 | in stock | [b228](https://www.kjmagnetics.com/b228-neodymium-block-magnet) |
| K&J b222 | 3.17 cube | N42 | through thickness | ±0.1 | 0.39 kg | $0.22 / $0.20 @250 | in stock | [b222](https://www.kjmagnetics.com/b222-neodymium-block-magnet) |
| K&J D24 | Ø3.17 × 6.35 rod | N42 | axial | ±0.1 | 0.39 kg, 6403 G | $0.32 | in stock | [d24](https://www.kjmagnetics.com/d24-neodymium-cylinder-magnet) |
| first4magnets 5×5×5 | 5 cube | N42 | through thickness | ±0.1 | 1.23 kg, 4600 G | £0.41 / £0.20 @1000 | in stock | [f4m 19215](https://www.first4magnets.com/product/5-x-5-x-5mm-thick-n42-neodymium-magnet-1kg-pull-19215) |
| first4magnets 3×3×3 | 3 cube | N42 | through thickness | — | 0.38 kg | £9.10/pack | — | [f4m 19980](https://www.first4magnets.com/product/3-x-3-x-3mm-thick-n42-neodymium-magnet-038kg-pull-19980) |
| AMF 22052 | 8 × 3 × **12** | N52 | **through the 12** | ±0.05 | 1.63 kg, 7215 G | $4.59 / $3.43 @100 | to order | [amfmagnets](https://amfmagnets.com/products/8mm-x-3mm-x-12mm-n52-magnetised-through-12mm) |

Custom is quote-only everywhere — [Magnet Store](https://magnetstore.co.uk/custom-manufactured-magnets/order-custom-magnets/), [K&J](https://www.kjmagnetics.com/custom-neodymium-magnets.asp), [e-magnets UK](https://e-magnetsuk.com/product-category/neodymium/) — and **none of them publishes a minimum order or a lead time.**

### The pick: supermagnete **S-03-06-N**, Ø3 × 6 axial rod

A quarter of a million in stock, €0.18 in 360s, axially magnetised, ±0.1 mm, European. It is the round equivalent of what the design wanted, and a round pocket prints rounder than a square one.

**What the device changes:** the magnet pocket becomes a Ø3.1 blind bore 6 mm deep instead of a 3 × 3 × 6 slot. That is a *simpler* part, not a harder one — no corners to under-extrude, and the magnet self-centres.

**Second choice if a square pocket is wanted after all: K&J b224** — 3.17 × 3.17 × 6.35 magnetised through the length, on the shelf at $0.31. The pocket grows 0.17 mm each way and 0.35 mm deep. Trivial.

**Note against the earlier claim:** I previously wrote that 3 × 3 × 6 "is not a catalogue size". That was wrong in substance — it is a catalogue size in imperial (b224) and its round equivalent is one of the highest-stock magnets in Europe. The error was searching metric block catalogues only.

---

## 2. Drive motor

### What exists

A full market survey of micro gearmotors gives **three height tiers**, and only one has depth, price, stock and back-drive together.

| Tier | Families | Smallest height | Verdict |
|---|---|---|---|
| Ø6–Ø8 round | [Pololu sub-micro planetary](https://www.pololu.com/category/56/plastic-dc-gearmotors), [NFP 6 mm](https://nfpshop.com/6mm-nano-planetary-dc-gearmotors), [PMD 206-xxx](https://catalogue.precisionmicrodrives.com/products/342a0fa3-b655-4f25-8f45-240ef142e8dc/206-10c-6mm-dc-coreless-gearmotor), [Faulhaber 0816+08/1](https://shop.faulhaber.com/0816p003sr-08-1-256-1-mg09.html) | **6 mm** | torque needs 136:1–700:1, which kills back-drive; or Faulhaber at **$202–282** |
| **10 mm (Ø10 round and 10 × 12 rectangular)** | **[Pololu micro metal](https://www.pololu.com/category/60/micro-metal-gearmotors)**, [ServoCity N20](https://www.servocity.com/premium-n20-gear-motors/), [Adafruit N20](https://www.adafruit.com/product/4641), [NFP GM10](https://nfpshop.com/product/10mm-metal-gear-motor-model-nfp-gm10-m20), [PMD 210-xxx](https://catalogue.precisionmicrodrives.com/products/de193b93-1164-47ea-bce4-96e2dcbc4ee1/210-102-10mm-dc-gearmotor-24mm-type) | **10 mm** | **the only place cheap + in stock + back-drivable + >20 mNm all intersect** |
| 12–15 mm and pancake | [PMD 212-xxx](https://catalogue.precisionmicrodrives.com/products/0708ba56-7373-4737-a813-e87eceeab33a/212-40d-12mm-dc-gearmotor-24mm-type), [iPower GM2804 gimbal](https://shop.iflight.com/ipower-gm2804-gimbal-motor-pro1153) | 12 mm / 15 mm | the best engineering answers, but over the 9.8 mm cavity |

**Confirmed dead: the 90° micro gearmotor.** Every Pololu right-angle plastic gearmotor is zero-stock/special-order — [#1120](https://www.pololu.com/product/1120), [#1123](https://www.pololu.com/product/1123), [#1124](https://www.pololu.com/product/1124), [#1593](https://www.pololu.com/product/1593). Chinese right-angles are worm-driven and will not back-drive.

### The pick: Pololu **10 × 12 × 25 micro metal gearmotor**, 6 V

Flat 10 mm face — a real bolt-down datum rather than a cylinder tangent. Ø3 D-shaft, 9 g, spur gears so it back-drives. [Dimension drawing](https://www.pololu.com/file/0J949/micro-metal-gearmotors-dimensions.pdf) · [datasheet](https://www.pololu.com/file/0J1487/pololu-micro-metal-gearmotors-rev-6-2.pdf). $23.95, hundreds of every ratio in stock.

| Candidate | rpm | Stall torque | Stock | Link |
|---|---|---|---|---|
| **#2367 MP 100:1** | **220** | 92 mNm | 366 | [pololu.com/product/2367](https://www.pololu.com/product/2367) |
| #2368 MP 150:1 | 150 | 128 mNm | 300 | [/2368](https://www.pololu.com/product/2368) |
| #1101 HP 100:1 | 310 | 167 mNm | 409 | [/1101](https://www.pololu.com/product/1101) |
| #3065 HPCB 100:1 (carbon brush, long life) | 330 | 157 mNm | 167 | [/3065](https://www.pololu.com/product/3065) |

Cheaper equivalents in the same form factor if cost matters at 60 units: [HandsOn GA12-N20-100](https://handsontec.com/index.php/product/ga12-n20-geared-mini-dc-motor/) at $4.25 ([drawing](https://www.handsontec.com/dataspecs/motor_fan/GA12-N20.pdf)), [DFRobot FIT0579](https://www.dfrobot.com/product-1736.html) at $7.50.

**Do not buy the encoder variants** — they add a PCB on the rear and break 10 mm. Encoding belongs on the knob.

### What the device changes: a friction bevel replaces the right-angle gearbox

The motor's shaft is **horizontal**. The knob's bore needs a wheel spinning about a **vertical** axis. Rather than hunt a gearbox that does not exist, the transmission turns the corner itself, with two parts:

1. The motor lies flat on the pad, shaft pointing radially, with a small rubber wheel on it.
2. That rubber wheel presses **upward** on the underside of a larger flat disc running on a plain vertical pin. The disc's rim is what touches the knob's bore.

This is the idler/rim drive from a record player. No gears, no backlash, no worm, and the reduction is set by where the rubber wheel meets the disc — so the ratio is a free parameter, adjustable by moving one part. The motor is a stock 10 × 12 × 25 can; the disc and the pin are printed.

---

## 3. Lift-off actuator

### What exists

| Family | Best stocked part | Size (mm) | Stroke | Force | Speed | Latches? | Price | Link |
|---|---|---|---|---|---|---|---|---|
| **Micro linear servo** | **AGFRC C1.5CLS PRO** | **21.4 × 15.2 × 6.0**, 1.5 g | 9 mm | **2.4 N** @6 V | 12 ms/mm | by gearbox + loop | ~$15–25/pr | [agfrc.com](https://www.agfrc.com/index.php?id=2438) · [Amazon](https://www.amazon.com/AGFRC-Micro-Linear-Servo-Coreless/dp/B08R73TZSH) |
| Micro linear servo | Micron SuperMicro 1.4 g | 18.1 × 15.2 × 7.8 | 8 mm | 0.34 N — too weak | 0.12 s | — | **£8.00** | [micronradiocontrol](https://www.micronradiocontrol.co.uk/servo.html) |
| Micro rotary servo | Micron 1.7 g digital | 14 × **6.2** × 18 | rotary | 0.075 kg·cm (≈2.5 N on a 3 mm crank) | 0.05 s/60° | — | **£5.75** | [same](https://www.micronradiocontrol.co.uk/servo.html) |
| **Latching solenoid** | **Geeplus S1L-0211** | **12 × 7 × 6** | NOT PUBLISHED | NOT PUBLISHED | <5 ms (family) | **yes, both ends, zero holding power** | quote | [geeplus latching](https://www.geeplus.com/latching-solenoids/) · [tech note](https://www.geeplus.com/latching-solenoids-general-technical-information/) |
| Latching solenoid | Delta DSML-0224-05 | NOT PUBLISHED | 5.08 mm | NOT PUBLISHED | — | yes | — | [DigiKey](https://www.digikey.com/en/products/detail/delta-electronics/DSML-0224-05/5214011) |
| Push solenoid | Geeplus 110C | Ø11 | 2 mm | 4.5 N @10% ED | <5 ms | no | quote | [geeplus push-pull](https://www.geeplus.com/push-pull-solenoids/) |
| Push solenoid | Adafruit 2776 | ~20 long, **Ø NOT PUBLISHED** | 3 mm | 0.78 N | — | no | $4.95 | [adafruit 2776](https://www.adafruit.com/product/2776) |
| Voice coil (camera) | Commonlands CLA321-VCM | 23.5 hole pitch, **height NOT PUBLISHED** | 0.4–0.6 mm | ~50 mN | fast | no | $29.00 | [commonlands](https://commonlands.com/products/voice-coil-motor-m12-lens-auto-focus-cla321) |
| Piezo bender | PiezoDrive BA4010 | 40 × 10 | 1.1 mm | 0.18 N | fast | no | $16.50 | [piezodrive](https://www.piezodrive.com/product/1-1mm-range-piezo-bender-actuator-ba4010/) |
| Piezo bender | PI PL112.10 | 18 × 9.6 × 0.67 | ±0.1 mm | 2.1 N | fast | no | quote | [piceramic](https://www.piceramic.com/en/products/piezoceramic-actuators/bender-actuators/pl112-pl140-picma-bender-103000) |
| SMA | Dynalloy Flexinol 0.13 | wire | 4 % of length | 2.2 N | **1.4–1.6 s to cool** | no | min order $250 | [dynalloy](https://dynalloy.com/technical-data-wires/) |
| SMA latching | Miga Gen1-RevG ThinLock | NOT PUBLISHED | — | — | — | yes | $39.95 | [migarobotics](https://www.migarobotics.com/shop-1) |

**Dead ends confirmed:** phone OIS/VCM and Nidec Copal shutter actuators are made in millions but are **OEM-only with no published dimensions, force or stroke and no distributor stock** ([Nidec](https://www.nidec.com/en/nidec-precision/product/search/category/B109/M111/S101/NCPL-Shutter-module-for-mobile-device/)). Micro latching relays enclose their armature. Miniature linear steppers start at Ø15 and move in mm/s.

### The pick: **AGFRC C1.5CLS PRO** micro linear servo — and the application changes

**6.0 mm tall**, so it passes under the magnet arms with room to spare. 2.4 N against the ~1 N needed. 12 ms per mm. Buyable today.

**And Ryan's point stands: the application was wrong, not the solenoid.** A solenoid is a two-state device, which is why it needed a spring, a hard stop and a swinging carriage. A servo is *proportional* — so the same actuator that lifts the wheel off also **sets how hard it presses**, which makes drive force a software parameter instead of a fixed geometry. That deletes the spring, the hard stop and the preload tuning in one move.

Second choice if zero holding current matters more than proportionality: **Geeplus S1L-0211**, 12 × 7 × 6, latching at both ends. Its stroke and force are not published — request the datasheet before designing to it.

---

## 4. Speaker

### What exists

The finding that matters: **everything 5–6 mm thick has a resonance of 500–630 Hz**, which means no fundamental below that at all. Depth, not diameter, buys sound.

| Part | Outline | Thick | Power | SPL | **Fo** | Band | Stock | Link |
|---|---|---|---|---|---|---|---|---|
| **Soberton SP-4005-1** | **Ø40** | **8.5** | 1.0 / 2.0 W | **93 dB** | **430 Hz** | 300 Hz–8 kHz | DigiKey | [soberton.com/sp-4005-1](https://www.soberton.com/sp-4005-1/) |
| PUI AS03208MS-3-R | 32.7 × 32.7 | **16.5** | 3 W | 85 dB | **200 Hz** | **200 Hz–20 kHz** | DigiKey 3,575 | [puiaudio](https://puiaudio.com/product/speakers-and-receivers/AS03208MS-3-R) |
| PUI AS04008PS-4W-R | 40 × 28.3 | 11.5 | 2 / 4 W | 84 dB | 380 Hz | 380 Hz–20 kHz | DigiKey 8,418 | [puiaudio](https://puiaudio.com/product/speakers-and-receivers/AS04008PS-4W-R) |
| Same Sky CSS-40408N | 40.1 × 40.1 | 14.5 | 5 / 8 W | **100 dB** | 440 Hz | NOT PUBLISHED | DigiKey | [samesky](https://www.sameskydevices.com/product/audio/speakers/miniature-(10-mm~40-mm)/css-40408n) |
| PUI AS04008MR-21-R | Ø40 | 5.0 | 1 / 1.5 W | 89 dB | 630 Hz | 630 Hz–6 kHz | Mouser 775 | [puiaudio](https://puiaudio.com/product/speakers-and-receivers/AS04008MR-21-R) |
| Soberton SP-3605 | Ø36 | 5.0 | 1.0 / 1.5 W | 90 dB | 550 Hz | 300 Hz–5 kHz | DigiKey | [soberton](https://www.soberton.com/sp-3605/) |
| Soberton SP-3205 | Ø32 | 5.2 | 0.8–1.2 W | 92 dB | 550 Hz | 300 Hz–8 kHz | DigiKey | [soberton](https://www.soberton.com/sp-3205/) |
| PUI AS04008CO-R *(the old BOM part)* | **40 × 20 oval**, diagonal 44.7 | 5.8 | 2 W | 83 dB | 500 Hz | 200 Hz–20 kHz | DigiKey 3,943 | [puiaudio](https://puiaudio.com/product/speakers-and-receivers/as04008co-r) |

No maker in this class publishes Thiele-Small parameters, Xmax, THD or a real response curve. **Fo is the only honest proxy**, and the back volume will matter more than the choice between any two of these.

### The pick: **Soberton SP-4005-1**, Ø40 × 8.5

The rim-ring cavity is **9.8 mm tall** (z 3 → 12.8), so 8.5 fits with 1.3 to spare, and Ø40 sits inside the r 46 ring bore. Against the 5 mm parts it buys **200 Hz lower resonance and +4 dB** for 3.5 mm of depth we already have. This is the "good component" answer.

If the device could ever find **16.5 mm** in one place, the PUI AS03208MS-3-R (200 Hz, 200 Hz–20 kHz) is in a different class from everything else on this list — it is the only part here genuinely suited to music. It does not fit today.

---

## 5. Display module — Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C

**Waveshare publishes DXF + dimensioned PDF + a 33 MB STEP assembly:** [ESP32-P4-WIFI6-TOUCH-LCD-3_4C.zip](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-TOUCH-LCD-3_4C.zip) — from the [resources page](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC/Resources-And-Documents). Product page: [waveshare.com](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-3.4c.htm) · wiki: [link](https://www.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-3.4C).

| Feature | Verified | Was in the model | |
|---|---|---|---|
| Disc OD × thickness | 115.00 × 6.00 | same | ok |
| Lens OD / viewing aperture | 112.50 ±0.10 / 88.20 ±0.20 | — | new |
| LCD active area | 87.60 | same | ok |
| PCB | 85.50 × 65.00 × 1.60 | same | ok |
| **PCB centre offset from disc centre** | **4.50 mm** | 0 | **WRONG** |
| PCB top face below front glass | 7.50 (1.50 air gap) | 1.00 | **WRONG** |
| Housing mounting | **4 × M4 at (±37.50, ±37.50) = Ø106.07 PCD at 45/135/225/315** | M2.5 on Ø104 | **WRONG** |
| Four free PCB holes | Ø3.00 on 58.00 × 49.00 | same | ok |
| Rear stack | PCB bottom −9.10, 4.00 clear, **2.00 PMMA backplate** to −15.10 | not modelled | **MISSING** |
| Tallest rear part | USB-A 6.40 above PCB, 0.50 edge overhang, 0.40 proud of the backplate | 6.40 | ok |
| USB-C ×2 | 3.25 tall, 1.04 overhang, centres 14.48 apart | — | new |
| Total thickness | 15.10 (web images say 15.00 — trust the CAD) | 15.0 | ok |
| Weight | **NOT PUBLISHED** | 60 g assumed | still **V** |

**The 4.5 mm offset matters.** The board's worst corner sits at **r 57.35** from the disc centre — 0.65 mm inside the Ø116 bore. Every earlier statement of the form "at azimuth X the board edge is at r 42.75" is wrong on one side and must be redone from the STEP.

---

## 6. Ring actuator

The ring needs **0.77 mm of travel at r 46 (1.44 mm at the magnet), held with no current.**

| Part | Body | Screw | Step | Force | Holds unpowered | Price | Link |
|---|---|---|---|---|---|---|---|
| **VSM0810 PM linear stepper** | **Ø8 × 8.2** | M2×0.4 or M1.7×0.3 | 18°, **0.015 mm** | 0.37 mNm pull-out | **yes** — 3.6° lead angle | $2–6, MOQ 1 | [micro-steppermotor.com](https://www.micro-steppermotor.com/) |
| NFP-0620-531-MG stepper+gearbox | Ø6 × 16 | — | 18° | 88 mNm | detent only | **$25.00**, 18 in stock | [nfpshop](https://nfpshop.com/product/6mm-micro-dc-stepper-gear-motor-16mm-type-model-nfp-0620-531-mg) |
| NFP-609-699-MS | Ø6 × 21.1 | — | — | 47 mNm | no | $15.00 | [nfpshop](https://nfpshop.com/product/6mm-mini-dc-gear-motor-20mm-type-model-nfp-609-699-0675-ms-metal-shaft) |

0.8 mm at 0.015 mm/step is **53 steps**, open loop, parked with the coils off. A Ø8 × 8.2 can replaces the 27 mm of gearmotor-plus-worm that would not fit bay 3.

---

## 7. Supercapacitors

| Part | C | V | ESR | Can | Price @100 | Stock | Link |
|---|---|---|---|---|---|---|---|
| **Abracon AHCR-S04R0SA206Q** | 20 F | 4.0 (2.5 V floor) | 600 mΩ | **Ø8.0 × 12.0** | $1.95 | 726 | Mouser |
| Abracon AHCR-S04R0SA106Q | 10 F | 4.0 | 1000 mΩ | Ø8 × 12 datasheet / **Ø6.3 × 12 Mouser listing — conflict, verify** | $1.83 | 130 | Mouser |

Two in series = **10 F at 8.0 V in a 16 × 12 × 8 block** — 8 mm tall, inside the 9.8 mm cavity. Lithium-ion hybrids: they cannot be run to zero, and ESR is ~20× a classic EDLC.

---

## 8. Bearings

| Part | Dims | Price ex VAT | Link |
|---|---|---|---|
| **623ZZ** | 3 × 10 × 4 | £2.56 / £1.92 @100 / £1.79 @999 | [Simply Bearings p170604](https://simplybearings.co.uk/shop/p170604) |
| 623-2RS | 3 × 10 × 4 | same breaks | [p170605](https://simplybearings.co.uk/shop/p170605) |
| F623ZZ flanged | 3 × 10 × 4, flange Ø11.5 × 1.0 | £3.42 | [p155242](https://simplybearings.co.uk/shop/p155242) |

Dynamic 0.64 kN, static 0.23 kN, 44,000 rpm in grease. Same-day UK.

---

## 9. Still open

1. **Port board** — 40 × 14 × 1.6 is an **invented envelope**, not a real board, and its −12 mm tangential offset is legacy (placed to clear supercaps that have since moved twice). Delete the offset; re-derive the outline once the USB-C, jack and DAC are laid out.
2. **Geeplus S1L-0211 stroke and force** — not in the public table; request the datasheet.
3. **Abracon AHCR-S04R0SA106Q can diameter** — datasheet Ø8, Mouser Ø6.3.
4. **Display module weight** — not published anywhere by Waveshare.
5. **Magnet field with a Ø3 × 6 rod in a round pocket** — the detent research was done for a 3 × 3 × 6 block face. Re-check the pull curve on the rig; a Ø3 face is 21 % less area than a 3 × 3 face.
