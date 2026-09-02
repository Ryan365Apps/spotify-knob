# Power budget and power architecture of the 60 — research report

Answer to the brief in `../the60-handoff-power-RD.md`. Research date 2026-09-02. Synthesised from four findings files in this folder — the evidence record, with every figure cited or marked as an estimate with its working:

- `findings-A-load-budget.md` — every consumer's current, the ring-motor estimate, the four scenario sums
- `findings-B-ports-compliance.md` — what real ports supply, detection mechanisms, USB-IF/CE/FCC obligations
- `findings-C-architecture-parts.md` — verified parts and prices for each architecture option, the full supercapacitor answer
- `findings-D-actuator-halo-heat.md` — carrier actuators and energy economics, halo perception, heat and touch-temperature limits

Findings first (sections 1–7), recommendation with fallback (section 8), first bench measurements (section 9), and the flags the brief asked for — things in the brief itself the evidence says are wrong (section 10).

---

## 1. The load budget (full working: findings-A)

The consumers, at 5 V input, headline figures (datasheet-cited unless marked estimate):

- **ESP32-P4 active** ≈ 0.48 W; idle ≈ 0.14 W. **ESP32-C6** Wi-Fi TX peak ≈ 1.37 W, modem-sleep ≈ 0.06 W (Espressif datasheets).
- **Display**: backlight 100% ≈ 0.6 W, panel logic ≈ 0.3 W — both estimates scaled from another Waveshare panel because the vendor publishes nothing for this board. The single cheapest measurement in the whole strand.
- **Speaker path**: 2 W electrical into 8 Ω ≈ 2.2 W at the rail (NS4150B class-D at 90%). Physics note: a 5 V bridge-tied amp into 8 Ω clips at ≈ 1.56 W continuous — "2 W" is the speaker's rating, not deliverable power.
- **Haptics (DRV2605L + 8 mm LRA)** ≈ 0.3–0.4 W while buzzing. **N20 gearmotor** 0.2–0.5 W running, 1.8–8 W stalled depending on variant. **Encoder** ≈ 0.09 W. **Touch, codec, mics, DAC stage**: all ≤ 0.2 W combined territory.
- **Halo (SK6812 RGBW)**: the W (white) die is 16.5–20 mA per LED; all-four-channels-on is 43.5–80 mA per LED — the two findings strands cite different secondary sources for this and **the spread is a flagged bench measurement** (the OPSCO datasheet publishes no per-channel current table). Either way the design conclusion holds: W-only white is ~4× cheaper than RGB-mixed white and all-channel white should be firmware-capped.
- **The ring motor cancelling the detent continuously is the budget.** First-principles estimate anchored on catalogue motor constants (Maxon EC 90 flat, iPower gimbal motors): cancelling 60 mNm continuously ≈ **1.4 W best case, 2–10 W plausible**; cancelling 150 mNm ≈ **9 W best case, 25 W plausible**. The sixty-steel-poles-no-magnets rotor makes this a reluctance machine, which makes these estimates generous. Everything else in the device combined is ~1.8–4.3 W.

**The four scenarios** (findings-A section 3, summarised against the brief's thresholds):

| Scenario | Total | Fits 2.5 W? | 4.5 W? | 7.5 W? | 15 W? |
|---|---|---|---|---|---|
| Idle on the desk | ≈ 0.84 W | **yes** (3×) | yes | yes | yes |
| Scrolling, detent cancelled by motor | 1.8 W + 1.4–25 W motor | **no** | best case only | 60 mNm cases only | not at plausible 150 mNm |
| Call ringing | ≈ 4.3 W avg / 7.8 W peak (all-channel halo; ≈ 2.9 W avg with W-only halo) | no | at the line, no margin | yes (peak marginal) | yes |
| Everything at once | ≈ 35 W unconstrained; ≈ 9.5 W with firmware limits | no | no | no | only the constrained build |

**The 2.5 W assumption supports the idle state and nothing else.**

## 2. What ports actually give (full detail: findings-B)

- Guaranteed floors: 2.5 W (USB 2.0 enumerated), 4.5 W (USB 3.x enumerated). Ports tolerate ~1 A+ in practice, but out-of-spec draw on a protected board can shut the port or the machine down.
- **The Type-C CC (configuration channel) advertisement is the high-value mechanism**: a resistor signature, no protocol, readable by two 5.1 kΩ pull-downs and an ADC (0.41 / 0.92 / 1.68 V for Default / 1.5 A / 3 A) — or hardened by a ~$1 TUSB320. It unlocks 7.5 W or 15 W and works before firmware boots.
- Estimated port reality for this buyer (an estimate built from cited vendor floors — Thunderbolt 4 mandates 15 W, USB4 7.5 W, Dell publishes 15 W/7.5 W, CalDigit/Dell monitor downstream ports 7.5–15 W): **~80–95% of the Type-C ports the buyer will use give ≥ 7.5 W; ~50–75% give 15 W; under 10% offer 9 V**. Desktop rear Type-C is the unknown — assume Default until measured. Type-A-only installs (est. 10–25%) cap at 4.5 W in-spec.
- **USB Power Delivery buys almost nothing here**: host *data* ports rarely offer more than 5 V; 9 V lives on charging ports. Standalone sink chips exist and are cheap (CYPD3177 $1.24 @100, STUSB4500 $1.51 @100, CH224K $0.28 @100) but only pay off in charger- or dock-fed topologies.
- Being a USB audio interface grants no extra power entitlement — but the precedent (MOTU M2 measured at ~7 W bus-powered) shows the market's honest posture: read CC, scale to the answer.

## 3. The architecture options compared (parts detail: findings-C)

| # | Option | Power | Added cost / height | One-cable? | No-battery? | Verdict |
|---|---|---|---|---|---|---|
| 1 | Live within 5 V / 500 mA | 2.5 W | $0 | yes | yes | Only the idle state fits. Dead as the sole architecture. |
| 2 | **Detect Type-C advertisement, tier the features** | 4.5 / 7.5 / 15 W | ~$0–1, no height | yes | yes | **The core of the recommendation.** Covers 80–95% of real ports at ≥7.5 W. |
| 3 | PD sink + buck for 9 V+ | >15 W where offered | $3–6, ≤3 mm | yes | yes | Cheap but mostly useless on host data ports (<10% offer 9 V). Optional bonus tier only. |
| 4 | Second power input + TPS2121 priority mux | up to ~15 W aux | $3–10, connector height fine | **no — second cable** | yes | Electrically trivial, philosophically expensive. Hold in reserve. |
| 5 | Powered pass-through (Y-cable / dock) | 7.5–20 W | Y-cable ~$10–20 but **not USB-compliant**; dock is customer-owned ($399 CalDigit class) | desk sees one cable | yes | Y-cable in the box is a non-compliant accessory — disqualified. "Works even better on a dock" is a free documentation line, not a dependency. |
| 6 | **Supercapacitor buffer for bursts** | +29–47 J bursts | ~$18–20 @1 (2× Eaton 10 F 2.7 V + LTC4041), fits under 34 mm lying flat | yes | **yes — see verdict below** | **Recommended.** Bridges the ringer and motor bursts on weak ports. Cannot fix continuous overdraw (a steady 4 W deficit drains it in ~26 s). |
| 7 | Audio-interface power class | none extra | — | — | — | A precedent, not a mechanism. |

**The supercapacitor verdict the brief demanded:** an EDLC (electric double-layer capacitor) does not violate "no battery" in spirit. It wears like a capacitor — gradual fade to a defined 70% floor, no cliff, no chemistry cycle, no transport regulation (the bank is 0.02–0.09 Wh, far under the UN 3499 0.3 Wh dangerous-goods line). At a firmware-set 5.0 V charge (derated from 5.4 V) the cited endurance rules extrapolate to ~7 years to *fade onset*, ~29 years at 4.6 V — projecting longer than the aluminium electrolytic capacitors every long-lived power supply already contains. Cycle life (~10⁶) is irrelevant at desk duty. Lithium-ion capacitors, by contrast, are battery chemistry in capacitor clothes and are excluded. The derate-vs-margin trade is a firmware constant; the sizing already carries end-of-life margin.

## 4. The carrier question (full working: findings-D)

**Winner on paper: the N20-class gearmotor + cam, made fast.** A Pololu HP 6 V 50:1 (590 RPM at 6 V, cited) turns a half-revolution cam in well under 100 ms at 5 V; dwell flats at the cam ends give unpowered hold by geometry; ~0.1–0.2 J per move; the only risk is stall-on-jam, solved by a firmware current limit. The challenger is a Takaha-class latching solenoid (5 mm stroke, 10 N magnetic hold, ~20 ms pulse — but coil data quote-required and the small-package force-vs-stroke physics is unforgiving). Voice coil and shape-memory alloy fail unpowered hold; piezo cannot reach 3 mm.

**The energy economics are not close.** A carrier round trip ≈ 0.4 J; continuous cancellation at 1–4 W breaks even after just **0.1–0.4 s of scrolling**. Over an hour: worst-mode carrier use ≈ 72 J versus 300–1,200 J for cancellation — a 4–60× win. At the worst moment, the carrier's peaks are milliseconds long (a bulk-capacitor problem); cancellation is the sustained draw that actually stresses the port. And section 6 adds the thermal twin: cancellation heat is deposited in coils at the rim, directly under the one part that must never feel warm.

## 5. The halo at lower power (full working: findings-D)

- Perception is the free lunch: **20% duty reads as ~52% of full perceived brightness** (CIE lightness law and the Stevens power law agree within a point). The noticed "20% cap limitation" is mostly not a limitation.
- The W die does white at 16.5–20 mA/LED versus 27+ mA mixed from RGB — use W-only white everywhere white is meant.
- **Target: 60 LEDs** on the 320 mm arc (5.3 mm pitch — dot-free behind ~5 mm of diffusion per the cited rules of thumb, and one LED per detent is an interaction asset). Budget: **~1.0 W sustained cap (60 × 16.5 mA × 20%), 5 W sub-second full-white peaks, 0.3 W dark floor** (1 mA/LED static — switch the strip's rail for a true off).
- Generosity comes from count, gamma and ambient adaptation, not duty: more LEDs at lower duty reads smoother and brighter for the same watts.

## 6. Heat (full working: findings-D)

- Computed case-to-ambient resistance of the sealed Ø135 × 34 mm enclosure ≈ **3 K/W** (estimate, working shown; assumes an emissive finish — polished bare metal radiates almost nothing, a real thermal reason to anodise).
- Safety is not the binding limit: IEC 62368-1's touchable-metal limit is 48 °C for >1 min contact (the standard's own example for the shorter class is "slight adjustment of a volume knob"), which allows ~8–9 W continuous. **The product rule binds first: a metal ring that never feels warm (~≤34 °C) caps the whole device at ≈ 4 W continuous.** Transients ride the steel base's minutes-long thermal time constant for free; sustained watts are the ledger.
- Design lever: everything thermally couples to the steel base; the ring stays isolated (the three V-wheels are already point-contact thermal breaks). The ring motor's stator must bolt to the base, never the bezel.

## 7. Compliance (full detail: findings-B)

- USB-IF: certification voluntary; never print the logo uncertified; buy a legitimate Vendor ID (US$6,000). Risk beyond that at 60 units: effectively nil.
- One combined lab campaign (FCC Part 15B SDoC + EN 55032/55035) grounds both the US declaration and the self-declared CE mark; low-thousands US$ per lab guides, exact figure quote required. RoHS/WEEE apply regardless.
- The supercapacitor bank is transport-trivial (far under the 0.3 Wh dangerous-goods threshold) — a genuine compliance advantage over any lithium buffer.
- **Open ruling that changes the route**: radios enabled (Radio Equipment Directive + FCC Part 15C with an FCC ID — pre-certified modules exist for this) versus USB-only with radios off (plain EMC route).

---

## 8. Recommendation (and fallback)

### The architecture

**One cable. Type-C current-advertisement detection with tiered budgets, a two-cell supercapacitor burst buffer, and the carrier — not the motor — handling long free-spins.**

1. **Power front end:** USB-C → eFuse with inrush limit (TPS25942A-class) → 5 V system rail. CC pins on 5.1 kΩ pull-downs read by a TUSB320 (~$1) or the ESP32-P4's ADC. No PD silicon in the base build.
2. **Tiered budgets, enforced in firmware:**
   - **2.5 W** (Default Rp on a USB 2.0 port): full control function, screen managed, halo W-only at reduced duty, ringer served from the buffer, no continuous motor work. The device *works* on the guaranteed minimum.
   - **4.5 W** (USB 3.x enumerated): everything above plus full screen and normal halo states.
   - **7.5 W** (1.5 A advertised — est. 80–95% of real Type-C ports): full feature set, including ringer scenario with margin.
   - **15 W** (3 A advertised): headroom — stronger motor feel moments, faster buffer recharge, full-white flashes without accounting.
3. **Burst buffer:** two Eaton HV1030 10 F / 2.7 V cells in series managed by one LTC4041 (charger + balancer + 2.5 A boost back into the rail): 46.9 J usable at a 5.0 V charge — covers the 29.4 J worst-case ringer deficit on a 2.5 W port with end-of-life margin, recharges in ~17 s. Added BOM ≈ $18–20 at singles. Charge voltage is the firmware-set longevity dial.
4. **Motion policy (the decision that makes the budget close):** the magnet carrier drops the detent for scroll-mode — a fast N20 + cam with dwell flats, ~0.2 J and ~100 ms per move — and the ring motor is reserved for *feel*: detent shaping, brief cancellation moments, event torque, bounded to short bursts the buffer and the 4 W thermal ledger can absorb. Continuous cancellation while a finger rests on a hotspot is the one requirement the evidence cannot make fit; see section 10.
5. **Concurrency limits in firmware:** all-channel white capped; speaker and motor never simultaneously at max; N20 stall timeout; halo rail switched off when dark.
6. **Thermals:** motor stator and LED board to the steel base; ring isolated; emissive internal finishes; device-level continuous target ≤ 4 W.

Confidence: high that this architecture serves every scenario in section 1 except continuous high-torque cancellation, on the honest port distribution, with no battery, one cable, and 34 mm intact.

### Fallback

If the bench rig proves sustained motor loads are essential (a ruling in section 10 goes the other way) and the motor lands at the good end of the Km range: add the PD tier — CYPD3177 + TPS82130 buck ($3–6, ≤3 mm) — and spec the full experience on 9 V-capable ports and docks, with the tiered 5 V behaviour as the floor everywhere else. If the motor lands mid-range or worse, no USB architecture carries continuous 150 mNm cancellation; the requirement itself has to move. The second-input option (TPS2121 mux) stays on the shelf as the last resort that trades the one-cable promise for unconditional power.

## 9. First three bench measurements

1. **USB power meter on the real Waveshare board** (any inline USB-C power meter feeding the dev board): idle, backlight 0% vs 100%, Wi-Fi states, touch active. Kills the three biggest estimate lines in the budget (backlight, panel logic, board overhead) in one session. While the meter is out: plug a USB-C tester into the studio's own desktop rear Type-C, front panel, dock and monitor ports and record the CC advertisement each gives — replacing the weakest input of the port-distribution estimate with data.
2. **Ring-motor torque-per-watt on the bench rig** (the rig already planned in the decision index's open questions A–F; add a bench PSU with current readout and a torque measurement): measure the prototype coil's actual Km, and the carrier's magnet-to-pole load force in the same session. The whole budget swings 1.4 W ↔ 36 W on Km, and the carrier actuator choice (N20 vs latching solenoid) hangs on the load force.
3. **SK6812 RGBW strip current** (bench PSU + multimeter on a 1 m strip): per-LED current for W-only, RGB-mixed and all-four white at several duties. The two secondary sources disagree (43.5 vs 80 mA all-on); the halo budget and the ringing scenario inherit whichever is true.

## 10. Flags — things in the brief the evidence says are wrong

Separately stated, as the brief requires, with the evidence:

1. **"The design currently assumes 5 V, 500 mA" is untenable as a product constraint.** Confirmed by the budget: 2.5 W covers idle only (0.84 W); every interactive scenario exceeds it. The fix is not one bigger number but the tiered detection architecture — the guaranteed minimum stays survivable (with the buffer), and 80–95% of real ports give 7.5 W+ for free.
2. **Interaction decision 1 — continuous detent cancellation while a finger rests on a hotspot — is the single requirement that breaks the product, and three independent lines of evidence converge against it.** Energy: 4–60× worse than moving the carrier over an hour, break-even after 0.1–0.4 s of scrolling. Budget: plausibly 2–25 W sustained, which no honest USB architecture carries at the upper detent range. Heat: the watts land in coils at the rim, under the ring that must never feel warm, in a device whose no-warm-ring ledger is ~4 W total. The carrier-drop alternative costs ~0.2 J and ~100 ms per mode change — which is also the brief's own interaction decision 2, so the fast carrier is needed anyway. This touches decision 19 (dynamic detent strength comes from the motor) and needs a ruling: the evidence supports the motor for *feel* and the carrier for *state*.
3. **"A 2 W speaker alone is most of a 2.5 W budget" is doubly off.** The NS4150B amplifier clips at ≈ 1.56 W continuous into 8 Ω from 5 V, so 2 W electrical is not reachable; and at a realistic ringer level (0.5 W, 50% cadence) the speaker line is ≈ 0.28 W average — the halo, not the speaker, dominates the ringing scenario.
4. **The brief's "60–80 mA per LED, confirm" partially fails confirmation.** The OPSCO SK6812 RGBW datasheet publishes no per-channel current table; secondary sources give 43.5–80 mA all-four-on. More importantly the design-relevant figure is the W-channel-only ~16.5–20 mA — the brief's number overstates the cost of a white halo by ~4×.
5. **The "20% brightness cap" is not the limitation it was noticed to be.** 20% duty reads as ~52% perceived brightness under the CIE lightness law. The halo's problem, if any, is LED count and diffusion, not the cap.
6. **The supercapacitor question has a clean answer: it is not a battery.** Wear mechanism, wear-out shape, transport law and projected calendar life (decades at a derated charge voltage, longer than ordinary electrolytics) all separate it from battery chemistry. Lithium-ion capacitors are the variant that would violate the principle. Worth recording as a decision when the buffer is adopted.
