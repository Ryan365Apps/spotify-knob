# Token list — the 60

Paste-able into a code repository and a brand guideline unchanged. Every token
derives from one of four physical facts: the 60-detent geometry (6° / 30° / 60°),
the 120 ms beat (one detent at brisk deliberate turning), the colour-is-light law
(`docs/VISION.md`), and the machined chamfer. **(V)** marks a value not yet
verified on hardware — a starting value, not a spec.

## Colour

Each colour is a perceptual target with two calibrated values, because an IPS
panel under glass and LEDs through a diffuser onto a desk are different media.
Halo values are placeholders until per-LED calibration exists.

```
color.green.screen      #2EE06E   (V)  // volume, selection — the owned thing
color.green.halo        calibrate (V)
color.amber.screen      #FFB340   (V)  // seek, attention — collision flagged, dissent.md item 1
color.amber.halo        calibrate (V)
color.white.screen      #EAEAEA   (V)  // the device: connections, position, boot
color.white.halo        calibrate (V)
color.red.screen        #E5484D   (V)  // mute and recording ONLY — never error
color.red.halo          calibrate (V)
color.ink               #101010   (V)  // near-black surface, screen and app
color.line              #3A3A3A   (V)  // monochrome line-work stroke
```

## Motion

```
motion.beat             120 ms    (V)  // one detent at brisk deliberate turning
motion.pulse            120 ms         // 1 beat — dot pulse, press
motion.land             240 ms         // 2 beats — anything settling into place
motion.arrive           360 ms         // 3 beats — a context arriving; the ceiling for all event motion
motion.boot             2400 ms        // the only animation allowed past 3 beats
ease.settle             cubic-bezier(0.2, 0.9, 0.1, 1)   // landings; never overshoots
ease.exit               cubic-bezier(0.4, 0.0, 1, 1)     // departures
ease.pulse              sine in-out
ease.breathe            sine, 4000 ms period
rule: screen angle = shaft angle, 1:1, uneased; springs are banned
rule: event animations decimate to ≥ 1 beat apart; positions render every frame
```

## Halo

```
halo.led.pitch          ~4 mm          // from the brief
halo.arc                324°           // horseshoe; 36° gap at rear
halo.led.count          ~90       (V)  // derived: Ø128 mm (V, CAD pending) × π × 324/360 ÷ 4 mm
halo.feature.min        3 LEDs         // never drive a lone LED
halo.tick.width         12° (~3 LEDs) (V)
halo.breathe            4000 ms, 15%→45% brightness (V)
halo.wall               80 ms @ 100%, decay 320 ms (V)
halo.hold               solid 60% amber, no animation (V)
halo.record             solid 25% red, never animated (V)
halo.brightness.night   day ÷ 5 (V)
rule: magnitude maps to the gauge (gap-edge anchored); position maps 1:1 to the knob
rule: halo and screen never animate simultaneously (exception: timer set-point landing)
```

## Sound

```
sound.tick              10 ms,  2.5 kHz filtered noise            (V)
sound.latch             140 ms, 500 Hz thunk −1 semitone + 2 kHz tail (V)
sound.yes               160 ms, 660→990 Hz (fifth up), 2 × 60 ms  (V)
sound.no                120 ms, 440→415 Hz (semitone down)        (V)
sound.land              1600 ms, 3 strikes @ 880 Hz; ×3 total, 8 s apart (V)
sound.hello             240 ms, 523→784 Hz rising pair            (V)
sound.goodbye           240 ms, 784→523 Hz falling pair           (V)
sound.hail              300 ms, 660 Hz, 40 ms soft attack, once   (V)
sound.gain.reference    the mechanical detent click at arm's length — measure first, set all gains relative
rule: silence by default; the speaker never voices rotation
rule: haptic-linked sounds land within ±10 ms of the haptic event
```

## Detent profiles

```
detent.free             motor off — bare magnets (always alive, power off included)
detent.feather          lightened detents (seek, fast lists)
detent.firm             reinforced detents — the default in-context feel
detent.wall             end-stop
detent.ratchet          patterned feel (reserved; needs a ruling before use)
rule: profile switches at t=0 of a context change — feel leads sight by 3 beats
```

## Type and grid (at 800 × 800; 9.3 px/mm; 60 cm viewing)

```
type.family             Inter (SIL OFL 1.1) — brand-pass candidates need embedded-licence quotes
type.figures            tabular (tnum), always
type.hero               260 px (V)  // timer / volume numerals; test 1.2× vertical stretch at desk angle
type.label              44 px  (V)
type.floor              33 px  (V)  // nothing below this may need reading
type.bezel              36 px  (V)  // rotated radially, dive-bezel style
grid.r.edge             400 px      // physical edge under chamfer
grid.r.safe             360 px (V)  // inside the chamfer's shadow
grid.r.dot              352 px (V)  // the green dot at twelve
grid.r.menu             300 px (V)  // ring-menu item centres
grid.r.scale            268–340 px (V) // outer scale: 60 ticks (one per detent), majors every 5
grid.r.content          220 px (V)  // hero disc
icon.grid               48 px  (V)
icon.stroke             3.5 px (V)  // square terminals; construct on 30°/60° angles
calib.panel.rotation    named factory parameter — aligns screen ticks to the metal ring
```

## Shapes and names

```
shape.ring   shape.dot   shape.chamfer   shape.tick     // the entire graphic identity; no logo
state names: asleep, awake, listening, holding, walled, landing, recording
halo states: off, breathe, arc, tick, wall, hold, record
sounds:      tick, latch, yes, no, land, hello, goodbye, hail
detents:     free, feather, firm, wall, ratchet
```
