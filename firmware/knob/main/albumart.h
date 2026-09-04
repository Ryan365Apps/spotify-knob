/* albumart.h - Wave 5. Fetch, decode and hold the current cover.
 *
 * The pipeline is BUILD.md section 6: pick the smallest image at least 300 px
 * wide, skip the work entirely when the URL has not changed, stream the JPEG
 * into PSRAM, decode 1:1 to 300x300 RGB565, and let the screen upscale it to
 * the 360 px circle. Everything happens on this module's own task - a decode
 * is 80-150 ms of pure CPU on a chip with no JPEG unit, and that cannot sit on
 * the LVGL thread.
 *
 * Two decoded buffers are kept, not one, so a track change can cross-fade from
 * the cover being replaced. They are allocated once at a fixed size and
 * reused. Allocating and freeing 180 KB per track change is how PSRAM
 * fragments and the device dies overnight.
 */
#pragma once

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "lvgl.h"

#ifdef __cplusplus
extern "C" {
#endif

#define ALBUMART_DIM  300      /* Spotify's middle size, and what we ask for */

/* Allocate buffers and start the fetch task. Safe to call repeatedly. */
esp_err_t albumart_start(void);

/* Stop the task and release everything. Called when the Spotify app exits, so
 * an app that is not on screen holds no cover and no connection. */
void albumart_stop(void);

/* Ask for a cover. Returns immediately. A URL equal to the one already shown
 * or already queued does nothing at all, which is the single most valuable
 * optimisation in the pipeline - most polls change nothing. Pass NULL or ""
 * to clear.
 *
 * `small_url` is Spotify's 64 px entry and is fetched *first*, upscaled, and
 * published before the full cover is even requested. On this device's link the
 * full cover measured 779-8981 ms - a 10x swing at the same file size, so the
 * variable is the radio, not the code. The thumbnail is 2-4 KB and lands in a
 * fraction of that, which is what turns "nothing for three seconds" into
 * "blurry immediately, sharp shortly after". Pass NULL to skip that stage. */
void albumart_request(const char *url, const char *small_url);

/* The decoded covers, always ALBUMART_DIM square and RGB565 whatever the
 * source was - a thumbnail is upscaled on decode so nothing downstream has to
 * know which stage it is looking at. NULL when there is none. `prev` is the cover being replaced and stays valid for the length of a
 * cross-fade. Both must be read under albumart_lock(). */
const uint16_t *albumart_front(void);
const uint16_t *albumart_prev(void);

/* Bumps every time a new cover lands. The screen watches this rather than
 * polling the buffers, and starts its fade when it changes. */
uint32_t albumart_generation(void);

/* Average colour of the current cover - what the idle bloom is tinted with, so
 * the whole field shifts with the music. Falls back to the design's warm
 * placeholder when no cover has been decoded. */
lv_color_t albumart_tint(void);

/* Held across a read of the buffers. The fetch task swaps them under the same
 * lock, so a composite can never straddle a swap. */
void albumart_lock(void);
void albumart_unlock(void);

#ifdef __cplusplus
}
#endif
