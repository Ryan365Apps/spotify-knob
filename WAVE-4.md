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

## Checkpoint C — Progress advances smoothly

**Pass when:** the white ring creeps forward continuously while a track plays — not in 5-second jumps — and stops when paused. (`BUILD.md`'s done condition: progress advances smoothly *between* polls.)

## Checkpoint D — Expiry survived inside the structure

**Pass when:** the log shows the forced-expiry sequence (`forced-expiry test: access token discarded` → 401 → refresh → recovered) and the screen keeps updating afterwards. This also closes **Wave 3 Checkpoint D**. The forced test is then removed and the T+55 min timer is the only refresh trigger.

## Checkpoint E — The contract audit

**PASSED 2026-09-03 (code audit, no hardware needed).** `player_state_t` appears in `spotify_app.c` and nowhere else — no Spotify *state* lives in the shell, which is `BUILD.md`'s Wave 4 done condition. `spotify_app.c` reaches the shell only through `app_shell.h` (`shell_token_get`, `shell_token_refresh_now`, `shell_auth_dead`, plus the test-only corrupt hook).

**One tension recorded, deliberately not resolved this wave.** The shell's *token module* is Spotify-specific: `SPOTIFY_TOKEN_URL`, OAuth refresh semantics, cJSON parsing of Spotify's response. That is what `BUILD.md` section 6 mandates ("token refresh stays in the shell, not in the Spotify app"), and the reason is sound — it must keep refreshing while you are looking at the Clock. But it means the shell knows one provider's auth scheme by name, which collides with the shared-core plan where the halo build swaps in a Windows media-session provider needing no OAuth at all. The clean shape is probably an auth-provider interface the shell owns and Spotify registers into. Not worth building while Spotify is the only provider; revisit when the second provider is real.

---

## Done when

- [ ] Structure boots: shell + Spotify app via `knob_app_t`, skeleton rendered (Checkpoint A)
- [ ] Track change on the phone updates the screen within one poll (Checkpoint B; closes Wave 3 C)
- [ ] Progress ring advances smoothly between polls (Checkpoint C)
- [ ] Forced token expiry survived in the app structure (Checkpoint D; closes Wave 3 D)
- [x] No Spotify state in the shell (Checkpoint E, 2026-09-03)
- [ ] **Committed** — the whole run from Wave 2 Checkpoint A to here, with no `build/`, `managed_components/`, `spotify_tokens.json` or `secrets_local.h` in the commit
- [ ] WAVE-3.md and this file deleted, results folded into `BUILD.md`
