# the 60 — halo bench test

**One number decides the diameter of the whole product, and it has never been measured.**

The halo is a ring of side-firing LEDs behind an opal diffuser. If the diffuser sits too close to the LEDs you see individual dots and scalloped banding instead of a continuous band of light. How far back it has to sit is the *gap*, and the gap is the largest single term in the device's radial budget:

> outside radius = 57.5 (the display) + clearance 0.75 + wall 1.5 + board 1.2 + **gap** + diffuser thickness

Every millimetre of gap is a millimetre on the radius and two on the diameter. The current design guesses. This test replaces the guess with a reading, in one evening.

---

## What is already fixed, and what this test is actually for

**The LED pitch is not a free variable — the package sets it.** The chosen part, OPSCO SK6812SIDE-A, is a 4020 package: 4.0 mm in its longest dimension, so centres cannot be closer than about 4.2 mm without the parts colliding. The LED ring sits at radius 60.35, a circumference of 379 mm, which divides into **90 LEDs at 4.21 mm pitch — and 90 is the maximum that physically fit.**

*(This corrects an earlier analysis that offered 120- and 150-LED options as ways to shrink the gap. They are not buildable with this part. Going finer means a smaller package and a different LED.)*

So pitch is fixed. **The only things left to tune are the gap and the diffuser** — which is precisely what this test measures.

---

## The rig

Do not test four discrete gaps. **Ramp the gap and read off where the dots vanish.**

- A **straight** test strip of the real LEDs at 4.21 mm pitch, about 100 mm long (24 parts). Either a small straight PCB from a prototype house, or hand-soldered parts on stripboard. A straight strip is slightly pessimistic compared to the real ring — on a ring the LEDs fan outward and blend a little better — so a pass here is a safe pass.
- A **3D-printed wedge fixture**: a flat channel holding the strip, with two side rails whose top edge ramps from **0.5 mm to 6.5 mm** above the LED emitting face over the 100 mm length. Print a millimetre scale along one rail. Lay a strip of diffuser on the rails; the gap now varies continuously along its length and you read the answer off the scale.
- A **3 mm-tall aperture mask** in front of the diffuser. The real halo is a 3 mm slot between the plinth and the knob's shadow gap, and aperture height changes how uniform it looks. Testing an unmasked strip flatters the result.
- Print the fixture in black, or paint it. A light-coloured fixture bounces light around and flatters the result too.

## Shopping list

| Item | Note | Rough cost |
|---|---|---|
| SK6812SIDE-A, 25 off | the real part — do not substitute a top-firing LED | £3 |
| Straight test PCB, 5 off | optional; stripboard works | £10 |
| Opal acrylic (PMMA) offcuts, 2 mm | get several light-transmission grades: roughly 30 %, 45 %, 60 %, 70 % | £15 |
| Opal acrylic, 1.5 mm and 3 mm | thickness trades against gap — test it as a variable | £10 |
| Light-diffusion film | a cheap alternative worth one datapoint | £5 |
| Any small addressable-LED controller | a spare microcontroller will do | — |

**About £40, plus PCB lead time if you go that route.**

## Method

1. Dark room. Phone on a tripod at about 600 mm — normal desk viewing distance. **Lock exposure, focus and white balance manually**; auto-exposure will silently rescale every shot and make them incomparable.
2. Photograph each diffuser sample at **full white brightness** (scalloping is worst here) and at about 20 %.
3. Repeat with one saturated colour. The red, green and blue dies sit at slightly different places inside the package, so at short gaps you can get colour fringing that white light hides.
4. For each photo, take a pixel-brightness profile along the strip and compute **modulation depth = (max − min) / (max + min)** across the ripple. Any image tool that plots a line profile will do.
5. Read off the distance along the ramp where modulation drops below the pass mark, and convert to a gap using the scale.

## Pass mark

**Modulation depth below 5 %, confirmed by eye at 600 mm.** The 5 % figure is a working threshold, not a standard — treat the photograph and your own eye as the real verdict and use the number to compare samples fairly.

Record, for each material: **minimum passing gap**, its thickness, and how much light it costs you (a dim, perfectly uniform diffuser is not a win).

## What the answer does

`x` is the total radial distance from the display's edge to the outside of the device. Outside diameter = 115 + 2x.

| gap | diffuser 1.5 | | diffuser 2.0 | | diffuser 3.0 | |
|---|---|---|---|---|---|---|
| | x | OD | x | OD | x | OD |
| 1.0 | 5.95 | **126.9** | 6.45 | 127.9 | 7.45 | 129.9 |
| 1.5 | 6.45 | 127.9 | 6.95 | 128.9 | 7.95 | 130.9 |
| 2.0 | 6.95 | 128.9 | 7.45 | 129.9 | 8.45 | 131.9 |
| 2.5 | 7.45 | 129.9 | 7.95 | 130.9 | 8.95 | 132.9 |
| 3.0 | 7.95 | 130.9 | 8.45 | 131.9 | 9.45 | 133.9 |
| 4.2 | 9.15 | 133.3 | 9.65 | **134.3** | 10.65 | 136.3 |

A thinner diffuser that needs a longer gap is a bad trade; a thicker one that blends at a short gap is a good one. That is why thickness is a test variable and not an assumption.

**The stake:** the range across that table is 127 to 136 mm — nine millimetres of product diameter, and about 100 g of knob mass, resting on a number that costs £40 and an evening to measure. It is the highest-value test on the list.

**Do this before committing to any diameter.** The current working assumption is x = 8.5 (Ø132), taken from a rule of thumb that the gap wants to be roughly one LED pitch. That rule is unsourced. It may well be pessimistic by 2 mm, which is 4 mm of diameter given away for nothing.
