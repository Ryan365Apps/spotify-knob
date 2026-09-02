/*
 * See bidi_knob.h. Decoding logic copied from Waveshare's demo driver
 * (bidi_switch_knob.c, "Modified by planevina 2025-01-20", Apache-2.0),
 * trimmed to one knob instance and renamed. The mechanism: each line is
 * polled every 3 ms; a line sitting low arms a debounce counter, and the
 * return to high after >= 2 armed ticks is one detent on that line.
 */
#include <stdlib.h>

#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "bidi_knob.h"

static const char *TAG = "bidi_knob";

#define TICKS_INTERVAL_MS 3
#define DEBOUNCE_TICKS    2

typedef struct {
    uint8_t gpio_a;
    uint8_t gpio_b;
    uint8_t level_a;
    uint8_t level_b;
    uint8_t debounce_a;
    uint8_t debounce_b;
    int count_value;
    bidi_knob_cb_t cb[BIDI_KNOB_EVENT_MAX];
    void *usr_data[BIDI_KNOB_EVENT_MAX];
} bidi_knob_t;

static bidi_knob_t *s_knob = NULL;
static esp_timer_handle_t s_timer = NULL;

static void process_channel(bidi_knob_t *knob, uint8_t current, uint8_t *prev,
                            uint8_t *debounce, bidi_knob_event_t event, int delta)
{
    if (current == 0) {
        if (current != *prev) {
            *debounce = 0;
        } else {
            (*debounce)++;
        }
    } else {
        if (current != *prev && ++(*debounce) >= DEBOUNCE_TICKS) {
            *debounce = 0;
            knob->count_value += delta;
            if (knob->cb[event]) {
                knob->cb[event](knob, knob->usr_data[event]);
            }
        } else {
            *debounce = 0;
        }
    }
    *prev = current;
}

static void poll_cb(void *arg)
{
    bidi_knob_t *knob = s_knob;
    process_channel(knob, (uint8_t) gpio_get_level(knob->gpio_a), &knob->level_a,
                    &knob->debounce_a, BIDI_KNOB_RIGHT, +1);
    process_channel(knob, (uint8_t) gpio_get_level(knob->gpio_b), &knob->level_b,
                    &knob->debounce_b, BIDI_KNOB_LEFT, -1);
}

bidi_knob_handle_t bidi_knob_create(const bidi_knob_config_t *config)
{
    if (config == NULL || s_knob != NULL) {
        ESP_LOGE(TAG, "bad config or already created");
        return NULL;
    }

    bidi_knob_t *knob = calloc(1, sizeof(bidi_knob_t));
    if (knob == NULL) {
        return NULL;
    }
    knob->gpio_a = config->gpio_encoder_a;
    knob->gpio_b = config->gpio_encoder_b;

    const gpio_config_t io = {
        .pin_bit_mask = (1ULL << knob->gpio_a) | (1ULL << knob->gpio_b),
        .mode = GPIO_MODE_INPUT,
        .intr_type = GPIO_INTR_DISABLE,
        .pull_up_en = 1,
    };
    if (gpio_config(&io) != ESP_OK) {
        free(knob);
        return NULL;
    }

    knob->level_a = (uint8_t) gpio_get_level(knob->gpio_a);
    knob->level_b = (uint8_t) gpio_get_level(knob->gpio_b);
    s_knob = knob;

    const esp_timer_create_args_t timer_args = {
        .callback = poll_cb,
        .dispatch_method = ESP_TIMER_TASK,
        .name = "bidi_knob",
    };
    ESP_ERROR_CHECK(esp_timer_create(&timer_args, &s_timer));
    ESP_ERROR_CHECK(esp_timer_start_periodic(s_timer, TICKS_INTERVAL_MS * 1000U));

    ESP_LOGI(TAG, "bidi knob up, CW line GPIO%d, CCW line GPIO%d",
             knob->gpio_a, knob->gpio_b);
    return (bidi_knob_handle_t) knob;
}

esp_err_t bidi_knob_register_cb(bidi_knob_handle_t handle, bidi_knob_event_t event,
                                bidi_knob_cb_t cb, void *usr_data)
{
    if (handle == NULL || event >= BIDI_KNOB_EVENT_MAX) {
        return ESP_ERR_INVALID_ARG;
    }
    bidi_knob_t *knob = handle;
    knob->cb[event] = cb;
    knob->usr_data[event] = usr_data;
    return ESP_OK;
}

int bidi_knob_get_count_value(bidi_knob_handle_t handle)
{
    return handle ? ((bidi_knob_t *) handle)->count_value : 0;
}

esp_err_t bidi_knob_clear_count_value(bidi_knob_handle_t handle)
{
    if (handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    ((bidi_knob_t *) handle)->count_value = 0;
    return ESP_OK;
}
