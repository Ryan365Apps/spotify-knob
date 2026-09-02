# Research findings — strand D/E/F: magnet-carrier actuator, halo at lower power, heat

Scope: the 60 by Cadrane (Ø135 × 34 mm desk dial, sealed, steel base, aluminium knob ring, one USB-C cable at 2.5–15 W). Written 2026-09-02. Every number is either cited to a datasheet/vendor/standard with URL, or explicitly marked **[estimate]** with the working shown. Findings are separated from assessment in each section.

---

## D. The magnet-carrier actuator

Requirement restated: move the magnet carrier ~3 mm in ~100 ms, several times a minute in the worst mode, and hold position **unpowered** at both ends of travel.

### D1. Fast N20-class gearmotor + cam — findings

Cam kinematics (working, not vendor data): a cam that delivers 3 mm of lift over **half a revolution** needs 0.5 rev / 0.1 s = 5 rev/s = **300 RPM** at the output shaft. Over a quarter revolution: 150 RPM. Over a full revolution: 600 RPM.

Pololu (the vendor of the reference N20-class "micro metal gearmotor" family) publishes exact no-load speed and current per ratio ([Pololu micro metal gearmotor category](https://www.pololu.com/category/60/micro-metal-gearmotors)):

| Variant | Ratio | No-load RPM @ 6 V | Free-run current | Stall current @ 6 V | Stall torque |
|---|---|---|---|---|---|
| HP 6V (high power) | 30:1 | 1,000 | — | 1.6 A | 0.57 kg·cm |
| HP 6V | 50:1 | 590 | — | 1.6 A | 0.86 kg·cm |
| HP 6V | 100:1 | 310 | — | 1.6 A | 1.7 kg·cm |
| MP 6V (medium power) | 30:1 | 720 | 70 mA | 0.67 A | 0.33 kg·cm |
| LP 6V (low power) | 50:1 | 270 | — | 0.36 A | 0.44 kg·cm |

(MP 30:1 row from the [Pololu #2364 product page](https://www.pololu.com/product/2364), which also states the general guidance: *"a general recommendation for brushed DC motor operation is 25% or less of the stall current."*)

Which ratios reach 300 RPM at 5 V (working): brushed-motor no-load speed scales roughly linearly with voltage, so multiply the 6 V figures by 5/6 **[estimate — standard DC-motor scaling, not a datasheet row]**:

- HP 100:1 → ~258 RPM at 5 V: marginal (116 ms per half-rev unloaded; slower under load). **Fails the 100 ms target under load.**
- HP 50:1 → ~490 RPM at 5 V: 61 ms per half-rev unloaded; meets 100 ms with load margin. **Best fit.**
- HP or MP 30:1 → ~600–830 RPM at 5 V: 36–50 ms per half-rev; large speed margin, less torque (0.33–0.57 kg·cm stall at 6 V = 32–56 mNm).

Current while moving: at Pololu's recommended ≤25% of stall — HP 6V stall scaled to 5 V ≈ 1.33 A **[estimate, linear scaling]** → **~0.33 A moving current** (plus ~0.1 A free-run baseline); MP 6V stall at 5 V ≈ 0.56 A → **~0.14 A** moving current.

Energy per move (working, **[estimate]**): 5 V × 0.4 A × 0.1 s ≈ **0.2 J** (HP); 5 V × 0.2 A × 0.1 s ≈ **0.1 J** (MP).

Stall risk: if the cam jams, an HP motor at 5 V dissipates ~5 V × 1.33 A ≈ **6.7 W** in a 10 × 12 × 26 mm motor — it will cook. Needs a firmware current limit or move-timeout. The MP variant stalls at ~2.8 W, much more survivable.

Holding: the spur gearbox is not stated to be self-locking (Pololu does not claim it; spur trains at these ratios are generally back-drivable). **Unpowered hold must come from cam geometry**: a dwell flat (zero-slope region) at each end of the cam profile means the carrier load produces no torque about the cam shaft — the mechanism parks. This costs nothing and is the standard cam trick; hold power = **0 W** by geometry, not by the gearbox.

### D2. Solenoid + mechanical latch (bistable/latching solenoid) — findings

Latching ("keep") solenoids hold both end positions with an internal permanent magnet, so hold power is **0 W** by construction; a current pulse of one polarity throws them, the reverse polarity returns them ([TLX Technologies, latching solenoid theory](https://www.tlxtech.com/solenoid-theory/latching-solenoid-theory)).

Real parts found:

- **Takaha TPP CG0836** bistable latching solenoid ([Takaha TPP solenoid page](https://takaha-japan.com/pages/tpp-solenoid)): stroke **5 mm**, holding force **10 N** with no voltage (permanent magnet), throw force 2.4 N one way / 2.7 N the other, energizing time **~20 ms**, size **23.0 × 23.0 × 36.8 mm**, $31.43. Takaha's product pages state 5 V models exist in the range and that pulse drive of 20–50 ms is the intended mode ([Takaha products page](https://takaha-japan.com/pages/products); [Takano latching solenoid overview](https://takano-usa.com/latching-soloenoid/)). Coil resistance/current for the CG0836 is not published on the page — **quote required**.
- **Takaha CA0315** (plain pull solenoid, for scale of the small end): 8 × 10 × 15 mm, 6 g, max stroke 3 mm, but force at nominal stroke only **0.05 N at 100% duty / 0.62 N at 6% duty** ([Takaha CA0315](https://takaha-japan.com/products/ca0315)). This shows the physics problem: solenoid force collapses with stroke, and a 3 mm-stroke solenoid small enough to be trivial to package has almost no force at the start of the stroke.

Energy per pulse (working, **[estimate]** — coil figures unpublished): a small latching solenoid driven at 5–10 W coil power for its rated 20–50 ms pulse takes 5–10 W × 0.02–0.05 s ≈ **0.1–0.5 J** per throw. Peak current at 5 V would be 1–2 A for those tens of milliseconds **[estimate]**.

Packaging: the CG0836's 36.8 mm dimension exceeds the 34 mm device height, so it can only lie flat (radially or tangentially); with the display disc and main board in the middle of the device, a 23 × 23 × 37 mm block on the base plate is plausible but not free. Whether a *smaller* latching solenoid delivers 3 mm of stroke at a force that beats the magnet carrier's own attraction to the sixty steel poles is exactly the bench-rig question — the carrier load force is currently unmeasured (open questions A–F in `docs/DECISIONS.md`, the bench-rig list).

### D3. Voice coil actuator — findings

Reference part: **Moticont LVCM-016-010-01** linear voice coil motor, datasheet drawing fetched directly ([Moticont product page](https://www.moticont.com/lvcm-016-010-01.htm); [datasheet PDF](https://www.moticont.com/pdf/lvcm-016-010-01.pdf)):

- Stroke **3.2 mm**; body Ø15.9 × 9.5 mm (+ coil overhang); coil 5 g, body 7 g.
- Force constant **1.1 N/A**; coil resistance **1.8 Ω**; continuous force **1.6 N** (max continuous power **4.0 W**); intermittent force **5.2 N at 10% duty**.

Working: to move 3 mm it is far faster than needed — at 5 N on a ~20 g moving mass, a = 250 m/s², t = √(2×0.003/250) ≈ 5 ms. Current for 1.6 N = 1.6/1.1 = **1.45 A** (2.6 V across 1.8 Ω — fine from 5 V). Energy per move with a generous 50 ms powered window at ~3.8 W ≈ **0.2 J** **[estimate]**.

Holding: a voice coil has **zero unpowered detent**. Holding 1 N of carrier load takes 0.91 A → **1.5 W continuously** — this fails the requirement outright. The fix is magnetic or mechanical end-latches, at which point the assembly is a hand-rolled latching solenoid (section D2) with a better force profile. Noted as required, not assumed away.

### D4. Piezo actuators — findings

Multilayer piezo stack travel is **0.1–0.15% of stack length** ([Physik Instrumente, displacement modes of piezo actuators](https://www.physikinstrumente.com/en/expertise/technology/piezo-technology/properties-piezo-actuators/displacement-modes); [PI Ceramic](https://www.piceramic.com/en/expertise/piezo-technology/properties-piezo-actuators/forces-stiffnesses)). 3 mm of direct stroke would need a 2–3 m stack. Amplified (lever/flexure) piezo actuators reach hundreds of micrometres, still an order of magnitude short. Piezo *motors* (ultrasonic/inchworm types) can do 3 mm and hold unpowered by friction, but they are precision-instrument parts with drive electronics at 100+ V.

### D5. Shape-memory alloy (SMA) wire — findings

Dynalloy Flexinol (the reference nickel-titanium — Nitinol — actuator wire) figures, from the vendor table ([RobotShop-hosted Dynalloy Flexinol technical data](https://cdn.robotshop.com/media/d/dyn/rb-dyn-13/pdf/flexinol-technical-data.pdf); [Dynalloy technical data page](https://dynalloy.com/technical-data-wires/)):

- Repeatable contraction **2–6% of wire length** for "tens of millions of cycles" when kept inside stress guidelines.
- 0.006" (0.15 mm) wire: 1.3 Ω/inch, max pull 330 g (≈3.2 N), **400 mA for a 1-second contraction**, cooling ("off") time **2.0 s (70 °C LT wire) / 1.2 s (90 °C HT wire)**.
- 0.003" (0.076 mm) wire: 5.0 Ω/inch, 80 g pull (≈0.78 N), 100 mA/1 s, cooling 0.5 s (LT) / 0.2 s (HT).

Working: 3 mm at 3–4% contraction needs **75–100 mm of wire** (routed around a pulley or the arc of the base). A 100 ms contraction needs a much larger pulse than the 1-second current; Dynalloy states contraction time is directly related to current input ([Dynalloy technical characteristics PDF](https://www.mouser.com/datasheet/2/813/TCF1140-2489969.pdf)) — roughly the same heat delivered ~10× faster ≈ 1.5–2 A pulse for 0.006" wire **[estimate]**. Energy per move: 100 mm of 0.006" wire ≈ 5.1 Ω; heating it to transition ≈ 0.4 A² × 5.1 Ω × 1 s ≈ **0.8 J** whether delivered slowly or fast **[estimate from the vendor 1-s figures]**.

Cycle rate: limited by **cooling**, not heating — 1.2–2.0 s off-time for 0.006" wire means ≈ 20–30 moves/minute maximum; "several times a minute" passes, with little margin if two wires (antagonistic pair) fire alternately.

Holding: SMA holds only while hot (powered) in the contracted direction; a bias spring holds the other end. Unpowered hold at **both** ends again requires a latch or over-centre spring.

### D — actuator comparison table

| Type | Example part | Stroke | Move time | Peak current @ 5 V | Energy/move | Hold power | Source |
|---|---|---|---|---|---|---|---|
| N20 gearmotor + cam | Pololu HP 6V 50:1 (or MP 30:1) | 3 mm via cam (free choice) | ~60–100 ms (half-rev cam) | ~0.3–0.4 A moving; 1.33 A stall fault [estimate from stall spec] | ~0.1–0.2 J [estimate] | 0 W (cam dwell flats) | [Pololu category](https://www.pololu.com/category/60/micro-metal-gearmotors), [#2364](https://www.pololu.com/product/2364) |
| Latching solenoid | Takaha TPP CG0836 | 5 mm | ~20–50 ms pulse | 1–2 A pulse [estimate; coil data: quote required] | 0.1–0.5 J [estimate] | 0 W (permanent magnet, 10 N hold) | [Takaha TPP](https://takaha-japan.com/pages/tpp-solenoid) |
| Voice coil | Moticont LVCM-016-010-01 | 3.2 mm | 5–50 ms | 1.45 A (1.6 N) to 4.7 A (5.2 N pk) | ~0.2 J [estimate] | **~1.5 W** (fails; needs added latch) | [Moticont](https://www.moticont.com/lvcm-016-010-01.htm) |
| Piezo stack | (any; PI/PI Ceramic app data) | 0.1–0.15% of length → µm class | µs–ms | n/a | n/a | 0 W | [PI](https://www.physikinstrumente.com/en/expertise/technology/piezo-technology/properties-piezo-actuators/displacement-modes) |
| SMA wire | Dynalloy Flexinol 0.006" × ~100 mm | 3 mm (4% of 75–100 mm) | ~100 ms hot [estimate]; 1.2–2 s cool | ~1.5–2 A pulse [estimate]; 0.4 A for 1-s move (vendor) | ~0.8 J [estimate] | 0 W one end (spring); needs latch for both | [Flexinol data](https://cdn.robotshop.com/media/d/dyn/rb-dyn-13/pdf/flexinol-technical-data.pdf) |

### D — energy economics: move-per-gesture vs continuous detent cancellation

The alternative to moving the carrier is the ring motor cancelling the magnetic detent continuously while scrolling, at the stated **1–4 W sustained** (given range, from the product context — not re-derived here).

Arithmetic, all steps shown, per-move energy from the table (**[estimate]** figures carried through):

- **Cost of one carrier round trip** (drop + raise, N20 route): 2 × 0.2 J = **0.4 J**.
- **Break-even scroll duration**: 0.4 J ÷ 1 W = **0.4 s**; 0.4 J ÷ 4 W = **0.1 s**. Any scroll gesture longer than 0.1–0.4 s is cheaper served by moving the carrier once than by cancelling the detent for its duration. Real scroll gestures are seconds long.
- **Typical hour**: worst-mode carrier use at 6 moves/minute = 360 moves/hour × 0.2 J = **72 J/h** (mean draw 20 mW). Ring-motor cancellation for a modest 5 minutes of accumulated scrolling per hour = 300 s × (1–4 W) = **300–1,200 J/h**. Even at only 30 s of scrolling per hour (30–120 J/h), cancellation is comparable at 1 W and worse at 4 W; at any realistic scrolling time it loses by 4× to 60×.
- **Worst moment (peak draw)**: cancellation is a *sustained* 0.2–0.8 A at 5 V for the whole gesture. The carrier actuators peak higher for far shorter: N20 ≈ 0.4 A for 100 ms (comparable to cancellation, shorter), latching solenoid 1–2 A for 20–50 ms, voice coil up to 4.7 A for milliseconds. Pulse peaks of this size are a bulk-capacitor problem, not a USB-C budget problem; the sustained 1–4 W of cancellation is the real budget line — and (see section F) it is dissipated as heat in coils near the rim.

**Assessment (D).** The N20-class gearmotor + cam with dwell flats already meets every line of the requirement: speed (50:1 HP or 30:1 MP at 5 V), zero unpowered hold by geometry, ~0.1–0.2 J per move, one moving part, and the only real risk (stall on jam) is a firmware current-limit away from solved. The Takaha-style latching solenoid is the credible challenger — faster, zero hold by magnet, but the small-package force-vs-stroke problem means the specific part must be force-tested against the measured carrier load (unmeasured; bench-rig item), and coil data is quote-required. Voice coil and SMA both fail unpowered hold without a bolted-on latch; piezo is not realistic at 3 mm. On energy, moving the carrier per gesture beats continuous cancellation by more than an order of magnitude over an hour and roughly ties it at the worst instant; this supports decision 19 (that dynamic detent strength comes from the motor) being reserved for *feel*, not used as a substitute for the carrier during long scrolls.

---

## E. The halo at lower power

### E1. SK6812 RGBW per-LED currents — findings

From the SK6812RGBW specification (OPSCO, Rev 01, hosted by Adafruit — [datasheet PDF](https://cdn-shop.adafruit.com/product-files/2757/p2757_SK6812RGBW_REV01.pdf)):

- Package: 5050 (5.5 × 5.0 × 1.6 mm), rated description "**0.25 Watt** power"; supply 3.5–5.5 V absolute max, typical VDD 5.2 V.
- Internal PWM (pulse-width modulation) frequency: **1.2 kHz typical** — well above flicker-visibility at any duty.
- **Static current 1 mA typical per LED even when dark** (IDD, "static power consumption").
- Output stage is fixed constant-current (test condition IOUT = 9 mA); there is no per-channel current adjustment.

Per-channel constant currents (vendor figures, consistent with the 0.25 W rating): **R/G/B 9 mA each, W 16.5 mA** ([Art LED, UCS2904 vs SK6812 RGBW](https://www.artleds.com/blog/ucs2904-vs-sk6812-rgbw); also quoted by [LED Lighting Hut](https://www.ledlightinghut.com/sk6812-rgbw-5050-smart-led.html)). Cross-check (working): (9×3 + 16.5) mA × 5.2 V ≈ 0.23 W ≈ the 0.25 W rating. Per-channel luminous intensity (mcd) is **not** published in this datasheet revision — gap.

So per LED: white via the W die alone = **16.5 mA**; white mixed from R+G+B = **27 mA**; all four on = **43.5 mA**.

### E2. Perceived brightness vs duty — findings

Human lightness perception versus luminance is strongly compressive. The CIE (Commission Internationale de l'Éclairage) 1976 lightness function is L\* = 116·(Y/Yn)^(1/3) − 16 for Y/Yn > 0.008856, and the best-fit pure power law to perception has an exponent of ~0.42 (Stevens-type) ([Wikipedia, Lightness](https://en.wikipedia.org/wiki/Lightness)).

Working — what a 20% duty cap actually looks like:

- CIE: L\* = 116 × 0.20^(1/3) − 16 = 116 × 0.585 − 16 = **51.8 → ~52% of full perceived brightness**.
- Stevens 0.42 exponent: 0.20^0.42 = **0.51 → ~51%**.
- For reference, 30% duty: L\* = 116 × 0.669 − 16 = **~62% perceived**.

So the current firmware cap at ~20% costs only about **half** the perceived brightness while saving 80% of the LED power. The two models agree within a point.

### E3. LED count vs pitch under a diffuser — findings (rules of thumb, marked as such)

From LED-strip/profile application guidance (trade sources, rules of thumb, **not** physics-derived):

- Increasing LED-to-diffuser distance blends adjacent point sources; deep channels (≥15 mm internal) let even basic opal diffusers read dot-free, and added depth beats a fancier diffuser for cost ([BRT LED profile guide](https://brt-led.com/article/choose-the-right-led-diffuser-strip-for-eliminating-hotspots/); [PTSMAKE profile guide](https://www.ptsmake.com/how-to-choose-install-led-aluminium-profiles-like-a-pro/)).
- Directly visible installations are advised at 120–240 LEDs/m (4.2–8.3 mm pitch) or COB (chip-on-board, continuous); shallow profiles demand the high-density end ([SignLite profile guide](https://www.signliteled.com/how-to-choose-the-right-led-profile-for-different-led-strips/)).
- The practical rule of thumb across these sources: **diffuser distance of the same order as the LED pitch, or greater, for a continuous line** [rule of thumb].

Applied to the 320 mm arc (working): 60 LEDs/m → 19 LEDs at 16.7 mm pitch (needs ~15 mm+ diffusion depth — unavailable in this base); 96/m → 31 LEDs at 10.4 mm; 144/m → 46 LEDs at 6.9 mm; **60 LEDs → 5.3 mm pitch**, dot-free behind roughly ≥5 mm of diffusion path [rule of thumb applied].

### E4. RGBW vs RGB for white — findings

With fixed constant-current drive, white from the dedicated W die costs **16.5 mA** versus **27 mA** for RGB-mixed white — the W die delivers white at **~40% less current**, before counting that a phosphor-converted white die also renders colour properly (the datasheet bins W at real colour temperatures, 2700–7000 K; Art LED quotes colour-rendering index Ra ≈ 80 for the white die). Datasheet lumen figures per channel are not published, so an efficacy (lumens-per-watt) comparison cannot be stated from this source — the current comparison above is the citable fact; the general point that phosphor white beats RGB-mixed white on efficacy is industry-standard but **unquantified here**.

### E5. Peak vs sustained — findings

The SK6812 is a fixed constant-current part: there is **no overdrive mode** — the datasheet's only levers are duty (the 8-bit value through its 1.2 kHz PWM) and how many LEDs are lit. Its thermal guidance is generic ("consider heat generation, stay within maximum ratings", datasheet application notes). So "pulsed overdrive for animations" per-LED does not exist for this part; what does exist is **budget-level pulsing**: a brief full-duty flash or sweep is fine for the supply as long as the *average* fits the budget and bulk capacitance covers the transient. A breathing animation whose duty averages 10% draws, by definition, half the power of a static 20% ring — animation is a power feature, not a cost.

One datasheet fact that matters at the low end: **1 mA static draw per LED**. Sixty dark LEDs idle at ~60 mA ≈ 0.3 W. If the halo has an off state that must be truly off, the strip's 5 V rail needs a load switch.

### E — assessment: target count and current budget

Built on the cited numbers above; this paragraph is assessment, not vendor fact.

- **Count: 60 LEDs** on the 320 mm arc (5.3 mm pitch). It clears the dot-free rule of thumb with only ~5 mm of diffusion depth (plausible inside the base edge), and sixty LEDs maps one-to-one onto the sixty detents — one addressable light per detent position is an interaction asset. Minimum acceptable: ~48 (6.7 mm pitch).
- **Current budget**: white ring on W channel only at 20% duty: 60 × 16.5 mA × 0.20 = **198 mA ≈ 1.0 W** — and it *reads* as ~52% of maximum brightness (section E2). At 30% duty: 297 mA ≈ 1.5 W, reading ~62%. Full-white transient flash: 990 mA ≈ 5 W for sub-second moments only. Colour states (green volume, amber seek) use one or two 9 mA channels and come in *under* the white figures. Typical animated states at ~10% average duty: ~0.5 W.
- **Verdict on the 20% cap**: it is not a perceptual problem — perception compresses 5:1 power into roughly 2:1 brightness. The generous move is not raising the cap; it is (a) using the W die instead of RGB-mixed white, (b) spending the budget on more LEDs at lower duty (smoother line, same watts), and (c) ambient-adaptive scaling — standard consumer-device practice — so the ring runs 5–10% duty in a dim room and holds 20–30% only under office lighting. Budget line for the power doc: **halo = 1.0 W sustained cap, 5 W sub-second peak, 0.3 W floor unless the rail is switched.**

---

## F. Heat

### F1. Enclosure thermal resistance to ambient — findings and working

Geometry (from `docs/CAD-BRIEF.md`, the mechanical brief): closed cylinder Ø135 × 34 mm, bottom face on the desk.

Surface areas (working):
- Side wall: π × 0.135 m × 0.034 m = **0.0144 m²**
- Top face: π × (0.0675 m)² = **0.0143 m²**
- Convecting/radiating area (top + side; bottom excluded, it sits on the desk): **≈ 0.029 m²**

Natural-convection film coefficient for enclosure surfaces: published typical range **2–10 W/(m²·K)**, with 5–8 W/(m²·K) typical for vertical surfaces ([Industrial Monitor Direct, enclosure heat-transfer analysis](https://industrialmonitordirect.com/blogs/knowledgebase/ventilated-electronics-enclosure-fea-heat-transfer-analysis); same source family covers the [radiation term](https://industrialmonitordirect.com/blogs/knowledgebase/gray-body-radiation-equation-for-electronics-enclosure-thermal-design)).

Radiation (working): linearised h_rad ≈ 4εσT³ ≈ ε × 6.1 W/(m²·K) near 300 K. Anodised aluminium and painted/oxidised steel have emissivity ε ≈ 0.8 → h_rad ≈ **~5 W/(m²·K)**; polished bare metal (ε ≈ 0.05) contributes almost nothing — a finish decision with a real thermal consequence. **[standard-physics working, not a fetched figure]**

Combined, anodised finish: h_total ≈ (5–8) + 5 ≈ 10–13 W/(m²·K) over 0.029 m² → hA ≈ 0.29–0.37 W/K → **R(case→air) ≈ 2.7–3.5 K/W**. Call it **≈ 3 K/W [estimate, working above]**. The desk adds a second path through the steel base, but a wooden desk is a poor heat sink (thermal conductivity of wood ~0.1–0.2 W/(m·K), two orders below metals); treat desk conduction as a bonus, not a design load path **[estimate]**.

So: each continuous watt raises the (assumed isothermal) case **≈ 3 °C** above ambient.

### F2. Touch-temperature limits — findings

IEC 62368-1 (the audio/video and information-technology equipment safety standard) adopts ISO 13732-1:2006 (ergonomics of hot-surface contact) for its touch limits. TS1 (thermal energy class 1 — no safeguard needed for any user) limits for **metal**, referenced to 25 °C ambient, from Table 42 as reproduced in the UL technical brief ([UL, IEC 62368-1 Technical Brief: Touch Temperature Limits, PDF](https://japan.ul.com/wp-content/uploads/sites/27/2014/06/1_techbrief_touchtemp.pdf)):

| Contact duration | Metal Tmax (TS1) | Plastic/rubber Tmax (TS1) |
|---|---|---|
| > 1 min (continuous use of control elements such as handles) | **48 °C** | 48 °C |
| 10 s – 1 min (the standard's own example: *"slight adjustment of a volume knob"*) | **51 °C** | 60 °C |
| 1 s – 10 s | 60 °C | 77 °C |
| < 1 s | 70 °C | 94 °C |

TS2 = TS1 + 10 K; anything above is TS3. The anticipated contact duration is declared by the manufacturer. The standard literally uses "slight adjustment of a volume knob" as its 51 °C example — but a dial that invites resting a hand on it should be designed to the >1 min class: **48 °C**.

Back-calculation for the aluminium ring (working, assumptions stated):
- Assume 22 °C room. Safety headroom to 48 °C = **26 K**. With R ≈ 3 K/W and (optimistically) an isothermal enclosure, that is ~**8–9 W continuous** before the *safety* limit approaches. Safety is not the binding constraint.
- The product rule is stricter: the knob must never feel warm. Skin-neutral surface temperature for metal is around 33–34 °C (below skin temperature a metal part reads cool because of its high thermal effusivity — the same material property behind Table 42's metal column). Ring at ≤ 34 °C in a 22 °C room = ΔT ≤ 12 K → with R ≈ 3 K/W isothermal, **≈ 4 W continuous through the whole enclosure** — and less than that if any source couples preferentially into the ring. **[assessment built on the cited limits and the R estimate]**

### F3. Where each watt goes — findings and assessment

| Source | Magnitude | Natural coupling | Lever |
|---|---|---|---|
| Display backlight (Ø115 display) | unverified — vendor figure needed for the ESP32-P4-WIFI6-Touch-LCD-3.4C panel (**quote required**) | mid-frame | mount panel frame to base chassis |
| Halo LEDs | 0.2–1.0 W per section E (LEDs are mostly heat; light output is a minority of electrical input) | base edge — already the right place | keep LED PCB on the steel base |
| Ring motor coils (detent cancel) | **1–4 W sustained while scrolling** (given) | **the rim — directly under the knob ring** | the problem child; see below |
| Magnet-carrier actuator | 0.1–0.8 J per event ≈ milliwatts average (section D) | base | none needed |
| ESP32-P4 system + Wi-Fi + regulators | ~0.5–1.5 W class **[estimate; measure on the bench]**; buck-regulator loss ~5–10% of throughput **[estimate]** | main board → standoffs | heat-strap board to base |

Assessment — the design lever: **everything couples to the steel base; the aluminium ring is isolated.** The base carries watts into its own surface, the halo edge, and (weakly) the desk; the ring rides on three V-wheels — point contacts, already a superb thermal break — and should keep an air gap plus low-emissivity facing surfaces everywhere else. Two sharp conclusions:

1. **The ring motor's cancellation heat lands in the worst place on the device.** Its stator must bolt to the base structure, never to the bezel — and section D's energy result now has a thermal twin: continuous detent cancellation is not just 10–60× the energy of moving the carrier, it deposits that energy adjacent to the one part that must never feel warm. Two independent arguments point the same way.
2. **The whole-device continuous budget wants to sit at ≈ 4 W or below** (working in F2) for the ring to stay perceptually cool, with short excursions (scroll bursts, halo flashes) riding on thermal mass — a steel base this size has minutes of thermal time constant, so transient watts are free; sustained watts are the ledger. **[assessment]**

---

## Confidence and gaps

- **High confidence (datasheet/standard, fetched and cited):** Pololu gearmotor RPM/stall per ratio; Moticont voice-coil constants; Takaha CG0836 latching-solenoid stroke/holding force/energizing time; Flexinol wire table (current, cooling times, 2–6% stroke, cycle life); SK6812RGBW 0.25 W rating, 1.2 kHz PWM, 1 mA static draw, 3.5–5.5 V; IEC 62368-1 TS1 metal touch limits (48/51/60/70 °C by duration); piezo stack 0.1–0.15% travel; CIE L\* arithmetic.
- **Vendor-adjacent (secondary source):** SK6812RGBW per-channel 9/16.5 mA — consistent with the 0.25 W rating but taken from reseller pages, not a datasheet table row. Confirm with a current-measured strip on the bench.
- **Marked estimates:** all energy-per-move figures (cited currents × assumed durations); 5 V scaling of 6 V motor specs; latching-solenoid pulse current (coil data quote required); enclosure R ≈ 3 K/W (h-range cited, geometry computed, isothermal assumption optimistic); system-power line items in F3.
- **Open gaps that block final numbers:** (1) the carrier's actual load force — the magnet-to-pole attraction the actuator must overcome — is unmeasured; it decides between the N20+cam and a latching solenoid, and it is a bench-rig measurement, not a datasheet fetch. (2) The 3.4C display's backlight power — vendor figure needed. (3) SK6812RGBW lumen output per channel is absent from the datasheet, so the RGBW-vs-RGB comparison is current-based (16.5 vs 27 mA), not efficacy-based. (4) Takaha's smaller latching models below the CG0836 need per-model force/stroke/coil tables — the public category pages returned 404/403 during this pass; a direct enquiry or per-product shop pages is the route.
