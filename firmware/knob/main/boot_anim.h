/*
 * The boot sequence: three blinks, a long wait, then a pulse.
 *
 * Drawn to design/boot-sequence.html. That document is authored for **the 60**
 * — 1080 × 1080, 2 600 points, an ESP32-P4-class fill rate — so what is here
 * is the same sequence at this panel's scale. The timeline is unchanged to the
 * millisecond, because the timing *is* the design; the point count is not,
 * because 2 600 additive points at 360 × 360 would be roughly 40 ms a frame on
 * a board where the Clock's 300-segment bloom already measures 27 ms.
 *
 * The design's own cost table anticipates exactly this, and its key structural
 * claim is what makes the translation cheap: everything after the run is
 * rotationally symmetric, so the whole sequence is one loop over one point
 * field with brightness as a function of radius and absolute time. There is no
 * phase machine. The phase names are a reading aid.
 *
 * It runs while the shell is bringing up Wi-Fi and the token, and the
 * heartbeat holds for as long as that takes — which is the one thing a baked
 * frame sequence could not do, and the reason the heartbeat exists.
 */
#pragma once

#include <stdbool.h>

#include "lvgl.h"

/* Build the canvas on `parent` and start the sequence. */
void boot_anim_start(lv_obj_t *parent);

/* True once the sequence has reached the heartbeat, which is the point after
 * which it is willing to be interrupted. Before that it is still saying
 * something; after it, it is only marking time. */
bool boot_anim_at_heartbeat(void);

/* Seconds since the sequence started. The shell uses it for its own patience
 * limit, so a device with no network still reaches the UI. */
float boot_anim_elapsed(void);

/* True while the sequence owns the screen. Input is swallowed for as long as
 * it is: a boot animation is not a screen you interact with. */
bool boot_anim_running(void);

/* Stop and free the canvas. Safe to call twice. */
void boot_anim_stop(void);
