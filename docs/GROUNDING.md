# the 60 — chassis, shield and ground scheme

**Date: 6 September 2026. Status: scheme proposed, for the decision index.** Closes the gap identified in `SYSTEM-REVIEW.md` 4.1, where the only statement about chassis potential in any document was that the plate has *"a ground-bond hole"*.

More urgent than when it was first raised, for two reasons that arrived since: **the plate is now black hard anodised, and hard anodising is an electrical insulator**; and **the plate is now two metals** — an aluminium core and a steel rim ring — which do not connect to each other by being screwed together through anodised faces.

---

## 1. What the object actually contains, electrically

Nobody has written this down, and half the scheme falls out of it.

| Conductor | State today | What it needs |
|---|---|---|
| **Aluminium plate core** | Anodised outside, **bare or chromate-coated inside** (decided 6 Sep) | To be the chassis reference. No masking needed — every bond is on an internal face |
| **Steel rim ring** | A separate conductor from the core, and the outermost metal | **A dedicated bonding screw** — section 4.1 |
| **Knob**, aluminium in production | Touches three plastic wheels and 0.4 mm of air. **Floating, and rubbed by the user** | A bleed path — section 5 |
| **Code strip**, chrome on polyester | Bonded inside the knob's bore, 1 to 2.5 mm from the optical encoder | Follows the knob |
| Structure, deck, diffuser, port face | Printed plastic | Nothing — and section 6 explains why the port face being plastic is load-bearing |
| **USB-C shell** | Held in the plastic port face | A defined route to chassis |
| **3.5 mm jack shell** | Held in the plastic port face | **Deliberately isolated** — section 6 |
| Barrel jack outer contact | The supply's negative return | The star point |
| **Motor frame** | Mounted to a printed carriage. **Floating, and switching at 20 ns edges next to an optical encoder** | A short bond to the motion board's ground |
| Touch sensor | Bonded under the lens, inside a floating metal knob | A stable reference — section 5 |
| Three board grounds | Star-connected at the inlet per the board briefs | Confirmed here |

**Two of these — the rim ring and the motor frame — are floating conductors that nobody has noticed.**

---

## 2. The supply decides the architecture

**Specify a Class II supply: two-pin, double insulated, no earth pin.**

The reasoning is short. The object already has an earth reference — the PC, through the USB cable's ground. A Class I (three-pin, earthed) brick would give it a **second** earth reference, and two earth references at different potentials with an audio cable between them is precisely how a ground loop hums. The audio brief spends a page on avoiding that; specifying an earthed brick would undo it.

**What Class II costs, and it is not nothing.** With the PC unplugged, the object floats, held near half mains by the supply's mains-side filter capacitors through a very high impedance. On a bare metal object this can be felt as a faint buzz under a damp hand. The safety standards cap this current in the sub-milliamp range precisely so it cannot be dangerous, but **on a premium object it is a quality issue, not a safety one**, and it is worth designing out rather than discovering:

- Require the **touch current or leakage figure on the supply's datasheet**, and prefer a low-leakage part.
- **Test it** — section 7.

---

## 3. The scheme

**One star point. One chassis bond. Stated once, here.**

```
                 12 V in ──▶ [ STAR POINT ]  on the carrier board, at the power inlet
                                  │
                                  ├──▶ 5 V converter ──┬──▶ carrier
                                  │                    ├──▶ audio board   (own pair)
                                  │                    └──▶ motion board  (own pair)
                                  │
                                  └──▶ ONE screw, to the plate's internal face
                                            │
                        aluminium plate core ──(bonding screw + star washer)── steel rim ring
                                            │
                                            └── USB-C shell, by a short wire
```

**Four rules that make it work:**

1. **The star point is the only place the three boards' returns meet.** Three separate pairs of wires leave it. Never daisy-chain, never share a return conductor. The board briefs already say this; this document fixes *where*.
2. **The chassis bonds to signal ground at exactly one point, at the star point.** Not at the plate, not at a convenient screw, not in two places. A second bond turns the chassis into a parallel return path and puts motor current through the metal the audio board references.
3. **Bond the chassis solidly, not through a resistor.** A one-megohm bleed is right for a floating part you cannot bond (the knob, section 5) and wrong for the enclosure, which has to work as a radio-frequency shield. A shield needs a low-impedance connection or it is just decoration — and this object has a motor bridge, an 800 kHz light data line and switching converters inside it, with compliance testing ahead (`SYSTEM-REVIEW.md` 4.2).
4. **The internal USB cables' shields bond at the hub end only**, as the carrier brief already specifies. One end, never both.

---

## 4. Anodising: external surfaces only

**Decided 6 September: anodise the outside, and leave the aluminium core's internal faces bare or chromate-conversion coated.** That removes the masking problem entirely — every bond and every thermal joint in the object is on an internal face, so there is nothing left to mask.

| Surface | Finish | Why |
|---|---|---|
| Closing plate, outer face | **Black hard anodised** | Visible underside; it radiates to the desk, and it carries no bond and no thermal joint |
| Any other external aluminium | Black hard anodised | Appearance |
| **Aluminium core, all internal faces** | **Chromate conversion, or bare** | Chromate is electrically conductive and protects against oxidation, so the chassis bond, the rim ring's bond, the compute module boss and the converter and driver gap pads all land on conducting metal with no masked features at all |
| Duct and fin channels | Chromate, or bare | Emissivity is irrelevant here — the fins face each other a few millimetres apart at the same temperature, so the net radiation between them is about zero |
| Steel rim ring | Open question | Steel is not anodised. Whatever finish it gets, see section 4.1 |

**The thermal cost is 0.048 W/K** — the internal face's emissivity falls from 0.88 to about 0.10, worth 2.8 K passive or 0.5 K with the blower. That is the price of deleting five masked features on sixty parts and the invisible fault they invite: an anodised pad everybody assumes is grounded and is not.

### 4.1 The rim ring's bonding screw

The steel rim ring is a separate conductor from the aluminium core, and it is the outermost metal — the part a hand rests against. It gets **one dedicated bonding screw** (Ryan, 6 September), not a fixing that happens to conduct:

- Into a tapped hole, with an **external-tooth star washer** under the head.
- **Both mating faces bare**; if the rim ring's finish covers this spot, either mask it or let the star washer cut through.
- **Close to the chassis bond point**, so the continuity check in section 7 is one measurement.
- **Hidden, and thread-locked or captive.**

Bare aluminium against bare steel is a galvanic pair, so the interface will oxidise over years and its resistance will climb. The star washer gives a gas-tight point contact that survives that, and it makes the bond an inspectable feature rather than an accident.

## 5. The knob: a bleed, not a bond

The knob is aluminium, floating, isolated by three plastic wheels and 0.4 mm of air, and the user rubs it. It will accumulate static, and the nearest thing to discharge into is the **reflective optical encoder, 1 to 2.5 mm away across a chrome-on-polyester strip.** There is no bleed path anywhere in the design. A sprung contact riding in the wheel groove was discussed in an earlier session and never made it into a specification.

**Fit a sprung contact — a phosphor-bronze leaf or a spring-loaded pin — bearing lightly on the knob, and connect it to chassis through a 1 MΩ resistor.**

Three points about that, each deliberate:

- **Sprung, and light.** It must not add measurable drag; the knob's feel is the product. Mount it where the drag is at the smallest radius available and where it is hidden.
- **1 MΩ, not a direct bond.** A direct connection gives a static discharge a fast, low-impedance path straight into the chassis and thence the boards. A megohm bleeds accumulated charge away continuously without ever providing that path. This is standard practice for exactly this case.
- **Contact will be intermittent** on a rotating part, which is fine for a bleed and useless for a shield. Do not expect the knob to be part of the enclosure's shielding, and do not design as though it is.

**It also helps the touch sensor.** A large floating conductor surrounding a capacitive sensor is a variable capacitive load on its edges. Bled to chassis — and chassis is at signal ground — the knob becomes a stable guard ring instead. One part, three problems.

**Bond the motor frame too**, with a short wire to the motion board's ground. A floating motor frame switching at 20 nanosecond edges, a few centimetres from the optical encoder, is a capacitive coupling path into the most exposed signal in the system.

---

## 6. What must not be bonded, and a fact that is currently accidental

**The 3.5 mm jack's metal shell must be isolated from the chassis.** The audio brief's rule is that the jack sleeve is that board's only ground reference to the outside world and nothing may share that copper. If the shell touches the plate, the chassis shares it, and the object hums.

**Right now this is true by accident and it should be made deliberate.** All three rear sockets are held in a **printed plastic port face**, so none of their shells touches metal. That is correct — and it is one design review away from being undone, because a metal port face would look better and nobody would connect the two facts.

**Write it into the specification as a requirement**, not as a consequence: *the port face is an insulator, and the 3.5 mm jack's shell is isolated from the chassis.*

The USB-C shell is the exception in the other direction — it **should** reach chassis (section 3), by a short wire, because a shielded connector's shell belongs on the shield.

---

## 7. Four tests, none of which needs equipment you do not have

1. **Continuity, on the first assembled unit.** Chassis bond pad to the rim ring; to the plate core; to the star point. Under 0.1 Ω each. **This is the test that catches the anodising fault**, and it takes a minute.
2. **The tingle test.** Object powered from the brick, **PC unplugged**, damp fingers on the knob and on the rim ring. If anything is felt, the supply's leakage is the cause, not the design — change the supply.
3. **The hum test.** Object into the PC, audio out to powered speakers on a different mains socket, nothing playing, volume up. Then unplug the USB and listen again. If the hum appears only with both connected, it is a loop, and the audio brief's unfitted isolation transformer footprints are the answer.
4. **Touch with the PC asleep or unplugged.** A capacitive sensor needs the controller's ground and the user's body to share a reference; with the PC gone, the object's reference is only the supply's leakage. **This is a real risk to a component the brief calls tier one** and it has never been considered. Test early, on the bench, before the enclosure is committed.

---

## 8. What this changes

| Document | Change |
|---|---|
| The current specification | **Anodise external surfaces only**, internal faces chromate or bare; the rim ring's dedicated bonding screw; the knob's sprung contact as a real part with a mounting; the port face stated as an insulator with the jack shell isolated |
| `BOARD-CARRIER.md` | The star point is on this board at the power inlet, and it carries the single chassis bond screw and the USB-C shell wire |
| `BOARD-AUDIO.md` §6 | Rule 4 confirmed and its mechanical precondition stated: the jack shell is isolated by the plastic port face |
| `BOARD-MOTION.md` | Add the motor frame bond and the knob's 1 MΩ bleed termination |
| `SOURCING-BOM.md` | Class II supply with a stated leakage figure; the sprung contact; the 1 MΩ resistor; star washers |
| `DECISIONS.md` | Index this |

**Still open:** the sprung contact's exact form and where it rides, which is a mechanical decision for the design session; and **the steel rim ring's finish**, which decides whether its bonding screw needs a masked spot or can rely on the star washer cutting through.
