# Radial — 3D models of the bought parts

Models of every component on the v8 buy list, as STEP files, for building the device
around in Fusion 360. Researched and built 4 September 2026.

## Read this first

Three vendors publish real 3D models. Everything else here I built from the
manufacturer's dimensioned drawing. Where a manufacturer does not publish a
dimension, I have not invented one — the gaps are listed below, part by part, and
the worst of them affects the gimbal motor, which is the part your whole stack
hangs off.

Nothing in this folder should be treated as a substitute for measuring the part
once it is on your bench. These are design references, not verified geometry.

## How the files are set up

- Millimetres, Z up.
- Round parts: the axis is Z through the origin.
- Parts that sit on a circuit board: **z = 0 is the top surface of the board**, so
  pads and lead feet sit at z = 0 and any through-hole leads run below it.
- Everything else: z = 0 is the face the part seats on.
- Each file is an assembly of named bodies, so you can see which surfaces rotate,
  which are adhesive, and which are reference volumes rather than material.
- No two solid bodies inside a file overlap, so Fusion will not report interference
  against the part with itself.

Bodies with these words in their name are **reference volumes, not material** —
delete them once you have used them:

| Name contains | What it is |
|---|---|
| `_ENVELOPE` | the space the part occupies, where the real shape is not published |
| `_keepout` | space that must stay clear (servo stroke, speaker lead exit) |
| `board_cutout_REQUIRED` | the notch you must cut in your circuit board |
| `reflective_gap` | the air gap the encoder needs to its code strip |
| `sensitive_area` | where the light sensor actually looks |
| `_ASSUMED` | I made this shape up because nothing is published |

---

## The three gaps that matter

### 1. The gimbal motor is an envelope only

The motor is the **JD-Power MY-3514C 2804**. The only dimension published for it
anywhere is the shop's size designation, "35x14mm". JD-Power's page carries no
specification table and states that all parameters are customisable, and no
dimensioned drawing has been retrieved for this part. So
`JD-Power_MY-3514C_2804_gimbal_motor.step` is a plain Ø35 × 14 cylinder and
nothing more — no hollow bore, no locating boss, no bolt patterns, no split
between the stationary base and the rotating bell.

Treat it as a keepout, not as the part. In particular, **Ø35 × 14 is probably
generous**: on JD-Power's sister part the DC-2813C, the same style of "28x13"
designation turns out to be **Ø27.5 ±0.1 × 13 ±0.2** on the manufacturer's own
drawing. The real 3514C body may well be nearer Ø34.5.

A proper drawing does exist for the 2813C, embedded as an image inside its
product page on jdpowersky.com rather than linked anywhere. The equivalent for
the 3514C is likely to be on `p-info.aspx?cid=1&id=46`, and finding it would
give the bolt patterns and the bore.

### 2. The clutch servo has no drawing at all

AGFRC publishes "21.4 × 15.2 × 6.0 mm", 1.5 g and 9 mm of stroke. That is the entire
mechanical specification. No drawing, no 3D model, no mounting lugs, no hole
positions, no pushrod diameter, and no statement of which body axis each of those
three numbers belongs to.

`AGFRC_C1p5CLS_PRO_linear_servo.step` therefore contains a plain 21.4 × 15.2 × 6.0
block, plus a pushrod and a stroke volume I invented so you have something to design
against. Both are named `_ASSUMED`. I have put the 21.4 along the stroke axis, which
is the sensible reading for a linear servo, but AGFRC does not say so.

This part drives your eccentric clutch. It is worth buying one before committing the
carriage geometry.

### 3. Two published dimensions contradict themselves

- **Speaker height.** Soberton's 2D drawing totals **9.05 mm**. Soberton's datasheet
  and product page both say **8.5 mm**. Both are Soberton documents. I modelled 9.05,
  the larger, so your cavity is never short. Your rim-ring cavity is 9.8 mm, so even
  at 9.05 it still fits, with 0.75 to spare rather than 1.3.
- **USB-C mid-mount offset.** GCT's Rev A1 drawing dimensions **2.10 mm**; GCT's own
  specification document says **2.0 mm** on all eleven pages. I used 2.10, from the
  drawing, which is the later document and the one that actually carries the dimension.

---

## One thing to change in `params.py`

`LRA_D, LRA_H = 10.0, 3.6` with the comment that the VLV101040A is 10 × 10 × 4.

Vybronics' drawing dimensions the metal can at **4.05 ± 0.05**, not 4.0, and the part
ships with a 0.25 mm Poron cushion bonded to the top face and 0.07 mm of double-sided
tape on the bottom. The real installed stack is **4.37 mm**, not the 4.0 your
reference block currently allows. It is only 370 microns, but it is in a cavity you
have already described as fully committed.

---

## The files

### Models the manufacturer publishes

| File | Source |
|---|---|
| `Waveshare_ESP32-P4-WIFI6-Touch-LCD-3.4C/*.stp` | Waveshare's own 33 MB STEP assembly, untouched. Also included: their DXF and dimensioned PDF. |
| `Soberton_SP-4005-1_vendor_mesh/*.obj` | Soberton's own 3D model. It is a mesh, not solid geometry — Soberton's viewer offers STEP but serves this. Use it to see the real cone profile, which no 2D drawing dimensions. |

**Note on the Waveshare file's origin:** it arrives with the disc centred on the
origin and Z running −11.75 to +3.75, so the front glass is at z = +3.75 and z = 0
sits inside the disc rather than on a face. I have left it exactly as Waveshare
shipped it rather than re-cutting a vendor model. In your stack the front glass is at
z = 34.30, so the file drops in at **z = +30.55**.

### Models built from published drawings

Grouped by the mechanism each part belongs to.

#### Dial — rotation, drive and position

| File | What it is | Key dimensions | Confidence |
|---|---|---|---|
| `623ZZ_3x10x4` | deep-groove ball bearing, shielded, ×3 — carries the rotating dial | 3 × 10 × 4, chamfer 0.15, inner shoulder Ø4.8, shield seat Ø8.2 | published in full |
| `JD-Power_MY-3514C_2804_gimbal_motor` | brushless gimbal motor — generates the detents and force feedback | Ø35 × 14 | envelope only; a size designation, not a toleranced dimension |
| `TMC6300-LA-T_QFN20_3x3` | three-phase motor driver — runs the gimbal motor | 3 × 3 × 0.85, 20 pins at 0.4, thermal pad 1.7 | published in full |
| `MT6701CT-STD_SOP8` | magnetic angle sensor — commutation, sits in the motor's hollow shaft | 4.9 × 3.9 body, 6.0 lead span, 1.45 tall | published in full |
| `MT6701_diametric_magnet_D6x2p5` | diametrically magnetised magnet — what that sensor reads | Ø6 × 2.5 | the magnet the sensor's datasheet specifies |
| `Broadcom_AEDR-8300-1K2` | reflective optical encoder — reads the code strip on the knob bore, and closes the haptic loop | 5.12 × 3.96 × 1.63, six pads, 1.96 row pitch, 2.0 mm typical gap | published in full |

#### Clutch

| File | What it is | Key dimensions | Confidence |
|---|---|---|---|
| `AGFRC_C1p5CLS_PRO` | linear servo — throws the eccentric clutch that switches detent modes | 21.4 × 15.2 × 6.0, 9 mm stroke | envelope only |

#### Haptic feedback

| File | What it is | Key dimensions | Confidence |
|---|---|---|---|
| `Vybronics_VLV101040A` | linear resonant actuator — the vibration you feel | 10 × 10 × 4.05 can, 13.9 overall with the flex tail, tape 0.07, cushion 0.25 | published in full |
| `TI_DRV2605L_VSSOP10_DGS` | haptic driver, ten-pin — drives that actuator | 3 × 3 body, 4.9 lead span, 1.1 tall | published in full |
| `TI_DRV2605L_DSBGA9_YZF` | haptic driver, nine-ball chip scale — same part, smaller package | 1.44 square, 0.625 tall, nine balls at 0.5 pitch | published in full |

#### Audio

| File | What it is | Key dimensions | Confidence |
|---|---|---|---|
| `Soberton_SP-4005-1_D40` | loudspeaker | Ø40 flange, Ø38/Ø35.5 front ring, Ø36.25 rear, Ø16.2 boss, 9.05 tall | drawing; height disputed |
| `ESS_ES9219Q_WQFN40_5x5` | digital-to-analogue converter with headphone amp | 5 × 5 × 0.75, 40 pins at 0.4, thermal pad 3.79 | published in full |
| `Switchcraft_35RAPC4BH3_3p5mm` | 3.5 mm stereo jack, panel-mount | body 14.0 × 11.5 × 6.0, M6 × 0.5 bushing out 3.5, five blade pins | published; axis height derived |

#### Halo and ambient light

| File | What it is | Key dimensions | Confidence |
|---|---|---|---|
| `OPSCO_SK6812SIDE-A_4020` | addressable RGB LED, side-emitting — about 90 of them on a flexible ring, firing down onto the desk | 4.0 × 1.6 footprint, 2.0 tall, side emitting | published; window position not published |
| `Vishay_VEML7700-TR_` | ambient light sensor — halo and screen track the room | 6.8 × 2.35 × 3.0, four leads at 1.27 pitch | published in full |

#### Power and ports

| File | What it is | Key dimensions | Confidence |
|---|---|---|---|
| `GCT_USB4520-03-0-A` | USB-C receptacle, mid-mount — power and data | 6.5 × 8.94 × 3.16, hangs 2.10 below the board, 9.24 × 6.20 board notch | published; offset disputed |
| `Abracon_AHCR-S04R0SA206Q_20F` | 20 F supercapacitor ×2, in series for 10 F at 8 V — rides out the motor's current spikes | Ø8 × 12 can, leads Ø0.6 at 3.5 pitch | can published; lead lengths are minima only |

Your buy list calls the DRV2605L a small chip-scale package. Texas Instruments ships
it in two: a 1.44 mm ball-grid part and a 3 mm ten-pin part. Both are here. The
ten-pin one is the only one you can hand-solder.

### Two details worth using

- **`Vishay_VEML7700...` contains `sensitive_area_0p336sq`.** The light sensor's
  sensitive area is 1.95 mm above the seating plane, not at the package's mid-height,
  and Vishay's application note calls this out specifically because people get it
  wrong. Line your aperture up with that body, not with the package centre. Aperture
  width is 0.5 + 2 × (1.43 × d), where d is the distance from the sensor face to the
  outer surface of your window — so a 1.5 mm thick wall wants a 4.8 mm hole.
- **`MT6701_diametric_magnet_D6x2p5`.** The commutation sensor's datasheet asks for a
  Ø6 × 2.5 magnet magnetised across its diameter, sitting 0.5 to 2.0 mm above the
  chip, 1.0 typical. The MY-3514C's bore is not published, so confirm the
  magnet fits before committing to this sensor.

---

## Regenerating

`build_parts.py` builds all seventeen models with build123d, the same library your
`the60_v8` source uses. Every dimension is a named constant at the point of use with
its source in the comment above it. Two reasons you will want it:

1. When JD-Power's dimension drawing for the 3514C turns up, or you measure the
   motor yourself, put the bore and bolt patterns in and re-cut the file.
2. If the Soberton or GCT contradictions get resolved, change one number.

```
pip install build123d
python build_parts.py
```

## Sources

Gimbal motor: [JD-Power MY-3514C](https://jdpowershop.com/?product=jd-power-my-3514c-2804-outer-rotor-hollow-shaft-gimbal-brushless-motor) ·
Servo: [AGFRC C1.5CLS PRO](https://www.agfrc.com/index.php?id=2438) ·
Bearing: [SKF 623-2Z datasheet](https://documents.klium.com/266479f7-c35f-4368-affe-6884164580ed/en/technical-data-sheet-skf-623-2z-623--2z-en.pdf) ·
Display: [Waveshare 3D package](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-TOUCH-LCD-3_4C.zip) ·
Speaker: [Soberton drawing](https://www.soberton.com/wp-content/uploads/2019/05/SP-4005-1.pdf), [datasheet](https://www.soberton.com/wp-content/uploads/2019/05/SP-4005-1-29-June-2018.pdf) ·
Buzzer: [Vybronics VLV101040A](https://www.vybronics.com/wp-content/uploads/datasheet-files/Vybronics-VLV101040A-datasheet.pdf) ·
Jack: [Switchcraft 35RAPC__H3 Rev J](https://www.switchcraft.com/assets/1/24/35rapc__h3_cd.pdf) ·
Encoder: [Broadcom AV02-0088EN](https://docs.broadcom.com/doc/AV02-0088EN) ·
Light sensor: [Vishay 84286](https://www.vishay.com/docs/84286/veml7700.pdf), [application note 84323](https://www.vishay.com/docs/84323/designingveml7700.pdf) ·
USB-C: [GCT USB4520 drawing](https://gct.co/files/drawings/usb4520.pdf) ·
Supercapacitor: [Abracon AHCR-S04R0S](https://abracon.com/datasheets/AHCR-S04R0S.pdf) ·
Halo LED: [OPSCO SK6812SIDE-A](https://www.ledlightinghut.com/files/SK6812SIDE-A-001.pdf) ·
Motor driver: [TMC6300 Rev 1.04](https://www.mouser.com/datasheet/2/256/TMC6300_Datasheet_V104-2066968.pdf) ·
Angle sensor: [MT6701 Rev 1.8](https://uelectronics.com/wp-content/uploads/2026/01/AR4799-MT6701-Encoder-Magnetico-14-Bits-Datasheet.pdf) ·
Haptic driver: [TI DRV2605L](https://www.ti.com/lit/ds/symlink/drv2605l.pdf) ·
Digital-to-analogue converter: [ESS ES9219 v1.2](https://www.esstech.com/wp-content/uploads/2022/09/ES9219-Datasheet-v1.2.pdf)

Abracon publishes a STEP file for the supercapacitor at
`abracon.com/Support/STEP/AHCR-S04R0S.STEP.zip` but their firewall refuses automated
requests. It will download fine in a browser if you want the real one — the part is a
plain can, so the model here is unlikely to differ.
