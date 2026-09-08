# the 60 — the small boards, the power inlet and the wiring

**Date: 8 September 2026. Status: sourcing answers, for the decision index.**
Answers `SMALL-PARTS-SOURCING-PROMPT.md` items A to M. Closes the `SOURCING-BOM.md`
line reading *"small boards — no briefs written"*.

Scope: **one prototype, bought this week.** Volume is a footnote on each item, not a
filter. Where a vendor does not publish a number it is written **not published**, not
estimated.

---

## 1. The headline

**Of the thirteen items, eight can be bought, two are genuinely custom, one is deleted by
a finding, and two are waiting on the parallel motion-board exercise.**

The single most important result is not a part. It is this:

> **The Raspberry Pi 5's USB-C socket carries no USB data.** It is a power input with
> the two configuration-channel pins used for power negotiation, and nothing else. All
> four data-carrying USB ports come from the RP1 support chip, which is host-only. A
> host computer plugged into the Pi 5's USB-C socket cannot see the object as a device.

If that holds — and it needs a twenty-minute bench check before anything is redesigned
around it — then **item E does not need solving, it needs deleting.** There is no second
5 V source, because there is no reason for the internal lead to exist. It also changes
what item G's external socket is for, and it means the prototype's link to the host
computer has to come from a microcontroller, which is a part already on the parts list.

The rest is mostly good news. The 3.5 mm jack's carrier board, the light sensor's board
and the vibration actuator's pogo-pin board can all be deleted in favour of bought parts.
**Two boards have to be custom: K, the knob encoder, and G, the USB-C receptacle.** Nobody
sells an AEDR-8300 breakout, and — corrected in §5 below — no panel-mount USB-C part made
by anybody fits the 8 mm of port face available below the halo. Both boards are small, and
putting them in one fabricator order makes the second one nearly free.

Two items came back worse than expected. **The specified mains supply family is Class I,
not Class II** — the GST60A and GSM60A parts have a three-pin earthed inlet, so the whole
grounding scheme in `GROUNDING.md` §2 would have been built on a wrong part. And **no
12 V to 5 V converter module in this size class publishes a still-air derating curve
against ambient temperature**, which means that number has to come from a bench
measurement rather than a datasheet.

---

## 2. The table

Prices are for one unit. VAT status is stated where the distributor showed it.

| | Item | Recommendation | Part / supplier | Price | Size | Status |
|---|---|---|---|---|---|---|
| **A** | Mains supply | Change the specified part — GST60A/GSM60A are **Class I** | Mean Well **GSM60B12-P1J**, TME or Mouser | £17.46 (Mouser) | 125 × 50 × 31.5 mm | **Bought** — verify one glyph on the datasheet |
| **B** | Power inlet | Keep the PJ-063AH; draw the CAD by hand | Same Sky **PJ-063AH**, RS 259-6514 | ~£1–2 | 13.0 × 10.3 × 6.5 mm | **Bought** — no CAD model published |
| **C** | 12 V → 5 V | Keep the converter. Buy two cheap ones and bench them | Hobbywing UBEC-5A **£12.90** + generic 5 A module **£6.90** | **£19.80** the pair | 50 × 17 × 10 and **35 × 19 × 7.8** mm | **Bought** — still-air figure not published by anyone, measure it |
| **D** | 5 V distribution | No hardware. It is a copper pour and a connector | — | £0 | — | **Handled by a part already being made** |
| **E** | Two 5 V sources | **Delete the problem.** See §4 | — | £0 | — | **Deleted by a finding** |
| **F** | Light sensor | Bought breakout with a pre-made cable | Adafruit 4162, The Pi Hut | £4.80 | 16.6 × 16.5 × 4.0 mm | **Bought** |
| **G** | External USB-C | **Correction: nothing panel-mount fits.** Keep the board | GCT **USB4520** on a ~10 × 10 mm board, in the encoder's fab order | ~£6 | aperture ~9 × 3.5 mm | **Custom** — or deleted by a microcontroller, see §5 |
| **H** | 3.5 mm jack | Bought panel jack. The board goes away | Black nylon panel jack, HiFi Collective | £1.24 + VAT | 6.3 mm hole, 3 mm max panel | **Bought** |
| **I** | Actuator contacts | Bought pre-wired pogo block, no board at all | Mill-Max **867-22-002-70-501010**, Mouser | $11.93 | 2 way, 2.54 mm pitch | **Bought** — spring force not published |
| **J** | Rotor sensor | Unbranded module is the only option; cable is unresolved | Generic MT6701 module, Amazon/eBay UK | ~£5–8 | 15 × 17 mm (QFN version) | **Undecided** — depends on the motion board |
| **K** | Knob encoder | Nothing exists. This one is genuinely custom | Broadcom **AEDR-8300-1W2**, Farnell UK | £8.10 ex VAT | see §5 | **Custom** |
| **L** | Harness | Split it. Do not buy the £460 tool for one unit. See §6 | Mixed — see §6 | £30–60 parts | — | **Undecided by design** |
| **M** | Bonding + knob bleed | Washers are trivial. The leaf is hand-formed from bought stock | RS + a UK shielding supplier | <£20 | — | **Bought stock, formed by hand** |

---

## 3. Part one — power

### A. The mains supply: the specified family is the wrong safety class

`GROUNDING.md` §2 makes the whole grounding scheme depend on a **Class II** supply —
double insulated, two-pin, no earth pin — because the object already gets an earth
reference from the computer, and a second one is how a ground loop hums.

**Two of the three obvious Mean Well parts are Class I.** Confirmed by opening the
datasheets:

- **GST60A12-P1J** — inlet is `IEC320-C14`, a three-pole earthed connector, and the
  withstand-voltage table lists `I/P-FG: 2KVAC O/P-FG: 0.5KVAC`, where FG is frame
  ground. There is a real earth reference.
  [datasheet](https://www.meanwell.com/Upload/PDF/GST60A/GST60A-SPEC.PDF)
- **GSM60A12-P1J** — same C14 inlet, and the datasheet states outright
  *"-V connected to AC FG (standard)"*: the negative output rail is bonded to protective
  earth. That is as unambiguous as Class I gets.
  [datasheet](https://www.meanwell.com/Upload/PDF/GSM60A/GSM60A-SPEC.PDF)
- **GS60A12-P1J**, the genuinely Class II Mean Well part, is **obsolete** at Mouser.
- **XP Power VEH60US12** is **no longer manufactured**, per XP Power's own page.

So the part named in the sourcing document would have quietly undone the audio ground
scheme. This is the item where "check the datasheet, not the category" earned its keep.

**Three current Class II candidates, all with a published leakage figure:**

| | **Mean Well GSM60B12-P1J** | **XP Power AMF60US12-P** | **XP Power AKM65US12C2** |
|---|---|---|---|
| Class II stated in words? | **No.** Inferred from a fixed `IEC320-C8` two-pole inlet, `2xMOPP` primary-to-secondary isolation, and a leakage section that lists only touch current with **no earth-leakage entry at all** — unlike its Class I sibling, which has both | **Yes** — *"Their Class II construction, gasketed design and reinforced isolation…"* | **Yes** — *"the class II version with suffix C2 has a polarized IEC320-C8 inlet"* |
| Touch / leakage current | *"Touch current < 50 µA / 264VAC"* | *"Patient leakage current 90 µA at 264VAC"* | *"Leakage current 100 µA, 264VAC"* |
| Mains inlet | C8 figure-of-eight — any generic UK figure-of-eight lead fits | No inlet; clip-on blade heads, and the **-P** suffix includes the UK blade | C8 polarised; a standard UK figure-of-eight lead fits |
| **DC plug** | **5.5 mm outer / 2.1 mm inner**, centre positive — the common size | **5.5 / 2.5 mm** — a 2.1 mm jack will sit loose | **5.5 / 2.5 mm** — same caveat |
| Size | 125 × 50 × 31.5 mm | 90.5 × 58.5 × 33.5 mm | 125 × 62.3 × 34 mm |
| UK price / stock | **£17.46 Mouser UK** (142 in stock, but flagged business-customers-only); **TME 219 in stock**, ships to the UK, no such flag | £27.40 Mouser, **not stocked, ~22 week lead** | £26.50 Mouser, **not stocked, ~20 week lead** |

Datasheets: [GSM60B](https://www.meanwell.com/Upload/PDF/GSM60B/GSM60B-SPEC.PDF) ·
[AMF60](https://www.xppower.com/storage/portals/0/pdfs/SF_AMF60.pdf) ·
[AKM65](https://www.xppower.com/storage/portals/0/pdfs/SF_AKM65.pdf)

**Order the GSM60B12-P1J from TME.** It is the only one of the three in stock this week,
and it is the only one with the 2.1 mm inner-diameter plug that matches the chosen inlet.
Its Class II case rests on physical grounds rather than the printed words — a C8 inlet is
defined by the standard for double-insulated equipment only, and the absence of an
earth-leakage line is itself evidence — which is solid, but note it is inference.

One caveat, worth thirty seconds: the "µ" symbol fails to extract from the Mean Well
PDF in two separate text tools, leaving the raw string "50 A/264VAC". That is a
font-encoding artefact, not a claim of fifty amps, but **open the PDF and look at the
line before you file the number.**

The GSM60B is a *medical* supply, which is why its leakage figure is so low and why it
costs £17 rather than £13. For an object with a bare metal knob under a damp hand, that
is the right place to spend five pounds.

> **Volume footnote.** No dead end. Mean Well GSM60B is a mainstream, in-production
> family; sixty units is nothing to it. Certification of the finished object is a
> separate matter and unchanged by this choice.

### B. The inlet

**Keep the CUI/Same Sky PJ-063AH.** Right-angle, through-board, 5.5 mm outer, 2.0 mm
centre pin, **rated 8 A** per the
[datasheet](https://dir.heisener.com/DatasheetDownload/PJ-063AH.pdf). Listed at
[RS 259-6514](https://uk.rs-online.com/web/p/dc-power-connectors/2596514) and DigiKey UK.
Body about 13.0 × 10.3 × 6.5 mm.

**The finding you asked for: there is no CAD model.** Same Sky's own 3D-model page for
this part returns *"the 3D model requested does not exist"*
([source](https://www.sameskydevices.com/product/resource/3dmodel/pj-063ah)) and Ultra
Librarian shows "No 3D Model Available". The mechanical model will have to be drawn from
the dimensioned 2D drawing in the datasheet. It is a simple prismatic part, so that is
an hour, not a problem — but it is an hour nobody had allowed for, and the common
assumption that every Same Sky part has a downloadable solid model is false for this one.

**One coupling to police:** the jack's centre pin and the brick's plug must match. The
GSM60B12 has a 2.1 mm inner-diameter plug, which fits the PJ-063AH's 2.0 mm pin. Both XP
Power alternatives have **2.5 mm** plugs, which would fit loosely and eventually
intermittently. If A changes, B changes with it.

> **Volume footnote.** No dead end. Commodity part, deep stock.

### C. Should there be a converter at all? Yes, and here is the arithmetic

This is the interesting question in part one, and it has a clean answer.

**The load.** From `SYSTEM-REVIEW.md` §3.1 as corrected by `HALO-BRIGHTNESS.md`:
worst case **about 7 A at 5 V, 35 W**; realistic sustained **about 2.5 A, 12.5 W**.

**What that does to a barrel connector and a lead.** A 60 W desktop brick's DC lead is
typically 18 AWG, about 1.5 m long. 18 AWG is 20.95 mΩ per metre, so the round trip is
about 63 mΩ.

| Arrangement | Current | Voltage lost in the lead | As a fraction of the rail | Heat in the lead |
|---|---|---|---|---|
| **12 V in, convert inside** | 3.2 A | 0.20 V | 1.7 % | 0.6 W |
| **5 V in, no converter** | 7.0 A | **0.44 V** | **8.8 %** | **3.1 W** |

The Pi 5 will not tolerate 4.56 V at the board. To deliver 5 V at the object with 5 V at
the inlet, the brick would have to be trimmed to about 5.5 V, or the lead thickened, and
neither is a thing you buy off a shelf.

Two further points against 5 V direct. The barrel jack would be running at **7 A against
an 8 A rating** — 88 % of a contact that also wears, and the published ratings for
nominally similar 5.5 mm jacks span 2.5 A to 8 A depending on the exact part, so it is
not a category you can trust, only a specific part. And a Class II 5 V 7 A brick with a
barrel output is close to a non-existent part: 5 V supplies at that current are almost
all USB-C power-delivery, which brings a whole negotiation problem with it.

**Conclusion: keep the 12 V brick and the internal converter.** The converter is not a
component you can delete; it is the thing that lets the cable be thin.

**Which converter — and an uncomfortable finding.** Nothing in this size class publishes
what you asked for:

| Part | Current | Still-air derating against ambient? | Size | Price / stock |
|---|---|---|---|---|
| **Pololu D24V90F5** | ~9 A | Curve **is** a no-airflow, no-heatsink figure, but its axis is **input voltage, not ambient temperature** — so **no ambient-referenced figure published** | 40.6 × 20.3 × 7.6 mm | $36.82, ships from Pololu US |
| Murata OKL2-T/6-W12N-C | 6 A | **Not verified** — Murata's own PDF server returned an error on every attempt | 12.2 × 12.2 × 7.2 mm | £5.34, DigiKey UK ships today |
| Traco TSR 3-2450N | 3 A | **Yes, plainly** — *"full load … up to +95 °C ambient … without any heat sink or forced cooling"* | 14.0 × 7.6 × 10.2 mm | £6.34, Mouser UK, 1,722 in stock |
| Analog Devices LTM4638 | 15 A | **Yes** — a real 0 LFM curve, ~14 A at 40 °C | 6.25 × 6.25 × 5.02 mm | £28–39, Mouser UK in stock |
| Generic Amazon/eBay "12 V to 5 V 8 A" | claimed | **No data of any kind published** | not published | £5–15 |

Sources: [Pololu D24V90F5](https://www.pololu.com/product/2866) ·
[Mouser OKL2-T/6-W12N-C](https://www.mouser.co.uk/en/ProductDetail/Murata-Power-Solutions/OKL2-T-6-W12N-C) ·
[LTM4638 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ltm4638.pdf)

The LTM4638 is the only part with a genuine, ambient-referenced still-air curve — and it
is a bare chip in a ball-grid package that has to be cooled *through* a circuit board,
not through its top face. Choosing it means designing a board, which is exactly what this
exercise exists to avoid. Ruled out on the mantra, not on the electronics.

**Corrected recommendation: do not spend £30 here.** The first draft of this document
recommended the Pololu D24V90F5 at $36.82, and that was not defensible. Pololu publishes
no ambient-referenced derating either, so the extra money was buying build quality and an
honest product page rather than data — and the number still had to come off a bench.

**The right answer comes from the radio-control world.** A switching "battery eliminator
circuit" is a 5 V regulator built to run continuously inside a sealed model aircraft with
no airflow. That is this use case exactly, they are finished boards, and they are cheap.

| Part | Rating | Size | Price | Source |
|---|---|---|---|---|
| **Hobbywing UBEC-5A (2-8S)** | **5 A continuous, 15 A peak**, 7.4–29.6 V in, overheat protection | 50 × 17 × 10 mm | **£12.90**, in stock | [Flying Tech](https://www.flyingtech.co.uk/product/hobbywing-5a-2-8s-ubec-with-5-0v-6-0v-7-4v-output/) |
| **Generic 2-13S 5 V 5 A module** | 5 A continuous, 8–55 V in; **no peak rating stated** | **35 × 19 × 7.8 mm** — fits the envelope | **£6.90**, in stock | [Flying Tech](https://www.flyingtech.co.uk/product/voltage-regulator-module-2-13s-5v-5a-bec/) |
| Hobbywing UBEC-8A (2-3S) | 8 A / 15 A, but the **input ceiling is 12.6 V** — no margin over a warm 12 V brick | 42 × 39 × 9 mm | £15.99, out of stock | [3DXR](https://www.3dxr.co.uk/electronics-c78/power-management-c91/voltage-regulators-becs-c101/hobbywing-8a-ubec-5v-6v-switchable-2-3s-p4787) |
| Generic LM2596 or XL4015 board | £3.45 of silicon that is genuinely 3 A, on a board with little copper and no thermal spec. Independent testing finds an LM2596 module wants a heatsink above about 1 A | varies | £3.45 | [eBay UK](https://www.ebay.co.uk/itm/165082020523) |

**Buy the Hobbywing and the generic, £19.80 the pair, and settle it on the bench.** The
Hobbywing's stated 5 A continuous / 15 A peak split is the figure that actually matters,
because the load's shape is a few amps continuous with a short coincident peak. The
generic is the better mechanical fit and half the price. Together they cost less than the
Pololu, and one of them will be the answer.

**One more finding, because it inverts the instinct:** the part in this whole survey with
the best published thermal data — the Traco TSR 3-2450N, *"full load up to +95 °C ambient
without any heat sink or forced cooling"* — is a **3 A part with no burst rating**, and
industrial converters of that type current-limit at roughly 110 to 150 % of rating. It
would have failed the peak requirement outright. **The best-documented part was not the
right part.** Spending more was not buying more certainty.

**The still-air number still has to be measured**, at any price, because nobody in this
class publishes one. The test is in `SMALL-PARTS-ORDER-LIST.md` §7, and it doubles as
`THERMAL-PLAN.md`'s Test B.

**And a design argument for buying capacitance rather than converter headroom.** The 7 A
worst case assumes the motor's 2 A, the halo's 2.21 A and the compute module's 2.5 A
peaks all land together. `SYSTEM-REVIEW.md` §3.4 already doubts the motor figure — it is
the driver's rating, not a measurement of a gimbal motor on a 5 V rail — and
`HALO-BRIGHTNESS.md` limits the halo by rolling mean. **The real shape of the load is
about 3 A continuous with a coincident peak lasting a few hundred milliseconds** — which
is exactly the shape a 5 A continuous / 15 A peak part is built for, and exactly why the
peak rating matters more than the continuous one. A few thousand microfarads of bulk
capacitance on the output shortens that peak still further and costs a pound.

> **Volume footnote.** A radio-control module is a hobby part with no certification
> support and no published derating — a genuine dead end at sixty units. At production the
> answer is a proper module with a baseplate (the TDK-Lambda i7C family has one) or a
> converter designed onto the carrier board. Nothing here forecloses that, and the bench
> measurement this prototype produces is the input to that choice.

### D. Distributing the 5 V

**No hardware. This item can be closed with a pen.**

`GROUNDING.md` §3 already places the star point on the carrier board at the power inlet.
That means the star is **a copper pour and a connector on a board that is being made
anyway** — three separate pairs leaving one node, which is a layout instruction, not a
purchase.

Nothing bought earns its space. For completeness, the two things that came closest:

- **WAGO 221-415 lever connector**, 32 A, 0.14–4 mm² per port, about £0.50 at RS, 6,000+
  in stock. It genuinely is a star point — one shared bus, independently clamped legs.
  Worth having *only* if the star has to live off-board and be serviceable. Check its
  height against the 11.5 mm internal cavity before assuming it fits; it is the tallest
  thing on this whole list.
  [RS 221-412](https://uk.rs-online.com/web/p/standard-terminal-blocks/8837544)
- **Adafruit brass distribution bus**, £1.90 at The Pi Hut, 55 × 19 × 11 mm without its
  flanges. Its current rating is the vendor's phrase *"good for at least 10 A … it's just
  a chunk of metal"* — which is honest, and is not a specification.

The automotive fused distribution blocks that show up in this search are 100 mm-plus
parts sized for car electrical systems. Wrong scale by a factor of three.

> **Volume footnote.** No dead end — the star is on the board.

---

## 4. Item E — the two 5 V sources, and why the answer is to delete the question

You asked for this to be treated as the most important item in part one. It is, but not
for the reason the question assumes.

### The finding

**The Raspberry Pi 5's own USB-C socket appears to carry no USB data.**

- The [Raspberry Pi 5 product brief](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-6-raspberry-pi-5-product-brief.pdf)
  lists the USB-C connector **only** under power — *"5 V/5 A DC power via USB-C, with
  Power Delivery support"* — and lists the four data ports separately as the USB-A
  connectors.
- The [RP1 peripherals datasheet](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008370-DS-1-rp1-peripherals.pdf)
  names its USB blocks `usbhost0` and `usbhost1` — *"two independent XHCI controllers"*.
  XHCI is a **host** controller specification. RP1 supplies all four USB-A ports and has
  no device-mode controller in it.
- The Compute Module 5 input/output board's documentation describes **a separate USB-C
  connector** *"for flashing CM5 or additional peripherals"* — that is the one wired to
  the processor's own device-capable USB 2.0 controller. It is a different connector on
  a different board. Almost every online discussion of "Pi 5 gadget mode" is actually
  about the compute module.
  [source](https://www.raspberrypi.com/documentation/computers/compute-module.html)

**Confidence: strong, but not schematic-proven.** Raspberry Pi has not published a
schematic for the Pi 5 at all — the product information portal carries product briefs,
mechanical drawings and 3D models, and no schematic document. So the specific claim "the
data pins are not connected to the USB-C socket" is inference from the product brief and
the RP1 architecture, not something read off a drawing.

**Check it on the bench before redesigning anything.** Twenty minutes: configure `dwc2`
and `libcomposite` on the Pi 5 exactly as the Pi 4 recipe describes, plug the Pi's USB-C
socket into a computer, and see whether anything enumerates. If nothing does, the finding
holds.

### What it means

Three things fall out.

**One: item E dissolves.** If nothing useful passes through the Pi's USB-C socket, there
is no reason to run an internal lead to it, and therefore no second 5 V source. The whole
question — cut the VBUS conductor, or fit an ideal-diode part — is answering a problem
that should not be built.

*VBUS is the 5 V power conductor in a USB cable. An ideal-diode part is a transistor
arranged to behave like a diode with almost no voltage drop, so two supplies can be
connected to one load without either pushing current back into the other.*

**Two: `SYSTEM-REVIEW.md` §3.2 and the `FUNCTION-ALLOCATION.md` bench item "Pi as a USB
keyboard, mains-powered, through the splitter" both need revising.** The USB-C data and
power splitter at £3 from The Pi Hut solves a real Pi 4 problem and does nothing for a
Pi 5. Do not buy it.

**Three: the prototype needs a different route to the host computer — and the part is
already on the list.** `BOARD-MOTION.md` §8 already establishes that the RP2350 does
composite USB keyboard, mouse and consumer-control out of the box under TinyUSB, with
public examples. The **Raspberry Pi Pico 2 at £3.60**, already on the
`FUNCTION-ALLOCATION.md` buy list, is the USB device. The Pi 5 talks to it over a serial
line and never talks to the host computer at all.

That is a better architecture for the prototype anyway. It matches where production is
going — `SYSTEM-REVIEW.md` §3.2 describes the production carrier solving this with a hub
in front of the compute module — and it removes the parallel-supply hazard by making it
impossible rather than by managing it.

### The four states, both ways

**Recommended arrangement — external USB-C socket goes to the microcontroller, not to
the Pi. The Pi is powered only from the header.**

| Mains | Computer | Pi runs | Host sees the object | Risk |
|---|---|---|---|---|
| on | disconnected | yes, from the header | no | none |
| on | connected | yes, from the header | yes, as the microcontroller's device | none — one supply, always |
| off | connected | no | no | none — the microcontroller may run off the computer's port; keep the two rails separate so it cannot back-feed the object |
| off | disconnected | no | no | none |

**If the bench check proves the Pi 5 *can* do device mode after all**, then the answer is
**cut the VBUS conductor in the internal lead**, not an ideal-diode part. Three reasons:

- It costs nothing and cannot fail in an ambiguous way.
- An ideal-diode part *keeps both sources live*, which means that with the mains off the
  object would try to run off the computer's port. A computer port cannot supply 7 A at
  5 V. The object would brown out under load, intermittently, in a way that looks like a
  software fault. That is the worst possible failure to design in deliberately.
- The USB specification requires a self-powered device not to draw VBUS from the host in
  any case.

And **add the thing neither candidate answer included**: bring the host's VBUS through a
resistor divider to a spare input pin as a *host-present sense* line, going nowhere near
the 5 V rail. That recovers the consequence `SYSTEM-REVIEW.md` §3.2 flagged — with VBUS
cut, the Pi has no electrical indication that a computer is attached — for the price of
two resistors.

| Mains | Computer | Pi runs | Data | Risk |
|---|---|---|---|---|
| on | disconnected | yes, header | no | none |
| on | connected | yes, header | yes; host-present line reads high | none — VBUS never reaches the rail |
| off | connected | **no** | no | none; the object is simply dark. It cannot be run from a computer port, by design |
| off | disconnected | no | no | none |

No pre-made data-only USB-C cable is sold in the UK. The realistic routes are the Pi Hut
splitter (for a Pi 4, not a Pi 5) or cutting the conductor inside a plug by hand.

> **Volume footnote.** The microcontroller route is the production architecture too, so
> this is a step towards sixty units rather than away from them.

---

## 5. Part two — the small boards

### F. Ambient light sensor — bought, easily

**Adafruit 4162, £4.80 at The Pi Hut, 13 in stock.**
[The Pi Hut](https://thepihut.com/products/adafruit-veml7700-lux-sensor-i2c-light-sensor-ada4162) ·
[Adafruit](https://www.adafruit.com/product/4162)

- **Board: 16.6 × 16.5 × 4.0 mm** including the connectors.
- Two STEMMA QT connectors, which means **a pre-made cable, no crimping**, and it chains.
- **No mounting holes.** This board is meant to be taped, glued or held.
- A right-angle variant, Adafruit 5378, keeps the same footprint but takes the connector
  out sideways, which is worth having in a 6 mm envelope.

**The number you asked for and did not get: the sensor's offset from the board edge is
not published.** No vendor states it in text. It is in the Eagle board file in
[Adafruit's PCB repository](https://github.com/adafruit/Adafruit-VEML7700-PCB) and has to
be read out of there. What matters mechanically is that the sensor sits near the middle,
so **the port face needs about 17 mm of clear space behind the 4.8 mm hole**, not 5 mm.

Three retailer names in the original brief turn out not to apply, which is worth
recording so nobody searches for them again: **Pimoroni** resells the Adafruit board
rather than making one; **M5Stack's** "DLight" ambient light unit is a BH1750, not a
VEML7700; **Seeed's** Grove light sensor is a phototransistor part. **DFRobot's** Gravity
board is real but 30 × 22 mm and has no confirmed UK stockist.

> **Volume footnote.** No dead end at sixty, but at that point the sensor is three
> components on the carrier board and this breakout disappears.

### G. External USB-C socket — correction: nothing panel-mount fits

**The recommendation in the first draft of this document was wrong, and this is why.** It
sized the connector against the object's 36 mm overall height. The number that governs is
not that one.

**The port face has about 8 millimetres of usable height.** `V9-SPECIFICATION.md` §4.14
puts the USB-C receptacle at **z 0.1 to 3.3** on a horizontal board in a slot through the
plate, and `V14-SPECIFICATION.md` §4.8 puts the halo band at **z 8.0 to 13.5**. Everything
on that face — the USB-C opening, the Ø6.3 jack hole and the Ø4.8 light-sensor aperture —
lives in the band below the halo.

Against that, the whole panel-mount market is out:

| Option | Panel cutout | Verdict |
|---|---|---|
| Adafruit 4218 round panel lead | **21.5–27 mm hole**, 29.5 mm nut | Three times the available height |
| Adafruit 6069, the smallest round part found anywhere | **12–18 mm hole** | Still half again too tall |
| Delock 87824, the only rectangular two-screw part found | **21.5 × 12.5 mm**, 28 mm screw pitch | Taller than the whole band, and its depth behind the panel is not published |
| Cliff CP30201 / CP30211 feedthrough | **Ø24 mm**, XLR-standard, 19 mm deep, 3 mm maximum panel thickness | No |
| Neutrik NAUSBC-5G | XLR D-shape cutout | No |

**So item G goes back to being what the design already had: a GCT USB4520 mid-mount
receptacle on a small board behind an aperture.** The aperture is then just the connector's
own shell, about **9 × 3.5 mm** — a phone-sized slot, not a hole with a nut around it.

That is the right answer anyway, for three reasons beyond fit. The board is about 10 × 10
mm with four solder pads, so it is the simplest board in the object. **It goes into the
same fabricator order as the encoder board** — most fabricators run several outlines under
one job — so it costs a few pounds and no extra shipping. And the **metal shell bonds to
the chassis properly**, by the short wire already modelled in `V14-SPECIFICATION.md` §4.9,
instead of being defeated by a plastic housing.

**The better answer, if the Pi 5 finding holds.** Once the host connection moves to a
microcontroller (§4), a small board with a **USB-C socket on its own edge** would be the
external socket, the host interface and the internal lead all in one part, and this board
would not need to exist at all:

| Board | Size | Price | Stock |
|---|---|---|---|
| **Seeed XIAO RP2350** | **21 × 17.5 mm**, thickness **not published** | **£4.80** | [In stock, The Pi Hut](https://thepihut.com/products/xiao-rp2350-raspberry-pi-rp2350) |
| Pimoroni Tiny 2350 | 22.9 × 18 × 5.8 mm including the socket | £6.50 | [Out of stock](https://shop.pimoroni.com/en-us/products/tiny-2350) |

**What has to be measured**, because no vendor publishes it: the board's overall thickness
and how far its socket's axis sits above the board. The design needs that axis at about
**z 2.5**, with the receptacle inside z 0.1–3.3. That is a callipers question and it costs
£4.80 to answer.

**Do not delete the USB-C board from the fabricator order until that measurement is
made.** Both boards in one job cost about £15 all in; ordering the second one later costs
another shipping charge and another week.

> **Volume footnote.** No dead end either way. The GCT mid-mount on a board is already the
> production intent; the microcontroller route is where the host interface is going anyway.

### H. The 3.5 mm jack — and the requirement is already satisfied by the panel

Two corrections first.

**Neutrik NRJ4HF and NRJ6HF are 6.35 mm parts, not 3.5 mm.** Neutrik's own product pages
describe them as quarter-inch sockets. They do not apply to this jack at all and should
come out of the notes. Neutrik's 3.5 mm offerings are branded Rean, and the Rean parts
that surface are plugs and adapters, not a panel-mount stereo socket.

**The incumbent Switchcraft 35RAPC4BH3 already has a thermoplastic body and cover**, per
[Switchcraft's own page](https://www.switchcraft.com/3-5mm-pc-horizontal-mount-jack-stereo-threaded-bushing/35rapc4bh3/).
Whether its *threaded bushing* — the part that touches the panel — is metal and bonded
internally to the sleeve is **not published**. That is a two-minute continuity check
between the bushing and the ground tab, and it will settle the question better than any
datasheet.

**The buyable answer: a black nylon panel-mount 3.5 mm stereo jack, £1.24 + VAT from
HiFi Collective.** 6.3 mm mounting hole, maximum panel thickness 3 mm. The retailer's own
words are the confirmation you asked for: *"The black nylon body makes it suitable for
fixing to steel chassis where isolation from the chassis is required."* That is a
retailer's claim rather than a manufacturer datasheet, so verify with a meter at goods-in.
[HiFi Collective](https://www.hificollective.co.uk/components/3-5mm-stereo-jack-socket-panel-mount.html)

Its 3 mm maximum panel thickness will need a local thinned boss in the printed port face.
Small, but it is a CAD change.

**The point worth making plainly, though.** `GROUNDING.md` §6 already establishes that the
port face is plastic, which is what makes this requirement true. **No jack's shell can
reach the chassis through a plastic panel, whatever the jack is made of.** So the
requirement is satisfied by the panel material, and the connector choice barely matters
to it. What actually needs policing is the second path: **no metal screw, standoff,
bracket or bond wire may bridge the jack's shell to anything with a chassis reference.**
That is the failure mode, and it will arrive as a fixing, not as a connector.

**The custom carrier board goes away.** A panel-mount jack with solder tags and two flying
leads does the whole job.

> **Volume footnote.** No dead end. Panel jacks are commodity.

### I. Vibration actuator contacts — bought, with an unpublished number

*A linear resonant actuator is a small vibration motor with a mass on a spring, driven at
its resonance. Pogo pins, or spring pins, are spring-loaded plungers that make contact by
pressing rather than by soldering.*

**Mill-Max 867-22-002-70-501010, $11.93 at Mouser, 993 in stock.** A moulded two-position
housing with a 305 mm pigtail of 24 AWG stranded wire already crimped on. **No board at
all** — this deletes the 7 × 8 mm custom board outright.
[Mill-Max](https://www.mill-max.com/products/spring-loaded/crimped-wire-cable-assembly/867/70-501010) ·
[Mouser](https://www.mouser.com/ProductDetail/Mill-Max/867-22-002-70-501010)
Two positions, 2.54 mm pitch, 1.4 mm maximum stroke.

**Its spring force is not published**, and force is the whole question here, because the
vendor's warning is that soldering separates the adhesive. Mill-Max's catalogue default is
stated in their engineering notes as **60 g at mid-stroke**, and their purpose-made
low-force options only reach **45 to 55 g**.
[Mill-Max low-force options](https://www.mill-max.com/products/new/introducing-low-force-spring-options-for-high-reliability-spring-loaded-interconnects)

Two pins at 45–60 g is **90 to 120 grams-force, roughly 1 newton, pressing the actuator
away from its pads.** A 10 × 10 × 4 mm actuator weighs a gram or two. One newton is very
much larger than anything its adhesive was meant to resist.

**So the design conclusion is not about the connector.** Whatever pin is chosen, **the
actuator needs a moulded pocket that reacts the pin force mechanically**, with the
adhesive doing nothing but locating it. That is an enclosure feature, and it is the
requirement `CONNECTORS.md` §4 exception 3 gestured at without stating. Ask Mill-Max for
the 867's force figure when you order; they will give it.

Nothing lower-force and housed was found. Harwin's S-series and Keystone's battery
contacts do not publish a spring force at all, so they cannot be designed against.

> **Volume footnote.** No dead end; Mill-Max is a production supplier. At sixty units the
> pins move onto the motion board and the pocket stays.

### J. Motor rotor sensor — the module is easy, the cable is the real question

**J1 — the board.** **No reputable vendor sells an MT6701 breakout.** Checked SparkFun,
Adafruit, Pimoroni, The Pi Hut, Waveshare and the SimpleFOC shop. SimpleFOC supports the
part in firmware but does not sell a board for it. This matches
`FUNCTION-ALLOCATION.md`'s existing note.

Unbranded modules are the only option. A published comparison of three of them:

| Module | Size | Package | Note |
|---|---|---|---|
| "XunXuanSmart" | **15 × 17 mm** | QFN-16 | Smallest; the mode-select pads are very small and fiddly to solder |
| "MT6701QT" | 23 × 23 mm | SOP-8 | All pins exposed, no rework needed |
| "01355" | 23 × 23 mm | SOP-8 | Cheapest; needs a hardware modification for quadrature output |

[source](https://garrysblog.com/2026/04/01/comparing-mt6701-modules-for-rotary-encoder-replacement/)

The bare chip is 2.9–3.1 mm square in QFN-16, 4.7–6.2 mm in SOP-8
([datasheet](https://www.magntek.com.cn/upload/pdf/202407/MT6701_Rev.1.8.pdf)).

**Dependency, flagged not assumed:** if the motion-board sourcing exercise returns a
bought board that already carries an MT6701 or equivalent, this item disappears. Do not
buy until that comes back — except for the one already on the
`FUNCTION-ALLOCATION.md` list for bench work, which is worth having regardless.

**J2 — the cable, and this is the honest part.**

**No vendor anywhere publishes a flex life for an excursion of 2.4 mm.** Every published
cycle rating is measured at a fixed tight bend radius through a full bend. What is
published:

| Option | Published cycle life | The catch |
|---|---|---|
| **Molex Premo-Flex 15166/15167/15168** flat flexible cable, 0.12 mm | **2.5 million cycles** | The test radius, stroke and speed behind that number are **not published**. And it forces a flat-cable connector onto the sensor board |
| Molex Premo-Flex 98266/98268, 0.22 mm | 100,000 cycles | Exactly at your requirement, no margin |
| Würth flat flexible cable | **Not published** — only a static "20 × 180° fold" handling spec, which is not a fatigue test | — |
| igus chainflex CF98.PLUS | >100 million cycles | Drag-chain cable, sized for machinery, far too large |
| Fine stranded silicone or PTFE hookup wire | **Not published by anybody** — sold as "ultra flexible" with no number | — |

*Flat flexible cable, often abbreviated FFC, is a flat ribbon of parallel conductors that
slots into a matching connector.*

**What the physics says.** Gore's technical note gives the governing relation: peak fibre
stress is proportional to conductor thickness and inversely proportional to bend radius,
so *"reducing the diameter of the cable results in an exponential increase in flex life
when the bend radius remains constant"*, and flat conductors reach roughly a hundred times
the flex life of round cable under equivalent conditions.
[Gore](https://www.gore.com/resources/tech-note-understanding-cable-stress-and-failure-high-flex-applications)

**The recommendation, stated as what it is — reasoning, not a citation.** 2.4 mm is a very
small excursion. Take it as a change in the bow of a pre-formed service loop, not as a
hinge: **fine stranded wire, 30 AWG or finer with a high strand count, anchored at both
ends with at least 25 mm of free length** — ten times the travel — so the movement is
distributed along the loop instead of concentrated at one radius. Under those conditions
the strain range is far below anything the rated products above are qualified against.

**If you want a number rather than an argument**, the Molex Premo-Flex 15166 series is the
only tested-and-published part that clears 100,000 cycles with real margin, and the price
is a flat-cable connector on a board that is already tight.

**Either way, this is a bench item.** A carriage, a motor, a cam and an evening gets you
to 100,000 cycles at a few hertz in about seven hours of unattended running. That is the
only number that will actually be true of your cable, in your loop, at your travel. It is
worth doing before the mechanical design commits.

> **Volume footnote.** Unbranded modules are a real dead end at sixty units — no
> continuity of supply, no datasheet control. The production answer is the sensor on the
> motion board. The cable question does not go away and gets worse at volume.

### K. Knob encoder — this one genuinely has to be custom

**No AEDR-8300 breakout exists.** Checked Broadcom's own pages for all eight
AEDR-8300 variants — every one is a bare component page with no evaluation or development
board — plus Farnell, Mouser, DigiKey and hobbyist sources. Nothing.
[Broadcom AEDR-8300-1W2](https://www.broadcom.com/products/motion-control-encoders/incremental-encoders/reflective-encoders/aedr-8300-1w2)

Confirmed from the [datasheet](https://www.farnell.com/datasheets/2345337.pdf), which
matches the design as drawn:

- **Recommended gap to the code strip: 1.0 / 2.0 / 2.5 mm, with 2.0 mm the typical value.**
- **Series resistor for the emitter: 220 Ω ±10 % at 5 V** (110 Ω at 3.3 V). Your figure
  is right, and putting it on this board is right — it keeps the emitter's current out of
  the cable.
- Supply 3.0–5.5 V. Resolution 212 lines per inch. Recommended optical radius for a
  curved code strip: 11 mm.
- **The package's outline dimensions could not be extracted from the datasheet text.** The
  drawing is there; the numbers need reading off it by eye. Flagged as not confirmed
  rather than not published.

Stock and price: **£8.10 ex VAT at Farnell UK** per `FUNCTION-ALLOCATION.md`, with a
14-week lead time on reorder. Newark lists 1,163 units at £9.37.

**So: one custom board, and it is the right one to be custom.** It carries a leadless
optical part that has to sit at a controlled 2.0 mm from a code ring, on a printed shim,
at a defined radius. That is a board whose whole job is dimensional precision. A breakout
would not have helped even if one existed.

> **Volume footnote.** No dead end — this board is in the production design already. The
> 14-week reorder lead time on the sensor is the thing to watch: order the sixty-unit
> quantity of AEDR-8300 far earlier than feels necessary.

---

## 6. Part three — wiring

### L. The harness — and an argument against spending £460

Three findings first, each of which changes the answer.

**Finding one: Molex Pico-Lock 1.50 right-angle headers are surface-mount only.** There is
no through-hole right-angle part in the 504050 series. If any board in the design assumed
a through-hole right-angle header, it has to become surface-mount or vertical. That is a
message for the board layouts, not for the harness.
[Molex product specification](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/504/504051/5040511001-PS-000.pdf)

The confirmed part families, all buyable singly in the UK:

| Function | Series | Example | Price |
|---|---|---|---|
| Right-angle surface-mount header | **504050** | 504050-0491 (4 way) | from £1.13, Farnell |
| Receptacle housing | **504051** | 504051-0201 (2 way) | singly at Farnell/RS |
| Crimp terminal, **24–28 AWG** | **504052-0098** | — | **£0.12**, minimum order 1 |

**Finding two: pre-crimped Pico-Lock leads are not a stocked UK item.** Farnell, RS,
Heilind and TME all stock loose terminals, housings and headers, and none stock
pre-crimped leads. Molex does run an **off-the-shelf discrete-wire cable assembly** line
for Pico-Lock — 2 to 12 circuits, 50 to 600 mm, straight-through pin mapping, listed at
both DigiKey and Mouser — but it only helps where a stock length and a one-to-one pinout
happen to suit. Neither distributor's marketing page yields part numbers or prices to an
automated fetch; **it needs a live parametric search on their sites**, and it is the first
thing worth ten minutes.
[DigiKey](https://www.digikey.co.uk/en/product-highlight/m/molex/pico-lock-off-the-shelf-ots-discrete-cable-assemblies) ·
[Mouser](https://www.mouser.com/en/new/molex/molex-pico-lock-assemblies)

Outside Molex's own line there is no ready-made Pico-Lock cable market at all. It is an
industrial part; the hobbyist ecosystem never adopted it.

**Finding three: only the official tool is confirmed to crimp the terminal.**
**Molex 63827-0800, £459.60 ex VAT, 4 in stock at Farnell UK**, explicitly specified for
*"Molex Pico-Lock 504052 Series 28-24 AWG Contacts"*.
[Farnell](https://uk.farnell.com/molex/63827-0800/hand-crimp-tool-1-50mm-pitch-pico/dp/2428561)
Every cheaper tool — Engineer PA-09 and PA-21, the IWISS SN and IWS ranges — makes a
generic claim ("suits Molex, JST, JAE", "100 terminal types") with **no named Pico-Lock
validation anywhere**. For a latched, current-carrying connector where a marginal crimp
produces exactly the intermittent fault you described, those are a gamble, not a fit.

**What to actually do.** The Pico-Lock decision in `CONNECTORS.md` was made for a
sixty-unit build, and it is still right for one. But **£460 of tooling to make twenty
leads once is the wrong shape of spend.** At sixty units it is about 1,200 crimps and the
tool costs 38 pence a crimp. At one unit it costs £23 a crimp.

So split the harness by what each run actually needs:

- **Signal runs — light sensor, encoders, sensors, anything under an amp.** Use
  **pre-made JST GH cables**, which are buyable pre-crimped in the UK from Flying Tech
  among others. GH has a real positive latch — *"large outer latch for positive lock"* —
  and is rated 1.0 A on 26 AWG. That is ample for signals, and it does not break the rule
  that made Pico-Lock the choice, because the rule was about latching and current, and GH
  satisfies latching. [JST GH datasheet](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)
- **Power runs — the three board feeds, the motor phases, the halo.** These are the few
  that need 2 A and 24 AWG, and there are perhaps five or six of them out of twenty. For
  one prototype, **solder them directly and heatshrink them.** A soldered joint is more
  reliable than a hand crimp made with an unvalidated tool, and the object is going to be
  opened by one person who knows what is inside it.
- **In parallel, get a quote.** Ask a UK harness house for the full Pico-Lock set now. It
  costs an email and the answer is the input to the production decision. **Jacarem** state
  outright *"we can assist with prototypes, pre-production and production quantities"*.
  [Jacarem](https://jacarem.co.uk/cable-assemblies/) Others worth including: GTK, St Cross
  Electronics, Agile Electronics. None publishes a minimum order — that is normal, and it
  means asking is the only way to know. Molex's own Custom Cable Creator, hosted through
  DigiKey and Mouser, is a web form worth filling in for comparison; its minimum order is
  **not published**.
- **Buy the tool only if** the harness house quote comes back worse than £460, or its lead
  time kills the build. Then it is justified, and it will be justified anyway at sixty.

**The risk nobody has written down: 30 mating cycles is the specification, not a floor.**
`CONNECTORS.md` §3 rejected Pico-EZmate for having 10 cycles and chose Pico-Lock for
having 30. Thirty is still a small number against first article, rework, firmware
bring-up, fit checks and service. Plan on replacing the receptacles at least once during
development, and buy spare housings and terminals now while you are ordering.

> **Volume footnote.** The Pico-Lock choice does not dead-end — it is the right family at
> sixty units, made by a harness house with proper tooling. What dead-ends is
> hand-crimping, which is why the quote matters more than the tool.

### M. Chassis bonding and the knob's bleed contact

**M1 is trivial.** All next-day from Farnell or RS, under £10 for the lot:

| Part | Supplier | Price |
|---|---|---|
| M3 external-tooth star washer, DIN 6797A | [RS 276-847](https://uk.rs-online.com/web/p/washers/0276847) | £4.78 / 250 |
| M4 external-tooth star washer | [RS 276-869](https://uk.rs-online.com/web/p/washers/0276869) | £4.93 / 250 |
| M3 ring terminal, 22–24 AWG | Farnell | ~£1.73 / 100 |
| 1 MΩ resistor, through hole, 0.25 W | Farnell | £0.029 each |

**M2 is the real question, and the honest answer is that no catalogue part exists for it.**

Nothing is sold as "a light static-bleed contact for a rotating knob". What exists:

| Option | Spring force published? | Verdict |
|---|---|---|
| **Mill-Max low-force spring pins** (0965/0975, 0933/0992) | **Yes — 45, 55 and 80 g**, against a 60–120 g catalogue default | The only published force found anywhere. A real candidate |
| Harwin S-series spring contacts | **No** — only free and working heights | Cannot design a "must not be felt" requirement against an unpublished number |
| Keystone battery contacts | **No** | Wrong duty — they hold a cell still, they do not wipe |
| **Phosphor-bronze / beryllium-copper finger stock** | **No — and that is the point.** Force is set by how you cut and form it | Sold as strip by UK shielding suppliers: **Kemtron** (Braintree), **OSCO**, **NTD Shielding** |
| Shaft-grounding brushes (Helwig) | No, at small sizes | Conceptually exactly this job — but sized for machine shafts, not a knob |
| Miniature slip rings | Not applicable | A full rotary joint. Needs a shaft through it, not a rim to touch. Over-engineered |

**The arithmetic that settles it.** Take the Mill-Max low-force figure of 45 g, which is
0.44 N, and a friction coefficient of about 0.4 for a plated tip on aluminium:

| Contact radius | Drag torque | As a fraction of a 60–150 mN·m detent |
|---|---|---|
| 10 mm | ~1.8 mN·m | **1.2 – 3 %** |
| 20 mm | ~3.5 mN·m | 2.3 – 6 % |
| 30 mm (near the rim) | ~5.3 mN·m | **3.5 – 9 %** |

So `GROUNDING.md` §5's instruction to mount it at the smallest radius available is not a
nicety — **it is a factor of three in perceived drag.** At 10 mm radius and half a newton,
the contact costs about two per cent of the detent torque, which will not be felt. At the
rim it is approaching a tenth, which will be.

**Recommendation: a hand-formed phosphor-bronze or beryllium-copper leaf, riding at the
smallest radius the mechanics allow, with a design target of under 0.5 N normal force and
under 2 mN·m of drag.** Buy finger stock from Kemtron, OSCO or NTD and form it. Two
reasons to prefer a leaf over a pin: a leaf presents a curved wiping surface to a rotating
part, where a pin's tip ploughs a track and can chatter; and the leaf's force is tunable
by hand against the actual knob, which is the only way this gets settled anyway.

**Keep a Mill-Max 45 g low-force pin in the drawer as the fallback**, because it is the
one option with a number on it, and if the leaf proves fiddly to make repeatable the pin
gives you a known force.

> **Volume footnote.** A hand-formed leaf is a genuine dead end at sixty units — sixty
> hand-formed leaves is sixty different forces. At production it becomes a stamped part
> or a specified spring pin. Prove the geometry by hand first; the production part follows
> from a form that is known to work.

---

## 7. The custom residue

**Two boards are genuinely custom: K, the knob encoder, and G, the USB-C receptacle.**

That is it, provided the Mill-Max pre-wired pogo block's spring force turns out to be
tolerable and the motion-board exercise settles J. And G disappears too if a
microcontroller with an edge-mounted USB-C socket measures up — see §5.

**One panelised set, or separate pieces?** Separate designs, one fabricator order.

- **Not one physical panel.** The two boards have different thicknesses, different
  mountings and different orientations, and K will very probably want a second revision
  after the optical gap is measured. A shared panel couples their revision cycles for no
  benefit and has to be snapped apart afterwards.
- **But one order.** Most prototype fabricators run several distinct outlines under a
  single job. Two designs, five of each, one stencil covering both, one shipping charge —
  about £15 all in. Ordering the second board a fortnight later costs another shipping
  charge and another week.
- **Five of each.** At these outlines five boards cost about the same as one.
- **Keep K a single design with one outline**, so the sensor's position relative to the
  mounting features is exact and unarguable.

**What was deleted:** the 3.5 mm jack's carrier board (H), the vibration actuator's pogo
board (I), the light sensor board (F), and the whole USB arbitration question (E). Four of
the six lines behind *"small boards — no briefs written"* close without a board being
designed, and a fifth may yet.

---

## 8. What to buy this week

It is not one order — it is six suppliers, because the parts genuinely live in different
places. Grouped, with the two that need a decision first marked.

**The Pi Hut** — one order, next day, about £16 inc. VAT

| Item | Part | Price |
|---|---|---|
| F | [Adafruit VEML7700 light sensor](https://thepihut.com/products/adafruit-veml7700-lux-sensor-i2c-light-sensor-ada4162) | £4.80 |
| E, G | [Seeed XIAO RP2350](https://thepihut.com/products/xiao-rp2350-raspberry-pi-rp2350) — the prototype's USB device, and possibly the external socket too. Measure its thickness | £4.80 |
| E | Raspberry Pi Pico 2 — the fallback USB device if the XIAO does not fit | £3.60 |
| — | STEMMA QT cable assortment, for F and anything else on that bus | ~£5 |

**TME** (ships to the UK) — item A

| Item | Part | Price |
|---|---|---|
| A | Mean Well **GSM60B12-P1J**, Class II, touch current < 50 µA | ~£18 |

**Farnell UK** — one order

| Item | Part | Price |
|---|---|---|
| K | Broadcom **AEDR-8300-1W2** — order **three**, the 14-week reorder lead is the risk and it is a leadless part you will be reflowing for the first time | £8.10 ex VAT each |
| K | 110 Ω resistors — **110 Ω, not 220 Ω**, because the encoder board runs at 3.3 V. See `BOARD-KNOB-ENCODER.md` §4.5 | pence |
| M | 1 MΩ resistors, 0.25 W | £0.03 each |
| L | Pico-Lock samples: 504050 headers, 504051 housings, 504052-0098 terminals — a handful of each, to have the parts in hand while the harness question is settled | £30–60 |

**RS Components** — item M

| Item | Part | Price |
|---|---|---|
| M | M3 and M4 external-tooth star washers | £9.71 for both packs |
| M | M3 ring terminals, 22–24 AWG | ~£2 |

**Mouser** — item I

| Item | Part | Price |
|---|---|---|
| I | Mill-Max **867-22-002-70-501010** pre-wired two-position spring block | $11.93 |

**Flying Tech** — item C, one order

| Item | Part | Price |
|---|---|---|
| C | [Hobbywing UBEC-5A (2-8S)](https://www.flyingtech.co.uk/product/hobbywing-5a-2-8s-ubec-with-5-0v-6-0v-7-4v-output/) — 5 A continuous, 15 A peak | £12.90 |
| C | [Generic 2-13S 5 V 5 A module](https://www.flyingtech.co.uk/product/voltage-regulator-module-2-13s-5v-5a-bec/) — the better envelope fit, half the price | £6.90 |

*Buy both and bench them against each other. Together they cost less than one Pololu.*

**A fabricator** — items K and G

| Item | Part | Price |
|---|---|---|
| K, G | Two board designs, five of each, plus one stencil covering both, 1.0 mm thick | ~£25 |
| G | GCT USB4520-03-0-A mid-mount receptacle, or [USB4085-GF-A at £0.81](https://uk.farnell.com/gct-global-connector-technology/usb4085-gf-a/usb-conn-2-0-type-c-r-a-rcpt-16pos/dp/2924867) | ~£2 |

**HiFi Collective** — item H

| Item | Part | Price |
|---|---|---|
| H | Black nylon 3.5 mm stereo panel-mount jack | £1.24 + VAT |

**Send the same day, costing nothing:**

- The **harness quote** to Jacarem, GTK, St Cross and Agile — twenty Pico-Lock assemblies,
  one set. This is the only item on the list with a multi-week clock and it is free to start.
- An email to **Mill-Max** asking for the 867 series' spring force at mid-stroke.
- An enquiry to **Kemtron, OSCO or NTD** for a small piece of phosphor-bronze or
  beryllium-copper finger stock.

**Do first, before spending:** the twenty-minute Pi 5 device-mode check in §4. It decides
whether the microcontroller line above is essential or merely useful, and it decides
whether the external USB-C socket needs its own board at all.

**Total, roughly £215 including the Pico-Lock samples, both converters and both boards.**

---

## 9. What could go wrong

**E — the Pi 5 finding could be wrong.** Raspberry Pi publishes no schematic for the Pi 5,
so the "no data on the USB-C socket" conclusion rests on the product brief and the RP1
architecture rather than on a drawing. If it is wrong, the parallel-supply problem returns
and the answer is the cut VBUS conductor plus the sense line, not the ideal diode.
**Mitigation: do the bench check before redesigning.** Either way the microcontroller
route is not wasted — it is where production is going.

**E, second order.** If the Pico 2 becomes the host interface, the object gains a second
processor that has to be flashed, versioned and kept in step with the Pi. That is a real
software cost that this hardware decision creates, and `SOFTWARE-HID-CONTRACT.md` is where
it lands. Flagging it rather than pretending it is free.

**J — the cable.** This is the item with the least evidence behind it. No vendor publishes
a flex life at 2.4 mm of travel, the recommendation is reasoning from fatigue mechanics
rather than a tested number, and the failure mode is an intermittent sensor fault on a
carriage that moves every time the clutch operates. That is the hardest fault in the
product to diagnose. **Mitigation: build the cycling rig.** Seven hours unattended gets you
to 100,000 cycles. It is the cheapest certainty available anywhere in this document.

**J, second.** The MT6701 module is unbranded. It may not be the same part next month,
and there is no datasheet control. Buy two now.

**L — the harness.** Three ways this bites. The Molex off-the-shelf assemblies may not
come in a length or pinout that suits, and that is only knowable from a live parametric
search. The harness houses may all come back with a setup charge that makes the £460 tool
look cheap. And **30 mating cycles will be consumed during development** — that is not a
risk, it is a certainty, so buy spare housings and terminals with the first order.

**A — the leakage figure.** The GSM60B12's "< 50 µA" needs a human to look at the PDF and
confirm the µ symbol, because two text extractors dropped it. And its Class II status is
inferred from the inlet type and the absence of an earth-leakage line, not stated in
words. If that matters more than stock, the XP Power AMF60US12-P says it in plain English
and costs twenty weeks.

**C — the still-air number.** Nobody publishes it at any price, which is why the expensive
part was not worth buying. **This number has to be measured**, and it belongs with
`THERMAL-PLAN.md`'s Test B rather than being carried as an assumption. The second risk is
that the radio-control parts' continuous ratings assume some airflow through a fuselage,
where this object is sealed and bolted to metal — conduction to an aluminium plate is a
better thermal path than still air, so this is probably favourable, but it is an inference
and not a vendor claim. The bench test in `SMALL-PARTS-ORDER-LIST.md` §7 is what settles both.

**G — the aperture, and a lesson about which dimension governs.** The first draft of this
document recommended a panel-mount lead that cannot fit, because it checked the connector
against the object's 36 mm height rather than against the 8 mm of port face below the halo.
The corrected answer is in §5. The lesson worth keeping: **on this object the governing
dimension is almost never the overall one.** It is whatever band of the height stack the
part actually has to live in, and `V13.md` lists every one of them.

**G, second.** If the microcontroller route is taken, the connector's mechanical loads go
into that small board and its mounting rather than into the chassis. Somebody will
eventually pull the cable sideways. A printed collar around the socket, taking the load
before the solder joints do, is the standard answer and it needs designing in — not added
after the first one breaks.

---

## 10. What this changes in the other documents

| Document | Change |
|---|---|
| `SOURCING-BOM.md` | The *"small boards — no briefs written"* line is replaced by the table in §2. Add the GSM60B12-P1J with its touch-current figure; delete the GST60A/GSM60A candidates as Class I |
| `GROUNDING.md` §2 | The Class II requirement stands, but the named candidate parts were Class I. Record the three verified Class II candidates and the reason |
| `GROUNDING.md` §5 | The knob's sprung contact gets a design target: under 0.5 N normal force, under 2 mN·m of drag, mounted at the smallest radius available. The arithmetic is in §6 above |
| `GROUNDING.md` §6 | Add the second rule: no metal fixing may bridge the 3.5 mm jack's shell to chassis. The plastic port face is necessary but not sufficient |
| `SYSTEM-REVIEW.md` §3.2 | **Revise.** The parallel 5 V source hazard is deleted, not solved, if the Pi 5 finding holds. The cut-VBUS cable specification is superseded |
| `FUNCTION-ALLOCATION.md` | Remove the USB-C data and power splitter (£3) — it addresses a Pi 4 problem. The bench item *"Pi as a USB keyboard, mains-powered, through the splitter"* becomes *"confirm the Pi 5 cannot do device mode, then move it to the Pico 2"* |
| `SOFTWARE-HID-CONTRACT.md` | The host interface moves to a microcontroller for the prototype. The contract now spans two processors |
| `CONNECTORS.md` §4 | Note that Pico-Lock 1.50 right-angle headers are **surface-mount only**; there is no through-hole right-angle part. Exception 3 gains its mechanical requirement: the actuator needs a pocket that reacts about 1 N of pin force |
| `THERMAL-PLAN.md` | Add the converter's still-air current at the real internal ambient to Test B. It is not published by any vendor |
| `V15-SPECIFICATION.md` §4.9 | **The USB-C receptacle board stays.** No panel-mount USB-C part fits the 8 mm band below the halo — record that, so it is not revisited. The aperture is the connector's own shell, about 9 × 3.5 mm |
| `V15-SPECIFICATION.md` | The converter envelope becomes **35 × 19 × 7.8 mm** (the generic module) or **50 × 17 × 10 mm** (the Hobbywing) — the second is 12 mm longer and 2 mm taller than the model allows, so the bench test decides a CAD change too. The light sensor needs ~17 mm of clear panel behind its 4.8 mm hole, not 5 mm; the 3.5 mm jack needs a 6.3 mm hole in a 3 mm-thick local boss |
| `BOARD-KNOB-ENCODER.md` | New document. The encoder board is specified there; its emitter resistor is **110 Ω**, not 220 Ω |
| `DECISIONS.md` | Index this |

**Still open, deliberately:** whether the Pi 5 can do USB device mode (one bench check);
the flex cable, pending the cycling rig; the harness route, pending quotes; item J,
pending the motion-board exercise; and the converter's real still-air rating, pending
Test B.
