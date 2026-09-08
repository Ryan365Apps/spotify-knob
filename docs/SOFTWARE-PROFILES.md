# Application profiles and dial feel — the 60

**Date:** 2026-09-07. **Status:** current requirements, edited in place — this is not a history. **Applies to:** the halo product (the 60) and its companion application, TorqueOS for Windows. **Reads with:** `docs/SOFTWARE-CONTEXTS.md` (which integration lives at which layer), `docs/SOFTWARE-INTERACTION-CORE.md` (the ring, timings, haptic vocabulary and colour law that this document does not restate), `docs/DECISIONS.md` (the decision index), `docs/SOFTWARE-HID-CONTRACT.md` (the rule that no human-typed string becomes a keystroke).

**Where this came from:** CNCDan's macropad video of 2025 (a six-key pad with a gimbal-motor haptic wheel, which itself credits Scott Bezek's SmartKnob project). Two ideas from it were taken: per-application profiles, and having a small set of named scroll modes rather than one behaviour. Everything below is the version for this product, not his.

---

## 1. What a profile is

A profile is the answer to one question: **when this application has focus, what does the bezel do and how does it feel?**

A profile holds four things:

1. **A default mode** — what the bezel does when no modifier is held.
2. **A modifier map** — what the bezel does while each screen hotspot is held.
3. **A feel setting for each of those** — detent count, detent strength, damping, whether the ends stop hard.
4. **A screen and halo state** — what the glass shows so the user can see what the bezel is currently doing.

Item 4 is not decoration. The bezel is one physical control that means different things in different applications, and there is no other way to know which. The screen is what makes a profile legible; without it a profile is a hidden mode, which is the failure case of every mode ever shipped.

## 2. What a profile is not

A profile is **not a macro definition**, and the profile editor is **not a macro editor**. The current position stands: the product does not sell keyboard macros, and the configuration model the user sees is never "which keystroke does this send".

That is a statement about the **configuration model**, not about the **transport**. A profile expresses intent — "next tab", "scrub forward", "raise the call volume". How the companion application delivers that intent is an implementation detail that may well be a keystroke where nothing better exists, and the user never sees it. Keeping those two apart is what lets the product cover a dozen applications cheaply without becoming a macro pad.

This separation also means an intent can be re-implemented later — keystroke first, a real integration afterwards — with no change to the profile the user configured.

## 3. How a profile is chosen

**Automatically, from the focused window. There is no profile picker.** The companion application already watches the foreground window; the profile follows it. The user never selects a profile in normal use — selecting one by hand is the weak version of this feature and is not built.

Two rules make that safe:

- **Unknown windows hold the current profile.** When focus lands on something with no profile, keep the one already loaded rather than dropping to the default. This is what handles windows that take focus for a moment and hand it back — elevation prompts, splash screens, installers, some notification popups. It is a one-line rule and it removes the need for any timing hack.
- **A profile change never takes effect while a finger is on the bezel.** If the profile switches mid-gesture, queue it and apply it when the bezel is at rest. A detent scale that changes under a moving hand reads as a fault, not a feature. This is the strictest rule in this document.

## 4. Where a profile is configured

Two surfaces, and the split matters.

**On the device — feel.** Detent count, detent strength, damping, spring rate. These have no correct value on paper; they can only be judged by turning the bezel while the application is in front of you. So they are adjusted on the glass, live, in context. This is also the demonstration that sells the object.

**In the companion application — everything else.** Which intent each mode drives, what the screen shows, icons and labels, the modifier map, which applications have profiles at all. This is authoring work across a dozen applications, and building it as a settings tree on a round screen would cost a great deal and take the glass away from the job it is good at.

## 5. The feel parameter set

Feel is data, not code. The parameter set is taken from SmartKnob, which is proven, and named in plain English here:

| Parameter | What it means |
|---|---|
| **Positions** | How many detents make up the range. Sixty for volume; nine for a nine-tab list; none for a timeline. |
| **Lowest and highest position** | The ends of the range, where the range is bounded. Absent for an unbounded control such as page scrolling. |
| **Detent width** | The angle occupied by one position. |
| **Detent strength** | How firmly the bezel is held in a position, from a free flywheel through to a hard click. |
| **End stop strength** | How hard the wall is at the lowest and highest position. |
| **Snap point** | How far past a detent the bezel must travel before the position actually changes. |

Six numbers, and they describe every mode below plus the bounded lists in section 6 — which the three named modes on their own cannot express.

## 6. Modes are presets over that parameter set

The user chooses a **mode** by name. The firmware stores a **parameter set**. Modes are presets, so a profile can sit between them where a use case needs it.

The named modes:

- **Detent scroll** — a click per line or item. Sixty positions, unbounded.
- **Free spin** — no detents; the bezel's own mass carries it. Note the difference from the video's version: that wheel is light and its motor is driven to fake momentum, whereas this bezel has real flywheel mass. Where the motor is needed here it is to **brake**, not to drive.
- **Centre spring** — the rate control. Deflect the bezel and the thing scrolls faster the further it is held from where it was grabbed; release and it returns. The return is always to **where the finger landed**, never to an absolute home — a continuous bezel has no home position.
- **Bounded list** — a fixed number of detents with hard walls at both ends. This is the mode the video does not have, and it is the one the switchers in section 7 need.

**Centre spring has an open engineering question before it is a feature.** A restoring torque has to fight the rotating mass of a roughly Ø150 bezel, and on release it will oscillate unless it is damped. The motor can damp it under closed-loop control, but that is continuous current in an object whose thermal budget is already the binding constraint (`docs/THERMAL-PLAN.md`, `docs/HALO-BRIGHTNESS.md`). **Bench test on the Raspberry Pi rig:** holding torque required at full deflection, and settling behaviour on release. If it cannot be held without the object warming, scope the mode to short bursts — which is all scrubbing ever is — rather than dropping it.

## 7. The switchers — the gold-standard interaction

This is the interaction the object is judged on:

> Rest a finger on a hotspot. Spin the bezel — it detents through the list, one detent per item. Land on the one you want. Lift the finger, and you are immediately scrolling that page.

Two switchers, on two different hotspots:

- **Tab switcher** — the tabs of the focused browser window.
- **Application switcher** — the open windows on the machine, the equivalent of Alt+Tab.

The hotspots are rest-to-hold, never toggles, exactly as the modifier hotspots already are.

### 7.1 The list must be positional and stable, not most-recently-used

**This is the decision that makes or breaks the gesture.** Windows orders the Alt+Tab list by most recently used, so it reshuffles after every switch. That is right for a two-item flip — tap to go back to the last application — and wrong for spinning to a target, because three detents means a different application every time and no muscle memory can form. Chrome's Ctrl+Tab is positional (the next tab rightwards); Firefox offers a preference to make it recently-used instead.

**Both switchers use a stable positional order.** Tabs in tab-bar order. Windows in a stable order such as taskbar order or an order the user pins.

Consequence: **do not send Alt+Tab.** The companion application enumerates windows and activates the one the bezel lands on. Known friction to design for: Windows restricts a background process from pulling a window to the foreground, so the activation has to be done by a process that is allowed to, and that is a solved but non-trivial piece of work.

### 7.2 The cost is inverted from what it looks like

The application switcher is the **cheaper** of the two. Enumerating and activating windows is a native Windows facility the companion application needs anyway. A browser's tab list needs an extension or the accessibility layer, per browser.

More generally: watching the focused window tells you **which** application has focus and nothing else, ever. Any behaviour whose detents align to a list — tabs, channels, open files — needs that application's **state**, which means a real integration. That line, not the number of applications, is what the maintenance cost tracks. See section 9.

### 7.3 Commit model, and it differs per switcher

- **Tabs: commit live.** Each detent actually switches the tab as it is passed. This is what Ctrl+Tab does and it feels direct. Cost is that reaching the eighth tab fires eight real tab activations.
- **Applications: commit on release.** The screen shows the list and the highlight moves; the window is activated only when the finger lifts. Activating each window in passing would be visually violent, which is why Alt+Tab works this way.

Deferred commit has a small ordering problem with "lift and you are scrolling": the target window needs focus before wheel events go anywhere useful. Sequence the activation and the scroll handover explicitly rather than discovering the race later.

### 7.4 Freeze the list when the hotspot is touched

Tabs open and close on their own, and a page can spawn one mid-gesture. The list, and therefore the detent count, is captured at the moment the hotspot is touched and does not re-derive until the finger lifts. This is the same rule as section 3's "never mid-gesture", applied to the list rather than the profile.

### 7.5 Hard ends, no wrap

`docs/SOFTWARE-INTERACTION-CORE.md` says rings wrap and clamped values bump. **A switcher is a clamped value, not a ring** — it stops hard at the first and last item, with the firm haptic and the visual kick that document already specifies.

The reason is positional: being able to slam to the end and count back two is an anchor the user can use without looking. Wrapping destroys it.

### 7.6 The weak link is finding the hotspot, not the spin

Everything else in this gesture is muscle memory. Two hotspots on flat glass have no tactile landmark, so acquiring them is the one visual step in an otherwise blind interaction — and if the user has to look down to arm the gesture, the whole thing is slower than Ctrl+Tab and the feature is dead.

Requirements that follow:

- The two hotspots sit far apart, at fixed clock positions that never move between profiles.
- They are generously sized — large enough to hit blind, not sized to a fingertip.
- Arming is confirmed instantly, and confirmed **where the eye already is**: the halo and the centre of the glass, not the hotspot itself.

### 7.7 Build this first

This gesture does not need the profile system to exist. Hardcode the browser case on the Raspberry Pi rig and find out whether the lift-and-scroll transition feels as good as it reads. It is the clearest answer to "why is this better than a scroll wheel", so it is both the first thing to prove and the demonstration.

## 8. Worked examples

| Application | Default | Held hotspot A | Held hotspot B |
|---|---|---|---|
| **Browser** | free scroll, unbounded | tab switcher — bounded list, detents = tab count, hard ends, live commit | application switcher |
| **Slack** | free scroll of the message list | channel list — bounded list | application switcher |
| **Code editor** | free scroll | open files — bounded list | application switcher |
| **Timeline editor** | centre spring scrub, no detents | — | application switcher |
| **Anything with no profile** | free scroll, plus volume and media transport | — | application switcher |

The application switcher is on the same hotspot in every profile, because it is about the machine rather than the application.

## 9. What this costs to run

Three tiers. Cost tracks the tier, not the number of applications.

1. **Deep integration** — Teams, Zoom, Meet, Claude Code, Spotify, and anything needing live list state such as browser tabs. Expensive to build, expensive to keep working, and it breaks on somebody else's release schedule. Keep this list as short as it can be defended.
2. **Intent-over-keystroke profiles** — most applications. Roughly a day each including feel tuning and icons, and close to no maintenance, because keyboard shortcuts are stable across application versions in a way that user interfaces are not. This tier is what makes a dozen applications tractable for one person.
3. **The generic default** — one profile that works in anything: scroll, volume, media transport.

**The recurring cost is distribution, not authoring.** Sixty devices in the field need a way to receive updated profile packs, signed, for years. That is a fixed cost paid once and then carried, and it is the line item worth pricing properly — another dozen tier-2 profiles is a rounding error beside it.

**Tailoring is capped at one session.** The 60-unit run supports a white-glove setup, and live feel tuning on the device is exactly what that session is for. What does not scale is sixty bespoke configurations maintained individually — that is sixty products, not a service. After the setup session, everything arrives as a pack every owner gets.

There is no plugin community and none is planned. Sixty owners and a direct line to them is a better feedback loop than a plugin marketplace, and it is the one advantage over a mass-market macro deck that cannot be copied.

## 10. Open questions

1. **Profile per application, or per context within an application?** A timeline editor's timeline and its media browser want different detent counts. Watching the window gets the first; the second needs per-application integration. This decides the tier mix and therefore the cost.
2. **Centre spring on this mass** — the bench measurement in section 6.
3. **The stable order for the application switcher** — taskbar order, or an order the user pins, and what happens when a window opens or closes between gestures.
4. **Whether tab switching earns a browser extension**, given section 7.2 says it is the expensive half of the gold-standard gesture.
