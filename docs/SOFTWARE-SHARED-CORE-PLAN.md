# Software shared core — the work that serves both builds

**Date:** 2026-09-02. **Against:** `docs/SOFTWARE-CONTEXTS.md` (the integration assessment for the 60), `BUILD.md` (the standard one-off desk device), `design/screens.html` rev W, `design/simulator.html`.

**The test for "shared":** it runs with no companion app on the PC, no motor, and no DAC — the three things the standard device does not have. Anything that passes runs on the standard hardware today and carries into TorqueOS (the halo's firmware and companion) unchanged. Anything that fails waits for the halo.

## Rulings recorded today

- **Timer lives inside the Clock app.** The selector stays at five apps — the design doc calls five slots at 72° close to the practical limit for a rim, and a timer and a clock are one subject anyway.
- **The standard device stays keyboard-only over Bluetooth.** The halo enumerates a wheel-only mouse alongside its keyboard so the bezel scrolls whatever has focus; the standard does not copy this. Its dial is volume, it lives next to a real mouse, and the build doc's security posture — the HID descriptor exposes a keyboard and nothing else — stands unbroken. Revisit only if the standard's dial ever runs out of jobs.

## The six shared pieces

**1. The interaction core.** The settled mechanics, one spec both tracks implement, with the simulator as the reference implementation:

- The ring: glyphs on the rim, one green dot above twelve, the selected glyph lit and glowing, every other glyph fading with angular distance (opacity `0.12 + 0.88·(1 − d/180)^1.6` for angular distance d in degrees — fitted to rev W's drawn values).
- Motion: the ring chases its target angle with critical damping — starts instantly, settles gently, retargets cleanly at any detent rate. Never a fixed-duration animation per detent. Rotation is cumulative, so wrapping never rewinds.
- End stops are felt, rings are not: a clamped value (volume at 0 or 100, brightness at its floor, an enum at either end) answers a rejected detent with a firm haptic and a small visual kick. Rings wrap and never bump.
- Back is visible: a chevron at the foot of every ring, the whole lower band as its hit target. Long-press and idle timeouts still work and are never the only way.
- Timing: dial overlay clears after 2 s, controls return after 5 s, selector backs out after 4 s.
- The haptic vocabulary: one click per detent, a heavier click on a press, a thud at a clamp. The standard speaks it through the DRV2605 vibration driver; the halo speaks it through the motor. Same words, different voice.
- The colour law: white is progress, green is volume, amber is seek, red is mute/recording.

**2. The HID input contract.** One document covering both transports (Bluetooth on the standard, USB on the halo): the fixed chord enum — no string a human typed ever becomes a keystroke; chords are serialized, at least 600 ms apart; a believed state changes only when a chord was actually dispatched. The halo's extra interfaces (the wheel-only mouse, later a telephony page for Meet) extend this document rather than fork it.

**3. Dictation.** The Wispr Flow hands-free chord: spin right for on, left for off, idempotent; same direction twice inside 2 s resyncs. (The waggle — the global entry gesture — was retired 2026-09-02 on Wave 2's D4 evidence: the dial miscounts fast reversals. Dictation is reached via the selector.) Designed, simulated, identical on both. Firmware lands at the standard's Wave 10 and transfers whole.

**4. The Launcher.** A ring of up to eight entries, each a label (free text, only ever drawn) and a chord (a dropdown, never a text field), edited on a browser page. Identical on both; only where the editor page lives differs — the standard's config server, the halo's companion settings.

**5. Timer, inside Clock.** Zero dependencies, works unplugged. Sixty detents, sixty minutes: the dial winds it, the bloom counts it down. The Clock app's dial currently does nothing, so the timer takes it — turning the dial on the clock face starts winding a timer; the design of that screen is the next simulator task.

**6. Now Playing behind a seam.** The screen (art, marquee, progress rim, the dial-feedback bloom) is shared. The data source is not: the standard polls Spotify's cloud API; the halo is fed the Windows media session by the companion, which covers every player, not just Spotify. The simulator already proves the seam — its mock engine and live engine drive one UI through one interface — and the firmware keeps the same shape: the player-state provider is swappable, and the UI never learns where the state came from.

## Halo-only, deferred with no work owed now

The Calls stack (all three layers — ring detection, vendor buttons, guaranteed mute), notifications, Claude Code hooks, spectrum and EQ, calendar, Slack, Granola, Focus, Markets, the companion app itself, the modifier hotspot deck, freespin, and scroll-as-home with its inversion of the standard's dial-is-volume rule. All of it depends on the companion, the motor, multi-touch glass, or the DAC.

## Build order

1. **Extract the interaction core** (piece 1) from BUILD.md section 5, screens rev W and the simulator into `docs/SOFTWARE-INTERACTION-CORE.md`. Mostly transcription; the decisions are already made and running.
2. **Design the timer** inside Clock — simulator first, then the screens doc. Smallest new thing, useful on both, and it exercises the spec written in step 1.
3. **Write the HID contract** (piece 2), standard scope now, halo interfaces as marked extensions.
4. **Pin the player seam** — a short paragraph in BUILD.md section 6 stating the provider interface, so the Spotify app's UI never grows a cloud dependency the halo cannot feed.
5. **First-hardware-day verify** on the standard board: the Bluetooth keyboard enumerates and a chord lands — the shared half of the contexts doc's verify list. The halo's own verifies (mute layering, ducking, touch-under-spin, motor-vs-detent) stay on its list untouched.

## What this buys

The standard device stops being merely first and becomes the halo's proving ground: every hour spent on the shell, the rings, the chords, the dictation and the launcher is spent once. When TorqueOS starts, it inherits a tested interaction core and an input contract, and the halo team's remaining work is exactly the halo-only list — which is the list that needs its hardware anyway.
