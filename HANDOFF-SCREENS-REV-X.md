# Handoff — screens.html rev W → rev X

Paste this whole file into the design session. Transient: delete it once rev X lands.

## What this project is

**Radial** — a desk knob that controls Spotify playback directly against the Spotify Web API, with no PC companion process. This handoff is for the **standard build**: a one-off device on the Waveshare ESP32-S3-Knob-Touch-LCD-1.8 (360×360 round screen, rotary dial, no push switch). Not the halo project (the 60). Governed by `BUILD.md`.

## The rule you are working under

The simulator leads; the docs follow. `design/simulator.html` is the reference implementation — where it and a document disagree, the simulator is right until someone deliberately settles otherwise. `design/screens.html` records the design language after it has survived contact. It is at **rev W** and this work takes it to **rev X**.

**Never use a bare reference.** Not "screen 14" — write "screen 14, the waggle overlay". Not "R4" — write "R4, the requirement to toggle play/pause from the screen". Every ID carries its meaning every time it appears, in the document and in conversation.

## Job 1 — retire screen 14, the waggle overlay

Screen 14 in rev W is the waggle overlay: a global dictation gesture fired by flicking the dial left-right-left. **It was retired on hardware evidence on 2026-09-02 and must come out of the screens document.**

Why it died: the gesture was safe only because a waggle nets to zero detents and therefore could not move the volume. Wave 2's reversal test (checkpoint D4) measured the real dial over ten fast waggles and got **+2, +1, 0, −2, 0, +1, +1, +2, +3, +4** detents of drift. The dial is not a quadrature encoder — it is two bidirectional detector switches, one pulse line per direction, and they miscount under fast direction changes. The net-zero argument is void. Swallowing the detents of a *recognised* waggle does not save it either, because every waggle that fails recognition still leaks drift into the volume.

Screen 14 currently states "Volume cost: None. A waggle nets to zero" — that claim is now measurably false and is the reason this cannot wait.

Dictation is reached the ordinary way instead: the app selector → Wispr Flow. Screens 13 A and 13 B (Wispr Flow, and Wispr Flow while capturing) already cover it and stay.

**Numbering constraint:** do not silently reuse the number 14 for something else — `BUILD.md` and this repo's history reference screen numbers, and a recycled number is a trap. Either leave 14 as an explicit "retired" entry with a one-line reason, or renumber deliberately and say so in the revision note. Your call; state which you did.

## Job 2 — draw the timer, which exists in the simulator and nowhere else

The timer is built and working in `design/simulator.html` and has **no screen in the screens document**. This is the outstanding half of a decision already taken: the shared-core plan (`docs/SOFTWARE-SHARED-CORE-PLAN.md`) rules that the timer lives inside the Clock app rather than taking a sixth selector slot, because the selector is capped at five apps and a timer and a clock are one subject anyway. It has zero dependencies, works unplugged, and is shared with the halo build unchanged.

Draw it to match the simulator exactly. The behaviour, read off the simulator source:

**Entry.** The Clock app's dial had no job, so the timer takes it. On the Clock face, turning the dial at all enters the winding screen. There is no menu and no button.

**Winding screen.** The selector's dimmed ground, a white wedge sweeping from twelve as a fraction of sixty minutes, the value large in the centre as `N` with a small `min`, the title `TIMER`, and the hint `ONE DETENT · ONE MINUTE`. Sixty detents, sixty minutes — the same sixty that names the halo device. Clamped 0–60: a rejected detent at either end gets the firm haptic and small visual kick that every clamped value in this system gets (rings wrap and never bump; values clamp and do). White because the colour law says white is progress — green is volume, amber is seek, red is mute and recording.

**Commit.** Two seconds after the last detent, with no confirmation step. Winding to zero while a timer is running cancels it. This matches every other dial-set value in the system: spin freely, the screen updates locally at every step, one write lands when you stop.

**Running.** Back to the Clock face — the idle bloom and the time as before — with the timer now riding the rim as a second arc, and the remaining time in small text below the clock. The clock stays the subject; the timer is a passenger on the same face.

**Done.** An overlay drops over whatever is on screen: `0:00` at clock size, breathing (a slow pulse, 1.2 s), with the hint `TIMER DONE · TAP ANYWHERE`. It buzzes periodically until touched rather than once, and it wakes the screen if the device had gone to sleep. Tap anywhere dismisses.

Open questions genuinely worth your judgement, rather than things already decided:

- What the running rim looks like against the progress rim it borrows from — same weight, or lighter, given nothing else is competing for the bezel on the Clock face.
- Whether the remaining-time text is always present or only inside the last minute.
- What the winding screen shows when a timer is *already* running and you turn the dial to adjust it — the simulator seeds the winding value from the remaining time, so it reads as editing rather than starting over, but the screen has never been drawn.

## What else to touch

`BUILD.md` is edited in place, never appended to — it describes the current plan, not a changelog. It already carries the waggle's retirement in its interaction model (section 5) and its risk register (section 9), so that half is done. Check whether its Wave 7 entry (Clock, Settings, and the selector) needs the timer naming, and whether section 5 should describe the timer now that it has screens.

Do not touch the firmware. There is a live hardware bring-up running in parallel — Waves 2 and 3 are done, Wave 4 (the app shell) is mid-flight — and `firmware/` belongs to that session.

## What to hand back

The regenerated `design/screens.html` at rev X, a one-paragraph revision note saying what changed and what you decided on the numbering question, and any place where drawing the timer made you doubt something the simulator does. That last one matters most: the simulator is the reference implementation, so a disagreement found while drawing is a real finding, not a nuisance.
