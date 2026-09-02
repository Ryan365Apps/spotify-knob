# Findings B1 — USB audio architecture for the 60

Research date: 2026-09-02. Question: should the ESP32-P4 (the main controller on the Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C board) present the USB Audio Class device itself, or should a dedicated USB-audio bridge chip do it? All prices and stock figures were read from the cited vendor pages on the research date and will drift. Findings are separated from assessment throughout; anything not read from a source is marked unverified.

---

## 1. ESP32-P4 as a native USB Audio Class device (findings, sourced)

### 1.1 Hardware capability

- The ESP32-P4 has one USB 2.0 On-The-Go high-speed peripheral running at 480 Mbit/s with an internal high-speed physical-layer transceiver (PHY), providing endpoint 0 plus 15 further endpoints (up to 8 IN endpoints concurrently active), and a second full-speed (12 Mbit/s) peripheral with endpoint 0 plus 6 endpoints. Source: [ESP-USB Programming Guide, USB Device Stack, ESP32-P4](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_device.html).
- The high-speed USB 2.0 OTG data pins are dedicated pins 49–50, not usable as general-purpose I/O. Source: [ESP-FAQ, USB](https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/usb.html).
- TinyUSB (the open-source USB device stack ESP-IDF wraps) gained USB OTG high-speed device support for ESP32-P4, merged October 2024. Source: [Adafruit blog, 2024-10-01](https://blog.adafruit.com/2024/10/01/usb-otg-high-speed-support-for-esp32-p4-merged-into-tinyusb/). The default TinyUSB port on ESP32-P4 is the high-speed port. Source: [ESP-USB Programming Guide](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_device.html).

### 1.2 The Espressif audio-class component: `usb_device_uac`

- Espressif ships `usb_device_uac`, a USB Audio Class (UAC — the USB device class for audio) device driver built on TinyUSB, for ESP32-S2/S3/P4. Latest version 1.3.1 at research date. Up to 8 speaker channels and 4 microphone channels, configurable (build-time) sample rate, volume and mute controls. Sources: [ESP Component Registry, usb_device_uac](https://components.espressif.com/components/espressif/usb_device_uac), [ESP-IoT-Solution, USB Device UAC](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_device/usb_device_uac.html).
- It implements UAC 2.0, not UAC 1.0: the source file uses TinyUSB's UAC 2.0 entities (`UAC2_ENTITY_CLOCK`, `UAC2_ENTITY_SPK_FEATURE_UNIT`), and the ESP-IoT-Solution overview states the audio device solution is "based on the UAC 2.0 protocol standard". Sources: [usb_device_uac.c on GitHub](https://raw.githubusercontent.com/espressif/esp-iot-solution/master/components/usb/usb_device_uac/usb_device_uac.c), [ESP-IoT-Solution, USB Device Solution](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_device_solutions.html).
- Endpoint synchronisation type: asynchronous isochronous with an explicit feedback endpoint. The source sets the TinyUSB feedback callback to `AUDIO_FEEDBACK_METHOD_FIFO_COUNT` (feedback value derived from FIFO fill level), and the component documentation says it "supports ISO FeedBack communication interface by default and automatically syncs with the host based on the remaining size of the UAC FIFO memory". Sources: [usb_device_uac.c](https://raw.githubusercontent.com/espressif/esp-iot-solution/master/components/usb/usb_device_uac/usb_device_uac.c), [component registry page](https://components.espressif.com/components/espressif/usb_device_uac).
- High-speed build support exists in the source (`#if CONFIG_TINYUSB_RHPORT_HS` → `USB_PHY_SPEED_HIGH`). Source: [usb_device_uac.c](https://raw.githubusercontent.com/espressif/esp-iot-solution/master/components/usb/usb_device_uac/usb_device_uac.c).
- Sample rates and bit depths are build-time configuration; the documentation's worked example uses 48,000 Hz at 16-bit. Dynamic (host-switchable) sample-rate configuration is explicitly listed as not supported. Sources: [ESP-IoT-Solution, USB Device UAC](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_device/usb_device_uac.html), [component registry page](https://components.espressif.com/components/espressif/usb_device_uac). A complete list of supported rate/depth combinations is not published — unverified.
- **Documented host-compatibility limitation, verbatim from Espressif's readme: the component "Cannot be compatible with both Windows and Linux simultaneously", and enabling the `UAC_SUPPORT_MACOS` macro "may make the device unrecognizable by Windows systems".** Sources: [component registry page](https://components.espressif.com/components/espressif/usb_device_uac), [ESP-IoT-Solution, USB Device UAC](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_device/usb_device_uac.html).

### 1.3 What the Windows host requires

Windows 10 release 1703 and later (including Windows 11) ship an in-box UAC 2.0 class driver, `usbaudio2.sys` (developed by Thesycon, supported by Microsoft). Relevant constraints, all from [Microsoft Learn, USB Audio 2.0 Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/usb-2-0-audio-drivers):

- Supports asynchronous, synchronous and adaptive isochronous endpoints; for asynchronous OUT it supports **explicit feedback only** — implicit feedback is not supported.
- Supports PCM (pulse-code modulation) 8-bit to 32-bit and IEEE-float formats.
- Single clock source only; picky, spec-literal descriptor parsing (exact endpoint sizing, alternate-setting rules, packet-size deviation of at most ±1 audio slot).

### 1.4 Community experience — real projects, real failures

- **ESP32-P4, `usb_device_uac`, high-speed, 8-channel 48 kHz 16-bit (March 2026):** enumerated and played on Linux; Windows enumeration failed. Root cause: the component hardcoded a "+4 byte" feedback allowance in the endpoint-size calculation, correct for stereo but wrong for 8 channels, producing an endpoint descriptor Windows rejects and Linux tolerates. Fixed by recalculating per channel count, one day later. Source: [TinyUSB discussion #3562](https://github.com/hathach/tinyusb/discussions/3562).
- **Generic TinyUSB UAC 2.0, Windows 10 (February 2024):** no feedback packets consumed by Windows, audio glitching after a few seconds; fine on Linux. Resolved by setting the feedback endpoint interval (`bInterval`) to 1. Source: [TinyUSB discussion #2477](https://github.com/hathach/tinyusb/discussions/2477).
- **TinyUSB UAC 2.0 + CDC (communications device class, i.e. virtual serial) composite:** worked on Windows 11 with TinyUSB v0.17.0, broke in v0.18.0 (invalid `bFunctionSubClass` in the audio interface descriptor) — evidence both that an audio+serial composite is achievable and that it regresses between stack releases. Source: [TinyUSB issue #3213](https://github.com/hathach/tinyusb/issues/3213).
- **ESP32-S3 hobby build (September 2025, atomic14 / Chris Greening):** UAC device at 16 kHz/16-bit; microphone-to-host path "very clean"; **host-to-speaker path "very crackly", unresolved by the author**; and the code "works on Mac, but not Windows" or vice versa, needing a build-time toggle. Sources: [atomic14, ESP32-S3 USB UAC](https://www.atomic14.com/2025/09/26/esp32-s3-usb-uac), [Substack version](https://atomic14.substack.com/p/esp32-s3-as-a-usb-audio-device).
- **ESP32-S3 (December 2023):** feature request after a user could not get the raw TinyUSB audio example to enumerate at all on ESP32-S3; Espressif later marked it done (this is what became `usb_device_uac`). Source: [esp-idf issue #12774](https://github.com/espressif/esp-idf/issues/12774).
- Earlier ESP32-S2/S3 silicon needed an isochronous-IN even/odd-frame fix in the TinyUSB DWC2 (DesignWare USB 2.0 controller) driver — without it every second packet was lost. Source: [TinyUSB pull request #1690](https://github.com/hathach/tinyusb/pull/1690). Later isochronous and zero-length-packet fixes for the DWC2 driver landed as recently as TinyUSB 0.21.0. Source: [TinyUSB changelog](https://docs.tinyusb.org/en/latest/info/changelog.html).
- **No published SINAD (signal-to-noise-and-distortion), noise-floor or jitter measurement of any ESP32-family UAC device was found** in this research pass — not on Audio Science Review, not in blogs. The community evidence is functional ("does it play"), never metrological.

### 1.5 Composite capability (audio + HID + serial) — findings

- ESP-IDF's TinyUSB integration supports composite devices and ships CDC, HID (human interface device), MSC (mass storage), MIDI classes; documented composite examples combine MSC + CDC. No official Espressif example combines UAC with HID or CDC. Sources: [ESP-IDF USB Device Stack (ESP32-S3)](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/usb_device.html), [ESP-IoT-Solution TinyUSB Application Guide](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/tinyusb_guide.html).
- TinyUSB itself can build UAC 2.0 + CDC composites (see issue #3213 above, working on v0.17.0); adding HID to a composite is standard TinyUSB descriptor work. That it is *possible* is sourced; that it is *stable across stack upgrades* is contradicted by the same source.

---

## 2. Dedicated USB-audio bridge chips (findings, sourced)

Availability and prices checked 2026-09-02 on the cited pages.

| Chip | UAC version | Max rate / depth | Audio interface out | Price class (1 / 100 pc) | Stock checked | Windows 10/11 driver | Seen in measured products |
|---|---|---|---|---|---|---|---|
| XMOS XU208 (xCORE-200, 8 logical cores, 1000 MIPS) | UAC 1.0 and 2.0 (reference firmware selectable) | PCM 384 kHz / 32-bit, DSD256+ (vendor/product claims) | I²S (inter-IC sound), S/PDIF | US$18.35 / US$13.08 (XU208-256-TQ64-C10, DigiKey) | DigiKey: 228 pcs, 12-week mfr lead ([page](https://www.digikey.com/en/products/detail/xmos/XU208-256-TQ64-C10/5148722)) | UAC2 → in-box `usbaudio2.sys`; Thesycon customised driver for ASIO/DSD (Topping ships one) | Yes — ubiquitous: Topping D10s and many Audio Science Review-measured DACs ([ASR D10s thread](https://www.audiosciencereview.com/forum/index.php?threads/topping-d10s-owner-measurements-quick-review.28462/), [product page naming XU208](https://www.audiophonics.fr/en/dac-without-volume/topping-d10s-dac-usb-32bit384khz-dsd-256-xmos-u208-es9038q2m-black-p-14686.html)) |
| XMOS XU316 (xcore.ai, 16 cores, 2400 MIPS) | UAC 1.0 and 2.0 | PCM 44.1–768 kHz, DSD64–512 (vendor/product claims: [XMOS](https://www.xmos.com/usb-multichannel-audio/), [Douk U2 Pro](https://doukaudio.com/products/douk-audio-u2-pro-xmos-xu316-digital-interface)) | I²S, S/PDIF, SPI, UART | US$13.05 / US$9.21 (XU316-1024-QF60B-C24, DigiKey); US$13.45 / US$9.54 (LCSC) | DigiKey: 1,015 pcs, 12-week lead ([page](https://www.digikey.com/en/products/detail/xmos/XU316-1024-QF60B-C24/16839845)); LCSC C6617472: 17 pcs ([page](https://www.lcsc.com/product-detail/C6617472.html)) | Same as XU208 | Yes — e.g. Topping E70 ([listing naming XU316](https://www.ebay.de/itm/285073047296)) and current Topping/SMSL generations |
| Comtrue CT7601 / CT7601PR (embedded 8051, single 12 MHz crystal, LQFP-80 or QFN-48) | UAC 2.0 (UAC 1.0 fallback mode: unverified) | PCM 768 kHz / 32-bit over USB/I²S/S/PDIF; DSD to 8× ([Comtrue product brief, mirrored](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588897237044219904)) | I²S, S/PDIF, DSD port | Quote required — no Western distributor price published | DigiKey/Mouser: none found; LCSC search: none; JLCPCB parts library lists "CT7601-USB" as C9900208305 (special-order) ([JLCPCB](https://jlcpcb.com/partdetail/JLCPCBAssembly-CT7601USB/C9900208305)) | UAC2 → in-box `usbaudio2.sys` (vendor ASIO driver: unverified) | Budget dongles and DIY cards; discussed as an XMOS alternative on [diyAudio](https://www.diyaudio.com/community/threads/2020-choice-of-usb-audio-bridge.351441/); no ASR-measured flagship identified (unverified) |
| Savitech SA9023 (Bravo/SaviAudio lineage) | UAC 1.0, full-speed | 96 kHz / 24-bit (32–96 kHz, 16/24-bit), adaptive isochronous by default, asynchronous option ([hifiduino](https://hifiduino.wordpress.com/category/usb-audio/)) | I²S | Grey market only: AliExpress listing US$9.16/pc ([listing](https://www.aliexpress.com/item/4000243245403.html)); franchised: quote required | No DigiKey/Mouser/LCSC stock found; brokers only ([Sierra IC quote page](https://www.sierraic.com/SA9023), Utsource) | Driver-free (UAC 1.0 → in-box `usbaudio.sys` on every Windows) ([Hifime](https://hifimediy.com/windows-drivers-for-hifime-dacs/)) | Budget DACs: HiFimeDIY, Audiophonics U-Sabre ([product](https://www.audiophonics.fr/en/dac-without-volume/audiophonics-u-sabre-usb-dac-24bit96khz-sa9023-es9023-otg-v22e-p-11055.html)) |
| Savitech SA9227 | UAC 2.0, USB high-speed | PCM 384 kHz / 32-bit, DSD64/128 ([datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/1178973/SAVITECH/SA9227.html)) | I²S, S/PDIF | Grey market: quote required | No franchised distributor stock found; Utsource/AliExpress brokers only | UAC2 → in-box `usbaudio2.sys` on Windows 10 1703+; vendor driver for older systems (unverified) | Mid-budget portable DACs (specific measured models: unverified) |

Identity note: "Bravo" is not a separate current vendor — Savitech's SA-series carries "SAVITECH DSP by SAVIAUDIO BRAVO" branding in its own literature. Source: [SaviAudio Bravo SA9023 brochure (PDF)](http://www.popular-hifi.com/projects/nad_stereo/racoon_sg300/bravo_sa9023.pdf).

Additional XMOS findings:
- The XMOS reference firmware (`sw_usb_audio` built on `lib_xua`) is a maintained, complete UAC implementation including **HID playback controls (volume, mute, transport)**, DFU (device firmware upgrade class) field update, and hooks for inserting user endpoints such as CDC into the composite. Sources: [lib_xua on GitHub](https://github.com/xmos/lib_xua), [XMOS USB Audio design guide](https://www.xmos.com/file/sw_usb_audio-sw_usb_audio-design-guide), [XM-008854-UG configuration defines](https://www.xmos.com/documentation/XM-008854-UG/html/doc/rst/api_xua_conf.html).
- XU208 requires external quad-SPI boot flash; the XUF208 variant integrates it and is also listed at DigiKey ([XUF208-256-TQ64-C10](https://www.digikey.com/product-detail/en/xmos/XUF208-256-TQ64-C10/880-1112-ND/5358025); stock quantity not captured — check before ordering).

**Assessment (bridge table):** XMOS is the only option with franchised-distributor stock, a maintained open reference firmware, and a deep record in exactly the products the 60 will be measured against. Comtrue and Savitech are cheaper in principle but are quote-required, Asia-broker sourcing at a 60-unit scale — the sourcing risk erases the BOM (bill of materials) saving. Between XMOS parts, the XU316 is currently cheaper than the XU208 at DigiKey and better stocked (1,015 pcs vs 228 pcs) because it is the current generation.

---

## 3. Two USB functions, one USB-C port (composite/hub wiring)

Findings:

- **Hub chip route:** Microchip USB2422, a 2-port USB 2.0 hi-speed hub controller with I²C-configurable descriptors, QFN-24 4×4 mm: LCSC C220747, 44 pcs in stock, US$2.193 at 1 pc / US$1.413 at 100 pcs. Sources: [LCSC product page](https://www.lcsc.com/product-detail/USB-ICs_Microchip-Tech-USB2422-I-MJ_C220747.html), [Microchip product page](https://www.microchip.com/en-us/product/usb2422). Cheaper 4-port hobby-grade alternatives exist and are widely used in DIY hardware: Terminus FE1.1s and Corechip SL2.1A ([open-source SL2.1A Type-C hub design](https://github.com/Hugoyhu/SL2.1A-Type-C-Hub), [DigiKey forum on FE1.1s](https://forum.digikey.com/t/fe1-1s-usb-2-0-high-speed-4-port-hub-controller-from-terminus-technologies/24300)).
- **Bridge-side composite route:** the XMOS reference design already enumerates audio + HID + DFU as one composite device (sources in section 2), so transport keys can come from the XMOS itself, fed by the ESP32-P4 over a wire-level link (I²C/UART/GPIO — the reference design reads physical buttons).
- The ESP32-P4 has *two* USB device controllers (the high-speed OTG and a full-speed USB-Serial-JTAG/OTG 1.1 sharing the full-speed PHY). Sources: [ESP-USB Programming Guide](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_device.html), [ESP-FAQ](https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/usb.html).

**Assessment (wiring):** the clean architecture for the 60 is: USB-C receptacle → USB2422-class 2-port hub → port 1: XMOS (UAC 2.0 audio, optionally its own HID/DFU) and port 2: ESP32-P4 high-speed OTG as HID media transport plus a CDC channel for the companion app and flashing. If a dedicated recovery/console port is wanted, a 4-port hub can also expose the P4's full-speed USB-Serial-JTAG. Added cost is roughly the hub chip (about US$2 at 100 pcs, LCSC price above) plus passives. Internal hubs are standard practice for multi-function USB products sharing one connector. Power note (assessment): everything downstream shares the 5 V / 1.5 A budget; the hub must be configured consistently with the device's declared USB power draw.

---

## 4. Latency and jitter: asynchronous vs adaptive/synchronous

Findings:

- In adaptive mode the device recovers its audio clock from the incoming USB data rate; in asynchronous mode the device runs its own local master clock and steers the *host* via a feedback endpoint, so the DAC clock never tracks USB bus timing. Sources: [Stereophile, HRT Music Streamer measurements](https://www.stereophile.com/content/hrt-music-streamer-usb-da-converter-measurements), [hifiduino USB audio notes](https://hifiduino.wordpress.com/category/usb-audio/).
- Measured comparison (Archimago, 2013): the adaptive-mode AUNE X1 showed "numerous sidebands with spurious noise" on the J-test, though below −100 dB relative to the 11 kHz tone; the asynchronous CM6631A interface showed "minimal data correlated sidebands", stable even at 100 % host CPU load. His conclusion: real on the analyser, most likely inaudible on decent gear. Source: [Archimago measurements](http://archimago.blogspot.com/2013/03/measurements-adaptive-aune-x1.html).
- Measured asynchronous XMOS product (Topping D10s, XU208): J-test sidebands below approximately −130 dBFS, jitter judged a non-issue. Sources: [ASR owner measurements thread](https://www.audiosciencereview.com/forum/index.php?threads/topping-d10s-owner-measurements-quick-review.28462/), [Archimago's D10s measurements](http://archimago.blogspot.com/2021/07/measurements-topping-d10s-inexpensive.html).
- The Espressif component is *also* asynchronous-with-feedback (section 1.2), and Windows accepts only explicit feedback (section 1.3). When the feedback path misbehaves on Windows, the failure mode is not subtle jitter but audible glitching within seconds ([TinyUSB discussion #2477](https://github.com/hathach/tinyusb/discussions/2477)).

**Assessment (jitter):** the sync-mode question is settled in favour of asynchronous, and both candidate architectures (ESP32-P4 native and every listed bridge except the SA9023's default adaptive mode) are asynchronous. The real differentiators are (a) the quality of the local audio clock feeding I²S — XMOS boards use dedicated audio crystals, while the ESP32-P4's I²S clock would come from an on-chip phase-locked loop whose audio-band phase noise is unmeasured (unverified either way) — and (b) implementation maturity of the feedback/descriptor plumbing on Windows, where the ESP32 path has a documented record of breakage and the XMOS path has a decade of shipped, measured products. No comparable measured latency figures for either path were found (gap); for playback-only use, latency is secondary to glitch-free streaming.

---

## 5. Which architecture de-risks the least-trusted path (assessment)

**The bridge-chip architecture — XMOS XU316 behind a 2-port hub — is the de-risking choice.**

1. The ESP32-P4-native path's only UAC implementation carries a vendor-documented inability to serve Windows and Linux (and macOS) with one build, needed descriptor bug-fixes as recently as March 2026 to enumerate on Windows at all, and has zero published audio measurements. The 60's audio must clear measurement scrutiny on Windows specifically; this is the wrong foundation to bet on unproven.
2. The XMOS path is what the reference-class desk DACs ship and what Audio Science Review measures well; parts are in franchised stock today at roughly US$9–13 at 100 pcs; the reference firmware already includes the HID transport controls and DFU field-update the product needs.
3. The composite problem is solved for about US$2 with a stocked hub chip, and it decouples the audio function (never re-flashed, never crashed by application code) from the interactive firmware — a longevity argument matching the 60's service strategy.

The ESP32-P4-native option deletes two chips and is not dead — but it must earn its place on a bench.

### The kill-or-keep bench experiment for ESP32-P4 native audio

- **Hardware:** the Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C already in hand; I²S out to a known-good DAC board (a PCM5102A module for a first pass; the project's ES9219Q path when available); measurement chain = a measurement-grade analogue-to-digital converter (e.g. E1DA Cosmos ADC or an RME interface) into REW on the PC.
- **Firmware:** `espressif/usb_device_uac` pinned at v1.3.1 on the high-speed port, speaker-only, two builds: 48 kHz/16-bit and 96 kHz/24-bit. Then add HID (consumer-control) and CDC interfaces to the TinyUSB descriptor set alongside the audio function.
- **Measure, on Windows 11 with the in-box `usbaudio2.sys` only:**
  1. Enumeration: binds to `usbaudio2.sys`, appears as an audio endpoint, survives 50 replug/reboot cycles — including with the HID+CDC composite present.
  2. Glitch soak: 24 h continuous playback captured by the ADC; count dropouts (target: zero).
  3. SINAD / THD+N (total harmonic distortion plus noise) at 1 kHz, −3 dBFS, and the noise floor with display, Wi-Fi, LEDs and (rig) motor drive all active — the shared-silicon interference question no datasheet answers.
  4. Jitter: 12 kHz J-test (24-bit), FFT of the analogue output; compare sideband structure against the published Topping D10s plots.
  5. Windows volume/mute from the sound panel actually reaching the feature unit.
- **Kill criteria (proposed thresholds, ours not sourced):** failure to enumerate reliably as a composite on stock Windows 11; any audible glitch in the soak; or data-correlated J-test sidebands above roughly −110 dBFS — any one, unfixed after a timeboxed week, kills the native option and the XU316 + USB2422 architecture is adopted.

---

## Confidence and gaps

**High confidence (primary or multiple sources):** ESP32-P4 high-speed 480 Mbit/s device capability; `usb_device_uac` being UAC 2.0, asynchronous with explicit feedback; the component's documented Windows/Linux mutual exclusivity; Windows 10 1703+ in-box UAC 2.0 driver behaviour (explicit feedback only, strict descriptors); XMOS XU208/XU316 pricing and stock at DigiKey/LCSC on the research date; XMOS reference firmware's HID + DFU + composite hooks; USB2422 hub price/stock; the asynchronous-vs-adaptive measured jitter direction.

**Medium confidence:** CT7601 specifications (vendor brief via third-party mirrors; Comtrue's own links returned HTTP 404 during this pass); SA9227 specs (datasheet aggregator, not vendor-direct); XU316 maximum rates (vendor marketing page and product listings, not the datasheet itself).

**Gaps / unverified:**
- No public audio measurements (SINAD, noise, jitter) of any ESP32 UAC device exist — the bench experiment is the only way to get them.
- ESP32-P4 I²S/PLL clock phase noise in the audio band: unverified either way.
- `usb_device_uac` full supported sample-rate/bit-depth matrix at high speed: not published; needs reading the Kconfig or asking Espressif.
- CT7601 and Savitech unit pricing and minimum order quantities: quote required.
- Whether specific measured products use CT7601 or SA9227: unverified.
- XUF208 (flash-integrated XU208) current stock quantity: not captured.
- Comparable measured latency figures for ESP32-native vs bridge paths: not found.
- XMOS 12-week manufacturer lead time means stock must be re-checked at commit time for the 60-unit run.
