# User journey — as built

Every screen on the device, what each input does on it, and where each one takes you. **As built, not as designed**: this describes the firmware in `firmware/knob/main/` at the date on each entry, and where it differs from `design/screens.html` rev W the difference is called out rather than smoothed over.

Kept current in the same turn as any interaction change, alongside `BUILD.md` and `design/simulator.html`. If this file and the device disagree, the file is wrong.

**Last updated 2026-09-04.** Standard build (the one-off device on the Waveshare board). The halo project, the 60, runs the same software and so the same map.

---

## The two rules

Everything below follows from these. If a screen ever needs a third rule, the model is wrong.

1. **A long-press anywhere opens the menu.** The menu is the radial ring of apps — written up as the app selector until 2026-09-04, still called `selector.c` in the firmware, called the menu everywhere from here. It sits *over* whatever you were doing rather than replacing it, so backing out of it costs nothing.
2. **Back means one level up, and the top level is the menu.** Inside an app with levels, back returns to that app's own root. At an app's root, back opens the menu. In the menu, back closes it and leaves you exactly where you were.

The back affordance is a chevron at the foot of the screen with a generous tap area, built once in `shell_back_button()` so it sits in the same place on every screen and cannot drift apart.

---

## The map

```
                            ┌──────────────┐
              long-press    │   THE MENU   │   back / 4 s idle / long-press
        ┌───────────────────┤  (6 slots)   ├───────────────────┐
        │                   └──────┬───────┘                   │
        │                          │ tap a glyph               │ returns you
        │                          ▼                           │ where you were
        │        ┌─────────┬─────────┬─────────┬─────────┐     │
        └────────┤ Spotify │  Clock  │Dictation│Launcher │◄────┘
                 └────┬────┴────┬────┴────┬────┴────┬────┘
                      │         │         │         │      + Settings
                      │         │         │         │
   ┌──────────────────┘         │         │         └──────────────┐
   ▼                            ▼         ▼                        ▼
NOW PLAYING                  Clock     13 A/B                   15 A ring
   │ tap                     face      one screen                │ tap entry
   ▼                            │ dial                           ▼
CONTROLS ──── tap chip ────►  wind     (no sub-screens)      15 B "Launching"
   │  5 s idle                  │ 2 s                             │ 1.5 s
   ▼                            ▼                                 ▼
NOW PLAYING                  Clock face                      Spotify (home)
   │ dial (volume allowed)
   ▼
volume / seek overlay ── tap, or 2 s ──► NOW PLAYING
```

---

## The menu

`main/selector.c` on top of `main/ring.c`. Opens on LVGL's top layer, so the app underneath is never torn down.

| Input | What happens |
|---|---|
| Long-press, from any app | Opens it |
| Dial | One slot per detent, one haptic click each. Wraps. **Reversed 2026-09-04** — clockwise now walks the ring the other way |
| Tap a rim glyph | Enters that app directly, wherever it sits on the ring |
| Tap the centre | Enters the selected app |
| Tap the **Back** slot | Closes the menu, leaves you where you were |
| Tap the chevron | Same as Back |
| Long-press | Same as Back |
| 4 s of nothing | Same as Back |

**The app underneath pauses while the menu is up** (2026-09-04). It stays active and keeps its buffers; it just stops animating, because everything it draws is covered and the work lands on the same thread the ring is animating on.

**Six slots: five apps and Back.** Back is deliberately a duplicate of the chevron. It is discoverable where a chevron is not, and the sixth slot puts the glyphs 126 px apart at the 126 px ring radius rather than 148, which is the difference Ryan read on glass as five glyphs "fighting for space" (2026-09-04).

Apps in registry order: **Spotify, Clock, Dictation, Launcher, Settings.** Spotify is app 0, which is what the device boots to and what `shell_switch_home()` returns to.

---

## Spotify

`main/spotify_app.c`. Three screens, one app.

### NOW PLAYING — the root

| Input | What happens |
|---|---|
| Tap | → CONTROLS |
| Dial, volume allowed | → the volume overlay |
| Dial, volume refused | → CONTROLS. **Changed 2026-09-04**; it used to fall back to seek |
| Long-press | → the menu |

No back chevron here, deliberately. This screen is the artwork, and permanent chrome on the one screen meant to be the album is the wrong trade.

### CONTROLS — one tap down

| Input | What happens |
|---|---|
| Previous / play-pause / next | Sends the command, icon flips optimistically |
| VOLUME chip | Assigns the dial to volume. Greyed out when the device refuses volume |
| SEEK chip | Assigns the dial to seek **for one adjustment**. Since 2026-09-04 this is the only way the dial ever seeks |
| Device pill | Transfers playback to an idle desktop |
| Chevron | → the menu. Spotify's back affordance lives on this screen |
| Tap the ground | Resets the 5 s timer |
| 5 s of nothing | → NOW PLAYING |
| Dial | → the volume overlay, replacing CONTROLS rather than layering over it |

### The volume / seek overlay

| Input | What happens |
|---|---|
| Dial | Adjusts. Green for volume, amber for seek. Writes once, 400 ms after the last detent |
| Tap | → NOW PLAYING, **immediately**. Added 2026-09-04; it used to make you wait out the two seconds |
| 2 s of nothing | → NOW PLAYING |

---

## Clock

`main/clock_app.c`.

| Screen | Input | What happens |
|---|---|---|
| Face | Dial | → the winding screen, seeded from any running timer |
| Face | Chevron | → the menu. **Added 2026-09-04**; before that the only exit was a long-press |
| Face | Long-press | → the menu |
| Winding | Dial | One detent, one minute. Clamped 0–60, firm haptic and a visible kick at both ends |
| Winding | 2 s of nothing | Commits, → the face with the arc and the remaining time |

The timer belongs to the shell, not to this app, so it keeps counting wherever you go and the alarm fires over whatever is on screen. The alarm owns every input until it is touched.

---

## Dictation (Wispr Flow)

`main/wispr_app.c`, screens 13 A and 13 B of rev W. One screen in two states; there are no sub-screens.

| Input | Believed off | Believed on |
|---|---|---|
| Tap | Sends the combo → on | Sends the combo → off |
| Spin right, 3 detents | Sends → on | Nothing (idempotent) |
| Spin left, 3 detents | Nothing (idempotent) | Sends → off |
| Same direction again within 2 s | Sends regardless — the resync | Sends regardless |
| Chevron | → the menu | → the menu |
| Long-press | → the menu | → the menu |

Leaving the app does **not** stop dictation, and the belief survives the exit. Pretending otherwise would be exactly the desync the resync gesture exists to fix. The belief does not survive a reboot: a device that has just booted has no business claiming dictation is running.

**Three detents, not one**, so a knock can never start dictation. Detents more than 600 ms apart are not one gesture.

---

## Launcher

`main/launcher_app.c`, screens 15 A, 15 B and 15 C of rev W. Three modes on one screen.

### 15 A — the ring (root)

| Input | What happens |
|---|---|
| Dial | One entry per detent, wraps, same reversed direction as the menu |
| Tap an entry | Sends its chord → 15 B |
| Tap **Task View** | Sends `Win`+`Tab` → 15 C |
| Chevron | → the menu |
| Long-press | → the menu |

Seven entries as built: six placeholders plus Task View, always last. The entries are compiled in until Wave 9's config page exists, because naming an application is typing and this device does not type.

### 15 B — "Launching"

Holds 1.5 s, then → Spotify. Nothing else does anything. It says **Launching**, never Launched: the device cannot know whether the application started, was already open, or whether the chord landed on a locked screen.

### 15 C — Task View

| Input | What happens |
|---|---|
| Dial | `Right` / `Left` arrow, one per detent |
| Tap | `Enter`, then → Spotify |
| Long-press | `Esc`, → the ring. The menu opens over it, and backing out of that returns to the ring |
| 5 s of nothing | `Esc`, → Spotify |
| Leaving the app | `Esc`, so Task View is never stranded open on the PC |

No position counter, because the device cannot know how many windows exist or which is highlighted. A readout would be invented.

---

## Settings

`main/settings_app.c`. Eight items on a ring, each opening a value.

| Screen | Input | What happens |
|---|---|---|
| Ring | Dial | One item per detent, wraps. **Reversed 2026-09-04** to match the menu |
| Ring | Tap | → that item's value |
| Ring | Long-press | → the menu |
| Value | Dial | Adjusts. **Not reversed** — a quantity has its own direction, and brightness that fell when you turned it up would be nonsense |
| Value | Tap | → the ring, and writes to NVS |

Written on leaving an item, never on every detent.

**Owed:** this app still carries its own copy of the ring rather than using `main/ring.c`. It is a value editor as well as a ring, so migrating it is more than a move. Until it happens, a change to ring behaviour has to be made in two places — which is exactly the drift that made the extraction worth doing.

---

## The loading spinner

Not a screen you navigate to — it is what Spotify shows before the first poll lands, and what the rate-limited and unavailable states sit on.

The comet's head is **rainbow, coloured by where each ray sits on the circle** (2026-09-04). The tail spans 45% of the ring, so about 160° of spectrum trails the head; the colours stay put and the light sweeps across them, which reads as a rainbow being lit rather than a coloured object moving. One turn takes 1.92 s. The resting field underneath stays neutral, because a rainbow at 10% alpha is two or three RGB565 levels per channel and reads as coloured noise rather than colour.

Before this it was purple, and that was a bug rather than a choice — see `BUILD.md` section 6 on what `px_blend` means by white.

---

## Sleep

Not a screen, but it is the first thing that happens to you on a normal day.

| State | Input | What happens |
|---|---|---|
| Awake, idle past the Settings timeout | — | Backlight off, and an invisible shield goes up on LVGL's system layer |
| Dark | Touch | Lights at once on the press, and the shield absorbs the whole gesture through to the release. The app underneath never learns the touch happened |
| Dark | Brief spin of the dial | Lights at once. The detent is dropped by the input task and does not reach the app |
| Dark | The alarm firing | Lights, and the alarm takes over |

Built 2026-09-04. Before that, sleep was only the backlight, so a touch in the dark both lit the screen and pressed whatever was under the finger.

---

## Where this differs from `design/screens.html` rev W

rev W is owned by a separate session taking it to rev X — read it, never edit it. Beyond the three rendering differences already listed in `BUILD.md` section 10, the navigation differs in four places, all decided on glass on 2026-09-04:

1. **Ring direction is reversed** in the menu and in Settings.
2. **The menu has a sixth slot**, Back, which rev W does not draw.
3. **The dial no longer falls back to seek** on a volume-refusing device; it opens CONTROLS.
4. **Every app has a visible back chevron.** rev W draws one on the rings; the Clock and Dictation did not have one at all.
