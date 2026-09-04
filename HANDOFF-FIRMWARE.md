# Handoff — firmware session

Paste this whole file into a fresh session. Transient: delete it once the work below has moved on.

**Last updated 2026-09-04**, after Waves 3, 4, 5, 6 and 7 were folded back into `BUILD.md` and Wave 8's code landed. This file used to carry a great deal of hard-won detail that `BUILD.md` did not; it now carries almost none, because that detail is in `BUILD.md` where it belongs.

## What this is and which track

**Radial** — a desk knob that controls Spotify directly against the Spotify Web API, no PC companion process. This handoff is the **standard build**: the one-off device on the Waveshare ESP32-S3-Knob-Touch-LCD-1.8, 360×360 round screen, rotary dial, **no push switch of any kind**. Governed by `BUILD.md`. Not the halo project (the 60), whose docs live in `docs/` and whose constraints must not be applied here.

The firmware and its companion are named **TorqueOS** (`docs/SOFTWARE-CONTEXTS.md`); the shell's log tag is `torque-os`, and per-app tags are `spotify`, `art`, `clock`, `settings`, `selector`.

## Read these first, in this order

1. **`BUILD.md` section 8, the build plan** — Waves 0 through 7 are complete, and each one's results and findings are written up there. Read Waves 4 through 7 before touching anything network-, memory- or drawing-related; they are where every expensive lesson on this board is recorded.
2. **`BUILD.md` section 6, the firmware design** — the `knob_app_t` app contract, who owns what, the polling and token rules, the album art pipeline, and two subsections that exist because they were paid for: *Drawing, and what it costs* and *Traps this build has already paid for*.
3. **`BUILD.md` section 10** — the current wave, and the design decisions still open.
4. **`WAVE-8.md`** — the current wave, step by step.
5. **`BUILD.md` section 4, working with the board** — the compile-check command, the flash loop, and why the `Compile time` line in the boot log lies about which build is running.
6. `docs/SOFTWARE-INTERACTION-CORE.md` — the settled interaction mechanics both builds implement, with `design/simulator.html` as the reference implementation.

## Who does what

Claude writes every line of firmware; Ryan never edits a source file. Claude compile-checks before handing over a flash; Ryan runs the flash and reports what the hardware and the log do. The board is on his desk, on COM7, in a rear USB-A port. Both commands are in `BUILD.md` section 4.

## Where the work stands

**Waves 0 through 7 are complete and verified on hardware.** Wi-Fi and auth, the app shell, Spotify, album art, controls, the Clock with its timer, the selector, and Settings. Three apps on the selector, all switching cleanly with heap and PSRAM returning to identical figures.

**Wave 8 (live-on-the-desk robustness) is in progress.** All four missing pieces of code landed 2026-09-04 and the build is clean: 5xx and transport backoff, Wi-Fi reconnect backoff, the task watchdog made to panic rather than merely complain, and a boot line naming the last reset. **None of it has been on hardware yet.** What remains is a flash and three soaks — see `WAVE-8.md`, which also carries three Wave 6 items that were never confirmed on glass.

**Waves 9, 10 and 11 are not started**, and section 8 describes each in full:

- **Wave 9 — serviceability.** The largest remaining wave: Wi-Fi provisioning over SoftAP with a captive portal and QR, the Windows scheduled task that re-authorises on day 170, `tools/reauth.py`, an `esp_http_server` config endpoint gated by a 120-second boot window, and the fallback screen. Read it in full before starting — the ordering matters.
- **Wave 10 — Wispr Flow.** NimBLE HID keyboard, keyboard only, bond in NVS. Measuring Wi-Fi throughput with BLE connected and disconnected is part of the wave, not an afterthought.
- **Wave 11 — Launcher.** Mode 1 is the ring, the config-page editor, the fixed chord enum and the eight-entry cap. Mode 2 is Task View driving. Build mode 1 first.

**The HID scroll control** is not a separate wave — it is the dial half of Waves 10 and 11, and it depends on the BLE HID path existing. Wave 10 is where that path gets proven.

## Hard rules that bear on this work

**No string typed by a human may ever become a keystroke.** The device will be a BLE HID keyboard and its HTTP config server is LAN-reachable. Chords are always an enum or dropdown, never free text. `BUILD.md` section 6 states this in full. It constrains Wave 11's editor directly: the chord field cannot accept free text, and that is a done condition, not a preference.

**USB HID and the flashing port share the same peripheral.** Firmware must use BLE HID, never USB HID, or the board can be bricked. Wave 10 depends on this being respected.

**`spotify_tokens.json` holds a live refresh token.** Never commit it, print it, or serve it.

**The Spotify quota is per developer account and shared with the simulator.** A Live-mode `design/simulator.html` tab polling every 3 s earned an 11-hour `Retry-After` once. Close Live-mode tabs before device testing.

## Nothing from this run is committed

`git log` ends at `7c6df99`. **`firmware/knob/main/bloom.{c,h}` and `albumart.{c,h}` are untracked**, so a stray `git clean` would take them permanently. Ryan has said not to worry about commits, so this is stated as exposure rather than a request.

`build/`, `managed_components/`, `sdkconfig`, `spotify_tokens.json` and `secrets_local.h` must stay out of any commit; `.gitignore` already covers all of them and nothing hazardous is tracked.

The working tree also contains a large amount of **halo-project** work — `design/cad/`, `design/artwork/drawings/`, `docs/Claude outputs/`, `docs/BoughtPartDimensions.md`, `docs/v9/`. That belongs to the 60 and to a different session. Do not fold it into firmware commits.

## The screens document is owned elsewhere

`design/screens.html` rev W is owned by a separate session taking it to rev X — **read it, never edit it**. Three built-in deviations from rev W are listed at the end of `BUILD.md` section 10 and should be reconciled once that session releases the file.
