# Spotify Knob — Build Document

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
| R4 | Toggle play/pause from the screen (and from the knob press) |
| R5 | The dial controls **volume** by default. Where the active device refuses volume it controls **track seek** instead, chosen at runtime (see the Wave 0 result below). The assignment can be switched by hand from the controls screen |
| R8 | Move playback to the PC from the device, so the dial regains volume control without picking up the phone |
| R6 | Work against playback on a phone or a Connect speaker — **not** the PC |
| R7 | Boot on power-up, reconnect on its own, and require no interaction on a normal day |

### Explicit non-goals

Playing audio on the device. Playlist browsing. Search. Library management. Controlling anything other than Spotify (that is a later project, and the architecture below does not block it).

### Verified constraints

**2026-08-31 — Wave 0 result.** Volume control was tested against two playback devices:

| Device | `supports_volume` | Volume command |
|---|---|---|
| Android phone (primary listening device) | `false` | `403 VOLUME_CONTROL_DISALLOW` |
| Windows desktop (Spotify desktop app) | `true` | `204` accepted |

The phone's refusal is a Spotify-side restriction on that class of device — not a fault, and there is no workaround. Because at least one real device does accept volume, **both variants of the second dial mode are in scope** and the choice is made at runtime. Album art is available at 640×640 on both.

---

## 2. Architecture

**A standalone Wi-Fi device talking directly to the Spotify Web API.**

The knob holds a Spotify refresh token, refreshes an access token hourly, polls `GET /me/player` for state, downloads album art over HTTPS, and issues control calls. Nothing else on the network is involved, and no software runs on any PC.

This is forced by R6. Because audio plays on a phone or a speaker, anything that reads now-playing state from the desktop is blind — the PC has no idea what the phone is doing. The cloud API is the only source of truth that follows playback wherever it goes.

### Constraints this creates

- Spotify **Premium is mandatory** — every Web API playback-control endpoint refuses free accounts.
- Control latency is a cloud round trip, roughly 150-400 ms from the UK, plus Spotify's own propagation to the phone. Responsive, but not instant.
- State is **polled, not pushed**. The screen lags reality by up to one poll interval when the track is changed on the phone.
- The refresh token expires **6 months after authorisation**. Re-authorisation is a scheduled chore (see Wave 8).
- TLS, JSON parsing and JPEG decoding all happen on the ESP32. This is the bulk of the firmware work.
- Volume is the only control the target playback device can refuse, and one of the two devices in use does refuse it. The second dial mode must therefore be chosen at runtime from `device.supports_volume`, never assumed or compiled in.

---

## 3. Hardware facts

| Item | Detail |
|---|---|
| Main MCU | ESP32-S3R8, 240 MHz, 8 MB PSRAM, 16 MB flash |
| Second MCU | ESP32-U4WDH, 4 MB flash — **audio subsystem only, not used by this project** |
| Display | 1.8" round, 360×360, **ST77916** driver, QSPI bus |
| Touch | **CST816** capacitive, I2C |
| Encoder | Mechanical rotary, quadrature, with push |
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
2. **The encoder push button is on GPIO0**, which is the ESP32-S3 boot strapping pin. Holding the knob in while power-cycling drops the board into download mode. Harmless at runtime; confusing the first time it happens.

---

## 4. Toolchain and dependencies

**ESP-IDF v5.5.x.** ESP-IDF v6.0 shipped in March 2026 and is fine in isolation, but the managed components this project leans on — and Waveshare's own board demos — are still written against the 5.x API surface. Wave 0 includes an explicit build check; if everything compiles clean on 6.0, use 6.0.

Build system: `idf.py` directly. PlatformIO is not needed and adds a version-pinning layer between you and the components.

The screen is driven by LVGL in C. There is no web browser for the ESP32, so HTML cannot render on the device's display — something must turn markup into pixels, and that something is a browser engine far larger than this chip can hold. HTML does appear in this project, but only in Wave 8, where the device serves a config page to a browser on your phone.

`main/idf_component.yml`:

```yaml
dependencies:
  idf: ">=5.4"
  lvgl/lvgl: "^9.2"
  espressif/esp_lvgl_port: "^2.7"           # display + touch + encoder glue for LVGL
  espressif/esp_lcd_st77916: "^1.0.1"       # QSPI panel driver
  espressif/esp_lcd_touch_cst816s: "^1.1.2"
  espressif/knob: "^1.1.0"                  # quadrature decoding for the encoder
  espressif/esp_jpeg: "^1.3"                # album art decode
```

Versions checked against the ESP Component Registry on 2026-08-31. `espressif/button` is deliberately absent — this board has no button.

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
```

Partition table: custom, single 4 MB app partition (headroom for OTA later) plus NVS. 16 MB flash makes this a non-issue.

---

## 5. Interaction model

Continuous control lives on the dial. Discrete control lives one tap away. Colour carries meaning consistently: **white is progress, green is volume, yellow is seek.**

### NOW PLAYING — the default screen

- Album art fills the circle. A thin white ring traces track progress around the bezel with a chip riding the current position — it earns its place on long podcast episodes even when it is redundant on a three-minute track. It belongs to this screen only; the dial screens replace it rather than layer over it.
- Title and artist, centred, with the title scrolling as a slow marquee only when it overflows.
- **Dial → volume.** Turning it raises the feedback overlay below.
- **Touch anywhere → CONTROLS.**

**There is no knob press** — the schematic verification in section 3 found no push switch on this board. **Play/pause is therefore the centre button on CONTROLS**, two taps from the default screen. No hidden gestures: no double-tap, no long-press. Decided 2026-08-31.

### Dial feedback — transient, ~2 s

Raised the moment the dial moves, gone two seconds after it stops. Artwork drops to near-black, a phyllotaxis bloom is cut by a wedge, and the value sits in the middle with no label — a percentage in green and a timestamp in amber cannot be mistaken for one another.

- **Volume:** green, 0–100%, ±5% per detent.
- **Seek:** amber, ±10 s per detent — the lit boundary is the playhead.

The bloom is one 300-point field shared by both, and by the idle screen where nothing is lit. Pre-render it once at boot; the only live work is the segments currently on.

Both write once, 400 ms after the last detent. Spin freely; the screen updates locally at every step.

### CONTROLS — one tap from the default screen

- **Transport across the middle:** previous, play/pause, next, at full thumb size. This is where skipping lives.
- **Two chips below:** VOLUME and SEEK, assigning the dial. The choice persists.
- **Device pill at the top:** shows where audio is playing. Tapping it transfers playback to the desktop via `PUT /me/player`.
- Auto-returns to NOW PLAYING after 5 s.

### Behaviours that need deciding once and then holding

- **Volume availability is read, never assumed.** `GET /me/player` returns `device.supports_volume`, re-checked on every poll. When false — which is the case on the phone — the VOLUME chip greys out and the dial falls back to seek so the knob is never inert. Transferring playback to the desktop re-enables it within one poll.
- **Transfer, not launch.** `PUT /me/player` moves playback to a device Spotify can already see, which requires the desktop app to be running. It cannot start or focus an application; nothing in the Web API can. Doing that would need a resident agent on the PC — deliberately out of scope, since this project currently runs no permanent background process on any machine.
- **Writes are debounced.** A single call 400 ms after the last detent is what keeps the device inside the rate limit during a long volume sweep.
- **Haptics.** One short DRV2605 click per detent, a heavier one on transport button presses. Cheap to add, and most of what makes the thing feel like a control rather than a screen.
- **Adverts.** `currently_playing_type == "ad"` — show "Advert", suppress the transport buttons. Not applicable on Premium, but three lines that prevent a confusing state.
- **Nothing playing.** `GET /me/player` returns HTTP 204. The screen shows the moiré ray field described in `design/screens.html`, tinted from the last cover's average colour, with the clock over it. The dial does nothing.
- **Sleep.** After 20 minutes idle the backlight goes off entirely and the animation stops — a permanently-powered desk object should not be a permanently-lit one. It wakes on touch, on dial movement, or on playback resuming anywhere.

Screen designs for all of the above live in `design/screens.html`.

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

`player_state_t` holds: `is_playing`, `track_id`, `title`, `artist`, `album_art_url`, `progress_ms`, `duration_ms`, `volume_percent`, `supports_volume`, `device_name`, `last_update_tick`.

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

**The 180-day expiry is a hard deadline, and it is predictable.** Spotify enforces a 6-month refresh token lifetime measured from the moment of the user's original authorization. Refreshing the access token does **not** reset or extend it. So the death date is simply `auth_date + 180 days`, which is why `auth_date` is stored — the device can warn before it happens rather than just stopping.

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
4. Leave the app in **development mode**. It permits up to 25 users and needs no review. Extended quota mode requires a real application and is not appropriate here.
5. Run `tools/spotify_auth.py --client-id <your id>`. It performs the PKCE flow, prints the refresh token, and then runs the pre-flight diagnostic.

PKCE rather than the client-secret flow, deliberately: the device never holds a secret, so a stolen board is not a stolen credential.

---

## 8. Build plan

Each wave has a done condition you can check rather than judge.

### Wave 0 — Prove the Spotify side — **COMPLETE (2026-08-31)**

Result recorded in section 1 under Verified constraints. Volume works on the desktop, not on the phone; both variants of the second dial mode are in scope.

### Wave 1 — Toolchain — **COMPLETE (2026-08-31)**

ESP-IDF v5.5.x installed and verified. Board schematic in the repo.

### Wave 2 — Board bring-up

- Flash `hello_world`, confirm the chip and PSRAM from the boot log.
- Bring up ST77916 over QSPI, CST816 over I2C, and the encoder via `espressif/knob`, all through `esp_lvgl_port`.
- Test UI: a number that increments on clockwise rotation, decrements anticlockwise, resets on knob press, and a button that changes colour on touch.
- **Done when:** all four inputs are demonstrably correct and the pin map in section 3 has been confirmed or corrected in this document.

### Wave 3 — Network and auth

- Wi-Fi STA, mbedTLS cert bundle, NVS-stored credentials, token refresh, one `GET /me/player`.
- **Done when:** the serial log prints the current track name and volume, and continues to print it correctly after the access token has expired and been refreshed once (verify by forcing a refresh, not by waiting an hour).

### Wave 4 — Now-playing screen, text only

- Poll loop, `player_state_t`, title/artist/progress/volume rendered. No art yet.
- **Done when:** changing tracks on the phone updates the screen within one poll interval, and the progress bar advances smoothly between polls.

### Wave 5 — Album art

- Download, decode at 1/2 scale, render, cross-fade, cache by URL.
- **Done when:** art appears within ~1.5 s of a track change, heap and PSRAM are stable across 50 consecutive track changes, and repeated polls of an unchanged track trigger zero downloads.

### Wave 6 — Controls

- Play/pause, dial-to-skip with burst collapsing and lockout, second dial mode with debounced writes, haptics, runtime selection between volume and seek from `supports_volume`.
- **Done when:** every control in section 5 works against the phone, a fast five-detent spin produces exactly one skip, a 10-second dial sweep produces at most a handful of API calls (count them in the log), and moving playback to a device that supports volume switches the second mode from seek to volume within one poll.

### Wave 7 — Live-on-the-desk robustness

- Wi-Fi reconnect with backoff, 401/429/204/5xx handling, backlight dim after inactivity, task watchdog, panic reboot.
- **Done when:** the device survives a router reboot, a 12-hour idle period, and a forced 429 without needing a power cycle.

### Wave 8 — Serviceability

Every 180 days the refresh token dies. That is Spotify policy, applies to every app, and cannot be engineered away. What *can* be engineered away is you having to notice.

**The target experience:** on roughly day 170, a browser tab opens on your PC by itself showing the Spotify login page. You click Agree. The knob reboots working. You are never told a token expired, and you never see one.

The expiry date is deterministic — 180 days from authorisation, and refreshing does not extend it — so this does not need monitoring, polling, or a background service. It needs a calendar entry.

**Why the PC is in the loop.** Spotify permits plain-HTTP redirect URIs only on `127.0.0.1`, so the knob cannot receive the OAuth callback itself, and Spotify offers no device authorisation grant (the "enter this code at spotify.com/pair" pattern TVs use). The browser and the loopback listener must live on a real computer. Since the knob is a desk extension of that computer, this is not a compromise.

Four parts:

**1. Initiation — a Windows scheduled task.** `tools/reauth.py --install-schedule` runs `schtasks` once to create a task that fires 170 days out, with "run as soon as possible after a missed start" enabled so a week of the PC being off does not break it. Each successful run re-arms the task for another 170 days, so it maintains itself and there is nothing to remember.

This is the whole initiation mechanism. No tray app, no service, no daemon, nothing running in the background.

**2. `tools/reauth.py --push-to`.** An extension of the Wave 0 script. When the task fires, it:

1. Starts the loopback listener on `127.0.0.1:8888`
2. Opens the browser on Spotify's login page — the same screen as Wave 0
3. Receives the code, completes the PKCE exchange
4. `POST`s the new refresh token to `http://spotify-knob.local/api/token`
5. Re-arms the scheduled task and exits

The device is found by mDNS, which Windows resolves natively; `--device <ip>` overrides it. If the knob is unreachable it writes the token to `spotify_tokens.json` and retries on next boot rather than losing it.

**3. A config endpoint on the device.** `esp_http_server` with two routes: `POST /api/token` (writes `refresh_token`, stamps `auth_date`, reboots) and `GET /` carrying Wi-Fi fields and OTA upload for the rarer jobs. HTML as a C string constant; reference implementation at https://randomnerdtutorials.com/esp-idf-esp32-web-server/, roughly 150 lines including Wi-Fi setup.

Gate both routes on physical presence: the server only responds for 10 minutes after a knob long-press, except `POST /api/token` which is additionally accepted during the first 60 seconds after boot so the retry path works unattended.

**4. A fallback screen.** If the schedule never ran — new PC, task deleted, six months of bad luck — the device must still be recoverable by someone who remembers nothing. On `invalid_grant` the display switches to:

```
      Spotify login expired

   Run  reauth.bat  on your PC

        spotify-knob.local
```

This screen is the recovery documentation. It should never be seen, and it must work when it is.

- **Done when:** the scheduled task exists and re-arms itself, a forced run re-authorises the device end to end with one click in the browser, and unplugging the knob mid-flow does not lose the new token.

---

## 9. Open risks

| Risk | Impact | Handling |
|---|---|---|
| Volume refused by the phone (**confirmed, Wave 0**) | R5 as originally written is unbuildable | Second dial mode is chosen at runtime: seek on the phone, volume on devices that allow it |
| ~~Pin map wrong~~ | — | **Closed 2026-08-31** — verified against the schematic; see section 3 |
| Component versions clash with each other or with IDF 5.5 | Half a day | `firmware/knob/` builds the full set with no hardware — run it before the board arrives |
| Rate limit hit despite the budget | Screen goes stale intermittently | `Retry-After` handling plus interval doubling, Wave 7 |
| Refresh token expiry at 6 months | Device dies silently | Wave 8 web config; calendar reminder as the interim |
| Accidental skips from knocking the knob | Daily irritation | Burst collapsing + lockout in Wave 6; quarter-turn commit as fallback |
| PSRAM fragmentation from repeated art buffers | Crash after hours | Fixed-size pre-allocated art buffers, verified in Wave 5 |

---

## 10. Current wave — step by step

> This section always describes **only the wave being worked on right now**. When the wave is done, it is deleted and replaced with the next one. Nothing accumulates here.

### Wave 2 — Board bring-up

**Goal:** every piece of hardware this project touches — screen, touch, dial, knob press — proven working under LVGL.

**This wave needs the board.** It is written to be worked through in order the day it arrives.

**Do this part now, before the board arrives.** `firmware/knob/` is a project that pulls in every library the real firmware needs and does nothing else. It builds with no hardware attached, and passing it closes the last risk that can be closed early:

```powershell
cd firmware\knob
idf.py set-target esp32s3
idf.py build
```

"Project build complete" is the whole test. If a component fails to download, correct its version in `main/idf_component.yml` against components.espressif.com. If one fails to compile, note which and stop — that means a version constraint needs loosening, not that anything is wrong with the design.

Everything from Checkpoint A onwards needs the board.

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

If it hangs on `Connecting......_____`, hold the knob in (it is wired to GPIO0, the boot pin), tap RESET, release.

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

**D1.** Add the `espressif/knob` component. Encoder A on **8**, B on **7**. There is no button, so `espressif/button` is not needed.

**D2.** Register with `lvgl_port_add_encoder()`, passing a knob handle and no button handle.

**D3.** Test UI: a large number in the centre. Clockwise increments, anticlockwise decrements.

**Checkpoint D done when** both directions are correct and one physical detent produces exactly one step — not two, not none. If a single detent moves the number by two, the knob component needs its counting mode adjusted.

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
