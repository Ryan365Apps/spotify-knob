# Wave 2 — Board bring-up

The current wave, moved out of `BUILD.md` section 10. When the wave is done, its results are written back into `BUILD.md` and this file is deleted.

**Goal:** every piece of hardware this project touches — screen, touch, dial, haptics — proven working under LVGL.

**Who does what.** All code is written by Claude directly into `firmware/knob/main/` — Ryan never edits a source file. Every step below is one of:

- **Already done** — nothing for anyone to do.
- **Info** — background, no action.
- **Claude:** — the code change for the step. Marked *landed* once it is in the repo; otherwise say "do <step>" and it gets written.
- **You:** — Ryan's action: a command to run, and the one thing to look at.
- **Pass when:** — the observable result required before the next step. Do not move on without it.

**Standing facts for the whole wave:**

- Run every command from the **ESP-IDF 5.5 PowerShell** shortcut, in `D:\Projects\PROD\spotify-knob\firmware\knob`.
- The board is on **COM7**, rear USB-A port, A-to-C cable. Not the monitor's USB hub — it swallows the connection (Checkpoint A).
- If anything fails to connect, **flip the USB-C plug at the board end** first: plug orientation selects which of the board's two chips you reach.
- **The re-flash loop, in full, every time:** press `Ctrl+]` in the terminal to kill the running monitor and get the prompt back, then run `idf.py -p COM7 flash monitor`, then look at whatever the step says to look at. Every "You:" step below means exactly this sequence.

---

## Checkpoint A — Reach the right chip — **PASSED 2026-09-02**

Board enumerated as `USB JTAG/serial debug unit` on COM7. Boot log: ESP32-S3 (QFN56) rev v0.2, `Found 8MB PSRAM device`, octal mode, memory test OK.

Two findings, kept for the day this has to be done again:

1. **A USB-C hub gives you a "Billboard Device" and nothing else.** The Aorus monitor's hub completed the Type-C handshake but passed no data; the billboard (Realtek `VID_0BDA&PID_5418`) is the hub's own controller, not the board. Fix: rear USB-A port, A-to-C cable.
2. **The IDF 5.5 hello_world example hides the PSRAM menu.** It ships with `idf_build_set_property(MINIMAL_BUILD ON)` in its `CMakeLists.txt`, hiding every unused component's menuconfig entry, including **ESP PSRAM**. Delete that line before `idf.py menuconfig`. (Irrelevant to `firmware/knob`, whose `sdkconfig.defaults` already sets everything.)

The original step-by-step is in git history (`BUILD.md` Checkpoint A, before 2026-09-02).

---

## Checkpoint B — The screen lights up

**B1 — project skeleton. Already done 2026-08-31.** `firmware/knob/` exists with its target set. Never run `idf.py create-project` or `idf.py set-target` here.

**B2 — dependencies and config. Already done 2026-08-31.** All ten libraries pinned in `main/idf_component.yml`; `sdkconfig.defaults` sets 16 MB flash, octal PSRAM at 80 MHz, custom partition table. No menuconfig needed, ever, in this project.

**B3 — flash the skeleton — PASSED 2026-09-02.** Boot log: `SPI Flash Size : 16MB` (no size warning), 8 MB octal PSRAM at 80 MHz, memory test OK, LVGL 9.5.0, IDF v5.5.5, `all components resolved and linked`. (The `Writing to serial is timing out` spam it ended with is gone as of B4 — the firmware now stays alive after printing.)

### B4 — backlight

**Info:** the simplest thing that proves the firmware can drive the board. If the backlight does not respond, nothing else will work, and it is learned in five lines instead of two hundred.

**PASSED 2026-09-02.** Glow at 50% duty; fully dark at 0% with the log confirming `backlight on GPIO47 at 0%` — GPIO47 controls the backlight and the code path is proven. (50% vs 90% was not distinguishable by eye on an empty panel; the 0% test is the discriminator worth keeping.)

### B5 — the panel

**Info:** the display is a 360×360 round panel, ST77916 driver, QSPI bus. The classic failure is a black screen from a vendor config missing `use_qspi_interface`. No tearing-effect line exists on this board.

**Claude:** *landed 2026-09-02* — QSPI bus + ST77916 init in `main.c` (API verified against the downloaded component header), backlight at 90%, and a loop cycling red, green, blue, white, black two seconds apart, each colour named in the log. Two fixes found on hardware: RGB565 **byte swap** (colours came out mangled — red as blue, blue as green), and **Waveshare's vendor init table** (`main/lcd_init_waveshare.h`, copied verbatim from their demo's 08_LVGL_Test) replacing the component's generic init, which left every colour washed out — their table ends in display-inversion ON, which the generic sequence never sends.

**Info:** light bleeding at the top and bottom edges on full black is backlight bleed — a physical property of the module, worst on all-black at 90% backlight in a dim room. Not fixable in firmware; the real UI's adaptive backlight and on-screen content make it recede.

**You:** `idf.py -p COM7 flash monitor`, then watch the screen for two full cycles.

**PASSED 2026-09-02 — Checkpoint B done.** Full cycle (red, green, blue, white, black) correct and saturated with the vendor init table in. On full black at 90% backlight the module shows edge glow and faint white lines from its light guide; at 40% they are nearly invisible — physical backlight structure, scales with duty, not a pixel defect. Backlight left at 40% as the working default.

---

## Checkpoint C — LVGL and touch

### C1 — the display under LVGL

**PASSED 2026-09-02.** `esp_lvgl_port` drives the panel; buffers ~1/10 screen in internal DMA-capable RAM, `swap_bytes` doing the byte-order fix proven in B5. Boot log clean, `LVGL display registered`.

### C2 — first pixels through LVGL

**Claude:** *landed 2026-09-02* — white `hello` centred on a black screen.

**PASSED 2026-09-02.** White `hello` centred on black, clean.

### C3 — the touch controller

**Info:** touch (CST816) and haptics (DRV2605, Checkpoint E) share one I²C bus. The bus handle created here is the one and only — Checkpoint E reuses it.

**Claude:** *landed 2026-09-02* — I²C bus on SDA 11 / SCL 12 at 400 kHz, CST816 registered with LVGL, bus handle kept file-global for Checkpoint E.

**PASSED 2026-09-02.** `touch registered` in the log, no I²C errors.

### C4 — touch proves itself

**Claude:** *landed 2026-09-02* — 220×220 centred button, blue normally, red while pressed, replacing the label.

**PASSED 2026-09-02 — Checkpoint C done.** Button responded across its whole face, coordinates correct, nothing outside it triggered.

---

## Checkpoint D — The dial

**D1 — wiring facts. Info only, corrected 2026-09-02.** Dial lines on GPIO8 (`EC1_A`) and GPIO7 (`EC1_B`). **The dial is not a quadrature encoder** — the first D3 attempt with the stock `espressif/knob` component read nothing (detents clicked, count stayed 0). The schematic's two SSCM110100 parts are bidirectional detector switches: one line pulses per detent clockwise, the other per detent anticlockwise. Waveshare's demo ships its own modified driver for this; it is ported into this project as `main/bidi_knob.c` (renamed symbols so `espressif/knob`, which `esp_lvgl_port` needs at compile time, still links). `BUILD.md` section 3 corrected. No push switch exists; `espressif/button` stays compile-only.

### D2 — register the encoder

**Claude:** *landed 2026-09-02, together with D3* — encoder on the knob component with detent-event callbacks. LVGL indev registration deliberately deferred to Wave 7 (the selector is the first thing that navigates); raw detent events are what is under test here.

**PASSED 2026-09-02** — after the D1 correction above; `bidi_knob` driver up, `encoder registered` in the log.

### D3 — direction and step size

**Claude:** *landed 2026-09-02* — the big button replaced by a large centred number; clockwise +1, anticlockwise −1 per detent.

**PASSED 2026-09-02.** Ten detents clockwise read exactly +10, ten back read exactly 0; directions correct, one click = one step. Checkpoint D closes at D4 below.

### D4 — the reversal test

**Info:** cheap encoders emit phantom counts on fast direction changes. If this one does, two things break at once: volume accuracy during corrections, and the waggle gesture (`BUILD.md` section 5), whose entire safety argument is that a waggle nets to zero.

**You:** with D3's counter on screen — note the number, waggle the dial fast left-right-left-right, stop, note the number again. Ten times. Read the ten drifts to Claude.

**RUN 2026-09-02 — FAILED, finding recorded.**

Measured drift over ten fast waggles: **+2, +1, 0, −2, 0, +1, +1, +2, +3, +4**. Eight of ten runs nonzero, bias clockwise, worst single run +4 detents.

What this breaks and what it doesn't:

- **The waggle's net-zero safety argument is void.** A recognised waggle can no longer be assumed to leave volume untouched — at ±5% per detent, +4 drift is a 20% volume jump. The section 5 design must be amended before Wave 10: the gesture detector, which already sits upstream of the debouncer (`raw detents → gesture detector → debouncer → active app`), must **swallow** the detents of a recognised waggle rather than rely on them cancelling. The open question becomes the unrecognised case — a waggle-like burst that fails detection and leaks drift into volume.
- **Slow corrections are unaffected.** D3 showed ten slow detents each way count exactly; drift appears only under fast reversal. A genuine overshoot correction contains a pause and modest speed, so its exposure is small — but this is asserted from the D3/D4 contrast, not separately measured.
- Driver-side tuning (the ported driver polls every 3 ms with a 2-tick debounce) might reduce the drift; whether the source is electrical bounce or the detector switches mid-travel during reversal is not established. Worth one tuning experiment before Wave 10, not worth blocking Wave 2.

---

## Checkpoint E — Haptics on the touch bus

**Info:** the DRV2605 has no managed component; its driver is a small set of hand-written register writes on C3's existing I²C bus handle. A second bus handle is the classic failure and must not be created.

**Claude:** *landed 2026-09-02* — hand-rolled DRV2605 driver in `main.c` on C3's bus handle (ERM motor, library 5, internal trigger, per the vendor demo); one strong-click effect per detent from the dial callback. Touch test built in: **tapping anywhere on the screen resets the counter to 0**.

**PASSED 2026-09-02 — Checkpoint E done.** One crisp click per detent, counting still exact, and the screen tap resets the counter — touch alive with haptics on the shared bus.

---

## Done when

- [x] Boot log shows `esp32s3` and `Found 8MB PSRAM` (Checkpoint A, 2026-09-02)
- [x] Real project flashes with 16 MB flash and PSRAM intact (B3, 2026-09-02)
- [x] Screen cycles solid colours with no offset, vendor init table in (Checkpoint B, 2026-09-02)
- [x] A touch button responds correctly across the whole screen (Checkpoint C, 2026-09-02)
- [x] One detent moves the counter by exactly one, both directions (Checkpoint D2/D3, 2026-09-02); ten fast waggles do **NOT** net to zero — drift +2,+1,0,−2,0,+1,+1,+2,+3,+4 recorded at D4, waggle design must be amended before Wave 10
- [x] One haptic click per detent, with touch still working (Checkpoint E, 2026-09-02)
- [ ] Committed, with no `build/` or `managed_components/` in the commit
- [ ] Results written back into `BUILD.md` (including D4's measured drift) and this file deleted
