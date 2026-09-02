# R&D brief — UI, light, display and sound design for the 60

**You are being handed one research strand of a hardware product.** You have no other
context; everything you need is here. The outcome is a *design system* in which
the screen, the ring of light, the sound and the click of the knob are one
language, and in which the product's brand and its in-use experience are the same
system, not two. Bring evidence: link references, frame-grab them, and say *why*
each works before saying what to take from it.

## The product

The 60, by Cadrane, is a desk dial: a Ø135 mm round touchscreen puck, 34 mm
tall, with a heavy knurled metal ring — the knob — around the screen, on a steel
base. The knob is three quarters of the visible side; below it you see only the
edge of the steel plate and a thin ring of light that fires down onto the desk.
The knob turns on wheels and clicks through **sixty magnetic detents** that work
with the power off; a motor changes the detent strength and adds end-stops and
dynamic feel on top. It controls a computer's audio over USB-C and carries its
own DAC with a headphone socket. Category line: "a haptic desk dial". It is a
heavy, expensive watch for the desk that invites idle handling. Limited series;
the customer buys KEF-LSX-class desk audio.

The four output channels you are designing for, with their real limits:

- **Screen.** 3.4-inch round IPS, 800 × 800, capacitive touch, under glass, framed
  by the metal ring's inner chamfer so the picture sits in a machined porthole.
  Viewed from about 60 cm, from above at roughly 40–50°, never head-on. Driven by
  an ESP32-P4 (dual-core RISC-V at 400 MHz, 32 MB PSRAM, a 2D pixel-processing
  block, **no 3D GPU**). Line drawing, sprites, alpha blends and scaled bitmaps
  are cheap; full-screen blur, glow and per-pixel shaders are not. Assume LVGL or
  a hand-written 2D renderer at 30–60 fps.
- **Halo.** Individually addressable RGB LEDs on a ring under the knob at about
  4 mm pitch, behind a translucent diffuser that leans outward and fires *down*
  onto the desk. The ring covers 324°; a 36° opaque segment at the back (12
  o'clock, facing away from the user) carries the sockets. So the halo is a
  horseshoe, open away from the user, and its light is seen mostly as a glow on
  the desk surface rather than as a bright ring.
- **Sound.** A small full-range driver under the base, firing down through a
  Ø34 mm aperture, for UI sound only (clicks, confirmations, the timer's end).
  Music goes to the DAC and headphones or the computer, never through this
  driver. Expect a driver that does little below ~400 Hz.
- **Haptics.** Sixty magnetic detents (a firm, evenly spaced click every 6°),
  plus a motor that can make the detents lighter or heavier, add end-stops, and
  in principle pattern the feel (a soft region, a hard wall, a ratchet). Knob
  position is read continuously at sub-detent resolution, so the screen can
  follow the knob *between* clicks, not just at them.

## What the software already does — treat as given

- Menus are **rings**: items arranged around the circumference, turned by the
  knob, with a single **green selection dot at twelve o'clock**. Colour comes
  only from light (screen and halo); the metal is monochrome black with one
  bright diamond-cut aluminium chamfer.
- **Contexts surface themselves.** The companion app on the computer decides
  what the dial is showing: a call starts and the Calls context takes the
  screen (mute button, halo breathing green); music plays and Now Playing takes
  it back; an AI coding agent asks for permission and the halo glows amber
  until the knob is pressed; a timer runs and the screen fills. The ring menu
  is the manual override and holds at most six owner-chosen entries: Now
  Playing, Timer, Markets, Launcher, Dictation, Settings.
- **The timer is the signature screen.** Sixty detents, sixty minutes: turn the
  knob like a dive bezel to twenty-five, a "phyllotaxis bloom" fills to
  twenty-five, the halo shows the same arc on the desk, and when it lands the
  speaker gives a kerchunk. This is the screen a watch collector will be shown.
- No logo on the face. No visible screws. Brand appears through behaviour,
  typography, light and sound, and on the underside, box and companion app.

## What is already decided — do not re-open

Round screen, ring menus, the green dot at twelve, light-only colour on a
monochrome object, halo as a downward glow with a gap at the back, sixty
detents, contexts that surface themselves, the six-entry ring cap, the timer as
the hero. Your job is to make these decisions *sing together*, not to replace
them.

## What is asked for

**A. The reference survey — what to steal and what to refuse.** Go through the
following and for each write two lines: what it does that a real product could
use, and what it does that only works on camera. *Film and television:* Jarvis
and the Iron Man HUDs (Perception, Cantina Creative — the radial menus, the
wireframe scans), Minority Report, Oblivion (GMUNK), Blade Runner 2049 and
Ex Machina (Territory Studio), Tron: Legacy, Prometheus, The Expanse, the
Westworld tablets, Mark Coleran's and Ash Thorp's FUI work. *Games:* Dead
Space's diegetic health bar, Destiny's cursor and radial menus, Elite
Dangerous and No Man's Sky ship HUDs, Gran Turismo 7 and Forza Horizon menus,
Cyberpunk 2077, Persona 5's motion, Nintendo's Switch system sounds, the PS5
UI. *Apple:* the Digital Crown's on-screen sync on Apple Watch, the iPod click
wheel and its clicker sound, watchOS complications, the Dynamic Island,
visionOS depth and glass, HomePod's top-surface light, the Apple Watch Ultra's
Wayfinder and Modular Ultra faces, the Jony Ive era of "the interface is the
object" and LoveFrom's typographic restraint. *Automotive:* the McLaren
instrument display (the folding cluster in the 720S, the Artura's binnacle),
Porsche's five-dial cluster and the Taycan's curved display, the 911's centre
tachometer as a brand asset, Porsche Design's watches and headphones, Rimac,
Pagani's exposed mechanism, the Mercedes Hyperscreen (as a warning),
bookofshapes.com and the "book of shapes" idea that a brand owns a family of
curves. *Hardware with a light ring:* Nest Thermostat (the original), Echo,
HomePod, Sonos Era, Teenage Engineering OP-1 and OB-4, Nothing's Glyph, Dyson,
the Playdate crank, Braun's Dieter Rams dials.

**B. Motion: synchronised radial elements and the detent.** Propose the motion
grammar. Sixty detents means every rotation is quantised: what happens on
screen *during* the 6° between clicks (does the ring menu slide continuously, or
does it snap?), what happens at the click (the item lands, the dot pulses, the
halo ticks, the speaker clicks — in what order and with what offsets in
milliseconds?), and how the four channels stay in lock when the knob is spun
fast (at 5 turns/second that is 300 clicks/second: the screen cannot draw 300
frames, the speaker cannot play 300 clicks — what does each channel do when it
falls behind?). Give recommended easing curves, durations tied to the detent
period, and a rule for how much on-screen motion is allowed to originate from
the device on its own rather than from the hand. Include micro-animations for:
boot/splash, wake from idle, a context arriving (call starts), a context
leaving, press, long-press, end-stop reached, timer landing, volume limit, USB
connect/disconnect, a low-priority notification, and error. Storyboard each in
a frame strip; specify each as time (ms), easing, and which channels fire.

**C. Depth on a flat round screen.** The screen is a porthole in machined
metal, viewed from above at an angle. Investigate what reads as depth without a
GPU and without head tracking: the Chinese naked-eye 3D billboards (Chengdu
Taikoo Li, Seoul's SM Town "Wave") and *why* they work only from one viewpoint
and whether a desk object has a "one viewpoint" too; the infinity-mirror /
"4D cube" effect and whether a rendered equivalent (concentric rings receding
into the centre, a lit rim) is worth the pixels; 3D wireframe models (the
Jarvis scan, Elite's ship silhouettes, the Apple Watch's globe) rendered as
lines — how many edges the P4 can draw at 60 fps and whether a wireframe of
*the dial itself* is a meaningful boot or settings image; parallax from the
knob (the world rotates with the ring), and the trick of making the on-screen
ring appear to be the *same object* as the metal ring around it. Give a
recommendation and a cost estimate in draw operations per frame.

**D. Light: the halo as a language.** Define the halo's vocabulary: breathing
(rate, depth, colour) for waiting; a solid arc for progress (the timer, the
volume); a tick that travels with the knob; a wall flash at an end-stop; an
amber hold for "needs you"; red for "recording"; white for "just showing you
where I am". Say what a downward-firing horseshoe with a gap at the back can
and cannot express, how it reads on light and dark desks, how to avoid a
sixty-dot look at 4 mm pitch, what brightness in the room vs at night, and how
the halo should relate to the screen's own colour (same hue, offset hue,
never both animating). Reference how Nest, HomePod, Echo, Sonos, Nothing and
Teenage Engineering resolve the same questions, and what has been written about
ambient light as notification (calm technology, Weiser and Brown; the Ambient
Orb; the Philips Ambilight research).

**E. Sound.** A palette for a small down-firing driver: the click, the
kerchunk, the confirm, the deny, the timer's end, connect and disconnect, the
"needs you" chime. Reference the iPod click wheel, Nintendo's Switch, the Leica
shutter, mechanical watch sounds, Teenage Engineering's OP-1 and Pocket
Operators, Braun clocks, Porsche's and McLaren's start-up chimes, Sonos's and
Apple's connect sounds, the Mac's startup chime and why it is loved, and the
literature on earcons and auditory icons (Blattner, Gaver, Brewster). Rules for
loudness relative to the mechanical click of the detent itself (the magnets
already make a sound — does the speaker double it, or stay out of the way?),
for silence by default, and for what must never make a sound (the ring
turning idly). Give a spectral guide for a driver that does little below
400 Hz and a list of sounds to prototype, each with duration, pitch envelope
and the moment it should land relative to the haptic click.

**F. Typography, iconography and the grid for a round 800 × 800 screen.** A
type recommendation (one family, tabular figures, legible at 60 cm from above,
licensable for embedded use — check the licence), a radial grid (safe area
inside the chamfer's shadow, the ring-menu radius, the dot at twelve, text on a
curve or not), icon language (line weight that matches the type, sixty-degree
and thirty-degree symmetry where it helps), and numerals for the timer and
volume that read at a glance. Reference watch dials (Nomos, Grand Seiko,
Porsche Design, Sinn), instrument clusters, and the Apple Watch's circular
layout guidance.

**G. One system: brand = product.** Write the spine of a design system in
which brand and experience are the same set of tokens: colour (the green, the
amber, the red, the white, black), motion (curves and durations derived from
the 6° detent), light (halo states), sound (the palette), haptic (detent
weight profiles named as brand words), type, the family of curves (the
chamfer, the ring, the dot) that recur on the object, the screen, the box,
the website and the companion app. Propose the naming (what the states and
sounds are called internally, so engineers and designers use the same words),
a state table (state → screen / halo / sound / detent, one row per state), and
the rules a companion-app screen on Windows or macOS must follow to be
recognisably the same brand as the dial without imitating a round screen.
Show how the boot splash, the box, the website hero and the settings screen
share the same three or four shapes. Cite design systems that do this well
across hardware and software (Apple HIG, Teenage Engineering, Braun/Rams,
Nothing, Porsche's brand system, Leica, Bang & Olufsen, Polestar, Rivian).

## Things to be sceptical about, on purpose

Sci-fi and game UI is designed to be *read by an audience* in two seconds and
then ignored; a desk object is looked at ten thousand times by one person who
must never be annoyed by it. Anamorphic 3D needs a single fixed eye. The
ESP32-P4 has no shader pipeline. A light ring in an office competes with
daylight. An idle animation that draws the eye is a bug on a desk. Say clearly
where a reference is spectacle and where it is usable, and prefer restraint
that can be *felt* in the hand over motion that must be watched.

## Form of the answer

One document with images and frame-grabs linked. Findings by section, each
ending with two or three concrete recommendations for the 60 with numbers
(durations in ms, easing curves, LED counts, colour values, font sizes in px at
800 × 800, sound durations and pitches). A separate one-page **state table**
(state → screen / halo / sound / detent) and a separate one-page **token list**
that could be pasted into a code repository and a brand guideline unchanged. A
short list of things you think we have got wrong, with the evidence, kept
separate from the rest. Finally, a prototype plan: which five animations and
five sounds to build first on the real hardware to test the grammar.
