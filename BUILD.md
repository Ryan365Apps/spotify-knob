# Radial — Build Document

**Target hardware:** Waveshare ESP32-S3-Knob-Touch-LCD-1.8
**Status:** pre-build. No code written yet.
**Scope of this document:** current requirements and the plan to meet them. It is not a changelog — when requirements change, this document is edited, not appended to.

---

## 1. What it must do

A permanently-powered desk device that removes the "wake phone → find Spotify → tap" loop.

| # | Requirement |
|---|---|
| R1 | Show the currently playing track's album art, large, on the round 360×360 screen |
| R2 | Show track title and artist |
| R3 | Skip to next / previous track from on-screen buttons, one tap from the default screen |
| R4 | Toggle play/pause from the screen |
| R5 | The dial controls **volume** by default. Where the active device refuses volume it controls **track seek** instead, chosen at runtime (see the Wave 0 result below). SEEK can also be assigned by hand from the controls screen — for one adjustment, reverting to volume when the overlay clears |
| R8 | Move playback to the PC from the device, so the dial regains volume control without picking up the phone |
| R9 | **Spotify is one app of several.** The device runs an app shell: a long-press opens a radial selector, the dial scrolls through apps like a Galaxy Watch bezel, a tap enters one. Spotify, Clock, Wispr Flow, the Launcher and Settings are in scope; the architecture must not have to change to add a sixth |
| R10 | Brightness, sleep timeout, haptics and dial step are adjustable on the device without a computer. **No setting ever requires typing** — the dial picks from a list, and anything needing a keyboard goes through the Wave 9 config page |
| R11 | **Setup is scan, type once, watch.** Config mode puts a scannable QR on the screen so no address is ever typed, and the device narrates every step of joining — live, to the phone and to its own screen — so a failure names itself instead of appearing as a silent reboot |
| R6 | Work against playback on a phone or a Connect speaker — **not** the PC |
| R7 | Boot on power-up, reconnect on its own, and require no interaction on a normal day |

### Explicit non-goals

Playing audio on the device. Playlist browsing. Search. Library management.

**Apps beyond Spotify, the Clock, Wispr Flow, the Launcher and Settings are explicitly out of scope for this build.** R9 requires the *shell* to exist and the app contract to be honoured — not a library of apps. The Granola record button remains a candidate for later and does still need a companion process on the PC, which this project deliberately does not have. Wispr Flow does not — see section 6.

### Verified constraints

**2026-08-31 — Wave 0 result.** Volume control was tested against two playback devices:

| Device | `supports_volume` | Volume command |
|---|---|---|
| Android phone (primary listening device) | `false` | `403 VOLUME_CONTROL_DISALLOW` |
| Windows desktop (Spotify desktop app) | `true` | `204` accepted |

The phone's refusal is a Spotify-side restriction on that class of device — not a fault, and there is no workaround. Because at least one real device does accept volume, **both variants of the second dial mode are in scope** and the choice is made at runtime. Album art is available at 640×640 on both.

**2026-08-31 — endpoint pre-flight, all clear.** This app's Client ID was created after Spotify's 11 February 2026 change, which restricts new Client IDs to "a smaller set of supported endpoints". Every endpoint the build depends on was therefore tested against live credentials (`tools/preflight_endpoints.py`):

| Endpoint | Requirement | Result |
|---|---|---|
| `GET /me/player` | Waves 3–7, every poll | 200 |
| `GET /me/player/devices` | R8 | 200 |
| `PUT /me/player/volume` | R5 | 204 on desktop, 403 on phone (expected) |
| `PUT /me/player/seek` | R5 fallback | 200 |
| `PUT /me/player` (transfer) | R8 | 204 — **requires a `device_ids` JSON body** |
| `PUT /me/player/pause` and `/play` | R4 | 200 |
| `POST /me/player/next` and `/previous` | R3 | 200 |

Nothing is restricted. Waves 3–6 can be built as specified. Re-run the script if a requirement ever depends on an endpoint not in this table.

---

## 2. Architecture

**A standalone Wi-Fi device talking directly to the Spotify Web API.**

The knob holds a Spotify refresh token, refreshes an access token hourly, polls `GET /me/player` for state, downloads album art over HTTPS, and issues control calls. Nothing else on the network is involved, and no software runs on any PC.

This is forced by R6. Because audio plays on a phone or a speaker, anything that reads now-playing state from the desktop is blind — the PC has no idea what the phone is doing. The cloud API is the only source of truth that follows playback wherever it goes.

### Constraints this creates

- Spotify **Premium is mandatory** — every Web API playback-control endpoint refuses free accounts.
- Control latency is a cloud round trip, roughly 150-400 ms from the UK, plus Spotify's own propagation to the phone. Responsive, but not instant.
- State is **polled, not pushed**. The screen lags reality by up to one poll interval when the track is changed on the phone.
- The refresh token expires **6 months after authorisation**. Re-authorisation is a scheduled chore (see Wave 9).
- TLS, JSON parsing and JPEG decoding all happen on the ESP32. This is the bulk of the firmware work.
- Volume is the only control the target playback device can refuse, and one of the two devices in use does refuse it. The second dial mode must therefore be chosen at runtime from `device.supports_volume`, never assumed or compiled in.

---

## 3. Hardware facts

| Item | Detail |
|---|---|
| Main MCU | ESP32-S3R8, 240 MHz, 8 MB PSRAM, 16 MB flash |
| Second MCU | ESP32-U4WDH, 4 MB flash. Provides **Classic Bluetooth (BR/EDR)**, which the S3 lacks — the S3 is BLE-only — and drives the audio subsystem. Unused here; UART link on GPIO48/38 |
| Display | 1.8" round, 360×360, **ST77916** driver, QSPI bus |
| Touch | **CST816** capacitive, I2C |
| Encoder | Mechanical rotary, quadrature, **no push switch** |
| Haptics | DRV2605 over I2C — used for detent feedback |
| Audio | PCM5100A I2S DAC, PDM mic, 3.5 mm jack — unused here |
| Power | USB-C, plus PH1.25 Li-ion socket. Desk use = USB-C permanently |

### Pin map — **verified against the Waveshare schematic, 2026-08-31**

Every line below is read off sheets 1, 2 and 4 of the official schematic. This is the reference; do not re-derive it from community sources.

| Function | GPIO | Signal name on the schematic |
|---|---|---|
| LCD QSPI SCLK | 13 | `LCD_QSPI_SCL` |
| LCD QSPI CS | 14 | `LCD_QSPI_CS` |
| LCD QSPI D0–D3 | 15, 16, 17, 18 | `LCD_QSPI_D0`…`D3` |
| LCD reset | 21 | `LCD_RST` |
| Backlight | 47 | `LCD_BLK`, PWM via an AO3400A |
| Touch SDA / SCL | 11 / 12 | `TP_SDA` / `TP_SCL` |
| Touch INT / RST | 9 / 10 | `TP_INT` / `TP_RST` |
| Haptics, DRV2605 | 11 / 12 | **shares the touch I²C bus** |
| Encoder A / B | 8 / 7 | `EC1_A` / `EC1_B` |
| Battery sense | 1 | `BATT_ADC`, 10K/10K divider off 5V |
| microSD, SDMMC | 2, 3, 4, 5, 6, 42 | `SDMMC_D3, CMD, SCK, D0, D1, D2` |
| USB | 19 / 20 | `USB_DN` / `USB_DP` |
| UART to second MCU | 48 / 38 | `ESP32S3_RX` / `ESP32S3_TX` |

### Three corrections this verification produced

1. **There is no knob button.** The encoder is a four-pin part — A, B and the frame. No push switch exists anywhere on the board, on either encoder. Every "knob press" in an earlier draft of section 5 was wrong.
2. **GPIO0 is not the encoder button.** It carries `I2S_SWITCH_IN`, which selects whether the S3 or the second MCU drives the audio DAC. It remains the boot strapping pin and so still matters for flashing, but nothing user-facing sits on it.
3. **`LCD_TE` is not connected to the S3.** Tearing-effect sync is unavailable; the panel driver must not be configured to expect it.

Two further facts worth having before Wave 2:

- **The haptic driver sits on the touch I²C bus.** One bus, two devices — initialise the CST816 and the DRV2605 on the same `i2c_master` handle rather than creating two. `HAPTIC_EN` is tied to 3V3 and `HAPTIC_TRIG` to ground, so the part is permanently enabled and driven entirely over I²C.
- **The two microcontrollers are wired together** over UART on GPIO48/38, and the S3 can drive the audio DAC directly over I²S on GPIO39/40/41. Unused here, but it means audio output is available later without new hardware.

### Two gotchas that will cost you an hour each if you do not know them

1. **The USB-C cable orientation selects which MCU you flash.** Flip the connector if the board enumerates as the wrong chip. This is a documented board behaviour, not a fault.
2. **There is no BOOT button and no RESET button either.** Sheet 1 shows only SW1 and SW2, and both are SSCM110100 rotary encoders. `CHIP_PU` and `GPIO0` carry 10K pull-ups and nothing else — there is no switch anywhere on the board able to pull either low. Download mode therefore depends entirely on the S3's native USB-Serial-JTAG auto-reset, which normally handles it without intervention. **There is no manual recovery to fall back on**, so if a flash fails, the first move is the cable orientation, not a button.

---

## 4. Toolchain and dependencies

**ESP-IDF v5.5.x.** ESP-IDF v6.0 shipped in March 2026 and is fine in isolation, but the managed components this project leans on — and Waveshare's own board demos — are still written against the 5.x API surface. Wave 0 includes an explicit build check; if everything compiles clean on 6.0, use 6.0.

Build system: `idf.py` directly. PlatformIO is not needed and adds a version-pinning layer between you and the components.

The screen is driven by LVGL in C. There is no web browser for the ESP32, so HTML cannot render on the device's display — something must turn markup into pixels, and that something is a browser engine far larger than this chip can hold. HTML does appear in this project, but only in Wave 9, where the device serves a config page to a browser on your phone.

`main/idf_component.yml`:

```yaml
dependencies:
  idf: ">=5.4"
  lvgl/lvgl: "^9.2"
  espressif/esp_lvgl_port: "^2.7"           # display + touch + encoder glue for LVGL
  espressif/esp_lcd_st77916: "^1.0.1"       # QSPI panel driver
  espressif/esp_lcd_touch_cst816s: "^1.1.2"
  espressif/knob: "^1.1.0"                  # quadrature decoding for the encoder
  espressif/button: "^4.2.0"                # required by esp_lvgl_port, see below
  espressif/esp_jpeg: "^1.3"                # album art decode
```

**`espressif/button` is required even though this board has no button.** `esp_lvgl_port.h` includes `esp_lvgl_port_knob.h` unconditionally, and that header hard-fails with `#error LVLG Knob requires button component` when `iot_button.h` is missing. It is a compile-time dependency of the port layer, not a statement about the hardware — the firmware simply never creates a button handle. Removing it breaks the build of every file that touches LVGL, not just the encoder.

**Known-good resolved set**, from an actual dependency resolution on 2026-08-31 against **ESP-IDF v5.5.5**. If a future build misbehaves, pin to exactly these:

| Component | Resolved |
|---|---|
| `lvgl/lvgl` | 9.5.0 |
| `espressif/esp_lvgl_port` | 2.9.0 |
| `espressif/esp_lcd_st77916` | 1.0.1 |
| `espressif/esp_lcd_touch_cst816s` | 1.1.2 |
| `espressif/esp_lcd_touch` | 1.2.1 (pulled in by cst816s) |
| `espressif/knob` | 1.1.0 |
| `espressif/esp_jpeg` | 1.3.1 |
| `espressif/button` | 4.2.0 |
| `espressif/cmake_utilities` | 0.5.3 (transitive) |

All eight downloaded cleanly with no version conflicts.

Everything else is in-tree ESP-IDF: `esp_wifi`, `esp_http_client`, `cJSON`, `nvs_flash`, and the mbedTLS certificate bundle (`CONFIG_MBEDTLS_CERTIFICATE_BUNDLE=y`) which covers `accounts.spotify.com`, `api.spotify.com` and the `i.scdn.co` image CDN without you pinning any certificates.

### sdkconfig settings that matter

```
CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_OCT=y
CONFIG_SPIRAM_SPEED_80M=y
CONFIG_MBEDTLS_CERTIFICATE_BUNDLE=y
CONFIG_MBEDTLS_DYNAMIC_BUFFER=y          # keeps TLS RAM down
CONFIG_ESP_MAIN_TASK_STACK_SIZE=8192
CONFIG_FREERTOS_HZ=1000
CONFIG_LV_COLOR_DEPTH_16=y
CONFIG_LV_USE_QRCODE=y                   # config-mode QR, Wave 9
CONFIG_BT_ENABLED=y                      # Wave 10 only
CONFIG_BT_NIMBLE_ENABLED=y               # NimBLE, not Bluedroid — roughly half the footprint
```

BLE is off until Wave 10. Turning it on costs somewhere around 150–200 KB of flash and a few tens of KB of RAM, against 95% of a 4 MB app partition currently free — so flash is not the constraint. RAM might be; measure at Wave 10 rather than guessing, since the album art buffer is the other large claimant.

Partition table: custom, single 4 MB app partition (headroom for OTA later) plus NVS. 16 MB flash makes this a non-issue.

---

## 5. Interaction model

Continuous control lives on the dial. Discrete control lives one tap away. Colour carries meaning consistently: **white is progress, green is volume, yellow is seek.**

### NOW PLAYING — the default screen

- Album art fills the circle. A thin white ring traces track progress around the bezel with a chip riding the current position — it earns its place on long podcast episodes even when it is redundant on a three-minute track. It belongs to this screen only; the dial screens replace it rather than layer over it.
- Title and artist, centred, with the title scrolling as a slow marquee only when it overflows.
- **Dial → volume.** Turning it raises the feedback overlay below.
- **Touch anywhere → CONTROLS.**
- **Long-press anywhere → APP SELECTOR.**

**There is no knob press** — the schematic verification in section 3 found no push switch on this board. **Play/pause is therefore the centre button on CONTROLS**, two taps from the default screen. No hidden gestures: no double-tap, no long-press. Decided 2026-08-31.

### Dial feedback — transient, ~2 s

Raised the moment the dial moves, gone two seconds after it stops. Artwork drops to near-black, a phyllotaxis bloom is cut by a wedge, and the value sits in the middle with no label — a percentage in green and a timestamp in amber cannot be mistaken for one another.

- **Volume:** green, 0–100%, ±5% per detent.
- **Seek:** amber, ±10 s per detent — the lit boundary is the playhead.

The bloom is one 300-point field shared by both, and by the idle screen where nothing is lit. Pre-render it once at boot; the only live work is the segments currently on.

Both write once, 400 ms after the last detent. Spin freely; the screen updates locally at every step.

### APP SELECTOR — long-press from any app

The Galaxy Watch bezel model, which is what a round screen and a rotary encoder are for.

- App glyphs sit on a **fan segment** — 36° per app around the fixed marker at twelve o'clock — not spread to the compass points. The selected app sits under the marker with its name filling the centre; its neighbours are one notch either side, and anything further is dimmed right down. Four apps span a quarter of the rim, and a fifth costs one more notch.
- **Dial → one app per detent, with a haptic click on each.** The fan turns under the marker rather than the marker moving, and it has **hard stops at both ends** — a segment does not wrap.
- **Tap the centre → enter the selected app. Tap a glyph → enter that app directly**, wherever it sits on the fan.
- **Long-press again, or 4 s idle → return to the app you came from**, not to the first app. Backing out of the selector should never change what you were doing.

With two apps this is a toggle wearing a carousel's clothes. It is built now anyway, because the cost of adding it later is rewriting whichever app was built without it.

### THE WAGGLE — dictation from any app

The dial is the active app's, and in Spotify that means volume. So the one gesture that has to work everywhere cannot be a rotation, a press or a hold — all of those are already spoken for. It is a **rapid reversal**: flick the dial left-right-left in one wrist movement.

**Definition.** A *reversal* is a detent whose direction differs from the previous detent. The gesture fires on **three reversals inside 600 ms**, each run being one to three detents. Both thresholds are compile-time constants and both will need tuning on real hardware.

**Why this does not fire by accident.** The only time you naturally reverse the dial is correcting an overshoot — too loud, come back two. That correction contains a *pause*: you hear the result before you react, and that dwell is comfortably over 300 ms. A waggle has no dwell in it at all. The discriminator is the gap between reversals, not their number.

**What the app underneath sees: nothing.** The gesture detector does not buffer detents and adds no latency — buffering would put a delay on every genuine direction change, which is exactly the overshoot case and would feel broken. Instead it exploits the debounce that already exists: volume writes accumulate and only go out 400 ms after the last detent, and a waggle's net displacement is zero by construction. So the pending delta cancels itself, no API call is ever sent, and when the gesture fires the accumulated delta is discarded outright. The on-screen number twitches for half a second and the overlay covers it.

Order of processing is therefore: **raw detents → gesture detector → debouncer → active app.**

**What happens on recognition.** A distinct double-click from the DRV2605 — the only haptic in the product that is not a single click — and then the waggle *navigates*:

- **Believed off:** the chord is sent and the device enters the Wispr app, remembering where you came from. The screen in front of you now *is* the believed state — no overlay needed.
- **Believed on, inside the Wispr app:** the chord is sent, dictation is believed off, and you are returned to the app the waggle-on interrupted, with a short DICTATION OFF overlay riding the transition.
- **Believed on, anywhere else:** the chord is sent, the overlay confirms, and you stay where you are.

Inside the Wispr app the waggle never blindly toggles — it only **dismisses**: off if needed, then back. Tap and the directional spins own toggling on that screen (see the mapping in section 6). One waggle in, one waggle out, and the pair nets to nothing but the dictation you did in between.

**Send discipline.** The believed state changes **only when a chord was actually dispatched**, and chords are serialised with at least 600 ms between them — one movement can never double-send, and a suppressed send never flips belief. Decided 2026-08-31, after the simulator produced exactly that double-send and desynced itself.

**It is still a toggle underneath, and Wispr can drop it.** A chord Wispr ignores (see the focus quirk in section 6) flips belief without flipping reality. The Wispr screen states what the device believes; Wispr's own Flow Bar is the truth; the resync spin recovers the difference. Waggle-on landing you on that screen means drift is visible immediately rather than on the next attempt.

### CONTROLS — one tap from the default screen

- **Transport across the middle:** previous, play/pause, next, at full thumb size. This is where skipping lives.
- **Two chips below:** VOLUME and SEEK, assigning the dial. SEEK assigns the dial for one adjustment; when the overlay clears and NOW PLAYING returns, the dial is volume again. The automatic seek fallback on volume-refusing devices is unaffected.
- **Device pill at the top:** shows where audio is playing. Tapping it transfers playback to the desktop via `PUT /me/player`.
- Auto-returns to NOW PLAYING after 5 s.

### Behaviours that need deciding once and then holding

- **Volume availability is read, never assumed.** `GET /me/player` returns `device.supports_volume`, re-checked on every poll. When false — which is the case on the phone — the VOLUME chip greys out and the dial falls back to seek so the knob is never inert. Transferring playback to the desktop re-enables it within one poll.
- **Transfer, not launch — over the API.** `PUT /me/player` moves playback to a device Spotify can already see, which requires the desktop app to already be running. Nothing in the Web API can start or focus an application. **The BLE HID keyboard added in Wave 10 can**, and this is the answer to the launch/focus question the Web API cannot solve: `Win`+`N` activates the Nth pinned taskbar item, launching Spotify if it is closed and focusing it if it is not. One chord, no resident agent, no companion process. It is optional, it belongs to Wave 10 rather than Wave 6, and it depends on the pin position holding — so the position is a Settings value, defaulting to off. See the HID section later in this section.
- **Writes are debounced.** A single call 400 ms after the last detent is what keeps the device inside the rate limit during a long volume sweep.
- **Haptics.** One short DRV2605 click per detent, a heavier one on transport button presses. Cheap to add, and most of what makes the thing feel like a control rather than a screen.
- **Adverts.** `currently_playing_type == "ad"` — show "Advert", suppress the transport buttons. Not applicable on Premium, but three lines that prevent a confusing state.
- **Nothing playing.** `GET /me/player` returns HTTP 204. The screen shows the moiré ray field described in `design/screens.html`, tinted from the last cover's average colour, with the clock over it. The dial does nothing.
- **Sleep.** After 20 minutes idle the backlight goes off entirely and the animation stops — a permanently-powered desk object should not be a permanently-lit one. It wakes on touch, on dial movement, or on playback resuming anywhere.

Screen designs for all of the above live in `design/screens.html`. A working click-through of the whole model — mock playback by default, live Spotify via `python tools/serve_sim.py` — is `design/simulator.html`. Its Wispr toggle is live too: `serve_sim.py` types the bound chord on the PC, standing in for the BLE keyboard.

---

## 6. Firmware design

Four FreeRTOS tasks, one owner of shared state.

```
  spotify_task   ── owns the HTTPS client, the token, and the poll loop
       │              writes into player_state_t under a mutex
       │
  ui_task        ── LVGL tick + render, reads player_state_t
       │              publishes user intents to a command queue
       │
  input_task     ── encoder + touch → LVGL indev (handled by esp_lvgl_port)
       │
  art_task       ── downloads and decodes album art off the UI thread
```

`player_state_t` holds: `is_playing`, `track_id`, `title`, `artist`, `album_art_url`, `progress_ms`, `duration_ms`, `volume_percent`, `supports_volume`, `device_name`, `last_update_tick`. **It belongs to the Spotify app, not to the shell.**

### The app shell (R9)

The shell owns everything shared and nothing app-specific. One app is active at a time; the rest are not merely hidden, they are stopped.

```c
typedef struct {
    const char *name;          /* shown in the selector            */
    const void *glyph;         /* selector icon                    */
    lv_color_t  accent;        /* the app's colour in the UI       */

    void (*on_enter)(lv_obj_t *parent);   /* build widgets, start polling */
    void (*on_exit)(void);                /* free buffers, stop polling   */
    void (*on_dial)(int delta);           /* detents, signed              */
    void (*on_tick)(void);                /* ~1 Hz housekeeping           */
} knob_app_t;
```

**Who owns what.** The shell owns Wi-Fi, the Spotify token refresh, the clock, the backlight and sleep timer, the haptic driver, and the selector itself. Apps own their own screen, their own network calls, and their own buffers.

**`on_exit` must actually free.** The 180 KB album-art buffer is the Spotify app's, and it is over a fifth of the internal-plus-PSRAM budget this project has any business using at once. An app that keeps its buffers alive while inactive turns "add a third app" into a memory problem. Pre-allocate on `on_enter`, release on `on_exit`, and never allocate per frame.

**Suspend the network too.** An inactive app makes no HTTP calls. Spotify's poll loop stops when you leave it, which also means the rate-limit budget is only ever spent by the app you are looking at.

**LVGL:** one `lv_obj_t` screen per app, created in `on_enter` and deleted in `on_exit`, switched with `lv_screen_load_anim()`. Lazy creation rather than one screen per app held permanently — the round display is 259 KB of framebuffer and there is no reason to pay for screens nobody is looking at.

**Token refresh stays in the shell**, not in the Spotify app. It has to keep running while you are looking at the clock, or coming back to Spotify would stall on a refresh.

### Five apps, and only five

**App 1 — Spotify.** Everything in section 5.

**App 2 — Clock.** The moiré bloom and the time, which already exist as the idle screen. Almost free, needs no network, and it is what proves the contract is real: if the Clock cannot be written against `knob_app_t` without touching shell code, the contract is wrong and a third app will break it too.

**App 3 — Wispr Flow.** One keystroke over BLE HID, specified in full later in this section. It is here rather than in a later project because it is the app that proves the shell can own a resource Spotify knows nothing about — the BLE stack — without Spotify having to care.

**App 4 — Launcher.** A short, ordered list of PC applications. The dial scrolls it, a tap sends one chord, and the device returns to Spotify. It has two modes.

**Mode 1 — the curated list.** Up to ten entries, each a label, a glyph and a **chord chosen from a fixed set**: `Win`+`1`–`9` for pinned taskbar items, or `Ctrl`+`Alt`+*key* for anything bound to a Windows shortcut `.lnk`. Entries are configured on the config page. Note the split this preserves — the **label is free text because it is only ever drawn on the screen**, and the chord is an enum. Nothing typed by a human reaches the HID layer, which is the rule from later in this section holding under pressure rather than merely being restated.

A list rather than the rim used by the app selector: the selector holds five familiar glyphs and needs no words, while this holds ten unfamiliar application icons and does. It reuses the Settings list mechanic exactly.

**It cannot confirm anything.** The device has no idea whether the app launched, was already open, or whether the chord landed on a locked screen. So it shows "Launching Slack" for 1.5 s and returns. Anything more confident would be a claim it cannot support.

**Mode 2 — drive Task View.** For the times you want the real window list rather than a list of apps.

**Use `Win`+`Tab`, never `Alt`+`Tab`.** Alt+Tab only stays open while Alt is *held*, so driving it means keeping a modifier down for the whole interaction — the exact thing ruled out earlier, and it would make every click a modified click while you dialled. `Win`+`Tab` opens Task View persistently, survives the release, and takes arrow keys.

| Gesture | Sends |
|---|---|
| Enter the mode | `Win`+`Tab` |
| Dial right / left | `Right` / `Left` arrow |
| Tap | `Enter` |
| Long-press, or 5 s idle | `Esc`, and leave the mode |

The idle timeout matters: without it, walking away leaves Task View open across your whole screen. In this mode the device screen is a legend, not a display — you are looking at the monitor. It shows the mode name and the three actions, and **no position counter**, because it cannot know how many windows exist or which is highlighted. A counter would be invented.

**App 5 — Settings.** Not a feature, a consequence. **There is no operating system on this device.** Every setting a phone gives you for nothing — brightness, network, sleep — either gets implemented here or does not exist. Contents, all of them dial-navigable:

| Item | Behaviour |
|---|---|
| Brightness | Dial adjusts the GPIO47 PWM duty live, 5% per detent, **floor of 10%** so it cannot be turned dark and lost. The setting is its own preview |
| Sleep timeout | Dial through 5 / 10 / 20 / 60 min / never. Currently hardcoded at 20 |
| Haptics | Off / light / firm |
| Dial step | Volume per detent: 2% / 5% / 10% |
| Wi-Fi | **Status only** — SSID and signal — plus a "Config mode" action that opens the Wave 9 server and puts its QR on screen |
| Spotify | Days until re-authorisation, plus "Re-auth now" |
| Dictation | BLE pairing state, and **Forget this PC** — the only destructive action in Settings, so it confirms |
| Launcher | Read-only here. The list is edited on the config page, because naming ten applications is typing |
| About | IP address, firmware version, uptime |

Screens for all of this are drawn in `design/screens.html` — the list (06), a continuous value (07), the pattern every fixed-choice setting uses (08), and both config modes (09 A and 09 B).

### The rule that shapes Settings: no text entry, ever

A 360 px round touchscreen with no keyboard is a bad place to type, and a Wi-Fi password is the worst thing anyone could ask you to type on one. **There is no on-screen keyboard at any point.** Credentials are typed on a phone or a PC and arrive over HTTP; the device only ever displays and triggers.

Everything else in the table above is a value the dial picks from a list — which is what a rotary encoder is actually good at.

### How config actually works

There is a chicken-and-egg problem worth naming: the config page is served *by the device*, so a device not yet on your network cannot serve you anything. Config therefore has **two modes**, and the device chooses between them. Both put a QR code on the screen, because the alternative is typing an address into a phone.

**Mode A — access point. When there is no network yet.**

Entered when NVS holds no Wi-Fi credentials, **or after three consecutive failed joins.** That second trigger matters: without it, changing your router would brick the device permanently with no way back in.

1. The device starts a SoftAP — `Radial-XXXX`, named from the last four of its MAC — with a WPA2 password derived from the same MAC, and runs a DNS server that resolves every hostname to itself.
2. The screen shows a QR encoding the standard Wi-Fi payload `WIFI:T:WPA;S:Radial-XXXX;P:<derived>;;`, with the SSID and `192.168.4.1` printed underneath as the fallback (screen 09 A). The iOS and Android camera apps both recognise that payload and offer "Join network", so joining costs one scan and one tap.
3. Once joined, the captive-portal DNS makes the phone open the page by itself.
4. The page lists **the networks the device can see**, because it scanned them — so you pick yours from a list rather than typing an SSID. You type only the password, on the phone's keyboard.
5. `POST` → the device attempts the join immediately, reporting progress over the socket below → on success, written to NVS.

The AP stays WPA2 rather than open. The password you type on the portal is your real Wi-Fi password, and on an open AP it would cross the air in the clear. The cost is four extra QR modules.

**No Spotify token here.** In AP mode the device has no internet, so OAuth cannot complete. The token arrives afterwards, in Mode B.

**Mode B — on your network. Everything after that.**

Opened from Settings → Wi-Fi → Config mode, or automatically for the first 120 seconds after boot.

1. The screen shows a QR encoding `http://<ip>/`, with `radial.local` and the raw IP printed underneath (screen 09 B). The **QR carries the IP, not the hostname**, because mDNS is well supported on Windows, macOS and iOS but patchy on some Android builds; the hostname is printed for the case where you are typing it on a PC.
2. An amber ring around the edge is the config window closing — the countdown drawn where the progress ring lives everywhere else.
3. You browse there from anything on the LAN and get one page: Wi-Fi, Spotify token, brightness and the rest.
4. `tools/reauth.py --push-to` posts to this same server, which is how the twice-yearly re-authorisation happens without you opening anything.
5. It closes on the timer or the moment the page saves. The page carries live credentials and should not sit open on the LAN.

**A separate status page has no window and stays up permanently** at `http://radial.local/status`: uptime, SSID, RSSI, IP, firmware version, last Spotify API error, free heap. It carries nothing secret, so it needs no timer — and it is what you read when the device is misbehaving and a 1.8″ screen is not enough.

### The live status channel

**The device reads posted form fields. It never watches you type.** The browser holds the input; the ESP32 receives an HTTP POST with the values in it and writes them to NVS. Mirroring keystrokes back to the screen is technically available — `esp_http_server` supports WebSockets and the page could push each character — and is deliberately **not** done. The only things ever typed are a Wi-Fi password and a Spotify token, and echoing either onto a desk-facing screen is shoulder-surfing by design.

The same channel carries **status** instead, which is the thing worth knowing. On save, the page opens a WebSocket to `ws://<ip>/ws` and holds it. The device emits one small JSON frame per state change, and both the phone and the device screen render the same five steps:

| # | Step | Emitted when |
|---|---|---|
| 1 | Settings received | POST parsed, fields validated |
| 2 | Network found | Target SSID present in the scan result |
| 3 | Joining | `esp_wifi_connect()` called |
| 4 | Got an address | `IP_EVENT_STA_GOT_IP` |
| 5 | Reaching Spotify | First `GET /me/player` returns 200 or 204 |

Frames are `{"step":3,"state":"ok"}` or `{"step":3,"state":"fail","why":"bad_password"}`. Failures are named rather than generic, because a wrong Wi-Fi password is the single most likely setup failure and it otherwise presents as a device that reboots and forgets you:

| `why` | Source | Screen |
|---|---|---|
| `bad_password` | `WIFI_REASON_4WAY_HANDSHAKE_TIMEOUT` | Amber, "Wrong password" |
| `not_found` | SSID absent from scan | Amber, "Network not found" |
| `no_ip` | DHCP timeout | Amber, "No address" |
| `no_route` | Spotify request failed at TCP/DNS | Amber, "No internet" |
| `token_bad` | `401` from Spotify | Amber, "Spotify rejected the token" |

An amber failure is retryable: the ring stops where it stopped, the AP stays up, and the phone keeps the form filled in so you retype one field rather than starting over. It does **not** reset the failed-join counter — three real failures still drop the device into Mode A.

On success the ring completes, one DRV2605 click fires — the only haptic in the whole flow — and the screen holds a tick for two seconds before going to now playing. The socket closes and the config window shuts immediately, not on the timer. Screens 12 A, 12 B and 12 C in `design/screens.html`; the three phone pages are in the same file, under "The page the code opens".

### The page the QR opens

Three views, one page, no framework — hand-written HTML and CSS served from a single `const char[]` in flash. It is styled to match the device (near-black ground, Michroma headings, green accent) so it reads as part of the same object rather than a router admin panel. Drawn at phone width in `design/screens.html` under "The page the code opens".

| View | Must show | Non-obvious requirement |
|---|---|---|
| P1 — pick a network | The networks **the device scanned**, with signal strength and a lock glyph | Not the phone's list. If a network is missing here the device cannot reach it, which answers half of all setup problems before you have one. 5 GHz entries are listed but marked — the S3 radio is 2.4 GHz only |
| P2 — password | The chosen SSID, one password field, a Show toggle, Connect | One field and nothing else. Show reveals it on the phone in your hand and nowhere else |
| P3 — connecting | The five steps from the table above, ticking live over the WebSocket | On failure the form stays filled so one field is retyped, not the whole thing. The copy says the phone can be put down, because the dial confirms independently |

Total page weight should stay under about 8 KB so it serves from flash without a filesystem. No web fonts — the device may have no internet at this point, and a page that waits on Google Fonts is a page that appears broken. System font stack only.

**Rendering the QR.** LVGL 9 ships a QR widget backed by an embedded encoder — enable `CONFIG_LV_USE_QRCODE=y` and call `lv_qrcode_create()`. No extra component, no extra dependency. Draw it dark-on-light, never inverted: the spec assumes dark modules on a light field and several decoders (iOS included) are unreliable the other way round. At 198 px of panel on a 360 px screen the Mode A code (version 3, 29 modules) works out at ~5.9 px per module, or about 21 mm physically — comfortable but worth confirming on real hardware in Wave 3.

### First-run sequence, end to end

1. Power on. No credentials → AP mode, screen 09 A.
2. Scan the QR with the phone camera → join `Radial-XXXX` → captive portal opens by itself.
3. Pick your network from the list, type the password, press Connect.
4. Watch the five steps on either screen. Device joins your Wi-Fi. Clock is right, Spotify is not connected yet.
5. On the PC: `python tools/spotify_auth.py --client-id <id>` → browser → approve → the script pushes the token to `radial.local`.
6. Device confirms. Working.

Steps 1–4 need a phone. Step 5 needs the PC. Nothing needs a keyboard on the device, and no address is typed anywhere.

**Bluetooth appears in Settings only as far as it does something.** The S3's BLE is used for exactly one thing — the HID keyboard the Wispr app needs — so Settings shows the pairing state and offers to forget it. There is no on/off toggle, because a radio you can switch off is a dictation trigger that mysteriously stops working. The Classic Bluetooth on the second MCU stays unused.

### Wispr Flow (app 3)

**What it is.** Radial presents itself to the PC as a Bluetooth keyboard and sends one shortcut. It does not talk to Wispr Flow, know whether Wispr is running, or require anything installed on the PC. Any application that can be driven by a hotkey can be driven this way; Wispr is simply the first one worth the trouble.

**Do not emulate the default.** Wispr's stock Windows push-to-talk is `Ctrl + Win`, and double-tapping it promotes the session to hands-free. Reproducing that over HID means a modifier-only report plus a timing-sensitive double-tap, which is fragile in both halves. It is unnecessary: Wispr supports **up to four shortcuts per action**, and push-to-talk and hands-free are **separate bindable actions**. So bind hands-free to an additional combination that only Radial ever sends, and leave the keyboard defaults untouched.

| | |
|---|---|
| Bind in | Flow Hub → Settings → General → Shortcuts → Change |
| Action | Hands-free (not push-to-talk) |
| Suggested combo | `Ctrl + Alt + F9` — one clean HID report, no timing, and nothing in Windows or Spotify claims it |
| Constraint | Windows hotkeys are 3 keys or fewer and need at least one modifier |
| Avoid | F13–F24. No physical keyboard has them so collisions are impossible, which is the appeal — but Wispr's docs do not confirm support and Windows key-name handling for them is inconsistent. Verify before relying on it |

**Why not hold-to-talk.** Push-to-talk would give deterministic state — hold the chord, dictation is on; release it, off — and HID can hold a chord indefinitely. It is still wrong. Holding `Ctrl` and `Alt` down for three minutes means every mouse click is a ctrl-click and every scroll is a zoom. A held modifier poisons the whole machine. Radial only ever sends discrete presses.

**The consequence: it is a toggle, so state must be inferred.** There is one hands-free action, not an on and an off. Radial therefore tracks what it *believes* the state to be, and that belief can drift — if you use the keyboard shortcut yourself, if Wispr times out, or if Wispr simply ignores the chord, **which it observably does sometimes when certain windows have focus** (seen with VS Code focused, 2026-08-31, from a physical keyboard as well as from the device path — Wispr's quirk, not the transport's). Three things make that acceptable:

1. **The dial is idempotent.** Right means "I want it on", left means "I want it off". If Radial already believes it is on, spinning right again does nothing rather than turning it off. This is the whole point of using direction rather than a plain toggle.
2. **Two spins the same way inside 2 s force the toggle regardless of belief.** That is the resync gesture, and it is the only recovery needed.
3. **Wispr's own Flow Bar is the source of truth and is already on your screen.** A desync is visible before it is confusing.

**Input mapping, inside the Wispr app screen.**

| Gesture | Believed off | Believed on |
|---|---|---|
| Tap | Send combo → on | Send combo → off |
| Spin right ≥ 3 detents | Send combo → on | Nothing |
| Spin left ≥ 3 detents | Nothing | Send combo → off |
| Same direction again within 2 s | Send combo regardless | Send combo regardless |
| Waggle | Leave, nothing sent | Send combo → off, then leave |

Three detents, not one, because this must never fire from a knock. Tap is the fast path when you are already looking at the screen; the spins carry direction for muscle memory; the waggle is only ever the exit. There is no dwell timer and no confirmation — the Flow Bar is the confirmation.

**Transport: BLE HID, not USB HID.** The S3's USB HID and its USB-Serial-JTAG flashing port are the same peripheral on the same pins and cannot both be active. **This board has no BOOT and no RESET button**, and GPIO0 is wired to `I2S_SWITCH_IN` rather than to a button, so if firmware claims the USB peripheral there may be no way back into download mode. That is a brick, not an inconvenience. BLE HID never touches USB and costs nothing that matters here.

**What BLE costs.** Wi-Fi and BLE share one radio on the S3 and coexist by time-slicing, so album art downloads will be measurably slower while BLE is connected. Espressif's own coexistence table marks Wi-Fi STA plus connected BLE as supported and stable on the S3, so this is a throughput question rather than a stability one. Measure it in Wave 10 before deciding whether BLE stays up permanently or only while the Wispr app is in the foreground — the second option trades a reconnect delay on entry for full Wi-Fi throughput the rest of the time. Decide with numbers, not in advance.

**One more thing the keyboard unlocks.** A hotkey can do anything the PC binds to one, so the same transport answers a question the Spotify Web API cannot: launching or focusing the desktop app. `Win`+`N` activates the Nth pinned taskbar item — launch if closed, focus if open. That makes the CONTROLS device pill able to *summon* the desktop player rather than only transfer to one that happens to be running. Two caveats keep it optional and off by default: it breaks silently if the taskbar order changes, and it is a blind action with no confirmation, since the device cannot see the PC's screen. The pin position lives in Settings.

**Chords, not typed strings.** A HID keyboard can send any keystroke, so `Win`+`R` then `spotify` then `Enter` genuinely works — but it is open-loop and has three failure modes a single chord does not:

| Failure | Why |
|---|---|
| Focus | The device cannot see the screen. It types into whatever has focus — a dialog that stole it, a chat window, a locked screen. `Win`+`R` is a system shortcut and is safe; the text after it goes wherever the Run box actually is |
| Timing | The Run box takes a variable few hundred ms to appear under load. Type too early and the first characters are lost, so any typed string needs padded delays and becomes probabilistic |
| Layout | HID sends **scancodes**, not characters; the PC maps them through the active keyboard layout. On a UK layout `@` and `"` are swapped relative to US, and `#`, `\` and `~` all move. Letters are safe, punctuation is not — which means paths, URLs and shell commands are exactly the fragile case |

**So push the fragile part onto the PC.** Bind the action to a hotkey there and have Radial send only that chord. A Windows shortcut `.lnk` has a **Shortcut key** property giving `Ctrl`+`Alt`+*key* with nothing installed; AutoHotkey covers anything more involved. The wireless half stays one atomic report with no timing and no layout dependency, and the arbitrary half runs where it is deterministic and you can debug it. This is the recommended pattern for every action beyond the Wispr toggle and the taskbar pin.

**The line this must not cross.** Radial will have two capabilities at once: an HTTP server reachable by anything on the LAN, and the ability to type arbitrary commands into the PC. **They must never be connected.** No endpoint — not on the config page, not on the status page, not "just for debugging" — may accept a string and send it as keystrokes. That endpoint is remote code execution on the PC for anyone on the network, and it is an easy thing to build by accident, because "let me POST a macro to the device" is the obvious next idea. The HID layer takes an enum of fixed, compile-time actions and nothing else. Configurable values (which taskbar pin, which Wispr chord) are indices and key codes chosen from a fixed set, never free text.

**Security, stated plainly.** A paired BLE HID keyboard can type anything into the PC it is paired with, so this firmware becomes a keystroke injector sitting on the desk. For a device on your own desk running your own firmware that is a fair trade, but it is a real change in what the device is, and it is the reason the HID descriptor should expose a keyboard and nothing else — no consumer-control page, no mouse.

**What this does to the parked volume spike.** `docs/BUILD-RECOMMENDATIONS.md` §4 proposed BLE HID consumer-control as a way to change the *phone's* system volume, sidestepping `VOLUME_CONTROL_DISALLOW`. It was parked partly because it meant standing up a whole BLE transport for one feature. That argument is now gone — the transport exists either way, and the marginal cost is a second HID report descriptor. The other objection still stands unchanged: BLE HID sends relative volume steps and cannot read the phone's level back, so the settled UI's absolute percentage would have no source. Cheaper does not make it right, and it stays parked.

**A note on the apps after this one.** The Granola record button still needs something running on the PC to receive it, and adding a companion process is a different architecture rather than a new app. That remains out of scope. Wispr Flow is in scope precisely because it needs nothing.

### Polling and rate limiting

Spotify's published rate limit is a rolling 30-second window with no documented numeric ceiling; a 429 carries a `Retry-After` header. In development mode the quota is now counted per developer account rather than per app. The plan stays well clear:

| Situation | Poll interval |
|---|---|
| Playing | 3 s |
| Paused or 204 | 10 s |
| After any control command | one poll at +400 ms, then resume normal cadence |
| After a 429 | honour `Retry-After`, then double the interval for 60 s |

That is roughly 20 requests per minute at worst — about 10 per rate-limit window.

**Progress is interpolated locally.** Between polls, advance the progress bar from `progress_ms + (now - last_update_tick)`. Never poll faster to make the bar smooth.

**Optimistic UI.** Every control action updates the screen immediately and is reconciled by the next poll. Waiting 300 ms for a cloud round trip before the play icon changes is exactly the sluggishness this device exists to remove.

### Token handling

Three NVS keys: `client_id`, `refresh_token`, and `auth_date` — the date the refresh token was minted.

- On boot: refresh immediately. Then refresh at T+55 min, and on any 401.
- The refresh response **may or may not** include a new `refresh_token`. If it does, write it to NVS before using it; if it does not, keep the existing one. Getting this wrong is how the device dies silently three weeks later.

**The 180-day expiry is a hard deadline, and it is predictable.** Authorisation was 2026-08-31, so this device stops working on or about **2027-02-27**. Put that in a calendar now; Wave 9 turns it into a convenience rather than a dependency. Spotify enforces a 6-month refresh token lifetime measured from the moment of the user's original authorization. Refreshing the access token does **not** reset or extend it. So the death date is simply `auth_date + 180 days`, which is why `auth_date` is stored — the device can warn before it happens rather than just stopping.

Two failure modes, handled differently:

| Response | Meaning | What the device does |
|---|---|---|
| Network error, timeout, 5xx | Wi-Fi or Spotify is having a moment | Retry with backoff. Keep showing the last known state. |
| `400` with `{"error": "invalid_grant"}` | The refresh token is dead. Permanent. | **Stop retrying.** Discard the token and switch to the re-auth screen. |

Retrying an `invalid_grant` is pointless — it will never succeed — and Spotify explicitly asks developers not to.

### Album art pipeline

**Use the 300×300 image, not the 640×640.** The screen is 360 px across and a text band covers the lower third of it. The larger file costs roughly three times the download, and more than that in decode time — `tjpgd` must Huffman-decode every block of the source regardless of the scale factor, so a 640² source is around 4.5× the work of a 300² one even when you throw half of it away. None of that buys a pixel anyone can see.

1. Pick the image by size, not by array position. Choose the smallest entry whose width is ≥ 300, falling back to the largest available. The array is ordered largest-first and is usually 640/300/64, but that is convention rather than contract.
2. Compare the chosen URL against the cached one. Same URL → do nothing. **This is the single most important optimisation** — most polls change nothing at all.
3. Stream the JPEG from `i.scdn.co` over HTTPS into a PSRAM buffer. Typically 15–25 KB at this size.
4. Decode with `esp_jpeg` at 1:1 → 300×300 RGB565, 180 KB in PSRAM. The S3 has no hardware JPEG unit, so this is CPU work — budget 80–150 ms, which is why it lives on its own task and not the UI thread.
5. Let LVGL scale the image to fill the 360 px circle at draw time. A 1.2× upscale of a 300 px source is imperceptible at desk distance, and it happens once per track change rather than per frame.
6. Swap into the LVGL image descriptor, keeping the previous buffer alive until the swap completes. Cross-fade over ~200 ms.
7. Optional, Wave 6: cache the last few covers keyed by URL in PSRAM for instant redraw when skipping back.

Pre-allocate the decode buffer once at a fixed 300×300×2 and reuse it. Allocating and freeing 180 KB on every track change is how PSRAM fragments and the device dies after six hours.

---

## 7. Spotify app setup

1. Spotify developer dashboard → **Create app**.
2. Redirect URI: `http://127.0.0.1:8888/callback` (Spotify permits plain HTTP only on loopback — this is why authorisation happens on the PC and not on the device).
3. Scopes: `user-read-playback-state`, `user-modify-playback-state`. Nothing more.
4. Leave the app in **development mode**. It permits **5 authenticated users** and needs no review — ample for one device. (Corrected 2026-08-31: this was 25 before February 2026. Extended quota is not an option at any scale that matters here — it requires a registered business, a launched service and a minimum of 250,000 monthly active users.)
5. Run `tools/spotify_auth.py --client-id <your id>`. It performs the PKCE flow, prints the refresh token, and then runs the pre-flight diagnostic.

PKCE rather than the client-secret flow, deliberately: the device never holds a secret, so a stolen board is not a stolen credential.

---

## 8. Build plan

Each wave has a done condition you can check rather than judge.

### Wave 0 — Prove the Spotify side — **COMPLETE (2026-08-31)**

Result recorded in section 1 under Verified constraints. Volume works on the desktop, not on the phone; both variants of the second dial mode are in scope.

### Wave 1 — Toolchain — **COMPLETE (2026-08-31)**

ESP-IDF v5.5.5 installed. Schematic read and section 3's pin map verified against it. `firmware/knob/` builds clean with the full dependency set — see section 4 for the known-good versions.

### Wave 2 — Board bring-up

- Flash `hello_world`, confirm the chip and PSRAM from the boot log.
- Bring up ST77916 over QSPI, CST816 over I2C, and the encoder via `espressif/knob`, all through `esp_lvgl_port`.
- Test UI: a number that increments on clockwise rotation and decrements anticlockwise, and a button that changes colour on touch.
- **Done when:** all four inputs are demonstrably correct and the pin map in section 3 has been confirmed or corrected in this document.

### Wave 3 — Network and auth

- Wi-Fi STA, mbedTLS cert bundle, NVS-stored credentials, token refresh, one `GET /me/player`.
- **Done when:** the serial log prints the current track name and volume, and continues to print it correctly after the access token has expired and been refreshed once (verify by forcing a refresh, not by waiting an hour).
- **Also in this wave:** render one `lv_qrcode` on the panel and scan it with a phone. It is five lines and it de-risks the whole of Wave 9 — if 198 px is not enough for a version-3 code, that is a layout problem worth finding now rather than at the end.

### Wave 4 — App shell, and Spotify inside it

- The `knob_app_t` contract from section 6, a shell that owns Wi-Fi and the token, and **Spotify written as an app from the first line** — even though it is the only one.
- Poll loop, `player_state_t`, title/artist/progress/volume rendered. No art yet, no selector yet.
- **Done when:** changing tracks on the phone updates the screen within one poll interval, the progress bar advances smoothly between polls, and no Spotify state lives in the shell.

The shell arrives here rather than later because the alternative is writing Spotify against the screen directly and then unpicking it. There is no selector at this point and no second app — just the seam, put in while it costs nothing.

### Wave 5 — Album art

- Download, decode at 1/2 scale, render, cross-fade, cache by URL.
- **Done when:** art appears within ~1.5 s of a track change, heap and PSRAM are stable across 50 consecutive track changes, and repeated polls of an unchanged track trigger zero downloads.

### Wave 6 — Controls

- Play/pause, dial-to-skip with burst collapsing and lockout, second dial mode with debounced writes, haptics, runtime selection between volume and seek from `supports_volume`.
- **Done when:** every control in section 5 works against the phone, a fast five-detent spin produces exactly one skip, a 10-second dial sweep produces at most a handful of API calls (count them in the log), and moving playback to a device that supports volume switches the second mode from seek to volume within one poll.

### Wave 7 — Clock, Settings, and the selector

- The Clock app: the moiré bloom and the time, written against `knob_app_t` without touching the shell.
- The Settings app: the table in section 6. Brightness first — it is the one that changes daily use.
- The radial selector from section 5: long-press to open, dial to rotate, tap to enter, returns to where you came from.
- **Done when:** switching between all three apps built so far ten times leaves heap and PSRAM where they started, Spotify stops polling while another app is up and resumes on return, brightness and sleep timeout survive a power cycle, and neither Clock nor Settings required a single change to shell code.

That last condition is the real test. If the Clock forced a shell change, the contract is wrong and a third app will force another.

### Wave 8 — Live-on-the-desk robustness

- Wi-Fi reconnect with backoff, 401/429/204/5xx handling, backlight dim after inactivity, task watchdog, panic reboot.
- **Done when:** the device survives a router reboot, a 12-hour idle period, and a forced 429 without needing a power cycle.

### Wave 9 — Serviceability

Every 180 days the refresh token dies. That is Spotify policy, applies to every app, and cannot be engineered away. What *can* be engineered away is you having to notice.

**The target experience:** on roughly day 170, a browser tab opens on your PC by itself showing the Spotify login page. You click Agree. The knob reboots working. You are never told a token expired, and you never see one.

The expiry date is deterministic — 180 days from authorisation, and refreshing does not extend it — so this does not need monitoring, polling, or a background service. It needs a calendar entry.

**Why the PC is in the loop.** Spotify permits plain-HTTP redirect URIs only on `127.0.0.1`, so the knob cannot receive the OAuth callback itself, and Spotify offers no device authorisation grant (the "enter this code at spotify.com/pair" pattern TVs use). The browser and the loopback listener must live on a real computer. Since the knob is a desk extension of that computer, this is not a compromise.

Four parts:

**0. Wi-Fi provisioning.** The AP-mode flow described in section 6 — SoftAP, captive portal, QR to join, network list, password typed on a phone, and the WebSocket status channel driving screens 12 A–C. Needed before anything else in this wave works, and it is also the recovery path when a router changes. Build it in this order: static page → POST handler → NVS write → WebSocket → QR. Each step is testable on its own, and the QR is last because it is the only part that needs the panel.

**1. Initiation — a Windows scheduled task.** `tools/reauth.py --install-schedule` runs `schtasks` once to create a task that fires 170 days out, with "run as soon as possible after a missed start" enabled so a week of the PC being off does not break it. Each successful run re-arms the task for another 170 days, so it maintains itself and there is nothing to remember.

This is the whole initiation mechanism. No tray app, no service, no daemon, nothing running in the background.

**2. `tools/reauth.py --push-to`.** An extension of the Wave 0 script. When the task fires, it:

1. Starts the loopback listener on `127.0.0.1:8888`
2. Opens the browser on Spotify's login page — the same screen as Wave 0
3. Receives the code, completes the PKCE exchange
4. `POST`s the new refresh token to `http://radial.local/api/token`
5. Re-arms the scheduled task and exits

The device is found by mDNS, which Windows resolves natively; `--device <ip>` overrides it. If the knob is unreachable it writes the token to `spotify_tokens.json` and retries on next boot rather than losing it.

**3. A config endpoint on the device.** `esp_http_server` with two routes: `POST /api/token` (writes `refresh_token`, stamps `auth_date`, reboots) and `GET /` carrying Wi-Fi fields and OTA upload for the rarer jobs. HTML as a C string constant; reference implementation at https://randomnerdtutorials.com/esp-idf-esp32-web-server/, roughly 150 lines including Wi-Fi setup.

Gate both routes on physical presence. With no knob press available, the gate is a **boot window: the server responds only for the first 120 seconds after power-up**, and is closed for the rest of the session. The physical presence check is the power cable, which is proportionate for a desk device and needs no UI. `POST /api/token` keeps that same window so the unattended retry path works.

*(A long-press on the CONTROLS device pill would be the better product and can replace this later. The boot window is chosen because it needs no change to a settled UI.)*

**4. A fallback screen.** If the schedule never ran — new PC, task deleted, six months of bad luck — the device must still be recoverable by someone who remembers nothing. On `invalid_grant` the display switches to:

```
      Spotify login expired

   Run  reauth.bat  on your PC

        radial.local
```

This screen is the recovery documentation. It should never be seen, and it must work when it is.

- **Done when:** the scheduled task exists and re-arms itself, a forced run re-authorises the device end to end with one click in the browser, and unplugging the knob mid-flow does not lose the new token.

### Wave 10 — Wispr Flow

- NimBLE HID keyboard descriptor, keyboard only. Pair with the PC once; bond stored in NVS so it reconnects on boot.
- Wispr app implementing `knob_app_t`, with the direction mapping and the 2-second resync rule from section 6.
- Optional and off by default: `Win`+`N` on the CONTROLS device pill, with the pin position set in Settings.
- **Measure Wi-Fi throughput with BLE connected and with it disconnected**, and decide from that whether BLE stays up permanently.
- The waggle detector from section 5, sitting upstream of the volume debouncer, plus the waggle's enter/dismiss navigation.
- **Done when:** spinning right starts dictation and spinning right again does not stop it; spinning left stops it; a waggle from NOW PLAYING lands in the Wispr app with dictation on and a second waggle returns to NOW PLAYING with it off; two spins the same way inside 2 s resync a deliberately desynced device; and the album art fetch time with BLE connected is recorded in this document; a waggle in the middle of a volume sweep toggles dictation **and sends no volume change to Spotify**; and 200 deliberate volume corrections produce zero false waggles.

### Wave 11 — Launcher

- Mode 1: the list, the config-page editor for it, and the fixed chord enum.
- Mode 2: Task View driving, including the 5 s idle `Esc`. Build this second — it is smaller, and it is worthless if mode 1 is not already proving the HID path.
- **Done when:** every configured entry launches or focuses its application from cold; the list survives a power cycle; Task View mode returns the dial to Spotify after 5 s of no input with Task View closed on the PC; and a chord sent while the PC is locked changes nothing on the PC and does not wedge the device.

---

## 9. Open risks

| Risk | Impact | Handling |
|---|---|---|
| Volume refused by the phone (**confirmed, Wave 0**) | R5 as originally written is unbuildable | Second dial mode is chosen at runtime: seek on the phone, volume on devices that allow it |
| ~~Pin map wrong~~ | — | **Closed 2026-08-31** — verified against the schematic; see section 3 |
| ~~Component versions clash~~ | — | **Closed 2026-08-31** — full set builds clean on IDF 5.5.5 |
| ~~Post-February-2026 Client ID may not reach every endpoint~~ | — | **Closed 2026-08-31** — all seven pre-flighted, none restricted; see section 1 |
| Rate limit hit despite the budget | Screen goes stale intermittently | `Retry-After` handling plus interval doubling, Wave 8 |
| Refresh token expiry at 6 months | Device dies silently | Wave 9 web config; calendar reminder as the interim |
| Accidental skips from knocking the knob | Daily irritation | Burst collapsing + lockout in Wave 6; quarter-turn commit as fallback |
| PSRAM fragmentation from repeated art buffers | Crash after hours | Fixed-size pre-allocated art buffers, verified in Wave 5 |
| QR unreadable at 21 mm | The scan-to-join path fails and setup falls back to typing | Verify on real hardware in Wave 3; the SSID and IP are printed under every code so there is always a manual route |
| Launcher chords go stale when the taskbar is reordered | Wrong app launches, silently | `Win`+`N` is inherently positional. Prefer `Ctrl`+`Alt` shortcut keys on `.lnk` files for anything you care about — those follow the file, not the position |
| A chord fires while the PC is locked or asleep | Nothing happens, and the device cannot say why | Accepted, not solved. The launcher is open-loop by design, which is why the confirmation says "Launching" and never "Launched" |
| A config-page endpoint that forwards text to the HID layer | Remote code execution on the PC from anywhere on the LAN | Architectural rule in section 6: the HID layer accepts a fixed action enum, never a string. Check for this in review, not at runtime |
| Encoder emits phantom counts on fast reversal | Volume drifts on every correction, and the waggle's net-zero safety argument fails | Measured at Wave 2 checkpoint D4, before anything depends on it |
| Waggle fires during a genuine volume correction | Dictation starts while you are turning the music down | Threshold is the gap between reversals, not their count; tuned on hardware against 200 real corrections in Wave 10 |
| BLE HID reconnect after PC sleep | Dictation trigger dead until replug | Windows is unreliable here. If it proves bad, Classic BT HID on the second MCU (UART, GPIO48/38) is the fallback — more work, better reconnect |
| BLE and Wi-Fi contending for one radio | Album art visibly slower | Measured in Wave 10; BLE can be scoped to the Wispr app if the numbers are bad |
| Radial's believed dictation state drifts from reality | Spinning right does nothing | Two spins the same way inside 2 s force the toggle; the Flow Bar is the visible truth |
| Wispr ignores its hands-free chord while certain apps have focus (**observed with VS Code, 2026-08-31**) | Belief flips, reality does not — the trigger looks dead | Wispr-side quirk, not the transport: it reproduces from a physical keyboard. Resync spin recovers; if it proves frequent, revisit whether hotkey-driven hands-free is reliable enough at all |
| Phone abandons the SoftAP mid-setup | Setup appears to hang; both iOS and Android drop a Wi-Fi network with no internet | Captive-portal responses on the well-known probe URLs (`/generate_204`, `/hotspot-detect.html`) keep the phone attached; Wave 9 |

---

## 10. Current wave — step by step

> This section always describes **only the wave being worked on right now**. When the wave is done, it is deleted and replaced with the next one. Nothing accumulates here.

### Wave 2 — Board bring-up

**Goal:** every piece of hardware this project touches — screen, touch, dial — proven working under LVGL.

**This wave needs the board.** It is written to be worked through in order the day it arrives.

**Dependency check — PASSED 2026-08-31.** `firmware/knob/` builds clean against ESP-IDF v5.5.5: all ten dependencies resolved, everything compiled and linked, `knob.bin` at 214 KB with 95% of the app partition free. The only failure it produced was a missing `espressif/button`, now fixed and explained in section 4.

Everything from Checkpoint A onwards needs the board. Nothing else can be done before it arrives.

**Approach:** four checkpoints, each verified before starting the next. Bringing up a QSPI display, an I2C touch controller and an encoder simultaneously and then asking "why is the screen black" is the slow way to do this.

Run every command from the **ESP-IDF 5.5 PowerShell** shortcut.

---

#### Checkpoint A — Reach the right chip

**A1.** Plug the board in with a USB-C cable you know carries data.

**A2.** Open Device Manager (Win+X, then M). Look under **Ports (COM & LPT)** and **Universal Serial Bus devices**:

| What you see | Meaning | Action |
|---|---|---|
| `USB JTAG/serial debug unit` | You have the ESP32-S3. Correct. | Note the COM port, continue |
| A CH340 or CP210x COM port | Probably the *second* microcontroller | **Unplug, flip the USB-C connector over, plug back in** |
| Nothing | Charge-only cable, or no driver | Try a different cable first |

This board has two microcontrollers sharing one USB-C socket and the orientation decides which one you reach. If anything below fails to connect, flip the cable before debugging anything else.

**A3.** Build and flash the stock example:

```powershell
cd D:\Projects\PROD\spotify-knob\firmware
Copy-Item -Recurse "$env:IDF_PATH\examples\get-started\hello_world" .
cd hello_world
idf.py set-target esp32s3
idf.py menuconfig
```

In menuconfig: **Component config** → **ESP PSRAM** → enable **Support for external, SPI-connected RAM** → **SPI RAM config** → **Mode of SPI RAM chip** → **Octal Mode PSRAM**. Press `Q` then `Y`.

```powershell
idf.py -p COM7 flash monitor
```

If it hangs on `Connecting......_____`: **flip the USB-C connector.** There is no BOOT or RESET button on this board (see section 3), so there is no button sequence to fall back on — the S3's native USB handles download mode by itself when you are talking to the right chip. A hang almost always means you are talking to the other one.

**Checkpoint A done when** the boot log contains both:

```
ESP-ROM:esp32s3-...
I (xxx) esp_psram: Found 8MB PSRAM device
```

`Ctrl+]` exits the monitor. If PSRAM reports 2 MB or is missing, octal mode is not set or you are on the wrong chip.

---

#### Checkpoint B — The screen lights up

**B1.** Create the real project alongside it:

```powershell
cd D:\Projects\PROD\spotify-knob\firmware
idf.py create-project knob
cd knob
idf.py set-target esp32s3
```

**B2.** Create `main/idf_component.yml` with the dependency list from section 4 of this document. Run `idf.py reconfigure` — it downloads them into `managed_components/`, which `.gitignore` already excludes.

**B3.** Backlight first, because it is the simplest thing that proves you are talking to the board. Configure **GPIO47** as an LEDC PWM output and set it to 50%.

**Do not skip to the panel.** If the backlight does not respond, nothing else will work and you have learned it in five lines instead of two hundred.

**B4.** Now the panel. Using `esp_lcd_st77916`:

- QSPI bus on SPI2: SCLK **13**, data lines **15, 16, 17, 18**
- Panel CS **14**, reset **21**
- 360×360, RGB565
- The vendor config must set `flags.use_qspi_interface = 1` — this is the single most common reason an ST77916 stays black

Fill the screen red, then green, then blue, two seconds apart.

**Checkpoint B done when** the display cycles three solid colours cleanly, with no tearing, offset or missing edges. An offset image means the panel gap/offset values need adjusting; cross-check against Waveshare's own ESP-IDF demo for this board before inventing values.

---

#### Checkpoint C — LVGL and touch

**C1.** Add `esp_lvgl_port`. Register the panel with `lvgl_port_add_disp()`. Use partial buffers — roughly 1/10 of the screen — allocated in internal DMA-capable RAM, not PSRAM.

**C2.** Draw a centred label reading `hello`.

**C3.** Add touch: `esp_lcd_touch_cst816s` on I2C — SDA **11**, SCL **12**, interrupt **9**, reset **10**, 400 kHz. Register it with `lvgl_port_add_touch()`.

**C4.** Replace the label with an `lv_button` that changes colour when pressed.

**Checkpoint C done when** the button responds to touch anywhere on its face and the touch coordinates are not mirrored or rotated. If pressing the top of the screen activates something at the bottom, the touch driver's swap/mirror flags need to match the panel's.

---

#### Checkpoint D — The dial

**D1.** Encoder A on **8**, B on **7**. `espressif/button` is in the dependency list for compile reasons only — do not wire it to anything.

**D2.** Register with `lvgl_port_add_encoder()`, passing a knob handle and no button handle.

**D3.** Test UI: a large number in the centre. Clockwise increments, anticlockwise decrements.

**Checkpoint D done when** both directions are correct and one physical detent produces exactly one step — not two, not none. If a single detent moves the number by two, the knob component needs its counting mode adjusted.

**D4 — the reversal test.** Zero the counter, then waggle the dial fast left-right-left-right and stop. **The counter must return to zero.** Cheap encoders emit phantom counts when direction changes at speed, and if this one does, two things break at once: volume accuracy during any correction, and the waggle gesture in section 5 — whose entire safety argument is that a waggle nets to zero. Record the drift over ten waggles in this document. Anything other than zero is a finding, not a rounding error.

---

#### Checkpoint E — Haptics on the touch bus

The DRV2605 shares I²C with the touch controller. Add it to the **same** bus handle and fire one click per detent.

**Checkpoint E done when** turning the dial gives one crisp click per step and touch still works. If touch dies the moment haptics initialise, two bus handles have been created where there should be one.

---

### Done when

- [ ] Boot log shows `esp32s3` and `Found 8MB PSRAM`
- [ ] Screen cycles three solid colours with no offset
- [ ] A touch button responds correctly across the whole screen
- [ ] One detent of the dial moves the counter by exactly one, both directions
- [ ] One haptic click per detent, with touch still working
- [ ] Committed, with no `build/` or `managed_components/` in the commit

---

### Notes for the next wave

Wave 3 is Wi-Fi, TLS and the token refresh. Nothing to prepare — the credentials from Wave 0 are already in `spotify_tokens.json`.
