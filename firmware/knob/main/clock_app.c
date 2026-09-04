/*
 * The Clock app (app 2). The phyllotaxis bloom, the time, and the timer.
 *
 * This app is the contract's real test (BUILD.md section 6): if the Clock
 * cannot be written against knob_app_t without touching shell code, the
 * contract is wrong and a third app will break it too. It reaches the shell
 * only through app_shell.h - haptics and the timer - and touches no network,
 * no token, and nothing Spotify owns.
 *
 * Two screen states, both inside this app's one LVGL screen:
 *
 *   face  - the bloom, the time, and (when set) the timer riding the rim
 *   wind  - turning the dial sets a timer, one detent per minute, 0-60
 *
 * The bloom geometry is the same field the dial overlays use, drawn unlit and
 * drifting: see design/simulator.html, which is the reference implementation.
 */
#include <math.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "albumart.h"
#include "app_shell.h"
#include "bloom.h"

static const char *TAG = "clock";

/* --- the bloom ----------------------------------------------------------
 * The field itself lives in bloom.c now, shared with the Spotify screen's
 * dial wedge and progress rim. Same 300 segments, same packing, different
 * segments lit - which is the argument screens.html rev W makes, and it only
 * holds if there is one implementation rather than three that drift apart.
 *
 * What stays here is the Clock's use of it: 5 fps, tinted by the last cover.
 */
#define CANVAS_W     360
#define CANVAS_H     360
#define BLOOM_MS     200                  /* 5 fps - slower than the eye tracks */

/* --- widgets, owned by this app between on_enter and on_exit ------------- */

static uint8_t   *s_canvas_buf = NULL;
static lv_obj_t  *s_canvas = NULL;
static lv_obj_t  *s_face_group = NULL;
static lv_obj_t  *s_time_label = NULL;
static lv_obj_t  *s_left_label = NULL;    /* remaining time, when a timer runs */
static lv_obj_t  *s_timer_arc = NULL;
static lv_obj_t  *s_wind_group = NULL;
static lv_obj_t  *s_wind_arc = NULL;
static lv_obj_t  *s_wind_value = NULL;
static lv_timer_t *s_bloom_timer = NULL;
static lv_timer_t *s_face_timer = NULL;
static lv_timer_t *s_commit_timer = NULL;

static bool s_winding = false;
static int  s_wind_min = 0;
static int64_t s_entered_us = 0;

/* The tint the bloom is drawn in: the average of the last decoded cover, so
 * the whole field shifts with the music exactly as idle-patterns.html
 * describes. Falls back to the design's warm placeholder before any cover has
 * been decoded, and after an app switch has dropped the last one. */
static lv_color_t s_tint;

static void bloom_render(lv_timer_t *t)
{
    (void) t;
    if (s_canvas == NULL || s_winding) {
        return;   /* the wind screen covers the bloom; do not pay for it */
    }
    const float secs = (float)((esp_timer_get_time() - s_entered_us) / 1000) / 1000.0f;

    const int64_t t0 = esp_timer_get_time();
    bloom_draw_idle((uint16_t *) s_canvas_buf, s_tint, secs);
    lv_obj_invalidate(s_canvas);

    static bool timed = false;
    if (!timed) {
        timed = true;
        ESP_LOGI(TAG, "bloom: %d rays in %lld ms, %d px written, brightest 0x%04X",
                 BLOOM_N, (esp_timer_get_time() - t0) / 1000,
                 bloom_last_px_written(), bloom_last_px_max());
    }
}

/* --- the clock face ------------------------------------------------------ */

static void face_update(lv_timer_t *t)
{
    (void) t;
    if (s_winding) {
        return;
    }

    time_t now = time(NULL);
    struct tm tm_now;
    localtime_r(&now, &tm_now);
    /* Before SNTP lands the year is 1970; say so rather than showing a lie. */
    if (tm_now.tm_year < 100) {
        lv_label_set_text(s_time_label, "--:--");
    } else {
        lv_label_set_text_fmt(s_time_label, "%d:%02d", tm_now.tm_hour, tm_now.tm_min);
    }

    if (shell_timer_running()) {
        const int left_ms = shell_timer_remaining_ms();
        const int total = shell_timer_total_ms();
        lv_obj_remove_flag(s_timer_arc, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_left_label, LV_OBJ_FLAG_HIDDEN);
        lv_arc_set_value(s_timer_arc, total > 0 ? (int32_t)((int64_t) left_ms * 1000 / total) : 0);
        lv_label_set_text_fmt(s_left_label, "%d:%02d", left_ms / 60000, (left_ms / 1000) % 60);
    } else {
        lv_obj_add_flag(s_timer_arc, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(s_left_label, LV_OBJ_FLAG_HIDDEN);
    }
}

/* --- winding a timer ----------------------------------------------------- */

/* The visual half of an end stop: a short kick in the direction the dial was
 * turned, springing back. The haptic is the other half and does most of the
 * work on hardware. */
static void kick_exec(void *obj, int32_t v)
{
    lv_obj_set_style_translate_x((lv_obj_t *) obj, v, 0);
}

static void wind_bump(int dir)
{
    shell_haptic_firm();
    lv_anim_t a;
    lv_anim_init(&a);
    lv_anim_set_var(&a, s_wind_value);
    lv_anim_set_exec_cb(&a, kick_exec);
    lv_anim_set_values(&a, 0, dir > 0 ? 9 : -9);
    lv_anim_set_duration(&a, 70);
    lv_anim_set_playback_duration(&a, 110);
    lv_anim_start(&a);
}

static void wind_show(bool on)
{
    s_winding = on;
    if (on) {
        lv_obj_add_flag(s_face_group, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(s_canvas, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_wind_group, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_add_flag(s_wind_group, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_canvas, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_face_group, LV_OBJ_FLAG_HIDDEN);
        face_update(NULL);
    }
}

/* Two seconds after the last detent the value commits itself. No confirmation
 * step: this is the same rule every dial-set value in the system follows -
 * spin freely, the screen keeps up, one write lands when you stop. */
static void wind_commit(lv_timer_t *t)
{
    (void) t;
    /* LVGL frees a repeat_count == 1 timer as soon as this returns, so the
     * pointer must go now - keep this line. */
    s_commit_timer = NULL;
    if (!s_winding) {
        return;
    }
    shell_timer_set(s_wind_min);
    if (s_wind_min > 0) {
        ESP_LOGI(TAG, "timer set: %d min", s_wind_min);
    } else {
        ESP_LOGI(TAG, "timer cancelled");
    }
    wind_show(false);
}

static void wind_arm_commit(void)
{
    if (s_commit_timer != NULL) {
        lv_timer_reset(s_commit_timer);
        return;
    }
    s_commit_timer = lv_timer_create(wind_commit, 2000, NULL);
    lv_timer_set_repeat_count(s_commit_timer, 1);
}

static void clock_on_dial(int delta)
{
    if (!s_winding) {
        /* The Clock's dial had no job, so the timer takes it. Turning the dial
         * at all enters winding - no menu, no button. An already-running timer
         * seeds the value, so this reads as editing rather than starting over. */
        s_wind_min = shell_timer_running() ? (shell_timer_remaining_ms() + 59999) / 60000 : 0;
        wind_show(true);
    }

    const int before = s_wind_min;
    s_wind_min += delta;
    if (s_wind_min < 0) {
        s_wind_min = 0;
    } else if (s_wind_min > 60) {
        s_wind_min = 60;
    }

    if (s_wind_min == before) {
        wind_bump(delta);          /* clamped: the detent lands on nothing */
    } else {
        lv_label_set_text_fmt(s_wind_value, "%d", s_wind_min);
        lv_arc_set_value(s_wind_arc, s_wind_min);
    }
    wind_arm_commit();
}

/* --- lifecycle ----------------------------------------------------------- */

static void clock_on_enter(lv_obj_t *parent)
{
    s_entered_us = esp_timer_get_time();
    s_winding = false;
    s_tint = albumart_tint();
    bloom_init();

    lv_obj_set_style_bg_color(parent, lv_color_black(), 0);

    /* The bloom's canvas: 259 KB, in PSRAM, allocated here and freed in
     * on_exit. An app that keeps this alive while inactive is what turns
     * "add another app" into a memory problem. */
    s_canvas_buf = heap_caps_malloc(CANVAS_W * CANVAS_H * 2, MALLOC_CAP_SPIRAM);
    assert(s_canvas_buf != NULL);
    s_canvas = lv_canvas_create(parent);
    lv_canvas_set_buffer(s_canvas, s_canvas_buf, CANVAS_W, CANVAS_H, LV_COLOR_FORMAT_RGB565);
    lv_obj_center(s_canvas);
    lv_obj_remove_flag(s_canvas, LV_OBJ_FLAG_CLICKABLE);
    lv_canvas_fill_bg(s_canvas, lv_color_black(), LV_OPA_COVER);

    /* The face: time, the timer's remaining, and the timer's rim arc. */
    s_face_group = lv_obj_create(parent);
    lv_obj_remove_style_all(s_face_group);
    lv_obj_set_size(s_face_group, CANVAS_W, CANVAS_H);
    lv_obj_center(s_face_group);
    /* Every lv_obj is clickable by default. A full-screen container that keeps
     * that flag swallows the long-press before it reaches the screen, and the
     * selector then cannot be opened from this app at all. */
    lv_obj_remove_flag(s_face_group, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

    s_timer_arc = lv_arc_create(s_face_group);
    lv_obj_set_size(s_timer_arc, 352, 352);
    lv_obj_center(s_timer_arc);
    lv_arc_set_rotation(s_timer_arc, 270);
    lv_arc_set_bg_angles(s_timer_arc, 0, 360);
    lv_arc_set_range(s_timer_arc, 0, 1000);
    lv_arc_set_value(s_timer_arc, 0);
    lv_obj_remove_style(s_timer_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_timer_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_arc_width(s_timer_arc, 3, LV_PART_MAIN);
    lv_obj_set_style_arc_opa(s_timer_arc, LV_OPA_TRANSP, LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_timer_arc, 3, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(s_timer_arc, lv_color_white(), LV_PART_INDICATOR);
    lv_obj_add_flag(s_timer_arc, LV_OBJ_FLAG_HIDDEN);

    s_time_label = lv_label_create(s_face_group);
    lv_obj_set_style_text_font(s_time_label, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(s_time_label, lv_color_white(), 0);
    lv_label_set_text(s_time_label, "--:--");
    lv_obj_center(s_time_label);

    s_left_label = lv_label_create(s_face_group);
    lv_obj_set_style_text_color(s_left_label, lv_color_hex(0x8A8F99), 0);
    lv_label_set_text(s_left_label, "");
    lv_obj_align(s_left_label, LV_ALIGN_CENTER, 0, 44);
    lv_obj_add_flag(s_left_label, LV_OBJ_FLAG_HIDDEN);

    /* The wind screen, hidden until the dial moves. */
    s_wind_group = lv_obj_create(parent);
    lv_obj_remove_style_all(s_wind_group);
    lv_obj_set_size(s_wind_group, CANVAS_W, CANVAS_H);
    lv_obj_center(s_wind_group);
    lv_obj_remove_flag(s_wind_group, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_color(s_wind_group, lv_color_hex(0x0A0B0D), 0);
    lv_obj_set_style_bg_opa(s_wind_group, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_wind_group, LV_RADIUS_CIRCLE, 0);
    lv_obj_add_flag(s_wind_group, LV_OBJ_FLAG_HIDDEN);

    /* White, because the colour law gives white to the device's own values -
     * green is volume, amber is seek, red is recording. */
    s_wind_arc = lv_arc_create(s_wind_group);
    lv_obj_set_size(s_wind_arc, 300, 300);
    lv_obj_center(s_wind_arc);
    lv_arc_set_rotation(s_wind_arc, 270);
    lv_arc_set_bg_angles(s_wind_arc, 0, 360);
    lv_arc_set_range(s_wind_arc, 0, 60);
    lv_arc_set_value(s_wind_arc, 0);
    lv_obj_remove_style(s_wind_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_wind_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_arc_width(s_wind_arc, 10, LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_wind_arc, lv_color_hex(0x1C1F24), LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_wind_arc, 10, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(s_wind_arc, lv_color_white(), LV_PART_INDICATOR);

    s_wind_value = lv_label_create(s_wind_group);
    lv_obj_set_style_text_font(s_wind_value, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(s_wind_value, lv_color_white(), 0);
    lv_label_set_text(s_wind_value, "0");
    lv_obj_align(s_wind_value, LV_ALIGN_CENTER, 0, -6);

    lv_obj_t *unit = lv_label_create(s_wind_group);
    lv_obj_set_style_text_color(unit, lv_color_hex(0x8A8F99), 0);
    lv_label_set_text(unit, "min");
    lv_obj_align(unit, LV_ALIGN_CENTER, 0, 30);

    lv_obj_t *title = lv_label_create(s_wind_group);
    lv_obj_set_style_text_color(title, lv_color_hex(0x57606E), 0);
    lv_label_set_text(title, "TIMER");
    lv_obj_align(title, LV_ALIGN_CENTER, 0, -78);

    lv_obj_t *hint = lv_label_create(s_wind_group);
    lv_obj_set_style_text_color(hint, lv_color_hex(0x434B57), 0);
    lv_label_set_text(hint, "ONE DETENT  ONE MINUTE");
    lv_obj_align(hint, LV_ALIGN_CENTER, 0, 96);

    /* The way out. Until 2026-09-04 the only one was a long-press nobody had
     * been told about, which is not an exit. It goes on the face group rather
     * than the screen so the winding overlay covers it. */
    shell_back_button(s_face_group);

    s_bloom_timer = lv_timer_create(bloom_render, BLOOM_MS, NULL);
    s_face_timer = lv_timer_create(face_update, 500, NULL);
    face_update(NULL);
    ESP_LOGI(TAG, "entered");
}

static void clock_on_exit(void)
{
    lv_timer_delete(s_bloom_timer);
    lv_timer_delete(s_face_timer);
    s_bloom_timer = s_face_timer = NULL;
    if (s_commit_timer != NULL) {
        lv_timer_delete(s_commit_timer);
        s_commit_timer = NULL;
    }
    /* Widgets die with the app's screen, which the shell deletes. The canvas
     * buffer does not - it is ours, and this is the line that keeps a third
     * app affordable. */
    s_canvas = s_face_group = s_time_label = s_left_label = s_timer_arc = NULL;
    s_wind_group = s_wind_arc = s_wind_value = NULL;
    heap_caps_free(s_canvas_buf);
    s_canvas_buf = NULL;
    s_winding = false;
    ESP_LOGI(TAG, "exited, canvas freed");
}

static void clock_on_tick(void)
{
    /* The face has its own 500 ms timer; nothing to do at 1 Hz. */
}

/* The bloom is 300 rays and 27 ms of work per render, measured on hardware
 * 2026-09-03. Running that under a menu that is trying to animate a ring at
 * 33 ms a frame is the single worst thing this app could do to it. */
static void clock_on_pause(void)
{
    if (s_bloom_timer != NULL) {
        lv_timer_pause(s_bloom_timer);
    }
    if (s_face_timer != NULL) {
        lv_timer_pause(s_face_timer);
    }
}

static void clock_on_resume(void)
{
    if (s_bloom_timer != NULL) {
        lv_timer_resume(s_bloom_timer);
    }
    if (s_face_timer != NULL) {
        lv_timer_resume(s_face_timer);
        face_update(NULL);       /* the time moved on while we were covered */
    }
}

const knob_app_t clock_app = {
    .name = "Clock",
    .glyph = LV_SYMBOL_BELL,
    .accent = { 0 },
    .on_enter = clock_on_enter,
    .on_exit = clock_on_exit,
    .on_dial = clock_on_dial,
    .on_pause = clock_on_pause,
    .on_resume = clock_on_resume,
    .on_tick = clock_on_tick,
};
