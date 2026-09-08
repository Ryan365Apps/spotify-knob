"""candidate layouts for the study"""
import sys
from layout_tool import *

PICO, ZERO, BOB, DRV, LS = ("Pico 2 (51x21)", 51, 21), ("ESP32-S3-Zero (25x18)", 25, 18), ("TMC6300-BOB (25x20)", 25.4, 20.3), ("DRV2605L (20x15)", 20, 15), ("level shifter (20x15)", 20, 15)
POLOLU = ("converter D24V90F5 (41x20)", 40.6, 20.3)

def base(name, grow=0.0, audio=None, converter=None, speaker=None, pillars=(160, 240, 320), blower_mirror=False, blower_daz=0.0, no_usbc_notch=False, park_audio=False):
    L = Layout(name, grow)
    if no_usbc_notch:   # the Pi powered through its header instead of the USB-C plug: the plug head's notch in the window goes
        L.items = [(n, (p.difference(box(-40.8 - 7, PI_Y0 - 14, -40.8 + 7, PI_Y0 - 0.75)) if n == "pi_window" else p)) for n, p in L.items]
    L.add_group("motor", dr=grow); L.add_group("lra", dr=grow); L.add_group("bonds")
    L.add_group("blower", mirror=blower_mirror, daz=blower_daz)
    if speaker is None: L.add_group("speaker", dr=grow)
    else: L.add_circle("speaker", speaker[0], speaker[1], 43.0)
    if park_audio: pass
    elif audio is None: L.add_group("audio", dr=grow)
    else: L.add_rect("audio (40x25)", audio[0], audio[1], 90, 40, 25)
    if converter is None: L.add_rect(POLOLU[0], 180, 65.5 + grow, 90, POLOLU[1], POLOLU[2])
    else: L.add_rect(POLOLU[0], converter[0], converter[1], 90, POLOLU[1], POLOLU[2])
    for az in POST_AZ: L.add(f"post {az}", affinity.scale(post_shape(az), (POST_R + grow) / POST_R, (POST_R + grow) / POST_R, origin=(0, 0)))
    for az in pillars: L.add(f"pillar {az}", affinity.scale(pillar_shape(az), (PILLAR_R + grow) / PILLAR_R, (PILLAR_R + grow) / PILLAR_R, origin=(0, 0)))
    return L

PREFER = {BOB[0]: (0, 60), DRV[0]: (-15, -70), LS[0]: (55, 40)}     # BOB near the motor, DRV near the actuator (az 257), LS near the halo tail notch (az 64) and the Pi's header
def boards(L, mcu, order=None, prefer=False):
    for nm, Lg, Wg in (order or [mcu, BOB, DRV, LS]):
        place_rect(L, nm, Lg, Wg, margin=1.5, r_range=(20, L.R), prefer=(PREFER.get(nm) if prefer else None))
    probs, free = L.evaluate(margin=1.0)
    bad = [(a, b, round(d, 2)) for a, b, d in probs if d < 1.0 and not (a.startswith("post") or a.startswith("pillar") or b.startswith("post") or b.startswith("pillar") or a == "internal_structure" or b == "internal_structure")]
    L.notes.append(f"free {free:.0f} mm2; contacts under 1 mm: {bad}")
    return L

import pickle
DEFS = {
    "A0": lambda: boards(base("A0  Ø175.4 as built, Pico"), PICO),
    "A1": lambda: boards(base("A1  Ø175.4 as built, ESP32-S3-Zero"), ZERO),
    "B0": lambda: boards(base("B0  Ø175.4 audio to the front (az 165), converter to az 205, pillar 160 -> 195; Pico", audio=(165, 64), converter=(205, 69.7), pillars=(195, 240, 320)), PICO),
    "B1": lambda: boards(base("B1  same as B0 with the ESP32-S3-Zero", audio=(165, 64), converter=(205, 69.7), pillars=(195, 240, 320)), ZERO),
    "C0": lambda: boards(base("C0  Ø185.4 (+5 radius) as built, Pico", grow=5.0), PICO),
    "A2": lambda: boards(base("A2  Ø175.4 as built; MCU on a tray above the adapter; BOB, DRV, LS on the plate"), None, order=[BOB, DRV, LS]),
    "A3": lambda: boards(base("A3  Ø175.4 as built, Pi powered via its header (no USB-C notch); Pico on the plate", no_usbc_notch=True), PICO),
    "A4": lambda: boards(base("A4  Ø175.4 as built, no USB-C notch; BOB, DRV, LS on the plate, MCU on the tray", no_usbc_notch=True), None, order=[BOB, DRV, LS]),
    "C2": lambda: boards(base("C2  Ø185.4 as built, no USB-C notch; Pico on the plate", grow=5.0, no_usbc_notch=True), PICO),
    "C3": lambda: boards(base("C3  Ø185.4 as built, no USB-C notch; BOB, DRV, LS on the plate, MCU on the tray", grow=5.0, no_usbc_notch=True), None, order=[BOB, DRV, LS]),
    "A5": lambda: boards(base("A5  Ø175.4, audio board and speaker parked, no USB-C notch; BOB, DRV, LS on the plate, MCU on the tray", no_usbc_notch=True, park_audio=True, speaker=(127.5, 59.2)), None, order=[BOB, DRV, LS]),
    "A6": lambda: boards(base("A6  Ø175.4, audio board parked (speaker kept), no USB-C notch; BOB, DRV, LS on the plate, MCU on the tray", no_usbc_notch=True, park_audio=True), None, order=[BOB, DRV, LS]),
    "A7": lambda: boards(base("A7  Ø175.4, audio parked, no USB-C notch; BOB near the motor, DRV near the actuator, LS near the halo notch; MCU on the tray", no_usbc_notch=True, park_audio=True), None, order=[BOB, DRV, LS], prefer=True),
    "C4": lambda: boards(base("C4  Ø185.4 as built, no USB-C notch; BOB near the motor, DRV near the actuator, LS near the halo notch; MCU on the tray", grow=5.0, no_usbc_notch=True), None, order=[BOB, DRV, LS], prefer=True),
    "C1": lambda: boards(base("C1  Ø185.4 audio to the front, converter to az 205; Pico", grow=5.0, audio=(165, 69), converter=(205, 74.7), pillars=(195, 240, 320)), PICO),
}
if __name__ == "__main__":
    key = sys.argv[1]
    L = DEFS[key]()
    print("==", L.name, flush=True)
    for n in L.notes: print("  ", n, flush=True)
    pickle.dump({"name": L.name, "grow": L.grow, "items": L.items, "movable": L.movable_names, "notes": L.notes, "R": L.R}, open(f"/home/claude/v9/v15/cand_{key}.pkl", "wb"))
