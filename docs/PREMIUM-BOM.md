# Premium dial — prototype BOM (ESP32-P4 3.4" concept)

**Date:** 2026-08-31
**Concept:** Waveshare ESP32-P4 3.4" round display as the face, a rotating aluminium bezel/knob around it, chunky weighted base, haptic feedback. Nest-thermostat scale (~100mm). Target: 3D-printed prototype first, then the £450 × 50 drop.

---

## The core board

**Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C** — [Waveshare page](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-3.4c.htm) · [Amazon UK](https://www.amazon.co.uk/Waveshare-Development-Resolution-Toughened-Microphones/dp/B0F9YP4DCS) · [PiHut £62.40, out of stock](https://thepihut.com/products/esp32-p4-3-4-round-touch-display-dev-board-800x800)

- 3.4" round IPS, **800×800**, optically bonded toughened glass, 10-point touch
- ESP32-P4 (dual-core RISC-V 360MHz) + ESP32-C6 co-processor (Wi-Fi 6 / BT5)
- **USB 2.0 OTG high-speed (480Mbps)** — 40× the S3's bandwidth; album art streaming is trivial
- 32MB PSRAM / 32MB flash, dual mics + speaker (unused), 40-pin GPIO header

Physical: display ≈ **86mm diameter** → bezel ring ~100mm OD → base ~110mm. Nest thermostat is 84mm; this is that class of object.

## Words used in this section

Plain definitions first, because the rest of this only makes sense with them.

| Term | What it actually means |
|---|---|
| **Detent** | The click you feel as a knob steps from one position to the next. A camera lens aperture ring has detents; a car radio volume knob usually doesn't. |
| **LRA** — linear resonant actuator | A tiny vibration motor. Not the spinning-weight kind in an old phone; this one is a weight on a spring that punches back and forth in a straight line, so it can start and stop within a few thousandths of a second. That sharpness is what makes a buzz feel like a *click*. It fakes a detent — nothing physically steps. |
| **On-axis sensor** | A part that reads rotation by looking at a magnet stuck to the end of a spinning shaft, directly on the centre line. Cheap and accurate — but it needs a centre line to sit on. |
| **Ring sensing** | Reading rotation from a ring of magnets bonded around the *inside of the knob itself*, with the sensor looking sideways at the ring. No shaft, no gears, nothing touching. Needed here because our centre is occupied by the display. |
| **Backlash** | Slop in a gear train. Turn one way, the gear takes up a fraction of a millimetre of play before the other side moves. It means the same physical position reads slightly differently depending on which direction you arrived from. |
| **Cogging** | The lumpy resistance you feel turning an electric motor by hand, caused by its magnets lining up with its steel teeth. Usually a defect; occasionally a feature. |
| **BLDC motor** — brushless DC | An electric motor with no brushes. Drive it cleverly and it can push back against your hand with a force the software chooses, which is how you get detents that change shape per screen. |

## The dial mechanism — the decision this product lives or dies on

**This is the one irrationally expensive interaction.** It is a 110 mm ring under the user's fingers on a permanently-sited desk object, and it is what the price is actually for. The intent is a heavy, expensive watch sitting on the desk that invites you to move it — it must reward idle handling, not just deliberate use.

### Two problems found in the current design

**1. We rejected gears for the motor and then accepted them for the sensor.**

This document argues that adding a gear to a motor "adds backlash that ruins the feel" — correct — and then specifies an AS5600 sensor "driven from a printed internal gear ring on the bezel via pinion." That is the same backlash, sitting on the path that decides *when the click fires*. The result is a detent that lands at a slightly different angle depending on which way you turned, which is exactly what makes a dial feel cheap.

The reason it was geared is legitimate: the AS5600 is an on-axis part, it needs a magnet on the centre line, and our centre line is an 86 mm display. There is no shaft.

**The fix is to stop using an on-axis part.** Bond a ring of alternating magnetic poles to the inside of the knob and read it with a sensor built for that job — the ams AS5304 / AS5306 / AS5311 family exists precisely for multi-pole rings and strips. No gear, nothing touching, no backlash, and far finer resolution than a geared AS5600. Optical or capacitive encoder rings solve it the same way. Roughly £15–25 instead of £7, which on this product is not a consideration.

**2. The vibration actuator is on the wrong side of the bearing.**

The plan puts the LRA in the base. The knob spins on a thin-section bearing whose entire purpose is to *mechanically isolate the knob from the base*. Your fingers are on the knob.

The Apple Watch comparison does not carry here. Apple's vibration engine is bolted to the same case your finger rests on, and the crown is 8 mm across. Ours is a 110 mm ring separated from the actuator by a precision bearing, so the click is likely to arrive in the base — and through it, the desk — rather than in the fingertips. It would feel like the object buzzed near your hand rather than the mechanism clicking under it.

**This is the single biggest untested assumption in the hardware.** It costs an afternoon to check.

### Three ways to make a detent, and how they interact

| Approach | What it is | Feel | Can software change it? | Cost / difficulty |
|---|---|---|---|---|
| **Vibration** (current plan) | LRA in the base pulses in time with rotation | Fake. Depends entirely on how much energy crosses the bearing | Yes — any number of steps, any pattern | ~£9, easy |
| **Magnetic detent** | A ring of magnets on the rotating part pulled toward steel pole pieces on the fixed part | **Real force at the fingertip.** Silent, no contact, no wear, no power. This is how a good camera lens ring feels | **No — the step count is fixed in metal** | ~£10–20, one weekend to prototype |
| **Motor force feedback** | A large-diameter brushless motor actively pushes back | Real force, and fully programmable | Yes — completely | No catalogue part exists at 90 mm bore; a custom ring motor is a real engineering programme |

**Magnets and a motor fight each other, and this needs deciding rather than deferring.** Fixed magnetic detents create a permanent lumpiness the motor would have to cancel out before it could impose a different pattern — and cancelling it costs continuous current and never quite works. Motor designers spend real effort *removing* cogging for this reason. So "magnets and a motor" is not additive: choose which one owns the feel.

### The option that resolves it: a detent you can physically switch off

Mount the steel pole pieces on a ring that moves about 1–2 mm along the axis, driven by one small actuator. Magnetic force falls away sharply with distance, so a millimetre or two collapses the detent to nothing.

That gives **two genuinely different mechanical characters in one object**: crisp discrete clicks for menus and lists, and a free-running, weighted, inertial spin for volume and scrubbing — with a real mechanical *clunk* as it changes over, which becomes a signature of the product rather than a side effect.

It is mechanically simple, needs no exotic parts, uses power only during the change, and delivers most of what force feedback promised without a custom motor. It is also the most direct expression of the object we are describing: a dial that changes its own character under your hand.

### The layered architecture — decided

Three layers, each doing the job it is actually good at. This resolves the "magnets or motor" question: it is both, but they own different things.

| Layer | Owns | Changes | Survives power off |
|---|---|---|---|
| **Magnet ring** | The fixed physical scale, and overall detent weight | Rarely — entering free-spin, or a user preference | **Yes** |
| **Motor** | Everything dynamic: end-stops, resistance ramping toward a limit, half-steps between magnet positions, per-context feel | Continuously, in milliseconds | No |
| **Vibration actuator** | Event confirmations layered on top — a save, a mode change, an alert | Per event | No |

**Why dynamic detent strength must come from the motor, not from moving the magnets.** Resistance building as you approach the end of a range has to arrive within about a tenth of a second or it feels disconnected from the hand. A self-locking screw needs several hundred milliseconds to move 1.5 mm. Running a small motor continuously during normal use also brings noise into an object designed to be silent, draws power from a budget already capping the halo at 20%, and wears a mechanism intended to last a decade. The motor changes force instantly, silently, with no moving part beyond the rotor already turning.

**The magnet ring still moves during use — but at gesture cadence, not detent cadence.** Switching from a detented context to free scrubbing is a real mechanical event you feel and hear, a few times an hour at most. That is the moment worth having.

**The magnets' real job is that the object is never inert.** Every motorised dial is dead when unplugged. With magnets, this one still clicks like a watch bezel with no power at all.

### Detent geometry — decided

- **A ring of magnets on the stationary part, not one.** A single magnet pulls the knob to one side, loading one part of the bearing race, felt as a tight spot that travels as you turn. Evenly spaced magnets cancel each other's side forces so the bearing sees no net sideways load. Extra strength is a bonus, not the reason.
- **Steel poles on the rotating bezel, magnets on the stator.** Keeps everything needing power or movement on the part that does not spin. This is already the intent.
- **60 steel poles, 6 magnets.** The poles set the detent count; the magnets only need to align with poles simultaneously. With 60 poles (6° apart) magnet counts of 3, 4, 5, 6, 10 or 12 work. **Eight does not** — 45° is seven and a half pole spacings, so half the magnets would pull toward a notch while the rest push away and the detent half-cancels.
- **60 divides usefully:** every 10th (6 positions) for the app selector, every 5th (12) for settings and menus, every 1 (60) for volume and brightness, and motor half-steps (120) for fine scrubbing. 120 is also a dive-bezel count. At 135 mm the spacing is about 7 mm of travel per click at the rim — comfortably watch-like.
- **Movement is axial — vertical, up and down along the spin axis.** One flat carrier ring lifted by one mechanism, so every magnet moves identically for free. Radial movement would need six separate motions or an iris mechanism.
- **The mechanism holding the carrier must hold position with no power.** That rules out a solenoid and shape-memory wire, and points at a fine screw turned by a small motor, or a cam shallow enough that it cannot back-drive. It also makes detent weight **continuously adjustable** rather than on/off — a setting that physically changes the mechanism and survives a power cut because it is a screw position, not a stored value.

**Consequence to measure, not argue about.** Magnetic pull passes through the bearing. It takes up the internal slack, so the knob loses any detectable wobble and feels more precisely located — good. It also increases friction, so a free spin dies away sooner — a cost. At the strengths discussed this is probably a net win, but it is exactly what the rig exists to find out.

**Target strength, as a starting hypothesis.** What the hand feels is twisting force divided by radius. At ~65 mm radius: a camera aperture ring is around 0.3 N at the fingers, a clicking volume knob 0.5–0.8 N, a dive bezel a deliberate 1.5–3 N. For "expensive watch on the desk", aim at the bezel end — roughly **60–150 mNm peak, adjustable across that range.** Design the magnet ring for the top of it; weakening with the air gap is easy, exceeding what the magnets can deliver is impossible.

**Add hidden mass.** Free-spin feel comes from inertia at the rim. A brass or steel insert concealed inside the aluminium bezel adds significant mass with nothing visible changing. Common in premium objects, near-free at this scale.

### Two findings from the assembly model (measured 2026-09-01)

**1. The gear train occupies exactly the space the magnet system needs.** `drive_wheel` and `wheel_mount` sit at Z 6.6–22.2 in the ring-shaped volume between the main board and the bearing. That is where the magnet carrier and its lift mechanism want to be. Replacing the geared sensor with ring sensing removes the slop problem *and* frees the ~16 mm of height the detent system needs. The two changes pay for each other.

**2. The bearing, carrier and display are stacked vertically when they should be concentric.** Currently: bearing at Z 23.1–36.1, display carrier 38.8–43.8, display module 42.3–57.3 — three components in series up the axis, which is what makes the object ~60 mm tall. A 6817 bearing has an 85 mm bore; the display assembly should pass *through* it rather than sit on top of it.

### Revised spike order — cheapest and most informative first

1. **Magnetic detent bench test.** A handful of N52 magnets, steel pole pieces, a printed carrier. Answers the central question: does a 110 mm ring need real force, or will faked clicks do? **Run this before any CNC drawing is committed.**
2. **Vibration coupling test.** Fire the LRA in the base and measure — or just feel — how much reaches a finger on the rotating ring. Cheap, and it either validates or kills the current plan.
3. **Ring sensing.** Replace the geared AS5600 with a multi-pole ring and a matching sensor. Removes the backlash contradiction above.
4. **Switchable detent.** Only once 1 has proved the detent feel is worth having.
5. **Motor force feedback.** Only if 1 shows that fixed detents are too limiting. Note that this document closed the option because no *catalogue* hollow motor exists at this bore — a custom large-diameter ring motor is how direct-drive turntables work, so this is a cost and programme question, not a physics one.

**Knock-on:** if the detent becomes real, the speaker's mechanical "kerchunk" stops being load-bearing for the feel. The speaker stays — it has its own job in notifications and alerts — but it should no longer be propping up a weak mechanism.

## BOM — prototype, qty 1, with purchase links [costs are estimates]

| # | Part | Buy | Est. cost |
|---|---|---|---|
| 1 | Waveshare ESP32-P4-Touch-LCD-3.4C | [Amazon UK](https://www.amazon.co.uk/Waveshare-Development-Resolution-Toughened-Microphones/dp/B0F9YP4DCS) · [Waveshare direct](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-3.4c.htm) · [PiHut £62.40, out of stock](https://thepihut.com/products/esp32-p4-3-4-round-touch-display-dev-board-800x800) | £70 |
| 2 | Thin-section bearing **6817-2RS, 85×110×13mm** — bore clears the 86mm screen. Buy budget ZEN, not SKF (£40+). Sealed = slight drag, which reads as quality; open variant 61817 if too stiff | [Bolton Engineering (ZEN)](https://bepltd.com/products/61817-2rs-85x110x13mm-zen-deep-groove-ball-bearing) · [Bearings Online](https://www.bearings-online.co.uk/item/186/DeepGrooveBallBearings/61817-2RS-Thin-Section-Ball-Bearing.html) | £10–15 |
| 3 | AS5600 magnetic encoder module (diametric magnet included); driven from a printed internal gear ring on the bezel via pinion | [HALJIA on Amazon UK](https://www.amazon.co.uk/HALJIA-Induction-Measurement-Magnetized-Precision/dp/B08BCB899Q) | £7 |
| 4 | DRV2605L haptic driver **with LRA actuator included**, I2C, built-in click/tick effect library. If ticks feel weak through the bezel, upgrade actuator to a Vybronics VLV-series LRA from Mouser, same driver | [Pimoroni — DRV2605L Linear Actuator Haptic Breakout](https://shop.pimoroni.com/products/drv2605l-linear-actuator-haptic-breakout) | £9 |
| 5 | **USB A-to-A cable (male-male, USB 2.0)** — required for Waveshare's Windows Display Expansion demo on day one | [Amazon UK search](https://www.amazon.co.uk/s?k=usb+a+to+a+male+male+cable+2.0) | £5 |
| 6 | Braided USB-C cable ~1.5m (PC end of the eventual captive cable) | [Amazon UK search](https://www.amazon.co.uk/s?k=braided+usb+c+cable+1.5m) | £6 |
| 7 | Steel weight — M10 penny washers or turned disc, 200–300g | [Amazon UK search](https://www.amazon.co.uk/s?k=m10+penny+washers+steel) / hardware shop | £4 |
| 8 | M3 heat-set inserts + screws kit (if not in stock) | [Amazon UK search](https://www.amazon.co.uk/s?k=m3+heat+set+inserts+kit) | £8 |
| 9 | 3D printed parts: base shell, bezel/knob body, gear ring, internals | Own printer, ~150g PETG | £4 |
| | **Prototype total, delivered** | | **~£120** |

Print the bezel in PETG, wrap it in aluminium tape or paint for feel-testing; the real one is CNC'd later.

## Projected unit cost at qty 50 (the £450 drop) [estimates]

| Part | Change at 50 | Est. |
|---|---|---|
| P4 board | Waveshare direct/bulk | £55–60 |
| Bearing, encoder, LRA+driver, magnet | Small-qty pricing | £18–22 |
| **CNC aluminium bezel/knob** (anodised) | Replaces print — PCBWay/Xometry batch | £25–40 |
| Base: CNC or heavy resin-cast + steel weight | | £15–25 |
| Captive braided cable | | £4 |
| Premium packaging (drop-worthy unboxing) | | £10–14 |
| Assembly | Own labour | — |
| **Landed per unit** | | **~£130–165** |

At £450 × 40 sold: gross ~£11.5–13k before compliance (£3–5k) and time. Consistent with the drop model in `COMMERCIAL-FEASIBILITY.md` — thinner than the £110 target discussed earlier because the P4 board and big screen cost more; acceptable for a validation run, and the custom-PCB version (dropping the dev board's unused mics/speaker/camera/GPIO) claws back £25–35/unit at run 2.

**Run-2 glass spec (do not retrofit on the dev board — its glass is already toughened + optically bonded; stacking a layer degrades look and touch):** when ordering the raw panel, specify custom round cover glass — **2.5D polished edge** (the finger's glass-to-knurl transition is the signature tactile moment; target zero visible step to the bezel), **oleophobic + AR coating**. ~£2–5/unit at volume from smartwatch-glass suppliers. Optional slight dome (watch-crystal look) — complicates touch, nice-to-have only. Prototype-level trick: wipe-on oleophobic coating (~£8) on the stock glass.

## Build order

1. **Order the P4 board now** (PiHut is out — Amazon or Waveshare direct). Lead item.
2. Print a base + fixed (non-rotating) bezel; get album art rendering at 800×800 over USB from the Windows companion app. This is Gate 3 on better hardware.
3. Add the bearing + free-spinning bezel + encoder; wire rotation to volume.
4. Add the LRA; tune detent ticks against the CrowPanel/M5Dial buzzer feel for comparison.
5. Only then decide whether the v1 BLDC experiment is worth a weekend.

## Open questions / risks

- **P4 toolchain maturity.** Arduino support is early; plan on ESP-IDF + LVGL 9. Waveshare's demo code for this exact board is the starting point.
- ~~USB device mode~~ **RESOLVED (2026-08-31).** The P4 supports device mode via TinyUSB at high speed (480Mbps) with HID/CDC/MIDI/composite classes ([esp-usb device docs](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_device.html)). Board-level: the 3.4C's HS OTG is on a **USB-A socket**, and Waveshare's own **"Windows Display Expansion" demo** connects this board to a PC as a USB device over an **A-to-A cable** ([SpotPear wiki mirror](https://spotpear.com/wiki/ESP32-P4-3.4-inch-Round-LCD-Display-TouchScreen-WIFI6.html)) — the album-art pipeline is vendor-demonstrated. For the product, the captive cable hides the A-to-A hack (A internally, USB-C at the PC end).
- **Better still (from the official spec, [product page](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-3.4c.htm?sku=31522)):** the board's main **USB-C port is the P4's second USB peripheral — a full-speed (12Mbps) device port that also powers the board**. One plain C-to-C cable = power + HID media keys + album art (a ~100KB JPEG moves in <1s, inside the 1.5s track-change budget). **Test this port first**; if art feels instant, the prototype needs no adapter and the captive cable is a standard C-to-C. The high-speed A port remains the upgrade path for streamed animations / display-expansion mode. (Second C port is UART debug only. Power question resolved: port 5 powers the board.)
- **Encoder route** — gear-driven AS5600 is the cheap proto answer; if the gear feel/noise disappoints, alternatives are an optical sensor reading tick marks inside the bezel, or a magnetic ring encoder (dearer).
- **Bezel wobble** is what separates premium from toy — the bearing seat tolerances matter more than anything else in the printed parts. Budget several reprints.
- **LRA in the base vs in the knob:** base is easier (no slip ring); test whether ticks transmit convincingly through the bezel via the bearing.
