/*
 * The ring: glyphs on the rim, one selected under a fixed dot at twelve, the
 * dial turning the ring beneath the dot.
 *
 * This is the mechanic docs/SOFTWARE-INTERACTION-CORE.md settles and
 * design/simulator.html demonstrates, and by 2026-09-04 it had been written
 * three times - the app selector, the Settings ring, and now the Launcher.
 * Two of those three had already drifted apart, and BUILD.md section 6 records
 * why that matters: every constant in a ring silently depends on how many
 * items it holds, and the two copies had different answers. So it lives here
 * once.
 *
 * The mechanics are the corrected ones, measured on hardware 2026-09-03:
 *
 *   - rotation is cumulative. Past the last item the ring carries on the same
 *     way, forever. Deriving the angle from the index makes it rewind a whole
 *     turn at the wrap
 *   - the fade is by distance in *slots*, never in degrees. Against a fixed
 *     180 degrees a three-item ring looks like it is not turning at all while
 *     an eight-item ring looks right, from identical code
 *   - the slide is a timed ease whose duration scales with the distance, never
 *     a fixed fraction of the remaining gap. A proportional chase settles in
 *     the same number of frames whatever the distance, so its angular speed
 *     scales with the item count
 *   - layout is not animation. The chase returns early when the ring is
 *     settled, and on entry it is always settled, so laying out from the
 *     animation callback leaves every glyph stacked in the centre
 *
 * Two rings can be alive at once: long-pressing inside the Launcher opens the
 * app selector over it. So this is instance-based rather than a module with
 * one set of statics.
 */
#pragma once

#include <stdbool.h>

#include "lvgl.h"

#define RING_MAX_SLOTS 8

typedef struct ring_t ring_t;

typedef struct {
    int count;                     /* 1..RING_MAX_SLOTS                     */
    int initial;                   /* which item to open on                 */

    /* The rim glyph and the centre name for item i. Called whenever the ring
     * lays out or the selection changes, so they must be cheap and must not
     * allocate. */
    const char *(*glyph_at)(int i);
    const char *(*name_at)(int i);

    /* Optional. Draw item i's glyph into `into`, a square container of `px`,
     * in `colour`. Return true if you drew it and the font symbol should not
     * be used. For shapes the symbol font cannot spell - see knob_app_t. */
    bool (*draw_glyph)(int i, lv_obj_t *into, int px, lv_color_t colour);

    /* A tap on the selected item, on its rim glyph, or on the centre. Called
     * through lv_async_call, so it is safe to destroy the ring inside it. */
    void (*on_pick)(int i);

    /* The chevron, the lower band, a long-press on the ring's own ground, or
     * the idle timeout. Same async guarantee. */
    void (*on_back)(void);

    /* True for the shell's app selector: the ring owns a solid ground that
     * takes taps and long-presses for itself.
     *
     * False for a ring inside an app screen, where the ring must stay
     * transparent to both - otherwise the container swallows the long-press
     * and the selector can never open from that app (BUILD.md section 6). */
    bool own_ground;

    bool show_count;               /* the "1 OF 7" line under the name      */
    int  idle_close_ms;            /* 0 = never close on its own            */
    lv_color_t accent;             /* the dot, and the selected glyph        */
} ring_cfg_t;

/* Build the ring inside parent. Returns NULL if the config is out of range or
 * there is no room for another live ring. */
ring_t *ring_create(lv_obj_t *parent, const ring_cfg_t *cfg);

/* Tear it down. Deletes its objects and timers; safe to call twice. */
void ring_destroy(ring_t *r);

/* One detent, signed. Wraps at both ends, because a ring has no ends. */
void ring_dial(ring_t *r, int delta);

int ring_selected(const ring_t *r);

/* Hide the whole ring, glyphs and hit targets together.
 *
 * A layer drawn over the ring is not enough on its own: an overlay that is not
 * itself clickable does not absorb a tap, so the tap reaches whatever is
 * underneath - and underneath is a rim glyph that would pick an item nobody
 * asked for. Hiding is what actually takes the ring out of hit-testing. */
void ring_set_hidden(ring_t *r, bool hidden);

/* Re-read the glyphs and the name for the current state, after the caller has
 * changed what the ring is showing. */
void ring_refresh(ring_t *r);
