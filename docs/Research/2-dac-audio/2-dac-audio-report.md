# DAC and audio for the 60 — research report

Answer to the brief in `../2-dac-audio-RD.md`. Research date 2026-09-02. This document synthesises four findings files in this folder; every number below is cited in one of them (with URLs) or marked unverified / quote required here. The findings files are the evidence record:

- `findings-A-market.md` — market and competitor survey (33 sources)
- `findings-B1-usb-architecture.md` — ESP32-P4 native USB audio versus bridge chips
- `findings-B2-dac-amp.md` — DAC chip comparison, amplification, volume mapping
- `findings-C-power-practice.md` — power/noise engineering, established practice, measurement rig

Structure: findings first (sections 1–4), then the recommendation (section 5), risks and de-risking experiments (section 6), and a section for findings that touch existing project decisions (section 7). SINAD = signal-to-noise-and-distortion ratio, the single-number metric Audio Science Review (audiosciencereview.com) ranks devices by; restated here once, used freely below.

---

## 1. Findings: market and competitors (full detail: findings-A)

**The niche is empty.** No shipping product combines a premium physical dial with a measurement-grade DAC (digital-to-analogue converter) and headphone output in one desk object. The desk-controller category is plastic and DAC-less — Elgato Stream Deck + confirmed to have no audio jack (audio lives in software or a separate XLR Dock accessory); BEACN Mix Create is USB-C only, "pair it with external audio hardware"; Loupedeck Live S has no audio hardware. The DAC/amp category treats the knob as a control, not the object. The 60 would be first in its exact niche.

**The landscape it enters** (condensed from the findings-A table; all figures cited there):

| Product | Price (as seen) | SINAD | Power @ 32 Ω | Output impedance | Position |
|---|---|---|---|---|---|
| Apple USB-C dongle | US $9 | ~98 dB | (not published) | 0.9 Ω | The transparency floor of the whole market |
| FiiO K11 | US $129 | line out 108.6 dB; headphone ~97 dB | 520 mW SE | <1.2 Ω SE | The value benchmark |
| Topping DX3 Pro+ | US $199 | ≈117 dB | ~1.8 W (press claim) | 0.1 Ω | The measured norm at US $200 |
| Schiit Magni Unity | US $199 w/ DAC | amp strong; DAC ~110 dB DR | 2.5 W | <0.1 Ω | "Reluctantly recommended" — weak DAC beside a good amp |
| JDS Labs Element IV | US $549 | ~120 dB | 3 W | 0.22 Ω | **The closest comparable: a knob-led DAC/amp** |
| Chord Mojo 2 | US $650–799 | (graph-bound) | ~90 mW (approx.) | (n/s) | Premium price, modest power — still recommended |
| RME ADI-2 DAC FS | US $1,299 | ≈116 dB THD+N | (not captured) | (not captured) | The desk endgame with screen + knob |

**What reviewers punish:** one pattern dominates — a DAC section that measures below its price peers, next to otherwise good hardware (FiiO K5 Pro, Magni Unity, original iFi Zen DAC at ~100 dB). Reviewers forgive modest output power (the Mojo 2's ~90 mW into 32 Ω passes at US $799); they do not forgive a below-peer DAC. The Audioengine D1's 10 Ω output impedance is the cautionary tale on that metric.

**The bar the 60 must clear** (derived in findings-A from the cited landscape; targets, not measurements):

- SINAD ≥ 105 dB at 2 Vrms (honest minimum ≈ FiiO K11 line out at 108.6 dB; safe target ≥ 110 dB; chasing the Element IV's ~120 dB is unnecessary and unwinnable at this board size)
- Noise ≤ 5 µVrms A-weighted at minimum gain (sensitive in-ear monitors are the test every reviewer runs)
- Output impedance ≤ 1 Ω
- Output power: findings-A proposes ≥ 150–300 mW into 32 Ω and ≥ 30–60 mW into 300 Ω. **This target conflicts with the one-chip architecture — see section 5.3, which is the honest resolution, not a silent one.**
- **Ship a per-unit measurement sheet with each numbered unit.** Nobody in the knob category can; everybody in the DAC category expects it. Category-unique, and cheap once the rig from section 5.6 exists.

---

## 2. Findings: USB architecture (full detail: findings-B1)

**ESP32-P4 native USB audio is real but unproven where it matters.** Espressif's `usb_device_uac` component (v1.3.1) is UAC 2.0 (USB Audio Class 2.0), asynchronous isochronous with the explicit feedback endpoint Windows requires, and runs on the P4's 480 Mbit/s high-speed port. But:

- Espressif's own readme states the component "Cannot be compatible with both Windows and Linux simultaneously".
- It needed a descriptor fix as recently as March 2026 just to enumerate on Windows in a multichannel build; TinyUSB (the underlying stack) has a record of audio-composite regressions between releases.
- **No published SINAD, noise or jitter measurement of any ESP32-family UAC device exists anywhere.** The community evidence is "does it play", never metrological.

**Windows side:** Windows 10 1703+ and 11 handle UAC 2.0 with the in-box `usbaudio2.sys` driver — explicit-feedback-only, strict spec-literal descriptor parsing. No custom driver needed on either architecture.

**Bridge chips:** XMOS is the only franchised-stock option. The XU316 (current generation) was US $13.05 at 1 pc / US $9.21 at 100 pcs with 1,015 pcs at DigiKey on the research date (12-week manufacturer lead — recheck at commit); its maintained reference firmware (`lib_xua`) already implements audio + HID (human interface device) playback controls + DFU (device firmware upgrade) as one composite. Comtrue and Savitech parts are cheaper on paper but are grey-market, quote-required sourcing — the risk erases the saving at 60 units.

**One port, two functions:** a Microchip USB2422 2-port USB 2.0 hub (US $2.19 at 1 pc / US $1.41 at 100 pcs, LCSC) shares the USB-C connector: port 1 the audio device, port 2 the ESP32-P4's HID/CDC (virtual serial)/flashing. Standard practice in multi-function USB products.

**Jitter:** asynchronous mode wins and both candidate paths are asynchronous. Measured XMOS products show J-test sidebands below ≈ −130 dBFS (Topping D10s); the ESP32 path's real risk is not subtle jitter but Windows feedback-path breakage, whose failure mode is audible glitching.

---

## 3. Findings: DAC chip, amplification, volume (full detail: findings-B2)

**The ES9219 situation, verified at the datasheet:** the v1.2 ordering table lists only ES9219Q and ES9219MQ (the MQA-licensed variant); ES9219C is gone, confirming the sourcing document. But ES9219Q distributor supply looks thin — Mouser showed 0 pcs on the OEMsTrade snapshot (an earlier same-day snippet said 89 — volatile either way), with published pricing only at the 25/100 breaks ($10.56 / $9.91). Quantity-50/500 pricing: quote required.

**Chip shortlist** (condensed; full 11-chip table with rails, packages and sources in findings-B2):

| Chip | Datasheet claim | Headphone driver | Stock 2026-09-02 | Price near 50 / 500 | Measured record |
|---|---|---|---|---|---|
| **Cirrus CS43131** | −115 dB THD+N, 130 dB-A DR | Yes — ground-centred, 30 mW @ 32 Ω, impedance detection, Popguard | DigiKey 261 (Active) | $12.74 / $11.94 | **Deepest**: Moondrop Dawn, Tanchjim Space and the best-measured dongle class |
| ESS ES9219Q | −114 dB THD+N, 121–123 dB-A DNR | Yes — 2.0 Vrms, internal charge pumps, jack sense | Thin (0–89 at Mouser, volatile) | quote required | Qudelix 5K class (~93 dB SINAD @ 0.4 V measured) — a tier below the CS43131 dongles in shipped practice |
| Cirrus CS43198 | −115 dB THD+N, 130 dB-A DR | No — line out, needs discrete stage | Mouser 1,904 | $13.53 / $11.75 | Truthear SHIO (117 dB SINAD maker spec) |
| AKM AK4493S | −115 dB THD+N, 123 dB S/N | No | Mouser 2,825 | $6.64 / $5.68 | Topping E30 II (~118 dB SINAD measured) |
| ESS ES9038Q2M / ES9039Q2M | −120 dB THD+N class | No — needs op-amp I/V stage | 3,170 / 628 | ~$16 / ~$15 (@25–100) | Desktop DACs; performance lives in the external stage |
| TI PCM5102A | −93 dB THD+N | No — line only, 1 kΩ min load | >14,000 across distributors | $2.64 / $2.24 | Bench-mule / prototype part, not the product |

**Amplification:** the TPA6120A2 needs ±5 V to ±15 V rails — a boost-plus-inverter build the 25 × 25 mm footprint and shared 5 V budget do not want. The only discrete stage that fits gracefully is an OPA1622 on charge-pump rails behind a line-out DAC — a two-chip solution that must out-measure a one-chip part already rated at 130 dB-A, which the shipped-product evidence says it generally does not. Output impedance target < 1 Ω (NwAvGuy's 1/8th rule; every credible product in section 1 complies), delivered natively by the integrated drivers. Line-level from the same jack needs no switching: ground-centred, ≤ 1 Ω source, 2 Vrms full scale drives any line input as-is; add a high/low gain mode (1 V / 2 Vrms, as the Qudelix 5K does) for sensitive in-ears.

**Volume and the 60 detents** (arithmetic on verified figures): both leading chips step at 0.5 dB natively with hardware soft-ramp (the ES9219 interpolates each step through up to 64 sub-levels; the CS43131 has a programmable ramp). The mapping: **1 dB per detent, dB-linear — 0 dB at the top, −59 dB at the bottom, mute below** (decibel-linear is documented audio-taper practice, per Microsoft's Core Audio guidance). Fine mode at 0.5 dB per detent needs no interpolation. Sub-detent rotation quantises to the 0.5 dB grid and lets the chip's ramp smooth it — never synthesise finer steps with rapid register writes. One attenuator in the chain: the DAC's own digital volume (with the chip's automatic analogue-gain tracking — DRE on the ES9219, equivalent settings on the CS43131 — left enabled), owned by the dial; the USB host volume (which the wire carries at 1/256 dB resolution, verified in the USB-IF audio class spec) is reflected, not stacked.

---

## 4. Findings: power, noise, established practice (full detail: findings-C)

**Power:** well-measured USB DACs treat VBUS as raw input: pi filter → per-function LDO (low-dropout regulator) tree. TI TPS7A20-class (300 mA, 7 µVrms noise) is the right size here. The CS43131's VP supply accepts 3.0–5.25 V — filtered USB 5 V feeds it directly — and its internal charge pump makes the negative rail, so no discrete bipolar supply exists on the board at all.

**Grounding decides the outcome, not regulator choice.** Espressif's own ESP32 audio design guideline: per-domain ground planes (Wi-Fi, audio, motor, LEDs) joined at a single 0 Ω-resistor tie, motors on separated returns. The USB ground *is* the PC's mains earth (hifisonix) — bond the steel base to it once, at the connector, and design for that rather than against it. JDS Labs' measured warning that "even small changes to firmware like LED intensity can degrade benchmarks" makes the halo's PWM (pulse-width modulation) frequency and return routing an audio design input.

**The motor at 20 mm is survivable — there is an existence proof.** The LG G7 ThinQ put an ES9218-family DAC (one generation before ES9219) in a phone with a vibration motor and two radios and measured 105 dB SINAD on Audio Science Review's rig; the WiiM Pro Plus measures ~115 dB with Wi-Fi on the same small board. Coupling paths in danger order: shared supply (killed by the LDO tree), ground returns (killed by layout), magnetic near-field (killed by tiny output loop area — jack on the audio board, which the architecture already does). The steel base helps a little; if a shield is ever needed it is a small annealed mu-metal can, not the structure. The 60's structural advantage: the motor is silent except during turns, so the honest acceptance criterion is *idle noise floor identical with motor absent vs present, and no audible artefact during rotation* — a bench-measurable pass/fail.

**Practice checklist** (each item carries a verified example part or named implementation in findings-C): single-point grounding; jack tip-switch detection (Same Sky SJ-3524-SMT-TR, 14.5 × 6 × 5 mm, datasheet read in full — fits the 4 mm jack band comfortably in the 34 mm height); pop suppression via the chip's power-state ramping (Popguard on CS43131) verified at the bench rather than a relay; mute-on-unplug from the tip switch; short-circuit survival (chip current limiter — CS43131 limits at 120–160 mA); ESD protection (TI TPD2E001, 1.5 pF, ±8 kV IEC 61000-4-2 — check clamp headroom above the ±2.83 V signal peaks on the bench); DC-coupled ground-centred output, so no blocking capacitors, verified as "≤ a few mV DC at the jack across power states".

**Measurement methodology:** Audio Science Review measures on an Audio Precision APx555 (quote required; not needed). A credible rig the project can own: **E1DA Cosmos ADCiso Grade A** (~US $200–263 street; 128–129 dB(A) SNR, galvanically isolated USB — its own floor sits below anything the 60 produces) + **REW** and **Multitone** (both free) + 32 Ω / 300 Ω power resistors (at 2 Vrms they dissipate 125 mW and 13 mW — ordinary 5 W resistors). Total under ~US $300. The QuantAsylum QA403 (US $599) is the one-box step up if the bench must also test third-party gear. The E1DA-plus-REW combination is already normalised on Audio Science Review; publish the rig, level and load with every figure.

---

## 5. Recommendation (section D of the brief)

### 5.1 The architecture

**USB-C → Microchip USB2422 two-port hub → { port 1: XMOS XU316 running the UAC 2.0 asynchronous reference firmware → I²S (inter-IC sound) → Cirrus CS43131 → 3.5 mm jack; port 2: ESP32-P4 high-speed USB (HID media transport + CDC serial for the companion app and flashing) }.** The ESP32-P4 controls the CS43131 over I²C (volume from the dial, gain mode, mute) while the XU316 streams the audio.

Why this shape, in one paragraph each:

- **Bridge, not P4-native (confidence: high).** The product's audio must clear measurement scrutiny on Windows specifically. The only ESP32 UAC implementation carries a vendor-documented Windows/Linux mutual exclusivity, a 2026 Windows-enumeration bug history, and zero published measurements; the XMOS path is what the reference-class desk DACs ship and what Audio Science Review measures well, and its firmware already includes the HID transport keys and field update. The hub also isolates the audio function from application-firmware crashes and reflashes — a longevity argument that matches the 60's service strategy. The P4-native option is not dead: it deletes two chips and gets the timeboxed kill-or-keep experiment in section 6.
- **CS43131, not ES9219Q (confidence: medium-high; see section 7 — this touches a sourcing decision).** Same headline class (−115 dB THD+N, 130 dB-A dynamic range), but: VP runs straight off filtered USB 5 V; ground-centred output with impedance detection, pop suppression and a current limiter built in; 40-QFN hand-assembly-friendly package; DigiKey Active status with published 50/500 pricing; and the deepest record in exactly the well-measured USB-powered products the 60 will be compared against. The ES9219Q's shipped record (Qudelix-class, ~93 dB SINAD at 0.4 Vrms measured) is a tier lower and its distributor supply is thin with quantity pricing unpublished.
- **One chip, not DAC-plus-op-amp (confidence: medium).** The two-chip route (CS43198 + OPA1622 on charge-pump rails) buys output swing the rear-jack use case rarely needs, at the cost of board area the 25 × 25 mm footprint barely has, a second noise budget next to a motor, and a measured-product record that says two-chip builds usually land below the one-chip 130 dB-A parts. The trade this accepts is output power — addressed honestly in 5.3.

### 5.2 Parts list

| Function | Part | Package / size | Price (cited in findings) | Note |
|---|---|---|---|---|
| USB hub | Microchip USB2422 | QFN-24, 4 × 4 mm | US $2.19 @1 / $1.41 @100 (LCSC) | I²C-configurable descriptors |
| USB audio bridge | XMOS XU316-1024-QF60B-C24 | QF60 | US $13.05 @1 / $9.21 @100 (DigiKey) | + quad-SPI boot flash (small, price not captured) |
| DAC + headphone driver | Cirrus CS43131-CNZR | 40-QFN, 5 × 5 mm | US $12.74 @50 / $11.94 @500 (DigiKey) | I²S in, I²C control from ESP32-P4 |
| Analogue LDO | TI TPS7A20-class ×2 (1.8 V rails) | small | quote required | 7 µVrms, 300 mA class |
| Jack | Same Sky SJ-3524-SMT-TR | 14.5 × 6 × 5 mm | price not captured — quote required | Tip switch → ESP32-P4 GPIO for detect/mute |
| ESD | TI TPD2E001 | tiny | quote required | ±8 kV IEC 61000-4-2, 1.5 pF |
| VBUS filter | pi filter (L/ferrite + C), passives | — | negligible, quote required | Per findings-C practice |

**Rough audio-subsystem BOM (bill of materials) cost:** the named silicon with published prices sums to ≈ US $28 at qty ~50 and ≈ US $23 at qty ~500. LDOs, jack, ESD, flash and passives are quote-required; a complete figure needs those quotes and is **not** stated here as if known. This is the audio slice only — motor, display and main board live in `../../SOURCING-BOM.md`.

### 5.3 Expected measured numbers — and the power trade-off, stated plainly

Expected at the jack, based on the measured record of CS43131 implementations (these are expectations to be proven on the project's own bench, not claims):

- SINAD: 108–115 dB class (Tanchjim Space / Moondrop Dawn territory; distortion components in the best implementations sit below −130 dB)
- Noise: the sub-2 µVrms A-weighted class the best CS43131/CS43198 devices reach; target ≤ 5 µVrms worst case
- Output impedance: < 1 Ω (native)
- Output: 2.0 Vrms full scale (+1 dB mode); **30 mW into 32 Ω; ≈ 13 mW into 300 Ω** (2 Vrms arithmetic)

That last line under-shoots the market strand's proposed floor of 150–300 mW into 32 Ω and 30–60 mW into 300 Ω. The two strands genuinely disagree, and the resolution is a positioning judgement, not an engineering one: the same market survey shows the Chord Mojo 2 recommended at US $650–799 with ~90 mW into 32 Ω, notes that the owner of a 300 Ω flagship headphone already owns an amp, and finds that reviewers punish weak DACs, not modest power. A rear-of-base 3.5 mm jack whose SINAD, noise and output impedance are beyond reproach at 2 Vrms is defensible; a jack that hisses or measures 97 dB is not, at any power. **If the ruling is that the 60 must also drive 300 Ω flagships with authority (3–4 Vrms), the architecture changes to CS43198 + OPA1622 on ±5 V charge-pump rails (LM27762-class) — that decision should be taken before schematic capture, and it costs board area, one more noise budget, and the one-chip measured pedigree.** Recommendation: accept 2 Vrms; put the sentence "drives in-ears and 32–300 Ω headphones cleanly; flagship-headphone owners will prefer their dedicated amp" in the product's own copy before a reviewer writes it less kindly.

### 5.4 Power budget

Audio slice of the 5 V / 1.5 A budget, from cited figures: CS43131 playback draw ≈ 26–40 mW plus delivered load power (≤ 125 mW worst case) — call it ≤ 0.2 W. USB2422 hub: small (figure not captured — verify). **XU316 running the USB audio firmware: draw not captured this pass — the one unbounded line; verify from the XMOS reference design power figures before closing the budget (gap, section 6).** Even with a pessimistic few hundred mW for the XU316, audio fits comfortably inside a 1.5 A budget shared with display, motor and ESP32-P4; the constraint is noise routing, not amperes.

### 5.5 Board and layout commitments

From findings-C, the non-negotiables the 25 × 25 mm board inherits: per-domain grounds with one deliberate tie; motor return currents never crossing the audio ground reference; steel base bonded to USB ground once at the connector; jack on the audio board (tiny output loop); halo PWM frequency and routing treated as an audio variable; TVS clamp checked for distortion at signal level on the bench.

### 5.6 Measurement rig

Buy: E1DA Cosmos ADCiso Grade A (~US $260 street). Download: REW, Multitone (free). Build: switched 32 Ω / 300 Ω 5 W load board (cheap; quote required). This measures SINAD/THD+N, noise, dynamic range, frequency response, multitone and (via loaded/unloaded delta) output impedance the same way Audio Science Review's audience expects, for under ~US $300 — and it is the instrument behind the per-unit measurement sheet from section 1. Upgrade path if needed: QuantAsylum QA403, US $599.

---

## 6. Risks and de-risking experiments

| # | Risk | De-risk experiment (small, specific) |
|---|---|---|
| 1 | **ESP32-P4 native USB audio** — the least-trusted path; if it worked it would delete the hub and bridge (≈ US $11–15/unit and board area) | Timeboxed one week on hardware in hand: `usb_device_uac` v1.3.1, high-speed port, 48 kHz/16-bit and 96 kHz/24-bit builds, plus HID+CDC composite; Windows 11 in-box driver only. Measure: 50 replug/reboot enumerations, 24 h glitch soak via the section 5.6 ADC, SINAD at 1 kHz −3 dBFS with display/Wi-Fi/LED/motor active, 12 kHz J-test vs published Topping D10s plots. Kill criteria: unreliable composite enumeration, any soak glitch, or data-correlated sidebands above ≈ −110 dBFS, unfixed in the week. Full protocol in findings-B1 §5. |
| 2 | **Motor noise at 20 mm** — no published measurement of this exact configuration exists anywhere | On the bench rig: same output measured motor-absent, motor-present-idle, motor-turning. Acceptance: first two indistinguishable; no audible artefact in the third. (Also the marketing measurement nobody else can publish.) |
| 3 | **CS43131 supply** — DigiKey 261 pcs is fine for prototypes, thin for 60 units + spares | Authorized-distributor quote for ~150 pcs now; the WLCSP variant is not an acceptable fallback for assembly. |
| 4 | **XMOS 12-week lead time** and the XU316 power draw gap | Re-check stock at commit; pull draw figures from the XMOS reference design docs; buy the eval board for the first I²S bring-up. |
| 5 | **Windows composite behaviour of hub + two devices** (audio endpoint naming, volume routing, companion-app discovery) | Breadboard: USB2422 eval/breakout + XU316 eval + P4 board; confirm endpoint names, HID keys and CDC all appear and survive sleep/resume. Decide where the Windows master-volume write lands (recommendation: reflect it to the CS43131 via the P4, one attenuator). |
| 6 | **TVS distortion at signal level** | One-hour bench check: THD sweep with and without TPD2E001 fitted at 2 Vrms. |
| 7 | **If the ES9219Q is retained** (section 7): datasheet items unread | Human read of the ES9219 v1.2 PDF (charge-pump output topology, soft-ramp registers, short-circuit rating) before any schematic. |

---

## 7. Findings that touch existing project decisions

Nothing in this brief's own "already decided" list is contested: measurement-first survives contact (section 1 shows it is the market's actual selection rule), OS-layer integration is what UAC 2.0 + in-box `usbaudio2.sys` delivers, USB-C-only power is sufficient (5.4), and the 25 × 25 × 6 mm audio board fits the one-chip architecture and the SJ-3524 jack.

Two findings challenge decisions recorded elsewhere in the project, with new evidence rather than fresh argument:

1. **The DAC chip.** `docs/SOURCING-BOM.md` records the ES9219Q as the DAC (correctly superseding the obsolete ES9219C — reconfirmed at the datasheet ordering table). New evidence from this pass: ES9219Q franchised stock is thin-to-zero with quantity pricing unpublished, its shipped implementations measure a tier below the CS43131 dongle class, and the CS43131 is in Active-status stock with published 50/500 pricing and the deeper measured record for this exact use case. **Recommendation: reopen that line item and specify CS43131, with ES9219Q as the alternate pending a supply quote.** Needs Ryan's ruling since it edits a sourcing decision.
2. **The USB topology assumption.** The repo's hardware-facts note "the ESP32-P4 enumerates as a USB audio device natively; no bridge chip is needed for the DAC path" is true as a capability statement but, on this pass's evidence (vendor-documented Windows/Linux exclusivity, zero published measurements, 2026 bug history), unsafe as a product architecture until the section 6 experiment passes. The recommended architecture assumes a bridge; the experiment can still delete it.

---

## 8. Confidence summary

**High:** the empty-niche finding; the reviewer-sentiment pattern (weak DACs punished, modest power forgiven); Windows UAC 2.0 in-box driver behaviour; XMOS/USB2422/CS43131 stock and pricing on the research date; CS43131 and ES9219 datasheet figures (both PDFs extracted); the volume-mapping arithmetic; the grounding and practice checklist; the measurement-rig costs.

**Medium:** exact expected SINAD of this implementation (bounded by the measured dongle class, proven only on the bench); the one-chip-beats-two-chip generalisation; several Audio Science Review figures read from graphs or search summaries (flagged per item in the findings files).

**Open:** XU316 power draw; ES9219Q volume pricing (quote required); the output-power positioning ruling (5.3); everything in the section 6 experiment table.
