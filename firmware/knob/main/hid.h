/*
 * The HID layer's public face: an enum of fixed actions, and nothing else.
 *
 * This is BUILD.md section 6's hard rule expressed as a type. Radial will be a
 * BLE HID keyboard, and its config server is reachable by anything on the LAN.
 * If any path existed from a string to a keystroke, that path would be remote
 * code execution on the PC for everyone on the network - and it is an easy
 * thing to build by accident, because "let me POST a macro to the device" is
 * the obvious next idea.
 *
 * So: no function in this module accepts a string. hid_send takes a
 * hid_action_t and nothing else, and every action maps to a modifier and usage
 * pair chosen at compile time inside hid.c. Configurable actions (which
 * taskbar pin, which shortcut letter) are indices into fixed ranges, never
 * free text. A label typed by a human is only ever drawn on a screen.
 *
 * If you are about to add a function here that takes a char*, stop.
 */
#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

typedef enum {
    HID_NONE = 0,

    /* Wispr Flow. One combo bound to Wispr's hands-free action - deliberately
     * not its stock Ctrl+Win double-tap, which needs a modifier-only report
     * and timing, and is fragile in both halves. See BUILD.md section 6. */
    HID_WISPR_TOGGLE = 1,

    /* Task View, the launcher's second mode. Win+Tab rather than Alt+Tab:
     * Alt+Tab only stays open while Alt is held, and holding a modifier
     * poisons every click and scroll on the machine. */
    HID_TASKVIEW_OPEN   = 2,
    HID_TASKVIEW_NEXT   = 3,
    HID_TASKVIEW_PREV   = 4,
    HID_TASKVIEW_PICK   = 5,
    HID_TASKVIEW_CANCEL = 6,

    /* Win+1 .. Win+9: the Nth pinned taskbar item, launch if closed and focus
     * if open. Positional, so it breaks silently when the taskbar is
     * reordered - which is why BUILD.md prefers the range below for anything
     * you care about. */
    HID_PIN_BASE = 16,
    HID_PIN_LAST = HID_PIN_BASE + 8,

    /* Ctrl+Alt+A .. Ctrl+Alt+Z: the Shortcut key property of a Windows .lnk.
     * It follows the file rather than a screen position, needs nothing
     * installed, and gives launch-or-focus for free. */
    HID_CTRL_ALT_BASE = 32,
    HID_CTRL_ALT_LAST = HID_CTRL_ALT_BASE + 25,
} hid_action_t;

/* Win + (n), n = 1..9. Any other n yields HID_NONE. */
static inline hid_action_t hid_pin(int n)
{
    return (n >= 1 && n <= 9) ? (hid_action_t)(HID_PIN_BASE + n - 1) : HID_NONE;
}

/* Ctrl + Alt + letter, letter = 'A'..'Z' or 'a'..'z'. Anything else is
 * HID_NONE - the range check is the whole point, so do not relax it. */
hid_action_t hid_ctrl_alt(char letter);

/* What the link is doing, for the one screen that reports it. */
typedef enum {
    HID_STATE_OFF = 0,       /* the stack is not running                   */
    HID_STATE_ADVERTISING,   /* waiting for a host to connect              */
    HID_STATE_PAIRING,       /* a passkey is on the screen, type it on the PC */
    HID_STATE_CONNECTED,     /* bonded, encrypted, ready to send           */
} hid_state_t;

/* Send one action as a single atomic key report: press, then release. Never
 * holds a modifier down, because a held modifier makes every mouse click on
 * the PC a ctrl-click for as long as it lasts.
 *
 * Chords are serialised with at least 600 ms between them (BUILD.md section
 * 5): one movement can never double-send, and a suppressed send never flips a
 * believed state, because this returns an error rather than pretending.
 *
 * Returns ESP_ERR_INVALID_ARG for an action outside the enum's ranges,
 * ESP_ERR_INVALID_STATE when no host is connected, and ESP_ERR_NOT_FINISHED
 * when it arrived inside another chord's 600 ms. */
esp_err_t hid_send(hid_action_t action);

/* True when a host is bonded and connected. The UI uses this to say what it
 * knows rather than what it hopes. */
bool hid_connected(void);

hid_state_t hid_state(void);

/* The six digits to type on the PC. Meaningful only in HID_STATE_PAIRING. */
uint32_t hid_passkey(void);

/* Start advertising, for when there is no bond to fall back on. */
esp_err_t hid_advertise(void);

/* Drop every bond. A paired BLE keyboard can type anything into the PC it is
 * paired with, so this is the one action in Settings that confirms first. */
void hid_forget_host(void);

/* True while the transport is a stub rather than a real BLE keyboard. Kept so
 * a screen can label itself honestly; false since Wave 10. */
bool hid_is_stub(void);

/* A human-readable name for a log line or a screen. This is the one direction
 * that is safe: an action becomes text. Text never becomes an action. */
const char *hid_action_name(hid_action_t action);

/* Note the seam here: init is free, start is not.
 *
 * hid_init() only makes the module safe to call. hid_start() brings the BLE
 * controller and the NimBLE host up, and on this board that costs about 40 KB
 * of internal RAM - which is roughly all the internal RAM there is once Wi-Fi,
 * LVGL and a TLS session have taken theirs. Measured on hardware 2026-09-04:
 * starting it at boot left 2635 bytes free and the device could not complete a
 * TLS handshake at all.
 *
 * So the stack starts on demand, when a screen that needs it is opened, and
 * the device boots exactly as it did before BLE existed. This is the option
 * BUILD.md always held open - scope BLE to the app that uses it, and decide
 * with numbers rather than in advance. */
void hid_init(void);
esp_err_t hid_start(void);

/* Give the radio back.
 *
 * Not optional housekeeping. With the link up, free internal RAM sits near
 * 26 KB and Spotify's TLS connect times out - measured on hardware
 * 2026-09-06, presenting as `Failed to open new connection in specified
 * timeout` rather than as anything mentioning Bluetooth. Whether the binding
 * constraint is the memory or the two radios time-slicing, the answer is the
 * same: a screen that needed the keyboard gives it back when you leave.
 *
 * The bond lives in NVS, so coming back reconnects rather than re-pairs. */
void hid_stop(void);

bool hid_is_started(void);
