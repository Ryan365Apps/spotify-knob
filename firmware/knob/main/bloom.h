/* bloom.h - the phyllotaxis field, shared by every screen that draws one.
 *
 * One packing, three lightings. `design/screens.html` rev W states the
 * geometry once and then reuses it: the idle/Clock field, the dial wedge for
 * volume and seek, and the outer rim that carries progress on NOW PLAYING are
 * the same 300 segments with different segments lit. Keeping that in one file
 * is the point - if the geometry ever drifts between screens, the screens stop
 * looking like the same instrument, which is the whole idea behind the design.
 *
 * Rendering is straight into an RGB565 canvas buffer, never through
 * lv_draw_line. See bloom.c for why that is not a micro-optimisation.
 */
#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "lvgl.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Canvas the whole family draws into: the full panel, RGB565. */
#define BLOOM_CANVAS_W   360
#define BLOOM_CANVAS_H   360
#define BLOOM_CANVAS_SZ  ((size_t) BLOOM_CANVAS_W * BLOOM_CANVAS_H * 2)

/* 300 segments between r=86 and r=170, per screens.html rev W. */
#define BLOOM_N          300

/* Precompute the packing. Cheap, idempotent, safe to call from every app's
 * on_enter - the second call onwards does nothing. */
void bloom_init(void);

/* The idle field: the Clock's screen, and the idle screen it becomes.
 *
 * `secs` drives three independent motions - a spin of one turn per 600 s, a
 * +/-0.07 deg drift in divergence either side of the golden angle, and a
 * three-lobed swell in segment length rotating through the field every ~34 s.
 * The drift is deliberately tiny; see bloom.c.
 *
 * Clears the buffer first. `tint` comes from the last decoded cover.
 */
void bloom_draw_idle(uint16_t *buf, lv_color_t tint, float secs);

/* The dial wedge: volume and seek.
 *
 * Segments light by *angle*, so a wedge opens clockwise from twelve through an
 * otherwise unordered field. `pct` is 0..1. `lit` is the value colour - green
 * for volume, amber for seek, white for the progress rim.
 *
 * `band` keeps only segments at or beyond that fraction of the way out (0..1).
 * Pass 0 for the full-field dial screens; pass 0.70 for NOW PLAYING, where
 * only the outer rim is drawn so artwork stays visible inside it.
 *
 * `clear` wipes the buffer first. NOW PLAYING passes false: the album art is
 * already in the buffer and the rim is composited over it.
 */
void bloom_draw_wedge(uint16_t *buf, lv_color_t lit, float pct, float band,
                      bool clear);

/* The boot field: the same 300 segments in white, with a bright head sweeping
 * round them. Shown while connecting, where the point is to say "working" - so
 * unlike the wedge, nothing here encodes a value.
 *
 * Split in two because the dim field never changes and redrawing all 300
 * segments per frame capped the animation at 5 fps, which is 45 degrees of
 * travel per frame and looks like stepping rather than sweeping. Draw the
 * field once into a spare buffer, then each frame copy it and lay only the
 * bright head over the top. */
void bloom_spinner_field(uint16_t *buf);
void bloom_spinner_head(uint16_t *buf, float secs);

/* The chip that rides the lit boundary on NOW PLAYING - a short bright stub at
 * exactly the progress angle, so the eye has a definite mark to read even
 * though the wedge's edge is deliberately ragged. */
void bloom_draw_chip(uint16_t *buf, lv_color_t colour, float pct);

/* Diagnostics from the last draw: pixels touched, and the brightest pixel
 * actually written. The second one earns its keep - a bloom can be
 * geometrically perfect and still invisible on the panel, which is exactly
 * what happened on 2026-09-03. */
int      bloom_last_px_written(void);
uint16_t bloom_last_px_max(void);

#ifdef __cplusplus
}
#endif
