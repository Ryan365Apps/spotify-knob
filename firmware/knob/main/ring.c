/*
 * The ring, extracted from selector.c on 2026-09-04 so the Launcher does not
 * become a third copy. See ring.h for the mechanics and why each one is the
 * way it is.
 */
#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "esp_log.h"
#include "esp_timer.h"

#include "ring.h"

static const char *TAG = "ring";

#define RING_RADIUS   126

/*
 * The chase, and why it is a fraction rather than a clock.
 *
 * Everything below is the Settings ring's mechanic, copied across on
 * 2026-09-04 after three wrong diagnoses of why the menu felt jerky and
 * Settings did not. The instruction was the right one: stop explaining the
 * difference and remove it.
 *
 * The difference that mattered is this one. A timed ease interpolates against
 * esp_timer_get_time(), so the position it computes depends on the *moment*
 * the callback happens to run - and LVGL timers are not called on a schedule,
 * they are called when lv_timer_handler gets round to them. Anything else on
 * the LVGL thread pushes that moment around, and a time-sampled interpolation
 * turns that jitter directly into uneven spatial steps. A proportional chase
 * advances by a fixed fraction of the remaining gap per call, so it takes an
 * even step whenever it is called and irregular timing costs nothing.
 *
 * 30 ms against a 33 ms refresh: one update per rendered frame.
 */
#define CHASE_MS      30
#define CHASE_FACTOR  0.25f

struct ring_t {
    ring_cfg_t cfg;

    lv_obj_t *root;
    lv_obj_t *slots[RING_MAX_SLOTS];
    lv_obj_t *hero_glyph;
    lv_obj_t *hero_name;
    lv_obj_t *hero_count;

    lv_timer_t *chase_timer;
    lv_timer_t *idle_timer;

    int   sel;
    float angle_now;             /* degrees, cumulative */
    float angle_target;
    bool  hidden;

    int   live_slot;             /* index into s_live, for the async guard */
};

/*
 * An async callback can outlive the ring that queued it: tap a glyph, the pick
 * switches apps, the app's on_exit destroys the ring, and the queued call then
 * runs against freed memory. LVGL lifetime bugs on this project have cost a
 * session before (BUILD.md section 6, the one-shot timer), so the pointer is
 * validated rather than trusted. Two slots is enough: the selector over an
 * app ring is the only case where two exist at once.
 */
#define RING_MAX_LIVE 2
static ring_t *s_live[RING_MAX_LIVE];

/* Packed into the void* an async call carries: which live slot, and the item
 * index it refers to. */
#define PACK(slot, idx)  ((void *)(intptr_t)(((slot) << 8) | ((idx) & 0xFF)))
#define UNPACK_SLOT(p)   ((int)((intptr_t)(p) >> 8))
#define UNPACK_IDX(p)    ((int)((intptr_t)(p) & 0xFF))

static ring_t *live_or_null(int slot)
{
    if (slot < 0 || slot >= RING_MAX_LIVE) {
        return NULL;
    }
    return s_live[slot];
}

static float slot_spacing(const ring_t *r)
{
    return (r->cfg.count > 0) ? (360.0f / (float) r->cfg.count) : 360.0f;
}

/* Full at the dot, barely there opposite it. Measured in degrees against a
 * fixed 180, which is the Settings ring's curve unchanged.
 *
 * A slot-based version replaced this on 2026-09-03 to make the fade
 * independent of the item count, and the argument for that still holds on
 * paper - with three items a neighbour sat 120 degrees out and nearly
 * vanished. It is back to degrees because the instruction was to make the two
 * rings identical rather than to keep explaining why they differ, and Settings
 * is the one that is right on glass. Revisit only if a ring ever holds three
 * items again; nothing does. */
static lv_opa_t falloff(const ring_t *r, float angle_deg)
{
    (void) r;
    float a = fmodf(angle_deg, 360.0f);
    if (a < 0) {
        a += 360.0f;
    }
    if (a > 180.0f) {
        a = 360.0f - a;
    }
    return (lv_opa_t)(255.0f * (0.12f + 0.88f * powf(1.0f - a / 180.0f, 1.6f)));
}

/* Position and fade every glyph at the current angle. Called from the chase,
 * and separately on entry - a settled ring never enters the chase, and a
 * layout that only happens inside the animation leaves everything stacked in
 * the middle. */
static void layout(ring_t *r)
{
    const float spacing = slot_spacing(r);
    for (int i = 0; i < r->cfg.count; i++) {
        const float deg = (float) i * spacing + r->angle_now;
        const float rad = deg * (float) M_PI / 180.0f;
        lv_obj_align(r->slots[i], LV_ALIGN_CENTER,
                     (int32_t)(RING_RADIUS * sinf(rad)),
                     (int32_t)(-RING_RADIUS * cosf(rad)));
        lv_obj_set_style_text_opa(r->slots[i], falloff(r, deg), 0);
    }
}

/* The selected glyph is a shade warmer than the rest. Set only when the
 * selection actually moves, never per frame: every lv_obj_set_style_* call
 * invalidates the object whether or not the value changed, and doing this
 * inside layout() was six extra full-object invalidations per frame that the
 * Settings ring has never paid. */
static void recolour(ring_t *r)
{
    for (int i = 0; i < r->cfg.count; i++) {
        lv_obj_set_style_text_color(r->slots[i],
                                    (i == r->sel) ? lv_color_hex(0xEAFFF1)
                                                  : lv_color_white(), 0);
    }
}

static void hero_update(ring_t *r)
{
    lv_label_set_text(r->hero_glyph, r->cfg.glyph_at(r->sel));
    lv_label_set_text(r->hero_name, r->cfg.name_at(r->sel));
    if (r->hero_count != NULL) {
        lv_label_set_text_fmt(r->hero_count, "%d OF %d", r->sel + 1, r->cfg.count);
    }
}

static void chase_cb(lv_timer_t *t)
{
    ring_t *r = lv_timer_get_user_data(t);
    if (r == NULL || r->hidden) {
        return;
    }
    const float gap = r->angle_target - r->angle_now;
    if (fabsf(gap) < 0.05f) {
        if (r->angle_now == r->angle_target) {
            return;              /* settled; nothing to animate */
        }
        r->angle_now = r->angle_target;
    } else {
        r->angle_now += gap * CHASE_FACTOR;
    }
    layout(r);
}

static void async_pick(void *packed)
{
    ring_t *r = live_or_null(UNPACK_SLOT(packed));
    if (r != NULL && r->cfg.on_pick != NULL) {
        r->cfg.on_pick(UNPACK_IDX(packed));
    }
}

static void async_back(void *packed)
{
    ring_t *r = live_or_null(UNPACK_SLOT(packed));
    if (r != NULL && r->cfg.on_back != NULL) {
        r->cfg.on_back();
    }
}

static void idle_cb(lv_timer_t *t)
{
    ring_t *r = lv_timer_get_user_data(t);
    if (r == NULL) {
        return;
    }
    /* LVGL deletes a repeat_count == 1 timer itself the moment this returns.
     * Drop the pointer here or ring_destroy frees it a second time, which
     * corrupts LVGL's heap and hangs the next allocation - measured on
     * hardware 2026-09-03 as a task watchdog inside lv_tlsf_free. */
    r->idle_timer = NULL;
    ESP_LOGI(TAG, "idle - backing out");
    lv_async_call(async_back, PACK(r->live_slot, 0));
}

static void poke_idle(ring_t *r)
{
    if (r->idle_timer != NULL) {
        lv_timer_reset(r->idle_timer);
    }
}

static void ground_cb(lv_event_t *e)
{
    ring_t *r = lv_event_get_user_data(e);
    const lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_CLICKED) {
        lv_async_call(async_pick, PACK(r->live_slot, r->sel));
    } else if (code == LV_EVENT_LONG_PRESSED) {
        lv_async_call(async_back, PACK(r->live_slot, 0));
    }
}

/* Tap a glyph and you pick that item wherever it sits on the ring - you should
 * not have to dial to something you can already see. The slot index is packed
 * with the ring's live slot rather than passed as user data, because the
 * callback needs both. */
static void slot_cb(lv_event_t *e)
{
    lv_async_call(async_pick, lv_event_get_user_data(e));
}

/* The centre is the biggest, most obvious thing on the screen and it names
 * what it would open, so it has to be the easiest target. Dialling to
 * something and then hunting for a small rim glyph to confirm it is
 * backwards. */
static void hero_cb(lv_event_t *e)
{
    ring_t *r = lv_event_get_user_data(e);
    lv_async_call(async_pick, PACK(r->live_slot, r->sel));
}

static void back_cb(lv_event_t *e)
{
    ring_t *r = lv_event_get_user_data(e);
    lv_async_call(async_back, PACK(r->live_slot, 0));
}

ring_t *ring_create(lv_obj_t *parent, const ring_cfg_t *cfg)
{
    if (cfg == NULL || cfg->count < 1 || cfg->count > RING_MAX_SLOTS ||
        cfg->glyph_at == NULL || cfg->name_at == NULL) {
        ESP_LOGE(TAG, "bad ring config");
        return NULL;
    }

    int slot = -1;
    for (int i = 0; i < RING_MAX_LIVE; i++) {
        if (s_live[i] == NULL) {
            slot = i;
            break;
        }
    }
    if (slot < 0) {
        ESP_LOGE(TAG, "no free live slot - a ring was not destroyed");
        return NULL;
    }

    ring_t *r = calloc(1, sizeof(ring_t));
    if (r == NULL) {
        ESP_LOGE(TAG, "out of memory");
        return NULL;
    }
    r->cfg = *cfg;
    r->live_slot = slot;
    s_live[slot] = r;

    r->sel = cfg->initial;
    if (r->sel < 0 || r->sel >= cfg->count) {
        r->sel = 0;
    }
    r->angle_now = r->angle_target = -(float) r->sel * slot_spacing(r);

    r->root = lv_obj_create(parent);
    lv_obj_remove_style_all(r->root);
    lv_obj_set_size(r->root, 360, 360);
    lv_obj_center(r->root);
    lv_obj_remove_flag(r->root, LV_OBJ_FLAG_SCROLLABLE);

    if (cfg->own_ground) {
        /* Plain ground: the shell selector is chrome, not an app, and should
         * not look like one. */
        lv_obj_set_style_bg_color(r->root, lv_color_hex(0x0A0B0D), 0);
        lv_obj_set_style_bg_opa(r->root, LV_OPA_COVER, 0);
        /* No radius. The screen is physically round, so a rounded fill buys
         * nothing you can see - and it costs something you can: LVGL treats a
         * background with a radius as not fully covering its rectangle, so it
         * cannot skip drawing the live app screen underneath. A plain fill
         * lets the cover check do its job. */
        lv_obj_add_flag(r->root, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_add_event_cb(r->root, ground_cb, LV_EVENT_CLICKED, r);
        lv_obj_add_event_cb(r->root, ground_cb, LV_EVENT_LONG_PRESSED, r);
    } else {
        /* Transparent to taps and long-presses, so the app screen underneath
         * still opens the selector. */
        lv_obj_remove_flag(r->root, LV_OBJ_FLAG_CLICKABLE);
    }

    /* The dot: one mark, one meaning. No arc, no ticks. */
    lv_obj_t *dot = lv_obj_create(r->root);
    lv_obj_remove_style_all(dot);
    lv_obj_set_size(dot, 9, 9);
    lv_obj_align(dot, LV_ALIGN_CENTER, 0, -160);
    lv_obj_remove_flag(dot, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(dot, cfg->accent, 0);
    lv_obj_set_style_bg_opa(dot, LV_OPA_COVER, 0);

    for (int i = 0; i < cfg->count; i++) {
        r->slots[i] = lv_label_create(r->root);
        lv_obj_set_style_text_font(r->slots[i], &lv_font_montserrat_28, 0);
        lv_label_set_text(r->slots[i], cfg->glyph_at(i));
        lv_obj_add_flag(r->slots[i], LV_OBJ_FLAG_CLICKABLE);
        lv_obj_set_ext_click_area(r->slots[i], 12);
        lv_obj_add_event_cb(r->slots[i], slot_cb, LV_EVENT_CLICKED, PACK(slot, i));
    }

    /* An invisible disc over the middle, so the whole centre is one target
     * rather than three separate labels with gaps between them. */
    lv_obj_t *hero_hit = lv_obj_create(r->root);
    lv_obj_remove_style_all(hero_hit);
    lv_obj_set_size(hero_hit, 168, 168);
    lv_obj_center(hero_hit);
    lv_obj_remove_flag(hero_hit, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_add_flag(hero_hit, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(hero_hit, hero_cb, LV_EVENT_CLICKED, r);

    r->hero_glyph = lv_label_create(r->root);
    lv_obj_set_style_text_font(r->hero_glyph, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(r->hero_glyph, lv_color_hex(0xEAFFF1), 0);
    lv_obj_align(r->hero_glyph, LV_ALIGN_CENTER, 0, -34);

    r->hero_name = lv_label_create(r->root);
    lv_obj_set_style_text_font(r->hero_name, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(r->hero_name, lv_color_white(), 0);
    lv_obj_align(r->hero_name, LV_ALIGN_CENTER, 0, 14);

    if (cfg->show_count) {
        r->hero_count = lv_label_create(r->root);
        lv_obj_set_style_text_font(r->hero_count, &lv_font_montserrat_20, 0);
        lv_obj_set_style_text_color(r->hero_count, lv_color_hex(0x57606E), 0);
        lv_obj_align(r->hero_count, LV_ALIGN_CENTER, 0, 48);
    }

    /* Back is visible: a gesture nobody can see is not an exit. */
    lv_obj_t *back = lv_label_create(r->root);
    lv_obj_set_style_text_font(back, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(back, lv_color_hex(0x5C6068), 0);
    lv_label_set_text(back, LV_SYMBOL_LEFT);
    lv_obj_align(back, LV_ALIGN_CENTER, 0, 138);
    lv_obj_add_flag(back, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_ext_click_area(back, 40);
    lv_obj_add_event_cb(back, back_cb, LV_EVENT_CLICKED, r);

    recolour(r);
    hero_update(r);
    layout(r);

    r->chase_timer = lv_timer_create(chase_cb, CHASE_MS, r);
    if (cfg->idle_close_ms > 0) {
        r->idle_timer = lv_timer_create(idle_cb, cfg->idle_close_ms, r);
        lv_timer_set_repeat_count(r->idle_timer, 1);
    }
    return r;
}

void ring_destroy(ring_t *r)
{
    if (r == NULL) {
        return;
    }
    if (r->chase_timer != NULL) {
        lv_timer_delete(r->chase_timer);
        r->chase_timer = NULL;
    }
    if (r->idle_timer != NULL) {
        lv_timer_delete(r->idle_timer);
        r->idle_timer = NULL;
    }
    if (r->root != NULL) {
        lv_obj_delete(r->root);
        r->root = NULL;
    }
    if (r->live_slot >= 0 && r->live_slot < RING_MAX_LIVE &&
        s_live[r->live_slot] == r) {
        s_live[r->live_slot] = NULL;
    }
    free(r);
}

void ring_dial(ring_t *r, int delta)
{
    if (r == NULL || delta == 0) {
        return;
    }
    /* Reversed 2026-09-04, at Ryan's call after using it: turning the dial
     * clockwise now walks the ring the other way. One negation here rather
     * than at every call site, so the menu, the Launcher and anything else
     * built on this ring can never disagree about which way is forward. */
    delta = -delta;

    /* A ring has no ends: the index wraps and the angle carries on. */
    r->sel = (r->sel + delta) % r->cfg.count;
    if (r->sel < 0) {
        r->sel += r->cfg.count;
    }
    r->angle_target -= (float) delta * slot_spacing(r);

    recolour(r);
    hero_update(r);
    poke_idle(r);
}

int ring_selected(const ring_t *r)
{
    return (r != NULL) ? r->sel : 0;
}

void ring_set_hidden(ring_t *r, bool hidden)
{
    if (r == NULL || r->root == NULL) {
        return;
    }
    r->hidden = hidden;
    if (hidden) {
        lv_obj_add_flag(r->root, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_remove_flag(r->root, LV_OBJ_FLAG_HIDDEN);
    }
}

void ring_refresh(ring_t *r)
{
    if (r == NULL) {
        return;
    }
    for (int i = 0; i < r->cfg.count; i++) {
        lv_label_set_text(r->slots[i], r->cfg.glyph_at(i));
    }
    recolour(r);
    hero_update(r);
    layout(r);
}
