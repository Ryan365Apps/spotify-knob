/*
 * The app selector: the Galaxy Watch bezel, which is what a round screen and
 * a rotary dial are for.
 *
 * The ring mechanic itself moved to ring.c on 2026-09-04, when the Launcher
 * would have made it a third implementation. What is left here is the part
 * that is actually about the shell: the ring holds apps, picking one switches
 * to it, and backing out returns you to exactly what you were doing.
 *
 * It lives on LVGL's top layer rather than owning a screen, so the app
 * underneath is never torn down just because you looked at the ring.
 */
#include <stdbool.h>

#include "esp_log.h"

#include "app_shell.h"
#include "ring.h"
#include "selector.h"

static const char *TAG = "selector";

#define IDLE_CLOSE_MS 4000

/*
 * The menu carries one slot that is not an app: Back, always last.
 *
 * It does the same thing as the chevron - close, and return to whatever you
 * were doing - so it is strictly a duplicate affordance, and it earns its
 * place twice over. It is discoverable, where a chevron at the bottom of a
 * ring is a thing you have to be told about. And it is a sixth item on a ring
 * that held five, which is the difference between glyphs 148 px apart and
 * glyphs 126 px apart at this radius. Ryan's read on glass was that five felt
 * like they were fighting for space (2026-09-04); the ring's timing was the
 * larger half of that and is fixed in ring.c, but the spacing is real too.
 */
#define BACK_GLYPH LV_SYMBOL_LEFT
#define BACK_NAME  "Back"

static ring_t *s_ring = NULL;
static int     s_app_count = 0;      /* apps only; the ring holds one more */

static const char *glyph_at(int i)
{
    if (i == s_app_count) {
        return BACK_GLYPH;
    }
    const knob_app_t *app = shell_app_at(i);
    return (app != NULL && app->glyph != NULL) ? (const char *) app->glyph : "?";
}

static const char *name_at(int i)
{
    if (i == s_app_count) {
        return BACK_NAME;
    }
    const knob_app_t *app = shell_app_at(i);
    return (app != NULL) ? app->name : "";
}

/* An app with a shape the symbol font cannot spell draws it itself. The menu
 * only forwards; it has no opinion about what any app looks like. */
static bool draw_glyph(int i, lv_obj_t *into, int px, lv_color_t colour)
{
    if (i == s_app_count) {
        return false;                     /* Back is a font chevron */
    }
    const knob_app_t *app = shell_app_at(i);
    if (app == NULL || app->draw_glyph == NULL) {
        return false;
    }
    app->draw_glyph(into, px, colour);
    return true;
}

static void on_pick(int index)
{
    if (index == s_app_count) {
        /* Back: close and leave the app underneath exactly as it was. The
         * menu never tore it down, so there is nothing to restore. */
        selector_close();
        return;
    }
    selector_close();
    shell_switch_to(index);
}

static void on_back(void)
{
    selector_close();
}

bool selector_is_open(void)
{
    return s_ring != NULL;
}

void selector_open(void)
{
    if (s_ring != NULL) {
        return;
    }
    s_app_count = shell_app_count();
    if (s_app_count > RING_MAX_SLOTS - 1) {
        s_app_count = RING_MAX_SLOTS - 1;   /* one slot is always Back */
    }

    const ring_cfg_t cfg = {
        .count = s_app_count + 1,
        .initial = shell_app_active_index(),
        .glyph_at = glyph_at,
        .name_at = name_at,
        .draw_glyph = draw_glyph,
        .on_pick = on_pick,
        .on_back = on_back,
        .own_ground = true,        /* the selector is chrome and owns its ground */
        .show_count = true,
        .idle_close_ms = IDLE_CLOSE_MS,
        .accent = LV_COLOR_MAKE(0x3F, 0xE0, 0x7A),
    };
    s_ring = ring_create(lv_layer_top(), &cfg);
    if (s_ring == NULL) {
        ESP_LOGE(TAG, "could not build the ring");
        return;
    }
    /* The app underneath is completely covered, so anything it draws from here
     * is thrown away - and on the LVGL thread that waste lands square in the
     * middle of the frames this ring is trying to animate. */
    shell_active_app_set_paused(true);
    ESP_LOGI(TAG, "open, %d apps + Back", s_app_count);
}

void selector_close(void)
{
    if (s_ring == NULL) {
        return;
    }
    ring_destroy(s_ring);
    s_ring = NULL;
    shell_active_app_set_paused(false);
    ESP_LOGI(TAG, "closed");
}

void selector_dial(int delta)
{
    ring_dial(s_ring, delta);
}
