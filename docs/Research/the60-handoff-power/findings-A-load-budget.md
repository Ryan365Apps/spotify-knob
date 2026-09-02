# The 60 — Findings A: the load budget, honestly

Every electrical consumer in the 60, with typical and worst-case current referred to the 5 V input rail. Each figure is either read from a datasheet or vendor page (URL given) or is explicitly marked **[EST]** — an estimate with its assumptions stated. Findings first; assessment is at the end and is kept separate.

Date of research: 2026-09-02. All web sources fetched on that date.

## 0. Method and conversion assumptions

- The design assumption under test: one USB (Universal Serial Bus) Type-C cable, 5 V / 500 mA = 2.5 W. Comparison points: 4.5 W (5 V / 0.9 A, USB 3.x), 7.5 W (5 V / 1.5 A, USB-C default), 15 W (5 V / 3 A, USB-C rated cable). 15 W is the ceiling at 5 V; anything above requires USB PD (Power Delivery) voltage negotiation to 9 V or higher plus local conversion.
- **[EST] Rail conversion:** loads on the 3.3 V rail (the two Espressif chips, codec, touch, panel logic) are converted to 5 V input power as P(5 V) = 3.3 V × I(3.3 V) / 0.85, assuming an 85 % efficient buck converter. The Waveshare schematic has not been read for this document; if the 3.3 V rail is a linear regulator instead, those line items rise ~28 % (a linear regulator draws the same current at 5 V as the load draws at 3.3 V).
- Loads assumed to sit directly on 5 V: SK6812 halo LEDs (datasheet supply 3.5–5.5 V), NS4150B speaker amplifier (5 V operation per its datasheet), DRV2605L haptic driver (2.5–5.2 V supply range), N20 gearmotor (5–6 V variants), custom ring motor coils, AEDR-8300 optical encoder (4.5–5.5 V).
- "Peak" means instantaneous worst case at 100 % duty; averages state their duty-cycle assumption inline.

## 1. Consumer-by-consumer table

| # | Consumer | Condition | Current at stated rail | At 5 V input | Source |
|---|----------|-----------|------------------------|--------------|--------|
| 1a | ESP32-P4 (main processor, dual-core RISC-V) | Active 360 MHz, dual core running 32-bit data access, all peripheral clocks enabled (typ2 column) | 123 mA @ 3.3 V | ~478 mW / 96 mA **[EST conversion]** | [ESP32-P4 Series Datasheet v1.2, Table 5-7](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_datasheet_en.pdf) |
| 1b | ESP32-P4 | Active 360 MHz, same load, peripheral clocks disabled (typ1) | 92 mA @ 3.3 V | ~357 mW / 71 mA | same |
| 1c | ESP32-P4 | Idle (WAITI, dual core idle) at 90 MHz | 28–44 mA @ 3.3 V | ~109–171 mW | same |
| 1d | ESP32-P4 | Light-sleep, all supplies enabled | 3.5 mA @ 3.3 V | ~14 mW | same, Table 5-8 |
| 2a | ESP32-C6 (Wi-Fi 6 / Bluetooth co-processor) | Wi-Fi TX peak, 802.11b 1 Mbps @ 21 dBm, 100 % duty | 354 mA @ 3.3 V | ~1 374 mW / 275 mA | [ESP32-C6 Series Datasheet v1.5, Table 5-7](https://documentation.espressif.com/esp32-c6_datasheet_en.pdf) |
| 2b | ESP32-C6 | Wi-Fi TX peak, 802.11ax MCS9 @ 16.5 dBm | 252 mA @ 3.3 V | ~978 mW | same |
| 2c | ESP32-C6 | Wi-Fi RX / listen | 78–82 mA @ 3.3 V | ~303–318 mW | same |
| 2d | ESP32-C6 | Modem-sleep (Wi-Fi clock-gated), CPU idle, 80–160 MHz | 14–17 mA @ 3.3 V | ~54–66 mW | same, Table 5-10 |
| 2e | ESP32-C6 | Light-sleep | 180 µA @ 3.3 V | ~0.7 mW | same, Table 5-11 |
| 2f | Waveshare board total | — | **not published** | — | [Waveshare wiki, ESP32-P4-WIFI6-Touch-LCD-3.4C](https://www.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-3.4C) — no board-level consumption figure anywhere on the wiki or product page |
| 3a | 3.4-inch 800×800 backlight, 100 % | **[EST]** scaled by active area from the 8-inch panel below | ~100–150 mA @ 5 V | ~500–750 mW (use 600 mW) | scaling basis: [Waveshare 8inch DSI LCD (C) wiki FAQ](https://www.waveshare.com/wiki/8inch_DSI_LCD_(C)): "working current of the backlight on is about 520 mA, backlight off about 150 mA" at 5 V → backlight ≈ 370 mA for ~185 cm² of 8-inch 16:10 panel; 3.4-inch round active area ≈ 58.6 cm² → 370 mA × 0.32 ≈ 118 mA. Assumes similar luminance (the 3.4C panel is 300 cd/m² per the [3.4inch DSI LCD (C) wiki FAQ](https://www.waveshare.com/wiki/3.4inch_DSI_LCD_(C)); 8-inch luminance unpublished) and similar backlight efficiency |
| 3b | Backlight 50 % | **[EST]** linear with PWM (pulse-width modulation) duty | ~60 mA @ 5 V | ~300 mW | assumption stated |
| 3c | Backlight 20 % | **[EST]** same linearity assumption | ~24 mA @ 5 V | ~120 mW | assumption stated |
| 3d | Panel logic + MIPI DSI (display serial interface) driver, backlight off | **[EST]** the 8-inch panel draws 150 mA @ 5 V with backlight off; a 3.4-inch panel's driver will be less but not proportionally | ~40–80 mA @ 5 V | ~200–400 mW (use 300 mW) | scaling basis as 3a; marked estimate |
| 4a | GT9271 touch controller (10-point capacitive) | Normal (touching/scanning) | 13 mA @ 2.8 V | ~43 mW **[EST conversion]** | [Goodix GT9271 datasheet §10.4](https://focuslcds.com/content/GT9271.pdf): normal 13 mA, green (idle) 4.5 mA, gesture 1.2 mA, sleep 70–120 µA, at AVDD = 2.8 V |
| 4b | GT9271 | Green mode (no touch) | 4.5 mA @ 2.8 V | ~15 mW | same |
| 5a | ES8311 mono audio codec | Normal operation (DC characteristics; DVDD 1.8 V, AVDD 3.3 V) | 8 mA typ | ~31 mW **[EST conversion]** (datasheet also claims "14 mW playback and record" as a feature) | [ES8311 datasheet](https://files.waveshare.com/wiki/common/ES8311.DS.pdf) |
| 5b | NS4150B class-D speaker amplifier driving 8 Ω at 2 W electrical | 90 % class-D efficiency (datasheet: "3 W output at 5 V / 4 Ω with 90 % efficiency; >90 % at normal levels") → rail power = 2 W / 0.90 | ~444 mA @ 5 V | ~2 222 mW | [NS4150 datasheet](https://aitendo3.sakura.ne.jp/aitendo_data/product_img/ic/power_amp/NS4150/NS4150.pdf); amp identity from the [Waveshare wiki](https://www.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-3.4C) ("integrates the es8311 codec chip and the NS4150B power amplifier chip") |
| 5c | Same amp at ringer level, 0.5 W electrical into the speaker | 0.5 W / 0.90 | ~111 mA @ 5 V | ~556 mW continuous; ~278 mW at a 50 % ring-cadence duty **[EST duty]** | same |
| 5d | Physics note on "2 W" | A bridge-tied class-D output from a 5 V rail into 8 Ω clips at ≈ 5²/(2×8) ≈ 1.56 W continuous sine (more with distortion). The "8 Ω 2 W speaker" on the wiki is the speaker's rating, not deliverable power | — | — | computed from V²/R; wiki wording: "PH 2.0 2P connector supporting 8Ω 2W speakers (recommended)" |
| 6 | ES7210 four-channel echo-cancellation ADC (analogue-to-digital converter) + 2 microphones | Normal recording, Fs = 16 kHz, AVDD 3.3 V: 63 mW; power-down 10 µA. Mics: **[EST]** ~0.5 mA each for analogue MEMS (micro-electro-mechanical systems) mics, part unpublished | 63 mW + ~3 mW | ~78 mW | [ES7210 datasheet, DC characteristics](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/6/7563.ES7210.pdf) |
| 7a | DRV2605L haptic driver | Standby 4.1 µA; quiescent (enabled, no signal) 0.5 mA; average no-load LRA drive 2.4 mA | small | ~3–12 mW | [TI DRV2605L datasheet §6.5](https://www.ti.com/lit/ds/symlink/drv2605l.pdf) |
| 7b | LRA (linear resonant actuator), 8 mm coin, Vybronics VG0832013D | Rated 1.8 Vrms @ 235 Hz; typical 58 mA, max 80 mA | 58–80 mA at the actuator | ~290–400 mW **[EST]** treating rail draw ≈ load current × 5 V (conservative for the DRV2605L's switched output stage) | [Vybronics VG0832013D page](https://www.vybronics.com/coin-vibration-motors/lra/v-g0832013d) |
| 8a | N20 gearmotor (cam / magnet-carrier lift), Pololu micro metal gearmotor 6 V HP (high-power), e.g. 50:1 | Stall 1.6 A; no-load 100 mA | 1.6 A stall | 8 000 mW stall / 500 mW no-load | [Pololu micro metal gearmotors category](https://www.pololu.com/category/60/micro-metal-gearmotors) |
| 8b | Same, 6 V MP (medium-power), e.g. 75:1 | Stall 0.67 A; no-load 70 mA | — | 3 350 mW stall / 350 mW no-load | same |
| 8c | Same, 6 V LP (low-power), e.g. 100:1 | Stall 0.36 A; no-load 40 mA | — | 1 800 mW stall / 200 mW no-load | same |
| 9 | Custom ring motor cancelling the detent continuously | **[EST — see §2 working]** 60 mNm: ~1.4 W (very good motor) to ~9–36 W (plausible-to-poor); 150 mNm: ~9 W (very good) to >50 W | see §2 | **1.4 W is the floor, not the expectation** | first-principles estimate anchored on Maxon and iPower catalogue motors, §2 |
| 10 | AEDR-8300 reflective optical encoder | Detector supply 2.2 mA typ / 5.0 mA max + LED 15 mA (13–18 mA range), all at 5 V | 17 mA typ / 23 mA max | 86 mW typ / 115 mW max | [Broadcom/Avago AEDR-8300 datasheet](https://download.mikroe.com/documents/datasheets/AEDR-8300%20Series%20Encoders.pdf), Recommended Operating Conditions + Electrical Characteristics |
| 11a | SK6812 RGBW LED, per LED, all four channels (R+G+B+W) full on | ~80 mA per LED at 5 V. The OPSCO datasheet publishes no per-channel current table (its graphs show ~15–20 mA-class channels); the 80 mA all-on figure is Adafruit's, i.e. 4 × ~20 mA/channel. White alone ≈ ~20 mA **[EST from 80/4]** | 80 mA/LED | 400 mW/LED | [SK6812RGBW datasheet (OPSCO, via Adafruit)](https://cdn-shop.adafruit.com/product-files/2757/p2757_SK6812RGBW_REV01.pdf); [Adafruit NeoPixel Überguide, powering section](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels) ("RGBW NeoPixels… may draw closer to 80 mA each") |
| 11b | SK6812 RGBW static (data idle, LEDs dark) | 1 mA per LED ("static power consumption IDD 1 mA typ") | 19–30 mA for the halo | 95–150 mW | OPSCO datasheet §8 |
| 12 | CS43131-class headphone DAC (digital-to-analogue converter) stage | Device ~23 mW (playback; design brief figure 26–40 mW) + headphone load ≤ 125 mW electrical | — | ~165–200 mW worst; ~60–100 mW typical listening **[EST]** | [Cirrus Logic CS43131 datasheet](https://statics.cirrus.com/pubs/proDatasheet/CS43131_DS1155F2.pdf) (23 mW playback; >30 mW into 32 Ω per channel capability); load figure from the design brief |

Halo LED counts over the 320 mm / 324° arc: **60 LEDs/m → 19 LEDs**; **96 LEDs/m → 30 LEDs** (0.32 m × density, rounded down).

| Halo scenario | 19 LEDs (60/m) | 30 LEDs (96/m) |
|---|---|---|
| 100 % all-channel white (R+G+B+W), 80 mA/LED | 1.52 A = 7.6 W | 2.40 A = 12.0 W |
| 50 % brightness, all-channel white | 0.76 A = 3.8 W | 1.20 A = 6.0 W |
| 20 % brightness, all-channel white | 0.30 A = 1.5 W | 0.48 A = 2.4 W |
| 100 % W-channel-only white (~20 mA/LED **[EST]**) | 0.38 A = 1.9 W | 0.60 A = 3.0 W |
| Dark (static IDD only) | 19 mA = 0.10 W | 30 mA = 0.15 W |

Brightness scaling assumption: SK6812 dims by PWM, so average current scales linearly with the 0–255 channel value. "White" can be commanded two ways; the W-only row is the sane one for a white halo and is 4× cheaper.

## 2. Ring motor estimate — the working, all of it

**What is being estimated.** The custom ring motor (coils on the stator acting on sixty steel poles in the bezel) must produce 60–150 mNm continuously to cancel the magnetic detent while a finger rests on a touch hotspot. Nothing about this motor exists yet; per the decision index `docs/DECISIONS.md`, nothing is bought until the bench rig measures real torque. So this is first-principles, anchored to catalogue motors.

**Framework.** For any wound motor, copper loss is P = I²R with I = T / Kt (T torque, Kt torque constant). Combine into the motor constant Km = Kt / √R, giving **P = (T / Km)²**. Km captures how much torque a motor makes per √watt of heat and is the honest single figure of merit.

**Catalogue anchors (published figures):**

| Motor | Kt | R (phase-to-phase) | Km | Notes |
|---|---|---|---|---|
| Maxon EC 90 flat, 90 W, part 244879 (48 V winding) | 217 mNm/A | 2.30 Ω | ≈ 143 mNm/√W | Ø90 mm, 648 g, iron-cored, permanent-magnet rotor. [Maxon EC 90 flat catalogue sheet](https://mat.transtechnik.fr/LINMOT/documentation/Moteurs/EC%20Motors/Maxon%20-%20EC_90_flat_244879.pdf) |
| Maxon EC 90 flat, part 323772 (24 V winding) | 70.5 mNm/A | 0.363 Ω | ≈ 117 mNm/√W | same sheet |
| iPower GM4108H-120T gimbal motor | **[EST]** implied 78–118 mNm/A (vendor: load torque 1 200–1 800 g·cm = 118–177 mNm at 1.5 A load current) | 11.1 Ω ± 5 % | ≈ 24–35 mNm/√W | Ø47 mm permanent-magnet gimbal motor. [iFlight product page](https://shop.iflight.com/gimbal-motors-cat44/ipower-motor-gm4108h-120t-brushless-gimbal-motor-pro217) |

**Assumptions for the 60's ring motor, each marked:**
- **[A1]** Coil circle radius ~60 mm (Ø120 mm), so 60 mNm = 1.0 N tangential force and 150 mNm = 2.5 N. The large radius is the one thing in this design's favour — force requirements are modest.
- **[A2]** The rotor has **no magnets** — only sixty steel poles (grub screws). That makes this a variable-reluctance actuator. Reluctance machines produce materially less torque per amp than permanent-magnet machines of the same size, and their torque goes roughly with I², so the linear I = T/Kt model used here is *generous* at these currents.
- **[A3]** The package is thin (inside a 34 mm-tall dial with the display in the middle), so copper cross-section and iron return path are both constrained — copper fill far below the 648 g Maxon flat motor.
- **[A4]** Assumed Km range for a competently built thin reluctance ring at this diameter: **10–50 mNm/√W**. Justification: a Ø47 mm *permanent-magnet* gimbal motor manages 24–35 mNm/√W; the 60's ring is ~2.5× the radius (helps linearly) but gives up rotor magnets (hurts by an estimated 2–5× on force per amp) and copper volume. The Maxon's 117–143 mNm/√W is what a dense, iron-cored, magnet-rotor design buys and is quoted as an unreachable upper bound in this envelope.

**Resulting continuous coil dissipation, P = (T/Km)²:**

| Km assumption | 60 mNm detent | 100 mNm | 150 mNm detent |
|---|---|---|---|
| 50 mNm/√W (very good outcome) | 1.4 W | 4.0 W | 9.0 W |
| 30 mNm/√W (gimbal-motor-class, plausible) | 4.0 W | 11.1 W | 25.0 W |
| 10 mNm/√W (poor but possible for thin air-gap reluctance) | 36 W | 100 W | 225 W |
| 117 mNm/√W (Maxon-class bound, not achievable here) | 0.26 W | 0.73 W | 1.6 W |

**Plausible range, stated as a range:** cancelling a 60 mNm detent continuously costs **≈ 1.4–36 W of coil heat, most plausibly 2–10 W**; cancelling 150 mNm costs **≈ 9 W at best, most plausibly 25 W or more**. Every number in this subsection is an estimate; only the three anchor rows are published figures.

## 3. Scenario sums

All figures are 5 V-input milliwatts; conversion assumptions from §0 apply.

### (a) Idle on the desk

Assumptions: screen dimmed to 20 % backlight; Wi-Fi associated but in modem-sleep; halo dark (static IDD only, 19-LED build); touch in green mode; audio path and ES7210 powered down; both motors off; encoder LED gated off by firmware (add 86 mW if not gated); board overhead (regulators' own draw, flash, misc) is an estimate.

| Line item | mW at 5 V |
|---|---|
| ESP32-P4, WAITI idle 90 MHz | 140 **[EST mid of 109–171]** |
| ESP32-C6, modem-sleep | 60 |
| Panel logic + MIPI driver | 300 **[EST]** |
| Backlight 20 % | 120 **[EST]** |
| GT9271 green mode | 15 |
| Halo static (19 LEDs) | 95 |
| ES8311 idle | 5 **[EST]** |
| Board overhead | 100 **[EST]** |
| **Total** | **≈ 0.84 W** |

Fits 2.5 W: **yes** (3× headroom). Fits 4.5 / 7.5 / 15 W: yes.

### (b) Scrolling with the detent cancelled

Assumptions: screen at 100 %; ESP32-P4 fully active (worst typ2 column); Wi-Fi in modem-sleep (scrolling is local; sync bursts ignored in the average); encoder on; touch normal; halo dark; speaker off; ring motor cancelling continuously.

| Line item | mW at 5 V |
|---|---|
| ESP32-P4, active 360 MHz (typ2) | 478 |
| ESP32-C6, modem-sleep | 60 |
| Panel logic + MIPI driver | 300 **[EST]** |
| Backlight 100 % | 600 **[EST]** |
| GT9271 normal | 43 |
| AEDR-8300 encoder | 86 |
| Halo static (19 LEDs) | 95 |
| Board overhead | 100 **[EST]** |
| **Subtotal, motor off** | **≈ 1.76 W** |
| + ring motor, 60 mNm, Km = 50 (best case) | +1 440 → **≈ 3.2 W** |
| + ring motor, 60 mNm, Km = 30 (plausible) | +4 000 → **≈ 5.8 W** |
| + ring motor, 150 mNm, Km = 50 (best case) | +9 000 → **≈ 10.8 W** |
| + ring motor, 150 mNm, Km = 30 (plausible) | +25 000 → **≈ 26.8 W** |

Fits 2.5 W: **no in every motor case**. Fits 4.5 W: only the 60 mNm best case, marginally. Fits 7.5 W: 60 mNm cases yes; 150 mNm no. Fits 15 W: 150 mNm only with a near-best-case motor; the plausible 150 mNm case fits nothing.

### (c) Call ringing

Assumptions: screen at 100 %; halo pulsing all-channel white at 50 % brightness with a 50 % pulse duty (a pulsing halo is not 100 % duty — stated); LRA pulsing at 50 % duty at max drive; speaker at ringer level 0.5 W electrical with a 50 % ring-cadence duty; ESP32-C6 in continuous RX for signalling (TX bursts excluded from the average, included in the peak); ESP32-P4 active; ES7210 + microphones live; encoder off; motors off; 19-LED halo (30-LED variant in parentheses).

| Line item | avg mW at 5 V | peak mW |
|---|---|---|
| ESP32-P4, active (typ2) | 478 | 478 |
| ESP32-C6, Wi-Fi RX (peak: 802.11b TX burst) | 303 | 1 374 |
| Panel logic + MIPI driver | 300 **[EST]** | 300 |
| Backlight 100 % | 600 **[EST]** | 600 |
| GT9271 normal | 43 | 43 |
| Halo pulse, 50 % bright × 50 % duty, all-channel white | 1 900 (3 000) | 3 800 (6 000) |
| LRA + DRV2605L, 50 % duty | 210 | 410 |
| Speaker ringer 0.5 W × 50 % duty (NS4150B, 90 % eff.) | 278 | 556 |
| ES8311 codec | 31 | 31 |
| ES7210 + mics | 78 | 78 |
| Board overhead | 100 **[EST]** | 100 |
| **Total** | **≈ 4.3 W (5.4 W at 30 LEDs)** | **≈ 7.8 W (10.0 W)** |

Fits 2.5 W: **no**. Fits 4.5 W: 19-LED build sits exactly at the line — no margin, and the 7.8 W coincident peak will brown out a 4.5 W source unless bulk capacitance rides it. Fits 7.5 W: average yes, peak marginal. Fits 15 W: yes. Cheap fix visible in the data: pulse the W channel only (halo line drops ~4×; average total → ≈ 2.9 W).

### (d) Everything at once (true worst case, no firmware limits)

Assumptions: 30-LED halo at 100 % all-channel white; ring motor cancelling 150 mNm at the *best-case* Km = 50; N20 HP variant at stall (cam jammed); speaker at 2 W electrical; LRA at max; Wi-Fi TX peak (802.11b); everything else at maximum. A fault-coincidence case, not an operating point.

| Line item | mW at 5 V |
|---|---|
| ESP32-P4 active (typ2) | 478 |
| ESP32-C6 Wi-Fi TX peak | 1 374 |
| Panel logic + backlight 100 % | 900 **[EST]** |
| GT9271 normal | 43 |
| Halo, 30 LEDs, 100 % all-channel white | 12 000 |
| Ring motor, 150 mNm, best-case Km = 50 (**plausible case is 25 W**) | 9 000 **[EST]** |
| N20 HP stall | 8 000 |
| Speaker 2 W electrical (over the 8 Ω / 5 V clipping limit — §1 5d) | 2 222 |
| LRA + driver peak | 410 |
| AEDR-8300 encoder (max) | 115 |
| ES8311 + ES7210 + mics | 109 |
| CS43131 DAC stage worst | 200 |
| Board overhead | 100 **[EST]** |
| **Total** | **≈ 35 W** |

Fits 2.5 / 4.5 / 7.5 / 15 W: **no, no, no, no.** Even a trimmed "worst realistic" build (19 LEDs, W-only white ≈ 1.9 W, LP-variant N20 at 1.8 W stall, motor at 60 mNm best case 1.4 W, speaker at the 1.56 W clipping limit ≈ 1.7 W rail) sums to ≈ 9.5 W — inside 15 W only, and only because the motor was given its most optimistic number.

## Confidence and gaps

**High confidence (datasheet numbers, cited):** ESP32-P4 and ESP32-C6 currents; GT9271; ES8311; ES7210; DRV2605L; VG0832013D LRA; Pololu N20 stall/no-load; AEDR-8300; SK6812 static IDD; NS4150 3 W / 90 % @ 5 V / 4 Ω; CS43131 23 mW; Maxon EC 90 flat Kt/R; GM4108H-120T resistance.

**Medium confidence:** the 80 mA/LED SK6812 RGBW all-on figure (Adafruit's number, order-of-magnitude confirmed by the datasheet graphs, but OPSCO publishes no per-channel current table — worth one bench measurement); NS4150B-vs-NS4150 equivalence (the wiki names NS4150B; the fetched datasheet is NS4150); the 85 % rail-conversion assumption (schematic not read — if 3.3 V comes from a linear regulator, all 3.3 V items rise ~28 %).

**Low confidence / gaps, in order of how much they move the total:**
1. **Ring motor Km** — the whole budget swings 1.4 W ↔ 36 W on this one estimate. Only the bench rig (open questions A–F in the decision index `docs/DECISIONS.md`) resolves it. Reluctance-vs-permanent-magnet torque behaviour also makes the linear model generous.
2. **Backlight current** — pure area scaling from an 8-inch panel; Waveshare publishes nothing for the 3.4C board or its panel. One USB power-meter reading of the bare dev board (backlight 0 % vs 100 %) kills lines 3a–3d's uncertainty.
3. **Board overhead and panel logic** — estimates; the same single measurement fixes both.
4. **Wi-Fi duty cycles** — TX at 100 % duty never happens in practice; averages assume RX-dominant signalling, stated inline.
5. **N20 running current under cam load** — vendor gives stall and no-load only; the real lift current sits between, lasts seconds, at near-zero duty, so it barely matters except at stall-fault.

## Assessment (separate from findings)

1. **2.5 W (5 V / 500 mA) supports the idle state and nothing else.** Scenario (a) fits with 3× headroom; every interactive scenario breaks it. The current design assumption is wrong for this product as specified.
2. **The ring motor's continuous detent cancellation is the budget.** Everything else in the dial combined is ~1.8–4.3 W; the motor alone is plausibly 2–25 W. Continuous cancellation of the *upper* detent range (150 mNm) is not USB-feasible at 5 V under any honest estimate. Two design outs are visible: (i) spec the cancellable detent at the low end (≤ 60 mNm) and demand Km ≥ 50 mNm/√W from the bench rig before committing, or (ii) don't cancel magnetically — use the N20-driven magnet carrier to *lower the detent mechanically* when a finger rests on the hotspot, which costs ~0.35 W for a second instead of watts forever. That interacts with decision 19 (that dynamic detent strength comes from the motor) and needs a ruling, not a quiet workaround.
3. **Minimum sane power target is USB-C 5 V / 3 A (15 W) with firmware concurrency limits** (halo capped to W-only white during motor activity; speaker and motor never simultaneously at max; N20 stall detection). If the plausible-case motor is confirmed at the bench, even 15 W fails for 150 mNm and the product needs USB PD at 9 V or 12 V with a local buck — which also fixes the cable-I²R and connector-drop problems a 3 A draw at 5 V invites.
4. **Halo LED count is a power decision, not a cosmetic one.** 19 vs 30 LEDs is 7.6 W vs 12 W at worst; W-only white is 4× cheaper than all-channel white at the same brightness. Cap all-channel white in firmware.
