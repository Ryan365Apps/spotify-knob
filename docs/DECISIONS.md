# Decisions — premium version

**Date:** 2026-09-01
**Purpose:** the single list of what has been decided, and what is still open. Detail and reasoning live in `VISION.md`, `PREMIUM-BOM.md` and `CAD-BRIEF.md`; this page is the index so nothing gets silently re-opened.

**Status key:** **Decided** — settled, do not re-litigate without new evidence. **Decided in principle** — direction agreed, one test could still change it. **Open** — genuinely undecided.

---

## Positioning

| # | Decision | Status |
|---|---|---|
| 1 | The device is called **Radial**. Hostname `radial.local`. | Decided |
| 2 | Market is people who buy KEF LSX-class desk audio — the same object logic applied to a peripheral. Limited series. | Decided |
| 3 | **The object is a heavy, expensive watch on the desk that invites you to move it.** It must reward idle handling, not only deliberate use. | Decided |
| 4 | **Anything that improves the feel of the ring wins; anything competing with it for budget loses.** | Decided |
| 5 | Not a Stream Deck competitor. The pitch is one perfect dial, not a configurable surface. | Decided |

## What Radial will never do

Each of these removes capability and costs something real. Full costs are named in `VISION.md`.

| # | Decision | Status |
|---|---|---|
| 6 | **No cloud, ever.** The device never talks to a server we own — verifiable with a packet capture. | Decided |
| 7 | **No battery.** A cell gives the object an expiry date, and everything else here argues for permanence. | Decided |
| 8 | **No vendor alignment.** Integrate at the layer the operating system owns, never the layer a vendor owns — Windows media transport, not the Spotify interface. | Decided |
| 9 | **No phone app.** The phone is a browser during setup and nothing more. | Decided |
| 10 | **No macros, no scripting, no user-defined actions.** You configure which apps appear; never what the dial does. | Decided |
| 11 | No speakerphone, and no music from the onboard speaker. | Decided |
| 12 | An open plugin store is **deferred, not refused** — it may one day be right, so it is not a principle. | Open |

## Tested and kept

Argued for removal, survived, recorded so they are not re-argued.

| # | Decision | Status |
|---|---|---|
| 13 | **Touch stays.** It complements the bezel gesture set and is the route to trackpad-class input later. | Decided |
| 14 | **Microphones stay** — dictation is a first-tier use case, so they are used deliberately rather than inherited from the dev board. | Decided |
| 15 | **Speaker stays** as a notification instrument — ringer, alerts, customisable sounds, tied to on-screen animation. Never a music source. | Decided |
| 16 | The audio output stage must clear measurement scrutiny, or it is the speakerphone mistake in a different component. Same rule, applied consistently. | Decided |

## The dial mechanism

The centre of the product. Reasoning in `PREMIUM-BOM.md`, geometry in `CAD-BRIEF.md` §2.

| # | Decision | Status |
|---|---|---|
| 17 | **Three layers.** Magnets own the fixed physical scale and overall weight; the motor owns everything dynamic; the vibration actuator owns event confirmations. | Decided |
| 18 | **The magnets' real job is that the object is never inert.** Every motorised dial is dead when unplugged; this one still clicks like a watch bezel with no power. | Decided |
| 19 | **Dynamic detent strength comes from the motor, not from moving the magnets** — resistance ramping toward a limit must arrive within about a tenth of a second, which a self-locking screw cannot do. | Decided |
| 20 | The magnet ring still moves during use, but at **gesture cadence** — mode changes, a few times an hour — not per detent. | Decided |
| 21 | **60 steel poles on the rotating bezel, 6 magnets on the stationary carrier.** | Decided |
| 22 | **8 magnets does not work** with 60 poles — 45° is seven and a half pole spacings, so the detent half-cancels. Valid counts: 3, 4, 5, 6, 10, 12. | Decided |
| 23 | 60 divides usefully: every 10th for the app selector, every 5th for menus, every one for volume, motor half-steps for fine scrubbing (120, a dive-bezel count). | Decided |
| 24 | **A ring of magnets, not one** — a single magnet side-loads the bearing and produces a travelling tight spot. | Decided |
| 25 | Steel on the rotor, magnets on the stator — everything needing power or movement stays on the part that does not spin. | Decided |
| 26 | Carrier moves **vertically**, one flat ring, about 2 mm of travel. | Decided |
| 27 | The lifting mechanism **must hold position with no power** — fine screw turned by a small motor, or a shallow self-locking cam. Not a solenoid, not shape-memory wire. | Decided |
| 28 | Consequently **detent weight is continuously adjustable** and survives a power cut, because it is a screw position rather than a stored value. | Decided |
| 29 | Target detent strength **60–150 mNm peak, adjustable**. Design the magnets for the top of the range. | Decided in principle |
| 30 | **Motor and magnets must be designed together** — the motor's own natural lumpiness either near-zero, or locked to the 60 poles in count and phase, or the two beat against each other. | Decided |
| 31 | The motor is a **custom large-diameter ring motor**. No catalogue part exists at this bore; large diameter makes it hard to buy and easy to make strong. | Decided in principle |
| 32 | **Add hidden mass** — a brass or steel insert concealed inside the aluminium bezel, for rim inertia. | Decided |

## Sensing

| # | Decision | Status |
|---|---|---|
| 33 | **Delete the gear train** (`drive_wheel`, `wheel_mount`) and the on-axis sensor. Gear slop makes the detent fire at a different angle depending on direction — the exact reason gearing was rejected for the motor. | Decided |
| 34 | **Replace with ring sensing** — a ring of alternating magnetic poles read from the side. Optical or capacitive rings solve it equally. | Decided |
| 35 | Keep the sensing ring **magnetically separate** from the detent magnets — different radius, height, or a steel shield between them. | Decided |

## Geometry and packaging

| # | Decision | Status |
|---|---|---|
| 36 | **135 mm outside diameter.** | Decided |
| 37 | **40 mm tall.** 45 mm is the failure threshold. Currently ~60 mm. | Decided |
| 38 | Ergonomic model is **a mouse, not a thermostat**: heel of the hand on the desk, two or three fingers to the screen, open palm across the bezel. | Decided |
| 39 | **Bearing and display must be concentric, not stacked** — the display passes through the bearing bore. Recovers 13 mm. | Decided |
| 40 | Deleting the gear frees ~16 mm in exactly the ring-shaped volume the magnet system needs. The two changes pay for each other. | Decided |
| 41 | Bearing approach: a larger thin-section ring, **or** three to four small ball bearings running in a V-groove machined into the bezel. Print both and compare. | Open |
| 42 | **250 g minimum, concentrated low.** Steel base plate at the bottom. | Decided |
| 43 | Halo fires **down and outward from the base skirt**, never from the rotating part. | Decided |
| 44 | **The captive cable must be replaceable**, or replaced free for life. An unreplaceable cable contradicts the no-expiry-date claim. | Decided |
| 45 | Wide 45° chamfer between knurl and glass, **diamond-cut after anodising** — the only jewellery on the object, and it survives the height reduction. | Decided |
| 46 | Bezel is 3D printed for prototyping and CNC aluminium for production, with nothing else in the assembly changing. | Decided |

## Light and sound

| # | Decision | Status |
|---|---|---|
| 47 | **The halo is not mechanically coupled to the magnet carrier.** Choreograph it in software instead — the light can lead the mechanical clunk by ~80 ms so the object reads as anticipating rather than reacting. | Decided |
| 48 | Colour is ownership: green = volume, amber = seek, white = the device, red reserved for mute and recording. Metal is monochrome; colour only ever comes from light. | Decided |
| 49 | If the detent becomes real, the speaker's mechanical "kerchunk" **stops being load-bearing** for the feel. The speaker keeps its own job in notifications. | Decided |

## Screen and interaction

| # | Decision | Status |
|---|---|---|
| 50 | Menus are **rings, not vertical lists** — selector, settings and launcher all use the same rim carousel with a centre hero. | Decided |
| 51 | Selection is **one green dot at twelve plus a glow on the glyph beneath it**. The earlier arc and twin ticks are gone — three marks for one selection was two too many. | Decided |
| 52 | Rim glyphs **fade with angular distance** from the dot, so the foot of the circle recedes. | Decided |
| 53 | **A visible back chevron on every ring**, with the lower band of the circle as its hit area. Long-press still works but is never the only way out. | Decided |
| 54 | Glyphs in the lower band are **not tappable** — the back zone owns that area, and the dimming is the honest signal. | Decided |
| 55 | **Launcher capped at eight entries.** The cap is the feature: a ninth makes every position one you read rather than one you know. Groups are designed and deliberately unbuilt. | Decided |
| 56 | Launcher chords come from **a dropdown, never a text field** — no string on the config page can become a keystroke. | Decided |
| 57 | Setup uses a **scannable code** on screen, and the device narrates every step of joining over a live connection to both the phone and its own screen. | Decided |

## Open — needs the bench rig before committing

Build these before any production drawing is committed.

| # | Question |
|---|---|
| A | **Detent strength.** What is light enough for the motor to overpower cleanly, and still satisfying with the power off? |
| B | **What does magnetic pull cost the free spin?** It removes bearing slack (good) and adds friction (bad). Measure, do not argue. |
| C | **Does vibration reach the fingers at all?** The actuator is on the base; the bezel spins on a bearing whose job is to isolate the two. This validates or kills the current haptic plan in an afternoon. |
| D | **Rollers or a continuous race** at 135 mm. |
| E | **Runout at the rim.** 0.05 mm is felt on a ring this size. It is the difference between expensive and cheap. |
| F | Does the display assembly clear a practical bearing bore, or does that force the roller approach? |

## Commercial and service — added 2026-09-01

| # | Decision | Status |
|---|---|---|
| 58 | **The run is 60 units** — sixty detent positions, sixty units. Scarcity from a fact about the object rather than a round number. Never exceeded. | Decided |
| 59 | **20% deposit at reservation, balance on dispatch.** Across the run that is ~£5,400, which is approximately the compliance budget — deposit money pays for the cost that kills projects at this stage. | Decided |
| 60 | **No deposits until one complete working unit exists.** Not a rig, not a printed bezel. This is the line Radford and Charge Cars crossed. | Decided |
| 61 | **Lead time published on the buy button**, as a month. | Decided |
| 62 | **Price rises through the run**, ladder published up front — early buyers carry real risk and should pay less for it. | Decided |
| 63 | Gates 2, 5 and 6 re-derived for 60 units. Gate 5 **inverts**: you avoid fixed costs rather than amortise them. Gate 6 becomes **£33–100 per unit** and is now a pricing input, so the test-house quote is urgent. | Decided |
| 64 | Audience threshold restated: **200–300 genuine signups**, not the 500 sized for a 1,000-unit campaign. | Decided |
| 65 | **Display designed as a replaceable module** on a defined mechanical and electrical interface, so a different panel can be fitted in a decade. | Decided |
| 66 | **Stock what is cheap and wears; design interfaces for what is expensive and will vanish.** | Decided |
| 67 | Optical bonding kept, with the consequence published: cracked glass means a replacement display module at cost. | Decided |
| 68 | **Free lifetime service, extended to second owners.** | Decided |
| 69 | **Exit guarantee:** if the project ends, firmware source and the config page are released publicly. | Decided |
| 70 | **The mode-change sound is a marketing asset as well as a feature** — design it to be recorded, because detent feel cannot be photographed. | Decided |
| 71 | Thirty-day try-and-return; returned units become the certified pre-owned channel. | Decided in principle |
| 72 | **Publish everything** — price, lead time, compatibility, repair costs, anti-goals, what happens if we stop. | Decided |
