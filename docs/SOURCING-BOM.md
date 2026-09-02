# the 60 — sourcing document for the 60-unit run

**Date:** 2026-09-02 · **Built against:** the v6a.2 mechanical model (Ø135 × 34.0 mm, described in the project note `desk-dial-p4-3.4c.md`), `docs/DECISIONS.md`, `docs/VISION.md`, `docs/PREMIUM-BOM.md` · **Quantity:** 60 units plus spares — buy 70 of anything cheap · **Buyer:** in the UK

## What this document is

Every part of the 60 that is bought rather than made, with real supplier options, prices read from supplier pages on 2026-09-02, stock and lead time, and the trade-offs. Every page used is listed under *Sources* at the end. Where no supplier publishes a number the entry says **quote required** and gives the nearest published figure as a proxy; nothing is estimated in a way that could be mistaken for a quote.

Prices are ex-VAT unless marked. Anything bought from China or the USA carries 20 % import VAT, duty on some lines, and a courier handling fee — budget roughly 25 % over the listed price on those lines. Where a dollar figure is compared with a sterling one, the conversion is approximate (about £1 = $1.33).

## Words used in this document

Plain definitions, because the rest only makes sense with them.

| Term | What it means here |
|---|---|
| **Bezel** | The rotating knurled aluminium ring the user turns. It is a deep cup: its skirt hangs down outside the base. |
| **Detent** | The click felt as the bezel steps from one position to the next. On the 60 it is made by sixty steel poles in the bezel passing six magnets on the base. |
| **Pole** | One of the sixty small steel pieces in the bezel that the magnets pull on. Currently drawn as M2.5 grub screws. |
| **Carrier** | The ring on the base that holds the six magnets and lifts ~3 mm to switch the detent off. |
| **Ring motor** | A motor shaped as a large-diameter ring so the display can sit inside it; used to push back against the hand with a force the software chooses. |
| **PCB** | Printed circuit board. A **PCB-stator motor** has its coils drawn as copper tracks on a flat board instead of wound wire. |
| **DAC** | Digital-to-analogue converter — the chip that turns digital audio into the signal a headphone hears. |
| **Encoder** | The sensor that reads how far the bezel has turned. A **reflective optical encoder** shines a light at a strip of dark and light stripes and counts them. |
| **LRA** | Linear resonant actuator — a small weight on a spring that punches back and forth, sharp enough to feel like a click. It gives event feedback, not the detent. |
| **Halo** | The ring of light at the base's lower edge, firing down onto the desk. |
| **Mid-mount USB-C receptacle** | A USB-C socket that sits in a cut-out in the board, half above and half below it, to keep height down. |
| **MOQ** | Minimum order quantity — the fewest pieces a supplier will sell. |
| **NRE** | Non-recurring engineering — a one-off charge for tooling or design, paid once regardless of quantity. |
| **Anodise** | An electrochemical finish that grows a hard, dyeable oxide layer on aluminium. **Type II** is the ordinary decorative kind. |
| **Bead blast** | Blasting the aluminium with glass beads before anodising to give a uniform matte texture. |
| **Diamond-cut** | Machining a thin skin off an already-anodised edge with a single-point tool so bright raw aluminium shows against the black — the alloy-wheel trick. |
| **V-wheel** | A small ball bearing with a V-shaped groove around its outside, running on a matching ridge. Three of them carry the bezel. |
| **N42 / N52** | Grades of neodymium magnet; the number is roughly the strength. N52 is the strongest common grade. |
| **ABEC** | A bearing precision scale; ABEC-1 is the coarsest commercial grade. |
| **Shore A** | A hardness scale for rubber; 40 is soft, 60 is a firm pad. |
| **SINAD, THD+N** | Audio measurement figures — signal-to-noise-and-distortion and total harmonic distortion plus noise. Higher SINAD and more negative THD+N are better. The audience for this product publishes these. |
| **I²S** | The digital audio wiring between the main processor and the DAC. |
| **I²C** | A two-wire control bus most small sensors and drivers use. |

## Six findings that change the design or the plan

1. **The V-wheel bearing is Ø12, not Ø10.** Every stocked "V623ZZ" wheel is 3 mm bore × **12 mm** outer diameter × 4 mm wide. A 3 × 10 × 3 open V623 exists from one US seller only. The v6a.2 model puts Ø10 × 4 wheels on posts at radius 52.9 mm running in a ridge at radius 56.4 mm — either the posts or the ridge move by about 1 mm, or the wheel becomes a plain 623ZZ bearing (3 × 10 × 4, NSK or SKF grade available in the UK) with a turned V-shaped collar pressed over it. The collar route is also the better wheel: no branded precision V-groove bearing exists in this size, only coarse-grade imports.
2. **"No catalogue ring motor" is confirmed with numbers.** Every frameless or hollow-shaft motor in the 100–135 mm outer-diameter class has a bore of 45–84 mm and is 13–35 mm tall. The motor is a custom item on every route. The cheapest credible route is a PCB-stator motor using the bezel's own magnets — but such motors give very little torque per amp, and nothing should be bought until the bench rig has measured what a Ø135 bezel actually needs. The motor is the schedule risk of the whole run.
3. **The DAC chip market has moved.** ESS parts are now stocked by Mouser UK at quantity one. The ES9219C that was assumed is **obsolete** — do not design it in. The ES9219Q (same chip, different package) is the right part: DAC, headphone amplifier and hardware volume control in one, £7.44 at 100 off. The ESP32-P4 can present itself to the PC as a USB audio device natively (Espressif's `usb_device_uac` component), so no separate USB-audio bridge chip is needed.
4. **The magnets and poles as drawn are not UK stock items.** No UK magnet seller stocks a 6 × 3 × 3 mm block; the nearest stocked exact size is in Singapore. Steel M2.5 × 2.5 mm grub screws are thin on UK stock, and an M2.5 thread has only about 2 mm of steel in its core, so the poles saturate early. Ø3 mm chrome-steel bearing balls pressed into blind holes are a stronger, cheaper and more consistent pole and should be tested on the rig alongside the grubs.
5. **Silicone does not stick to ordinary double-sided tape.** If the base pad is silicone it needs a silicone-compatible adhesive; natural rubber, nitrile or neoprene bond to standard 3M tape and grip a desk just as well.
6. **Bought parts land at roughly £230–290 per unit before the motor, the custom carrier board and assembly** (roll-up at the end), against the £130–165 in `docs/PREMIUM-BOM.md`. The earlier figure predates the DAC, the halo, the milled-groove bezel and the packaging specification; it should be retired.

## Summary table

| # | Category | Per unit | Recommended source | Unit price at run quantity | Status |
|---|---|---|---|---|---|
| 1 | Display and main board (Waveshare ESP32-P4 3.4C) | 1 | Waveshare direct, Shenzhen | $65–75 list; about £60–68 landed | 60-piece price: quote required |
| 2 | CNC aluminium bezel, 6061-T6 | 1 | JLCCNC, Xometry UK, Hubs UK instant quotes; Penta Precision (UK) | quote required | send the model this week |
| 3 | Bead blast and matte black anodise | 1 | Parallel Precision (published price) or Acorn Plating | about £4–8 plus a batch minimum | published |
| 4 | Diamond-cut bright chamfer after anodise, plus protection | 1 | the machining shop, as a second setup | quote required | sample first |
| 5 | Steel base plate Ø122 × 3, powder-coated black | 1 | Fractory, Xometry UK or LaserMaster | about £6–12 | instant quote |
| 6 | Hidden brass mass ring, laser-cut 2 mm brass | 1 | Hawkshead Metal or Metal Offcuts | about £15–17 in brass, £3–5 in steel | published proxy |
| 7 | Wheel bearings | 3 | Simply Bearings 623ZZ plus a turned V-collar | £0.25–2.60 each | finding 1 |
| 8 | Detent magnets, 6 × 3 × 3 mm | 6 | Supreme Magnets (Singapore) or K&J (USA) | $0.22–0.31 each | no UK stock |
| 9 | Detent poles (M2.5 steel grubs or Ø3 steel balls) | 60 | RS PRO or Simply Bearings | about £0.03–0.10 each | finding 4 |
| 10 | Rotation encoder and code strip | 1 | Broadcom AEDR-8300-1K2, Mouser or DigiKey | $8.01 at 100 | in stock |
| 11 | Carrier lift gearmotor | 1 | Pololu 75:1 micro gearmotor with encoder | $23.32 at 100 | in stock |
| 12 | Ring motor and its driver | 1 | custom PCB-stator or ring stator; DRV8313 or TMC6300 driver | quote required plus NRE | rig first |
| 13 | Haptic driver and actuator | 1 | TI DRV2605L plus Vybronics VLV101040A | about $6.30 | in stock |
| 14 | DAC and headphone amplifier | 1 | ESS ES9219Q, Mouser UK | £7.44 at 100 | 200 inbound, due 15 Sep |
| 15 | 3.5 mm headphone jack, threaded metal bushing | 1 | Switchcraft 35RAPC4BH3, Mouser UK | £2.39 at 100 | 15,000 in stock |
| 16 | Notification speaker, 40 mm, 8 Ω, 2 W | 1 | PUI AS04008CO-R, Mouser UK | £2.50 at 100 | in stock |
| 17 | Halo LEDs on a flexible ring board | about 40 | OPSCO SK6812SIDE-A via LCSC/JLCPCB; SK6805 RGBW reel for real white | $0.06–0.14 each plus the ring | ring: quote required |
| 18 | Opal diffuser ring | 1 | Perspex LED-diffusing opal, laser-cut (Simply Plastics) | about £3–8 | priced per cut |
| 19 | Ambient light sensor | 1 | Vishay VEML7700-TR | $1.02 at 100 | in stock |
| 20 | USB-C mid-mount receptacle | 1 | GCT USB4520-03-0-A | $0.52 at 100 | 20,000 in stock |
| 21 | Detachable braided USB-C cable, right-angle | 1 | ByteCable or WJW custom (MOQ 100), or Anker A81L6 | $1.50–2.80 custom; about £12 Anker | samples |
| 22 | Rubber base pad Ø121 × 1.5 | 1 | Delta Rubber, CNC-cut natural rubber or nitrile with 3M adhesive | quote required, about £2–5 | no tooling |
| 23 | Retail packaging: rigid box, insert, certificate | 1 | Packhelp (MOQ 120) or Tiny Box Company stock box plus foil | £6–16 all-in | see bands |
| 24 | Fasteners, heat-set inserts, grease | set | Accu, Ruthex or CNC Kitchen | about £3–5 | stock |

## 1. Display and main board — Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C

The one part with no alternative: the whole geometry is built around its Ø115 × 6 mm display disc and its 85.5 × 65 mm main board.

| Source | Price | Stock | Notes |
|---|---|---|---|
| Waveshare direct | $64.99–74.99 list; no quantity break shown | not shown | A 60–100 piece price is quote required through their inquiry form. Their customisation page says semi-custom variants start at 500 pieces, so do not expect a custom board |
| The Pi Hut (UK) | £62.40 including VAT | **sold out** | Has a business-purchase portal; trade price quote required |
| Amazon UK, third-party sellers | not verified | — | Reseller channel only |

Pros: proven, optically bonded glass, the exact part the model is built on. Cons: single source, no UK stock today, shipping from Shenzhen with import VAT and duty, and no bare-panel option — the same glass sold alone as Waveshare's "3.4inch DSI LCD (C)" costs *more* ($82–85) than the whole board, so for 60 units the complete board is the only economic path. Order all 60 plus spares in one lot so the numbered run gets one panel batch and therefore one brightness and colour.

## 2. CNC aluminium bezel

Ø134 × 25.9 mm deep cup, 56 milled V-grooves 1.2 mm deep on the outside, smooth chamfers, a V-ridge in the bore for the wheels, sixty radial M2.5 tapped holes for the poles.

**Alloy.** 6061-T6, or 6082-T6 (the UK near-equivalent — confirm the black shade on a sample). 7075 anodises with a bronze tint and shade variation between parts; JLCCNC's own guide names 6061 and 6063 as the alloys for an even deep black.

**Do not call the knurl a knurl.** To a supplier "knurling" means a pattern rolled into the surface at 0.8–1.6 mm pitch; JLCCNC only offers 0.8 and 1.0 mm rolled knurl and warns that the rolling force distorts thin-walled cups — which this part is. The 56-tooth, 1.2 mm-deep pattern at about 7.5 mm pitch is 56 milled grooves on a rotary fourth axis. Model them explicitly and let the instant-quote engines price the machining time. The sixty radial tapped holes are the second-largest time item after the grooves.

| Supplier | Price at 60 | Lead | Pros | Cons |
|---|---|---|---|---|
| JLCCNC, China | quote required (instant from the model) | 3 working days plus shipping | Cheapest route; bead-blast plus black anodise offered as a combination; engineering review | UK reviewers report anodise defects and surprise import charges; post-anodise machining "not recommended" as standard; 6082 not stocked |
| PCBWay CNC, China | quote required (manual review) | from 1 day for simple parts | Bead-blast plus anodise combination exists | No published knurl capability; their finish page warns of rack marks and colour variation |
| Xometry UK | quote required (instant, under a minute) | from 8 days | UK invoicing and support; 6082 available; ISO 9001; custom finishes via "Other" | Parts made across their network; no published unit prices |
| Hubs (Protolabs Network) UK | quote required | from 5 working days | Knurling, grooving and boring explicitly listed; 4.9 of 5 on 286 reviews | Partner-dependent quality; anodise partner varies |
| Penta Precision, Portchester, UK | quote required (send STEP and drawing) | 6–8 weeks for 26–100 off | One-stop machining plus in-house sulphuric anodise, no import; lathes to Ø380 | Long lead; UK shop rates are several times China |
| Protolabs in-house | **not viable** | — | — | Maximum aluminium turning diameter is 100 mm; 6061 not offered |

Cost drivers to expect in every quote: the groove milling passes, the sixty tapped holes, thin-wall distortion (may force a two-operation strategy), and the post-anodise chamfer as a second setup. No supplier publishes a per-part figure for a milled decorative-groove part of this size. Only the quotes will settle it; the roll-up at the end carries this line as a wide range and says so.

## 3. Anodising and the bright chamfer

**Anodise.** Type II sulphuric, matte black, bead-blast pre-finish. Bead blasting is quoted separately everywhere. Rack contact marks are unavoidable — specify the rack point (one of the M2.5 holes) and accept that one thread stays uncoated.

| Supplier | Price | Lead | Notes |
|---|---|---|---|
| Parallel Precision, Lydney | **published: £4 plus VAT each at 50 off, £2.80 at 100** (black, 15 µm minimum; bead blast extra; 10 % off if they also machine the part) | 6–7 working days | The only UK page with a quantity table; a candidate for machining and anodise together |
| Acorn Plating, Sandhurst | from £0.45 per item for colour, **£150 minimum charge**; micro bead blasting in-house | about 1–2 weeks | Hobby and small-batch friendly; parts must arrive clean |
| Metro Plating, Uxbridge | quote required | 3–5 working days | Batches from 1 to 50,000; free samples |
| Badger Anodising, Birmingham | quote required | — | Bead blast plus anodise |
| Peterborough Plating (PPC) | quote required | 4-hour express available | Glass-bead vapour honing as the pre-finish alternative |

Budget £150–300 for the batch of 60 including bead blast.

**Diamond-cut chamfer after anodise** — decision 45 in `docs/DECISIONS.md`, that the wide 45° chamfer between knurl and glass is diamond-cut after anodising and is the only jewellery on the object. The alloy-wheel trade does it as coat → single-point lathe cut removes a skin → clear lacquer, oven cured; any lacquer damage lets water in and makes milky patches. Wheel refurbishers' lathes are built for wheel hubs, so fixturing a Ø134 bezel is a favour, not a service — treat them as a fallback and have the machining shop do a light final chamfer pass on the returned anodised parts (soft jaws, protective film, sharp polished insert). Protection is the open question: clear lacquer (chip risk, as the iPhone 5's chamfer showed) or a second clear anodise (slightly frosts the bright cut and needs masking). **Sample both on two parts before the run.** Neither JLCCNC nor PCBWay publishes a bright-edge-after-anodise option; it is a manual request with a second setup charge.

## 4. Steel base plate

Ø122 × 3 mm, Ø34 central aperture for the speaker, six countersinks, two edge notches, about 254 g.

**Finish.** Black oxide alone rusts within weeks indoors unless oiled, and oil under a rubber pad will stain — reject it. Powder coat (about 75 µm thick, about 1,000 hours salt-spray) is the right finish for a hidden plate; specify the countersinks oversize or masked because the coating part-fills them. Zinc plating with black passivate is the thin-film alternative if the countersinks must stay crisp. 304 stainless, bare or bead-blasted, avoids the issue at higher material cost.

| Supplier | Price at 60 | Lead | Countersinks | Notes |
|---|---|---|---|---|
| Fractory (UK network) | instant quote under £5,000 | 9 working days (5 expedited) | via network | No minimum order; finishing via partners |
| LaserMaster (UK) | "from about £25 plus VAT"; countersinks by quote | 5–7 working days | yes, by quote (also tapping, powder coat) | Parts arrive with laser pips and possible scuffs |
| Xometry UK | instant quote | express within 5 days | on request | Powder coat, zinc and black oxide all listed |
| The Laser Cutting Company, Sheffield | quote required | — | **laser-cut countersinks in the same pass**, no secondary operation | Industrial; 60 pieces is fine |
| Unicorn Sheet Metal, Wallsend | instant quote, £60 minimum including VAT | — | — | — |
| SendCutSend (USA) | — | — | — | **Ships only to the USA and Canada** |

Proxy: Stephens Gaskets' published guide gives £1.50–3 per 50 mm mild-steel disc at 100 off and a £50 minimum order. A Ø122 × 3 plate with eight features will sit at about **£4–8 to cut plus £1–3 for countersinking plus a finishing batch charge**. Ask for the countersinks in the same quote to avoid a second minimum, and put the mass ring (section 6) on the same order.

## 5. Wheel bearings — three per unit

See finding 1: the stocked V-groove wheel is Ø12, not the Ø10 the model assumes.

| Option | Price | Notes |
|---|---|---|
| Simply Bearings 623ZZ, 3 × 10 × 4, budget grade | £2.56; £1.92 at 99 or more; £1.79 at 999 or more | UK stock; NSK and SKF versions also available. Add a turned V-collar in Delrin, PEEK or steel from the bezel shop, which also lets the groove angle be tuned to the ridge |
| V623ZZ 3 × 12 × 4, AliExpress lot of 200 | about $0.25 each (headline) | ABEC-1 carbon steel, unknown grease, no traceability |
| V623ZZ 3 × 12 × 4, eBay UK | £2.61 each, 4 in stock | UK stock but a tiny quantity |
| VXB V623 3 × 10 × 3 open (USA) | $39.99 per 10, 30 % off at 100 or more | The only Ø10 V-groove found; 30–60 day lead; US import |
| V624ZZ 4 × 13 × 6 | — | The OpenBuilds wheel; too big for the current post |

Recommendation: plain 623ZZ from NSK or SKF with a turned V-collar, 200 off. It is the only way to get a branded precision race under the premium part, and the collar is a two-minute lathe job for whoever makes the bezel.

## 6. Hidden mass ring in the bezel

Decision 32 in `docs/DECISIONS.md` — add hidden mass inside the bezel for rim inertia. A 2 mm-section ring at Ø125 is about 4.5 cm³: roughly **40 g in brass, 35 g in steel, 80 g in tungsten alloy**. If more than about 40 g is wanted, the section is the lever, not the material.

| Option | Price | Notes |
|---|---|---|
| Laser-cut 2 mm CZ108 brass, Hawkshead Metal | published for a 100 mm disc: £17.14 each at 50, £15.29 at 250 (a Ø125 ring will be similar) | No minimum; free delivery; the site notes it is "running several weeks behind" |
| Metal Offcuts (Merseyside); The Laser Cutting Company / Charles Day Steels (Sheffield) | quote required | Small batches welcome; same-day cutting on many orders |
| Laser-cut steel ring on the base-plate order | about £2–5 | Shares the minimum charge; needs zinc or powder coat if not fully enclosed |
| Tungsten heavy alloy, Stanford Advanced Materials (USA) | quote required | Only if 40 g is not enough; sintered, expensive, US import |
| Tungsten putty or polymer | — | Creeps and is hard to fix cleanly — not for a premium part |

## 7. Detent magnets — six per unit, buy 500

| Supplier | Part | Price | Notes |
|---|---|---|---|
| Supreme Magnets, Singapore | 6 × 3 × 3 mm block, **N52**, nickel-copper-nickel coated, magnetised through the 3 mm thickness | $0.25; 10 % off at 50–199, 12 % at 200–499, 15 % at 500 or more; 1,966 in stock | The only stocked exact size found; import VAT and courier apply |
| K&J Magnetics, USA | B422 = 6.35 × 3.17 × 3.17 mm, N42 | $0.32; $0.31 at 100–249 | Imperial size, 0.35 mm and 0.17 mm oversize — check the pocket |
| first4magnets / Magnet Expert, UK | 6 × 3 × 3 is **not stocked**; custom manufacture offered | quote required | Nearest stock: 3 × 3 × 3 N42 at £0.22 (50 off); Ø6 × 3 disc N42 at £0.31 (250 off) |
| supermagnete, Germany | nearest 8 × 4 × 3 or 10 × 5 × 3 N45 | €0.35 at 160 or more | No 6 × 3 × 3 |
| Alibaba factory run | quote required | Insist on grade test certificates |

Check the magnetisation direction against the carrier drawing: every stocked part is magnetised through its thin 3 mm axis, none through the 6 mm length. Nickel coating is fine here; epoxy only matters for cosmetics or moisture.

## 8. Detent poles — sixty per unit, 3,600 for the run

Decision 21 in `docs/DECISIONS.md` — sixty steel poles on the rotating bezel, six magnets on the stationary carrier. The poles must be ferromagnetic: plain or black steel, never A2 or A4 stainless. A flat point (DIN 913) gives a consistent flux face; a cup point (DIN 916) has a thin, inconsistent rim.

| Option | Price | Notes |
|---|---|---|
| RS PRO 0431993, M2.5 × 3 cup point DIN 916, grade 14.9 black steel | price on application; UK stock status unavailable at fetch | The exact specification; confirm with RS UK sales |
| RS PRO 2873970, M2.5 × 5 self-colour steel | £2.40 per 25 = £0.096 each, back-order | Too long for a 2.5 mm hole unless threaded deeper; about £345 for the run |
| Accu SSU-M2.5-2.5-A2 | — | A2 stainless — **not suitable**; Accu has no steel option at this size |
| Westfield Fasteners | black-oxide 45H steel only from M3 up | — |
| Bolt Base | will source any material on request | quote required |
| **Ø3 mm chrome-steel (52100) bearing balls, grade G100**, Simply Bearings | fractions of a penny each in thousands (page not fetched — quote required) | Hardened, perfectly consistent, press into Ø2.95 blind holes; more steel in the flux path than an M2.5 core |
| Ø3 × 6 mm hardened dowel pins DIN 6325 | Fixaball, £3.79 per pack, sold out | 3 mm-long pins are a custom cut |

The bezel drawing currently has sixty tapped holes; if the rig prefers balls, the holes become sixty Ø2.95 blind drills, which is cheaper to machine.

## 9. Rotation encoder

Decision 34 in `docs/DECISIONS.md` — read the bezel angle from a ring rather than a geared on-axis sensor. The v6a.2 model uses a reflective optical encoder reading a striped strip bonded in the bezel bore, which also keeps the sensing immune to the six detent magnets (decision 35, keep the sensing magnetically separate from the detent).

| Part | Price | Stock | Notes |
|---|---|---|---|
| **Broadcom AEDR-8300-1K2** | Mouser $9.96 single, $8.01 at 100; DigiKey $8.63 at 100; Avnet $5.93 | Mouser 2,547; DigiKey 1,018 | Two-channel, 36–180 lines per inch, 2 mm working gap. On the Ø115.8 bore at 7.09 lines per mm that is about 2,560 stripes → about 10,000 counts per turn with four-times decoding. Needs a chrome-on-polyester or laser-marked strip; holding the 2 mm gap against a printed ring's runout is the manufacturing risk |
| Broadcom AEDR-8320-1Q2 | DigiKey $12.61 at 100 | 1,941 | Finer pitch |
| Broadcom AEDR-8500-102 | Farnell €12.33 at 100 | to order, **18-week lead** | Adds an index channel for absolute homing; the lead time rules it out for this run |
| PixArt PAT9125EL | $2.13, brokers only | no franchised stock | Optical-mouse-style surface tracker; drifts and slips — prototype only |
| ams AS5304 plus MS10 magnetic strip | DigiKey zero stock; strip quote required | poor | Supply risk, and a magnetic strip beside the detent magnets needs a keep-out |
| RLS AksIM-4 ring, 115 mm | quote required | — | The one true "ring encoder" at this size; industrial pricing and a bonded magnet ring |

Recommendation: AEDR-8300-1K2, about £7 per unit plus code strips.

## 10. Carrier lift gearmotor

Decision 27 in `docs/DECISIONS.md` — the lifting mechanism must hold position with no power: a fine screw turned by a small motor, or a shallow self-locking cam. The v6a.2 model reserves 2 mm under the carrier for a cam ring.

| Option | Price | Notes |
|---|---|---|
| **Pololu 75:1 micro metal gearmotor MP 6 V with 12 CPR encoder (#5137)** | $29.95; $23.32 at 100 | 10 × 12 mm gearbox, 290 rpm, 0.78 kg·cm stall; best documented; US import |
| DFRobot FIT0483 N20 100:1 with encoder | $11.90 at Mouser | zero stock, 5 on order |
| AliExpress GA12-N20 with encoder, 10-pack | about $92 per 10 headline | Quality lottery |
| Actuonix PQ12-P micro linear actuator | $75.40 | Holds position unpowered, but 3 mm of a 20 mm stroke and audible at 55 dB — expensive for the job |
| 8–10 mm permanent-magnet stepper with leadscrew (AliExpress) | quote required | A self-locking screw meets decision 27 directly; needs an end-stop or stall detection |

For a 3° cam an N20 gearmotor at 75–150:1 with encoder is adequate; the leadscrew stepper is the quieter, self-locking alternative worth one sample.

## 11. Ring motor and its driver

Decision 31 in `docs/DECISIONS.md` — the motor is a custom large-diameter ring motor because no catalogue part exists at this bore — and decision 30, that motor and magnets must be designed together so their natural lumpiness does not beat against each other.

**What exists.** The closest catalogue parts: Kollmorgen TBM-12913 (outer diameter 128.9 mm, **bore 55.9 mm**, 13.3 mm tall); Mosrac U130 (130 mm, bore 84 mm, 25.9 mm tall); Allied Motion Megaflux MF0127 (about 127 mm, 6–15 mm tall, bore unverified — worth one direct ask, expect 80–95 mm); Celera Motion Omni+ 130 frame (bore unspecified; UK distributor INMOCO); Maxon EC frameless DT85 (bore 47 mm). CubeMars RI100 and GL100 gimbal motors have 30–45 mm bores. A 115 mm bore inside a 135 mm outer diameter leaves 10 mm radially for magnets, air gap, back-iron, teeth and winding — no standard product does that.

**Custom routes.**

| Route | Cost | Assessment |
|---|---|---|
| Custom wound ring stator from a Chinese winding house (Alibaba) | quote required; lamination NRE (laser-cut laminations avoid a stamping die at 60) plus hand winding | The 10 mm radial band forces 3–4 mm slots: low torque, and slot cogging that must be locked to the sixty poles or it beats — decision 30 again |
| **PCB-stator motor** — coils as copper tracks on a flat 4–6-layer board ring at Ø115–135, with the bezel's own magnet ring as the rotor | the board is cheap from JLCPCB or PCBWay (quote per layer stack); ECM (pcbstator.com) offers co-development, price unpublished | Zero cogging by construction; ECM cites the Thrustmaster T598 steering wheel as a shipped example. Torque per amp is low: a convincing end-stop on a Ø135 rim needs roughly 20–40 mNm, so plan a two-sided (dual-rotor) layout and a magnetic simulation before spending |
| Coils around the six magnets acting on the sixty poles (the "hybrid stepper" idea) | bench experiment first | With all six magnets aligning at once it is a single-phase reluctance machine — it can only pull to the nearest detent, never push away or hold an arbitrary angle; it needs three phase-offset groups, and reluctance force on a grub tip is mostly radial, not tangential |
| Fallback: a SmartKnob-class hollow gimbal motor (SparkFun now has one made) driving the bezel by friction wheel or belt | SparkFun IoT Brushless Motor Driver kit $84.96 at 100 includes motor, ESP32, TMC6300 driver and current sensing | Loses direct drive and reintroduces slip — the fault decision 33 removed from the sensor — but it is a catalogue chain that works today |

**Drivers from an ESP32.** The SimpleFOC library (field-oriented control — the software technique that lets a motor push with a chosen force) supports ESP32, S3 and C3 through the MCPWM peripheral; low-side current sensing works on ESP32 with MCPWM only, in-line sensing on any analogue input pins. Torque-mode haptics (end-stops, ramps) want two in-line phase shunts with INA240-class amplifiers; voltage-mode works for detents but drifts thermally and is noisier.

| Driver | Price | Notes |
|---|---|---|
| TI DRV8313PWPR, bare three-phase driver chip | LCSC $2.73 at 100, 715 in stock | Cheapest onto your own board, no current sense |
| SimpleFOC Mini (DRV8313 board) | $6.20 at Elecrow, out of stock | Voltage mode only |
| Trinamic TMC6300 (SparkFun breakout) | $15.26 at 100 | The SmartKnob driver; 2–11 V only |
| SimpleFOC Shield v3.2 | €15–30 | In-line ACS712 current sense, Arduino form factor |
| MPS MP6540 | no distributor stock found | Do not design in until availability is confirmed |

## 12. Haptics

Decision 17 in `docs/DECISIONS.md` — the vibration actuator owns event confirmations only. Open question C in the same document — whether vibration reaches the fingers across the wheel bearings at all — decides whether this line stays.

| Part | Price | Stock |
|---|---|---|
| **TI DRV2605L** driver, I²C, built-in click library | Mouser $1.22 at 100; DigiKey $1.26; LCSC $0.93 | 3,394 at Mouser |
| **Vybronics VLV101040A** linear resonant actuator, 10 × 10 × 4 mm, 170 Hz, 10 ms rise | DigiKey about $5.00 | 4,800–9,900 at DigiKey |
| Vybronics VG0832022D coin actuator, Ø8 × 3.2 mm | quote required | Smaller and weaker |
| TDK PowerHap piezo plus Boréas BOS1901 driver | quote; BOS1901CQR "restricted / obsolete" at Mouser | Supply risk — skip |
| Precision Microdrives C08 / C10 (UK) | quote required | Will quote |

About $6.30 per unit before VAT.

## 13. DAC and headphone amplifier

Decision 16 in `docs/DECISIONS.md` — the audio output stage must clear measurement scrutiny or it is the speakerphone mistake in a different component. Mouser UK, sterling ex-VAT, 2026-09-02:

| Part | £ each | £ at 100 | Stock | Assessment |
|---|---|---|---|---|
| **ESS ES9219Q** — DAC, headphone amplifier and hardware analogue volume in one chip | 9.91 | **7.44** | zero now, **200 inbound due 15 Sep 2026**, 3-week factory lead after that | Datasheet −114 dB THD+N at 2 V into 300 Ω; its volume register *is* the knob. Order 70 against the inbound lot now |
| ESS ES9219C | — | — | **obsolete / restricted**, zero distributor stock | Do not use |
| Cirrus Logic CS43131 — DAC plus ground-centred headphone amplifier, 130 dB dynamic range | 13.91 | 10.35 | **34 pieces**; reels have a 4,000–6,000 minimum | The best-measuring integrated part (the current dongle favourite) but unbuyable at 60 without a broken reel — ask Cirrus or Arrow |
| Cirrus Logic CS43198, line-out only | 13.65 | 9.42 | 1,904 | Needs a separate headphone amplifier |
| ESS ES9039Q2M / ES9038Q2M, DAC only | 14.04 / 15.85 | 10.54 / 11.90 | 612 / 3,170 | Desktop-class with an external amplifier; you own the current-to-voltage stage and the power rails, and the measurements depend on your layout |
| AKM AK4493SEQ, DAC only | 6.90 | 4.57 | 2,825 | Cheapest premium DAC; 24-week factory lead |
| TI PCM5102APW, DAC with a 2.1 V line driver | 5.18 | 3.31 | 326 | "Apple-dongle class"; the good-enough fallback |

Headphone amplifier stages if a DAC-only chip is chosen: TI OPA1622 (£3.64 at 100, 150 mW per channel, −118 dB, runs from a single 5 V — the cleanest low-voltage choice); TPA6120A2 (£2.81 at 10, needs positive and negative rails); TPA6132A2 (£0.47, 25 mW, fine for in-ear monitors only).

Module route for comparison: the Adafruit PCM5102 breakout (£4.50 including VAT at The Pi Hut, 12 left) plus an OPA1622 carrier. The HiFiBerry DAC2 HD (£107.90) has no headphone output and is a 65 × 56 mm add-on board — wrong shape and price. AliExpress ES9038Q2M and CS43131 boards cannot be quoted, carry no compliance paperwork, and have a documented fake-chip problem. Given the audience publishes measurement sweeps, the module route is not the premium story.

Reputation anchor: the Apple USB-C dongle measures about 98 dB SINAD and is the community's "transparent floor"; a competent ES9219Q or CS43131 layout beats it comfortably; a PCM5102A design lands around it.

## 14. 3.5 mm headphone jack

| Part | £ at 100 | Stock | Insert detect | Notes |
|---|---|---|---|---|
| **Switchcraft 35RAPC4BH3** — right-angle board mount, **threaded nickel bushing with hex nut** | **2.39** | 14,993 | yes, on tip and ring | A real machined nut on the port-block face, still soldered to the board |
| Switchcraft 35RAPC4BHN2, same body, plain bushing | 1.38 | 785 | yes | The classic |
| Switchcraft 35RASMT4BHNTRX, surface mount | 1.20 | 9,452 | yes | For reflow assembly |
| CUI SJ1-3535NG | 0.84 | 12,687 | yes | Cheapest reputable through-hole; plastic bushing |
| Amphenol ACJS-MV35-3S, metal panel jack | 0.77 | 973, 16-week factory lead | no | Wires to the board; cheapest metal-nut panel jack |
| Switchcraft 35FM3AU, flush-mount, sealable | 11.49 | 139 | check datasheet | Beautiful flush metal face; expensive and thin stock |
| Lumberg 1503 09 (Farnell) | 1.64 | 1,643 | — | The threaded 1503 08 version is obsolete |

Note: Neutrik NMJ, Rean NYS216 and Amphenol ACJS-MHDR are 6.35 mm (quarter-inch) parts, not 3.5 mm. If the port-block face is thicker than the 35RAPC4BH3's thread length, fall back to the panel jack and take insert detection from the DAC's own jack-detect pin — the ES9219 and CS43131 both have one.

## 15. Notification speaker

Decision 15 in `docs/DECISIONS.md` — the speaker stays as a notification instrument, never a music source. Down-firing through the plate aperture, 8 Ω to match the Waveshare board's speaker header. Mouser UK:

| Part | Depth | Power | £ at 100 | Stock | Notes |
|---|---|---|---|---|---|
| **PUI AS04008CO-R**, 40 mm oval | **5.8 mm** | 2 W | **2.50** | 964 | Thinnest 2 W part; fits the cradle |
| Visaton K 40 (article 2840) | plastic basket | 1 W | 4.51 | 597 | German, published response curve — the named-brand alternative for the product page |
| Visaton K 50 | deeper | 2–3 W, 83 dB | 2.54 | 4,617 | Best value if the Ø34 aperture can grow |
| CUI CMS-40558N-L152 | 5.5 mm | 0.5 W, 90 dB | 1.75 | 679 | Enough for a chime, marginal for voice |
| Dayton CE40P-8 (SoundImports, EU) | 23 mm | 2 W, 200 Hz–20 kHz | €7.40–8.95 | 10 or more | Best sound, too deep for a 34 mm object |
| Dayton CE38MB-32 | 5.6 mm | 32 Ω, 0.25 W, 72 dB | — | — | Wrong impedance, too quiet — reject |
| Tectonic BMR 28 / 35 mm | — | 4 Ω, 10 W | quote required | poor UK stock | Ideal dispersion for down-firing, unavailable |

Amplifier: the Waveshare board's own class-D output and two-pin header (rated 8 Ω 2 W on the sibling 4C board's wiki — confirm on the 3.4C) covers this. Add a MAX98357A (£1.30 at 100, I²S input) only if the speaker moves onto your own board with independent volume.

## 16. Halo LEDs and diffuser

Decision 43 in `docs/DECISIONS.md` — the halo fires down and outward from the base skirt, never from the rotating part — and decision 48, that white means "the device" and colour only ever comes from light.

**Geometry.** A 324° arc at radius 57 mm is about 322 mm of lit length: 29 LEDs at 90 per metre, 39 at 120, 46 at 144. A ready-made side-view strip bent around a vertical skirt fires along the axis (down onto the desk), which is what v6a.2 wants; a *radially* firing ring needs a custom ring-shaped flexible board.

| Option | Price | Stock | Assessment |
|---|---|---|---|
| **OPSCO SK6812SIDE-A**, bare 4020-package side-view addressable RGB LED, LCSC C5378721 | $0.064 at 150; $0.055 at 1,500 | 233,000 | Cheapest custom-ring route; JLCPCB can place them. **RGB only** — white is mixed from three colours, not a phosphor white |
| Worldsemi WS2812B-4020 side-view | $0.077 at 500 | 20,000 | First-party part with a datasheet; RGB only |
| **LEDLightingHut SK6805SIDE-FRGBW**, side-view **RGBW** (a fourth, dedicated white die), 3000 K or 6500 K | $279.50 per 2,000-piece reel, about $0.14 each | in stock | The only side-view addressable RGBW found; two reels cover the run's ~2,800 with spares; SK6805 is the lower-current variant; US import |
| Adafruit NeoPixel side-light strip, 90 or 120 per metre | $21.56 / $27.96 per metre at 100 | **both out of stock** | Known quality; about three units per metre; RGB only |
| Superlightingled SK6812 4020 RGBW side strip | quote required (price hidden) | — | Exists; colour bins unknown |
| Dialight 587-1064-137F 4020 side-view addressable | quote required | in stock | Western-branded, same OPSCO-class die |
| ams OSRAM OSIRE E3731i | quote required | — | Best colour consistency (per-LED calibration data stored on the chip) but top-view, RGB, and its bus is not NeoPixel-compatible |
| Nichia or Lumileds side-view addressable RGBW | — | — | **Does not exist** — Nichia's side-view range is backlight white |
| Custom flexible ring board, JLCPCB | quote (Ø125 bounding box; 5-piece minimum; 4–5 day lead) | — | With a stiffener under the pads |

Quality flags: at the 20 % power cap (`docs/VISION.md`, firmware brightness cap on the halo) an 8-bit LED leaves about 51 usable levels per channel, so fades will step unless the firmware uses gamma tables and temporal dithering; the 16-bit parts (HD108) do not come side-view. SK6812 and WS2812 publish no colour bins — buy the whole run from one reel and date code and hand-select. A phosphor white is the visible upgrade over mixed white for decision 48's "white = the device". Power: about 40 RGBW LEDs at 20 % is roughly 0.64 A worst case — fine on 5 V 3 A, but add it to the board's draw.

**Opal diffuser.** Perspex cast LED-diffusing opal (grade 1TL1 at 36 % transmission or 1TL2 at 48 %, 3 or 5 mm) from Simply Plastics, laser-cut as a Ø124 / Ø117 ring — hotspot-free and reads as a finished part; the page prices per cut piece (delivery £6.95–19.95). Perspex Opal 040 (about 50–70 % transmission) is brighter but shows the LED pitch unless stood off 6–8 mm. Limitation: a laser-cut ring is flat, so the 22° outward lean in v6a.2 is either CNC-cut from 5 mm sheet or dropped. The printed natural-PETG ring is fine for prototypes; layer lines and pitch hotspots read as "printed" at this price point.

## 17. Ambient light sensor

`docs/VISION.md` calls for adaptive brightness for screen and halo together.

| Part | Package | $ at 100 | Stock | Notes |
|---|---|---|---|---|
| **Vishay VEML7700-TR** | 6.8 × 2.35 × 3 mm | 1.02 | 33,655 at Mouser | 16-bit, 0–120,000 lux, filtered to the eye's response; big enough to hand-rework; in JLCPCB's parts library |
| ROHM BH1750FVI-TR | 2.6 × 1.6 mm | 0.62 | 30,928 at LCSC | Cheapest; needs a light pipe |
| TI OPT4001 | 2.1 × 1.9 mm | 1.01 | out of stock at LCSC | Best accuracy — check Mouser first |
| TI OPT3001 | 2 × 2 mm | 1.06 | 2,850 | Hard to hand-solder |
| Lite-On LTR-303 | 2 × 2 mm | 0.55 | 15,815 at Mouser | 20-week factory lead |
| Broadcom APDS-9960 | — | about 0.40 | out of stock | Adds proximity wake but is a mediocre light sensor |

Do not put the sensor behind the opal ring (50–65 % attenuation); give it a Ø2–3 mm aperture in the port block.

## 18. USB-C mid-mount receptacle

The v6a.2 model has the receptacle in a laser-cut notch in the plate, 3.2 mm tall.

| Part | Height | $ at 100 | Stock | Notes |
|---|---|---|---|---|
| **GCT USB4520-03-0-A**, 16-pin USB 2.0 mid-mount, 5 A | **3.16 mm**, 2.10 mm offset | 0.518 (0.463 at 250) | 19,971 at Mouser | Fits the 3.2 mm target; 10,000 insertions; check the offset variant (-1) against a 0.8 mm board |
| GCT USB4525-03-A, 24-pin, 0.8 mm offset | — | £0.56–0.97 at Farnell UK | 1,010, 12-week lead | UK stock in sterling; more pins than needed |
| SHOU HAN TYPE-C 16P CB1.6 073, LCSC | 1.6 mm sink | 0.071 at 150 | 52,535 | Fifteen times cheaper, 5,000 insertions; the sink suits a 1.6 mm board |
| HCTL 16-pin mid-mount, 0.54 mm offset, LCSC | — | 0.142 | 1,245 | Unknown brand |
| JAE DX07S016JA1R1500 | — | 0.40 at 1,500 | 5,015 | Japanese-tier quality; confirm mid- versus top-mount in the datasheet |
| GCT USB4050 | — | — | **obsolete** — do not design in |

Amphenol 12401610E4#2A, Würth 632723300011 and Molex 105450 are top-mount, not mid-mount. All need 5.1 kΩ resistors on the CC pins to get 5 V 3 A from a USB power-delivery source.

## 19. Detachable braided USB-C cable

Decision 44 in `docs/DECISIONS.md` — the cable must be replaceable. A 5 V 3 A USB 2.0 cable needs no electronic marker chip and no USB-IF certification; a custom cable still needs CE/UKCA and RoHS paperwork from the factory. A right-angle plug's moulding height must be checked against the 0.25 mm clearance to the desk pad in v6a.2.

| Option | MOQ | Unit | Lead | Assessment |
|---|---|---|---|---|
| **ByteCable (China), 90° right-angle braided C-to-C, custom logo, colour and length** | 100 | $1.30–2.80 (5 % off at 100–200) | not stated; free samples | Cheapest credible custom route; verify quality on samples |
| WJW (China) custom OEM | 100 (some tiers 1,000) | quote in 24 hours | 7-day sample plus 25-day production | Right-angle, Pantone braid, moulded logo, custom boxes; CE/RoHS/REACH |
| Anker A81L6 right-angle braided 240 W, 1.8 m, 2-pack | retail | not shown (US listing) | stock | USB-IF certified, 24-month warranty; the credible off-the-shelf choice, but 1.8 m and unbranded |
| Nomad Kevlar Carbide 1.5 m | retail | $35 | stock | The most "Leica-adjacent" cable; about £30 dominates the parts cost |
| Native Union Belt 1.2 m | business quote | $19.99 | stock | 1.2 m only |
| UGREEN nylon 100 W | retail | £6 | stock | Decent, not premium |
| Cablelab (UK) / Mechcables (USA), hand-made | 1 | £25–60 / $55–99 | 1–3 weeks | Keyboard-cable aesthetic, not this product's |

## 20. Rubber base pad

Ø121 × 1.5 mm, full face, adhesive-backed, non-marking. See finding 5 on adhesive.

| Option | Price | Notes |
|---|---|---|
| **Delta Rubber (UK), CNC-cut from a drawing file** | quote required | **No tooling charge, no minimum**; silicone, nitrile, EPDM, neoprene; 1–3 days from stock. A steel-rule die is £200–600 and only pays above about 500 pieces |
| Polymax SILONA black silicone 1.5 mm, 60 Shore A, adhesive option | sold per linear metre (2 mm is £77.42 per metre; 1.5 mm by quote) | One 1.2 × 1 m sheet yields about 60 discs; needs a silicone-compatible adhesive (3M 9731 class) |
| Natural rubber or nitrile 1.5 mm sheet plus 3M 9448A tape (Viking Tapes, 50 mm × 50 m) | material only | Bonds to ordinary tape; natural rubber is non-marking, nitrile can mark lacquered wood |
| Sorbothane | 3 mm is the thinnest standard | Too soft — creeps and marks; not for a full-face pad |
| Alibaba custom silicone pads | quote; typical MOQ 500–1,000 | Over the run's MOQ |

Expect £2–5 per pad, cut and adhesive applied.

## 21. Packaging

Decision 58 in `docs/DECISIONS.md` — the run is sixty numbered units. A rigid magnetic-closure box about 170 × 170 × 80 mm, black, blind deboss or foil, foam or pulp insert, numbered certificate card.

| Supplier | MOQ | Unit | Lead | Notes |
|---|---|---|---|---|
| **Packhelp rigid magnetic box** | **120** | €11.14 at 120, €9.72 at 150 | not stated | The only low-MOQ custom rigid box found; hot-stamp foil, soft-touch; inserts on request; nearest stock size 200 × 200 × 90, a custom size is a quote. You will own 60 spare boxes |
| Tiny Box Company, stock black ribbed magnetic | 1 | £3.46 (200 × 160 × 80), £4.09 (230 × 230 × 100) | stock | Foil branding on part of the range, minimums quote required; no 170 × 170, no insert |
| PackMojo rigid plus foam | 300 | quote | 2 weeks after artwork | MOQ is five times the run |
| Supplied Packaging (UK) | 500 | "£3–5" at 2,000 | 4–6 weeks UK/EU | Price anchor only |
| Progress Packaging, Huddersfield | quote | quote | quote | The Leica-tier UK option — foil, emboss, Colorplan papers, foam and inlay; expect a four-figure minimum spend |
| PakFactory (North America) | "depends" | quote | 10–20 working days plus shipping | Blind deboss, foam inserts; import VAT and duty |
| Packlane (USA) | 25 | quote tool | about 10 days | Mailers, not rigid magnetic |
| Delta Global | — | — | — | Enterprise scale; unlikely at 60 |

Realistic all-in bands per unit at 60–120, ex-VAT: **stock box plus foil logo plus laser-cut foam insert plus printed card: £6–10**; **Packhelp-class custom rigid plus insert plus card: £11–16**; **UK bespoke with deboss, wrap, pulp insert and certificate: £20–40, with a minimum spend likely over £2,000 and 6–8 weeks**. Hidden: a foil or deboss block at £50–150 per design, samples at £50–200, and rigid boxes ship assembled so freight is bulky.

## 22. Fasteners, inserts, grease

M3 and M2 screws and M3 heat-set inserts from Accu or Ruthex; three M3 × 12 wheel axles; two M2 for the USB-C breakout; six M3 countersunk for the plate. Roughly £3–5 per unit at run quantities. A light PTFE or bearing grease for the V-collars is pennies.

## Cost roll-up, per unit, landed in the UK, ex-VAT

This is an estimate assembled from the figures above, with the quote-required lines carried as ranges so the total's uncertainty is visible. It shows where the money goes; it is not a quote and must not be quoted onward as one.

| Line | Low £ | High £ | Basis |
|---|---|---|---|
| Display and board | 60 | 68 | $65–75 list plus import |
| CNC bezel (grooves, sixty holes) | 40 | 150 | quote required — China low, UK high; the widest line |
| Bead blast and black anodise | 5 | 8 | Parallel Precision published plus minimum |
| Bright chamfer and protection | 5 | 15 | second setup, quote required |
| Steel plate, powder coated | 6 | 12 | proxy from Stephens Gaskets guide |
| Brass mass ring | 15 | 17 | Hawkshead published |
| Wheels (3) and collars | 3 | 9 | 623ZZ plus turning |
| Magnets (6) | 1.5 | 2.5 | Supreme / K&J |
| Poles (60) | 2 | 6 | balls low, grubs high |
| Encoder and strip | 7 | 9 | AEDR-8300 |
| Lift gearmotor | 10 | 20 | Pololu / DFRobot |
| Haptic driver and actuator | 5 | 6 | DRV2605L plus VLV101040A |
| DAC, jack and amplifier passives | 11 | 16 | ES9219Q plus 35RAPC4BH3 |
| Speaker | 2.5 | 4.5 | PUI / Visaton |
| Halo LEDs and flexible ring | 6 | 14 | 40 LEDs plus JLCPCB flex |
| Opal ring | 3 | 8 | Perspex laser-cut |
| Ambient sensor and USB-C receptacle | 1.5 | 2 | VEML7700 plus USB4520 |
| Cable | 2 | 12 | custom / Anker |
| Rubber pad | 2 | 5 | Delta Rubber |
| Packaging | 6 | 16 | bands above |
| Fasteners and inserts | 3 | 5 | — |
| **Bought parts, motor excluded** | **about 197** | **about 405** | |

Excluded and still to cost: the ring motor and its driver (custom — NRE plus per-unit, rig first); the custom carrier board that hosts the DAC, LEDs, encoder, sensor and drivers (JLCPCB assembly, likely £10–25 per board at 60 — an estimate, not a quote); assembly labour; compliance testing (decision 63 in `docs/DECISIONS.md`, that compliance is now a pricing input at £33–100 per unit); and the halo diffuser if it goes CNC rather than laser-cut. The likely middle of the range, with a Chinese bezel and Packhelp packaging, is **£230–290 per unit** — against £130–165 in `docs/PREMIUM-BOM.md`, which predates the DAC, halo, milled-groove bezel and packaging specification and should be retired.

## What to do this week

1. Send the bezel model (grooves modelled, sixty holes) to JLCCNC, Xometry UK and Hubs for instant quotes, and to Penta Precision for a UK quote with anodise. Ask each explicitly about a post-anodise chamfer pass.
2. Order 70 × ES9219Q from Mouser UK against the inbound lot before it sells through.
3. Ask Waveshare for a 70-piece price on the 3.4C board and a single-batch commitment.
4. Order the rig parts: 50 × 6 × 3 × 3 N52 blocks (Supreme), 100 × Ø3 steel balls and 100 × M2.5 steel grubs, 10 × 623ZZ NSK, one AEDR-8300-1K2. The rig answers findings 1 and 4 and the open questions A to E in `docs/DECISIONS.md` (detent strength, cost to free spin, vibration coupling, rollers versus race, rim runout) before any metal is cut.
5. Request samples: ByteCable right-angle cable, Delta Rubber pad (send the drawing file), Packhelp box, Perspex 1TL2 ring.
6. Move the wheel post or ridge radius in the model for a Ø12 wheel, or switch to 623ZZ plus collar, and re-run the clearance checks.

## Sources

Metalwork: jlccnc.com/blog/knurling-cnc · jlccnc.com/cnc-machining · jlccnc.com/blog/black-anodizing-aluminum · uk.trustpilot.com/review/jlccnc.com · pcbway.com/rapid-prototyping/cnc-machining/ · pcbway.com …/bead-blast-anodized-color/ · xometry.uk/cnc-turning/ · xometry.uk/laser-cutting/ · xometry.com/finishes/ · hubs.com/cnc-machining/united-kingdom/ · protolabs.com/en-gb/services/secondary-services/anodising/ · protolabs.com/services/cnc-machining/cnc-machining-maximum-extents/ · protolabs.com/en-gb/resources/blog/what-is-knurling/ · pentaprecision.co.uk/services/cnc-machining · hdproto.com/cnc-knurling-guide/ · diamondmf.com/best-aluminum-alloy-for-anodizing/ · parallelprecision.co.uk/blog/how_much_does_anodising_cost · acornplating.com/anodising · metroplating.co.uk · badgeranodising.co.uk/services/bead-blasting · anodising.co.uk · thewheelspecialist.co.uk/alloy-wheel/finishes/diamond-cutting · wheelgods.co.uk · dcrsystems.co.uk · fractory.com/laser-cutting-service-uk/ · lasermaster.co.uk/pages/faqs · lasercutting.co.uk/laser-cutting-services/bevel-and-countersink/ · unicornlasercutting.co.uk · sendcutsend.com/faq/can-you-ship-to-countries-outside-of-the-us/ · stephensgaskets.co.uk/laser-cutting-cost-guide · okdor.com/is-black-oxide-rust-proof/ · hawksheadmetal.co.uk (2 mm brass laser cut) · metaloffcuts.co.uk/laser-cutting/ · daysteel.co.uk/laser-cutting/brass-cutting/ · metals4u.co.uk (2 mm brass sheet) · samaterials.com tungsten counterweight parts · wise.com/gb/import-duty/from-china

Motion and sensing: cubemars.com (GL100, RI100) · kollmorgen.com TBM and TBM2G selection guides · mosrac.com frameless torque motors · allient.com megaflux · novanta.com omni-series · inmoco.co.uk · maxongroup.com EC frameless DT brochure · tq-group.com robodrive · pcbstator.com · github.com/ziteh/pcb-motor · pcbway.com PCB_Stator_Axial_Flux project · github.com/scottbez1/smartknob · elecrow.com SimpleFOC Mini · docs.simplefoc.com/boards, /esp_mcu, /low_side_current_sense · sparkfun.com TMC6300 and IoT Brushless Motor Driver · lcsc.com C92482 (DRV8313) · octopart.com MP6540 · first4magnets.com · magnetexpert.com · supermagnete.de · suprememagnets.com 6x3x3 · kjmagnetics.com B422 · amfmagnets.co.uk · accu.co.uk SSU-M2.5 · nutbolt.org grub screws · int.rsdelivers.com 0431993 · uk.rs-online.com 2873970 · boltbase.com · fixaball.co.uk dowel pins · simplybearings.co.uk 623ZZ · ebay.co.uk 151937961360 · vxb.com V623 · plexrobotics.com V623ZZ · lcsc.com AEDR-8300-1K2 · octopart.com AEDR-8300 / AEDR-8320 · de.farnell.com AEDR-8500-102 · octopart.com PAT9125EL · findchips.com AS5304A · mouser.com AS5000-MS10 datasheet · rls.si AksIM-4 · pololu.com/product/5137 · mouser.com FIT0483 · robotshop.com PQ12 · lcsc.com C527464 (DRV2605L) · octopart DRV2605LDGSR · vybronics.com VLV101040A · oemstrade.com VLV101040A · tdk-electronics PowerHap · mouser.com BOS1901CQR

Audio: mouser.co.uk product pages for CS43131, CS43198, PCM5102A, AK4493SEQ, OPA1622, TPA6132A2, TPA6120A2, ES9038Q2M, ES9039Q2M, ES9219Q, ES9219C, ES9218PQ, 35RAPC4BHN2, 35RAPC4BH3, 35RASMT, 35FM3AU, 35PM, SJ1-3535NG, SJ1-3524N, SJ-3524, STX-3120, ACJS-MV35-3S, ACJS-MHDR, NYS216, AS04008, CMS-40558, Visaton K 40, Visaton K 50, MAX98357AETE, PAM8302AASCR, TPA2016D2 · findchips.com ES9219C · cirrus.com/products/cs43131 · esstech.com ES9219 datasheet · audioreview.frieve.com Apple dongle · audioreviews.org Truthear SHIO · archimago.blogspot.com HiFiBerry DAC2 HD · diyaudio.com fake ES9038/AK4493 thread · hifiberry.com DAC2 HD · thepihut.com Adafruit PCM5102 · adafruit.com 6251, 3678, 3968, 3006 · components.espressif.com usb_device_uac · diyinhk.com XU208 · diyaudio.com CT7601 thread · jlcpcb.com SA9227 · waveshare.com/wiki ESP32-P4-WIFI6-Touch-LCD-4C · uk.farnell.com Lumberg 1503 09 / 1503 03 · octopart Lumberg 1503 08 · soundimports.eu CE40P-8, CE38MB · uk.rs-online.com Tectonic · digikey.com TEBM28C10-4B

Light, power, cable, base, packaging, display: adafruit.com 3635, 3634 · lcsc.com C5378721, C2890037, C5348912, C965557, C78960, C17612395, C90462, C93222, C2906290, C5345941, C165948, C3197885, C5119948, C134092 · ledlightinghut.com side-emitting RGBW · superlightingled.com SK6812 4020 RGBW side · btf-lighting.com SK6812 RGBW · dialightsignalsandcomponents.com 587-1064-137F · ams-osram.com OSIRE E3731i · led-ld.nichia.co.jp side-view · hida-led.com HD108 · jlcpcb.com flexible-pcb · simplyplastics.com LED-diffusing opal disc · theperspexshop.co.uk opal-040 · plasticstockist.com Opal 040 · mouser.com VEML7700-TR, LTR-303ALS-01, USB4520-03-0-A, USB4520-03-1-A, USB4125-GF-A · jlcpcb.com C504893 · gct.co usb4520, usb4050 · uk.farnell.com USB4525-03-A · electromaker.io 12401610E4 · digikey.com 632723300011 · anker.com/uk A82E2 · service.anker.com A81L6 · nomadgoods.com Kevlar Carbide · nativeunion.com Belt Cable · uk.ugreen.com nylon C-C · bytecable.com usb-cable-31 and usb-c-cables · wjwsy.com custom USB cable · cablelab.co.uk · mechcables.com · store.cablemod.com · deltarubber.co.uk custom gaskets · polymax.co.uk black silicone sheet, rubber moulding · edmundoptics.com Sorbothane PSA · vikingtapes.co.uk 3M 9448A · packhelp.com magnetic box · tinyboxcompany.co.uk magnetic boxes, branding · packmojo.com magnetic rigid plus foam, MOQ · suppliedpackaging.com rigid boxes · progresspackaging.co.uk rigid boxes · pakfactory.com magnetic boxes, foam inserts · packlane.com rigid boxes · deltaglobal.co · waveshare.com esp32-p4-wifi6-touch-lcd-3.4c, customization, 3.4inch-dsi-lcd-c · waveshare.com/wiki ESP32-P4-WIFI6-Touch-LCD-3.4C · thepihut.com esp32-p4-3-4-round-touch-display

Not fetchable on the day (blocked or not rendering), so not used for numbers: Alibaba and AliExpress product pages, Amazon UK, Audio Science Review threads, Actuonix, Precision Microdrives, practicalmachinist and other forums, the UK Trade Tariff commodity page, Pimoroni.
