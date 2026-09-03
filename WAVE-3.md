# Wave 3 — Network and auth

The current wave, expanded from `BUILD.md` section 8. When it is done, results are written back into `BUILD.md` and this file is deleted (Wave 2's record went the same way — its findings live in `BUILD.md` sections 3, 8 and 9).

**Goal:** the board on Wi-Fi, holding a live Spotify session on its own: TLS to Spotify's servers, the refresh token in NVS, an access token that renews itself, and one real playback query working end to end. Plus one deliberately early de-risk: a QR code on the panel.

**Who does what.** Same as Wave 2: Claude writes all code into `firmware/knob/` — Ryan never edits a source file, with one exception in step A1 where he types his Wi-Fi name and password into a gitignored secrets file (they must not pass through chat). Steps are **Already done** / **Info** / **Claude:** (code, marked *landed* when in the repo) / **You:** (a command or action plus the one thing to look at) / **Pass when:** (the observable result required before the next step).

**Standing facts for the whole wave:**

- Run every command from the **ESP-IDF 5.5 PowerShell** shortcut, in `D:\Projects\PROD\spotify-knob\firmware\knob`.
- **The re-flash loop, in full, every time:** press `Ctrl+]` in the terminal to kill the running monitor, then run `idf.py -p COM7 flash monitor`, then look at whatever the step says to look at. Board direct into a rear USB-A port — never the monitor's hub.
- **No secret ever appears in a log, in chat, or in git.** The refresh token, access token and Wi-Fi password are never printed — log lines say that a thing happened, never what the value was. `spotify_tokens.json` and the new `secrets_local.h` are gitignored.
- The Spotify credentials already exist on disk from Wave 0: the Client ID in `notes.md`, the refresh token in `spotify_tokens.json` (minted 2026-08-31, dies ~2027-02-27).
- Wave 2's dial/touch test UI stays on screen through A–D (it is harmless); checkpoint E replaces it with the QR test.

---

## Checkpoint A — On the network

**Info:** credentials live in NVS (non-volatile storage — the flash key-value store), per `BUILD.md` section 6. Wave 9 later gives them a proper provisioning flow; this wave seeds them from a compiled-in secrets header that exists only on this PC. On boot the firmware checks NVS; if the keys are missing it writes them from the header and says so in the log.

### A1 — the secrets file

**Claude:** *landed 2026-09-02* — gitignored `firmware/knob/main/secrets_local.h` (Wi-Fi fields blank for Ryan; Spotify fields generated locally from `spotify_tokens.json`/`notes.md` without passing through chat; verified invisible to `git status`), the `.gitignore` entry, and the NVS-seeding code in `main.c`.

**You:** open `firmware/knob/main/secrets_local.h` in the editor and fill in the two Wi-Fi fields — the network name and password, exactly as your phone joins them. Save. Then run `git status` and confirm `secrets_local.h` does **not** appear in it.

**Pass when:** both Wi-Fi fields are filled and `git status` does not list the file.

### A2 — join the network

**Claude:** *landed 2026-09-02* — Wi-Fi STA (station mode) bring-up: seed-if-missing NVS, connect with 2 s retry, IP logged on join.

**PASSED 2026-09-03** — `wifi connected, ip 192.168.86.41`, WPA2, channel 6. Three findings from getting there:

1. **The SSID has a trailing space** (`"Living room "`) — invisible in the header, found by the scan-on-failure diagnostic that now lives in the firmware (after three failed joins it logs every visible 2.4 GHz network with channel and RSSI). Disconnect reason 201 = network not found; 15/204 = bad password.
2. **NVS re-seeds whenever `secrets_local.h` differs** — the original seed-only-if-empty logic silently ignored corrections. Wave 9 replaces this with NVS-as-sole-truth.
3. **The default system event task stack (2304 bytes) overflowed** once the Wi-Fi handlers ran — crashed on the first disconnect. Raised to 4096 in `sdkconfig.defaults`; scan records made static. Event handlers must stay small and never block.

---

## Checkpoint B — A token of its own

**Info:** the refresh flow is `POST https://accounts.spotify.com/api/token` with the refresh token and Client ID (PKCE public client — no secret). TLS trust comes from the mbedTLS certificate bundle already enabled in `sdkconfig.defaults`. Two rules from `BUILD.md` section 6 apply from the first line: the response **may or may not** contain a new refresh token — if it does, it is written to NVS before use, and if not the old one is kept (getting this wrong kills the device weeks later); and a `400 invalid_grant` means the token is dead — no retry, ever.

**Claude:** *landed 2026-09-03* — the token module: refresh from a dedicated network task started on the first IP (never in an event handler), exponential backoff on transient failures, rotation into NVS, `invalid_grant` stops dead. Log lines report success and the `expires_in` figure only.

**You:** the re-flash loop.

**Pass when:** the log shows the TLS connection succeeding and a line equivalent to `token refreshed, expires_in 3600` — with no token text anywhere in the output.

---

## Checkpoint C — Ask Spotify something real

**Info:** the target is `GET https://api.spotify.com/v1/me/player` — the endpoint the whole product polls. It returns 200 with JSON when something is playing, 204 with an empty body when nothing is. Both are correct results.

**Claude:** *landed 2026-09-03, together with D* — a 5-second poll loop in the network task: bearer-token GET into a 16 KB PSRAM buffer, cJSON parse, one log line with track, artist, volume and play state; a distinct line for 204 idle; 401 triggers a refresh and carries on.

**You:** start some music on any of your Spotify devices (phone or desktop), then the re-flash loop. Once it's printing, change tracks and watch the next poll pick it up. Also pause everything and confirm the idle line appears.

**Pass when:** the log prints the correct current track name and volume, updates on a track change, and reports idle correctly when nothing plays.

---

## Checkpoint D — Survive a token expiry

**Info:** `BUILD.md`'s done condition requires the poll to keep working after the access token has expired and been refreshed once — verified by forcing it, not by waiting an hour. The firmware fakes the expiry: after the first successful poll it deliberately discards the in-RAM access token, refreshes again, and polls again, logging each stage.

**Claude:** *landed 2026-09-03, in C's flash* — after the first successful poll the in-RAM access token is overwritten once; the next poll 401s, refreshes, and recovers. Log lines: `forced-expiry test: access token discarded` → `access token rejected (401) - refreshing` → `forced-expiry test: recovered`. Removed (made time-based) in Wave 4.

**You:** covered by C's flash — one flash tests both checkpoints.

**Pass when:** the log shows the full sequence and the second poll prints the same correct track data as the first.

---

## Checkpoint E — The QR spike

**Info:** Wave 9's whole config story assumes a scannable QR on this panel. Five lines now de-risk it: render one `lv_qrcode` at 198 px carrying the longest realistic payload — the Mode A Wi-Fi join string `WIFI:T:WPA;S:Radial-XXXX;P:<derived-password>;;` (`BUILD.md` section 6). If a version-3 code doesn't scan at that size, that is a layout problem worth finding now.

**Claude:** *landed 2026-09-03* — dial test screen replaced by a 198 px `lv_qrcode` (black-on-white modules on the black screen) carrying `WIFI:T:WPA;S:Radial-4F2A;P:9f3a7c21b8d4;;`; `CONFIG_LV_USE_QRCODE` enabled in `sdkconfig.defaults`. Landed out of order while Checkpoint C/D sit out a Spotify rate-limit penalty (429 with `Retry-After 39037 s` ≈ 10.8 h — an account-level dev-mode quota penalty, suspected cause a Live-mode simulator tab; the firmware now honours Retry-After instead of polling through it).

**PASSED 2026-09-03.** Phone camera recognised the 198 px code at arm's length and offered the join-network action. Wave 9's config-screen layout assumption holds.

---

## Done when

- [ ] Board joins Wi-Fi from NVS-stored credentials; nothing secret in git or the log (Checkpoint A)
- [ ] Access token refreshes over TLS; rotation and `invalid_grant` rules implemented (Checkpoint B)
- [ ] `GET /me/player` prints correct track name and volume, and handles 204 idle (Checkpoint C)
- [ ] Poll still correct after a forced token expiry and refresh (Checkpoint D)
- [x] A 198 px `lv_qrcode` scans first try from arm's length (Checkpoint E, 2026-09-03)
- [ ] Committed — including the still-uncommitted Wave 2 work — with no `build/`, `managed_components/`, `spotify_tokens.json` or `secrets_local.h` in the commit
- [ ] Results written back into `BUILD.md` and this file deleted
