# Industrial design research — findings for the 60

Answer to the research brief `docs/Research/3-industrial-design-RD.md`. Compiled 2026-09-02 from six research strands; each strand's full findings, source links and image links live in its own file in this folder:

- [section-A-knurl.md](section-A-knurl.md) — the knurl and the turned edge
- [section-B-proportion.md](section-B-proportion.md) — proportion and stance
- [section-C-automotive.md](section-C-automotive.md) — automotive rotary controllers
- [section-D-light.md](section-D-light.md) — light as the only colour
- [section-E-hci.md](section-E-hci.md) — human-interface research on rotary input
- [section-F-packaging-finish.md](section-F-packaging-finish.md) — packaging, unboxing and finish

Every number below is either cited in the section file or marked unverified/estimated there; nothing is invented. This document is the summary and the recommendation set; the evidence and images are in the section files.

---

## A. The knurl and the turned edge

The precise/aggressive line is set by depth more than pitch. Coin reeding — the one fine knurl with a public spec (US Mint: 119 reeds on the Ø24.26 mm quarter, ≈0.64 mm pitch) — is the texture fingers already read as "money-precise"; Surefire's deep full-sharp rolled knurl is the documented "chews up pockets" pole, and the Rotring 600 pencil ("secure… not a cheese grater") is the loved middle. Every comfortable example truncates or radiuses its crests. Tudor's Black Bay is the closest analogue to the 60 — a 60-click bezel whose 2026 revision deliberately traded coin-edge refinement for "toothier" knurling to fight detent torque. One structural observation: objects turned tangentially with fingertips (lens rings, bezels, the Apple Digital Crown, coins) converge on axial ridges; diamond knurl is the fist-grip pattern. The clous-de-Paris watch tradition shows fine diamond can be jewellery instead.

**Recommendations** (full reasoning and sources in [section-A-knurl.md](section-A-knurl.md)):

1. Side knurl: raised-point diamond in the style of RGE per DIN 82 (the German knurl standard), 30° helix, 90° tooth profile, **420 points around Ø134 → 1.00 mm circumferential pitch = exactly 7 diamond columns per detent**, phase-locking the texture to the sixty clicks.
2. Tooth depth **0.28–0.30 mm** — truncated from the theoretical full-sharp 0.42 mm — with flatted or ~0.05 mm radiused crests; mark V (unverified) in CAD until a machined test ring is felt. Abrasion, not slip, is the failure mode on an object touched hundreds of times a day.
3. End the knurl in a **0.8 mm plain turned band at root depth** before the coin-edged rim and before the 1.2 mm lower chamfer, so no tooth dies raggedly into the diamond-cut chamfer. Give the coin-edge rim **600 reeds (0.70 mm pitch)** so both textures share the 60-grid.

## B. Proportion and stance

Ratio alone carries no permanence. The 60's envelope (Ø135 × 34 mm, ratio 0.25) is within 3 mm of the **Jabra Speak2 75 conference speakerphone** (Ø132.5 × 35 mm, 466 g plastic, Jabra's own tech sheet) — the one desk puck everyone owns and knows is portable. What separates permanent from portable in the survey is mass-per-footprint, the densest-reading material at the desk plane, and top-facing controls. The Nest Learning Thermostat (Ø83 × 32 mm, 252 g of stainless ring) proves a metal ring around a round screen reads as an instrument when the ring mass is real; the Leica M11's brass-vs-aluminium top plates (640 g vs 530 g, identical looks) show felt density on first pickup is a paid-for specification. The best light-under-mass precedent is the Naim Mu-so 2nd generation: aluminium chassis hovering on a lit acrylic plinth — light below the mass at desk level, metal-to-metal seams kept dark.

**Recommendations** ([section-B-proportion.md](section-B-proportion.md)):

1. Keep the 2.8 mm shadow line genuinely dark — physical baffle between the halo channel and the gap, darkest available internal finish. Light leaking into that seam makes the knob float and contradicts the mass story. At ~2% of diameter the width itself is fine.
2. Write a **felt-mass floor into the mechanical brief** and size the steel plate by it, not by structure. North of 1 kg is the researcher's estimate, explicitly marked estimated; the point is that the number becomes a requirement.
3. Recess the silicone pad **6–10 mm (estimated)** behind a crisp knife-edge bottom line; no visible bumper; note the HomePod silicone-on-oiled-wood staining precedent when picking pad material.

## C. Automotive rotary controllers

The E65 BMW 7 Series (2001) shipped a true force-feedback iDrive knob — Alps Electric motor and belt, Immersion-designed per-screen feel profiles with programmable detents, hard stops and "hills" — and BMW deleted the force feedback in the March 2007 update. Feel that exists only under power ages badly; production iDrive controllers since 2008 (made by Preh GmbH) are plain spring-follower-on-toothed-ring. The documented field failures across iDrive and Mercedes COMAND are plastic wear parts — a worn plastic guide ring making rotation "gritty", a broken plastic shaft — inside otherwise premium controllers. Bentley's knurled titanium organ stops are the clearest "control that invites idle handling" precedent; Rolls-Royce's version of the iDrive knob is "chunkier… with a slightly smoother feel" (outlet unverified), i.e. at high mass, off-detent friction must drop. The industry is legislating knobs back (Euro NCAP, the European car-safety assessment programme, requires physical controls for five functions from January 2026); what reviewers consistently say was lost to touchscreens is eyes-free operation. The 60's magnet-baseline-plus-motor split matches the magnetic-detent patent frontier, not any shipping car part — the architecture is ahead of automotive practice, not behind it.

**Recommendations** ([section-C-automotive.md](section-C-automotive.md)):

1. The motor layer only ever **adds** (end stops, inter-zone "hills", per-context damping) — never required for the baseline click. Adopt Immersion's screen-agnostic architecture: firmware knows feel profiles, not application state.
2. **No plastic in the torque path, no sliding plastic in the detent path.** The only published automotive detent-torque figure found is Panasonic's Magic Knob at 25 mN·m ±30% — a floor for scale, not a target; the real number comes from the bench rig.
3. Light from below, through openings — never a lit surface. Matches the 60's colour-only-from-light law and endorses the halo placement over any illuminated marking on the ring.

## D. Light as the only colour

The Echo Dot 4th generation already proved the 60's exact scheme at mass-market scale: Amazon moved the light ring to the base to glow down onto the desk, and reviewers preferred it. The hot-spot rule of thumb is 1:1 — diffuser standoff equal to LED pitch — so at the assumed 4 mm pitch (unverified), 4 mm of clearance erases the emitters with no light guide or micro-lens work. Diffuser numbers from primary datasheets: PLEXIGLAS Satinice 0D010 DF opal PMMA (acrylic) gives 83% transmission at 3 mm with diffusing beads through the body, and comes as Ø50–200 mm extruded tube — a real stock form for the ring. The desk is the biggest unmanaged variable: reflected glow differs roughly 17× between white laminate and a black mat (light-reflectance values ~85 vs ~5), and gloss desks mirror the ring and expose residual hot-spots. Verdict on the 36° gap: **feature, not flaw** — the 60 is an instrument with a front, a broken ring reads as a gauge arc with a natural zero and maximum, and a deliberate gap beats a full ring with a dim detour around the sockets. Condition: the arc endpoints must be designed (opaque baffles or a software fade over the last 2–3 LEDs) or the termini read as faults.

**Recommendations** ([section-D-light.md](section-D-light.md)):

1. Diffuser: opal PMMA (acrylic) with beads through the body, **3 mm wall** — start with PLEXIGLAS Satinice 0D010 DF, machinable from stock extruded tube.
2. Standoff **≥4 mm** from LED die to diffuser inner face (6 mm if height allows); white channel walls and white solder mask behind the LEDs; verify uniformity on a gloss-black test plate, the worst case.
3. Design the arc endpoints (baffles plus optional 2–3-LED fade) and add **an ambient light sensor plus one-time desk calibration as a requirement, not firmware polish**; ring-off must be a first-class state.

## E. Human-interface research

The literature splits by task, not device: touch wins discrete selection among visible targets on speed and errors; the rotary wins continuous adjustment on accuracy and glance economy, and was the only interface meeting the US National Highway Traffic Safety Administration's 12-second eyes-off-road criterion in the SAE on-road comparison. Knowles and Sheridan (1966) found users prefer high inertia, low friction, viscous over stick-slip — the heavy machined ring on good bearings is the empirically preferred feel. Detent practice: named-position selection lives at 30–45° spacing (8–12 per revolution); fine adjustment at 24–30+ per revolution — the 60's 6° pitch is a precision-adjustment pitch, and one detent = one menu item is the automotive convention. Menu depth: Miller's 1981 optimum is two levels of about eight items; rotary steps-to-target is linear in list distance, so long lists should scroll under the fixed dot, never lay out as ring positions. The SmartKnob open-source community (the closest field report on software-defined detents) values context-dependent feel, endstops and snap-to-position, and its documented failure is fine or weak virtual detents being overpowered by the motor's own passive torque field. Accessibility: physical detents give position and count with zero vision, zero sound and — on the 60 — zero power; tangible interaction beats gesture in preference studies with visually impaired users; a detented knob sidesteps the fine-pointing and steady-tap failures touchscreens impose on tremor users.

**Recommendations** ([section-E-hci.md](section-E-hci.md)):

1. Map divisions to tasks: **6 or 12 detents for menu/mode selection, 60 for continuous adjustment; treat 120 as experimental** until the bench rig proves a 3° motor detent between 6° magnetic poles is perceivable at all.
2. Ring menus: **at most two levels of 6–12 items**; anything longer scrolls under the twelve-o'clock dot.
3. Route tasks deliberately: discrete jumps to touch, continuous and eyes-free actions to the ring.

## F. Packaging, unboxing and finish

Compact beats grand: reviewers reward considered, plastic-free, compact packaging (anOrdain, Christopher Ward, Teenage Engineering) and complain about lavish bulk (Bang & Olufsen's box weight, Omega boxes "too nice to store", Grand Seiko undershooting). The limited-run pattern (Leica) puts the number on the certificate and an engraving, not the box graphics. Named UK suppliers found for a 60-unit run: Clyde Presentation Packaging (who make anOrdain's boxes), Showcase Creative, Pillbox Design, Fantastic Mr Box for rigid boxes; Blush Publishing and others for letterpress certificates — every price quote required. On finish: MIL-A-8625 (the US military anodising specification) Type III hardcoat is 12–75 µm against Type II sulfuric anodise's 5–15 µm, far more abrasion-resistant, and its native colour range on 6xxx alloy — dark grey, black, natural — is exactly the 60's palette, so the durability upgrade costs nothing aesthetically. The iPhone 5 "scuffgate" (dark thin anodise plus diamond-cut edges scuffing bright in daily handling) is the documented cautionary tale. Critical process gap: the freshly diamond-cut chamfer is bare aluminium and must be sealed (clear lacquer per alloy-wheel practice, or a second clear anodise — unverified, confirm with the anodiser) or it dulls and fingerprint-etches. No UK shop sells diamond-cut-after-anodise as a catalogue service for small parts; it needs a machinist-plus-anodiser pair and quotes.

**Recommendations** ([section-F-packaging-finish.md](section-F-packaging-finish.md)):

1. Package like anOrdain, not Omega: compact UK short-run rigid box, letterpress-numbered cotton certificate ("No. 07/60"), a booklet naming the people, a good USB-C cable, a polishing cloth, no plastic. All quotes required.
2. Specify the handled ring as **Type III hardcoat per MIL-A-8625, 6xxx alloy, matte set by a bead-blast recipe agreed on test panels**; approve fingerprint behaviour under raking light on the panels.
3. **Decide the bright chamfer's sealing step before CAD freeze** — it affects process order, cost and the ring's exact brightness, and needs named suppliers in `docs/SOURCING-BOM.md`.

---

## What we think is wrong — kept separate, with the evidence

In descending order of confidence:

1. **"Diamond-cut after anodising" is an incomplete process description.** The cut ring is bare aluminium; unsealed, it oxidises, dulls and takes fingerprint etching — the alloy-wheel industry documents this failure mode extensively, and Apple's own patent flow implies a sealing step. A sealing operation (clear lacquer, or a second clear anodise — unverified) must be added to the process. Evidence in [section-F-packaging-finish.md](section-F-packaging-finish.md) §F2.3.
2. **The finish spec implies Type II anodise where Type III hardcoat is the right call.** The iPhone 5 in slate — thin dark anodise with cut edges — scuffed bright in normal handling; hardcoat's native palette is exactly matt black / dark grey / natural, so the upgrade is free aesthetically. Evidence in [section-F-packaging-finish.md](section-F-packaging-finish.md) §F2.1–F2.3.
3. **The 120-step division fights the magnetic detent field.** Every second step of a 120 mode falls at the energy maximum between two 6° magnetic poles; the SmartKnob community's documented experience is that fine or weak virtual detents are overpowered by an underlying passive torque field, and mechanical-switch practice treats sub-15° spacing as too fine for positive detent action. 120 may only be honest as software resolution, not felt detents — a bench-rig question. Evidence in [section-E-hci.md](section-E-hci.md) §E5 and "Possibly wrong".
4. **Diamond knurl is the outlier pattern for a fingertip-rotated ring.** Every surveyed object sharing the 60's gesture — lens rings, dive bezels, the Digital Crown, coins — uses axial ridges; diamond is the fist-grip pattern. The decision can stand as ornament (the clous-de-Paris tradition), but then the coin-edged rim is doing the real rotational grip work, and if a sample ring feels slippery the fix is the rim's reeding, not deeper diamonds. Evidence in [section-A-knurl.md](section-A-knurl.md) §5 and "Possibly wrong".
5. **The base's outward taper is a floating gesture on an object that wants to read grounded.** Grounded objects get wider or stay straight toward the desk; reverse taper appears in deliberately floating designs and survives only under overwhelming density signals (Devialet Phantom, 11.4 kg). The optical goal is right; the taper should be the minimum the halo optics need. Direction-of-risk flag, not a measured fault — no taper angle is recorded. Evidence in [section-B-proportion.md](section-B-proportion.md) "Possibly wrong".
6. **The single green selection dot must not be the only selection cue.** Colour-alone signalling fails the Web Content Accessibility Guidelines' use-of-colour criterion (1.4.1); the fixed twelve-o'clock position is a sufficient second cue only if position, not colour, is what actually distinguishes selected from unselected. Evidence in [section-E-hci.md](section-E-hci.md) §E6.

Flags that are checks, not errors: the 36° gap width should be verified against the actual socket cluster (36° ≈ 42 mm of arc; if the connectors need less, the gap carries unexplained dark arc — [section-D-light.md](section-D-light.md)); the Jabra Speak2 75 envelope collision means the mass floor is load-bearing, not optional ([section-B-proportion.md](section-B-proportion.md)); and "heavy" must pair with low off-detent friction or it reads as stiff — the Rolls-Royce "chunkier and smoother" datapoint ([section-C-automotive.md](section-C-automotive.md)).

## Honesty notes

- Manufacturers publish almost no knurl specs; where a count appears it is a click count (Tudor 60, Rolex 120) or a government spec (US Mint reeding). The "Hexxagon" flashlight named in the brief could not be identified.
- The BMW iDrive 24-detents-per-revolution figure circulating online is unverified; the Rolls-Royce "chunkier, smoother" quote's outlet is unverified.
- Several primary papers (Miller 1981, Knowles & Sheridan 1966, the SAE on-road study) are paywalled; findings are taken from abstracts and are marked as such in [section-E-hci.md](section-E-hci.md).
- No study exists of hand posture on a ~135 mm rotating desk puck; the rim-grip assumption is inference from geometry and needs the bench rig.
