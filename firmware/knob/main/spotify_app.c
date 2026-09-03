/*
 * The Spotify app (app 1). Provider + screen, behind the knob_app_t contract.
 *
 * player_state_t belongs here, not to the shell (BUILD.md section 6). It is
 * written by the poll task under a mutex and read by the UI timer. The
 * provider seam: screens read the struct without knowing who wrote it -
 * nothing outside this file mentions Spotify, HTTP or JSON.
 *
 * Wave 4 scope: poll loop, title/artist/progress/volume, smooth progress
 * between polls. No album art (Wave 5), no controls (Wave 6).
 */
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "cJSON.h"
#include "esp_crt_bundle.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

#include "app_shell.h"

static const char *TAG = "spotify";

#define PLAYER_URL     "https://api.spotify.com/v1/me/player"
#define PLAYER_BUF_LEN (16 * 1024)
#define POLL_MS        5000

typedef struct {
    bool     valid;            /* false until the first successful poll */
    bool     is_playing;
    char     track_id[64];
    char     title[128];
    char     artist[128];
    char     album_art_url[256];
    int      progress_ms;
    int      duration_ms;
    int      volume_percent;
    bool     supports_volume;
    char     device_name[64];
    int64_t  last_update_tick;  /* esp_timer_get_time() at the poll */
} player_state_t;

static player_state_t s_state;
static SemaphoreHandle_t s_state_mutex;

/* The poll task is created once and lives for the life of the firmware,
 * idling on a semaphore whenever the app is not active. The obvious
 * alternative - create it in on_enter, wait for it to die in on_exit - would
 * make leaving the app block until any in-flight HTTP request finished, up to
 * the 10 s timeout. on_exit runs on the LVGL thread, so that wait is a frozen
 * screen. Nothing is allowed to block the switch. */
static volatile bool s_active = false;
static SemaphoreHandle_t s_wake;
static char *s_poll_buf = NULL;

/* UI widgets, owned by this app, valid between on_enter and on_exit. */
static lv_obj_t *s_progress_arc = NULL;
static lv_obj_t *s_title_label = NULL;
static lv_obj_t *s_artist_label = NULL;
static lv_obj_t *s_volume_label = NULL;
static lv_timer_t *s_ui_timer = NULL;

/* The dial overlay (BUILD.md section 5): raised on the first detent, gone two
 * seconds after the last. Green for volume, amber for seek - the value is the
 * label, so neither needs a word on it. */
static lv_obj_t  *s_dial_group = NULL;
static lv_obj_t  *s_dial_arc = NULL;
static lv_obj_t  *s_dial_value = NULL;
static lv_obj_t  *s_dial_unit = NULL;
static lv_timer_t *s_dial_hide_timer = NULL;
static bool s_dial_up = false;
static bool s_dial_seek = false;   /* chosen per gesture from supports_volume */
static int  s_dial_volume = 0;
static int  s_dial_seek_ms = 0;

/* One write 400 ms after the last detent, never one per detent - that is what
 * keeps a long sweep inside the rate limit. Set on the LVGL thread, sent by
 * the poll task, which is the only place HTTP belongs. */
#define WRITE_DEBOUNCE_US 400000
static volatile int     s_pending_volume = -1;
static volatile int     s_pending_seek_ms = -1;
static volatile int64_t s_write_due_us = 0;

/* --- provider: the poll ------------------------------------------------- */

static int s_retry_after_s = 0;

/* When Spotify is throttling us, say so. The screen used to sit on
 * "connecting..." for the whole penalty, which is a lie - the device is
 * connected, it is being told to wait. */
static volatile int64_t s_limited_until_us = 0;

static esp_err_t http_event(esp_http_client_event_t *evt)
{
    if (evt->event_id == HTTP_EVENT_ON_HEADER &&
        strcasecmp(evt->header_key, "Retry-After") == 0) {
        s_retry_after_s = atoi(evt->header_value);
    }
    return ESP_OK;
}

/* One HTTP client for the life of the active app, not one per request.
 *
 * Building and tearing down a client every 5 s leaked about 6 KB of internal
 * RAM each time (measured 2026-09-03: 70 KB free falling to 20 KB over a
 * minute of polling, taking TLS down with it - first hardware AES, then the
 * handshake itself, which reported as certificate verification failures that
 * were really just malloc failures). Keeping the handle also keeps the TLS
 * session, so a poll costs one request rather than a full handshake.
 *
 * Everything here runs on the poll task, so no locking is needed - and every
 * error path releases the handle so the next attempt starts clean. */
static esp_http_client_handle_t s_http = NULL;

static void http_release(void)
{
    if (s_http != NULL) {
        esp_http_client_close(s_http);
        esp_http_client_cleanup(s_http);
        s_http = NULL;
    }
}

static esp_err_t http_ensure(void)
{
    if (s_http != NULL) {
        return ESP_OK;
    }
    const esp_http_client_config_t cfg = {
        .url = PLAYER_URL,
        .method = HTTP_METHOD_GET,
        .crt_bundle_attach = esp_crt_bundle_attach,
        .timeout_ms = 10000,
        .event_handler = http_event,
        .keep_alive_enable = true,
    };
    s_http = esp_http_client_init(&cfg);
    return (s_http != NULL) ? ESP_OK : ESP_FAIL;
}

/* Send one request on the shared handle. Returns ESP_OK with the status set;
 * on any transport failure the handle is released and the caller retries. */
static esp_err_t http_request(const char *url, esp_http_client_method_t method,
                              int *out_status, char *body, int body_len)
{
    char token[512];
    if (shell_token_get(token, sizeof(token)) != ESP_OK) {
        return ESP_ERR_INVALID_STATE;
    }
    if (http_ensure() != ESP_OK) {
        return ESP_FAIL;
    }

    static char auth[576];
    snprintf(auth, sizeof(auth), "Bearer %s", token);
    esp_http_client_set_url(s_http, url);
    esp_http_client_set_method(s_http, method);
    esp_http_client_set_header(s_http, "Authorization", auth);
    if (method != HTTP_METHOD_GET) {
        esp_http_client_set_header(s_http, "Content-Length", "0");
    }

    esp_err_t err = esp_http_client_open(s_http, 0);
    if (err != ESP_OK) {
        http_release();
        return err;
    }
    esp_http_client_fetch_headers(s_http);
    *out_status = esp_http_client_get_status_code(s_http);

    if (body != NULL) {
        const int len = esp_http_client_read_response(s_http, body, body_len - 1);
        body[len > 0 ? len : 0] = '\0';
    } else {
        /* Drain whatever came back: an unread body leaves the connection out
         * of step and the next request on it would read this one's tail. */
        char sink[128];
        while (esp_http_client_read(s_http, sink, sizeof(sink)) > 0) {
        }
    }

    /* If the response did not complete, the stream position is unknown and
     * the handle cannot safely be reused. */
    if (!esp_http_client_is_complete_data_received(s_http)) {
        http_release();
    }
    return ESP_OK;
}

static esp_err_t player_poll(char *buf, int *out_status)
{
    s_retry_after_s = 0;
    return http_request(PLAYER_URL, HTTP_METHOD_GET, out_status, buf, PLAYER_BUF_LEN);
}

static void copy_json_str(char *dst, size_t dst_len, const cJSON *obj, const char *key)
{
    const cJSON *v = cJSON_GetObjectItem(obj, key);
    snprintf(dst, dst_len, "%s", cJSON_IsString(v) ? v->valuestring : "");
}

static void state_from_json(const char *json)
{
    cJSON *root = cJSON_Parse(json);
    if (root == NULL) {
        ESP_LOGW(TAG, "player response did not parse");
        return;
    }
    const cJSON *item = cJSON_GetObjectItem(root, "item");
    const cJSON *artists = cJSON_GetObjectItem(item, "artists");
    const cJSON *artist0 = cJSON_GetArrayItem(artists, 0);
    const cJSON *device = cJSON_GetObjectItem(root, "device");
    const cJSON *progress = cJSON_GetObjectItem(root, "progress_ms");
    const cJSON *duration = cJSON_GetObjectItem(item, "duration_ms");
    const cJSON *volume = cJSON_GetObjectItem(device, "volume_percent");
    const cJSON *sup_vol = cJSON_GetObjectItem(device, "supports_volume");
    const cJSON *playing = cJSON_GetObjectItem(root, "is_playing");

    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    s_state.valid = true;
    s_state.is_playing = cJSON_IsTrue(playing);
    copy_json_str(s_state.track_id, sizeof(s_state.track_id), item, "id");
    copy_json_str(s_state.title, sizeof(s_state.title), item, "name");
    copy_json_str(s_state.artist, sizeof(s_state.artist), artist0, "name");
    copy_json_str(s_state.device_name, sizeof(s_state.device_name), device, "name");
    s_state.progress_ms = cJSON_IsNumber(progress) ? progress->valueint : 0;
    s_state.duration_ms = cJSON_IsNumber(duration) ? duration->valueint : 0;
    s_state.volume_percent = cJSON_IsNumber(volume) ? volume->valueint : -1;
    s_state.supports_volume = cJSON_IsTrue(sup_vol);
    s_state.last_update_tick = esp_timer_get_time();

    /* Album art URL: smallest image >= 300 px wide (BUILD.md section 6);
     * stored now, used in Wave 5. */
    const cJSON *album = cJSON_GetObjectItem(item, "album");
    const cJSON *images = cJSON_GetObjectItem(album, "images");
    int best_w = 0;
    const cJSON *img;
    cJSON_ArrayForEach(img, images) {
        const cJSON *w = cJSON_GetObjectItem(img, "width");
        const cJSON *url = cJSON_GetObjectItem(img, "url");
        if (!cJSON_IsNumber(w) || !cJSON_IsString(url)) {
            continue;
        }
        const bool better = (w->valueint >= 300 && (best_w < 300 || w->valueint < best_w)) ||
                            (best_w < 300 && w->valueint > best_w);
        if (better) {
            best_w = w->valueint;
            snprintf(s_state.album_art_url, sizeof(s_state.album_art_url), "%s", url->valuestring);
        }
    }
    xSemaphoreGive(s_state_mutex);

    /* Every field above is copied into s_state - copy_json_str and the two
     * snprintf calls - so nothing borrows a pointer into the tree and it can
     * go now. This is the leak that emptied internal RAM in two minutes
     * (2026-09-03): the parsed player response is 5-7 KB of small nodes and
     * strdup'd strings, and with CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL=16384
     * every one of those small allocations comes out of internal RAM. Losing
     * one tree per five-second poll is exactly the rate that was measured. */
    cJSON_Delete(root);

    ESP_LOGI(TAG, "now playing: '%s' by %s | volume %d%% | %s",
             s_state.title, s_state.artist, s_state.volume_percent,
             s_state.is_playing ? "playing" : "paused");
}

static void state_set_idle(void)
{
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    s_state.valid = true;
    s_state.is_playing = false;
    s_state.title[0] = '\0';
    s_state.last_update_tick = esp_timer_get_time();
    xSemaphoreGive(s_state_mutex);
}

/* A control call: PUT with the token, no body, on the same shared handle. */
static void player_command(const char *url, const char *what)
{
    int status = 0;
    if (http_request(url, HTTP_METHOD_PUT, &status, NULL, 0) != ESP_OK) {
        ESP_LOGW(TAG, "%s unreachable", what);
        return;
    }
    if (status == 403) {
        /* The phone refuses volume; the dial should already be on seek.
         * Wave 0 measured exactly this. */
        ESP_LOGW(TAG, "%s refused (403) - device disallows it", what);
    } else if (status >= 400) {
        ESP_LOGW(TAG, "%s -> HTTP %d", what, status);
    } else {
        ESP_LOGI(TAG, "%s -> HTTP %d", what, status);
    }
}

static void pending_write_check(void)
{
    if (s_write_due_us == 0 || esp_timer_get_time() < s_write_due_us) {
        return;
    }
    const int vol = s_pending_volume;
    const int seek = s_pending_seek_ms;
    s_write_due_us = 0;
    s_pending_volume = -1;
    s_pending_seek_ms = -1;

    char url[192];
    if (vol >= 0) {
        snprintf(url, sizeof(url), "%s/volume?volume_percent=%d", PLAYER_URL, vol);
        player_command(url, "volume");
    } else if (seek >= 0) {
        snprintf(url, sizeof(url), "%s/seek?position_ms=%d", PLAYER_URL, seek);
        player_command(url, "seek");
    }
}

/* Sleep in <=100 ms slices so leaving the app is noticed promptly, and so a
 * debounced write still goes out while the poll itself is waiting out a 429. */
static void poll_wait(int ms)
{
    for (int i = 0; i < ms / 100 && s_active; i++) {
        vTaskDelay(pdMS_TO_TICKS(100));
        pending_write_check();
    }
}

static void poll_task(void *arg)
{
    /* The forced-expiry test that used to live here passed on hardware
     * (2026-09-03: token discarded -> 401 -> refreshed -> recovered) and has
     * been removed. The T+55 min timer and any real 401 are the only refresh
     * triggers now. */
    for (;;) {
    /* Inactive: no buffer held, no HTTP made, no rate-limit budget spent.
     * The app that is not in front of you costs nothing. */
    xSemaphoreTake(s_wake, portMAX_DELAY);
    s_poll_buf = heap_caps_malloc(PLAYER_BUF_LEN, MALLOC_CAP_SPIRAM);
    if (s_poll_buf == NULL) {
        ESP_LOGE(TAG, "no PSRAM for the poll buffer");
        continue;
    }

    while (s_active) {
        if (shell_auth_dead()) {
            ESP_LOGE(TAG, "auth dead - polling stopped until re-auth");
            break;
        }
        int status = 0;
        const esp_err_t err = player_poll(s_poll_buf, &status);
        if (err == ESP_ERR_INVALID_STATE) {
            /* no token yet - shell is still refreshing */
        } else if (err != ESP_OK) {
            ESP_LOGW(TAG, "poll unreachable, retrying");
        } else if (status == 200) {
            state_from_json(s_poll_buf);
        } else if (status == 204) {
            state_set_idle();
            ESP_LOGI(TAG, "nothing playing (204)");
        } else if (status == 401) {
            ESP_LOGW(TAG, "access token rejected (401) - asking shell to refresh");
            shell_token_refresh_now();
            continue;
        } else if (status == 429) {
            const int wait_s = (s_retry_after_s > 0) ? s_retry_after_s + 1 : 30;
            ESP_LOGW(TAG, "rate limited (429), Retry-After %d s - honouring it", s_retry_after_s);
            s_limited_until_us = esp_timer_get_time() + (int64_t) wait_s * 1000000;
            poll_wait(wait_s * 1000);
            continue;
        } else {
            ESP_LOGW(TAG, "poll HTTP %d", status);
        }
        poll_wait(POLL_MS);
    }

    /* Inactive means no connection held, not just no requests made. */
    http_release();
    heap_caps_free(s_poll_buf);
    s_poll_buf = NULL;
    ESP_LOGI(TAG, "poll stopped, buffer and connection released");
    }
}

/* --- screen ------------------------------------------------------------- */

/* Progress interpolated locally between polls. Never poll faster to make the
 * bar smooth (BUILD.md section 6). */
static int64_t progress_now(const player_state_t *st)
{
    int64_t progress = st->progress_ms;
    if (st->is_playing) {
        progress += (esp_timer_get_time() - st->last_update_tick) / 1000;
    }
    if (st->duration_ms > 0 && progress > st->duration_ms) {
        progress = st->duration_ms;
    }
    return progress;
}

static void ui_timer_cb(lv_timer_t *t)
{
    player_state_t st;
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    st = s_state;
    xSemaphoreGive(s_state_mutex);

    if (!st.valid || st.title[0] == '\0') {
        const int64_t limited_left = s_limited_until_us - esp_timer_get_time();
        if (limited_left > 0) {
            const int left_s = (int)(limited_left / 1000000);
            lv_label_set_text(s_title_label, "rate limited");
            lv_label_set_text_fmt(s_artist_label, "Spotify says wait %d:%02d",
                                  left_s / 60, left_s % 60);
        } else {
            lv_label_set_text(s_title_label, st.valid ? "nothing playing" : "connecting...");
            lv_label_set_text(s_artist_label, "");
        }
        lv_label_set_text(s_volume_label, "");
        lv_arc_set_value(s_progress_arc, 0);
        return;
    }

    lv_label_set_text(s_title_label, st.title);
    lv_label_set_text(s_artist_label, st.artist);
    if (st.volume_percent >= 0) {
        lv_label_set_text_fmt(s_volume_label, "vol %d%%", st.volume_percent);
    } else {
        lv_label_set_text(s_volume_label, "");
    }

    if (st.duration_ms > 0) {
        lv_arc_set_value(s_progress_arc,
                         (int32_t)(progress_now(&st) * 1000 / st.duration_ms));
    } else {
        lv_arc_set_value(s_progress_arc, 0);
    }
}

static void spotify_on_enter(lv_obj_t *parent)
{
    lv_obj_set_style_bg_color(parent, lv_color_black(), 0);

    /* Thin white progress ring tracing the bezel (BUILD.md section 5). */
    s_progress_arc = lv_arc_create(parent);
    lv_obj_set_size(s_progress_arc, 352, 352);
    lv_obj_center(s_progress_arc);
    lv_arc_set_rotation(s_progress_arc, 270);
    lv_arc_set_bg_angles(s_progress_arc, 0, 360);
    lv_arc_set_range(s_progress_arc, 0, 1000);
    lv_arc_set_value(s_progress_arc, 0);
    lv_obj_remove_style(s_progress_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_progress_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_arc_width(s_progress_arc, 3, LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_progress_arc, lv_color_hex(0x202020), LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_progress_arc, 3, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(s_progress_arc, lv_color_white(), LV_PART_INDICATOR);

    s_title_label = lv_label_create(parent);
    lv_obj_set_width(s_title_label, 260);
    lv_obj_set_style_text_align(s_title_label, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(s_title_label, LV_LABEL_LONG_SCROLL_CIRCULAR);
    lv_obj_set_style_text_font(s_title_label, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_title_label, lv_color_white(), 0);
    lv_label_set_text(s_title_label, "connecting...");
    lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, -24);

    s_artist_label = lv_label_create(parent);
    lv_obj_set_width(s_artist_label, 240);
    lv_obj_set_style_text_align(s_artist_label, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(s_artist_label, LV_LABEL_LONG_DOT);
    lv_obj_set_style_text_color(s_artist_label, lv_color_hex(0xB0B0B0), 0);
    lv_label_set_text(s_artist_label, "");
    lv_obj_align(s_artist_label, LV_ALIGN_CENTER, 0, 8);

    s_volume_label = lv_label_create(parent);
    lv_obj_set_style_text_color(s_volume_label, lv_color_hex(0x1DB954), 0);
    lv_label_set_text(s_volume_label, "");
    lv_obj_align(s_volume_label, LV_ALIGN_CENTER, 0, 40);

    /* The dial overlay, hidden until a detent arrives. Artwork drops away
     * behind it (near-black here until Wave 5 puts art on the screen). */
    s_dial_group = lv_obj_create(parent);
    lv_obj_remove_style_all(s_dial_group);
    lv_obj_set_size(s_dial_group, 360, 360);
    lv_obj_center(s_dial_group);
    lv_obj_remove_flag(s_dial_group, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_color(s_dial_group, lv_color_hex(0x08090B), 0);
    lv_obj_set_style_bg_opa(s_dial_group, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(s_dial_group, LV_RADIUS_CIRCLE, 0);
    lv_obj_add_flag(s_dial_group, LV_OBJ_FLAG_HIDDEN);

    s_dial_arc = lv_arc_create(s_dial_group);
    lv_obj_set_size(s_dial_arc, 300, 300);
    lv_obj_center(s_dial_arc);
    lv_arc_set_rotation(s_dial_arc, 270);
    lv_arc_set_bg_angles(s_dial_arc, 0, 360);
    lv_arc_set_value(s_dial_arc, 0);
    lv_obj_remove_style(s_dial_arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(s_dial_arc, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_arc_width(s_dial_arc, 10, LV_PART_MAIN);
    lv_obj_set_style_arc_color(s_dial_arc, lv_color_hex(0x1C1F24), LV_PART_MAIN);
    lv_obj_set_style_arc_width(s_dial_arc, 10, LV_PART_INDICATOR);

    s_dial_value = lv_label_create(s_dial_group);
    lv_obj_set_style_text_font(s_dial_value, &lv_font_montserrat_48, 0);
    lv_label_set_text(s_dial_value, "0");
    lv_obj_align(s_dial_value, LV_ALIGN_CENTER, 0, -6);

    s_dial_unit = lv_label_create(s_dial_group);
    lv_obj_set_style_text_color(s_dial_unit, lv_color_hex(0x8A8F99), 0);
    lv_label_set_text(s_dial_unit, "");
    lv_obj_align(s_dial_unit, LV_ALIGN_CENTER, 0, 32);

    s_ui_timer = lv_timer_create(ui_timer_cb, 250, NULL);

    s_active = true;
    xSemaphoreGive(s_wake);
    ESP_LOGI(TAG, "entered");
}

static void spotify_on_exit(void)
{
    /* Returns immediately. The poll task notices within 100 ms - or when its
     * in-flight request finishes - and frees the buffer itself. */
    s_active = false;
    lv_timer_delete(s_ui_timer);
    s_ui_timer = NULL;
    if (s_dial_hide_timer != NULL) {
        lv_timer_delete(s_dial_hide_timer);
        s_dial_hide_timer = NULL;
    }
    s_dial_up = false;
    /* Widgets die with the app screen (deleted by the shell). */
    s_progress_arc = s_title_label = s_artist_label = s_volume_label = NULL;
    s_dial_group = s_dial_arc = s_dial_value = s_dial_unit = NULL;
    ESP_LOGI(TAG, "exited");
}

/* --- the dial (R5) -------------------------------------------------------
 * Volume by default; seek where the active device refuses volume, chosen at
 * runtime from supports_volume and never assumed. The screen updates at every
 * detent; only the write is debounced. */

static void dial_hide_cb(lv_timer_t *t)
{
    (void) t;
    s_dial_hide_timer = NULL;
    s_dial_up = false;
    lv_obj_add_flag(s_dial_group, LV_OBJ_FLAG_HIDDEN);
}

static void dial_arm_hide(void)
{
    if (s_dial_hide_timer != NULL) {
        lv_timer_reset(s_dial_hide_timer);
        return;
    }
    s_dial_hide_timer = lv_timer_create(dial_hide_cb, 2000, NULL);
    lv_timer_set_repeat_count(s_dial_hide_timer, 1);
}

static void spotify_on_dial(int delta)
{
    player_state_t st;
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    st = s_state;
    xSemaphoreGive(s_state_mutex);

    if (!st.valid || st.title[0] == '\0') {
        /* No state means no idea what the current volume is, and a dial that
         * guesses is worse than one that waits. Logged because "declined" and
         * "the detent never arrived" look identical on the glass. */
        ESP_LOGI(TAG, "dial ignored - no player state yet");
        return;
    }

    const bool seek = !st.supports_volume;
    if (!s_dial_up || seek != s_dial_seek) {
        /* First detent of a gesture: seed from what Spotify last told us. */
        s_dial_seek = seek;
        s_dial_volume = (st.volume_percent >= 0) ? st.volume_percent : 50;
        s_dial_seek_ms = (int) progress_now(&st);
        s_dial_up = true;
        lv_obj_remove_flag(s_dial_group, LV_OBJ_FLAG_HIDDEN);
        lv_obj_set_style_arc_color(s_dial_arc,
                                   seek ? lv_color_hex(0xF5CE6B) : lv_color_hex(0x3FE07A),
                                   LV_PART_INDICATOR);
        lv_obj_set_style_text_color(s_dial_value,
                                    seek ? lv_color_hex(0xF5CE6B) : lv_color_hex(0x3FE07A), 0);
        lv_arc_set_range(s_dial_arc, 0, seek ? (st.duration_ms > 0 ? st.duration_ms : 1) : 100);
    }

    if (seek) {
        const int before = s_dial_seek_ms;
        s_dial_seek_ms += delta * 10000;          /* +/-10 s per detent */
        if (s_dial_seek_ms < 0) {
            s_dial_seek_ms = 0;
        } else if (st.duration_ms > 0 && s_dial_seek_ms > st.duration_ms) {
            s_dial_seek_ms = st.duration_ms;
        }
        if (s_dial_seek_ms == before) {
            shell_haptic_firm();                  /* the track has ends */
        } else {
            s_pending_seek_ms = s_dial_seek_ms;
            s_pending_volume = -1;
            s_write_due_us = esp_timer_get_time() + WRITE_DEBOUNCE_US;
        }
        lv_label_set_text_fmt(s_dial_value, "%d:%02d",
                              s_dial_seek_ms / 60000, (s_dial_seek_ms / 1000) % 60);
        lv_label_set_text_fmt(s_dial_unit, "of %d:%02d",
                              st.duration_ms / 60000, (st.duration_ms / 1000) % 60);
        lv_arc_set_value(s_dial_arc, s_dial_seek_ms);
    } else {
        const int before = s_dial_volume;
        s_dial_volume += delta * shell_dial_step();   /* Settings: 2, 5 or 10% */
        if (s_dial_volume < 0) {
            s_dial_volume = 0;
        } else if (s_dial_volume > 100) {
            s_dial_volume = 100;
        }
        if (s_dial_volume == before) {
            shell_haptic_firm();                  /* 0 and 100 are ends */
        } else {
            s_pending_volume = s_dial_volume;
            s_pending_seek_ms = -1;
            s_write_due_us = esp_timer_get_time() + WRITE_DEBOUNCE_US;
        }
        lv_label_set_text_fmt(s_dial_value, "%d", s_dial_volume);
        lv_label_set_text(s_dial_unit, "%");
        lv_arc_set_value(s_dial_arc, s_dial_volume);
    }
    dial_arm_hide();
}

static void spotify_on_tick(void)
{
    /* Housekeeping slot; nothing needed in Wave 4. */
}

const knob_app_t spotify_app = {
    .name = "Spotify",
    .glyph = NULL,
    .accent = { 0 },  /* green, set properly when the selector exists */
    .on_enter = spotify_on_enter,
    .on_exit = spotify_on_exit,
    .on_dial = spotify_on_dial,
    .on_tick = spotify_on_tick,
};

void spotify_app_init(void)
{
    s_state_mutex = xSemaphoreCreateMutex();
    s_wake = xSemaphoreCreateBinary();
    assert(s_state_mutex != NULL && s_wake != NULL);
    xTaskCreate(poll_task, "spotify_poll", 8192, NULL, 5, NULL);
}
