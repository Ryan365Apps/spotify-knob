# the 60 — what to change for v6c, and why

**Date:** 2 September 2026. **What was reviewed:** the software contexts document (the one that makes the knob a scroll wheel by default), the sourcing document for the 60-unit run, the decisions index, and the four research answers in `docs/Research/` — the detent mechanism, the headphone DAC and audio, the industrial design references, and the screen/light/sound design. **Measured against:** the current v6b model — 135 mm across, 33.9 mm tall, the knob 76 % of the visible side, every automated check passing.

This is a proposal, not a build. Nothing in the model has been changed yet. Each change below says what it costs in height, what it costs in parts or power, which earlier decision it touches, and what has to be measured before it is final. Anything marked **(unverified)** is a number I have not been able to confirm.

---

## The short version

There are seven changes. Three come from your rulings, four from the research.

1. **Make the clicks adjustable in a tenth of a second, using the magnets rather than the motor.** Split the six magnets into two groups of three and slide the groups apart by half a click spacing. Click strength goes from full to zero smoothly, holds without power, and costs about a thousandth of the energy of having the motor fight the clicks. This is the change that makes the "rest a finger to free the knob" idea possible on USB power.
2. **A complete 360° ring of light.** The USB-C and headphone sockets move into a low tunnel at the back of the base, under the light ring, so the ring no longer needs a gap for them. Cables leave at desk level from the back, the way a HomePod's does. Costs 2.5 mm of height.
3. **Make the ring of light brighter the right way.** The "20 % cap" was a guess sitting on another guess. The real losses are in the plastic and the geometry, not the current. Fix the optics first, define brightness in real units, let the firmware read what the USB port can give, and add a dedicated white light source that is three times as efficient as the colour LEDs.
4. **Let the click mechanism change the light's spread.** Three ways to do it; the two mechanical ones are drawn, the electronic one is recommended first as the benchmark the mechanical ones have to beat.
5. **Fix the wheels.** The wheel in the model does not exist as a stock part. Use a standard 3 × 10 × 4 mm bearing with a turned collar, and shape the knob so that a single thin ring bearing can replace the three wheels on the machined production unit.
6. **Fold in the research corrections** — magnet orientation, the material of the steel pegs, the audio chip, the knurl, the surface finish, an index mark for the position sensor.
7. **Add weight.** A steel ring in the floor of the base (+141 g) and a brass ring hidden in the knob (+40 g), to about 630 g total. No height.

Result: about **34.0 mm tall** (v6b is 33.9), the knob **72 %** of the side (was 76 % — the four points go to the plinth that hides the cables), one steel plate with a notch at the back, the same number of printed parts. If the ring motor is added later it needs 3 mm more, giving 37 mm — under the 40 mm ceiling.

---

## 1. What making the knob a scroll wheel does to the hardware

The software document now says: by default the knob scrolls whatever is on screen, and when you rest a finger on the "feel" spot the clicks should fade out until the knob spins freely like a flywheel. It is honest about the consequence: *the ring motor must fully cancel the clicks while the knob spins, for as long as the finger rests there, within the USB power budget.*

The detent research puts numbers on that and they do not add up. The clicks as drawn have a strength of about 74 mNm (a millinewton-metre is the unit for how hard a knob resists turning; 74 is a firm watch-bezel click at this size). The motor that fits inside the object makes about 65 mNm for a moment at 5 watts, and can only sustain 30 to 60. So it cannot reliably cancel the clicks, and trying costs the whole 5 watts that the light ring is already short of. The research's own error band on the click strength is −40 % to +65 %, so the real number could be worse.

Four things follow.

**Cancelling the clicks is the magnets' job, not the motor's.** Change 1 does it passively. The motor is then only ever adding the fast, brief effects on top — a wall at the end of a range, rising resistance near a limit, a half-click — which is exactly the control scheme the detent research recommends (render the difference between what you want and what the magnets already give; do nothing when they agree). The motor can be specified at the 30 mNm the research thinks a printed-circuit-board motor can reach, instead of having to beat 74.

**Free spin is now a feature, so drag and weight matter.** A flywheel feel needs low friction when off a click and high inertia. The coast-down test on the bench rig (spin it, time how long it takes to stop) is now the first test to run; the hidden brass ring in the knob stops being optional; and wheels versus a ring bearing has to be judged on drag as well as wobble.

**Position sensing.** Smooth scrolling and the moving light tick both need the knob's position between clicks, continuously. The optical sensor in the sourcing document reads about 10,000 positions per turn (0.036° each): fine for scrolling, a little coarse for the motor's control loop, which the research wants at 0.022°. Either way the sensor needs an **index mark** — a single reference point on the knob — so that when the device powers up it knows where the clicks are without having to nudge the knob to find out. The sensor variant with an index built in has an 18-week lead time; the alternative is one printed mark on the knob read by a second cheap sensor.

**Touch.** The display's touch controller handles ten fingers. The grips the software lists — thumb on the side, a hand resting alongside, an outstretched finger, a fingertip on the top rim — need the firmware to ignore a resting palm while the ring moves under other fingers. That is a firmware test, not a shape change. The 5.9 mm flat rim on top should not get narrower: the industrial design research found the rim grip is the only one that keeps the hand clear of the screen.

The software document still has two buyers in it (Windows and Teams, or Mac and Meet). Nothing here depends on which one wins.

## 2. A complete ring of light — the cable tunnel

**Your objection is right, and for a second reason as well.** The 36° block takes 10 % of the circumference away from any scale drawn on the ring. Worse, the block sits at twelve o'clock — the one angle the screen already owns with its green selection dot — so the light research had to invent a workaround ("start the arc at the edge of the gap") purely because of where the sockets were. The industrial design research argued the gap was a feature, an instrument arc with a zero and a maximum, and recommended against a full ring. That argument only holds while the gap is a deliberate arc end. Once the sockets no longer need the band, it is just an unexplained dark patch at the top.

**Where the sockets go.** They stay at the same height above the desk — the USB-C socket centred 2 mm above the steel plate's underside, the headphone socket about 2.25 mm — but move inward, into a **pocket in the back of the base**: 34 mm wide, open at the bottom, from the desk surface up to 6 mm, with its back wall about 46 mm from the centre. The plug bodies lie inside the pocket; the cables come out at desk level at the back. The light ring moves up to sit 6 to 9 mm above the plate underside (the side-firing LEDs are 2 mm tall, so a 3 mm band is enough) and runs the full circle above the pocket. What you see below the knob, from the desk up: the 1.5 mm rubber pad, the 3 mm steel plate edge, a **3 mm dark plinth band**, the 3 mm ring of light, then the 0.6 mm shadow gap under the knob. The plinth is the "crisp knife-edge bottom line" the industrial design research asked for, and its 3 mm is what pays for the tunnel's headroom.

The numbers: a USB-C plug body is typically 6.5 mm thick and 11 mm wide (slim ones 5.5 mm). Centred on the socket it spans from 1.25 mm below the plate underside to 5.25 mm above — inside the pocket, which runs from 1.5 mm below (the pad is notched too) to 6 mm above. A headphone plug body is 6 to 8 mm across; at 2.25 mm up, a 7 mm body fits under the 6 mm ceiling, and an 8 mm body needs the ceiling raised to 6.5 mm at the headphone socket only. Two cables side by side need 11 + 8 + gaps ≈ 31 mm; the pocket is 34. The steel plate loses a 34 × 14 mm notch at the back (11 g); the pad is notched to match.

**One "port board" carries everything at the back.** The audio research wants the headphone socket on the same small board as the audio chip, with a very short signal path; the sourcing document wants the USB-C socket lying within the plate's thickness. Put both on **one board, about 40 × 14 mm, sitting in the plate's notch**: the USB-C socket (a mid-mount type 3.16 mm tall), the small USB hub chip, the Cirrus CS43131 audio chip (5 × 5 mm — the audio research's pick over the ESS part in the sourcing document, because the ESS part's supply is thin), the right-angle headphone socket (14.5 × 6 × 5 mm; its barrel height must be checked against the tunnel ceiling), the surge-protection parts, two small voltage regulators, and the ambient light sensor looking out through a 2.5 mm hole in the plinth. All grounds meet at one point at the USB-C socket, and the steel plate is connected to ground there and nowhere else — the audio research is firm on this, because the USB ground is the PC's mains earth. If the processor's own USB audio turns out not to be good enough (a one-week test), the extra bridge chip needs another 10 × 10 mm; allow 50 × 14 for the board.

Cost: 2.5 mm of height, one notch in the plate, one in the pad. Benefit: a continuous ring, a real twelve o'clock, hidden cables, and the light ring's underside no longer has to carry sockets.

## 3. Brighter light — what is actually limiting it

**The cap was the wrong unit.** "20 %" meant 20 % of an undefined maximum, chosen because the design assumed a 500 mA USB port that nobody measured. Every light state in the screen/light research is written as a percentage of a "day cap" that has never been defined in real units, and the industrial design research gives no brightness figure either. So, the physics first.

- A full ring at 57 mm radius is 358 mm long: **90 LEDs at 4 mm spacing**, or 45 at 8 mm.
- What the desk needs: the lit area on the desk (from the base edge out to about 110 mm from centre) is about 260 cm². Adding 300 lux across it — clearly visible in a normally lit office of 300–500 lux — needs only **about 8 lumens landing on the desk**. Allowing for a realistic 25 % of the light making it out through the plastic and geometry, that is **about 30 lumens emitted**. Night is a fifth of that.
- What the parts make, at full and at 20 % (datasheet-class figures, order of magnitude): the side-firing 4020-size RGB LEDs currently assumed give about 540 lumens at full for 3.2 amps, so 108 lumens at 20 % for 0.65 amps. The RGBW version with a real white chip gives about 810 at full. A row of ordinary mid-power white LEDs (the kind in good desk lamps) gives about **120 lumens per watt against 35–45** for the addressable colour parts.

So at 20 % the ring already makes three to five times what the desk needs — **if the optics let it out**. A 36 %-transmission opal diffuser, a black skirt behind the LEDs and a printed plastic ring can lose 80 % of it. That is the most likely reason a rig halo looks starved. The power problem is real only for the coloured *sustained* states: the amber "needs you" hold at 60 % on a 90-LED ring is red plus green at about 1.3 amps.

**The proposal, in order of value:**

1. **Optics first.** A 3 mm opal with 83 % transmission (the industrial design research names PLEXIGLAS Satinice 0D010 DF) instead of the 36 % grade; white solder mask on the LED board and white channel walls (recovers 17–45 % of the light the diffuser bounces back); at least 4 mm between the LEDs and the diffuser's inner face, because the current 1.5 mm will show the LEDs as dots at 4 mm spacing. Expected gain: two to three times more light on the desk for no extra power.
2. **Define the day brightness in lumens** — I suggest 60 lumens emitted, three times the need, and 12 at night — and give the firmware a **current governor**: a piece of code that turns any requested light state into LED current and scales it to fit a measured budget. The governor is what makes "brighter than 20 %" safe on a good port and harmless on a bad one.
3. **Know what the port can give.** A USB-C source tells the device whether it can supply 1.5 or 3 amps at 5 volts through a voltage on the cable's CC pin; reading it at boot needs no extra chip. A USB-A-to-C cable shows the default: 500 mA, or 900 mA on a USB 3 port. Set the governor from that. A Power Delivery chip (about 30 p, 3 × 3 mm) that asks for 9 volts is only worth adding if the ring motor turns out to need it; the light does not.
4. **A separate white light source.** Keep the addressable colour LEDs for the colour language, at low duty. Add a second row of 24–30 mid-power white LEDs on the same ring board, on one dimming channel, for the "lamp" state: 60 lumens for half a watt. This is the part that splits *lamp* from *language*, so the two never share a budget.

With those, a phone-call ring (light breathing at 45 %, vibration, speaker at 2 watts peak, screen at full) fits a 7.5-watt port; everything at once needs 15 watts. That is what the power research must confirm with a USB meter on the real board. The power brief is written and its questions D and E are exactly this; this section is the working hypothesis for it, not a replacement.

## 4. Letting the click mechanism change the light

Your ask: when the clicks change, the light's angle should change too, spreading it across the desk. Two research strands are against it. The decision index says, as decision 47, that the light is not mechanically coupled to the magnet carrier and should instead be choreographed in software, leading the mechanical clunk by 80 ms. The screen/light research says moving parts for theatre break the longevity promise, and that if a bystander's eye is drawn to the dial when nobody is touching it, that is a bug. Those are real costs, not taste. Three ways to do it, rated honestly:

**A — a diffuser ring that drops.** The opal ring hangs from three pins that reach up through the base roof to ramps on the same ring that moves the magnets. Clicks on: the opal sits high, mostly hidden in the shadow gap, a 1 mm line of light. Clicks freed: the opal drops 2 mm, showing 3 mm, and because it leans outward the light now leaves lower and reaches further across the desk. The object visibly *opens* when the feel frees. That is a genuine physical tell of a state the hand can feel, not theatre. Costs: a moving translucent part on the outside (a dust shelf and a seam, and it needs a spring to return), the shadow gap varies between 0.6 and 2.6 mm, and light leaking into the gap makes the knob look as if it is floating, which the industrial design research warns against. No height. My view: the closest match to what you asked for, and the riskiest part on the object.

**B — a hidden rotating shutter.** The moving ring extends down inside the light band as a thin ring of alternating clear and frosted windows at the LED spacing; the ring's 14° of travel is three and a half windows, so every LED swaps from a clear window (narrow, bright, close to the base) to a frosted one (wide and soft). No external moving part; the change is real but subtle; the windows have to be laser-cut acrylic, not printed. No height.

**C — two rows of LEDs.** A second row on the ring board aimed at the lower part of the diffuser; "spread" becomes a software state with the 80 ms lead decision 47 asks for, and the current governor pays for it. No mechanism, no risk, and it is the control experiment the other two have to beat.

Recommendation: build **C** in v6c (it is a change to the LED board), draw **A** as an optional part with its own checks, and decide on the rig with the light on over a dark desk and a glossy one. If A wins, decision 47 gets amended with evidence.

## 5. The click mechanism — fast, and powered by the magnets

**Why the magnets can do it for free.** The clicks come from six magnets in the base pulling on sixty steel pegs in the knob. All six magnets line up with pegs at the same instant (sixty divided by six is a whole number), so all six pull together and you feel one firm click every 6°. A magnet does not care which way round the steel is; it only wants to sit opposite a peg. So if three of the six magnets are slid sideways by half a peg spacing — 3°, which is 1.6 mm at their radius — those three want to sit *between* pegs at exactly the moment the other three want to sit *on* pegs. The two pulls cancel and the clicks vanish. Slide them only part of the way and the click is weaker: a quarter of the way gives about 70 %, half gives 50 %, three quarters about 30 %, all the way gives none. One sideways movement of 1.6 mm sets the click strength anywhere between full and nothing, smoothly, without lifting anything.

**How it is built.** The magnets no longer sit in fixed pockets. Each sits in a small sliding shoe on the same ring as before, free to move 0.8 mm each way sideways, held in by lips. Each shoe has a pin reaching down into an angled slot in a thin ring underneath. Turning that lower ring by about 14° pushes three shoes one way and three the other by 1.6 mm each. Both sets move, in opposite directions, so the knob's rest positions stay exactly where they were. That symmetry matters: if only one set moved, an untouched knob would creep a quarter of a click every time a call arrived. The lower ring is turned by the same small gearmotor as now, with a plain gear instead of the slow worm gear; a 30:1 gearbox at 730 rpm does the 14° in about 90 ms. The slots are angled at about 8° to the ring — shallow enough that the magnets' own sideways pull (about 0.6 newtons per group when fully cancelled) cannot push the ring back — so it holds wherever it is put with no power at all.

**What it costs and saves.** One full swap takes about 150 millijoules of electricity — what a small LED uses in a second — of which only about 2 millijoules is actual work against the magnets. Having the motor fight the clicks for an hour of scrolling would take about 18,000 joules; six hundred swaps an hour take 90. That factor of two hundred is what makes the finger-on-feel idea possible on USB power. Because the magnets now do the heavy, continuous work, the ring motor only ever adds the brief effects and can be smaller and cooler. Firmware can map finger pressure or knob speed to a slot angle and let the carrier follow at ten updates a second, with the motor smoothing only the last hundred milliseconds.

**Height.** The lifting travel, its ramps and followers go: the lower ring is 1.5 mm (was 4). But the research also found the magnets must stand on their 6 mm edge — the other way round loses more than three quarters of the click strength — so the carrier ring grows from 4.9 to 7.5 mm. Net: the click band is 9.0 mm instead of 9.9. The pegs are now always centred on the magnets instead of being a compromise between a raised and a lowered position.

**What it does to the research's own problem.** The detent research found that lowering the magnets 3 mm only halves the clicks (52 % left) and asked for 4.5 mm of travel to get them below 11 %. With the sliding groups, what is left in the cancelled state depends on how well the two groups of three match each other, not on travel: two groups within 10 % of each other leave under 5 % (about 4 mNm), far below the rig's pass mark of 30. The 4.5 mm travel and its height are withdrawn.

**The risks, plainly.** The "clean wave" shape of the click is a model prediction; if the real click has a second, faster ripple in it, that ripple *adds* rather than cancels and the freed state keeps a faint texture. Measure it on the rig with the groups fully shifted. The shoes are sliding plastic in the magnet path; the industrial design research forbids plastic in the *torque* path, and the shoes do not carry the knob's torque, but each one has its magnet's 0.7 newton pull riding on its lips — use acetal or PEEK shoes, or a brass carrier on the machined unit. There are now six more sliding fits inside the ±0.05 mm concentricity budget, and the research's warning that ±0.1 mm of runout is ±15–20 % of click strength applies to each shoe. And while the groups are moving, the knob is briefly held by one set alone: at normal turning speeds this is felt as one click that goes soft, which is what the screen/light research wants ("feel leads sight by about a third of a second").

**Which decisions this touches.** Decision 19 (dynamic click strength comes from the motor, because a screw cannot move in a tenth of a second) — the premise no longer holds; sustained strength goes to the carrier, effects under 100 ms stay with the motor. Decision 20 (the magnet ring moves a few times an hour) — now a few times a minute, cheaply. Decision 26 (the carrier moves vertically, about 2 mm) — now sideways, 0.8 mm each way. Decisions 27 and 28 (holds position with no power; strength is continuously adjustable and survives a power cut) — kept exactly. Decisions 30 and 31 (motor and magnets designed together; the motor is a custom ring) — unchanged. Sourcing is unchanged: sixty pegs, six magnets, plus six small shoes.

## 6. Wheels versus a ring bearing

**The wheel in the model does not exist.** Every stocked V-groove wheel of this type is 3 mm bore, **12 mm** outside, 4 mm wide; the 10 mm version is one American seller. Two fixes: move the three posts inward by 1 mm for a 12 mm wheel, or keep 10 mm with a plain 3 × 10 × 4 bearing (NSK or SKF, about £2) and a turned V-shaped collar over it. The sourcing document's recommendation is the right one: a turned acetal or PEEK collar over a branded bearing is the only way to get a precision race, it lets the groove angle be tuned to the ridge on the knob, and it is a two-minute lathe job for whoever machines the knob. **Adopt the 3 × 10 × 4 bearing with a 12 mm collar, posts at 51.9 mm radius.** The main board's short edge is 42.75 mm from centre at the 0° post and its long edges 32.5 mm from centre at the 120° and 240° posts; a 12 mm wheel at 51.9 clears both. The USB-A socket that overhangs the board is still unverified.

**The real question is three wheels or one ring.** Wheels won earlier because a ring bearing would have had to surround the 115 mm display disc. In the deep-cup design that is no longer true: a thin ring bearing can sit *below* the disc, between the base and the knob's skirt, at about 19.5 to 26 mm up. A four-point-contact thin-section bearing of 114.3 mm bore, 127 mm outside and 6.35 mm wide (the Kaydon KA045XP0 size, made by several firms) fits: the four disc posts on their 104 mm circle pass through its bore, and the main board's 107.4 mm diagonal sits inside it. "Four-point contact" means one bearing resists tilting on its own, which matters when a heavy knob is pushed on one side. The knob's skirt would step out from 61.4 to 63.5 mm radius above 19.5 mm, leaving 3.5 mm of wall to the knurl — fine in aluminium, marginal in printed plastic. The race is 6.35 mm tall against the wheels' 4, so 2.4 mm more height.

| | Three wheels in a V-ridge | Thin-section ring bearing |
|---|---|---|
| Wobble at the rim | set by three printed or machined posts and a machined ridge; a three-lobed wobble is a named rig test | set by the race: about 0.02–0.04 mm for import grade, better for RBC/Kaydon |
| Play | none axially if the ridge is preloaded; sideways set by post tolerance | none in any direction with light preload |
| Drag when spun | lowest — three rolling contacts, no seals | higher — seals and a full set of balls (open type is lower) |
| Noise | three points can tick on a printed ridge | silent |
| Cost | 3 × £2 plus collars | import grade tens of pounds; RBC/Kaydon-brand via MISUMI, quote needed **(unverified)** |
| Prototype | prints today | needs the stepped skirt and a seat in the base |

Recommendation: **wheels for every printed unit, and shape v6c so the bearing drops in** for the machined unit — a step in the skirt and a seat in the base, switched by one parameter. The rig's wobble test (0.05 mm at the rim) and the coast-down drag test decide. That is the "print both and compare" that decision 41, the open wheels-or-race question, already asks for, without maintaining two models.

## 7. Research findings folded into v6c

| What | v6b | v6c | Where it comes from |
|---|---|---|---|
| Magnet orientation | 3 × 6 × 3 mm "facing outward", not pinned | 3 mm radial × 3 tangential × **6 tall**, magnetised outward, all six the same way, stated on the drawing | detent research: worth a factor of 4.4 |
| Magnet grade | N42 | N42; N52 as a shim-level option **(unverified)** | detent research: +24 % |
| Steel pegs | M2.5 × 2.5 grub screws, "steel" | **M3 turned flat-point studs in free-cutting mild steel** (EN1A), 3 mm across; 3 mm chrome-steel balls in blind holes tested alongside | detent research: standard hardened grub screws add grit, stainless kills the click; +27 % from the bigger face. Sourcing document: balls are cheaper and more consistent |
| Magnet-to-peg gap | 0.8 mm | 0.8 nominal, shoes shimmable to 0.6; combined concentricity ±0.05 mm | detent research: strength goes as gap to the power −1.5 |
| Carrier travel | 3 mm vertical | none — sideways groups | section 5 |
| Position sensor | optical, no index | optical plus an index mark | detent research: power-up alignment without a homing nudge |
| Ring motor space | none | reserve a 3 mm annulus from 54 to 61 mm radius on top of the base, under the knob's flange, with cut-outs at the three posts **(unverified)** | detent research: printed-circuit-board motor with rotor magnets in the flange |
| Audio chip | ES9219Q (sourcing document) | **Cirrus CS43131** on the rear port board; the processor's own USB audio kept as a one-week kill-or-keep test | audio research: ESS supply is thin |
| Headphone socket | generic 6 mm barrel, 4 mm up | Same Sky SJ-3524 right-angle, 14.5 × 6 × 5 mm, about 2.25 mm up, with a plug-detect switch | audio research |
| Grounding | — | one ground point at the USB-C; plate bonded there only; separate ground areas for radio, audio, motor and LEDs | audio research |
| Wheel | 10 mm V-wheel | 3 × 10 × 4 bearing + 12 mm turned collar, posts at 51.9 | sourcing document finding 1 |
| Diffuser | 36 % opal at 58.5 mm radius | 83 % opal, 3 mm, at least 4 mm from the LEDs, white channel walls | industrial design research |
| Outward lean of plate and diffuser | 22° | **8° at most** — past a few degrees the object looks as if it is hovering | industrial design research |
| Rubber pad | full face, 1.5 mm | set in 6–10 mm from the edge; nitrile or neoprene, not silicone (silicone does not stick to tape) | industrial design research; sourcing document |
| Shadow gap under the knob | 0.6 mm | keep it dark: matt-black inner faces and a baffle between the light channel and the gap | industrial design research |
| Knurl (machined unit only) | 56 teeth, 1.2 mm deep | diamond pattern at about 1.0 mm pitch (420 points), 0.28–0.30 mm deep, a 0.8 mm plain band at each end, cut before anodising; rim reeding 600 teeth at 0.7 mm | industrial design research |
| Finish | "anodised" | **Type III hardcoat anodising** on a 6000-series alloy, bead-blast recipe agreed on test panels; the bright diamond-cut chamfer must be **sealed** (clear lacquer or clear anodise) or it will corrode | industrial design research |
| Weight | 254 g plate | plus a 3 mm steel ring in the floor from 20 to 48 mm radius (141 g) and a 40 g brass ring in the knob → about 630 g with a 180 g aluminium knob | industrial design research; sourcing document |
| Ambient light sensor | none | one behind a 2.5 mm hole in the plinth | sourcing document; light research |
| Speaker | 2 W generic | kept; never plays a click to double the magnets; useful range 800 Hz–5 kHz | screen/light/sound research |
| Light ring | 324°, 20 % cap | 360°, brightness defined in lumens, current governor, two LED rows | sections 2 and 3 |

Deliberately *not* folded in: the fine knurl is a taste decision — you asked for chunky diamond knurling twice, and the research says a fine pitch reads "precise" while depth is what reads "aggressive". Its numbers go on the machined unit only; the printed knurl stays coarse because a 0.3 mm deep knurl does not print. The industrial design research's "more than 1 kg" weight floor is an estimate with no measurement behind it; 630 g is what the geometry gives for no height, and a 5 mm plate reaching 800 g costs 2 mm. The 120-step half-click mode: the industrial design research doubts you can feel a 3° step against 6° magnets; with the sliding groups the leftover click is near zero so the mode is at least physically honest. It stays experimental.

## 8. Which earlier decisions change

| Decision | What it says | After v6c |
|---|---|---|
| 19 | Dynamic click strength comes from the motor, because a screw cannot move in a tenth of a second | **Amended**: a slotted ring does; sustained strength to the carrier, effects under 100 ms to the motor |
| 20 | The carrier moves a few times an hour | **Amended**: a few times a minute, about 150 millijoules each |
| 26 | The carrier moves vertically, about 2 mm | **Replaced**: sideways, 0.8 mm each way, two groups in opposite directions |
| 27, 28 | Holds position without power; continuously adjustable | Kept |
| 29 | Click strength 60–150 mNm, design for the top of the range | Kept; the top of the range no longer conflicts with half-clicks |
| 41 | Wheels or a ring bearing — open | Still open, now with a drop-in path for both |
| 43 | The light fires down and outward from the fixed base | Kept |
| 47 | The light is not mechanically coupled to the magnet carrier | **Under test** (section 4): option C keeps it, option A amends it |
| CAD brief item 5 | The six magnets and sixty pegs are the motor's magnetic circuit | **Withdrawn**: the detent research shows that machine can only modulate click strength by a few per cent, never drive |
| — | The 36° port block (v6a.2) | **Replaced** by the rear tunnel |
| — | The 20 % light cap (vision document) | **Replaced** by a lumen target and a current governor |

## 9. The height budget after v6c

Heights are measured from the underside of the steel plate; the rubber pad sits below at −1.5 mm.

| Height (mm) | What is there |
|---|---|
| 0 – 3 | steel plate, 122 mm across, with a 34 × 14 mm notch at the back for the tunnel (243 g); steel ring inside the floor from 20 to 48 mm radius (141 g) |
| −1.5 – 6.0 | the rear cable tunnel, 34 mm wide, back wall 46 mm from centre; the port board at 0.4–3.6 |
| 3 – 6 | the dark plinth band, with the light-sensor hole |
| 6 – 9 | the ring of light: 90 side-firing LEDs and the white row on a ring board at 56.5–57 mm radius; opal from 61 to 62 mm, leaning out no more than 8°, all the way round |
| 9 – 10 | the base roof |
| 9.6 | bottom edge of the knob's skirt (0.6 mm shadow gap) |
| 10 – 11.5 | the slotted ring that moves the magnet shoes (14° of travel; gear teeth on a tab) |
| 11.5 – 19 | the carrier ring with six shoes; magnets from 12.5 to 18.5; steel pegs at 15.5 |
| 19.1 – 20.3 | position sensor and index reading the skirt's inside face |
| 20.5 | the knob's flange (with the step for the ring bearing above it, if that variant is built) |
| 21.4 – 25.4 | three bearings with 12 mm collars on posts at 51.9 mm radius |
| 25.9 – 31.9 | the display disc; the main board hangs below it to 16.9 |
| 32.3 – 34.0 | the knob's rim |

**34.0 mm tall, the knob 72 % of the side.** Add 3 mm if the ring-motor annulus is reserved (37.0), 2.4 mm if the ring bearing replaces the wheels on the machined unit (36.4), both (39.4 — right at the line).

## 10. What to measure before any of this is frozen

Each is about an afternoon on the bench rig or with a datasheet.

1. The shape of the click and what is left with the groups fully shifted. Pass: under 5 mNm.
2. Whether the angled slots hold without creeping, in printed and acetal shoes, with the knob parked a quarter of a click off centre for 24 hours.
3. Swap time and current with the 30:1 gearmotor and gear, and the sound it makes — decision 70 says the mode-change sound is a marketing asset, and this is that sound.
4. The opal's transmission and whether the LEDs show as dots at 3 mm and 4.5 mm spacing, on a dark desk, a pale one and a glossy one; lumens on the desk with a light meter — this defines the day brightness.
5. What your own USB ports advertise on the CC pin (desktop rear, front header, laptop, dock), with a USB meter — question B of the power brief.
6. The headphone socket's barrel height against the tunnel ceiling; the plug body sizes of the cable that will actually ship.
7. The touch controller's palm rejection with the ring turning under the hand.
8. Rim wobble and the three-lobed ripple with 12 mm collars on printed posts — the number that decides wheels versus bearing.
9. Carried over from v6b: the display disc's rear mounting-hole circle (assumed at least 103 mm), where the display's flat cable exits, and the USB-A socket's overhang.

## 11. Where I disagree with the research

- **"The 36° gap is a feature."** Only while it is a designed arc end. With the sockets gone it is an unexplained dark arc at twelve o'clock. Overruled by section 2.
- **"More than 1 kg."** An estimate with no measurement behind it. 630 g of steel and aluminium in a 135 mm object already reads as permanent. Decide by hand.
- **"No moving parts for theatre."** Right as a rule. Option A in section 4 is not theatre if it is tied to a state the hand can feel — but it has to earn its place against option C on the rig.
- **"Design the carrier for 4.5 mm of travel."** Withdrawn by the sliding groups, which reach near-zero with no travel at all.
- **"Momentary feel is the motor's job"** (software document). Contradicted by the detent research's own motor numbers. Section 5 moves the sustained job to the magnets.
- **The audio research's 1.5-amp assumption.** Every audio file assumes 5 volts at 1.5 amps without saying where the figure comes from. The power brief must settle the budget before the port board is laid out.
