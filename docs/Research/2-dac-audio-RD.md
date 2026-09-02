# R&D brief — DAC and audio for the 60

**You are being handed one research strand of a hardware product.** You have no other
context; everything you need is here. Cite sources for facts, and separate
findings from recommendations.

## The product, in two paragraphs

The 60 is a desk dial made by Cadrane: a Ø135 × 34 mm round touchscreen puck with
a heavy knurled metal ring around the screen, on a steel base, connected to a
computer by USB-C. It controls system volume and media transport and shows
what is playing. It is positioned as a heavy, expensive watch for the desk — a
limited series aimed at people who buy KEF-LSX-class desk audio, audiophiles,
desk-setup enthusiasts. Everything about it is judged on feel and on measured
quality; anything that would embarrass it under measurement is out.

It carries a **3.5 mm headphone/line output** driven by an onboard DAC. This was
a contested feature and it survived: it is core, it faces away from the user at
the back of the base beside the USB-C, and the jack is what the DAC serves. The
main controller is an Espressif ESP32-P4 (Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C
board, which also carries a small onboard speaker output and two microphones).
The speaker is a notification instrument only — never music. The microphones
stay for dictation.

## What is already decided — do not re-litigate

1. **The audio output must clear measurement scrutiny**, or it is the same mistake
   as a bad speakerphone in a different component. Objective performance (SINAD,
   noise floor, output impedance, crosstalk, jitter) is the bar, not marketing.
2. The jack serves headphones and line-level equally; assume both.
3. No cloud, no phone app, no vendor alignment: the device integrates at the
   operating-system layer (Windows media transport, USB Audio Class), never a
   streaming vendor's interface.
4. USB-C is the only connection and the only power: budget assumes 5 V, and a
   sensible share of 1.5 A at most for everything, of which audio gets a slice.
5. The enclosure is 34 mm tall with the jack barrel inside a 4 mm band; the DAC
   board must be small and sit on the base floor beside the main board — roughly
   a 25 × 25 mm footprint and under 6 mm tall is the space that exists.

## What is asked for

**A. Market and competitors.** What do people who buy this class of object use
for desk audio today, and what do they pay? Survey desktop DAC/amps and DAC-knob
hybrids: iFi Zen DAC, Schiit Modi/Magni stack, Topping E30/L30 and DX-series,
FiiO K-series, JDS Labs Element (a volume-knob-led design — study it closely),
Chord Mojo, Audioengine D1, the Apple USB-C dongle, and any desk controller that
integrates volume + DAC (Loupedeck Live S? Stream Deck+ does not; note what
does). For each: price, DAC chip, measured performance (Audio Science Review
numbers where they exist), headphone output power into 32 Ω and 300 Ω, output
impedance, what reviewers praise and complain about. Then say where a Ø135 dial
at a premium price with a good-but-not-flagship DAC sits in that landscape, and
what measured performance it needs to avoid being the weak point of an
audiophile's desk.

**B. Architecture options for a USB-C desk device.**
- USB Audio Class 2 device on the ESP32-P4 versus a dedicated USB audio bridge
  (XMOS, Comtrue, Savitech, Bravo SA9xxx-class) versus letting the host see a
  separate composite audio function. Which the ESP32-P4 can do natively, at what
  sample rates, and with what jitter/latency — with sources.
- I²S DAC choices in the ~£2–£15 range that measure well: ESS ES9018K2M /
  ES9038Q2M / ES9219, Cirrus CS43131 / CS43198 (integrated headphone amp),
  AKM AK4493 / AK4377, TI PCM5102A / PCM1794, Sabre-class dongle chips. For each:
  measured SINAD, output stage requirements, whether it includes a headphone
  driver, power draw, package, availability, reference designs.
- Headphone amplification: is the DAC's integrated driver enough for 32–300 Ω
  headphones at this price point, or does it need a discrete op-amp stage (TI
  TPA6120, OPA1622, LME49600-class)? Output impedance target, and how to meet
  line-level use from the same jack.
- Power: USB 5 V is noisy and shared with a screen, LEDs, a motor and an ESP32
  with Wi-Fi. What regulation and isolation does a clean output need (LDO trees,
  ferrites, ground topology, separate analogue rail), and what is the realistic
  noise floor achievable in a 34 mm plastic-and-steel box with a motor 20 mm away?
- Volume control: digital in the DAC vs analogue attenuation, and how a
  60-detent physical dial maps onto it (dB per detent, fine steps between
  detents, curve).

**C. Established practice.** What the good desktop designs do that the bad ones
don't: grounding, jack switching and detection, pop suppression on
connect/power, mute-on-unplug, output protection, ESD on the jack, DC blocking.
Reference the JDS, Schiit and Topping teardowns and the ASR measurement
methodology, so the design can be measured the same way.

**D. Recommendation.** One architecture with a parts list (chip, amp, regulators,
jack part number with dimensions), a power budget, the expected measured
numbers, a rough BOM cost at 50 and 500 units, and the measurement rig needed to
prove it (what to buy or borrow: an ADC interface, REW/ARTA, load resistors).
State the risks — the ESP32-P4 USB audio path is the one we least trust — and
how to de-risk each with a small experiment.

## Form of the answer

One document. Findings first with sources, then the recommendation with the
evidence behind each choice and a confidence. Numbers with units. A comparison
table for competitors and one for DAC chips. Anything in "already decided" you
believe is wrong goes in its own section with the evidence — do not silently
design around it.
