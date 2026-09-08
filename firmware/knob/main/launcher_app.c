/*
 * The Launcher (app 4). Drawn to design/screens.html rev W, screens 15 A (the
 * ring), 15 B (launching) and 15 C (Task View).
 *
 * A short, ordered list of PC applications. The dial scrolls it, a tap sends
 * one chord, and the device goes back to where it started. Identical mechanic
 * to the app selector, one level down and pointed at the PC instead of at
 * Radial - the dial does the same thing in both, which is the point of having
 * a shell at all.
 *
 * Two things this screen will never do, both from BUILD.md section 6:
 *
 *   - **It cannot confirm anything.** The device has no idea whether the
 *     application launched, was already open, or whether the chord landed on a
 *     locked screen. So it says "Launching" for 1.5 s and returns. Anything
 *     more confident would be a claim it cannot support, and closing the loop
 *     needs a process running on the PC that this project deliberately does
 *     not have.
 *   - **No string here becomes a keystroke.** A label is free text because a
 *     label is only ever drawn. The chord beside it is a hid_action_t, and
 *     hid.h is where that rule is enforced by the type system rather than by
 *     everyone remembering it.
 *
 * Eight entries is a hard cap and the cap is the feature: fixed positions are
 * the entire value, and a ninth entry makes every position one you read rather
 * than one you know.
 */
#include <stdbool.h>

#include "esp_log.h"
#include "esp_timer.h"

#include "app_shell.h"
#include "hid.h"
#include "launcher_app.h"
#include "ring.h"

static const char *TAG = "launcher";

#define COL_GROUND   0x0A0B0D
#define COL_GREEN    0x3FE07A

#define LAUNCHING_MS 1500
#define TASKVIEW_IDLE_MS 5000

typedef struct {
    const char  *label;      /* free text: only ever drawn                 */
    const char  *glyph;      /* from a fixed set, never an uploaded icon   */
    hid_action_t action;     /* an enum. This is the rule, in one field    */
} entry_t;

/*
 * Placeholders until Wave 9's config page exists - the editor is where these
 * are meant to come from, and naming an application is typing, which is a
 * thing this device does not do.
 *
 * The chords are the Ctrl+Alt range on purpose. A .lnk shortcut key follows
 * the file; Win+N follows a taskbar position, which you will one day drag.
 * Create the shortcuts under
 * %APPDATA%\Microsoft\Windows\Start Menu\Programs and set the Shortcut key on
 * each - a .lnk anywhere else accepts the key in its properties dialog and
 * then silently does nothing.
 *
 * Task View is always last, with its own glyph, and it is entered like any
 * other launch.
 */
static const entry_t ENTRIES[] = {
    { "VS Code",   LV_SYMBOL_EDIT,      HID_CTRL_ALT_BASE + ('C' - 'A') },
    { "Browser",   LV_SYMBOL_HOME,      HID_CTRL_ALT_BASE + ('B' - 'A') },
    { "Slack",     LV_SYMBOL_ENVELOPE,  HID_CTRL_ALT_BASE + ('S' - 'A') },
    { "Files",     LV_SYMBOL_DIRECTORY, HID_CTRL_ALT_BASE + ('E' - 'A') },
    { "Terminal",  LV_SYMBOL_KEYBOARD,  HID_CTRL_ALT_BASE + ('T' - 'A') },
    { "Spotify",   LV_SYMBOL_AUDIO,     HID_CTRL_ALT_BASE + ('P' - 'A') },
    { "Task View", LV_SYMBOL_LIST,      HID_TASKVIEW_OPEN },
};
#define ENTRY_COUNT ((int)(sizeof(ENTRIES) / sizeof(ENTRIES[0])))

typedef enum { MODE_RING, MODE_LAUNCHING, MODE_TASKVIEW } mode_t;

static mode_t     s_mode = MODE_RING;
static ring_t    *s_ring = NULL;
static lv_obj_t  *s_launch_layer = NULL;
static lv_obj_t  *s_launch_name = NULL;
static lv_obj_t  *s_task_layer = NULL;
static lv_timer_t *s_hold_timer = NULL;
static int64_t    s_task_last_input_us = 0;
static bool       s_swallow_click = false;

/* --- the ring's view of the list ---------------------------------------- */

static const char *glyph_at(int i)
{
    return (i >= 0 && i < ENTRY_COUNT) ? ENTRIES[i].glyph : "?";
}

static const char *name_at(int i)
{
    return (i >= 0 && i < ENTRY_COUNT) ? ENTRIES[i].label : "";
}

/* --- mode plumbing ------------------------------------------------------ */

static void show_layer(lv_obj_t *layer, bool visible)
{
    if (layer == NULL) {
        return;
    }
    if (visible) {
        lv_obj_remove_flag(layer, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_add_flag(layer, LV_OBJ_FLAG_HIDDEN);
    }
}

static void hold_timer_stop(void)
{
    if (s_hold_timer != NULL) {
        lv_timer_delete(s_hold_timer);
        s_hold_timer = NULL;
    }
}

static void go_home(void *unused)
{
    (void) unused;
    shell_switch_home();
}

static void launching_done_cb(lv_timer_t *t)
{
    (void) t;
    /* One-shot: LVGL deletes this timer itself the moment the callback
     * returns, so the pointer has to be dropped here. Deleting it a second
     * time corrupts LVGL's heap (BUILD.md section 6). */
    s_hold_timer = NULL;
    /* And the switch goes through an async call rather than happening inside
     * lv_timer_handler, because it tears down the screen this timer is
     * standing on. */
    lv_async_call(go_home, NULL);
}

/* The ring is hidden rather than merely covered whenever another mode is up.
 * An overlay that is not itself clickable does not absorb a tap, so a tap
 * would reach the rim glyph underneath and launch something nobody asked
 * for. */
static void enter_ring_mode(void)
{
    s_mode = MODE_RING;
    show_layer(s_launch_layer, false);
    show_layer(s_task_layer, false);
    ring_set_hidden(s_ring, false);
}

static void enter_launching(const entry_t *e)
{
    s_mode = MODE_LAUNCHING;
    lv_label_set_text(s_launch_name, e->label);
    ring_set_hidden(s_ring, true);
    show_layer(s_task_layer, false);
    show_layer(s_launch_layer, true);

    hold_timer_stop();
    s_hold_timer = lv_timer_create(launching_done_cb, LAUNCHING_MS, NULL);
    lv_timer_set_repeat_count(s_hold_timer, 1);
}

static void enter_taskview(void)
{
    if (hid_send(HID_TASKVIEW_OPEN) != ESP_OK) {
        ESP_LOGW(TAG, "Task View not opened - no host");
        return;
    }
    s_mode = MODE_TASKVIEW;
    s_task_last_input_us = esp_timer_get_time();
    shell_haptic_click();
    ring_set_hidden(s_ring, true);
    show_layer(s_launch_layer, false);
    show_layer(s_task_layer, true);
    ESP_LOGI(TAG, "Task View mode - dial moves, tap selects, hold cancels");
}

/* Esc, then out. Called by the tap, the long-press and the idle timeout, and
 * the idle one is not a nicety: without it, walking away leaves Task View open
 * across the whole screen with no way back except the keyboard you were trying
 * not to touch. */
static void leave_taskview(bool cancel, bool go_to_home)
{
    if (s_mode != MODE_TASKVIEW) {
        return;
    }
    hid_send(cancel ? HID_TASKVIEW_CANCEL : HID_TASKVIEW_PICK);
    enter_ring_mode();
    if (go_to_home) {
        lv_async_call(go_home, NULL);
    }
}

/* --- input -------------------------------------------------------------- */

static void on_pick(int index)
{
    if (index < 0 || index >= ENTRY_COUNT) {
        return;
    }
    const entry_t *e = &ENTRIES[index];

    if (e->action == HID_TASKVIEW_OPEN) {
        enter_taskview();
        return;
    }
    if (hid_send(e->action) != ESP_OK) {
        ESP_LOGW(TAG, "%s not launched - no host connected", e->label);
        return;
    }
    shell_haptic_click();
    ESP_LOGI(TAG, "launching '%s' with %s", e->label, hid_action_name(e->action));
    enter_launching(e);
}

static void on_back(void)
{
    /* Back from any ring is the menu, not the app you happened to start in.
     * The rule is in docs/USER-JOURNEY.md and it is the same everywhere. */
    shell_open_menu();
}

static void launcher_on_dial(int delta)
{
    if (s_mode == MODE_TASKVIEW) {
        s_task_last_input_us = esp_timer_get_time();
        /* One arrow key per detent. The device cannot know how many windows
         * exist or which is highlighted, which is why this screen carries no
         * position counter - a readout would be invented. */
        for (int i = 0; i < (delta > 0 ? delta : -delta); i++) {
            hid_send(delta > 0 ? HID_TASKVIEW_NEXT : HID_TASKVIEW_PREV);
        }
        return;
    }
    if (s_mode == MODE_RING) {
        ring_dial(s_ring, delta);
    }
    /* MODE_LAUNCHING ignores the dial: it is a 1.5 s statement, not a screen
     * you interact with. */
}

/* The shell owns the long-press on this screen and LVGL sends CLICKED on
 * release either way, so a long-press has to be swallowed here - otherwise
 * letting go of one would also select a window in Task View. */
static void screen_click_cb(lv_event_t *e)
{
    const lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_LONG_PRESSED) {
        s_swallow_click = true;
        if (s_mode == MODE_TASKVIEW) {
            /* Hold to cancel: Esc, and back to the ring. The shell opens the
             * selector over the top, and backing out of that returns here. */
            leave_taskview(true, false);
        }
        return;
    }
    if (s_swallow_click) {
        s_swallow_click = false;
        return;
    }
    if (s_mode == MODE_TASKVIEW) {
        leave_taskview(false, true);       /* Enter, then back to the default screen */
    }
}

/* --- the three layers --------------------------------------------------- */

static lv_obj_t *layer_create(lv_obj_t *parent)
{
    lv_obj_t *l = lv_obj_create(parent);
    lv_obj_remove_style_all(l);
    lv_obj_set_size(l, 360, 360);
    lv_obj_center(l);
    /* Not clickable, or it swallows the shell's long-press and the selector
     * can never open from this app (BUILD.md section 6). */
    lv_obj_remove_flag(l, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_color(l, lv_color_hex(COL_GROUND), 0);
    lv_obj_set_style_bg_opa(l, LV_OPA_COVER, 0);
    lv_obj_add_flag(l, LV_OBJ_FLAG_HIDDEN);
    return l;
}

static void build_launching_layer(lv_obj_t *parent)
{
    s_launch_layer = layer_create(parent);

    /* A full green rim. It is not a progress bar - there is nothing to make
     * progress on - it is the colour of the device doing something. */
    lv_obj_t *arc = lv_arc_create(s_launch_layer);
    lv_obj_set_size(arc, 344, 344);
    lv_obj_center(arc);
    lv_obj_remove_style(arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(arc, LV_OBJ_FLAG_CLICKABLE);
    lv_arc_set_bg_angles(arc, 0, 360);
    lv_arc_set_angles(arc, 0, 360);
    lv_obj_set_style_arc_width(arc, 5, LV_PART_MAIN);
    lv_obj_set_style_arc_color(arc, lv_color_hex(COL_GREEN), LV_PART_MAIN);
    lv_obj_set_style_arc_width(arc, 0, LV_PART_INDICATOR);
    lv_obj_set_style_arc_opa(arc, LV_OPA_TRANSP, LV_PART_INDICATOR);

    /* "Launching", never "Launched". The word is chosen to claim exactly what
     * is known: a keystroke was sent. */
    lv_obj_t *verb = lv_label_create(s_launch_layer);
    lv_obj_set_style_text_font(verb, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(verb, lv_color_white(), 0);
    lv_label_set_text(verb, "Launching");
    lv_obj_align(verb, LV_ALIGN_CENTER, 0, -12);

    s_launch_name = lv_label_create(s_launch_layer);
    lv_obj_set_style_text_font(s_launch_name, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_launch_name, lv_color_hex(0x9AA0A8), 0);
    lv_label_set_text(s_launch_name, "");
    lv_obj_align(s_launch_name, LV_ALIGN_CENTER, 0, 24);
}

static void build_taskview_layer(lv_obj_t *parent)
{
    s_task_layer = layer_create(parent);

    lv_obj_t *title = lv_label_create(s_task_layer);
    lv_obj_set_style_text_font(title, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(title, lv_color_hex(COL_GREEN), 0);
    lv_obj_set_style_text_letter_space(title, 4, 0);
    lv_label_set_text(title, "TASK VIEW");
    lv_obj_align(title, LV_ALIGN_CENTER, 0, -110);

    /* A legend, not a display. Here the device is driving Windows' own Task
     * View and you are looking at the monitor, so the screen stops trying to
     * be a window list and becomes a key to what the dial currently does. */
    static const char *const ROW_KEY[] = { "DIAL", "TAP" };
    static const char *const ROW_ACT[] = { "move", "select" };
    for (int i = 0; i < 2; i++) {
        lv_obj_t *k = lv_label_create(s_task_layer);
        lv_obj_set_style_text_font(k, &lv_font_montserrat_20, 0);
        lv_obj_set_style_text_color(k, lv_color_hex(0x6E7278), 0);
        lv_obj_set_style_text_letter_space(k, 3, 0);
        lv_label_set_text(k, ROW_KEY[i]);
        lv_obj_align(k, LV_ALIGN_CENTER, 0, -34 + i * 62);

        lv_obj_t *a = lv_label_create(s_task_layer);
        lv_obj_set_style_text_font(a, &lv_font_montserrat_24, 0);
        lv_obj_set_style_text_color(a, lv_color_white(), 0);
        lv_label_set_text(a, ROW_ACT[i]);
        lv_obj_align(a, LV_ALIGN_CENTER, 0, -6 + i * 62);
    }

    lv_obj_t *hint = lv_label_create(s_task_layer);
    lv_obj_set_style_text_font(hint, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(hint, lv_color_hex(0x5C6068), 0);
    lv_label_set_text(hint, "HOLD TO CANCEL");
    lv_obj_align(hint, LV_ALIGN_CENTER, 0, 108);
}

/* --- lifecycle ---------------------------------------------------------- */

static void launcher_on_enter(lv_obj_t *parent)
{
    hid_start();     /* on demand, not at boot - see hid.h */

    lv_obj_set_style_bg_color(parent, lv_color_hex(COL_GROUND), 0);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_LONG_PRESSED, NULL);
    s_swallow_click = false;

    const ring_cfg_t cfg = {
        .count = ENTRY_COUNT,
        .initial = 0,
        .glyph_at = glyph_at,
        .name_at = name_at,
        .on_pick = on_pick,
        .on_back = on_back,
        /* False: this ring lives inside an app screen and must stay
         * transparent to the shell's long-press. */
        .own_ground = false,
        .show_count = true,
        .idle_close_ms = 0,          /* you are in this app; it does not time out */
        .accent = LV_COLOR_MAKE(0x3F, 0xE0, 0x7A),
    };
    s_ring = ring_create(parent, &cfg);

    build_launching_layer(parent);
    build_taskview_layer(parent);
    enter_ring_mode();

    ESP_LOGI(TAG, "entered, %d entries%s", ENTRY_COUNT,
             hid_is_stub() ? " (HID is the Wave 10 stub)" : "");
}

static void launcher_on_exit(void)
{
    hold_timer_stop();
    /* Leaving with Task View still open on the PC would strand it there. */
    if (s_mode == MODE_TASKVIEW) {
        hid_send(HID_TASKVIEW_CANCEL);
    }
    s_mode = MODE_RING;

    ring_destroy(s_ring);
    s_ring = NULL;
    /* The shell deletes the screen and every widget on it. This app holds no
     * buffers of its own. */
    s_launch_layer = s_launch_name = s_task_layer = NULL;
    hid_stop();       /* the radio is Spotify's again - see hid.h */
    ESP_LOGI(TAG, "exited");
}

static void launcher_on_tick(void)
{
    if (s_mode != MODE_TASKVIEW) {
        return;
    }
    if (esp_timer_get_time() - s_task_last_input_us >
        (int64_t) TASKVIEW_IDLE_MS * 1000) {
        ESP_LOGI(TAG, "Task View idle %d s - cancelling", TASKVIEW_IDLE_MS / 1000);
        leave_taskview(true, true);
    }
}

const knob_app_t launcher_app = {
    .name = "Launcher",
    .glyph = LV_SYMBOL_LIST,
    .accent = LV_COLOR_MAKE(0x3F, 0xE0, 0x7A),
    .on_enter = launcher_on_enter,
    .on_exit = launcher_on_exit,
    .on_dial = launcher_on_dial,
    .on_tick = launcher_on_tick,
};
