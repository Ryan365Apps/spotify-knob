# Findings — UI, light, display and sound design for the 60

Answers the R&D brief in `docs/Research/4-ui-light-sound-RD.md` (the brief asking for a
design system in which screen, halo, sound and detent are one language). Companion
files in this folder:

- `state-table.md` — one page: state → screen / halo / sound / detent.
- `tokens.md` — one page: the token list, paste-able into a repo or a brand guideline.
- `dissent.md` — things I think the brief has wrong, with evidence, kept separate.
- `prototype-plan.md` — the five animations and five sounds to build first on hardware.

A note on evidence: references below are linked to canonical sources (studio
portfolios, vendor pages, papers). Frame-grabs from films and games cannot be
captured from this environment; each entry that needs one is marked **[grab]** with
the exact scene or screen to capture. Every number that is not derived from the
brief's own figures is marked **(V)** — a starting value to verify on hardware, per
the project rule that no dimension or figure may be invented.

Two derived figures used throughout, shown once here with their arithmetic:

- **Pixels per millimetre:** the 3.4-inch round panel has an active area of
  Ø86.4 mm (3.4 in × 25.4 mm/in); 800 px / 86.4 mm ≈ **9.3 px/mm**.
- **Detent arithmetic:** 60 detents = one click per 6°. At a deliberate turning
  speed of about 2 detents/second the detent period is ~500 ms; at a hard spin of
  5 turns/second it is 3.3 ms (300 clicks/second, as the brief says).

---

## A. The reference survey — what to steal and what to refuse

Two lines each: steal / refuse. Grouped as in the brief.

### Film and television

**Iron Man HUDs (Perception, Cantina Creative)** — [perception.studio](https://www.experienceperception.com), [cantinacreative.com](https://cantinacreative.com) **[grab: Iron Man 2, suitcase-suit HUD boot; Avengers, Jarvis radial menu]**
Steal: radial menus that bloom from a centre and collapse back to it — everything has a home position. Refuse: layered translucent clutter; it reads only because the camera holds still and an actor narrates what it means.

**Minority Report** **[grab: the scrubber timeline]**
Steal: direct manipulation — the hand moves, the data moves, 1:1, no cursor between them. Refuse: everything floats; nothing has a resting state, which on a desk object becomes fatigue.

**Oblivion (GMUNK)** — [gmunk.com/OBLIVION-GFX](https://gmunk.com/OBLIVION-GFX) **[grab: the desk console, light table]**
Steal: the closest single reference to our register — monochrome line-work, one accent colour, thin strokes on glass, generous emptiness. It is a *desk console* designed to be lived with for a shift. Refuse: it depends on a huge backlit white environment; our object is black metal in a normal room.

**Blade Runner 2049 (Territory Studio)** — [territorystudio.com](https://territorystudio.com/project/blade-runner-2049/) **[grab: Wallace Corp archive reader, K's spinner dash]**
Steal: interfaces treated as physical artefacts — worn, low-contrast, mono; UI *as object* rather than UI *on object*. Refuse: atmosphere ranks above legibility; half the beauty is film grain and lens bloom we cannot render.

**Ex Machina (Territory Studio)**
Steal: the power of a screen that is mostly off — Nathan's house shows information only at the moment of need. Refuse: nothing; this one is nearly all lesson.

**Tron: Legacy** **[grab: identity disc UI]**
Steal: glow discipline — one hue per allegiance, which is exactly our colour-is-ownership law; the identity disc as a ring that carries state. Refuse: everything glows; on our chip full-screen glow is expensive, and when everything glows nothing does.

**Prometheus** **[grab: the orrery scene]**
Steal: convincing 3D from points and short line segments at low density — a wireframe budget our 2D chip can afford. Refuse: volumetric particles; that is a render farm on screen.

**The Expanse** **[grab: Rocinante ops console]**
Steal: diegetic screens with dull, plausible latency; typography doing the work, not motion. Refuse: information density tuned for an audience freeze-framing, not an operator glancing.

**Westworld tablets** **[grab: behaviour-editing tablet]**
Steal: proof that a calm, pale, paper-like register reads as *more* advanced than dark sci-fi; restraint as menace. Refuse: light-mode UI on our device would fight the black metal and flood the porthole at night.

**Mark Coleran (FUI)** — [coleran.com](http://www.coleran.com)
Steal: screens that imply an operating system continuing beyond the frame — our contexts (which surface themselves; a given in the brief) should feel like windows onto one continuous machine. Refuse: the deliberate over-busyness that reads as "computer" to a cinema audience.

**Ash Thorp** — [ashthorp.com](https://ashthorp.com)
Steal: typographic hierarchy inside HUDs — type as the structure, graphics as its servant. Refuse: the density and layer count.

### Games

**Dead Space (health bar on the spine)** **[grab: rig health bar]**
Steal: the state lives on the object, not in an overlay — this is the halo's whole argument, validated. Refuse: nothing; it is the canonical diegetic UI.

**Destiny (cursor and radial menus)** **[grab: character radial]**
Steal: a cursor with weight and inertia — motion implies mass, which suits a heavy knob. Refuse: cursor-driven interaction itself; we have a physical detent, we never need a floating pointer.

**Elite Dangerous / No Man's Sky ship HUDs** **[grab: Elite target-ship wireframe]**
Steal (Elite): the one-hue wireframe ship silhouette — the direct model for a boot wireframe of the dial itself; cheap line-work with high object pride. Refuse (both): HUD chrome everywhere; No Man's Sky's decorative dot-noise.

**Gran Turismo 7 / Forza Horizon menus** **[grab: GT7 café menu, licence-test result card]**
Steal (GT7): machined-metal materiality, tabular data presented with dignity, silence between sounds. Refuse (Forza): festival energy — the exact opposite of a watch on a desk.

**Cyberpunk 2077**
Steal: commitment — the UI style is worn everywhere including the box and marketing, which is our section G (brand = product) done at scale. Refuse: glitch-as-brand; deliberate damage ages badly on a longevity product.

**Persona 5** **[grab: menu transition]**
Steal: every transition has one strong direction and *lands* — commit to a motion signature and repeat it until it is a brand asset. Refuse: the maximalism; at 60 detents/turn that energy would be nauseating.

**Nintendo Switch system sounds**
Steal: a click palette that is tiny, dry, quiet and designed for shared rooms; the "snap" is loved because it is short and certain. Refuse: nothing at the sound layer; refuse the visual toy-store part.

**PS5 UI**
Steal: how little motion a premium feel actually needs — most of the calm is stillness plus one slow particle field. Refuse: that particle field needs a GPU (graphics processor) we do not have.

### Apple

**Digital Crown on Apple Watch** **[grab: crown scroll with rubber-band end-stop]**
Steal: the master rule of this whole document — on-screen motion is owned by the hand, 1:1, with haptic and visual end-stops in lockstep. Refuse: their detents are synthesised by a haptic engine; ours are real magnets, which is better and must never be masked.

**iPod click wheel and clicker sound**
Steal: click decimation — at high scroll speed the iPod drops clicks rather than smearing them, and the dry piezo timbre never wears out. Refuse: the wheel's acceleration curve (position, not velocity, must map to our ring — the dial is absolute, sixty detents, sixty minutes).

**watchOS complications**
Steal: glanceable density on a small round face — tabular numerals, fixed slots, no truncation surprises. Refuse: the cramped edge-of-dial text; our 60 cm viewing distance is triple a wrist's.

**Dynamic Island**
Steal: contexts surfacing themselves inside a fixed physical frame — the strongest recent proof our given interaction model works and feels premium. Refuse: the blur and spring physics; ours must land with machined precision, not jelly.

**visionOS depth and glass**
Steal: hierarchy from shadow and scale only — depth cues that survive without a GPU. Refuse: translucency and blur, which are per-pixel shader work we cannot afford.

**HomePod top light**
Steal: light as *presence*, not data — it breathes when listening and is otherwise dark. Refuse: the top-surface placement logic; our light fires down and must read on the desk, not on the object.

**Apple Watch Ultra — Wayfinder and Modular Ultra faces** **[grab: night mode red]**
Steal: bezel numerals as instrument furniture; the all-red night mode as proof one hue swap can re-voice a whole face. Refuse: complication clutter at our viewing distance.

**Jony Ive era / LoveFrom**
Steal: "the interface is the object" — one typeface, one radius family shared between hardware fillets and screen corners; this is the book-of-shapes idea (that a brand owns a family of curves) executed. Refuse: nothing; this is section G's north star.

### Automotive

**McLaren folding cluster (720S, Artura binnacle)** **[grab: slim mode fold]**
Steal: mode changes marked by a *physical commitment* — our context switches should feel that decisive on screen even though nothing moves mechanically. Refuse: the actual motorised screen; moving parts for theatre violate our longevity law.

**Porsche five-dial cluster, Taycan curved display, 911 centre tachometer**
Steal: one sacred anchor held for sixty years — the centre tach is their green-dot-at-twelve; instruments as brand assets. Refuse: the Taycan's tendency to render fake physical dials; we have a real ring, we never draw a fake one.

**Porsche Design (watches, headphones)**
Steal: black-on-black with one machined bright edge — materially our object already; their typography is instrument-derived and licensable thinking. Refuse: the branding-by-logo; we have no logo on the face.

**Rimac / Pagani (exposed mechanism)**
Steal (Pagani): mechanism as ornament — our sixty magnets are invisible but their *consequence* (the click) is the ornament; celebrate it in sound and motion honesty. Refuse: jewel-box clutter.

**Mercedes Hyperscreen** — the warning, as the brief says
Steal: nothing. Refuse: the belief that more display is more premium; it is the anti-object.

**bookofshapes.com / the "book of shapes" idea** — [bookofshapes.com](https://bookofshapes.com)
Steal: wholesale, as the method for section G — the brand is a small family of curves that recurs at every scale. Refuse: nothing.

### Hardware with a light ring

**Nest Thermostat (original)** **[grab: leaf moment, heat-orange fill]**
Steal: our category ancestor — ring + dial + one number + colour as state; the whole screen changes hue to say what the *system* is doing. Refuse: full-screen colour floods; on a porthole in black metal, colour stays rationed to light elements.

**Amazon Echo**
Steal: the cyan pointer on the blue ring — the light ring can *point*, which our knob-following tick inherits. Refuse: light that means "the cloud is listening"; our light must only ever mean something the owner asked for.

**Sonos Era**
Steal: connect/join sounds that are short, pitched, and end conversations rather than starting them. Refuse: capacitive-only control — validated by their users' complaints; our knob is the answer to that.

**Teenage Engineering OP-1 / OB-4** — [teenage.engineering](https://teenage.engineering)
Steal: 2D sprite graphics that are proudly cheap to render yet read as luxury because they are *drawn well* — the existence proof for our chip; motion only as signal. Refuse: the toy register; the 60 is a watch, not an instrument-toy.

**Nothing Glyph**
Steal: naming and codifying light patterns so they can be documented and marketed. Refuse: the vocabulary size — most Glyph patterns go unlearned and unused; the lesson is a hard cap (ours is six halo states, section D).

**Dyson**
Steal: engineering data displayed as pride (their airflow graphs) — our settings screen can show detent-strength curves the same way. Refuse: cyclone-grey visual language; wrong material world.

**Playdate crank** — [play.date](https://play.date)
Steal: the crank moments — hardware input driving the world 1:1 produces delight with zero graphics budget. Refuse: whimsy as default; ours is earned at moments like the timer land, not constant.

**Braun / Dieter Rams dials** **[grab: T3 radio dial, ET66 calculator]**
Steal: the dot and line as a complete marking language; "as little design as possible" as the entire tone of voice; the coloured dot on a monochrome object. Refuse: nothing. This is the register the whole system should sit in.

### Section A recommendations

1. Adopt the **Oblivion/Elite register**: monochrome line-work at 2–3 px stroke (V)
   on black, one accent hue at a time, generous emptiness. It is cheap on the
   ESP32-P4 (the dial's processor, which has no 3D GPU) and correct for the brand.
2. Adopt the **Digital Crown rule** as law: on-screen motion is owned by the hand,
   1:1 with shaft angle, always. The magnets animate the screen; software never
   fakes a detent the hand did not feel.
3. Cap the vocabulary everywhere Nothing failed to: **six halo states, eight
   sounds, five detent profiles**, named, documented in `tokens.md`, and never
   extended without retiring something.

---

## B. Motion — synchronised radial elements and the detent

### The base clock is the detent, not the wall clock

All durations derive from the detent period at deliberate turning speed. Measured
turning speeds for the actual knob do not exist yet (bench-rig item), so this
document assumes **deliberate turning ≈ 2–8 detents/second** (V), giving a working
base unit:

> **1 beat = 120 ms** (V) — roughly one detent at brisk deliberate turning.
> Standard durations are multiples: pulse 120 ms, land 240 ms, arrive 360 ms,
> boot only may exceed 600 ms.

### Between the clicks (the 6°)

The ring menu **slides continuously at 1:1** with the shaft angle, read at
sub-detent resolution. No software snapping, no interpolation toward detent
centres. The physical magnets already pull the shaft into the detent; if the
screen is honestly 1:1, the *magnets themselves produce the visual snap*, and
screen and hand can never disagree. This is the single most important motion
decision in this document: the snap is real, so rendering it would double it.

### At the click — order and offsets

| Channel | What fires | Offset from magnetic click | Budget |
|---|---|---|---|
| Haptic | The magnetic detent itself | t = 0 — it *is* the clock | — |
| Sound | Nothing. The magnets own the click (section E) | — | — |
| Halo | Tick marker advances one LED-step | ≤ 10 ms | LED update is near-free |
| Screen | Item highlight crosses over; dot pulse begins | ≤ 1 frame (16.7 ms at 60 fps) | pulse: 120 ms sine in-out, dot 100% → 140% → 100% scale (V) |

Perceptual grounding: haptic–audio events fuse as simultaneous within roughly
±10 ms, haptic–visual within roughly ±50 ms (commonly cited multimodal
simultaneity windows — treat as literature guidance, not spec (V); the prototype
plan includes measuring what the hand actually tolerates). The ordering rule:
**touch first, light second, pixels third, sound only for events.**

### When the knob is spun fast

At 5 turns/second the shaft crosses 300 detents/second. No channel should try to
keep up per-detent; each has a defined degradation:

- **Screen** — rotation stays continuous and 1:1 at whatever frame rate holds
  (rotation is one transform, cheap). Per-detent pulses decimate: the dot pulses
  at most once per beat (120 ms), so above ~8 detents/second pulses merge into a
  steady shimmer. Above ~15 detents/second (V) item labels are replaced by the
  coarse index (numerals only) until speed drops.
- **Halo** — the tick is positional, not evented: it renders the current angle
  every LED frame and therefore never falls behind or queues.
- **Sound** — nothing to degrade; detents are silent by design. (If a ratchet
  detent profile is ever given a voice, it must be a velocity-driven granular
  loop, never queued samples — queued clicks arriving late is the worst sound a
  precision object can make.)
- **Haptic** — the motor may lighten detent strength as velocity rises and
  restore it as the knob slows (flywheel feel), consistent with decision 19 in
  `docs/DECISIONS.md`, the decision that dynamic detent strength comes from the
  motor. Strength curve is a bench-rig question.

The rule that generalises: **events queue, positions don't. Render positions;
decimate events.**

### How much motion may originate from the device

Three legal sources of on-screen motion, nothing else:

1. **The hand** — unlimited, 1:1, uneased (the magnets are the easing).
2. **An event** — a context arriving or leaving, a press, a land: one animation,
   ≤ 360 ms, then stillness.
3. **Ambient** — the halo may breathe; the screen may show only clock-hand-slow
   change (the timer's arc creeping, a progress dot). Test: if a bystander's eye
   is drawn to the dial when nobody is touching it, it is a bug — the brief's
   own words, adopted as an acceptance criterion.

### Easing family (named, for `tokens.md`)

| Name | Curve | Use |
|---|---|---|
| `settle` | cubic-bezier(0.2, 0.9, 0.1, 1) | anything landing into place; the signature |
| `exit` | cubic-bezier(0.4, 0.0, 1, 1) | anything leaving; accelerates out, no lingering |
| `pulse` | sine in-out | dot pulse, halo tick |
| `breathe` | full sine, 4000 ms period | halo waiting states only |

`settle` overshoots never. A machined part slides home and stops; it does not
bounce. Spring physics is banned from the system.

### Micro-animation storyboards

Frame strips as text (frame = what is on screen at that time). Channels column
lists what fires, in firing order.

**Boot / splash** — total 2400 ms, once per power-on
| t (ms) | frame |
|---|---|
| 0 | black |
| 300 | wireframe of the dial itself begins drawing: profile sweep, meridian lines appearing radially (section C) |
| 1400 | wireframe complete, rotates 30° with `settle` |
| 1900 | wireframe dissolves outward to the bezel; ring menu fades in |
| 2200 | green dot lands at twelve with one `pulse` |
Channels: screen (above); halo — one white sweep around the 324° arc at 30%
brightness (V), 300→1400 ms; sound — `hello` at 2200 ms as the dot lands; detent —
motor runs its calibration before 300 ms, so the first touch is already correct.

**Wake from idle** — 240 ms
| 0 | idle state (dark or clock) | 240 | active context, `settle` |
Channels: screen fade+scale from 96%→100%; halo returns to context state over
240 ms; no sound; detent already live (magnets never sleep — a brand fact worth
stating everywhere).

**Context arriving (call starts)** — 360 ms
| 0 | current context | 120 | current context slides down-screen 40 px, `exit`, dimming to 60% | 360 | call context lands from top with `settle`; dot re-lights |
Channels: halo crossfades to breathing green over 360 ms; sound — `hail` only if
the context demands attention (a call does; a track change does not); detent —
motor swaps to the arriving context's profile at t=0 (feel changes *first*: the
hand learns the context switch before the eye).

**Context leaving** — 240 ms, mirror of arriving but faster; the departing
context exits with `exit`, the restored one lands with `settle`. No sound.

**Press (knob or screen)** — 120 ms
| 0 | pressed element at 100% | 60 | 94% scale | 120 | back to 100%, action fires |
Channels: haptic — actuator tick at t=0 (the press has no magnet, so the
actuator, the event-haptics layer from `docs/PREMIUM-BOM.md`'s three-layer model,
supplies the click); sound — `tick` within ±10 ms of the actuator; screen as
above; halo unchanged (presses are local, light is global).

**Long-press** — 600 ms hold to fire
| 0 | element at 100% | 0–500 | a thin ring draws clockwise around the pressed element, linear | 600 | ring completes, action fires with one `pulse` |
Channels: haptic — soft actuator tick at 0, firm tick at 600; sound — `yes` at
600 ms if the action confirms something; halo unchanged. Linear easing on the
draw is deliberate: progress toward a threshold must not lie.

**End-stop reached** — 240 ms
| 0 | content at limit | 0–120 | content compresses 4 px against the stop direction (V) | 240 | relaxes home with `settle` |
Channels: haptic — motor wall at t=0 (the wall *is* the event); halo — `wall`
flash, 80 ms full ring at owner hue then 320 ms decay; sound — none (the hand
already knows; light confirms at distance); screen as above. The 4 px compression
is the only elastic motion in the system, and it is telling the truth — the hand
really is pushing against a wall.

**Timer landing (set-point reached while turning)** — 240 ms
| 0 | bloom filling, numerals counting with the knob | 0 | knob stops on a detent | 240 | bloom settles, numerals weight up (regular→medium (V)), arc end caps |
Channels: haptic — the magnetic detent itself, plus one firm actuator tick at
t=0 confirming capture; sound — `latch` (the kerchunk) within ±10 ms of the
actuator tick; halo — the arc's leading end blooms once, 150%→100% over 500 ms;
screen as above.
This is the hero moment; it is also the only moment three channels fire at once.

**Timer end** — 1600 ms + repeats
| 0 | full bloom | 0–800 | bloom releases outward, petals fading edge-first | 800–1600 | numerals "0:00" alone, one `pulse` |
Channels: sound — `land`, three decaying strikes, repeated twice more at 8 s
intervals (V) then silent forever; halo — slow white pulse continues until
dismissed (light persists, sound gives up: calm-technology ordering, section D);
haptic — none until touched; first touch anywhere dismisses.

**Volume limit** — same skeleton as end-stop; owner hue green; if the limit is a
software cap rather than the motor wall, the actuator supplies the wall tick.

**USB connect / disconnect** — 240 ms
| 0 | current screen | 240 | a small device glyph lands in / lifts out of the status position with `settle`/`exit` |
Channels: sound — `hello` / `goodbye`; halo — one white tick at the gap edge
(the "device" colour is white per the design law in `docs/VISION.md` that colour
is ownership); detent unchanged.

**Low-priority notification** — 360 ms, then still
| 0 | current screen | 360 | a single dot in the notification slot fades in, no motion afterwards |
Channels: halo — nothing (the halo is reserved for states that need the room to
know); sound — nothing; this is the periphery, calm technology's outer ring.

**Error** — 240 ms
| 0 | attempted action | 120 | the acting element shakes once, ±3 px (V), 2 cycles | 240 | still |
Channels: sound — `no`; haptic — double actuator tick; halo — unchanged unless
the error is systemic (then amber `hold`). Red is never used for errors: red
means recording and mute only, per the design law in `docs/VISION.md`.

### Section B recommendations

1. **1:1 or nothing.** Screen angle equals shaft angle, always; the magnets are
   the animator between clicks. All eased motion is reserved for events, capped
   at 360 ms, `settle`/`exit` only, no springs.
2. **Positions render, events decimate.** Halo tick and ring rotation are
   positional and can never lag; dot pulses and sounds are events, rate-limited
   to one per 120 ms beat.
3. **Feel leads sight.** On a context switch the detent profile changes at t=0,
   pixels land at 360 ms. The hand should know before the eye does.

---

## C. Depth on a flat round screen

### The anamorphic question, answered honestly

The Chengdu Taikoo Li and Seoul SM Town "Wave" billboards work because they are
corner-mounted two-plane displays with one designed viewpoint, no competing
reference geometry, and viewers who look for seconds and move on. The 60 has a
*better* fixed viewpoint than a street (the owner sits at a desk: ~60 cm,
40–50° elevation, azimuth roughly stable) but two things kill perspective
fakery anyway: the head moves continuously through several centimetres, and the
machined chamfer is a truth reference two millimetres from the picture — real
geometry against which any rendered perspective error is instantly visible.
**Refuse anamorphic geometry.** What survives from the billboards is their real
trick: content that *breaks an implied frame* reads as deep. A ring that draws
slightly "under" the chamfer shadow does this without any perspective math.

### What reads as depth on a 2D pipeline

Ranked by cost on the ESP32-P4 (the dial's processor: 2D pixel engine, no GPU,
alpha blends and scaled bitmaps cheap, per-pixel shaders not):

1. **Baked rim lighting — 1 blit.** A precomputed 800 × 800 alpha bitmap:
   specular gradient at the top edge, soft occlusion shadow inside the chamfer's
   lower arc, consistent with overhead room light. Composited over every screen.
   This is the porthole illusion: the picture appears *machined into* the metal.
   Static, so the head-motion problem never arises.
2. **Concentric recession (the rendered infinity mirror) — ~10 blits.**
   Pre-scaled ring sprites stepping down in size and brightness toward the
   centre. Worth the pixels only where depth is the message: the timer's well,
   idle, boot. As a persistent background it violates the ambient-motion rule.
3. **Wireframe of the dial itself — measured, not assumed.** An Elite-Dangerous-
   style line rendering of the 60's own profile: sixty meridians (one per
   detent — the geometry *is* the brand) over a lathe profile of ~20 segments
   ≈ **1,200 line segments** plus ring cross-sections, call it ≤ 2,000 segments
   per frame as the test budget (V). Whether the P4 draws 2,000 anti-aliased
   segments at 60 fps is prototype item P4 in `prototype-plan.md` — no claimed
   number, measure it. Rotating it needs only a per-frame 3D→2D transform of
   ~1,300 points in software, which the 400 MHz dual core should absorb (V).
   Use: boot, and the settings screen's "about this unit" as the object's
   self-portrait with the unit number.
4. **Knob parallax — free.** The world rotates with the ring (already law from
   section B). The depth trick on top: the screen's outermost tick ring rotates
   1:1 with the knurled metal ring 2 mm away from it, so pixels and metal read
   as one rigid object. This requires a one-time angular calibration of panel
   mounting rotation (a named parameter for the factory, in `tokens.md`).

### Recommendation and cost

Adopt 1 and 4 always-on (2 blits + one rotated tick-ring draw per frame);
adopt 3 for boot and settings only, gated on the measured line budget; adopt 2
only inside the timer. Total persistent depth cost: **~3 draw operations per
frame** over the content. Refuse anamorphic perspective permanently.

---

## D. Light — the halo as a language

### What a downward horseshoe can and cannot say

The halo is ~90 LEDs (light-emitting diodes) — derived: a ring at Ø128 mm (V,
diameter from CAD pending) has a 402 mm circumference; the 324° arc is 362 mm;
at the brief's ~4 mm pitch that is ~90 LEDs — seen only as reflected glow on the
desk. It can say: *hue* (4–5 discriminable owner colours), *magnitude* (arc
length), *position* (a local brightening), *rhythm* (breathing vs solid vs one
flash). It cannot say: text, count, anything at the back 36°, anything fine —
the diffuser and the desk bounce low-pass everything. Treat it as a one-word
channel: each state is one word.

### The gap problem, turned into the gauge

The 36° opaque segment faces away from the user — which is also where the
screen's sacred twelve-o'clock dot lives. A twelve-anchored halo arc would begin
inside the dead zone. Resolve it by making the halo a **gauge, not a mirror**:
arcs anchor at the gap's clockwise edge and sweep the 324° to the other edge;
the two horseshoe ends become the "empty" and "full" posts. From the owner's
seat the gap is hidden behind the object, so a full 324° sweep still reads as a
complete ring. The screen mirrors angle for *position* (the tick), but
*magnitude* (timer, volume) maps to the gauge. This is a deliberate departure
from the brief's line that the halo shows "the same arc" as the timer — argued
in `dissent.md` item 2.

### The vocabulary — six states, named

| Name | Pattern | Numbers (all V until hardware) |
|---|---|---|
| `breathe` | sine brightness, waiting/listening | 4000 ms period, 15% → 45% brightness, owner hue |
| `arc` | solid gauge arc for magnitude | gauge-mapped 0–324°; edge feathered over 3 LEDs |
| `tick` | position marker travelling with the knob | 12° wide (~3 LEDs), gaussian edges, 1:1 with shaft |
| `wall` | end-stop flash | 80 ms at 100%, decay 320 ms, owner hue |
| `hold` | needs-you: solid, motionless | 60% amber, no animation — a held breath; resolves on press |
| `record` | solid dim red | 25%, never animated, never breathing (a blinking red light is an alarm; a still one is a fact) |

Plus `off`, the default. Six states, hard cap (the Nothing Glyph lesson,
section A).

### Avoiding the sixty-dot look

At 4 mm pitch behind a leaning diffuser: never drive a lone LED; every feature
spans ≥ 3 LEDs with gaussian falloff; apply per-LED calibration and gamma
before any pattern logic; move features by fractional-LED interpolation (the
tick's position is continuous, section B). If the diffuser still resolves dots
on a glossy desk, the fix is optical (diffuser geometry), not more software —
flag for the CAD track.

### Desk, room, night

Dark matte desks absorb: the glow footprint shrinks, so brightness caps rise.
Pale desks bounce: the halo can read from across a room. Glossy and glass desks
mirror the LEDs as point sources — the worst case; the down-angle and diffuser
must be validated on glass (prototype plan). Brightness: two global levels,
day and night, ratio ≈ 5:1 (V), switched by ambient sensor if the 3.4C board
has one — **unverified whether it does; check the schematic** — otherwise by
the companion app's clock. All halo brightness values in `tokens.md` are
percentages of the day cap so the palette survives recalibration.

### Halo versus screen

Same hue family, one animator at a time: whichever channel carries the change
moves; the other holds still. The single exception is the timer landing, where
arc-bloom and screen-settle fire together as the hero moment. Screen colour and
LED colour will not match from shared hex values — LEDs through a diffuser onto
wood are a different medium than an IPS panel (the in-plane-switching LCD) under
glass; `tokens.md` therefore defines each colour as a perceptual target with two
calibrated values, screen and halo.

### Grounding

The framing is Weiser and Brown's calm technology (["Designing Calm
Technology"](https://calmtech.com/papers/designing-calm-technology), 1995): the
halo is the periphery, the screen is the centre, and a state escalates by moving
from one to the other — never by getting louder in place. The Ambient Orb and
Philips' Ambilight research support the mechanism (peripheral colour is read
pre-attentively; light extending beyond a screen's frame is perceived as the
same object — which is exactly the halo-desk-screen relationship). Nest proved
hue-as-system-state on a dial; HomePod proved breathing-as-listening; Echo
proved the ring can point. All already absorbed into the six states above.

### Section D recommendations

1. **Gauge, not mirror**: halo magnitude anchors at the gap edges; position
   ticks stay 1:1 with the knob. Accept and design the gap rather than pretending
   it is not there.
2. **Six named states**, minimum feature width 3 LEDs, fractional-LED movement,
   per-LED calibration below the pattern layer. Numbers in `tokens.md`, all (V)
   until the diffuser is tested on dark, pale and glass desks.
3. **Escalation = migration**: periphery (halo) → centre (screen) → sound, in
   that order, never skipping straight to sound. Only `hold` (amber) and the
   timer's end may recruit sound at all.

---

## E. Sound

### Rules before palette

1. **Silence is the default.** The idle object never sounds. The turning ring
   never sounds from the speaker — the magnets already voice it, honestly, in
   sync, for free, and a speaker doubling them can only add latency and doubt.
2. **Sounds mark events the user caused or must notice.** Nothing else.
3. **One sound per 2 s maximum** (except `land`, the timer's end sequence).
4. **Relative loudness law**: UI sounds sit just above the acoustic level of the
   mechanical detent click heard at arm's length — measure the click first on
   the real assembly (prototype plan P6), then set gains relative to it. No
   absolute dB targets until then; an invented number here would be a fake spec.
5. The Mac startup chime is loved because it means "all is well" *once, at a
   moment of doubt* — its lesson is placement, not timbre. Its fixed loud volume
   is the part to refuse.

### The driver's physics

A small full-range driver through a Ø34 mm down-firing aperture, little output
below ~400 Hz: build weight from **harmonic implication, not fundamentals** — a
500 Hz fundamental with strong 1–1.5 kHz harmonics reads as a "thunk" though no
sub-400 Hz energy exists. Keep meaning in transients (5–20 ms attacks), energy
concentrated 800 Hz–5 kHz, decays short and dry (the down-firing bounce off the
desk adds its own small reverb — record prototypes through the real aperture
onto a real desk before judging them).

### The palette — eight sounds, named

All numbers are design targets (V) to be tuned on the real driver:

| Name | Event | Duration | Pitch envelope | Lands relative to haptic |
|---|---|---|---|---|
| `tick` | touch press (no magnet there) | 10 ms | 2.5 kHz filtered noise click | ±10 ms of actuator tick |
| `latch` | timer set-point captured (the kerchunk) | 140 ms | 500 Hz thunk transient falling ~1 semitone + 2 kHz mechanical tail | ±10 ms of actuator |
| `yes` | confirm | 160 ms | two 60 ms tones, 660 → 990 Hz (a fifth up), 40 ms gap | after the visual settle begins |
| `no` | deny / error | 120 ms | 440 Hz falling to 415 Hz (a semitone down), dry | with the shake |
| `land` | timer end | 1600 ms | three decaying strikes at 880 Hz + harmonic stack; repeats ×2 at 8 s, then silent | n/a |
| `hello` | USB connect / boot complete | 240 ms | 523 → 784 Hz rising pair | with the dot landing |
| `goodbye` | USB disconnect | 240 ms | mirrored falling pair, 784 → 523 Hz | with the glyph exit |
| `hail` | needs-you (call, agent permission) | 300 ms | single 660 Hz, soft 40 ms attack, played once only | with the halo `hold` onset |

`yes`/`no` and `hello`/`goodbye` are deliberate mirror pairs — the earcon
literature's strongest finding is that families built from a shared motive with
one varied parameter are learned fastest (Blattner et al., "Earcons and Icons",
Human–Computer Interaction, 1989; Brewster's earcon guidelines). `latch` leans
the other way, toward Gaver's auditory icons (SonicFinder, 1989): not a musical
motive but a *plausible mechanical event* — the sound a lockring would make if
the timer really were a bezel. The hero sound should be diegetic; the utility
sounds should be earcons. That split is the palette's design thesis.

Reference timbres to A/B against during tuning: the iPod clicker (dry, piezo,
never fatiguing), the Switch snap (short, certain, room-friendly), the Leica
shutter (damped mechanism — the model for `latch`), OP-1 confirmations
(pitched, tiny), Sonos connect (ends the conversation). Porsche's and McLaren's
start-up theatre is the anti-reference for everything except `hello` — and even
there, 240 ms, not four seconds.

### Timing law

Sound belonging to a haptic event lands within ±10 ms of it; sound belonging to
a visual event starts as the `settle` begins, not when it ends. Nothing ever
waits for a sound to finish.

### Section E recommendations

1. **The speaker never doubles the detent.** Rotation is voiced by magnets
   alone; the speaker exists for events. This also solves the 300-clicks/second
   problem outright — there is nothing to fall behind on.
2. Build the palette as **earcon families for utility, one auditory icon for
   the hero**: mirror pairs `yes`/`no` and `hello`/`goodbye` sharing a motive;
   `latch` designed as a plausible mechanism sound, tuned through the real
   aperture onto a real desk.
3. **Measure the mechanical click first**, then set all gains relative to it.
   Loudness is a relationship, not a number.

---

## F. Typography, iconography and the grid

### The typeface

Requirements: one family, true tabular figures, legible at 60 cm from 40–50°
above, licensable for embedding in a commercial hardware product.

- **Development and default recommendation: [Inter](https://rsms.me/inter/)** —
  SIL Open Font License 1.1, which permits embedding in commercial firmware at
  no cost; tabular figures via the `tnum` feature; optical sizes in Inter 4;
  proven at small sizes on screens. Licence status is the OFL's published terms —
  still confirm the version shipped carries the OFL text (V).
- **Brand-pass candidates** (evaluate before the box and website lock): Söhne
  (Klim Type Foundry), ABC Diatype (Dinamo), Neue Haas Grotesk (Monotype). All
  are commercial; embedded/OEM licensing for a hardware product is in every case
  **quote required** — none publishes a flat embedded price, and no figure
  should be assumed. A premium face is worth pursuing for the numerals alone,
  but Inter is good enough that the decision can wait without blocking anything.
- Watch-dial grounding: Nomos (restrained grotesk dials), Grand Seiko
  (legibility through contrast and polish, not weight), Sinn and instrument
  clusters (the register our numerals should sit in: certain, unornamented).

### Sizes, with the arithmetic shown

At 9.3 px/mm (derived at the top of this document) and 60 cm viewing distance,
1 mm on screen subtends ~5.7 arcminutes. Instrument-panel practice puts
glance-critical text at ≥ 20 arcminutes of cap height ≈ 3.5 mm ≈ **33 px
minimum for anything that must be read**. One more factor the brief is right to
flag: at 40–50° elevation the vertical axis foreshortens by cos(45°) ≈ 0.71, so
either accept it or draw glance-critical numerals ~1.2× taller than square (V —
test both on hardware; a slightly extended numeral may look *more* correct on
the desk than a geometrically round one).

| Role | Size (px at 800 × 800) | Notes |
|---|---|---|
| Timer / volume hero numerals | 260 (V) | tabular, two digits + colon fits inside r = 220 content disc |
| Ring-menu labels | 44 (V) | horizontal, never curved |
| Secondary / status | 33 (V) | the floor; nothing below this must ever need reading |
| Bezel minute numerals | 36 (V) | rotated radially like a dive bezel, tick-aligned |

### The radial grid

Centre origin, radii in px at 800 × 800 (all V pending the chamfer-shadow
check on hardware):

- r = 400 — physical edge under the chamfer.
- r ≤ 360 — safe area (40 px inset for the chamfer's shadow at desk viewing
  angle; verify by photographing the mounted panel).
- r = 352 — the green dot at twelve.
- r = 300 — ring-menu item centres.
- r = 268–340 — the outer scale band (bezel numerals, minute ticks: 60 ticks,
  one per detent, majors every 5).
- r ≤ 220 — hero content disc (numerals, bloom, album art).

Text on a curve: **no**, with one exception — the rotated bezel numerals on the
outer scale, following dive-watch practice. Everything else is horizontal at
radial positions, which is what Nomos and Grand Seiko dials actually do and what
Apple's circular-layout guidance for watchOS converges on (content in the
centre, furniture at the rim).

### Iconography

Line icons on a 48 px grid (V), stroke 3.5 px (V) to match the type's stem
weight at label size, terminals square (machined, not friendly-round). Angular
grammar: construct on 30° and 60° increments so icons rhyme with the detent
geometry (6° × 5 = 30°) — a hexagonal construction bias that quietly repeats
the object's own number. One icon size; scale by integer factors only.

### Section F recommendations

1. **Inter now; premium face as a brand decision later**, gated on a written
   embedded-licence quote. Tabular figures are non-negotiable in any candidate.
2. Adopt the radial grid above with the **33 px legibility floor** and the
   1.2× vertical stretch test for hero numerals at the real desk angle.
3. **Sixty ticks on the outer scale, one per detent**, majors every five — the
   screen's scale and the hand's scale are the same instrument, which is the
   porthole trick (section C) done with typography.

---

## G. One system: brand = product

### The thesis

The brand is not applied to the product; the product's own physics are the
brand. Sixty detents give the angle system (6°, 30°, 60°), the detent period
gives the motion system (120 ms beat), the design law from `docs/VISION.md`
(colour only ever comes from light, on a monochrome object) gives the colour
system, and the machined chamfer gives the family of curves. Everything in
`tokens.md` derives from one of those four physical facts. That is the
book-of-shapes idea (that a brand owns a family of curves) applied to a brand
that also owns a *number* (60), a *beat* (120 ms) and a *law* (colour is light).

### The family of shapes

Four shapes, recurring at every scale:

1. **The ring** — the knob, the ring menu, the halo, the box lid's emboss, the
   website hero, the companion app's volume element.
2. **The dot** — the selection dot at twelve, the notification dot, the "on"
   state everywhere, the one green element on the box.
3. **The chamfer** — the 45° (V — from CAD) bright edge; on screen as the baked
   rim light (section C), on the box as the lid bevel, in the app as the one
   bright hairline separating regions.
4. **The tick** — the 6° unit; minute marks, icon angles, the halo's travelling
   marker, the website's section rules.

Boot splash: the dial draws itself in wireframe (shapes 1 + 4). Box: black,
ring embossed, one green dot (2). Website hero: the face at 1:1 scale, dot at
twelve (1 + 2). Settings screen: rings of options, chamfer hairlines (1 + 3).
Same four shapes, no logo needed — which is the point of having no logo on
the face.

### Naming — one internal language

Plain lowercase English words, Braun's register, no code-names. Engineers,
designers and the manual use the same words:

- **Halo states**: `off`, `breathe`, `arc`, `tick`, `wall`, `hold`, `record`.
- **Sounds**: `tick`, `latch`, `yes`, `no`, `land`, `hello`, `goodbye`, `hail`.
- **Detent profiles**: `free` (motor off, bare magnets), `feather` (lightened),
  `firm` (reinforced), `wall` (end-stop), `ratchet` (patterned). Named as brand
  words because they will appear in marketing verbatim — "sixty firm clicks" is
  copy and spec in the same breath.
- **Device states**: `asleep`, `awake`, `listening`, `holding` (needs-you),
  `walled` (at a limit), `landing` (a capture moment), `recording`.

### Colour, stated once

Per the design law in `docs/VISION.md`: colour is ownership. **Green** = volume
and selection (the live, owned thing). **Amber** = seek and attention — these
two meanings collide and need a ruling; argued in `dissent.md` item 1.
**White** = the device itself (connections, position, boot). **Red** = mute and
recording only — never error, never alarm. Black is the object, not a colour.
Each colour ships as a perceptual target with two calibrated values (screen
and halo) in `tokens.md`.

### The state table

One row per state, four output columns — separate file, `state-table.md`, per
the brief's request that it be paste-able on one page.

### Rules for the companion app (Windows/macOS)

The app must be recognisably the same brand without cosplaying a round screen:

1. **Never draw a fake dial or a fake round screen.** The real one is on the
   desk; a rendering of it next to it would be the Taycan's fake gauges.
2. Same type, same sizes scaled by physical height (the app's labels should
   subtend roughly the same visual angle as the dial's — the dial's tokens are
   already in physical terms via 9.3 px/mm).
3. Same colour law: near-black neutral surfaces, colour only for state, the
   same four hues, one green dot marks the active/selected thing everywhere.
4. Same motion tokens: `settle` and `exit`, the 120 ms beat, nothing animates
   that the user did not cause.
5. Circles appear only as complete elements (the dot, a progress ring) —
   never as decorative arcs pretending the window is round.
6. The chamfer becomes the app's one bright hairline rule between regions.
7. Sound: the app is silent; the dial is the only thing in the system that
   speaks. Two devices chiming is a committee.

### Reference systems that do this well

Apple HIG (one token system across watch, phone, box and store), Teenage
Engineering (industrial design, UI sprites, packaging and website visibly one
hand), Braun/Rams (the dot-and-line language surviving fifty years), Nothing
(dot-matrix carried from LED hardware to OS to packaging — the vocabulary-size
failure is separate from the coherence success), Porsche (one silhouette, one
instrument layout, held for decades), Leica (a red dot rationed so hard it
means something), Bang & Olufsen (aluminium as interface), Polestar and Rivian
(digital-first brand systems where app, vehicle UI and web are one grid).

### Section G recommendations

1. **Derive, don't decorate**: every token traces to one of the four physical
   facts (the 60/6° geometry, the 120 ms beat, the colour-is-light law, the
   chamfer). Anything that cannot cite its parent fact is out.
2. Adopt the **four-shape family** (ring, dot, chamfer, tick) as the entire
   graphic identity — face, box, website, app — in place of a logo.
3. Freeze the **naming** now and use it in code, docs and marketing unchanged;
   `tokens.md` is written to be that single source.
