/*
 * Driver for this board's dial: two SSCM110100 bidirectional detector switches,
 * NOT a quadrature encoder. One line (EC1_A, GPIO8) pulses low-then-high per
 * detent clockwise; the other (EC1_B, GPIO7) per detent anticlockwise. The
 * stock espressif/knob quadrature decoder reads nothing from this scheme -
 * found the hard way at Wave 2 checkpoint D (2026-09-02).
 *
 * Ported from Waveshare's demo (04_Encoder_Test, components/user_encoder_bsp,
 * itself a modified espressif/knob, Apache-2.0). Renamed bidi_knob_* to avoid
 * symbol clashes with espressif__knob, which esp_lvgl_port still links.
 */
#pragma once

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*bidi_knob_cb_t)(void *knob_handle, void *usr_data);
typedef void *bidi_knob_handle_t;

typedef enum {
    BIDI_KNOB_LEFT = 0,   /*!< one detent anticlockwise */
    BIDI_KNOB_RIGHT,      /*!< one detent clockwise */
    BIDI_KNOB_EVENT_MAX,
    BIDI_KNOB_NONE,
} bidi_knob_event_t;

typedef struct {
    uint8_t gpio_encoder_a;   /*!< pulse line for clockwise (EC1_A) */
    uint8_t gpio_encoder_b;   /*!< pulse line for anticlockwise (EC1_B) */
} bidi_knob_config_t;

bidi_knob_handle_t bidi_knob_create(const bidi_knob_config_t *config);
esp_err_t bidi_knob_register_cb(bidi_knob_handle_t handle, bidi_knob_event_t event,
                                bidi_knob_cb_t cb, void *usr_data);
int bidi_knob_get_count_value(bidi_knob_handle_t handle);
esp_err_t bidi_knob_clear_count_value(bidi_knob_handle_t handle);

#ifdef __cplusplus
}
#endif
