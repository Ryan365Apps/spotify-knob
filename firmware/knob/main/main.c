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
#include <stdlib.h>
#include <string.h>

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

#include "cJSON.h"
#include "esp_crt_bundle.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "nvs.h"

#include "app_shell.h"
#include "bidi_knob.h"
#include "lcd_init_waveshare.h"
#include "secrets_local.h"
#include "spotify_app.h"

#include "freertos/semphr.h"

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

/* Wave 3, checkpoint A: NVS-stored credentials and Wi-Fi STA.
 *
 * NVS namespace "radial" holds: wifi_ssid, wifi_pass, client_id,
 * refresh_token, auth_date (BUILD.md section 6). On first boot the keys are
 * seeded from the gitignored secrets_local.h; after that NVS is the truth.
 * Nothing secret is ever logged - log lines say what happened, not the value. */
#define NVS_NAMESPACE "radial"

static void nvs_seed_if_missing(void)
{
    nvs_handle_t h;
    ESP_ERROR_CHECK(nvs_open(NVS_NAMESPACE, NVS_READWRITE, &h));

    if (SECRET_WIFI_SSID[0] == '\0') {
        ESP_LOGE(TAG, "secrets_local.h Wi-Fi fields not filled in");
        nvs_close(h);
        return;
    }

    /* Re-seed whenever the compiled-in secrets differ from NVS, so a fixed
     * password in secrets_local.h actually takes effect on the next flash.
     * (Wave 9 replaces this: NVS becomes the sole truth once provisioning
     * has a real flow.) */
    char cur_ssid[33] = { 0 };
    char cur_pass[65] = { 0 };
    size_t ssid_len = sizeof(cur_ssid);
    size_t pass_len = sizeof(cur_pass);
    nvs_get_str(h, "wifi_ssid", cur_ssid, &ssid_len);
    nvs_get_str(h, "wifi_pass", cur_pass, &pass_len);
    if (strcmp(cur_ssid, SECRET_WIFI_SSID) == 0 && strcmp(cur_pass, SECRET_WIFI_PASS) == 0) {
        nvs_close(h);
        return;  /* NVS already matches the header */
    }
    ESP_ERROR_CHECK(nvs_set_str(h, "wifi_ssid", SECRET_WIFI_SSID));
    ESP_ERROR_CHECK(nvs_set_str(h, "wifi_pass", SECRET_WIFI_PASS));
    ESP_ERROR_CHECK(nvs_set_str(h, "client_id", SECRET_CLIENT_ID));
    ESP_ERROR_CHECK(nvs_set_str(h, "refresh_token", SECRET_REFRESH_TOKEN));
    ESP_ERROR_CHECK(nvs_set_str(h, "auth_date", SECRET_AUTH_DATE));
    ESP_ERROR_CHECK(nvs_commit(h));
    nvs_close(h);
    ESP_LOGI(TAG, "NVS seeded from build secrets");
}

static esp_err_t nvs_get_string(const char *key, char *buf, size_t buf_len)
{
    nvs_handle_t h;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READONLY, &h);
    if (err != ESP_OK) {
        return err;
    }
    err = nvs_get_str(h, key, buf, &buf_len);
    nvs_close(h);
    return err;
}

/* The shell's token module (BUILD.md section 6: token refresh stays in the
 * shell). Refresh on boot, at T+55 min, and on demand via
 * shell_token_refresh_now(); rotate the refresh token into NVS when a new one
 * arrives; a 400 invalid_grant means the token is dead - stop, never retry.
 * Token values are never logged. */
#define SPOTIFY_TOKEN_URL "https://accounts.spotify.com/api/token"

static char s_access_token[512];
static bool s_token_valid = false;
static bool s_auth_dead = false;
static SemaphoreHandle_t s_token_mutex;    /* guards the three fields above */
static SemaphoreHandle_t s_refresh_mutex;  /* serialises concurrent refreshes */

static esp_err_t token_refresh_locked(void)
{
    char refresh[256];
    char client_id[64];
    ESP_ERROR_CHECK(nvs_get_string("refresh_token", refresh, sizeof(refresh)));
    ESP_ERROR_CHECK(nvs_get_string("client_id", client_id, sizeof(client_id)));

    static char body[512];
    snprintf(body, sizeof(body),
             "grant_type=refresh_token&refresh_token=%s&client_id=%s",
             refresh, client_id);

    const esp_http_client_config_t cfg = {
        .url = SPOTIFY_TOKEN_URL,
        .method = HTTP_METHOD_POST,
        .crt_bundle_attach = esp_crt_bundle_attach,
        .timeout_ms = 10000,
    };
    esp_http_client_handle_t client = esp_http_client_init(&cfg);
    if (client == NULL) {
        return ESP_FAIL;
    }
    esp_http_client_set_header(client, "Content-Type", "application/x-www-form-urlencoded");

    esp_err_t err = esp_http_client_open(client, strlen(body));
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "token endpoint unreachable: %s", esp_err_to_name(err));
        esp_http_client_cleanup(client);
        return err;
    }
    esp_http_client_write(client, body, strlen(body));
    esp_http_client_fetch_headers(client);
    const int status = esp_http_client_get_status_code(client);

    static char resp[2048];
    const int len = esp_http_client_read_response(client, resp, sizeof(resp) - 1);
    resp[len > 0 ? len : 0] = '\0';
    esp_http_client_cleanup(client);

    if (status == 400 && strstr(resp, "invalid_grant") != NULL) {
        ESP_LOGE(TAG, "refresh token dead (invalid_grant) - re-auth required, not retrying");
        s_auth_dead = true;
        return ESP_FAIL;
    }
    if (status != 200) {
        ESP_LOGW(TAG, "token refresh failed, HTTP %d (transient, will retry)", status);
        return ESP_FAIL;
    }

    cJSON *root = cJSON_Parse(resp);
    if (root == NULL) {
        ESP_LOGW(TAG, "token response did not parse");
        return ESP_FAIL;
    }
    const cJSON *at = cJSON_GetObjectItem(root, "access_token");
    const cJSON *expires = cJSON_GetObjectItem(root, "expires_in");
    const cJSON *rt = cJSON_GetObjectItem(root, "refresh_token");
    if (!cJSON_IsString(at)) {
        cJSON_Delete(root);
        return ESP_FAIL;
    }
    xSemaphoreTake(s_token_mutex, portMAX_DELAY);
    snprintf(s_access_token, sizeof(s_access_token), "%s", at->valuestring);
    s_token_valid = true;
    xSemaphoreGive(s_token_mutex);

    /* Rotation rule: a new refresh token in the response is written to NVS
     * before anything uses it; absent one, the old token stays. */
    if (cJSON_IsString(rt) && strcmp(rt->valuestring, refresh) != 0) {
        nvs_handle_t h;
        ESP_ERROR_CHECK(nvs_open(NVS_NAMESPACE, NVS_READWRITE, &h));
        ESP_ERROR_CHECK(nvs_set_str(h, "refresh_token", rt->valuestring));
        ESP_ERROR_CHECK(nvs_commit(h));
        nvs_close(h);
        ESP_LOGI(TAG, "refresh token rotated into NVS");
    }
    ESP_LOGI(TAG, "token refreshed, expires_in %d",
             cJSON_IsNumber(expires) ? expires->valueint : -1);
    cJSON_Delete(root);
    return ESP_OK;
}

static esp_err_t token_refresh(void)
{
    xSemaphoreTake(s_refresh_mutex, portMAX_DELAY);
    const esp_err_t err = token_refresh_locked();
    xSemaphoreGive(s_refresh_mutex);
    return err;
}

/* Shell services (app_shell.h). */

esp_err_t shell_token_get(char *buf, size_t buf_len)
{
    esp_err_t err = ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_token_mutex, portMAX_DELAY);
    if (s_token_valid) {
        snprintf(buf, buf_len, "%s", s_access_token);
        err = ESP_OK;
    }
    xSemaphoreGive(s_token_mutex);
    return err;
}

esp_err_t shell_token_refresh_now(void)
{
    return token_refresh();
}

bool shell_auth_dead(void)
{
    return s_auth_dead;
}

void shell_token_corrupt_for_test(void)
{
    xSemaphoreTake(s_token_mutex, portMAX_DELAY);
    snprintf(s_access_token, sizeof(s_access_token), "deliberately-broken");
    xSemaphoreGive(s_token_mutex);
}

/* Refresh on boot (with backoff), then every 55 minutes. */
static void token_task(void *arg)
{
    int backoff_s = 2;
    while (token_refresh() != ESP_OK) {
        if (s_auth_dead) {
            vTaskDelete(NULL);
        }
        vTaskDelay(pdMS_TO_TICKS(backoff_s * 1000));
        if (backoff_s < 60) {
            backoff_s *= 2;
        }
    }
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(55 * 60 * 1000));
        if (token_refresh() != ESP_OK && s_auth_dead) {
            vTaskDelete(NULL);
        }
    }
}


static void wifi_event_cb(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        static int fail_count = 0;
        const wifi_event_sta_disconnected_t *ev = data;
        ESP_LOGW(TAG, "wifi disconnected (reason %d), retrying", ev->reason);
        if (++fail_count == 3) {
            /* Diagnostic: show what the 2.4 GHz radio can actually see. */
            ESP_LOGW(TAG, "three failures - scanning for visible networks");
            esp_wifi_scan_start(NULL, false);
            return;  /* reconnect resumes from SCAN_DONE */
        }
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_SCAN_DONE) {
        /* Static: the event task's stack is small, and this array is ~1.3 KB. */
        static wifi_ap_record_t recs[10];
        uint16_t n = 10;
        if (esp_wifi_scan_get_ap_records(&n, recs) == ESP_OK) {
            for (int i = 0; i < n; i++) {
                ESP_LOGI(TAG, "  seen: '%s' ch%d rssi %d", (const char *) recs[i].ssid,
                         recs[i].primary, recs[i].rssi);
            }
        }
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        static bool token_task_started = false;
        const ip_event_got_ip_t *ev = data;
        ESP_LOGI(TAG, "wifi connected, ip " IPSTR, IP2STR(&ev->ip_info.ip));
        if (!token_task_started) {
            token_task_started = true;
            xTaskCreate(token_task, "token", 8192, NULL, 5, NULL);
        }
    }
}

static void wifi_start(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    const wifi_init_config_t init_cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init_cfg));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_cb, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event_cb, NULL));

    wifi_config_t cfg = { 0 };
    ESP_ERROR_CHECK(nvs_get_string("wifi_ssid", (char *) cfg.sta.ssid, sizeof(cfg.sta.ssid)));
    ESP_ERROR_CHECK(nvs_get_string("wifi_pass", (char *) cfg.sta.password, sizeof(cfg.sta.password)));

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &cfg));
    ESP_ERROR_CHECK(esp_wifi_start());
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

/* The dial (Wave 2). NOT a quadrature encoder - two bidirectional detector
 * switches, one pulse line per direction, read by main/bidi_knob.c (ported
 * from Waveshare's demo). The espressif/knob component stays as a compile-time
 * dependency of esp_lvgl_port only.
 *
 * Shell role (Wave 4): one haptic click per detent, then dispatch the signed
 * delta to the active app. */
static bidi_knob_handle_t s_knob = NULL;
static const knob_app_t *s_active_app = NULL;

static void dial_cb(void *arg, void *usr_data)
{
    const bidi_knob_event_t event = (bidi_knob_event_t)(uintptr_t) usr_data;
    haptic_click();                             /* one click per detent */
    if (s_active_app != NULL && s_active_app->on_dial != NULL) {
        s_active_app->on_dial(event == BIDI_KNOB_RIGHT ? 1 : -1);
    }
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

    /* The encoder and haptics (Wave 2). */
    dial_init();
    haptics_init();

    /* Credentials into NVS, then onto the network (Wave 3). */
    s_token_mutex = xSemaphoreCreateMutex();
    s_refresh_mutex = xSemaphoreCreateMutex();
    assert(s_token_mutex != NULL && s_refresh_mutex != NULL);
    nvs_seed_if_missing();
    wifi_start();

    /* Wave 4: the shell hosts apps behind knob_app_t. One app for now; the
     * selector arrives in Wave 7. The app builds its own screen and frees it
     * on exit; the shell owns the switch. */
    spotify_app_init();
    s_active_app = &spotify_app;
    lvgl_port_lock(0);
    lv_obj_t *app_screen = lv_obj_create(NULL);
    s_active_app->on_enter(app_screen);
    lv_screen_load(app_screen);
    lvgl_port_unlock();
    ESP_LOGI(TAG, "shell up, app '%s' active", s_active_app->name);

    /* ~1 Hz housekeeping tick to the active app. */
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        if (s_active_app != NULL && s_active_app->on_tick != NULL) {
            s_active_app->on_tick();
        }
    }
}
