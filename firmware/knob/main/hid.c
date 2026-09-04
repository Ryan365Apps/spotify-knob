/*
 * The HID layer. Wave 10 puts NimBLE behind this; today it is a stub that
 * logs what it would have sent, so the Wispr and Launcher screens can be
 * judged on glass before any BLE stack exists.
 *
 * The stub reports itself as connected. That is deliberate and it is why
 * hid_is_stub() exists: the screens need to be exercisable now, and every
 * send prints a line saying no keystroke left the building. Nothing here
 * touches the radio, so this cannot affect Wi-Fi throughput, and nothing here
 * claims USB - USB HID and the flashing port are the same peripheral on this
 * board and there is no BOOT button to recover with (BUILD.md section 3).
 *
 * When Wave 10 lands, delete HID_TRANSPORT_STUB and fill in send_report().
 * The rest of the firmware should not need one line changed, because nothing
 * above this file knows what a key code is.
 */
#include <stdint.h>
#include <stdio.h>

#include "esp_log.h"

#include "hid.h"

static const char *TAG = "hid";

/* Wave 10 removes this. */
#define HID_TRANSPORT_STUB 1

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

#if HID_TRANSPORT_STUB

static esp_err_t send_report(const chord_t *c)
{
    ESP_LOGI(TAG, "would send modifiers 0x%02X usage 0x%02X - no BLE yet (Wave 10)",
             c->modifiers, c->usage);
    return ESP_OK;
}

bool hid_connected(void)
{
    /* The stub says yes so the screens can be worked on. hid_is_stub is how
     * anything that cares tells the difference. */
    return true;
}

bool hid_is_stub(void)
{
    return true;
}

void hid_init(void)
{
    ESP_LOGW(TAG, "HID transport is the Wave 10 stub - actions are logged, "
                  "nothing is sent to the PC");
}

#else
#error "Wave 10: implement NimBLE HID here. Keyboard descriptor only - no consumer control, no mouse."
#endif

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
    ESP_LOGI(TAG, "send %s", hid_action_name(action));
    return send_report(&c);
}
