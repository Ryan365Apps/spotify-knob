# Dissent — things I think the brief (or the current plan) has wrong

Kept separate as asked. Each item states the claim, the evidence, and what to do
about it. None of these re-opens a Decided item in `docs/DECISIONS.md` (the 60's
decision index); where one touches a decision it asks for a ruling on an
execution detail, not a reversal.

**1. Amber means two things.** The design law in `docs/VISION.md` assigns amber
to *seek*; the brief assigns amber to *needs-you* (the agent-permission hold, the
attention state). A colour that means both "you are scrubbing through a track"
and "something is waiting on you" is two words spelled the same. Evidence: the
whole value of a four-hue system is pre-attentive reading — Nest and HomePod work
because one hue never carries two meanings in the same context. Options: give
needs-you to amber and move seek to white (position is "the device showing you
where you are", which white already means), or accept the collision because seek
is hand-in-motion and needs-you is hands-off, so they can never co-occur. I lean
to the second — the states are temporally exclusive — but it needs a ruling
recorded, not an accident.

**2. "The halo shows the same arc" cannot be literally true.** The brief's timer
description says the halo shows the same arc as the screen. The screen's arc is
anchored at twelve o'clock — which sits inside the halo's 36° dead segment at the
rear. A twelve-anchored halo arc is born with its origin invisible. The findings
document (section D, the halo language) proposes gauge mapping instead: arcs
anchor at the gap's edges and sweep the 324°. From the owner's seat the gap hides
behind the object, so a full sweep still reads as a ring. This changes the
brief's words but preserves its intent; it should be confirmed as the intended
reading.

**3. The speaker must never double the detent.** The brief asks, open-endedly,
whether the speaker doubles the magnetic click or stays out of the way. The
findings document takes a hard position: never. Evidence: the magnets voice the
click with zero latency and perfect honesty; any speaker click arrives late
(audio path latency), and at spin speeds the sample queue collapses — the iPod
solved this by decimation, but we get the same result free by silence. This also
dissolves the brief's 300-clicks/second sound problem entirely. If a future
ratchet detent profile wants a voice, it must be a velocity-driven loop, not
queued samples.

**4. 5 turns/second is probably not a real operating point.** A Ø135 mm knob
with firm magnetic detents flicked hard may briefly coast fast, but sustained
5 turns/second by hand on a 34 mm-tall desk puck is doubtful — the figure reads
like a stress ceiling, not a use case. Unverified either way: the bench rig
(open questions A–F in `docs/DECISIONS.md`) should measure achievable and
comfortable detents/second, and the degradation ladder in the findings document
(section B) should be re-tuned to measured numbers. Design for the measured
95th percentile, engineer to survive the flick.

**5. The phyllotaxis bloom is texture, not data.** The timer hero is Decided and
this does not contest it. But a phyllotaxis fill does not communicate *how many*
minutes are set — point counts are unreadable past about six. The bloom carries
the beauty; the numeral and the arc must carry the number. The hero screen needs
all three layers, with the bloom explicitly subordinate: if the numeral were
deleted, the screen should fail its own legibility test.

**6. 30–60 fps "assume LVGL" hides the real risk.** Full-screen 800 × 800 at
60 fps over the display link with alpha compositing is plausible on the ESP32-P4
(the dial's processor) but unproven for *this* stack; the depth work in the
findings document (section C) budgets ~2,000 wireframe line segments per frame
on top. Nothing in the motion grammar survives a 20 fps reality. The very first
hardware prototype (prototype plan, item P1) should be a frame-rate soak test
before any grammar is judged — a motion system tuned in a 60 fps simulator and
shipped at half that is the most likely way this whole document fails.

**7. Whether the board has an ambient light sensor is load-bearing and unknown.**
The halo's day/night behaviour (section D of the findings document) currently
assumes clock-based switching as the fallback. If the Waveshare 3.4C board (the
60's compute module) has no light sensor, a bright halo on a dark evening desk
is the product's most annoying failure mode and the companion app must own the
schedule from day one. Check the schematic; record the answer in
`docs/SOURCING-BOM.md` or the decision index either way.
