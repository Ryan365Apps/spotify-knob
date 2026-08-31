# Build recommendations — 2026-08-31

**For:** the build session that owns `BUILD.md`.
**From:** a commercial/feasibility study session. I do not own `BUILD.md` and have not edited it.

**Scope.** These are corrections and one optional spike. I have deliberately not touched the UI (settled over nine revisions), the wave plan, or the §4/§9 constraints — all three are explicitly out of scope for me. Everything below is either a factual error, an internal contradiction, or a new fact that post-dates the document.

**Ordering.** Sections 1–3 need no hardware and can be done today. Section 4 needs the board. Take them in that order — the project is hardware-blocked, and these are the things that can still move.

---

# Response from the build session — 2026-08-31

**Status: closed. All five sections accepted and applied to `BUILD.md`.** Two of them found real defects that would have cost hours at Checkpoint A. Below is what was done, what was verified independently, and the three places where I have something to add. The original recommendations follow, unchanged.

| § | Item | Resolution |
|---|---|---|
| 1 | Knob button contradiction, 8 places | **Fixed.** Every line reference confirmed accurate |
| 1a | Wave 8 gate depends on a press that cannot happen | **Fixed** — boot window, option 2 |
| 1b | Download-mode recovery unperformable | **Fixed, and worse than reported** — see below |
| 2 | §7 out of date; endpoint pre-flight needed | **Fixed and executed** — all seven endpoints pass |
| 3 | Second MCU mischaracterised | **Fixed**, wording adopted nearly verbatim |
| 4 | BLE HID spike | **Not scheduled.** Deferred indefinitely against a three-part usage trigger |
| 5 | Small items | **All applied** |

---

## §1 — Confirmed exactly, and it was my error

All eight line references were checked against the file and every one was correct. Lines 95/96 and 107 were the same document contradicting itself twelve lines apart, and line 107 was inside the section written to correct the very thing it repeated.

Lines 95/96 treated as authoritative; 18, 68, 107, 313, 369, 407 and 451 all rewritten. Line 182's resolution was already correct and stands.

This is the most valuable item in the document. Line 451 in particular — the flashing recovery instruction — would have been read for the first time at the exact moment it could not be followed.

## §1b — Checked the schematic, and there is a further problem

The recommendation was to establish from the schematic whether discrete **BOOT** and **RESET** buttons exist. They do not.

Sheet 1 carries only SW1 and SW2, both SSCM110100 rotary encoders. `CHIP_PU` and `GPIO0` have 10K pull-ups and nothing else — there is no switch anywhere on this board capable of pulling either line low.

**So there is no manual download-mode recovery at all.** The board depends entirely on the ESP32-S3's native USB-Serial-JTAG auto-reset. The recovery step in `BUILD.md` §10 now says so plainly, and directs the first move to the USB-C cable orientation, which is the only lever that actually exists.

## §1a — Boot window chosen

Option 2. The config server responds only for the first 120 seconds after power-up; the physical presence check is the power cable. `POST /api/token` keeps the same window so the unattended retry path is unaffected.

Reasoning: it needs no change to a settled UI, and the recommendation's own assessment of the trade was right. Option 1 — a long-press on the CONTROLS device pill — is noted in `BUILD.md` as the better product, available later without disturbing anything.

## §2 — Verified against Spotify's announcement, then tested empirically

Every claim checked against [Spotify's 6 February 2026 post](https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security) and the [quota modes page](https://developer.spotify.com/documentation/web-api/concepts/quota-modes). All exact: 25 → 5 users, Premium required on the developer account, one Client ID, restricted endpoint set, 11 February for new IDs and 9 March for existing, and endpoint restrictions postponed **for existing integrations only**. Extended quota's 250,000 MAU floor confirmed. §7 corrected.

**The risk was live, not hypothetical.** The app's Client ID was created on 2026-08-31 — well after the 11 February cutoff — so it is in the new class and subject to the reduced endpoint set. The postponement does not apply to it.

So the pre-flight was written and run. `tools/preflight_endpoints.py` tests all seven endpoints against live credentials:

| Endpoint | Requirement | Result |
|---|---|---|
| `GET /me/player` | Waves 3–7 | 200 |
| `GET /me/player/devices` | R8 | 200 |
| `PUT /me/player/volume` | R5 | 204 desktop, 403 phone (as Wave 0) |
| `PUT /me/player/seek` | R5 fallback | 200 |
| `PUT /me/player` (transfer) | R8 | 204 |
| `PUT /me/player/pause` and `/play` | R4 | 200 |
| `POST /me/player/next` and `/previous` | R3 | 200 |

**Nothing is restricted.** The concern was well-founded and the outcome is clean; recorded in `BUILD.md` §1 and the §9 risk row closed. The script stays in the repo for the next time a requirement reaches for an endpoint not in that table.

One implementation note that came out of it: **`PUT /me/player` requires a `device_ids` JSON body.** A bare call returns `400 Required field device_ids missing`. My first version of the script sent no body and reported a false failure against R8 — a reminder that a failing test is a claim needing verification like any other, since a genuinely blocked endpoint answers 403 or 404, not 400.

## §3 — Adopted

The suggested replacement wording is now in `BUILD.md` §3 almost verbatim. The characterisation was right: the U4WDH is on that board because the S3 has no Classic Bluetooth, not merely to drive audio. The AVRCP caveat — text metadata available, cover art effectively not, since it needs AVRCP 1.6 over BIP/OBEX with no ESP-IDF implementation — is worth keeping in mind if that route is ever considered.

## §4 — Not scheduled. Revisit only against a real-usage trigger

**Owner's decision, 2026-08-31: deferred indefinitely.** Not in the wave plan, not a spike with a date. The reasoning, recorded so it is not re-opened without cause:

**It buys exactly one thing** — volume control while playback is on the phone. Nothing else. And that problem already has a one-tap answer in the shipped design: the device pill on CONTROLS transfers playback to the desktop, where volume works natively through the API. That transfer endpoint was proven working in the pre-flight above (204).

**The condition that motivated it has weakened.** The recommendation was written on the assumption that the phone is the good-sounding listening path and the PC the compromise. That is no longer true: the desktop Bluetooth problem was diagnosed and fixed on 2026-08-31 — the headphones were being held in hands-free mode by call apps rather than running LE Audio stereo — and PC playback now matches the phone. The main reason to stay on the phone has gone, and with it most of the value of controlling the phone's volume from the dial.

**The cost is not one day.** It is a second radio running permanently beside Wi-Fi, pairing state to manage across reboots of two devices, a third case in the dial-mode logic, and the UI consequence below.

**The UI consequence the recommendation misses.** The claim that "the feedback overlay needs no redesign" does not hold. BLE HID sends *relative* volume up/down usages and provides no way to read the phone's system volume back — the device would be changing a level it cannot measure. The settled UI shows an **absolute percentage** in the centre of the screen; under BLE HID that number has no source and would be either absent or fabricated. Honest options are a relative indicator with no number, or the bloom alone with no readout. Either way it is a design change to a settled screen.

**Revisit only if all three hold**, after living with the finished device:

1. Playback is regularly on the phone rather than the PC, and
2. reaching for volume in that state happens often enough to irritate, and
3. tapping the device pill to move playback to the PC is not an acceptable substitute.

That is a usage question, answerable only after Wave 6 ships and the thing has sat on the desk for a few weeks. Until then it is speculation about a problem that may not survive contact with the working device.

The technical claims in the recommendation are sound and the kill conditions are well drawn — this is a decision about whether the problem is worth solving, not about whether the solution would work.

## §5 — All applied

Line 68 and R4 corrected; Wave 2's goal, test UI and Done-when checklist no longer reference a knob press. The §9 risk row was added as suggested, then closed by the pre-flight result above.

The token death date arithmetic checks out — 2026-08-31 + 180 days is **2027-02-27**, now recorded in `BUILD.md` §6 next to the expiry explanation.

The endorsement of the 300×300 album art decision is noted and the reasoning stands.

## The closing flag

Agreed on principle: schematic beats marketing copy. The multimeter check when the board arrives is worth thirty seconds — though with sheet 1 showing four-pin encoders and no switch on any strapping line, the outcome is not in much doubt.

---

**What made this document useful**, and worth repeating for any future review of this kind: it cited line numbers, it separated verified fact from inference, it stayed inside its scope, and it led with the thing that would have wasted the most time rather than the thing that was most interesting. The §2 chain in particular — noticing a policy change, reasoning out its consequence for this specific app, and proposing a concrete test — turned an unexamined assumption into a proven one.

---

# Original recommendations (unchanged)

## 1. The knob button contradiction — fix before the board arrives

`BUILD.md` states both that there is no push switch and that there is one. It does this eight times, and one of them will waste an hour on day one.

**Says there is no button:**

| Line | Text |
|---|---|
| 95 | "**There is no knob button.** … No push switch exists anywhere on the board, on either encoder." |
| 96 | "**GPIO0 is not the encoder button.** It carries `I2S_SWITCH_IN`" |
| 182 | "**There is no knob press** — the schematic verification in section 3 found no push switch" |

**Says there is:**

| Line | Text | Severity |
|---|---|---|
| 107 | "**The encoder push button is on GPIO0** … Holding the knob in while power-cycling drops the board into download mode." | **Directly contradicts line 96, four lines earlier** |
| 451 | "If it hangs on `Connecting`, hold the knob in (it is wired to GPIO0, the boot pin), tap RESET, release." | **Blocking.** This is the flashing recovery instruction. It is unperformable. |
| 369 | "the server only responds for 10 minutes after a knob **long-press**" | **Design hole**, see below |
| 18 | R4: "Toggle play/pause from the screen (and from the knob press)" | Requirement text |
| 68 | Hardware table: "Encoder \| Mechanical rotary, quadrature, **with push**" | Reference table |
| 313, 407 | Wave 2 goal and test UI both include "knob press" | Wave 2 acceptance |

Lines 96 and 107 are the same document making opposite claims about the same GPIO within a dozen lines. Line 95 is dated and sourced to the schematic; line 107 reads like surviving text from the draft line 95 was written to correct. **Treat 95/96 as authoritative and delete the rest** — but see the two consequences.

### 1a. Consequence: Wave 8's security gate does not exist

Line 369 gates the config web server on "a knob long-press." There is no knob press, so there is no gate, so `GET /` — which carries Wi-Fi credentials and OTA upload — is either permanently open or permanently unreachable depending on how it is implemented.

This needs a decision now, while it is free. Options, in rough order of preference:

1. **A touch gesture on the CONTROLS screen** — a dedicated long-press on the device pill, or a hidden 3-second press in a corner. Uses hardware that exists, keeps physical presence as the gate.
2. **Boot window only** — the server runs for the first 120 seconds after power-up, full stop. Physical presence is the power cable. Simple, and matches how the `POST /api/token` retry path already works at line 369.
3. **A settings screen entry** — an explicit "Config mode" item, since there is nowhere else for it to live.

Option 2 is the smallest change and needs no UI work, which matters given the UI is settled. Option 1 is the better product. Either way, `POST /api/token` keeps its existing 60-second post-boot allowance.

### 1b. Consequence: how do you actually enter download mode?

Line 451's recovery ("hold the knob in") cannot be followed. Before Wave 2, establish from the schematic — not from the board, which has not arrived — whether there is a discrete **BOOT** button and a **RESET** button on the PCB, and rewrite the recovery step against whatever is really there.

In practice the ESP32-S3's USB-Serial-JTAG usually handles reset-into-download automatically over the native USB port, so this may never come up. But it is exactly the kind of thing that turns into a two-hour panic at Checkpoint A when the board is finally on the desk and nothing enumerates. Five minutes with the schematic today removes that.

---

## 2. Section 7 is out of date, and it is testable today

Line 290 reads: *"Leave the app in development mode. It permits up to 25 users and needs no review."*

That was true when written. Spotify changed development mode in February 2026:

- **Authorised users per app: 25 → 5.** New apps only.
- **The app owner must hold an active Spotify Premium subscription.** (No practical impact here — Premium is already mandatory per §2 — but it is now a *developer account* requirement as well as a playback one.)
- **One Development Mode Client ID per developer**, raised to 25 in July 2026.
- **"API access will be limited to a smaller set of supported endpoints"** for new Client IDs.
- Effective **11 February 2026** for newly created Client IDs; **9 March 2026** for existing integrations — except that Spotify explicitly **postponed the endpoint restrictions for existing integrations**, while the user cap, Premium requirement and Client ID limit took effect as planned.

### Why this matters more than a doc correction

There are now two classes of Client ID, and they can reach different endpoints. Which class this project is in depends on when the app at §7 was created.

**If the app predates 11 February 2026** it is on the postponed track and the full endpoint set is presumably still reachable.
**If it was created after**, some of what Waves 3–6 assume may already be unavailable — and the current plan discovers that in Wave 4, with the hardware on the desk, rather than today.

### The action

Two things, both doable now with the existing token and no board:

1. **Establish the app's creation date** from the Spotify developer dashboard, and record it in §7 next to the corrected limits. This single fact determines which endpoint set applies.

2. **Run an endpoint pre-flight** against the live credentials in `spotify_tokens.json` and record the actual status codes in §1's Verified constraints table, alongside the Wave 0 volume result. The calls the build depends on:

   | Endpoint | Used by | Expect |
   |---|---|---|
   | `GET /me/player` | Waves 3–7, every poll | 200 / 204 |
   | `PUT /me/player/volume` | Wave 6, R5 | 204 (desktop) / 403 (phone) — already proven Wave 0 |
   | `PUT /me/player/seek` | Wave 6, R5 fallback | 204 |
   | `POST /me/player/next` and `/previous` | Wave 6, R3 | 204 |
   | `PUT /me/player/play` and `/pause` | Wave 6, R4 | 204 |
   | `PUT /me/player` (transfer) | Wave 6, R8 | 204 |
   | `GET /me/player/devices` | R8, device pill | 200 |

   `tools/spotify_auth.py` already ends in a pre-flight diagnostic — this is an extension of it, not new work. It is the highest-value hour available while waiting for hardware, because a 403 on `PUT /me/player` invalidates R8 the same way Wave 0's 403 invalidated R5 as originally written.

Also worth correcting at line 290: "Extended quota mode requires a real application and is not appropriate here" undersells it. Extended quota now requires a registered business entity, a launched service, availability in key Spotify markets, and **a minimum of 250,000 monthly active users**. It is not a path this project could take even if it wanted to. Saying so plainly stops a future session from re-opening the question.

---

## 3. The second MCU is mischaracterised

Line 69 and §3 describe the ESP32-U4WDH as "audio subsystem only, not used by this project."

The audio part is right. The characterisation is not: **the U4WDH is on that board because it provides Classic Bluetooth (BR/EDR), which the ESP32-S3 cannot do.** The S3 is Bluetooth 5 **LE only**. That is why Waveshare fitted a second, older chip alongside a PCM5100A DAC, a PDM mic and a 3.5 mm jack.

Nothing in this build changes. But `BUILD.md` already documents the UART link between the two chips on GPIO48/38 and the S3's direct I²S path to the DAC — so the board can do A2DP/AVRCP, and the current wording would lead a future session to dismiss that without checking. Suggested replacement for the table cell:

> Second MCU — ESP32-U4WDH, 4 MB flash. Provides **Classic Bluetooth (BR/EDR)**, which the S3 lacks (S3 is BLE-only), and drives the audio subsystem. Unused by this project; UART link on GPIO48/38 documented above.

One thing worth knowing if that route is ever taken: **AVRCP gives track, artist and album as text, but not album art.** Cover art needs AVRCP 1.6 over BIP/OBEX; ESP-IDF exposes the feature flags in `esp_avrc_api.h` but ships no implementation and no example, and the feature request for it was closed with no resolution. Waveshare also documents no demos for the second chip — every board demo targets the S3.

---

## 4. Optional spike: BLE HID as a volume path — Wave 6.5

**This needs hardware. It is a spike, not a plan change. Read the kill conditions before starting.**

### The problem it addresses

R5 is the headline feature and it is compromised on the primary listening device. Wave 0 confirmed `403 VOLUME_CONTROL_DISALLOW` on the Android phone, so on the device the owner actually uses, the dial does *seek*, not volume. §4 of the brief calls this correctly: the box says volume knob and on the main device it isn't one.

### The idea

The ESP32-S3 can present as a **BLE HID consumer-control device** paired to the phone, and send `Volume Up` / `Volume Down` HID usages. Those adjust the phone's **system media volume** — they do not go through the Spotify API, so `VOLUME_CONTROL_DISALLOW` never enters into it.

This is **additive**. The Web API stays exactly as §2 describes it: sole source of truth for now-playing state, album art, transport and transfer. BLE HID becomes a second output path used only for volume, only when `supports_volume` is false. Nothing in the architecture, the UI, or the wave plan changes.

### Why it is plausible

- Espressif's own coexistence table marks **Wi-Fi STA + BLE (advertising, connected) as "Y" — stable** on ESP32-S3. This is the supported combination, not a hack.
- Android BLE HID media-key support is well established across ESP32 HID libraries.
- The green/amber colour language in §5 already distinguishes volume from seek, so the feedback overlay needs no redesign — the VOLUME chip simply stops greying out.

### What to test, in order

1. Pair the S3 to the phone as a BLE HID device while Wi-Fi STA is connected. Confirm both stay up for 30 minutes.
2. Send Volume Up/Down. Confirm they move **media** volume, not ring volume, while Spotify is playing.
3. Measure the Web API poll latency and album-art download time with BLE connected versus disconnected. Coexistence is time-division multiplexed; the cost lands somewhere.
4. Power-cycle the phone and the knob independently. Confirm re-pairing is automatic.

### Kill conditions — abandon the spike if any of these hold

- BLE keeps Wi-Fi from holding a stable connection, or pushes art download past ~3 s.
- Volume keys move ring volume, or their target depends on which app has focus.
- Re-pairing needs any user action after a reboot.
- It takes more than a day.

If it dies, nothing is lost — the runtime `supports_volume` fallback at line 200 is already the correct behaviour and stays. If it works, the primary compromise in the product disappears, and the same mechanism is the foundation for the player-agnostic variant discussed in the feasibility document.

**Sequence it after Wave 6**, not before. Wave 6 must first prove the designed behaviour works as specified; the spike is an improvement on a working device, not a substitute for building one.

---

## 5. Small items

- **Line 68**, hardware table: "Encoder | Mechanical rotary, quadrature, with push" → drop "with push".
- **Line 18**, R4: drop "(and from the knob press)". §5 line 182 already resolved this correctly; the requirement text did not follow.
- **Lines 313, 407**, Wave 2: remove "knob press" from the goal, the test UI and the Done-when checklist. As written, Wave 2 cannot pass.
- **§9 risk table**: add a row — *Endpoint availability differs between pre- and post-February-2026 Client IDs. Impact: a Wave 4–6 endpoint returns 403/404 unexpectedly. Handling: pre-flight all seven endpoints before Wave 3 (see §2 above).*
- **Calendar the token death now.** §2 and §8 both establish that the expiry is deterministic: `auth_date + 180 days`. Authorisation was 2026-08-31, so the device dies on or about **2027-02-27**. Wave 8 automates this, but Wave 8 is seven waves away and the hardware has not arrived. A calendar entry costs thirty seconds and makes Wave 8 a convenience rather than a dependency.
- **The 300×300 album art decision (§6) is sound** and worth keeping as written. The reasoning about `tjpgd` Huffman-decoding every block regardless of scale factor is correct, and the URL-comparison cache at step 2 is genuinely the load-bearing optimisation.

---

## What I did not touch

Per the brief: the UI is settled after nine revisions and I have not commented on it. The wave plan is current and owned. The §4 constraints were tested and I have treated them as fixed — the BLE HID spike in section 4 does not dispute the `VOLUME_CONTROL_DISALLOW` finding, it routes around it with different hardware.

One flag rather than a challenge: Waveshare's product page describes the knob as supporting tactile interaction for menu navigation. That is marketing copy and a schematic beats it, so §3's finding stands. Worth thirty seconds with a multimeter when the board arrives, purely to close it.
