# the 60 — v15 open questions

**Open for v15: five bench-decided items** (27–31 below); everything else is settled. v11 carries v10's settled list with the rulings of 6 September; v15 adds Ryan's four rulings of 6 September evening (the blower required; the structure printed inverted on its flat seat; dowel pins in through-holes; a separate, height-selectable encoder shim — and the bleed foot flat, its mount following the same logic) and the v15 brief (`DESIGN-CHANGES.md` items 1–6) as built. Ryan approved every v10 default on 5 September 2026 and added one correction: glue is allowed for securing the display. Three v10 defaults could not be built as written and were changed during the build (marked *built differently* below and explained in `V10.md`). The settled table:

| # | Question | Settled |
|---|---|---|
| 1 | Diameter | **Ø175.4 outside, bore Ø166.4** — ruled 6 Sep: a flat rim of at least 20 mm on the knob's top, the knob keeping v10's shape (4.5 wall), so the bore and everything inside scale out to the rim; the chin (r 72.05) no longer sets anything |
| 2 | Top ring | superseded 6 Sep: **20 mm flat** between the chamfers, 24.2 mm picture edge to knob edge (`v11_top_ring.png`) |
| 3 | Display route | **HDMI adapter** (DM-ADTTR-014); Linux panel driver deferred to the production carrier |
| 4 | Plate thickness | **8 mm** at the rim; 6 Sep: the plate is the heatsink — an aluminium core (v15: **2 web, 5 duct, 1 closing plate**, piers under every top screw) with a **stainless rim ring** (v15), ribs on top, the converter on the plate; exhaust at the rear through the ring's 18–60 openings and the undercut (`THERMAL-PLAN.md`) |
| 5 | Barrel plug under the halo | **pad pocket**; the jack on a vertical board, axis z 3.5 |
| 6 | Pi 5 V on the header vs the PC's USB-C | **VBUS (the cable's 5 V wire) cut in the internal cable**; `usb_max_current_enable=1` |
| 8 | Servo | **on the plate** (v12, Ryan's layout): lying in a floorless frame inboard of the carriage, pushing a 14.5 mm tab; the Pi moved 10 toward 270° and the adapter's overhang clears the frame by 0.28 |
| 9 | Motion board link | **UART on the header**, one 2 × 5 housing with the 5 V feed |
| 10 | Vent | *built differently*: 16 × Ø4 passive in v10; v15: **the blower is fitted and required** (Ryan, 6 Sep) — Delta BFB0305HA-C on the plate over the +y plenum, through the ring's openings and its underside groove; the perimeter slits are the speaker's port only |
| 11 | Cooler | **heatsink on, fan off**; v12: the adapter's underside is 1.2 above the fins — bench item 1 measures it; 15 mm standoffs (the seat allows 2.3 more) or option B (Pi inverted on a plate boss) are the fallbacks |
| 12 | Halo LEDs | superseded (Ryan, 5 Sep evening): a bought 5 mm addressable **strip stuck to the wall**, ~46 LEDs, not discrete LEDs on the plate |
| 13 | Knurl | **78 starts** at Ø175.4 (the v9 7.1 mm pitch kept), 33° helix, **three** whole rows on the 2.4 shorter skirt (v11: four) |
| 14 | Panel orientation | chin at 180°, flex at 0° |
| 15 | Bare panel availability | Ryan to confirm with DisplayModule; dummy disc otherwise (spec 4.4) |
| 16 | Cover lens | Ø140 × 2.5, touch tail at the flex edge — with the supplier |
| 17 | Adapter to panel flex | the adapter is a **kit** (datasheet, 6 Sep): driver board + 150 mm flat cable + a display **connect board** that takes the panel's flex — Ryan to confirm the 45-way mates with its CN2 and to **measure the connect board** (modelled 30 × 46 from its photograph, corner holes assumed; the bracket's bosses follow) |
| 18 | Board envelopes | audio 25 × 40 × **3.6** and motion 30 × 30 × **3.6** (1.6 board + 2.0 Pico-Lock connectors; v14) plus a 4.0 moulded USB plug each; converter 38 × 25 × **8**; touch 30 × 20 × 3 stacked on the adapter |
| 19 | Adapter flipped? | **not yet.** v13: the encoder faces up at a code ring under the crown (Ryan's idea, better than the turret), the code band is off the bore and the seat is now set by the adapter's HDMI socket (26.0; the wheels would allow 24.2). Flipping the adapter would make the touch board the ceiling and bring the seat to 24.8 — 1.2 mm — for a downward-facing cable entry. Ryan's call |
| 23 | Rim edge treatment | **closed** (v15, design-changes items 3 and 5): the venting is the decoration — 108 obround openings 1.8 × 4.5 on 3°, mirrored, three reeds above, 0.3 polished chamfers, bare brushed stainless |
| 24 | Rim ring finish | **closed** (v15): stainless, bare — electropolished after machining, brushed axially; no masking, the star washer cuts through |
| 25 | Bleed leaf | form built as a leaf with its foot flat on the seat flange at 200° (v15: the insert in a boss under the flange), bearing on the crown at r 71.5 (ASSUMED 4 × 0.2 phosphor bronze); bench: its drag must not be felt; the encoder's shims serve under its foot if more preload is wanted |
| 26 | Pogo pins and sensor lead | the LRA's pogo board 7 × 8 (ASSUMED) and pins (Ø1.5, 2.2 compressed, ASSUMED): confirm against the flex tail's real pads; the rotor sensor lead: specify the flex-rated cable (10⁵ cycles at 2.4 mm) |
| 22 | Code ring under the crown | **built** (v13): AEDR-8300 face up on the seat flange at 310°, r 76, 2.0 gap to a 0.15 recess in the crown's underside at r 72.5–79.5. Prototype: a stuck film ring; machined knob: laser-ablated stripes in the anodise (no strip). Bench: stray daylight through the rim gap; gap variation with the knob pushed and pulled on its wheels |
| 20 | The Pi's USB-C lead | an **up-angled** plug (ASSUMED head 12 × 12.5 × 6.5, lead straight up): a straight plug reaches r 75 through the ring at the Pi's new place; a right-angled one collides with the HDMI plug either way. Measure the lead |
| 21 | Bell band | **closed** (v13): back to v11's 9.0–17.8 (2.9 of bore contact) — the code band no longer sits above it |
| — | Glue | **allowed for the display** (Ryan, 5 Sep): the panel bonds to the seat on 0.5 mm foam tape; the screwed carrier ring is dropped |
| 27 | The blower running | **bench**: flow / pressure at the trench, noise at 1 m with the object closed at full speed and at the Pi's PWM, skin temperature at 13 W; the −y arc's reverse flow vs re-ingestion of the 18–60 exhaust (40 mm apart across the port face). The model's estimate: ~0.5 L/s at ~25 Pa, ~1.0 W/K, 38 °C at 25 °C |
| 28 | The Pi 5's fan header | **bench**: its position on the board (the model ASSUMES beside the GPIO header's end at the USB side, (10, 14)) and its current rating against the blower's 0.13 A (0.20 max) |
| 29 | Encoder shim | **bench**: which of 0.7 / 0.8 / 0.9 / 1.0 / 1.1 gives the 2.0 optical gap on the real parts; the radial slot's use for centring over the code ring |
| 30 | Dowel pins | **bench**: the Ø2 H7 ream in printed PETG and the press fit of a 2 m6 dowel; the glass locating on three Ø2 pins (0.15 off its edge) |
| 31 | The stainless ring's machining | **supplier**: 120 obround plunges 1.8 wide through a 3.7 wall on a rotary (or laser), the four-arc underside groove, electropolish then brush; whether 0.3 chamfers survive the brushing; cost against the v14 mild-steel ring |

The questions as they were put, for the record:

---|---|---|---|---|
| 1 | 1 | Diameter: Ø154 with a plain bore, or Ø150 with an undercut | **Ø154** → **Ø175.4** (6 Sep, 20 mm rim) | |
| 2 | 2 | Approve the top ring at 13.5 mm (drawing) | approve → superseded 6 Sep: rim ≥ 20 mm | |
| 3 | 15 | Can the bare DM-TFTR50-413 be bought in ones? | if not: dummy disc | |
| 4 | 3 | Display route for v10: HDMI adapter, or Pi 5 DSI direct | **adapter** | |
| 5 | 11 | Cooler: keep it (A′) or delete it and conduct into the plate (B) | **A′** | |
| 6 | 4 | Plate thickness: 8, 5 or 10 mm | **8** | |
| 7 | 5 | Barrel plug under the halo: pad pocket, halo notch, or 10 mm plate | **pad pocket** | |
| 8 | 10 | Vent: passive with a software cap, or through-flow with the fan | **through-flow** | |
| 9 | 8 | Servo: tangential with a rocker, or direct radial push as v9 | **tangential** | |
| 10 | 6 | Pi 5 V on the header while the PC's USB-C is plugged in | **VBUS (the cable's 5 V wire) cut in the internal cable** | |
| 11 | 9 | Motion board to Pi: UART on the header, or USB | **UART** | |
| 12 | 16 | Cover lens: Ø140, 2.5 thick, tail at the flex edge | as stated | |
| 13 | 17 | Does the adapter mate with the panel's 45-way 0.3 mm flex? | ask DisplayModule | |
| 14 | 18 | Board envelopes: audio 25 × 40 × 6, motion 50 × 40 × 8, touch controller 20 × 30 × 4, converter 25 × 38 × 10 | as stated | |
| 15 | 12 | Halo LED count at r 73.3: 90 or 112 | **90** | |
| 16 | 13 | Knurl starts at Ø154: 68 (v9 pitch) or 56 (v9 count) | **68** | |
| 17 | 14 | Panel orientation: chin at 180°, flex at 0° | as stated | |

---

## 1. Diameter — Ø154 or Ø150

**Context.** The panel's driver chin puts glass at r 72.05 (MEASURED). The knob's bore must clear it at every angle: Ø145. The v9 knob wall is 4.5 (1.0 knurl + 3.5 under the root): Ø154.

**Why it matters.** It is the object's diameter, the ring's width and the plate's mass; everything in the spec is derived from it.

**Options.**
- **A. Ø154, plain bore Ø145 (default).** Simple one-piece knob, the display carrier drops straight in. Ring 13.5 mm picture-edge to knob-edge.
- **B. Ø153.6 — knurl 0.8 deep instead of 1.0**, wall 4.3. Saves 0.4; the knurl is visibly shallower.
- **C. Ø150 by an undercut.** Bore Ø142 with a 3.3 mm tall internal groove Ø145.5 at the chin's height; the wall there is 2.25 mm (no knurl on that band — the smooth land under the chamfer grows from 0.8 to about 6.5 mm). The loaded carrier cannot drop straight in: the panel enters shifted 2.5–3.1 mm sideways so the chin clears the bore, then centres into the groove — and the carrier's skirt (r 72.1) cannot exist at that height, so the carrier becomes two parts. CNC: an internal undercut cutter. Not recommended: it trades 4 mm of diameter for a fiddly assembly and a knob that is no longer "the simplest shape".

**Default: A.**

## 2. The top ring — approve the drawing

`v10_top_ring.png`: at Ø154 the metal from the picture edge to the knob edge is 13.5 mm (lip edge 0.7 outside the picture, 1.0 inner chamfer, 9.3 flat, 2.5 outer chamfer). v9 was 18.7. A narrower ring needs a smaller knob (question 1) or a wider outer chamfer (each 1 mm of chamfer takes 1 mm off the flat). **Default: approve as drawn.**

## 3. Display route for v10 — HDMI adapter or Pi 5 DSI direct

**Context.** The brief says assume the DisplayModule adapter. The Pi 5 also has two 4-lane DSI connectors and could drive the panel directly through a small board (±5 V, 1.8 V, the 37 V backlight driver, the 22-way to 45-way flex change — about 25 × 40, ASSUMED) if a Linux panel driver with the HX8399-C initialisation sequence exists. It does not; it must be written, with the sequence from DisplayModule. Production needs exactly that driver on the CM5 carrier.

**Why it matters.** The adapter is 65 × 64 and is the reason v10 has a mezzanine deck. Without it the boards fit on the floor and the deck goes; the height drops about 2 mm (the fan's intake plenum then decides). But the driver is software on the critical path of a prototype whose purpose is software.

**Options.** A. Adapter now (default), driver later on the carrier. B. Driver now, no adapter, no deck. **Default: A.**

## 4. Plate thickness

**Context.** 4.16 of the spec. 8 mm: 1.16 kg solid, 0.70 kg after the Pi window and slots; fits all three plug bodies under the halo; halves the spreading resistance; costs 3 mm of the knob's share of the side (77 % → 70 %), no overall height. 5 mm: 0.43 kg net; no plug body fits under the halo without a notch. 10 mm: 1.4 kg / 0.9 kg net; every plug fits with margin; the knob is 64 % of the side (below the v9 two-thirds rule). **Default: 8.**

## 5. Barrel plug under the halo

**Context.** 6.8 of the spec. A right-angle 5.5 × 2.1 plug has a Ø8.5 body (ASSUMED — measure the one that comes with the brick, or specify one). Under an 8 mm plate's top edge with the pad, 9.0 mm is available; the body needs the pad pocketed through under it (15 × 20).

**Options.** A. Pad pocket (default). B. Notch the halo diffuser and LED ring over ±8° at the barrel — the 360° halo becomes 344°. C. 10 mm plate (question 4). D. Straight plug on a 90° adapter — adds a lump at the back. **Default: A.**

## 6. Pi power on the header while the PC is on its USB-C

**Context.** The converter feeds 5 V into header pins 2/4/6. The PC's USB-C also supplies 5 V on VBUS to the same rail through the Pi's power path. Two supplies in parallel at slightly different voltages circulate current; the Pi 5's power-management chip also uses the USB-C's negotiation to decide how much current the USB-A sockets may draw (it assumes 3 A without it — set `usb_max_current_enable=1` in the boot configuration).

**Options.** A. Internal USB-C cable with VBUS not connected (a data-only cable, or the red wire cut) — the Pi is self-powered, the PC sees a self-powered device, nothing parallels (default). B. An ideal-diode board on the header feed. C. Live with it. **Default: A.** Production: the carrier's USB-C is designed for it.

## 8. Servo — tangential with a rocker, or direct radial push

**Context.** In v9 the servo sat inboard of the carriage and pushed it directly; the sector was 57 mm deep (r 15 to 72.5). In v10 the Pi's long edge is at r 28 on the motor side; a direct push needs the Pi shifted 15 mm toward 270°, which eats the speaker's crescent.

**Options.** A. Servo tangential beside the carriage tab, a 1 : 1 printed rocker turns its stroke radial; sector 43 mm deep (default). The rocker is one more printed part with a pin. B. Direct push, Pi shifted 15 mm, speaker moved onto the deck (+9 mm of deck height where it sits — the deck is 8 mm — so the speaker would need its own cut-out over the motor sector; possible, crowded). C. Direct push with the motor at 180° in front of the Pi's short end — the crescent there is 25 mm; no. **Default: A.**

## 9. Motion board link to the Pi

A. UART (plus 5 V) through one 2 × 5 housing on the 40-pin header — one plug, no cable across the cavity (default). B. USB to a Pi USB-A socket — a 120 mm internal cable, but the same code path as production if the carrier uses an internal USB hub. **Default: A** for v10; production decides with the carrier.

## 10. Vent — passive, or through-flow with the fan

**Context.** 6.9 of the spec: the skin gives ~0.4 W/K; the v9 ports add almost nothing; the fan in a closed cavity stirs but does not exchange. 11 W sustained means a 50 °C skin.

**Options.** A. Through-flow (default): intake at the rim gap, exhaust at the ports enlarged to 24 × Ø4, a printed baffle so the cavities connect only through the fan; 0.6 W/K from 0.5 L/s. Dust enters at the lens edge and settles inside. B. Intake through four Ø8 holes in the plate and four radial channels in the pad; exhaust at the ports; the desk side gets the dust. C. Passive: ports as v9, halo sustained current capped in software (~1 A), accept a warm object. **Default: A** for v10 — it is printed geometry and a bigger drill; remove the baffle and it is C.

## 11. Cooler — keep (A′) or delete (B)

**Context.** 8.3 and 8.4 of the spec: the same height within half a millimetre (41.7 vs 41.3). A′: the cooler as bought, the fan hole in the deck, the fan runs only above ~50 °C; nothing machined. B: silent, the SoC 4 K above the plate, a machined Ø26 boss and a thermal pad that must absorb the height tolerance; the Pi's sockets face down (its micro-SD then faces up — handy). **Default: A′** for v10; production is B's principle with the CM5.

## 12. Halo LED count

90 carried from v9 is a 5.1 mm pitch at r 73.3 (v9: 4.1); 112 restores the pitch and adds 0.8 A at full white. Same flex design, longer. **Default: 90**, decided on the bench with the diffuser.

## 13. Knurl starts

56 starts at Ø154 is an 8.6 mm pitch and a 37° helix; 68 keeps the v9 7.1 mm pitch and ~32°. Four whole rows either way. **Default: 68.**

## 14. Panel orientation

Chin at 180° (under the knob wall toward the user, invisible), flex tab at 0° where the adapter's panel connector is. Any rotation works; the picture is software. **Default: as stated.**

## 15. Is the bare panel available in ones?

If DisplayModule will not sell one, v10 uses the dummy disc of 4.4 (printed, with the chin and the tab from the STEP, and a clear acrylic lens) and software runs on the Waveshare bench display. Nothing else changes. **Ryan to say.**

## 16. Cover lens

Ø140 × 2.5, black border from r 63.5 outward, touch tail 8 mm wide at the flex edge — all ASSUMED; the carrier is designed to these. Acceptable range Ø135–140.5. **Ryan / the lens supplier.**

## 17. Adapter to panel

The panel's flex is 45-way at 0.3 mm; the adapter's output was noted as 60-pin. Confirm with DisplayModule that DM-ADTTR-014 mates directly or ships with a bridge flex, and get the adapter's mechanical drawing. **Ryan.**

## 18. Board envelopes

Audio 25 × 40 × 6 (Ryan's footprint, height assumed), motion 50 × 40 × 8 (proposed), touch controller 20 × 30 × 4 (assumed), converter 25 × 38 × 10 (Pololu D24V90F5 class, assumed). Deck bosses are placed to these; change them here and they change in one line. **Default: as stated.**
