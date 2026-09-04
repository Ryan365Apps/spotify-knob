/*
 * Wispr Flow (app 3). Drawn to design/screens.html rev W, screens 13 A (off)
 * and 13 B (capturing).
 *
 * The whole app is one keystroke. It does not talk to Wispr, know whether
 * Wispr is running, or need anything installed on the PC - it sends a combo
 * bound to Wispr's hands-free action and that is all. So there is nothing to
 * configure on screen and nothing to read, and the screen says only which way
 * to turn.
 *
 * The hard part is that hands-free is one toggle action rather than an on and
 * an off, so the device can only flip it and never set it. Three things make
 * that acceptable, all from BUILD.md section 6:
 *
 *   1. The dial is idempotent. Right means "I want it on" and left means "I
 *      want it off", so spinning right twice starts dictation once.
 *   2. Two spins the same way inside 2 s send the combo regardless of belief.
 *      That is the resync, and it is the only recovery needed.
 *   3. Wispr's own Flow Bar is the truth and is already on the screen you are
 *      looking at. A desync is visible before it is confusing.
 *
 * This screen therefore shows a belief and says so by never claiming more.
 * The elapsed time is counted from the moment the combo was sent, which is
 * honest about exactly what the device knows.
 *
 * Three detents, not one, because this must never fire from a knock.
 */
#include <math.h>
#include <stdbool.h>

#include "esp_log.h"
#include "esp_timer.h"

#include "app_shell.h"
#include "hid.h"
#include "wispr_app.h"

static const char *TAG = "wispr";

/* rev W's palette. Red rather than green because every other red ring anyone
 * has seen means something is recording, and green already means volume
 * here. */
#define COL_LIVE      0xFF7A87
#define COL_GROUND    0x0A0B0D
#define COL_DIM_RING  0x1B1C1E   /* rgba(255,255,255,.09) over the ground */

#define SPIN_DETENTS      3
#define SPIN_GAP_MS     600      /* detents further apart than this are not one spin */
#define RESYNC_MS      2000

/* The breathe is stepped at 10 fps rather than animated at LVGL's refresh
 * rate. Changing the arc's opacity invalidates its whole bounding box, which
 * for a full-circle arc is effectively the screen - and BUILD.md section 6 is
 * blunt about counting per-frame work before flashing it. A 2.6 s breathe at
 * 10 fps is 26 steps, which is smooth for something this slow, and it is a
 * fifth of the redraws the default rate would have asked for. */
#define BREATHE_MS     2600
#define BREATHE_STEP_MS 100

static lv_obj_t   *s_arc = NULL;
static lv_obj_t   *s_mic_body = NULL;
static lv_obj_t   *s_mic_arc = NULL;
static lv_obj_t   *s_mic_stand = NULL;
static lv_obj_t   *s_state_label = NULL;
static lv_obj_t   *s_hint_label = NULL;
static lv_obj_t   *s_elapsed_label = NULL;
static lv_timer_t *s_breathe_timer = NULL;

/* What the device believes, which is not what it knows. Deliberately not
 * persisted: after a reboot the device has no business claiming dictation is
 * running, and assuming off costs one spin to correct. */
static bool    s_believed_on = false;
static int64_t s_started_us = 0;

static int     s_accum = 0;          /* detents since the last spin or gap */
static int64_t s_last_detent_us = 0;
static int     s_last_spin_dir = 0;
static int64_t s_last_spin_us = 0;

static bool    s_swallow_click = false;

/* --- the screen --------------------------------------------------------- */

static void paint(void)
{
    if (s_arc == NULL) {
        return;
    }
    if (s_believed_on) {
        lv_obj_set_style_arc_color(s_arc, lv_color_hex(COL_LIVE), LV_PART_MAIN);
        lv_obj_set_style_arc_opa(s_arc, LV_OPA_COVER, LV_PART_MAIN);

        lv_obj_set_style_border_color(s_mic_body, lv_color_hex(COL_LIVE), 0);
        lv_obj_set_style_arc_color(s_mic_arc, lv_color_hex(COL_LIVE), LV_PART_MAIN);
        lv_obj_set_style_bg_color(s_mic_stand, lv_color_hex(COL_LIVE), 0);

        lv_label_set_text(s_state_label, "Live");
        lv_obj_set_style_text_color(s_state_label, lv_color_hex(COL_LIVE), 0);

        lv_obj_add_flag(s_hint_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_elapsed_label, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_set_style_arc_color(s_arc, lv_color_hex(COL_DIM_RING), LV_PART_MAIN);
        lv_obj_set_style_arc_opa(s_arc, LV_OPA_COVER, LV_PART_MAIN);

        lv_obj_set_style_border_color(s_mic_body, lv_color_hex(0x4D4D4D), 0);
        lv_obj_set_style_arc_color(s_mic_arc, lv_color_hex(0x4D4D4D), LV_PART_MAIN);
        lv_obj_set_style_bg_color(s_mic_stand, lv_color_hex(0x4D4D4D), 0);

        lv_label_set_text(s_state_label, "Dictation");
        lv_obj_set_style_text_color(s_state_label, lv_color_white(), 0);

        lv_obj_remove_flag(s_hint_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(s_elapsed_label, LV_OBJ_FLAG_HIDDEN);
    }
}

static void elapsed_update(void)
{
    if (!s_believed_on || s_elapsed_label == NULL) {
        return;
    }
    const int s = (int)((esp_timer_get_time() - s_started_us) / 1000000);
    lv_label_set_text_fmt(s_elapsed_label, "%d:%02d", s / 60, s % 60);
}

static void breathe_cb(lv_timer_t *t)
{
    (void) t;
    if (s_arc == NULL) {
        return;
    }
    if (!s_believed_on) {
        lv_obj_set_style_arc_opa(s_arc, LV_OPA_COVER, LV_PART_MAIN);
        return;
    }
    /* 1.0 down to 0.5 and back, rev W's 2.6 s cycle. */
    const float phase = (float)((esp_timer_get_time() / 1000) % BREATHE_MS) /
                        (float) BREATHE_MS;
    const float k = 0.5f + 0.5f * cosf(phase * 2.0f * (float) M_PI);
    lv_obj_set_style_arc_opa(s_arc, (lv_opa_t)(127 + 128.0f * k), LV_PART_MAIN);
}

/* --- the one thing it does ---------------------------------------------- */

static void send_toggle(const char *why)
{
    if (hid_send(HID_WISPR_TOGGLE) != ESP_OK) {
        /* Belief is only worth holding if the keystroke left. */
        ESP_LOGW(TAG, "combo not sent (%s) - belief unchanged", why);
        return;
    }
    s_believed_on = !s_believed_on;
    if (s_believed_on) {
        s_started_us = esp_timer_get_time();
    }
    shell_haptic_click();
    ESP_LOGI(TAG, "%s -> believed %s", why, s_believed_on ? "on" : "off");
    paint();
    elapsed_update();
}

/* One completed three-detent spin, direction signed. */
static void spin(int dir)
{
    const int64_t now = esp_timer_get_time();
    const bool resync = (dir == s_last_spin_dir) &&
                        (now - s_last_spin_us < (int64_t) RESYNC_MS * 1000);
    s_last_spin_dir = dir;
    s_last_spin_us = now;

    if (resync) {
        /* The only recovery gesture in the product: send regardless of what
         * the device believes, because the belief is what is wrong. */
        send_toggle("resync spin");
        return;
    }
    if (dir > 0 && !s_believed_on) {
        send_toggle("spin right");
    } else if (dir < 0 && s_believed_on) {
        send_toggle("spin left");
    } else {
        /* Idempotent by design. Spinning right when it is already believed on
         * does nothing, which is the whole reason for using direction rather
         * than a plain toggle. */
        ESP_LOGI(TAG, "spin %s ignored - already believed %s",
                 (dir > 0) ? "right" : "left", s_believed_on ? "on" : "off");
        shell_haptic_firm();
    }
}

static void wispr_on_dial(int delta)
{
    const int64_t now = esp_timer_get_time();

    /* Detents further apart than the gap are not one gesture. Without this a
     * slow drift over a minute would eventually add up to a spin. */
    if (now - s_last_detent_us > (int64_t) SPIN_GAP_MS * 1000) {
        s_accum = 0;
    }
    s_last_detent_us = now;

    /* A reversal starts a new count rather than cancelling out, so
     * right-right-left-left-left still reads as a left spin. */
    if ((s_accum > 0 && delta < 0) || (s_accum < 0 && delta > 0)) {
        s_accum = 0;
    }
    s_accum += delta;

    if (s_accum >= SPIN_DETENTS) {
        s_accum = 0;
        spin(+1);
    } else if (s_accum <= -SPIN_DETENTS) {
        s_accum = 0;
        spin(-1);
    }
}

/* Tap is the fast path when you are already looking at the screen: it always
 * sends, because you can see the state you are asking to change. The shell
 * owns the long-press on this same screen and LVGL sends CLICKED on release
 * either way, so the long-press has to be swallowed here - otherwise letting
 * go of one would toggle dictation underneath the selector. */
static void screen_click_cb(lv_event_t *e)
{
    const lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_LONG_PRESSED) {
        s_swallow_click = true;
        return;
    }
    if (s_swallow_click) {
        s_swallow_click = false;
        return;
    }
    send_toggle("tap");
}

/* --- lifecycle ---------------------------------------------------------- */

static void wispr_on_enter(lv_obj_t *parent)
{
    lv_obj_set_style_bg_color(parent, lv_color_hex(COL_GROUND), 0);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_LONG_PRESSED, NULL);

    s_accum = 0;
    s_last_detent_us = 0;
    s_last_spin_dir = 0;
    s_last_spin_us = 0;
    s_swallow_click = false;

    /* The rim ring. A full circle either way: this is a state, not a
     * quantity, so it never shows a proportion. */
    s_arc = lv_arc_create(parent);
    lv_obj_set_size(s_arc, 344, 344);
    lv_obj_center(s_arc);
    lv_obj_remove_style(s_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_arc_set_bg_angles(s_arc, 0, 360);
    lv_arc_set_angles(s_arc, 0, 360);
    lv_obj_set_style_arc_width(s_arc, 5, LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_arc, 0, LV_PART_INDICATOR);
    lv_obj_set_style_arc_opa(s_arc, LV_OPA_TRANSP, LV_PART_INDICATOR);

    /* The mic, drawn from three primitives rather than carried as an asset.
     * rev W's glyph is a 60 px stroke drawing and this is what it is made of:
     * a capsule, the arc under it, and the stand. */
    lv_obj_t *mic = lv_obj_create(parent);
    lv_obj_remove_style_all(mic);
    lv_obj_set_size(mic, 60, 60);
    lv_obj_align(mic, LV_ALIGN_CENTER, 0, -38);
    lv_obj_remove_flag(mic, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

    s_mic_body = lv_obj_create(mic);
    lv_obj_remove_style_all(s_mic_body);
    lv_obj_set_size(s_mic_body, 16, 28);
    lv_obj_align(s_mic_body, LV_ALIGN_CENTER, 0, -8);
    lv_obj_remove_flag(s_mic_body, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_radius(s_mic_body, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_opa(s_mic_body, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(s_mic_body, 4, 0);
    lv_obj_set_style_border_opa(s_mic_body, LV_OPA_COVER, 0);

    s_mic_arc = lv_arc_create(mic);
    lv_obj_set_size(s_mic_arc, 28, 28);
    lv_obj_align(s_mic_arc, LV_ALIGN_CENTER, 0, -4);
    lv_obj_remove_style(s_mic_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_mic_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_arc_set_bg_angles(s_mic_arc, 0, 180);      /* LVGL 0 deg is 3 o'clock */
    lv_arc_set_angles(s_mic_arc, 0, 180);
    lv_obj_set_style_arc_width(s_mic_arc, 4, LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_mic_arc, 0, LV_PART_INDICATOR);
    lv_obj_set_style_arc_opa(s_mic_arc, LV_OPA_TRANSP, LV_PART_INDICATOR);

    s_mic_stand = lv_obj_create(mic);
    lv_obj_remove_style_all(s_mic_stand);
    lv_obj_set_size(s_mic_stand, 4, 9);
    lv_obj_align(s_mic_stand, LV_ALIGN_CENTER, 0, 16);
    lv_obj_remove_flag(s_mic_stand, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_opa(s_mic_stand, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_mic_stand, 2, 0);

    /* Sizes are a step or two above rev W's pixel figures, the same
     * correction Waves 5 and 6 had to make: those figures were read off a
     * monitor showing the panel at roughly twice life size, and everything
     * carried across straight was unreadable at 46 mm. */
    s_state_label = lv_label_create(parent);
    lv_obj_set_style_text_font(s_state_label, &lv_font_montserrat_28, 0);
    lv_obj_align(s_state_label, LV_ALIGN_CENTER, 0, 48);

    s_hint_label = lv_label_create(parent);
    lv_obj_set_style_text_font(s_hint_label, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_hint_label, lv_color_hex(0x6E7278), 0);
    lv_label_set_text(s_hint_label, "SPIN RIGHT TO START");
    lv_obj_align(s_hint_label, LV_ALIGN_CENTER, 0, 108);

    s_elapsed_label = lv_label_create(parent);
    lv_obj_set_style_text_font(s_elapsed_label, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_elapsed_label, lv_color_hex(0x8A8F96), 0);
    lv_label_set_text(s_elapsed_label, "0:00");
    lv_obj_align(s_elapsed_label, LV_ALIGN_CENTER, 0, 100);

    shell_back_button(parent);

    paint();
    elapsed_update();
    s_breathe_timer = lv_timer_create(breathe_cb, BREATHE_STEP_MS, NULL);

    ESP_LOGI(TAG, "entered, believed %s%s", s_believed_on ? "on" : "off",
             hid_is_stub() ? " (HID is the Wave 10 stub)" : "");
}

static void wispr_on_exit(void)
{
    if (s_breathe_timer != NULL) {
        lv_timer_delete(s_breathe_timer);
        s_breathe_timer = NULL;
    }
    /* The shell deletes the screen and every widget on it; this app holds no
     * buffers of its own, so there is nothing else to give back. The belief
     * survives on purpose - leaving the screen does not stop dictation, and
     * pretending otherwise would be the desync it is trying to avoid. */
    s_arc = NULL;
    s_mic_body = s_mic_arc = s_mic_stand = NULL;
    s_state_label = s_hint_label = s_elapsed_label = NULL;
    ESP_LOGI(TAG, "exited, belief kept: %s", s_believed_on ? "on" : "off");
}

static void wispr_on_tick(void)
{
    elapsed_update();
}

/* The breathe invalidates a full-circle arc every 100 ms. Invisible under the
 * menu, and not free. */
static void wispr_on_pause(void)
{
    if (s_breathe_timer != NULL) {
        lv_timer_pause(s_breathe_timer);
    }
}

static void wispr_on_resume(void)
{
    if (s_breathe_timer != NULL) {
        lv_timer_resume(s_breathe_timer);
    }
}

const knob_app_t wispr_app = {
    .name = "Dictation",
    .glyph = LV_SYMBOL_CALL,
    .accent = LV_COLOR_MAKE(0xFF, 0x7A, 0x87),
    .on_enter = wispr_on_enter,
    .on_exit = wispr_on_exit,
    .on_dial = wispr_on_dial,
    .on_tick = wispr_on_tick,
    .on_pause = wispr_on_pause,
    .on_resume = wispr_on_resume,
};
