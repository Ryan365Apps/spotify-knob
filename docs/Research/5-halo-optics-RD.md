# The light ring: what shipping products actually do

Research into thin, ring-shaped, back-lit diffusers in consumer products, and what it means for a Ø175 mm ring, 5.5 mm tall, 2 mm thick radially, with 53 LEDs on a 10 mm pitch sitting 0.2 mm behind it.

Everything below is tagged **[sourced]** (stated in the document cited) or **[inferred]** (my reading, not stated anywhere). Arithmetic I have done myself is marked as such.

---

## The short version

**The 0.2 mm gap is the problem, and machining the ring from opal acrylic does not touch it.** Moving from a 3D print to machined acrylic fixes stiffness and surface quality. It does not change the optics at all. The ring will still show 53 bright spots with dark valleys between them.

Every published manufacturer figure for "how far back does a diffuser have to sit to hide the LEDs" is expressed as a ratio of **LED spacing to LED-to-diffuser distance**. The published range is **1 : 0.75 at the very best, more usually 1 : 1 to 1 : 4**. Your design is at **1 : 0.02**. That is roughly forty times short of the most aggressive number any diffuser manufacturer publishes, and the gap between "your number" and "their number" is not the kind of gap a better material closes.

**The second finding is more useful than the first.** Almost every shipping product that reads as a continuous, dot-free ring of light does *not* solve this problem. It avoids it. It uses **a light guide** — a clear ring lit from its edge or end by a small number of LEDs, with the light travelling *around* the ring inside the plastic and being scratched out along the way by surface features. Amazon, Apple, Google and the whole German automotive supply chain all do this. A light guide has no "gap" to run out of, because the LEDs are not behind the visible surface at all.

**The third finding is a supply problem you will hit whatever you decide.** Opal acrylic tube does not exist at Ø175 mm, and does not exist at a 2 mm wall in any large diameter. The entire UK stock range is 3 mm wall in fixed steps: 150, 160, 200, 250 mm.

---

## 1. Which products actually have a thin ring-shaped diffuser, and which do not

Two of the candidates on your list turn out not to have one at all, which is worth knowing before you cite them as precedent.

| Product | Does it have a thin ring diffuser? | Evidence |
|---|---|---|
| **Amazon Echo (original, 2014)** | Yes — the strongest documented case | Patent US9721586B1 [sourced] |
| **Amazon Echo Dot 4th/5th gen** | Yes — ring at the base | Three independent teardowns [sourced] |
| **Amazon Echo Studio** | Yes — translucent ring on the underside, 24 LEDs | EDN teardown [sourced] |
| **Amazon Echo Auto** | Yes — a light *bar*, and the only patent anywhere with real numbers | Patent US10620913B2 [sourced] |
| **Apple HomePod mini** | Yes, but formed differently — see below | Patent US11346542B2 + two teardowns [sourced] |
| **Apple HomePod (2018)** | No ring. Backlit + and − symbols routed clean through the circuit board | iFixit [sourced] |
| **Nest Learning Thermostat** | **No.** The outer ring is a steel input dial with an etched inner surface read by an optical sensor. The glow is the screen behind curved glass | iFixit teardown, 2nd gen [sourced] |
| **Nest Thermostat E** | Yes — and it is an edge-lit stack, the closest analogue to what I would recommend | Justin Alvey teardown [sourced] |
| **Bang & Olufsen Beosound** | **No.** B&O's own support pages describe point indicator LEDs on or under a touch plate, not rings. Their own aluminium manufacturing page lists machining, brushing and anodising only — no perforation, no light transmission | B&O support and manufacturing pages [sourced] |
| **Teenage Engineering OB-4** | **No.** TE's own spec sheet lists glass-filled polycarbonate and milled aluminium, and mentions no illuminated display or diffuser | teenage.engineering product page [sourced] |
| **Dyson** | No evidence found either way. The full technical teardown of the Airwrap covers no LEDs, light guides or diffusers at all | MistyWest teardown [sourced, negative] |
| **Sonos Era / Move / Roam** | Nothing published on the optics. iFixit documents only fasteners | iFixit [sourced, negative] |
| **Philips Hue, Nanoleaf, Govee, LIFX** | Nothing published on diffuser material, thickness, gap or pitch for any of them | [sourced, negative] |
| **BMW iDrive, Audi MMI, Mercedes** | No teardown with optical detail exists publicly. But their supplier (Preh) and their peers have filed patents that describe the method precisely | Patents below [sourced] |
| **High-end keyboards** | Yes, and the practice is well documented: laser-cut acrylic or tempered glass diffuser sheets sold as separate parts | KPrepublic, Drop, Dygma [sourced] |

**Two corrections worth carrying forward.** If you were planning to point at B&O or Teenage Engineering as precedent for a lit ring, the evidence does not support it. If you want a citable precedent for light emerging from an aluminium surface, the evidence base is Apple's microperforation patents (US7778015, US8303151): holes of 20–50 µm through 250–400 µm metal, with a **300–400 µm side-lit light guide layer** bonded behind with optically clear adhesive [sourced]. That is a very different construction from a visible diffuser ring, but it is the documented one.

---

## 2. What the diffusers are made of, and how they are held

### The only patent anywhere that gives real numbers

**Amazon, US10620913B2, the Echo Auto light bar.** I verified this directly against the claims. Verbatim:

> "The linear light bar component has a thickness of about **1 millimeter** and an optical transmission value greater than about **35%** and less than about **75%**."

And from the description [sourced]:

- The visible skin is **translucent black polycarbonate**, transmission "between about 45% and about 60%, such as about 50%"
- Behind it sits a **separate translucent white polycarbonate diffuser**, with "one or more rough surfaces"
- Behind that, a **white polycarbonate reflector at about 45°**
- The white diffuser is not flat. It has **bumps pitched to the LED spacing**: "a central axis of an LED may be aligned with a midpoint of an arc of curvature of the corresponding curved portion", and the "width of a flat portion may be based … on a distance between adjacent LEDs"

So Amazon's answer to a thin light bar is a **three-layer stack** — reflector, shaped white diffuser, thin dark skin — where the diffuser geometry is explicitly designed around where each LED is. Not one homogeneous opal wall.

### The Echo ring family: light pipe first, diffuser second

**US9721586B1** (original Echo) describes the knob's upper lip fitted with an **"edge pipe"**, fed by a separate **"light pipe diffusion ring"** mounted on the circuit board, which is itself fed by the LEDs. Twelve RGB LEDs. So: LEDs → mixing ring → edge pipe → visible surface. Two optical stages before anything is seen [sourced].

**US9574762B1 / US9641919B1 / US10976486B1 / US11287565B1** (the later Echo/Dot family) describe [sourced]:

- LEDs that **fire downwards**, not outwards
- A reflector with **one cup per LED**, each containing a **triangular light-spreading element**, turning the light 180° upwards
- A ring "made of a **diffusive material**" that "may comprise a single light pipe such that light received at a discrete portion of the light pipe diffuses to other locations"
- Retention, verbatim: the ring "may reside atop vertical walls of the light-reflector housing" and a **"clamp plate … may secure the light reflector in place"**

That last point is good news for you: **clamping a diffuser ring between two housing parts is the normal, patented way to do it.** Your lip-above / rebate-below scheme is exactly the industry-standard retention. Johnson Controls' thermostat halo patent US10655881 says the same thing outright: "the halo diffuser is coupled to the front portion and the back portion and is **located between** the front portion and the back portion" [sourced].

### Nest Thermostat E — the closest working analogue

From Justin Alvey's teardown, verbatim [sourced]:

> "Peeling off the back reflective layer of the screen, exposes another transparent layer, used for spreading the light from the **6 side-facing LED's** (similiar to how the Kindle Paperwhite screen is lit up). The next white layer appears to aid diffusing of the light to create a nice even white glow."

Six LEDs. Side-facing. Firing *into the edge* of a clear spreading layer, with a reflector behind and a white diffuser in front. The ring itself is unpainted moulded **polycarbonate** — a supplier parts listing calls it "Google Nest Thermostat E, White Polycarbonate Ring" [sourced].

### HomePod mini — graded diffusion with deliberate air gaps

Apple's US11346542B2 discloses three stacked layers with **air gaps between every one of them** [sourced]:

- A **lens diffuser** with one lens per LED — "a coarse diffuser that spreads light widely (but not necessarily smoothly)"
- A **textured diffuser** — "a medium diffuser"
- A **volume diffuser** with scattering particles such as titanium dioxide — spreads "lightly"
- "The presence of air gaps may help promote light mixing"

And the ring itself: "A **light-guiding portion of the lens diffuser layer** may guide light to a **circular peripheral edge** to form an illuminated ring." Nineteen LEDs, which both teardowns confirm [sourced].

Note the pattern. Apple does not use a thicker or milkier diffuser. It uses **three weak diffusers separated by air**, because each interface mixes.

### Retention methods actually evidenced

| Method | Product | Source |
|---|---|---|
| Clamped between front and back housing | Johnson Controls thermostat halo | US10655881 [sourced] |
| Seated on reflector housing wall, held by a clamp plate | Amazon Echo family | US9574762B1 etc. [sourced] |
| Four T5 Torx screws | Echo Dot 4th gen | EE World [sourced] |
| Screws plus interference/snap fit | Echo Studio | EDN [sourced] |
| Four screws plus four snap clips | Sonos Era 100 touch bar | iFixit [sourced] |
| Light adhesive ("pops right off") | HomePod mini diffuser dome | EDN Asia [sourced] |
| Adhesive foam gasket | Nest Thermostat E | Alvey [sourced] |
| Silicone sealant | Hue A19 bulb diffuser | atomic14 [sourced] |

**Nobody uses a hard interference fit into metal.** Everything is clamped, screwed, snapped, or bedded on something compliant.

### What nobody publishes

Across roughly forty sources: **one** diffuser thickness figure (1 mm, Echo Auto) and **zero** stated LED-to-diffuser gaps in any product patent or teardown. LED pitch is never given in millimetres — only counts (6, 12, 19, 24) and "substantially equal spacing". If you were hoping to find a shipping product that runs a 0.2 mm gap and copy it, it is not in the public record, and I think the reason is that it does not exist.

---

## 3. Avoiding visible dots: what works, and what works at 0.2 mm

### The published numbers

**BrightView Technologies** is the only diffuser manufacturer I found that publishes the geometry number rather than just haze and transmission. Their table's column heading, which I verified on the live page, is literally *"Distance to achieve complete LED hiding (Distance between lamps : Working distance to diffuser)"* [sourced]:

| Product | Type | Efficiency | LED spacing : distance needed |
|---|---|---|---|
| C-HE15 | single-sided | 93–96% | 1 : 4 |
| C-HE40 | single-sided | 90–94% | 1 : 2.3 |
| C-HE90 | single-sided | 87–92% | 1 : 1.3 |
| C-HH80 | double-sided | 89–93% | 1 : 1 |
| C-HH90 | double-sided | 88–93% | 1 : 0.85 |
| **V-H080** | volumetric | 87–96% | **1 : 0.90** |
| **V-H105** | volumetric | 79–90% | **1 : 0.75** |

Their own guidance: "choose the highest-efficiency diffuser that meets your lamp-hiding goals." The pattern is monotonic — more hiding costs light. (One row, C-HE30 at 1:1.25, breaks the trend and is probably a typo on their page.)

**Best published case: 1 : 0.75.** At your 10 mm pitch that demands **7.5 mm** behind the LEDs. You have 0.2 mm. To make 1 : 0.75 work at 0.2 mm you would need an LED pitch of **0.27 mm**, which is not a thing.

**LEDrise**, an LED module vendor, states the common rule and — usefully — uses your exact pitch as the example [sourced, verified verbatim]:

> "For optimal results, the distance between the LEDs and the cover should be equal to the LED pitch. For instance, **if the LED pitch is 10 mm, the distance between the LEDs and the cover should also be 10 mm.**"
>
> "If the LED pitch is larger than the distance to the cover, the individual LED's emission light will become increasingly noticeable as the difference between the two grows. This results in undesirable hotspots."

**Evonik, Röhm, Perspex and Covestro publish no distance guidance at all.** I checked PLEXIGLAS Satinice TI 211-11, Perspex Spectrum LED, and Covestro's "Shaping LED diffuser performance" white paper. They all publish transmission percentages and say nothing about how far back the sheet must sit [sourced, absence]. **Inferred:** the reason is structural. A bulk-scattering sheet smears a source over roughly its own thickness times a scattering factor. A 2 mm wall can smear over millimetres, not the ~10 mm your pitch demands. Which is why they leave cavity geometry to the luminaire designer.

### Technique by technique

| Technique | Works at a 0.2 mm gap? | Notes |
|---|---|---|
| **Light guide / edge-lit ring** | **Yes** — the only architecture with real sub-millimetre evidence | See below |
| **Side-firing LEDs feeding a guide** | **Yes**, as the feed into the above | Nest E, automotive |
| Second diffusing layer with an air gap | No — needs radial room you do not have | HomePod mini needs the depth |
| **Denser LED pitch** | Helps linearly, but cannot get you there alone | 4.2 mm pitch still leaves 1 : 0.05 |
| White/reflective cavity walls | No. Worth about **2.4% more light**, and nothing for uniformity | LEDrise [sourced] |
| Microlens array film | Best film option, but still needs about 1 : 0.3 | BrightView white paper |
| **A printed mask or reflective dot over each LED** | **Yes** — a real, published technique | See below |
| Crossed prismatic films | Partly. 86% uniformity at 1 : 0.6 with a stack under 200 µm | LED professional / LASSIE-FP7 |

**The light guide is the answer the whole industry reached.** The clearest single demonstration is the "zero optical distance" mini-LED backlight work in *Crystals* 13(2):241, which defines zero optical distance as **no gap at all** between the LED and the light guide — the LEDs are embedded *in* the guide, light travels sideways, and cone-shaped microstructures pull it out. Result: 91.5% uniformity, single zone [sourced]. The gap stops being a variable because there is no gap; the light travels along the ring, not across a cavity.

**The automotive patents are the practical version of the same idea, at your scale.** They are worth reading in full because they are essentially a recipe:

- **US6685327B2** (Siemens, now Continental — an illuminated rotary control knob): "homogeneous illumination of the adjusting knob … can be realized with **just three light-emitting diodes**", at 120° intervals, feeding a conical PMMA ring. The deflecting faces are deliberately **not concentric**, so "overlapping of the streams of light of two neighboring deflecting faces" fills the sectors. The annular exit face "is formed in a **roughened manner**" [sourced].
- **DE102015115365A1** (Lisa Dräxlmaier, illuminated air vent surround): a light guide running round the opening **without interruption**, fed by **a single point light source**, coupled in **tangentially at an acute angle of 1–30°**, minimum bend radius **15 mm (18 mm preferred)**, with an extraction structure distributing light round the ring [sourced]. One LED, one continuous ring.
- **DE102012209998A1** (appliance control knob): the complete numeric recipe — **3 LEDs**, wall thickness **2–4 mm, preferably 3 mm**, constant round the ring, extraction facets at **30–60°, preferably 45°**, PC or PMMA [sourced].
- **US20060067084A1** (Schefenacker): the numeric definition of "dot-free" — "the prism base width is advantageously only approximately **1 mm**", and "even at a spacing of approximately **1.5 mm**, the prisms can no longer be resolved by the human eye" [sourced].
- **US10723262B1** (Continental, "Light guide for ring gauge illumination"): the extraction gradient, quantified as surface roughness varying "between about zero at a first location on the circumference up to about **400 micrometers** at a second and different location" [sourced].
- **US6991359B2**: extraction dot size and density "progressively increase … at an **exponential rate** in relation to a distance from the light incident surface" [sourced].

Read together: **grade the extraction from nearly nothing at each LED to maximum at the midpoint between LEDs, keep the features under about 1 mm and spaced under about 1.5 mm, and roughen the exit face as a final smoothing stage.**

**The masking technique is the direct-lit fallback, and it is real.** Yılmaz et al., "Masking LED hot spots in a thin direct lit backlight unit using semitransparent and perforated masks," *Optics Communications* (2013). The mini-LED version is the same thing under a different name — reflective mirror dots printed on the guide directly above each LED, knocking down the peak so the valleys can catch up [sourced]. Applied to your ring, this means printing or masking a small opaque or semi-opaque patch on the diffuser's inner face directly over each LED. It costs light and it demands registration accuracy, but it is the one direct-lit trick with published support at very short distances.

---

## 4. Off-the-shelf supply for a Ø175 mm ring

### Opal acrylic tube does not exist at your size

I verified the full catalogue at Clear Plastic Tube Shop. **Every opal acrylic tube they stock has a 3 mm wall**, in these outside diameters: 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 160, 200, 250 mm [sourced]. Plastock's extruded opal range is the same picture — 3 mm wall throughout, 20 to 250 mm [sourced].

**There is no 175 mm. There is no 2 mm wall at any large diameter.** And you cannot turn a 200 mm tube down to 175: the 200 mm tube has a 194 mm bore, so getting to a 175 mm outside diameter removes the entire wall and 19 mm more.

Cast acrylic tube is where odd diameters normally live, and ePlastics does list 6.75″ and 7.00″ outside diameters (175 mm is 6.89″) — but **only in clear**, minimum wall 0.125″ (3.2 mm) [sourced].

Indicative pricing if you did move to a stock size: a 2000 mm length of 200 mm opal tube is £232.50, which parts into roughly 360 rings at 5.5 mm — about **£0.65 per ring in material** [my arithmetic from sourced pricing].

### Cutting the annulus from sheet

The geometry point worth making: cut from **5.5 mm sheet**, not 2 mm sheet, and you get exactly the part you want — an annulus 175 mm outside, 171 mm inside, 5.5 mm tall, with a 2 mm radial wall. Identical light path to a parted tube ring.

The catch is minimum feature size. CutLaserCut states the rule plainly: "minimum cut widths be no smaller than the corresponding thickness of the material" [sourced]. A 2 mm web in 5.5 mm stock is a ratio of 0.36 — well outside that. **Inferred:** this is a CNC routing job with vacuum fixturing, not a laser job. The acrylic CNC guidance gives a **1.5 mm minimum wall** (raised to 2.5 mm for unsupported walls over 10 mm tall), so your 2 mm × 5.5 mm sits just inside the envelope [sourced].

**A cheap fix hiding in the stock list:** Perspex Spectrum LED opal comes in 3, 4, 5, 6, 8, 10 mm [sourced]. Your 5.5 mm height matches nothing. Move the ring height to **5.0 or 6.0 mm** and the part comes straight off stock thickness with no facing operation.

### Grades and transmission

At 3 mm thickness unless noted [sourced]:

| Grade | Transmission | Note |
|---|---|---|
| Perspex Opal 030 | 67–70% | Two sources give 67 and 70 |
| Perspex Opal 1TL2 | **48% or 59%** | **Two published sources disagree — confirm with the mill** |
| Perspex Opal 040 | 46–51% | |
| Perspex Opal 1TL1 | 36% | |
| Perspex Opal 050 | 36–37% | |
| Evonik PLEXIGLAS **0D010 DF** | **83%** | True volume diffusion — light-diffusing beads distributed through the material |
| Evonik WH02 | 44% | White translucent, surface satin |
| Evonik WD300 DF | 21% | Optimal diffusion, 56° half-value angle |
| Simply Plastics opal polycarbonate | 28% at 3 mm, 14% at 5 mm | Heavily loaded |

Two notes. **1T21, 1TL3, 1TL4 and WH72 have no published transmission data** in current manufacturer literature — 1TL3 and 1TL4 do not appear in the Perspex Spectrum LED range at all [sourced, absence]. And your wall is 2 mm, not 3, so real transmission will be higher than these numbers, but for a scattering material the relationship is not a simple exponential — bench-test rather than extrapolate [inferred].

### Injection moulding is out at your volume

By the moulders' own published figures: Get It Made quotes **£3,816 tooling** for a *simple* 45 × 28 × 15 mm part, and says outright "for volumes around 500x and below, it can often be cheaper to CNC machine or 3D Print". Rutland Plastics: "a simple single-cavity tool may cost around **£10,000**" [sourced]. A 175 mm ring needs a much larger tool than the £3,816 example, so treat that as a floor. **Inferred:** a 2 mm wall running 550 mm round is also a genuinely hard moulding — very high flow length to wall thickness, and weld lines where the flow fronts meet.

### Alternatives worth a look

- **Silicone neon-flex diffuser tubing** bends to the circle rather than needing a large-diameter part. A 175 mm ring is 550 mm of circumference, so a 5 m roll makes about nine rings [my arithmetic]. The cross-sections stocked are much larger than 2 × 5.5 mm, but there is a range.
- **Clear cast tube lined with diffuser film** sidesteps the opal-tube gap entirely — clear tube does exist near your diameter.
- **Custom extrusion.** Polinter (Spain) extrude PMMA and PC lighting profiles and tube. A die for a true 175/171 opal tube is the realistic route if the diameter is non-negotiable [inferred].
- **3D printing is not a fix.** Formlabs' own community reports White Resin is a poor volume diffuser and users resort to mixing clear and white; MJF nylon is essentially opaque at 2 mm. No vendor publishes transmission data for any of these, and layer lines across a 2 mm wall will read as banding when lit [sourced user reports; the banding point is inferred].

---

## 5. What argues against thin machined acrylic

### Crazing needs two things, and you have both

Plaskolite states the mechanism in one sentence [sourced]:

> "For crazing to take place, the sheet must have **residual stress AND be attacked by a solvent or cleaner**."

They name acetone and isopropyl alcohol explicitly, as used for cleaning residue, and recommend "just mild soap and water". Curbell adds the sharper point: **"molded-in stresses … can be enough to cause environmental stress cracking in glassy polymers after contact with an agent without any externally applied stress"** [sourced].

The quantitative version, from *Polymers* 15(6):1375 [sourced]:

| Condition | Stress at which crazing starts |
|---|---|
| Regular PMMA, unmachined | **31.4 MPa** |
| Regular PMMA, after alcohol exposure | 29.8 MPa |
| Oriented PMMA, unmachined | 51.4 MPa |
| Oriented PMMA, after alcohol | 43.4 MPa |

Machining alone dropped the threshold by 4.6 MPa. Alcohol produced a **threefold increase in sensitivity to stress**.

**Inferred:** 31.4 MPa is not a large stress. Forcing a slightly undersize ring into a metal groove, or over-torquing a retaining part, can plausibly reach it — and machining plus an IPA wipe moves the threshold down and triples the sensitivity.

### Annealing

Evonik's official ACRYLITE guidance [sourced]: **80 °C**, **one hour per millimetre of thickness, minimum two hours**, then slow cooling. Because "machining stresses occur only at and slightly below the surface", a part whose only fabrication is machining can use the two-hour minimum. Annealing "reduces to a minimum the likelihood that crazing or large-scale cracking will occur", and after cementing it can raise bond strength by more than 50%.

Note a conflict in the literature: a CNC machining guide recommends **pre**-annealing at 80 °C to relieve mill stress so the part does not move during cutting; Evonik's guidance is to anneal **after** fabrication. **Inferred:** both are defensible and they address different stresses. For a part that will be solvent-cleaned or adhesive-bonded in assembly, the post-machining anneal is the one that matters.

### Thermal expansion against metal

Coefficients of linear thermal expansion, from datasheets [sourced]:

- PLEXIGLAS cast/extruded PMMA: **7 × 10⁻⁵ per °C**
- Perspex cast acrylic: **7.7 × 10⁻⁵ per °C**
- Aluminium 6061: about 2.36 × 10⁻⁵ per °C
- Stainless 304: about 1.73 × 10⁻⁵ per °C

Over a 175 mm diameter and a 20 °C swing [my arithmetic]:

| Material | Change on 175 mm |
|---|---|
| PMMA | **0.245–0.270 mm** |
| Aluminium | 0.083 mm |
| Stainless | 0.061 mm |

**Differential against aluminium: about 0.17 mm on diameter, 0.085 mm on radius. Against stainless: about 0.20 mm on diameter.** The acrylic moves three to four and a half times as much as the metal it is trapped in.

Automotive practice, where documented, deals with this in one of two ways rather than by floating clips: **match the coefficients by material pairing** (US20110170309A1 names aluminium with polyphenylene sulfide, or steel with bulk moulding compound), or **over-mould so the guide and its carrier are one part** (Preh's two-shot approach in DE102016112028A1) [sourced]. I could not find any patent or supplier document stating the "one fixed datum, everything else on slots" rule for a light-guide ring in a metal surround, despite looking specifically for it in both English and German [sourced, absence]. It is standard plastics practice; it is just not written down for this case.

### Moisture

PMMA absorbs water: 41 mg in 24 hours at 23 °C, and **2.1% maximum weight gain at saturation** [sourced, Evonik, ISO 62]. The ACRYLITE annealing page notes crazing develops when acrylic "contacts solvents **or absorbs water**", and the CNC guidance warns against flood coolant for exactly this reason [sourced].

**Inferred:** linear swelling is roughly a third of the volumetric change, so a swing between bone-dry and saturated is order 0.3–0.5 mm on a 175 mm diameter — comparable to or larger than the thermal term, and pushing the same way. Clearance, not interference.

### Fragility

Notched Izod impact: **acrylic 0.4 ft-lb/in versus polycarbonate 14 ft-lb/in** [sourced, Curbell]. That is a factor of about 35.

**Inferred:** a 2 mm × 5.5 mm section at 175 mm diameter is a hoop with almost no radial stiffness. As a closed ring it resists hoop loads reasonably, but the failure mode is a crack running from an edge chip — and edge chips happen in machining, deburring, handling and assembly. Evonik's **PLEXIGLAS Resist** family is the middle path: notched impact 2.5–6.5 kJ/m² against 1.6 for standard cast, at the cost of tensile strength (40–60 MPa against 80), modulus, and a *higher* expansion coefficient (up to 11 × 10⁻⁵) [sourced].

### Yellowing: not your problem

Acrylic is the material that does not yellow; polycarbonate is the one that does. Curbell calls acrylic "inherently UV stable" and notes that indoor polycarbonate grades are not UV-stabilised. Evonik claims "unequalled resistance to weathering and aging" [sourced].

**Inferred:** indoors, behind phosphor-converted white LEDs that emit no ultraviolet-B or ultraviolet-C and only a blue pump peak, opal cast acrylic should not visibly yellow over the product's life. I found no controlled dataset on LED-induced yellowing of opal PMMA [sourced, absence], so this is reasoning from the mechanism, not a measurement.

### The one documented product failure that matches your part

**Flos Romeo Moon S2 / Romeo Louis II S2 pendant recall, US Consumer Product Safety Commission, 2017** [sourced]. The failure was **the plastic ring retaining the internal glass diffuser**: "The glass diffuser can detach and fall, posing an impact injury hazard." Units sold 1996–2006 at $800–$1,900; the remedy was a repair kit that reinforced the plastic-only ring with metal. No injuries reported.

That is a thin plastic retaining ring in a lit premium product, failing over a long service life, fixed by adding metal. It is the closest documented precedent to the risk in your part — though note the roles are reversed: there the plastic ring was structural and the glass was the diffuser.

---

## 6. What I would change, and why

### First: separate the two problems the current design conflates

The prototype was flimsy **and** the optics do not work. Machining from opal acrylic fixes the first and does nothing for the second. If you machine the ring and change nothing else, you will have a beautiful, rigid, expensive ring with 53 visible bright spots.

Also worth flagging: your own earlier halo bench-test note fixed the LED pitch at **4.21 mm** (90 SK6812SIDE parts at radius 60.35, described as the physical maximum for that package) and identified the gap as the one number that had never been measured. The current design has gone to **10 mm pitch and a 0.2 mm gap** — worse on both variables simultaneously. Whatever else you decide, that regression is worth understanding before it gets built.

### Second: pick one of three architectures. The current one is not on the list.

**Option A — turn the diffuser into a light guide. This is what shipping products do, and what I would build.**

Stop treating the 2 mm acrylic wall as a screen the light shines *through*, and treat it as a pipe the light travels *along*. The changes:

- Rotate the LEDs to fire **tangentially**, along the ring, injecting into the acrylic wall rather than at it. You already specify side-firing parts; this is a board-layout change, not a radial-budget change.
- Put a **graded extraction pattern** on the ring's inner face: nearly nothing next to each LED, densest at the midpoint between LEDs. Sourced numbers to design to: features under **1 mm** wide, spaced under **1.5 mm** so the eye cannot resolve them (US20060067084A1); grading expressed as surface roughness from about zero up to **400 µm** (US10723262B1); or density increasing exponentially with distance from the source (US6991359B2).
- **Roughen or lightly frost the outer face** as the final smoothing stage (US6685327B2).
- Consider dropping to a **clear or lightly diffusing** acrylic rather than a heavy opal. A light guide needs to transmit along its length; a 36% opal will absorb the light before it travels 5 mm. Evonik's **Edgelight** grades exist precisely for this, and claim "uniform light extraction over the entire part surface without additional scattering foils" [sourced].
- With extraction doing the work, you may not need 53 LEDs. The automotive precedents run rings on **three** LEDs, and an air-vent surround ring on **one**. Your case is easier than theirs because you need per-segment colour control — but even 12 or 16 would cut cost, current and heat sharply.

The honest risk: this is optical design, and it needs iteration. The extraction gradient has to be tuned, probably by test-cutting a few rings with different patterns. It is the difference between a project that needs an evening on the bench and one that needs a few weekends.

**Option B — stay direct-lit, but buy back radial room and halve the pitch.**

The published numbers say what you need. Go to **4.2 mm pitch** (SK6812SIDE 4020 at its physical minimum — about 128 LEDs round a Ø175 ring by my arithmetic) and find **3 mm of gap**. That gives a ratio of 1 : 0.71, essentially at BrightView's best volumetric diffuser spec of 1 : 0.75. Then a 2–3 mm opal wall at 36–48% transmission does the rest, and you are inside published manufacturer guidance rather than forty times outside it.

Three millimetres of radius on a Ø175 mm object is 3.4% of the diameter. Compared to the alternative — a ring that visibly dots — it is cheap. **This is the single highest-value change available if the light guide feels too risky.**

**Option C — direct-lit with per-LED masking, if you truly cannot find the room.**

Print a small semi-opaque or reflective patch on the diffuser's inner face directly over each LED, knocking down the peak so the valleys can catch up. Published in *Optics Communications* (2013) and used in mini-LED backlights as "reflective mirror dots". Combine with a microlens-array film. **Inferred:** this can work, but registration between a printed pattern and 53 LEDs on a 175 mm circle is fussy, you lose a lot of light, and the result is fragile against any assembly variation in ring rotation. I would treat it as a fallback, not a plan.

### Third: change the ring's dimensions to match what you can buy

- **Height 5.5 mm → 5.0 or 6.0 mm.** Perspex Spectrum LED stock thicknesses are 3, 4, 5, 6, 8, 10. Matching one removes a whole machining operation.
- **If the diameter is negotiable at all, consider 160 or 200 mm with a 3 mm wall** and the ring parted from stock extruded opal tube. Material cost drops to under a pound a ring, the wall gets 50% thicker (which helps diffusion), and the whole supply problem disappears. If Ø175 is a fixed brand or ergonomic decision, say so and move on — but it is currently costing you the easiest route to the part.
- **Wall 2 mm is close to the machining floor** (1.5 mm minimum per the CNC guidance). Going to 2.5 or 3 mm buys margin on both machining and diffusion.

### Fourth: how to retain it — and what will break it

- **Radial clearance, never an interference fit.** The thermal differential against aluminium is about 0.085 mm on radius over a 20 °C swing, moisture swell is of the same order or larger and pushes the same way, and process tolerance on a 175 mm laser or router cut is ±0.175 mm at best. Budget at least **0.3 mm radial clearance** and hold the ring with something compliant — a foam gasket, an O-ring, or a silicone bead — rather than trapping it hard between two machined metal faces. Your lip-and-rebate scheme is the right idea and matches how everyone else does it; the detail that matters is that the clamp is compliant in the radial direction.
- **Ban isopropyl alcohol and acetone from assembly and from the care instructions.** This is the single cheapest reliability decision available. Soap and water. The alcohol data is unambiguous: a threefold increase in stress sensitivity.
- **Anneal after machining:** 80 °C, two hours minimum for a machining-only part, slow cool.
- **Specify cast, not extruded.** Cast PMMA is preferred for machining on both melting resistance and stress-whitening grounds.
- **Chamfer or radius every edge** and handle the parts as if they were glass. The notched impact figure is 0.4 ft-lb/in; a chip at the edge is where the crack will start.

### Fifth: what to measure before committing

You already wrote the right test — the wedge fixture that ramps the gap from 0.5 to 6.5 mm along a straight strip and lets you read off where the dots vanish. Nothing in this research replaces it. What the research does is tell you what to expect: **the answer will land somewhere between 0.75 and 1.0 times the LED pitch**, so at 4.2 mm pitch expect 3–4 mm, and at 10 mm pitch expect 7–10 mm. If the bench test comes back saying 0.2 mm is fine, something is wrong with the test.

Add one variable the original test plan does not include: **a sample with the LEDs turned to fire tangentially into the edge of the acrylic**, with and without a scratched extraction pattern on the inner face. That is a half-hour addition to the same rig and it is the experiment that decides between Option A and Option B.

---

## Sources

**Patents**

- [US9721586B1 — Amazon, Voice controlled assistant with light indicator](https://patents.google.com/patent/US9721586B1/en)
- [US9574762B1 — Amazon, Light assemblies for electronic devices](https://patents.google.com/patent/US9574762)
- [US9641919B1 — Amazon, Audio assemblies for electronic devices](https://patents.google.com/patent/US9641919)
- [US10620913B2 — Amazon, Portable voice assistant device with linear lighting elements](https://patents.google.com/patent/US10620913) · [full text on Justia](https://patents.justia.com/patent/10620913)
- [US11346542B2 — Apple, Electronic device with diffusively illuminated housing portions](https://patents.google.com/patent/US11346542B2/en)
- [US7778015 — Apple, Microperforated and backlit displays](https://patents.google.com/patent/US7778015)
- [US8303151 — Apple, Microperforation illumination](https://patents.google.com/patent/US8303151)
- [US10655881 — Johnson Controls, Thermostat with halo light system](https://patents.justia.com/patent/10655881)
- [US6685327B2 — Siemens/Continental, Illuminating the adjusting knob of an input unit](https://patents.google.com/patent/US6685327B2/en)
- [US20060067084A1 — Schefenacker, Light guide for vehicle lights](https://patents.google.com/patent/US20060067084)
- [US10723262B1 — Continental, Light guide for ring gauge illumination](https://patents.google.com/patent/US10723262B1/en)
- [DE102012209998A1 — BSH, Lichtleiter für ein Bedienelement](https://patents.google.com/patent/DE102012209998A1/en)
- [DE102015115365A1 — Lisa Dräxlmaier, Illuminated air vent](https://patents.google.com/patent/DE102015115365A1/en)
- [EP3479187A2 / DE102016112028A1 — Preh, Rotary actuator with improved light guide](https://patents.google.com/patent/EP3479187A2/en)
- [US20100195346A1 — Valeo Vision, Optical device for an automotive vehicle](https://patents.google.com/patent/US20100195346A1/en)
- [US6991359B2 — Light guide plate with differently configured dots](https://patents.google.com/patent/US6991359B2/en)
- [US20110170309A1 — Reflector in a lighting apparatus of a motor vehicle](https://patents.google.com/patent/US20110170309A1/en)

**Teardowns**

- [iFixit — Nest Learning Thermostat 2nd generation](https://www.ifixit.com/Teardown/Nest+Learning+Thermostat+2nd+Generation+Teardown/13818)
- [Justin Alvey — Nest Thermostat E teardown](https://justlv.medium.com/nest-thermostat-e-teardown-and-on-making-beautiful-devices-for-the-home-ae6ada01bb26)
- [HD Supply — Nest Thermostat E white polycarbonate ring](https://hdsupplysolutions.com/p/google-nest-thermostat-e-white-polycarbonate-ring-p999168)
- [iFixit — HomePod mini](https://www.ifixit.com/News/49645/homepod-mini-round-full-of-sound-and-now-torn-down) · [EDN Asia — HomePod mini](https://www.ednasia.com/teardown-apple-homepod-mini/)
- [iFixit — HomePod](https://www.ifixit.com/Teardown/HomePod+Teardown/103133)
- [EDN — Echo Dot 4th generation](https://www.edn.com/seeing-inside-whats-amazons-fourth-generation-echo-dot-got/) · [Brian Dorey — Echo Dot 4th gen](https://www.briandorey.com/post/echo-dot-4th-gen-smart-speaker-teardown) · [EE World](https://www.eeworldonline.com/teardown-amazon-4th-generation-echo-dot-faq/)
- [EDN — Echo Studio](https://www.edn.com/disassembling-the-echo-studio-amazons-apple-homepod-foe/)
- [iFixit — Sonos Era 100 outer casing](https://www.ifixit.com/Guide/Sonos+Era+100+Outer+Casing+Disassembly/186126)
- [MistyWest — Dyson Airwrap teardown](https://www.mistywest.com/posts/dyson-airwrap-2/)
- [atomic14 — Philips Hue bulb teardown](https://www.atomic14.com/2023/05/04/hue-light-hacking)
- [Bang & Olufsen — light indicator support page](https://support.bang-olufsen.com/hc/en-us/articles/360042473852-Light-indicator) · [All about aluminium](https://www.bang-olufsen.com/en/us/story/all-about-aluminium)
- [Teenage Engineering — OB-4 product page](https://teenage.engineering/products/ob-4) · [iFixit OB-4 teardown](https://www.ifixit.com/Teardown/Teenage+Engineering+OB-4+Teardown+and+Internals/161711)
- [Dygma Defy — RGBW development notes](https://dygma.com/blogs/product-development/the-only-rgbw-keyboard)

**Diffusion and optics**

- [BrightView Technologies — symmetric LED diffusers](https://www.brightviewtechnologies.com/lighting/symmetric-led-diffusers) · [mini-LED white paper](https://www.brightviewtechnologies.com/pdf/BrightView_Technologies-Mini_LED_Whitepaper.pdf)
- [LEDrise — LED pitch and distance to cover](https://www.ledrise.eu/blog/led-pitch-and-distance-to-cover-for-optimum-backlighting/)
- [Crystals 13(2):241 — Zero-optical-distance mini-LED backlight](https://www.mdpi.com/2073-4352/13/2/241)
- [Crystals 12(3):313 — Mini-LED backlight technology progress](https://www.mdpi.com/2073-4352/12/3/313)
- [Optics Communications — Masking LED hot spots with semitransparent and perforated masks](https://www.sciencedirect.com/science/article/abs/pii/S0030401813010419)
- [LED professional — Ultrathin direct-lit LED module with beam-shaping thin-film optics](https://www.led-professional.com/resources-1/articles/ultrathin-direct-lit-led-module-with-beam-shaping-thin-film-optics)
- [3M Diffuser Films 3635 / 3735 datasheet](https://multimedia.3m.com/mws/media/823536O/3m-diffuser-film-3635-30-3635-70.pdf)
- [Uniformity tape](https://en.wikipedia.org/wiki/Uniformity_tape)

**Materials and supply**

- [Evonik PLEXIGLAS Satinice TI 211-11](https://www.plexiglas.de/files/plexiglas-content/pdf/technische-informationen/211-11-EN-PLEXIGLAS-Satinice.pdf)
- [Röhm PLEXIGLAS lighting grades — Edgelight, Softlight](https://www.plexiglas-polymers.com/en/application-areas/lighting)
- [Perspex Spectrum LED](https://www.perspex.co.uk/materials/perspex-cast-acrylic/spectrum-led/) · [Perspex opal light transmission datasheet](https://www.theplasticshop.co.uk/plastic_technical_data_sheets/perspex_sheet_opals_light_transmission_values.pdf) · [Perspex product guide](https://www.perspex.co.uk/Perspex/media/General/technical-library/Typical%20Physical%20Properties/PERSPEX-PRODUCT-GUIDE_1.pdf)
- [Covestro — Shaping LED diffuser performance](https://solutions.covestro.com/-/media/covestro/solution-center/whitepapers/shaping-led-diffuser-performance.pdf) · [optical portfolio brochure](https://solutions.covestro.com/-/media/covestro/solution-center/brochures/pdf/optical-portfolio_brochure_en_v9.pdf)
- [Curbell — Plastic diffuser solutions for LED lighting](https://www.curbellplastics.com/wp-content/uploads/2022/11/Plastic-Diffuser-Solutions-for-LED-Lighting.pdf) · [Environmental stress cracking white paper](https://www.curbellplastics.com/wp-content/uploads/2022/11/Plastics-Environmental-Stress-Cracking-White-Paper.pdf)
- [Clear Plastic Tube Shop — opal acrylic tube](https://www.clearplastictube.co.uk/opal-acrylic-tube) · [Plastock — extruded opal tube](https://www.plastock.co.uk/products/acrylic-extruded-opal-tube)
- [CutLaserCut — opal acrylic sheet and cutting rules](https://cutlasercut.com/materials/opal-acrylic-sheet/) · [Prototype Projects — laser cutting tolerances](https://www.prototypeprojects.com/expertise/laser-cutting/)
- [Simply Plastics — LED light diffusing opal acrylic](https://www.simplyplastics.com/catalog/products-by-use/plastic-lighting-materials/led-light-diffusing-opal-acrylic-sheet/c-24/c-110/p-676)
- [Get It Made — injection moulding costs](https://get-it-made.co.uk/resources/how-much-injection-moulding-costs) · [Rutland Plastics — UK injection moulding cost guide](https://www.rutlandplastics.co.uk/how-much-does-injection-moulding-cost-in-the-uk/)

**Failure modes**

- [Plaskolite TEC380 — How crazing occurs](https://plaskolite.com/docs/default-source/tec/tec380_opx_l_craze.pdf)
- [Polymers 15(6):1375 — Crazing initiation and growth in PMMA under alcohol and stress](https://www.mdpi.com/2073-4360/15/6/1375)
- [ACRYLITE — Annealing acrylic sheet](https://www.acrylite.co/resources/fabrication-manuals/annealing-acrylite-acrylic-sheet)
- [ASTM F484 — Stress crazing of acrylic plastics in contact with liquid compounds](https://store.astm.org/f0484-08r19.html)
- [US CPSC — Flos pendant light fixture recall, 2017](https://www.cpsc.gov/Recalls/2017/flos-recalls-pendant-light-fixtures-due-to-impact-injury-hazard)
