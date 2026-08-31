# Radial — feasibility, architecture and the conditions for commercial viability

**Date:** 2026-08-31
**Answers:** `COMMERCIAL-BRIEF.md` §3 and §7, and the follow-up question — not *"can I sell this"* but *"what would have to be true for a hardware device here to be commercially viable."*

**How to read this.** Part 1 establishes what is closed and why, because it constrains everything after it. Part 2 sets out the three architectures that survive. Part 3 is the substance: seven gates, each a condition that must hold, each with a test. Part 4 describes the product that clears them. Part 5 is what to do next, cheapest first.

Figures marked **[estimate]** are my own and need verification before any money moves. Figures without that mark are sourced, and the sources are at the end.

---

## Part 1 — What is actually closed, and the principle that follows

The brief asks whether Spotify licensing permits selling this. It does not, and it is worth being precise about the shape of the closure, because the shape determines the workaround.

**Three independent closures.** Any one would be enough; all three hold.

1. **Developer Terms §II.1** limits approved devices to *"desktop computers, laptops, netbook PCs, tablets, mobile, and such other devices that we approve in writing from time to time."* A standalone Wi-Fi dial is not on the list.

2. **The Commercial Hardware programme is shut to new applicants.** Spotify's own eligibility page: *"Spotify currently accepts applications only from organizations (not individuals)"* and — decisively — *"Spotify only accepts **new** applications if you want to integrate a digital voice assistant such as Amazon Alexa or Google assistance."* This closes the brief's §3 question 2 without needing to test whether a control-only device would qualify. Unless the product embeds Alexa or Google Assistant, the eSDK route does not exist.

3. **Extended quota mode is arithmetically out of reach.** It now requires a registered business entity, a launched service, availability in key Spotify markets, "commercial viability", and **a minimum of 250,000 monthly active users**. There is no intermediate tier between development mode and that floor. A desk accessory will not reach 250k MAU.

Development mode meanwhile got tighter, not looser: as of February 2026, five authorised users per app (down from 25), Premium required for the developer account, one Client ID per developer (raised to 25 in July 2026), and a reduced endpoint set for new Client IDs.

**The direction of travel is consistent.** Two crackdown waves — November 2024 and February 2026 — removed endpoints and data fields wholesale. Spotify issued a cease-and-desist in October 2025 over a 100-line metadata scraper. Nothing suggests a reversal.

### Why the Stream Deck workaround does not transfer as-is

Elgato Stream Deck+, Ulanzi Deck and MiraBox StreamDock all ship Spotify control on physical dials today, and all handle licensing the same way: **the buyer creates their own Spotify developer app** and pastes a Client ID and Secret into the software.

The reason this works is not the bring-your-own-credentials trick. It is that **the software runs on the PC**. The API call originates from a laptop — explicitly an approved device under §II.1. The hardware is a USB peripheral sending button presses to an approved device; Spotify never sees a dial.

A standalone Wi-Fi knob calling the API itself is the exact thing §II.1 does not cover. Having each buyer supply their own credentials changes *who* is in breach, not *what* is in breach — and it means shipping setup instructions that walk every customer into a terms violation. That is not a foundation for a product with a warranty.

**The principle to carry forward:** *any commercially viable version of this device either makes no Spotify API calls at all, or makes them from a computer.* Everything in Part 2 follows from that one line.

---

## Part 2 — The three architectures that survive

| | **A — Host-tethered** | **B — Untethered HID** | **C — Standalone + BYO credentials** |
|---|---|---|---|
| **Control path** | USB/BLE HID to a PC, or serial to a companion app | BLE or USB HID media keys | Spotify Web API direct from device |
| **Metadata source** | OS media session on the host | None | Spotify Web API |
| **Album art** | **Yes** (Windows), fragile on macOS | **No** | Yes |
| **Works with** | Anything playing on that PC — Spotify, YouTube, Apple Music | Anything, any host | Spotify only, anywhere |
| **Needs Spotify API** | **No** | **No** | Yes |
| **Legal exposure** | **None** | **None** | High, and shifted onto the buyer |
| **Volume on a phone** | n/a (PC playback) | **Yes** — system volume, no 403 | **No** — `VOLUME_CONTROL_DISALLOW` |
| **Setup burden** | Install one app | **None** | Wi-Fi + OAuth + Client Secret entry |
| **Re-auth every 180 days** | No | No | **Yes, forever** |
| **Brick risk from Spotify** | None | None | **Total** |
| **Software to maintain** | Desktop app, per-OS | Firmware only | Firmware only |

**A is the only architecture that keeps album art without touching Spotify's API.** Windows exposes `GlobalSystemMediaTransportControlsSessionManager`, which returns title, artist and a thumbnail for whatever is playing, whichever app is playing it. That is the whole product's visual identity, preserved and made player-agnostic in one move.

**macOS is a genuine liability, not a porting task.** There is no public equivalent. `MediaRemote` is a private framework, Apple broke it in macOS 15.4, and there is an open developer request asking Apple to provide a supported API. A Mac build would sit on a framework Apple is actively closing. Treat Mac as out of scope, explicitly, rather than as a later milestone.

**B is trivially legal and technically easy, and it destroys the differentiator.** No metadata means the round 360×360 screen shows a clock and a generative pattern. The screen is the most expensive component and the entire aesthetic case for the object; B pays for it and then does not use it.

**C is what `BUILD.md` describes.** It is the right architecture for a personal device and the wrong one for a product, for every reason in the table.

One board-level note for A and B: this dev board's USB-C data lines are switched between its two onboard MCUs by plug orientation (`BUILD.md` §10, Checkpoint A). "Flip the cable if it doesn't work" is acceptable on a dev board and unshippable on a product — a custom PCB removes it, but it rules out USB HID on *this* board.

---

## Part 3 — Seven gates

These are conditions, not opinions. Each has a pass/fail test. A product that clears all seven is viable; one that fails any single gate is not, and the cheapest thing to do is find out which one fails first.

### Gate 1 — BOM must escape the dev board

The Waveshare board is **$44.99–46.99 direct, $48.75 on AliExpress, $52.99 on Amazon**. Call it £38–42 landed.

A direct-to-consumer hardware product needs roughly **2.5–3× fully-loaded cost** to survive returns, support, payment fees and restocking; a retail-channel product needs **4–5×**. On the dev board alone, before case, power supply, packaging, cable or a single minute of labour, that is a £95–125 product at the direct multiple. Add an enclosure and packaging and the same maths lands at £160–210 for an object built on a $45 dev board — competing against a Stream Deck+ at £160 that does vastly more.

**The dev board is a prototyping decision that cannot survive into production.** A custom PCB carrying an ESP32-S3-WROOM module, the round panel, an encoder and a haptic driver removes the second MCU, the audio DAC, the mic, the SD slot, the battery circuitry and the 3.5 mm jack — none of which this product uses.

**[estimate]** Electronics BOM at 1,000 units: **£14–22**, of which the 1.8" 360×360 round panel is likely more than half. Round colour LCDs at this size are a specialty part with few suppliers — this is both the cost driver and the supply risk. Enclosure adds £6–15 depending on process; machined aluminium is expensive per-unit, injection moulding shifts it to **£3–8k of tooling [estimate]** amortised across the run.

> **Test:** three quotes for the panel at 500/1,000/2,000 units, and one turnkey PCBA quote at 1,000. Free, takes two weeks, and it is the single most decision-relevant number in this document.
>
> **Pass:** landed cost per finished unit under £35 at 1,000 units.
> **Fail:** over £50 — at which point no viable price point exists (Gate 2).

### Gate 2 — The price must commit to one end of a barbell

The market is served at both ends and hollow in the middle:

- **Commodity USB volume knobs**: $10–25 on Amazon, dozens of SKUs, plug-and-play, play/pause/skip/mute.
- **Elgato Stream Deck+**: ~$160–200, four dials, touchscreen, plugin ecosystem including Spotify.
- **Griffin PowerMate**, the iconic single-dial controller: discontinued.

**The £60–90 middle is where this dies.** Too expensive to be an impulse purchase, too cheap to read as a designed object, and beaten on features by something at £160.

That leaves two positions:

- **Under ~£35.** Requires a BOM under £10 and volumes in the thousands. Unreachable with a round colour LCD. Rule it out.
- **£120–160.** Reachable, but only if the object justifies it: album art on the round screen, a machined case, and no setup ritual. This is the only surviving position, and it is worth noting that it demands Architecture A specifically.

> **Test:** does the BOM from Gate 1 support a £120–160 retail price at a 2.5–3× multiple, with the enclosure quality that price implies?
>
> **Pass:** yes, with £40+ gross margin per unit.
> **Fail:** the answer requires pricing at £70–100.

### Gate 3 — The differentiator must survive the architecture

The only defensible asset is **album art filling a circular screen**. It is what makes it an object rather than a knob, and it is what justifies Gate 2's high position.

Architecture B destroys it. Architecture C preserves it and cannot be sold. **Architecture A preserves it, and is the only one that does.** So the companion app is not an accessory to the product — it *is* the product's differentiator, and Windows-first is a positioning decision rather than a compromise.

This has a consequence worth stating plainly: it makes the addressable market *Windows desktop users who listen to music while working*, not *Spotify users*. That is a smaller and much better-defined market, and it is reachable — desk-setup communities, r/battlestations, productivity and audio channels — in a way "Spotify users" never was.

> **Test:** build the companion app spike. Windows SMTC → album art and metadata → a dev board over USB serial, rendered on the round screen.
>
> **Pass:** art appears within ~1.5 s of a track change, from any player, with no Spotify credentials anywhere in the system.
> **Fail:** SMTC thumbnails prove unreliable or too slow across Spotify, a browser and Apple Music.

### Gate 4 — Support cost per unit must stay under ~£5

This is where hobby hardware becomes a business or does not.

At £140 retail with 40% gross margin, each unit yields roughly **£56 gross [estimate]**. One 20-minute support exchange, valued at £30/hour, costs about £10 plus the context-switch. A **15% contact rate is survivable. A 50% contact rate is not** — and it does not merely reduce margin, it consumes the founder's time until shipping more units makes things worse.

The current design has three failure moments, and they are the three worst kinds:

| Moment | Architecture C | Architecture A |
|---|---|---|
| Wi-Fi setup | Captive portal on a device with no keyboard | **Gone** — it is a USB peripheral |
| Initial auth | OAuth + Client ID + **Client Secret** onto a 360×360 round touchscreen | **Gone** — no accounts |
| Re-auth at 180 days | Every unit, twice a year, forever | **Gone** — nothing expires |

Wi-Fi provisioning and OAuth on a screen with no keyboard reliably produce contact rates far above 15%. **Architecture A removes all three failure moments outright.** That is a stronger commercial argument for A than the legal one, and it compounds: no support burden also means no refund wave, no review-score damage, and no recurring obligation attached to units sold two years ago.

> **Test:** hand an assembled unit and its packaging to five people who have never seen it. Count how many reach music playing without asking a question.
>
> **Pass:** 4 of 5, unaided, under five minutes.
> **Fail:** anyone needs to be told anything not printed in the box.

### Gate 5 — Volume must clear the fixed costs

Certification, tooling and setup do not scale down. **[estimate]** a first run below ~500 units cannot amortise them; 1,000–2,000 is where the numbers start working.

For a solo maker with no existing audience, a niche desk accessory on Crowd Supply, Kickstarter or Tindie plausibly moves **200–1,500 units [estimate]** on a first campaign. That straddles the amortisation threshold, which means **audience is a prerequisite, not a launch activity**. The realistic sequence is: build an audience around the object over months, then run the campaign — not campaign-first.

> **Test:** a landing page showing the rendered screens (`design/screens.html` already exists — the asset is built), posted to two or three relevant communities. Measure email signups over two weeks.
>
> **Pass:** 500+ genuine signups from organic posts. That predicts a fundable campaign.
> **Fail:** under 150. Not a verdict on the product — a verdict on reaching the people who would buy it, which is the harder problem.

### Gate 6 — Compliance must be budgeted, not discovered

A product with a 2.4 GHz radio sold in the UK/EU needs UKCA/CE marking, EMC testing, and RED (Radio Equipment Directive) conformity; the US needs FCC. Using a **pre-certified module** — ESP32-S3-WROOM rather than a bare chip — removes the radio testing, which is the expensive half, but does **not** remove finished-product EMC testing. Add RoHS, WEEE registration and packaging regulations.

**[estimate] £2–6k** for a product built on a pre-certified module. This is the line item that most often kills a maker project after the prototype works, because it arrives at the point where the money has already gone into tooling.

> **Test:** one email to a UK test house describing the product and the module, asking for a ballpark. Free, one week.
>
> **Pass:** the figure is budgeted before tooling is ordered.
> **Fail:** it is discovered after.

### Gate 7 — The product must have no brick date

**Car Thing is the case study, and it is unambiguous.** Spotify's own control-only device, $89.99, backed by Spotify's brand with zero licensing friction. Production ended 15 months after launch. Spotify took a **$31.4 million** loss on it and **bricked every unit in December 2024**, prompting refund demands.

Any product that depends on a third-party cloud API at runtime has a shutdown date it does not control. For Architecture C that risk is not hypothetical — it is a company that has already demonstrated both the willingness to revoke API access at scale and the willingness to brick its own hardware.

Architectures A and B have no brick date. Nothing to revoke, nothing to expire, no account to lose. A device that works identically in 2035 is a materially different product to sell, warrant and review.

> **Test:** if the vendor of every third-party service vanished tomorrow, does the device still do its primary job?
>
> **Pass:** yes.
> **Fail:** anything else.

---

## Part 4 — The product that clears all seven

Stated concretely, because "a generic media controller" is too vague to evaluate:

> A machined-aluminium desk dial with a 1.8" round screen. Connects to a Windows PC by USB-C. A small companion app reads the OS media session and streams album art, title and artist to the device; the dial adjusts system volume, and a tap gives previous / play-pause / next. It shows the artwork for **whatever is playing** — Spotify, YouTube in a browser, Apple Music, a local file. No account, no Wi-Fi, no login, nothing that expires. Positioned at **£120–160** as a desk object, sold to people who build their desk setups deliberately.

Against the gates: BOM clears if the panel quotes come back reasonable (1); the price commits to the top of the barbell (2); album art survives and becomes player-agnostic, which is strictly more valuable than Spotify-only (3); all three support moments are eliminated (4); the audience is definable and reachable (5); compliance is a known, budgetable figure (6); and there is nothing that can ever be revoked (7).

### The tension worth naming

This product does not do the thing `BUILD.md` was written for.

R6 requires it to work when playback is on a **phone or a Connect speaker, explicitly not the PC**. Architecture A only knows about audio playing on the PC it is plugged into. The sellable product and the personal product are different devices, and no amount of engineering reconciles them — the requirement that makes the personal version good (follow playback anywhere via the cloud) is the exact requirement that makes it unsellable.

That is the honest centre of this assessment. It is not an argument against either device. It is an argument for being clear about which one is being built at any given moment, and for not letting the personal build quietly accumulate features on the assumption it will become the product later. **It will not become the product. It is a different product.**

### What this does for the personal build

Two findings transfer usefully and cost nothing:

- **BLE HID for volume** (see `BUILD-RECOMMENDATIONS.md` §4) removes the one real compromise in the current design — the dial doing seek instead of volume on the primary listening device. Espressif marks Wi-Fi STA + BLE connected as stable on the ESP32-S3, and Android's BLE HID media-key support is well established. It is a one-day spike after Wave 6, and it is additive: the Web API stays the source of truth for everything else.
- **The Windows companion app is a weekend spike**, and it is the cheapest possible test of Gate 3 — the highest-uncertainty gate — using hardware that is already on order.

---

## Part 5 — What to do next, cheapest first

Four tests. **None requires committing money to hardware, and three can start this week.** Run them in this order and stop at the first hard fail.

| # | Test | Cost | Time | Gate | Kill condition |
|---|---|---|---|---|---|
| 1 | **Audience test.** Landing page from `design/screens.html`, posted to two or three desk-setup communities. Count signups. | £0–200 | 2 weeks | 5 | Under 150 signups |
| 2 | **Panel and PCBA quotes.** Three suppliers, 500/1,000/2,000 units. | £0 | 2 weeks | 1, 2 | Landed cost over £50/unit |
| 3 | **Companion app spike.** Windows SMTC → album art → round screen over USB serial. | 1 weekend | 1 weekend | 3 | Art unreliable or slow across three players |
| 4 | **Certification ballpark.** One email to a UK test house. | £0 | 1 week | 6 | Over £10k |

Tests 1 and 2 run in parallel and need no hardware. Test 3 needs the board, which is arriving anyway for Wave 2, and it is a weekend rather than a wave.

**The decision point is after all four**, and it is genuinely open. My read on the prior odds is that Gate 5 — audience — is the most likely hard fail and the least discussed, and Gate 1 the most likely soft fail. Gates 3, 4 and 7 all pass comfortably under Architecture A, which is a better position than the brief's framing assumed, because the brief treated the generic route as "a worse product technically." Against these gates it is a *better* product commercially in five of seven dimensions, and worse in exactly one: it cannot follow playback off the PC.

### What would change the conclusion

- **Test 1 returns 1,000+ signups.** The audience problem is solved, and the rest is execution and money. Proceed.
- **Test 2 returns a panel under £8 at 1k.** Gate 2's low position reopens and a £60–80 product becomes arguable — which changes the strategy completely.
- **Test 3 fails.** Album art is gone, and with it Gate 3. What remains is Architecture B, competing against $15 knobs. Stop, and open-source the firmware.
- **Spotify reopens the Commercial Hardware programme to non-voice-assistant devices.** Unlikely, worth a calendar check annually, and it would change everything.

---

## Sources

Spotify: [Developer Terms](https://developer.spotify.com/terms) · [Commercial Hardware programme](https://developer.spotify.com/documentation/commercial-hardware/) · [Distribution requirements](https://developer.spotify.com/documentation/commercial-hardware/launch/requirements) · [Quota modes](https://developer.spotify.com/documentation/web-api/concepts/quota-modes) · [Update on Developer Access and Platform Security, Feb 2026](https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security) · [February 2026 migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide) · [Updating the Criteria for Web API Extended Access, Apr 2025](https://developer.spotify.com/blog/2025-04-15-updating-the-criteria-for-web-api-extended-access)

Market: [Rithum Spotify Connect Controller](https://shop.rithumhome.com/products/spotify-connect) · [Rithum launch announcement](https://rithumhome.com/rithum-launches-spotify-web-connect-integration/) · [Knobby on Tindie (retired)](https://www.tindie.com/products/milowinningham/knobby-a-little-remote-for-spotify-and-more/) · [BarRaider Spotify plugin setup](https://docs.barraider.com/faqs/spotify/getting-started/) · [Ulanzi Deck Spotify setup](https://www.ulanzistudio.com/doc/Spotify_en) · [Stream Deck+ pricing](https://www.techbuzz.ai/articles/elgato-stream-deck-plus-hits-lowest-price-at-159-99) · [Car Thing](https://en.wikipedia.org/wiki/Car_Thing)

Technical: [Waveshare board page](https://www.waveshare.com/esp32-s3-knob-touch-lcd-1.8.htm) · [CNX Software board analysis](https://www.cnx-software.com/2025/06/25/battery-powered-knob-display-board-pairs-esp32-s3-and-esp32-wireless-socs-features-audio-dac-for-audio-visualization/) · [ESP32-S3 SoC spec](https://www.espressif.com/en/products/socs/esp32-s3) · [ESP32-S3 RF coexistence](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/coexist.html) · [Windows SMTC session manager](https://learn.microsoft.com/en-us/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionmanager) · [nowplaying-cli broken on macOS 15.4](https://github.com/kirtan-shah/nowplaying-cli/issues/28) · [Request for a public macOS Now Playing API](https://github.com/feedback-assistant/reports/issues/637) · [ESP-IDF AVRCP cover art request](https://github.com/espressif/esp-idf/issues/10988)

Enforcement: [Spotify cease and desist, Oct 2025](https://thereallo.dev/blog/spotify-cease-and-desist) · [Feb 2026 third-party app crackdown](https://www.headphonesty.com/2026/02/spotify-crackdown-thousands-third-party-music-apps/)
