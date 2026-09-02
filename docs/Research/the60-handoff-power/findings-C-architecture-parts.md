# Power architecture parts research — strand C (hardware behind each option)

Researched 2026-09-02. All prices in USD as listed on the cited distributor page on that date; stock figures are snapshots and move daily. Anything not read from a source is marked **unverified** or "quote required". Package heights for bare integrated circuits (all under 1.1 mm) are never the height constraint inside the 34 mm budget — connectors, inductors and capacitors are.

Context assumed from the brief: the 60 is powered by one USB-C (Universal Serial Bus Type-C) cable from a computer; guaranteed-minimum port power is 2.5 W (5 V × 500 mA, the USB 2.0 default); peak demand 6–12 W; no battery, ever.

---

## 1. Type-C 3 A detection path (read the source's current advertisement, stay at 5 V)

### Findings

How the mechanism works: a USB-C sink presents a 5.1 kΩ pull-down resistor (Rd) on each CC (Configuration Channel) pin. The source advertises its 5 V current capability by sourcing a defined current into CC: 1.5 A capability = 180 µA ±8%, 3.0 A capability = 330 µA ±8% (default USB power = 80 µA). ([DigiKey forum engineering answer](https://forum.digikey.com/t/simple-way-to-use-usb-type-c-to-get-5v-at-up-to-3a-15w/7016/11), [Hackaday USB-C resistor guide](https://hackaday.com/2023/01/04/all-about-usb-c-resistors-and-emarkers/))

**What ESP32 firmware can read without any dedicated chip:** the CC voltage across the sink's own 5.1 kΩ Rd is simply I × R (working, with the cited advertisement currents):

- Default power source: 80 µA × 5.1 kΩ = **0.41 V**
- 1.5 A source: 180 µA × 5.1 kΩ = **0.92 V**
- 3.0 A source: 330 µA × 5.1 kΩ = **1.68 V**

These are ~0.5 V apart — trivially resolved by any ESP32 ADC (analogue-to-digital converter) channel wired to the CC pin behind Rd. The USB Type-C specification's sink detection bands (vRd) confirm the same separation (band values not re-verified verbatim against the spec table — **unverified**, but the computed voltages above follow from the cited currents). Firmware must re-sample after attach and on advertisement change (a source may drop from 3 A to 1.5 A dynamically; the sink must respond within the spec's adjustment time — **timing value unverified**).

A dedicated CC controller adds what an ADC does not give: interrupt on advertisement change, debounce, cable orientation, and correct behaviour while the ESP32 is in reset/boot. It adds nothing electrically necessary for a 15 W sink.

One board-level caution: the Waveshare ESP32-P4 board has its own USB-C connector and may already terminate CC with its own Rd resistors — whether its CC pins are routed anywhere readable must be checked against the vendor schematic (**open question for the electronics pass**).

### Parts table

| Part | Function | Price (USD) | Stock | Size / height | Source |
|---|---|---|---|---|---|
| TI TUSB320IRWBR | CC logic, reports advertised current on 2 GPIO/I²C | $1.87 @1, $1.11 @100 (Mouser); from $0.83 (LCSC) | 1,273 (Mouser); LCSC variant TUSB320RWBR out of stock | X2QFN-12, 1.6 × 1.6 mm, ≤0.4 mm tall (**height from package family, unverified vs drawing**) | [Mouser via Octopart](https://octopart.com/part/texas-instruments/TUSB320IRWBR), [LCSC C2674065](https://www.lcsc.com/product-detail/C2674065.html) |
| onsemi FUSB302BMPX | Full CC PHY incl. PD BMC; usable as I²C-driven sink monitor | $0.56 (LCSC) | 22,393 (LCSC) | MLP-14 1.7 × 2.0 mm (**dims unverified**) | [LCSC C132291](https://www.lcsc.com/product-detail/C132291.html) |
| ST STUSB4500QTR (non-PD use) | Overkill for 5 V-only detection but works standalone | $2.25 @1, $1.51 @100 (LCSC) | 4,003 (LCSC); 8,680 (Mouser) | QFN-24 4 × 4 mm, ~0.9 mm (**std QFN profile, unverified**) | [LCSC C2678061](https://www.lcsc.com/product-detail/C2678061.html) |
| Discrete: 2 × 5.1 kΩ Rd + ESP32 ADC pin | Detection for the cost of two resistors | <$0.01 | commodity | 0402 | working above |

### Assessment

The discrete Rd-plus-ADC path is free and sufficient for "am I allowed 1.5 A or 3 A at 5 V". The TUSB320 is the textbook hardening of it at ~$1. FUSB302 only makes sense if firmware later wants PD (Power Delivery) messaging without new silicon — but it needs a full PD stack in firmware; it is not set-and-forget.

---

## 2. USB PD sink path (negotiate 9 V/12 V, buck back to 5 V rails)

### Findings

Three credible standalone sink controllers, none needing firmware:

- **ST STUSB4500** — NVM-programmed PDO (Power Data Object) profiles, negotiates autonomously at dead-battery. QFN-24.
- **Infineon (Cypress) CYPD3177 EZ-PD BCR** ("Barrel Connector Replacement") — resistor-strapped voltage/current request, no programming tool needed, up to 100 W. QFN-24 4 × 4 mm. ([Infineon product page](https://www.infineon.com/part/CYPD3177-24LQXQ))
- **WCH CH224K** — PD 3.0 sink, voltage select by pin strap, 9/12/20/28 V, VBUS input 4–30 V. Credible: stocked in volume at LCSC and JLCPCB assembly, but documentation is Chinese-first and there is no compliance story — fine for the standard build, questionable for a premium 60-unit run's certification narrative.

A PD path forces a **buck converter** from the negotiated 9 V or 12 V back to the 5 V system rail at 2–3 A. Candidates:

- **TI TPS62933** (SOT-583, 1.6 × 2.1 × 0.6 mm): 3.8–30 V in, 3 A out, TI claims >90% efficiency stepping 12 V-class rails down ([TI product page](https://www.ti.com/product/TPS62933)). Needs an external inductor — a typical 2.2–4.7 µH, 4-A-class shielded power inductor is a 4 × 4 × 3 mm part (**inductor selection assumption, not yet chosen**). Solution height ≈ 3 mm.
- **TI TPS82130** MicroSiP module (3.0 × 2.8 × 1.53 mm, inductor integrated): 17 V max in (fine for 9 V and 12 V PDOs, rules out 15 V/20 V), 3 A out, efficiency up to ~95% (**headline figure from TI marketing page; curve not re-read**). Total solution height 1.53 mm — the lowest-profile option found. ([TI datasheet](https://www.ti.com/lit/ds/symlink/tps82130.pdf))
- **MPS MP2315S**: 4.5–24 V in, 3 A, 500 kHz synchronous; widely used. Price not captured this pass — **quote required**. ([MPS datasheet](https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MP2315S/document_id/981))

### Parts table

| Part | Function | Price (USD) | Stock | Size / height | Source |
|---|---|---|---|---|---|
| STUSB4500QTR | Standalone PD sink controller | $2.25 @1 / $1.38 @1k (LCSC) | 4,003 LCSC + 8,680 Mouser | QFN-24 4 × 4 × ~0.9 mm | [LCSC C2678061](https://www.lcsc.com/product-detail/C2678061.html) |
| CYPD3177-24LQXQ | Standalone PD sink, resistor-strapped | $1.20 @1 / $0.92 @980 (LCSC); $2.07 Mouser (T&R variant) | 861 LCSC | QFN-24 4 × 4 mm, ~0.6 mm (**unverified**) | [LCSC C2959321](https://www.lcsc.com/product-detail/C2959321.html) |
| CH224K | Low-cost PD sink | $0.49 @1 / $0.26 @1k (LCSC) | 3,684 LCSC | ESSOP-10, 1.0 mm tall | [LCSC C970725](https://www.lcsc.com/product-detail/USB-PD_WCH-Jiangsu-Qin-Heng-CH224K_C970725.html) |
| TPS62933DRLR | 12 V→5 V, 3 A buck | from $0.24 (LCSC) | in stock LCSC | SOT-583 + 4 × 4 × 3 mm inductor | [LCSC C3200405](https://www.lcsc.com/product-detail/C3200405.html), [TI](https://www.ti.com/product/TPS62933) |
| TPS82130SILR | 12 V→5 V, 3 A buck **module** | $2.76–3.43 (LCSC); £2.08 (RS, 3,944 in stock) | in stock | 3.0 × 2.8 × **1.53 mm** total | [LCSC C473914](https://www.lcsc.com/product-detail/C473914.html), [RS](https://uk.rs-online.com/web/p/dc-dc-converters-ics/1330778) |
| MP2315S | Alternative buck | quote required | — | TSOT/SOIC + inductor | [MPS](https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MP2315S/document_id/981) |

**Total added cost for the PD path** (sink controller + buck module + passives): roughly **$3–6 at 60-unit quantities** (CYPD3177 ~$1.10 + TPS82130 ~$2.80 + passives), board area roughly 4 cm² including the buck's input/output capacitors (**area is an estimate, not a layout**). Height impact ≤3 mm — negligible against 34 mm.

### Assessment

The PD path is cheap and short. Its real cost is systemic: it only helps when the *source* offers PD contracts above 15 W, which a computer's data port usually does not (data ports commonly advertise only 5 V at 1.5 A/3 A). PD sink silicon pays off only in a two-input or charger-fed topology.

---

## 3. Second power input (aux power + priority mux)

### Findings

- **Panel-mount second USB-C:** CLIFF CP30711MB feed-through adapter (USB-C receptacle → USB-C plug, panel mount) — $25.50 @1, $18.43 @100, 46 in stock at DigiKey, 6-week lead. Panel cut-out and behind-panel depth not captured — **quote required**. ([DigiKey CP30711MB](https://www.digikey.com/en/products/detail/cliff-electronic-components-ltd/CP30711MB/13921982)) A plain PCB-mount receptacle (e.g. GCT USB4105 class, ~3.3 mm tall) fronted by the enclosure wall is the ~$1-class alternative (**price not captured this pass**).
- **Barrel jack:** Switchcraft 721A panel-mount DC power jack (2.1 mm ID / 5.5 mm OD) — $7.80 at DigiKey ([DigiKey 721A](https://www.digikey.com/en/products/detail/switchcraft-inc/721A/8571716)). Behind-panel depth for this family typically ~15–20 mm (**unverified**). Cheaper CUI/Same Sky panel jacks exist at $1–3 (**not individually verified**).
- **Priority mux (the part that makes two inputs clean):** TI TPS2121 — dual-input single-output power multiplexer, 2.8–22 V, 56 mΩ, integrated FETs, adjustable 1–4.5 A current limit, seamless automatic switchover. **Verified: $1.23 @1 / $0.81 @1k, 993 in stock at LCSC; $2.44 at DigiKey. VQFN-HR-12, 2 × 2.5 mm.** ([LCSC C485916](https://www.lcsc.com/product-detail/C485916.html), [DigiKey TPS2121RUXR](https://www.digikey.com/en/products/detail/texas-instruments/TPS2121RUXR/9859001))
- **eFuse alternative:** TI TPS25942A eFuse power mux, 2.7–18 V, 5 A class, reverse-current blocking — $0.61 at LCSC but only 46 in stock there (deeper stock elsewhere **not checked**). ([LCSC C181295](https://www.lcsc.com/product-detail/C181295.html))

### Assessment

Electrically the easiest robust path: TPS2121 prefers the aux input when present, falls back to data-VBUS, switchover is glitchless into a bulk capacitor. The whole added BOM (bill of materials) is ~$3–10 depending on connector choice. The cost is entirely philosophical: a second visible cable — which the product brief calls a core-value violation — or a second port that ships empty and invites the question.

---

## 4. Powered pass-through (one cable to the device, power injected upstream)

### Findings

- **Docks with powered downstream USB-C data ports are real and shipping.** CalDigit TS4 Thunderbolt 4 dock: one front USB-C port delivers **20 W with full data**; list price $399.99 (street ~$304–320). ([CalDigit TS4](https://www.caldigit.com/thunderbolt-station-4/), [Amazon listing](https://www.amazon.com/CalDigit-TS4-Thunderbolt-Dock-USB/dp/B09GK8LBWS)) This is exactly the desired topology: the desk device sees one cable carrying host data + 20 W.
- **Ordinary powered hubs:** a compliant USB 3.x hub port supplies 900 mA (4.5 W); ports implementing BC 1.2 CDP (Battery Charging spec, Charging Downstream Port) supply up to 1.5 A (7.5 W) with data ([Wikipedia USB hardware](https://en.wikipedia.org/wiki/USB_hardware)). Even a $30–60 powered hub raises the guaranteed floor from 2.5 W to 4.5–7.5 W — but which cheap hubs actually implement CDP is per-model folklore; **specific verified models: quote required**.
- **Y-cables / splitters:** purchasable everywhere — e.g. MOGOOD 60 W USB-C splitter, one leg PD charge + one leg data into a single device plug ([Amazon](https://www.amazon.com/MOGOOD-USB-C-Splitter-Adapter-Female/dp/B0DG55BS6V), ~$10–20 class, listed price not captured); VIVOSUN 1-male-to-2-female $11.99 (eBay); generic USB-C Y $13.55 (eBay). **Standing under the spec: not compliant.** USB-C extension and splitter assemblies sit outside the USB-C cable specification; reputable connector vendors do not make them, and the failure modes (wrong e-marking, over-current through undersized conductors) are documented. ([Hackaday, "All about USB-C: illegal adapters"](https://hackaday.com/2022/12/27/all-about-usb-c-illegal-adapters/), [Tom's Hardware discussion](https://forums.tomshardware.com/threads/does-a-true-usb-c-power-splitter-exist.3814790/)) Whether a given splitter's power leg feeds VBUS cleanly while the data leg's VBUS is also present is per-product roulette — two sources merging on one VBUS pin with no ORing is exactly what section 3's TPS2121 exists to prevent.
- **Inline "PD injector" as a clean product category: absent.** What is sold under that name is either a Y-splitter (above) or PoE (Power over Ethernet) gear.

### Assessment

The only spec-honest pass-through is "the customer owns a dock or powered hub", which cannot be a shipped dependency — but it can be the documented escape hatch: the device works at 2.5 W and does everything at 7.5 W+. Shipping a Y-cable in a premium product's box means shipping a non-compliant accessory; that reads as a disqualifier for the 60.

---

## 5. Supercapacitor buffer (full answer)

### 5a. Sizing — the working

**Assumptions (marked):** port sustains 2.5 W continuously; buck-boost converter efficiency 85% cap-to-rail (**assumption, typical for this class**); bank recharges whenever the burst is over; baseline electronics already consume the port's full 2.5 W during the burst (worst case).

**Burst A — ringer: 5 W for 10 s.** Load energy = 50 J. Port supplies 2.5 W × 10 s = 25 J. Deficit = 25 J at the load = **25 / 0.85 ≈ 29.4 J drawn from the bank**.

**Burst B — motor: 3 W for 2 s on top of a saturated port.** Deficit = 6 J at load = **7.1 J from the bank**. (If the 1–4 W detent-cancel draw is *continuous*, no capacitor of any size helps — a buffer bridges only bursts shorter than its energy divided by the deficit. At a steady 4 W total against a 2.5 W port, the 46.9 J bank below dies in ~26 s. Continuous overdraw needs a bigger port, not a buffer.)

**Usable energy** between charge voltage V₁ and minimum converter input V₂: E = ½ C (V₁² − V₂²).

**Option 1 — two 2.7 V cells in series (bank ≈ 5 V, needs balancing).** Two 10 F cells in series → 5 F. Charge to 5.0 V (derated from 5.4 V for lifetime), let the buck-boost ride down to 2.5 V:
E = ½ × 5 F × (5.0² − 2.5²) = ½ × 5 × 18.75 = **46.9 J usable** → covers the 29.4 J ringer burst with ~60% margin, which also covers end-of-life capacitance fade to 70% (46.9 × 0.7 = 32.8 J > 29.4 J). ESR (equivalent series resistance) check: 2 × 34 mΩ = 68 mΩ; peak bank current at 5.9 W / 3.0 V ≈ 2.0 A → 0.14 V droop, negligible against the 2.5 V window. Recharge: 29.4 J at ~2 W spare port power / 85% ≈ **17 s** to full.

**Option 2 — single 3.0 V, 25 F cell (no balancing, higher currents).** Charge to 2.7 V (10% derate), discharge to 1.8 V (LTC3128 minimum input is 1.73 V):
E = ½ × 25 × (2.7² − 1.8²) = ½ × 25 × 4.05 = **50.6 J usable**. But peak converter input current at 5.9 W / 1.8 V ≈ 3.3 A — above the LTC3128's 3 A and the LTC4041's 2.5 A boost ratings. Workable only if the burst spec drops or the cut-off rises (cutting at 2.2 V yields 30.6 J — exactly the requirement, zero margin). **The two-cell 5 V bank is the engineering answer.**

**Option 3 — 5.5 V coin-cell EDLC (electric double-layer capacitor) modules: eliminated by arithmetic.** Eaton KR-class ESR is 30 Ω ([DigiKey KR-5R5V105-R](https://www.digikey.com/en/products/detail/eaton-electronics-division/KR-5R5V105-R/1556244)); at the 2 A the ringer needs, I × R = 60 V of drop. These parts exist for real-time-clock retention at microamps, not watt-class bursts.

**Option 4 — LIC (lithium-ion capacitor).** Higher energy density, but one electrode is lithium-doped battery chemistry: cannot sit at 0 V, has a charge-voltage floor, cycle life in the 10⁵ range rather than 10⁶, and low-temperature charging limits. It is a small battery with capacitor manners — **conflicts with the no-battery principle** and is excluded on those grounds, not on availability.

### 5b. Real parts

| Part | Function | Price (USD) | Stock | Size / height | Source |
|---|---|---|---|---|---|
| Eaton HV1030-2R7106-R | EDLC cell, 10 F, 2.7 V, 34 mΩ @100 Hz | $3.28 @1 | 5,811 DigiKey | Ø10.0 × 31.5 mm — lies flat well under 34 mm | [DigiKey](https://www.digikey.com/en/products/detail/eaton-electronics-division/HV1030-2R7106-R/3878071) |
| VINATech WEC3R0256QG | EDLC cell, 25 F, 3.0 V, 25 mΩ @1 kHz | $3.72 @1 / $1.75 @1k | 1 (!) DigiKey, 8-wk lead | Ø16 × 26.5 mm | [DigiKey](https://www.digikey.com/en/products/detail/vinatech-co-ltd/WEC3R0256QG/16164487) |
| VINATech VEC3R0106QG | EDLC cell, 10 F, 3.0 V | ~$2.40–3 class (**exact quote required**) | stocked EU (Farnell/Rapid) | Ø10 × 30 mm | [Farnell](https://uk.farnell.com/vinatech/vec3r0-106qg/cap-10f-3v-super-cap-radial/dp/2663718) |
| Eaton KR-5R5V105-R | 5.5 V coin module, 1 F, 30 Ω | $5.69–7.65 | DigiKey stock | coin stack | [DigiKey](https://www.digikey.com/en/products/detail/eaton-electronics-division/KR-5R5V105-R/1556244) |
| Maxwell/UCap ESHSR-0010C0-002R7 | EDLC 10 F 2.7 V (second source) | quote required | DigiKey listing exists | Ø10 class | [DigiKey](https://www.digikey.com/en/products/detail/maxwell-technologies/ESHSR-0010C0-002R7/946802) |

Two Eaton HV1030 cells lying horizontally occupy roughly 10 × 21 × 32 mm — comfortably inside a Ø135 × 34 mm envelope beside the display board (**placement assumption for the CAD pass, not a layout**).

### 5c. Charge management and delivery

| Part | Function | Price (USD) | Stock | Package | Source |
|---|---|---|---|---|---|
| ADI LTC3128 | Buck-boost supercap **charger** with programmable average input current limit to 3 A ±2% and **active 2-cell balancing** — charges from a current-limited port without ever exceeding it (this is the inrush answer) | $3.95 @1k (ADI); singles ~$5–8 Newark (**quote required**) | Newark/ADI listed | 4 × 5 mm QFN-20 or TSSOP-24 | [ADI](https://www.analog.com/en/products/ltc3128.html), [Newark](https://www.newark.com/analog-devices/ltc3128eufd-pbf/supercapacitor-charger-qfn-ep/dp/51AK6771) |
| ADI LTC4041 | Complete backup manager for 2.9–5.5 V rails: step-down charger for 1–2 series supercaps **with balancing**, plus **2.5 A boost** that back-feeds the 5 V rail when input sags below a programmable threshold — single-chip version of the whole buffer | $6.26 @2.5k reel (DigiKey); ~$10.60 singles (Newark) | DigiKey listed | QFN-24 4 × 5 mm | [DigiKey](https://www.digikey.com/en/products/detail/analog-devices-inc/LTC4041IUFD-PBF/9446093), [ADI](https://www.analog.com/en/products/ltc4041.html) |
| TI TPS25942A | eFuse / inrush limit / reverse blocking on the port side | $0.61 (LCSC, 46 pcs — thin; elsewhere unchecked) | 46 LCSC | WQFN 4 × 3.5 mm | [LCSC C181295](https://www.lcsc.com/product-detail/C181295.html) |

Topology that closes: port → eFuse → 5 V system rail; LTC4041 hangs on that rail, charges the 2-cell bank within a resistor-set current budget, and boosts back into the rail during bursts. One chip, two cells, balancing included. Added BOM ≈ **$10.60 + 2 × $3.28 + passives ≈ $18–20 @1** (~$13–15 at 60-off — **extrapolated, quote required**).

### 5d. Lifetime and failure mode — the honest answer

**The endurance data.** Both cited cells carry the same distributor-listed endurance spec: **1,000 h at 65 °C at rated voltage** ([DigiKey HV1030 attribute](https://www.digikey.com/en/products/detail/eaton-electronics-division/HV1030-2R7106-R/3878071), [DigiKey WEC3R0256QG attribute](https://www.digikey.com/en/products/detail/vinatech-co-ltd/WEC3R0256QG/16164487)). End of life is defined as **capacitance −30% or ESR ×2–3, whichever first — and end of life means degraded, not dead** ([Abracon, "Supercapacitor Lifetime Explained", 2024](https://abracon.com/uploads/resources/Supercapacitor-Lifetime-Explained.pdf)).

**The extrapolation rules (industry-standard, cited):** life ~doubles per 10 °C below rated temperature ([Eaton supercapacitor FAQ](https://www.eaton.com/sg/en-us/products/electronic-components/faq/supercapacitor-modules-frequently-asked-questions.html)); voltage derating is stronger still — Abracon shows a 0.2 V derate (~3%) doubling lifetime, and Eaton's application guidance states that 10–15% float-voltage derating at 25 °C ambient yields **lifetimes up to 20 years** (same two sources).

**Applied to the 60 (working, assumptions marked):** desk ambient ~25 °C. Temperature alone: 1,000 h × 2^((65−25)/10) = ×16 = 16,000 h ≈ 1.8 years *if floated at the full rated 5.4 V*. Charging the bank to 5.0 V instead (0.4 V derate ≈ two of Abracon's doublings) → ~7 years; to 4.6 V → ~29 years; and because the sizing carries a margin that still meets spec at −30% capacitance, "end of life" arrives silently as a smaller margin, years later again. The derate-vs-capacity trade is a firmware constant, not a hardware change. (Extrapolation beyond manufacturer tables is an **engineering estimate**, flagged as such.)

**Cycle life vs calendar life:** EDLC cycle life is quoted in the 500,000–1,000,000-cycle class by manufacturers ([Skeleton Technologies overview](https://www.skeletontech.com/skeleton-blog/supercapacitors-101-maintenance-and-lifespan-of-supercapacitors)); even 100 ringer bursts a day is 27+ years of cycles. **Calendar (float) life at temperature and voltage dominates**, and it is set by the derating chosen above.

**"Does it wear out like a battery?"** No — it wears out like a capacitor, the wear mechanism every long-lived electronic object already contains. The comparison, with numbers: a standard aluminium electrolytic capacitor is rated 2,000 h at 105 °C and follows the same doubling-per-10 °C Arrhenius law — 2,000 h × 2^((105−45)/10) = 128,000 h ≈ **14.6 years at a 45 °C internal ambient** ([Nippon Chemi-Con lifetime FAQ](https://www.chemi-con.co.jp/en/faq/detail.php?id=alLifetime), [XP Power application note](https://www.xppower.com/resources/blog/electrolytic-capacitor-lifetime-in-power-supplies)). A properly derated EDLC at desk temperature projects *longer* than the electrolytics in the power supplies around it. Unlike a battery: no chemical conversion cycle, no cliff-edge failure, no swelling/vent/transport regulation, and degradation is gradual fade to a defined 70% floor. An EDLC gives the object a slow softening measured in decades, not an expiry date. LICs forfeit exactly this argument and are excluded.

---

## 6. USB-audio power class

### Findings

- **What the spec allows:** a USB 2.0 bus-powered device may declare at most 500 mA (2.5 W); USB 3.x raises the per-port default to 900 mA (4.5 W) ([Wikipedia USB hardware](https://en.wikipedia.org/wiki/USB_hardware)). The USB Audio Class confers **no additional power entitlement**. Power comes from the port-power rules — Type-C current advertisement (1.5 A/3 A), BC 1.2, or PD — never from the device class. "We are an audio interface" changes nothing at the protocol level.
- **What audio interfaces actually draw:** well over the USB 2.0 default, leaning on Type-C current advertisement. A field report measured the bus-powered MOTU M2 at ~5 V × 1.5 A ≈ 7 W on an iPad Pro USB-C port ([Pawpaw Technology article — secondhand measurement, treat as indicative](https://www.pawpaw.cn/en/news/article/2025-07-11-from-lightning-to-usb-c-have-power-supply-issues-for-portable-audio-interfaces-been-solved/)); Focusrite states USB-C iPad ports power all bus-powered Scarlett models with no external supply (**reported via search results; original Focusrite page not fetched, unverified verbatim**). Dongle DAC (digital-to-analogue converter) draws: Apogee Groove 340 mA measured; AudioQuest claims ~25% less for the DragonFly ([audioreviews.org dongle survey](https://www.audioreviews.org/dongles-portable-dac-amps/)); Apple's USB-C dongle draws far less (tens-of-mA class — widely reported, **precise figure not captured, quote required**).

### Assessment

The audio-interface precedent cuts two ways. It proves hosts routinely deliver 5–7 W to bus-powered audio devices over Type-C without complaint — the 2.5 W "guaranteed minimum" is a floor almost no modern laptop port actually enforces. But it grants no spec cover: a device drawing 7 W from a port advertising 1.5 A is doing what MOTU does, not what the spec promises. The honest posture for the 60 is the same as theirs: read the CC advertisement (section 1), scale features to the answer, and let the supercap bank (section 5) make the guaranteed-minimum case survivable.

---

## Confidence and gaps

- **High confidence:** all LCSC/DigiKey prices and stock quoted were read from live distributor pages on 2026-09-02; the CC-detection voltage arithmetic; the supercap sizing arithmetic; the coin-module elimination; Y-cable non-compliance.
- **Medium confidence:** IC package heights taken from package-family norms, not each mechanical drawing; supercap lifetime extrapolations use manufacturer-published doubling rules but extend beyond their tables; the Eaton HV endurance figure came from DigiKey's attribute line — Eaton's own datasheet PDF timed out on three fetch attempts, so one manual download should confirm 1,000 h vs 1,500 h and the room-temperature life claim.
- **Gaps / quote required:** MP2315S and Maxwell ESHSR pricing; CLIFF CP30711MB panel dimensions; exact LTC3128 single-unit price; which specific powered hubs implement BC 1.2 CDP at 1.5 A; Apple dongle's precise measured draw; whether the Waveshare ESP32-P4 board exposes its CC pins (needs the vendor schematic, not the web).
- **Design-level flags for the synthesizer:** a *continuous* 4 W motor draw defeats any buffer — the supercap answers bursts only; the two-cell 5 V bank with LTC4041 is the only supercap option meeting current, energy and balancing requirements simultaneously; TUSB320 was out of stock at LCSC (fine at Mouser/Arrow) and TPS25942A stock at LCSC was 46 units — neither is a supply risk at 60 units, but both belong on the watch list.
