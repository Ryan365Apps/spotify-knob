# State table — the 60

One row per device state: what each output channel does. Names are the internal
vocabulary defined in `tokens.md`. All timing and brightness values are design
targets (V — to verify on hardware). "—" means the channel deliberately does
nothing, which is a designed state, not an omission.

| State | Screen | Halo | Sound | Detent (motor profile) |
|---|---|---|---|---|
| Boot | wireframe self-draw → ring menu, dot lands (2400 ms) | one white sweep, 30% | `hello` at dot-land | calibrating, then `firm` |
| Asleep (idle) | dark, or clock at ≤ 33 px equivalent stillness | `off` | — | `free` (bare magnets — always alive) |
| Wake | active context settles in (240 ms) | context state resumes | — | context profile |
| Now Playing | track, album art in r ≤ 220 disc | `off` | — | `firm` |
| Volume turn | green arc + numeral follow knob 1:1 | green `tick` at knob angle | — | `firm` |
| Volume limit | 4 px compression against stop | green `wall` flash | — | `wall` |
| Seek | amber scrubber follows knob 1:1 | amber `tick` | — | `feather` |
| Mute | red mute glyph, still | red `record`-style solid, 25% | — | `firm` |
| Timer — setting | bloom fills with knob, numerals count | green `arc` (gauge-mapped) grows | — | `firm` |
| Timer — set-point lands | bloom settles, numerals weight up (240 ms) | arc end blooms 150%→100% | `latch` ±10 ms of actuator | `firm` + one actuator tick |
| Timer — running | arc creeps clock-slow; screen otherwise still | green `arc` shrinking | — | `firm` |
| Timer — end | bloom releases, 0:00 alone | white slow pulse until touched | `land` ×3, 8 s apart, then silent | `firm` |
| Call incoming | call context arrives (360 ms) | green `breathe` | `hail` once | swaps to call profile at t=0 |
| Call active | mute button, call time | green `breathe`, slower | — | `firm` |
| Needs-you (agent permission) | request card arrives | amber `hold` — solid, motionless | `hail` once | `firm` |
| Dictation / recording | recording state, red element | red `record` — solid 25%, never animated | — | `firm` |
| End-stop reached | 4 px compression, `settle` back | owner-hue `wall` flash | — | `wall` |
| Press | element 100%→94%→100% (120 ms) | — | `tick` ±10 ms of actuator | actuator tick (no magnet at press) |
| Long-press | threshold ring draws linear 600 ms | — | `yes` on fire, if confirming | soft tick at 0, firm tick at 600 ms |
| Confirm | element settles (240 ms) | — | `yes` | — |
| Error / deny | one ±3 px shake (240 ms) | — (amber `hold` only if systemic) | `no` | double actuator tick |
| USB connect | device glyph lands | one white tick at gap edge | `hello` | — |
| USB disconnect | device glyph lifts out | one white tick at gap edge | `goodbye` | — |
| Low-priority notification | one still dot fades in | — | — | — |
| Context leaving | outgoing `exit`, incoming `settle` (240 ms) | crossfade to new owner state | — | new profile at t=0 |

Standing laws the table encodes: the speaker never voices rotation (magnets own
the click); red never means error (red = mute and recording only, per the design
law in `docs/VISION.md`); the halo and screen never animate at once except the
timer set-point landing; escalation always travels halo → screen → sound.
