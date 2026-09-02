/*
 * Radial - dependency check only.
 *
 * This program deliberately does almost nothing. Its whole job is to prove that
 * every library the real firmware depends on downloads, compiles and links
 * against the installed ESP-IDF - before the hardware arrives.
 *
 * No driver is initialised here. Bring-up belongs in Wave 2, one peripheral at
 * a time, so that a failure points at one thing.
 */

#include <stdio.h>

#include "driver/i2c_master.h"
#include "driver/ledc.h"
#include "driver/spi_master.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
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

#include "bidi_knob.h"
#include "lcd_init_waveshare.h"

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

/* Wave 2, step B4: prove the firmware can drive the board by lighting the
 * backlight. The panel itself comes in B5. */
static void backlight_init(uint32_t duty_pct)
{
    const ledc_timer_config_t timer = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_10_BIT,      /* 0..1023 */
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = 5000,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&timer));

    const ledc_channel_config_t channel = {
        .gpio_num   = PIN_BACKLIGHT,               /* GPIO47 */
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = (1023 * duty_pct) / 100,
        .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&channel));
    ESP_LOGI(TAG, "backlight on GPIO%d at %lu%%", PIN_BACKLIGHT, (unsigned long) duty_pct);
}

/* Wave 2, step B5: the ST77916 panel over QSPI. 360x360, RGB565. */
#define LCD_HOST   SPI2_HOST
#define LCD_H_RES  360
#define LCD_V_RES  360

static esp_lcd_panel_handle_t panel_init(esp_lcd_panel_io_handle_t *out_io)
{
    const spi_bus_config_t bus_cfg = ST77916_PANEL_BUS_QSPI_CONFIG(
        PIN_LCD_SCLK, PIN_LCD_D0, PIN_LCD_D1, PIN_LCD_D2, PIN_LCD_D3,
        LCD_H_RES * 40 * sizeof(uint16_t));
    ESP_ERROR_CHECK(spi_bus_initialize(LCD_HOST, &bus_cfg, SPI_DMA_CH_AUTO));

    const esp_lcd_panel_io_spi_config_t io_cfg =
        ST77916_PANEL_IO_QSPI_CONFIG(PIN_LCD_CS, NULL, NULL);
    esp_lcd_panel_io_handle_t io = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi(
        (esp_lcd_spi_bus_handle_t)LCD_HOST, &io_cfg, &io));

    st77916_vendor_config_t vendor_cfg = {
        .init_cmds      = waveshare_init_cmds,   /* vendor tuning; without it colours wash out */
        .init_cmds_size = sizeof(waveshare_init_cmds) / sizeof(waveshare_init_cmds[0]),
        .flags = { .use_qspi_interface = 1 },    /* forget this and the panel stays black */
    };
    const esp_lcd_panel_dev_config_t panel_cfg = {
        .reset_gpio_num = PIN_LCD_RST,
        .rgb_ele_order  = LCD_RGB_ELEMENT_ORDER_RGB,
        .bits_per_pixel = 16,
        .vendor_config  = &vendor_cfg,
    };
    esp_lcd_panel_handle_t panel = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_panel_st77916(io, &panel_cfg, &panel));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel, true));
    *out_io = io;
    return panel;
}

/* Wave 2, step C1: LVGL owns the panel from here on. Buffers live in internal
 * DMA-capable RAM, never PSRAM. swap_bytes does the RGB565 byte-order fix that
 * B5's manual test proved necessary. */
static lv_display_t *lvgl_init(esp_lcd_panel_io_handle_t io, esp_lcd_panel_handle_t panel)
{
    const lvgl_port_cfg_t port_cfg = ESP_LVGL_PORT_INIT_CONFIG();
    ESP_ERROR_CHECK(lvgl_port_init(&port_cfg));

    const lvgl_port_display_cfg_t disp_cfg = {
        .io_handle     = io,
        .panel_handle  = panel,
        .buffer_size   = LCD_H_RES * 36,   /* ~1/10 of the screen */
        .double_buffer = true,
        .hres          = LCD_H_RES,
        .vres          = LCD_V_RES,
        .color_format  = LV_COLOR_FORMAT_RGB565,
        .rotation      = { .swap_xy = false, .mirror_x = false, .mirror_y = false },
        .flags         = { .buff_dma = true, .swap_bytes = true },
    };
    lv_display_t *disp = lvgl_port_add_disp(&disp_cfg);
    assert(disp != NULL);
    return disp;
}

/* Wave 2, step C3: touch. One i2c_master bus for the whole board - the DRV2605
 * haptic driver (Checkpoint E) joins THIS handle. Never create a second bus. */
static i2c_master_bus_handle_t i2c_bus = NULL;

static void touch_init(lv_display_t *disp)
{
    const i2c_master_bus_config_t bus_cfg = {
        .i2c_port   = I2C_NUM_0,
        .sda_io_num = PIN_I2C_SDA,
        .scl_io_num = PIN_I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_cfg, &i2c_bus));

    esp_lcd_panel_io_i2c_config_t tp_io_cfg = ESP_LCD_TOUCH_IO_I2C_CST816S_CONFIG();
    tp_io_cfg.scl_speed_hz = 400000;
    esp_lcd_panel_io_handle_t tp_io = NULL;
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(i2c_bus, &tp_io_cfg, &tp_io));

    const esp_lcd_touch_config_t tp_cfg = {
        .x_max = LCD_H_RES,
        .y_max = LCD_V_RES,
        .rst_gpio_num = PIN_TOUCH_RST,
        .int_gpio_num = PIN_TOUCH_INT,
        .levels = {
            .reset = 0,
            .interrupt = 0,
        },
    };
    esp_lcd_touch_handle_t tp = NULL;
    ESP_ERROR_CHECK(esp_lcd_touch_new_i2c_cst816s(tp_io, &tp_cfg, &tp));

    const lvgl_port_touch_cfg_t touch_cfg = {
        .disp   = disp,
        .handle = tp,
    };
    lvgl_port_add_touch(&touch_cfg);
    ESP_LOGI(TAG, "touch registered");
}

/* Wave 2, checkpoint E: DRV2605 haptics. Hand-rolled register writes - no
 * managed component exists for it. Lives on the SAME i2c_master bus handle as
 * touch (section 3: they share the bus); a second handle would break touch.
 * Setup mirrors Waveshare's demo: ERM motor, library 5, internal trigger. */
#define DRV2605_ADDR        0x5A
#define DRV2605_REG_MODE    0x01
#define DRV2605_REG_LIBRARY 0x03
#define DRV2605_REG_WAVESEQ 0x04
#define DRV2605_REG_GO      0x0C

static i2c_master_dev_handle_t s_drv2605 = NULL;

static void drv2605_write(uint8_t reg, uint8_t val)
{
    const uint8_t buf[2] = { reg, val };
    const esp_err_t err = i2c_master_transmit(s_drv2605, buf, sizeof(buf), 100);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "drv2605 write 0x%02X failed: %s", reg, esp_err_to_name(err));
    }
}

static void haptics_init(void)
{
    const i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address  = DRV2605_ADDR,
        .scl_speed_hz    = 400000,
    };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(i2c_bus, &dev_cfg, &s_drv2605));

    drv2605_write(DRV2605_REG_MODE, 0x00);      /* out of standby, internal trigger */
    drv2605_write(DRV2605_REG_LIBRARY, 0x05);   /* ERM library 5, as in the vendor demo */
    ESP_LOGI(TAG, "haptics ready");
}

static void haptic_click(void)
{
    drv2605_write(DRV2605_REG_WAVESEQ, 1);      /* effect 1: strong click, 100% */
    drv2605_write(DRV2605_REG_WAVESEQ + 1, 0);  /* end of sequence */
    drv2605_write(DRV2605_REG_GO, 1);
}

/* Wave 2, steps D2/D3: the dial feeding a counter. The dial is NOT a
 * quadrature encoder - it is two bidirectional detector switches, one pulse
 * line per direction, read by main/bidi_knob.c (ported from Waveshare's demo).
 * The espressif/knob component stays as a compile-time dependency of
 * esp_lvgl_port only. No LVGL indev registration yet - the selector (Wave 7)
 * is the first thing that navigates; raw detent events are under test here. */
static bidi_knob_handle_t s_knob = NULL;
static lv_obj_t *s_count_label = NULL;
static int32_t s_count = 0;

static void dial_cb(void *arg, void *usr_data)
{
    const bidi_knob_event_t event = (bidi_knob_event_t)(uintptr_t) usr_data;
    s_count += (event == BIDI_KNOB_RIGHT) ? 1 : -1;
    haptic_click();                             /* checkpoint E: one click per detent */
    if (lvgl_port_lock(50)) {
        lv_label_set_text_fmt(s_count_label, "%ld", (long) s_count);
        lvgl_port_unlock();
    }
}

/* Checkpoint E's touch-still-works proof, and handy for dial tests: tapping
 * anywhere resets the counter. */
static void screen_tap_cb(lv_event_t *e)
{
    s_count = 0;
    lv_label_set_text(s_count_label, "0");
}

static void dial_init(void)
{
    const bidi_knob_config_t cfg = {
        .gpio_encoder_a = PIN_ENCODER_A,
        .gpio_encoder_b = PIN_ENCODER_B,
    };
    s_knob = bidi_knob_create(&cfg);
    assert(s_knob != NULL);
    ESP_ERROR_CHECK(bidi_knob_register_cb(s_knob, BIDI_KNOB_LEFT, dial_cb,
                                          (void *)(uintptr_t) BIDI_KNOB_LEFT));
    ESP_ERROR_CHECK(bidi_knob_register_cb(s_knob, BIDI_KNOB_RIGHT, dial_cb,
                                          (void *)(uintptr_t) BIDI_KNOB_RIGHT));
    ESP_LOGI(TAG, "encoder registered");
}

void app_main(void)
{
    backlight_init(40);

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

    /* C1: panel up, LVGL on top of it. */
    esp_lcd_panel_io_handle_t io = NULL;
    esp_lcd_panel_handle_t panel = panel_init(&io);
    lv_display_t *disp = lvgl_init(io, panel);
    ESP_LOGI(TAG, "LVGL display registered");

    /* C3: the touch controller on the shared I2C bus. */
    touch_init(disp);

    /* D3: dial test UI - a large number, clockwise +1, anticlockwise -1. */
    lvgl_port_lock(0);
    lv_obj_set_style_bg_color(lv_screen_active(), lv_color_black(), 0);
    s_count_label = lv_label_create(lv_screen_active());
    lv_label_set_text(s_count_label, "0");
    lv_obj_set_style_text_color(s_count_label, lv_color_white(), 0);
    lv_obj_set_style_text_font(s_count_label, &lv_font_montserrat_48, 0);
    lv_obj_center(s_count_label);
    lv_obj_add_flag(lv_screen_active(), LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(lv_screen_active(), screen_tap_cb, LV_EVENT_CLICKED, NULL);
    lvgl_port_unlock();

    /* D2: the encoder. */
    dial_init();

    /* E: haptics on the shared bus. */
    haptics_init();

    /* Stay alive so the monitor has something to talk to. */
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
