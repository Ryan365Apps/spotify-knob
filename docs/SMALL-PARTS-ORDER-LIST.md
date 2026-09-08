# the 60 — the order list for the small parts

**Date: 8 September 2026. Companion to `SMALL-PARTS-SOURCING.md`**, which carries the
reasoning, the sources and the rejected options. This document is for buying. Every line
says what the part does in plain words, what it costs and where it comes from.

**Prototype quantity: one of everything unless a line says otherwise.**

---

## 1. Do these three things first — they change what you buy

| # | Do this | Takes | What it decides |
|---|---|---|---|
| 1 | **The Pi 5 device-mode check.** Set up `dwc2` and `libcomposite` on the Pi 5 exactly as the Pi 4 recipe describes, plug the Pi's own USB-C socket into a computer, and see whether anything appears | 20 min | Whether the external USB-C socket goes to the Pi or to a microcontroller. Changes basket B and basket F |
| 2 | **Look at the Mean Well GSM60B12 datasheet** and confirm the touch-current line reads "< 50 µA" | 2 min | Whether the power supply in basket A is the one to buy |
| 3 | **Ten minutes on DigiKey's Pico-Lock parametric search**, filtered to off-the-shelf cable assemblies | 10 min | Whether the harness needs hand-crimping at all. Changes basket E |

Everything else can be ordered today without waiting.

---

## 2. The baskets

Seven suppliers. Work down them in order; A and C are the long poles.

### Basket A — the power chain — **TME** (Poland, ships to the UK)

| ✓ | What it is, in plain words | Part | Qty | Price |
|---|---|---|---|---|
| ☐ | **The mains brick.** Turns mains into 12 V, 5 A. Two-pin, no earth pin, so the object's metal knob and rim never get a second earth reference and the audio circuit cannot hum. Its datasheet publishes a touch-current figure of under 50 microamps, which is the number that decides whether a damp hand feels anything | Mean Well **GSM60B12-P1J** | 1 | **~£18** |

*Why TME and not Mouser: Mouser flags this part as business-customers-only for UK and EU
buyers. TME shows 219 in stock and no such restriction.*

*Buy a generic figure-of-eight mains lead with a UK plug at the same time if you have not
got a spare — the brick ships without one. Any "kettle lead, figure 8" from Amazon or CPC,
about £4.*

**⚠ This part decides the DC plug size.** The GSM60B12 has a 5.5 mm outer / 2.1 mm inner
plug, which fits the PJ-063AH inlet already in the model. Both XP Power alternatives have
2.5 mm inner plugs and would need a different inlet. Do not substitute without checking.

---

### Basket B — the small bought boards — **The Pi Hut** (UK, next day)

| ✓ | What it is, in plain words | Part | Qty | Price |
|---|---|---|---|---|
| ☐ | **The room-brightness sensor.** Sits behind the 4.8 mm hole in the rear port face and tells the display and the halo how bright the room is. Comes with connectors at both ends, so no crimping and no soldering | Adafruit VEML7700, product 4162 | 1 | **£4.80** |
| ☐ | **The thing that talks to the computer.** If the Pi 5 cannot present itself as a USB device — see check 1 above — this microcontroller does it instead, appearing to the computer as a keyboard while the Pi drives everything else | Raspberry Pi Pico 2 | 2 | **£7.20** |
| ☐ | **Ready-made sensor cables.** Latching four-way cables for the light sensor and anything else on the same two-wire bus. Buying these is how you avoid crimping twenty leads by hand | STEMMA QT / Qwiic cable assortment | 1 set | **~£5** |

**Basket B total: about £16 including VAT.**

**⚠ The external USB-C socket is not in this basket, and the earlier recommendation was
wrong.** The Adafruit panel-mount lead needs a 21.5 to 27 mm round hole; even its small
sibling needs 12 mm. **The port face has about 8 mm of height below the halo** — the halo
band starts at z 8.0 and the receptacle sits at z 0.1–3.3. **No panel-mount USB-C part
made by anybody fits that**, round or rectangular; the smallest rectangular flange found
anywhere is 21.5 × 12.5 mm. The socket goes back to a small board behind an aperture, as
the design already had it — see basket G.

**Optionally add a small microcontroller with a USB-C socket on its edge**, which would
serve as both the host interface and the external socket in one part:
[Seeed XIAO RP2350](https://thepihut.com/products/xiao-rp2350-raspberry-pi-rp2350),
21 × 17.5 mm, **£4.80, in stock at The Pi Hut.** See basket G.

---

### Basket C — the encoder and the passives — **Farnell UK** (next day)

This is the basket with the long lead time hidden in it.

| ✓ | What it is, in plain words | Part | Qty | Price |
|---|---|---|---|---|
| ☐ | **The knob's position sensor.** A reflective optical part the size of a grain of rice that watches a striped ring on the underside of the knob and reports how far it has turned. This is what the motor renders the detents against | Broadcom **AEDR-8300-1W2** | **3** | £8.10 ex VAT each = **£24.30** |
| ☐ | **The emitter's current-setting resistor.** Sets the sensor's internal light source to 15 milliamps. Lives on the encoder board so the cable carries a steady supply rather than a switched current | 110 Ω ±1 %, 0402 or 0603 | 10 | pence |
| ☐ | **The sensor's decoupling capacitor** | 100 nF, 0402 or 0603, X7R | 10 | pence |
| ☐ | **The static bleed resistor.** Drains charge off the metal knob to chassis slowly, without giving a static discharge a fast path into the boards | 1 MΩ, 0.25 W, through hole | 5 | £0.03 each |
| ☐ | **Connector samples.** Enough of the chosen harness family to have the parts in hand while the crimping question is settled — see basket E | Molex 504050 headers, 504051 housings, 504052-0098 terminals; a handful of each in 2, 4 and 6 way | — | **£30–60** |

**Basket C total: about £60–90 ex VAT.**

**⚠ Buy three of the encoder, not one.** Farnell quote a **14-week lead time on reorder**.
It is a leadless part that has to be reflowed, you will be soldering it yourself onto a
board you have not made before, and a spare costs eight pounds against a fourteen-week
wait. This is the single most order-early item on the whole list.

---

### Basket D — the fasteners and bonding hardware — **RS Components** (next day)

| ✓ | What it is, in plain words | Part | Qty | Price |
|---|---|---|---|---|
| ☐ | **External-tooth star washers, M2.5** (every former M3 fixing is M2.5 since 8 Sep). Bite through any surface finish to make a bond you can inspect, rather than a screw that happens to conduct. These are what make the steel rim ring and the aluminium plate actually one conductor | RS PRO, DIN 6797A, M2.5 | pack | **£4.78 / 250** |
| ☐ | **The same in M4** | RS PRO, DIN 6797A, M4 | pack | **£4.93 / 250** |
| ☐ | **Ring terminals.** For the chassis bond wire | M2.5 stud, 22–24 AWG | 10 | ~£2 |

**Basket D total: about £12.**

---

### Basket E — the harness — **decision, not a purchase yet**

Do not buy the tool this week. The reasoning is in `SMALL-PARTS-SOURCING.md` §6; the
short version is that £460 of tooling to make twenty leads once costs £23 a crimp, and it
only becomes sensible at sixty units.

| ✓ | Do this | Where | Cost |
|---|---|---|---|
| ☐ | **Run the parametric search** for Molex Pico-Lock off-the-shelf cable assemblies. If a stock length and pinout fit, several of the twenty leads are solved with no tooling at all | DigiKey UK, Mouser UK | £0 to look |
| ☐ | **Order pre-made latched signal cables** for everything under one amp — sensors, encoders, the two-wire bus. A latch and one amp is all a signal run needs | JST GH pre-made sets, Flying Tech UK | ~£15 |
| ☐ | **Email four harness houses** for a quote on twenty Pico-Lock assemblies, one set. Free, and the answer is the input to the production decision | Jacarem, GTK, St Cross Electronics, Agile Electronics | £0 |
| ☐ | *Only if the quotes come back badly:* the official crimp tool. The only tool anyone confirms crimps this terminal | Molex 63827-0800, Farnell, 4 in stock | £459.60 ex VAT |

**For the five or six runs that actually carry current** — the three board feeds, the motor
phases, the halo — solder them directly and heatshrink them for the prototype. A soldered
joint beats a hand crimp made with an unvalidated tool, and you are the only person who
will ever open this unit.

**⚠ Buy spare housings and terminals now.** The chosen connector is rated for **30 mating
cycles** and development will use them up. That is not a risk, it is arithmetic.

---

### Basket F — the odds and ends — four small suppliers

| ✓ | What it is, in plain words | Part | Supplier | Price |
|---|---|---|---|---|
| ☐ | **The 12 V to 5 V converter.** Everything inside runs on 5 volts. Converting inside the object rather than outside it is what lets the brick's lead stay thin — at 5 volts and seven amps that lead would lose nearly half a volt | **Hobbywing UBEC-5A (2-8S)** — 5 A continuous, 15 A peak, 50 × 17 × 10 mm | [Flying Tech](https://www.flyingtech.co.uk/product/hobbywing-5a-2-8s-ubec-with-5-0v-6-0v-7-4v-output/) | **£12.90** |
| ☐ | **The same job, cheaper and a better mechanical fit.** Buy both and bench-test them against each other — together they still cost less than one Pololu | Generic **2-13S 5 V 5 A** module — 5 A continuous, **35 × 19 × 7.8 mm**, which fits the envelope almost exactly | [Flying Tech](https://www.flyingtech.co.uk/product/voltage-regulator-module-2-13s-5v-5a-bec/) | **£6.90** |
| ☐ | **The vibration actuator's contacts.** Two spring-loaded pins in a moulded block with wire already attached, so the actuator is contacted by pressure instead of solder. Its maker warns that soldering to it lifts the adhesive | Mill-Max **867-22-002-70-501010** | Mouser | **$11.93** |
| ☐ | **The headphone socket.** A nylon-bodied panel jack. The nylon is the point: this socket's shell is the audio circuit's only reference to the outside world, and if it touches the chassis the object hums | Black nylon 3.5 mm stereo panel jack | HiFi Collective | **£1.24 + VAT** |
| ☐ | **The motor rotor sensor.** Reads a magnet on the motor shaft. No reputable brand makes a board for this chip, so an unbranded module is the only option — buy two, because it may not be the same part next month | Generic MT6701 module, the 15 × 17 mm version if you can identify it | Amazon UK or eBay UK | **~£12 for two** |

**Basket F total: about £43.**

**⚠ On the converter — the earlier £30 recommendation was not defensible.** These are
switching regulators from the radio-control world, built to run continuously inside a
sealed model with no airflow, which is this use case exactly. The Hobbywing states a real
**5 A continuous / 15 A peak** split, which is the thing that actually covers the transient
when the Pi, the display, the motor and the halo peak together; the £6.90 part states 5 A
continuous and fits the envelope. **Buy both, at £19.80 the pair, and settle it on the
bench** — the test is in §6. Note also that the Traco part with the best published thermal
data in the whole survey is a 3 A part with no burst rating, so it would have failed the
peak requirement outright. Spending more money was not buying more certainty here.

**⚠ Hold the MT6701 if the motion-board exercise is close to reporting.** If it recommends
a bought board that already carries a rotor sensor, this line disappears. One module for
bench work is worth having regardless.

---

### Basket G — the encoder board — **a fabricator, once the design is done**

See `BOARD-KNOB-ENCODER.md` for what goes on it.

| ✓ | What it is | Where | Price |
|---|---|---|---|
| ☐ | **Five copies of the encoder board**, 1.0 mm thick, two layer | JLCPCB, PCBWay or Aisler | **~£10 for five** plus shipping |
| ☐ | **Five copies of the USB-C receptacle board** — a GCT USB4520 mid-mount and four solder pads, about 10 × 10 mm. Put it in the same fab order as a second design; most fabricators run several outlines under one job, so the marginal cost is a few pounds and no extra shipping | Same order | **~£5** |
| ☐ | **A stainless steel solder-paste stencil** covering both designs. The encoder is a leadless part with its pads underneath — it cannot be soldered with an iron | Same order | **~£8** |
| ☐ | Low-temperature solder paste, if you have not got any | Amazon UK or Farnell | ~£15 |
| ☐ | **The USB-C receptacle itself** | GCT **USB4520-03-0-A**, or USB4085-GF-A at £0.81 from [Farnell UK](https://uk.farnell.com/gct-global-connector-technology/usb4085-gf-a/usb-conn-2-0-type-c-r-a-rcpt-16pos/dp/2924867) | ~£1–2 |

**The alternative worth measuring first.** If the Pi 5 device-mode check comes back
negative, the host connection moves to a microcontroller anyway — and a **Seeed XIAO
RP2350 (21 × 17.5 mm, £4.80, in stock at The Pi Hut)** has a USB-C socket on its own edge.
Mounted behind the port face aperture, it would be the external socket, the host interface
and the internal lead all at once, and this board would not need to exist.

**What to measure:** the XIAO's overall height and where its socket's axis sits above the
board. The design needs that axis at about **z 2.5**, with the receptacle inside z 0.1–3.3.
Seeed do not publish the board thickness, so this is a callipers question, not a datasheet
one. £4.80 to find out.

---

## 3. What you are deliberately not buying

| Item | Why not |
|---|---|
| **USB-C data and power splitter, £3, The Pi Hut** | It solves a Raspberry Pi 4 problem. The Pi 5's USB-C socket appears to carry no data at all, so there is nothing to split |
| **An ideal-diode board for the 5 V feed** | It would keep the computer's port live as a second supply, so with the mains off the object would try to run from a laptop port that cannot give seven amps. That fails as an intermittent brown-out, which looks like a software fault |
| **A power distribution board or bus bar** | The star point is already a copper pour and a connector on the carrier board. Nothing bought earns its space |
| **A USB-C receptacle board (item G's custom board)** | Deleted by the panel-mount lead in basket B |
| **A 3.5 mm jack carrier board** | Deleted by the panel jack in basket F |
| **A pogo-pin board for the vibration actuator** | Deleted by the pre-wired Mill-Max block in basket F |
| **A light sensor board** | Deleted by the Adafruit breakout in basket B |
| **The Molex crimp tool, this week** | See basket E |

---

## 4. Free, and send them today

Each of these costs an email and has a clock on it.

| ✓ | Send to | Asking for |
|---|---|---|
| ☐ | **Jacarem, GTK, St Cross Electronics, Agile Electronics** | A quote for twenty Molex Pico-Lock 1.50 mm cable assemblies, one set, prototype quantity. Jacarem state outright that they take prototype volumes |
| ☐ | **MELTEC, PWB Encoders, Laser Lab, Optry Tech** | A quote for the code ring. The specification to send them is in `BOARD-KNOB-ENCODER.md` §6 — it is a complete, quotable spec, so this can go today |
| ☐ | **Mill-Max** | The spring force at mid-stroke for the 867-22-002-70-501010. It is not published, and it is the number that decides whether the actuator needs a mechanical pocket |
| ☐ | **Kemtron, OSCO or NTD Shielding** | A small piece of phosphor-bronze or beryllium-copper finger stock, for the knob's static bleed leaf |

---

## 5. The total

| Basket | Supplier | Roughly |
|---|---|---|
| A | TME — the mains brick | £22 |
| B | The Pi Hut — the bought breakouts | £16 |
| C | Farnell — the encoder, passives, connector samples | £75 |
| D | RS — washers and terminals | £12 |
| E | Signal cables only, this week | £15 |
| F | Flying Tech, Mouser, HiFi Collective, Amazon | £43 |
| G | Fabricator — two board designs, five of each, and a stencil | £30 |
| | **Total** | **about £215 including VAT and shipping** |

The £460 crimp tool sits outside that, deliberately, until the harness quotes come back.

---

## 6. If you only do one thing this week

**Order basket C.** The encoder is the only part on the list with a fourteen-week clock on
a reorder, it is the one genuinely custom board, and everything about the knob's feel
depends on it working.


---

## 7. The converter bench test

Two modules, £19.80 the pair. This settles which one stays, and it is the only way to get
a still-air number, because no vendor in this class publishes one.

1. **Mount the candidate on the actual aluminium plate**, through the thermal gap pad, in
   the actual object or as close a mock-up as you have. Warm room, about 25–30 °C.
2. **Hold 3 A for an hour.** Track the case and plate temperature with a stuck-on sensor.
   **Pass:** the temperature curve flattens, and the output stays between 4.9 and 5.1 V.
   **Fail:** still climbing after an hour, or the output has sagged.
3. **Superimpose a 6 A pulse for 500 ms, every few seconds, for several minutes.** A second
   load resistor switched by a transistor is enough of a rig.
   **Pass:** the output never dips below **4.75 V** — the Pi 5's brownout threshold — and
   the module does not reset or latch off.
   **Fail:** any dip below 4.75 V, a restart, or a hot smell.

Whichever module passes both, in your box, is proven for this build whatever it cost. This
also produces the still-air figure that `THERMAL-PLAN.md` Test B needs, so it is not an
extra job — it is that job, done early.
