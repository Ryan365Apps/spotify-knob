/*
 * The app selector: the Galaxy Watch bezel, which is what a round screen and
 * a rotary dial are for.
 *
 * Drawn to docs/SOFTWARE-INTERACTION-CORE.md, whose reference implementation
 * is design/simulator.html:
 *
 *   - one green dot fixed above twelve; the glyph beneath it is the selection
 *   - every other glyph fades with angular distance from the dot
 *   - the ring turns under the dot, never the dot around the ring
 *   - rotation is cumulative: past the last app the ring carries on the same
 *     way, forever. Deriving the angle from the index instead makes the ring
 *     rewind a whole turn at the wrap, which is the bug this comment exists
 *     to prevent
 *   - motion is a critically-damped chase toward the target angle, never a
 *     fixed-duration animation per detent, so it retargets cleanly however
 *     fast the detents arrive
 *
 * It lives on LVGL's top layer rather than owning a screen, so the app
 * underneath is never torn down just because you looked at the ring.
 */
#include <math.h>
#include <stdbool.h>

#include "esp_log.h"

#include "app_shell.h"
#include "selector.h"

static const char *TAG = "selector";

#define RING_RADIUS   126
#define MAX_SLOTS     8
#define CHASE_MS      30
#define CHASE_FACTOR  0.25f      /* fraction of the remaining gap per frame */
#define IDLE_CLOSE_MS 4000

static lv_obj_t  *s_root = NULL;
static lv_obj_t  *s_slots[MAX_SLOTS];
static lv_obj_t  *s_hero_glyph = NULL;
static lv_obj_t  *s_hero_name = NULL;
static lv_obj_t  *s_hero_count = NULL;
static lv_timer_t *s_chase_timer = NULL;
static lv_timer_t *s_idle_timer = NULL;

static int   s_count = 0;
static int   s_sel = 0;
static float s_angle_now = 0.0f;    /* degrees, cumulative */
static float s_angle_target = 0.0f;

static float slot_spacing(void)
{
    return (s_count > 0) ? (360.0f / (float) s_count) : 360.0f;
}

/* Full at the dot, barely there opposite it. The exponent is what keeps the
 * far side of the ring from competing with the selection. */
static lv_opa_t falloff(float angle_deg)
{
    float a = fmodf(angle_deg, 360.0f);
    if (a < 0) {
        a += 360.0f;
    }
    if (a > 180.0f) {
        a = 360.0f - a;
    }
    const float k = powf(1.0f - a / 180.0f, 1.6f);
    return (lv_opa_t)(255.0f * (0.12f + 0.88f * k));
}

static void layout(void)
{
    const float spacing = slot_spacing();
    for (int i = 0; i < s_count; i++) {
        const float deg = (float) i * spacing + s_angle_now;
        const float rad = deg * (float) M_PI / 180.0f;
        lv_obj_align(s_slots[i], LV_ALIGN_CENTER,
                     (int32_t)(RING_RADIUS * sinf(rad)),
                     (int32_t)(-RING_RADIUS * cosf(rad)));
        lv_obj_set_style_text_opa(s_slots[i], falloff(deg), 0);
        lv_obj_set_style_text_color(s_slots[i],
                                    (i == s_sel) ? lv_color_hex(0xEAFFF1) : lv_color_white(), 0);
    }
}

static void hero_update(void)
{
    const knob_app_t *app = shell_app_at(s_sel);
    lv_label_set_text(s_hero_glyph, (const char *) app->glyph);
    lv_label_set_text(s_hero_name, app->name);
    lv_label_set_text_fmt(s_hero_count, "%d OF %d", s_sel + 1, s_count);
}

static void chase_cb(lv_timer_t *t)
{
    (void) t;
    const float gap = s_angle_target - s_angle_now;
    if (fabsf(gap) < 0.05f) {
        if (s_angle_now == s_angle_target) {
            return;
        }
        s_angle_now = s_angle_target;
    } else {
        s_angle_now += gap * CHASE_FACTOR;
    }
    layout();
}

/* Deleting the selector from inside one of its own event callbacks would free
 * the object LVGL is still dispatching on. Both exits therefore go through
 * lv_async_call, which runs them after the event has finished. */
static void do_close(void *unused)
{
    (void) unused;
    selector_close();
}

static void do_enter(void *index_as_ptr)
{
    const int index = (int)(intptr_t) index_as_ptr;
    selector_close();
    shell_switch_to(index);
}

static void idle_cb(lv_timer_t *t)
{
    (void) t;
    /* LVGL deletes a repeat_count == 1 timer itself the moment this returns.
     * Drop our pointer here or selector_close will free it a second time,
     * which corrupts LVGL's heap and hangs the next allocation - measured on
     * hardware, 2026-09-03, as a task watchdog inside lv_tlsf_free. */
    s_idle_timer = NULL;
    ESP_LOGI(TAG, "idle - returning to the app you came from");
    lv_async_call(do_close, NULL);
}

static void poke_idle(void)
{
    if (s_idle_timer != NULL) {
        lv_timer_reset(s_idle_timer);
    }
}

static void ground_cb(lv_event_t *e)
{
    const lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_CLICKED) {
        lv_async_call(do_enter, (void *)(intptr_t) s_sel);
    } else if (code == LV_EVENT_LONG_PRESSED) {
        lv_async_call(do_close, NULL);
    }
}

static void slot_cb(lv_event_t *e)
{
    /* Tap a glyph and you enter that app directly, wherever it sits on the
     * ring - you should not have to dial to something you can already see. */
    const int index = (int)(intptr_t) lv_event_get_user_data(e);
    lv_async_call(do_enter, (void *)(intptr_t) index);
}

static void back_cb(lv_event_t *e)
{
    (void) e;
    lv_async_call(do_close, NULL);
}

bool selector_is_open(void)
{
    return s_root != NULL;
}

void selector_open(void)
{
    if (s_root != NULL) {
        return;
    }
    s_count = shell_app_count();
    if (s_count > MAX_SLOTS) {
        s_count = MAX_SLOTS;
    }
    s_sel = shell_app_active_index();
    s_angle_now = s_angle_target = -(float) s_sel * slot_spacing();

    s_root = lv_obj_create(lv_layer_top());
    lv_obj_remove_style_all(s_root);
    lv_obj_set_size(s_root, 360, 360);
    lv_obj_center(s_root);
    lv_obj_remove_flag(s_root, LV_OBJ_FLAG_SCROLLABLE);
    /* Plain ground: the shell is chrome, not an app, and should not look like
     * one. */
    lv_obj_set_style_bg_color(s_root, lv_color_hex(0x0A0B0D), 0);
    lv_obj_set_style_bg_opa(s_root, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_root, LV_RADIUS_CIRCLE, 0);
    lv_obj_add_flag(s_root, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(s_root, ground_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_add_event_cb(s_root, ground_cb, LV_EVENT_LONG_PRESSED, NULL);

    /* The dot: one mark, one meaning. No arc, no ticks. */
    lv_obj_t *dot = lv_obj_create(s_root);
    lv_obj_remove_style_all(dot);
    lv_obj_set_size(dot, 9, 9);
    lv_obj_align(dot, LV_ALIGN_CENTER, 0, -160);
    lv_obj_remove_flag(dot, LV_OBJ_FLAG_CLICKABLE);   /* the ground's tap must pass */
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(dot, lv_color_hex(0x3FE07A), 0);
    lv_obj_set_style_bg_opa(dot, LV_OPA_COVER, 0);

    for (int i = 0; i < s_count; i++) {
        s_slots[i] = lv_label_create(s_root);
        lv_obj_set_style_text_font(s_slots[i], &lv_font_montserrat_20, 0);
        lv_label_set_text(s_slots[i], (const char *) shell_app_at(i)->glyph);
        lv_obj_add_flag(s_slots[i], LV_OBJ_FLAG_CLICKABLE);
        lv_obj_add_event_cb(s_slots[i], slot_cb, LV_EVENT_CLICKED, (void *)(intptr_t) i);
    }

    s_hero_glyph = lv_label_create(s_root);
    lv_obj_set_style_text_font(s_hero_glyph, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(s_hero_glyph, lv_color_hex(0xEAFFF1), 0);
    lv_obj_align(s_hero_glyph, LV_ALIGN_CENTER, 0, -34);

    s_hero_name = lv_label_create(s_root);
    lv_obj_set_style_text_font(s_hero_name, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_hero_name, lv_color_white(), 0);
    lv_obj_align(s_hero_name, LV_ALIGN_CENTER, 0, 14);

    s_hero_count = lv_label_create(s_root);
    lv_obj_set_style_text_color(s_hero_count, lv_color_hex(0x57606E), 0);
    lv_obj_align(s_hero_count, LV_ALIGN_CENTER, 0, 44);

    /* Back is visible: a gesture nobody can see is not an exit. */
    lv_obj_t *back = lv_label_create(s_root);
    lv_obj_set_style_text_font(back, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(back, lv_color_hex(0x5C6068), 0);
    lv_label_set_text(back, LV_SYMBOL_LEFT);
    lv_obj_align(back, LV_ALIGN_CENTER, 0, 138);
    lv_obj_add_flag(back, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_ext_click_area(back, 40);
    lv_obj_add_event_cb(back, back_cb, LV_EVENT_CLICKED, NULL);

    hero_update();
    layout();

    s_chase_timer = lv_timer_create(chase_cb, CHASE_MS, NULL);
    s_idle_timer = lv_timer_create(idle_cb, IDLE_CLOSE_MS, NULL);
    lv_timer_set_repeat_count(s_idle_timer, 1);
    ESP_LOGI(TAG, "open, %d apps", s_count);
}

void selector_close(void)
{
    if (s_root == NULL) {
        return;
    }
    lv_timer_delete(s_chase_timer);
    s_chase_timer = NULL;
    if (s_idle_timer != NULL) {
        lv_timer_delete(s_idle_timer);
        s_idle_timer = NULL;
    }
    lv_obj_delete(s_root);
    s_root = NULL;
    s_hero_glyph = s_hero_name = s_hero_count = NULL;
    ESP_LOGI(TAG, "closed");
}

void selector_dial(int delta)
{
    if (s_root == NULL) {
        return;
    }
    /* A ring has no ends: the index wraps and the angle carries on. */
    s_sel = (s_sel + delta) % s_count;
    if (s_sel < 0) {
        s_sel += s_count;
    }
    s_angle_target -= (float) delta * slot_spacing();
    hero_update();
    poke_idle();
}
