# A small off-the-shelf drive for the knob

**Date:** 2 September 2026. Ruling: the knob turning itself is a must-have. With walls handled by a brake, spin-down by an eddy brake, click strength by the sliding magnets and events by the vibration actuator, the motor no longer has to push against the hand a thousand times a second. It only has to **turn the knob when asked, and be completely out of the way when not.** That is a small gearmotor on a friction wheel that lifts off, not a custom ring motor.

## The mechanism

A rubber-tyred wheel, about 10 mm across, on the output shaft of a small gearmotor. The motor sits on a short swinging arm inside the base. At rest a spring holds the wheel half a millimetre clear of the knob's inside face, so the free spin sees nothing — no gearbox, no drag. When the software wants the knob to move, a small solenoid (or the existing cam mechanism's spare travel) swings the arm in, the tyre presses on the knob with a few newtons, the motor runs, the position sensor already in the design closes the loop, and when the knob reaches its target the wheel lifts off again and the magnets drop it into the nearest click — which is the kerchunk you wanted to record.

## Numbers, for the current 122.8 mm inside face

- Ratio: a 10 mm wheel on a 122.8 mm track is 12.3 to 1.
- Speed: a 30:1 micro metal gearmotor free-runs at about 1,100 rpm at 6 V, so the knob turns at up to about 1.5 turns a second unloaded, realistically 0.6–0.8 loaded — a 60° nudge in about a third of a second, a full turn in a second and a half.
- Torque: the same motor stalls at 0.45 kg·cm (44 mNm). Through 12.3 to 1 that is over 500 mNm at the knob before the tyre slips. The tyre slips first: 3 newtons of pressure on a polyurethane tyre gives about 130 mNm at the knob — still more than the 74 mNm click, so the knob can **click round** through the detents rather than needing them cancelled first.
- Power: about 0.3–0.5 amps at 5 volts while turning, so 1.5–2.5 watts for under a second per move. That is a burst the power research's supercapacitor buffer absorbs; it is not a continuous load and it makes no heat in the ring.
- Size: the gearmotor body is 10 × 12 mm in section, about 30 mm long with the gearbox, lying flat on the base floor like the cam motor already does. It fits in the base at every diameter under discussion.
- Drag when disengaged: none. The wheel is not touching.
- Noise: a metal-gearbox N20 whines audibly at close range. For prototypes that is fine; for production a coreless motor with a planetary gearbox is quieter and more efficient at two to four times the price.

## Candidates

| Motor | Price | Notes |
|---|---|---|
| [Pololu 30:1 Micro Metal Gearmotor HPCB 6V with extended shaft](https://www.pololu.com/product/3072) | $27.45 single, $21.38 at 100 | 1,100 rpm, 0.45 kg·cm stall at 6 V, carbon brushes (long life), 10 × 12 mm gearbox. The known-quantity prototype part. The [plain HPCB version](https://www.pololu.com/product/3062) without the rear shaft is the same motor; the [encoder version](https://www.pololu.com/product/5185) is unnecessary because the knob's own position sensor closes the loop |
| Generic GA12-N20, 6 V, 300–1,000 rpm (AliExpress, already in the sourcing document for the cam) | £2–4 | Same footprint and shaft; quality varies between batches; fine for the printed prototypes, sample before the run |
| 10–12 mm coreless motor with planetary gearbox (AliExpress, or Faulhaber/Maxon at the top end) | £8–15 generic, £40+ branded | Quieter, higher efficiency, lower cogging; the production upgrade if the N20 whine is unacceptable |
| A small solenoid to swing the arm (6–8 mm push type, 2 mm stroke, 5 V) | about £1 | Energised only while driving (under a second). A latching type holds engaged with no current if longer drives are wanted |

Recommendation: Pololu 30:1 HPCB for the prototypes — one part, one datasheet, no lottery — and sample the generic N20 and a coreless planetary alongside it on the rig for noise.

## What the same wheel gives for free

Because the wheel is a controllable contact between the knob and a motor, it does three more jobs when engaged:

- **Brake.** Short the motor's terminals and the gearbox becomes a speed-proportional drag through the tyre — a wall you run into softly. Add a friction pad on the same arm and it is a hard stop. This is the end-stop wall from the motor list, at no extra part.
- **Crude spring.** Energise the motor against the hand and the knob pushes back. Through a gearbox and a tyre it feels like a gearbox, not like a watch spring — honest caveat; test it for the jog-and-return idea and drop it if it feels cheap.
- **Nudge.** A 5° twitch to say "look at me" — the notification version of self-movement.

## The two things you asked to have explained

**Any number of clicks per turn (item 3).** The magnets give exactly sixty clicks or none. The app ring has six items, so between apps you would feel ten clicks while the pointer moves once. A force motor could make clicks one to nine vanish and click ten feel big — any count, per screen. Without it you have three honest options: accept sixty clicks and let every tenth one count, with the screen showing progress in between (most menu dials do this); add a **second, smaller ring of pegs and magnets** — twelve pegs and three magnets on their own sliding carrier — so the knob has three physical feels, sixty clicks, twelve clicks, or free; or use the drive wheel's brake to make the non-counting clicks feel damped. The second peg ring is the one worth drawing.

**A notch at a saved value (item 5).** A single extra dip you can feel at one particular position — your usual volume, the centre of a balance or tone control, the last place you left a scrub — so you can find it by hand without looking. A force motor can put a dip anywhere. Nothing passive can, because it would need a peg that moves. The nearest substitute is the vibration actuator giving one tick as you pass the value.

## Height and diameter

Nothing here depends on the 135 mm outside diameter. The wheel needs a smooth cylindrical band on the knob somewhere the base can reach it — on the inside face of the skirt in the current design, or on the inner ring of the two-piece knob if the smaller-diameter concept goes ahead — about 6 mm tall. The motor lies flat in the base. No height is added.
