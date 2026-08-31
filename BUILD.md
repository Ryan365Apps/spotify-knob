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
| R3 | Skip to next / previous track by spinning the dial |
| R4 | Toggle play/pause from the screen (and from the knob press) |
| R5 | Switch the dial into volume mode via an on-screen control, then spin to set volume |
| R6 | Work against playback on a phone or a Connect speaker — **not** the PC |
| R7 | Boot on power-up, reconnect on its own, and require no interaction on a normal day |

### Explicit non-goals

Playing audio on the device. Playlist browsing. Search. Library management. Controlling anything other than Spotify (that is a later project, and the architecture below does not block it).

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
- Volume is the only control that the target playback device can refuse. See R5 and Wave 0.

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

### Pin map (verify against the Waveshare schematic before writing driver init)

| Function | GPIO |
|---|---|
| LCD CS | 14 |
| LCD SCLK | 13 |
| LCD D0–D3 | 15, 16, 17, 18 |
| LCD RESET | 21 |
| Backlight | 47 |
| Touch SDA / SCL | 11 / 12 |
| Touch INT / RST | 9 / 10 |
| Encoder A / B | 8 / 7 |
| Encoder push | 0 |

> These come from community ESPHome and Tasmota configurations for this board, cross-checked against the Waveshare wiki. Treat them as a strong starting hypothesis, confirm in Wave 1, and correct this table if any pin is wrong.

### Two gotchas that will cost you an hour each if you do not know them

1. **The USB-C cable orientation selects which MCU you flash.** Flip the connector if the board enumerates as the wrong chip. This is a documented board behaviour, not a fault.
2. **The encoder push button is on GPIO0**, which is the ESP32-S3 boot strapping pin. Holding the knob in while power-cycling drops the board into download mode. Harmless at runtime; confusing the first time it happens.

---

## 4. Toolchain and dependencies

**ESP-IDF v5.5.x.** ESP-IDF v6.0 shipped in March 2026 and is fine in isolation, but the managed components this project leans on — and Waveshare's own board demos — are still written against the 5.x API surface. Wave 0 includes an explicit build check; if everything compiles clean on 6.0, use 6.0.

Build system: `idf.py` directly. PlatformIO is not needed and adds a version-pinning layer between you and the components.

`main/idf_component.yml`:

```yaml
dependencies:
  idf: ">=5.4"
  lvgl/lvgl: "^9.2"
  espressif/esp_lvgl_port: "^2.7"      # display + touch + encoder glue for LVGL
  espressif/esp_lcd_st77916: "^1.0"    # QSPI panel driver
  espressif/esp_lcd_touch_cst816s: "^1.0"
  espressif/knob: "^0.1"               # required by esp_lvgl_port's encoder support
  espressif/button: "^3.5"             # required for the encoder push
  espressif/esp_jpeg: "^1.3"           # album art decode, supports 1/2 1/4 1/8 downscale
```

Check the current version of each in the ESP Component Registry when you add it; the carets above reflect what was published at the time of writing.

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

Two modes. The screen is never more than one gesture from either.

**NOW PLAYING (default)**

- Album art fills the circle, 320×320, centred.
- Track title and artist on a translucent band across the lower third.
- Small play/pause glyph, dimmed, top of screen.
- **Dial spin → next / previous track.** Clockwise next, anticlockwise previous.
- **Knob press → play/pause.**
- **Tap anywhere → reveal the control ring** (play/pause button centre, volume chip below it). Auto-hides after 4 s.

**VOLUME**

- Entered by tapping the volume chip.
- Album art dims to ~30%, a thick arc traces the circle edge, large percentage in the middle.
- **Dial spin → volume, 5% per detent.**
- Auto-returns to NOW PLAYING after 4 s of no rotation.

### Behaviours that need deciding once and then holding

- **Accidental skips.** One detent equals one skip is what you asked for, and it is the right default for a deliberate spin. It is also the most likely source of annoyance — a knocked knob skips a track. Mitigation built in from Wave 5: a 300 ms lockout after each skip, and detents arriving inside a single 400 ms burst collapse to **one** skip rather than five. If it still misfires in real use, the fallback is requiring a quarter-turn before the first skip commits.
- **Volume writes are debounced.** Spin freely; the arc updates locally at once, and a single `PUT /me/player/volume` fires 400 ms after the last detent. This is what keeps you inside the rate limit.
- **Haptics.** One short DRV2605 click per detent, a heavier one on skip commit. Cheap to add, and it is most of what makes the thing feel like a real control rather than a screen.
- **Volume may not be available.** `GET /me/player` returns `device.supports_volume`. When false, the volume chip renders greyed with the device name — Spotify genuinely refuses volume control on some phone and web endpoints, and silently failing would be worse. Wave 0 tests this against your actual device before any firmware is written.
- **Adverts.** `currently_playing_type == "ad"` — show "Advert", suppress skip. Not applicable on Premium, but it costs three lines and prevents a confusing state.
- **Nothing playing.** `GET /me/player` returns HTTP 204. Show the last art heavily dimmed with a clock; dial and buttons do nothing until playback resumes somewhere.

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

- `client_id` and `refresh_token` live in NVS, not in source, not in git.
- On boot: refresh immediately. Then refresh at T+55 min, and on any 401.
- The refresh response **may or may not** include a new `refresh_token`. If it does, write it to NVS before using it; if it does not, keep the existing one. Getting this wrong is how the device dies silently three weeks later.
- Two consecutive refresh failures → show a re-auth screen rather than an endless retry loop.

### Album art pipeline

1. Compare the new `album.images[0].url` against the cached one. Same URL → do nothing. This is the single most important optimisation; most polls change nothing.
2. Stream the 640×640 JPEG from `i.scdn.co` over HTTPS into a PSRAM buffer (typically 40–90 KB).
3. Decode with `esp_jpeg` at **1/2 scale → 320×320 RGB565** (~205 KB in PSRAM). The S3 has no hardware JPEG unit, so budget 200–400 ms of CPU — hence the dedicated task.
4. Swap into the LVGL image descriptor, keeping the previous buffer alive until the swap completes. Cross-fade over ~200 ms.
5. Cache the last N covers keyed by URL in PSRAM if you want instant redraw on back-skip. Optional, Wave 6.

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

### Wave 0 — Prove the Spotify side before touching the board *(30 min, do this first)*

Nothing in this project is worth building if the API will not control your actual playback device.

- Create the Spotify app, run `tools/spotify_auth.py`.
- Start playback on the phone/speaker you actually use, run the diagnostic.
- **Done when:** the diagnostic prints a track, a 640×640 art URL, and `PASS` on the volume test. If volume returns `403 VOLUME_CONTROL_DISALLOW`, stop and re-scope R5 before writing firmware.

### Wave 1 — Toolchain and flashing

- Install ESP-IDF v5.5.x, build and flash `hello_world` to the S3.
- **Done when:** `idf.py monitor` shows the boot log, and you have found the USB-C orientation that reaches the S3 rather than the audio ESP32.

### Wave 2 — Panel, touch, encoder

- Bring up ST77916 over QSPI, CST816 over I2C, encoder via `espressif/knob`, all through `esp_lvgl_port`.
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

- Play/pause, dial-to-skip with burst collapsing and lockout, volume mode with debounced writes, haptics, `supports_volume` gating.
- **Done when:** every control in section 5 works against the phone, a fast five-detent spin produces exactly one skip, and a 10-second volume sweep produces at most a handful of API calls (count them in the log).

### Wave 7 — Live-on-the-desk robustness

- Wi-Fi reconnect with backoff, 401/429/204/5xx handling, backlight dim after inactivity, task watchdog, panic reboot.
- **Done when:** the device survives a router reboot, a 12-hour idle period, and a forced 429 without needing a power cycle.

### Wave 8 — Serviceability

- Web config page on the device (paste a new refresh token, change Wi-Fi) and OTA update.
- **Done when:** a new refresh token can be installed without a USB cable. This is what you will need in six months, and it is much less appealing to build then.

---

## 9. Open risks

| Risk | Impact | Handling |
|---|---|---|
| Volume control refused on your playback device | R5 unbuildable | Tested in Wave 0, before any firmware |
| Pin map wrong for one or more peripherals | Half a day | Wave 2 confirms each individually against the schematic |
| Component versions incompatible with IDF 6.0 | Half a day | Wave 1 pins 5.5.x; only move up if it compiles clean |
| Rate limit hit despite the budget | Screen goes stale intermittently | `Retry-After` handling plus interval doubling, Wave 7 |
| Refresh token expiry at 6 months | Device dies silently | Wave 8 web config; calendar reminder as the interim |
| Accidental skips from knocking the knob | Daily irritation | Burst collapsing + lockout in Wave 6; quarter-turn commit as fallback |
| PSRAM fragmentation from repeated art buffers | Crash after hours | Fixed-size pre-allocated art buffers, verified in Wave 5 |

---

## 10. Current wave — step by step

> This section always describes **only the wave being worked on right now**. When the wave is done, it is deleted and replaced with the next one. Nothing accumulates here.

### Wave 0 — Prove the Spotify side

**Goal:** find out, before spending any of your time on firmware, whether the Spotify Web API will actually control the device you listen on. Specifically whether it will let you change the volume.

**You will not touch the knob hardware in this wave.** Do not plug it in. Everything happens on your PC and takes about half an hour.

**Why this is first:** Spotify refuses volume control on some playback devices. It returns a `403` and there is no workaround — it is a decision made on Spotify's side about that device. If your phone is one of them, requirement R5 has to change, and it is far better to discover that now than after Wave 6.

---

#### Step 1 — Set up the repository

Create the project folder and get this document into it.

```bash
mkdir spotify-knob
cd spotify-knob
git init
mkdir tools firmware
```

Put `BUILD.md` in the root and `spotify_auth.py` in `tools/`. You should end up with:

```
spotify-knob/
├── BUILD.md            <- this document
├── .gitignore
├── tools/
│   └── spotify_auth.py
└── firmware/           <- stays empty until Wave 1
```

Create `.gitignore` with exactly this content:

```
spotify_tokens.json
build/
managed_components/
sdkconfig
sdkconfig.old
dependencies.lock
.vscode/
```

That first line matters. The script writes your refresh token to `spotify_tokens.json`, and that token is a live credential to your Spotify account. It must never reach GitHub.

```bash
git add .
git commit -m "Wave 0: build document and Spotify auth tooling"
```

---

#### Step 2 — Create a Spotify developer app

You are not publishing anything. This just gets you a Client ID so Spotify knows which app is asking.

1. Go to **https://developer.spotify.com/dashboard** and log in with the same Spotify account you actually listen on.
2. Click **Create app**.
3. Fill in the form:
   - **App name:** `Spotify Knob` (any name works)
   - **App description:** `Desk hardware controller` (any text works)
   - **Redirect URI:** `http://127.0.0.1:8888/callback`
     Type this **exactly**, then click **Add**. One wrong character and the login will fail later with `INVALID_CLIENT: Invalid redirect URI`. It must be `127.0.0.1`, not `localhost` — Spotify treats those as different.
   - **Which API/SDKs are you planning to use:** tick **Web API** only.
4. Accept the terms and click **Save**.
5. On the app page click **Settings**. Copy the **Client ID** — a long string of letters and numbers.

You do **not** need the Client Secret. This project deliberately avoids it so that the finished device never has to store one.

Leave the app in the default **development mode**. It allows up to 25 users and needs no review from Spotify. You will never need more.

---

#### Step 3 — Install the one Python dependency

```bash
pip install requests
```

Python 3.8 or newer. Everything else the script uses is in the standard library.

---

#### Step 4 — Start music playing

Before running the script, **start playing something on the device you actually listen on** — your phone, or the speaker. Not the PC.

Leave it playing. The script needs live playback to inspect, and Spotify reports nothing at all when nothing is playing.

---

#### Step 5 — Run the script

```bash
python tools/spotify_auth.py --client-id PASTE_YOUR_CLIENT_ID_HERE
```

What happens, in order:

1. A browser tab opens on a Spotify login/consent page. It asks permission to read and control your playback. Click **Agree**.
2. The tab redirects to a page saying "Done. Close this tab and return to the terminal." Close it. (If your browser shows a connection error instead, the redirect URI in step 2 does not match — go back and fix it.)
3. The terminal prints a block containing `SPOTIFY_CLIENT_ID` and `SPOTIFY_REFRESH_TOKEN`. **Save these somewhere safe** — a password manager is ideal. They are what you will load onto the device in Wave 3.
4. The script pauses and asks you to press Enter once music is playing. It already is, so press Enter.

---

#### Step 6 — Read the diagnostic

The script prints something like this:

```
Device          : Ryan's Phone (Smartphone)
supports_volume : True
volume_percent  : 62
is_playing      : True
Track           : Radiohead - Weird Fishes
Album art sizes : 640x640, 300x300, 64x64
Largest art URL : https://i.scdn.co/image/ab67616d0000b273...

Disallowed actions on this device: ['resuming']

Testing volume control ...
PASS: volume control accepted (HTTP 204).
```

Check four things:

| Line | What you need to see | If it is wrong |
|---|---|---|
| `Device` | The phone or speaker you are listening on | You started playback in the wrong place — restart it on the right device and re-run |
| `supports_volume` | `True` | R5 is at risk. Read the failure notes below. |
| `Album art sizes` | Includes `640x640` | Note the largest size you do get; the art pipeline will be built around it |
| Volume test | `PASS` | R5 is not buildable against this device. Read the failure notes below. |

`Disallowed actions` listing `resuming` while music plays is normal — you cannot resume something already playing.

---

#### Step 7 — Record the result

Add one line to the top of this document under section 1 stating the date you ran this and whether volume passed. Commit it. That single fact drives whether Wave 6 builds a volume mode at all.

---

### Done when

All four of these are true:

- [ ] `spotify_auth.py` printed a refresh token, and you have stored it somewhere you will still be able to find in six months
- [ ] The diagnostic identified your real playback device by name
- [ ] It printed a `640x640` (or largest available) album art URL
- [ ] The volume test printed `PASS`

Then, and only then, move to Wave 1 and plug in the board.

---

### If the volume test fails

You will see `403` and a message containing `VOLUME_CONTROL_DISALLOW` or `Cannot control device volume`. This is Spotify refusing, not a bug in the script. Do not spend time debugging it.

Try this in order:

1. **Re-run against a different playback device.** Play on a Connect speaker instead of the phone, or vice versa. Support varies device by device — it is common for it to work on one and not the other.
2. **Check `supports_volume` for each device you tried.** If it is `False`, that device will never accept volume commands.

If no device you care about supports it, stop and change requirement R5 before writing firmware. The realistic replacement is that the dial's second mode seeks within the current track (scrub forward/back) rather than changing volume, which uses the always-available `seek` endpoint. Everything else in this document is unaffected.
