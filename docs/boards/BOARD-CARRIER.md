# the 60 — board 1 of 3: the carrier board

**Date: 5 September 2026. Status: design brief, not yet drawn.** Written to be handed to a contract electronics designer with no further conversation needed to start. Everything here is sourced; anything a vendor does not publish is marked **not published**, and anything I concluded rather than read is marked **judgement**.

Companion documents: `the60-board-audio.md`, `the60-board-motion.md`, `the60-electronics-build-path.md`, `the60-processor-and-display-options.md`, `SOURCING-BOM.md`.

---

## 1. What this board is

The carrier holds the Raspberry Pi Compute Module 5 and everything that is not real-time and not audio. It owns the device's single connection to the outside world.

It carries: the compute module and its two 100-pin connectors; the internal USB hub; the external USB-C socket that goes to the computer; the mains power inlet and the 5 V distribution to the other two boards; the display connection; and the ambient light sensor.

It does **not** carry: the motor, encoder, halo or haptics (motion board), or any audio (audio board).

---

## 2. The topology — settle this before anything is drawn

This is the single most important architectural fact in the whole product, and it is not obvious.

```
                    ┌──────────────── inside the object, mains powered ───────────────┐
                    │                                                                  │
 PC ──USB-C cable──▶│ USB-C receptacle ──▶ USB 2.0 hub, upstream port                  │
    (data only,     │  Rd 5.1k x2 to GND   │                                           │
     no power       │  VBUS ──▶ divider ──▶│ VBUS_DET                                  │
     drawn)         │                      ├─ downstream 1 ─▶ CM5 pins 103/105         │
                    │                      │                  (keyboard + mouse + link)│
                    │                      ├─ downstream 2 ─▶ audio board              │
                    │                      └─ downstream 3 ─▶ motion board             │
                    │                                                                  │
                    │ CM5 USB 3.0 port 0 ─▶ (host) anything the CM5 owns itself        │
                    │ CM5 USB 3.0 port 1 ─▶ (host)                                     │
                    │                                                                  │
                    │ Mains PSU ─▶ 5 V ─┬─▶ CM5 (2.5 A)                                │
                    │                   ├─▶ hub                                        │
                    │                   ├─▶ audio board   (own pair of wires)          │
                    │                   └─▶ motion board  (own pair of wires)          │
                    └──────────────────────────────────────────────────────────────────┘
```

**Why it must be this way.** USB is a strict tiered star: one host at the root, hubs in between, functions at the leaves. When the compute module is acting as a keyboard it is a *function*, and a function has no downstream ports. So the compute module cannot sit between the computer and the other two boards. All three sit on the hub.

**The compute module can be a device and a host at the same time**, because these are different pieces of silicon. The USB 2.0 device-capable port is a Synopsys DWC2 core inside the BCM2712 itself, on **module pins 103 (USB_N) and 105 (USB_P)**. The two USB 3.0 ports are separate xHCI controllers in the RP1 chip, and Raspberry Pi's own RP1 peripherals datasheet says plainly that they **"do not support … Device-mode operation"**. They are hosts, permanently. So anything the compute module needs to own itself hangs off USB 3.0 and is invisible to the computer; anything the computer needs to see hangs off the hub.

**A second benefit that is easy to miss.** The compute module has no VBUS input pin anywhere in its 200 pins, and Raspberry Pi do not publish how its gadget controller decides a host is attached when the board is self-powered. With the hub in front, the hub's downstream port supplies VBUS to the compute module continuously from our own 5 V rail, so the module's attach state never changes and never needs to. When the computer is unplugged, the **hub** drops its upstream pull-up within ten seconds and the module never notices. This removes an undocumented behaviour from the critical path.

---

## 3. Settled parts

| Function | Part | Notes |
|---|---|---|
| Computer | **Raspberry Pi Compute Module 5**, 4 GB memory, 32 GB storage, wireless | 40 x 55 mm, 4.94 mm assembled on the 1.5 mm connector. In production until at least January 2036 |
| Module connectors x2 | **Amphenol 10164227-1001A1RLF** (1.5 mm stack, no clearance under the module) or **-1004A1RLF** (4.0 mm stack, 2.5 mm clearance) | Raspberry Pi specify these by part number. **Note this changed from the Compute Module 4's Hirose DF40** — do not fit the Hirose part the internet remembers. The tall option also changed from 3.0 mm to 4.0 mm |
| USB hub | **Microchip USB2514B**, four ports, USB 2.0 high speed, QFN-36 6 x 6 mm | Strap-configurable, no firmware. A USB 3 hub buys nothing: the module's gadget port is USB 2.0 only |
| External socket | **GCT USB4520-03-0-A** mid-mount USB-C, 3.16 mm tall, $0.518 at 100 | Already in the sourcing document |
| Display connector | **Hirose FH12-22S-0.5SH**, 22 way, 0.5 mm pitch | What the official Raspberry Pi board fits, and the footprint ships in their KiCad project |
| Light sensor | **Vishay VEML7700-TR**, $1.02 at 100 | Needs its own aperture — not behind the halo diffuser, which attenuates 50-65 % |

---

## 4. What the module needs to boot — the complete list

Raspberry Pi's own datasheet is unambiguous and the answer is pleasantly short.

**Power: one rail.** 5 V, 4.75-5.25 V, on **pins 77, 79, 81, 83, 85, 87**, rising monotonically. Nothing else.

**One mandatory strap.** **GPIO_VREF (pin 78)** must be tied to CM5_3.3V (pins 84/86) or CM5_1.8V (pins 88/90). The datasheet says "this pin can't be floating or connected to ground". It also sets the logic level of the general-purpose pins; total current across all 28 of them must not exceed 50 mA.

**No sequencing circuit is needed.** PMIC_Enable (pin 99) has a 100 kΩ pull-up to 5 V on the module, so leaving it unconnected starts the module as soon as 5 V is valid. The module brings up its own 3.3 V and then its 1.8 V at least 1 ms later, internally. There is no power-good input on the Compute Module 5 — the CM4's RUN_PG is gone and pin 92 is now a power button.

**Signals worth fitting even though none are mandatory:**

| Pin | Signal | Fit it? | Why |
|---|---|---|---|
| **93** | `nRPIBOOT` | **Yes — a link or two test pads to ground** | Pulls the module into flashing mode over USB. This is how the storage gets written in production and how a bricked unit is recovered. Must be low within 2 ms of the 5 V rail rising |
| **20** | `EEPROM_nWP` | Yes, on a link | Low write-protects the boot memory. Raspberry Pi recommend final products pull it low. Must be low **before** power-up |
| **99** | `PMIC_Enable` | Test pad, or an open-drain transistor | Only for a commanded hard-off, and only after the operating system has shut down |
| **92** | `PWR_Button` | Optional, momentary to ground | Short press wakes or offers shutdown; holding over five seconds forces shutdown. Useful for service |
| **21** | `LED_nACT` | Yes | Flashes boot error codes. Direct drive through 1 kΩ. Invaluable during bring-up |
| **76** | `VBAT` | Judgement: yes | Real-time clock backup, 2.5-3.5 V. A coin cell keeps time while unplugged for over three years. Cheap, and it makes the timer context feel right after a power cut |
| **94 / 96** | `CC1` / `CC2` | **No — leave unconnected** | These go to the module's power-management chip for USB power delivery negotiation. Our device is mains powered and must never try to draw power from the computer |
| **101** | `USB_OTG_ID` | A 0 Ω pad to ground, not fitted | See section 5 |
| **89 / 91** | `WL_nDisable` / `BT_nDisable` | Links to ground | Only if wireless is to be disabled in firmware-independent hardware |

**A rule that matters specifically because this product has three boards.** Datasheet section 4.2.1: *"When CM5 is powered-down or off, there must be no external voltage applied to any pin, otherwise CM5 might not power up again."* If the audio or motion board drives a signal into the compute module while the module is off, it may not restart. Either make the internal 5 V domains collapse together, or buffer every cross-board signal.

**Raspberry Pi's own bring-up checklist**, to hand to the contractor: pull PMIC_Enable low and apply a 2 A load — the rail must stay above 4.75 V including noise, ideally above 4.9 V. Remove the load, keep PMIC_Enable low; if 3.3 V or 1.8 V exceeds 200 mV something is back-feeding. Release PMIC_Enable, confirm it goes high, confirm 3.3 V rises above 3.15 V and 1.8 V above 1.71 V, and watch LED_nACT oscillate.

---

## 5. USB device mode — how it is actually enabled

Raspberry Pi published a white paper, *"Using OTG mode on Raspberry Pi SBCs"* (RP-009276-WP, 1 October 2025), whose scope explicitly includes the Compute Module 5, and it describes our exact topology: power the board separately, leave the USB port free for data, and add to `/boot/firmware/config.txt`:

```
dtoverlay=dwc2,dr_mode=peripheral
```

The `dr_mode=peripheral` is not optional — the whitepaper says the ID line that would normally select the role **"is not present on Raspberry Pi 4 or 5"**. Gadget functions are then composed with configfs and `libcomposite`.

**Ignore the ID pin.** The datasheet's pin table, its section 2.4.2 note, and the OTG white paper contradict each other about what pin 101 does; the device tree contains no reference to it at all; and every shipped official IO board leaves it floating. Route it to a 0 Ω pad to ground, do not fit the resistor, and force the role in software.

**Wiring:** route only **USB_P (105)** and **USB_N (103)** to the hub as a **90 Ω differential pair, matched within 0.15 mm**. Note from the datasheet: *"USB 2.0 pairs can't be P/N swapped."* Do not connect any incoming VBUS to the module — there is no pin for it.

**⚠ The highest-risk item in the entire product.** Raspberry Pi's white paper documents serial, Ethernet and mass storage gadgets. It does **not** document a keyboard-and-mouse gadget, and Raspberry Pi publish no support statement for one. Composing `functions/hid.usb0` is standard mainline Linux and there are a decade of Raspberry Pi Zero examples, but nobody has published the specific combination of **a Compute Module 5 in peripheral mode presenting a keyboard-and-mouse gadget through a self-powered hub to Windows**. **Prove this on a bought Compute Module, the official IO board and an off-the-shelf powered hub before the contractor draws anything.** It is two days of work and it protects a sixty-unit commitment.

---

## 6. The hub

**Self-powered, not bus-powered.** The device takes mains power and must draw under 1 mA from the computer's port.

**VBUS detection is mandatory and is the whole host-presence mechanism.** The USB2514B datasheet is explicit: *"a downstream port can never provide power to its D+ or D− pull-up resistors unless the upstream port's VBUS is in the asserted state. The VBUS_DET pin monitors the state of the upstream VBUS signal and will not pull up the D+ resistor if VBUS is not active."* Ours is the detachable case, so **divide the incoming VBUS down to 3.3 V and feed VBUS_DET** — Microchip's own recommended divider is 50 kΩ / 100 kΩ. Getting this wrong means the device back-drives the computer's port, fails compliance, and misbehaves when the computer sleeps.

**Mark the internal ports non-removable.** The USB2514B has `NON_REM[1:0]` strap pins sampled at reset: `11` marks ports 1, 2 and 3 non-removable. Microchip's datasheet notes that *"declaring a port as non-removable automatically causes the hub controller to report that it is part of a compound device"* — which is exactly the behaviour we want, and it comes free. Windows then treats the whole object as one unit and will not offer to eject the internal boards.

**Other USB2514B requirements:** `RBIAS` needs **12.0 kΩ ±1 %** to ground; a 24 MHz crystal; the 36-pin package supports active-high port power control only.

**On the external socket:** since the device draws no power from the cable, present **5.1 kΩ ±20 % from each of CC1 and CC2 to ground** — one resistor per pin, never one shared. That is purely an attach signal.

---

## 7. The display connection

The official 22-way flat-flex carries the four data lanes, the clock lane, ground returns, two general-purpose pins, an I²C pair for touch, and 3.3 V. Lane assignment on the module:

| | D0−/D0+ | D1−/D1+ | CLK−/CLK+ | D2−/D2+ | D3−/D3+ |
|---|---|---|---|---|---|
| **MIPI0** | 115 / 117 | 121 / 123 | 127 / 129 | 133 / 135 | 139 / 141 |
| **MIPI1** | 175 / 177 | 181 / 183 | 187 / 189 | 193 / 195 | **194 / 196** |

Note that MIPI1's fourth lane breaks the odd/even pattern. Copy it literally.

Routing: **100 Ω differential, intra-pair matched within 0.15 mm**. Raspberry Pi state all these pairs are matched to under 0.05 mm on the module and that pair-to-pair matching is not required.

**What the flat-flex does not carry, and this is the gap.** There is **no backlight enable, no backlight power and no dedicated panel reset**. The official Raspberry Pi display takes its power on a separate three-pin cable to the general-purpose header, not through the flat-flex. For our third-party panel, backlight enable, backlight brightness and panel reset must come from spare general-purpose pins on connector 1 over our own cable, and **Raspberry Pi publish no reference circuit or recommended pin assignment for this**. Their documentation says only that for unsupported displays *"you must provide a custom driver."*

The I²C pair on the flat-flex (**SCL0 pin 80, SDA0 pin 82**) has 1.8 kΩ pull-ups on the module and is what the touch controller talks on.

**Decide DSI0 versus DSI1 versus internal HDMI before layout**, because it changes which module pins get routed. The recommendation is DSI0 on the 22-way connector. Internal HDMI is a fallback that costs a bridge board and real power; if it is used, the carrier must supply 5 V on HDMI pin 18 through a current-limited switch, and note that the Compute Module 5 — unlike the CM4 — has **no ESD protection on its HDMI signals at all**.

---

## 8. Power

**One rail in, one rail out, star-distributed.**

| Load | Current |
|---|---|
| Compute module, idle | 400 mA |
| Compute module, operating | 900 mA |
| Compute module, **design peak** | **2.5 A** (Raspberry Pi: *"Power supply designs should accommodate 5 V at up to 2.5 A"*) |
| Hub | tens of mA |
| Audio board | 135 mA typical, 340 mA worst case |
| Motion board | motor 1.2 A, halo up to 3.3 A at full white, servo transient |
| Display | ~400 mA |

**Supply: follow the v10 specification, not the figure a Raspberry Pi carrier would normally use.** The v10 mechanical work concluded a **12 V 5 A barrel inlet with a 5 V 10 A buck converter on board**, in preference to USB-C power, because the halo at full white alone is over 3 A and the compute module peaks at 2.5 A. A 5 V 5 A supply — the figure Raspberry Pi negotiate on their own board — is **not enough for this product**. Reconcile the exact numbers with `V10-SPECIFICATION.md` before the contractor starts; that document is the authority on the power budget and this one defers to it.

The halo's brightness cap is now a firmware parameter rather than a physical limit, and it should be **stated explicitly as a design number** rather than discovered — cap at 40 % white and the halo draws 1.3 A instead of 3.3 A.

**Star the distribution at the inlet.** Three separate pairs of wires leave the carrier's power inlet node — one to the audio board, one to the motion board, one staying on the carrier. Never daisy-chain, never share a return conductor. The motion board's return current must not flow through any copper the audio board uses as a reference, or the audio will hum. This costs one extra connector and is the single most effective noise measure in the product.

**Bulk capacitance near the module.** The official board distributes seven 10 µF 0805 capacitors on its 5 V net.

---

## 9. Thermal — the unsolved part

Raspberry Pi published *"Thermal modelling of Raspberry Pi Compute Module 5"* (RP-009520-WP-1, 1 December 2025), and its mitigation advice is: **airflow, or underclock**. Verbatim: *"It is not recommended that CM5 be left to self-regulate using protective throttling."*

They do **not** publish a junction-to-ambient or junction-to-case thermal resistance, and they give **no guidance on conducting heat into a carrier board or an enclosure**. For a sealed metal desk object there is no published Raspberry Pi solution. What they do give is a layer-by-layer conduction stack you can model:

| Layer | Thickness | Material | Conductivity |
|---|---|---|---|
| Heat spreader on the processor | 0.5 mm | Stainless steel | 15 W/mK |
| Processor to spreader | 0.1 mm | Thermal adhesive | 1 W/mK |
| Silicon | 0.8 mm | — | 140 W/mK |

The **stainless-steel heat spreader is the surface to couple to**, and the official cooler shows the reference interface: thermally conductive silicone touching the processor, the wireless module and the power-management chip — three components, not one.

**Recommendation (judgement, not vendor guidance):** plan a conduction path from the module's heat spreader through a gap pad into a machined part of the chassis, model it against the white paper, and validate with a two-hour run at worst-case ambient before committing tooling. Budget 12.5 W peak from the module alone. Raspberry Pi's published fallback is underclocking, which is a text file change rather than a respin — a genuine safety net.

**Also flag the wireless antenna keep-out:** at least 10 mm clearance, no metal or ground plane beneath it, a ground-plane cut-out of at least 6.5 x 11 mm and preferably 8 x 15 mm. In a metal enclosure this is the most likely thing to go wrong, and Raspberry Pi explicitly recommend the external antenna variant where the clearance cannot be met. **Decide this against the mechanical design, not on the board.**

---

## 10. What Raspberry Pi publish, and what they do not

The complete Compute Module 5 IO Board design is downloadable from `pip.raspberrypi.com`, no login, as **KiCad 9 files**. Take **`RP-008099-DD-1-CM5 IO Board, revision 2, KiCAD files.zip`** — revision 2, not revision 1.

Inside: the full PCB layout with its netlist, the hierarchical schematic, eleven custom footprints including **`Raspberry-Pi-5-Compute-Module.kicad_mod`** (the land pattern with the four M2.5 holes and the outline — the single most valuable file in the archive), eight STEP models including the board-to-board receptacle, and a 35-line bill of materials.

**Not included, and the contractor must be told:** no PDF schematic (it must be opened in KiCad 9), no gerbers, no drill files, no fabrication or assembly drawings, no stackup or impedance table, no pick-and-place file, and **no manufacturer part numbers** — the supplier column is empty on every line.

**On the licence, honestly.** The design data carries no open-hardware licence and no LICENSE file. The governing text on every Raspberry Pi document is *"RPL grants users permission to use the RESOURCES solely in conjunction with the Raspberry Pi products."* Deriving our carrier from theirs is use in conjunction with a Raspberry Pi product, and their own IO board datasheet says it *"can be used as either a reference design … These can be used in your own reference designs."* But it is not CERN-OHL or MIT, and if the commercial side matters, have someone read that clause.

**Better-documented third-party references, all with readable PDF schematics** — which the official board does not have:

| Project | Why look at it | Licence |
|---|---|---|
| **CM5 MINIMA** (`github.com/piecol/CM5_MINIMA_REV2`) | The best open small-carrier reference. Full KiCad **plus PDF schematics**, JLCPCB and PCBWay production files, 6 layers, ~54 x 57 mm | **CERN-OHL-S-2.0** |
| **Waveshare CM5-NANO-B** | Full schematic PDF of a commercially manufactured minimal carrier the size of the module | No stated licence — reference only |
| **Argo** (azlan-works) | Readable full schematic PDF; two USB-C, one power/flashing and one USB 3.0 | CERN-OHL-S-2.0, but commercial reproduction not permitted |

---

## 11. Layout rules for the contractor

- **Six layers.** Judgement: the USB pair, the display pairs and a quiet reference for the light sensor all want a solid plane, and the cost difference at 60 boards is trivial.
- **One unbroken ground plane. Do not split it.** Partition by placement, not by copper.
- **Route the differential pairs first** — the USB pair to the hub, then the display lanes — before any other routing.
- Use Raspberry Pi's own `.kicad_mod` for the module footprint rather than redrawing it.
- **Module keep-out:** with the 1.5 mm connector there is **zero** clearance under the module — nothing may be placed there. The 4.0 mm connector gives 2.5 mm. Decide early, because it affects the height stack.
- Mounting: four M2.5 holes on a **33.0 x 48.0 mm rectangle**, 2.7 mm drill, inset 3.5 mm from the module edge. Connector centres are **34.00 mm apart**.
- **Connectors everywhere, no solder joints in final assembly.** JST GH (1.25 mm, positive latch) for signals; JST VH or Molex Micro-Fit for power. **No JST SH anywhere** — it has no latch and is unsuitable for something that gets picked up.

---

## 12. Open questions

1. **Prove the keyboard gadget through a hub, on bought hardware, before layout.** Section 5. Everything else on this board is routine; this is not.
2. **DSI or internal HDMI**, and if DSI, which of the two interfaces. It changes which pins get routed.
3. **Backlight enable, backlight brightness and panel reset** — which general-purpose pins, and what the cable to the panel looks like. No Raspberry Pi reference exists.
4. **Wireless antenna** — internal with a 10 mm keep-out, or the external antenna variant. A mechanical decision with an electrical deadline.
5. **1.5 mm or 4.0 mm module connector**, which follows from the height stack and from whether anything needs to live under the module.
6. **Does the carrier own the external USB-C socket, or does a small port board at the back?** If the socket moves off this board, keep the run under 100 mm on a twisted pair and say so in the drawing.
7. **Thermal path into the chassis** — needs a model and a bench run.
8. **The halo's brightness cap**, which sizes the whole supply. State the number.

## Sources

[CM5 datasheet](https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf) · [CM5 IO Board datasheet](https://datasheets.raspberrypi.com/cm5/cm5io-datasheet.pdf) · [CM5 IO Board design files, rev 2](https://pip.raspberrypi.com/categories/1098-design-files) · [Using OTG mode on Raspberry Pi SBCs, Oct 2025](https://pip.raspberrypi.com/categories/685-app-notes-guides-whitepapers) · [Thermal modelling of CM5, Dec 2025](https://pip.raspberrypi.com/categories/685-app-notes-guides-whitepapers) · [RP1 peripherals datasheet](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf) · [Microchip USB2514B datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/00001692C.pdf) · [Amphenol BergStak 0.40 mm](https://www.amphenol-icc.com/product-series/bergstak-0-40mm.html) · [CM5 MINIMA open carrier](https://github.com/piecol/CM5_MINIMA_REV2) · [Waveshare CM5-NANO-B schematic](https://files.waveshare.com/wiki/CM5-NANO-B/CM5-NANO-B-Sch.pdf) · [Linux USB gadget documentation](https://docs.kernel.org/usb/gadget-testing.html)
