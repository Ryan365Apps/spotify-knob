| # | Item | What it is | What closes it | Type | Blocks |
|---|---|---|---|---|---|
| 1 | Bush access on your print | Model says all three sockets are reachable through Ø5.1 bores with the plate off; you found otherwise on the print | Tell me which post and what driver you used; I check the printed geometry | Question for you | v16 bush rule and assembly wording |
| 2 | Later preload adjustment | Adjusting a built object needs three Ø4 holes through the ring and the pad | Yes or no | Decision | Ring drawing |
| 3 | Board route | Pico 2 fits; ESP32 DevKitC does not without the audio board out | Pico route, or DevKitC with audio parked | Decision | Every board placement in v16 |
| 4 | Where the Pico goes | Tray above the adapter (everything kept, bare boards, 5 mm headroom, cables re-routed) or on the plate with audio board and speaker parked | Pick one | Decision | v16 layout |
| 5 | Board fixings | New boards need piers in the web or a printed carrier; no positions exist yet | Follows from 3 and 4; I design them | Design work (mine) | v16 |
| 6 | Harness and connectors | ~20 cable assemblies, no routes drawn; Pico-Lock right-angle is surface-mount only; bought breakouts have 2.54 mm headers | Accept a split harness for the prototype (sourcing doc §6) and let me route it | Decision, then design work | v16 checks (cables vs moving carriage) |
| 7 | Rotor sensor cable | 2.4 mm flex, 10⁵ cycles, no vendor life figure | Bench cycling rig, or accept the Premo-Flex 0.12 figure | Measurement | Nothing in CAD; a risk carried |
| 8 | Motor | Three 2804/2805 candidates ordered, none measured; must be 14–19.5 tall with the bell above z 14.9 | Measure height, bell diameter, bell start height | Measurement | Carriage, hole, ratio (parametric — number change only) |
| 9 | Servo | AGFRC not chosen; frame parametric; 0.75 mm behind, 2.5 on the blower side | Measure the three candidates' envelope and pushrod height | Measurement | Frame — number change unless >2.5 mm wider on the blower side |
| 10 | Halo bench rig | Bounced-pool assumption, opal grade, LED count, ledge heat — all untested | Build the £40 rig in HALO-OPTICS §8 | Measurement | Final strip and count; not the v16 geometry |
| 11 | LED count vs stock strips | "60 or 120" needs a custom flex; stock densities give 53/63/76/84/105 | Accept a stock count, or commission a flex | Decision | Strip purchase, peak current |
| 12 | Lip vs throw | 0.8 lip with 4.0 throw as written, or 1.5 lip with ~3.3 | Pick one (I build 0.8 as written unless told) | Decision | v16 halo |
| 13 | Diffuser top face | 4 mm top face exposed and glowing, or covered by the lip | Pick one | Decision (aesthetic) | v16 halo |
| 14 | Ring finish under the shelf | Axial brushing cannot reach the 1 mm shelf's underside; turned finish instead? | Pick one | Decision (aesthetic) | Ring drawing |
| 15 | Halo peak current | 2.88 A at 60, 5.76 A at 120; converter sized on 2.54 | Follows from 11; converter chosen to suit | Decision | Converter part, second power feed |
| 16 | Converter still-air rating | No module publishes one | Test B (inlet current logging) | Measurement | Converter choice |
| 17 | Mains supply | Specified family is Class I | Adopt GSM60B12-P1J (Class II) per sourcing doc | Decision (recommended: yes) | Grounding doc |
| 18 | Pi 5 USB device mode | Sourcing doc says its USB-C carries no data | Twenty-minute bench check | Measurement | External USB-C's purpose, host link on the Pico |
| 19 | External USB-C part | Round panel-mount needs 21.5–27 mm hole; port face is 9.5 mm tall | Keep the socket-on-board behind a slot (my recommendation) | Decision | Port face |
| 20 | Light sensor breakout | 16.5 mm tall behind a hole at z 4; sensor position on board unpublished | Measure the board, or lower the hole | Measurement | Port face |
| 21 | Code ring | Custom part, nobody sells it; sensor has 14-week reorder lead time | Send quote requests to the four suppliers | Action (yours) | The whole encoder; long pole |
| 22 | Knob bleed contact | Hand-formed leaf, force under 0.5 N, drag under 2 mN·m — untested | Bench | Measurement | Nothing in CAD |
| 23 | Thermal operating point | ~0.5 L/s, ~1 W/K is an estimate | Test B plus a flow/temperature measurement on the built plate | Measurement | Nothing; validates the plate |
| 24 | Radius | +5 mm at your disposal; buys 900 mm² and 0.8 mm of clearance, costs 5 mm of bezel | Keep Ø175.4 unless wanted for heft | Decision | Everything, if changed — decide before v16 |
| 25 | `base_plate_AL.step` on disk | Differs from the committed file (re-saved 14:15) | Say if deliberate; otherwise I restore it | Question for you | Nothing |
| 26 | Documents out of step | DESIGN-CHANGES item 4 (v10 motor numbers), BOM halo lines, spec's halo tail, THERMAL-PLAN halo heat | I rewrite them with v16 | Design work (mine) | Nothing |

Items 3, 4, 12, 13, 24 are the ones I need before starting v16; the rest either ride along as parameters or are yours to schedule. If you want this table kept as a file in the repo alongside DESIGN-CHANGES.md, say so and I will commit it with v16.