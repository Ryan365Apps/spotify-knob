# Prototype plan — first five animations, first five sounds

What to build first on the real hardware to test the grammar, and the question
each one answers. Ordered: P1 gates everything after it. Each item has a
pass/fail so the test means something.

## Pre-flight

**P0 — measure the mechanical detent click.** Record the magnetic click on the
real (or bench-rig) detent assembly at arm's length, on a desk. Every sound gain
in `tokens.md` is defined relative to this recording. Also measure achievable
and comfortable detents/second by hand (dissent item 4, the doubt that 5
turns/second is real). No pass/fail — this is calibration.

**P1 — frame-rate soak.** Full-screen 800 × 800 composite: baked rim bitmap +
rotating 60-tick ring + a 260 px numeral pair, sustained. Then add anti-aliased
line segments until frame rate breaks; record the count.
*Pass:* 60 fps sustained on the base composite; the line budget is whatever the
number turns out to be — it decides whether the boot wireframe (animation A5)
lives or dies. *Fail:* below 30 fps on the base composite → the motion grammar
gets re-tuned to measured reality before anything else is built (dissent item 6).

## Five animations

**A1 — detent glide and settle (the ring menu).** Screen angle 1:1 with shaft,
no software snapping; dot pulse on detent crossing, decimated to one per 120 ms
beat. The core claim of section B of the findings document: the magnets animate
the screen.
*Pass:* turning feels like moving one rigid object; no perceptible lag between
click-in-hand and highlight-on-screen (target ≤ 1 frame). *Fail:* any visible
rubber-banding or double-snap.

**A2 — timer set and land.** Bloom + arc + numeral follow the knob; on the
set-point detent: actuator tick, `latch` within ±10 ms, numeral weight-up,
halo arc-end bloom — the only three-channel moment in the system.
*Pass:* the land feels like one event, not a chord of three. *Fail:* any
perceived ordering ("the sound came after") → tighten offsets and re-test.

**A3 — context arrival (the call).** Detent profile swaps at t=0, screen lands
at 360 ms, halo crossfades, `hail` once. Tests the "feel leads sight" rule.
*Pass:* a blindfolded user notices the feel change before a watching user
notices the screen change (actually test this, two people). *Fail:* the swap
feels like a glitch in the hand.

**A4 — end-stop wall.** Motor wall + 4 px screen compression + halo `wall`
flash, no sound.
*Pass:* the wall reads as one physical fact across hand, screen and desk.
*Fail:* the compression reads as bounce or lag — then delete it; the haptic
wall alone may be enough, and stillness is the house style.

**A5 — boot wireframe.** The dial draws itself (sixty meridians over the lathe
profile), rotates 30°, dissolves to the ring menu; gated on P1's measured line
budget.
*Pass:* completes inside 2400 ms at full frame rate and reads as *this object*,
not "a 3D graphic". *Fail on budget:* fall back to the concentric-recession
boot (section C of the findings document, the cheap depth option).

## Five sounds

Each tuned through the real Ø34 mm down-firing aperture onto a real desk (dark
and pale), levels set relative to the P0 click recording. Durations and pitches
start from `tokens.md` and are expected to move.

**S1 — `latch`** (the kerchunk). The hero. A/B against a Leica-style damped
mechanism recording. *Pass:* people describe it with a mechanical word (clunk,
latch, lock), not a musical one.

**S2 — `yes` / `no`** (tuned as a pair). Mirror motive, one varied parameter.
*Pass:* strangers guess which is which, ten out of ten, at conversational room
level.

**S3 — `land`** (timer end). Three decaying strikes, ×3 with 8 s gaps, then
permanent silence while the halo persists. *Pass:* audible from 3 m in a normal
room at day gain, and nobody in the room calls it an alarm.

**S4 — `hello` / `goodbye`** (pair). *Pass:* identifiable as connect/disconnect
without being told; shorter than feels safe — trim until it almost vanishes,
then back off one step.

**S5 — `hail`** (needs-you). Played once with the amber `hold`. *Pass:* it turns
the head without raising the pulse; if anyone reaches for a snooze control that
does not exist, it is too much.

## Exit criteria for the phase

The grammar passes when A1–A4 and S1–S2 pass on hardware and the frame-rate
budget from P1 is written into `tokens.md` as a measured number replacing the
(V) marks it covers. Then `state-table.md` gets promoted from proposal to spec
and the remaining states are built against it.
