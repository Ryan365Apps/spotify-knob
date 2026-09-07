# the 60 — bill of materials

**Parts to buy. Nothing else.** Reasoning lives in the documents that made each decision; this file is the shopping list and is rewritten in place.

**Run:** 60 units. **Buy column** is what to order including spares. **Buyer:** UK. Prices ex-VAT, read on the date in the last column. China and USA lines carry roughly 25 % on top for import VAT, duty and handling.

**Status key:** ✅ specified and in stock · ⏳ specified, supply or lead time to confirm · ❓ not yet specified — cannot be ordered

---

## 1 · Display

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| `DM-TFTR50-413` | 5 in round panel, 1080×1080, bare, 136.5 × 132.2 × 1.98 mm, active Ø127.0, HX8399-C driver, 4-lane display interface | 1 | 65 | DisplayModule | $119 ea, 20 % off at 500+ | ⏳ 3-week factory lead. Order all in one lot for one brightness bin |
| `TTG050BRT-01` | Same panel class, second source | — | — | Tailor Pixels | $40–61 | ⏳ verify same part and bin before switching |
| Cover lens with bonded touch | Round lens to drawing, optically bonded, 10-point capacitive, controller part number required | 1 | 65 | Chinese module house | quote | ❓ **no supplier engaged. Longest lead item in the product** |
| `FH12-22S-0.5SH` | 22-way 0.5 mm display flat-flex connector, carrier end | 1 | 70 | Hirose, via Mouser/DigiKey | ~$1 | ✅ |

## 2 · Computer

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| `CM5104032` | Raspberry Pi Compute Module 5, 4 GB memory, 32 GB storage, wireless | 1 | 70 | Okdo / Farnell / RS for quantity; Pi Hut retail | £112 | ⏳ **supply risk — ask distribution for a real lead time before committing to a build date** |
| `10164227-1004A1RLF` | Compute module board-to-board connector, 4.0 mm stack (or `-1001A1RLF` for 1.5 mm) | 2 | 145 | Amphenol | ~$2 ea | ✅ not the Hirose part used on the CM4 |
| CR1220 + holder | Real-time clock backup cell | 1 | 70 | any | <£1 | ✅ |

## 3 · Made boards

| Board | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Carrier | 6-layer. Compute module, hub, USB-C, display connector, light sensor, power distribution, panel rails and backlight driver | 1 | 65 | PCBWay turnkey | ~£35–75 across all three boards | ❓ design not started |
| Audio | 6-layer | 1 | 65 | PCBWay turnkey | — | ❓ design not started |
| Motion | 4-layer, thermal vias under the driver | 1 | 65 | PCBWay turnkey | — | ❓ design not started |
| Small boards | Jack carrier, USB-C carrier, light sensor, commutation, encoder breakout, actuator contact bracket | 6 | 6 × 65 | panelise together | — | ❓ no briefs written |

## 4 · Carrier board parts

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| `USB2514B` | 4-port USB 2.0 hub, QFN-36, strap-configurable | 1 | 70 | Microchip | ~$2.50 | ✅ |
| 24 MHz crystal | For the hub | 1 | 70 | any | <£1 | ✅ |
| `USB4520-03-0-A` | USB-C receptacle, mid-mount, 3.16 mm | 1 | 70 | GCT | $0.52 @100 | ✅ |
| `VEML7700-TR` | Ambient light sensor | 1 | 70 | Vishay | $1.02 @100 | ✅ needs its own aperture, not behind the diffuser |
| Panel supply set | +5 V / −5 V analogue, 1.8 V logic, and a 37 V 20 mA constant-current backlight driver with dimming | 1 | 65 | — | — | ❓ **not designed. The prototype adapter does this today** |
| 5.1 kΩ 1 % | CC pull-downs, one per pin, never shared | 2 | 200 | any | — | ✅ |

## 5 · Audio board parts

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| `XU316-1024-QF60B-C24` | XMOS 16-core USB audio controller, 7 × 7 mm | 1 | 70 | DigiKey | $7.53 @25, $6.85 @100 | ✅ 719 in stock, 12-week factory lead |
| `A316-Mini-V1` | Alternative: the above plus crystal and flash in a 13 × 13 mm module | 1 | 70 | Phaten | quote | ⏳ no published price or minimum order — ask |
| `ES9219Q` | Digital-to-analogue converter, QFN-40 5 × 5 mm | 1 | 70 | Mouser | $9.91 @100 | ⏳ **170 in stock, its sibling is obsolete — buy the whole run now** |
| `IM72D128V` | Digital microphone, 72 dB(A), 4 × 3 × 1.2 mm, bottom port. **Fit one, lay out two.** The second only earns its place if something does array processing — nothing in the design does today | 1 | 100 | Infineon | ~$2 ea | ⏳ enclosure needs one acoustic port, and it is not designed yet |
| `ASDLJ-E-49.152MHZ-L-R-T` | Master clock oscillator, 54 fs jitter | 1 | 70 | Abracon | $2.01 @1 | ✅ |
| `ASDLJ-E-45.1584MHZ-L-R-T` | Second master clock | 1 | 70 | Abracon | ~$2 | ✅ |
| `AT25FF321A` | Boot flash, quad-SPI | 1 | 70 | Renesas | ~$1 | ✅ part XMOS's own application ships |
| 24 MHz crystal | 12 pF load, ESR ≤ 60 Ω | 1 | 70 | Epson FA-238 or IQD | <£1 | ✅ omit if the module is used |
| `TPS62822` | 0.9 V core regulator, design for 1 A | 1 | 70 | TI | ~$1 | ✅ also used for the 3.3 V rail |
| `TPS7A20` | Low-noise analogue 3.3 V regulator | 1 | 70 | TI | ~$1 | ✅ |
| `SP3012-03UTG` | 3-channel line protection, 0.5 pF | 1 | 70 | Littelfuse | <£1 | ✅ |
| `35RAPC4BH3` | 3.5 mm line-output jack, threaded nickel bushing | 1 | 70 | Switchcraft | £2.39 @100 | ✅ shell must be isolated from chassis |
| `20021521-00020T4LF` | Debug header, 1.27 mm 2×10 | 1 | 5 | Amphenol | ~£2 | ✅ keep one, not per unit |

## 6 · Motion board parts

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| `RP2350B` | Microcontroller, 80-pin, 48 pins out | 1 | 70 | Raspberry Pi | $0.90 | ✅ |
| Flash + 12 MHz crystal | External boot flash and crystal | 1 | 70 | any | ~£1 | ✅ |
| `TMC6300-LA-T` | Three-phase motor driver, QFN 3 × 3 mm | 1 | 70 | Analog Devices | ~$4 | ✅ 1.0 A continuous per bridge — set the stall limit in firmware |
| `MT6701CT-STD` | Motor rotor angle sensor, serial mode | 1 | 70 | MagnTek | ~$2 | ✅ |
| Ø6 × 2.5 magnet | Diametrically magnetised, for the above | 1 | 70 | — | <£1 | ⏳ the motor maker may fit it |
| `AEDR-8300-1W2` | Knob encoder, reflective, 212 lines per inch, 3.0–5.5 V | 1 | 70 | Broadcom, via Mouser | ~$8 @100 | ⏳ **check stock at 70. The `-1K2` is 75 lines per inch, 5 V only, and Farnell list it as no longer stocked** |
| Code ring | Chrome on polyester, reflective ≥60 %, dark <10 %, bonded into the crown's underside recess | 1 | 70 | MELTEC, PWB Encoders, Laser Lab or Optry Tech | quote | ❓ **thickness and substrate unsourced; 0.15 mm assumed** |
| `DRV2605L` | Haptic driver, I²C address 0x5A | 1 | 70 | TI | $1.22 @100 | ✅ |
| `VLV101040A` | Linear resonant actuator, 10 × 10 × 4 mm, 170 Hz | 1 | 70 | Vybronics | ~$5 | ✅ **must not be soldered — spring contacts only** |
| `SN74AHCT1G125DBVR` | 5 V level shifter for the halo data line | 1 | 70 | TI | <£1 | ✅ must be HCT or AHCT, not HC/AHC |
| `USBLC6-2SC6` | USB port protection | 1 | 70 | ST | <£1 | ✅ |
| `MAX98357A` | Class-D amplifier for the notification speaker | 1 | 70 | Analog Devices | £1.30 @100 | ⏳ **which board carries it is unresolved — not the audio board** |
| `INA240A1` + 50 mΩ 2512 | In-line current sense, **footprints only, do not fit** | 0 | 10 | TI / Susumu | — | ✅ 0 Ω links fitted instead |

## 7 · Motor and mechanism

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Gimbal motor, 2804 frame | Drives the knob's bore through a silicone band and renders the detents | 1 | 70 | JD-Power MY-3514C, or a generic 2804/2805 | £8–56 | ⏳ **almost nothing published — buy three now and measure them.** The MY-3514C is £56 and its hollow shaft is inherited from the old centre-mounted layout; the motor is now off-axis with nothing passing through it, so test whether a generic gimbal motor qualifies |
| Silicone friction band | ~0.6 × 8 mm, Shore 40–70, stretched onto the bell | 1 | 100 | — | <£1 | ❓ hardness chosen on the bench |
| 1.5 g linear servo | Clutch actuator. **2.4 mm of travel is all the mechanism needs**; the 2.4 N figure is the AGFRC's published output, not a measured requirement | 1 | 70 | see note | £8–47 | ⏳ **AGFRC C1.5CLS PRO is £47 and is the premium badge on a commodity class.** Spektrum SPMAS2000 £11.95, Hobbypower/Flash Hobby GS-1502 cheaper. Buy all three and measure the force the clutch actually needs |
| `623ZZ` | Wheel bearing, 3 × 10 × 4 | 3 | 200 | Simply Bearings | £1.92 @99 | ✅ |
| V-collar | Turned, pressed onto the bearing | 3 | 200 | knob machinist | quote | ⏳ POM in production |
| Eccentric bush | Turned brass, sets wheel preload | 3 | 200 | knob machinist | quote | ⏳ |

## 8 · Halo and light

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Addressable LED strip | 5 mm wide, ~100 LEDs per metre, WS2812B-2020 or SK6812 class, adhesive backed. **≈53 LEDs per unit** — recompute from the strip radius as built | ~0.55 m | 40 m | LCSC or a strip house | ~£3 per metre | ⏳ **buy two candidate strips and bench-test before committing.** One reel and one date code for the whole run |
| Opal diffuser ring | Perspex 1TL1 (36 %) or 1TL2 (48 %), cut to the L-section | 1 | 70 | Simply Plastics | £3–8 | ⏳ printed PETG for prototypes only |

## 9 · Enclosure

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Knob | One-piece CNC 6082-T6 cup, milled diamond pattern, V-groove in the bore, code-ring recess in the crown | 1 | 65 | JLCCNC, Xometry UK, Hubs UK, Penta Precision | quote | ⏳ groove-to-bore concentricity 0.05 total — say so on the request |
| Knob finish | Bead blast, Type II matte black anodise | 1 | 65 | Parallel Precision | £4 @50, £2.80 @100 | ✅ |
| Knob bright chamfer | Diamond-cut after anodise, second setup, then protection | 1 | 65 | machining shop | quote | ⏳ sample lacquer and clear anodise on two parts first |
| Base plate, aluminium core | 6082, ducted: 2 mm web with local thickening at every tapped hole, 3 × 5 mm fin channels, top-face ribs, Ø7 piers under the top screws | 1 | 65 | CNC shop | quote | ⏳ 341 g as built |
| Base plate finish | **Black hard anodise external faces only. Internal faces chromate conversion or bare** | 1 | 65 | anodiser | quote | ✅ no masking required |
| Closing plate | 1 mm, closes the duct, outer face black anodised, 9 screws | 1 | 65 | CNC or laser | quote | ✅ |
| Duct gasket | 0.2 mm, between the closing plate and the plate core | 1 | 70 | die-cut | ~£1 | ⏳ material to choose |
| Stainless rim ring | Outer band, 8 mm tall × 8 mm thick, ~205 g. **92 obround openings 2.0 × 4.5** (64 intake, 28 exhaust), 0.3 mm polished chamfer at every opening, **no reeding** | 1 | 65 | CNC | quote | ⏳ **brushed axially.** Bond screw needs bare metal or a star washer that cuts through |
| Rubber pad | Ring, non-marking, adhesive backed. Natural rubber or nitrile, not silicone | 1 | 70 | Delta Rubber | £2–5 | ✅ no tooling, no minimum |

## 10 · Power

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Mains supply | **12 V, 5 A, Class II two-pin, double insulated.** Require the touch-current / leakage figure on the datasheet | 1 | 65 | Mean Well, XP Power or similar | £15–25 | ❓ **part not chosen** |
| `PJ-063AH` | Barrel inlet, 5.5 × 2.1 mm, right angle | 1 | 70 | CUI / Same Sky | ~£1 | ⏳ fetch the CAD model |
| 12 V → 5 V converter | ~7 A. Bought module for prototypes; on the carrier for production | 1 | 70 | — | £5–10 | ⏳ **check the derating curve — a module rated 10 A is rated 10 A with airflow** |
| `BFB0305HA-C` | Radial blower, 30 × 30 × 10 mm, 0.68 L/s free air, 71 Pa. **Required and fitted** | 1 | 70 | Delta | ~£10 | ✅ mounts on the plate under the motion board's saddle |
| Thermal gap pads | Under the compute module boss, the converter and the motor driver | 3 | 250 | Bergquist or similar | ~£1 | ✅ |

## 11 · Connectors, cable and harness

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Pico-Lock 1.50, right angle | **The connector family for every crimped joint.** 2.00 mm mated, 30 mating cycles, AWG 24–28, 2–6 A, positive lock. Circuit counts follow the interface list | ~18 | — | Molex | ~£0.50 ea | ✅ exact part numbers once the interface list is fixed |
| Internal USB assemblies | Pre-made twisted pair, under 150 mm, hub to audio and hub to motion | 2 | 150 | harness house | quote | ⏳ **not a crimped connector — a crimp and a loose wire is not a 90 Ω transmission line** |
| Wiring harness | ~20 assemblies. One runs to the moving carriage and needs flex-rated cable | 1 set | 65 | harness house | quote | ❓ **have it made. Hand-crimping is where solo builds go wrong** |
| Spring contacts | Pogo pins for the vibration actuator, on their own small board in a clip | 2 | 150 | Mill-Max | ~£1 | ✅ |
| Knob bleed contact | Sprung phosphor-bronze leaf or spring pin, plus a 1 MΩ resistor | 1 | 70 | — | <£1 | ❓ form and mounting not designed |
| USB-C cable | Detachable, braided, right angle | 1 | 70 | ByteCable / WJW custom, MOQ 100 | $1.30–2.80 | ⏳ or an Anker retail cable at ~£12 |

## 12 · Fasteners and small parts

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| M3 countersunk + heat-set inserts | Plate to pillars | 8 | 700 | Accu / Ruthex | — | ✅ |
| M2.5 screws and nuts | Boards | ~16 | 1,200 | Accu | — | ✅ |
| M2 screws | Port face rail | 2 | 200 | Accu | — | ✅ |
| External-tooth star washers | Chassis bond and rim-ring bond | 2 | 200 | any | — | ✅ |
| Grub screws | Lock the eccentric bushes | 3 | 250 | Accu | — | ✅ |
| Ø2 m6 × 8 dowel pins | Display centring, in bosses under the seat flange | 3 | 250 | Accu | — | ✅ |
| M2 × 18 | Blower saddle through-bolts | 2 | 200 | Accu | — | ✅ |
| Display bonding tape | 0.5 mm double-sided foam, under the glass edge | 1 | 70 | 3M | — | ✅ |
| Thread lock | For the bonding screws | — | 1 | Loctite | — | ✅ |

**No screws anywhere on the knob.**

## 13 · Packaging

| Part | Description | Per unit | Buy | Supplier | Price | Status |
|---|---|---|---|---|---|---|
| Rigid box, insert, certificate | Black, magnetic closure, foil or blind deboss, foam or pulp insert | 1 | 120 | Packhelp (MOQ 120) or Tiny Box Company | £6–16 all in | ⏳ **re-quote at the current diameter.** Foil or deboss block £50–150 one-off |

## 14 · Prototype and bench only — do not order in quantity

| Part | Description | Qty | Supplier | Price |
|---|---|---|---|---|
| Raspberry Pi 5 | Development machine, same processor and software as the compute module | 1 | The Pi Hut | £62.40 for 2 GB |
| `DM-ADTTR-014` | HDMI-to-display adapter kit — driver board, 150 mm flat cable, display connect board | 1 | DisplayModule | $99 |
| Waveshare 5 in HDMI round touch display | Bench display, 150 × 150 × 7 mm — cannot be enclosed | 1 | Waveshare | £124.80 inc VAT |
| Compute module + official IO board + powered hub | For the gadget-mode and flashing bench test | 1 set | Pi Hut | ~£200 |
| `TMC6300-BOB` | Motor driver breakout, to start the motor work without a board | 1 | Newark 70AH6601 | ~£30 |
| SmartKnob development kit | Hand-feel benchmark | 1 | SeedLabs | ~£100 |
| `XA-XTAG4` | XMOS 1.8 V debug adapter — older 3.3 V adapters will not work | 1 | XMOS | ~$28 |

---

## Deleted — do not buy

The Waveshare ESP32-P4 board · detent magnets and the sixty steel balls · the brass mass ring · the magnet carrier gearmotor · the ring motor, drive tyre and solenoid · the headphone amplifier stage · **the supercapacitors** (the Abracon part cannot supply the current; the Eaton replacement does not fit the cavity) · **the custom flexible LED ring** (a bought strip replaces it) · the steel base plate.

## Roll-up

| | Low £ | High £ |
|---|---|---|
| Bought parts and made boards, per unit, landed, ex-VAT | **≈ 400** | **≈ 780** |

Middle of the range with a Chinese knob: **roughly £500–580 per unit.** Not a quote.

**Excluded:** board layout contract (£4,000–8,000 one-off), assembly labour, and compliance testing (£6,000–12,000 plus a retest — see `docs/SYSTEM-REVIEW.md` 4.2).

## Cannot be ordered until specified

The cover lens and touch sensor · the panel's rails and backlight driver · the mains supply · the code ring · the wiring harness · the knob's bleed contact · the six small boards · which board carries the speaker amplifier · the duct gasket material.
