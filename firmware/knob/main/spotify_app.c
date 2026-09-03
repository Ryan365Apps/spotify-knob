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

static TaskHandle_t s_poll_task = NULL;
static volatile bool s_poll_stop = false;
static char *s_poll_buf = NULL;

/* UI widgets, owned by this app, valid between on_enter and on_exit. */
static lv_obj_t *s_progress_arc = NULL;
static lv_obj_t *s_title_label = NULL;
static lv_obj_t *s_artist_label = NULL;
static lv_obj_t *s_volume_label = NULL;
static lv_timer_t *s_ui_timer = NULL;

/* --- provider: the poll ------------------------------------------------- */

static int s_retry_after_s = 0;

static esp_err_t http_event(esp_http_client_event_t *evt)
{
    if (evt->event_id == HTTP_EVENT_ON_HEADER &&
        strcasecmp(evt->header_key, "Retry-After") == 0) {
        s_retry_after_s = atoi(evt->header_value);
    }
    return ESP_OK;
}

static esp_err_t player_poll(char *buf, int *out_status)
{
    char token[512];
    if (shell_token_get(token, sizeof(token)) != ESP_OK) {
        return ESP_ERR_INVALID_STATE;
    }

    s_retry_after_s = 0;
    const esp_http_client_config_t cfg = {
        .url = PLAYER_URL,
        .method = HTTP_METHOD_GET,
        .crt_bundle_attach = esp_crt_bundle_attach,
        .timeout_ms = 10000,
        .event_handler = http_event,
    };
    esp_http_client_handle_t client = esp_http_client_init(&cfg);
    if (client == NULL) {
        return ESP_FAIL;
    }
    static char auth[576];
    snprintf(auth, sizeof(auth), "Bearer %s", token);
    esp_http_client_set_header(client, "Authorization", auth);

    esp_err_t err = esp_http_client_open(client, 0);
    if (err != ESP_OK) {
        esp_http_client_cleanup(client);
        return err;
    }
    esp_http_client_fetch_headers(client);
    *out_status = esp_http_client_get_status_code(client);
    const int len = esp_http_client_read_response(client, buf, PLAYER_BUF_LEN - 1);
    buf[len > 0 ? len : 0] = '\0';
    esp_http_client_cleanup(client);
    return ESP_OK;
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

static void poll_task(void *arg)
{
    /* Wave 3 checkpoint D / Wave 4 checkpoint D: after the first successful
     * poll, force a token expiry once and prove recovery. Removed when the
     * checkpoint passes. */
    bool forced_expiry_done = false;

    while (!s_poll_stop) {
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
            if (!forced_expiry_done) {
                forced_expiry_done = true;
                ESP_LOGW(TAG, "forced-expiry test: access token discarded");
                shell_token_corrupt_for_test();
            }
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
            for (int i = 0; i < wait_s * 10 && !s_poll_stop; i++) {
                vTaskDelay(pdMS_TO_TICKS(100));
            }
            continue;
        } else {
            ESP_LOGW(TAG, "poll HTTP %d", status);
        }
        for (int i = 0; i < POLL_MS / 100 && !s_poll_stop; i++) {
            vTaskDelay(pdMS_TO_TICKS(100));
        }
    }
    s_poll_task = NULL;
    vTaskDelete(NULL);
}

/* --- screen ------------------------------------------------------------- */

static void ui_timer_cb(lv_timer_t *t)
{
    player_state_t st;
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    st = s_state;
    xSemaphoreGive(s_state_mutex);

    if (!st.valid || st.title[0] == '\0') {
        lv_label_set_text(s_title_label, st.valid ? "nothing playing" : "connecting...");
        lv_label_set_text(s_artist_label, "");
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

    /* Smooth progress: interpolate from the last poll while playing. */
    int64_t progress = st.progress_ms;
    if (st.is_playing) {
        progress += (esp_timer_get_time() - st.last_update_tick) / 1000;
    }
    if (st.duration_ms > 0) {
        if (progress > st.duration_ms) {
            progress = st.duration_ms;
        }
        lv_arc_set_value(s_progress_arc, (int32_t)(progress * 1000 / st.duration_ms));
    } else {
        lv_arc_set_value(s_progress_arc, 0);
    }
}

static void spotify_on_enter(lv_obj_t *parent)
{
    s_poll_buf = heap_caps_malloc(PLAYER_BUF_LEN, MALLOC_CAP_SPIRAM);
    assert(s_poll_buf != NULL);

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

    s_ui_timer = lv_timer_create(ui_timer_cb, 250, NULL);

    s_poll_stop = false;
    xTaskCreate(poll_task, "spotify_poll", 8192, NULL, 5, &s_poll_task);
    ESP_LOGI(TAG, "entered");
}

static void spotify_on_exit(void)
{
    s_poll_stop = true;
    while (s_poll_task != NULL) {
        vTaskDelay(pdMS_TO_TICKS(50));  /* poll task deletes itself */
    }
    lv_timer_delete(s_ui_timer);
    s_ui_timer = NULL;
    /* Widgets die with the app screen (deleted by the shell). */
    s_progress_arc = s_title_label = s_artist_label = s_volume_label = NULL;
    heap_caps_free(s_poll_buf);
    s_poll_buf = NULL;
    ESP_LOGI(TAG, "exited, buffers freed");
}

static void spotify_on_dial(int delta)
{
    /* Wave 6: volume/seek. Nothing yet. */
    (void) delta;
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
    assert(s_state_mutex != NULL);
}
