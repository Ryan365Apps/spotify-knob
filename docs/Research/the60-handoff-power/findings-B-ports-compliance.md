# Findings B — What a computer's USB port can actually supply, and the compliance obligations

Research strand for the 60 by Cadrane (the premium desk dial, powered by one USB Type-C cable from the computer, 2.5 W to ~10 W depending on architecture). Researched 2026-09-02. All prices and stock levels were read on that date and will drift.

Findings and assessment are kept separate throughout. Everything in a "Findings" block is read from a cited source; everything in an "Assessment" block is our interpretation.

---

## 1. Supply mechanisms — summary table

| Mechanism | Power at 5 V | How the device detects it | Sink-side hardware needed |
|---|---|---|---|
| USB 2.0 default (Standard Downstream Port) | 100 mA (0.5 W) unconfigured → 500 mA (2.5 W) after the host accepts the device's configuration descriptor | USB enumeration (the device asks for 500 mA in its descriptor; host grants or not) | None beyond the USB data connection |
| USB 3.x default | 150 mA → 900 mA (4.5 W) after configuration | USB enumeration, as above | A USB 3.x-capable device controller (an FS/HS-only device enumerating on a 3.x port is still treated as USB 2.0: 500 mA) |
| USB Type-C current advertisement, 1.5 A | 7.5 W | Analogue voltage on the CC (configuration channel) pin — no digital protocol at all | Rd (5.1 kΩ pull-down) + a comparator or a Type-C port controller chip |
| USB Type-C current advertisement, 3.0 A | 15 W | Same CC voltage measurement, higher threshold | Same |
| USB Power Delivery (PD) contract | Up to 15 W at 5 V; 9 V and above only if the source offers it | BMC (biphase mark coded) digital protocol on CC | A PD sink controller (STUSB4500, CYPD3177, CH224K — section 4) |
| BC1.2 (Battery Charging 1.2) CDP (Charging Downstream Port) | 1.5 A (7.5 W) with data | Voltage handshake on D+/D− before enumeration | A BC1.2 detection block (built into CH224K and many PMICs) |
| BC1.2 DCP (Dedicated Charging Port) | 1.5 A, **no data** | D+/D− shorted at the port | Same — but useless for the 60, which needs the data link |

Assessment: for a device that must always have a working data connection, the two mechanisms that matter are **enumerated USB configuration** (the guaranteed floor: 2.5 W or 4.5 W) and the **Type-C CC advertisement** (7.5 W or 15 W, free to read, no protocol). PD is a bonus tier; BC1.2 CDP is a niche middle case.

---

## 2. Legacy USB 2.0 / 3.x rules (findings)

- Section 7.2.1 of the USB 2.0 specification defines a "unit load" as 100 mA. A device may draw at most one unit load (100 mA) until configured; a high-power device may draw up to five unit loads (500 mA) once the host has accepted its configuration. Suspend current is limited to 2.5 mA. Sources: [Beyond Logic, USB in a NutShell ch. 2](https://www.beyondlogic.org/usbnutshell/usb2.shtml), [Dell community summary of USB 2.0 §7.2.1](https://www.dell.com/community/en/conversations/locked-topics-laptops-general/usb-power-requirements-a-little-insight/647e39ecf4ccf8a8de128d1c).
- USB 3.x raises the unit load to 150 mA and the configured maximum to 6 unit loads = 900 mA, i.e. 4.5 W ([Tom's Hardware forum citing the header/port ratings](https://forums.tomshardware.com/threads/usb-3-1-gen2-motherboard-header-amps.3688074/)).
- Enumeration is what unlocks the higher figure: the device states `bMaxPower` in its configuration descriptor; a host may refuse to configure a device that asks for more than the port can give (this is why an unconfigured device must live on 100/150 mA).
- **Over-current practice.** Hosts are required to have over-current protection, but it is commonly implemented as a PTC "polyfuse" shared across a gang of ports, or as one limit on the whole 5 V rail. In practice ports mechanically and electrically tolerate well over 500 mA: "having an allowance of 1 A or even 1.5 A became the norm", and per-port limiting is often absent ([Hackaday, "USB and the Myth of 500 Milliamps", 2024](https://hackaday.com/2024/07/03/usb-and-the-myth-of-500-milliamps/)). When a limit *is* enforced and tripped, behaviour ranges from the port dropping out to the whole machine halting with a "USB over-current detected, system will shut down" firmware trap on some ASUS boards ([Tom's Hardware thread](https://forums.tomshardware.com/threads/solved-usb-over-current-use-detected-your-pc-will-shutdown-in-15-seconds-asus-h110-m-a-m-2-motherboard.3496063/)).

Assessment: drawing ~1 A from a Type-A port will almost always work, but it is out-of-spec, unguaranteed, and the failure mode on a protected port is ugly (port shutdown or system shutdown). The 60 should treat 500 mA / 900 mA as the enumerated ceiling on any port whose CC line says "Default".

---

## 3. USB Type-C current advertisement (findings)

The source (host) advertises how much current its port can source by the value of the pull-up (Rp) it presents on the CC pin; the sink presents a 5.1 kΩ pull-down (Rd) and reads the resulting voltage. No digital negotiation is involved — it is a resistor divider.

- Rp values when pulled to 5 V (equivalently, current sources into CC): **56 kΩ / 80 µA = Default USB** (500 mA on USB 2.0, 900 mA on USB 3.x), **22 kΩ / 180 µA = 1.5 A**, **10 kΩ / 330 µA = 3.0 A**. Sources: [TI application report SLVA704, "USB Type-C CC pin"](https://www.ti.com/lit/an/slva704/slva704.pdf); [Renesas engineer school, USB Type-C](https://www.renesas.com/en/support/engineer-school/usb-power-delivery-03); [Infineon knowledge base on Rp/Rd/Ra](https://community.infineon.com/t5/Knowledge-Base-Articles/USB-Type-C-connector-Rp-Rd-and-Ra-termination-resistors/ta-p/253544).
- Sink-side CC voltage thresholds (per TI SLVA704, above): roughly **>0.66 V ⇒ at least 1.5 A**, **>1.23 V ⇒ 3.0 A**; below that, Default. The Chromium OS hardware reference gives the 3 A source band as 0.85 V < vRd < 2.45 V ([Chromium OS cable and adapter reference](https://www.chromium.org/chromium-os/developer-library/reference/hardware/cable-and-adapter-tips-and-tricks/)).
- The advertisement can change at runtime (a host may drop from 3 A to 1.5 A when another device attaches); a compliant sink must track it and reduce draw within the specified time.
- Hardware to read it: two comparators on CC1/CC2, or a dedicated Type-C port controller. Examples of PD-less sink-side parts: **STUSB4500L** — "standalone USB Type-C sink port controller", 5 V only, up to 3 A (15 W), no PD engine, dead-battery capable ([ST product page](https://www.st.com/en/interfaces-and-transceivers/stusb4500l.html), [datasheet](https://www.st.com/resource/en/datasheet/stusb4500l.pdf)). TI TUSB320 and ONsemi FUSB301 are the same class of part. An MCU with an ADC (analogue-to-digital converter) on CC also works — the ESP32-P4 could read CC directly with the divider handled in hardware design.

Assessment: this is the highest-value mechanism per unit of engineering. It is analogue, instant, requires no firmware to be running (important for the supercapacitor-charging phase before the system boots), and 1.5 A/7.5 W covers the 60's mid architecture. It must be paired with the rule in section 2: **Default advertisement means fall back to the enumerated 500/900 mA, not to 1.5 A.**

---

## 4. USB Power Delivery standalone sink controllers (findings)

What negotiating more than 5 V requires: a PD sink must run the full PD protocol state machine on CC (BMC-coded packets, GoodCRC timing, Source_Capabilities parsing, Request, contract management). This is not doable with discrete logic; it needs either a PD-capable MCU/PHY plus firmware, or one of the standalone "sink trigger" controllers below, which run autonomously with the requested PDOs (power data objects — the voltage/current tuples a source offers) set by non-volatile memory or resistor straps.

| Part | Maker / status | Package | Price and stock (checked 2026-09-02) | Behaviour on a non-PD port |
|---|---|---|---|---|
| STUSB4500 | STMicroelectronics; distributor listings active (ST's own page was unreachable during this research — status unconfirmed at source) | QFN-24-EP 4×4 mm | LCSC: 4,003 in stock; $2.25 @1, $1.92 @10, $1.51 @100 ([LCSC C2678061](https://lcsc.com/product-detail/USB-ICs_STMicroelectronics-STUSB4500QTR_C2678061.html)) | Behaves as a Type-C sink; runs from VBUS in dead-battery mode; 3 NVM-configurable sink PDOs, "doesn't need any software to run (it is autonomous)" ([ST's usb-c GitHub](https://github.com/usb-c/STUSB4500), [datasheet](https://www.st.com/resource/en/datasheet/stusb4500.pdf)). 5 V-only fallback should be verified on the bench — the README does not state it explicitly. |
| STUSB4500**L** | STMicroelectronics | QFN-24 | Listed at DigiKey/RS ([DigiKey STUSB4500LBJR](https://www.digikey.com/en/products/detail/stmicroelectronics/STUSB4500LBJR/10709022)) — price quote required | Not a PD chip at all: Type-C 5 V sink controller up to 3 A, the "CC comparator chip" option ([ST page](https://www.st.com/en/interfaces-and-transceivers/stusb4500l.html)) |
| CYPD3177 (EZ-PD BCR, "Barrel Connector Replacement") | Infineon (ex-Cypress); active, in volume stock | QFN-24 | DigiKey: 6,825 in stock; $2.07 @1, $1.244 @100 ([DigiKey CYPD3177-24LQXQ](https://www.digikey.com/en/products/detail/infineon-technologies/CYPD3177-24LQXQ/10238328)); also Newark 2,789 @ $1.97, Arrow 670 @ $2.11 (via [Octopart](https://octopart.com/cypd3177-24lqxq-cypress+semiconductor-102743253)) | No firmware; min/max voltage and current set by resistor dividers. On a Type-C-only (no-PD) source "it will pass 5 V and not have any PD negotiation"; on a legacy Type-A adapter it falls back to D+/D− (BC1.2-style) detection; on a failed contract SAFE_PWR_EN asserts and it defaults to 5 V/900 mA ([Infineon community answers](https://community.infineon.com/t5/EZ-PD-USB-Type-C/How-does-the-CYPD3177-EZ-PD-BCR-treat-legacy-and-quot-USB-C-only-quot-charging/td-p/74639), [BCR FAQ](https://community.infineon.com/t5/Knowledge-Base-Articles/EZ-PD-Barrel-Connector-Replacement-BCR-FAQs/ta-p/289954)) |
| CH224K | WCH (Jiangsu Qin Heng); current, widely used in hobby "PD trigger" boards | ESSOP-10 | LCSC: 3,684 in stock; $0.49 @1, $0.28 @100 ([LCSC C970725](https://www.lcsc.com/product-detail/USB-PD_WCH-Jiangsu-Qin-Heng-CH224K_C970725.html)) | Requests 9/12/20/28 V by logic pins or one resistor; supports PD 3.0/2.0 **and** BC1.2 and legacy divider schemes; if nothing negotiates, output stays at the 5 V VBUS ([WCH product page](https://www.wch-ic.com/products/CH224.html), [datasheet](https://components101.com/sites/default/files/component_datasheet/WCH_CH224K_ENG.pdf), [family overview](https://done.land/components/power/powersupplies/usb/usbtriggers/ch224/)) |
| CH221K | WCH | SOT-23-class small package | LCSC/AliExpress-tier availability; quote required | PD 2.0/3.0 only, single-resistor voltage select; predecessor to CH224K ([SnapEDA datasheet page](https://www.snapeda.com/parts/CH221K/WCH/datasheet/)) |

Findings, PD-specific: a PD contract at 9 V or higher is only possible if the source offers a 9 V PDO. Host data ports on PCs, laptops and Macs are 5 V sources; the higher-voltage PDOs live on charger-side ports (a dock's dedicated charging port, a monitor's upstream host port). See section 5 and 6.

Assessment: for the 60, PD chips buy little on real host ports (they will nearly always conclude a 5 V contract or fall back to Type-C 5 V), but the CYPD3177's behaviour — resistor-configured, no firmware, clean 5 V/900 mA safe fallback, deep stock at ~$1.24 @100 — makes it the best "belt and braces" candidate if PD is wanted at all. CH224K is a fifth the price and fine electrically, but it is a Chinese-domestic part with thinner documentation and no compliance pedigree; acceptable for the standard build's experiments, harder to defend in a premium product's BOM (bill of materials). The cheapest correct architecture may be no PD chip at all: Rd + CC comparator (or STUSB4500L) and a 5 V-only power budget.

---

## 5. BC1.2 (Battery Charging 1.2) — relevance (findings)

BC1.2 defines three port types: SDP (Standard Downstream Port — normal data port, 500 mA rules), CDP (Charging Downstream Port — full USB 2.0 data **and** up to 1.5 A), DCP (Dedicated Charging Port — D+/D− shorted, 1.5 A, no data). Detection is a two-stage voltage handshake on D+/D− before enumeration; primary detection separates SDP from charging ports, secondary separates CDP from DCP. Sources: [Microchip BC1.2 support article](https://support.microchip.com/s/article/BC1-2-SDP-CDP-DCP), [Microchip AN1905](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/00001905C.pdf), [TI SLVAE17A (TPS65987D BC1.2 implementation)](https://www.ti.com/lit/an/slvae17a/slvae17a.pdf).

Assessment: for a data device, DCP is irrelevant (no data). CDP matters only on the shrinking set of Type-A "charging" ports on motherboards, docks and monitors. On Type-C, the CC advertisement supersedes it: BC1.2 detection is only worth running when CC reads Default Rp — the Chromium OS reference states the default advertisement "indicates that the power sink needs to use some other method of finding what current the power source can provide. This method could be BC1.2" ([Chromium OS reference](https://www.chromium.org/chromium-os/developer-library/reference/hardware/cable-and-adapter-tips-and-tricks/)). Worth having only if it comes free inside another chip (as in CH224K); not worth a dedicated IC.

---

## 6. What real ports supply — evidence, then estimate

### Evidence (findings)

**Desktop motherboards.**
- Rear and front Type-A: 500 mA (USB 2.0) / 900 mA (USB 3.x) per spec; front-panel USB 3.0 header rated 900 mA × 5 V = 4.5 W per port ([Tom's Hardware header thread](https://forums.tomshardware.com/threads/usb-3-1-gen2-motherboard-header-amps.3688074/)). Protection is typically ganged polyfuses; real tolerance ~1–1.5 A ([Hackaday, 2024](https://hackaday.com/2024/07/03/usb-and-the-myth-of-500-milliamps/)).
- Rear Type-C: present on most current mid/high-end boards; current advertisement is vendor-specific and rarely published. Some ASUS boards advertise fast-charge (Quick Charge 4+, up to 60 W) on specific Type-C ports ([ASUS motherboard filter page listing rear Type-C](https://www.asus.com/us/motherboards-components/motherboards/all-series/filter?Spec=600)); the typical unmarked rear Type-C port should be assumed Default (900 mA) unless measured.

**Windows laptops.**
- Dell states its Latitude/Precision USB-C ports "supply a single voltage of 5 V and a maximum current of 3 A" (15 W), with a BIOS power-saving option that limits ports to 1.5 A (7.5 W), and reduced current on second/third ports and on battery ([Dell KB 000224141](https://www.dell.com/support/kbdoc/en-us/000224141/power-delivery-capabilities-of-usb-c-ports-on-latitude-and-precision-laptops)).
- Thunderbolt 3: 15 W required on the "first" port, 7.5 W on others; Thunderbolt 4: 15 W on all ports; plain USB4: minimum drops to 7.5 W ([Windows Central TB4/USB4 comparison](https://www.windowscentral.com/thunderbolt-4-usb4-usb), [USB4/TBT3 compatibility spec, usb.org](https://www.usb.org/sites/default/files/USB4%E2%84%A2%20Thunderbolt3%E2%84%A2%20Compatibility%20Requirements%20Specification%20Rev%201.0%20-%2020210129_0.pdf)).

**Macs.** Apple's user-facing documentation does not publish port output wattage ([About USB-C on Mac](https://support.apple.com/en-is/guide/mac-help/mchl447b9239/11.0/mac/11.0)). All current Macs carry Thunderbolt 4/5 or USB4 ports, so the Thunderbolt/USB4 minimums above (15 W / 7.5 W) are the applicable floor. Community measurements and accessory-compatibility threads are consistent with 15 W (5 V/3 A) on Apple Silicon Thunderbolt ports ([MacRumors thread](https://forums.macrumors.com/threads/usb-power-output-of-m1-and-m2-macbook-usb-c-thunderbolt-ports.2356508/) — forum evidence, not vendor data).

**Docks and monitors.**
- CalDigit TS4 (a common premium desk dock): downstream Thunderbolt 4/USB4 ports 15 W (5 V/3 A); downstream USB-C data ports 7.5 W (5 V/1.5 A); one front 20 W charging port (5 V/3 A, 9 V/2.22 A) ([CalDigit TS4 power delivery profiles](https://www.caldigit.com/ts4s-power-delivery-profiles/)).
- Dell UltraSharp hub monitors (U2723QE, U2724DE): downstream USB-C data port rated 15 W ([Dell U2723QE product page](https://www.dell.com/en-us/shop/dell-ultrasharp-27-4k-usb-c-hub-monitor-u2723qe/apd/210-bdpf/monitors-monitor-accessories)).
- Apple Studio Display: the upstream Thunderbolt port delivers 96 W to the host; its three downstream USB-C ports' wattage is not published by Apple ([Studio Display specs](https://www.apple.com/studio-display/specs/); [community reports of 15 W-class accessories failing on the downstream ports](https://forums.macrumors.com/threads/studio-display-usb-c-port-wattage.2341746/)).

**9 V-and-up PD from host-side ports:** the only sighting in the evidence above is the dock's dedicated *charging* port (CalDigit's 20 W front port). No motherboard, laptop or monitor *data* port in the evidence offers more than 5 V to a downstream device.

### Estimate (assessment — built from the inputs above, not data)

Assumed buyer profile: audiophile/desk-setup owner, hardware ≤ ~6 years old, connecting the 60 to whichever port is convenient — laptop or Mac direct, dock/monitor, or desktop rear panel. Inputs: the vendor floors above (Thunderbolt 15 W, USB4 7.5 W, Dell 15 W/7.5 W, dock 7.5–15 W, monitor 15 W), the unknown-but-assumed-Default desktop rear Type-C, and the 4.5 W Type-A ceiling.

- **>500 mA at 5 V available in practice:** essentially every port (~100%) — either legitimately (900 mA USB 3.x, Type-C advertisement) or by polyfuse headroom. But only ~"all Type-C + USB 3.x Type-A" (est. 90%+ of this buyer's ports) give it *within spec*.
- **≥1.5 A (7.5 W) via Type-C advertisement:** est. 80–95% of the Type-C ports this buyer would plug into (all Thunderbolt/USB4 laptop and Mac ports, dock and monitor downstream Type-C; the main shortfall is desktop rear Type-C of unknown advertisement and BIOS-limited laptop ports).
- **≥3 A (15 W):** est. 50–75% of those Type-C ports (Thunderbolt 3 first port / all TB4 ports, Dell 3 A ports, monitor 15 W ports; excludes plain-USB4 7.5 W ports, dock USB-C data ports, and limited configurations).
- **PD at 9 V or above from the port the device will actually live on:** est. under 10%, and not something the product can require. 9 V exists mainly on charging-designated ports, not data ports.
- **Type-A-only connection (adapter or old desktop):** a real minority case that caps the device at 4.5 W in-spec; est. 10–25% of installs, dominated by desktop users who route to the rear panel.

Design implication (assessment): the architecture must be fully functional at **4.5 W** (USB 3.x enumerated, or Default-Rp Type-C), reach full feature set at **7.5 W** (1.5 A advertisement), and treat **15 W** as opportunistic headroom (motor feel intensity, halo brightness, supercapacitor charge rate). A 10 W-minimum architecture would strand a meaningful fraction of real desks.

---

## 7. Sink-side decision tree (findings + assessment)

The standard ordering, per the Type-C ecosystem documentation already cited (TI SLVA704; Chromium OS reference; Infineon BCR behaviour):

1. **On attach, read CC.** If Rp indicates 3.0 A → budget 15 W. If 1.5 A → budget 7.5 W. Keep monitoring CC: the advertisement is dynamic and the sink must shed load if it drops.
2. **If a PD source is present** (PD messaging seen on CC), the negotiated contract replaces the advertisement. A standalone sink controller (section 4) does this without firmware; the result is still almost always 5 V on a host port.
3. **If CC reads Default Rp** (56 kΩ / 80 µA) or the connection is via a Type-A adapter: optionally run BC1.2 detection on D+/D− — a CDP (Charging Downstream Port) grants 1.5 A. The Chromium OS reference is explicit that Default Rp is the case where "the power sink needs to use some other method" such as BC1.2 ([source](https://www.chromium.org/chromium-os/developer-library/reference/hardware/cable-and-adapter-tips-and-tricks/)).
4. **Otherwise fall back to enumerated USB:** 100/150 mA until configured, then 500 mA (USB 2.0) or 900 mA (USB 3.x) per the unit-load rules of USB 2.0 §7.2.1 ([Beyond Logic](https://www.beyondlogic.org/usbnutshell/usb2.shtml)).
5. **Never draw the higher advertised/BC1.2 current while the port says Default and the device is enumerated for less** — that is the one genuinely non-compliant behaviour a host can punish (over-current trip, port or system shutdown, section 2).

Assessment for the 60: step 1 alone (a CC comparator or STUSB4500L-class part feeding the power management) plus step 4 (honest `bMaxPower` handling in firmware) covers >90% of the estimated port population; steps 2–3 are refinements to buy only if the power architecture actually needs 9 V or the Type-A/CDP corner.

---

## 8. Compliance — section G of the brief

### 8.1 USB-IF (USB Implementers Forum) (findings)

- **Certification is voluntary; the logo is not.** The USB-IF logos may only be used on products that have passed USB-IF compliance testing and are on the Integrators List, which requires a USB Vendor ID. Logo licence: US$3,500 for a two-year term for non-members, waived for members ([usb.org logo licence](https://www.usb.org/logo-license)).
- **Vendor ID:** US$6,000 to purchase standalone without the logo agreement ([usb.org, Getting a Vendor ID](https://www.usb.org/getting-vendor-id)). Compliance program details: [usb.org/compliance](https://www.usb.org/compliance).
- Drawing >500 mA (or >900 mA on 3.x) without Type-C/BC1.2/PD justification violates the USB specification's power rules (section 2) — this matters for certification but is not separately policed.
- Enforcement reality is trademark-shaped: shipments *bearing USB logos* have been detained at customs pending proof of authorisation ([industry account, aiiconn](https://www.aiiconn.com/news-detail.asp?seq=32) — single-source, treat as anecdotal).

Assessment for a 60-unit run: skip USB-IF certification and **do not print any USB-IF logo or "certified" language** on the device, packaging or marketing — describe ports functionally ("USB-C", used descriptively; this is a judgement, not legal advice). The obligations that remain: acquire a legitimate Vendor ID (US$6,000) or a licensed sub-allocation rather than squatting a VID/PID, and be spec-honest in power behaviour (sections 2–7), because that is what protects customers' machines. Risk of *not* certifying at 60 units: effectively nil beyond the logo prohibition.

### 8.2 CE (Conformité Européenne, EU) and FCC (Federal Communications Commission, US) (findings)

- **EU EMC (electromagnetic compatibility):** the EMC Directive 2014/30/EU applies; harmonised standards for multimedia equipment are EN 55032 (emissions) and EN 55035 (immunity — ESD, radiated RF, EFT/burst, surge, dips) ([TÜV SÜD overview](https://www.tuvsud.com/en-gb/services/testing/electromagnetic-compatibility-testing/emc-testing-multimedia-equipment)). CE under the EMC Directive is self-declared (manufacturer's Declaration of Conformity backed by a technical file); no notified body required.
- **The Low Voltage Directive 2014/35/EU does not apply** — its scope starts at 75 V DC; a 5 V (even 20 V PD) USB device is below it. Safety expectations are instead carried by IEC/EN 62368-1 (audio/video and ICT equipment safety), under which a USB-powered circuit classifies as ES1 (electrical energy source class 1, touchable) and PS1 (<15 W) or PS2 (≤100 W) power source ([UL 62368-1 classification brief](https://japan.ul.com/wp-content/uploads/sites/27/2014/06/1_techbrief_classandele_measurement.pdf), [Element overview](https://www.element.com/nucleus/2020/en-62368-standard-update-information)). RoHS 2011/65/EU and WEEE registration apply regardless of run size; UKCA mirrors CE for Great Britain.
- **US:** FCC Part 15 Subpart B, unintentional radiator, via SDoC (Supplier's Declaration of Conformity) — testing at any competent lab, no FCC filing, a US responsible party named. One ANSI C63.4/CISPR 32 test campaign substantially covers FCC 15B, EN 55032, ICES-003 (Canada) and AS/NZS at once ([Compliance Testing cost guide](https://www.celectronics.com/Resources/EMC-Testing-Cost-Guide), [FCC 15B page](https://www.celectronics.com/FCC-Part-15B-Unintentional-Radiator-Testing)).
- **Does PD change anything?** No — negotiating 9 V or 20 V over CC changes neither the EMC class nor Low Voltage Directive scope (still <75 V DC). It adds the PD front-end switcher as an emissions source to be tested as-configured.
- **Radio warning (assessment, flag for a ruling):** the 60's candidate board (Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C) carries a Wi-Fi/Bluetooth radio module. If any radio ships enabled, the EU Radio Equipment Directive 2014/53/EU replaces the EMC-Directive route and FCC Part 15C (intentional radiator) applies — Part 15C requires certification with an FCC ID, which pre-certified modules with modular approval exist to satisfy. If the 60 ships USB-only with radios permanently disabled, the unintentional-radiator route stands. This fork changes cost and paperwork materially.
- **Typical lab cost for this class** (from lab-published guides, not quotes): FCC SDoC alone ~US$500–1,500; a combined FCC 15B + EN 55032/55035 CE campaign runs higher (immunity adds 1–2 lab shifts), complex multi-market programs to US$25,000; timeline 1–3 weeks ([cost guide](https://www.celectronics.com/Resources/EMC-Testing-Cost-Guide), [MarkReady EMC guide](https://markready.io/guides/emc-testing)). A figure for the 60 specifically is **quote required**.

Assessment — what a 60-unit run buys vs self-declares: pay a lab for one combined emissions + immunity campaign on a production-representative unit (satisfying FCC 15B SDoC and grounding the CE Declaration of Conformity), self-declare CE/UKCA on that evidence, hold the technical file, register for WEEE where sold. A formal IEC 62368-1 certification (CB report) is not legally required for this device in EU/US and is out of proportion at 60 units; design to its ES1/PS2 principles and document that in the file.

### 8.3 Supercapacitor bank — transport and safety (findings)

- Electric double-layer capacitors are dangerous goods **UN 3499, Class 9** only when energy storage capacity exceeds **0.3 Wh**; at or below 0.3 Wh they are not subject to dangerous-goods regulations (IATA/ADR) ([Honeywell DGR note](https://sps-support.honeywell.com/s/article/Do-Capacitors-reside-under-the-dangerous-good-regulations-DGR), [HazMat Tool UN 3499](https://www.hazmattool.com/info.php?a=Capacitor%2C+electric+double+layer+with+an+energy+storage+capacity+greater+than+0.3+Wh&b=UN3499&c=9), [ANA Cargo EDLC guidance](https://www.anacargo.jp/en/int/news/restriction/2012/pdf/120703-1-2.pdf)).
- Arithmetic on the contemplated bank (calculation from E = ½CV², not a sourced figure): 5 F at 5 V = 62.5 J = **0.017 Wh**; 25 F at 5 V = 312.5 J = **0.087 Wh**. Both far under 0.3 Wh; the line is only approached above ~85 F at 5 V.
- Lithium-battery regimes (UN 38.3 test reports, IATA lithium provisions) do not apply — those are for lithium cells. Hybrid **lithium-ion capacitors** are a different case with their own guidance ([Abracon UN/IATA note](https://abracon.com/uploads/resources/UN-IATA-Transportation-Guidelines.pdf)); avoid them and this stays simple.
- Capacitors must still vent safely, and the bank enters the IEC 62368-1 energy-source analysis in the safety file.

Assessment: a few farads at 5 V is transport-trivial — no dangerous-goods marking, no carrier restrictions, air-shippable. A genuine advantage of the supercapacitor architecture over any lithium buffer, which would drag in UN 38.3 testing and carrier paperwork at any size. Worth recording in `docs/DECISIONS.md` when the energy-buffer decision is made.

---

## 9. Confidence and gaps

**High confidence (multiple/authoritative sources):** unit-load rules (100/500 mA, 150/900 mA); Rp values 56/22/10 kΩ and 80/180/330 µA with sink thresholds; Thunderbolt 15 W / USB4 7.5 W minimums; CYPD3177 behaviour and price/stock; CH224K price/stock; UN 3499 0.3 Wh threshold; USB-IF logo US$3,500 and Vendor ID US$6,000; FCC 15B SDoC / EN 55032+55035 CE routing.

**Medium confidence:** STUSB4500 lifecycle status (distributors stock and sell it; ST's own page was unreachable twice during this research — confirm "Active" at source before designing in). STUSB4500 5 V-only fallback wording (implied by Type-C sink + dead-battery operation; verify on datasheet or bench). Mac downstream-port wattages (spec-floor reasoning plus forum measurements; Apple publishes nothing). Desktop rear Type-C advertisement levels (no published vendor data found — treat as Default until measured).

**Gaps / next actions:**
1. **Measure, don't model, the desktop Type-C case:** a cheap USB-C tester across the studio's own boards (ASUS/MSI rear Type-C, front-panel Type-C, a couple of docks) would replace the weakest estimate input with data.
2. STUSB4500L exact price: listed at DigiKey/RS but not price-checked here — quote required.
3. The radio question (section 8.2) needs a ruling: USB-only vs enabled Wi-Fi/Bluetooth flips the certification route (EMC Directive + FCC 15B SDoC vs Radio Equipment Directive + FCC 15C certification/modular approval).
4. EMC lab quotes for a combined FCC 15B + EN 55032/55035 campaign: quote required.
5. The port-distribution estimate in section 6 is an estimate built from the cited vendor floors and one dock/monitor sample each; no published survey of host-port power output was found.
