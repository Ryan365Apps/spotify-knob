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

## BOM — prototype, qty 1 [all estimates]

| # | Part | Source / example | Est. cost |
|---|---|---|---|
| 1 | Waveshare ESP32-P4-Touch-LCD-3.4C | Amazon UK / Waveshare direct | £70 |
| 2 | Thin-section bearing for bezel, ~90×100mm (e.g. 6813-2RS or KA-series) | Bearing supplier / AliExpress | £8–14 |
| 3 | Bezel position sensing: printed internal gear ring on bezel → pinion → AS5600 magnetic encoder | AliExpress / Pimoroni | £4 |
| 4 | LRA haptic actuator (large coin/linear, e.g. Vybronics) + DRV2605L driver breakout | Mouser / Adafruit | £10 |
| 5 | Braided USB-C cable, ~1.5m (captive at device end) | Amazon | £6 |
| 6 | Steel weight — stack of washers or a turned disc, 200–300g | Hardware shop | £4 |
| 7 | 3D printed parts: base shell, bezel/knob body, gear ring, internals | Own printer, ~150g filament | £4 |
| 8 | Fasteners, wire, heat-set inserts, magnet for encoder | Stock | £6 |
| | **Prototype total** | | **~£112** |

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

## Build order

1. **Order the P4 board now** (PiHut is out — Amazon or Waveshare direct). Lead item.
2. Print a base + fixed (non-rotating) bezel; get album art rendering at 800×800 over USB from the Windows companion app. This is Gate 3 on better hardware.
3. Add the bearing + free-spinning bezel + encoder; wire rotation to volume.
4. Add the LRA; tune detent ticks against the CrowPanel/M5Dial buzzer feel for comparison.
5. Only then decide whether the v1 BLDC experiment is worth a weekend.

## Open questions / risks

- **P4 toolchain maturity.** Arduino support is early; plan on ESP-IDF + LVGL 9. Waveshare's demo code for this exact board is the starting point.
- ~~USB device mode~~ **RESOLVED (2026-08-31).** The P4 supports device mode via TinyUSB at high speed (480Mbps) with HID/CDC/MIDI/composite classes ([esp-usb device docs](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_device.html)). Board-level: the 3.4C's HS OTG is on a **USB-A socket**, and Waveshare's own **"Windows Display Expansion" demo** connects this board to a PC as a USB device over an **A-to-A cable** ([SpotPear wiki mirror](https://spotpear.com/wiki/ESP32-P4-3.4-inch-Round-LCD-Display-TouchScreen-WIFI6.html)) — the album-art pipeline is vendor-demonstrated. For the product, the captive cable hides the A-to-A hack (A internally, USB-C at the PC end). **Remaining sub-check:** whether the A port alone powers the board in device mode, or the captive cable needs a Y-split inside the base feeding the power USB-C too.
- **Encoder route** — gear-driven AS5600 is the cheap proto answer; if the gear feel/noise disappoints, alternatives are an optical sensor reading tick marks inside the bezel, or a magnetic ring encoder (dearer).
- **Bezel wobble** is what separates premium from toy — the bearing seat tolerances matter more than anything else in the printed parts. Budget several reprints.
- **LRA in the base vs in the knob:** base is easier (no slip ring); test whether ticks transmit convincingly through the bezel via the bearing.
