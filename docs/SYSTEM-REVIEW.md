# the 60 — whole-system compatibility and assembly review

**Date: 5 September 2026. Status: review, nothing here is a decision.** Written against `docs/v10/V10-SPECIFICATION.md` (5 Sep, evening), `docs/boards/BOARD-CARRIER.md`, `BOARD-AUDIO.md`, `BOARD-MOTION.md`, `docs/SOURCING-BOM.md` and `docs/VISION.md`.

The question this answers: the design has grown from one development board into three made boards, a two-level chassis, a mains supply and a bought panel, and each part of it has been worked on separately. **What have the separate pieces stopped agreeing about, and what is nobody holding?**

Method: build the register of every interface between two things, then check both sides say the same number. Where a number drives a conclusion, it was checked against the vendor's own document, not against another of our documents. Four external verifications were done specifically for this review — connector heights, the flashing path through a hub, UK conformity obligations, and the touch-temperature standard — and are cited where used.

**How confident each finding is** is marked: **[hard]** the numbers come from a vendor or a standard and the conflict is arithmetic; **[likely]** the reasoning is sound but one input is our own assumption; **[watch]** it may be nothing, but nobody has looked.

---

## 1. The five that would stop the build

Ranked by how much later work they invalidate, not by how hard they are to fix.

### 1.1 The object cannot get rid of its own heat, and the standard that governs it is stricter than the design assumes **[hard]**

The specification's own thermal sum, section 6.9: about 10 W sustained, a skin of roughly 0.036 m², an assumed 11 W/m²K, giving 0.40 W/K and **+25 K — a 47 °C surface in a 22 °C room.**

Two problems with that, and they both push the same way.

**The limit is lower than 47 °C.** IEC 62368-1 Table 38 is the touch-temperature table for this class of product, and its first three rows are headed *"Handles, knobs, grips, etc."* For bare metal: **48 °C** for a part held for more than a minute, **51 °C** for one "held for short periods of time or touched occasionally (>10 s and <1 min)". The standard's worked example for that middle row is, precisely, *slight adjustment of a volume knob*. And the limits are absolute temperatures measured **at a 25 °C room ambient**, not at 22 °C — so the specification's own figure becomes **50 °C at the standard's ambient, against a 51 °C limit, with nothing left over.**

There is one escape hatch, footnote f: metal covered by plastic or rubber **at least 0.3 mm thick** may use the plastic limit of 60 °C. Anodising does not qualify — the coating figures in ISO 13732-1 start at 50 µm of lacquer and buy only a few degrees.

**The 10 W is optimistic and the 0.036 m² is optimistic.** Reworking the sustained load with the parts as they now stand — a compute module doing real graphics rather than idling, the panel and its backlight, the halo at a realistic colour, the motor holding detents, and the step-down converter's own losses — lands at **12 to 14 W**, not 10. And the 0.036 m² counts the knob as radiating skin. **The knob is thermally disconnected from every heat source in the object**: it touches three plastic wheels and 0.4 mm of air, nothing else. It is the largest external surface and it is the one not attached to the heat. What is left directly coupled is the plate rim and the plate's underside, and the underside is lying on a rubber pad on a wooden desk, which is a blanket.

Working the narrow air gap as a conduction path, the knob does get warmed across it, so the real figure is somewhere between the two — but every correction available moves the number the wrong way, including the low emissivity of a polished aluminium knob, which barely radiates at all.

**What this means.** The passive, fanless assumption is the single load-bearing assumption in the mechanical design and it has never been modelled or measured. The v10 print's temperature log (section 7 of the specification) is the right test and it should be treated as a **gate**, not an item — if it fails, the fallback in the specification (option B, the conduction boss) does not fix it either, because option B improves the path from the processor to the plate and the problem is the path from the plate to the room.

The levers, cheapest first: **state the halo's sustained brightness cap as a number** (it is asked as an open question in two separate board briefs and answered in neither); underclock the compute module, which Raspberry Pi themselves offer as the sanctioned mitigation and which is a text file rather than a respin; or move air through the object (1.1a).

**The obvious fix is not available, and it is worth understanding why.** The intuitive answer to "the knob is the big surface and it is not connected to the heat" is to connect it. You cannot: section 1.1's own limit is on the knob, so deliberately conducting heat into it means heating the exact surface the standard caps at 51 °C. **The largest radiating surface in the object is the one you are not allowed to make hot.** That closes off conduction as the answer and leaves air.

### 1.1a The fan was ruled out by a part that does not exist in production **[hard]**

Worth separating, because the specification's finding 3 reads as "no fan" and what it actually says is narrower.

The Active Cooler's fan was not fitted for one reason: *"its 34 × 34 intake hole in the deck and the 65 × 64 adapter cannot both exist — the fan sits 15 mm from the Pi's centre and the adapter's centre must be within 24 mm of the axis to fit the deck, so every legal adapter position covers the hole."*

**The 65 × 64 adapter is v10-only.** Production deletes it — no HDMI, no ribbon, no deck. So the collision that removed the fan disappears with the part that caused it, and **the fan is an open question for production, not a closed one.** It can also be reopened in v10 by taking the specification's own question 3: write the panel driver now, drive the panel by four-lane display serial interface straight from the Pi 5, and delete the adapter. That frees the deck, and it does production work early rather than twice.

Three things to hold in mind if it is taken:

- **A fan alone does not fix 1.1.** The specification says so in 6.9: it would *"exhaust into the same cavity it draws from; it would not change the skin figure."* A fan moves heat from the chip into the box. Only **through-flow** — a separate intake and exhaust with a baffle, so air passes through the object once — moves heat from the box to the room.
- **Through-flow is decisively better than anything passive.** 0.5 L/s of air carries **0.6 W/K**, against the whole skin's optimistic 0.4 W/K. At 13 W that is roughly an 11 K average rise inside instead of 30 K, and it is the only mechanism in the design that scales.
- **The 30 mm fan at 8,000 rpm is audible**, on a silent desk object that also contains microphones for dictation. But it is temperature-controlled, and with the adapter gone there is room for a **larger, slower fan** moving the same air — a 40 mm part at a quarter of the speed is inaudible. If a fan is taken, take a big slow one, not the Raspberry Pi part.

**This is a decision to make before the production enclosure**, because the intake path — the rim gap between the lens and the lip, or holes through the plate with channels in the pad — changes the object's outside.

Raspberry Pi's own words, from their December 2025 thermal white paper, are worth having in front of you when this is decided: *"It is not recommended that CM5 be left to self-regulate using protective throttling."*

### 1.2 Every power connector specified in the board briefs is too tall to fit on the deck **[hard]**

The specification gives about **6 mm** of vertical space above a board on the mezzanine deck (board top face at z 23.38, ceiling at 29.3). The two board briefs specify JST VH or Molex Micro-Fit for power and JST GH for signals, and both explicitly forbid JST SH. Checked against the manufacturers' own drawings:

| Connector | Mated height above board | Fits in 6 mm? |
|---|---|---|
| JST VH, top entry | 16.5 mm | No |
| JST VH, side entry | 10.5 mm | No |
| Molex Micro-Fit 3.0, vertical | 17.3–17.6 mm | No |
| Molex Micro-Fit 3.0, dual-row right angle | 10.3 mm | No |
| Molex Micro-Fit 3.0, single-row right angle | 6.98 mm | No, marginally |
| JST PH, top entry | 8.0 mm | No |
| JST PH, side entry | 4.8 mm | Yes |
| JST GH, top entry | 7.3 mm | No |
| JST GH, side entry | 4.35 mm | Yes |

**VH cannot be made to fit in any orientation.** That is not a preference, it is 10.5 mm into 6 mm.

Two further corrections fall out of the same check. **JST PH has no positive latch** — its datasheet feature list gives a fully shrouded header and board retention, not a lock — so the motion brief's rule ("one rule above all: no friction-fit") rules out its own recommendation for the motor phases. And **JST GH is rated 1.0 A**, so the motion brief's "LED ring power, three feeds at 1.1 A each" is over the contact rating if GH were used, though it specifies PH there, which is 2 A.

**There is a clean answer.** Latched families exist that fit in the height and carry the current:

| Part family | Pitch | Mated height | Current per contact | Latch |
|---|---|---|---|---|
| **Molex Pico-EZmate Plus** (212134) | 1.00 mm | **1.20 mm** | **2.8 A** | Yes |
| **JST ACH** | 1.20 mm | **1.40 mm** | **2.0 A** (1–3 ways) | Yes, push-to-release |
| **Hirose DF57 / DF57AH** | 1.20 mm | 1.4–1.6 mm | up to 3.0 A | Yes, swing-lock |
| **Molex Pico-Lock 1.50**, right angle | 1.50 mm | **2.00 mm** | 2.0 A | Yes |

For the 5 A feed into the carrier, parallel contacts — a four-way Pico-EZmate Plus as two power and two ground is 5.6 A with a 1.2 mm mated height. **This closes the connector question across all three boards in one decision**, and it should be made before any board is drawn, because connector choice sets the escape routing at the board edge.

### 1.3 The audio and motion boards are allocated a third of the area they need **[hard]**

| Board | Space the specification allocates | Space the brief says it needs | Shortfall |
|---|---|---|---|
| Audio | **25 × 40 = 1,000 mm²**, 6 mm tall | 45 × 55 = 2,475 mm² with the module; 55 × 65 = 3,575 mm² discrete | **2.5 to 3.6×** |
| Motion | **30 × 30 = 900 mm²**, 7.4 mm tall | 50 × 45 = 2,250 mm² to 60 × 50 = 3,000 mm² | **2.5 to 3.3×** |

The specification is honest about how it got there — *"the first draft proposed 50 × 40, but the deck's free sector beside the servo is 30 × 30"*. The board was resized by what the mechanism left over. Nobody then asked whether the electronics still fit, and they do not: the audio board's area is eaten by four regulators with their inductors, roughly fifty decoupling capacitors, the debug header, and the connectors — not by the two chips.

This is not a layout problem that a good contractor solves. It is an architectural one, and there are only four real answers:

1. **Move the audio board off the deck.** It is the board with the least reason to be near the panel; its only short cable is to the microphones, and the microphones want to be on their own flex anyway (the brief already prefers this). The floor's 270° crescent beside the speaker is where it belongs, next to the jack it feeds.
2. **Stack.** Two 30 × 30 boards on 4 mm standoffs is more area than one 30 × 60 and costs 4 mm of height the deck may not have.
3. **Merge the audio and motion boards into one.** Tempting on area, and wrong: the audio brief's entire noise argument depends on the motor's return current never touching the audio board's reference copper.
4. **Reduce the mechanism's footprint** so the deck has more free sector. Least likely, since the motor's radius is set by the bore.

The recommendation is (1), and it should be settled before either board is drawn, because it changes the cable lengths for the speaker, the jack, the microphones and the power feed all at once.

### 1.4 The panel's own power supplies are not designed, budgeted or assigned **[hard]**

The panel needs, from the specification's own section 4.1: **1.8 V logic, ±5 V analogue rails, and a backlight of twelve white LEDs in series at 37.2 V, 20 mA.**

In v10 the DisplayModule adapter board provides all of this — that is a large part of why the adapter exists. For production the specification deletes the adapter and says the carrier does it: *"the CM5 carrier's DSI output straight to the flex, ±5 V and the 37 V backlight driver on the carrier."*

The carrier brief does not contain any of it. Its power table has one line, *"Display ~400 mA"*, and its display section covers the four data lanes, the clock, 3.3 V and the touch bus. So the production carrier must gain:

- a **+5 V and −5 V analogue pair** for the panel;
- a **1.8 V logic rail**;
- a **37 V constant-current boost converter** with dimming control, driving 20 mA into a series string;
- the **backlight enable, brightness and panel reset** signals, which the brief already flags as having no Raspberry Pi reference circuit and no recommended pin assignment.

A 37 V boost from a 5 V rail on the same board as a compute module and a low-noise audio path is not difficult, but it is a switching converter running at a few hundred kilohertz with a 37 V node on it, and it needs to be in the plan. **[likely]** it adds 1 to 1.5 W of its own losses to section 1.1's budget.

Alongside it, the software half: the specification notes the production carrier *"needs a Linux panel driver with the HX8399-C initialisation sequence from DisplayModule"*. That is on the critical path for the product's headline feature, it has no owner and no estimate, and the initialisation sequence has to be obtained from the vendor.

### 1.5 The internal speaker has no amplifier, because both documents say it belongs to the other one **[hard]**

The specification, section 4.12: *"the speaker (2-wire, the XMOS drives a small class-D on this board — the speaker amplifier is the board's, the 3.5 mm output has none)."*

The audio brief, section 8: *"**No speaker drive on this board.** If an internal speaker is ever added it needs its own class-D amplifier on another board; putting one here would undo sections 6 and 7."* And section 1: *"There is no headphone amplifier and no speaker drive on this board."*

The speaker is a real part in a real cradle at (17, −46) with two M3 screws in the plate. Nothing drives it.

Two related things fall out of the same gap. The converter is a two-channel part feeding a line output; a speaker needs either a third channel or a shared one, and **if it shares, something must mute the internal speaker when a jack is inserted.** The chosen jack, the Switchcraft 35RAPC4BH3, has switch contacts for exactly this, and nothing in any document reads them. And **[likely]** the audio brief's objection is right on the merits — a class-D amplifier switching at a few hundred kilohertz a few millimetres from the converter's charge-pump and its ground-sense network is the wrong neighbour — so the resolution is probably a small amplifier on the motion board or on its own, not on the audio board.

---

## 2. The interface register

Every place two things in this product have to agree. **Disagree** means the two ends of the same connection are described differently in two documents.

| # | Interface | Carrier / mechanical says | Board brief says | State |
|---|---|---|---|---|
| 1 | Audio board → computer | v10: USB-A on the Pi (a device **of the Pi**) | Production: USB **downstream of the internal hub**, a sibling of the compute module | **Disagree — see 2.1** |
| 2 | Motion board → computer | v10: serial on the 40-pin header | Production: USB downstream of the hub, presenting keyboard and mouse | **Disagree — see 2.1** |
| 3 | Touch controller → computer | USB to the Pi | I²C on the display flat-flex (the Raspberry Pi way) | **Disagree** |
| 4 | Panel data | v10: HDMI → adapter → 45-way flex | Production: DSI0 on a 22-way Hirose to the flex | Consistent; the adapter's ability to accept a 45-way 0.3 mm flex is an open item with the vendor |
| 5 | Panel rails and backlight | adapter (v10) / carrier (production) | not in the carrier brief | **Gap — 1.4** |
| 6 | Halo LED count | **46**, a bought 5 mm strip, ~1.0 A | **90**, custom flex, 3.30 A, three injection points | **Disagree — see 2.2** |
| 7 | Halo data | strip's own lead to the motion board | level-shifted 5 V through an AHCT buffer, 470 Ω at the first LED, 100 nF per LED | Partly obsolete: the last three are properties of a flex you design, not of a bought strip |
| 8 | Board power connectors | 6 mm of height above the deck | JST VH / Micro-Fit | **Disagree — 1.2** |
| 9 | Signal connectors | "low-profile JST-SH, 5 mm" | "Never JST SH" (both briefs) | **Disagree — 1.2 gives the answer** |
| 10 | Audio board size | 25 × 40 × 6 | 45 × 55 minimum | **Disagree — 1.3** |
| 11 | Motion board size | 30 × 30 × 7.4 | 50 × 45 to 60 × 50 | **Disagree — 1.3** |
| 12 | Speaker drive | audio board | explicitly not the audio board | **Disagree — 1.5** |
| 13 | 3.5 mm jack | its own carrier board at the plate | Kelvin ground sense taken **at the jack** | Consistent only if the sense pair runs the ~60 mm down the cable; see 4.4 |
| 14 | Light sensor | its own board at the **rear port face**, behind a Ø4.8 hole | on the carrier, needs its own aperture, must not see the halo | **Disagree — see 6.6** |
| 15 | Energy buffer (supercapacitors) | not mentioned anywhere in the mechanical design | two Ø10 × 31.5 mm cylinders, or Ø10 × 22.3 mm | **Impossible — see 3.3** |
| 16 | Vibration actuator | on a pad on the structure at 258° | "spring contacts or pogo pins, do not solder" | **Gap — there is no board at the actuator to carry pins** |
| 17 | Motor rotor sensor | in the carriage, which **moves** 2.4 mm | JST GH, 5-way, "keep it short, twisted or shielded" | **Gap — a cable to a moving part with no flex life specified** |
| 18 | Motor rail | 5 V (driver's maximum is 11 V) | "consider a boost converter for the motor rail alone" | See 3.4 — there is already a 12 V rail |
| 19 | External USB-C | its own vertical board at the port face | both briefs ask "which board owns this?" | Settled mechanically; the briefs have not been told |
| 20 | Chassis / ground bond | one "ground-bond hole" in the plate | audio: jack sleeve is the only reference to the outside world | **Gap — see 4.1** |

### 2.1 v10 does not test the two things most likely to fail

Interfaces 1 and 2 are not a documentation slip — they are two different architectures.

In v10 the audio board is a USB device **of the Pi**. The PC therefore cannot see it as a sound card at all; the Pi would have to re-present it as a USB audio gadget of its own, which is a completely different and much harder software path. In production the audio board is a **sibling** of the compute module on the internal hub, and the PC sees it directly.

Likewise the motion board talks serial to the Pi in v10 and presents itself as a keyboard and mouse to the PC in production.

**So v10 proves the mechanical design and nothing about the electrical architecture.** That is a legitimate scope for a mechanical prototype, and the specification says as much. But it means the two riskiest claims in the whole product are still untested and there is no plan that tests them:

- a compute module in peripheral mode presenting a keyboard and mouse **through a self-powered hub** to Windows;
- an XMOS audio device enumerating as a sibling through the same hub, alongside it.

The carrier brief already prescribes the fix — two days on a bought compute module, the official input/output board and an off-the-shelf powered hub. **It should be scheduled as its own bench task with its own date, not left as an open question**, because if it fails, the whole topology changes and the carrier is redrawn.

New information from this review, which lowers the risk but does not close it: a keyboard-and-mouse gadget **is** published working on the same BCM2712 silicon (`freewarefocus/py400kb`, on Pi 5, Pi 400 and Pi 500+), and a compute module 5 composite gadget **is** published working for networking, serial and storage (PiLink PL-R5). Nobody has published the combination on a compute module, nobody has published two separate HID interfaces on this generation, and nobody has published any of it through a hub. Also worth knowing before the bench day: Raspberry Pi's own CM5 datasheet hedges — *"The USB 2.0 port can operate in USB On-The-Go (OTG) mode. While not officially documented, some users have successfully enabled this functionality."*

### 2.2 The halo changed and the electrical documents did not hear

Ryan's ruling on 5 September moved the halo from discrete side-firing LEDs on a custom flex to **a bought addressable strip stuck to the wall**. The specification carries that through: 46 LEDs, about 1.0 A at full white, 5 W.

The motion brief and the carrier brief still carry **90 LEDs and 3.3 A**, and the specification's own power section (6.8) still says *"halo 3.2–4.0 A at full white"* — so the specification contradicts itself between 4.8 and 6.8.

The consequences are all good news and all need acting on:

- **The 5 V step-down converter was sized at 10 A largely because of the halo. It no longer needs to be.** See 3.1. That matters because the converter is the second largest heat source and it has an 8 mm height allocation.
- The refresh time falls from 2.70 ms to 1.38 ms per frame, so the argument for splitting the string into three chains largely evaporates.
- The "470 Ω at the first LED, 100 nF per LED, three power injection points 120° apart, 2 oz copper on the flex" instructions are properties of a flex you design. **On a bought strip you get what the strip has.** The motion board's obligation shrinks to one level-shifted data line and a power feed — but you also lose the ability to specify the decoupling, which is the usual reason cheap strips glitch. Worth buying two candidate strips and looking at the data line on a scope before committing.
- **46 LEDs against 60 detents.** The halo cannot show one light per detent; its angular quantisation is 7.8° against a 6° detent. Any light language built on "one notch, one LED" is not available. That is a design decision, not a fault, but it should be made deliberately.

---

## 3. Power

### 3.1 The budget, reworked with the parts as they now stand

The specification's section 6.8 worst case (8–10 A at 5 V) was written before the halo changed and uses the Pi 5's 5 A supply rating rather than the compute module's 2.5 A design peak.

| Load at 5 V | Worst case | Realistic sustained | Source |
|---|---|---|---|
| Compute module | **2.5 A** | 1.0–1.4 A | Raspberry Pi: *"Power supply designs should accommodate 5 V at up to 2.5 A"* |
| Halo, 46 LEDs | 1.0 A (full white) | 0.3 A (a colour at 30 %) | specification 4.8 |
| Panel, logic + analogue + backlight | 0.4 A | 0.4 A | derived from 4.1: 37.2 V × 20 mA plus rails and converter losses |
| Motor | 2.0 A quoted — **but see 3.4** | 0.2–0.5 A | driver's peak rating, not the motor's measured draw |
| Clutch servo | 0.5 A assumed | 0 A between transitions | not published by the vendor |
| Audio board | 0.34 A | 0.135 A | audio brief section 7 |
| Motion board logic | 0.15 A | 0.15 A | estimate |
| Hub, touch, light sensor | 0.10 A | 0.10 A | estimate |
| **Total at 5 V** | **≈ 7.0 A, 35 W** | **≈ 2.5 A, 12.5 W** | |
| **From the 12 V inlet at 90 %** | **≈ 3.2 A, 39 W** | ≈ 1.2 A, 14 W | |

**The 12 V 5 A brick is right-sized** — 65 % loaded at the worst case, which is the correct place to be. **The 5 V 10 A converter is oversized**, and shrinking it to a 7 A part is worth doing on both height and heat.

Two things the budget does not yet say and should: **whether these peaks can coincide** (the motor's is milliseconds, the halo's is sustained, the compute module's is a burst) and **what happens when they do**. That is a transient question about the converter's response and the wiring impedance, not about the number on the brick's label.

### 3.2 The parallel 5 V sources in v10 are a real hazard, not just an open question **[hard]**

The specification flags it twice (4.5 and 6.8, question 6): the converter feeds the Pi on header pins 2/4/6 while the PC's USB-C cable is plugged into the Pi's own USB-C socket. That parallels two 5 V sources through the Pi's power-management chip.

This should be closed now rather than carried, and it is a **cable specification, not a board change**: cut the VBUS conductor in the internal USB-C cable so only the four data conductors and the shield reach the Pi. Buy or make one cable that way, mark it, and note in the build document that a standard cable must never be substituted.

Note the consequence to check on the bench: with VBUS cut, the Pi has no electrical indication that a host is attached. On the production carrier this is solved properly and elegantly — the hub sits in front, supplies VBUS to the compute module from our own rail continuously, and drops its own upstream pull-up when the PC goes away. **In v10 there is no hub, so host presence must come from somewhere else or be ignored.** Worth an hour's thought before the first plug-in.

### 3.3 The energy buffer cannot physically exist in this object **[hard]**

The motion brief specifies two Eaton HB supercapacitors in series, Ø10 × 31.5 mm each, or Ø10 × 22.3 mm for the smaller part.

The internal cavity between the plate top (z 8.0) and the deck (z 19.48) is **11.5 mm**, and the board envelope on the deck is 7.4 mm. Neither part fits in any orientation, on either level. The mechanical design does not mention supercapacitors anywhere, so this has never been reconciled.

**Delete the bank.** The brief already offers the exit — *"instrument the 5 V rail on the bench with the motor rendering detents at full effort and look at the droop. If it is under 100 mV, delete the bank"* — and 3.4 below suggests the droop will be small, because the motor probably cannot draw the current the bank was sized for. Doing so also deletes the balancing resistors, the inrush limiter, and the safety note about the board staying live after unplugging.

**But keep the reason the bank was attractive**, which was not the motor at all: it kept the rail up long enough for a graceful shutdown. That problem is real and is addressed in 3.5.

### 3.4 The 2 A motor figure is probably wrong, and there is a 12 V rail nobody is using **[likely]**

The MY-3514C is a gimbal motor: high phase resistance, low current, built for smooth torque at low speed rather than for power. Its parameters are unpublished — the motion brief says so and budgets a day of bench measurement — but gimbal motors of this frame are typically 8 to 20 Ω per phase. **On a 5 V rail that is a few hundred milliamps, not 2 amps.** The 2 A in every power table is the *driver's* peak rating, which the motor will never reach at 5 V.

Two consequences:

- **The power budget should not carry 2 A for the motor until it has been measured.** It inflates the converter, the connectors and the wiring.
- **The torque available is voltage-limited, not current-limited**, which is exactly what the motion brief suspects: *"Raising the motor rail above 5 V is the cheapest torque available."* It proposes a boost converter from 5 V. **There is already a 12 V rail at the inlet.** A small 12 V → 9 V step-down is simpler, more efficient and quieter than a 5 V → 9 V boost, and the specification even notes the 12 V rail is *"available for anything that wants it later"* without connecting the two thoughts. The driver's published maximum is 11 V, so 9 V is a safe target with headroom.

This is the one place in this review where the separate documents have left value on the table rather than created a risk.

### 3.5 There is no clean shutdown, and the compute module runs Linux **[hard]**

The object has no power switch. Its on/off is the barrel plug. The compute module boots Linux from eMMC and **every disconnection is an unclean shutdown.** Over sixty units in daily use that is a filesystem-corruption story, and the field recovery path for it is section 7.5, which is itself unproven.

This is a well-understood problem with three standard answers, and one of them should be chosen deliberately:

1. **A read-only root filesystem with a writable overlay.** Costs nothing in hardware, is the standard answer for appliances, and needs to be decided early because it shapes how TorqueOS stores settings.
2. **Detect the loss of mains upstream and shut down.** Needs a comparator on the 12 V rail, a signal to the compute module, and enough hold-up capacitance on the 5 V rail to complete a shutdown — a few hundred milliseconds, which is a bank of electrolytics rather than supercapacitors.
3. **A soft power button.** Pin 92 on the module is a power button input; the carrier brief already suggests fitting it. It would need somewhere to be on a seamless object.

(1) plus (2) is the right combination, and (2) is also what the motion brief wanted the supercapacitors for — *"park the clutch, fade the halo, tell the computer... that is what makes the object feel considered rather than just cutting out."*

---

## 4. Electrical integrity, grounding and compliance

### 4.1 The chassis is a floating metal object the user holds, and nothing says what it is bonded to **[hard]**

The plate has *"a ground-bond hole"* and that is the sum of what the documents say about chassis potential.

This matters more here than in a plastic product, for four reasons at once:

- **The supply is almost certainly a Class II double-insulated brick with no earth.** The chassis potential is then set by the brick's mains-side filter capacitors, which typically hold it near half mains through a high impedance. On a bare metal object under the hand that is the classic faint tingle, and into an audio path it is the classic hum.
- **The audio board's rule says the jack sleeve is its only reference to the outside world and nothing may share that copper.** If the jack's metal shell also bonds to the steel plate, that rule is broken by the mechanics. The specification's jack, the Switchcraft 35RAPC4BH3, is a metal panel jack in a steel plate. **Decide explicitly whether the shell is isolated from the plate**, and the audio brief already says it must be.
- **The knob is a floating conductor the user rubs.** It touches three plastic wheels and air. It will accumulate charge, and the nearest thing for it to discharge into is the optical encoder, 1 to 2.5 mm away across the code strip. There is no bleed path anywhere in the specification. An earlier conversation raised running a sprung contact in the wheel groove for exactly this and **it has not survived into the specification.** It should — a leaf or a conductive bearing, one part, and it also stabilises the capacitive touch reference.
- **The touch sensor needs a stable ground reference against the user.** Capacitive touch on a floating chassis inside a metal ring the user is gripping is a harder problem than touch on a normal tablet, and touch was named a tier-one component.

**This is one decision — a written chassis and shield grounding scheme — and it should be made before either board is drawn.** It sets where the shield of the internal USB cable lands, whether the jack shell is isolated, whether the knob is bonded, and where the star point is.

### 4.2 Conformity: nothing in any document mentions it, and it is not optional at sixty units **[hard]**

Verified for this review. For a UK company placing sixty units on the market:

- **Because the product contains a radio** (the compute module's wireless), the **Radio Equipment Regulations 2017** apply to the finished product and *displace* the EMC and electrical safety regulations, pulling both back in as essential requirements. So it is one regime, not three, but it is the strictest one.
- **The pre-certified module does not carry over.** There is no "modular approval" concept under the UK or EU regime — the manufacturer self-declares conformity of *"the radio equipment, in all its possible configurations"*, and that means your dial, not the module. You may **reuse** the module's transmitter test evidence if the antenna, host and firmware conditions hold; you must still do **radiated spurious emissions in your host, and the full electromagnetic compatibility suite**, because your motor driver, your LED strip, your converters and your USB-C cable are noise sources the module was never tested with. Raspberry Pi say the same thing in their own antenna guidance.
- **There is no small-volume or prototype exemption.** The scope exclusions cover radio amateur, marine, airborne and research evaluation kits. Sixty units placed on the market is placing on the market.
- **CE marking alone is now valid for Great Britain**, indefinitely, since SI 2024/696 removed the expiry on recognition of EU requirements. For sixty units that is the obvious route — one mark, both markets. (Note the GOV.UK RoHS guidance page is out of date on this.)
- **WEEE is the one real relief:** under 5 tonnes a year makes you a small producer, registering directly with the Environment Agency for about £30 a year rather than joining a scheme.
- **You must produce a technical file and a declaration of conformity regardless of who does the testing**, and the required contents are listed item by item in the regulations — including photographs of internal layout, circuit diagrams, the versions of firmware affecting conformity, and the test reports. Retention is ten years.

**Cost, as an order of magnitude rather than a quote.** One UK laboratory publishes a price list: £2,600 to £4,500 for electromagnetic compatibility depending on how many cabled interfaces the product has, and £5,000 for radio testing per sample. Most laboratories quote rather than publish. **A realistic budget for this product is £6,000 to £12,000 for full testing plus at least one retest cycle**, and it sits at the expensive end because a brushless motor driver, an LED strip, a display and switching converters in a metal enclosure with a cable to a PC is a hard case.

**The cheapest legitimate lever is to disable the radio and not ship it.** If the product is not radio equipment the whole Radio Equipment regime falls away, the safety regulations do not bite at 12 V DC, and you are left with electromagnetic compatibility plus RoHS and WEEE. The product is USB-connected and mains-powered; ask honestly what the wireless is for.

This belongs in the commercial documents as a line item with a date, because pre-compliance testing wants to happen on the **first** assembled unit, not the sixtieth.

### 4.3 The emissions risks specific to this design **[likely]**

Worth knowing before layout, because they are cheap to design around and expensive to fix afterwards:

- **An 800 kHz data line running the full 465 mm circumference of the object** is a loop antenna with harmonics well into the range the tests sweep. Keep the return tight against it, and prefer the shortest possible run from the buffer to the strip's first LED.
- **A motor bridge switching with 7 ns fall times** a few centimetres from an optical encoder and a converter. The motion brief's "keep the phase current loop tiny" is the right instruction and it is the one most often ignored.
- **A metal enclosure with three cables leaving it** is a shield with three holes in it. Cables are the usual radiator, not the box.
- **The compute module's wireless antenna keep-out** — at least 10 mm, no metal beneath — inside a machined metal object. The carrier brief flags it and rightly calls it a mechanical decision with an electrical deadline. If the radio survives 4.2's question, **the external antenna variant is probably the honest answer**, and it needs a place to live.

### 4.4 The Kelvin ground sense loses most of its point over a cable **[likely]**

The audio brief makes the converter's ground-sense connection to the jack sleeve a headline item — *"this is the difference between the datasheet's distortion figure and a mediocre one"*. The mechanical design puts the jack on its own carrier at the plate, roughly 60 mm and one connector away from the audio board on the deck.

Sensing through a crimped contact and 60 mm of wire is still better than not sensing, but it is not what the datasheet figure was measured with. Either accept it knowingly and stop quoting the figure, or move the audio board down to the floor beside the jack — which is what 1.3 recommends for a different reason. **The two problems have the same solution.**

---

## 5. Thermal, beyond section 1.1

### 5.1 The step-down converter is a bought module in a hot box on a plastic deck **[likely]**

A 5 V converter delivering 15 W sustained at 90 % efficiency dissipates about 1.7 W; at the 35 W worst case, nearly 4 W. It is a 38 × 25 × 8 mm bought module with no heatsink, screwed to a **printed deck**, inside a cavity that section 1.1 says runs 20 to 30 K above the room.

Two things to check rather than assume. **A bought module rated 10 A is rated 10 A with airflow** — derated in still air at 50 °C ambient it may be a 4 to 5 A part, and the vendor's derating curve is the thing to read before believing the number. And **PETG softens around 80 °C**; a warm regulator bolted to it is a soft mount. For v10 that is acceptable; for production, mount the converter's function to the steel, not to plastic.

Shrinking it to 7 A per 3.1 helps on all three counts.

### 5.2 The motor driver is a 1 A continuous part with a 2 A number attached to it **[hard]**

The TMC6300's published continuous rating is **1.0 A per bridge below 110 °C**; 2 A is its peak. Its own datasheet says thermal behaviour becomes critical at or above 1.4 A and demands four layers with five thermal vias in the pad — which the motion brief correctly specifies.

The case nobody has worked is **a user leaning on the knob against an end stop**. That is not a transient: it is two phases carrying direct current for as long as the user pushes. **Define the end-stop and stall current limit in firmware as a number with a duration**, and check the driver's junction temperature at it. Per 3.4 this may be a non-issue on a 5 V rail, and may become one if the motor rail is raised to 9 V.

### 5.3 Where the heat is not

Worth stating plainly because it inverts the intuition: the halo's heat lands on the **printed structure wall**, not on the steel. At the specification's own numbers (about 5 W over 465 mm of strip at full white) that is fine for PETG. It would not be for a denser strip, and the specification says so. Keep it in mind if the strip choice changes.

---

## 6. What still has no owner

Not risks — absences. Each of these appears in one document and nowhere else, or in none.

### 6.1 The cover lens with its bonded touch sensor — the largest single gap

Every number in specification 4.2 is marked ASSUMED: the diameter, the thickness, the border, the tail width and position. There is **no supplier, no part, no touch controller chip, and no settled interface** (interface 3 in the register disagrees between I²C and USB).

This is the part that delivers *"the absolute fundamental requirement is that the screen feels fast and it's beautiful"*, it is a custom optical bonding job to a bare panel, and it sits on the critical path for the display seat, the deck layout and the knob's lip. **It is the item most worth starting this week**, because it is the one with the longest lead time and the least control.

Note also that **whichever route touch takes, its path to the PC runs through the compute module's gadget port** — so Windows Precision Touchpad behaviour, which was an explicit ambition, depends entirely on the single unproven item in 2.1.

### 6.1a The production board layout has not been done at all

The two-level arrangement — floor plus mezzanine deck — exists because of three v10-only parts: the full Pi 5, its cooler, and the 65 × 64 adapter. Production deletes all three. Specification 8.5 then works the production height stack carefully (compute module on a plate boss, carrier, panel, lens, 33.9 mm overall) and says *"No deck, no adapter, no ribbon, no Pi window"* — **but it never says where the audio and motion boards go.**

They cannot simply stay where they were, because there is no deck. And the floor is not obviously roomier: the carrier now has to hold the module, the hub, the external socket, the panel's rails and its 37 V backlight driver (1.4) and the light sensor, which makes it considerably larger than the module's own 55 × 40, and it shares the floor with the motor sector, the speaker, the step-down converter and the rear sockets — the same 15,600 mm² that section 8.2 already showed cannot hold everything.

**This is the next piece of layout work and it should be done before any board is drawn**, because it decides how many boards there are. Merging the carrier and the motion board is plausible once the deck is gone; merging the audio board into either is not, for the noise reasons in 1.3.

### 6.2 There are nine made circuit boards, not three

Specification 5.8 lists them: the jack carrier, the audio board, the motion board, the USB-C board, the light-sensor board, the encoder breakout, the commutation board, the LED flex, and the carrier. **Three have briefs. Six do not.** They are small and mostly trivial, but each needs a schematic, a fabrication order, an assembly and a test, and at sixty units that is real cost and real schedule. Name an owner for the six, even if the answer is "one afternoon each, batched into one panel".

### 6.3 The wiring harness

Counting the register and the assembly sequence, the object contains **about twenty cable assemblies**. None is specified as a drawing. Two need particular attention:

- **The cable to the rotor sensor runs into the carriage, which moves** 2.4 mm every time the clutch actuates. That is a flexing cable with a life requirement and no specification. It needs a flex-rated cable and a strain-relieved route, or the sensor needs to move.
- **The halo strip's lead has to cross the structure wall** to reach the motion board on the deck, past the vent slits, the code band and the wheels. Not modelled.

The motion brief's advice stands and should be a purchasing decision now: *"At sixty units, buy pre-crimped leads or have the harness made."*

### 6.4 The code strip has a seam **[likely]**

A 455 mm strip on a 455 mm circumference means the two ends meet. **An incremental optical encoder with a butt joint produces one bad count position per revolution**, and nothing addresses it — not an index mark, not a deliberate overlap, not a software strategy for detecting and ignoring it.

Related and also unaddressed: the encoder is **incremental**, so absolute knob position is unknown at power-on. For volume that is correct behaviour. For "sixty detents" as absolute positions with end stops it needs either a homing strategy or an explicit decision that positions are always relative.

### 6.5 The vibration actuator has nowhere to put its pogo pins

The actuator sits on a pad on the structure at 258°. Its vendor warns against soldering wires to it; the motion brief therefore specifies spring contacts or pogo pins. **Pogo pins need a small board to mount to and a controlled compression distance**, and there is no board at 258°. Either add one to the list in 6.2 or accept soldered wires against the vendor's advice and say so.

### 6.6 The light sensor is in the wrong place

The carrier brief says it *"needs its own aperture — not behind the halo diffuser, which attenuates 50–65 %"*. The specification puts it behind a Ø4.8 hole in the **rear port face**, at desk level, under the halo, facing the wall behind the object.

That is a sensor for adapting display brightness to the room, pointed away from the room, next to the object's own light source. It will read the halo's spill and the desk. **[likely]** the correct place is the top surface, near the lens, facing the user's ceiling — which is a mechanical problem because the top surface is either the knob (which rotates) or the 12.8 mm metal ring.

### 6.7 Software is not in any of these documents

TorqueOS on the compute module, the RP2350 firmware, the XMOS firmware, the HID descriptors, the Precision Touchpad descriptor, the panel driver from 1.4, and the protocol between the compute module and the motion board. The hardware documents are now detailed and the software is a larger job than the hardware. It does not need a specification today, but **it needs to appear on the same plan**, because two hardware decisions are waiting on it: whether touch is I²C or USB, and whether the panel driver is written now (which would let production skip the adapter entirely — the specification's own question 3).

---

## 7. Assembly and service

### 7.1 The display is bonded before it is ever powered

Specification 6.10, step 3, bonds the panel to the structure's seat with tape. The panel is not connected to anything until step 6 and not powered until the whole object is built. If the panel is dead, or the flex is nicked, you peel the most expensive single part off a bonded seat.

**Insert a bench bring-up before the object is assembled**: panel, adapter and Pi on the bench, running, for an hour, before the panel goes near the structure. It costs nothing and it is the difference between a bad afternoon and a bad week.

### 7.2 The riskiest connection is made blind, holding a deck

Step 6 plugs the panel's **45-way 0.3 mm-pitch flex** into the adapter while the deck is held above the structure, with 44 mm of the flex's 45.8 mm already used by the route. That is a delicate zero-insertion-force connector on a fragile flex, made two-handed, over the panel, with no slack.

Worth designing around: a longer flex path, or a bridge flex with a connector at the seat so the deck can be plugged after it is seated, or an assembly fixture that holds the deck at a known height.

### 7.3 The motor goes in third from last, blind, into a fitted deck

Step 8 inserts the carriage with a 28 mm tall tab **up through a 6 × 10.6 mm slot** in a deck that is already screwed down, engaging the servo's pushrod above it, from below, with the drive band already on the bell. This is the hardest step in the sequence and it is nearly the last.

The checker proves the clearances. **It does not prove that a hand can do it.** Consider whether the motor and its carriage can go in before the deck, with the servo linkage made afterwards through a service opening.

### 7.4 Service means total teardown

Everything is re-openable, and reopening means: pad off, three screws, plate off, then the entire stack comes apart from the bottom and the display stays bonded to the structure. **To replace a failed audio board you disassemble the whole product.**

For a sixty-unit halo product that may be the right answer — but it should be a **stated decision** with a repair story attached, not a consequence nobody chose. It also argues for burning in each unit before it ships.

### 7.5 The production programming and field recovery path is unproven **[hard]**

The compute module's storage is written by holding pin 93 low at power-up and running Raspberry Pi's `rpiboot` from a PC. After final assembly, the only route to that port is **through the internal hub**, because the external USB-C socket faces the hub's upstream port, not the module.

Verified for this review, and the answer is genuinely unsettled. Raspberry Pi's own documents contradict each other: the `usbboot` README's recommended host configuration explicitly puts a **powered hub in the data path**, while the troubleshooting guide says *"Remove any hubs between the Compute Module and the host"* and the flashing guide warns that *"in some cases, USB hubs can prevent the host device from recognising the Compute Module."* The tool itself has a command-line flag for selecting a module by its position in a multi-level hub tree, which is not the behaviour of a tool that assumes a direct connection. **No published report exists of `rpiboot` through a hub inside a product, either working or failing.**

One concrete thing to test for, which is the most plausible failure mode: **`rpiboot` runs in three or four stages and the device disconnects and re-enumerates with a different descriptor at each one.** A cheap hub that handles one enumeration may not handle four in quick succession.

**Add this to the two-day bench task in 2.1 — it is the same hardware.** If it fails, every unit must be programmed before assembly and can never be recovered in the field without a teardown, which changes the production process and the warranty story.

---

## 8. The order to take the decisions

Ordered so that each one unblocks the next, not by size.

| | Decision | Blocks | Effort |
|---|---|---|---|
| 1 | **The bench rig**: bought compute module + official IO board + powered hub. Prove the keyboard-and-mouse gadget to Windows, the audio device as a sibling, and `rpiboot` through the hub | The entire carrier architecture; 2.1, 7.5 | 2–3 days |
| 2 | **State the halo's sustained brightness cap and the thermal target** as numbers | The power budget, the converter size, the enclosure, compliance | an afternoon |
| 3 | **The production board layout** — where all three boards sit with no deck, and therefore how many boards there are (6.1a); includes where the audio board lives, deck or floor | Board sizes, three cable lengths, the Kelvin sense, 1.3 and 4.4 | 1–2 days |
| 3a | **Fan or no fan, and if a fan, through-flow** (1.1a) | The production enclosure's outside; follows from 2 | half a day |
| 4 | **The connector family**, one decision across all three boards | Every board's edge routing | an hour, with 1.2's table |
| 5 | **Chassis and shield grounding scheme**, written down | Both boards, the jack, the knob, the touch sensor | half a day |
| 6 | **Start the lens and touch sensor enquiry** | The seat, the deck, the knob lip, touch behaviour | longest lead time — start now |
| 7 | **Reconcile the halo to 46 LEDs** across all four documents | Power, the motion board, the light language | an hour |
| 8 | **Measure the motor** — phase resistance, torque, actual current at 5 V and at 9 V | The power budget, the supercapacitor question, the boost decision | a day |
| 9 | **Scope the panel's rails and backlight driver** onto the carrier | The carrier's area, its heat, its cost | a day |
| 10 | **Put conformity on the plan** with a date and a budget | Nothing yet — but it gets expensive if it is late | half a day |

Items 2, 4 and 7 are decisions you can take this week from what is already written down. Item 1 is the one that matters most, because everything on the carrier board is routine except the thing nobody has proved.

---

## What this review did not cover

Acoustics and the speaker's enclosure volume; the knurl and the finish; anything commercial; the interaction design; and the software architecture beyond noting in 6.7 that it is absent from these documents. The mechanical clearances were taken as proven — the specification says its checker proves them and this review did not re-derive them.
