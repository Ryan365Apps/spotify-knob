# the 60 — the connector family

**Date: 6 September 2026. Status: decision proposed, for the decision index.** Closes the question raised in `SYSTEM-REVIEW.md` 1.2 and left open in `BOARD-CARRIER.md` §11, `BOARD-AUDIO.md` §8 and `BOARD-MOTION.md` §10.

**Decision: Molex Pico-Lock 1.50 mm, right-angle, for every crimped connection in the object.** Three deliberate exceptions, listed in section 4.

---

## 1. What the choice has to satisfy

| Requirement | Why |
|---|---|
| **Mated height under about 5 mm** | The boards sit on the mezzanine deck with roughly 6 mm from their top face to the ceiling (`V11.md` height stack: boards from z 21.98, ceiling 29.5) |
| **A positive latch** | Both board briefs already state the rule. The object gets picked up and carried |
| **2 A on one contact** | The motor phases, and the halo's power feed |
| **Real wire — AWG 24 or thicker** | A 5 A board feed and a motor phase cannot run on AWG 30 |
| **More than about 25 mating cycles** | See section 3. This is the requirement nobody wrote down |
| **Available crimped, or crimpable by a harness house** | Sixty units, built by one person |

---

## 2. What was specified, and why none of it works

From the vendors' own drawings:

| Specified in the briefs | Mated height | Current | Latch | Verdict |
|---|---|---|---|---|
| JST VH, top entry | 16.5 mm | 10 A | Yes | **Over four times the available height** |
| JST VH, side entry | 10.5 mm | 10 A | Yes | Still nearly twice the height |
| Molex Micro-Fit 3.0, vertical | 17.3–17.6 mm | 8.5 A | Yes | No |
| Molex Micro-Fit 3.0, dual-row right angle | 10.3 mm | 8.5 A | Yes | No |
| JST PH, top entry | 8.0 mm | 2 A | **No latch** | No, twice over |
| JST PH, side entry | 4.8 mm | 2 A | **No latch** | Fits, but breaks the briefs' own rule |
| JST GH, top entry | 7.3 mm | 1.0 A | Yes | Too tall, and too little current |
| JST GH, side entry | 4.35 mm | **1.0 A** | Yes | Fits — but the briefs use it for a 1.1 A halo feed, which is over its rating |
| JST SH (in the CAD's board envelopes) | 2.95–6.3 mm | 1.0 A | **No latch** | Banned by both briefs, still in the model |

**Every power connector named in the three board briefs is too tall.** And two rules in those briefs contradict each other: JST PH is recommended for the motor phases while the same section forbids friction-fit connectors — **JST PH has no positive latch.** Its datasheet lists a fully shrouded header and board retention, not a lock.

---

## 3. The specification nobody checked, and it disqualifies the obvious answer

My first recommendation was going to be **Molex Pico-EZmate Plus**, on the strength of its part page: 1.00 mm pitch, 1.20 mm mated, **2.8 A per contact**, locking. It looked ideal.

Molex's own [product specification](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/212/212132/2121321000-PS-000.pdf) says something different:

- **Rated current 1.8 A maximum on AWG 28** at six circuits, 1.5 A on AWG 30 — not 2.8 A. The part page's figure is a best case at the lowest circuit count.
- **Wire is limited to AWG 28 and 30.** A motor phase or a 5 A board feed cannot run on that.
- **Durability: 10 mating cycles.**

**Ten cycles is the number that matters and it is the one nobody was looking at.** A first article, a rework, firmware bring-up, a fit check, a service event — each connector in this object will be mated and unmated dozens of times before the first unit ships. A ten-cycle connector is worn out during development, and the failure it produces is intermittent contact on a motor sensor line, which is the hardest fault in this product to diagnose.

Molex's part page for this series also carries the note *"Limited Information Available. This part is not formally published to our online part catalog."* That alone should keep it out of a sixty-unit build.

Worth recording as a general lesson for the rest of the parts list: **the part page's headline current is a maximum under best conditions; the product specification's derating table is the number to design to.**

---

## 4. The decision

**Molex Pico-Lock 1.50 mm, right-angle**, for every crimped connection.

| Specification | Value |
|---|---|
| Pitch | 1.50 mm |
| **Mated height, right angle** | **2.00 mm** — four millimetres of clearance in a six-millimetre envelope |
| **Durability** | **30 mating cycles minimum** |
| **Wire** | **AWG 24 to 28** (a second terminal covers 30 to 32) |
| Current | 2 to 6 A per circuit depending on gauge and circuit count |
| Voltage | 150 V |
| Circuits | 2 to 12 |
| Latch | Yes — side positive locks |

It is the only part surveyed that clears every line in section 1 at once. It also removes a coupling: at 2.00 mm the connector choice no longer depends on how much height the deck leaves, so the board layout and the connector family stop constraining each other.

**Three exceptions, each for a stated reason:**

1. **The two internal USB links** (hub to audio board, hub to motion board) are **not a crimped connector**. A crimped contact and a loose wire is not a 90 Ω transmission line. Use a pre-made twisted-pair assembly under 150 mm, as both briefs already specify.
2. **The 5 V feeds into each board** use **paralleled contacts** — a four-way as two power and two ground on AWG 24. In production, when the boards bolt to the plate (`THERMAL-PLAN.md` §10), several of these should stop being cables at all.
3. **The vibration actuator** takes **spring contacts or pogo pins**, because its vendor warns against soldering wires to it. That is an enclosure feature, not a connector, and it still has no board to mount to — see `SYSTEM-REVIEW.md` 6.5.

---

## 5. What this changes

| Document | Change |
|---|---|
| `BOARD-CARRIER.md` §11 | Replace "JST GH for signals, JST VH or Micro-Fit for power" with Pico-Lock 1.50 right-angle throughout |
| `BOARD-AUDIO.md` §8 connector table | Same. The power inlet becomes a four-way Pico-Lock, not JST VH |
| `BOARD-MOTION.md` §10 connector table | Same. This also fixes the internal contradiction — JST PH was recommended for the motor phases under a rule forbidding unlatched connectors |
| `V11-SPECIFICATION.md` board envelopes | The motion board's connector allowance drops from "low-profile JST-SH, 5 mm tall" to 2.0 mm. Small, but it is height back |
| `SOURCING-BOM.md` | One connector family, plus the pre-made USB assemblies. Exact part numbers follow from the circuit counts once the interface list in `SYSTEM-REVIEW.md` §2 is settled |
| `DECISIONS.md` | Index this |

**Still open, deliberately:** the exact part numbers, which follow from the circuit count per interface; and **who crimps the harness.** At sixty units and roughly twenty cable assemblies, having the harness made is almost certainly cheaper than hand-crimping and far more reliable — the motion brief already says so. A harness house crimps whatever is specified with proper tooling, which is what makes a 1.50 mm pitch part a reasonable choice for a solo build.
