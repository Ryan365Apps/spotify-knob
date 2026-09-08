# the 60 — the knob encoder board

**Date: 8 September 2026. Status: design brief, for the decision index.**
The one board on `SMALL-PARTS-SOURCING.md`'s list that genuinely has to be custom. Sits
alongside `BOARD-CARRIER.md`, `BOARD-AUDIO.md` and `BOARD-MOTION.md`, and supersedes
`BOARD-MOTION.md` §5.2 where the two disagree.

Geometry is taken from `V13.md` onward: the sensor lies on a 0.9 mm boss on the seat
flange at **azimuth 310°, r 76**, facing up at a code ring in a 0.15 mm recess in the
crown's underside at r 72.5–79.5, across a 2.0 mm gap. Board z 26.9–27.9, sensor face
29.53, code ring face 31.53.

---

## 1. What this board is for, and why it cannot be bought

The knob spins freely. The motor renders sixty detents against it. **Everything the object
feels like depends on knowing, continuously and without error, where the knob is** — and
`V10.md` already establishes why: the drive ratio between the bore and the motor's bell is
4.14 : 1, so sixty knob detents are 14.5 motor turns, not a whole number. The detent
cannot be rendered from the motor's own angle. It has to come from the knob.

Nobody sells a board for this. Every one of Broadcom's eight AEDR-8300 variants is a bare
component page with no evaluation board, and no third party has made one. That is not a
gap in the market — it is because the board's entire job is dimensional. It holds a 5.12 ×
3.96 mm leadless part at a controlled radius, at a controlled height, at a controlled
angle. A general-purpose breakout could not have done that even if one existed.

**So the board carries three passive components and one sensor, and its real content is
the drawing.**

---

## 2. The part, and one decision to make

### 2.1 Change the variant: `-1W2`, not `-1K2`

`BOARD-MOTION.md` §5.2 specifies the **`-1K2`** at 75 lines per inch and already flags two
reasons to revisit it. Both hold up:

| | `-1K2` (specified) | **`-1W2` (recommended)** |
|---|---|---|
| Resolution | 75 lines per inch | 212 lines per inch |
| Supply | **4.5–5.5 V — a 5 V part** | **3.0–5.5 V — runs at 3.3 V** |
| Level shifting | **Required.** A dual Schmitt buffer, per `BOARD-MOTION.md` | **None.** Outputs are already at logic level |
| Stock | Farnell UK: **"No Longer Stocked"** | **In stock, £8.10 ex VAT**, 14-week reorder lead |
| Line pitch on the ring | 338.7 µm — bars about 170 µm wide | **119.8 µm — bars about 60 µm wide** |

**Take the `-1W2`, and be clear that the reason is the 3.3 V supply and the stock, not the
resolution.** At 3.3 V the level shifter disappears from the design entirely — one fewer
part, one fewer failure mode, and the signal that travels the cable is already the signal
the microcontroller wants.

**The resolution is a side effect, and it is more than the product needs** — §3 shows it
comes out at 268 counts per detent where 96 would have been comfortable. The cost of that
side effect is real and lands on somebody else: the code ring supplier now has to hold a
**60 micrometre feature on a 153 mm ring**, where the `-1K2` would have asked for 170
micrometres.

**So this is the lever to pull if the code ring quotes come back badly.** Going back to a
coarser variant costs one dual Schmitt buffer (SN74LVC2G17DBVR, pennies, already named in
`BOARD-MOTION.md`) and nothing else. Get the ring quoted at 212 lines per inch first —
§6 is a complete specification to send — and keep the coarser option in your pocket.

### 2.2 There is no index channel

The AEDR-8300 has six pins and two output channels. **There is no index or zero mark.**
The knob's angle is therefore **relative, and it starts from nothing at every power-up.**

For rendering detents that is fine, because a detent is a relative thing. But nothing in
the design should ever assume the object knows which way the knob is pointing in absolute
terms — no profile that maps a fixed angle to a fixed value, no "return to twelve
o'clock". If that is ever wanted, it needs a separate feature: one index mark on the ring
read by a second sensor, or a magnet and a hall part. **Worth writing into
`SOFTWARE-INTERACTION-CORE.md` before somebody designs against an assumption.**

---

## 3. The numbers that fall out of the geometry

### 3.1 Set the line count first, then let the radius follow

The sensor's detector is a fixed-pitch photodiode array. It expects the pattern in front
of it to be at **exactly** 212 lines per inch — the datasheet gives the line density as a
minimum and a maximum of the same number, 8.35 lines per millimetre, which is its way of
saying there is no tolerance on this. A pattern at the wrong pitch walks out of step with
the array across the detector's aperture and the signal degrades.

But a ring has to close: the number of lines around it must be a whole number. **So do not
pick the radius and then divide. Pick the line count, and let the radius follow.**

Exact line pitch: 25.4 / 212 = **0.1198113 mm**.
Radius for N lines: r = N × 0.1198113 / 2π.

| Lines, N | Radius, mm | Lines per detent | Quadrature counts per rev | **Counts per detent** |
|---|---|---|---|---|
| 3960 | **75.512** | 66 | 15,840 | **264** |
| **4020** | **76.656** | **67** | **16,080** | **268** |
| 4080 | 77.800 | 68 | 16,320 | 272 |

**Recommend N = 4020, code ring optical radius 76.656 mm.** It is the closest of the three
to the r 76 already in the model, it is a multiple of 60 so a detent boundary always lands
on a whole number of counts, and it sits comfortably inside the r 72.5–79.5 recess with
room for the band in §3.2.

**The CAD change is +0.656 mm on the encoder boss's radius.** Small, but it has to be
exact, because §4.3's alignment budget is only ±0.38 mm and this is not the place to spend
any of it on a rounding error.

Angular resolution at 16,080 counts per revolution: **0.0224° per count**, against a 6°
detent.

### 3.2 The striped band is 2 mm wide, not 7 mm

The recess in the crown's underside is 7 mm radially (r 72.5–79.5). **That is the
mechanical feature. The optical pattern inside it is much narrower.**

The datasheet specifies the window and bar **length** — their radial extent — as **1.80 to
2.31 mm**. Longer bars put reflective area outside the detector's field of view where it
can only add stray light and cost contrast.

**So: a 2.0 mm striped band centred at r 76.656 — that is r 75.656 to r 77.656 — and the
rest of the 7 mm recess left non-reflective.** This matters because a code ring supplier
handed "a 7 mm ring" will draw 7 mm bars, and it will be wrong in a way that is hard to
diagnose afterwards.

### 3.3 Speed, and who counts the pulses

The datasheet's maximum count frequency is **60 kHz**, and its own formula is
count frequency = revolutions per minute × N / 60.

| Situation | Knob speed | Cycles per second, per channel | Quadrature counts per second |
|---|---|---|---|
| A deliberate turn | 0.5 rev/s | 2,010 | 8,040 |
| A brisk turn | 1 rev/s | 4,020 | 16,080 |
| A hard flick | 3 rev/s | 12,060 | 48,240 |
| **The sensor's limit** | **14.9 rev/s** | **60,000** | 241,000 |

**The sensor is not the constraint.** 14.9 revolutions per second on a 175 mm knob is a rim
speed of about 8 metres per second — nobody will do that with a finger.

**The receiver is the constraint.** Roughly **fifty thousand counts a second** on a hard
flick is nothing to a hardware quadrature decoder and a great deal to a Linux program
handling interrupts. **Decode in hardware on the motion board's microcontroller** — the
RP2350's programmable input/output blocks do this without troubling the processor — and
give the Pi a position, not a pulse train. This is not a new requirement, but it is now a
number rather than an instinct.

### 3.4 The outputs are slow, and that matters more than the speed

| Parameter | Value |
|---|---|
| Output type | TTL-compatible, actively driven (2.4 V high at −0.2 mA, 0.4 V low at 8 mA) |
| **Rise time** | **500 ns** typical, at 25 pF |
| Fall time | 100 ns typical |

At a hard flick the period is 83 µs, so a 500 ns rise is under one per cent of it — the
speed is irrelevant. **What matters is that a 500 nanosecond edge is slow, and it has to
survive a journey across an object containing a motor bridge switching in 20 nanoseconds
and an 800 kHz light data line.** A slow edge crossing a plain logic threshold in a noisy
place is exactly how a quadrature decoder gains a count it should not have, and a
miscounted knob feels like the detents have slipped.

**Requirement: a Schmitt-trigger input at the motion board end.** The
**SN74LVC2G17DBVR** named in `BOARD-MOTION.md` §5.2 is still the right part — but with the
`-1W2` it is there for hysteresis, not for level shifting. Keep it, and put it at the
receiving end so the buffered signal travels the shortest distance.

---

## 4. The board

### 4.1 The part's real dimensions, now confirmed

Read off the outline drawing in the datasheet (AV02-3572EN), tolerance ±0.15 mm:

| | Value |
|---|---|
| Length, along the pin rows | **5.12 mm** |
| Width | **3.96 mm** |
| **Height** | **1.63 mm** |
| Package | **Surface mount, leadless** — six pads underneath, plus two exposed ground pads under the optical domes |
| Moisture sensitivity | Level 3 |

**The CAD is already right.** Board top 27.9 + package height 1.63 = **sensor face 29.53**,
which is exactly what `V13.md` records. That is a useful confirmation — the height stack
was built on an assumed package height and the assumption was correct.

### 4.2 Orientation — the package's long axis is radial

The emitter and detector sit at opposite ends of the 5.12 mm length. The datasheet defines
the optical radius as *"the distance between the codewheel center and the centerline
between the two domes"*, and its orientation note says the encoder tolerates radial play
best when the emitter-to-detector axis is parallel to the bars.

The bars on a ring run radially. **Therefore the package's long axis lies on a radial line
through the knob's centre, and the optical spot is at the package's midpoint, level with
pins 2 and 5.**

| Pin | Function | Position |
|---|---|---|
| 1 | Channel B | one end, one side |
| 2 | Ground | middle, same side |
| 3 | Emitter supply | other end, same side |
| 4 | Ground | other end, other side |
| 5 | Channel A | middle, other side |
| 6 | Detector supply | one end, other side. **A chamfer marks this corner** |

**The one thing the datasheet does not give you: it never dimensions the optical centre.**
There is no callout locating the spot in millimetres from an edge or a pin. Geometry says
it is at the package's centre — the dome housing is symmetric within 0.95 mm margins on
the width, and the pin rows are symmetric about the middle row — but that is derived, not
stated.

**So design to the package outline's centre, and prove it on the first article.** §7 test 1.

### 4.3 The alignment budget

| Parameter | Datasheet limit | Where it is spent here |
|---|---|---|
| **Gap, sensor face to code ring** | 1.0 min, 2.0 typical, **2.5 max** | See §4.4 — this is the one to re-centre |
| Radial misalignment | **±0.38 mm** | Boss position, board's placement of the package, code ring concentricity — all three share this |
| Tangential misalignment | ±0.38 mm | Irrelevant; the pattern is continuous round the circle |
| Angular misalignment | **±1.5°** | The package's long axis against true radial. Set by the boss, not by the screws |
| Code ring tilt | **1°** | The crown's underside flatness at the sensor's spot |

**Two consequences for the printed boss.**

**Use a locating spigot, not just screws.** Two screws in round clearance holes give the
board about a degree of rotational freedom before they are tightened, and the angular
budget is only ±1.5° in total. A 1.5 mm spigot in the boss and a matching hole in the
board fixes the orientation before anything is tightened.

**Slot the mounting holes radially by ±0.5 mm.** The optical centre's position within the
package is derived rather than published, so the first article may need trimming. Slots
cost nothing and buy back the one tolerance nobody can predict.

### 4.4 Move the nominal gap to 1.75 mm

The allowed gap runs from 1.0 to 2.5 mm. **The design sits at 2.0, which is not the middle
of that range** — it leaves +0.5 mm of headroom above and 1.0 mm below.

`V14-QUESTIONS.md` item 22 already lists *"gap variation with the knob pushed and pulled
on its wheels"* as a bench item, and that variation goes both ways. The knob rides on
three wheels in a V-groove; it will have some axial play, and the crown will not be
perfectly flat.

**Recommend: raise the boss from 0.9 mm to 1.15 mm, putting the sensor face at 29.78 and
the nominal gap at 1.75 mm.** The budget becomes symmetric at **±0.75 mm**, which is twice
the margin in the direction that currently has least. It costs 0.25 mm of empty cavity and
changes nothing else in the height stack.

**This makes an axial requirement on the wheels**, which should go into the specification:
*the knob's total axial play at the encoder's azimuth, including the crown's flatness,
must stay within ±0.75 mm.*

### 4.5 What goes on the board

Four components. That is the whole bill of materials.

| Item | Value | Why it is on this board and not elsewhere |
|---|---|---|
| **AEDR-8300-1W2** | — | The sensor |
| **Emitter resistor** | **110 Ω ±10 %**, 0402 or 0603 | Sets the emitter to 15 mA. **At 3.3 V it is 110 Ω, not the 220 Ω in the sourcing brief — 220 Ω is the figure for a 5 V supply.** It lives here so the cable carries a steady rail, not the emitter's current |
| **Decoupling capacitor** | 100 nF X7R, 0402 or 0603, at pin 6 | The datasheet requires supply ripple under 100 mV peak to peak |
| **Two series resistors** | 33 Ω, optional but recommended | On channels A and B, at the source. They damp the edge into the cable and limit the damage from a shorted lead. They cost nothing |

**Nothing else.** In particular, **no connector.** The board top is at 27.9 and the crown's
underside is at 31.38, so there is 3.48 mm of headroom and the package alone takes 1.63 of
it. A right-angle Pico-Lock header at 2.00 mm mated height would technically fit, and it
would put a cable route under the moving knob for no benefit. **Solder four wires to pads
on the inboard edge.** This board is not going to be unplugged.

### 4.6 The cable

Four conductors: **3.3 V, ground, channel A, channel B.**

Total board current is about **19 mA** — 15 mA emitter plus 4 mA detector — and it is
steady, not switched, which is the whole reason the resistor is on the board. Voltage drop
over any sane cable is a few millivolts. Conductor size is set by handling, not by current:
**28 or 30 AWG stranded is right.**

Two routing rules, both from `GROUNDING.md`:

- **Run the ground conductor between A and B**, or twist the bundle. These are the slowest
  edges in the object travelling the longest distance.
- **Keep the run away from the motor's phase leads and the halo's data line.** The motion
  board is at azimuth 50°, r 52; this board is at azimuth 310°, r 76. The cable's last few
  centimetres are the risky part, and that is exactly where the Schmitt buffer sits.

### 4.7 Board outline and fabrication

| | Requirement |
|---|---|
| Layers | Two |
| **Thickness** | **1.0 mm** — the CAD has the board at z 26.9–27.9. **The default at every fabricator is 1.6 mm**, so this has to be specified explicitly in the order or the gap comes out 0.6 mm wrong |
| Outline | About 12 mm radially × 8 mm tangentially, final shape from the CAD. Needs the package at the design radius, room for three 0402 parts, four wire pads on the inboard edge, two slotted mounting holes and the spigot hole |
| Land pattern | **Use the datasheet's recommended land pattern exactly** — pads 1.08 × 0.72 mm, rows 1.96 mm apart, 0.94 mm from the centreline |
| Keep-out | **No tracks under the two exposed ground pads between the pin columns.** The datasheet says this explicitly. Give them copper and tie them to ground |
| Silkscreen | **A radial datum line through the package's centre**, extended to both board edges, so the alignment in §7 test 1 can be checked by eye against the boss |
| Finish | Immersion gold, or lead-free levelled solder. Either is fine on a part this size |
| Quantity | **Five.** At this outline five boards cost about the same as one, and this is the board most likely to want a second revision |

### 4.8 Assembly — this part cannot be hand-soldered

The pads are underneath a leadless package. There is nothing for an iron to reach.

| | |
|---|---|
| Peak temperature | **255 ± 5 °C** |
| Time above 217 °C | 60 to 150 s |
| Time above 250 °C | 10 to 20 s |
| Preheat | 40 to 125 °C over up to 120 s |
| Moisture sensitivity | **Level 3** — bake before reflow if the parts have been out of their sealed bag for more than a week |

**Order a stencil with the boards** — about £8, and it is the difference between this
working and not. Paste, stencil, place by hand under magnification, and reflow on a hot
plate or with hot air. Watch the chamfered corner: it marks pin 6.

Two handling warnings from the datasheet:

- **"Exposure to extreme light intensity, such as from flashbulbs or spotlights, may cause
  permanent damage."** Do not photograph the assembled board with a flash and do not leave
  it under a bright inspection lamp.
- The compound **may turn yellow after reflow**. That is cosmetic and expected.

Electrostatic sensitivity is Human Body Model class 2 — ordinary care, a wrist strap.

---

## 5. What could go wrong

**The optical centre is not where the geometry says it is.** It is derived, not published.
Mitigation: five boards, slotted holes, and test 1 before the CAD is frozen.

**Stray daylight through the rim gap.** `V14-QUESTIONS.md` item 22 already flags it. The
0.4 mm rim gap is a long way from the sensor and the path is indirect, so this is probably
fine — but the sensor's own datasheet carries a light-damage warning, and a reflective
encoder confused by ambient light produces exactly the intermittent miscount that is
hardest to diagnose. **Print the boss and its surround in matt black**, and run test 4.

**The production knob's ring may not behave like the prototype's.** See §6.3. This is the
one in this document that could cost a redesign rather than an evening.

**The code ring's concentricity.** The radial budget is ±0.38 mm and the ring must share it
with the boss's position. A bonded film ring on a Ø153 mm crown, placed by hand, will not
hold that. **Make a bonding jig** — a printed ring that locates on the crown's bore and
sets the film's position — before bonding anything.

**Nobody has measured the crown's flatness.** The tilt budget is 1°. Over the sensor's
2 mm spot that is generous, but the crown is a printed part on the prototype and printed
parts warp. Check it on the first crown that comes off the machine.

---

## 6. The code ring — a specification to send to a supplier today

This is quotable as it stands. Send it to **MELTEC, PWB Encoders, Laser Lab and Optry
Tech**, per `FUNCTION-ALLOCATION.md`.

### 6.1 The specification

| Parameter | Value | Source |
|---|---|---|
| Form | An annular ring, pattern on one face | design |
| **Line count** | **4020 lines** (4020 reflective bars and 4020 gaps) | §3.1 |
| **Line pitch** | **0.1198113 mm** (212 lines per inch), no tolerance offered | datasheet |
| **Pattern radius, centre of the band** | **76.656 mm** | §3.1 |
| **Band radial width** | **2.0 mm**, from r 75.656 to r 77.656 | datasheet: window/bar length 1.80–2.31 mm |
| Window to bar ratio | **0.9 to 1.1** | datasheet |
| **Reflective areas** | **Specular reflectance 60 to 85 %** | datasheet |
| **Non-reflective areas** | **Specular reflectance 10 % or less** | datasheet |
| Outside the band | Non-reflective, to the same 10 % figure, out to the recess edges at r 72.5 and r 79.5 | §3.2 |
| Concentricity of the pattern to the ring's own datum | **0.10 mm or better** | §5 |
| Substrate | Chrome on polyester is the assumed answer. **0.15 mm total thickness**, to sit in the crown's recess | assumption, not a vendor's spec — ask them |
| Outer and inner diameter of the physical ring | To suit a 0.15 mm recess at r 72.5–79.5 | design |
| Quantity | **Three for the prototype**, and a quotation at sixty | — |

### 6.2 The questions to ask them

1. Can you hold a **60 micrometre feature** at this diameter, and what is your pitch
   accuracy and its accumulation around a full circle?
2. What substrate and thickness do you recommend, and does it come with an adhesive back?
3. What **specular** reflectance do your reflective and non-reflective areas actually
   achieve, and how do you measure it? The sensor's datasheet specifies specular, not
   diffuse, reflectance measured on a TMA µScan.
4. What is the lead time for three, and for sixty?
5. **Would a coarser pitch — 338.7 micrometres, 75 lines per inch — be materially cheaper,
   faster or more accurate?** This is the question that decides whether §2.1's variant
   choice gets revisited.

### 6.3 The production knob is a different problem, and it needs a coupon

`V13.md` records the plan: **a stuck film ring on the prototype, laser-ablated stripes in
the anodise on the machined knob.**

Those are not the same optical surface. Chrome on polyester is a **specular** mirror, which
is what the datasheet specifies. **Laser-ablating black anodise exposes bare aluminium,
which is typically rough, and rough aluminium scatters — it is a diffuse reflector, not a
specular one.** The sensor may see far less signal from an ablated ring than from a film
one, at the same nominal reflectance.

**So the prototype working proves nothing about the production knob**, and this is the kind
of thing that surfaces after the tooling is committed.

**Test it with a coupon, now, while it costs nothing.** Have one flat anodised aluminium
coupon laser-ablated with a patch of the same 212-lines-per-inch pattern, and compare it on
the bench against a piece of the film ring, with the actual sensor at the actual gap. An
afternoon.

**If ablation does not give enough specular contrast, the answer is not a redesign** — it
is to keep the bonded film ring as the production part too. A film in a machined recess is
a perfectly respectable production solution, and knowing that early is worth more than
hoping.

---

## 7. Bench tests, in the order to do them

| # | Test | What it settles | Time |
|---|---|---|---|
| 1 | **First article alignment.** Fit the board to the boss. Check the silkscreen datum line against the boss's radial mark under magnification, and measure the package centre's radius against the mounting features | Whether the optical centre is where the geometry says. Do this **before** the CAD is frozen | 1 hour |
| 2 | **Gap sweep.** Print shims giving 1.25, 1.50, 1.75, 2.00 and 2.25 mm. Turn the knob slowly and scope both channels at each. Record amplitude, duty cycle and phase | The real gap window for **this** ring and **this** knob, rather than the datasheet's generic one. Confirms or overturns §4.4 | 2 hours |
| 3 | **Axial play.** At the chosen gap, push the knob down and lift it on its wheels while turning. Watch for signal loss | Whether the ±0.75 mm budget in §4.4 is actually met by the wheels | 30 min |
| 4 | **Stray light.** Full daylight, then a desk lamp aimed at the rim gap, then a torch. Turn the knob and count | Whether the rim gap needs a light trap | 30 min |
| 5 | **Duty and phase at speed.** Scope A and B at a slow turn and a hard flick. The datasheet allows up to 75 electrical degrees of pulse-width error and 60 of phase error at the limits of the mounting tolerance — the decoder has to tolerate that much slop | Whether the decoder needs to be more forgiving than a textbook quadrature decoder | 1 hour |
| 6 | **The miscount test.** Mark the knob and the rim. Turn exactly ten revolutions by hand, compare the count to 160,800. Repeat ten times, in both directions | The only test that actually proves the encoder works. **Any drift at all is a miscount and must be chased** | 1 hour |
| 7 | **The reflectance coupon.** §6.3 | Whether the production knob can use ablated anodise, or needs a bonded film | 1 afternoon, once the coupon arrives |

Tests 1 to 6 are one day with the parts in hand. Test 7 needs a coupon ordered now.

---

## 8. What this changes in the other documents

| Document | Change |
|---|---|
| `BOARD-MOTION.md` §5.2 | **Variant changes from `-1K2` to `-1W2`**, and with it the supply from 5 V to 3.3 V. The SN74LVC2G17DBVR stays, as a Schmitt buffer for noise immunity rather than as a level shifter. The counts-per-detent table is superseded by §3.1 here |
| `BOARD-MOTION.md` | Add: quadrature decoding is in hardware on the microcontroller, not on the Pi. Roughly 50,000 counts per second on a hard flick |
| `V15-SPECIFICATION.md` §4.7 | **Encoder radius 76.0 → 76.656.** Boss height **0.9 → 1.15**, nominal gap **2.0 → 1.75**, sensor face 29.53 → 29.78. Boss gains a locating spigot; the board's mounting holes are radially slotted |
| `V15-SPECIFICATION.md` | New requirement: the knob's total axial play at azimuth 310° must stay within ±0.75 mm, including the crown's flatness |
| `MECHANICAL-REQUIREMENTS.md` | The code ring's pattern is a **2.0 mm band**, not the full 7 mm recess; concentricity to 0.10 mm; a bonding jig is needed to achieve it |
| `SOURCING-BOM.md` | Encoder board: 5 off, 1.0 mm thick, plus a stencil. Emitter resistor is **110 Ω**, not 220 Ω, because the board runs at 3.3 V. Buy **three** AEDR-8300-1W2, not one |
| `SOFTWARE-INTERACTION-CORE.md` | **There is no index channel.** Knob angle is relative and resets at power-up. Nothing may assume an absolute knob position |
| `DECISIONS.md` | Index this |

**Still open, deliberately:** the code ring supplier and whether 212 lines per inch is
quotable at a sensible price; whether laser-ablated anodise gives enough specular contrast
for the production knob; and the board outline, which follows from the CAD once §4.4's
boss change is made.

---

## 9. Sources

- [AEDR-8300-1Wx datasheet, Avago/Broadcom AV02-3572EN](https://www.farnell.com/datasheets/2345337.pdf)
  — every electrical, optical, mechanical and reflow figure in this document
- [Broadcom AEDR-8300-1W2 product page](https://www.broadcom.com/products/motion-control-encoders/incremental-encoders/reflective-encoders/aedr-8300-1w2)
- Project documents: `V13.md`, `V15-SPECIFICATION.md` §4.7, `V14-QUESTIONS.md` items 22 and
  26, `BOARD-MOTION.md` §5.2, `GROUNDING.md`, `FUNCTION-ALLOCATION.md`
