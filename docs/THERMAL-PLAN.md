# the 60 — thermal architecture: the base plate as the heatsink

**Date: 5 September 2026. Status: design proposal, for approval before it enters the specification.** Revised the same evening to Ryan's second proposal — a one-piece black anodised aluminium base plate, the 3 mm duct machined out of the plate's own thickness rather than added to the object's height, an 8 mm lip retained at the outside for the rear plug bodies, ribs on the plate's top face, the heat-generating parts bolted to the plate, an exhaust port and a fan. Superseded text has been removed, not struck through.

Read with `docs/SYSTEM-REVIEW.md` section 1.1 (why the object cannot currently reject its own heat) and `docs/v10/V10-SPECIFICATION.md` section 6.9 (the vent analysis this replaces).

**Verdict: the revised proposal is materially better than the first version and it is the architecture to build. Machining the duct out of the plate costs no height, turns an open slot into a real duct with walls, and removes the tipping problem entirely. Aluminium and black anodising are worth about 0.1 W/K for free. The costs are 0.46 kg of mass, which can be partly bought back, and a fan — which is still needed, because the material change alone does not close the gap.**

---

## 1. The problem being solved

`SYSTEM-REVIEW.md` 1.1: the sustained load is 12 to 14 W; the object's passive skin is worth about 0.4 W/K at best; that is a rise of over 30 K; and **IEC 62368-1 caps a bare-metal knob at 51 °C touched occasionally and 48 °C held for over a minute, measured at a 25 °C room.** The object as designed lands at or over that limit.

The review also showed why the intuitive fix is closed: the knob is the largest external surface, so conducting heat into it is the obvious answer — and it is the exact surface the standard caps. **The largest radiator in the object is the one you are not allowed to make hot.** That leaves air, and it leaves the base plate.

---

## 2. Answering the question directly: what are the vertical vent slits doing?

**Nothing in the cooling path. They stay acoustic.** The contradiction was in my description, not in the plan.

There is exactly **one** forced-air path and it lives entirely **below the plate's web**:

```
room air ──▶ intake slots machined through the rim, front and sides
          ──▶ the 3 mm duct, across the fin channels
          ──▶ blower at the rear
          ──▶ exhaust slots machined through the rim at the rear
```

**The web has no holes in it.** The forced stream never enters the object's cavity, never passes the panel, never passes the encoder, and never reaches the 89 perimeter slits.

The cavity above the plate is a **separate volume**. It is not hermetic — it breathes to atmosphere through those same 89 acoustic slits, at essentially zero velocity, driven only by buoyancy. That is the important distinction and it is what "sealed" meant: **the cavity is not in the forced path.** Dust settles into it slowly, as it would into any desk object, rather than being driven through it at a litre a second for ten years.

The slits keep the job they already have — the speaker's acoustic port — and nothing about the audio design changes.

---

## 3. The physics that sets the design

**Air under a hot plate does not convect.** A fluid layer heated from above is stably stratified: warm air sits at the top of the gap against the metal and stays there. Convection needs heating from below. So the duct, unfanned, moves heat only by conduction and radiation:

| Path, duct open, no fan | Conductance |
|---|---|
| 3 mm of still air, plate to desk | 0.15 W/K |
| 3 mm of rubber, plate to desk (what it replaces) | 1.15 W/K |
| **The desk itself**, spreading into wood from a Ø148 disc | **0.04 W/K** |
| Radiation, black anodised underside to desk | 0.10 W/K |

Rubber is the better conductor of the two, and it does not matter, because **the desk is the bottleneck either way at 0.04 W/K.** It is a blanket, not a sink, and nothing done to the pad changes that.

**The duct's value is that it is an air intake and a defined flow path.** Specification 6.9 already established that through-flow is the only mechanism that scales — *"0.5 L/s of air carries 0.6 W/K, more than the whole skin"* — and could not find a clean intake. Underneath is the answer: invisible, nowhere near the user's hands, nowhere near the display, drawing the coolest air in the room.

---

## 4. What the aluminium and the anodising actually buy

Three separate gains, and it is worth keeping them apart because only two are large.

**Black anodising is the big free win — emissivity.** This is the number that changes:

| Finish | Emissivity | Radiative coefficient |
|---|---|---|
| Polished aluminium | 0.05 | 0.3 W/m²K |
| Mill or powder-coated steel | ~0.25 | 1.6 W/m²K |
| **Black anodised aluminium** | **0.88** | **5.5 W/m²K** |

That is an eighteen-fold improvement on bare aluminium and a three-fold one on steel, and it applies on **both faces**: the underside radiating to the desk, and the plate's top face radiating up into the cavity. It costs a bath process. **Specify the anodising on the internal faces too, not only where it is seen** — the cavity's only route to the cold plate is radiation, and a masked or polished internal face throws that path away.

**Aluminium spreads four times better than steel.** Spreading resistance falls to about a quarter (170 W/mK against 45), which means the plate runs close to isothermal instead of hot under the compute module and cool at the rim. For a part whose whole job is to take heat in at one point and reject it over a large area, that is exactly the property you want. It also removes the galvanic pairing that a bonded aluminium fin insert in a steel plate would have created — it is now one part.

**Machining freedom.** Aluminium mills several times faster than mild steel, which is what makes a two-sided part — ducted below, ribbed above — economic at sixty units.

**What it does not buy: enough to delete the fan.** See section 8.

---

## 5. The geometry, worked

Ryan's insight is that the 8 mm exists for one reason and it is a **rim** requirement, not a whole-plate requirement. The plug bodies at the rear — barrel Ø8.5, USB-C 6.5 tall, jack Ø6–8 — must fit between the desk and the halo's bottom edge, which sits at the plate's top face. Only the outside of the plate has to be 8 mm. The middle can be anything.

Proposed section, from the bottom up:

| Layer | z, from the plate's underside | Extent |
|---|---|---|
| **Closing plate**, 1 mm, screwed on | 0–1 | r 0–66 |
| **The duct**, 3 mm, with fin channels | 1–4 | r 0–66 |
| **Web**, 4 mm | 4–8 | r 0–66 |
| **Rim**, solid 8 mm | 0–8 | r 66–77 |
| **Top-face ribs**, standing up into the cavity | above 8 | in the free crescents |

**Height cost: zero.** The object stays at 40.3 mm in v10 and about 34 mm in production. This is strictly better than my earlier version, which added 1.5 mm by thickening the pad.

Three consequences, all improvements:

**The duct has walls, so the air goes where it is sent.** An open-edged slot under a plate leaks in every direction and a fan mostly stirs the room. A machined channel from a defined intake to a defined exhaust is what makes the forced-convection figure in section 7 achievable rather than optimistic.

**The tipping problem disappears.** The rim is continuous metal at full height all the way round, so the rubber sits under a continuous ring and the object is supported at r 66–77 in every direction. The intake apertures become **machined slots through the rim**, not gaps in the rubber. That is better twice over: rubber compresses and its aperture changes with load and age, whereas a machined slot does not; and the slots sit just above the desk where nobody sees them.

**The closing plate makes the duct serviceable.** Unscrew it and the fin channels can be cleaned. An intake 3 mm off a desk will inhale dust over a decade, and this is the difference between a ten-minute service and a full teardown.

### 5.1 Ribs on the top face

They cost no web thickness — they stand up from the 8 mm level into the cavity, in the crescents the boards and the mechanism leave free.

**Make them tall and sparse rather than short and dense.** The cavity is stratified the same way the duct is, but inverted: cool at the bottom against the cold plate, warm at the top. Ribs that reach 5 to 8 mm up sample the warmer air and do real convective work; a short dense array sits in the cool layer and only adds radiating area. Since the radiating path is already served by the black anodising, height is worth more than area here.

**They are structural as well as thermal.** A dished plate with a stiffening rim and ribs on its inner face is how a casting is stiffened, and it answers the obvious worry about a 4 mm web in a Ø154 part. They earn their place twice.

---

## 6. The mass, honestly

This is the real cost and it should be decided against the number.

| | Mass |
|---|---|
| Steel plate as designed today, after cut-outs | **0.66 kg** |
| Aluminium plate as proposed, after cut-outs and the duct | **≈ 0.20 kg** |
| **Loss** | **≈ 0.46 kg** |

Against a whole-object mass of roughly 1.4 kg, that is about a third of the object, and the plate was deliberate ballast — the specification raised it from 5 mm to 8 mm partly to add 0.4 kg against the brief's "more is better".

**It can be partly bought back, and at the best possible radius.** Make the rim a separate ring of a denser metal, set into the aluminium plate:

| Rim material | Mass gained | Plate total |
|---|---|---|
| Aluminium (as proposed) | — | 0.20 kg |
| **Steel rim ring** | **+0.20 kg** | **0.41 kg** |
| **Brass rim ring** | **+0.23 kg** | **0.43 kg** |

The rim is at r 66–77, the largest radius in the object, which is where mass does most for perceived heft and for the object's resistance to being pushed around the desk. It is also outside the fin area, so it is not in the thermal path and does not undo the aluminium.

**And it can do three jobs at once**: ballast, the intake aperture (the slots are machined through it), and the bearing surface the rubber sits on. Brass against black anodised aluminium at the very bottom edge, below the engine-turned detail, is also a legitimate design move rather than a compromise. The one caveat is a dissimilar-metal joint — indoors, dry, with the pad between it and the desk, it is a non-issue, but it should be a deliberate non-issue.

**Or accept the loss.** A Ø154 × 34 mm object at 1 kg is still substantial. This is Ryan's call and he has already made it; the numbers are here so it is made with them in view.

---

## 7. The numbers, with the blower

Fin channels 3 mm tall on a 4 mm pitch over about 80 % of the web:

| | Value |
|---|---|
| Plate underside, Ø132 usable | 0.0172 m² |
| Finned area at a 2.5× fin factor | **0.034 m²** |
| Heat transfer coefficient, laminar flow in a 3 mm channel at about 1 m/s | 32 W/m²K |
| **Surface capability of the ducted underside** | **1.1 W/K** |
| Air's own capacity at 1.0 L/s | 1.2 W/K |

Surface and airflow are well matched at about **1 litre per second**.

**Specify a radial blower, not an axial fan.** This corrects my earlier note. A fin array is back-pressure, and an axial fan stalls against back-pressure — it moves air freely or not at all. A small centrifugal blower develops pressure and is the right machine for a ducted path. It is also the right shape: 5 to 8 mm thick, so it fits inside a locally deepened region of the duct rather than needing cavity space.

**Exhaust: machined slots through the rim at the rear, matching the intake.** Not the 44 × 30 mm socket slot, whose free area changes depending on what the user has plugged in — a thermal path that varies with the user's cable choices is not a thermal path. Everything then happens inside the duct and the port slot is untouched.

The one thing to check on the bench is **recirculation**: intake and exhaust are then both at desk level, about 100 mm apart. The exhaust is a directed jet and the intake is diffuse over a wide arc, which should be enough, but if it is not, the alternative is a short riser taking the exhaust up through the plate's rear edge below the halo — more machining, better separation, and still no opening into the cavity.

---

## 8. Passive or fanned — this is now a genuine choice

The material change helps but does not close the gap on its own. Black anodised aluminium with ribs is worth roughly **0.5 W/K** passive against the current 0.4.

**Skin temperature at 13 W sustained:**

| Architecture | Conductance | 22 °C room | 25 °C room, the standard's ambient |
|---|---|---|---|
| As designed today, steel, passive | 0.4 W/K | 54 °C | **57 °C — over the limit** |
| Black anodised aluminium, ribbed, passive | 0.5 W/K | 48 °C | **51 °C — exactly at the limit** |
| **Ducted, with a blower** | **1.1 W/K** | **34 °C** | **37 °C** |

**Read the other way — what load each architecture can carry for a 40 °C skin in a 22 °C room:**

| Architecture | Sustained load allowed |
|---|---|
| Steel, passive | 7.2 W |
| Black anodised aluminium, ribbed, passive | **9.0 W** |
| Ducted, with a blower | **19.8 W** |

**So there is a real passive route, and it is a power budget rather than a mechanism: cap the object at about 9 W sustained.** That means stating the halo's brightness cap as a hard number and underclocking the compute module — Raspberry Pi's own sanctioned mitigation, and a text file rather than a respin.

That is the actual decision, and it is a product decision rather than an engineering one:

- **13 W and a blower** — full brightness, full clocks, an object that runs cool to the touch, and a small moving part that is audible under sustained load in a silent object that also contains microphones for dictation.
- **9 W and no blower** — silent, simpler, one fewer failure mode, at the cost of a dimmer halo and a slower processor, and with no margin: 51 °C in a 25 °C room is the limit exactly, not a target.

**The sensible engineering answer is to build the duct either way.** Machining it costs almost nothing once the plate is aluminium and the rim carries the 8 mm; it is worth 0.1 W/K even unfanned; and it means the blower is a **fitted or not-fitted decision made after measurement**, rather than a plate respin. Fit the blower's mounting and its duct, leave the part unfitted on the first build, and measure.

---

## 9. Directing heat away from the knob

**Correct, and it is what makes the rest work — though not by insulating.** Heat in a closed cavity goes to whichever boundary is coldest. Once the plate is aluminium, black anodised inside, actively cooled and near-isothermal, it is the coldest boundary by a wide margin and the cavity's heat goes down on its own. The structure's lid stops the convective loop that would otherwise carry warm air up to the lens and the knob's lip.

**One expectation to correct.** The structure cannot insulate the knob and cannot be made to. A 1.6 mm PA12 wall in series with the 0.4 mm running gap is about 46 W/m²K, and over the knob's inner bore that is roughly **0.4 W/K of coupling straight into the knob**. That leak is through the **side wall**, not the top, and it cannot be closed — 0.4 mm is the running clearance. **The knob will always sit close to cavity temperature, so the touch limit is really a limit on the cavity.**

### 9.1 Ribs inside the knob — no, on two grounds

**Geometrically there is nowhere.** The bore runs at 0.4 mm clearance to the structure for its whole height and already carries the 90° V-groove for the wheels and the 0.15 mm code-strip recess. Any useful rib fouls the structure, the wheels or the strip.

**And thermally it is backwards.** Ribs inside the knob make it a better **absorber** of cavity heat, and the knob is the one surface with a legal temperature limit on it. It is the thing being protected, not a sink to load.

**It could not be the radiator anyway.** The knob's entire outer surface is about 0.017 m², or 0.025 m² counting the diamond knurl, which in still air at 11 W/m²K is **0.28 W/K** — four times worse than the ducted underside, before considering that polished aluminium radiates almost nothing at ε 0.05.

**Right instinct, wrong face: the ribs go on the plate's top side**, which is section 5.1.

**And the cavity does not have to do much**, because the two sources not bolted to the plate reject their heat outward rather than into it: the panel cools **forwards through its own lens** (about 2 W across the Ø127 picture through 2.5 mm of glass, roughly 0.14 W/K and a 14 K rise — the way every phone works), and the halo cools **outward through its diffuser**. So the cavity is a stratified dead volume, which is acceptable provided nothing important is left floating in it.

---

## 10. The consequence for the board layout

`SYSTEM-REVIEW.md` 6.1a flagged that the production board layout does not exist — the two-level deck is a v10-only arrangement and nothing says where the boards go once the compute module and its carrier replace the Pi 5.

**This plan answers it: the boards mount to the plate.** Carrier flat to the aluminium with the compute module conducting into its boss; the step-down converter and the motor driver — the second and third largest sources — likewise on thermal gap pads. That puts roughly 9 of the 13 W directly into cooled metal and leaves only the halo and the panel radiating into a cavity whose floor is cold.

It solves three things at once: the production layout, `SYSTEM-REVIEW.md` 5.1's worry about a warm converter bolted to a printed deck, and the thermal path. **It is the strongest argument yet for deleting the deck concept in production and treating the base plate as the chassis.**

---

## 11. Details that will bite if they are not written down

- **Anodising is an electrical insulator.** Hard anodising is a good dielectric, so the chassis ground bond needs either a **masked area** left bare during the bath or a thread-forming screw that cuts through the layer. This connects to `SYSTEM-REVIEW.md` 4.1, where the chassis grounding scheme is still undefined — and it is now more urgent, because an anodised plate that everyone assumes is grounded and is not is a hard fault to find.
- **Mask the thermal interfaces too**, or accept the anodic layer's resistance under the compute module's boss. It is thin, but it is in the highest-heat-flux joint in the object.
- **The closing plate needs a gasket or a machined lip**, or the duct leaks at its own seam and the blower's work goes nowhere.
- **The intake slots want a coarse geometry**, straight and at least 3 mm, so a decade of desk dust can be blown out through the exhaust rather than packing into a fine mesh.
- **The engine-turned edge detail and the anodising interact.** Anodising follows the machined surface faithfully and black anodise on a turned edge reads very differently from black anodise on a flat face. Worth a sample before sixty parts.

---

## 12. What to measure, and when

The plan rests on figures that are calculated, not measured. Three bench hours **before the production plate is cut**:

1. **The real sustained load.** Instrument the 12 V inlet and log it through an hour of genuine use — animation running, halo at the chosen brightness, motor rendering detents. Every watt at the inlet becomes heat in the object except the light that escapes. This replaces the 12–14 W estimate, and section 8 turns entirely on it.
2. **The passive baseline on the v10 print.** Thermocouples on the plate, on the knob and in the cavity, an hour at load, in a known room. This is already `V10-SPECIFICATION.md` section 7's temperature log — treat its output as the input to this plan, not as a pass or fail.
3. **The ducted case, roughly, with a cardboard duct and a bought blower** taped under the v10 print. Half an hour of work, and it says whether 1.1 W/K is real before anything is machined.

---

## 13. What changes in the existing documents, if this is approved

| Document | Change |
|---|---|
| `V10-SPECIFICATION.md` 4.16 | Plate becomes **one-piece black anodised 6082 aluminium**, 8 mm rim at r 66–77, 4 mm web, 3 mm ducted underside with fin channels, 1 mm screwed closing plate, machined intake slots front and sides and exhaust slots at the rear, top-face ribs, dark internal faces, masked ground-bond pad. Mass restated at ≈ 0.20 kg, or ≈ 0.41 kg with a steel or brass rim ring |
| `V10-SPECIFICATION.md` 4.18 | Pad stays 1.5 mm and becomes a plain ring under the rim; it is no longer part of the airflow |
| `V10-SPECIFICATION.md` 5.2 | Structure gains a **lid** closing the cavity inside r 62, with clearance for the panel's back components and its flex slot |
| `V10-SPECIFICATION.md` 6.9 | Rewritten: one forced path, entirely below the web; the 89 perimeter slits are **acoustic only** and are not vents; the rim-gap intake is dropped |
| `V10-SPECIFICATION.md` 8.5 | Production layout: boards mount to the plate, no deck |
| `SYSTEM-REVIEW.md` 1.1, 1.1a, 6.1a | Point at this document for the answer |
| `SOURCING-BOM.md` | Add the blower, thermal gap pads, the closing plate and its fasteners, the rim ring if taken; change the plate's material and finish |
| `VISION.md` | The plate is now black anodised aluminium, not steel. This is visible and it changes the object's description |

**Decisions needed to proceed:** the rim ring — aluminium, steel or brass (section 6); blower fitted or not fitted on the first build (section 8, and the recommendation is to build the duct either way and decide after measuring); exhaust through the rim or up a rear riser (section 7); and confirmation that 0.46 kg is an acceptable loss, which Ryan has already given but which is recorded here with the number attached.

---

## 14. Handover to the design session — stated as rules, not dimensions

Everything above is geometry-independent except four things, which were written against the Ø154 v10 plate. Those four are restated here as rules so the design session can apply them to whatever diameter and rim the corrected model lands on. **This section is the brief. The rest of the document is the reasoning behind it.**

**Material and finish**

1. Base plate becomes **6082 aluminium, black hard anodised on external surfaces only** (decided 6 September). The internal faces are **chromate conversion coated or bare** — chromate is electrically conductive, so no masking is needed anywhere.
2. **No masked bare areas.** Every bond and every thermal joint in the object is on an internal face, and internal faces now conduct. The cost is 0.048 W/K of cavity radiation — 2.8 K passive, 0.5 K ducted — in exchange for deleting five masked features on sixty parts. The closing plate's outer face stays black anodised: it is visible and it radiates to the desk.

**Section through the plate**

3. The plate keeps its **full thickness as a solid rim** at the outside. The rim's height is whatever the halo band and the rear plug bodies already require — it is not a thermal number.
4. **The rim's inner radius is derived, not given.** It must run inboard of the diffuser's seat and of the port face's fixing holes by at least 3 mm, so that neither lands on the ducted region.
5. Inside that radius: **2 mm web, 5 mm duct with fin channels, 1 mm closing plate** screwed on, with a gasket or a machined lip so the duct does not leak at its own seam. The web was 4 mm and the duct 3 mm up to v14; the split was a round number, never derived, and it cost about 25 Pa of airflow resistance to save a stiffness margin the fins and the rim ring already provide. Keep the web at 4 mm **locally** only where a joint carries real load — the chassis bond screw and the closing-plate screw islands — and take that thickening **downward into the duct as an island with the channels routed round it**, never upward, which would raise every board sitting on the web.
6. **The duct comes out of the plate's own thickness. Overall height must not change.**

**Openings**

7. **Intake: openings through the rim's edge face over the front and sides**, aligned with the duct layer, plus the continuous 1.5 mm undercut on the bottom outer edge as a supplement. The undercut alone is not enough: it is blocked when the object stands on a soft mat or cloth, and edge-face openings are not.
8. **Openings through the edge face are required, not forbidden.** This rule previously banned them because the edge face carried the engine turning; that decoration was deleted in v14, and the openings are now the decoration. They must sit on one uniform pitch all the way round, mirrored about the front-to-back centreline so the two side views are identical, with no blind openings anywhere and a plain arc across the port face.
9. **No openings through the plate's top face.** That is the halo's light channel — an opening there leaks light out and lets dust into the light path.
10. **Exhaust: rear only, on a different arc from the intake** so the object does not breathe its own exhaust, and **never the socket slot** — its free area changes with whatever the user has plugged in. It runs on **two paths**: through the rim's edge face on the arcs either side of the port face, and downward through the pad's voids. **The edge-face part alone must be at least 200 mm²**, because the downward path is blocked when the object stands on a soft mat. Total rear exhaust target about 400 mm². The exhaust must never again be a small fraction of the intake: at 147 mm² it was throwing away more than a third of the entire pressure budget.

**Fins and the blower**

11. Fin channels **5 mm tall on a 4 mm pitch, straight**, running front to rear from the intake arc to a rear plenum. Coarse and straight so a decade of desk dust can be blown out rather than packing in. Straight and front-to-rear is not a style choice: air enters at the rim and leaves at the rim, so it travels front to back, and radial fins would sit across that flow. **Fin only where the heat is** — over the compute module and converter footprints — and leave the rest of each channel as open cavity, which has roughly a seventh of the resistance and costs no useful surface area, because aluminium spreads heat sideways well enough that fins elsewhere earn little.
12. **The blower is fitted and required** (Ryan, 6 September; v15). A fin array is back-pressure and an axial fan stalls against it, so it is a radial blower — and no radial blower with a usable curve is 5 mm thick (the 3 mm Sunon class gives 0.3 L/s free air at 36 dB(A)), so it does not live in the duct: a Delta BFB0305HA-C (30 × 30 × 10, 0.68 L/s free, 71 Pa at no flow, 29 dB(A)) stands on the plate over the +y rear plenum, inlet face down on a gasket over a hole in the web, its side outlet into a printed hood that turns the air down a trench cut from the top into the ring's rear exhaust groove. It breathes only duct air. Expected operating point about 0.5 L/s at ~25 Pa through this duct, about 1.0 W/K with the passive skin — 38 °C at 13 W in a 25 °C room. One blower: a second on the other side was costed at ~2 K of margin for double the noise and another 0.65 W. The motion board rides on the blower's saddle.

**Above the plate**

13. **Ribs on the plate's top face**, 5 to 8 mm tall, in the crescents the boards and the mechanism leave free. Tall and sparse rather than short and dense — they reach up into the warmer stratified air, and they stiffen the web at the same time.
14. **The internal structure gains a lid** closing the cavity inside the display seat's inner radius, with clearance for the panel's back components and its flex slot.
15. **The step-down converter mounts to the plate on a thermal gap pad; the motor driver's board rides on the blower's saddle (v15).** The compute module does NOT sit on the web: since v12 the Raspberry Pi 5 is in a window through the web and the duct, on the closing plate, keeping its own heatsink (fan off) — its heat reaches the fin channels through the window's walls and the cavity air, which is why the fins are finned end to end beside the window rather than "under the hot spots" (rule 11's second sentence does not apply to this layout). In production the Compute Module 5 on a plate boss is the plan; the plate is the chassis, no mezzanine deck.

**Report back**

16. The plate's **mass, before and after**, and the same figure with a steel or brass rim ring fitted in place of the aluminium rim. The aluminium change costs roughly 0.7 kg on a Ø175 plate and the ring buys about 0.2 kg of it back at the largest radius. That number should be seen before it is locked.
17. The **intake and exhaust free areas** actually achieved, and the fin count.

**Reported back from v15 (7 September 2026, `docs/v15/V15.md` and `checks.txt`).** Deflection under knob load: nil before and after — the knob's load path (wheels → structure wall → wall foot and pillars → the solid rim, r ≥ 75.2) never crosses the web; the web carries the boards and the servo. Intake: 80 openings 1.8 × 4.5 = 592 mm² through the edge face over 60–300 plus a 0.8 undercut (285 mm²); throat 17 passages 9 × 3.5 = 535 mm². Exhaust: 28 openings = 207 mm² through the edge face on 18–60 and 300–342 plus the undercut (104 mm²); the blower's trench 18 × 7 = 126 mm² into the 18–60 groove; the −y side's 300–342 arc is pulled in reverse by the blower. Fins: 19 channels 3 × 5 on 4, finned full length (12 at +y fanned, 7 at −y). System pressure at 1.0 L/s is not reachable with one 30 mm blower; the estimate at 0.5 L/s is ~25 Pa (fins 8, intake 3, trench and outlet 7, groove and openings 5), all still to be measured. Every ring fixing is on a land (checked with the countersink cone). Mass: in `checks.txt`.

**One thing not to re-open.** The hollow knob does **not** solve the touch-temperature limit. Its 3 mm rim bridges the annular cavity — about 41 W/K of aluminium against 0.1 W/K for the air gap, roughly four hundred to one — so the knob stays essentially isothermal and the limit still applies to all of it. The cavity is worth having for mass and for the larger top rim's radiating area; it is not insulation.
