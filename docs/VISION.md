# Vision & roadmap — the desk dial

**Date:** 2026-09-01
**Companion docs:** `PREMIUM-BOM.md` (prototype hardware), `COMMERCIAL-FEASIBILITY.md` (gates, pricing, drop model), `design/screens.html` (screen design language).

## One line

A CNC-knurled 110mm dial around a 105mm round display — one wonderfully tactile knob, a screen that shows exactly one thing well, and a companion app on the PC that gives it a context for whatever you're doing. Jabra Speak2 55 footprint. Not a Stream Deck competitor: *the one perfect dial* that sits beside anything.

## Form

- ~110mm knurled aluminium outer knob, free-rotating, haptic
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

## Context roadmap (each = screen layout + dial mapping + data source in the companion app)

**Tier 1 — the five that must be flawless (drop ships these):**
1. **Calls / mute** — the commercial wedge. Rotate = call volume, press = mute, halo = unmissable status. Teams/Zoom APIs.
2. **Media + album art** — the founding use case. SMTC on Windows: art from whatever is playing; volume, seek, transport. (Spotify becomes one source among many.)
3. **System volume** — always-works fallback, HID.
4. **Dictation / Wisprflow** — push-to-talk on the dial, recording state on halo (red), HID hotkeys.
5. **App launcher / selector** — the Galaxy-Watch-bezel radial from screen 05; five slots at 72°, one green dot.

**Tier 2 — cheap once the context engine exists:** clock/timer/pomodoro, weather, calendar/next-meeting (Granola), stocks ticker, brightness and settings radials (screens 06–08).

**Tier 3 — novel, differentiating:** **Claude Code status** (waiting/working glance state, press to approve a permission prompt, chime on completion), OBS/streaming, MX-Creative-Console-style per-app creative maps (brush size, timeline scrub), MIDI/HID device mode so pro apps map it natively with zero plugin work.

**Anti-goals:** speakerphone (Jabra owns acoustic quality; a mediocre one defines the reviews), music from the onboard speaker, an open plugin store at launch, any cloud dependency (Gate 7: no brick date).

## Hardware evolution

| Stage | What | Key deltas |
|---|---|---|
| v0 prototype (~£120) | Waveshare 3.4C, 3D printed, passive bearing + LRA ticks | Prove art pipeline (port 5 first), feel, contexts |
| Bench spike (+~£20) | Hollow-shaft gimbal BLDC + driver + encoder, no display | Real force-feedback detents/endstops — "witchcraft" tier. If it feels right, drop v1 adopts motor layout (display stem through hollow shaft, FPC through bore, RP2040/S3 co-processor runs FOC) |
| The drop (50 × £450) | CNC knurled knob, halo ring, speaker, captive cable, white-glove onboarding | Landed ~£130–165 + ring/speaker ~£8 |
| Run 2 | Custom PCB (P4 module, proper USB-C device port, drop unused dev-board parts), raw panel + custom 2.5D glass, **DAC + headphone/line out (+£10–15)**, ambient light sensor | Claws back £25–35/unit; NANO board is the reference layout; DAC power design is the one real engineering task |

## Open spikes, in order

1. Port-5 test: art + HID over the board's full-speed USB-C alone (see BOM doc — likely kills the adapter).
2. Windows SMTC → art on the round screen (Gate 3, now on the real panel).
3. BLDC bench feel test.
4. Halo prototype: one SK6812 ring + diffuser print, wired to the 40-pin header — same week as first case print.
5. DAC breakout (e.g. PCM5102/ES9023 board, ~£8) on the P4's I2S → line out to desk speakers; dial writes DAC volume directly. Proves the "your DAC is the knob" feel long before the custom PCB.
6. Kerchunk tuning: layer speaker transients under LRA events; A/B with haptics-only — cheap, pure software.
