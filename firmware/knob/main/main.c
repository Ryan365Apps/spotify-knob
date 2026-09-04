/*
 * Radial - the TorqueOS shell.
 *
 * This file started life as a dependency check and is now the shell described
 * in BUILD.md section 6: it brings up the panel, touch, the dial and haptics,
 * owns Wi-Fi and the Spotify token, owns the clock, the backlight and the
 * sleep timer, and hosts apps behind the knob_app_t contract. Apps own their
 * own screen, their own network calls and their own buffers.
 *
 * Nothing Spotify-specific belongs here except the token module, which is in
 * the shell deliberately - refresh has to keep running while you are looking
 * at the Clock. See the tension recorded under Wave 4 in BUILD.md section 8.
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
#include "clock_app.h"
#include "hid.h"
#include "launcher_app.h"
#include "lcd_init_waveshare.h"
#include "secrets_local.h"
#include "selector.h"
#include "settings_app.h"
#include "spotify_app.h"
#include "wispr_app.h"

#include "esp_netif_sntp.h"
#include "esp_task_wdt.h"
#include "esp_timer.h"
#include "freertos/queue.h"
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

/* The shell's log tag. TorqueOS is the firmware and its companion
 * (docs/SOFTWARE-CONTEXTS.md); the per-app tags below it stay as the app
 * names - "spotify", "clock", "selector". */
static const char *TAG = "torque-os";

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
    /* This is the compiled boot level, not the stored one - NVS is not up yet.
     * The stored brightness is applied by settings_load a few lines into
     * app_main and logged there. Do not read this line as the live value. */
    ESP_LOGI(TAG, "backlight on GPIO%d at %lu%% (boot default, pre-NVS)",
             PIN_BACKLIGHT, (unsigned long) duty_pct);
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

    /* Orientation is set in lvgl_init, in software - see the note there for
     * why the panel's own MADCTL was abandoned. */
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel, true));
    *out_io = io;
    return panel;
}

/* Wave 2, step C1: LVGL owns the panel from here on. Buffers live in internal
 * DMA-capable RAM, never PSRAM. swap_bytes does the RGB565 byte-order fix that
 * B5's manual test proved necessary. */
static lv_display_t *lvgl_init(esp_lcd_panel_io_handle_t io, esp_lcd_panel_handle_t panel)
{
    /* LVGL on core 0, explicitly.
     *
     * The default is no affinity, which left the scheduler free to put the
     * compositor and the JPEG decode on the same core - and it did, while the
     * other one idled. Pinning both, in opposite directions, is what makes the
     * split deterministic rather than a matter of luck: this on 0, the art
     * task on 1 (see albumart.c). */
    lvgl_port_cfg_t port_cfg = ESP_LVGL_PORT_INIT_CONFIG();
    port_cfg.task_affinity = 0;
    ESP_ERROR_CHECK(lvgl_port_init(&port_cfg));

    const lvgl_port_display_cfg_t disp_cfg = {
        .io_handle     = io,
        .panel_handle  = panel,
        /* These live in internal DMA-capable RAM, which is the scarcest thing
         * on this board: at 1/10 of the screen, double-buffered, they were
         * 52 KB, and a TLS handshake then failed to allocate (esp-aes: Failed
         * to allocate memory, 2026-09-03). 1/18 costs a few more flush chunks
         * per frame and gives 23 KB back. */
        .buffer_size   = LCD_H_RES * 20,
        .double_buffer = true,
        .hres          = LCD_H_RES,
        .vres          = LCD_V_RES,
        .color_format  = LV_COLOR_FORMAT_RGB565,
        .rotation      = { .swap_xy = false, .mirror_x = false, .mirror_y = false },
        .flags         = { .buff_dma = true, .swap_bytes = true, .sw_rotate = true },
    };
    lv_display_t *disp = lvgl_port_add_disp(&disp_cfg);
    assert(disp != NULL);

    /* 180 degrees, so the cable points away from you.
     *
     * Done in software, after two attempts at the panel register did nothing.
     * MADCTL 0xC0 - MX and MY - is the textbook way and costs no CPU, and the
     * driver demonstrably transmits it: the vendor table carries the byte and
     * the "36h command has been used" warning proves the code reaches that
     * entry. The panel simply did not turn. Either this module's scan order is
     * fixed in the 0xF0 page registers regardless of MADCTL, or something else
     * is overriding it; either way, two goes at a register that reports
     * success while doing nothing is enough.
     *
     * Software rotation cannot silently no-op. The cost is a reversal of each
     * flush chunk, and those live in internal DMA RAM at 1/18 of the screen -
     * about 7200 pixels per chunk, which is small next to the SPI transfer it
     * is already waiting on. esp_lvgl_port rotates the touch coordinates to
     * match (esp_lvgl_port_disp.c, "Solve rotation screen and touch"), which
     * is why touch_init sets no mirror flags of its own. */
    lvgl_port_lock(0);
    lv_display_set_rotation(disp, LV_DISPLAY_ROTATION_180);
    lvgl_port_unlock();
    ESP_LOGI(TAG, "display rotated 180 degrees (software, cable away from you)");

    return disp;
}

/* Wave 2, step C3: touch. One i2c_master bus for the whole board - the DRV2605
 * haptic driver (Checkpoint E) joins THIS handle. Never create a second bus. */
static i2c_master_bus_handle_t i2c_bus = NULL;

static lv_indev_t *s_touch_indev = NULL;

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
        /* No mirror flags here: esp_lvgl_port rotates touch to match the
         * display rotation itself. Setting them as well would flip twice and
         * land back where it started. */
    };
    esp_lcd_touch_handle_t tp = NULL;
    ESP_ERROR_CHECK(esp_lcd_touch_new_i2c_cst816s(tp_io, &tp_cfg, &tp));

    const lvgl_port_touch_cfg_t touch_cfg = {
        .disp   = disp,
        .handle = tp,
    };
    s_touch_indev = lvgl_port_add_touch(&touch_cfg);
    /* 550 ms is the long-press threshold the interaction core specifies; the
     * LVGL default of 400 ms fires while you are still deciding. */
    lv_indev_set_long_press_time(s_touch_indev, 550);
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


/* Wave 8: reconnect with backoff.
 *
 * The disconnect handler used to call esp_wifi_connect() again immediately,
 * every time. Against a router that is still booting - which is the failure
 * this device is most likely to meet on an ordinary day - that is a flat-out
 * retry loop for as long as the router takes. The first retry stays immediate,
 * because a momentary blip should not cost a second; after that it doubles
 * 1, 2, 4 ... to a 30 s ceiling, and an IP arriving resets it.
 *
 * The retry is scheduled on a one-shot esp_timer rather than slept for,
 * because this handler runs on the system event task. Wave 3 already
 * overflowed that task's stack, and a handler that blocks stalls every other
 * event behind it. */
#define WIFI_BACKOFF_MIN_MS  1000
#define WIFI_BACKOFF_MAX_MS 30000
static esp_timer_handle_t s_wifi_retry_timer = NULL;
static int s_wifi_backoff_ms = 0;
static int s_wifi_fail_count = 0;

/* Bumped on every IP acquisition. An app that has backed off after a network
 * failure watches this so a router coming back does not leave it sitting out
 * the rest of a sixty-second wait it no longer needs. */
static volatile uint32_t s_net_generation = 0;

uint32_t shell_net_generation(void)
{
    return s_net_generation;
}

static void wifi_retry_cb(void *arg)
{
    esp_wifi_connect();
}

static void wifi_retry_schedule(void)
{
    const int delay_ms = s_wifi_backoff_ms;
    s_wifi_backoff_ms = (s_wifi_backoff_ms == 0) ? WIFI_BACKOFF_MIN_MS
                                                 : s_wifi_backoff_ms * 2;
    if (s_wifi_backoff_ms > WIFI_BACKOFF_MAX_MS) {
        s_wifi_backoff_ms = WIFI_BACKOFF_MAX_MS;
    }

    if (s_wifi_retry_timer == NULL) {
        const esp_timer_create_args_t args = {
            .callback = wifi_retry_cb,
            .name = "wifi_retry",
        };
        if (esp_timer_create(&args, &s_wifi_retry_timer) != ESP_OK) {
            /* No timer means no retry at all, which is worse than a flat-out
             * one. Fall back to the old behaviour and say so. */
            ESP_LOGE(TAG, "no wifi retry timer - reconnecting immediately");
            esp_wifi_connect();
            return;
        }
    }
    esp_timer_stop(s_wifi_retry_timer);      /* harmless if it is not running */
    if (esp_timer_start_once(s_wifi_retry_timer, (uint64_t) delay_ms * 1000) != ESP_OK) {
        ESP_LOGE(TAG, "wifi retry timer would not start - reconnecting immediately");
        esp_wifi_connect();
        return;
    }
    ESP_LOGW(TAG, "wifi retry in %d ms", delay_ms);
}

static void wifi_event_cb(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        const wifi_event_sta_disconnected_t *ev = data;
        ESP_LOGW(TAG, "wifi disconnected (reason %d)", ev->reason);
        if (++s_wifi_fail_count % 3 == 0) {
            /* Diagnostic: show what the 2.4 GHz radio can actually see. Every
             * third consecutive failure, not only the third ever - a device
             * that has been up for a month and then loses its router deserves
             * the same diagnostic a fresh one gets. */
            ESP_LOGW(TAG, "%d failures in a row - scanning for visible networks",
                     s_wifi_fail_count);
            esp_wifi_scan_start(NULL, false);
            return;  /* reconnect resumes from SCAN_DONE */
        }
        wifi_retry_schedule();
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
        wifi_retry_schedule();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        static bool token_task_started = false;
        const ip_event_got_ip_t *ev = data;
        ESP_LOGI(TAG, "wifi connected, ip " IPSTR, IP2STR(&ev->ip_info.ip));
        /* Connected, so the next disconnection starts from an immediate retry
         * again rather than from wherever the last outage left the backoff. */
        s_wifi_backoff_ms = 0;
        s_wifi_fail_count = 0;
        s_net_generation++;
        if (!token_task_started) {
            token_task_started = true;
            xTaskCreate(token_task, "token", 8192, NULL, 5, NULL);
            /* The shell owns the clock (BUILD.md section 6), so it owns
             * getting the time right. Without this the Clock app has nothing
             * to show but 1970. */
            esp_sntp_config_t sntp_cfg = ESP_NETIF_SNTP_DEFAULT_CONFIG("pool.ntp.org");
            esp_netif_sntp_init(&sntp_cfg);
            ESP_LOGI(TAG, "SNTP started");
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

/* --- device settings -----------------------------------------------------
 * Held in RAM, applied immediately, written to NVS when a value screen is
 * left. Defaults match BUILD.md section 6. */
static int s_brightness = 40;   /* the working default Wave 2 settled on */
static int s_sleep_min = 20;
static int s_haptics = 2;       /* firm */
static int s_dial_step = 5;
static bool s_settings_dirty = false;

/* A transient scale on top of the brightness setting, 0..256.
 *
 * Apps use this for fades. It deliberately does not touch s_brightness: the
 * value in Settings is what the user chose and an animation has no business
 * overwriting it, nor writing it to NVS. Anything that reads the brightness
 * back still sees their number. */
static int s_dim_scale = 256;

static void backlight_duty(int pct)
{
    const int scaled = (pct * s_dim_scale) >> 8;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, (1023 * scaled) / 100);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

/* Fading the backlight rather than the pixels.
 *
 * Dimming in the framebuffer would mean recompositing the whole screen every
 * frame of the fade - a 259 KB memcpy plus the bloom, at 16 fps, on the task
 * that has already tripped the watchdog twice today. The backlight is a PWM
 * register write. It also fades the text, which pixel dimming would have to
 * handle separately, and it cannot band: an RGB565 fade to black runs out of
 * levels long before it gets there. */
void shell_backlight_scale(int per256)
{
    if (per256 < 0) {
        per256 = 0;
    } else if (per256 > 256) {
        per256 = 256;
    }
    s_dim_scale = per256;
    backlight_duty(s_brightness);
}

int  shell_brightness(void)   { return s_brightness; }
int  shell_sleep_min(void)    { return s_sleep_min; }
int  shell_haptics(void)      { return s_haptics; }
int  shell_dial_step(void)    { return s_dial_step; }

void shell_brightness_set(int pct)
{
    if (pct < 10) {
        pct = 10;      /* floor: the screen must never be turned dark and lost */
    } else if (pct > 100) {
        pct = 100;
    }
    if (pct != s_brightness) {
        s_settings_dirty = true;
    }
    s_brightness = pct;
    backlight_duty(pct);
}

void shell_sleep_min_set(int minutes)
{
    s_settings_dirty |= (minutes != s_sleep_min);
    s_sleep_min = minutes;
}

void shell_haptics_set(int level)
{
    s_settings_dirty |= (level != s_haptics);
    s_haptics = level;
}

void shell_dial_step_set(int pct)
{
    s_settings_dirty |= (pct != s_dial_step);
    s_dial_step = pct;
}

static void settings_load(void)
{
    nvs_handle_t h;
    if (nvs_open(NVS_NAMESPACE, NVS_READONLY, &h) != ESP_OK) {
        return;
    }
    int32_t v;
    if (nvs_get_i32(h, "brightness", &v) == ESP_OK) { s_brightness = (int) v; }
    if (nvs_get_i32(h, "sleep_min", &v) == ESP_OK)  { s_sleep_min = (int) v; }
    if (nvs_get_i32(h, "haptics", &v) == ESP_OK)    { s_haptics = (int) v; }
    if (nvs_get_i32(h, "dial_step", &v) == ESP_OK)  { s_dial_step = (int) v; }
    nvs_close(h);
}

/* Called every time a settings screen is left, which includes leaving status
 * screens where nothing can have changed. Flash endurance should not pay for
 * browsing, so a save with nothing to save costs nothing. */
void shell_settings_save(void)
{
    if (!s_settings_dirty) {
        return;
    }
    s_settings_dirty = false;

    nvs_handle_t h;
    if (nvs_open(NVS_NAMESPACE, NVS_READWRITE, &h) != ESP_OK) {
        return;
    }
    nvs_set_i32(h, "brightness", s_brightness);
    nvs_set_i32(h, "sleep_min", s_sleep_min);
    nvs_set_i32(h, "haptics", s_haptics);
    nvs_set_i32(h, "dial_step", s_dial_step);
    nvs_commit(h);
    nvs_close(h);
    ESP_LOGI(TAG, "settings written to NVS: brightness %d%%, sleep %d min, haptics %d, dial step %d%%",
             s_brightness, s_sleep_min, s_haptics, s_dial_step);
}

/* Facts for the Settings app. */
static char s_ip_str[16] = "0.0.0.0";
static char s_ssid[33] = "";

const char *shell_ip(void)   { return s_ip_str; }
const char *shell_wifi_ssid(void)
{
    if (s_ssid[0] == '\0') {
        wifi_config_t cfg;
        if (esp_wifi_get_config(WIFI_IF_STA, &cfg) == ESP_OK) {
            snprintf(s_ssid, sizeof(s_ssid), "%s", (const char *) cfg.sta.ssid);
        }
    }
    return s_ssid;
}

int shell_wifi_rssi(void)
{
    wifi_ap_record_t ap;
    return (esp_wifi_sta_get_ap_info(&ap) == ESP_OK) ? ap.rssi : 0;
}

int shell_uptime_s(void)
{
    return (int)(esp_timer_get_time() / 1000000);
}

/* The refresh token dies 180 days after authorisation and refreshing does not
 * extend it, so the date is arithmetic rather than a guess (section 6). */
int shell_reauth_days(void)
{
    char auth_date[16] = { 0 };
    if (nvs_get_string("auth_date", auth_date, sizeof(auth_date)) != ESP_OK) {
        return -1;
    }
    struct tm tm_auth = { 0 };
    if (sscanf(auth_date, "%4d-%2d-%2d", &tm_auth.tm_year, &tm_auth.tm_mon,
               &tm_auth.tm_mday) != 3) {
        return -1;
    }
    tm_auth.tm_year -= 1900;
    tm_auth.tm_mon -= 1;
    const time_t authed = mktime(&tm_auth);
    const time_t now = time(NULL);
    if (now < 1000000000) {
        return -1;   /* clock not set yet; say nothing rather than something wrong */
    }
    return 180 - (int)((now - authed) / 86400);
}

static void haptic_effect(uint8_t effect)
{
    drv2605_write(DRV2605_REG_WAVESEQ, effect);
    drv2605_write(DRV2605_REG_WAVESEQ + 1, 0);  /* end of sequence */
    drv2605_write(DRV2605_REG_GO, 1);
}

/* The vocabulary in docs/SOFTWARE-INTERACTION-CORE.md: one short click for a
 * detent, something heavier for a press or a refused detent. Effect 1 is a
 * strong click at 100%, 7 a soft bump, 16 a 1000 ms alert - the DRV2605's own
 * library 5 numbering. The Settings value scales the whole vocabulary rather
 * than muting parts of it. */
void shell_haptic_click(void)
{
    if (s_haptics == 0) {
        return;
    }
    haptic_effect(s_haptics == 1 ? 7 : 1);
}

void shell_haptic_firm(void)
{
    if (s_haptics == 0) {
        return;
    }
    haptic_effect(s_haptics == 1 ? 1 : 16);
}

/* The dial (Wave 2). NOT a quadrature encoder - two bidirectional detector
 * switches, one pulse line per direction, read by main/bidi_knob.c (ported
 * from Waveshare's demo). The espressif/knob component stays as a compile-time
 * dependency of esp_lvgl_port only.
 *
 * Shell role (Wave 4): one haptic click per detent, then dispatch the signed
 * delta to the active app. */
static bidi_knob_handle_t s_knob = NULL;

/* --- the app registry ----------------------------------------------------
 * The shell owns the list, the screen lifecycle and the selector. An app
 * never switches itself. */
/* Five apps and only five (BUILD.md section 1, R9 - the requirement that the
 * device is an app shell rather than a Spotify screen). Spotify is app 0
 * because it is what the device shows on boot and what everything returns
 * to. */
static const knob_app_t *const s_apps[] = {
    &spotify_app, &clock_app, &wispr_app, &launcher_app, &settings_app,
};
#define APP_COUNT (sizeof(s_apps) / sizeof(s_apps[0]))

static int s_active_index = 0;
static const knob_app_t *s_active_app = NULL;
static lv_obj_t *s_app_screen = NULL;

int shell_app_count(void)
{
    return (int) APP_COUNT;
}

const knob_app_t *shell_app_at(int index)
{
    return (index >= 0 && index < (int) APP_COUNT) ? s_apps[index] : NULL;
}

int shell_app_active_index(void)
{
    return s_active_index;
}

void shell_switch_home(void)
{
    shell_switch_to(0);
}

/* Long-press from anywhere opens the selector. The handler is attached by the
 * shell to every app screen it creates, so an app cannot forget it and cannot
 * override it. */
static void open_selector_async(void *unused)
{
    (void) unused;
    selector_open();
}

static void app_screen_event(lv_event_t *e)
{
    if (lv_event_get_code(e) == LV_EVENT_LONG_PRESSED && !selector_is_open()) {
        ESP_LOGI(TAG, "long-press - opening the menu");
        shell_haptic_firm();
        lv_async_call(open_selector_async, NULL);
    }
}

void shell_active_app_set_paused(bool paused)
{
    if (s_active_app == NULL) {
        return;
    }
    void (*fn)(void) = paused ? s_active_app->on_pause : s_active_app->on_resume;
    if (fn != NULL) {
        fn();
    }
}

void shell_open_menu(void)
{
    if (selector_is_open()) {
        return;
    }
    /* Deferred, because a caller is usually inside an event being dispatched
     * on the screen the menu is about to cover. */
    lv_async_call(open_selector_async, NULL);
}

/* --- sleep and waking ----------------------------------------------------
 *
 * The screen going dark used to be the whole of sleep, which meant a touch on
 * a dark screen both lit it and pressed whatever happened to be under the
 * finger. Reaching for a dark knob is how you turn it on; it is not how you
 * skip a track you cannot see.
 *
 * So going dark also raises an invisible shield on LVGL's system layer. It
 * takes the press, lights the screen, and absorbs the whole gesture through
 * to the release before removing itself - LVGL delivers RELEASED and CLICKED
 * to whatever was pressed, so the app underneath never learns the touch
 * happened. The dial is handled in input_task, which is simpler: it is not an
 * LVGL input device, so there is nothing to absorb. */
static bool      s_asleep = false;
static lv_obj_t *s_wake_shield = NULL;

bool shell_is_asleep(void)
{
    return s_asleep;
}

static void wake_shield_delete_async(void *unused)
{
    (void) unused;
    if (s_wake_shield != NULL) {
        lv_obj_delete(s_wake_shield);
        s_wake_shield = NULL;
    }
}

/* Deferred, because this is usually called from inside the shield's own event
 * callback and deleting an object mid-dispatch frees what LVGL is standing
 * on. Queueing it twice is harmless: the second call finds NULL. */
static void wake_shield_drop(void)
{
    if (s_wake_shield != NULL) {
        lv_async_call(wake_shield_delete_async, NULL);
    }
}

void shell_wake(void)
{
    if (!s_asleep) {
        return;
    }
    s_asleep = false;
    backlight_duty(s_brightness);
    lv_display_trigger_activity(NULL);
    ESP_LOGI(TAG, "awake");
}

static void wake_shield_cb(lv_event_t *e)
{
    if (lv_event_get_code(e) == LV_EVENT_PRESSED) {
        shell_wake();            /* light it the instant the finger lands */
    } else {
        wake_shield_drop();      /* released: the gesture is spent, stand down */
    }
}

/* Caller holds the LVGL lock. */
static void sleep_enter(void)
{
    if (s_asleep) {
        return;
    }
    s_asleep = true;
    backlight_duty(0);
    if (s_wake_shield == NULL) {
        s_wake_shield = lv_obj_create(lv_layer_sys());
        lv_obj_remove_style_all(s_wake_shield);
        lv_obj_set_size(s_wake_shield, 360, 360);
        lv_obj_center(s_wake_shield);
        lv_obj_remove_flag(s_wake_shield, LV_OBJ_FLAG_SCROLLABLE);
        lv_obj_add_flag(s_wake_shield, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_add_event_cb(s_wake_shield, wake_shield_cb, LV_EVENT_PRESSED, NULL);
        lv_obj_add_event_cb(s_wake_shield, wake_shield_cb, LV_EVENT_RELEASED, NULL);
    }
    ESP_LOGI(TAG, "screen off (%d min idle)", s_sleep_min);
}

static void back_button_cb(lv_event_t *e)
{
    (void) e;
    shell_haptic_click();
    shell_open_menu();
}

/*
 * One back affordance, built in one place, so it sits in the same spot on
 * every screen and cannot drift. A gesture nobody can see is not an exit, and
 * until 2026-09-04 the only way out of the Clock or Dictation was a long-press
 * you had to have been told about.
 */
lv_obj_t *shell_back_button(lv_obj_t *parent)
{
    lv_obj_t *back = lv_label_create(parent);
    lv_obj_set_style_text_font(back, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(back, lv_color_hex(0x5C6068), 0);
    lv_label_set_text(back, LV_SYMBOL_LEFT);
    lv_obj_align(back, LV_ALIGN_CENTER, 0, 138);
    lv_obj_add_flag(back, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_ext_click_area(back, 40);
    lv_obj_add_event_cb(back, back_button_cb, LV_EVENT_CLICKED, NULL);
    return back;
}

static lv_obj_t *app_screen_create(void)
{
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_flag(screen, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(screen, app_screen_event, LV_EVENT_LONG_PRESSED, NULL);
    return screen;
}

void shell_switch_to(int index)
{
    if (index < 0 || index >= (int) APP_COUNT) {
        return;
    }
    lvgl_port_lock(0);
    if (index == s_active_index && s_app_screen != NULL) {
        lvgl_port_unlock();
        return;
    }
    const knob_app_t *outgoing = s_active_app;
    lv_obj_t *old_screen = s_app_screen;

    /* No dial reaches an app that is between screens. */
    s_active_app = NULL;
    if (outgoing != NULL && outgoing->on_exit != NULL) {
        outgoing->on_exit();
    }

    s_active_index = index;
    s_app_screen = app_screen_create();
    s_apps[index]->on_enter(s_app_screen);
    lv_screen_load(s_app_screen);
    if (old_screen != NULL) {
        lv_obj_delete(old_screen);
    }
    s_active_app = s_apps[index];
    lvgl_port_unlock();

    ESP_LOGI(TAG, "app '%s' active (heap %u internal, %u PSRAM)", s_active_app->name,
             (unsigned) heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
             (unsigned) heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
}

/* --- the timer -----------------------------------------------------------
 * Shell-owned because the clock is (BUILD.md section 6): it has to keep
 * counting while you are looking at Spotify, and fire wherever you are. */
static int64_t s_timer_end_us = 0;
static int     s_timer_total_ms = 0;
static bool    s_alarm_ringing = false;
static lv_obj_t *s_alarm_overlay = NULL;

void shell_timer_set(int minutes)
{
    if (minutes <= 0) {
        s_timer_end_us = 0;
        s_timer_total_ms = 0;
        return;
    }
    s_timer_total_ms = minutes * 60 * 1000;
    s_timer_end_us = esp_timer_get_time() + (int64_t) s_timer_total_ms * 1000;
}

bool shell_timer_running(void)
{
    return s_timer_end_us != 0;
}

int shell_timer_remaining_ms(void)
{
    if (s_timer_end_us == 0) {
        return 0;
    }
    const int64_t left = (s_timer_end_us - esp_timer_get_time()) / 1000;
    return (left > 0) ? (int) left : 0;
}

int shell_timer_total_ms(void)
{
    return s_timer_total_ms;
}

static void alarm_dismiss_cb(lv_event_t *e)
{
    (void) e;
    s_alarm_ringing = false;
    lv_obj_add_flag(s_alarm_overlay, LV_OBJ_FLAG_HIDDEN);
    ESP_LOGI(TAG, "alarm dismissed");
}

/* Built once and kept hidden on the top layer: the alarm has to be able to
 * appear over whatever app is up, without that app knowing it exists. */
static void alarm_overlay_create(void)
{
    s_alarm_overlay = lv_obj_create(lv_layer_top());
    lv_obj_remove_style_all(s_alarm_overlay);
    lv_obj_set_size(s_alarm_overlay, 360, 360);
    lv_obj_center(s_alarm_overlay);
    lv_obj_remove_flag(s_alarm_overlay, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_color(s_alarm_overlay, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(s_alarm_overlay, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_alarm_overlay, LV_RADIUS_CIRCLE, 0);
    lv_obj_add_flag(s_alarm_overlay, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(s_alarm_overlay, alarm_dismiss_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t *zero = lv_label_create(s_alarm_overlay);
    lv_obj_set_style_text_font(zero, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(zero, lv_color_white(), 0);
    lv_label_set_text(zero, "0:00");
    lv_obj_center(zero);

    lv_obj_t *hint = lv_label_create(s_alarm_overlay);
    lv_obj_set_style_text_color(hint, lv_color_hex(0x8A8F99), 0);
    lv_label_set_text(hint, "TIMER DONE  TAP ANYWHERE");
    lv_obj_align(hint, LV_ALIGN_CENTER, 0, 52);

    lv_obj_add_flag(s_alarm_overlay, LV_OBJ_FLAG_HIDDEN);
}

static void alarm_fire(void)
{
    s_timer_end_us = 0;
    s_alarm_ringing = true;
    lvgl_port_lock(0);
    lv_obj_remove_flag(s_alarm_overlay, LV_OBJ_FLAG_HIDDEN);
    lv_obj_move_foreground(s_alarm_overlay);
    lvgl_port_unlock();
    ESP_LOGI(TAG, "timer done - ringing until touched");
}

/* --- input ---------------------------------------------------------------
 * Dial callbacks arrive on the esp_timer task, which is also where the knob's
 * own polling runs. Doing the haptic I2C write and the LVGL work there would
 * stall that task - a bloom render can hold the LVGL lock for tens of
 * milliseconds - and the stall would cost us detents. So the callback only
 * posts, and this task does the work. (BUILD.md section 6's input_task.) */
static QueueHandle_t s_dial_queue = NULL;

static void dial_cb(void *arg, void *usr_data)
{
    const bidi_knob_event_t event = (bidi_knob_event_t)(uintptr_t) usr_data;
    const int8_t delta = (event == BIDI_KNOB_RIGHT) ? 1 : -1;
    xQueueSend(s_dial_queue, &delta, 0);
}

static void input_task(void *arg)
{
    int8_t delta;
    for (;;) {
        if (xQueueReceive(s_dial_queue, &delta, portMAX_DELAY) != pdTRUE) {
            continue;
        }
        if (s_alarm_ringing) {
            continue;   /* the alarm owns every input until it is dismissed */
        }
        shell_haptic_click();               /* one click per detent */
        lvgl_port_lock(0);
        /* The dial is not an LVGL input device, so tell LVGL it happened -
         * that is what the sleep timer measures. */
        lv_display_trigger_activity(NULL);
        if (shell_is_asleep()) {
            /* A brief spin of a dark screen turns it on and does nothing
             * else. Adjusting the volume of something you cannot see is not
             * what anybody reaching for a dark knob meant. */
            shell_wake();
            lvgl_port_unlock();
            continue;
        }
        if (selector_is_open()) {
            selector_dial(delta);
        } else if (s_active_app != NULL && s_active_app->on_dial != NULL) {
            s_active_app->on_dial(delta);
        }
        lvgl_port_unlock();
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

/* Wave 8: name the last reset out loud.
 *
 * A device that reboots on its own and comes back looking fine is a device
 * that is hiding something, and a twelve-hour soak is unreadable without this
 * line. It is also the only honest way to tell a panic reboot from someone
 * pulling the cable. ESP_LOGI's format argument has to be a string literal -
 * the macro concatenates it - so this returns a name to pass as %s rather
 * than being a ternary at the call site. */
static const char *reset_reason_name(esp_reset_reason_t r)
{
    switch (r) {
    case ESP_RST_POWERON:   return "power-on";
    case ESP_RST_EXT:       return "external reset";
    case ESP_RST_SW:        return "software restart";
    case ESP_RST_PANIC:     return "PANIC - the previous run crashed";
    case ESP_RST_INT_WDT:   return "INTERRUPT WATCHDOG";
    case ESP_RST_TASK_WDT:  return "TASK WATCHDOG - a task stopped feeding it";
    case ESP_RST_WDT:       return "watchdog";
    case ESP_RST_BROWNOUT:  return "BROWNOUT - the supply sagged";
    case ESP_RST_DEEPSLEEP: return "deep sleep wake";
    case ESP_RST_SDIO:      return "SDIO reset";
    /* This board has no BOOT or RESET button and flashes over the S3's native
     * USB-Serial-JTAG, so a reset at the end of idf.py flash arrives through
     * the USB peripheral rather than through a pin. Naming it keeps the most
     * common reset on this desk out of the "unknown" bucket. */
    case ESP_RST_USB:       return "USB peripheral (a flash, most likely)";
    case ESP_RST_JTAG:      return "JTAG";
    case ESP_RST_EFUSE:     return "EFUSE ERROR";
    case ESP_RST_PWR_GLITCH: return "POWER GLITCH";
    case ESP_RST_CPU_LOCKUP: return "CPU LOCKUP - double exception";
    default:                return "unknown";
    }
}

static bool reset_was_a_fault(esp_reset_reason_t r)
{
    return r == ESP_RST_PANIC || r == ESP_RST_TASK_WDT ||
           r == ESP_RST_INT_WDT || r == ESP_RST_WDT || r == ESP_RST_BROWNOUT ||
           r == ESP_RST_CPU_LOCKUP || r == ESP_RST_PWR_GLITCH ||
           r == ESP_RST_EFUSE;
}

void app_main(void)
{
    backlight_init(40);

    const esp_reset_reason_t reset_reason = esp_reset_reason();
    if (reset_was_a_fault(reset_reason)) {
        ESP_LOGE(TAG, "last reset: %s", reset_reason_name(reset_reason));
    } else {
        ESP_LOGI(TAG, "last reset: %s", reset_reason_name(reset_reason));
    }

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    /* Settings before anything that uses them; brightness applies at once so
     * the boot flash is at the level you chose, not the compiled default. */
    settings_load();
    backlight_duty(s_brightness);
    ESP_LOGI(TAG, "settings loaded: brightness %d%%, sleep %d min, haptics %d, dial step %d%%",
             s_brightness, s_sleep_min, s_haptics, s_dial_step);

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

    /* The encoder and haptics (Wave 2). Haptics first: the input task fires a
     * click as soon as a detent arrives, and the queue must exist before the
     * dial can post to it. */
    haptics_init();
    s_dial_queue = xQueueCreate(16, sizeof(int8_t));
    assert(s_dial_queue != NULL);
    xTaskCreate(input_task, "input", 4096, NULL, 6, NULL);
    dial_init();

    /* Credentials into NVS, then onto the network (Wave 3). */
    s_token_mutex = xSemaphoreCreateMutex();
    s_refresh_mutex = xSemaphoreCreateMutex();
    assert(s_token_mutex != NULL && s_refresh_mutex != NULL);
    nvs_seed_if_missing();
    wifi_start();

    /* UK time, so the Clock app reads correctly once SNTP lands. */
    setenv("TZ", "GMT0BST,M3.5.0/1,M10.5.0", 1);
    tzset();

    /* Wave 4 and 7: the shell hosts apps behind knob_app_t, and owns the
     * selector that moves between them. Each app builds its own screen and
     * frees its own buffers; the shell owns the switch. */
    spotify_app_init();
    /* The HID transport. Wave 10 puts NimBLE behind this; today it logs what
     * it would have sent so the Wispr and Launcher screens can be judged on
     * glass without a BLE stack existing. Nothing here touches the radio. */
    hid_init();
    lvgl_port_lock(0);
    alarm_overlay_create();
    lvgl_port_unlock();
    shell_switch_to(0);
    ESP_LOGI(TAG, "shell up, %d apps, long-press for the selector", shell_app_count());

    /* Wave 8: the shell's own loop is watched.
     *
     * The idle tasks on both cores are already subscribed by default, and that
     * is what caught the first bloom implementation starving LVGL. What was
     * missing is that the watchdog only printed a backtrace - so the device
     * wedged and stayed wedged. CONFIG_ESP_TASK_WDT_PANIC now makes it a
     * panic, and the panic handler reboots, so a wedge recovers on its own.
     *
     * Subscribing this loop as well catches the other shape of failure: the
     * idle tasks running happily while the shell has stopped ticking, which is
     * what a deadlock on the LVGL lock would look like. This loop sleeps a
     * second at a time and does tens of milliseconds of work, so a ten-second
     * timeout has an order of magnitude of headroom. */
    ESP_ERROR_CHECK(esp_task_wdt_add(NULL));

    /* ~1 Hz housekeeping: the timer and sleep are the shell's, the tick is the
     * app's. */
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        esp_task_wdt_reset();

        /* Sleep: a permanently-powered desk object should not be a
         * permanently-lit one. LVGL already tracks touch inactivity; the input
         * task feeds dial movement into the same counter.
         *
         * This loop only ever puts the device to sleep. Waking is event-driven
         * - the shield on a touch, input_task on a detent - because a wake
         * that waited up to a second for the next tick would feel broken. The
         * idle_ms check below is the belt and braces for any path that resets
         * the activity counter without going through shell_wake. */
        if (!s_alarm_ringing && s_sleep_min > 0) {
            lvgl_port_lock(0);
            const uint32_t idle_ms = lv_display_get_inactive_time(NULL);
            if (!s_asleep && idle_ms > (uint32_t) s_sleep_min * 60000) {
                sleep_enter();
            } else if (s_asleep && idle_ms < 1000) {
                shell_wake();
                wake_shield_drop();
            }
            lvgl_port_unlock();
        } else if (s_asleep) {
            /* The alarm, or sleep turned off in Settings. Either way it should
             * be lit. */
            lvgl_port_lock(0);
            shell_wake();
            wake_shield_drop();
            lvgl_port_unlock();
        }

        if (s_timer_end_us != 0 && esp_timer_get_time() >= s_timer_end_us) {
            alarm_fire();
        }
        if (s_alarm_ringing) {
            shell_haptic_firm();   /* keeps ringing until it is touched */
        }
        if (s_active_app != NULL && s_active_app->on_tick != NULL) {
            s_active_app->on_tick();
        }

        /* Heap telemetry every 30 s. A steady figure means the TLS failure was
         * fragmentation or a high-water mark; a falling one means a leak, and
         * the two want completely different fixes. `largest` is the number
         * that actually decides whether a handshake can allocate. */
        static int ticks;
        if (++ticks % 30 == 0) {
            /* DMA-capable is reported separately because it is what actually
             * failed: esp-aes allocates DMA descriptors for hardware AES, and
             * that pool can be exhausted while ordinary internal RAM looks
             * comfortable. */
            ESP_LOGI(TAG, "heap: %u internal (%u largest), %u DMA (%u largest), %u PSRAM",
                     (unsigned) heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
                     (unsigned) heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL),
                     (unsigned) heap_caps_get_free_size(MALLOC_CAP_DMA),
                     (unsigned) heap_caps_get_largest_free_block(MALLOC_CAP_DMA),
                     (unsigned) heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        }
    }
}
