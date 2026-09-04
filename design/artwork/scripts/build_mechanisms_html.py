"""
build_mechanisms_html.py — writes design/artwork/MECHANISMS.html from the v9 model.

Balloon positions are not eyeballed: every keyed item carries a point in the
model's own coordinates, and this script projects it through the same camera
that rendered the view (views.json, written by the60_v9_mech_sections.py).
Re-render a view with different framing and re-run this, and the balloons move
with it.

Anchors:  B("name")        the centroid of that body in the assembly
          RZ(r, z)         radius r at height z, on the section's own azimuth
          RZA(r, z, az)    the same at another azimuth
          XY(x, y)         a point in plan
"""
import json, math, os, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MECH = os.path.join(ROOT, "design", "artwork", "examples", "mechanisms")
OUT  = os.path.join(ROOT, "design", "artwork", "MECHANISMS.html")

VIEWS  = json.load(open(os.path.join(MECH, "views.json")))
BODIES = json.load(open(os.path.join(HERE, "bodies.json")))
FREE   = json.load(open(os.path.join(HERE, "bodies_free.json")))

# ---------------------------------------------------------------- anchors
def B(name):      return ("body", name)
def RZ(r, z):     return ("rz", r, z)
def RZA(r, z, a): return ("rza", r, z, a)
def XY(x, y):     return ("xy", x, y)

def anchor_point(view, a):
    kind = a[0]
    if kind == "body":
        src = FREE if view.get("src") == "free" else BODIES
        return src[a[1]]["c"]
    if kind == "xy":
        return [a[1], a[2], 0.0]
    az = math.radians(a[3] if kind == "rza" else view["az"])
    r, z = a[1], a[2]
    return [r * math.cos(az), r * math.sin(az), z]

def pct(view, a):
    x, y, z = anchor_point(view, a)
    if view["kind"] == "plan":
        u, v = -y, x
    else:
        az = math.radians(view["az"])
        u, v = x * math.cos(az) + y * math.sin(az), z
    w, h = view["res"]
    sw = view["scale"]; sh = sw * h / w
    return (50.0 + (u - view["cu"]) / sw * 100.0,
            50.0 - (v - view["cv"]) / sh * 100.0)

# ---------------------------------------------------------------- legend
LEGEND = [
    ("#FF8948", "gimbal motor"), ("#E8541F", "drive band"), ("#F2A93B", "clutch servo"), ("#F7C86B", "sliding carriage"),
    ("#7F94A8", "bearings"), ("#35C08A", "encoder"), ("#A96BE0", "haptic LRA"),
    ("#3D8BF2", "speaker"), ("#2FBFB5", "supercaps"), ("#B9CC2F", "USB-C"),
    ("#8FB01F", "3.5 mm jack"), ("#D6E36A", "light sensor"), ("#6E8F1A", "DAC"),
    ("#FFD9A0", "halo LEDs"), ("#E8C070", "LED flex"), ("#F0E4C4", "diffuser"),
    ("#93A2B0", "display"), ("#3E7D5A", "circuit boards"), ("#B4BBC1", "steel plate"),
    ("#E4E9ED", "printed structure"), ("#69717A", "cut face"),
]

# ---------------------------------------------------------------- the sheet
SECTIONS = [
dict(view="00-plan-floor", title="Plan — the floor",
 cap="Horizontal section at z 12, looking down. Twelve o'clock is 0°, the USB-C socket at the "
     "back. Everything on this level stands on the steel plate or, in the carriage's case, on the "
     "pad through a hole in it, and goes in before the plate is closed.",
 keys=[
  ("Gimbal motor JD-Power MY-3514C", "az 90° · r 40.5 · Ø35 × 14 · z 4.2–18.2 — the whole drive, on a sliding carriage", B("motor_motor_ENVELOPE")),
  ("Sliding carriage", "printed Ø37 shoe, z 0–4.2, on the pad through the plate; the tab points inboard", RZA(23.0, 2.0, 90)),
  ("Linear servo AGFRC C1.5CLS PRO", "az 90° · 21.4 × 15.2 × 6.0 · z 6.5–12.5 — pushes the carriage tab directly", B("servo_body_ENVELOPE")),
  ("Speaker Soberton SP-4005-1", "centre (0, −30) · Ø40 × 9.05 · z 5–14.05 — stands cone-up on its rear boss", B("speaker")),
  ("Driver board 30 × 22", "az 152° · r 33 · z 8.0–9.6 on 3 mm standoffs — TMC6300 and DRV2605L", B("driver_board")),
  ("Two 20 F supercapacitors", "lying on the driver board, z 9.6–17.6", B("supercap1_can_with_sleeve")),
  ("Haptic LRA Vybronics VLV101040A", "az 165° · bonded to a pad on the inside of the wall, centre z 11.5", B("lra_can")),
  ("USB-C GCT USB4520 mid-mount", "az 0°, 10 mm off centre · socket centre z 3.3, on a board at z 2.2–3.8", B("usbc_body")),
  ("3.5 mm jack Switchcraft 35RAPC4BH3", "az 0°, 9 mm the other way · axis z 2.0, hanging under a board at z 5.0", B("jack_body")),
  ("Light sensor VEML7700", "az 0°, on centre · on a vertical board, looking out through a Ø4.8 hole at z 2.5", B("veml7700_package")),
  ("Perimeter sound ports", "Ø2 at z 12 on a 15° grid — 24 drilled, the 4 over the motor cut-out are lost", RZA(56.5, 12.0, 240)),
 ],
 note="The three M3 countersunk screws that pull the structure down onto the plate are at 125°, "
      "245° and 332° on r 53, driven from underneath before the pad goes on."),

dict(view="00b-plan-board", title="Plan — the board and the wheels",
 cap="Horizontal section at z 26, looking down: through the display's own circuit board, which is "
     "what decides where the three support wheels can go. The board is 85.5 × 65 and sits 4.5 off "
     "centre, so its corners reach r 56.6 while the wheel collars run out to r 59.2. At 60° and 120° "
     "a collar would foul it outright; 30, 150 and 270° are the positions that clear.",
 keys=[
  ("Display PCB 85.5 × 65 × 1.6", "z 25.6–27.2 · offset 4.5 toward the header edge · its corners reach r 56.6", B("display_pcb")),
  ("623ZZ wheel @ 30°", "3 × 10 × 4 in a printed Ø13.2 V-collar · axis r 52.63 · z 23.4–27.4", B("collar_0")),
  ("623ZZ wheel @ 150°", "the tightest of the three: the collar clears the board edge by 2.0", B("collar_1")),
  ("623ZZ wheel @ 270°", "3.3 clear · at 30° there is 11.0, which is why the three are not evenly useful", B("collar_2")),
  ("Support column @ 42°", "4 × 6 printed block, r 51.5–57.5 — one of four that carry the display", RZA(54.5, 26.0, 42)),
  ("V-groove in the knob bore", "root r 59.3 · z 23.8–27.0 — the wheels run in the groove, not on a ridge", RZA(59.0, 26.0, 300)),
  ("Knurled knob wall", "Ø125 outside, Ø116 bore · 56 starts, 1.0 deep, 30° helix", RZA(61.0, 26.0, 345)),
 ],
 note="The columns are at 42, 138, 222 and 318°, three degrees off the display's own M4 holes at "
      "45, 135, 225 and 315°. Two of those four holes sit 0.5 mm from the edge of the board, so no "
      "column can stand under them; the 1.2 mm seat tab reaches across instead."),

dict(view="01-drive", title="Self-turning drive — engaged",
 cap="Vertical section at 90°, through the motor. The gimbal motor stands on the pad through a "
     "stadium-shaped hole in the plate and drives the knob directly: a 0.6 mm flat silicone band "
     "round its Ø35 bell presses on the Ø116 bore, which is a 3.31 : 1 reduction.",
 keys=[
  ("Gimbal motor Ø35 × 14", "z 4.2–18.2 · centre r 40.5 engaged · the bell is assumed to start 4.3 above the base face", B("motor_motor_ENVELOPE")),
  ("Flat drive band 0.6", "z 9.0–17.8 · drawn uncompressed, so its outer face at r 58.6 laps the r 58.0 bore — that 0.6 is the squeeze, held by 2.4 N of servo preload", RZ(58.3, 13.4)),
  ("Knob bore Ø116", "the driven surface; the skirt starts at z 9.0, six tenths above the diffuser lip", RZ(59.8, 20.0)),
  ("Sliding carriage", "Ø37 shoe, z 0–4.2, riding on the pad; a Ø36 rim locates the motor, no bolt pattern yet", RZ(30.0, 2.1)),
  ("Servo push tab", "1.5 × 8 × 9 standing off the carriage's inboard side — the pushrod bridges the last 4 mm", RZ(22.2, 6.0)),
  ("Commutation board 12 × 12", "z 0–1.6 inside the carriage, MT6701 looking up a Ø9 sight hole at the shaft magnet", B("commutation_board")),
  ("Linear servo", "z 6.5–12.5 on the plate — no over-centre mechanism, no spring; preload is a software number", B("servo_body_ENVELOPE")),
  ("Steel plate 5 mm", "the carriage passes through it; the plate is the halo's bottom edge, not a floor for the motor", RZ(50.0, 2.5)),
 ],
 note="Band grip at 2.4 N is the item that decides whether this drive works. If it slips, the "
      "fallback is a 2 : 1 bell-crank on the servo, which doubles the force at the cost of half the stroke."),

dict(view="01b-clutch", title="Self-turning drive — released",
 cap="The same section with the carriage retracted. The servo pulls back 2.4 mm and the whole "
     "motor goes with it: the band leaves the bore and the knob spins free on its three wheels. "
     "There is no detent hardware anywhere in v9 — every click is the motor.",
 keys=[
  ("Motor retracted 2.4", "centre r 38.1 · the bell now clears the bore by 2.40, the band by 1.8", B("motor_motor_ENVELOPE")),
  ("The gap", "this is the whole clutch: 2.4 mm of radial travel, held by the servo, no latch", RZ(57.0, 13.4)),
  ("Carriage at its stop", "the tab, not the servo's own 9 mm stroke, is what limits the travel", RZ(27.6, 2.1)),
  ("Servo pushrod", "assumed on the 21.4 mm body axis; the rod-to-tab joint is not drawn yet", RZ(19.0, 9.5)),
 ],
 note="The servo's 9 mm stroke keep-out runs on past the carriage tab in the interference check. "
      "That contact is expected, not a fault: the tab is the real stop."),

dict(view="02-encoder", title="Encoder",
 cap="Vertical section at 330°, through the AEDR-8300. It looks outward at a code band printed on "
     "the knob bore across the 2.00 mm gap the part is specified for. The band is a 4.2 mm tall "
     "strip because the package is 3.96 mm across.",
 keys=[
  ("Broadcom AEDR-8300-1K2", "package face 2.00 from the bore · centred z 20.5", B("encoder_package")),
  ("Encoder board", "1.0 thick, z 18.4–22.6, standing vertically in a pocket in the wall", RZ(53.6, 18.9)),
  ("Code band on the bore", "z 18.4–22.6 in a 0.15 recess, so the strip finishes flush with r 58.0", RZ(58.0, 22.2)),
  ("Encoder tower", "printed, part of the internal structure; the window through the wall is the only opening here", RZ(51.5, 20.5)),
  ("Ledge", "z 15.6–17.4, inner r 49 — the shelf the structure hangs everything else from", RZ(52.0, 16.5)),
 ],
 note="The code strip's 0.15 mm thickness is assumed. If the strip you can actually buy is thicker "
      "the recess changes, not the gap: the gap is what the encoder needs."),

dict(view="03-wheels", title="Knob support wheels",
 cap="Vertical section at 30°, through one of the three wheels. A 623ZZ bearing sits in a printed "
     "V-collar and runs in a V-groove cut into the knob bore. The groove, rather than a ridge, is "
     "what lets the Ø115 display pass down through the Ø116 bore during assembly.",
 keys=[
  ("623ZZ bearing 3 × 10 × 4", "axis r 52.63 · z 23.4–27.4 — cut through, so it shows as two rings", RZ(55.9, 25.4)),
  ("Printed V-collar Ø13.2", "1.3 flank, 0.6 flat — it is the collar that touches the groove, not the bearing", RZ(49.0, 23.9)),
  ("Eccentric bush", "0.9 mm eccentric, flange resting at z 22.8; a half-turn with a 2 mm hex key retracts the wheel", RZ(51.7, 19.5)),
  ("V-groove in the bore", "root r 59.3 · z 23.8–27.0", RZ(59.3, 25.4)),
  ("Wheel post Ø8", "printed, up to z 22.8 — the bush drops in from above and is turned from below", RZ(49.3, 19.0)),
  ("Display PCB edge", "z 25.6–27.2 — the wheels have to miss it, which is what fixes them at 30/150/270°", RZ(44.0, 26.4)),
 ],
 note="Turn all three bushes to their retracted position, lower the knob on, then turn them back a "
      "half-turn each. That is the only way the knob goes on or comes off."),

dict(view="04-ports", title="Ports",
 cap="Horizontal section at z 3, looking down on the back of the device. All three back-panel parts "
     "live in one 32 mm slot cut clean through the steel plate: the USB-C socket 10 mm to one side, "
     "the 3.5 mm jack 9 mm to the other, the light sensor on centre. One board could not put the "
     "jack's axis and the socket at the same height, so there are three small ones.",
 keys=[
  ("USB-C GCT USB4520-03-0-A", "mid-mount, socket centre z 3.3, mating face flush with the port face", B("usbc_body")),
  ("USB-C board 11 × 12 × 1.6", "z 2.2–3.8, lying on a shelf moulded into the port face", XY(41.0, -10.0)),
  ("3.5 mm jack Switchcraft 35RAPC4BH3", "axis z 2.0, body z −1 to 5, hanging under a board at z 5.0", B("jack_body")),
  ("Light sensor VEML7700", "on a vertical board, looking rearward through a Ø4.8 aperture at z 2.5", B("veml7700_package")),
  ("Light-sensor board", "1.0 × 6.0, z −1.4 to 5.5, standing in a slot in the port face", XY(45.6, -1.0)),
  ("Printed port face 1.5", "r 49.5–51, 32 wide, z −1.5 to 5 — it closes the slot and carries all three", XY(50.3, 15.0)),
  ("Slot through the plate", "from r 35 to the rim, 32 wide, taking the cable's right-angle plug", XY(52.0, -15.0)),
  ("Steel plate", "5 mm, and this slot is the only opening in it apart from the carriage’s", XY(52.0, 20.0)),
 ],
 note="Everything on this level has to finish below z 5.0, because that is where the halo starts — "
      "which is why the jack hangs under its board instead of standing on one. The internal plug and "
      "the boxed cable's right-angle plug are both assumed sizes and they set the width of this slot, "
      "so measure the cable you actually ship before the plate is cut."),

dict(view="05-halo", title="Halo light ring",
 cap="Vertical section at 200°. Ninety side-firing LEDs lie flat on the plate on a flex ring and "
     "fire outward into the diffuser. This is the change that matters: a side-view LED on a flex "
     "wrapped round a cylinder fires up or down, not out.",
 keys=[
  ("SK6812SIDE-A, 90 of them", "r 58.8 · z 5.2–7.2 · emitting face pointing radially outward", RZ(58.8, 6.2)),
  ("LED flex ring", "r 57.7–60.0 · z 5.0–5.2, lying flat on the plate top — continuous, 360°", RZ(57.9, 5.1)),
  ("Halo diffuser", "r 60.0 in, 62.0–62.5 out · z 5.0–7.6 · 2.0–2.5 of wall", RZ(61.2, 6.3)),
  ("Retaining lip", "z 7.6–8.4, out to r 60.5 — printed as part of the structure, holds the diffuser down", RZ(60.0, 8.0)),
  ("Knob skirt", "starts z 9.0: a 0.6 mm shadow gap over the lip, so the light line reads as a gap", RZ(60.0, 9.6)),
  ("Steel plate edge", "Ø124 — the plate's own edge is the bottom of the light line", RZ(61.0, 2.5)),
  ("Wall and its sound ports", "the Ø2 perimeter ports at z 12 sit above the halo, inside the skirt", RZ(49.0, 12.0)),
 ],
 note="The ring is unbroken all the way round only if the motor's stator base really is narrower "
      "than its bell. The model assumes Ø30 for the lowest 4.3 mm; at Ø35 the ring is interrupted "
      "for about ±11° at the motor."),

dict(view="06-bay", title="Electronics bay",
 cap="Full-diameter section at 152°, through the driver board. This is the whole vertical stack in "
     "one picture — plate, floor components, ledge, code band, wheels, display board, display, knob.",
 keys=[
  ("Driver board", "az 152° · r 33 · z 8.0–9.6 — TMC6300 for the motor, DRV2605L for the haptic", B("driver_board")),
  ("Supercapacitors", "two 20 F cans lying on the board, z 9.6–17.6", B("supercap1_can_with_sleeve")),
  ("Haptic LRA", "az 165° · bonded to the wall at centre z 11.5 — into the structure, not the knob", B("lra_can")),
  ("Speaker", "cone-up at (0, −30), breathing into the cavity and out through the perimeter ports", B("speaker")),
  ("Encoder", "az 330°, the far side of this cut", B("encoder_package")),
  ("Display PCB and disc", "board z 25.6–27.2, disc z 28.7–34.7, glass at 34.7", B("display_case")),
  ("Knob crown", "z 35.1–38.1 over a 0.4 rim gap; total height 39.6 including the pad", RZA(30.0, 36.6, 332)),
  ("Steel plate", "Ø124 × 5, about 385 g — most of the mass, and all of the stability", RZA(45.0, 2.5, 332)),
 ],
 note="Height from the pad's underside to the top of the crown is 39.6 against a 40 mm limit, and "
      "the knob is 76 % of the side against a 67 % floor. Both are the tightest they have been."),

dict(view="07-speaker", title="Speaker and sound path",
 cap="Vertical section at 270°. The speaker stands cone-up on its rear boss in a printed cradle, "
     "breathing into the cavity above it and out through the ring of small ports round the wall. "
     "Nothing fires down into the plate, because the plate is solid.",
 keys=[
  ("Speaker Ø40 × 9.05", "centre (0, −30) · z 5–14.05 · cone up, standing on its rear boss", B("speaker")),
  ("Printed cradle", "a ring under the Ø40 flange with three snap fingers over it, z 5–12.25", RZ(44.0, 6.0)),
  ("Ledge", "z 15.6–17.4 — the cavity the cone breathes into is everything under this shelf", RZ(40.0, 16.5)),
  ("Perimeter sound port", "Ø2 at z 12, on a 15° grid round the wall", RZ(56.5, 12.0)),
  ("Wall", "r 55.5–57.6, and the ports go straight through it into the shadow gap", RZ(56.5, 20.0)),
  ("Steel plate", "solid under the speaker; the pad below it is the foot", RZ(30.0, 2.5)),
 ],
 note="Cone-up plus perimeter ports is the v9 arrangement — down-firing made no sense once the "
      "plate became a solid 5 mm slab with only the port slot through it. The cradle is held by two "
      "M3 countersunk from below, 48 mm apart; both sit off this cut, behind the speaker."),

dict(view="08-display", title="Display seat",
 cap="Vertical section at 42°, through one of the four support columns. The display hangs from four "
     "1.2 mm tabs in the 1.5 mm gap between the top of its board and the back of its disc, held by "
     "M4 × 4 driven before the plate goes on.",
 keys=[
  ("Support column", "4 × 6, r 51.5–57.5, part of the internal structure", RZ(54.5, 24.0)),
  ("Seat tab 1.2", "z 27.5–28.7 — 0.39 clear of the board, touching the back of the disc", RZ(55.0, 28.1)),
  ("Display disc Ø115 × 6", "z 28.7–34.7 · glass at 34.7 · active area Ø87.6", RZ(50.0, 31.7)),
  ("Display PCB", "z 25.6–27.2 · the 1.5 mm gap above it is all the room the tab has", RZ(45.0, 26.4)),
  ("Knob bore and groove", "the bore runs straight past at r 58; the groove is just below this cut", RZ(59.0, 25.4)),
  ("Knob crown", "z 35.1–38.1, clearing the glass by the 0.4 rim gap", RZ(47.0, 36.6)),
 ],
 note="The M4 holes are at 45, 135, 225 and 315° on a 106.07 PCD, three degrees off the columns and "
      "not on this cut. Tapped depth allows 3.5 mm of engagement, which is why the screws are M4 × 4 "
      "and not longer."),
]

# ---------------------------------------------------------------- emit
CSS = """:root{--paper:#EDEEEF;--card:#F7F8F8;--ink:#15181B;--ink2:#4A525A;--ink3:#7E8891;--rule:#CFD4D9;--acc:#C8352B;--warn:#8A5A2B;--warnbg:#F3E9DC}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;font-size:16px;line-height:1.55}
h1,h2{font-family:"Barlow Semi Condensed","Arial Narrow",Arial,sans-serif;margin:0;line-height:1.1;text-wrap:balance}
h1{font-size:2.4rem;font-weight:700}
h2{font-size:1.6rem;font-weight:600}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header.tb{border:2px solid var(--ink);background:var(--card);padding:18px 22px;margin:24px 0 10px}
header.tb p{margin:8px 0 0;color:var(--ink2);max-width:74ch}
.lbl{font-family:"JetBrains Mono",monospace;font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3)}
section{border-top:2px solid var(--ink);margin-top:44px;padding-top:16px}
.cap{color:var(--ink2);max-width:74ch;margin:8px 0 16px}
.figwrap{display:grid;grid-template-columns:1.35fr 1fr;gap:24px;align-items:start}
@media (max-width:900px){.figwrap{grid-template-columns:1fr}}
.fig{position:relative;background:var(--card);border:1px solid var(--rule)}
.fig img{display:block;width:100%;height:auto}
.balloon{position:absolute;transform:translate(-50%,-50%);width:23px;height:23px;border-radius:50%;
  background:var(--card);border:1.5px solid var(--ink);color:var(--ink);
  font-family:"JetBrains Mono",monospace;font-size:.72rem;display:grid;place-items:center;
  box-shadow:0 0 0 2.5px rgba(247,248,248,.85)}
ol.key{list-style:none;counter-reset:k;padding:0;margin:0}
ol.key li{counter-increment:k;position:relative;padding-left:34px;margin:0 0 11px;font-size:.94rem}
ol.key li::before{content:counter(k);position:absolute;left:0;top:1px;width:23px;height:23px;border-radius:50%;
  border:1.5px solid var(--ink);display:grid;place-items:center;font-family:"JetBrains Mono",monospace;font-size:.72rem}
ol.key b{display:block}
ol.key span{color:var(--ink2);font-size:.86rem;font-family:"JetBrains Mono",monospace}
.note{border-left:3px solid var(--warn);background:var(--warnbg);padding:9px 13px;margin:16px 0 0;max-width:74ch;font-size:.92rem;color:#3E3428}
.note b{color:var(--warn)}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:14px 0 0;font-size:.84rem;color:var(--ink2)}
.legend i{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:5px;vertical-align:-1px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.18)}
.figwrap.wide{grid-template-columns:1fr}
.figwrap.wide ol.key{columns:2;column-gap:26px}
.figwrap.wide ol.key li{break-inside:avoid}
@media (max-width:700px){.figwrap.wide ol.key{columns:1}}
.open{margin:16px 0 0;max-width:78ch;font-size:.94rem;color:var(--ink2)}
.open li{margin:0 0 8px}
@media print{body{background:#fff}section{break-inside:avoid}header.tb{break-after:avoid}}"""

INTRO = ("Every bought component placed exactly as the v9 model puts it, cut open one mechanism at a "
         "time. Coloured solids are bought parts, light grey is printed structure, and the dark grey "
         "faces are where the section knife passed — if a surface is dark grey you are looking through "
         "something, not at it. All dimensions in millimetres. z = 0 is the underside of the steel "
         "plate, with the 1.5 mm pad below that. Azimuth is measured anticlockwise from the USB-C "
         "socket at the back, which is 0° and sits at twelve o'clock in the two plan views.")

OPEN_ITEMS = [
 ("Motor base diameter and bell height.", "The model assumes the stator base is Ø30 for its lowest "
  "4.3 mm. If the base is the full Ø35 the LED ring is interrupted at the motor; if the bell starts "
  "lower than 4.3 it fouls the diffuser lip. Nothing is published — measure it."),
 ("Which end of the shaft carries the magnet.", "v9 puts the commutation board under the motor "
  "inside the carriage. If JD-Power fits the magnet at the top instead, the board moves up and the "
  "display rises about 3 mm, which is over the height limit."),
 ("Motor bolt pattern.", "The carriage has a Ø36 locating rim and nothing else. There is no drawing."),
 ("Servo lugs and pushrod.", "The mount is a tray and the rod-to-tab joint is not drawn."),
 ("Band grip at 2.4 N.", "If the flat band slips on the bore, add the 2 : 1 bell-crank."),
 ("Electrical layout.", "The driver, port, encoder and commutation boards are outlines only."),
]

def esc(s): return html.escape(s, quote=False)

def render():
    out = []
    out.append("<title>The 60 — Where Everything Fits</title>")
    out.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap">')
    out.append("<style>\n" + CSS + "\n</style>")
    out.append('<div class="wrap"><header class="tb">'
               '<span class="lbl">Cadrane · the 60 · v9 · sections</span>'
               '<h1>Where Everything Fits</h1><p>' + esc(INTRO) + '</p>'
               '<div class="legend">'
               + "".join(f'<span><i style="background:{c}"></i>{esc(n)}</span>' for c, n in LEGEND)
               + '</div></header>')
    for sec in SECTIONS:
        v = VIEWS[sec["view"]]
        out.append(f'<section><span class="lbl">{sec["view"]}</span><h2>{esc(sec["title"])}</h2>'
                   f'<p class="cap">{esc(sec["cap"])}</p>')
        balloons = []
        items = []
        for i, (lab, sub, anc) in enumerate(sec["keys"], 1):
            L, T = pct(v, anc)
            L = min(max(L, 2.0), 98.0); T = min(max(T, 2.0), 98.0)
            balloons.append(f'<div class="balloon" style="left:{L:.2f}%;top:{T:.2f}%">{i}</div>')
            items.append(f'<li><b>{esc(lab)}</b><span>{esc(sub)}</span></li>')
        wide = " wide" if v["res"][0] / v["res"][1] > 1.8 else ""
        out.append(f'<div class="figwrap{wide}"><div class="fig">'
                   f'<img src="examples/mechanisms/{sec["view"]}.png" alt="{esc(sec["title"])}">'
                   + "".join(balloons) + '</div><div><ol class="key">'
                   + "".join(items) + '</ol>'
                   + (f'<div class="note"><b>Note.</b> {esc(sec["note"])}</div>' if sec.get("note") else "")
                   + '</div></div></section>')
    out.append('<section><span class="lbl">open items</span><h2>What these views do not settle</h2>'
               '<p class="cap">v9 passes its own interference checks — 302 bodies, 0 failures, '
               '0 warnings, 14 expected envelope contacts. Every one of the items below is a number '
               'the model assumed, and every one is settled with calipers rather than another '
               'iteration.</p><ol class="open">'
               + "".join(f'<li><b>{esc(a)}</b> {esc(b)}</li>' for a, b in OPEN_ITEMS)
               + '</ol></section>')
    out.append('</div>')
    return "\n".join(out)

if __name__ == "__main__":
    open(OUT, "w", encoding="utf-8").write(render())
    print("wrote", OUT, os.path.getsize(OUT))
