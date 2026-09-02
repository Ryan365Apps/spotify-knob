# Strand E — the bench rig

Design for a bench rig that answers the five open questions on the detent mechanism of
the 60 (the Ø135 mm desk dial by Cadrane) **before** any production drawing is made.
This document is the full design: for each question the measurement method, the
specific purchasable instrument with a cited listing, and the pass/fail number with its
justification. It ends with the rig structure, the data-capture path (with the
sample-rate working), the test matrix, and a one-page build list.

Conventions in this document:

- Every number carries units. Every number is either derived (working shown), cited
  (source linked), or explicitly marked "estimate, unverified".
- Prices are as listed on the cited page on 2026-09-02, in the listing's currency.
  An unpublished price is written "quote required", never estimated.
- Acronyms are expanded at first use and the expansion is repeated where it helps.

Fixed inputs, restated from the R&D brief (`docs/Research/1-detent-haptics-RD.md`) and
the mechanical brief (`docs/CAD-BRIEF.md`):

| Input | Value | Source |
|---|---|---|
| Detent count / pitch | 60 detents, 360°/60 = **6.000° = 0.1047 rad** | brief (decided) |
| Target peak detent torque | **60–150 mNm** | brief |
| Future motor torque class | **30–100 mNm** | brief |
| Knob ring mass | ~180 g aluminium; ~85 g 3D-printed prototype | brief |
| Ring rides on | three V-groove wheels in an inner ridge | brief |
| Magnet gap | ~0.8 mm radial, nominal; cam lowers magnets 3 mm | brief |
| Poles / magnets | 60 × Ø2.5 mm steel poles at pitch circle Ø122.8 mm; 6 × N42 3×6×3 mm stationary | brief |
| Actuator | one LRA-class (linear resonant actuator) vibration motor on the **stationary base** | brief |
| Felt wobble threshold | 0.05 mm at the rim is felt | brief (given) |

---

## Question 1 — Detent strength: torque profile vs angle

**What must be learned.** The actual peak detent torque, the shape of the
torque-vs-angle curve over one 6° detent period (sinusoidal vs peaky), and its
symmetry clockwise vs counter-clockwise — so that (a) the unpowered feel can be judged
against the 60–150 mNm target and (b) the future motor layer (30–100 mNm class) is
known to have the authority to mask or override the passive detent.

### Method: reaction-torque measurement on a floating stator

Do not try to measure torque at the rotating knob — a gauge coupled to the knob winds
up its own cable and cannot sweep continuous revolutions. Instead measure the **reaction
torque on the magnet carrier** (the stator):

1. The stationary hub (magnet carrier + lowering cam) is mounted not rigidly but on
   its own low-friction pivot — a standard 608ZZ deep-groove ball bearing (8 mm bore),
   coaxial with the knob axis — so it is free to rotate a fraction of a degree.
2. A rigid printed arm on the floating stator bears tangentially on a load cell at a
   known radius **R = 50 mm** from the axis. Reaction torque T = F × R.
3. A slow constant-speed drive (section "Rig structure") rotates the knob ring at
   ~12°/s while force and knob angle are logged together. Newton's third law: the
   torque the magnets exert on the knob equals the reaction on the carrier.
4. Sweep one full revolution clockwise, one counter-clockwise; overlay the 60 detent
   periods to get mean profile, spread, and CW/CCW asymmetry.

At 12°/s the inertial torque contribution is negligible: angular acceleration within a
detent is of order (peak-to-peak velocity ripple × sweep rate), and even a full
stop-start within one detent at this speed gives I·α ≈ 7×10⁻⁴ kg·m² × (0.21 rad/s ÷
0.25 s) ≈ 0.6 mNm — under 1% of the 60 mNm target floor. (Inertia derivation is in
Question 2.)

**Force scaling (working).** Peak torque 150 mNm at arm radius 50 mm →
F = 0.150 N·m ÷ 0.050 m = **3.0 N** (≈ 306 gf). Floor case 60 mNm → 1.2 N. So the load
cell needs ~5 N capacity with good resolution below 0.1 N.

### Instruments

**Recommended: lever arm + load cell + microcontroller (build cost ≈ US$25 in parts).**

- Load cell: **TAL221 miniature straight-bar load cell, 500 g** (≈ 4.9 N) capacity —
  the 500 g sibling of the SparkFun 100 g part
  ([SparkFun SEN-14727 listing, US$14.50](https://www.sparkfun.com/mini-load-cell-100g-straight-bar-tal221.html);
  the 500 g variant is SparkFun SEN-14728 at a similar price — verify at order,
  price for the 500 g unit not captured). Aluminium body, four strain gauges in a
  Wheatstone bridge, M3 mounting holes
  ([TAL221 datasheet, SparkFun CDN](https://cdn.sparkfun.com/assets/9/9/a/f/3/TAL221.pdf)).
  At 3.0 N peak the cell runs at ~61% of capacity — comfortable.
- Bridge ADC (analogue-to-digital converter): **NAU7802, 24-bit, up to 320 samples/s**
  ([Adafruit NAU7802 board; listed at US$5.95 via DigiKey per search results](https://www.adafruit.com/product/4538)) —
  see the sample-rate working in the data-capture section for why this beats the HX711.
- Angle: **AS5600 12-bit contactless magnetic rotary encoder**, 4096 counts/rev =
  0.088°/count, I2C (inter-integrated circuit bus) readout — ~68 counts per 6° detent,
  ample ([module listings on Amazon and The Pi Hut](https://thepihut.com/products/grove-12-bit-magnetic-rotary-position-sensor-encoder-as5600);
  generic modules typically under £10 — price not captured on the listing, estimate,
  unverified).
- Calibration: hang known masses (a calibrated weight set, or coins of published mass)
  on the load cell arm; two-point calibration is sufficient for a ratiometric bridge.

**Commercial option (for cross-checking, not required).** A bench digital torque gauge
covering 0.01–0.5 N·m:

- **Mark-10 series TT03, model MTT03-50Z**: capacity 50 ozF·in = 36 N·cm =
  **360 mNm**, 2000 Hz internal sampling, USB output
  ([Global Test Supply listing](https://www.globaltestsupply.com/product/mark-10-mtt03-50z-digital-torque-gauges-series-tt03));
  series pricing starts at **US$1,330**
  ([Judge Tool & Gage, series TT03 page](https://www.judgetool.com/products/mark-10-series-tt03-digital-torque-gauges/)).
- **PCE-TM 80** torque meter, measuring range 0.1–0.5 N·m, resolution 0.0001 N·m
  ([PCE Instruments torque meter category](https://www.pce-instruments.com/us/measuring-instruments/test-meters/torque-meter-torque-tester-kat_41567.htm)) —
  note its 0.1 N·m floor sits **above** the 60 mNm bottom of our target band; price
  quote required.
- **Kern/Sauter digital torquemeter, 0.5 N·m capacity, 0.0001 N·m readability**
  ([John Morris Group listing](https://www.johnmorrisgroup.com/kern-digital-torquemeter-05nm-00001nm-2)) —
  price quote required.

The commercial gauges cost 50× the DIY rig and none is clearly better for a
torque-vs-angle **profile** (they capture peak well, angle poorly). The DIY reaction rig
is the primary instrument; borrow or rent a Mark-10 once, at the end, to sanity-check
the calibration if budget allows.

### Pass/fail

1. **Peak detent torque between 60 and 150 mNm** at the nominal 0.8 mm gap
   (brief target — below 60 mNm the unpowered click is too faint on a 180 g ring;
   above 150 mNm the 30–100 mNm motor class cannot fight it).
2. **Motor headroom:** with the cam engaged (magnets lowered 3 mm), residual peak
   detent torque must be **≤ 30 mNm** — i.e. below the *weakest* candidate motor —
   so the motor layer can fully mask the passive scale when software wants a smooth
   or re-programmed feel. If the cam cannot get residual torque under 30 mNm, either
   the cam throw grows or the motor floor rises; both are drawing changes, which is
   exactly why this is measured before drawings.
3. **Symmetry:** clockwise and counter-clockwise peak torque within ±10% of each other
   (feel-based tolerance — estimate, unverified; an asymmetric detent reads as a
   "grain" direction and the brief's design law has none).
4. **Spread:** standard deviation of the 60 per-detent peaks ≤ 10% of the mean
   (estimate, unverified; pole position tolerance shows up here first).

---

## Question 2 — Spin cost: what magnetic pull costs the free spin

**What must be learned.** The drag the magnet array adds to a free-spinning knob.
A conservative (lossless) detent field would return every millijoule it takes, but real
steel poles passing real magnets lose energy to magnetic hysteresis in the steel and
eddy currents in nearby conductors; the wheels and any seal add mechanical drag. If
loss is high, the knob "slams" to a stop and the flywheel feel of a heavy aluminium
ring is wasted.

### Method: coast-down with a known inertia

Flick the knob to a known speed, log angle vs time until it stops, and extract drag
torque from the deceleration of a known inertia. Three magnet states: **engaged**
(nominal 0.8 mm gap), **lowered** (cam dropped 3 mm), **removed** (magnets out —
mechanical baseline).

**Inertia of the ring (working).** Model the 180 g aluminium knob ring as an annulus.
The ring's material sits roughly between inner radius r₁ ≈ 55 mm and outer radius
r₂ ≈ 67.5 mm (Ø135 outside; inner bound is an estimate from the CAD brief's wall
build-up — estimate, unverified):

- Annulus: I = ½·m·(r₁² + r₂²) = 0.5 × 0.180 kg × (0.055² + 0.0675²) m²
  = 0.09 × (0.003025 + 0.004556) = **6.8×10⁻⁴ kg·m²**
- Thin-ring upper bound at the rim: I = m·r₂² = 0.180 × 0.0675² = **8.2×10⁻⁴ kg·m²**

Use **I ≈ 7×10⁻⁴ kg·m² (±20%)** for the aluminium ring; scale by mass for the 85 g
printed prototype: **I ≈ 3.3×10⁻⁴ kg·m²**. Before testing, refine I from the CAD mass
properties of the actual ring — the ±20% band above is only for planning.

**Procedure.**

1. Flick the knob to ≥ 2 rev/s (ω₀ = 12.6 rad/s). Speed need not be exact — the
   AS5600 encoder log gives the true ω₀ of every run.
2. Log angle at ≥ 200 samples/s until the ring stops. Repeat 5× per configuration.
3. Fit ω(t). Drag torque at any speed: T_d(ω) = −I·dω/dt. A constant-drag (Coulomb)
   component shows as a linear ω(t) tail; a viscous component curves it.
4. For the magnets-engaged state, additionally count detents traversed and compute
   the **net energy lost per detent pass**:
   E_loss/detent = (½Iω₀² − bearing loss over the traversed angle) ÷ detents passed.

**Reference energies (working).** Kinetic energy at 2 rev/s on the aluminium ring:
KE = ½ × 7×10⁻⁴ × 12.57² = **55 mJ**. Energy barrier of one detent, taking the torque
profile as sinusoidal with period p = 0.1047 rad and peak T_p:
E_b = ∫₀^(p/2) T_p·sin(2πθ/p) dθ = T_p·p/π → at T_p = 100 mNm, **E_b = 3.3 mJ**
(2.0 mJ at 60 mNm, 5.0 mJ at 150 mNm). So a 2 rev/s flick carries ~17 barrier-heights
of energy; how far it actually coasts depends entirely on the *loss* per detent, which
is the unknown being measured.

### Instrument

The AS5600 encoder and microcontroller already on the rig (Question 1) — no additional
hardware. The knob is flicked by hand; the encoder measures the achieved ω₀.

### Pass/fail (feel-based proxy, with justification)

1. **Mechanical baseline (magnets removed): drag ≤ 2 mNm**, equivalently the aluminium
   ring coasts **≥ 5 revolutions** from a 2 rev/s flick.
   Working: constant drag T stops the ring after θ = ω₀²·I/(2T);
   θ = 5 rev = 31.4 rad → T = 12.57² × 7×10⁻⁴ ÷ (2 × 31.4) = **1.8 mNm**.
   Justification: this is the quality bar of a good tuned flywheel dial; it is a
   feel-based target (estimate, unverified) but it also keeps mechanical drag well
   under the 30 mNm motor floor, so the motor layer never fights the wheels.
2. **Magnets lowered: coast within 25% of the magnets-removed baseline** (revolutions
   from the same ω₀). Justification: the cam-lowered state is the "smooth scroll"
   state; residual magnetic drag must be imperceptible next to wheel drag.
   Feel-based threshold — estimate, unverified.
3. **Magnets engaged: the ring traverses ≥ 30 detents (≥ half a revolution) from a
   2 rev/s flick.** Working: 55 mJ available minus ~π rad × 1.8 mNm ≈ 6 mJ of bearing
   loss over half a revolution leaves ~49 mJ; over 30 detents that permits an average
   net loss of ≤ 1.6 mJ per detent pass — about half the barrier height of a 100 mNm
   detent. Justification: a flick that dies in fewer than ~10 detents feels braked,
   not weighted; 30+ reads as "heavy tuner". The number is a feel proxy (estimate,
   unverified) to be recalibrated against fingers on the day, but it fixes what "good"
   means before the test instead of after.

---

## Question 3 — LRA reach: does base vibration arrive at the fingers?

**What must be learned.** The LRA (linear resonant actuator) sits on the **stationary
base**; the fingers are on the knob ring, which touches the base only through three
V-groove wheel contacts. Steel-on-aluminium point contacts transmit vibration, but
across two press angles and a compliant printed structure the attenuation is unknown.
If the click cannot reach the fingers, event haptics must move into the knob (slip
rings or battery — a major architecture change), so this is measured first.

### Method

1. Mount the LRA rigidly to the rig base plate (adhesive pad, per its datasheet
   mounting guidance).
2. Drive it at and around its rated resonance with a haptic driver, sweeping
   140–200 Hz in 5 Hz steps — the coupled structure may shift the effective resonance.
3. Measure acceleration **on the knob rim** (the touch surface) with a small digital
   accelerometer puck; simultaneously measure on the base plate next to the LRA to get
   the transmission ratio.
4. Compute the RMS (root-mean-square) acceleration at the drive frequency from an FFT
   (fast Fourier transform) of the rim signal; report rim acceleration and rim/base
   ratio vs frequency, with a finger resting on the rim and without (finger damping is
   part of the real use case).

### Instruments

- **Actuator (the device-representative LRA): Vybronics VG1040003D coin LRA**,
  Ø10 mm, resonance 170 Hz, rated **2.0 G RMS at 2.5 V RMS drive**
  ([Vybronics product page](https://www.vybronics.com/coin-vibration-motors/lra/v-g1040003d);
  [DigiKey listing VG1040003D](https://www.digikey.com/en/products/detail/vybronics-inc/VG1040003D/10285886),
  price not captured at listing time — verify at order). Note the G rating follows the
  industry convention of a ~100 g test sled; bolted to a several-hundred-gram base
  plate the absolute acceleration will be proportionally lower — that reduction is part
  of what the test measures.
- **Driver: Adafruit DRV2605L haptic motor controller breakout, US$7.95**, I2C, drives
  LRA at auto-detected resonance
  ([Adafruit product 2305](https://www.adafruit.com/product/2305)).
- **Accelerometer: Adafruit ADXL345 3-axis digital accelerometer breakout, US$17.50**
  ([Adafruit product 1231](https://www.adafruit.com/product/1231)), output data rate
  configurable 10–3200 Hz
  ([Adafruit ADXL345 learning guide](https://learn.adafruit.com/adxl345-digital-accelerometer)).
  Run at 1600 Hz over SPI (serial peripheral interface): ≥ 9× the 170 Hz signal, no
  aliasing concern. The breakout weighs ~1.3 g (estimate, unverified) — negligible mass
  loading on a 180 g ring. Its noise density (~hundreds of µg/√Hz class) is coarse for
  broadband work but fine here because the measurement is narrowband at a known drive
  frequency: FFT-bin the signal and average 10 bursts.
- **Phone-based alternative (sanity check only): phyphox**, the RWTH Aachen
  sensor-logging app with built-in acceleration FFT
  ([phyphox accelerometer experiments](https://phyphox.org/experiment/?hardware=accelerometer)).
  Typical phone accelerometer sampling is ~400 Hz
  ([survey of smartphone sensors, arXiv 2501.04886](https://arxiv.org/pdf/2501.04886)),
  giving a 200 Hz Nyquist limit — marginal for a 170 Hz drive and useless above it.
  A ~200 g phone also mass-loads a 180 g ring completely, so the phone goes **on the
  base only**, to confirm the LRA is actually shaking the base as expected.

### Pass/fail, from vibrotactile perception thresholds

The fingertip's vibrotactile detection threshold is a U-shaped function of frequency
with maximum sensitivity around 250 Hz, falling at ~12 dB/octave from ~40 Hz toward
that minimum — established by Verrillo, R.T. (1963), "Effect of Contactor Area on the
Vibrotactile Threshold", *J. Acoust. Soc. Am.* 35(12)
([Semantic Scholar record](https://www.semanticscholar.org/paper/784ee3052ccefb395ee07fe35d61a7e01aa498a3);
[survey: Psychophysical comparison of auditory and tactile perception, Springer 2020](https://link.springer.com/article/10.1007/s12193-020-00333-z)).
At the 250 Hz minimum, displacement sensitivity is below 1 µm; the most sensitive
published fingertip figures reach ~0.1 µm, and force-threshold studies report ~1 mN at
250 Hz ([Vibrotactile Force Perception Thresholds at the Fingertip, Springer](https://link.springer.com/chapter/10.1007/978-3-642-14064-8_15)).

Converting displacement thresholds to acceleration at our 170 Hz drive,
a = (2πf)²·x:

- x = 0.1 µm → a = (2π×170)² × 1×10⁻⁷ = **0.11 m/s²** (best-case detection)
- x = 1.0 µm → a = **1.14 m/s²** (conservative detection)

So the detection band at 150–250 Hz spans roughly **0.1–1 m/s²**, consistent with the
brief. A haptic *event* must be clearly felt, not marginally detectable — the usual
engineering margin is ≥ 10 dB above threshold.

- **Pass: ≥ 1.0 m/s² RMS (≈ 0.10 g) at the knob rim** at the drive frequency, finger
  resting on the rim. That is ~19 dB above the 0.11 m/s² best-case threshold and at
  the top of the conservative threshold band — a definite click for essentially all
  users.
- **Marginal: 0.3–1.0 m/s²** — detectable but weak; acceptable only if the concept
  brief downgrades base haptics to "subtle confirmation".
- **Fail: < 0.3 m/s²** at the rim — base-mounted event haptics do not reach the
  fingers across the V-wheels; move the actuator or drop the feature.

---

## Question 4 — Rollers vs race: does three-point support tick or wobble?

**What must be learned.** A continuous bearing race supports the ring everywhere;
three discrete wheels support it at 120° intervals. Two artefacts are possible:
(a) a **3-per-revolution wobble** as the ring's own runout and the wheels' position
errors beat against the three-point support, and (b) **wheel-flat ticking** at the
wheel rotation frequency — each Ø12 mm V-wheel rolls on the ridge (contact diameter
~Ø120 — estimate, unverified until the CAD is frozen), so each wheel turns roughly
120/12 = **~10 times per knob revolution**; a flat or seam on a wheel ticks at ~10, 20,
30… cycles per revolution. Both are frequency-separable from the 60-per-revolution
detent signal, which is the whole basis of the measurement.

### Method

1. **Displacement trace:** dial indicator (Question 5's instrument) probing the rim
   top face, logged by eye against the AS5600 angle every 6° (60 stations), knob
   rotated slowly by hand; repeat on the outside diameter. Plot vs angle; a 3-lobe
   pattern is support wobble, a ~10-lobe pattern is wheel form error.
2. **Torque ripple:** run the Question 1 reaction-torque sweep **with magnets
   removed**. Whatever periodic torque remains is pure mechanics. FFT the
   torque-vs-angle trace; read the amplitude at 3 cycles/rev and at the wheel order
   (~10 cycles/rev and harmonics).
3. **Coast-down smoothness:** from the Question 2 encoder logs (magnets removed),
   compute angular velocity vs angle; FFT the velocity ripple. Ticking wheels show as
   the wheel order riding on the decay.
4. **Ear and finger check**, recorded as a note: ticking that instruments barely see
   can still be audible in a quiet room, and the 60 is a desk object.

### Instruments

No new hardware: the Question 1 rig (torque + angle), the Question 2 logs, and the
Question 5 dial test indicator.

### Pass/fail

1. **Non-detent torque ripple ≤ 5 mNm peak-to-peak** (sum of 3/rev and wheel-order
   components, magnets removed). Justification: 5 mNm is ~8% of the 60 mNm minimum
   detent peak — below roughly a tenth of the detent signal the mechanics hide under
   the detent feel (the ~10% masking figure is a feel-based engineering margin —
   estimate, unverified). It is also only ~2.5× the 2 mNm bearing-drag budget, i.e.
   the same order as drag the fingers already accept.
2. **Velocity ripple during coast ≤ 5% of mean angular velocity** at any wheel-order
   frequency (estimate, unverified — a smoothness proxy; revise against feel).
3. **3-per-revolution displacement component ≤ 0.02 mm** at the rim, so that it
   consumes less than half of the 0.05 mm total wobble budget of Question 5.
4. Any audible per-wheel tick at listening distance in a quiet room is a fail
   regardless of the numbers (subjective gate, recorded per configuration).

If the three-wheel support fails here and a continuous race cannot fit (the sourcing
document `docs/SOURCING-BOM.md` records that no thin-section bearing clears the main
board inside Ø135), the fallback is more wheels (six) or a ground-steel running ridge —
both drawing changes, hence the test-first order.

---

## Question 5 — Rim wobble: axial and radial runout

**What must be learned.** Whether the assembled knob ring runs within the felt
threshold. The brief gives 0.05 mm at the rim as felt; the rig verifies the prototype
sits under it and quantifies how much comes from the printed parts vs the wheels.

### Method

1. Rig base bolted down; dial test indicator on a magnetic base, stylus on the rim.
2. **Radial:** stylus on the Ø135 outside cylindrical face, knob rotated slowly by
   hand through 2 full revolutions; record min/max — the difference is TIR (total
   indicated runout). Log the reading at each of 12 stations (every 30°) to separate
   a 1/rev component (centring error) from 3/rev (support) and higher orders.
3. **Axial:** stylus on the top face near the rim, same procedure.
4. Repeat the whole measurement 3× with the knob lifted and re-seated between runs, to
   separate repeatable geometry from seating scatter.

### Instrument

- **Mitutoyo 513-404-10E lever-type dial test indicator**: 0.8 mm range, **0.01 mm
  graduation**, jewelled anti-magnetic movement
  ([Higher Precision listing](https://www.higherprecision.com/products/indicators/mitutoyo-513-404-10e-metric-horizontal-basic-set-dial-test-indicator-range-0_8mm-graduation-0_01mm);
  [H Roberts & Sons listing](https://www.hroberts-di.com/products/mitutoyo-513-404-10e-lever-dial-indicator-horizontal-type-graduation-0-01mm-range-0-8mm-scale-0-40-0-stylus-length-17-4mm-bezel-diameter-40mm)).
  US retailer listings for comparable 513-404 variants sit in the **US$225–290** range
  ([Amazon listing for 513-404-10A](https://www.amazon.com/Mitutoyo-513-404-10A-DIAL-Accuracy-Yellow/dp/B079H6K6RV));
  exact UK price: quote required. 0.01 mm graduation resolves the 0.05 mm limit in
  five divisions — sufficient; the finer 0.002 mm Mitutoyo variants cost more and add
  nothing here.
- Budget alternative: generic import lever dial test indicators with 0.01 mm
  graduation exist for roughly a tenth of the Mitutoyo price (estimate, unverified —
  no listing captured); acceptable for this rig since the pass line is 5 graduations,
  but buy the Mitutoyo if the indicator will also serve the production QC bench.
- Magnetic indicator base with fine adjust: ~£15 (estimate, unverified).

### Pass/fail

- **≤ 0.05 mm TIR radial** on the Ø135 face **and ≤ 0.05 mm TIR axial** at the rim,
  after re-seating (worst of 3 runs). Justification: the 0.05 mm felt threshold is
  given in the brief; runout at or above the felt threshold on a £-premium object is
  a fail by definition.
- Diagnostic split (not pass/fail, but recorded): 1/rev component vs higher orders,
  because a 1/rev error is centring (fixable in assembly) while 3/rev and wheel-order
  point at the support concept (Question 4's territory).

---

## Rig structure

One printed fixture, one competent person, one weekend of printing.

- **Base plate:** printed (or 12 mm plywood with printed inserts), ~220 × 220 mm,
  three M5 holes for bolting/clamping to the bench. Everything mounts to it, so all
  relative positions survive re-tests.
- **Stator tower (centre):** carries the magnet carrier and its 3 mm lowering cam,
  mounted on a 608ZZ ball bearing (8 mm bore deep-groove, skate-bearing commodity)
  so the whole carrier floats for reaction-torque measurement. A printed lock pin
  rigidly grounds the stator for every test *except* the Question 1 torque sweep.
  A 50 mm reaction arm on the stator bears on the load cell tower.
- **Load cell tower:** the TAL221 bar cell mounted vertically by its M3 holes, contact
  tip at 50 mm radius, adjustable ±2 mm to preload lightly against the arm.
- **Wheel posts:** three posts at 120° carrying the V-groove wheels per the current
  concept (wheel hardware per `docs/SOURCING-BOM.md`, which records that every stocked
  V623ZZ wheel is 3 × 12 × 4 mm). Posts are printed with ±0.5 mm shim seats so wheel
  position tolerance itself can be explored.
- **Knob ring:** the 3D-printed prototype ring (85 g) with its 60 steel poles; an
  aluminium ring (180 g) joins the matrix if/when one exists.
- **Encoder spider:** the real device has a display in the centre; the rig does not,
  so a light three-spoke printed spider clips into the ring bore and carries the
  AS5600's diametral magnet on the axis, over the stationary AS5600 board. The spider
  adds ~5 g near the axis (estimate, unverified) — inertia contribution m·r² is
  negligible against 7×10⁻⁴ kg·m².
- **Constant-speed drive:** a 28BYJ-48 geared stepper motor (commodity hobby part,
  ~£5 with ULN2003 driver board — estimate, unverified) on a swing arm, driving the
  ring's outer rim through a soft friction wheel at ~12°/s for torque sweeps; swings
  clear for flick tests. Slip in a friction drive is harmless because angle truth
  comes from the AS5600 on the ring, not from step counting.
- **Gap shims:** the 0.4 / 0.8 / 1.2 mm radial gaps are set with slip shims behind the
  magnet carrier seats, cut from feeler-gauge stock (a feeler gauge set is ~£8 —
  estimate, unverified) so the gap is set by ground steel, not by printed tolerance.
- **Instrument mounts:** a flat steel strip glued to the base plate gives the magnetic
  indicator base a home; the ADXL345 puck attaches to the rim with thin double-sided
  tape (removable, adds no fastener mass).

## Data-capture path

**Controller:** one Raspberry Pi Pico or ESP32 development board (~£5–8, estimate,
unverified) reads all three sensors and streams timestamped CSV (comma-separated
values) over USB serial to a laptop; plots in Python. No wireless, no firmware
cleverness — this is lab tooling.

**Is the HX711's 80 samples/s enough? (working).** The torque-vs-angle sweep needs to
resolve the shape of a 6° detent period; call the requirement ≥ 20 samples per detent,
i.e. one sample per 0.3°. At a sample rate S the maximum sweep speed is S × 0.3°/s:

- HX711 at 80 samples/s → max sweep 24°/s → a full revolution takes ≥ 15 s.
- Chosen sweep 12°/s → 40 samples per detent on the HX711 — **so yes, 80 samples/s is
  enough**, with 2× margin, provided the sweep stays slow (which is desirable anyway
  to keep inertial torque negligible — see Question 1).

The HX711 remains the fallback, not the choice, for two reasons: its 80 samples/s mode
is its noisy mode (the part is quietest at 10 samples/s —
[Adafruit HX711 guide](https://learn.adafruit.com/adafruit-hx711-24-bit-adc), board
US$5.95 class, [SparkFun HX711 amplifier US$11.50](https://www.sparkfun.com/)), and its
two-wire clocked readout is awkward to timestamp tightly against the I2C sensors. The
**NAU7802 at 320 samples/s** ([Adafruit board, listed at US$5.95 per DigiKey/search
results](https://www.adafruit.com/product/4538)) gives 4× the rate on the same I2C bus
as the AS5600, so force and angle are read back-to-back in one loop with a single
clock — at 320 samples/s and 12°/s that is **160 samples per detent**, enough to see
profile asymmetry, not just peak.

**Rates per test:** torque sweep — NAU7802 at 320 samples/s + AS5600 polled in the
same loop; coast-down — AS5600 at ≥ 200 samples/s (I2C fast mode handles this
comfortably); LRA test — ADXL345 at 1600 Hz over SPI, buffered in its internal FIFO
(first-in-first-out buffer) to dodge I2C jitter.

## Test matrix

Configurations: radial gap {0.4, 0.8, 1.2 mm} × magnet state {engaged, lowered} ×
ring {printed 85 g, aluminium 180 g if available}. Magnet-removed runs are the
mechanical baseline, run once per ring. Tests: **T1** torque sweep (Question 1),
**T2** coast-down ×5 flicks (Question 2), **T3** LRA transmission (Question 3),
**T4** ripple/FFT (Question 4, uses T1+T2 data with magnets removed), **T5** runout
(Question 5).

| # | Gap | Magnets | Ring | T1 torque | T2 coast | T3 LRA | T4 ripple | T5 runout |
|---|-----|---------|------|-----------|----------|--------|-----------|-----------|
| 0a | — | removed | printed | ✓ (baseline) | ✓ (baseline) | ✓ | ✓ | ✓ |
| 0b | — | removed | alu | ✓ (baseline) | ✓ (baseline) | ✓ | ✓ | ✓ |
| 1 | 0.4 mm | engaged | printed | ✓ | ✓ | — | — | — |
| 2 | 0.4 mm | lowered | printed | ✓ | ✓ | — | — | — |
| 3 | 0.8 mm | engaged | printed | ✓ | ✓ | ✓ (worst case: stiff detent path) | — | — |
| 4 | 0.8 mm | lowered | printed | ✓ | ✓ | — | — | — |
| 5 | 1.2 mm | engaged | printed | ✓ | ✓ | — | — | — |
| 6 | 1.2 mm | lowered | printed | ✓ | ✓ | — | — | — |
| 7–12 | as 1–6 | as 1–6 | alu | ✓ | ✓ | ✓ (config 9 only) | — | — |

Notes: T3 (LRA) and T5 (runout) do not vary with magnet gap, so they run on the
baseline configurations plus one engaged case to check whether magnet coupling changes
vibration transmission. The gap sweep exists because detent torque scales steeply with
gap — three points bracket the 0.8 mm nominal and tell the CAD how much tolerance the
0.8 mm figure can absorb, which feeds the production drawing directly.

## Build list (one page)

Prototype ring, steel poles, N42 magnets, and V-wheels are already part of the
project's sourcing (`docs/SOURCING-BOM.md`) and are not re-costed here.

| Item | Qty | Price as listed | Source |
|---|---|---|---|
| TAL221 500 g mini load cell (SparkFun SEN-14728; 100 g sibling cited) | 1 | US$14.50 (100 g listing; 500 g verify at order) | [SparkFun](https://www.sparkfun.com/mini-load-cell-100g-straight-bar-tal221.html) |
| Adafruit NAU7802 24-bit load-cell ADC (Stemma QT) | 1 | US$5.95 (per DigiKey/search) | [Adafruit 4538](https://www.adafruit.com/product/4538) |
| SparkFun HX711 amplifier (fallback ADC, optional) | 1 | US$11.50 | [SparkFun](https://www.sparkfun.com/) |
| AS5600 magnetic encoder module + diametral magnet | 1 | listing found, price not captured — est. under £10, unverified | [The Pi Hut](https://thepihut.com/products/grove-12-bit-magnetic-rotary-position-sensor-encoder-as5600) |
| Adafruit ADXL345 accelerometer breakout | 1 | US$17.50 | [Adafruit 1231](https://www.adafruit.com/product/1231) |
| Adafruit DRV2605L haptic driver breakout | 1 | US$7.95 | [Adafruit 2305](https://www.adafruit.com/product/2305) |
| Vybronics VG1040003D coin LRA, 170 Hz, 2.0 G RMS | 2 | price not captured — verify at order | [DigiKey](https://www.digikey.com/en/products/detail/vybronics-inc/VG1040003D/10285886) |
| Mitutoyo 513-404-10E dial test indicator, 0.01 mm | 1 | US$225–290 range per US retail; UK quote required | [Higher Precision](https://www.higherprecision.com/products/indicators/mitutoyo-513-404-10e-metric-horizontal-basic-set-dial-test-indicator-range-0_8mm-graduation-0_01mm) |
| Magnetic indicator base | 1 | ~£15 — estimate, unverified | generic |
| Raspberry Pi Pico (or ESP32 dev board) | 1 | ~£5–8 — estimate, unverified | generic |
| 28BYJ-48 stepper + ULN2003 driver | 1 | ~£5 — estimate, unverified | generic |
| 608ZZ bearing (floating stator pivot) | 2 | ~£2 — estimate, unverified | generic |
| Feeler gauge set (shim stock for 0.4/0.8/1.2 mm gaps) | 1 | ~£8 — estimate, unverified | generic |
| Filament, fasteners, tape, wire | — | ~£15 — estimate, unverified | on hand / generic |
| Calibration weights (or use coins of published mass) | 1 set | ~£10 — estimate, unverified | generic |

**Total: roughly £300–360 including the Mitutoyo indicator, or ~£120–150 with a budget
indicator — estimate.** (Mixed-currency sum at an assumed ≈ US$1.25/£ — conversion
unverified.) The optional Mark-10 MTT03-50Z commercial torque gauge (from US$1,330,
[Judge Tool series page](https://www.judgetool.com/products/mark-10-series-tt03-digital-torque-gauges/))
is deliberately excluded: rent or borrow one for a one-day calibration cross-check if
the DIY numbers will be load-bearing in a supplier negotiation.

## Sources

- SparkFun TAL221 load cell: https://www.sparkfun.com/mini-load-cell-100g-straight-bar-tal221.html and datasheet https://cdn.sparkfun.com/assets/9/9/a/f/3/TAL221.pdf
- Adafruit NAU7802: https://www.adafruit.com/product/4538 · Adafruit HX711 guide: https://learn.adafruit.com/adafruit-hx711-24-bit-adc
- AS5600 module: https://thepihut.com/products/grove-12-bit-magnetic-rotary-position-sensor-encoder-as5600
- Adafruit ADXL345: https://www.adafruit.com/product/1231 and https://learn.adafruit.com/adxl345-digital-accelerometer
- Adafruit DRV2605L: https://www.adafruit.com/product/2305
- Vybronics VG1040003D: https://www.vybronics.com/coin-vibration-motors/lra/v-g1040003d and https://www.digikey.com/en/products/detail/vybronics-inc/VG1040003D/10285886
- Mark-10 TT03 series: https://www.globaltestsupply.com/product/mark-10-mtt03-50z-digital-torque-gauges-series-tt03 and https://www.judgetool.com/products/mark-10-series-tt03-digital-torque-gauges/
- PCE torque meters: https://www.pce-instruments.com/us/measuring-instruments/test-meters/torque-meter-torque-tester-kat_41567.htm · Kern/Sauter: https://www.johnmorrisgroup.com/kern-digital-torquemeter-05nm-00001nm-2
- Mitutoyo 513-404-10E: https://www.higherprecision.com/products/indicators/mitutoyo-513-404-10e-metric-horizontal-basic-set-dial-test-indicator-range-0_8mm-graduation-0_01mm and https://www.amazon.com/Mitutoyo-513-404-10A-DIAL-Accuracy-Yellow/dp/B079H6K6RV
- Verrillo (1963): https://www.semanticscholar.org/paper/784ee3052ccefb395ee07fe35d61a7e01aa498a3 · threshold surveys: https://link.springer.com/article/10.1007/s12193-020-00333-z and https://link.springer.com/chapter/10.1007/978-3-642-14064-8_15
- phyphox: https://phyphox.org/experiment/?hardware=accelerometer · phone accelerometer rates: https://arxiv.org/pdf/2501.04886
