# the 60 — halo brightness: the decision, and why it is not a cap

**Date: 6 September 2026. Status: decision proposed, for the decision index.** Settles the question asked in `BOARD-CARRIER.md` (open question 8), `BOARD-MOTION.md` (open question 6) and `SYSTEM-REVIEW.md` — *"state the halo's brightness cap as a design number"* — which has been asked in three documents and answered in none.

**Requirement, as stated by Ryan, 6 September:** *"there are enough LEDs to make the device look cool, and they are bright enough to do so."* Plus a preference to keep the object passive — no blower — if it can be done.

**Decision: there is no sustained brightness cap. The halo is limited by a rolling average, not by a ceiling on brightness.** The halo may go to full white whenever the user is interacting with it. Firmware limits the **ten-minute mean** of estimated halo power, not the instantaneous frame. That satisfies the requirement as stated and costs the thermal design almost nothing.

---

## 1. First, a correction that changes the numbers

`V10-SPECIFICATION.md` 4.8 states the halo at full white as **1.0 A, 5 W**, from an assumed 0.1 W per LED. The WS2812B-2020 datasheet gives **16 mA per colour channel**, so **48 mA and 0.24 W per LED at full white** — 2.4 times the assumed figure.

| Strip | LEDs on the 465 mm circumference | Full white |
|---|---|---|
| 100 per metre, WS2812B-2020 | 46 | **2.21 A, 11.0 W** |
| 60 per metre | 28 | 1.34 A, 6.7 W |
| 144 per metre | 67 | 3.22 A, 16.1 W |
| 46 × SK6812 SIDE-A (the earlier discrete plan) | 46 | 1.69 A, 8.4 W |

So the halo at full white is a **7 to 16 watt device**, depending on a strip nobody has chosen yet. The specification's 5 W is wrong and low.

An irony worth recording so the correction is not made in the wrong direction: `V11.md` bench item 6 still carries **3.2 A**, inherited from the old 90-LED discrete design. That number was never right for this strip either, but it is much closer to the truth than the 1.0 A that replaced it.

---

## 2. Why a sustained cap is the wrong instrument

The object weighs about 1.2 kg, most of it metal. Its heat capacity is roughly **840 J/K**, and against a passive conductance of 0.5 W/K that gives a thermal time constant of **28 minutes**.

Skin temperature therefore follows the **half-hour average**, not the instantaneous load. An eight-watt burst of halo does this:

| Burst of +8 W | Skin temperature rise |
|---|---|
| 1 minute | +0.6 K |
| 3 minutes | +1.6 K |
| 10 minutes | +4.8 K |
| 30 minutes | +10.5 K |
| sustained | +16 K |

**A three-minute interaction at full brightness costs 1.6 K.** The same brightness left on permanently costs 16 K. It is the same halo. The difference is entirely duty cycle.

A fixed brightness cap throws that away — it makes the object permanently dimmer in order to survive a condition (full white, forever) that no real use produces.

---

## 3. What to do instead

**Limit the ten-minute rolling mean of halo power, in firmware, on the motion board.**

The mechanism already exists in the design: `BOARD-MOTION.md` section 6 specifies computing a per-frame current estimate by summing the frame's byte values. Feed that estimate into a rolling accumulator and scale global brightness down only when the *mean* approaches its budget. Instantaneous frames are never limited.

| Parameter | Value | Where it lives |
|---|---|---|
| Peak, instantaneous | **full white, unlimited** — 2.21 A on a 100/m strip | Sizes the converter, the wiring and the connector. Hardware number, fixed now |
| **Ten-minute rolling mean** | **2.0 W provisional** (about 400 mA) | Firmware constant on the motion board. Set properly after the measurement in section 5 |
| At rest, untouched | dim or ambient-matched, well under 1 W | Behaviour, not a limit |

**What 2 W of rolling mean actually buys**, which is the point:

| Behaviour | Rolling mean |
|---|---|
| Full white while interacting, 5 % of the time, 0.5 W at rest | 1.0 W |
| Full white while interacting, 10 % of the time, 0.5 W at rest | 1.6 W |
| Full white while interacting, 20 % of the time, 1.0 W at rest | 3.0 W |

So a **2 W budget allows the halo to be at full brightness for roughly one minute in eight, indefinitely**, on top of a dim resting glow. For a device that lights up when you touch it, that is not a constraint — it is more than the interaction pattern will use. And a halo that responds is better product behaviour than one that simply sits on.

---

## 4. The uncomfortable part: the halo was never the problem

The reworked sustained budget, **with the halo switched off entirely**:

| Load, sustained | Watts at 5 V |
|---|---|
| Compute module running real graphics | 6.0 (optimistically 4.5) |
| Panel, its rails and backlight | 2.0 |
| Motor rendering detents | 1.5 (optimistically 0.5) |
| Audio board | 0.7 |
| Motion board logic | 0.75 |
| Hub, touch, light sensor | 0.5 |
| Converter losses at 90 % | 1.3 |
| **Total, no halo at all** | **12.7 W** (optimistically 9.9 W) |

Against `THERMAL-PLAN.md`'s budgets: **9.0 W passive, 19.8 W ducted.**

**The object exceeds its passive budget with the halo switched off.** Capping the halo to zero would not make it passive. The compute module and the panel do that on their own.

This is not an argument against staying passive. It is an argument that **the halo is the wrong lever to pull**, and that the three real levers are elsewhere.

---

## 5. What "try to stay passive" actually requires

In order of size. All three are behaviour, none is a mechanism, and none costs brightness during use.

1. **The compute module is idle almost all the time, and the design should exploit that.** A desk dial spends the overwhelming majority of its life showing something static or slow. The 6 W figure is an animation running continuously. Set the processor governor so it idles genuinely low and clocks up on interaction, and the half-hour mean falls a long way below 6 W. Underclocking the ceiling is Raspberry Pi's own sanctioned mitigation and remains available on top.
2. **The panel and its backlight sleep or dim when untouched.** 2 W, continuously, for a screen nobody is looking at. The ambient light sensor should be driving this anyway.
3. **The halo on its rolling mean**, per section 3.

With all three, the half-hour mean plausibly lands near the passive budget rather than 3 to 4 W above it. **Plausibly is not the same as does**, which is why section 6 exists.

**And build the duct regardless.** `THERMAL-PLAN.md` rule 12 already reserves the blower's envelope and leaves the part unfitted. That is exactly the right posture for "try to stay passive": design for passive, build the duct, fit nothing, measure. If the measurement says no, the blower drops in without a plate respin. If it says yes, you have a silent object and an empty pocket nobody sees.

---

## 6. The measurement that actually settles this — two evenings

Neither of us should pick the brightness number from a desk. Two cheap tests decide it.

**Test A — how bright does it look? One evening.**

Buy two candidate strips (a 100 per metre 2020, and one denser or brighter alternative). Run each at a set of known currents behind a printed mock-up of v11's diffuser and its 11 mm light channel. Measure the diffuser's luminance with a phone light-meter application or a £30 meter, and — more importantly — **look at it**, in a dark room and in daylight.

Targets to judge against:

| Reference | Luminance |
|---|---|
| White paper on a desk in a 500 lux office | 110 cd/m² |
| Phone screen at a comfortable indoor brightness | 200 cd/m² |
| Phone at full brightness | 700 cd/m² |
| **What should read as clearly emissive in daylight** | **~300 cd/m²** |
| **What should read as present but not glaring in a dim room** | **~20 cd/m²** |

This gives the two numbers that matter: the current needed for the daytime maximum, and the current for the night minimum. The ambient light sensor interpolates between them.

**Note that v11 has already cost brightness and nobody has measured how much.** The light now crosses an 11 mm channel from a strip at r 74 to a diffuser at r 86.75, so the same light is spread over 1.17 times the length — about 85 % of the surface brightness from the geometry alone, before any loss in the channel. `V11.md` flags this as its own bench item 5. Test A covers both.

**Test B — what is the real sustained load? One evening.**

Log the 12 V inlet current for an hour of genuine use, with the display doing what it will really do and the motor rendering detents. Every watt at the inlet becomes heat in the object except the light that leaves it. This replaces every estimate in section 4 with a number, and it is the input to the passive-or-ducted decision.

**Do B before A.** If B comes back at 13 W, the halo's rolling mean is set by what is left over, and Test A tells you what that looks like. If B comes back at 9 W, the halo gets a more generous budget and Test A tells you whether it needs one.

---

## 7. What this changes in the other documents

| Document | Change |
|---|---|
| `V10/V11-SPECIFICATION.md` 4.8 | Halo full white corrected from 1.0 A / 5 W to **2.21 A / 11.0 W** on a 100 per metre 2020 strip, with the table in section 1 for other strips |
| `V11.md` bench item 6 | 3.2 A replaced by 2.21 A; the converter is sized for the **peak**, not the mean |
| `BOARD-MOTION.md` §6 and open question 6 | Closed: no fixed cap. Specify the **rolling-mean limiter**, ten-minute window, 2.0 W provisional, and the halo's power feed sized for 2.21 A peak |
| `BOARD-CARRIER.md` §8 and open question 8 | Closed: the halo's contribution to the sustained budget is **2 W**, its peak is 2.21 A |
| `SOURCING-BOM.md` | The strip is still unchosen; add the two candidates for Test A |
| `DECISIONS.md` | Index this decision |
| `THERMAL-PLAN.md` §8 | The passive-or-ducted choice now rests on Test B, not on the halo |

**Still open, and deliberately so:** which strip; the daytime and night-time current figures, from Test A; and the final rolling-mean budget, from Test B. None of these blocks the CAD or the board layout, because the hardware is sized by the peak and the rest is a firmware constant.
