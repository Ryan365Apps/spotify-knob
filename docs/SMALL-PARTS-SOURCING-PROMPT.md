# Handoff prompt — the small boards, the power inlet, and the wiring

Copy everything below the line into a new session.

---

## The premise

I am building **one working prototype** of a premium haptic desk dial. A production run of sixty to seventy units exists as a plan, but it is not what this exercise is about. Treat volume sourcing as a secondary check — a "does this dead-end later" note on each recommendation — not a filter. **A single breakout board or cable that I can buy one of, this week, is a perfectly good answer.** Minimum order quantities, unit price at volume and certification are all secondary.

## Your job

Everything below is a small function that has to exist in the object and currently has **no home** — most of them are one component on a fifteen-millimetre square of circuit board. My bill of materials lists six of them as a single line reading *"small boards — no briefs written"*, which is where work goes to die.

**The mantra is buy convenience.** I am one person. I do not want to have six tiny circuit boards laid out, panelised and assembled if a breakout board, a pre-made cable or a panel-mount part already does the job. For a prototype, an ugly bought part on flying leads beats an elegant custom board that does not exist yet.

For each function, tell me where it should live, in this order of preference:

1. **On something already in the device**, or handled by a part already being bought.
2. **On something I can buy** — a breakout board, a module, a pre-made cable, a panel-mount part.
3. **On a small custom board, and only where nothing buyable exists.** If some of these do end up custom, tell me whether they should be one panelised set or separate pieces.

**Do not design a circuit board.** No schematic, no layout, no parts list for a custom board.

## Part one — power

**A. Choose the mains power supply.** The requirement is **12 V, 5 A, Class II (double insulated, two-pin, no earth connection)**, an external brick. **The part has not been chosen.** One specific thing to check that most people skip: **the datasheet must publish a touch-current or leakage-current figure.** The object has a metal knob and a metal rim, and the grounding design assumes a Class II supply — a Class I supply with an earth pin would change the whole scheme. Name two or three specific parts with links, and confirm each one publishes that figure.

**B. Get that power into the object.** Currently a CUI PJ-063AH right-angle barrel inlet, 5.5 by 2.1 mm. Confirm or improve. Note that the mechanical model needs a CAD model of whatever is chosen.

**C. Convert 12 V to 5 V.** Currently a bought converter module of about 6 to 7 amps, envelope 38 by 25 by 8 mm, bolted to the aluminium base plate through a thermal gap pad. Two things to check. **First, the derating curve** — a module advertised at 10 A is usually rated 10 A only with forced airflow, and I need the still-air number. **Second, the more interesting question: should there be a converter at all?** A 5 V supply straight into the object removes a whole component and its heat. Against that, 5 V at the full load is a lot of current down one barrel connector. Work out the actual total load, then tell me which arrangement is right.

**D. Distribute the 5 V without the motor's return current flowing through the audio circuitry's reference.** The design rule is a star from the inlet — separate pairs of wires to each destination, never daisy-chained, never a shared return conductor. Tell me whether this needs any hardware at all beyond a connector and a piece of copper, or whether there is a bought distribution part worth having.

**E. Resolve two 5 V sources being connected at once.** This one can stop the prototype working, so treat it as the most important item in part one. The Raspberry Pi 5 is fed 5 V on its 40-pin header from the converter. The host computer's USB-C cable is also plugged into the Pi's USB-C socket, which is a power input. That is two supplies in parallel. The two candidate answers already on the table are **cutting the 5 V wire inside the internal USB cable**, or **fitting an ideal-diode part on the header feed**. Tell me which is right, what it costs, whether a bought cable or part does it, and what happens in each of the four combinations of mains-connected and computer-connected.

## Part two — the small boards

**F. Ambient light sensor.** A Vishay VEML7700 on an I²C bus, behind a 4.8 mm hole in a printed rear port face, so the display and the halo can adapt to the room. This is the most obviously buyable item on the list — several vendors sell exactly this sensor as a breakout. Find them and **give me actual board dimensions**, because it has to fit behind a small hole in a crowded rear panel.

**G. External USB-C socket.** A socket on the outside of the object, connected inward to the Raspberry Pi's own USB-C socket by a short lead. Currently a GCT USB4520 mid-mount receptacle on a small custom board. **Its metal shell is deliberately bonded to the chassis.** Is there a panel-mount USB-C to USB-C lead, or a bought breakout, that deletes the custom board? Watch the internal space: the lead has to leave the Pi's socket going straight up, because a right-angle plug there collides with an HDMI plug.

**H. 3.5 mm headphone jack.** A jack on the outside, connected inward. Currently a Switchcraft 35RAPC4BH3 on a plain custom carrier board. **Its shell must stay electrically isolated from the metal chassis** — it is the audio circuitry's only outside-world ground reference, and if it touches the chassis the object hums. This is a stated requirement, not a preference, and it is why the port face is a printed plastic part rather than metal. Find a buyable panel-mount jack or breakout **that does not bond its shell to its mounting**, and say explicitly how you confirmed that.

**I. Vibration actuator contacts.** The actuator is a linear resonant type, 10 by 10 by 4 mm. Its maker warns that **soldering wires to it can separate the adhesive**, so it must be contacted by **spring pins, not solder**. Currently a 7 by 8 mm custom board with two pogo pins pressing against pads. Mill-Max is the named supplier. Is there a buyable pogo-pin block or connector that does this?

**J. Motor rotor sensor board.** An MT6701 magnetic sensor reading a magnet on the motor shaft, on a small board. **It rides on the motor's carriage, which moves 2.4 mm every time the clutch operates**, so its cable must be flex-rated for at least a hundred thousand cycles at that travel. Two questions: is there a bought MT6701 breakout small enough, and **what cable actually survives that duty** — this is a real sourcing question and I have no answer for it.

**K. Knob encoder board.** A Broadcom AEDR-8300 reflective optical sensor on a small board, sitting on a printed shim on a flange, looking up at a code ring on the underside of the knob at a 2.0 mm gap. The only external component its datasheet specifies is a 220 Ω resistor, which should live on this board so the cable carries no high-current node. Is there a bought breakout, and if not, is this the one that genuinely has to be custom?

**Note on J and K:** a parallel exercise is looking at whether a bought board can cover the device's motion functions. If it recommends something that already carries one of these sensors, that board disappears from this list. Flag the dependency rather than assuming either way.

## Part three — wiring

**L. The harness.** About twenty cable assemblies. The chosen connector family is **Molex Pico-Lock 1.50 mm, right angle** — 2.00 mm mated height, 30 mating cycles, positive latch, AWG 24 to 28. It was chosen over the small JST parts specifically because those have no latch, and this object gets picked up. Questions: **are pre-crimped Pico-Lock leads buyable in the UK in single quantities**, or does every one have to be hand-crimped? Hand-crimping 1.5 mm contacts is where solo builds go wrong, and one marginal crimp produces an intermittent fault that takes a week to find. If pre-made leads are not available, what is the realistic alternative — a harness house that will quote one set, a different connector family that ships pre-made, or a crimp tool worth buying?

**M. Chassis bonding hardware.** External-tooth star washers and ring terminals, and a 1 MΩ resistor bleeding the metal knob to ground through a sprung phosphor-bronze leaf. The leaf's form and mounting are **not designed**. Is there a buyable spring contact or sprung pin that does this job — bearing lightly on a rotating aluminium part without being felt through the knob?

## Explicitly out of scope

Do not spend effort on these — each is being handled elsewhere or sits lower in my priority order:

- **The motor, encoder logic, clutch servo, vibration driver and the LED string's control.** A separate exercise covers those.
- **The carrier board.** It hosts a Compute Module 5, which is the production computer, not the prototype's.
- **The audio board.** Lowest priority of everything in the project.
- **The display and the HDMI adapter.** Already bought and confirmed separately.

## What to give me back

1. **The headline in one paragraph.** How many of these thirteen items can be bought, and how many end up custom.
2. **A table**: items A to M down the side; for each, the recommendation, the specific part or supplier, the price, the size, and a status of **bought / custom / undecided**.
3. **The custom residue** — whatever is genuinely left, with a note on whether it is one panelised set or separate pieces.
4. **What to buy this week**, with links and prices, in one order if possible.
5. **What could go wrong**, especially on items E, J and L, which are the three I think are genuinely uncertain.

Every claim about a part's capability must come from a datasheet, a vendor page or a distributor listing, with the source linked. Where a vendor does not publish something — a leakage figure, a flex life, a still-air derating curve — write **not published** rather than estimating, because those are exactly the numbers that get assumed and then bite.

## Constraints

- **UK sourcing, one of each.** Prices in pounds where you can, and whether it ships here and how fast.
- **Space.** The object is 175 mm across and 36 mm tall and it is full. Give actual dimensions for everything. "This needs more room than the model currently has" is a finding to report, not a disqualification.
- **The two grounding rules are absolute:** the USB-C shell bonds to the chassis, the 3.5 mm jack's shell must not. Do not recommend anything that breaks either.
- **Volume, as a footnote only.** One line per item on whether it dead-ends at sixty to seventy units.

## Style

Plain English. Explain any acronym or abbreviation the first time you use it. Critical thinking rather than enthusiasm. Where the honest answer is "this one has to be a custom board", say so plainly rather than proposing a bought part that nearly works.
