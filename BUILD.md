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
| R5 | The dial controls **volume**. Where the active device refuses volume — which is every phone tested — the dial does **not** quietly become something else: it opens the controls screen, which carries every action the dial cannot perform. SEEK is assigned by hand from that screen, for one adjustment, reverting to volume when the overlay clears. *(Changed 2026-09-04. The automatic seek fallback was specified here, built, used on the desk, and removed: turning the dial for volume and watching the track scrub instead is not a graceful degradation, it is the device doing something you did not ask for. Ryan's call.)* |
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
| Encoder | **Not quadrature** (corrected 2026-09-02, Wave 2 checkpoint D): two SSCM110100 bidirectional detector switches — one pulse line per direction of rotation. Read by the ported Waveshare driver `firmware/knob/main/bidi_knob.c`; the espressif/knob quadrature component cannot decode it. **No push switch** |
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

### Three gotchas that will cost you an hour each if you do not know them

1. **The USB-C cable orientation selects which MCU you flash.** Flip the connector if the board enumerates as the wrong chip. This is a documented board behaviour, not a fault.
2. **There is no BOOT button and no RESET button either.** Sheet 1 shows only SW1 and SW2, and both are SSCM110100 rotary encoders. `CHIP_PU` and `GPIO0` carry 10K pull-ups and nothing else — there is no switch anywhere on the board able to pull either low. Download mode therefore depends entirely on the S3's native USB-Serial-JTAG auto-reset, which normally handles it without intervention. **There is no manual recovery to fall back on**, so if a flash fails, the first move is the cable orientation, not a button.
3. **A USB-C hub swallows the board entirely** (hit 2026-09-02). Through a monitor/dock/front-panel hub, Device Manager shows only a "Billboard Device" — the hub's own controller announcing a failed data connection (seen: Aorus monitor, Realtek `VID_0BDA&PID_5418`) — and nothing of the board in either orientation. Plug directly into a rear USB-A port with an A-to-C cable.

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
CONFIG_MBEDTLS_DYNAMIC_BUFFER=n          # deliberately OFF — see below
CONFIG_ESP_MAIN_TASK_STACK_SIZE=8192
CONFIG_ESP_SYSTEM_EVENT_TASK_STACK_SIZE=4096   # 2304 overflowed once Wi-Fi handlers ran
CONFIG_FREERTOS_HZ=1000
CONFIG_LV_COLOR_DEPTH_16=y
CONFIG_LV_USE_QRCODE=y                   # config-mode QR, Wave 9
CONFIG_ESP_TASK_WDT_PANIC=y              # a wedge reboots instead of printing forever
CONFIG_ESP_TASK_WDT_TIMEOUT_S=10
CONFIG_ESP_SYSTEM_PANIC_PRINT_REBOOT=y
CONFIG_ESP_SYSTEM_PANIC_REBOOT_DELAY_SECONDS=1 # so the backtrace reaches the monitor
CONFIG_BT_ENABLED=y                      # Wave 10 only
CONFIG_BT_NIMBLE_ENABLED=y               # NimBLE, not Bluedroid — roughly half the footprint
```

**`CONFIG_MBEDTLS_DYNAMIC_BUFFER` is off on purpose and the comment above used to say the opposite.** It exists to save RAM by allocating TLS buffers only while they are in use, and against this workload — one long-lived connection, a request every few seconds — the buffers were not coming back. Fixed buffers cost more at rest and cost the *same* at rest forever, which is the trade a device holding one connection for days should take. The reasoning is written into `sdkconfig.defaults` as well. Do not re-enable it to save memory without measuring free heap over ten minutes.

**`sdkconfig` is gitignored and is not regenerated from `sdkconfig.defaults` once it exists.** A setting added only to the defaults file will not reach a build on a machine that already has an `sdkconfig`. Change both.

### Working with the board

**Compile check**, which Claude runs before handing over any flash, from any PowerShell. Both environment variables are required — without them `export.ps1` looks for a `py3.14` virtual environment under `~\.espressif` that does not exist:

```powershell
$env:IDF_TOOLS_PATH='C:\Espressif'
$env:IDF_PYTHON_ENV_PATH='C:\Espressif\python_env\idf5.5_py3.11_env'
& 'C:\Espressif\frameworks\esp-idf-v5.5.5\export.ps1' | Out-Null
cd D:\Projects\PROD\spotify-knob\firmware\knob; idf.py build
```

**The flash loop**, from the ESP-IDF 5.5 PowerShell shortcut. The `cd` is not optional: the shortcut opens in the IDF install directory and `idf.py` builds whichever directory it is standing in, so without it cmake refuses with "Current directory is not buildable".

```powershell
cd D:\Projects\PROD\spotify-knob\firmware\knob
idf.py -p COM7 flash monitor
```

`Ctrl+]` first if a monitor is already running. Board on COM7, direct into a rear USB-A port, never the monitor's hub. If it will not connect, flip the USB-C plug at the board end before debugging anything else.

**The `Compile time` line in the boot log does not tell you which build is running.** It read the same value across several different flashes on 2026-09-03 while the ELF SHA256 changed each time. To know whether a build landed, add a log line and look for it.

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

**A tap dismisses it immediately** rather than waiting out the two seconds — you have finished with it, and that is what the tap means. Added 2026-09-04.

### THE MENU — long-press from any app

**Naming, settled 2026-09-04: this is "the menu".** It was written up as the app selector and is still called `selector.c` in the firmware, but in every document and every conversation from here it is the menu — the radial ring of apps a long-press opens over whatever you were doing. The whole navigation model is written out as-built in [docs/USER-JOURNEY.md](docs/USER-JOURNEY.md).

The Galaxy Watch bezel model, which is what a round screen and a rotary encoder are for.

- App glyphs sit around the rim, plus one slot that is not an app: **Back, always last**, which closes the menu and leaves you where you were. It does the same thing as the chevron and earns its place twice — a chevron at the foot of a ring is something you have to be told about, and a sixth slot puts the glyphs 126 px apart at this radius instead of 148. Five felt like they were fighting for space on glass (2026-09-04).
- Selection is a single green dot above twelve o'clock with the glyph beneath it lit and glowing; every other glyph fades with angular distance — full at twelve, barely there at six. No arc, no ticks: one mark, one meaning.
- **Eight slots is the ceiling for a rim at this radius**, Back included, which is the constraint R9 — the requirement that the device is an app shell rather than a Spotify screen — was written to expose.
- **Dial → one app per detent, with a haptic click on each.** The ring turns under the marker rather than the marker moving, and it **wraps** — a ring has no ends, so it never bumps. **Direction reversed 2026-09-04**, in the menu and in Settings alike, at Ryan's call after using it. Only the rings reversed: a value editor still goes up when you turn right, because a quantity has a direction of its own and brightness that fell when you turned it up would be nonsense.
- **Advance an animation by a fraction per call, not by elapsed time.** A timed ease interpolates against `esp_timer_get_time()`, so the position it computes depends on the *moment* the callback runs — and LVGL timers are not called on a schedule, they run when `lv_timer_handler` gets round to them. Anything else on the LVGL thread pushes that moment around, and a time-sampled interpolation turns that jitter straight into uneven spatial steps. A proportional chase (`angle += gap × 0.25`) takes an even step whenever it is called, so irregular timing costs nothing. This is the difference that made the menu feel jerky while the Settings ring felt smooth from what was otherwise near-identical code.
- **Animate at the display's refresh period, never faster.** `CONFIG_LV_DEF_REFR_PERIOD` is 33 ms, so LVGL renders every 33 ms whatever a timer does. The menu's chase ran at 16 ms, written up as "~60 fps" and never that: two moves per rendered frame, only one of them ever drawn. Settings has always run at 30 ms — one update per frame.
- **An opaque background with a radius does not count as covering anything.** LVGL's cover check treats a rounded fill as masked, so it cannot skip drawing what is underneath. The menu's ground was a full-screen circle over a live app screen, paying for both. The panel is physically round; a rounded fill buys nothing you can see.
- **Set a style only when its value changes.** Every `lv_obj_set_style_*` call invalidates the object whether or not the value moved. The menu was re-setting each glyph's colour inside its per-frame layout, which is six extra full-object invalidations a frame that Settings never paid.

**On how this one was found, because the method is the lesson.** Three explanations were offered for the judder — the item count, then the easing curve's fixed offset, then the timer period — and each was argued from the code, flashed, and was wrong or partial. What settled it was being told to stop explaining the difference and remove it: diff the two rings line by line, list every mechanical difference, and make the jerky one match the smooth one. That found the time-sampled ease immediately, because it was on the list. **When two things that should behave the same do not, diff them before theorising about either.**
- **Selection is a green dot at twelve, and a glow on the glyph beneath it.** Two signals, one meaning. An earlier draft carried a dot, twin tick marks *and* a conic arc; three marks for one selection is two too many, and the extras read as decoration rather than state.
- **Rim glyphs fade with angular distance from the dot** — full at twelve, about 12% at six. It puts the eye where the selection is, and it makes the foot of the circle recede so the back chevron is the only lit thing down there. The curve is `0.12 + 0.88 × (1 − d)^1.6`, with `d` the angular distance normalised so six o'clock is 1.
- **Tap the centre → enter the selected app. Tap a glyph in the upper two thirds → enter that app directly.** Glyphs in the lower band are *not* tappable, because the back chevron owns that area and one region cannot mean two things. Their dimming is the honest signal that they are reachable by dial only — which is why the falloff and the back zone were designed together rather than one after the other.
- **Back is visible on every screen, not just every ring.** A chevron sits at the foot, with a generous tap area around it, and every app has one — the Clock and Dictation got theirs on 2026-09-04, having previously offered nothing but a long-press you had to have been told about. A gesture nobody can see is not an exit. Spotify's lives on CONTROLS rather than on NOW PLAYING, for the reason given below.
- **Back means one level up, and the top level is the menu.** Inside an app with levels — Spotify's CONTROLS, a Settings value, the Launcher's Task View — back returns to that app's own root. At the root it opens the menu. In the menu itself it closes and leaves you where you were. Two rules, and the whole map is in [docs/USER-JOURNEY.md](docs/USER-JOURNEY.md).

All of the above applies identically to the Settings ring and the Launcher ring — and since 2026-09-04 it is literally the same code, `main/ring.c`, rather than three implementations that agreed by intention. A ring that behaves differently at a different level is a second thing to learn.

With two apps this is a toggle wearing a carousel's clothes. It is built now anyway, because the cost of adding it later is rewriting whichever app was built without it.

### The waggle — retired on hardware evidence (2026-09-02)

There was a global dictation gesture here: a rapid left-right-left reversal of the dial, safe because a waggle nets to zero detents and so never moves the volume. Wave 2's reversal test (D4) killed it: over ten fast waggles the dial drifted **+2, +1, 0, −2, 0, +1, +1, +2, +3, +4** detents — the bidirectional detector switches miscount under fast direction changes, so the net-zero argument is void, and swallowing recognised waggles still leaks drift through every waggle that fails recognition. Slow detents count exactly, so ordinary corrections are unaffected.

Dictation is therefore reached the ordinary way — selector → Wispr — and there is no global gesture. Two things outlive the waggle:

- **Send discipline.** The believed dictation state changes **only when a chord was actually dispatched**, and chords are serialised with at least 600 ms between them — one movement can never double-send, and a suppressed send never flips belief. Decided 2026-08-31 after the simulator double-sent and desynced itself; the rule holds for every chord the device ever sends.
- **The belief model.** A chord Wispr ignores (see the focus quirk in section 6) flips belief without flipping reality. The Wispr screen states what the device believes; Wispr's own Flow Bar is the truth; the resync spin recovers the difference.

### CONTROLS — one tap from the default screen

- **Transport across the middle:** previous, play/pause, next, at full thumb size. This is where skipping lives.
- **Two chips below:** VOLUME and SEEK, assigning the dial. SEEK assigns the dial for one adjustment; when the overlay clears and NOW PLAYING returns, the dial is volume again. Since 2026-09-04 this is the **only** way the dial ever seeks.
- **The back chevron lives here**, not on NOW PLAYING. NOW PLAYING is the artwork, and permanent chrome on the one screen meant to be the album is the wrong trade; CONTROLS is one tap away and is already the screen you reach for when you want the device rather than the music.
- **Device pill at the top:** shows where audio is playing. Tapping it transfers playback to the desktop via `PUT /me/player`.
- Auto-returns to NOW PLAYING after 5 s.

### Behaviours that need deciding once and then holding

- **Volume availability is read, never assumed.** `GET /me/player` returns `device.supports_volume`, re-checked on every poll. When false — which is the case on the phone — the VOLUME chip greys out and **turning the dial raises CONTROLS instead of adjusting anything**. Transferring playback to the desktop re-enables volume within one poll. The knob is never inert; it just stops pretending the turn meant something else.
- **Transfer, not launch — over the API.** `PUT /me/player` moves playback to a device Spotify can already see, which requires the desktop app to already be running. Nothing in the Web API can start or focus an application. **The BLE HID keyboard added in Wave 10 can**, and this is the answer to the launch/focus question the Web API cannot solve: `Win`+`N` activates the Nth pinned taskbar item, launching Spotify if it is closed and focusing it if it is not. One chord, no resident agent, no companion process. It is optional, it belongs to Wave 10 rather than Wave 6, and it depends on the pin position holding — so the position is a Settings value, defaulting to off. See the HID section later in this section.
- **Writes are debounced.** A single call 400 ms after the last detent is what keeps the device inside the rate limit during a long volume sweep.
- **Haptics.** One short DRV2605 click per detent, a heavier one on transport button presses. Cheap to add, and most of what makes the thing feel like a control rather than a screen.
- **End stops are felt, rings are not.** Where a value clamps — volume at 0 or 100, brightness at its floor, an enum at either end — the rejected detent produces a firm haptic and a small visual bump instead of silence. The three rings (selector, Settings, Launcher) wrap and never bump; only clamped values have ends.
- **Adverts.** `currently_playing_type == "ad"` — show "Advert", suppress the transport buttons. Not applicable on Premium, but three lines that prevent a confusing state.
- **Nothing playing.** `GET /me/player` returns HTTP 204. The screen shows the moiré ray field described in `design/screens.html`, tinted from the last cover's average colour, with the clock over it. The dial does nothing.
- **Sleep, and how it wakes.** After the configured idle period the backlight goes off entirely — a permanently-powered desk object should not be a permanently-lit one. It wakes on a touch or on a brief spin of the dial, and **the input that wakes it does nothing else**: going dark raises an invisible shield that takes the press, lights the screen, and absorbs the whole gesture through to the release, so the app underneath never learns the touch happened. The dial is simpler, because it is not an LVGL input device — the input task drops the detent after waking. Reaching for a dark knob is how you turn it on; it is not how you skip a track you cannot see. *(Built 2026-09-04. Before that, sleep was only the backlight, so a touch in the dark both lit the screen and pressed whatever was under the finger.)*

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

**The provider seam (recorded 2026-09-02, for the shared core).** `player_state_t` is written by a *provider* behind one small interface — fill the struct, plus the command set: play/pause, next, previous, seek, volume, transfer — and the screens read the struct without knowing who wrote it. On this build the only provider is the Spotify Web API poller. The halo build swaps in the companion's Windows media-session feed and renders the same screens. The enforcement rule: nothing above the seam mentions Spotify, HTTP or JSON. The simulator already proves the shape — its mock engine and live engine drive one UI through one interface.

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

**`on_pause` and `on_resume`: the menu is over you, stop animating.** Optional, added 2026-09-04. The app stays active and keeps every buffer — this is not a small `on_exit`. It means the menu covers you completely, so anything you draw is discarded, and on this device that waste is not free: the Clock's bloom is 27 ms of work per render on the LVGL thread, and 27 ms landing inside a 33 ms animation frame is a visible stutter in the ring the menu is trying to turn. Pause timers, do not delete them. Leave polling alone — it costs the LVGL thread nothing and stopping it only makes coming back slower.

**`on_exit` must actually free.** The 180 KB album-art buffer is the Spotify app's, and it is over a fifth of the internal-plus-PSRAM budget this project has any business using at once. An app that keeps its buffers alive while inactive turns "add a third app" into a memory problem. Pre-allocate on `on_enter`, release on `on_exit`, and never allocate per frame.

**Suspend the network too.** An inactive app makes no HTTP calls. Spotify's poll loop stops when you leave it, which also means the rate-limit budget is only ever spent by the app you are looking at.

**LVGL:** one `lv_obj_t` screen per app, created in `on_enter` and deleted in `on_exit`, switched with `lv_screen_load_anim()`. Lazy creation rather than one screen per app held permanently — the round display is 259 KB of framebuffer and there is no reason to pay for screens nobody is looking at.

**Token refresh stays in the shell**, not in the Spotify app. It has to keep running while you are looking at the clock, or coming back to Spotify would stall on a refresh.

### Five apps, and only five

**App 1 — Spotify.** Everything in section 5.

**App 2 — Clock.** The moiré bloom and the time, which already exist as the idle screen. Almost free, needs no network, and it is what proves the contract is real: if the Clock cannot be written against `knob_app_t` without touching shell code, the contract is wrong and a third app will break it too.

**App 3 — Wispr Flow.** One keystroke over BLE HID, specified in full later in this section. It is here rather than in a later project because it is the app that proves the shell can own a resource Spotify knows nothing about — the BLE stack — without Spotify having to care.

**App 4 — Launcher.** A short, ordered list of PC applications. The dial scrolls it, a tap sends one chord, and the device returns to Spotify. It has two modes.

**Mode 1 — the curated list.** Up to eight entries, each a label, a glyph and a **chord chosen from a fixed set**: `Win`+`1`–`9` for pinned taskbar items, or `Ctrl`+`Alt`+*key* for anything bound to a Windows shortcut `.lnk`. Entries are configured on the config page. Note the split this preserves — the **label is free text because it is only ever drawn on the screen**, and the chord is an enum. Nothing typed by a human reaches the HID layer, which is the rule from later in this section holding under pressure rather than merely being restated.

**The rim, not a list.** Same mechanic as the app selector, one level down: entries on the ring, the selected one named in the centre, a fixed marker at twelve. A vertical list wastes both corners of a circle and imposes a top and a bottom on an input that has neither.

Glyphs are chosen per entry from a fixed set on the config page. They are not the real application icons — those are bitmaps the device has nowhere to keep, and fetching them would mean knowing what is installed, which it cannot.

**Eight entries is a hard cap, and the cap is the feature.** At a 126 px radius glyphs crowd past eight, but the real reason is that fixed positions are the entire value — a ninth entry makes every position one you read rather than one you know, and at that point the PC's own Start menu is better at this than Radial will ever be.

At eight, **ADD ENTRY** greys out and the count turns amber. It does not paginate and it does not scroll. If eight is genuinely proven insufficient in use, the escape hatch is **groups** — a ring of categories, each opening a ring of apps, two taps deep. That is designed and deliberately not built: it should stay unbuilt until eight has actually failed, because adding it pre-emptively costs the flatness that makes the launcher fast.

### The launcher editor

Wi-Fi setup is a phone job — you are standing at the device. Editing the launcher is not: you are at the PC, looking at the taskbar you are about to reference, wanting a real keyboard. Same server, same config window, a layout that assumes a desktop browser. Drawn in `design/screens.html` as P4.

Five controls and no more: drag to reorder, a glyph from a fixed set, a free-text label, a chord, delete.

| Control | Why it is shaped this way |
|---|---|
| Reorder | Order is the point. A fixed position is what lets your hand learn the list, so reordering must be easy and must be the thing you do last |
| Glyph | Picked from a fixed set. **No icon upload** — real application icons are bitmaps the device has nowhere to keep, and fetching them would mean knowing what is installed |
| Label | Free text, because a label is only ever drawn on a screen |
| Chord | **A dropdown, never a text field.** `Win`+`1`–`9` and `Ctrl`+`Alt`+`A`–`Z`, nothing else |
| Delete | Immediate, no confirm. Re-adding costs four seconds |

The chord dropdown is where the rule from later in this section becomes a UI decision rather than a principle: **no string on this page can become a keystroke.** A free-text chord field would be exactly the LAN-reachable remote execution path that must not exist, and it would look completely reasonable in a code review.

**It cannot confirm anything.** The device has no idea whether the app launched, was already open, or whether the chord landed on a locked screen. So it shows "Launching Slack" for 1.5 s and returns. Anything more confident would be a claim it cannot support.

**Mode 2 — drive Task View.** For the times you want the real window list rather than a list of apps. It is entered like any launch: **Task View is the last entry on the ring**, with its own glyph.

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
| About | IP address, firmware version, uptime |

There is no Launcher row — its entries are edited on the config page (naming applications is typing) and a read-only row would only restate that. Eight items keeps the ring at 45° per slot.

Screens for all of this are drawn in `design/screens.html` — the settings ring (06), a continuous value (07), the pattern every fixed-choice setting uses (08), and both config modes (09 A and 09 B).

**Settings is a ring too, for the same reasons.** Eight items on the rim, the selected one filling the centre with its current value, name above and value below — you are choosing what to change, so the name leads. It wraps continuously, because a ring has no ends. The cost is real and worth naming: a list showed all eight values at once and the ring shows one, so auditing every setting now takes a full turn instead of a glance. That trade is accepted because you come here to change one thing, not to read eight.

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

Three detents, not one, because this must never fire from a knock. Tap is the fast path when you are already looking at the screen; the spins carry direction for muscle memory; the back chevron leaves without touching the state. There is no dwell timer and no confirmation — the Flow Bar is the confirmation.

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

### Binding a chord on the PC

Every Windows shortcut has a **Shortcut key** field: right-click the `.lnk` → Properties → **Shortcut** tab. Press a letter and Windows prefixes `Ctrl`+`Alt` automatically. That is the whole mechanism, and it needs nothing installed.

**The detail that decides whether it works at all:** the shortcut must live on the **Desktop** or in the Start Menu. A `.lnk` in `D:\shortcuts\` accepts a shortcut key in its properties dialog and then silently does nothing. The right home is:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs
```

Registered, and invisible on the desktop — which is what you want for ten of them.

| | |
|---|---|
| Behaviour | Same as clicking the shortcut: launches if closed, focuses the existing window if already running. Launch-or-focus comes free rather than needing logic |
| Prefix | `Ctrl`+`Alt` only, so about 30 usable bindings. Check for collisions — some vendor utilities claim `Ctrl`+`Alt` combinations, Intel graphics historically taking the arrow keys |
| First fire | Can lag a second or two while the shell resolves the target. Subsequent presses are instant |
| Scope | Per-user, stored in your profile |
| Escalation | AutoHotkey removes the `Ctrl`+`Alt` constraint and the startup lag, at the cost of a permanent background process. Start with `.lnk`; move only if it fails |

**This is preparable now, without the board.** Create the shortcuts, assign the keys, and test each one from your own keyboard. That is the entire PC-side configuration, verified independently. When Radial later sends one of those chords it is sending something already proven to work, so any failure is in the BLE path and nowhere else.

**The line this must not cross.** Radial will have two capabilities at once: an HTTP server reachable by anything on the LAN, and the ability to type arbitrary commands into the PC. **They must never be connected.** No endpoint — not on the config page, not on the status page, not "just for debugging" — may accept a string and send it as keystrokes. That endpoint is remote code execution on the PC for anyone on the network, and it is an easy thing to build by accident, because "let me POST a macro to the device" is the obvious next idea. The HID layer takes an enum of fixed, compile-time actions and nothing else. Configurable values (which taskbar pin, which Wispr chord) are indices and key codes chosen from a fixed set, never free text.

**Security, stated plainly.** A paired BLE HID keyboard can type anything into the PC it is paired with, so this firmware becomes a keystroke injector sitting on the desk. For a device on your own desk running your own firmware that is a fair trade, but it is a real change in what the device is, and it is the reason the HID descriptor should expose a keyboard and nothing else — no consumer-control page, no mouse.

**What this does to the parked volume spike.** `docs/BUILD-RECOMMENDATIONS.md` §4 proposed BLE HID consumer-control as a way to change the *phone's* system volume, sidestepping `VOLUME_CONTROL_DISALLOW`. It was parked partly because it meant standing up a whole BLE transport for one feature. That argument is now gone — the transport exists either way, and the marginal cost is a second HID report descriptor. The other objection still stands unchanged: BLE HID sends relative volume steps and cannot read the phone's level back, so the settled UI's absolute percentage would have no source. Cheaper does not make it right, and it stays parked.

**A note on the apps after this one.** The Granola record button still needs something running on the PC to receive it, and adding a companion process is a different architecture rather than a new app. That remains out of scope. Wispr Flow is in scope precisely because it needs nothing.

### Drawing, and what it costs

The Spotify and Clock screens each composite into one full-screen RGB565 canvas in PSRAM — 259 KB — rather than stacking LVGL objects that take turns being hidden. **Pixel writes into that canvas are the entire cost of drawing**, because every blend is a read-modify-write across the PSRAM bus. The Clock's own instrument gives the exchange rate: **6060 writes cost 26 ms**.

Three separate times a correct change was flashed without anyone counting its writes, and each one was felt immediately: an anti-aliasing rewrite that multiplied writes twentyfold, a full-screen recomposite running four times a second, and per-detent compositing on the input task. Two of the three tripped the task watchdog. **Count the per-frame work before flashing, not after it feels slow.**

The rules that came out of that:

- **Hundreds of LVGL primitives per frame is not a viable shape.** Each `lv_draw_line` is a full draw-task dispatch and blend pass — cheap for the handful of shapes a screen normally holds, ruinous three hundred times a frame. A hot inner loop writes into the canvas buffer directly and hands LVGL the finished image with one `lv_obj_invalidate`. That is an exception earned by measurement, not a rejection of the library; everything that is not a hot loop still uses LVGL's drawing.
- **Fill by scanline coverage, not by bilinear splatting.** Splatting each sample into four pixels costs roughly twenty writes where a scanline fill costs one per pixel, for the same smoothness.
- **Stop re-compositing what has not changed.** NOW PLAYING blits the cover once into a cached background that each redraw `memcpy`s from. The dial screens `memset` instead of blitting, because the design dims artwork to 6% there, which in RGB565 is one level out of 31 and already invisible.
- **The composite is throttled to 1 Hz at rest and bypassed while anything is animating.** If the screen feels unresponsive, find what is failing to mark itself as animating. Do not remove the throttle to fix it.
- **LVGL is pinned to core 0 and the album-art task to core 1.** Unpinned, both competed for core 0 while core 1 idled, and JPEG decode times varied 140–1702 ms for identical work. Any new task that does real work needs its core decided.

**RGB565 has different per-channel thresholds, and low-alpha blending has to account for it.** Red and blue have 32 levels, green has 64, so a truncating blend toward white lights green at alpha ≥ 5 but red and blue only at ≥ 9 — faint blends come out green. `main/bloom.c` dithers the sub-level remainder with a 4×4 Bayer offset to fix it. **Any new low-alpha blending into RGB565 needs the same treatment**, and the bug is invisible at high alpha, which is why it only ever showed in the unlit half of the bloom.

**The same asymmetry bit a second time, hiding underneath the first (found 2026-09-04).** `px_blend` blends toward a *channel* value — 0–31 for red and blue, 0–63 for green — and three call sites were passing `255, 255, 255` because that is what white looks like. Every channel saturates, but not at the same rate: at alpha 25, red and blue reach 24 of their 31 levels while green reaches 24 of 63. So "white" came out strongly magenta. It was visible as a purple loading spinner and as a magenta cast through the unlit field of the dial screens, and it survived the Bayer fix because the two faults are independent. **A colour crossing into a blend is only white if it is white in the space the blend works in** — `WHITE_R5/G6/B5` now exist so nobody has to remember which space that is.

**Values carried from the simulator to the panel have to be looked at on glass.** Opacity, stroke width and type size were all set against a monitor showing the panel at roughly twice life size, and all three were wrong on hardware: bloom alphas roughly doubled, spindles from 0.8–1.3 px to 1.6–3.4, and the whole type ramp up a size or two. A display-calibration difference, not a change of intent.

### Two seams that exist as code, not as intentions

**`main/ring.c` now carries the Settings ring's mechanics verbatim** — proportional chase at 30 ms, falloff by degrees against a fixed 180 — rather than the variants that had accumulated. The slot-based falloff it replaced was a real improvement on paper, since a three-item ring fades badly when measured against a fixed 180°, but nothing holds three items any more and matching the ring that is right on glass beats keeping the version that argues better. Revisit only if a ring ever gets that small again.

**The ring lives in one place: `main/ring.c`.** The mechanic - glyphs on the rim, one selected under a fixed dot at twelve, the ring turning beneath the dot - had been written twice by 2026-09-03 and the two copies had already drifted: the app selector used the corrected timed ease and slot-based falloff, and Settings still used the proportional chase the selector had abandoned. The Launcher would have made it three. Every constant in a ring silently depends on how many items it holds, so three copies means three different answers to the same question. The selector and the Launcher both use `ring.c` as of 2026-09-04. **`main/settings_app.c` has not been migrated yet** and still carries its own copy; it is a value editor as well as a ring, so it is a larger job than a move.

Two rings can be alive at once - long-pressing inside the Launcher opens the app selector over it - so `ring.c` is instance-based, and an async callback validates its ring against a small table of live instances before touching it. That guard exists because an LVGL object can be freed between a callback being queued and it running, and this project has already lost a session to one lifetime bug of that shape.

**The HID layer takes an enum and nothing else: `main/hid.h`.** The rule stated later in this section - no string typed by a human may ever become a keystroke - is enforced there by the type system rather than by everyone remembering it. `hid_send` accepts a `hid_action_t`; every action maps to a modifier and usage pair chosen at compile time inside `hid.c`; the configurable actions (`Win`+1-9, `Ctrl`+`Alt`+A-Z) are indices into fixed ranges, and an index outside those ranges fails closed. Nothing in the module accepts a `char *`. **If you are about to add a function there that does, stop** - that is the LAN-reachable remote execution path this document exists to prevent, and it would look entirely reasonable in a code review.

The transport behind it is a stub until Wave 10: it logs the report it would have sent and reports itself connected, so the Wispr and Launcher screens can be judged on glass before any BLE stack exists. `hid_is_stub()` is how a screen tells the difference and says so honestly.

### Traps this build has already paid for

Each of these cost a flash cycle or worse.

- **Express a constant in slots or in time, never in degrees or in a fraction of a gap.** A ring falloff measured against a fixed 180° and a chase moving a fixed fraction per frame both broke when the item count changed: the selector with three apps behaved nothing like Settings with eight, from identical code.
- **Layout is not animation.** A chase callback that returns early when the ring is already settled will never lay anything out, because on entry it is always settled. The Settings ring drew all eight icons stacked in the centre until the first detent.
- **A one-shot LVGL timer is deleted by LVGL when it fires** (`lv_timer.c:103`). Deleting it again corrupts LVGL's heap, and it only shows on the path where the timer actually fired — so the first few open/close cycles look clean and the fourth hangs the next allocation inside `lv_tlsf_free`. Drop the pointer inside the callback.
- **Every `lv_obj_create` object is clickable by default.** A full-screen container that keeps the flag swallows the long-press, and the selector can never open from that app.
- **`ESP_LOGI`'s format argument must be a string literal**, never a ternary — the macro concatenates it.
- **A `.glyph` of `NULL` handed to `lv_label_set_text` gets LVGL's placeholder.** The Spotify app showed in the selector ring as "Text".
- **The panel ignores MADCTL rotation.** `esp_lcd_panel_mirror` and a `0xC0` in the vendor table were both tried, both transmitted correctly, and neither had any effect; the scan order appears fixed in the `0xF0` page registers. Rotation is done in software with `lv_display_set_rotation` and `sw_rotate`, and `esp_lvgl_port` rotates touch to match — do not also mirror the touch config or it flips twice.
- **A boot-time constant that resembles a live value is a trap.** `backlight_init(40)` logged the compiled default before NVS was mounted and read exactly like a restored setting, costing a test cycle chasing a persistence bug that did not exist. Label a value at the point it is printed.

### Polling and rate limiting

Spotify's published rate limit is a rolling 30-second window with no documented numeric ceiling; a 429 carries a `Retry-After` header. In development mode the quota is now counted per developer account rather than per app. The plan stays well clear:

| Situation | Poll interval |
|---|---|
| Playing | 3 s |
| Paused or 204 | 10 s |
| After any control command | one poll at +400 ms, then resume normal cadence |
| After a 429 | honour `Retry-After`, then double the interval for 60 s |
| After a 5xx or a transport failure | back off 2 s, 4 s, 8 s … to a 60 s ceiling, resetting on the first success. Keep showing the last known state — a 500 from Spotify says nothing about what is playing |

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
3. Stream the JPEG from `i.scdn.co` over HTTPS into a PSRAM buffer. **Measured 20–59 KB** — corrected 2026-09-03; the 15–25 KB this section assumed was low.
4. Decode with `esp_jpeg` at 1:1 → 300×300 RGB565, 180 KB in PSRAM. The S3 has no hardware JPEG unit, so this is CPU work — **measured 140–220 ms**, corrected 2026-09-03 from a budgeted 80–150 ms. That is why it lives on its own task, at priority 3, rather than on the UI thread.
5. **Upscale into the canvas by hand, not by LVGL** (corrected 2026-09-03). A nearest-neighbour lookup plus a scrim multiply per pixel is what lets one opaque RGB565 canvas carry cover, scrim and bloom together. Letting LVGL scale at draw time instead means an ARGB8888 canvas at 518 KB blended every frame.
6. Swap into the LVGL image descriptor, keeping the previous buffer alive until the swap completes. Cross-fade over ~200 ms.
7. Optional, not built: cache the last few covers keyed by URL in PSRAM for instant redraw when skipping back.

**Fetch the 64 px thumbnail first, then the full cover.** The thumbnail is 2–4 KB and lands almost at once. It is published with no fade — fading in something already blurry only delays it — and it opens the connection the cover reuses a few hundred milliseconds later, so the cover pays no TLS handshake at all. Where the smallest entry in the array is already the one being shown, skip the thumbnail stage rather than fetch the same file twice.

**Abandon a fetch the moment the track moves on**, checking both before the socket opens and after every read chunk. On a link measured at 4–76 KB/s that is the difference between the cover you want arriving first and arriving last. Abandoning has to close the connection, because the stream position is unknown afterwards.

Pre-allocate the buffers once and never free them: two 180 KB covers plus the 64 KB download, 424 KB of PSRAM held for the life of the device. Allocating and freeing 180 KB per track change is how PSRAM fragments and the device dies after six hours, and the same argument applies to app switches — going inactive makes the module quiet, it does not make it hand the memory back.

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

### Wave 2 — Board bring-up — **COMPLETE (2026-09-02)**

All five checkpoints passed in one bench day: chip + 8 MB octal PSRAM confirmed, ST77916 up over QSPI, CST816 touch, the dial counting exactly, DRV2605 haptics clicking per detent on the shared I²C bus. Test UI: a counter driven by the dial, reset by a screen tap. Four findings worth keeping:

1. **The dial is not a quadrature encoder** — section 3 corrected; driver ported from the vendor demo as `firmware/knob/main/bidi_knob.c`.
2. **The panel needs Waveshare's vendor init table** (`main/lcd_init_waveshare.h`, from their demo) — the generic ST77916 init leaves colours washed out (no display-inversion command). RGB565 also needs byte-swapping on the wire (`swap_bytes` in the lvgl_port config).
3. **Fast-reversal drift is real** — see the confirmed row in section 9 (open risks) for the D4 numbers and the Wave 10 consequence.
4. On full black at high backlight the module shows edge glow and faint lines from its light guide — physical, scales with backlight duty, invisible at the 40% working default.

(Transient trap, recorded for re-runs: the IDF 5.5 hello_world example ships `MINIMAL_BUILD ON`, which hides the ESP PSRAM menuconfig entry until that line is deleted.)

### Wave 3 — Network and auth — **COMPLETE (2026-09-03)**

Wi-Fi STA, the mbedTLS certificate bundle, NVS-stored credentials, token refresh, and `GET /me/player`. Credentials are seeded into NVS from a gitignored `main/secrets_local.h` that never passes through chat or git; Wave 9 (serviceability) replaces that seeding with real provisioning.

The done condition was met inside Wave 4's structure rather than this one: the log printed the correct track and volume, then survived a deliberately forced token expiry — `access token discarded` → `access token rejected (401)` → `token refreshed, expires_in 3600` → the same correct data again. The forced-expiry test has since been removed; the T+55 min timer and any real 401 are the only refresh triggers now.

Three findings, all of which cost time:

1. **The SSID had a trailing space** (`"Living room "`), invisible in the header. Found by the scan-on-failure diagnostic that now ships in the firmware — after three failed joins it logs every visible 2.4 GHz network with channel and RSSI. Disconnect reason 201 is "network not found"; 15 and 204 mean a bad password.
2. **NVS re-seeds whenever `secrets_local.h` differs from what is stored.** Seeding only when the keys were empty silently ignored corrections. Wave 9 makes NVS the sole truth.
3. **The default system event task stack (2304 bytes) overflowed** once the Wi-Fi handlers ran, crashing on the first disconnect. Raised to 4096 in `sdkconfig.defaults`, and the scan record array made static. Event handlers must stay small and must never block.

**The QR spike passed the same day.** A 198 px `lv_qrcode` carrying the longest realistic payload — the Wi-Fi join string `WIFI:T:WPA;S:Radial-4F2A;P:9f3a7c21b8d4;;` — was recognised by a phone camera at arm's length, first try. That is Wave 9's whole config-screen layout assumption holding. `CONFIG_LV_USE_QRCODE` is on in `sdkconfig.defaults`.

### Wave 4 — App shell, and Spotify inside it — **COMPLETE (2026-09-03)**

The `knob_app_t` contract, a shell owning Wi-Fi and the token, and Spotify written as an app from the first line. Every done condition passed on hardware: a track change on the phone appears within one poll, the progress ring creeps smoothly between polls rather than stepping, and `player_state_t` exists in `main/spotify_app.c` and nowhere else.

**The runtime choice for the dial's second mode proved itself without being told.** The first dial gestures produced `seek -> HTTP 200`, not volume, because the active device reported `supports_volume: false` — the Wave 0 finding arriving as a runtime decision rather than a compiled assumption. That is R5, the requirement that the dial controls volume where the device allows it and seek where it does not.

**The memory hunt is the part of this wave worth keeping.** Free internal RAM fell about 6 KB per poll — 70023 free at 124 s, 33739 at 154 s, 20243 at 184 s — with the largest free block collapsing alongside it. Three suspects were investigated in order and only the third was the leak:

1. **A fresh `esp_http_client` per poll.** Replaced with one client held for the life of the active app, released when the app goes inactive or a transport error occurs. **This was not the leak** — the heap fell at the same rate with one connection as it had with a handshake every five seconds. Kept anyway: it is correct, and it removes a TLS handshake every 5 s.
2. **`CONFIG_MBEDTLS_DYNAMIC_BUFFER`.** The failing allocation named it — `Dynamic Impl: alloc(4437 bytes) failed` — and 4437 bytes was close to what went missing per request. **Also not the leak**: it named the allocator that *failed*, not the one that lost the memory. Turned off regardless, with the reasoning written into `sdkconfig.defaults`, because fixed TLS buffers are the right trade for a device that holds one connection for days.
3. **The actual leak: `state_from_json` called `cJSON_Parse` and never `cJSON_Delete`.** One whole parsed tree lost every five seconds. A `/me/player` response is a few dozen small nodes plus a `strdup` of every string, and with `CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=16384` every allocation under 16 KB comes out of **internal** RAM — which is why PSRAM sat untouched while internal emptied. The token-refresh path parses the same way and always deleted, which is why an hourly refresh never showed the problem and a five-second poll emptied the board in two minutes.

Verified after the fix: nine minutes of continuous polling, roughly ninety requests, three track changes, **net movement +40 bytes**, with the largest free block never leaving 31744.

Two lessons this wave paid for, both of which have bitten since:

- **Certificate errors that begin after a period of correct operation are a memory symptom, not a trust problem.** `PK verify failed`, `Certificate matched but signature verification failed` and `Failed to verify certificate` were all malloc failures wearing a disguise.
- **The right instrument settles an argument that reasoning cannot.** Heap telemetry every 30 s, printing the largest free block alongside the total, turned three plausible hypotheses into one measurement. It still prints, from the shell's housekeeping loop.

**One tension recorded and deliberately not resolved.** The shell's token module is Spotify-specific: `SPOTIFY_TOKEN_URL`, OAuth refresh semantics, cJSON parsing of Spotify's response. Section 6 mandates that, and the reason is sound — refresh must keep working while you are looking at the Clock. But it means the shell knows one provider's auth scheme by name, which collides with the shared-core plan where the halo build swaps in a Windows media-session provider needing no OAuth at all. The clean shape is an auth-provider interface the shell owns and Spotify registers into. Not worth building while Spotify is the only provider.

**One artifact accepted as inherent.** Pausing *from the phone* overshoots the progress ring by about two steps and snaps back; resuming freezes it and then jumps forward. The device holds the last polled position and adds elapsed time locally, so for up to one poll interval it is confidently wrong about a change it has not heard about. Spotify offers no push channel and polling faster is ruled out in section 6. Wave 6 removed the common case by making the device the initiator; what remains is visible only when playback is controlled from somewhere else. Easing to the polled value over ~300 ms is the open option, and it is an interaction change, so it goes through `design/simulator.html` first.

### Wave 5 — Album art — **COMPLETE (2026-09-03)**

`main/albumart.{c,h}`: pick the smallest image at least 300 px wide, compare the URL against the one already shown and do nothing when they match, stream the JPEG into PSRAM, decode to 300×300 RGB565, upscale into the 360 px circle, cross-fade over 200 ms. Every done condition met — art inside the 1.5 s budget, zero downloads on unchanged tracks, heap and PSRAM flat across many track changes and ten minutes of running. The 50-change soak was not run as a formal block; the heap returns to the same figure after every change, which is the same evidence by a different route.

**The buffers are allocated once and never freed** — two 180 KB covers plus a 64 KB download, 424 KB of PSRAM held for the life of the device. `albumart_stop()` makes the module go quiet and frees nothing, which is section 6's rule about never churning 180 KB per track change, applied to app switches as well. The PSRAM baseline with Spotify active is now **7679916**, down 688 KB from Wave 7's figure: the 424 KB of art buffers plus the Spotify screen's own 259 KB canvas.

**The connection lifetime took three attempts, and each was measured rather than argued.**

| Policy | Internal free / largest block | Cover latency |
|---|---|---|
| Held open permanently | 27823 / 14336 | fast |
| Closed after every fetch | 60219 / 31744 | 2197–3183 ms |
| Held 10 s after a fetch (**shipped**) | 59443–59491 / 31744 between covers | 97–588 ms |

Holding it permanently cost 41 KB of internal RAM and left a largest free block of 14336 — **below the 16 KB input buffer a new TLS handshake needs**. The moment that connection dropped it could not have come back, and it would have surfaced as a certificate error rather than as the memory problem it was.

**The rule this leaves: reuse a connection you use every few seconds, drop one you use every few minutes, and for anything bursty in between hold it just long enough to cover the burst.**

**The load is two-stage: blur, then sharpen.** Spotify's 64 px thumbnail, 2–4 KB, is fetched first, upscaled and published with no fade, so something of the right colour is on the glass almost at once; the full cover follows and its publish drives the fade that matters. The reason this works is better than expected — **the thumbnail opens the connection and the cover reuses it a few hundred milliseconds later, so the cover never pays a handshake at all.** Everything downstream sees one 300×300 buffer and never learns which stage produced it. Where the smallest entry in the array *is* the one being shown, the thumbnail stage is skipped rather than fetching the same file twice.

**Stale fetches are abandoned, and the check runs before the socket opens as well as during the read.** A four-track skip run was downloading covers for tracks already skipped past. Abandoning mid-download has to close the connection — the stream position is unknown afterwards — so a run of abandons was paying three handshakes back to back; checking before opening removed them.

**Fetch time is dominated by the radio, not the code.** Reused connections ranged 779–8981 ms for similar file sizes at `rssi: -78`, which is 76 KB/s down to 4 KB/s on the same link. The two-stage load, not the connection policy, is what made the figure reliable.

### Wave 6 — Controls — **COMPLETE (2026-09-03)**

Play/pause, previous and next, the VOLUME and SEEK chips, and the device pill, against both the phone and the desktop. Every command returned a clean status on hardware: `next -> HTTP 200`, `previous -> HTTP 200`, `volume -> HTTP 204`, `seek -> HTTP 200`, and the pill transferring playback both ways between two named devices at `HTTP 204`. Volume tracked `supports_volume` across those transfers without being told — 100% on one device, then 98% and 50% on the other.

**Transport requests are queued, not sent.** A tap runs on the LVGL thread and the HTTP handle belongs to the poll task, which is exactly why that handle needs no locking. A button leaves a note and the poll task posts it on its next turn: worst case a fraction of a second, and the one-writer rule that connection reuse depends on survives.

**The poll interval is cut short after any transport command.** `play -> HTTP 404` is Spotify's NO_ACTIVE_DEVICE, not a missing endpoint, and the play icon had already flipped optimistically with nothing to correct it — a 204 poll carries no state to correct it *with*. The screen now tells the truth within a few hundred milliseconds instead of up to five seconds, whether the command worked or not. Nothing on the device can fix a 404: the Web API can transfer playback to a device it can already see, but it cannot launch one.

**The long-press had to be swallowed.** LVGL sends `CLICKED` on release whether or not `LONG_PRESSED` already fired, so letting go of a long-press would have opened CONTROLS underneath the selector. The first click after a long press is dropped.

**Three things are still unconfirmed on glass** and are carried into Wave 8's bench time rather than holding this wave open: one skip from a fast five-detent spin, a 10-second dial sweep counted in the log, and the CONTROLS chips with their 5 s auto-return specifically.

### Wave 7 — Clock, Settings, and the selector — **COMPLETE (2026-09-03)**

Three apps on the ring, all switching cleanly. `main/clock_app.c`, `main/settings_app.c` and `main/selector.c`, with the shell gaining an app registry, screen switching, SNTP, the alarm overlay and an input task.

**The contract held.** The Clock was written without a single change to shell code on its behalf, which is this wave's real done condition. Everything the shell gained — haptics, the timer, the registry — is a service section 6 already gives it. The honest caveat: the input task and the switching machinery were always in the design, but the second app is what caused them to be written.

**Memory returns exactly, not approximately.** PSRAM lands on the same figure every time — 8384448 with Spotify exited, 8368060 with it active, and the Clock's 259 KB canvas showing as a clean round trip down to 8122300 and back. Repeated across four power cycles. A canvas leak would appear as 256 KB steps and there are none. (Those figures predate Wave 5's art buffers; see that wave for the current baseline.)

Three things the shell had to grow, each for a hardware reason:

1. **Dial events go through a queue to an input task.** They arrive on the esp_timer task, which is also where the dial's own polling runs; a haptic I²C write or a bloom render there would stall that task and cost detents. This is section 6's `input_task`, arriving because the hardware demanded it.
2. **The timer belongs to the shell, not the Clock app.** A timer that stopped counting when you left the Clock would be useless, and it has to fire wherever you are. The Clock app is its UI. Same split as the token and the Spotify app.
3. **The Spotify poll task is persistent**, idling on a semaphore when inactive rather than being created and destroyed. The old shape made `on_exit` wait for an in-flight HTTP request — up to a 10 s timeout — and `on_exit` runs on the LVGL thread, so that wait was a frozen screen. Nothing may block a switch.

**The bloom is affordable only because it bypasses LVGL.** The first implementation called `lv_draw_line` once per ray, 300 times a frame, into a PSRAM canvas. It did not merely run slowly: it starved the LVGL task so completely that `IDLE0` never ran, the task watchdog fired repeatedly and the device wedged. Each `lv_draw_line` is a full draw-task dispatch and blend pass — cheap for the few shapes a screen normally holds, ruinous three hundred times a frame, and worse again with the canvas in PSRAM where every blend is a read-modify-write across a slow bus. Rewritten as a DDA walk with an inline RGB565 blend straight into the canvas buffer: **300 rays in 27 ms**, about 14% of one core at the 5 fps the design calls for, and that is the budget every future full-screen effect has to fit.

**Settings persists on leaving an item, never on every detent.** All four dial-set values survive a power cycle at non-default settings. A false alarm here cost a test cycle and is worth the warning: brightness was reported as not surviving, when in fact `backlight_init(40)` runs as the first statement of `app_main`, before `nvs_flash_init`, and logged a compiled constant that looked exactly like a restored value. **A boot-time constant that resembles a live value is a trap; label it at the point it is printed.** That line now says `(boot default, pre-NVS)`, and both the load and save paths print all four values.

**Sleep is proven on hardware** — `screen off (10 min idle)` — which also closed the part of this wave that had only been inferred from what NVS held.

### Wave 8 — Live-on-the-desk robustness — **IN PROGRESS**

- Wi-Fi reconnect with backoff, 401/429/204/5xx handling, backlight dim after inactivity, task watchdog, panic reboot.
- **Already standing**, built as a side effect of Waves 3 to 7: 204 and 401 with token refresh, 429 with `Retry-After` and an honest rate-limited screen, token refresh with exponential backoff, Wi-Fi reconnect on disconnect, and backlight sleep proven live.
- **Genuinely missing:** 5xx handling, backoff on the Wi-Fi reconnect (it retries flat out, which hammers a router that is still booting), the task watchdog, and panic reboot.
- **Done when:** the device survives a router reboot, a 12-hour idle period, and a forced 429 without needing a power cycle.

Step-level detail is in `WAVE-8.md`; section 10 carries the table of what stands and what does not.

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
- **Done when:** spinning right starts dictation and spinning right again does not stop it; spinning left stops it; two spins the same way inside 2 s resync a deliberately desynced device; and the album art fetch time with BLE connected is recorded in this document.

**The UI half landed 2026-09-04, ahead of the transport.** `main/wispr_app.c` implements screens 13 A and 13 B of `design/screens.html` rev W: the belief, the three-detent threshold, the idempotent direction mapping and the 2 s resync are all built and can be judged on glass. What is missing is only the transport - `main/hid.c` is a stub that logs the report it would have sent and reports itself connected, so the screens are exercisable without a BLE stack existing. Wave 10 deletes `HID_TRANSPORT_STUB`, fills in `send_report`, and does the throughput measurement; nothing above `hid.h` should need a line changed.

### Wave 11 — Launcher

- Mode 1: the ring, the P4 config-page editor, the fixed chord enum, and the eight-entry cap with its greyed-out add button.
- Mode 2: Task View driving, including the 5 s idle `Esc`. Build this second — it is smaller, and it is worthless if mode 1 is not already proving the HID path.
- **Done when:** the chord field on the editor cannot accept free text; every configured entry launches or focuses its application from cold; the list survives a power cycle; Task View mode returns the dial to Spotify after 5 s of no input with Task View closed on the PC; and a chord sent while the PC is locked changes nothing on the PC and does not wedge the device.

**The UI half landed 2026-09-04, ahead of the transport and ahead of the editor.** `main/launcher_app.c` implements screens 15 A, 15 B and 15 C: the ring, the 1.5 s "Launching" statement, and Task View mode with its arrow mapping, hold-to-cancel and 5 s idle escape. Two things are deliberately deferred. The entry list is a compiled placeholder rather than NVS, because the editor that fills it is Wave 9's config page and naming an application is typing. And the chords are real `hid_action_t` values but nothing sends them yet.

---

## 9. Open risks

| Risk | Impact | Handling |
|---|---|---|
| Volume refused by the phone (**confirmed, Wave 0**) | The dial has nothing to adjust on the device most listening happens on | **Revised 2026-09-04.** The first answer was an automatic fallback to seek, and it was built and used before being removed — a dial you turned for volume that scrubbed the track instead was worse than one that did nothing. It now raises CONTROLS, which carries every action the dial cannot perform, SEEK included. See R5 |
| ~~Pin map wrong~~ | — | **Closed 2026-08-31** — verified against the schematic; see section 3 |
| ~~Component versions clash~~ | — | **Closed 2026-08-31** — full set builds clean on IDF 5.5.5 |
| ~~Post-February-2026 Client ID may not reach every endpoint~~ | — | **Closed 2026-08-31** — all seven pre-flighted, none restricted; see section 1 |
| Rate limit hit despite the budget (**happened 2026-09-03**: 429 with an 11-hour `Retry-After`, caused by forgotten simulator tabs polling on the same dev-mode account quota, not by the firmware) | Screen goes stale for hours; the quota is per developer account, so anything else using the Client ID spends the device's budget | `Retry-After` handling plus interval doubling, Wave 8. Simulator now stops polling in hidden tabs and `serve_sim.py` no longer auto-opens them |
| Refresh token expiry at 6 months | Device dies silently | Wave 9 web config; calendar reminder as the interim |
| Accidental skips from knocking the knob | Daily irritation | Burst collapsing + lockout in Wave 6; quarter-turn commit as fallback |
| ~~PSRAM fragmentation from repeated art buffers~~ | — | **Closed 2026-09-03** — the three art buffers are allocated once and never freed. PSRAM returns to an identical figure after every track change and every app switch |
| ~~QR unreadable at 21 mm~~ | — | **Closed 2026-09-03** — a 198 px code carrying the full Wi-Fi join string was recognised first try at arm's length (Wave 3). The SSID and IP are still printed under every code as a manual route |
| Internal RAM is thin while the art connection is held (**measured 2026-09-03**: 23–27 KB free, 12800–14336 largest block, against ~59 KB / 31744 with it closed) | If the *player's* connection dropped inside that 10 s window, its handshake buffer might not fit | Accepted. It releases the handle and retries on the next poll, by which time the art connection has aged out — a one-poll delay, not a wedged device. The window was already halved from 20 s to 10 s over this |
| Album art fetch time is set by the radio, not the code (**measured 2026-09-03**: 4–76 KB/s on one link at `rssi: -78`) | Covers arrive late on a weak link regardless of what the firmware does | The two-stage thumbnail-then-cover load keeps something correct on the glass at once. Re-measure closer to the access point before concluding anything else about fetch time |
| Launcher chords go stale when the taskbar is reordered | Wrong app launches, silently | `Win`+`N` is inherently positional. Prefer `Ctrl`+`Alt` shortcut keys on `.lnk` files for anything you care about — those follow the file, not the position |
| A chord fires while the PC is locked or asleep | Nothing happens, and the device cannot say why | Accepted, not solved. The launcher is open-loop by design, which is why the confirmation says "Launching" and never "Launched" |
| A config-page endpoint that forwards text to the HID layer | Remote code execution on the PC from anywhere on the LAN | Architectural rule in section 6: the HID layer accepts a fixed action enum, never a string. Check for this in review, not at runtime |
| Encoder emits phantom counts on fast reversal (**confirmed, Wave 2 D4, 2026-09-02**: drift +2,+1,0,−2,0,+1,+1,+2,+3,+4 over ten fast waggles, clockwise bias, worst +4) | Fast direction changes miscount; slow single detents count exactly, so ordinary corrections are barely exposed | **The waggle gesture was retired over this** (section 5, 2026-09-02). Residual exposure is volume accuracy during violent corrections; one driver-tuning experiment (poll/debounce in `bidi_knob.c`) still worth trying |
| BLE HID reconnect after PC sleep | Dictation trigger dead until replug | Windows is unreliable here. If it proves bad, Classic BT HID on the second MCU (UART, GPIO48/38) is the fallback — more work, better reconnect |
| BLE and Wi-Fi contending for one radio | Album art visibly slower | Measured in Wave 10; BLE can be scoped to the Wispr app if the numbers are bad |
| Radial's believed dictation state drifts from reality | Spinning right does nothing | Two spins the same way inside 2 s force the toggle; the Flow Bar is the visible truth |
| Wispr ignores its hands-free chord while certain apps have focus (**observed with VS Code, 2026-08-31**) | Belief flips, reality does not — the trigger looks dead | Wispr-side quirk, not the transport: it reproduces from a physical keyboard. Resync spin recovers; if it proves frequent, revisit whether hotkey-driven hands-free is reliable enough at all |
| Phone abandons the SoftAP mid-setup | Setup appears to hang; both iOS and Android drop a Wi-Fi network with no internet | Captive-portal responses on the well-known probe URLs (`/generate_204`, `/hotspot-detect.html`) keep the phone attached; Wave 9 |

---

## 10. Current wave — step by step

> This section always describes **only the wave being worked on right now**. When the wave is done, it is deleted and replaced with the next one. Nothing accumulates here.

### Wave 8 — Live-on-the-desk robustness — in progress, see `WAVE-8.md`

The step-level detail — per-step actions, exact commands, a pass test per step — lives in **`WAVE-8.md`** at the repo root. When the wave is done its results are written back here and that file is deleted, which is the process Waves 2 through 7 all followed.

**Where it starts.** Most of this wave was built as a side effect of Waves 3 to 7, so it is worth being precise about what already stands, and putting the time on what does not:

| Behaviour | State |
|---|---|
| 204, nothing playing | Working — a distinct idle state on screen and a 10 s poll interval |
| 401 with token refresh | Working — proven first by a forced expiry, since by real ones |
| 429 with `Retry-After` | Working — honoured rather than polled through, with an honest rate-limited screen |
| Token refresh backoff | Working — exponential, and a `400 invalid_grant` stops dead rather than retrying |
| Wi-Fi reconnect on disconnect | Working, but it **retries flat out** |
| Backlight sleep after inactivity | Working — `screen off (10 min idle)` seen on hardware |
| **5xx from Spotify** | **Missing** |
| **Backoff on the Wi-Fi reconnect** | **Missing** — flat-out retry hammers a router that is still booting |
| **Task watchdog** | **Missing** |
| **Panic reboot** | **Missing** |

Four small pieces of code, then three soak tests: a router reboot, twelve hours idle, and a forced 429, each survived without a power cycle. More waiting than coding.

**Three things from Wave 6 (controls) are still unconfirmed on glass** and belong in this wave's bench time, since the board will be sitting there anyway: exactly one skip from a fast five-detent spin, a 10-second dial sweep with its API calls counted in the log, and the CONTROLS chips with their 5 s auto-return.

---

### Notes for the next wave

Wave 9 is serviceability, and it is the largest remaining wave: Wi-Fi provisioning over SoftAP with a captive portal and QR, the Windows scheduled task that re-authorises on day 170, `tools/reauth.py`, the `esp_http_server` config endpoint gated by a 120-second boot window, and the fallback screen. Section 8's Wave 9 is written out step by step and **the ordering matters** — static page, then POST handler, then NVS write, then WebSocket, then QR — because each step is testable on its own and the QR is the only part that needs the panel.

**Two things can be done on the PC at any time, with no board.** Bind the Wispr hands-free action to its own shortcut (section 6), and create the launcher `.lnk` shortcuts with their `Ctrl`+`Alt` keys. Both are verifiable from your own keyboard, and doing them early means Waves 10 and 11 only ever have to prove the BLE path.

### Design decisions still open

These are decisions, not code, and each is parked deliberately.

- **Which idle pattern.** `design/idle-patterns.html` offers six candidates with no decision recorded anywhere. The Clock ships number 06, the bloom, by default rather than by choice. It wants judging at 46 mm and then recording here.
- **Michroma.** `design/screens.html` rev W sets the title in Michroma; only Montserrat is on the device. rev W's own footer flags the width as the live question — about 13 characters fit before a title scrolls. Adding the face means a `sdkconfig` change and converting the font, worth doing only once the sizes have been judged at true size.
- **The progress-ring snap.** Pausing from the phone overshoots the ring and snaps back, because local interpolation is confidently wrong for up to one poll. An eased correction over ~300 ms would read as deliberate. It is an interaction change, so it goes through `design/simulator.html` first.
- **The 204 "nothing playing" ray field**, tinted from the last cover. Both the tint and the field exist now, so this is small — but it belongs with the idle-pattern decision above rather than ahead of it.
- **Adverts** (`currently_playing_type == "ad"`). Three lines, not yet written.

### Deviations from `design/screens.html` rev W, to reconcile at rev X

rev W is owned by a separate session taking it to rev X — **read it, never edit it**. Three things now differ and should be reconciled once that session releases the file:

- **CONTROLS, the one-tap transport screen, uses the full NOW PLAYING composite** — artwork undimmed, progress rim present. rev W specifies artwork at 45% and no rim. On the panel that read as the screen going wrong rather than as a layer arriving.
- **The progress rim draws nothing where unlit.** rev W has a faint unlit band; at any alpha visible on glass it made the ring read as a full white circle with the progress mark lost in it.
- **Type sizes are larger throughout**, and the volume `%` is full size rather than a small dim suffix. LVGL cannot mix sizes inside one label, and a second positioned label for one glyph costs more alignment than it is worth.
