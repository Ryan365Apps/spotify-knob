# Vision — the 60

**Date:** 2026-09-04. **Status:** current requirements. This document is rewritten in place, never appended to; the previous version is in git.

**Companion documents:** `DECISIONS.md` (the numbered decision index), `SOURCING-BOM.md` (every bought part), `v9/V9-SPECIFICATION.md` (the mechanical specification), `SOFTWARE-CONTEXTS.md` (what the software does), `COMMERCIAL-FEASIBILITY.md` (gates, pricing, the run), and the two architecture documents written into the Claude project on 4 September 2026: the processor and display options paper, and the electronics build path.

---

## One line

A machined knurled ring around a five-inch round screen, on a heavy steel base, that plugs into a computer and becomes the one control worth reaching for. Sixty detents, rendered by a motor, so the feel of the click is software. Its own digital-to-analogue converter, so the computer's audio passes through it and the knob is the volume control in the hardware itself.

The category line is **"Cadrane 60 — a haptic desk dial"**. It is not a Stream Deck competitor. It is the one perfect dial that sits beside anything.

## The object

**A heavy, expensive watch sitting on your desk that invites you to move it.** The dial must reward idle handling, not only deliberate use — picked up, spun, fidgeted with. That is the emotional target. Every other decision serves it: if something improves the feel of the ring it wins, and if it competes for budget with the feel of the ring it loses.

The second requirement, added 4 September and now equal in weight: **the screen must feel fast and be beautiful.** Not "acceptable for embedded hardware" — genuinely fluid, sixty frames a second, with depth and light that stand up to being looked at ten thousand times. This is what moved the product off a microcontroller and onto a computer with a real graphics processor.

## Form

- **Roughly Ø150 mm.** The earlier Ø135 limit is withdrawn. The diameter now follows the panel: a Ø127 picture in a 136.5 mm module, plus the knob wall. The proportion that matters is the picture as a share of the face, and it improves — about 85 %, against 70 % on the Ø125 build.
- **Height is derived from the parts, not imposed.** The old 40 mm ceiling was set by a development board we no longer use. A flatter object is accepted.
- **Mass is wanted.** The steel base plate grows with the diameter; more heft reads as quality and helps the flywheel.
- **The knob is one piece** — lip, skirt, diamond knurl and chamfers, no seam, no visible screw. It is the majority of the visible side. It turns on three small wheels running in a groove cut into its own bore, and it touches nothing else. It never touches the display.
- **The metal ring on the top face is about 11 mm wide** at this diameter. That is a deliberate change of character from the earlier design and must be looked at on a print before it is accepted.
- **Sixty detents per turn**, rendered by a gimbal motor pressing on the knob's bore through a silicone band, with the pattern and the weight set in software. The passive magnet detent is deleted. A servo sets the motor's preload, so free spin is real — the motor lifts physically clear.
- **The knob turns itself**, slowly. Not for speed — for a call ringing, for confirming an action, for a splash flourish.
- **Halo ring** of addressable light at the base's lower edge, under an opal diffuser, firing down and outward onto the desk. Full 360°. On the static base, never on the rotating knob.
- **A dedicated mains power supply.** The device is no longer limited to what one computer's cable can deliver. The old firmware cap of roughly 20 % on halo brightness is withdrawn — the halo will be driven properly bright.
- **Sockets at the back:** the mains inlet, a cable to the computer, and a 3.5 mm line output. No permanent cable.
- **Perimeter ports** in the base wall under the knob's skirt for the speaker, the microphones and heat.
- Down-firing notification speaker; the board's microphones retained and made to work, because dictation is a first-tier context.
- **Ambient light sensor** at the back, so screen and halo dim together and evenings never need a manual override.

## What is inside, and why

Settled 4 September 2026 after a full survey of what is buyable.

**A computer, not a microcontroller.** Production is a Raspberry Pi Compute Module 5; development is a Raspberry Pi 5, which is the same processor and the same software. The ESP32-P4 is out. It has no graphics processor at all, its pixel accelerator can only rotate in ninety-degree steps — useless for a menu that tracks the knob between detents — and its memory bandwidth measures about 85 megabytes a second against the 140 the new panel needs simply to be scanned out. No microcontroller sold today does runtime blur, glow and shaded three-dimensional line art at this resolution, at any price.

Rockchip parts are faster on paper. Raspberry Pi was chosen anyway, for one reason that matters more than raw numbers: this is built by one person with an assistant and the internet, and Raspberry Pi is where the answers are written down. Open upstream graphics drivers, a curated list of display panels that work with a single line of configuration, and a supported way for the device to present itself to a computer as a keyboard and mouse.

**The real-time work leaves the computer.** The motor control loop, the encoder, the vibration actuator, the clutch servo and the LED ring go on their own small microcontroller, which also presents the scroll wheel to the computer directly. A heavy animation frame can then never disturb a click, and the scroll is one hop from the encoder to the cable. This separation is a requirement, not an optimisation.

**Audio leaves the computer too.** Its own board: an XMOS controller presenting a proper asynchronous sound card to the computer, feeding an ESS converter. The two microphones are captured by the same chip, so the computer sees one sound card with a speaker and a microphone. The equaliser and the spectrum analysis run there, where the samples already are, and send only their results to the screen.

**No headphone drive.** The 3.5 mm socket is a line output to powered speakers. The device is a front end for the audio equipment the owner already has, not a replacement for it.

**Three boards and a small hub**, therefore, sharing one cable to the computer. That is a compound device in the USB specification's own words — the standard arrangement, not a workaround.

## Design law

- **Colour is ownership.** Green means volume, amber means seek, white means the device itself, red is reserved for mute and recording.
- **The metal is monochrome; colour only ever comes from light** — the screen and the halo. No printed or painted accent anywhere on the object.
- **Value is an arc from the dot at twelve.** The screen draws it; the halo draws the same arc, the same colour, the same clock position at desk level — the bloom overflowing the glass onto the desk. The halo never shows information the screen does not.
- **Sound is subordinate to light.** Notification-grade only. Every sound has a halo equivalent and an off switch.
- **Sound as haptic texture.** The speaker layers a subtle mechanical noise under haptic events, the way a shutter sound completes a photograph. Quiet enough to read as the mechanism, not as a speaker.
- **One bright line.** A wide 45° chamfer between the knurl and the glass, diamond-cut after anodising: one crisp ring of bright raw aluminium against matt black. That single machined line is all the jewellery.

## Aesthetic direction

Moodboard: KEF LS50, watch bezels and knurled hardware, the Totem Alfa machined knob, restomod Saab 900.

- **Knob:** diamond knurl at watch-bezel coarseness — deep enough to catch a fingertip, not aggressive. The only heavily textured surface.
- **Base:** matt black mass, with the halo as a full-width rear light bar wrapped into a ring, just off the desk.
- **Underside:** machined concentric ribs around the speaker — the engineering you find when you pick it up.
- **Finishes:** matt black anodise with the diamond-cut edge, and a silver bead-blast variant. Same machining programme, different bath.

## The screen

The display decision was settled on evidence rather than preference, and two findings are worth carrying forward because they will come up again.

**There is nothing sharper to buy.** Between three and five inches, across every panel maker and module house checked, the round display catalogue is three panels: 3.4 inch at 800×800, 4 inch at 720×720, and 5 inch at 1080×1080. Round panels are cut from rectangular mother glass and inherit whatever resolution the volume application — motorcycle and car instrument clusters — needed. All three are already past what the eye resolves at desk distance, so resolution is not the lever. Picture size, border width, brightness, black level and optical bonding are.

**Round organic-LED panels stop at 1.75 inches.** There is no catalogue part at three inches or above; the round screen in the new MINI was a custom programme between a supplier and BMW. That matters because our design law wants a black object whose screen disappears into it, and a liquid-crystal panel never fully extinguishes. The recovery is optical bonding, which we must not lose, plus a brighter panel run dim, plus never rendering pure black as the dominant field.

## Built to outlast us

No battery, so the commonest cause of premature death is removed. No cloud, so nothing dies when a server is switched off. Integration at the layer the operating system owns, so no vendor's product decision can end it.

**The display is still the time bomb, and the survey made the case stronger.** A bonded round panel is one factory's part number, and the whole catalogue is three panels wide. In ten years this one will not exist. The answer is the one the Danish tap maker VOLA has used since 1968: the visible body never changes while the working part inside it is updated across decades, so a fifty-year-old tap is still serviceable with current parts. **Design the display as a module on a defined mechanical and electrical interface** — fixed outside diameter, fixed mounting pattern, documented connector — so a different panel can be fitted in 2036. Nearly free now, impossible to retrofit later.

The same argument now applies to the computer. A compute module on a documented connector can be replaced with whatever exists later; a processor soldered to the main board cannot. Raspberry Pi commits to producing this one until at least January 2036.

**Split the inventory problem by cost and behaviour.** Stock what is cheap and wears — wheels, cable, silicone band, servo — all storable in a drawer for twenty years. Design interfaces for what is expensive and will be discontinued — the display and the computer — and do not stock those.

**A trade to state rather than discover.** Optical bonding is right, but it makes glass and panel one part, so a crack means a new display module rather than new glass. Keep the bonding and publish the consequence with a price: cracked glass means a replacement display module, fitted by us, at cost. Repairability only reads as a luxury feature when the cost of each repair is published.

**Free lifetime service, extending to second owners.** At sixty units this costs a few hours a year and every owner will be known personally. It returns field-wear data nobody else in this category has, and sixty numbered units will have a watched resale market, which is the most credible quality proof available.

**The exit guarantee.** A published commitment that if the project ends, the firmware source and the configuration page are released publicly. It costs nothing until it is needed, and it is the one thing a technically literate buyer of a connected object actually worries about.

## What the software is

The firmware and its companion application are **TorqueOS**. The device is a display and a controller; the integrations run in a companion application on the computer, Windows first and macOS to follow.

**Scroll is home.** The bezel is a scroll wheel by default, which works in every application ever written with no vendor code, and the screen is a deck of touch modifier hotspots around a Now Playing widget. A finger resting on a hotspot varies the detent from full clicks to a free flywheel. Touching the left zone opens media, where the bezel is volume.

**Contexts surface themselves.** A call starts and the call context takes the screen; music plays and Now Playing takes it back; a coding agent asks permission and the halo glows amber until the knob is pressed; a timer runs and the screen fills. The ring menu is the manual override and holds at most six owner-chosen entries.

**The timer is the signature screen.** Sixty detents, sixty minutes: turn the knob like a dive bezel to twenty-five, a bloom fills to twenty-five, the halo shows the same arc on the desk, and when it lands the speaker gives a kerchunk. That is the screen a watch collector is shown.

Priorities, in order: calls and mute, media and album art, system volume, dictation, the launcher, notifications, and the coding agent's status. Below that: timer, clock, calendar, spectrum display. Parked: market data, where the buyer brings their own licence.

## What the 60 will never do

Decisions, not deferrals. Each removes capability, and each cost is named so nobody reopens the argument cheaply.

**No cloud, ever.** The device never talks to a server we own — verifiable with a packet capture, which is the point. *Costs:* no remote analytics, no silent fixes. Updates are user-initiated over the local page.

**No battery.** A desk object with a cable and a heavy base, eighteen inches from a computer. A battery buys nothing and costs a charge state, thermal limits, transport testing, and decisively an expiry date. *Consequence resolved:* the cable is not captive and is replaceable.

**No vendor alignment.** Integrate at the layer the operating system owns, never the layer a vendor owns. *Costs:* no per-service features. The exception is narrow and named: accepting, declining and ending a call needs per-application work for Teams, Zoom and Meet, because no operating system exposes it — but the promise that the device reacts to every call on the machine is kept at the system layer.

**No phone application.** Setup uses a phone as a browser and nothing more.

**No macros, no scripting, no user-defined actions.** You configure which contexts appear and in what order; you never define what the dial does. Stream Deck's proposition is infinite configurability, which is why it needs an afternoon of setup. Ours is the inverse: it arrives already knowing what to do.

**No speakerphone, and no music from the onboard speaker.** Jabra owns acoustic quality in this footprint and a mediocre one would define the reviews. The same logic governs the converter: this audience runs measurement sweeps and publishes them. Either the audio clears that scrutiny or it is the speakerphone mistake in a different component.

**Deferred, not refused:** an open plugin store.

### Tested and kept

- **Touch** — first tier, and the path to trackpad-class input. A question raised on 4 September and still open: whether the screen should also present itself to the computer as a precision touchpad. It is technically clean, and it argues for ten-point touch on the production panel rather than five.
- **Microphones** — dictation is a first-tier context, not an accident of a development board. Kept, and therefore used.
- **Speaker** — kept as a notification instrument, never a music source.

## Where the project is

| Stage | State |
|---|---|
| Mechanical, v9 | Built around the old 3.4 inch panel and the ESP32-P4 board. Superseded by the architecture change; v10 is briefed |
| Mechanical, v10 | To be specified: the five-inch panel, a computer with its cooling, and a mains inlet as well as the data socket |
| Electronics | Architecture settled. No board designed yet. The carrier board will be laid out by a contractor and assembled by a factory — no hand soldering |
| Software | Not started on the new platform. Godot to prototype, Qt Quick for the product |
| Hardware in hand | Raspberry Pi 5 and the five-inch round HDMI display on order |

## The open questions that matter

1. Does the bare five-inch panel need a start-up command sequence, and will the supplier provide it? It decides whether the production display is a week of work or a specialist job.
2. Touch on the production panel — a bonded sensor on a round cover lens must be specified. Five points or ten, and the trackpad question decides it.
3. Prove on the bench that the compute module runs from its own power supply while appearing to the computer as a keyboard. Everything else depends on it.
4. The metal ring on the top face narrows to about 11 mm. Look at it before accepting it.
5. Grounding the rotating knob so a resting finger survives the ring turning. The proposal is a spring-loaded contact running in the same groove as the wheels.
6. The halo diffuser gap, which sets the final diameter and is still a guess.
