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

## The haptics decision (made before the BOM makes sense)

True motor force-feedback (SmartKnob-style BLDC) **does not scale to a 90mm ring** — hollow motors with that bore don't exist off the shelf, and gearing one in adds backlash that ruins the feel. This is why nobody sells a force-feedback ring this size.

**The Apple Watch digital crown proves the alternative.** The crown is a *passive* encoder on a good bearing; the "clicks" are Taptic Engine vibrations synced to rotation — and everyone reads it as premium. So:

- **v0 (this BOM):** passive bezel on a thin-section bearing + position sensing + a strong LRA in the base firing per-detent ticks. Software still defines detent count/feel per context (radial menus etc.) — it just can't push back against your hand.
- **v1 (later spike, optional):** offset BLDC + printed ring gear experiment for real force feedback. One weekend, one motor, likely conclusion: not worth the backlash.

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
