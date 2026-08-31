# Radial — brief for a productisation study

**Written for a fresh session with no prior context.** Everything you need is in this document plus the two files it points at. You are not expected to read the conversation that produced it.

**Your job:** work out whether this could become a commercial product, and what that would take. Competition, pricing, positioning, UX, manufacturing, and risk. You are not being asked to build anything, and the technical design below is settled — treat it as given, not as something to improve.

---

## 1. What it is

A dedicated physical dial that sits on a desk and controls Spotify.

It is a **remote control, not a player.** It never touches audio. Spotify plays wherever it was already playing — a phone, a laptop, a speaker — and this device tells Spotify what to do over the internet, the same way the controls on your phone's lock screen do.

The hardware is an off-the-shelf development board: a **Waveshare ESP32-S3-Knob-Touch-LCD-1.8**. A 1.8-inch round 360×360 touchscreen with a rotary encoder around it, Wi-Fi, in a machined metal case. It is bought, not designed.

What it does:

- Shows the album art of whatever is playing, filling the round screen
- Shows track title and artist
- The dial adjusts volume
- One tap brings up previous / play-pause / next, and a switch to make the dial scrub through the track instead
- When nothing is playing, it becomes a slowly evolving generative pattern with a clock

The whole point is removing a small daily friction: at a desk for hours, changing volume or skipping a track currently means picking up a phone, waking it, finding Spotify, and tapping. This makes it a movement of one hand without looking away from the screen you were already looking at.

---

## 2. Where the project actually is

Be precise about this, because it affects what "productising" means.

| Built and proven | Designed but not built | Not started |
|---|---|---|
| Spotify authentication, working, with a token-minting script | All seven screens, at true pixel size, in a rendered mockup | Any firmware beyond a dependency check |
| Verified pin map read off the manufacturer's schematic | The full interaction model | Enclosure, branding, packaging |
| A full library stack that compiles clean | An eight-wave build plan with test conditions | Any commercial work at all |

**The hardware has not arrived yet.** Nothing has ever run on the device. This is a design and a plan, not a working prototype.

Two supporting files, both in this repo:

- `BUILD.md` — the complete technical build document. Requirements, architecture, verified wiring, interaction model, and the wave-by-wave plan.
- `design/screens.html` — the seven screens, live and animating at their real 360×360 size. Open it in a browser.

---

## 3. The commercial blocker you must resolve first

**Spotify's Developer Terms almost certainly prohibit this as a product, and everything else in your study is moot until you have established the position.** Do this before pricing, before competitors, before anything.

Section II.1 of the [Developer Terms](https://developer.spotify.com/terms) restricts approved devices to *"desktop computers, laptops, netbook PCs, tablets, mobile, and such other devices that we approve in writing from time to time."* A dedicated hardware knob is not on that list. Building one for personal use is a hobbyist reading of the terms; selling one is a different question entirely.

The sanctioned route for hardware is the [Commercial Hardware programme](https://developer.spotify.com/documentation/commercial-hardware/), and it is built for a different kind of company:

- **Organisations only.** Individuals are explicitly not eligible.
- Requires an eSDK licence, an NDA, certification through Spotify's testing platform, and two physical test devices submitted for evaluation.
- Has **minimum distribution requirements** — quantities are not published, but the framing is aimed at manufacturers, not makers.
- The programme is oriented around *playback* devices (speakers, AV receivers) that receive audio via Spotify Connect. A control-only device with no audio path may not fit the programme's shape at all.

Separately, apps in development mode are limited to 25 users. Extended quota is discretionary — Spotify *"makes no promise or guarantee that such extended access request will be approved."*

**Concrete questions to answer:**

1. Has anyone shipped a commercial Spotify-only hardware controller? If not, is that because nobody tried, or because Spotify said no? Find evidence either way.
2. Does the Commercial Hardware programme accept control-only devices, or does it require an audio path?
3. Is there a legitimate reading under which a small company could ship this? What would it cost in time and money to find out authoritatively?
4. **What does the product look like if Spotify is off the table?** This is the most valuable branch. A generic media controller driving system-level media keys works with Spotify, YouTube, Apple Music and everything else, needs no API permission at all, and sidesteps the whole problem — but loses album art and needs a host computer. Is that a better product commercially even though it is a worse one technically?

---

## 4. Hard-won constraints that shape any product

These were discovered by testing, not assumed. They are facts about how Spotify actually behaves, and each one has product consequences.

**Volume control is refused on phones.** Spotify returns `403 VOLUME_CONTROL_DISALLOW` when the playback device is a phone. Tested and confirmed. It works on the desktop app and most Connect speakers. So the headline feature — turn the dial, change the volume — silently does not work on what is, for many people, their main listening device. The current design falls back to track-scrubbing. **For a product, this is a support nightmare and a review-score problem**: the box says "volume knob" and for some buyers it will not be one.

**The login expires every 180 days.** Spotify refresh tokens now have a hard six-month lifetime that refreshing does not extend. Every unit will stop working twice a year until the owner re-authorises it. The current design handles this with a scheduled task on the owner's PC. **A shipped product needs a re-authorisation flow that a non-technical buyer can complete unaided** — this is a real design problem, not a footnote.

**Spotify Premium is mandatory.** Every playback-control endpoint refuses free accounts. That is a hard gate on the addressable market.

**State is polled, not pushed.** The device asks Spotify what is playing every few seconds. The screen can lag reality by a poll interval, and there is a rate limit to respect.

**The board has no button.** Confirmed from the schematic — the knob turns but does not click. Play/pause is a touch target. If a product wanted a satisfying physical click, that means custom hardware, not this board.

---

## 5. What to explore

The obvious ground:

- **Competitors.** Look at least at: Nanoleaf/Elgato-style stream controllers, the Behringer/Loupedeck class of dial controllers, Muse/Yoto-style dedicated music appliances, Raspberry Pi based Spotify displays sold as kits, and the DIY community selling ESP32 knob builds on Tindie and Etsy. Establish whether anyone has done exactly this and what happened to them.
- **Pricing and unit economics.** The board is off-the-shelf; find its actual cost. Work out what a small run would cost with packaging and a power supply, and what price the market would bear.
- **Positioning.** Is this a music gadget, a desk-toy, a productivity accessory, or an ambient display that happens to control music?
- **UX for people who are not the builder.** Wi-Fi setup, Spotify login, and re-authorisation are the three moments where a hobby project becomes a support burden.

Ground that is less obvious but probably more important:

- **Is the product the software or the object?** The firmware could be sold or given away for hardware people already own. That sidesteps manufacturing entirely and changes the business from hardware to something else.
- **Is Spotify the right anchor at all?** See §3.4. A device that controls whatever is playing may be a bigger market and a smaller legal problem.
- **What is the honest size of this?** Be sceptical. The friction it removes is small, and the buyer must own a £30-plus desk object to remove it. Establish whether that is a business, a side project that pays for itself, or a thing worth building once for oneself and open-sourcing.

---

## 6. What not to do

- **Do not redesign the UI.** It has been through nine revisions with the owner and is settled. Look at it, critique it commercially if you have grounds, but do not restart it.
- **Do not re-plan the build.** `BUILD.md` is current and owned.
- **Do not assume the technical constraints in §4 are solvable.** They were tested. Treat them as fixed unless you find hard evidence otherwise.

---

## 7. What to produce

A written assessment covering: the Spotify licensing position first and plainly, the competitive picture, a pricing and unit-economics view, the UX gaps between a personal build and a sellable product, the main risks, and a clear recommendation on whether to pursue this — including "no, and here is what to do instead" if that is where the evidence points.

The owner values honest, evidence-based analysis over enthusiasm. A well-argued "this should stay a personal project" is a perfectly good answer, and more useful than an optimistic one.
