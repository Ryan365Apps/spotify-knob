# Vision & roadmap — the desk dial

**Date:** 2026-09-01
**Companion docs:** `PREMIUM-BOM.md` (prototype hardware and the dial mechanism), `CAD-BRIEF.md` (what the model must change), `COMMERCIAL-FEASIBILITY.md` (gates, pricing, drop model), `design/screens.html` (screen design language).

## One line

A CNC-knurled 110mm dial around a 105mm round display — one wonderfully tactile knob, a screen that shows exactly one thing well, and a companion app on the PC that gives it a context for whatever you're doing. Jabra Speak2 55 footprint. Not a Stream Deck competitor: *the one perfect dial* that sits beside anything.

## The object

**A heavy, expensive watch sitting on your desk that invites you to move it.** The dial must reward idle handling, not only deliberate use — picked up, spun, fidgeted with. That is the emotional target, and the mechanism section of `PREMIUM-BOM.md` is where it is either delivered or lost.

Everything else on this page is in service of that. If a decision improves the feel of the ring, it wins; if it competes for budget with the feel of the ring, it loses.

## Form

- **135 mm outside diameter, 40 mm tall.** The ergonomic model is a mouse, not a thermostat: heel of the hand on the desk, two or three fingers reaching the touchscreen, open palm across the bezel to spin it. At 60 mm the wrist lifts off the desk and every interaction becomes a reach; at 40 mm the hand stays planted. The current model is ~60 mm — see `CAD-BRIEF.md` §1 for where the 20 mm comes from. Treat 45 mm as the failure threshold.
- Knurled aluminium outer knob, free-rotating. **Detent mechanism is an open decision** — see `PREMIUM-BOM.md`; the current vibration-only plan has an untested assumption (the vibration source sits on the opposite side of the bearing from your fingers) and a contradiction (a geared position sensor, when gearing was rejected elsewhere for adding slop)
- ~105mm round display (800×800), fixed, optically bonded glass
- Chunky weighted base (~250g+), captive braided USB-C
- **Halo ring**: SK6812 RGBW ring at the base's lower edge, under a printed opal diffuser, firing down/outward onto the desk (Jabra-style corona). On the static base, never the rotating knob.
- Down-firing 8Ω 2W speaker into the under-base gap; board's dual mics + echo cancellation retained
- **Ambient light sensor** (VEML7700/BH1750 class, ~£1–2) behind a small window or light pipe on the base — adaptive brightness for screen *and* halo, so evenings never need a manual override. Halo must dim on the same curve as the screen or it dominates a dark room.
- **Audio front-end (run 2 flagship): quality DAC + headphone/line out, ~£10–15 BOM** (ESS Sabre-class chip + clean amp stage + power filtering). The device enumerates as a USB audio interface: PC audio flows through the dial out to your KEF desk speakers or Bose/quality headphones — the knob controls volume *in the DAC itself*, true zero-lag hardware volume. **Positioning: it never competes with the user's expensive audio gear — it becomes its front-end.** The pitch upgrades from "a nice knob" to "your DAC is the knob"; desk nerds are audio nerds. Caveat: this crowd measures — clean 5V-to-analog power design is the bounded-but-real engineering task; done well it's the review headline. Spike early with a DAC breakout; ships on the run-2 custom PCB.
- Run 2 glass: 2.5D polished edge, oleophobic + AR (see BOM doc)

## Design law (from the screen mockups — the halo and sounds inherit it)

- **Colour is ownership:** green = volume, amber = seek, white = the device itself. Red reserved for mute/recording.
- **Value is an arc from the dot at twelve.** The screen draws it as the phyllotaxis bloom; the halo draws the *same arc, same colour, same clock position* at desk level — the bloom overflowing the glass onto the desk. The halo never shows information the screen doesn't; up close it's reinforcement in peripheral vision, across the room it collapses to status (steady red = muted, breathing green = in a call, off = idle).
- **Sound is subordinate to light.** Notification-grade only (chimes, alerts, detent-confirms) — never music, never uninvited. Every sound has a halo equivalent and an off switch.
- **Sound as haptic texture:** the speaker layers a subtle mechanical "kerchunk" under haptic events — end-stops, mode changes, a heavy detent landing — the way a camera shutter sound completes the gesture. Software-driven, so it's tuned per event and per context, and it makes the LRA feel stronger than it is. Quiet enough that it reads as the mechanism, not a speaker.
- Firmware brightness cap ~20% on the halo (full-white RGBW ring exceeds USB power budget; ambient should be dim anyway).

## Aesthetic direction (moodboard: KEF LS50, watch bezels/knurled hardware, Totem Alfa machined knob, restomod Saab 900)

**Law: the metal is monochrome; colour only ever comes from light** (screen bloom + halo — the colour-ownership rules above). No printed or painted accents anywhere on the object.

- **Knob:** diamond knurl, watch-bezel coarseness — deep enough to catch a fingertip, not aggressive. The *only* heavily textured surface (knurl OR fluting, never both; fluting also needs 4th-axis machining — dearer).
- **Bevel:** wide 45° chamfer between knurl and glass, **diamond-cut after anodising** — one crisp ring of bright raw aluminium against matt black (diamond-cut alloy wheel / restomod trick). This single machined line is all the jewellery.
- **Base:** matt black mass, Saab-restomod attitude; the halo is the full-width rear light bar wrapped into a ring, just off the desk.
- **Underside / speaker aperture:** KEF-style machined concentric ribs radiating around the down-firing speaker — the "engineering you find when you pick it up" moment. Totem-style castellated radial cuts as an option for the top trim ring.
- **Finish SKUs:** matt black anodise + diamond-cut edge ("turbo"), and silver bead-blast. Same machining program, different anodise bath — cheap variant split for the drop (e.g. 40 black / 10 silver).

## Built to outlast us

Four decisions already point this way and were made for other reasons: no battery removes the commonest cause of premature death in electronics; no cloud means nothing dies when a server is switched off; Gate 7 forbids a brick date; and integrating at the operating-system layer means no vendor's product decision can end it.

What is missing is a parts and service strategy, which is what this actually runs on. Meze publishes a catalogue where every pad, cable and driver module is a purchasable spare. Chris Reeve refurbishes free, forever. Vitsœ has kept shelving parts compatible since 1960. The question to answer is: **which part can an owner replace in year seven?**

**The display is the time bomb.** A bonded round panel is a product from one factory with one part number, and in ten years it will not exist — not hard to find, gone. The fix is not stockpiling. It is the approach the Danish tap maker VOLA has used since 1968: the visible body of their Arne Jacobsen mixer tap has never changed, while the valve cartridge inside it has been updated across the decades — so a fifty-year-old tap can still be serviced with current parts, and the same body is still sold today. **A shell that never changes, around a working part that can be replaced with whatever exists later.** **Design the display as a module on a defined mechanical and electrical interface** — fixed outside diameter, fixed mounting pattern, documented connector — so a different panel can be fitted in 2036. Nearly free now, impossible to retrofit later.

**Split the inventory problem by cost and behaviour:**

- **Stock what is cheap and wears** — bearing, cable, magnets, the detent carrier actuator. All under £20, all storable in a drawer for twenty years.
- **Design interfaces for what is expensive and will be discontinued** — the display and the main board. Do not stock them; make them swappable for whatever exists later.

That is the difference between a promise that can be kept and one that gets quietly broken in year eight.

**A trade to state rather than discover: bonded glass versus repairability.** Optical bonding is right — no air gap, deeper blacks, better touch — but it makes glass and panel one part, so a crack means a new display module rather than new glass. Keep the bonding, and publish the consequence with a price: *cracked glass means a replacement display module, fitted by us, at cost.* Repairability only reads as a luxury feature if the cost of each repair is published.

**Free lifetime service, and it extends to second owners.** At 60 units this costs a few hours a year and you will personally know every owner. Bearing re-lubricated, detent re-tensioned, re-anodised if it needs it. It also returns real field-wear data that nobody else in this category has. Serving second owners is unusual and deliberate: sixty numbered units will have a watched resale market, and resale value is the most credible quality proof available.

**The exit guarantee.** Gate 7 covers what happens if a service dies. This covers what happens if *we* stop: a published commitment that if the project ends, the firmware source and the configuration page are released publicly. It costs nothing until it is needed, and it is the one thing a technically literate buyer of a connected object actually worries about.

## Context roadmap (each = screen layout + dial mapping + data source in the companion app)

**Tier 1 — the five that must be flawless (drop ships these):**
1. **Calls / mute** — the commercial wedge. Rotate = call volume, press = mute, halo = unmissable status. Teams/Zoom APIs.
2. **Media + album art** — the founding use case. SMTC on Windows: art from whatever is playing; volume, seek, transport. (Spotify becomes one source among many.)
3. **System volume** — always-works fallback, HID.
4. **Dictation / Wisprflow** — push-to-talk on the dial, recording state on halo (red), HID hotkeys.
5. **App launcher / selector** — the Galaxy-Watch-bezel radial from screen 05; five slots at 72°, one green dot.

**Tier 2 — cheap once the context engine exists:** clock/timer/pomodoro, weather, calendar/next-meeting (Granola), stocks ticker, brightness and settings radials (screens 06–08).

**Tier 3 — novel, differentiating:** **Claude Code status** (waiting/working glance state, press to approve a permission prompt, chime on completion), OBS/streaming, MX-Creative-Console-style per-app creative maps (brush size, timeline scrub), MIDI/HID device mode so pro apps map it natively with zero plugin work.

## What Radial will never do

These are **decisions, not deferrals.** Each one removes capability the product could have had, each one costs something real, and the cost is named so nobody re-opens the argument cheaply. Anything that belongs on this list and isn't yet is a gap; anything here that acquires an exception stops being a principle.

**No cloud. Ever.** The device never talks to a server we own. Verifiable by anyone with a packet capture, which is the point — for a connected object this is the most checkable claim available, and almost nobody in the premium hardware world can make it.
*Costs:* no remote analytics, no silent fixes, no A/B testing. Firmware updates are user-initiated over the local page. When an upstream API changes, the user has to act.

**No battery.** This is a desk object with a captive cable and a 250 g base, sited eighteen inches from a PC. A battery would buy nothing and cost a charge state to manage, thermal limits, UN38.3 testing and air-freight restrictions, a worse power budget on a halo already capped at 20% — and, decisively, **an expiry date.** Every other decision here argues for permanence; a swollen cell in year five contradicts all of them.
*Costs:* it never leaves the desk. **Consequence to resolve:** a captive cable that cannot be replaced is the one detail that would undercut this claim — either make it field-replaceable behind a service screw, or replace it free for life and say so.

**No vendor alignment. Integrate at the layer the OS owns, never the layer a vendor owns.** SMTC, not the Spotify API. HID, not a vendor plugin. Note what this already cost: the founding use case *was* Spotify, and moving to SMTC deliberately swapped a richer integration for a poorer, more universal one.
*Costs:* no playlists, no library browsing, no device transfer, no per-service features. Expect to be asked for a Spotify-only feature within a week of shipping; this line is the answer.

**No phone app. The phone is a browser and nothing more.** Setup uses a phone — QR, captive portal, config page — but that is a web page served by the device, not an application.
*Costs:* no push notifications, no remote control from a phone, no companion app features. In exchange: no app store, no two mobile platforms, and no annual OS churn that can brick the product.

**No macros, no scripting, no user-defined actions.** You configure *which* apps appear and in what order; you never define *what the dial does*. Stream Deck's proposition is infinite configurability, which is why it needs an afternoon of setup and why no two are alike. Radial's inverse proposition is that it arrives already knowing what to do.
*Costs:* power users will ask, and the answer is no. Crossing this line means competing with Stream Deck on Stream Deck's terms, against a plugin marketplace we do not have.

**No speakerphone, and no music from the onboard speaker.** Jabra owns acoustic quality in this footprint and a mediocre one would define the reviews.
*Note the same logic applied consistently:* it bears on the run-2 DAC too. Audio measurement is a culture — this crowd runs sweeps and posts them. Either the DAC clears that scrutiny or it is the speakerphone mistake in a different component.

**Deferred, not refused:** an open plugin store. Stated honestly as a deferral because it may one day be right; it is not a principle.

### Tested and kept

Three additions were argued for removal and survived. Recorded so they are not re-litigated:

- **Touch** — complements the bevel gesture set, and is the path to trackpad-class input later. Kept.
- **Microphones** — dictation is a first-tier context, not an accident of the dev board. Kept, and therefore *used*, not merely present.
- **Speaker** — ringer and notification UX tied to on-screen animation, customisable alert sounds. Kept as a notification instrument, still never a music source.



## Hardware evolution

| Stage | What | Key deltas |
|---|---|---|
| v0 prototype (~£120) | Waveshare 3.4C, 3D printed, passive bearing + LRA ticks | Prove art pipeline (port 5 first), feel, contexts |
| Bench spike (~£25) | **Magnetic detent rig first** — magnets on a printed rotor against steel pole pieces, no electronics. Then a vibration-coupling test across the bearing | Answers whether a 110mm ring needs real mechanical force or tolerates faked clicks. Cheapest, most informative, and blocks the CNC drawings until answered |
| Bench spike 2 | Switchable detent: pole-piece ring moved 1–2mm by one small actuator | Two mechanical characters in one object — crisp clicks for menus, free inertial spin for volume, with an audible change-over. Most of what force feedback promised, without a custom motor |
| The drop (50 × £450) | CNC knurled knob, halo ring, speaker, captive cable, white-glove onboarding | Landed ~£130–165 + ring/speaker ~£8 |
| Run 2 | Custom PCB (P4 module, proper USB-C device port, drop unused dev-board parts), raw panel + custom 2.5D glass, **DAC + headphone/line out (+£10–15)**, ambient light sensor | Claws back £25–35/unit; NANO board is the reference layout; DAC power design is the one real engineering task |

## Open spikes, in order

1. Port-5 test: art + HID over the board's full-speed USB-C alone (see BOM doc — likely kills the adapter).
2. Windows SMTC → art on the round screen (Gate 3, now on the real panel).
3. BLDC bench feel test.
4. Halo prototype: one SK6812 ring + diffuser print, wired to the 40-pin header — same week as first case print.
5. DAC breakout (e.g. PCM5102/ES9023 board, ~£8) on the P4's I2S → line out to desk speakers; dial writes DAC volume directly. Proves the "your DAC is the knob" feel long before the custom PCB.
6. Kerchunk tuning: layer speaker transients under LRA events; A/B with haptics-only — cheap, pure software.
