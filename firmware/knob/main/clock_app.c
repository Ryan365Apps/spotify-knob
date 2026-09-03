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

#include "app_shell.h"

static const char *TAG = "clock";

/* --- the bloom ----------------------------------------------------------
 * 300 rays on a phyllotaxis spiral. r, t and length never change, so they are
 * computed once on_enter; only the angle moves, and it moves in two ways:
 *
 *   spin       a slow rotation of the whole field, one turn per 600 s
 *   divergence a drift of +/-0.07 deg either side of the golden angle
 *
 * The divergence figure is deliberately tiny. Push it further and the packing
 * degenerates into a few thick spokes - avoiding exactly that is what the
 * golden angle is for. The visible motion comes instead from a three-lobed
 * swell in ray length rotating through the field every ~34 s, which cannot
 * degenerate because it does not touch the packing.
 */
#define BLOOM_N      300
#define BLOOM_RI     86.0f
#define BLOOM_RO     170.0f
#define BLOOM_CX     180.0f
#define BLOOM_CY     180.0f
#define GOLDEN_RAD   2.39996323f          /* 137.507764 degrees */
#define DRIFT_RAD    0.00122173f          /* 0.07 degrees */
#define CANVAS_W     360
#define CANVAS_H     360
#define BLOOM_MS     200                  /* 5 fps - slower than the eye tracks */

static float s_ray_r[BLOOM_N];            /* radius of each ray's midpoint */
static float s_ray_t[BLOOM_N];            /* 0 at the inner edge, 1 at the rim */
static float s_ray_len[BLOOM_N];          /* half-length, before the swell */

/* The scatter that gives the field its grain. Deterministic, so the bloom is
 * the same figure on every boot. */
static float ray_hash(int i)
{
    const float v = sinf((float) i * 12.9898f) * 43758.5453f;
    return v - floorf(v);
}

static void bloom_precompute(void)
{
    for (int i = 0; i < BLOOM_N; i++) {
        const float frac = (float) i / (float) BLOOM_N;
        const float r = sqrtf(BLOOM_RI * BLOOM_RI +
                              frac * (BLOOM_RO * BLOOM_RO - BLOOM_RI * BLOOM_RI));
        s_ray_r[i] = r;
        s_ray_t[i] = (r - BLOOM_RI) / (BLOOM_RO - BLOOM_RI);
        s_ray_len[i] = (2.2f + r * 0.045f) * (0.4f + 1.35f * ray_hash(i));
    }
}

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

/* The tint the bloom is drawn in. Wave 5 averages this from the last cover;
 * until then it is the warm default the design uses for placeholder art. */
static lv_color_t s_tint;

/* The rays are drawn straight into the canvas buffer rather than through
 * lv_draw_line.
 *
 * The first attempt used LVGL's line drawing, one call per ray. That
 * machinery - a draw-task dispatch and a blend pass each time - is built for
 * a few shapes per frame, not three hundred into a PSRAM buffer, and it
 * starved the LVGL task so completely that the idle task never ran and the
 * task watchdog fired (measured on hardware, 2026-09-03). A ray is a handful
 * of pixels; writing them directly is both faster and less code.
 */
static int s_px_written;      /* diagnostic: proves the loop reached the buffer */
static uint16_t s_px_max;     /* brightest pixel actually written, RGB565 */

static inline void px_blend(uint16_t *buf, int x, int y,
                            int r5, int g6, int b5, int alpha)
{
    if (x < 0 || x >= CANVAS_W || y < 0 || y >= CANVAS_H) {
        return;
    }
    s_px_written++;
    uint16_t *p = &buf[y * CANVAS_W + x];
    const uint16_t c = *p;
    int dr = (c >> 11) & 0x1F, dg = (c >> 5) & 0x3F, db = c & 0x1F;
    dr += ((r5 - dr) * alpha) >> 8;
    dg += ((g6 - dg) * alpha) >> 8;
    db += ((b5 - db) * alpha) >> 8;
    const uint16_t out = (uint16_t)((dr << 11) | (dg << 5) | db);
    *p = out;
    if (out > s_px_max) {
        s_px_max = out;
    }
}

static void bloom_render(lv_timer_t *t)
{
    (void) t;
    if (s_canvas == NULL || s_winding) {
        return;   /* the wind screen covers the bloom; do not pay for it */
    }
    const float secs = (float)((esp_timer_get_time() - s_entered_us) / 1000) / 1000.0f;
    const float div  = GOLDEN_RAD + DRIFT_RAD * sinf(secs / 240.0f * 2.0f * (float) M_PI);
    const float spin = secs / 600.0f * 2.0f * (float) M_PI;
    const float swell_phase = secs / 34.0f * 2.0f * (float) M_PI;

    const int64_t t0 = esp_timer_get_time();
    uint16_t *buf = (uint16_t *) s_canvas_buf;
    memset(buf, 0, (size_t) CANVAS_W * CANVAS_H * 2);
    s_px_written = 0;
    s_px_max = 0;

    const int r5 = s_tint.red >> 3, g6 = s_tint.green >> 2, b5 = s_tint.blue >> 3;

    for (int i = 0; i < BLOOM_N; i++) {
        const float a = (float) i * div + spin - (float) M_PI_2;
        const float ca = cosf(a), sa = sinf(a);
        const float swell = 0.72f + 0.42f * sinf(3.0f * a + swell_phase);
        const float half = s_ray_len[i] * swell;
        const float cx = BLOOM_CX + ca * s_ray_r[i];
        const float cy = BLOOM_CY + sa * s_ray_r[i];

        /* Rays thin and darken toward the centre: the field has grain rather
         * than regularity, and the rim reads as the edge of something.
         *
         * The simulator's 0.05-0.31 opacity range was set against a bright
         * monitor. On this panel at 40% backlight it came out invisible
         * (2026-09-03) - peak rays landed around RGB(74,28,8). Roughly
         * doubled here, which is a display-calibration difference, not a
         * change of intent. */
        const int alpha = (int)(255.0f * (0.10f + 0.55f * s_ray_t[i] * swell));
        const bool thick = s_ray_t[i] > 0.55f;

        const float x0 = cx - ca * half, y0 = cy - sa * half;
        const float dx = 2.0f * ca * half, dy = 2.0f * sa * half;
        const float adx = fabsf(dx), ady = fabsf(dy);
        const int steps = (int)((adx > ady) ? adx : ady) + 1;
        const float sx = dx / (float) steps, sy = dy / (float) steps;

        float px = x0, py = y0;
        for (int s = 0; s <= steps; s++) {
            const int xi = (int)(px + 0.5f), yi = (int)(py + 0.5f);
            px_blend(buf, xi, yi, r5, g6, b5, alpha);
            if (thick) {
                px_blend(buf, xi + 1, yi, r5, g6, b5, alpha);
            }
            px += sx;
            py += sy;
        }
    }
    lv_obj_invalidate(s_canvas);

    static bool timed = false;
    if (!timed) {
        timed = true;
        ESP_LOGI(TAG, "bloom: %d rays in %lld ms, %d px written, brightest 0x%04X",
                 BLOOM_N, (esp_timer_get_time() - t0) / 1000, s_px_written, s_px_max);
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
    s_tint = lv_color_hex(0xE4572E);
    bloom_precompute();

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

const knob_app_t clock_app = {
    .name = "Clock",
    .glyph = LV_SYMBOL_BELL,
    .accent = { 0 },
    .on_enter = clock_on_enter,
    .on_exit = clock_on_exit,
    .on_dial = clock_on_dial,
    .on_tick = clock_on_tick,
};
