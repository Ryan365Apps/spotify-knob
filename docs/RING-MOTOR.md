# The ring motor — what it gives, what it costs, and what else could give the same thing

**Date:** 2 September 2026. Written to answer one question: at £20–45 a unit plus a real engineering programme, does the ring motor earn its place? The test is the one you set — it stays only for excellence we cannot get any other way.

## What the motor is

A torque motor built into the knob: a ring of small magnets set into the knob's underside, over a flat, iron-free stator made as a printed circuit board fixed to the base (the detent research's recommendation; the earlier "coils around the six detent magnets" idea does not work as a motor). It does not spin the knob in normal use. It pushes and pulls against your hand with a force the software chooses, up to about 30–60 mNm sustained and about 65 in bursts (estimates; the click as drawn is about 74). It is the SmartKnob principle at 135 mm.

## Everything the motor can do, and what else could do it

| Feature | What it feels like | Can anything else do it? | How good is the substitute |
|---|---|---|---|
| **1. End-stop walls** — volume max, the end of a list, zero | The knob stops against something soft and springs back a little | Nothing passive makes a position-dependent wall. The vibration actuator can *signal* the end with a firm thud and the light ring can flash — this is what Apple's Digital Crown and Microsoft's Surface Dial do | Signal, not stop. Good enough for most people; not the same in the hand |
| **2. Springs and return-to-centre** — a jog wheel that springs back for scrubbing | Twist against a spring, let go, it returns | Nothing else | None |
| **3. Any number of clicks per turn** — 6 for the app ring, 12 for menus, 30, 120 half-clicks, or none, per screen | The scale changes under your fingers when the screen changes | The sliding-magnet carrier gives 60 or none, and anything between in strength. A *second* set of pegs and magnets (12 pegs, 3 magnets) on a second carrier gives one more count, e.g. 12 for menus. Firmware can also simply skip clicks — 60 physical clicks, every fifth one counts | Two or three physical counts instead of any count. Every-fifth-counts is what most menu dials already do |
| **4. Resistance ramps** — the knob getting heavier as you approach a limit | Gradual, continuous | The sliding carrier can raise click strength as you approach (100 ms lag, 10 updates a second). The vibration actuator can tick harder | Coarser than the motor, but present |
| **5. Textures** — ratchets, a coarse zone and a fine zone, a "notch" at a saved value | Feel changes by position | The vibration actuator can fake a ratchet with speed-driven ticks (Apple does this). A notch at a saved value: no | Partial |
| **6. Damping and inertia** — how fast a free spin dies away, the knob feeling heavier or lighter | The spin-down character | An **eddy-current brake**: a ring of copper or aluminium on the base beside a magnet ring on the knob gives smooth, silent, speed-proportional drag with no power and no contact (the same principle as a car speedometer and the damped flywheels in good tape decks). Sliding the conductor in and out makes the drag adjustable, from the same fast carrier mechanism. The brass mass ring sets the inertia | Good, arguably better — passive damping is smoother than a control loop and needs no sensing |
| **7. The knob moves itself** — the ring turns to show a value set elsewhere (volume changed on the PC, a track change), or nudges to say "look at me" | Spectacle | Nothing else. This is the one thing only a motor can do | None |
| **8. Click cancellation while scrolling** | Free flywheel | The sliding carrier, at a thousandth of the energy | Better than the motor at this |
| **9. Half-clicks (120 per turn)** | Finer scale for scrubbing | Firmware resolution on the position sensor; no physical click | The industrial design research doubts a 3° click is felt against the 6° magnets anyway |

Of the nine, the motor is *irreplaceable* for three: walls (1), springs (2) and self-movement (7). It is *better* for one (3, arbitrary counts). For the rest a passive part matches or beats it.

## What it costs

| Cost | Size |
|---|---|
| Money | £20–45 per unit (the stator board is cheap; the magnet ring, driver and current sensing are not), before the engineering — a custom motor nobody has wound yet, torque constant uncertain by a factor of two until a board is made |
| Height | 3 mm at least (the annulus for the stator under the knob's flange) |
| Power and heat | Bursts only, with the supercapacitor buffer the power research recommends. Continuous use is out: the power research's ledger for "the ring never feels warm" is about 4 W for the whole device, and the motor's heat lands in the coils under the ring |
| Free spin | The knob's magnets sweeping over the stator's copper make a drag that cannot be switched off — imperceptible if the copper is laid as narrow radial spokes, a viscous drag if not. The rig's first test |
| Firmware | A 1,000-updates-a-second torque loop, position sensing to 0.02°, a per-click calibration table, a passivity-safe wall design. This is the SmartKnob programme; it is months, not weeks |
| Electrical noise | Switching currents beside a headphone DAC; the audio research says solvable by layout, but it is a second noise budget |
| Schedule | The sourcing document calls the motor "the schedule risk of the whole run" |
| A collision to check | The knob's motor magnets and the detent's six magnets and sixty pegs share the same annulus; whether they interfere needs a simulation or a bench check (the detent research flags this) |

## The honest comparison of the two products

**Without the motor:** sliding magnet carrier (60 clicks, or none, or anything between, in 100 ms), optionally a second 12-peg carrier for menus, an adjustable eddy brake for spin-down character, the brass mass ring, the vibration actuator for events and faked ratchets, the light ring for limits. Every part passive, silent, cool, cheap, printable, and understood. What you cannot have: walls you push against, springs, a knob that moves itself.

**With the motor:** all of the above plus walls, springs, arbitrary counts and self-movement — the demo that makes a reviewer say "it just turned on its own." Plus £20–45, 3 mm, a firmware programme, a thermal ceiling on how much of it you can use, and the risk that the motor does not reach the torque the estimate promises.

## Recommendation

Do not decide now, and do not let the CAD decide for you. Reserve the motor's annulus and the seat for its magnet ring in the knob as parameters that can be switched on, build the passive version first, and put two things on the rig side by side: the vibration-actuator "wall" and a real motor wall. If the difference is what MKBHD notices, the motor has earned its place. If the eddy brake, the sliding clicks and the light ring already read as "it does something no other dial does", the motor is £20–45 of spectacle the product does not need. The one feature that argues for keeping the option open is 7, self-movement, because nothing else can ever provide it and it is the most photographable thing the object could do.
