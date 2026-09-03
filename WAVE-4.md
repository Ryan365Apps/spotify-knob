# Wave 4 — App shell, and Spotify inside it

**Started early 2026-09-03**, while Wave 3's Checkpoints C and D sit out the Spotify rate-limit penalty. Wave 3 is not closed: its C/D verification and the wave commit both remain, and both are folded into this wave's checkpoints below (the same log lines prove them). One wave doc at a time resumes when this one closes.

**Goal (from `BUILD.md` section 8):** the `knob_app_t` app contract, a shell that owns Wi-Fi and the token, and Spotify written as an app from the first line — even though it is the only one. Poll loop, `player_state_t`, title/artist/progress/volume rendered. No art (Wave 5), no selector (Wave 7).

**Who does what.** As before: Claude writes all code; Ryan runs the re-flash loop (`Ctrl+]`, then `idf.py -p COM7 flash monitor`) and reports what the hardware and log do. ESP-IDF 5.5 PowerShell, `firmware\knob`, board on COM7 direct into a rear USB-A port.

**Claude can compile-check before handing over a flash** (added 2026-09-03, saves Ryan a cycle on typos), from any PowerShell:

```powershell
$env:IDF_TOOLS_PATH='C:\Espressif'
$env:IDF_PYTHON_ENV_PATH='C:\Espressif\python_env\idf5.5_py3.11_env'
& 'C:\Espressif\frameworks\esp-idf-v5.5.5\export.ps1' | Out-Null
cd D:\Projects\PROD\spotify-knob\firmware\knob; idf.py build
```

Both environment variables are required: without them `export.ps1` looks for a `py3.14` venv under `~\.espressif` that does not exist. Flashing stays with Ryan — the board is on his desk.

**The architectural rules being enforced this wave** (`BUILD.md` section 6): the shell owns Wi-Fi, token refresh, haptics, the dial dispatch and the tick; apps own their screen, their network calls, and their buffers, and free them on exit. `player_state_t` belongs to the Spotify app, never the shell, and is written behind the provider seam — nothing above it mentions Spotify, HTTP or JSON.

---

## Checkpoint A — The structure stands

**Claude:** the restructure —

- `main/app_shell.h`: the `knob_app_t` contract verbatim from `BUILD.md` section 6, plus the shell's token API (`shell_token_get`, `shell_token_refresh_now`).
- `main/spotify_app.c`: the Spotify provider and screen. `player_state_t` under a mutex; a poll task started by `on_enter` and stopped by `on_exit`; the NOW PLAYING skeleton — thin white progress ring around the bezel, centred title (marquee when overflowing), artist below, volume in green below that, a distinct idle state for 204.
- `main.c` becomes the shell: hardware bring-up, Wi-Fi, the token module (refresh on boot, at T+55 min, and on demand), haptic click + dial dispatch to the active app, 1 Hz tick. The Wave 3 QR test screen and the old log-only poll loop are retired; the forced-expiry test moves into the Spotify app's first poll so Wave 3 Checkpoint D can still be verified from this build.

**Build verified clean 2026-09-03** — `knob.bin` 0x155bf0 bytes, 67% of the app partition free.

**You:** the re-flash loop.

**Pass when:** it boots; the screen shows the NOW PLAYING skeleton (thin ring at the bezel, `connecting...` then `nothing playing` while the rate limit holds); dial clicks still fire haptics; the log shows the shell bringing up hardware, `shell up, app 'Spotify' active`, and the Spotify app's poll task running (429 lines are expected tonight).

## Checkpoint B — Live data (needs the rate limit expired)

**You:** with music playing, power the board and watch screen + log. Change tracks on the phone.

**Pass when:** title, artist and volume on screen are correct and a track change appears within one poll (~5 s). Pausing everything shows the idle state. This also closes **Wave 3 Checkpoint C**.

## Checkpoint B result — **PASSED 2026-09-03**

Once the rate limit expired: `now playing: 'Workhorse' by All Them Witches | volume 100% | playing`, polling steadily every ~5 s. This closes **Wave 3 Checkpoint C** too.

**And R5 chose correctly without being told.** The first dial gestures produced `seek -> HTTP 200`, not volume — the active device reports `supports_volume: false`, exactly the Wave 0 finding, so the dial fell back to seek at runtime rather than sitting inert. The runtime choice is real, not a compiled assumption.

## The connection-per-poll leak — found and fixed 2026-09-03

**The evidence.** Heap telemetry every 30 s, with Spotify active throughout:

| t | internal free | largest block |
|---|---|---|
| 124 s | 70023 | 31744 |
| 154 s | 33739 | 25600 |
| 184 s | 20243 | 10752 |

About **6 KB lost per poll**, steadily, and the largest block collapsing with it. Everything downstream was a symptom of that and nothing more: hardware AES failing to allocate, then `PK verify failed` / `Certificate matched but signature verification failed`, which look alarming and are really `Dynamic Impl: alloc(4437 bytes) failed` wearing a disguise. **Certificate errors on a device that was verifying certificates happily a minute earlier mean memory, not trust.**

**The cause** was building and tearing down an `esp_http_client` for every poll — a fresh TLS handshake every 5 s, visible as a `Certificate validated` line each time, and something in that cycle did not fully release.

**The fix:** one client for the life of the active app. The handle is created on first use, reused for polls and control calls alike, and released whenever the app goes inactive or a transport error occurs, so the next attempt starts clean. An unread response body is drained, and a response that did not complete releases the handle rather than leaving the stream out of step. The TLS session survives between requests, so a poll is now one request rather than a whole handshake — cheaper in memory, CPU and latency at once.

This is the change that had been deferred a run earlier as "the likely proper fix, deliberately not attempted while the cause is still a hypothesis". The telemetry turned it into a measurement, and then it was worth doing.

**It was not the leak.** Connection reuse worked exactly as intended — one `Certificate validated` for a whole session instead of one every five seconds — and the heap still fell at the same 5–7 KB per *request*:

| t | internal free | DMA free |
|---|---|---|
| 66 s | 79539 | — |
| 93 s | 41943 | 34155 |
| 123 s | 5323 | 13547 |

So the cost was never the handshake or the client handle. It was the request cycle itself. Connection reuse is kept regardless: it is correct, and it removes a handshake every five seconds.

## Suspected and cleared: dynamic mbedTLS buffers — 2026-09-03

The failing allocation had been naming the culprit the whole time and it took three readings to notice: `Dynamic Impl: alloc(4437 bytes) failed`. **`Dynamic Impl` is `CONFIG_MBEDTLS_DYNAMIC_BUFFER`'s own allocator**, and 4437 bytes is the size that went missing per request.

That option exists to save RAM by allocating TLS buffers only while they are in use. Against this workload — one long-lived connection, a request every few seconds — the buffers were not coming back. It is now **off**. Fixed buffers cost more at rest and cost the *same* at rest forever, which is the trade a device that holds one connection for days should take.

`sdkconfig.defaults` carries the reasoning so nobody re-enables it to save memory and quietly reintroduces this. The check that settles it is free heap over ten minutes, not over ten seconds.

**This was not the leak either.** `Dynamic Impl` named the allocator that *failed*, not the one that lost the memory — with something else eating internal RAM at 5-7 KB every five seconds, whatever allocated next was going to fall over, and the dynamic-buffer allocator ran on every request so it was always first in the queue. The option stays off regardless: fixed buffers are the right trade for one connection held for days, and changing it back now would mean testing two variables at once.

**A note on reading these failures.** `PK verify failed`, `Certificate matched but signature verification failed`, `Failed to verify certificate` — three lines that all point at TLS trust, on a device that had been verifying the same certificate happily a minute earlier. They were all malloc failures wearing a disguise. When certificate errors appear *after* a period of correct operation, suspect memory before trust.

## The actual leak: the parsed player response — 2026-09-03

`state_from_json` in `main/spotify_app.c` called `cJSON_Parse` on every poll and never called `cJSON_Delete`. One whole parsed tree lost every five seconds.

The size matches the measurement exactly. A Spotify `/me/player` response is several KB of JSON, and cJSON turns it into a few dozen small nodes plus a `strdup` of every string. With `CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=16384`, every allocation under 16 KB comes out of **internal** RAM, so the whole tree lands in the scarcest pool on the board. That is the 5-7 KB per request, and it is why PSRAM sat untouched while internal RAM emptied.

It also explains why the first fix changed nothing. HTTP connection reuse was correct and worth having, but the leak was never in the HTTP client — it was in what the caller did with the body afterwards. The token-refresh path in `main.c` parses the same way and *does* delete on both exits, which is why an hourly refresh never showed the problem and a five-second poll emptied the device in two minutes.

Fixed by deleting the tree at the end of the function. Every field is copied into `s_state` before that point, so nothing borrows a pointer into it.

**Verified on hardware 2026-09-03.** Nine minutes of continuous polling, roughly ninety requests, three track changes:

```
I (32082)  torque-os: heap: 68659 internal (31744 largest), 60871 DMA (31744 largest), 8368060 PSRAM
I (152573) torque-os: heap: 68699 internal (31744 largest), 60911 DMA (31744 largest), 8368060 PSRAM
I (333311) torque-os: heap: 68699 internal (31744 largest), 60911 DMA (31744 largest), 8368060 PSRAM
I (513946) torque-os: heap: 68699 internal (31744 largest), 60911 DMA (31744 largest), 8368060 PSRAM
```

Net movement across the whole run: **+40 bytes**. Largest free block never moved off 31744. Two samples dipped (68643, then 67099 with PSRAM down 168 bytes) and both came straight back, which is an allocation in flight at sample time, not a loss. For comparison, the leaking build fell about 6 KB per poll and would have been at zero well before the second heap line.

One `Certificate validated` for the session, at 17 s, so connection reuse is holding too.

## Superseded — the first response to the TLS failure

```
E (160905) esp-aes: Failed to allocate memory
E (160906) esp-tls-mbedtls: read error :-0x0001
W (160911) spotify: poll HTTP -1
```

Every poll opens a fresh HTTPS connection — a full handshake every 5 s, visible as a `Certificate validated` line each time — and one of them could not allocate. `CONFIG_MBEDTLS_DYNAMIC_BUFFER` was already enabled, so this is headroom, not configuration.

First move, in this build: the LVGL draw buffers were 1/10 of the screen, double-buffered, in internal DMA-capable RAM — 52 KB of the scarcest memory on the board. Cut to 1/18, giving 23 KB back for a few more flush chunks per frame. Heap telemetry now prints every 30 s with the largest free block, because a steady figure means fragmentation or a high-water mark and a falling one means a leak, and those want different fixes.

**Not yet done, and the likely proper fix:** reuse one HTTP client across polls instead of building and tearing one down every five seconds. That removes the repeated handshake entirely — cheaper in memory, CPU and latency. Deliberately not attempted while the cause is still a hypothesis; the telemetry decides.

## Checkpoint C — Progress advances smoothly

**Pass when:** the white ring creeps forward continuously while a track plays — not in 5-second jumps — and stops when paused. (`BUILD.md`'s done condition: progress advances smoothly *between* polls.)

**PASSED 2026-09-03.** The ring creeps smoothly. Local interpolation in `progress_now` is doing its job and the poll interval is invisible while a track plays.

**One artifact observed, and it is inherent rather than a defect.** Pausing *from the phone* makes the ring overshoot by about two steps and then snap back; resuming leaves it frozen for a moment and then jumps forward to catch up. Both are the same thing: the device holds the last polled position and adds elapsed time locally, so for up to one poll interval it is confidently wrong about a change it has not heard about yet. The correction arrives with the next poll.

Spotify offers no push channel for playback state, so the only lever is the poll interval, and `BUILD.md` section 6 rules out polling faster to smooth the bar. Accepted as-is. **Wave 6 removes the common case**: once play/pause is on the device, the device initiates the change and can apply it optimistically, leaving the artifact visible only when playback is controlled from somewhere else.

*Optional, not built:* easing to the polled value over ~300 ms when it disagrees with the interpolated one. It would not remove the phantom progress, only make the correction read as deliberate. That is an interaction change, so it goes through `design/simulator.html` first, which means after the rev W → rev X screens session releases `design/screens.html`.

## Checkpoint D — Expiry survived inside the structure

**PASSED 2026-09-03.** The full sequence ran on hardware: `forced-expiry test: access token discarded` → `access token rejected (401) - asking shell to refresh` → `token refreshed, expires_in 3600`. This closes **Wave 3 Checkpoint D** too. The forced test has been removed; the T+55 min timer and any real 401 are now the only refresh triggers.

## Checkpoint E — The contract audit

**PASSED 2026-09-03 (code audit, no hardware needed).** `player_state_t` appears in `spotify_app.c` and nowhere else — no Spotify *state* lives in the shell, which is `BUILD.md`'s Wave 4 done condition. `spotify_app.c` reaches the shell only through `app_shell.h` (`shell_token_get`, `shell_token_refresh_now`, `shell_auth_dead`, plus the test-only corrupt hook).

**One tension recorded, deliberately not resolved this wave.** The shell's *token module* is Spotify-specific: `SPOTIFY_TOKEN_URL`, OAuth refresh semantics, cJSON parsing of Spotify's response. That is what `BUILD.md` section 6 mandates ("token refresh stays in the shell, not in the Spotify app"), and the reason is sound — it must keep refreshing while you are looking at the Clock. But it means the shell knows one provider's auth scheme by name, which collides with the shared-core plan where the halo build swaps in a Windows media-session provider needing no OAuth at all. The clean shape is probably an auth-provider interface the shell owns and Spotify registers into. Not worth building while Spotify is the only provider; revisit when the second provider is real.

---

## Done when

- [x] Structure boots: shell + Spotify app via `knob_app_t`, skeleton rendered (Checkpoint A, 2026-09-03)
- [x] Track change on the phone updates the screen within one poll (Checkpoint B, 2026-09-03; closes Wave 3 C)
- [x] Progress ring advances smoothly between polls (Checkpoint C, 2026-09-03)
- [x] Forced token expiry survived in the app structure (Checkpoint D, 2026-09-03; closes Wave 3 D)
- [x] No Spotify state in the shell (Checkpoint E, 2026-09-03)
- [x] Free internal RAM flat over ten minutes of polling (the memory hunt, 2026-09-03)
- [ ] **Committed** — the whole run from Wave 2 Checkpoint A to here, with no `build/`, `managed_components/`, `spotify_tokens.json` or `secrets_local.h` in the commit
- [ ] WAVE-3.md and this file deleted, results folded into `BUILD.md`
