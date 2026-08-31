/*
 * Dial4Spotify - dependency check only.
 *
 * This program deliberately does almost nothing. Its whole job is to prove that
 * every library the real firmware depends on downloads, compiles and links
 * against the installed ESP-IDF - before the hardware arrives.
 *
 * No driver is initialised here. Bring-up belongs in Wave 2, one peripheral at
 * a time, so that a failure points at one thing.
 */

#include <stdio.h>

#include "esp_log.h"
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "nvs_flash.h"

/* Every dependency, included so the compiler has to accept all of them. */
#include "lvgl.h"
#include "esp_lvgl_port.h"
#include "esp_lcd_st77916.h"
#include "esp_lcd_touch_cst816s.h"
#include "iot_knob.h"
#include "jpeg_decoder.h"

/* Verified against the Waveshare schematic, 2026-08-31. See BUILD.md section 3.
 * Unused for now; Wave 2 wires them up. */
#define PIN_LCD_SCLK      13
#define PIN_LCD_CS        14
#define PIN_LCD_D0        15
#define PIN_LCD_D1        16
#define PIN_LCD_D2        17
#define PIN_LCD_D3        18
#define PIN_LCD_RST       21
#define PIN_BACKLIGHT     47

#define PIN_I2C_SDA       11   /* touch AND haptics share this bus */
#define PIN_I2C_SCL       12
#define PIN_TOUCH_INT      9
#define PIN_TOUCH_RST     10

#define PIN_ENCODER_A      8
#define PIN_ENCODER_B      7
/* No encoder button exists on this board. */

static const char *TAG = "dial4spotify";

void app_main(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    ESP_LOGI(TAG, "--- dependency check ---");
    ESP_LOGI(TAG, "LVGL            %d.%d.%d",
             LVGL_VERSION_MAJOR, LVGL_VERSION_MINOR, LVGL_VERSION_PATCH);
    ESP_LOGI(TAG, "IDF             %s", esp_get_idf_version());
    ESP_LOGI(TAG, "internal heap   %u bytes free",
             (unsigned) heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
    ESP_LOGI(TAG, "PSRAM           %u bytes free",
             (unsigned) heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    ESP_LOGI(TAG, "all components resolved and linked");

    /* PSRAM is not optional for this project - say so loudly if it is missing. */
    if (heap_caps_get_free_size(MALLOC_CAP_SPIRAM) == 0) {
        ESP_LOGE(TAG, "no PSRAM detected - check octal mode in menuconfig");
    }
}
