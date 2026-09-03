# Handoff — firmware session, 2026-09-03

Paste this whole file into a fresh session. Transient: delete it once the work below has moved on.

## What this is and which track

**Radial** — a desk knob that controls Spotify directly against the Spotify Web API, no PC companion process. This handoff is the **standard build**: the one-off device on the Waveshare ESP32-S3-Knob-Touch-LCD-1.8, 360×360 round screen, rotary dial, **no push switch of any kind**. Governed by `BUILD.md`. Not the halo project (the 60), whose docs live in `docs/` and must not have their constraints applied here.

The firmware and its companion are named **TorqueOS** (`docs/SOFTWARE-CONTEXTS.md`); the shell's log tag is `torque-os`, and per-app tags are `spotify`, `clock`, `settings`, `selector`.

## Read these first, in this order

1. `WAVE-7.md` — the wave in flight (the Clock app, the timer, the selector, Settings). Its checkpoints carry every hardware finding from today.
2. `WAVE-4.md` — the app shell and Spotify inside it. Checkpoints B and D have passed; **the memory investigation at the end of it is the live issue** (see below).
3. `docs/SOFTWARE-INTERACTION-CORE.md` — the settled interaction mechanics both builds implement, with `design/simulator.html` as the reference implementation.
4. `BUILD.md` sections 5 and 6 — the interaction model and the firmware design, including the `knob_app_t` app contract.

`WAVE-3.md` is complete but not yet folded back into `BUILD.md`.

## Who does what

Claude writes every line of firmware; Ryan never edits a source file. Claude compile-checks before handing over a flash; Ryan runs the flash and reports what the hardware and the log do. The board is on his desk.

**Compile check**, from any PowerShell:

```powershell
$env:IDF_TOOLS_PATH='C:\Espressif'
$env:IDF_PYTHON_ENV_PATH='C:\Espressif\python_env\idf5.5_py3.11_env'
& 'C:\Espressif\frameworks\esp-idf-v5.5.5\export.ps1' | Out-Null
cd D:\Projects\PROD\spotify-knob\firmware\knob; idf.py build
```

Both environment variables are required. **Ryan's flash loop** — the `cd` is not optional, because the ESP-IDF shortcut opens in the IDF install directory and `idf.py` builds whatever directory it is standing in:

```powershell
cd D:\Projects\PROD\spotify-knob\firmware\knob
idf.py -p COM7 flash monitor
```

`Ctrl+]` first if a monitor is already running. Board on COM7, rear USB-A port, never the monitor's USB hub. If it will not connect, flip the USB-C plug at the board end before debugging anything else.

## The one thing waiting for an answer

A **memory leak of 5–7 KB per HTTPS request** took the device from 80 KB free internal RAM to 5 KB in about two minutes of polling, after which TLS failed. Two fixes were made; the second is unverified.

1. **HTTP connection reuse** (landed, confirmed working): one `esp_http_client` for the life of the active app instead of one per poll. Proven by a single `Certificate validated` per session rather than one every five seconds. **This was not the leak** — the heap fell at the same rate with it in place — but it is correct and stays.
2. **`CONFIG_MBEDTLS_DYNAMIC_BUFFER` turned off** (landed, **unverified on hardware**). This is the actual suspect: the failing allocation was always reporting `Dynamic Impl: alloc(4437 bytes) failed`, and `Dynamic Impl` is that option's own allocator. The reasoning is written into `sdkconfig.defaults` so nobody re-enables it to save RAM.

**The next thing to do is read a log.** The shell prints heap telemetry every 30 s:

```
torque-os: heap: N internal (N largest), N DMA (N largest), N PSRAM
```

Leave Spotify active for **ten minutes**, not one — the previous build looked healthy for the first ninety seconds. Flat means the leak is closed and Wave 4 can be signed off. Still falling means the dynamic-buffer hypothesis was also wrong, and the next suspects are the per-request `esp_http_client_set_header` / `set_url` calls and the response header list.

**How to read TLS failures here:** `PK verify failed`, `Certificate matched but signature verification failed` and `Failed to verify certificate` all appeared during this hunt and none of them were about certificates. They were malloc failures in disguise. Certificate errors that begin *after* a period of correct operation are a memory symptom.

## Where the work stands

**Wave 2 (board bring-up) — complete.** Screen, touch, dial, haptics all proven. The dial is **not a quadrature encoder**: it is two bidirectional detector switches, one pulse line per direction, driven by `main/bidi_knob.c` ported from Waveshare's demo. It miscounts under fast direction reversal (checkpoint D4 measured drift up to +4 detents over ten fast waggles), which is why the waggle gesture was retired.

**Wave 3 (network and auth) — complete**, closed by Wave 4's checkpoints.

**Wave 4 (app shell, Spotify inside it) — checkpoints B, D and E passed.** Real playback polls and renders; the token forced-expiry test passed and has been removed. Checkpoint C (progress advancing smoothly between polls) has not been explicitly confirmed on glass. The memory issue above is the blocker.

**Wave 7 (Clock, timer, selector, Settings) — built, mostly verified.** Three apps on the selector. Outstanding: Checkpoint D wants heap and PSRAM stable across ten app switches (two round trips looked clean), and Checkpoint F wants Settings confirmed — brightness dimming live, haptics OFF genuinely silencing the clicks, and the chosen brightness surviving a power cycle.

**Wave 5 (album art) and Wave 6 (transport buttons) — not started.** Wave 6's dial half is done: volume and seek both work, chosen at runtime from `supports_volume`, both branches proven on hardware. The transport buttons and play/pause are not built.

## Things that will bite you

- **The Spotify quota is per developer account and is shared with the simulator.** A Live-mode `design/simulator.html` tab left open polls every 3 s and earned the device an 11-hour `Retry-After` on 2026-09-03. Close Live-mode tabs before device testing. `tools/serve_sim.py` no longer auto-opens tabs and the simulator no longer polls while hidden.
- **`ESP_LOGI`'s format argument must be a string literal**, never a ternary — the macro concatenates it. This cost two build failures today.
- **Every `lv_obj_create` object is clickable by default.** A full-screen container that keeps that flag swallows the long-press and the selector can never open from that app.
- **A one-shot LVGL timer (`lv_timer_set_repeat_count(t, 1)`) is deleted by LVGL itself when it fires.** Deleting it again corrupts LVGL's heap and hangs the next allocation. Drop the pointer inside the callback.
- **LVGL's own drawing is far too slow for hundreds of primitives per frame.** The bloom's 300 rays through `lv_draw_line` starved the LVGL task until the watchdog fired; writing pixels straight into the canvas buffer does the same work in 27 ms.
- **Values carried from the simulator to the panel need looking at on glass.** The bloom's opacity range was set against a bright monitor and was invisible on the device until roughly doubled.
- **LVGL draw buffers live in internal DMA-capable RAM**, the scarcest memory on the board. They are at 1/18 of the screen; do not raise that without checking what TLS has left.

## Nothing is committed

Everything from Wave 2 onward is still in the working tree — `git log` ends at `c3c6c71`. New files: `firmware/knob/main/clock_app.{c,h}`, `selector.{c,h}`, `settings_app.{c,h}`, and `WAVE-7.md`. A commit was always intended to close Wave 7 and cover the whole run; `build/`, `managed_components/`, `spotify_tokens.json` and `secrets_local.h` must stay out of it.

`HANDOFF-SCREENS-REV-X.md` belongs to a **separate design session** taking `design/screens.html` from rev W to rev X. Do not touch `design/screens.html`; that session owns it.
