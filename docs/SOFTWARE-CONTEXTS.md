# Software contexts for the 60 — integration assessment

**Date:** 2026-09-02 (revised the same day after rulings). **Against:** `docs/DECISIONS.md`, `docs/VISION.md`, `BUILD.md` section 6 (the app shell). **Given:** integrations run in a Windows companion app first, macOS later; the device is a display and a controller; OS-level routes are always preferred over vendor tie-ins; ambition first, dismiss only after thorough investigation. Every API claim was checked against a source today; sources are at the end.

## Rulings recorded today

Calls must service any calling technology, with Teams, Zoom and Meet the three to try hard for. Notifications is Tier 1. Claude Code is Tier 1. Markets (crypto, equities) is Tier 3 and parked — the buyer likely brings their own data licence, and the design must accommodate that. Anything a scroll wheel controls in the focused application should be controllable by the bezel. Vendor-specific effort is reserved for Teams, Zoom, Meet and Claude; Figma and video-editing tools are explicitly not on that list. Granola has a trigger under test by Ryan. The firmware and companion need a name. A spectrum display is wanted.

## Verdict, in short

The OS layer gets much further into Calls than the first draft allowed, because three Windows mechanisms together give a vendor-free picture of *when* a call is ringing and *when* one is live — and that is the part that has to be flawless for the ring/accept/decline moment to feel anticipatory. What the OS cannot do is press the vendor's buttons (accept, decline, end) or mute in a way the vendor's UI agrees with, and those remain per-app work for exactly the three apps you named. The bezel-as-scroll-wheel idea is pure OS layer, works in every application ever written, and should be built before any of the vendor work because it makes the object useful on day one with nothing installed. The spectrum display is free on the DAC path, since the audio literally passes through the device.

The first-draft framing stands: **contexts that surface themselves, a six-entry ring for manual override.**

## Calls — the deep investigation

The state machine has four states — idle, ringing, in call, ended — and per-state controls. Each row says which layer can do it and what is unproven.

### Knowing a call is ringing (OS layer, three signals)

1. **Audio session activity per process.** Windows exposes every application's playback stream through the audio session API (`IAudioSessionManager2` / `IAudioSessionEnumerator`): process ID, state (active / inactive / expired), and a live peak meter. When Teams, Zoom or Chrome starts a stream and its peak level is moving, something is playing from that process. A ringtone from a calling app *before* the microphone is in use is a ring.
2. **Microphone in use, per app.** Windows records every app's microphone access under `HKCU\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone` (packaged apps by name, desktop apps under `NonPackaged` by executable path) with `LastUsedTimeStart` and `LastUsedTimeStop` timestamps. This is what the tray microphone icon reads. Zoom is explicitly shown in the forensic write-ups; Teams and Chrome follow the same path. Mic start for a calling app is the transition ringing → in call; mic stop is ended. Registry change notifications (`RegNotifyChangeKeyValue`) make it event-driven rather than polled.
3. **Communications ducking notifications.** Windows attenuates other audio when a *communications* stream starts, and any application can subscribe to the start and stop of that (`IAudioVolumeDuckNotification`: `OnVolumeDuckNotification` / `OnVolumeUnduckNotification`), even if it opts out of being ducked itself. Teams is known to trigger ducking. **Verify:** whether Zoom and Chrome-hosted Meet open their streams with the communications role; if they do not, signal 2 still covers them.

Together: a known calling app playing audio with no microphone open is **ringing**; the same app with the microphone open is **in call**; microphone released is **ended**. No vendor code, no window reading, works for Webex, Slack huddles, WhatsApp desktop and anything else that rings and opens a mic. This is the Tier-1 promise: the object reacts to every call on the machine. Ringing drives the radial ripple on the screen, the pulsing haptic, and the halo pulse — halo leading the haptic by the 80 ms the light-and-sound decision already specifies. The ping sound and vibration for the notification dot are the same machinery at lower intensity.

Caller identity is a bonus, not a dependency: the notification listener (Tier 1 anyway) catches "X is calling" where the app toasts it; where it does not, the ring screen shows the app's own icon and name, which the OS also gives you.

### Accept and decline (vendor layer, three apps)

There is no OS-level "answer" on Windows for these apps (HID telephony hook-switch would be it, and Teams gates its protocol behind partner NDA, Zoom restricts it to listed brands, Meet accepts generic devices for mute only). So the green and red buttons are per-app:

- **Teams:** the incoming-call window exposes accept and decline through UI Automation (the accessibility tree); keyboard shortcuts also exist (`Ctrl`+`Shift`+`S` accept audio, `Ctrl`+`Shift`+`A` accept video, `Ctrl`+`Shift`+`D` decline). **Verify** whether the shortcuts fire when Teams' call window is not focused; if they do, UI Automation is only needed for reading state.
- **Zoom:** meeting invites and Zoom Phone calls ring in a native window; UI Automation can press its buttons. Zoom's "call control in third-party apps" is Zoom Phone only, admin-enabled, marketplace apps only — not for us.
- **Meet:** meetings are joined, not answered; the only ring is a Google Chat call in a browser tab. Accept is a browser button; a small Chrome extension is the clean route and doubles as the mute-state reader.

Red and green are the reserved colours in the design law: green already means volume and red means mute/recording. **The ring screen is the one place both appear as *buttons* rather than *ownership*, so it needs its own rule** — proposed: while ringing, green and red are the *only* colours on the glass, no bloom, and the halo pulses white. That keeps colour-is-ownership intact everywhere else.

### In call — mute (the hard one; OS route investigated and not dismissed)

Your question: mute the active audio input device at the OS and let the software catch it. Investigated, and the answer is *it works, and Teams punishes it*.

- **Endpoint mute** (`IAudioEndpointVolume::SetMute` on the default communications capture device) genuinely silences you in every app — a physics-level mute, which is what a red halo *should* mean. Teams detects it and treats you as muted, but it also throws a repeating "Your microphone is muted" overlay over the meeting that cannot be turned off — a 400-plus-user complaint still open as of July 2025. Zoom shows nothing, so your tile appears unmuted to others while you are silent, which is the exact confusion that got PowerToys Video Conference Mute deprecated.
- **Per-session capture mute** (`ISimpleAudioVolume` on the app's *capture* session rather than the device) is the interesting variant: silences only that app's microphone stream. **Verify** whether Teams' nag is tied to endpoint mute or to any silence — if Teams does not notice a session-level mute, this is a clean OS mute for everything except the participant-list icon.
- **Vendor mute** (UI Automation pressing the app's own button) is what MuteDeck ships post-API and is the only way the other participants *see* you muted.

Proposed product behaviour, not a compromise but a layering: the bezel press mutes at the vendor layer when a supported app is recognised, and *also* mutes the endpoint as a guarantee; the halo goes red only when the OS confirms the capture path is silent. For an unrecognised app, endpoint mute alone still works and the halo still goes red — the promise "red means nobody can hear you" is kept for any software. The Teams nag is the one thing to solve, and the session-mute test is how.

### In call — volume (OS layer, done)

Per-application render volume (`ISimpleAudioVolume` on the calling app's playback session) gives call volume independent of music; the master endpoint is the fallback. On the DAC path the device sets its own hardware volume. Nothing to verify.

### In call — end (vendor layer)

Teams `Ctrl`+`Shift`+`H`, Zoom `Alt`+`Q` (then confirm), Meet a button; all three via UI Automation when unfocused. Same per-app module as accept/decline. A long press on the bezel ends; the screen asks nothing because the vendor app already confirms where it wants to.

### Camera and hand (vendor, read-only if cheap)

Not requested; UI Automation gives them for free once the per-app module exists. Camera state deserves the halo (a steady white segment at twelve), hand-raised does not.

## The bezel as a scroll wheel — now the default mode (decided 2026-09-02)

> **Superseded in part, 2026-09-07.** The interaction model below still stands, but what the bezel does and how it feels is now set **per application by a profile**, chosen automatically from the focused window. The profile sets the default feel; the feel hotspot described below is a momentary override that snaps back on release, never a second persistent source of the same state. See `docs/SOFTWARE-PROFILES.md`, which also carries the tab and application switcher gesture and the maintenance cost of profiles.

The device enumerates a second HID interface as a mouse with a vertical wheel and a horizontal wheel (AC Pan), in the same composite device as the keyboard it already presents. Whatever has focus scrolls; Windows routes it, no companion required. Sixty magnetic detents at 120 wheel units each is one notch per click; the motor's fine steps emit sub-notch deltas for smooth scrolling, which Windows supports natively. Timeline scrubbing, brush size, spreadsheets, PDFs — all of it with zero vendor work, which is why Figma and Premiere stay off the vendor list.

**This inverts R5** (the standard-build requirement that the dial is volume by default) **for the Halo product.** The reasoning: scrolling is continuous and frequent, volume is rare and urgent; a continuous action cannot afford a mode entry, a rare one can afford a single touch.

### The interaction model as decided

- **Default screen is Scroll.** The glass is a modifier deck around a Now Playing widget: a hotspot for `Ctrl` (zoom), one for `Shift` (pan), and one for *feel* — rest a finger on it and the bezel runs from full detent through to a free flywheel, with scroll speed following. Multi-touch, so two resting fingers is `Ctrl`+`Shift`. The hotspots are rest-to-hold, never toggles: lift the finger and the modifier releases, which is the same rule as a physical key and means nothing can be left stuck.
- **Touch the left zone → Media.** Now Playing fills the glass, the bezel is volume (it will beat an arc-touch on feel; the arc stays as the visual). Tap to return; auto-return after a short delay once you have skipped or adjusted, the same 5 s pattern the CONTROLS overlay already uses. **Not the waggle** — the waggle is the one global gesture and it belongs to dictation; giving it a second meaning reopens a settled thing.
- **Grips the bezel must serve, all effortless, all leaving two fingers free to touch:** thumb on the side, a hand resting alongside, an outstretched finger, a fingertip on the top rim. The flat coin rim and the 34 mm height were chosen for exactly the last two.
- **Left-hand / right-hand mode** mirrors the hotspot layout. Cheap, and it decides which side "the left zone" is.

### What this asks of the hardware (record against DECISIONS.md, do not let it drift)

- **Momentary feel is the motor's job, not the carrier's.** DECISIONS.md item 19 (dynamic detent strength comes from the motor, because it must arrive within about a tenth of a second) and item 20 (the magnet carrier moves only at gesture cadence, a few times an hour) both hold: a finger resting on the feel hotspot drives the *motor* to cancel or reinforce the magnets in real time; the carrier is for mode changes that persist. Consequence: **the motor must be able to fully cancel the unpowered detent while the ring is spinning at scroll speed, continuously, within the USB power budget** the halo is already capped for. That is bench-rig question A ("what is light enough for the motor to overpower cleanly, and still satisfying with the power off") restated as a hard requirement, and it argues for designing the magnets at the *bottom* of the 60–150 mNm band rather than the top.
- **Touch while spinning.** The touch controller must report a resting finger reliably while the ring moves under the other fingers, and must reject a palm resting alongside. **Verify:** which controller the 3.4C uses and its multi-touch count (GT911-class parts do five points); palm rejection is firmware, and the resting-hand grip is the test case.
- **The HID composite.** Keyboard (chords, modifiers), mouse (two wheels, no buttons, no pointer), and later a telephony page for Meet — one device, three interfaces. The rule that no human-typed string ever becomes a keystroke is unaffected: modifiers are fixed usages.

### Why this is a level above a mouse wheel, stated plainly

A mouse wheel has one axis, one feel, and its modifiers live on another device. This has one axis whose *feel* is a live control, whose modifiers are under the same hand, and whose mass and radius make a free spin last. Windows still just sees a wheel — the whole difference is inside the object, which is the correct place for it.

## Spectrum display

Two meanings, both cheap, and worth deciding which is wanted:

- **Spectrum analyser (visualiser).** On the DAC path the PCM stream passes through the device, so a 32-band FFT runs on the ESP32-P4 with nothing on the PC. Without the DAC, the companion captures the PC's output with WASAPI loopback and streams bins over USB. Rendered as the phyllotaxis bloom breathing to the music it is on-brand; rendered as bars it is a 1990s hi-fi.
- **Equaliser (adjusting bands).** On the DAC path a parametric EQ is a few biquad filters on the device, the bezel sweeps the band and the ring shows the curve. This is the "your DAC is the knob" pitch with a second verb. Bench it after the DAC spike; measurement-crowd caveat from the vision doc applies.

## Every candidate, one row each

"Layer" is where the integration lives. **OS** = something Windows exposes to any program. **Standard** = a published cross-vendor protocol. **Vendor** = a specific company's API or interface, which they can change or withdraw.

| Context | Layer | Read | Write | What breaks | Tier |
|---|---|---|---|---|---|
| **Now Playing** | OS — Windows media session | title, artist, art, position, state, for any player | transport, seek | Nothing new | **1** |
| **Volume / DAC** | OS + hardware | system, per-app, DAC volume | set | Nothing | **1** |
| **Calls** — ring / in-call detection | OS — audio sessions, mic-use registry, ducking notifications | ringing, live, ended, which app | — | Ducking role per app (verify) | **1** |
| **Calls** — accept / decline / end / visible mute | Vendor — UI Automation per app (Teams, Zoom), Chrome extension (Meet) | mute, camera, hand | accept, decline, end, mute | Vendor UI redesigns; UI language | **1** |
| **Calls** — guaranteed mute | OS — capture endpoint or session mute | silent or not | mute | Teams nag on endpoint mute (verify session variant) | **1** |
| **Notifications** | OS — `UserNotificationListener` | app, title, body, time, for every toast | dismiss | Needs MSIX packaging and one consent; toasts only | **1** |
| **Claude Code** | Local hooks (`PermissionRequest`, `Notification`, `Stop`, session events); a hook can *answer* a permission request | waiting / working / done; what it asks | approve or deny with a press | Claude Code only; the desktop app has no hooks | **1** |
| **Bezel as wheel** | Standard — HID mouse wheel | — | scroll, zoom, pan in the focused app | Nothing | **1** |
| **Dictation** (Wispr Flow) | Standard — HID chord | believed state only | toggle | Drift, already designed for | **1** |
| **Launcher** | Standard — HID chord | — | launch / focus | Nothing | **1** |
| **Timer** | none | — | — | Nothing | **1** — sixty detents, sixty minutes, works unplugged |
| **Spectrum** | hardware (DAC path) or OS (loopback capture) | audio | EQ bands (DAC path) | Nothing | **2** |
| **Calendar / next meeting** | Vendor — Microsoft Graph delegated `Calendars.Read`; Google Calendar API | next event, minutes to go | join | Tenant admin consent; Google app verification | **2** — pairs with Calls: halo pre-warms |
| **World clock** | none | — | — | Nothing | **2** |
| **Slack** | Vendor — Web API user token; mentions via toasts | mention badge (toasts, no API); status, DND (API) | status, snooze | Admin approval; OAuth redirect must be HTTPS, likely a hosted page | **2 badge / 3 status** |
| **Granola** | Vendor — read-only API (Business/Enterprise); trigger under test | notes ready | start (Ryan's hack) | No recording state readable | **3**, folded into Calls |
| **Focus** | Graph presence, Slack DND; Windows has no public Focus Assist API | state | set | Windows itself cannot be told | **3** |
| **Markets** | Standard (crypto public feeds) / Vendor licence (equities) | prices | — | Real-time equities is a licence | **3 — parked; bring-your-own-licence** |

## The software is TorqueOS (decided 2026-09-02)

The firmware and its companion are **TorqueOS**, one word. Torque is what the mechanism does — detent torque, motor torque, the units the bench rig measures in — and it reads as a car specification to the buyer, which is the right register. The companion app is "TorqueOS for Windows" and later "TorqueOS for Mac".

Vocabulary that goes with it, from the words considered along the way: the ring is the *bezel* in every screen and document; the free-flywheel scroll mode is *freespin*; the machined finish is *billet* aluminium. None of those is a product name.

Known collisions, none of them a hardware or consumer brand: Torque3D (a game engine), Torque Pro (a car-diagnostics phone app), Magtrol's TORQUE test-bench software. torqueos.com and torqueos.io are both registered, so the software lives at cadrane.com. Names rejected on the way and why: Calibre (an e-book application in the same class, and "Calibre 60" reads as a gun), Escapement, Momentum OS (at least three live products use it), Radial OS (the Radial Engineering marks that ended Radial as a product name), Spin OS (an unownable common verb; domains taken), Bezel (a luxury-watch marketplace with the same buyer).

**Still to do before anything is printed:** a trademark search for TorqueOS in class 9 (software) in the UK, EU and US. A domain check is not that.

## What this does to the ring

Contexts that surface themselves and never need a ring slot: Calls (ringing, in call), Now Playing, Claude waiting, Timer running, Next meeting at two minutes.

Scroll is home, not a ring entry, and Media is one touch from it. Ring, owner-curated, six maximum, default order: Timer, Launcher, Dictation, Spectrum, Markets, Settings. The launcher cap's argument — fixed positions the hand learns — applies unchanged.

## Verify before committing (each is an afternoon, in this order)

1. **Session-level capture mute vs Teams' nag.** Mute Teams' capture session with `ISimpleAudioVolume`; see whether the "your microphone is muted" overlay appears and whether other participants see a mute icon. Decides the whole mute layering.
2. **Ducking role per app.** Subscribe to duck notifications; start a Teams call, a Zoom call, a Meet call in Chrome. Note which fire. Signal 2 (mic registry) is the fallback either way.
3. **Mic-use registry latency.** Time from clicking Accept to `LastUsedTimeStart` changing. It must be under ~300 ms for the screen transition to feel causal.
4. **Teams accept/decline shortcuts unfocused.** If they work, the Teams module is half the size.
5. **UI Automation exposure of the new Teams mute button state** across two Teams updates, in English.
6a. **Touch controller under a spinning ring** — multi-touch count, resting-finger stability, palm rejection with a hand alongside.
6b. **Motor cancelling the detent continuously at scroll speed** on the bench rig, with current measured against the USB budget.
6. **HID wheel with sub-notch deltas** — confirm Windows treats a `Resolution Multiplier` wheel from our descriptor as smooth scroll in Chrome, Explorer and Excel.
7. **Meet WebHID mute LED feedback** to a generic device — hobbyist builds report Meet accepts the device; LED sync undocumented.
8. **MSIX-packaged tray app** holding the notification-listener capability, unelevated.

## Decided items this touches

- Item 8, "never the layer a vendor owns": Calls detection is now OS; accept/decline/end/visible-mute are vendor and limited to the three named apps plus Claude Code. Proposed reading recorded: the rule forbids depending on a vendor for a Tier-1 *promise*; the promise here ("reacts to every call, red means silent") is kept at the OS layer, and the vendor layer adds convenience on top.
- Item 6, "no cloud, ever": Slack's OAuth redirect must be HTTPS, which likely means a page we host. Slack status/DND is the only feature on this list that touches it; the mention badge from toasts does not. Decide when Slack reaches the top of Tier 2.
- Item 2, who the buyer is: still two buyers in the brief (Wall Street on Windows and Teams; the founder on Mac, Meet and Claude Code). Windows-first serves the first. Unchanged from the first draft and still needs a written answer.

## Sources

Windows call-state signals: [Microsoft Learn — audio session enumeration (`audiopolicy.h`)](https://learn.microsoft.com/en-us/windows/win32/api/audiopolicy) · [Microsoft Learn — ducking notifications, `OnVolumeDuckNotification`](https://learn.microsoft.com/en-us/windows/win32/api/audiopolicy/nf-audiopolicy-iaudiovolumeducknotification-onvolumeducknotification) · [Microsoft Learn — the ducking experience and opting out](https://learn.microsoft.com/en-us/windows/win32/coreaudio/disabling-the-ducking-experience) · [svch0st — tracking processes accessing camera and microphone (CapabilityAccessManager registry, Zoom shown)](https://svch0st.medium.com/can-you-track-processes-accessing-the-camera-and-microphone-7e6885b37072) · [Velociraptor — CapabilityAccessManager artifact](https://docs.velociraptor.app/exchange/artifacts/pages/windows.registry.capabilityaccessmanager/) · [Microsoft Q&A — Teams "your microphone is muted" overlay on device-level mute](https://learn.microsoft.com/en-us/answers/questions/4428298/how-do-i-prevent-the-your-microphone-is-muted-mess)
Teams API retirement and routes: [Windows Forum — Teams Stream Deck controls end after 30 June API retirement](https://windowsforum.com/windows-news.4/teams-stream-deck-controls-end-after-june-30-api-retirement.442758/) · [HANDS ON Teams — shortcuts after the deprecation](https://teams.handsontek.net/2025/11/28/keep-using-elgato-stream-deck-microsoft-teams-api-deprecation/) · [Microsoft Q&A — new Teams and Win+Alt+K](https://learn.microsoft.com/en-us/answers/questions/4440107/new-teams-does-not-recognise-the-global-mute-win-a) · [Microsoft Q&A — USB HID control of Teams needs the partner-only protocol](https://learn.microsoft.com/en-us/answers/questions/1376779/how-to-use-usb-hid-to-control-teams) · [Microsoft Q&A — HID mute usages, telephony page recommended](https://learn.microsoft.com/en-us/answers/questions/5860057/windows-support-for-usb-hid-hutrr110-(system-micro)
Teams shortcuts: [Microsoft Support — keyboard shortcuts for Teams (accept audio Ctrl+Shift+S, accept video Ctrl+Shift+A, decline Ctrl+Shift+D, end Ctrl+Shift+H)](https://support.microsoft.com/en-us/accessibility/teams/keyboard-shortcuts-for-microsoft-teams)
Interface discovery: [MuteDeck — Teams guide](https://mutedeck.com/guides/stream-deck/microsoft-teams) · [MuteDeck — global mute options on Windows, PowerToys deprecation](https://mutedeck.com/fix/windows-global-mute-key) · [MuteDeck — shortcuts per app](https://mutedeck.com/blog/2026-02-02-keyboard-mute-button/) · [MuteMe — after the Teams API](https://muteme.com/blogs/news/dont-panic-a-solution-is-coming-for-our-teams-users)
Zoom and Meet: [Zoom — supported USB HID devices](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0064819) · [Zoom — call control in third-party apps (Zoom Phone only)](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0070147) · [Google Meet — call controls](https://support.google.com/meet/answer/12562325?hl=en) · [Homemade USB mute button on Meet](https://gergely.imreh.net/blog/2023/08/making-a-usb-mute-button-for-online-meetings/)
Notifications: [Microsoft Learn — notification listener](https://learn.microsoft.com/en-us/windows/apps/develop/notifications/app-notifications/notification-listener)
Claude Code: [Hooks guide](https://code.claude.com/docs/en/hooks-guide)
Granola: [Granola API docs](https://docs.granola.ai/introduction)
Slack: [Slack — app approval](https://slack.com/help/articles/222386767-Manage-app-approval-for-your-workspace) · [Slack OAuth — "the redirect_uri must use HTTPS"](https://docs.slack.dev/authentication/installing-with-oauth/)
Market data (parked): [Polygon.io tiers](https://tradingtoolshub.com/review/polygon-io/) · [Coinbase websocket limits](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-rate-limits)
