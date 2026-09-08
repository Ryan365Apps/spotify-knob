/*
 * HID policy: the action enum, the one table that turns an action into a key
 * code, and the send discipline. The transport is behind hid_transport.h and
 * is NimBLE as of Wave 10 - see hid_ble.c.
 *
 * The split is the point. This file is short enough to read in a minute, and
 * everything the security rule depends on is in it: hid_send takes a
 * hid_action_t, chord_for is the only function that produces a key code, and
 * an action outside the enum's ranges fails closed. Nothing here accepts a
 * string, and nothing below here ever sees anything but two bytes.
 *
 * The stub this replaced (2026-09-04) reported itself connected so the Wispr
 * and Launcher screens could be built before the radio existed. hid_is_stub()
 * survives it and now returns false.
 */
#include <stdint.h>
#include <stdio.h>

#include "esp_log.h"
#include "esp_timer.h"

#include "hid.h"
#include "hid_transport.h"

static const char *TAG = "hid";

/* USB HID modifier bits and usage IDs. These are the only place in the
 * firmware where a key code appears, and they are all compile-time
 * constants. */
#define MOD_CTRL  0x01
#define MOD_SHIFT 0x02
#define MOD_ALT   0x04
#define MOD_GUI   0x08

#define KEY_A         0x04      /* .. 0x1D for Z */
#define KEY_1         0x1E      /* .. 0x26 for 9 */
#define KEY_ENTER     0x28
#define KEY_ESC       0x29
#define KEY_TAB       0x2B
#define KEY_F1        0x3A      /* .. 0x45 for F12 */
#define KEY_F9        (KEY_F1 + 8)
#define KEY_RIGHT     0x4F
#define KEY_LEFT      0x50

typedef struct {
    uint8_t modifiers;
    uint8_t usage;
} chord_t;

hid_action_t hid_ctrl_alt(char letter)
{
    if (letter >= 'a' && letter <= 'z') {
        letter = (char)(letter - 'a' + 'A');
    }
    if (letter < 'A' || letter > 'Z') {
        return HID_NONE;
    }
    return (hid_action_t)(HID_CTRL_ALT_BASE + (letter - 'A'));
}

/* The whole mapping, and the only function that produces a key code.
 *
 * Returns false for anything outside the enum's ranges, which is what makes a
 * garbage value fail closed rather than send something arbitrary. */
static bool chord_for(hid_action_t action, chord_t *out)
{
    if (action >= HID_PIN_BASE && action <= HID_PIN_LAST) {
        out->modifiers = MOD_GUI;
        out->usage = (uint8_t)(KEY_1 + (action - HID_PIN_BASE));
        return true;
    }
    if (action >= HID_CTRL_ALT_BASE && action <= HID_CTRL_ALT_LAST) {
        out->modifiers = MOD_CTRL | MOD_ALT;
        out->usage = (uint8_t)(KEY_A + (action - HID_CTRL_ALT_BASE));
        return true;
    }
    switch (action) {
    case HID_WISPR_TOGGLE:
        /* BUILD.md section 6 suggests Ctrl+Alt+F9: one clean report, no
         * timing, and nothing in Windows or Spotify claims it. Bind it in
         * Flow Hub to the hands-free action, not to push-to-talk. */
        out->modifiers = MOD_CTRL | MOD_ALT;
        out->usage = KEY_F9;
        return true;
    case HID_TASKVIEW_OPEN:
        out->modifiers = MOD_GUI;
        out->usage = KEY_TAB;
        return true;
    case HID_TASKVIEW_NEXT:
        out->modifiers = 0;
        out->usage = KEY_RIGHT;
        return true;
    case HID_TASKVIEW_PREV:
        out->modifiers = 0;
        out->usage = KEY_LEFT;
        return true;
    case HID_TASKVIEW_PICK:
        out->modifiers = 0;
        out->usage = KEY_ENTER;
        return true;
    case HID_TASKVIEW_CANCEL:
        out->modifiers = 0;
        out->usage = KEY_ESC;
        return true;
    default:
        return false;
    }
}

const char *hid_action_name(hid_action_t action)
{
    /* Static, because ESP_LOGI's format argument must be a string literal and
     * the value has to survive the call. The ranged actions are the only ones
     * that need composing, and the composition is from an index, never from
     * anything a person typed. */
    static char composed[24];

    if (action >= HID_PIN_BASE && action <= HID_PIN_LAST) {
        snprintf(composed, sizeof(composed), "Win+%d", (int)(action - HID_PIN_BASE) + 1);
        return composed;
    }
    if (action >= HID_CTRL_ALT_BASE && action <= HID_CTRL_ALT_LAST) {
        snprintf(composed, sizeof(composed), "Ctrl+Alt+%c",
                 (char)('A' + (action - HID_CTRL_ALT_BASE)));
        return composed;
    }
    switch (action) {
    case HID_WISPR_TOGGLE:    return "Ctrl+Alt+F9 (Wispr hands-free)";
    case HID_TASKVIEW_OPEN:   return "Win+Tab";
    case HID_TASKVIEW_NEXT:   return "Right";
    case HID_TASKVIEW_PREV:   return "Left";
    case HID_TASKVIEW_PICK:   return "Enter";
    case HID_TASKVIEW_CANCEL: return "Esc";
    default:                  return "nothing";
    }
}

bool hid_is_stub(void)
{
    return false;      /* NimBLE landed in Wave 10 */
}

bool hid_connected(void)
{
    return hid_transport_connected();
}

hid_state_t hid_state(void)
{
    return hid_transport_state();
}

uint32_t hid_passkey(void)
{
    return hid_transport_passkey();
}

esp_err_t hid_advertise(void)
{
    return hid_transport_advertise();
}

void hid_forget_host(void)
{
    hid_transport_forget_host();
}

static bool s_started = false;

void hid_init(void)
{
    /* Deliberately empty of anything expensive. Starting the radio at boot
     * took internal RAM from 43 KB to 2635 bytes on hardware (2026-09-04) and
     * the device could no longer complete a TLS handshake, so it never got
     * past the splash. The stack now waits until a screen asks for it. */
    ESP_LOGI(TAG, "HID ready, radio not started - it comes up with Dictation, "
                  "the Launcher, or Settings");
}

esp_err_t hid_start(void)
{
    if (s_started) {
        return ESP_OK;
    }
    if (hid_transport_stopping()) {
        /* A teardown is still in flight. Starting on top of it is how the
         * stack ends up half up and half down. */
        ESP_LOGW(TAG, "still shutting down - not starting again yet");
        return ESP_ERR_INVALID_STATE;
    }
    const esp_err_t err = hid_transport_init();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "BLE HID did not start (%s) - screens will report no host "
                      "rather than pretending", esp_err_to_name(err));
        return err;
    }
    s_started = true;
    return ESP_OK;
}

void hid_stop(void)
{
    if (!s_started) {
        return;
    }
    /* Asynchronous: the teardown has to wait for a disconnect before it frees
     * anything, and this is called from on_exit on the LVGL thread where
     * nothing may block. s_started drops now so nothing re-enters mid-flight;
     * the radio itself is gone a few hundred milliseconds later. */
    hid_transport_deinit();
    s_started = false;
    ESP_LOGI(TAG, "HID stopping - the radio and its memory come back shortly");
}

bool hid_is_started(void)
{
    return s_started;
}

/*
 * Send discipline, from BUILD.md section 5.
 *
 * Chords are serialised with at least 600 ms between them, so one movement can
 * never double-send. The simulator desynced itself exactly this way on
 * 2026-08-31, which is where the rule comes from.
 *
 * The refusal is reported rather than swallowed, and that matters: the Wispr
 * app only flips its believed state when a chord was actually dispatched, so a
 * suppressed send has to come back as an error or the belief drifts from
 * reality with nothing to correct it.
 */
#define CHORD_GAP_MS 600
static int64_t s_last_send_us = 0;

esp_err_t hid_send(hid_action_t action)
{
    chord_t c;
    if (!chord_for(action, &c)) {
        ESP_LOGW(TAG, "refusing an action outside the enum (%d)", (int) action);
        return ESP_ERR_INVALID_ARG;
    }
    if (!hid_connected()) {
        ESP_LOGW(TAG, "%s not sent - no host connected", hid_action_name(action));
        return ESP_ERR_INVALID_STATE;
    }

    const int64_t now = esp_timer_get_time();
    if (now - s_last_send_us < (int64_t) CHORD_GAP_MS * 1000) {
        ESP_LOGW(TAG, "%s suppressed - inside the %d ms chord gap",
                 hid_action_name(action), CHORD_GAP_MS);
        return ESP_ERR_NOT_FINISHED;
    }

    ESP_LOGI(TAG, "send %s", hid_action_name(action));
    const esp_err_t err = hid_transport_send(c.modifiers, c.usage);
    if (err == ESP_OK) {
        s_last_send_us = esp_timer_get_time();
    }
    return err;
}
