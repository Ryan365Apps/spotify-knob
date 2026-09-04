/*
 * The Settings app (app 3). Not a feature, a consequence: there is no
 * operating system on this device, so every setting a phone gives you for
 * nothing - brightness, sleep, network - either gets implemented here or does
 * not exist (BUILD.md section 6).
 *
 * The same bezel ring as the app selector, one level down: eight items on the
 * rim, the selected one filling the centre with its current value, wrapping
 * continuously. Tapping enters it; tapping again leaves and writes to NVS.
 *
 * The rule this app exists to honour: no setting is ever typed. Each is a
 * value the dial picks from a range or a list.
 */
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#include "esp_log.h"

#include "app_shell.h"
#include "settings_app.h"

static const char *TAG = "settings";

#define RING_RADIUS   126
#define CHASE_MS      30
#define CHASE_FACTOR  0.25f

/* --- the items ----------------------------------------------------------- */

typedef enum {
    ITEM_BRIGHTNESS,      /* a continuous value; the screen is its own preview */
    ITEM_SLEEP,
    ITEM_HAPTICS,
    ITEM_DIAL_STEP,
    ITEM_WIFI,            /* the rest are status: read, never set, on the dial */
    ITEM_SPOTIFY,
    ITEM_DICTATION,
    ITEM_ABOUT,
    ITEM_COUNT
} setting_item_t;

static const char *const ITEM_NAME[ITEM_COUNT] = {
    "Brightness", "Sleep", "Haptics", "Dial step",
    "Wi-Fi", "Spotify", "Dictation", "About"
};

/* LVGL's built-in symbols, so no glyph assets are needed to prove the ring. */
static const char *const ITEM_GLYPH[ITEM_COUNT] = {
    LV_SYMBOL_EYE_OPEN, LV_SYMBOL_POWER, LV_SYMBOL_BELL, LV_SYMBOL_LOOP,
    LV_SYMBOL_WIFI, LV_SYMBOL_AUDIO, LV_SYMBOL_KEYBOARD, LV_SYMBOL_LIST
};

static const int SLEEP_OPTS[] = { 5, 10, 20, 60, 0 };   /* 0 = never */
#define SLEEP_OPT_COUNT (sizeof(SLEEP_OPTS) / sizeof(SLEEP_OPTS[0]))
static const int STEP_OPTS[] = { 2, 5, 10 };
#define STEP_OPT_COUNT (sizeof(STEP_OPTS) / sizeof(STEP_OPTS[0]))
static const char *const HAPTIC_NAMES[] = { "OFF", "LIGHT", "FIRM" };

/* --- widgets ------------------------------------------------------------- */

static lv_obj_t  *s_ring = NULL;
static lv_obj_t  *s_slots[ITEM_COUNT];
static lv_obj_t  *s_hero_glyph = NULL;
static lv_obj_t  *s_hero_name = NULL;
static lv_obj_t  *s_hero_value = NULL;
static lv_obj_t  *s_detail = NULL;      /* the value / status screen */
static lv_obj_t  *s_detail_title = NULL;
static lv_obj_t  *s_detail_value = NULL;
static lv_obj_t  *s_detail_sub = NULL;
static lv_obj_t  *s_detail_arc = NULL;
static lv_timer_t *s_chase_timer = NULL;

static int   s_sel = 0;
static bool  s_in_detail = false;
static float s_angle_now = 0.0f;
static float s_angle_target = 0.0f;

#define SPACING (360.0f / (float) ITEM_COUNT)

/* --- helpers ------------------------------------------------------------- */

static void value_text(int item, char *buf, size_t len)
{
    switch (item) {
        case ITEM_BRIGHTNESS: snprintf(buf, len, "%d%%", shell_brightness()); break;
        case ITEM_SLEEP:
            if (shell_sleep_min() == 0) {
                snprintf(buf, len, "NEVER");
            } else {
                snprintf(buf, len, "%d MIN", shell_sleep_min());
            }
            break;
        case ITEM_HAPTICS:   snprintf(buf, len, "%s", HAPTIC_NAMES[shell_haptics()]); break;
        case ITEM_DIAL_STEP: snprintf(buf, len, "%d%%", shell_dial_step()); break;
        case ITEM_WIFI:      snprintf(buf, len, "%d dBm", shell_wifi_rssi()); break;
        case ITEM_SPOTIFY: {
            const int d = shell_reauth_days();
            if (d < 0) {
                snprintf(buf, len, "--");
            } else {
                snprintf(buf, len, "%d D", d);
            }
            break;
        }
        case ITEM_DICTATION: snprintf(buf, len, "--"); break;   /* BLE is Wave 10 */
        default:             buf[0] = '\0'; break;
    }
}

static lv_opa_t falloff(float angle_deg)
{
    float a = fmodf(angle_deg, 360.0f);
    if (a < 0) {
        a += 360.0f;
    }
    if (a > 180.0f) {
        a = 360.0f - a;
    }
    return (lv_opa_t)(255.0f * (0.12f + 0.88f * powf(1.0f - a / 180.0f, 1.6f)));
}

static void hero_update(void)
{
    char v[24];
    value_text(s_sel, v, sizeof(v));
    lv_label_set_text(s_hero_glyph, ITEM_GLYPH[s_sel]);
    lv_label_set_text(s_hero_name, ITEM_NAME[s_sel]);
    lv_label_set_text(s_hero_value, v);
}

/* Place every glyph on the ring at the current angle and fade it by distance.
 *
 * Split out of the chase timer because that timer returns early once the ring
 * has settled - correct, since there is nothing to animate - but on entry the
 * ring is *already* settled at zero, so it returned before laying anything out
 * at all. Every icon stayed stacked at the centre behind the hero until the
 * first detent moved the dial (found on hardware 2026-09-03). Layout is not
 * animation; it has to happen once whether or not anything is moving. */
static void ring_layout(void)
{
    for (int i = 0; i < ITEM_COUNT; i++) {
        const float deg = (float) i * SPACING + s_angle_now;
        const float rad = deg * (float) M_PI / 180.0f;
        lv_obj_align(s_slots[i], LV_ALIGN_CENTER,
                     (int32_t)(RING_RADIUS * sinf(rad)),
                     (int32_t)(-RING_RADIUS * cosf(rad)));
        lv_obj_set_style_text_opa(s_slots[i], falloff(deg), 0);
    }
}

static void chase_cb(lv_timer_t *t)
{
    (void) t;
    if (s_in_detail) {
        return;
    }
    const float gap = s_angle_target - s_angle_now;
    if (fabsf(gap) < 0.05f) {
        if (s_angle_now == s_angle_target) {
            return;
        }
        s_angle_now = s_angle_target;
    } else {
        s_angle_now += gap * CHASE_FACTOR;
    }
    for (int i = 0; i < ITEM_COUNT; i++) {
        const float deg = (float) i * SPACING + s_angle_now;
        const float rad = deg * (float) M_PI / 180.0f;
        lv_obj_align(s_slots[i], LV_ALIGN_CENTER,
                     (int32_t)(RING_RADIUS * sinf(rad)),
                     (int32_t)(-RING_RADIUS * cosf(rad)));
        lv_obj_set_style_text_opa(s_slots[i], falloff(deg), 0);
    }
}

/* --- the detail screen --------------------------------------------------- */

static void detail_refresh(void)
{
    char v[40];
    lv_label_set_text(s_detail_title, ITEM_NAME[s_sel]);

    switch (s_sel) {
        case ITEM_BRIGHTNESS:
            lv_obj_remove_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            lv_arc_set_range(s_detail_arc, 0, 100);
            lv_arc_set_value(s_detail_arc, shell_brightness());
            lv_label_set_text_fmt(s_detail_value, "%d", shell_brightness());
            lv_label_set_text(s_detail_sub, "%");
            break;
        case ITEM_SLEEP:
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            if (shell_sleep_min() == 0) {
                lv_label_set_text(s_detail_value, "never");
            } else {
                lv_label_set_text_fmt(s_detail_value, "%d", shell_sleep_min());
            }
            lv_label_set_text(s_detail_sub,
                              shell_sleep_min() == 0 ? "5 - 10 - 20 - 60 - never"
                                                     : "minutes");
            break;
        case ITEM_HAPTICS:
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(s_detail_value, HAPTIC_NAMES[shell_haptics()]);
            lv_label_set_text(s_detail_sub, "off - light - firm");
            break;
        case ITEM_DIAL_STEP:
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text_fmt(s_detail_value, "%d%%", shell_dial_step());
            lv_label_set_text(s_detail_sub, "volume per detent");
            break;
        case ITEM_WIFI:
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(s_detail_value, shell_wifi_ssid());
            snprintf(v, sizeof(v), "%d dBm  %s", shell_wifi_rssi(), shell_ip());
            lv_label_set_text(s_detail_sub, v);
            break;
        case ITEM_SPOTIFY: {
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            const int d = shell_reauth_days();
            if (d < 0) {
                lv_label_set_text(s_detail_value, "--");
                lv_label_set_text(s_detail_sub, "clock not set yet");
            } else {
                lv_label_set_text_fmt(s_detail_value, "%d", d);
                lv_label_set_text(s_detail_sub, "days until re-auth");
            }
            break;
        }
        case ITEM_DICTATION:
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(s_detail_value, "not paired");
            lv_label_set_text(s_detail_sub, "BLE keyboard arrives in Wave 10");
            break;
        default:
            lv_obj_add_flag(s_detail_arc, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(s_detail_value, shell_ip());
            snprintf(v, sizeof(v), "up %d min", shell_uptime_s() / 60);
            lv_label_set_text(s_detail_sub, v);
            break;
    }
}

static bool item_is_settable(int item)
{
    return item <= ITEM_DIAL_STEP;
}

/* --- input --------------------------------------------------------------- */

static int index_of(const int *opts, int count, int value)
{
    for (int i = 0; i < count; i++) {
        if (opts[i] == value) {
            return i;
        }
    }
    return 0;
}

static void settings_on_dial(int delta)
{
    if (!s_in_detail) {
        /* Reversed 2026-09-04 to match the menu, at Ryan's call. Only the ring
         * turns the other way - a value editor still goes up when you turn
         * right, because a quantity has a direction of its own and brightness
         * that fell when you turned it up would be nonsense. */
        const int step = -delta;

        /* A ring has no ends. */
        s_sel = (s_sel + step) % ITEM_COUNT;
        if (s_sel < 0) {
            s_sel += ITEM_COUNT;
        }
        s_angle_target -= (float) step * SPACING;
        hero_update();
        return;
    }

    switch (s_sel) {
        case ITEM_BRIGHTNESS: {
            const int before = shell_brightness();
            shell_brightness_set(before + delta * 5);   /* live: it is its own preview */
            if (shell_brightness() == before) {
                shell_haptic_firm();                    /* the 10% floor, and 100% */
            }
            break;
        }
        case ITEM_SLEEP: {
            int i = index_of(SLEEP_OPTS, SLEEP_OPT_COUNT, shell_sleep_min()) + delta;
            if (i < 0 || i >= (int) SLEEP_OPT_COUNT) {
                shell_haptic_firm();                    /* a list has ends */
                return;
            }
            shell_sleep_min_set(SLEEP_OPTS[i]);
            break;
        }
        case ITEM_HAPTICS: {
            const int i = shell_haptics() + delta;
            if (i < 0 || i > 2) {
                shell_haptic_firm();
                return;
            }
            shell_haptics_set(i);
            break;
        }
        case ITEM_DIAL_STEP: {
            int i = index_of(STEP_OPTS, STEP_OPT_COUNT, shell_dial_step()) + delta;
            if (i < 0 || i >= (int) STEP_OPT_COUNT) {
                shell_haptic_firm();
                return;
            }
            shell_dial_step_set(STEP_OPTS[i]);
            break;
        }
        default:
            shell_haptic_firm();     /* status items have nothing to turn */
            return;
    }
    detail_refresh();
}

static void tap_cb(lv_event_t *e)
{
    (void) e;
    if (s_in_detail) {
        s_in_detail = false;
        shell_settings_save();       /* committed on leaving, not per detent */
        lv_obj_add_flag(s_detail, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_ring, LV_OBJ_FLAG_HIDDEN);
        hero_update();
    } else {
        s_in_detail = true;
        detail_refresh();
        lv_obj_add_flag(s_ring, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_detail, LV_OBJ_FLAG_HIDDEN);
        if (!item_is_settable(s_sel)) {
            ESP_LOGI(TAG, "'%s' is status only", ITEM_NAME[s_sel]);
        }
    }
}

/* --- lifecycle ----------------------------------------------------------- */

static void settings_on_enter(lv_obj_t *parent)
{
    s_in_detail = false;
    s_sel = 0;
    s_angle_now = s_angle_target = 0.0f;

    lv_obj_set_style_bg_color(parent, lv_color_hex(0x0A0B0D), 0);

    s_ring = lv_obj_create(parent);
    lv_obj_remove_style_all(s_ring);
    lv_obj_set_size(s_ring, 360, 360);
    lv_obj_center(s_ring);
    lv_obj_remove_flag(s_ring, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);

    lv_obj_t *dot = lv_obj_create(s_ring);
    lv_obj_remove_style_all(dot);
    lv_obj_set_size(dot, 9, 9);
    lv_obj_align(dot, LV_ALIGN_CENTER, 0, -160);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(dot, lv_color_hex(0x3FE07A), 0);
    lv_obj_set_style_bg_opa(dot, LV_OPA_COVER, 0);
    lv_obj_remove_flag(dot, LV_OBJ_FLAG_CLICKABLE);

    for (int i = 0; i < ITEM_COUNT; i++) {
        s_slots[i] = lv_label_create(s_ring);
        lv_obj_set_style_text_font(s_slots[i], &lv_font_montserrat_28, 0);
        lv_obj_set_style_text_color(s_slots[i], lv_color_white(), 0);
        lv_label_set_text(s_slots[i], ITEM_GLYPH[i]);
    }

    s_hero_glyph = lv_label_create(s_ring);
    lv_obj_set_style_text_font(s_hero_glyph, &lv_font_montserrat_36, 0);
    lv_obj_set_style_text_color(s_hero_glyph, lv_color_hex(0xEAFFF1), 0);
    lv_obj_align(s_hero_glyph, LV_ALIGN_CENTER, 0, -40);

    s_hero_name = lv_label_create(s_ring);
    lv_obj_set_style_text_color(s_hero_name, lv_color_hex(0x9EA5B0), 0);
    lv_obj_align(s_hero_name, LV_ALIGN_CENTER, 0, -8);

    /* Name above, value below: you are choosing what to change, so the name
     * leads and the value confirms. */
    s_hero_value = lv_label_create(s_ring);
    lv_obj_set_style_text_font(s_hero_value, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_hero_value, lv_color_hex(0x3FE07A), 0);
    lv_obj_align(s_hero_value, LV_ALIGN_CENTER, 0, 22);

    /* The detail screen, hidden until an item is entered. */
    s_detail = lv_obj_create(parent);
    lv_obj_remove_style_all(s_detail);
    lv_obj_set_size(s_detail, 360, 360);
    lv_obj_center(s_detail);
    lv_obj_remove_flag(s_detail, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_color(s_detail, lv_color_hex(0x0A0B0D), 0);
    lv_obj_set_style_bg_opa(s_detail, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_detail, LV_RADIUS_CIRCLE, 0);
    lv_obj_add_flag(s_detail, LV_OBJ_FLAG_HIDDEN);

    s_detail_arc = lv_arc_create(s_detail);
    lv_obj_set_size(s_detail_arc, 300, 300);
    lv_obj_center(s_detail_arc);
    lv_arc_set_rotation(s_detail_arc, 270);
    lv_arc_set_bg_angles(s_detail_arc, 0, 360);
    lv_obj_remove_style(s_detail_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_detail_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_arc_width(s_detail_arc, 10, LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_detail_arc, lv_color_hex(0x1C1F24), LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_detail_arc, 10, LV_PART_INDICATOR);
    /* White: brightness belongs to the device, and white is the device's own
     * colour - green is volume, amber is seek. */
    lv_obj_set_style_arc_color(s_detail_arc, lv_color_white(), LV_PART_INDICATOR);

    s_detail_title = lv_label_create(s_detail);
    lv_obj_set_style_text_color(s_detail_title, lv_color_hex(0x57606E), 0);
    lv_obj_align(s_detail_title, LV_ALIGN_CENTER, 0, -78);

    s_detail_value = lv_label_create(s_detail);
    lv_obj_set_style_text_font(s_detail_value, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(s_detail_value, lv_color_white(), 0);
    lv_obj_set_width(s_detail_value, 300);
    lv_obj_set_style_text_align(s_detail_value, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(s_detail_value, LV_LABEL_LONG_DOT);
    lv_obj_align(s_detail_value, LV_ALIGN_CENTER, 0, -6);

    s_detail_sub = lv_label_create(s_detail);
    lv_obj_set_style_text_color(s_detail_sub, lv_color_hex(0x8A8F99), 0);
    lv_obj_set_width(s_detail_sub, 300);
    lv_obj_set_style_text_align(s_detail_sub, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(s_detail_sub, LV_LABEL_LONG_DOT);
    lv_obj_align(s_detail_sub, LV_ALIGN_CENTER, 0, 40);

    /* Tap anywhere enters the selected item, or leaves it. The shell's
     * long-press still reaches the screen because nothing here is clickable. */
    lv_obj_add_event_cb(parent, tap_cb, LV_EVENT_CLICKED, NULL);

    hero_update();
    ring_layout();      /* not chase_cb: it returns early on a settled ring */
    s_chase_timer = lv_timer_create(chase_cb, CHASE_MS, NULL);
    ESP_LOGI(TAG, "entered");
}

static void settings_on_exit(void)
{
    lv_timer_delete(s_chase_timer);
    s_chase_timer = NULL;
    shell_settings_save();
    s_ring = s_detail = s_hero_glyph = s_hero_name = s_hero_value = NULL;
    s_detail_title = s_detail_value = s_detail_sub = s_detail_arc = NULL;
    ESP_LOGI(TAG, "exited");
}

static void settings_on_tick(void)
{
    if (s_in_detail && s_sel == ITEM_ABOUT) {
        detail_refresh();     /* uptime ticks while you look at it */
    }
}

const knob_app_t settings_app = {
    .name = "Settings",
    .glyph = LV_SYMBOL_SETTINGS,
    .accent = { 0 },
    .on_enter = settings_on_enter,
    .on_exit = settings_on_exit,
    .on_dial = settings_on_dial,
    .on_tick = settings_on_tick,
};
