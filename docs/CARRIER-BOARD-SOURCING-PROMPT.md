# PARKED — do not run this yet

**Status, 7 September 2026: this is a production-phase document. It should not be handed to a session while the goal is one working prototype.**

**Why.** The carrier board exists to host a **Compute Module 5** — a bare module with no ports that has to be soldered onto a custom board. The prototype does not use one. It uses a **whole Raspberry Pi 5**, bought as a finished product, which arrives with its own ports, power management and storage. The v15 specification says this plainly in its own words: *"It is not the product: the product runs a Compute Module 5 on a custom carrier, and every dimension that exists only to hold a full Pi 5, its cooler, the HDMI adapter and their cables is tagged v10-ONLY."*

So the design has always carried both computers on purpose — the Pi 5 for the prototype, the Compute Module on a carrier for production. `docs/boards/BOARD-CARRIER.md` is **not out of date**; it describes the second of those two. An earlier draft of this document claimed the carrier had been superseded. That was wrong and has been corrected here.

**When to run this.** When the decision is made to move from the Pi 5 to the Compute Module — which is a production decision, not a prototype one.

**What is genuinely needed for the prototype instead.** A handful of small functions that exist whichever computer is fitted, and none of which amount to a carrier board: the mains inlet and the 12 V to 5 V converter, the star distribution of that 5 V, the two-parallel-5-volt-sources problem (specification question 6), the ambient light sensor, the external USB-C socket and the 3.5 mm jack. Those are the six "small boards" in the bill of materials, listed there with no briefs written. **That is the exercise worth running now, and it is a different and much smaller one than this document.**

---

# Handoff prompt — what is left of the carrier board, and can I buy it?

Copy everything below the line into a new session.

---

## The premise

I am building **one working prototype** of a premium haptic desk dial. A production run of sixty to seventy units exists as a plan, but it is not what this exercise is about. Treat volume sourcing as a secondary check — a "does this dead-end later" note on each recommendation — not a filter. **A single development board or breakout that I can buy one of, this week, is a perfectly good answer.** Minimum order quantities, unit price at volume and certification are all secondary.

## Read this first, because it changes the question

The design once used a **Raspberry Pi Compute Module 5** — a bare module with no ports, which has to be soldered onto a custom "carrier" board that gives it power, sockets and a display connector. A design brief was written for that carrier board: six layers, a compute module, an internal USB hub, a USB-C socket, a display connector, an ambient light sensor, power distribution and a backlight driver.

**That brief is out of date. The design has since moved to a whole Raspberry Pi 5 single-board computer, bought as a finished product.** The Pi 5 arrives with its own USB-C socket, its own USB-A sockets, its own HDMI outputs, its own power management and its own storage. The display now goes through a **bought HDMI-to-MIPI adapter** — three parts: a driver board, a flat cable and a display connect board — rather than a display connector on a custom board. So most of what the carrier board existed to do has already been bought.

**Your first job is to establish what is actually left.** Not to look for a carrier board — to work out whether one is still needed at all, and if so what small residue of functions it would carry. Go through the function list below and tell me, for each, whether it is already answered by hardware in the design, answerable by something else I can buy, or genuinely homeless.

Be prepared for the honest answer to be *"there is no carrier board any more, just five small things that need homes."* That would be a good outcome and you should say so plainly.

## Your job

For each function below, tell me where it should live, in this order of preference:

1. **On something already in the device.** The Raspberry Pi 5 and the bought display adapter are already there. If one of them does a job, that job costs nothing.
2. **On something I can buy.** A breakout board, a module, a cable, a finished part. Several of these functions are one component on a fifteen-millimetre square of circuit board, and for a prototype a bought breakout on flying leads is completely adequate.
3. **On a custom board, and only what genuinely cannot go anywhere else.** If something is left, tell me how small it can be made and whether it is one board or three separate tiny ones.

**Do not design a circuit board.** No schematic, no layout, no parts list for a custom board.

## The functions

**A. Run the application software and drive the display.** Already answered — a Raspberry Pi 5, bought whole. Confirm rather than investigate.

**B. Get the picture onto a round MIPI panel.** Currently a bought HDMI-to-MIPI adapter in three parts, taking HDMI out of the Pi. Confirm what this adapter actually provides — and specifically whether it handles the next item.

**C. Backlight enable, backlight brightness and panel reset for a third-party panel.** The old carrier brief listed a panel supply set — plus and minus 5 V analogue, 1.8 V logic, and a 37 V 20 mA constant-current backlight driver with dimming — and marked it **not designed**, with the note that "the prototype adapter does this today". **Establish whether that is true.** If the bought adapter already drives the backlight and dims it, this function is answered and a whole subsystem disappears. If it does not, this is probably the single hardest homeless function and I need to know now.

**D. Take mains power and produce 5 V for everything.** Currently a 12 V barrel inlet and a bought 12 V to 5 V converter module, rated around 6 A. The Pi 5 alone can peak at 5 A, and there is a motor, a servo and up to ninety addressable LEDs besides. Confirm the arrangement and tell me if there is a better bought answer — including whether a 5 V supply straight in, with no converter, would be simpler.

**E. Distribute that 5 V without the motor's return current flowing through the audio circuitry's reference.** The rule in the design is a star from the inlet: separate pairs of wires to each board, never daisy-chained, never a shared return. This is the single most effective noise measure in the object. Tell me whether it needs any hardware at all beyond a connector and a piece of copper, or whether there is something worth buying.

**F. Resolve two 5 V sources being connected at once.** The design has a known gap here: the Pi's 40-pin header is fed 5 V from the converter, while the host computer's USB-C cable is also plugged into the Pi's USB-C socket. Two supplies in parallel. The two candidate answers already on the table are cutting the 5 V wire inside the internal USB cable, or putting an ideal-diode part on the header feed. **Tell me which is right, and whether there is a bought cable or part that does it.**

**G. Provide a USB-C socket on the outside of the object** and connect it inward to the Pi's own USB-C socket. Currently a GCT USB4520 mid-mount receptacle on a small custom board, with a short internal lead. Its metal shell is bonded to the chassis. Is there something buyable — a panel-mount USB-C to USB-C lead, or a bought breakout — that removes the custom board?

**H. Provide a 3.5 mm headphone jack on the outside** and connect it inward. Currently a Switchcraft jack on a plain custom carrier board. **Its shell must stay electrically isolated from the metal chassis** — it is the audio circuitry's only outside-world ground reference, and if it touches the chassis the object hums. Same question: is there a buyable part or breakout?

**I. Read the ambient light level**, so the display and the halo can adapt to the room. Currently a Vishay VEML7700 on a tiny custom board behind a 4.8 mm hole, on an I²C bus. This is the most obviously buyable thing in the list — several vendors sell exactly this sensor as a breakout. Find them, with dimensions, because it has to fit behind a small hole in a port face.

**J. Flash, boot and recover the software, and get service access.** On a Compute Module this needed dedicated pins and links on the carrier. On a Pi 5 it is a memory card or on-board storage. Confirm what is actually needed and what should be brought out for service on a sealed object.

**K. An internal USB hub — is one still needed?** The old design required a four-port hub because a compute module in device mode cannot also be a hub for other boards. In the current design the audio board plugs into one of the Pi's own USB-A sockets, and the motion functions talk over a plain serial link. **So the hub may have disappeared entirely.** Establish whether it has. If it has, a chip, a crystal, a bias resistor and a set of strap pins leave the parts list.

## Overlap with another piece of work

There is a parallel exercise running on the device's motion, haptic and lighting functions. One question appears in both and must not be answered twice differently:

**Can the Raspberry Pi 5 present itself to the host computer as a keyboard and mouse, with no driver installed?** The Pi has a USB device-mode controller and Linux has a gadget framework that can compose one. If it works, a knob turn becomes a scroll event with nothing in between and no microcontroller needs a USB stack.

**If you get to this before the other session does, answer it properly** — what Linux's USB gadget framework supports on a Pi 5, whether a keyboard-and-mouse composite device can coexist with the Pi's other USB roles, whether it works when the Pi is separately mains powered rather than drawing power from the cable, and what Windows and macOS actually do with it. It was flagged in the old brief as the highest-risk item in the whole product, on the grounds that nobody has published this exact combination working. **If you cannot verify it from published sources, say so and tell me the two-day bench test that would settle it.**

## Constraints, in order of how much they matter

- **It has to work, once, on a bench, soon.** That is the whole test.
- **Space.** The object is 175 mm across and 36 mm tall and it is full. The Pi 5 lies on the base plate; small boards live on a printed port face at the rear. Give me actual dimensions for anything you recommend, and treat "this needs more room than the model currently has" as a finding to report rather than a disqualification. For a prototype I will make room.
- **The 3.5 mm jack's shell must stay isolated from the chassis, and the USB-C shell must be bonded to it.** These are stated requirements, not preferences. Do not recommend a part or an arrangement that breaks either.
- **UK sourcing, one of each.** Prices in pounds where you can, and whether it ships here and how fast.
- **Volume, as a footnote only.** One line per recommendation on whether it dead-ends at sixty to seventy units.

## What to give me back

1. **The headline in one paragraph.** Whether a carrier board still exists, and if so what is on it.
2. **An allocation table**: functions A to K down the side; for each, where it lives in your recommendation, and a note. Make the homeless rows obvious.
3. **What disappeared.** Functions the old brief listed that the move to a Pi 5 has already deleted — I want this stated explicitly so I can strike them from the bill of materials.
4. **Anything genuinely left over**, and the cheapest honest way to close it for one prototype.
5. **What to buy this week**, with links and prices.
6. **What could go wrong** — where a bought part or a Pi-side implementation would let me down later.

Every claim about a specific board, chip or module's capability must come from a datasheet, a schematic, a vendor page or a repository, with the source linked. Where a vendor does not publish something, write **not published** rather than estimating. Do not tell me something "should" work.

## Style

Plain English. Explain any acronym or abbreviation the first time you use it. Critical thinking rather than enthusiasm. If the honest answer to any function is that it still needs designing, say so clearly rather than softening it.
