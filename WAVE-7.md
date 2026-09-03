# Wave 7 — The Clock, the timer, and the selector

**Started 2026-09-03**, out of order and deliberately. Wave 4's remaining checkpoints (B, C and D) all need live Spotify data, and the developer account is sitting out an 11-hour rate-limit penalty earned by forgotten simulator tabs. This wave needs no network at all, so it is the work that fits the blocked evening.

Wave 4 is not closed. Its Checkpoints B, C and D still stand and resume the moment the quota does.

**Goal (from `BUILD.md` section 8):** the Clock app written against `knob_app_t` without touching shell code, and the radial selector — long-press to open, dial to rotate, tap to enter, returning to where you came from. Settings is the third part of Wave 7 and is **not** in this pass; it wants the ring mechanic proven first.

**Why the Clock is the real test.** `BUILD.md` section 6 says it plainly: if the Clock cannot be written against the app contract without changing shell code, the contract is wrong and a third app will break it too. That is the condition this wave exists to check, and it is checkable by reading the diff before the board is even plugged in.

**Who does what.** Unchanged: Claude writes all code and compile-checks it; Ryan runs the re-flash loop and reports what the hardware does. Board on COM7 in a rear USB-A port, never the monitor's hub.

**The re-flash loop, in full.** The ESP-IDF 5.5 PowerShell shortcut opens in the IDF install directory, and `idf.py` builds whichever directory you are standing in — so the `cd` is not optional, and without it cmake refuses with "Current directory is not buildable":

```powershell
cd D:\Projects\PROD\spotify-knob\firmware\knob
idf.py -p COM7 flash monitor
```

`Ctrl+]` first if a monitor is already running.

---

## What landed

**Claude:** *landed 2026-09-03, build verified clean — `knob.bin` 0x175570 bytes, 64% of the app partition free, no warnings.*

- `main/clock_app.c` — the Clock app. The phyllotaxis bloom on a 259 KB PSRAM canvas allocated in `on_enter` and freed in `on_exit`, the time in Montserrat 48, and the timer: turning the dial enters winding, one detent per minute, clamped 0–60, committing two seconds after the last detent. A running timer rides the rim as a white arc with the remaining time beneath the clock.
- `main/selector.c` — the app selector, on LVGL's top layer so the app underneath is never torn down just because you looked at the ring. One green dot above twelve, glyph falloff by angular distance, cumulative rotation that never rewinds at the wrap, and a critically-damped chase toward the target angle. Tap a glyph to enter it directly, tap the centre for the selected one, chevron or long-press or 4 s idle to leave.
- `main/app_shell.h` — three new shell services, all of them things the shell already owns: haptics (`shell_haptic_click`, `shell_haptic_firm`), the timer (`shell_timer_set` and friends), and the app registry with `shell_switch_to`.
- `main.c` — the shell grew an app registry, screen switching, SNTP (the Clock app has nothing to show without it), the alarm overlay, and an **input task**.

**Three things worth knowing about the shell changes:**

1. **Dial events now go through a queue to an input task.** They arrive on the esp_timer task, which is also where the dial's own polling runs. Doing the haptic I2C write and the LVGL work there would stall that task — a bloom render can hold the LVGL lock for tens of milliseconds — and the stall would cost detents. This is `BUILD.md` section 6's `input_task`, arriving because the hardware demanded it.
2. **The timer belongs to the shell, not the Clock app.** Section 6 already gives the shell the clock; a timer that stopped counting when you left the Clock app would be useless, and it has to fire wherever you are. The Clock app is its UI. Same split as the token and the Spotify app.
3. **The Spotify poll task is now persistent**, idling on a semaphore when the app is inactive rather than being created and destroyed. The old shape made `on_exit` wait for an in-flight HTTP request — up to a 10 s timeout — and `on_exit` runs on the LVGL thread, so that wait was a frozen screen. Nothing may block a switch. Inactive still means no buffer held and no request made, which is what section 6 actually asks for.

---

## Checkpoint A — It boots and the two apps are both reachable

**You:** the re-flash loop.

**Pass when:** it boots to Spotify as before; a long press of about half a second anywhere raises the selector with two glyphs on the ring; turning the dial rotates it with one haptic click per app; tapping enters. Entering the Clock shows the bloom and a time. The log shows `shell up, 2 apps, long-press for the selector` and an `app 'Clock' active` line with the heap figures after it.

**Opening, closing and switching PASSED 2026-09-03.** Long-press, dial, tap and the 4 s idle timeout all behaved, and the switch tore Spotify down in the right order (`exited` → `poll stopped, buffer freed`).

**One bug found and fixed in the same run: letting the idle timeout close the selector corrupted LVGL's heap.** `lv_timer_set_repeat_count(t, 1)` makes LVGL delete the timer itself the moment the callback returns — its own source says so at `lv_timer.c:103`. `selector_close` then deleted the same timer a second time, and the double free hung the next allocation inside `lv_tlsf_free` with the task watchdog firing on `IDLE0`.

It only appeared on the *idle* path. Closing by chevron or long-press never fired the timer, so the pointer was still live and the delete was legitimate — which is why the first three open/close cycles were clean and the fourth was not. A one-shot LVGL timer is owned by LVGL after it fires; the pointer must be dropped inside the callback. Both one-shot timers in this firmware now say so in a comment.

## Checkpoint B — The bloom is affordable

**Info:** the bloom draws 300 line segments into a full-screen canvas at 5 fps. That is the first thing in this project that could plausibly be too slow, so it times itself once and says so.

**FAILED 2026-09-03, fixed the same day — the finding this checkpoint existed for.**

The first implementation called `lv_draw_line` once per ray into the canvas. On hardware it did not merely run slowly: it starved the LVGL task so completely that `IDLE0` never ran and the task watchdog fired repeatedly, the device wedged, and the timing log it was supposed to print was never reached. The backtrace put it squarely in `bloom_render` → `lv_draw_line` → `lv_dpx`.

The cause is a mismatch of scale, not a bug in LVGL. Each `lv_draw_line` is a full draw-task dispatch and blend pass — cheap for the few shapes a screen normally holds, ruinous three hundred times a frame, and worse again with the canvas in PSRAM where every blend is a read-modify-write across the slow bus.

**The fix:** draw the rays straight into the canvas buffer. A ray is a handful of pixels; a DDA walk with an inline RGB565 alpha blend is both faster and less code than the call it replaces, and `lv_obj_invalidate` then hands the finished canvas to LVGL as one image. LVGL's drawing is still used for everything else on the screen — this is a hot inner loop earning an exception, not a rejection of the library.

**PASSED 2026-09-03 after the rewrite: `bloom: 300 rays in 27 ms`.** No watchdog, and touch and the dial stayed responsive. At the 5 fps the design calls for that is about 14% of one core, which is the budget every future full-screen effect now has to fit — the halo's spectrum display included.

**A second finding, from the same run: it was invisible.** The rays rendered but could not be seen on the panel. The simulator's opacity range of 0.05–0.31 was set against a bright monitor; at 40% backlight on a 46 mm screen the brightest ray landed around RGB(74, 28, 8), which is not there. Roughly doubled to 0.10–0.65 — a display-calibration difference, not a change of intent, and worth remembering the next time a value is carried from the simulator to the panel without being looked at on glass.

## Checkpoint C — The timer

**You:** on the Clock, turn the dial. Set a couple of minutes, stop, and let it commit. Then long-press to the selector and go to Spotify.

**Pass when:** turning the dial raises the winding screen seeded from any running timer; one detent is one minute; a detent at 0 going down and at 60 going up gives the firm haptic and a visible kick instead of silence; two seconds after you stop it commits and returns to the face with the arc and the remaining time showing; the countdown keeps running while you are in Spotify; and when it expires the alarm appears **over whatever app is up**, buzzing about once a second until touched.

**PASSED 2026-09-03.** The whole chain held on hardware: winding, one minute per detent, the firm haptic and kick at both ends, the two-second commit back to the face, the countdown surviving a switch into Spotify, and the alarm firing over the app that was up rather than only over the Clock. `clock: timer cancelled` in the log confirms the cancel path too.

## Checkpoint D — Memory is where it started

**Info:** the canvas is 259 KB of PSRAM. An app that fails to free it turns a third app into a memory problem, which is `BUILD.md`'s stated reason for the whole contract.

**You:** note the PSRAM figure in the `app '...' active` log line, then switch back and forth between Spotify and the Clock ten times and note it again.

**Pass when:** the PSRAM figure returns to the same value each time you land on a given app — no downward drift across ten switches. The Clock's `exited, canvas freed` and Spotify's `poll stopped, buffer freed` should both appear each time.

**PASSED 2026-09-03.** PSRAM returns to identical figures, not merely close ones: **8368060** whenever Spotify is the active app and **8384448** with it exited, repeated across every switch and across four power cycles. The Clock's canvas shows up as a clean round trip — 8384448 down to 8122300 on entry (262 148 bytes, the 259 KB canvas) and back to 8368060 after `exited, canvas freed`. Both release lines fired on every exit without exception.

Internal RAM settles at **68699** on Spotify and **102699** on Settings. The ~34 KB gap is the TLS session plus the poll buffer, which is why the boot-time `app 'Spotify' active` figure of ~113 500 is higher than the steady-state one: at that moment Wi-Fi is still associating and no connection exists yet. Not drift.

Fewer than ten switches were logged in one sitting, but the pass is on exact return rather than approximate: a canvas leak would appear as 256 KB steps and there are none.

## Checkpoint F — Settings

**Claude:** *landed 2026-09-03, build clean.* `main/settings_app.c` — the third ring, eight items at 45°, same mechanic as the selector and the same falloff. Four are set by the dial (brightness, sleep, haptics, dial step) and four are status (Wi-Fi, Spotify, Dictation, About). Tap enters an item, tap again leaves it and writes to NVS — committed on leaving, never on every detent.

The shell gained what it needed to make them real, all of it shell-owned by section 6: the settings themselves with NVS persistence, backlight duty control, the haptic strength that scales the whole vocabulary, and **sleep** — LVGL already counts touch inactivity, and the input task now feeds dial movement into the same counter, so the sleep setting actually turns the screen off.

**You:** long-press to the selector, dial round to the gear, enter it.

**Pass when:** the ring turns with one item per detent and wraps; entering Brightness and turning the dial dims the screen *as you turn* (it is its own preview) and stops at the 10% floor with a firm haptic rather than going dark; Haptics set to OFF genuinely silences the detent clicks and FIRM restores them; leaving an item logs `settings written to NVS`; and after a power cycle the brightness you chose is what the device boots at.

**Persistence PASSED 2026-09-03.** All four stored settings survive a power cycle, at non-default values:

```
I (23817) torque-os: settings written to NVS: brightness 55%, sleep 10 min, haptics 2, dial step 2%
        -- power cycle --
I (1029)  torque-os: settings loaded: brightness 55%, sleep 10 min, haptics 2, dial step 2%
```

**A false alarm worth recording, because it cost a test cycle.** Brightness was first reported as *not* surviving. It always had. `backlight_init(40)` runs as the first statement of `app_main`, before `nvs_flash_init`, and logged `backlight on GPIO47 at 40%` on every boot — a compiled constant that looked exactly like a restored value. The stored brightness is applied twelve lines later by `backlight_duty(s_brightness)`, which logged nothing at all. The instrument was wrong, not the code.

Both lines now say what they are: the boot line is tagged `(boot default, pre-NVS)`, and `settings_load` and `shell_settings_save` each print all four values. **A boot-time constant that resembles a live value is a trap; label it at the point it is printed.**

**The rest of Checkpoint F PASSED 2026-09-03.** The ring moves one item per detent and wraps past the end. Brightness dims *as you turn*, so the screen really is its own preview, and it stops at the 10% floor with a firm click rather than going black. Haptics OFF silences the detent clicks and FIRM restores them, which means the strength setting is scaling the whole vocabulary as intended.

## Checkpoint E — The contract held

**PASSED 2026-09-03 (code audit, no hardware needed).** The Clock app was written without a single change to shell code on its behalf. Everything the shell gained — haptics, the timer, the registry — is a service the shell already owned by `BUILD.md` section 6, and the Spotify app is untouched by the Clock's arrival. `clock_app.c` includes exactly one project header, `app_shell.h`, and touches no network, no token and nothing Spotify owns.

The one change that was *not* free is worth naming: the shell needed the input task and the switching machinery. Neither is app-specific, both were always in the design, and neither was made to accommodate the Clock — but the contract had never actually been exercised by a second app before today, and it is honest to say that the second app is what caused them to be written.

---

## Done when

- [x] The Clock app exists and is written against `knob_app_t` without shell changes on its behalf (Checkpoint E, 2026-09-03)
- [x] Both apps reachable through the selector, one haptic click per app (Checkpoint A, 2026-09-03)
- [x] The bloom's render time recorded here (Checkpoint B, 2026-09-03: 300 rays in 27 ms)
- [x] The timer sets, commits, survives an app switch, and fires over whatever is on screen (Checkpoint C, 2026-09-03)
- [x] Heap and PSRAM return to where they started across ten switches (Checkpoint D, 2026-09-03)
- [x] Settings ring navigates, brightness dims the screen live, and all four dial-set values survive a power cycle (Checkpoint F, 2026-09-03)
- [ ] `WAVE-3.md`, `WAVE-4.md` and this file folded into `BUILD.md` and deleted

## Known, and deliberately not fixed tonight

- **Spotify's dial does nothing.** Volume and seek are Wave 6. Turning the dial on the Spotify screen gives you a haptic click and no more, which is correct for now.
- **The bloom does not dim under the wind screen**, it is hidden outright. Cheaper, and the wind screen is a full-cover ground anyway.
- **Two apps make the selector a toggle wearing a carousel's clothes**, exactly as `BUILD.md` predicted. It is built now because the cost of adding it later is rewriting whichever app was built without it.
