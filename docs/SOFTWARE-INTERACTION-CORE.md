# Software interaction core — the mechanics both builds implement

**Date:** 2026-09-02. **Status:** transcription of settled, simulator-proven behaviour — the decisions were made in `design/simulator.html` and `design/screens.html` rev W and argued in `BUILD.md` section 5; this document is the single place a firmware author reads them. **Applies to:** the standard device and the halo (TorqueOS) equally. The reference implementation is the simulator; where a number here disagrees with it, the simulator is wrong and this document wins only after the disagreement is noticed and settled.

## Input primitives

- **Detent** — one signed step from the dial. On the standard, one physical click of the detector switches (proven exact at slow speed, Wave 2 D3; miscounts under fast reversal, D4 — see Retired below).
- **Tap** — touch released before the long-press threshold.
- **Long-press** — touch held **550 ms**. Opens the app selector from anywhere; never anything else.
- There is no knob press (the hardware has none) and no double-tap. No hidden gestures.

## The ring — one mechanic, used three times

The app selector (5 slots at 72°), Settings (8 at 45°), and the Launcher (8 at 45°) are the same widget with different contents. Glyphs sit at a 126 px radius on the 360 px screen.

- **Selection** is a single green dot fixed above twelve o'clock; the glyph beneath it is lit and glowing. No arc, no ticks — one mark, one meaning.
- **Falloff:** every other glyph fades with angular distance from the dot. Opacity = `0.12 + 0.88 · (1 − d/180)^1.6`, d the angular distance in degrees, evaluated continuously so glyphs brighten and dim *through* a turn, not per step.
- **The ring turns under the dot**, never the dot around the ring. The selected thing is always in the same place.
- **Rotation is cumulative.** Scrolling past the last item carries the ring onward in the same direction forever; only the selection index wraps. Deriving the angle from the index — which rewinds visually at the wrap — is the bug this sentence exists to prevent.
- **Motion is a critically-damped chase**, never a fixed-duration animation per detent. Keep a display angle and a target angle; every frame move the display a fixed fraction of the remaining gap (the simulator uses 0.25 per frame at ~60 Hz, settling in roughly 120 ms). Retargets blend cleanly at any detent rate. This is the Apple-crown / Galaxy-bezel pattern, and it is also how the LVGL ring should be driven: chase a target every tick, no `lv_anim` per detent.
- **Tap the centre** enters the selected item. **Tap a glyph** selects and enters it directly.
- **The centre (the hero)** shows the selected item's glyph, name, and — on Settings — its current value beneath the name: you are choosing what to change, so the name leads and the value confirms.

## Ends: wrap or bump, never silence

- **Rings wrap.** A ring has no ends and never bumps.
- **Clamped values bump.** Volume at 0 or 100, seek at either end of the track, brightness at its 10% floor or 100%, an enum at either extreme: the rejected detent answers with a firm haptic and a small visual kick — the whole screen face rotates ~2.5° in the attempted direction and springs back over ~180 ms, ease-out. A detent that lands on nothing must never feel like nothing.

## Back is visible

A chevron sits at the foot of every ring and the whole lower band (bottom ~96 px) is its hit target — the falloff leaves it the only lit thing down there. On the selector it returns to the app you came from; on Settings and the Launcher it goes up to the selector. Long-press and the idle timeouts still work and are never the only way out. Item screens (a value being adjusted) return to their ring on any tap.

## Timing rules

| Situation | Rule |
|---|---|
| Dial feedback overlay (volume / seek / timer wind) | clears 2 s after the last detent |
| Controls screen | returns to now playing after 5 s without interaction |
| App selector | backs out after 4 s idle, to the app you came from |
| Debounced writes | one network/HID action 400 ms after the last detent, never per detent |
| Long-press threshold | 550 ms |
| Chord spacing | ≥ 600 ms between HID chords (see the HID contract) |

**Optimistic UI:** every control action updates the screen immediately and is reconciled by the next read of truth. **Interpolation:** progress advances locally between polls; never poll faster to smooth a bar.

## The haptic vocabulary

One vocabulary, two voices — the standard speaks it through the DRV2605, the halo through the motor.

| Event | Haptic |
|---|---|
| Detent accepted | one short click |
| Button / transport press | one heavier click |
| Clamp rejected a detent | firm thud, with the visual bump |
| Timer done | repeated strong click, ~1 s period, until touched |
| Join/setup success | one click — the only haptic in the whole setup flow |

There is no double-click in the vocabulary (it belonged to the retired waggle).

## The colour law

White is progress and the device's own values (brightness, timer). Green is volume and selection. Amber is seek, warnings, and the config window. Red (`--live` `#E23D4C` / `--live-lit` `#FF7A87`) is recording/mute — the breathing ring on live dictation, and nothing else. Colour is ownership; a colour never carries two meanings on one screen.

## Retired, with the evidence

**The waggle** (rapid left-right-left reversal as a global dictation toggle) — retired 2026-09-02. Wave 2's D4 reversal test measured +2, +1, 0, −2, 0, +1, +1, +2, +3, +4 detents of drift over ten fast waggles: the detector switches miscount under fast direction changes, so the gesture's net-zero safety argument is void. Consequence for this document: no global gestures exist beyond long-press; fast-reversal input must never be load-bearing; and volume already tolerates the residual risk because slow detents count exactly.
