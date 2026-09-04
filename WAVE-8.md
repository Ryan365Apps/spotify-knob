# Wave 8 — Live-on-the-desk robustness

The current wave, expanded from `BUILD.md` section 8. When it is done, results are written back into `BUILD.md` and this file is deleted — the process Waves 2 through 7 all followed.

**Goal:** the device survives the ordinary bad days without anyone touching it. The router reboots, Spotify has a moment, something wedges — and the knob is correct again afterwards with no power cycle and no explanation required.

**Who does what.** Unchanged. Claude writes every line of firmware and compile-checks before handing over a flash; Ryan runs the flash and reports what the hardware and the log do. The board is on his desk.

**Steps are marked** *Already done* / *Info* / *Do + Pass when*, the format Waves 3 to 7 used.

**The re-flash loop, in full.** The ESP-IDF 5.5 PowerShell shortcut opens in the IDF install directory and `idf.py` builds whichever directory it is standing in, so the `cd` is not optional:

```powershell
cd D:\Projects\PROD\spotify-knob\firmware\knob
idf.py -p COM7 flash monitor
```

`Ctrl+]` first if a monitor is already running. Board on COM7, rear USB-A port, never the monitor's hub. If it will not connect, flip the USB-C plug at the board end before debugging anything else.

**This wave is mostly waiting.** Four small pieces of code, all of which have landed, and then three soaks that take a router reboot, an evening, and a decision about whether the third is worth its cost.

---

## Checkpoint A — What was already standing

**Info, no work.** Most of Wave 8 arrived as a side effect of Waves 3 to 7. Recording it so the bench time goes on what is actually missing:

| Behaviour | State before this wave |
|---|---|
| 204, nothing playing | Working — a distinct idle state, and a 10 s poll interval |
| 401 with token refresh | Working — proven by a forced expiry, since by real ones |
| 429 with `Retry-After` | Working — honoured rather than polled through, with a rate-limited screen that says how long |
| Token refresh backoff | Working — exponential, and a `400 invalid_grant` stops dead |
| Wi-Fi reconnect on disconnect | Working, but retrying flat out |
| Backlight sleep after inactivity | Working — `screen off (10 min idle)` seen on hardware |

Four things were genuinely missing: **5xx handling, backoff on the Wi-Fi reconnect, the task watchdog, and panic reboot.** All four have now landed and are covered below.

---

## Checkpoint B — 5xx and transport failures back off

**Claude:** *landed 2026-09-04, build clean — `knob.bin` 0x19bfc0, 60% of the app partition free, no warnings.*

`main/spotify_app.c` gained one backoff shared by two paths that were both retrying at full speed:

- **A 5xx from Spotify.** Previously it fell into the generic `poll HTTP %d` line and the loop carried on at three seconds. Now it doubles 2 s, 4 s, 8 s … to a 60 s ceiling and resets on the first clean response.
- **A transport failure** (`poll unreachable`) — the same class of problem seen from the other end, and previously the same flat-out retry. Same backoff.

Three decisions inside it worth knowing:

1. **The last known state stays on the screen.** A 500 from Spotify says nothing at all about what is playing, so blanking the screen would be the device inventing bad news. The "unavailable, retrying in *N* s" message appears **only** when there is no track to show in the first place — a cold boot into an outage.
2. **A 5xx releases the HTTP handle.** A 502 or 503 usually comes from an edge that is about to drop the connection anyway, and the next attempt is seconds away, so the handshake it costs is free. This is the same reasoning that already releases the handle on an incomplete response.
3. **A 5xx on a control command drops the command rather than retrying it.** Re-sending a skip a minute later would skip a track the listener has since chosen for themselves.

**Info — the backoff does not block an app switch.** `poll_wait` breaks its wait into 20 ms slices and exits on `s_active` going false, so leaving Spotify during a 60 s backoff still tears down within 20 ms. A transport button pressed during a backoff also cuts the wait short, which is right: a person pressing a button is an explicit "try now".

**Do:** nothing on its own. This checkpoint is verified inside Checkpoint E's router-reboot soak, which exercises the transport-failure path through the same backoff function. A genuine 5xx cannot be forced from here without pointing the firmware at a broken host, so the 5xx branch is verified by construction and by its log line — `Spotify NNN - retrying in N ms` — if one ever appears.

**Pass when:** pulling the network produces `poll unreachable - retrying in 2000 ms`, then 4000, 8000, and so on up to 60000 rather than a line every three seconds; and the intervals reset to 2000 after the network comes back.

---

## Checkpoint C — Wi-Fi reconnects with backoff

**Claude:** *landed 2026-09-04, in the same build.*

`main/main.c` no longer calls `esp_wifi_connect()` straight back on every disconnect.

- **The first retry stays immediate**, because a momentary blip should not cost a second.
- After that it doubles 1 s, 2 s, 4 s … to a 30 s ceiling.
- **An IP arriving resets it**, so the next outage starts from an immediate retry again rather than from wherever the last one left off.

**Info — the retry is scheduled, not slept for.** It runs on a one-shot `esp_timer` rather than a delay inside the handler, because the handler lives on the system event task. Wave 3 already overflowed that task's stack, and a handler that blocks stalls every other event queued behind it. The rule from that wave still holds: event handlers stay small and never block.

**Info — the scan diagnostic now repeats.** It fired on the third failure *ever*; it now fires on every third consecutive failure and resets on a successful join. A device that has been up for a month and then loses its router deserves the same diagnostic a fresh one gets.

**Info — an IP arriving cancels the Spotify backoff too.** By the time the router is back, the poll backoff from Checkpoint B has usually grown to its 60 s ceiling, and without this the screen would stay stale for up to a minute after the network returned. The shell now publishes `shell_net_generation()` — a counter bumped on every IP acquisition — and the poll loop's wait breaks out when it changes. The seam holds: the shell says *the network changed*, not *re-poll Spotify*.

**Do:** reboot the router while the device is running and watch the log.

**Pass when:** the retry intervals visibly lengthen — `wifi retry in 0 ms`, then 1000, 2000, 4000 and upward, capping at 30000 — instead of a constant stream of attempts; the network scan appears every third consecutive failure; and the device rejoins on its own and resumes polling, with no power cycle, once the router is back. `network back - dropping the poll backoff` should follow the `wifi connected, ip ...` line within a fraction of a second, and the correct track should be on screen a moment after that rather than up to a minute later.

---

## Checkpoint D — The watchdog bites, and the device says why

**Claude:** *landed 2026-09-04, in the same build.*

**Info — the task watchdog was never absent, it was toothless.** It was already initialised and already watching the idle task on both cores; that is exactly what caught the first bloom implementation starving LVGL on 2026-09-03. But `CONFIG_ESP_TASK_WDT_PANIC` was off, so all it did was print a backtrace every few seconds while the device stayed wedged. Three changes:

- **`CONFIG_ESP_TASK_WDT_PANIC=y`** — a wedge now panics, and the panic handler reboots. A wedge costs a reboot rather than a power cycle.
- **`CONFIG_ESP_TASK_WDT_TIMEOUT_S=10`**, raised from 5, so only a genuine wedge trips it. The longest single piece of work in this firmware is a JPEG decode at 140–220 ms, so ten seconds is two orders of magnitude of headroom.
- **`CONFIG_ESP_SYSTEM_PANIC_REBOOT_DELAY_SECONDS=1`**, so the backtrace reaches the serial monitor before the chip resets. With no delay the tail of it is lost, and the tail is the part worth having.

Both `sdkconfig.defaults` and the live `sdkconfig` carry these. `sdkconfig` is gitignored and is **not** regenerated from the defaults file once it exists, so anything set only in the defaults would not have reached this build.

**The shell's own loop is now subscribed too.** The idle tasks catch starvation; a subscribed shell loop catches the other shape of failure — the idle tasks running happily while the shell has stopped ticking, which is what a deadlock on the LVGL lock would look like. That loop sleeps a second at a time and does tens of milliseconds of work, so ten seconds is comfortable.

**And the device now names its last reset on every boot.** A device that reboots on its own and comes back looking fine is a device that is hiding something, and a twelve-hour soak is unreadable without this line. It is also the only honest way to tell a panic reboot from someone pulling the cable. A fault reads at error level, everything else at info.

**Do:** flash, and read the first few lines. Then pull the USB cable and plug it back in, and read them again.

**Pass when:** the boot log carries `last reset: software restart` immediately after a flash and `last reset: power-on` after a cable pull. Anything reading `PANIC`, `TASK WATCHDOG` or `BROWNOUT` at error level during this wave is a finding to record here, not a line to ignore.

*(The panic-reboot path itself is proven opportunistically rather than by a deliberate crash: any fault during the soaks below must show as the named reason on the next boot rather than as a silent restart. If it is worth proving deliberately, say so and a temporary hook can be added for one flash and then removed — it should not ship.)*

---

## Checkpoint E — The three soaks

This is where the wave's time actually goes. Two of the three are unattended.

### E1 — Router reboot

**Do:** with music playing and the device on the NOW PLAYING screen, reboot the router. Leave the device alone. When the router is back, leave it a further few minutes.

**Pass when:** the device rejoins on its own, resumes polling, and shows the correct track again — with no power cycle, no reflash, and no wedge. The log shows lengthening Wi-Fi retries during the outage, lengthening poll backoff behind them, and both resetting afterwards. This closes Checkpoints B and C together.

### E2 — Twelve hours idle

**Do:** leave the device powered and untouched overnight, with the monitor running and logging.

**Pass when:** it is still correct in the morning; heap and PSRAM are on the same figures as at the start; `last reset` at the top of the log is still the only reset in the log; and the screen slept and woke as configured. Anything the token refresh did at T+55 min and every hour after should be visible and uneventful.

### E3 — A forced 429

**Info, and this one needs a decision.** `BUILD.md`'s done condition asks for a forced 429. That path has already been survived live: on 2026-09-03 the developer account earned a 429 carrying an 11-hour `Retry-After`, the device honoured it rather than polling through, showed an honest rate-limited screen with a countdown, and recovered on its own when the penalty expired — no power cycle.

Deliberately earning another one costs **hours of a dead device** for no new information, and the quota is per developer account and shared with the simulator, so it also takes `design/simulator.html` down with it.

**The recommendation is to take the 2026-09-03 event as the evidence and not re-earn one.** Ryan's call.

---

## Also on the bench while it is sitting there

Three things from Wave 6 (controls) were never confirmed specifically on glass, and the board will be in front of Ryan anyway:

- **One skip from a fast five-detent spin.** Spin the dial five detents quickly on NOW PLAYING and count the skips in the log. Exactly one.
- **A 10-second dial sweep, counted.** Sweep the dial continuously for ten seconds in the second dial mode and count the API calls in the log. A handful, not one per detent — the 400 ms write debounce is what makes that true.
- **The CONTROLS chips and the 5 s auto-return.** Tap into CONTROLS, then leave it alone: it should return to NOW PLAYING after five seconds. SEEK should make the next dial gesture amber and the one after it green again. VOLUME should be grey while the phone is the active device and lit when the desktop is.

---

## Done when

- [x] 5xx and transport failures back off rather than retrying flat out (Checkpoint B, code landed 2026-09-04)
- [x] Wi-Fi reconnect backs off, resets on an IP, and re-runs its scan diagnostic (Checkpoint C, code landed 2026-09-04)
- [x] Task watchdog panics, the panic reboots, and the boot log names the last reset (Checkpoint D, code landed 2026-09-04)
- [ ] Router reboot survived without a power cycle (E1)
- [ ] Twelve hours idle survived, heap and PSRAM unmoved (E2)
- [ ] 429 — settled either by the 2026-09-03 evidence or by a forced one (E3)
- [ ] The three Wave 6 items confirmed on glass
- [ ] Results folded back into `BUILD.md` and this file deleted
