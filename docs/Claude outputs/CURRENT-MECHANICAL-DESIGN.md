# the 60 — current mechanical design

**This is the one document to read for how the 60 is built mechanically.** It is kept current: when the model changes, this changes the same day, and the change log at the bottom says what moved and why. Everything else (research answers, version read-mes, proposals) is history or evidence; if it disagrees with this page, this page wins.

| | |
|---|---|
| **Design version** | **v8, 3 September 2026** |
| **State** | Fully modelled and checked (0 failures, 0 warnings; pairwise interference across 17 bodies, knob clear at four angles, clutch releases). **Not yet printed** — no part has been in a hand. Nothing below has been proven on a bench. |
| **Files** | `docs/v8/` — `the60_v8.zip` holds every made part as STEP and STL, two assembly STEPs (clutch engaged / released), the GA drawing and the source. `V8.md` in the same folder is the print list and the open items. |
| **How a change is made** | Every dimension lives in one file, `v8/params.py`. Change the number, run `checks.py`, then `export.py` for the STEP/STL set and `drawings.py` for the GA. Nothing is edited by hand in CAD. |
| **Sourcing** | `docs/BOUGHT-PARTS-DIMENSIONS.md` — chosen parts in a table at the top, grouped by assembly, with dimensions, cost and links; alternatives kept below. |
| **Owner** | Ryan (Cadrane). Maintained with Claude. |

---

## 0. What v8 is, in one paragraph

**The detent is no longer mechanical.** v1–v7.1 made the clicks with steel and magnets and then had to invent a mechanism to switch them off. v8 deletes all of it. A **gimbal BLDC** presses against the inside of the knob and renders the feel electrically — 60 clicks, or 12, or 4, or none, or springs, end stops, strength that ramps toward the end of a list — all software on one torque. The same motor spins the knob, so the separate drive motor goes too. One small **eccentric clutch** on a micro servo lifts the motor clear for true free-spin. Fifteen bought part numbers and two whole mechanisms leave the design; one motor, one servo and 4.9 mm of height come in.

---

## 1. The object in numbers

| | v7.1 | **v8** | Note |
|---|---|---|---|
| Diameter | Ø125 | **Ø125** (knob), Ø123 (plate), Ø122 (pad) | unchanged |
| Height | 34.3 mm | **39.2 mm** including the 1.5 mm pad; knob top at 37.7 above the plate's underside | Limit 40; 45 is failure. **This is 0.8 mm under the limit** — see open item 6 |
| Knob share of the side | 71 % | 30.6 of 37.7 mm = **81 %** | Must be at least two thirds |
| Picture | Ø87.6 | **Ø87.6** visible; the knob's lip reaches in to Ø89.0 | The lip covers the display's dead border |
| Display | assumed | Ø115 × 6 disc, board 85.5 × 65 **offset 4.5 mm** from the disc centre, 15.5 mm total depth, 4 × M4 on **Ø106.07** | Waveshare ESP32-P4 3.4C, from the published STEP — no longer assumed |
| Clicks | 60, magnetic, fixed pattern | **any pattern, rendered** — 60, 12, 4, none, springs, ramps | The product's name is now a default, not a mechanism |
| Detent torque | 60–150 mNm | **171–284 mNm available** at the knob | 2.90 : 1 up from the motor's 59–98 mNm |
| Mass | 321 g made parts | **348 g** made parts (205 g steel plate; knob 79.5 g PETG / **169 g** aluminium) plus display, motor and hardware | At least 250 g, low |
| Halo | z 6–9 | **z 3.5–6.5**, 3 mm tall, opal, full 360° | Dropped so the motor bell clears it |
| Sockets | USB-C + 3.5 mm jack at 90° | unchanged | Face away from the user |
| Bearing | three 623ZZ in V-collars | **unchanged**, moved to 60/180/300° | |
| Self-turning | separate motor + lift-off tyre | **the same gimbal**, 174 rpm for 1 rev/s against ~2,100 free-run | |

Coordinates used everywhere: **z** is height above the steel plate's underside (the pad is below zero); **r** is radius from the centre; azimuth 0° is +X, 90° is the back where the cable leaves, angles run anticlockwise seen from above.

---

## 2. How it works, mechanism by mechanism

### 2.1 The knob and what carries it

The knob is **one piece**: a cup Ø125 across and **30.6 mm** tall (was 23.2 — it grew because the motor sits under the display and pushes everything up). Its top is a 3 mm lip reaching inward to Ø89 with a 2.5 × 45° chamfer outside and a 1.0 × 45° at the glass; its side carries the diamond knurl; its skirt hangs down outside the base to 7.1 mm above the plate, leaving a 0.6 mm dark shadow gap over the halo. Inside, the bore is a plain cylinder, **Ø116**, 0.5 mm clear of the Ø115 display all round.

**The bore is now smooth.** There are no ball pockets, no peg holes, no seams, no inserts and no screws anywhere on the knob. Three things use the bore, from the bottom up: the **drive band** (z 7.5–16.2, 8.7 mm of it) that the motor bell runs against; the **code band** (z 19.0–22.0) with the bonded reflective strip the encoder reads; and the **V-groove** (z 24.3–27.5) the wheels ride in — 90° included, 1.3 mm deep, with a 0.6 mm flat at the root so contact is on the flanks only.

In the prototype the knob is printed in PETG top-face-down with no supports; in production it is CNC-turned 6082 aluminium, bead-blasted, Type III hardcoat black, top chamfer diamond-cut bright after anodising and sealed. **Aluminium mass is now 169 g, up from 118 g**, because it is 7.4 mm taller. That is good for the flywheel feel but see open item 4.

The knob sits on **three wheels at 60°, 180° and 300°**, each a 623ZZ bearing (3 × 10 × 4) pressed into a turned Ø13.2 collar whose rim is a convex 90° V. V-on-V locates the knob radially and axially at once and takes the lift-off load, so the knob cannot be pulled off. Each wheel's pin is offset 0.9 mm on an **eccentric bush** (Ø5, Ø7 flange **0.6 mm thick** resting on a post, 2 mm hex socket underneath). Pin turned inward, the wheel sits 0.57 mm inside the bore and the knob drops on; half a turn from underneath seats it in the groove and sets the preload.

*Why 60/180/300 and not 0/120/240:* the display board is not concentric with the disc — it is offset 4.5 mm in +x. At 0° the board reaches r 47.25 and fouls the wheel post; at 180° it only reaches r 38.25. 60/180/300 is the only 120°-spaced set where the board is inside r 46 at all three posts. The three M3 plate screws were moved to the same azimuths so posts and screws share structure.

### 2.2 The clicks — rendered, not built

An **iPower GM3506** gimbal motor (Ø40 × 17.8, 24 slots / 22 poles, 5.6 Ω, 59–98 mNm) stands on the rubber pad at azimuth 0°, r 38, **through a Ø44 hole in the steel plate** — it costs no plate thickness, only the height above it. A rubber band (0.6 mm, Shore 40–70) on its bell runs against the knob's bore between z 7.5 and 16.2.

The ratio is **2 × 58 / 40 = 2.90 : 1** in the knob's favour: the bell is small and the bore is large, so the motor's torque is **multiplied**, not divided. 59–98 mNm at the motor becomes **171–284 mNm at your hand**, against a 60–150 mNm detent target. There is margin, not a shortfall.

Everything the old mechanism did, and several things it could not, are now one control loop reading the encoder and commanding torque:

| Feel | How |
|---|---|
| 60 clicks per turn | a sawtooth restoring torque with a 6° period |
| 12, or 4, or 24 | change the period — no hardware knows the difference |
| No clicks | command zero torque, or release the clutch |
| Click **strength** 0–100 % | scale the torque; continuously variable, per click |
| Detents that stiffen toward the end of a list | scale the torque as a function of position |
| End-stop walls | a hard spring past a limit |
| Springs, return-to-centre, viscous damping | it is the same loop |
| Turning itself, full rotations | drive the same motor open-loop or to a target |

### 2.3 The clutch — how the motor gets out of the way

Rendered detents are not free-spin. A motor pressed against the bore always has cogging, friction and back-EMF drag, and the GM3506 is 24N22P specifically because that combination gives **264 cogging cycles per turn** (against 84 for every 12N14P rival at this size), which is the smoothest available. Even so, "no detents" and "the knob spins like a bearing" are different things, and the second one needs contact removed.

The motor sits on a small carriage. Under it is an **eccentric** — a bush whose pin is 1.2 mm off centre — turned by a micro linear servo (AGFRC C1.5CLS PRO, 21.4 × 15.2 × 6.0, 9 mm travel, 2.4 N) at azimuth 225°, r 38. Half a turn of the eccentric moves the motor **2.4 mm** radially inward, and the bell leaves the bore completely.

**It holds both states with no current.** The eccentric is near top-dead-centre when engaged: the 5 N contact force pushes almost straight down the crank, with almost no lever arm to turn it back. A light spring supplies the preload; the servo only flicks the eccentric between the two stable positions. Idle current, engaged or released, is zero.

### 2.4 Reading the angle

Unchanged from v7.1: a **Broadcom AEDR-8300** reflective optical encoder on a tower on the ledge at 60° looks outward at the code band on the bore, 2 mm away — about 2,585 stripes, ~10,300 counts per turn, one index mark. Optical, so nothing magnetic disturbs it. It is now doing more work than before: it closes the loop that makes the detents, so its resolution and latency are directly the haptic quality. The GM3506's hollow Ø8.6 shaft would also take a magnetic encoder (MT6701) for commutation of the motor itself.

### 2.5 The halo

A ring of addressable LEDs on a flexible board on the outside of the base's LED wall (r 55.5–57.0), firing outward into an **opal diffuser ring** — Ø117 inside, Ø123.2 at the bottom to Ø125 at the top, 3 mm tall — leaning out so the light lands on the desk. Full 360°; the cable tunnel passes underneath it at the back.

**It dropped to z 3.5–6.5** (was 6–9). The motor bell's underside is at z 6.8, so the halo had to get out from under it. That leaves only a 0.5 mm plinth band below the halo instead of 3 mm — the dark band under the light is now nearly gone, which is a look change, not just a number (open item 7).

### 2.6 The base

**Steel plate.** Ø123 × 3 mm mild steel, laser-cut, powder-coated black, about 205 g: the ballast and the floor. Through-cut in one pass: the **Ø44 gimbal hole** at az 0 r 38, the **Ø36 speaker aperture offset −6 mm** from centre (pushed away from the motor), three countersinks at 60/180/300° r 40 for the M3 shell screws, the 34 mm rear notch for the cable tunnel, the port-board pocket and a pocket for the clutch servo. A full-face Ø122 × 1.5 rubber pad is bonded underneath; the motor, servo and port board stand on the pad through their holes, which is how they cost no height.

**Base shell.** One printed part (PA12 MJF in production) screwed to the plate from below into three M3 heat-set inserts. From the bottom up: a 0.5 mm plinth band; the LED wall; the **ledge** (r 49–57.6, z 16.6–18.4) carrying three Ø8 wheel posts with Ø5.1 bush bores and four Ø6.8 M4 display bosses on Ø106.07 at 45/135/225/315°; an inner roof clearing the board's components; the speaker cradle; the encoder tower; the motor carriage pocket and the servo pocket. **The six magnet-tower slots are gone**, so the ledge is a continuous ring — much stiffer than v7.1's. Floor ribs at seven azimuths and an inner wall skin keep the shell a single solid.

**Ports and audio.** A 40 × 14 port board on the pad at 90° carries mid-mount USB-C, the 3.5 mm jack and the DAC. Speaker: 40 mm Soberton SP-4005-1, down-firing, **offset −6 mm** so it clears the motor. Buzzer at 130°, r 34. Two supercapacitors at 285°, r 30 — moved from 105/119° where they clashed with each other. Light sensor at 110°.

### 2.7 Where everything is

Height stack, z from the plate's underside: −1.5–0 pad · 0–3 steel plate · **0–17.8 the gimbal, standing on the pad through the plate** · 3–3.5 plinth · 3.5–6.5 halo · 6.8 bell underside · 7.1 knob skirt bottom · 7.5–16.2 the drive band on the bore · 16.6–18.4 ledge · 18.8 lowest board component · 19.0–22.0 code band · 23.9–27.9 wheels · 24.3–27.5 groove · 25.2–26.8 main PCB · 28.3–34.3 display disc · 34.7–37.7 knob lip.

Around the circle: **gimbal 0°** (r 38) · wheels, plate screws **60/180/300°** · display bosses 45/135/225/315° · encoder 60° · cable tunnel and ports 90° · light sensor 110° · Buzzer 130° · **clutch servo 225°** (r 38) · supercaps 285° (r 30) · speaker centre offset −6 mm on the 0° axis.

---

## 3. Parts

### Made parts

| No. | Part | Qty | Prototype | Production | What it is |
|---|---|---|---|---|---|
| 60-08-01 | Base plate | 1 | printed stand-in | laser-cut 3 mm steel, powder-coated | ballast and floor; Ø44 motor hole, Ø36 speaker aperture |
| 60-08-02 | Base shell | 1 | PETG | PA12 MJF | the fixed body; continuous ledge, no tower slots |
| 60-08-03 | Halo diffuser | 1 | natural PETG | opal PMMA | the light ring, dropped to z 3.5–6.5 |
| 60-08-04 | Knob | 1 | PETG | CNC 6082, hardcoat | one piece: lip, skirt, knurl, groove — **smooth bore** |
| 60-08-10 | Wheel V-collar | 3 | PETG | POM, turned | convex V on a 623ZZ |
| 60-08-12 | Eccentric bush | 3 | PETG | brass, turned | sets and locks the wheels; flange thinned to 0.6 |
| 60-08-13 | Motor carriage | 1 | PETG | aluminium | holds the GM3506; rides the clutch eccentric |
| 60-08-14 | Clutch eccentric | 1 | PETG | brass, turned | 1.2 mm throw = 2.4 mm lift; over-centre when engaged |

**Deleted from v7.1:** 60-07-06 magnet ring A · 60-07-07 magnet ring B · 60-07-08 rocker · 60-07-09 drive arm · 60-07-11 tyre hub. (60-07-05 was the v7 crown, already deleted.)

### Bought parts

Full detail, prices and links in `docs/BOUGHT-PARTS-DIMENSIONS.md`. Per unit: the Waveshare 3.4C display and board · **iPower GM3506 gimbal motor** · **TMC6300 three-phase driver** · **MT6701 commutation encoder** (optional, in the hollow shaft) · **AGFRC C1.5CLS PRO micro servo** · 3 × 623ZZ bearings · AEDR-8300 encoder and code strip · DRV2605L and a 10 × 10 × 4 Buzzer · ES9219Q DAC, Switchcraft 35RAPC4BH3 jack · Soberton SP-4005-1 40 mm speaker · ~90 side-view addressable LEDs on a flexible ring · VEML7700 light sensor · GCT USB4520 mid-mount USB-C · right-angle braided USB-C cable · rubber pad · 3 M3 csk, 3 M3 inserts, 4 M4 × 6, 3 M2 × 4, 3 M2 grubs.

**No longer bought:** 6 × N42 magnets · 60 × Ø3 chrome-steel balls · Ø8 planetary gearmotor and worm · drive motor · 2 mm O-ring · Ø6 push solenoid.

---

## 4. How it goes together

1. Base shell upside down. A bush into each of the three wheel posts from above, flange on the post top; bearing and collar onto the pin. Turn each bush so the pin points **inward** — wheels retracted.
2. Display screwed to its four M4 bosses from below.
3. Knob lowered over the display and the retracted wheels; the straight, now perfectly smooth bore clears everything. (No balls to press in first — that step is gone.)
4. From underneath, half a turn on each bush so the pin points outward; the collars seat in the groove. Lock the bushes.
5. LED board outside the LED wall, diffuser over it.
6. Motor onto its carriage, carriage onto the clutch eccentric, servo into its pocket; band over the bell. Set the eccentric to engaged (over-centre) and check the 5 N preload.
7. Port board, speaker, Buzzer, supercaps into their pockets on the pad; plate on, three M3 countersunk from below.

Everything is re-openable in reverse. No glue anywhere. **Step 1 of v7.1 — the two magnet rings, six towers through six slots and the rocker — no longer exists.**

---

## 5. Mechanical requirements in force

The requirements from v7.1 §5 stand unchanged except where the architecture removed the thing they governed. The requirements that **died with the mechanical detent** are listed here so nobody reinstates them:

**Retired 3 September 2026 with the mechanical detent:** the click must be magnetic and contactless · the clicks must cost no power at idle (they now cost motor current whenever a click is being rendered — see open item 8) · click-to-click uniformity within 10 % by magnet matching (now a software property) · the six magnets must be sorted by pull before fitting · the clicks-off state must cancel to zero (there is nothing to cancel) · the two-phase-vs-three-phase-vs-radial-retraction question (moot) · the peg wall thickness rule · the ball concentricity rule (±0.05 on the peg circle).

**Still in force and now more important:** the knob clears every static part by at least 0.4 mm · the bore is concentric to the groove within 0.05 total, because **runout now modulates the drive preload** and therefore the rendered torque · rim back-play a fraction of a millimetre · Ø125, under 40 mm, knob at least two thirds of the side, at least 250 g and low · the halo is on the fixed base and never on the rotating part.

**Standing working rule (Ryan, 3 September 2026): the part determines the design, not the other way round.** Source the part first, then place it. No layout is built around an envelope that has not been found for sale. v8 was built this way and it is why the architecture changed.

**Deliverable rules D1–D3 (Ryan, 3 September 2026), met by v8:** the package contains a **single assembly STEP with every component named and in its assembled position** (`the60_v8_assembly.step`, 20 named components — open that in Fusion, not the individual parts); a second STEP shows the alternate state (`..._clutch_released.step`); the parts in `parts/` are in print orientation and will not assemble themselves.

---

## 5h. History — the mechanisms v8 deleted, and why

Kept because the reasoning is still worth having, not because any of it is live.

- **v6 lifted a single magnet carrier 3 mm** to switch the clicks off. Research showed that leaves **52 %** of the click. Killed the lift.
- **v7 replaced it with a differential carrier**: two rings 3° apart so group A pulls in as group B pulls out. In principle zero; in practice a half-pitch shift cancels the odd harmonics but **doubles the even ones**, leaving a modelled **6–33 %** residual (1–7 % if a third phase is added). That number was never measured, and v8 made the measurement unnecessary.
- **Radial retraction** was the better mechanical answer that never got built: pulling the magnet from a 0.8 to a 2.0 mm gap leaves 12 % of the click, needs only 1.2–1.7 mm of travel, is monotonic and continuously variable. Six radial sliders on a cam ring. If the gimbal ever fails on the bench, this is the fallback.
- **Electromagnets were out by an order of magnitude.** 318 amp-turns per magnet across the gap, ~8–12 W for six continuously (an earlier figure of 32.5 W was inflated by forcing the coil into an unnecessarily small window — the conclusion held, the margin was 3× smaller than stated).
- **Electropermanent magnets were genuinely viable** and nearly won: AlNiCo 5 beside N42 between iron poles, ~806 amp-turns, 45 mJ per switch, **270 mJ for all six**, ~4.5 mW average, zero at idle — and strength control comes free from pulse width. Two things stopped it: **AlNiCo 5 self-demagnetises in an open circuit** (Knaian measured holding force halving after one 0.75 mm excursion; our gap is permanent), and **nothing is sold at this size** — 360 hand-wound assemblies for a 60-piece run.
- **The finding that reset everything:** the "3 mm lift leaves 52 %" constraint was measured on the *old 6 mm-tall* magnet. A Ø3 × 6 rod lying flat is 3 mm tall, so 3 mm of lift leaves **7.8 %**. That constraint died with the magnet it was measured on — and with it the belief that there was no room for a motor, which is what opened the door to the gimbal.
- **The bay scheme** (six 60° bays between the magnet arms, wheel towers at 2:30/6:30/10:30, port board at 12) organised the v7.2 floor. The arms are gone, so the bays are gone; the floor is now an open disc with a motor at 0° and a servo at 225°.
- **Checker gap, found by the supercap clash:** two Ø8 × 12 cells 14° apart interpenetrated by 2.88 mm and no test caught it, because both were built into one reference shape and the pairwise test never compares a part with itself. **Any reference representing more than one physical object must be exported as separate named parts.** Still open — see item 9.

---

## 6. Open items — what the bench has to settle, in order of how much they can move the design

1. **Cogging of the GM3506.** 24N22P gives 264 cogging cycles per turn against 84 for every 12N14P rival — the strongest smoothness argument available at this size. **Nobody publishes a number.** Hand-feel it against a SmartKnob motor (SparkFun ROB-20441) before committing. This is the single thing that decides whether v8 feels like a product or a prototype.
2. **The rubber band is a torsional spring** between motor and knob, and it is the likely limit on how sharp a click can feel. Shore 40 versus Shore 70 on the rig.
3. **Slip.** 5 N of preload carries 150 mNm at μ = 0.5, which is below the 171–284 mNm the ratio makes available — so the band, not the motor, may set the ceiling. Measure the real μ on anodised aluminium and on PETG.
4. **Knob mass** 169 g in aluminium, up from 118. Good for the flywheel, but if it feels heavy, hollowing the crown takes some back.
5. **Encoder latency.** The AEDR-8300 loop is now the haptics. Measure the delay from stripe to torque; anything over a few milliseconds will be felt as mush.
6. **Height, 39.2 mm — 0.8 mm from the limit.** Ryan approved "3.5 mm is fine"; the true increase is **4.9 mm**. If that is too much: the CubeMars GL30 (Ø34.5 × 15.7) saves 2.1 mm but is 12N14P; the JD-Power DC-2813C (Ø28 × 13) saves 4.8 mm but publishes no electrical specs at all.
7. **The halo's dark band.** Only 0.5 mm of plinth is left below the light, against 3 mm in v7.1. Look at it lit before accepting.
8. **Idle power.** The old detent cost nothing at rest. A rendered detent costs current whenever it is holding you against a click face. Measure the resting draw with a finger on the knob and decide whether the clutch should release on inactivity.
9. **Multi-cell reference parts (checker gap).** Split every multi-object reference into separately named parts and test the cells against each other. Fewer offenders in v8 than v7.1, but the blind spot is unfixed.
10. **Port board** is still an invented 40 × 14 × 1.6 envelope. Derive it from the real USB-C, jack and DAC.
11. **Display board.** The 4.5 mm offset, Ø106.07 M4 PCD and 15.5 mm depth now come from Waveshare's published STEP rather than assumption — but verify against the real board, because the wheel azimuths depend on the offset.
12. **Eccentric bush lock** (printed bushes hold the knob preload; brass with an M2 grub in production) · **groove contact** (0.05 off the flanks; notchiness three times a turn means the collars are bottoming) · **encoder index strip** against printed runout · **vibration through the wheels**.

---

## 7. Change log

| Date | Version | What changed and why |
|---|---|---|
| **3 Sep 2026** | **v8** | **A different machine.** Mechanical detent deleted entirely — 60 balls, 6 magnets, both carrier rings, rocker, seat ring, ring gearmotor and worm, six towers and their slots, the separate drive motor, tyre hub, O-ring and lift-off solenoid: fifteen part numbers and two mechanisms. Replaced by one iPower GM3506 gimbal on the pad through a Ø44 hole in the plate, driving the bore at 2.90:1 (171–284 mNm at the hand), rendering any detent pattern in software and spinning the knob itself; one eccentric clutch on a micro servo lifting it 2.4 mm clear for free-spin, over-centre so neither state draws current. Height 34.3 → **39.2 mm**, knob 71 → **81 %** of the side, halo dropped to z 3.5–6.5 so the bell clears. Wheels and plate screws moved to 60/180/300° because the display board is offset 4.5 mm. Display numbers taken from Waveshare's STEP. Speaker offset −6 mm, supercaps to 285°. 0 failures, 0 warnings. Named assembly STEP delivered (D1–D3 met). |
| 3 Sep 2026 | v7.2 | Never built. Design freedoms F1–F6 granted, bay scheme adopted, catalogue-first sourcing rewrite, then the detent-switching question reopened and the architecture reset to v8. Its reasoning is preserved in §5h. |
| 2 Sep 2026 | v7.1 | Knob made one piece after Ryan rejected the screwed crown. Straight Ø116 bore so the display passes from below; V-groove replaces the ridge; wheels on eccentric bushes; Ø125; plate Ø124. 0 collisions. |
| 2 Sep 2026 | v7 | First build with every part printable and a drawing per made part. Ø123 (from 135); full 360° halo over a rear cable tunnel; differential magnet rings replace the 3 mm lift (research: lifting leaves 52 % of the click); lift-off friction-tyre drive replaces the ring motor; 623ZZ + collar wheels. Two-piece knob — superseded the same day. |
| 2 Sep 2026 | v6c | Proposal only: differential phase carrier, 360° halo, brighter halo, bearing-ready skirt. |
| 2 Sep 2026 | v6a.2 / v6b | Ø135 × 34, port block at 12 o'clock breaking the halo, printed carrier and cam ring with an N20 + worm. |
| 1 Sep 2026 | v1–v5 | Ø135; 6817 bearing around the display (59–78 mm tall); v5 tapered base and halo at 59.9 mm. All superseded by the CAD brief's 40 mm limit. |
