# Software HID contract — what the device may ever type

**Date:** 2026-09-02. **Applies to:** the standard device over Bluetooth (BLE HID) and the halo over USB, one contract. Halo-only extensions are marked. **Sibling documents:** `docs/SOFTWARE-INTERACTION-CORE.md` (when input happens), `BUILD.md` section 6 (the Wispr app and the security rule this contract enforces).

## The descriptor

- **Standard:** a keyboard, and nothing else. No consumer-control page, no mouse, no telephony. Ruled 2026-09-02 against copying the halo's wheel: the standard's dial is volume and it lives next to a real mouse.
- **Halo (extension):** a composite device — the same keyboard, a mouse exposing a vertical wheel and a horizontal wheel (AC Pan) with **no buttons and no pointer**, and later a telephony page for Meet. One physical device, multiple interfaces.

## The chord enum — the load-bearing rule

**No string a human typed ever becomes a keystroke.** The HID layer accepts an enum of fixed, compile-time actions and nothing else. Configurable values arriving over HTTP or from a config page are indices and key codes chosen from a fixed set — never free text. No endpoint, on any surface, may accept a string and send it as keystrokes; that endpoint is remote code execution on the paired PC.

The fixed set:

| Action | Chord | Used by |
|---|---|---|
| Dictation hands-free toggle | `Ctrl`+`Alt`+`F9` (whatever is bound in Wispr's Flow Hub; this is the bound value) | Wispr app |
| Launch entry 1–9 (taskbar) | `Win`+`1` … `Win`+`9` | Launcher |
| Launch entry (shortcut key) | `Ctrl`+`Alt`+`A` … `Ctrl`+`Alt`+`Z` | Launcher |
| Task View open / navigate / choose / leave | `Win`+`Tab` · `Right` / `Left` · `Enter` · `Esc` | Launcher mode 2 |
| Summon player (optional, off by default) | `Win`+`N`, N a Settings value | Controls device pill |

## Send discipline

- **Discrete presses only.** A chord is one press-and-release report sequence; modifiers are never held across user actions. A held modifier poisons the whole machine (every click becomes a modified click).
- **Serialised.** One chord in flight at a time; the next waits. Two interleaved chords can leave a modifier logically stuck down system-wide — observed 2026-08-31 when the simulator's first bridge overlapped two synthesized sends. A real HID report is atomic, but the discipline stays.
- **At least 600 ms between chords.** One physical gesture can never double-send.
- **Belief follows dispatch.** Any believed state (dictation on/off) changes only when its chord was actually sent. A suppressed, queued-then-dropped, or failed send must not flip belief. The receiving application can still ignore a delivered chord (Wispr observably drops its hotkey when certain windows have focus); belief drift is recovered by the user-facing resync, never by retrying automatically.
- **Open-loop honesty.** The device never claims an effect, only a send: "Launching", never "Launched". Nothing on the PC reports back, by design.

## Transport notes

- **Standard:** NimBLE, keyboard descriptor only; bond stored in NVS, reconnects on boot. BLE HID never touches USB — the S3's USB peripheral is the flashing path and this board has no BOOT/RESET recovery, so claiming USB is a brick risk.
- **Halo (extension):** USB composite. The wheel uses 120 units per detent (one notch per magnetic detent); the motor's fine steps emit sub-notch deltas, which Windows renders as smooth scroll via the Resolution Multiplier — verify item 6 in `docs/SOFTWARE-CONTEXTS.md`.

## First-hardware verify (standard)

With Wave 3+ running: pair to the PC, send the dictation chord from the device, and confirm it lands with Wispr's Flow Bar while the device screen shows the believed state. This is the shared half of the contexts doc's verify list; everything else there is halo-only.
