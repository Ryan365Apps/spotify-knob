/*
 * The Spotify app (app 1). Provider + screen, behind the knob_app_t contract.
 *
 * player_state_t belongs here, not to the shell (BUILD.md section 6). It is
 * written by the poll task under a mutex and read by the UI timer. The
 * provider seam: screens read the struct without knowing who wrote it -
 * nothing outside this file mentions Spotify, HTTP or JSON.
 *
 * Wave 4 scope: poll loop, title/artist/progress/volume, smooth progress
 * between polls. Wave 5 added the cover. Controls are still Wave 6.
 */
#include <stdbool.h>
#include <math.h>
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

#include "albumart.h"
#include "app_shell.h"
#include "bloom.h"

static const char *TAG = "spotify";

/* rev W's palette. The design law: green is volume, amber is seek, white is
 * the device itself. */
#define COL_GREEN_LIT  0x3FE07A
#define COL_AMBER_LIT  0xF5CE6B

#define PLAYER_URL     "https://api.spotify.com/v1/me/player"
#define PLAYER_BUF_LEN (16 * 1024)
/* BUILD.md section 6 specifies the cadence and the code was not following it -
 * a flat 5 s everywhere, which is why a track changed on the PC took 3-4 s to
 * appear (hardware, 2026-09-03). Nothing can be done about *not knowing* until
 * we ask; the only lever is how often we ask.
 *
 *   playing        3 s   - the case you are watching
 *   paused or 204 10 s   - nothing is going to change on its own
 *
 * Slowing the idle case pays for speeding the active one, so this is cheaper
 * on quota than the flat 5 s it replaces, not dearer. */
#define POLL_MS_PLAYING  3000
#define POLL_MS_IDLE    10000
#define POLL_MS          POLL_MS_PLAYING   /* the default before any state */

typedef struct {
    bool     valid;            /* false until the first successful poll */
    bool     is_playing;
    char     track_id[64];
    char     title[128];
    char     artist[128];
    char     album_art_url[256];
    char     album_art_small_url[256];   /* the 64 px entry, loaded first */
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

/* UI widgets, owned by this app, valid between on_enter and on_exit.
 *
 * One canvas carries every pixel that is not text: the cover, the scrim over
 * it, and the bloom. NOW PLAYING and the dial screens are the same widget with
 * different segments lit, which is the whole argument of screens.html rev W -
 * so they are the same buffer here too, rather than two overlays taking turns
 * to be hidden. */
static uint8_t  *s_canvas_buf = NULL;
static lv_obj_t *s_canvas = NULL;
static lv_obj_t *s_title_label = NULL;
static lv_obj_t *s_artist_label = NULL;
static lv_timer_t *s_ui_timer = NULL;

/* Text for the two states. The midtext pair is NOW PLAYING; the value pair is
 * the dial screens, where the number takes the centre and there is no label at
 * all - a percentage in green and a timestamp in amber cannot be mistaken for
 * one another. */
static lv_obj_t *s_dial_value = NULL;
static lv_obj_t *s_dial_unit = NULL;

/* The composited cover, kept so the bloom can be redrawn without re-running
 * art_blit.
 *
 * art_blit is 129 600 pixels of read, multiply and write against PSRAM, and it
 * was running on every single detent. That is what made the dial screens lag
 * while the menus - which composite nothing - stayed snappy (hardware,
 * 2026-09-03). The cover does not change between detents, so it is blitted
 * once into this buffer and each redraw starts from a straight memcpy, which
 * PSRAM does an order of magnitude faster than a per-pixel multiply. */
static uint8_t *s_bg_buf = NULL;
static bool s_bg_valid = false;

/* Cross-fade state. Non-zero means a cover change is in flight. */
static uint32_t   s_art_gen = 0;
static int64_t    s_fade_start_us = 0;
static lv_timer_t *s_fade_timer = NULL;

/* What the last composite drew, so a redraw that would change nothing is
 * skipped. The chip moving one pixel is the finest thing worth a repaint. */
static int  s_drawn_pct_x1000 = -1;
static bool s_drawn_dial = false;
static int64_t s_last_compose_us = 0;

/* A whole-screen recomposite is not cheap: a 259 KB memcpy, ~15 000 bloom
 * pixel writes, then LVGL redrawing and flushing all 360x360 over SPI. The UI
 * tick runs at 250 ms and progress crosses a 1/1000 step every ~180 ms on a
 * three-minute track, so NOW PLAYING was doing all of that four times a second
 * and the LVGL task never yielded - the task watchdog fired on IDLE0 with the
 * backtrace sitting in the panel flush (hardware, 2026-09-03).
 *
 * Once a second is plenty for a progress mark. The chip moves about four
 * pixels between repaints at that rate, which is under the eye's notice on a
 * bar that takes minutes to cross. */
#define COMPOSE_MIN_INTERVAL_US 1000000

/* The dial path draws on a timer too, and for a harder reason than cost.
 *
 * spotify_on_dial used to call screen_compose directly. That runs on the input
 * task, holding the LVGL lock, and a composite is ~45 ms - so a fast spin
 * queued detents faster than they could be drawn and the input task never
 * yielded. The task watchdog caught it with the backtrace sitting in
 * draw_segment, called from spotify_on_dial, called from input_task (hardware,
 * 2026-09-03).
 *
 * Now a detent only updates the value and sets this flag. The timer draws at
 * most every 100 ms, which coalesces a burst of detents into one composite and
 * keeps the drawing off the input task entirely. The number in the middle
 * still updates on every single detent - that is the part you actually watch
 * while turning. */
#define DIAL_COMPOSE_INTERVAL_US 100000
static bool     s_dial_dirty = false;
static float    s_dial_pct = 0.0f;
static uint32_t s_dial_colour = 0;
static int64_t  s_dial_drawn_us = 0;
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

/* Defined with the screen code, but the poll loop needs it to work out when
 * the current track is due to end. */
static int64_t progress_now(const player_state_t *st);

static int s_retry_after_s = 0;

/* When Spotify is throttling us, say so. The screen used to sit on
 * "connecting..." for the whole penalty, which is a lie - the device is
 * connected, it is being told to wait. */
static volatile int64_t s_limited_until_us = 0;

/* Wave 8: a 5xx, or a transport failure, is Spotify or the network having a
 * moment - and the answer is to ask less often, not to keep asking every three
 * seconds. The backoff doubles from 2 s to a 60 s ceiling and resets on the
 * first clean response. The last known state stays on the screen throughout: a
 * 500 says nothing at all about what is playing. */
#define FAIL_BACKOFF_MIN_MS  2000
#define FAIL_BACKOFF_MAX_MS 60000
static int s_fail_backoff_ms = 0;
static volatile int64_t s_backoff_until_us = 0;

static int fail_backoff_next(void)
{
    s_fail_backoff_ms = (s_fail_backoff_ms == 0) ? FAIL_BACKOFF_MIN_MS
                                                 : s_fail_backoff_ms * 2;
    if (s_fail_backoff_ms > FAIL_BACKOFF_MAX_MS) {
        s_fail_backoff_ms = FAIL_BACKOFF_MAX_MS;
    }
    s_backoff_until_us = esp_timer_get_time() + (int64_t) s_fail_backoff_ms * 1000;
    return s_fail_backoff_ms;
}

static void fail_backoff_clear(void)
{
    s_fail_backoff_ms = 0;
    s_backoff_until_us = 0;
}

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
                              int *out_status, char *body, int body_len,
                              const char *req_body)
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
    const int req_len = (req_body != NULL) ? (int) strlen(req_body) : 0;
    if (req_len > 0) {
        esp_http_client_set_header(s_http, "Content-Type", "application/json");
    } else if (method != HTTP_METHOD_GET) {
        esp_http_client_set_header(s_http, "Content-Length", "0");
    }

    esp_err_t err = esp_http_client_open(s_http, req_len);
    if (err != ESP_OK) {
        http_release();
        return err;
    }
    if (req_len > 0 && esp_http_client_write(s_http, req_body, req_len) != req_len) {
        http_release();
        return ESP_FAIL;
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
    return http_request(PLAYER_URL, HTTP_METHOD_GET, out_status, buf, PLAYER_BUF_LEN, NULL);
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

    /* Two URLs, both chosen by size rather than array position - the array is
     * ordered largest-first and is usually 640/300/64, but that is convention
     * and not contract.
     *
     *   album_art_url        smallest at least 300 px wide (BUILD.md section 6)
     *   album_art_small_url  the smallest entry of all, the 64 px thumbnail
     *
     * The thumbnail is fetched first and upscaled so something of the right
     * colour is on the glass while the real cover is still arriving. On this
     * link the cover measured 779-8981 ms, so that gap is worth filling. */
    const cJSON *album = cJSON_GetObjectItem(item, "album");
    const cJSON *images = cJSON_GetObjectItem(album, "images");
    int best_w = 0;
    int small_w = 0;
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
        if (small_w == 0 || w->valueint < small_w) {
            small_w = w->valueint;
            snprintf(s_state.album_art_small_url,
                     sizeof(s_state.album_art_small_url), "%s", url->valuestring);
        }
    }
    /* If the smallest entry *is* the one we are going to show, there is no
     * thumbnail stage to run. */
    if (small_w == best_w) {
        s_state.album_art_small_url[0] = '\0';
    }

    /* Report what Spotify actually offered, once per boot.
     *
     * The array is documented as ordered largest-first and is conventionally
     * 640/300/64, but that is convention rather than contract - so the sizes
     * on offer are worth knowing rather than assuming. If anything between 64
     * and 300 ever appears, the first stage should use it: 64 up to 360 is a
     * 5.6x upscale and looks it, however well it is interpolated. */
    static bool sizes_logged = false;
    if (!sizes_logged) {
        char sizes[64] = "";
        int n = 0;
        cJSON_ArrayForEach(img, images) {
            const cJSON *w = cJSON_GetObjectItem(img, "width");
            if (cJSON_IsNumber(w)) {
                n += snprintf(sizes + n, sizeof(sizes) - n, "%s%d",
                              (n > 0) ? "/" : "", w->valueint);
                if (n >= (int) sizeof(sizes) - 1) {
                    break;
                }
            }
        }
        if (n > 0) {
            sizes_logged = true;
            ESP_LOGI(TAG, "cover sizes offered: %s - using %d for the thumbnail, "
                          "%d for the cover", sizes, small_w, best_w);
        }
    }
    xSemaphoreGive(s_state_mutex);

    /* Hand the cover to the art task. It compares the URL against the one it
     * is already showing and does nothing when they match, which is almost
     * every poll - BUILD.md calls that the single most valuable optimisation
     * in the pipeline, and it is why polling every 5 s costs no downloads. */
    albumart_request(s_state.album_art_url, s_state.album_art_small_url);

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
static void player_command_m(const char *url, esp_http_client_method_t method,
                             const char *what)
{
    int status = 0;
    if (http_request(url, method, &status, NULL, 0, NULL) != ESP_OK) {
        ESP_LOGW(TAG, "%s unreachable", what);
        return;
    }
    if (status == 403) {
        /* The phone refuses volume; the dial should already be on seek.
         * Wave 0 measured exactly this. */
        ESP_LOGW(TAG, "%s refused (403) - device disallows it", what);
    } else if (status == 404) {
        /* Spotify's NO_ACTIVE_DEVICE. Not a missing endpoint - there is simply
         * nowhere to send the command, which is what a 204 poll is also
         * telling us. Nothing on the device can fix it: the Web API can
         * transfer playback to a device it can already see, but it cannot
         * start one. Tap the device pill once the desktop app is running. */
        ESP_LOGW(TAG, "%s -> HTTP 404, no active device - start playback "
                      "somewhere, or tap the device pill", what);
    } else if (status >= 500) {
        /* Spotify's problem, not ours. The command is dropped rather than
         * retried: re-sending a skip a minute later would skip a track the
         * listener has since chosen. */
        ESP_LOGW(TAG, "%s -> HTTP %d, Spotify unavailable - command dropped", what, status);
    } else if (status >= 400) {
        ESP_LOGW(TAG, "%s -> HTTP %d", what, status);
    } else {
        ESP_LOGI(TAG, "%s -> HTTP %d", what, status);
    }
}

static void player_command(const char *url, const char *what)
{
    player_command_m(url, HTTP_METHOD_PUT, what);
}

/* --- transport, requested from the screen, sent from the poll task -------
 *
 * A tap runs on the LVGL thread and the HTTP handle belongs to the poll task,
 * which is the whole reason that handle needs no locking. So a button does not
 * make a request - it leaves a note, and the poll task posts it on its next
 * turn. Worst case that is a fraction of a second, and it keeps the one-writer
 * rule that Wave 4's connection reuse depends on. */
typedef enum {
    CMD_NONE = 0,
    CMD_PLAY,
    CMD_PAUSE,
    CMD_NEXT,
    CMD_PREV,
    CMD_TRANSFER,
} player_cmd_t;

static volatile player_cmd_t s_pending_cmd = CMD_NONE;

/* After a skip, keep asking until the track actually changes.
 *
 * A fixed settle delay cannot work here. Too long and every skip pays for the
 * worst case; too short and the poll returns the track you just left, after
 * which nothing happens until the next scheduled poll - which is why a 120 ms
 * settle produced a *five second* wait for the new title, POLL_MS exactly
 * (hardware, 2026-09-03). Guessing Spotify's latency is the wrong shape of
 * solution: ask again, quickly, until the answer changes.
 *
 * Capped, because a skip at the end of a playlist legitimately changes
 * nothing and this must not become a hot loop against a rate-limited API. */
#define SKIP_RETRY_MS     250
#define SKIP_RETRY_MAX    12          /* ~3 s of asking, then give up */
static char s_await_from[64];         /* track_id we are trying to leave */
static int  s_await_tries = 0;

/* True from the moment a skip is sent until the new track lands. The screen
 * goes black while it is set, so the press has a visible effect immediately
 * instead of leaving the previous cover up looking like nothing happened. */
static volatile bool s_awaiting_track = false;

/* Track change transition.
 *
 * Three elements, three timelines, because they become ready at three
 * different moments and pretending otherwise is what made the first attempt
 * wrong. Fading the backlight moved all of them together, so the screen came
 * back up on a bloom over black with no artwork - it had faded *in* on content
 * that had not arrived.
 *
 *   bloom    unwinds from wherever it is back to zero, and stays lit. It is
 *            the device's own mark, not Spotify's, so it has nothing to wait
 *            for and no reason to disappear.
 *   title    fades out, then back in when the new title actually arrives.
 *   artwork  fades out, then back in when the new cover arrives - slower,
 *            because it is the thing worth looking at and it is last.
 *
 * Each fade-in is triggered by its own content changing, not by a clock. That
 * is the whole point: nothing comes back before it has something to show.
 */
#define TR_OUT_MS      500
#define TR_TITLE_IN_MS 400
#define TR_ART_IN_MS   700

static int      s_art_level = 256;     /* 0..256, applied to the cover */
static int      s_art_target = 256;
static int64_t  s_art_fade_us = 0;
static int      s_art_from = 256;
static int      s_art_fade_ms = TR_OUT_MS;

static int      s_title_opa = 255;
static int      s_title_target = 255;
static int64_t  s_title_fade_us = 0;
static int      s_title_from = 255;
static int      s_title_fade_ms = TR_OUT_MS;

static float    s_bloom_pct = 0.0f;    /* what the rim is currently showing */
static bool     s_bloom_unwind = false;
static float    s_bloom_from = 0.0f;   /* where the unwind started */
static int64_t  s_bloom_us = 0;
#define TR_UNWIND_MS 600
static uint32_t s_tfade_gen = 0;
static char     s_tfade_track[64];
static char     s_shown_title[128];

static void fade_to(int *from, int64_t *at, int *target, int *ms,
                    int now_level, int to, int duration)
{
    *from = now_level;
    *target = to;
    *at = esp_timer_get_time();
    *ms = duration;
}

static int fade_level(int from, int target, int64_t at, int ms)
{
    if (at == 0) {
        return target;
    }
    const int64_t el = (esp_timer_get_time() - at) / 1000;
    if (el >= ms) {
        return target;
    }
    return from + (int)((int64_t)(target - from) * el / ms);
}

/* A track changed. Start everything on its way out. */
static void track_change_begin(void)
{
    fade_to(&s_art_from, &s_art_fade_us, &s_art_target, &s_art_fade_ms,
            s_art_level, 0, TR_OUT_MS);
    fade_to(&s_title_from, &s_title_fade_us, &s_title_target, &s_title_fade_ms,
            s_title_opa, 0, TR_OUT_MS);
    /* The rim runs backwards to zero over a fixed time, so it reads as
     * travelling round the ring rather than just shrinking. */
    s_bloom_from = s_bloom_pct;
    s_bloom_us = esp_timer_get_time();
    s_bloom_unwind = true;
    s_tfade_gen = albumart_generation();
    s_shown_title[0] = '\0';
}
/* Instrument for "how long until it is actually on the glass".
 *
 * Every timing so far has come from log lines written when a response was
 * *parsed*, which says nothing about when the pixels changed. Between the two
 * sit the UI tick, the 1 Hz composite throttle, the CONTROLS overlay and
 * LVGL's own refresh - and those are all mine, so attributing the wait to the
 * network without measuring them is an assumption, not a finding.
 *
 * s_skip_press_us is set on the button press; the two flags below make each
 * stage report itself once. */
static volatile int64_t s_skip_press_us = 0;
static bool s_report_title = false;
static bool s_report_cover = false;

/* Move playback to the desktop.
 *
 * Transfer, not launch: PUT /me/player moves audio to a device Spotify can
 * already see, so the desktop app has to be running. Nothing in the Web API
 * can start or focus an application - that is what the BLE keyboard is for in
 * Wave 10, and why this is not a bug to be fixed here.
 *
 * Picks the first device reporting type "Computer" that is not already the
 * active one. Runs on the poll task and borrows its buffer, which is free at
 * this point in the loop. */
static void player_transfer(void)
{
    if (s_poll_buf == NULL) {
        return;
    }
    int status = 0;
    if (http_request("https://api.spotify.com/v1/me/player/devices",
                     HTTP_METHOD_GET, &status, s_poll_buf, PLAYER_BUF_LEN,
                     NULL) != ESP_OK || status != 200) {
        ESP_LOGW(TAG, "device list -> HTTP %d", status);
        return;
    }

    cJSON *root = cJSON_Parse(s_poll_buf);
    if (root == NULL) {
        return;
    }
    char id[64] = "";
    char name[64] = "";
    const cJSON *devices = cJSON_GetObjectItem(root, "devices");
    const cJSON *d;
    cJSON_ArrayForEach(d, devices) {
        const cJSON *type = cJSON_GetObjectItem(d, "type");
        const cJSON *did  = cJSON_GetObjectItem(d, "id");
        const cJSON *act  = cJSON_GetObjectItem(d, "is_active");
        if (!cJSON_IsString(type) || !cJSON_IsString(did)) {
            continue;
        }
        if (strcmp(type->valuestring, "Computer") != 0 || cJSON_IsTrue(act)) {
            continue;
        }
        snprintf(id, sizeof(id), "%s", did->valuestring);
        const cJSON *dn = cJSON_GetObjectItem(d, "name");
        snprintf(name, sizeof(name), "%s", cJSON_IsString(dn) ? dn->valuestring : "?");
        break;
    }
    cJSON_Delete(root);

    if (id[0] == '\0') {
        ESP_LOGW(TAG, "no idle Computer to transfer to - is the desktop app running?");
        return;
    }

    char body[128];
    snprintf(body, sizeof(body), "{\"device_ids\":[\"%s\"],\"play\":true}", id);
    if (http_request(PLAYER_URL, HTTP_METHOD_PUT, &status, NULL, 0, body) != ESP_OK) {
        ESP_LOGW(TAG, "transfer unreachable");
        return;
    }
    ESP_LOGI(TAG, "transfer to '%s' -> HTTP %d", name, status);
}

/* Returns true when something was actually sent, so the caller can re-poll at
 * once rather than let the screen sit on its optimistic guess. */
static bool pending_cmd_check(void)
{
    const player_cmd_t cmd = s_pending_cmd;
    if (cmd == CMD_NONE) {
        return false;
    }
    s_pending_cmd = CMD_NONE;

    char url[192];
    switch (cmd) {
        case CMD_PLAY:
            snprintf(url, sizeof(url), "%s/play", PLAYER_URL);
            player_command_m(url, HTTP_METHOD_PUT, "play");
            break;
        case CMD_PAUSE:
            snprintf(url, sizeof(url), "%s/pause", PLAYER_URL);
            player_command_m(url, HTTP_METHOD_PUT, "pause");
            break;
        case CMD_NEXT:
        case CMD_PREV:
            /* Remember what we are leaving, so the poll can tell whether the
             * skip has landed yet. */
            xSemaphoreTake(s_state_mutex, portMAX_DELAY);
            snprintf(s_await_from, sizeof(s_await_from), "%s", s_state.track_id);
            xSemaphoreGive(s_state_mutex);
            s_await_tries = SKIP_RETRY_MAX;
            s_awaiting_track = true;

            snprintf(url, sizeof(url), "%s/%s", PLAYER_URL,
                     (cmd == CMD_NEXT) ? "next" : "previous");
            player_command_m(url, HTTP_METHOD_POST,
                             (cmd == CMD_NEXT) ? "next" : "previous");
            break;
        case CMD_TRANSFER:
            player_transfer();
            break;
        default:
            break;
    }
    return true;
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
/* Wait out the poll interval, but cut it short when a transport command has
 * just gone out.
 *
 * A press used to leave the screen showing its own optimistic guess for up to
 * five seconds - and when the command failed, as `play -> HTTP 404` did with no
 * active device, the guess never got corrected at all because a 204 carries no
 * state to correct it with. Re-polling straight after a command means the
 * screen is telling the truth within a few hundred milliseconds either way.
 * The 300 ms is for Spotify's own side to apply the change before we ask. */
static void poll_wait(int ms)
{
    /* 20 ms slices, not 100.
     *
     * Pressing next used to cost four delays in series before the new title
     * appeared: up to 100 ms for this loop to notice the command, the command
     * round trip, a 300 ms settle, the poll round trip, then up to 250 ms for
     * the UI tick. Two of those five were pure waiting on our side.
     *
     * The two round trips are unavoidable - Spotify's next returns 204 with no
     * body, so the device has to ask what is playing afterwards. Everything
     * else is now as small as it can safely be: 20 ms to notice, 120 ms to let
     * Spotify apply the skip, and a 50 ms UI tick to show it. */
    const uint32_t net_gen = shell_net_generation();

    for (int i = 0; i < ms / 20 && s_active; i++) {
        vTaskDelay(pdMS_TO_TICKS(20));
        if (pending_cmd_check()) {   /* transport first: a press should feel prompt */
            /* A token pause only. Whether Spotify has caught up is settled by
             * asking again, not by waiting a guessed amount - see the skip
             * retry note above pending_cmd_check. */
            vTaskDelay(pdMS_TO_TICKS(80));
            return;
        }
        pending_write_check();

        /* Wave 8: the network coming back is news worth acting on at once.
         * Without this a router reboot would leave the screen up to a minute
         * stale, because the backoff had grown to sixty seconds while the
         * router was down and there is nothing to interrupt it. */
        if (shell_net_generation() != net_gen) {
            ESP_LOGI(TAG, "network back - dropping the poll backoff");
            fail_backoff_clear();
            return;
        }
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
            const int wait_ms = fail_backoff_next();
            ESP_LOGW(TAG, "poll unreachable - retrying in %d ms", wait_ms);
            poll_wait(wait_ms);
            continue;
        } else if (status == 200) {
            fail_backoff_clear();
            state_from_json(s_poll_buf);
        } else if (status == 204) {
            fail_backoff_clear();
            state_set_idle();
            ESP_LOGI(TAG, "nothing playing (204)");
        } else if (status >= 500) {
            const int wait_ms = fail_backoff_next();
            ESP_LOGW(TAG, "Spotify %d - retrying in %d ms", status, wait_ms);
            /* A 5xx often comes from an edge that is about to drop the
             * connection anyway. Start the next attempt on a fresh handle
             * rather than one we no longer trust - the handshake costs
             * nothing here, because the next attempt is seconds away. */
            http_release();
            poll_wait(wait_ms);
            continue;
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
        /* Poll again when the track is due to end, rather than on the next
         * five-second tick.
         *
         * A track ending naturally was taking up to a full poll interval to
         * show - measured as a two-second lag on the title and artwork
         * (2026-09-03), and up to five in the worst case. But the device
         * already knows when the track ends: it has the duration and the
         * position, and progress_now interpolates between them. So it can ask
         * at the moment the answer changes instead of guessing.
         *
         * This costs no extra requests in steady state - it re-times a poll
         * that was going to happen anyway - which matters, because the quota
         * is shared with the simulator and a 429 costs hours. The 400 ms is
         * for Spotify's own state to settle on the new track. */
        int wait_ms = POLL_MS_IDLE;

        /* Still waiting for a skip to show up? Ask again soon. */
        if (s_awaiting_track) {
            xSemaphoreTake(s_state_mutex, portMAX_DELAY);
            const bool changed = (strcmp(s_state.track_id, s_await_from) != 0);
            xSemaphoreGive(s_state_mutex);
            if (changed || --s_await_tries <= 0) {
                if (!changed) {
                    ESP_LOGW(TAG, "skip did not change the track - end of queue?");
                }
                s_awaiting_track = false;
            } else {
                poll_wait(SKIP_RETRY_MS);
                continue;
            }
        }

        xSemaphoreTake(s_state_mutex, portMAX_DELAY);
        if (s_state.valid && s_state.is_playing) {
            wait_ms = POLL_MS_PLAYING;
            /* And sooner still if the track is about to end, so a natural
             * change lands on the beat rather than up to an interval late. */
            if (s_state.duration_ms > 0) {
                const int left = s_state.duration_ms - (int) progress_now(&s_state);
                if (left > 0 && left + 400 < wait_ms) {
                    wait_ms = left + 400;
                }
            }
        }
        xSemaphoreGive(s_state_mutex);
        poll_wait(wait_ms);
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

/* --- CONTROLS (screen 03) ------------------------------------------------
 *
 * One tap from NOW PLAYING. Bare icons with no buttons drawn around them - the
 * artwork stays visible behind, and the tap target is still 40 px of glass
 * whatever the icon looks like. Auto-returns after 5 s.
 *
 * This is where play/pause lives, and it has to: the schematic verification in
 * BUILD.md section 3 found no push switch on this board, so the centre button
 * here is the only play/pause there is. No hidden gestures - no double-tap, no
 * long-press. Settled 2026-08-31.
 */
/* Five seconds of idle before CONTROLS returns to NOW PLAYING, per BUILD.md
 * section 5 - but a skip is not idling.
 *
 * Pressing next re-armed the full five seconds, so the track changed in under
 * a second and then the overlay sat there for five more before showing it. The
 * wait people notice after a skip is this timer, not the network (hardware,
 * 2026-09-03).
 *
 * A skip is a finished action whose result lives on the other screen, so it
 * gets a much shorter leash - still long enough to press next again, which is
 * the one thing you are likely to do next. Browsing the chips or the device
 * pill keeps the full five, because those have no result to go and look at. */
#define CONTROLS_IDLE_MS       5000
#define CONTROLS_AFTER_SKIP_MS 1200
#define TAP_TARGET        48       /* >= the 40 px the design asks for */

static lv_obj_t *s_ctl_group = NULL;
static lv_obj_t *s_ctl_play = NULL;
static lv_obj_t *s_ctl_pill = NULL;
static lv_obj_t *s_ctl_chip_vol = NULL;
static lv_obj_t *s_ctl_chip_seek = NULL;
static lv_timer_t *s_ctl_idle_timer = NULL;
static bool s_ctl_up = false;

/* A long-press opens the selector, and LVGL sends CLICKED on release either
 * way. Without this, letting go of a long-press would also open CONTROLS
 * behind the selector. */
static bool s_swallow_click = false;

/* SEEK chosen from CONTROLS assigns the dial for one adjustment only; when the
 * overlay clears, the dial is volume again (BUILD.md section 5). The automatic
 * fallback on volume-refusing devices is a separate thing and unaffected. */
static bool s_seek_once = false;

static void controls_show(bool on);
static void dial_hide_now(void);

static void ctl_idle_cb(lv_timer_t *t)
{
    (void) t;
    s_ctl_idle_timer = NULL;
    controls_show(false);
}

static void ctl_arm_idle_ms(int ms)
{
    if (s_ctl_idle_timer != NULL) {
        lv_timer_delete(s_ctl_idle_timer);
    }
    s_ctl_idle_timer = lv_timer_create(ctl_idle_cb, ms, NULL);
    lv_timer_set_repeat_count(s_ctl_idle_timer, 1);
}

static void ctl_arm_idle(void)
{
    ctl_arm_idle_ms(CONTROLS_IDLE_MS);
}

static void ctl_transport_cb(lv_event_t *e)
{
    const player_cmd_t cmd = (player_cmd_t)(intptr_t) lv_event_get_user_data(e);
    shell_haptic_firm();          /* a press is heavier than a detent */

    if (cmd == CMD_PLAY) {
        /* Toggle from what the last poll said, and flip the icon at once
         * rather than waiting up to 5 s for the next poll to confirm. The
         * device initiated this, so it is allowed to believe itself. */
        xSemaphoreTake(s_state_mutex, portMAX_DELAY);
        const bool playing = s_state.is_playing;
        s_state.is_playing = !playing;
        xSemaphoreGive(s_state_mutex);
        s_pending_cmd = playing ? CMD_PAUSE : CMD_PLAY;
        lv_label_set_text(s_ctl_play, playing ? LV_SYMBOL_PLAY : LV_SYMBOL_PAUSE);
        ctl_arm_idle();          /* play/pause has no result to go and see */
        return;
    }
    s_pending_cmd = cmd;
    /* Blank the text here, on the press, rather than waiting for the poll.
     * Together with the black canvas in screen_compose this makes the skip
     * visible immediately - the device is saying "asking", which is true. */
    s_awaiting_track = true;
    /* Start the transition on the press rather than waiting for the poll to
     * confirm - the skip is going to happen, and half a second of fade-out is
     * time the fetch gets to use. */
    track_change_begin();
    s_skip_press_us = esp_timer_get_time();
    s_report_title = true;
    s_report_cover = true;
    lv_label_set_text(s_title_label, "");
    lv_label_set_text(s_artist_label, "");
    s_drawn_pct_x1000 = -1;
    s_bg_valid = false;
    /* Next and previous: get out of the way and show what is now playing. */
    ctl_arm_idle_ms(CONTROLS_AFTER_SKIP_MS);
}

static void ctl_chip_cb(lv_event_t *e)
{
    const bool want_seek = (bool)(intptr_t) lv_event_get_user_data(e);

    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    const bool can_volume = s_state.supports_volume;
    xSemaphoreGive(s_state_mutex);

    if (!want_seek && !can_volume) {
        shell_haptic_firm();      /* greyed out: the device refuses volume */
        ctl_arm_idle();
        return;
    }
    s_seek_once = want_seek;
    shell_haptic_click();
    lv_obj_set_style_border_color(s_ctl_chip_vol,
                                  lv_color_hex(want_seek ? 0x3A3F47 : COL_GREEN_LIT), 0);
    lv_obj_set_style_border_color(s_ctl_chip_seek,
                                  lv_color_hex(want_seek ? COL_AMBER_LIT : 0x3A3F47), 0);
    ctl_arm_idle();
}

/* --- the screen ----------------------------------------------------------
 *
 * Everything that is not text lives in one RGB565 canvas: the cover, the scrim
 * over it, and the bloom. Compositing it here rather than stacking LVGL
 * objects is what makes the cross-fade and the near-black dial wash cost a
 * multiply per pixel instead of a full alpha-blended layer per frame.
 */

#define FADE_MS        200      /* BUILD.md section 6, step 6 */
#define SCRIM_BITS     5        /* radius^2 >> 5 indexes the table */
#define SCRIM_ENTRIES  ((180 * 180 >> SCRIM_BITS) + 2)

/* rev W's scrim:
 *   radial-gradient(circle at 50% 50%,
 *     rgba(0,0,0,.62) 0%, rgba(0,0,0,.26) 60%, rgba(0,0,0,.55) 100%)
 *
 * Darkest under the title, lightest through the mid-ring where the cover does
 * its work, dark again at the bezel so the rim reads against it. Indexed by
 * radius *squared* so no pixel ever needs a square root.
 */
static uint8_t s_scrim[SCRIM_ENTRIES];

static void scrim_build(void)
{
    for (int i = 0; i < SCRIM_ENTRIES; i++) {
        const float r = sqrtf((float)(i << SCRIM_BITS));
        float t = r / 180.0f;
        if (t > 1.0f) {
            t = 1.0f;
        }
        const float alpha = (t <= 0.6f) ? (0.62f + (0.26f - 0.62f) * (t / 0.6f))
                                        : (0.26f + (0.55f - 0.26f) * ((t - 0.6f) / 0.4f));
        s_scrim[i] = (uint8_t)(255.0f * (1.0f - alpha));
    }
}

/* The cover, nearest-neighbour from 300 to 360. A 1.2x upscale of a 300 px
 * source is imperceptible at desk distance and it happens once per track
 * change, not once per frame (BUILD.md section 6, step 5).
 *
 * `dim256` is a flat multiplier - 256 for NOW PLAYING, 15 for the dial
 * screens, where rev W drops the artwork to 6% so the bloom owns the screen.
 */
static void art_blit(uint16_t *buf, int dim256, bool use_scrim)
{
    albumart_lock();
    const uint16_t *front = albumart_front();
    const uint16_t *prev  = albumart_prev();

    int k = 256;
    if (s_fade_start_us != 0 && prev != NULL) {
        const int64_t el = (esp_timer_get_time() - s_fade_start_us) / 1000;
        k = (el >= FADE_MS) ? 256 : (int)((el * 256) / FADE_MS);
    }

    if (front == NULL) {
        memset(buf, 0, BLOOM_CANVAS_SZ);
        albumart_unlock();
        return;
    }

    for (int y = 0; y < BLOOM_CANVAS_H; y++) {
        const int dy = y - 180;
        const int dy2 = dy * dy;
        const uint16_t *rowf = front + ((y * 5) / 6) * ALBUMART_DIM;
        const uint16_t *rowp = (prev != NULL && k < 256)
                             ? prev + ((y * 5) / 6) * ALBUMART_DIM : NULL;
        uint16_t *dst = buf + y * BLOOM_CANVAS_W;

        for (int x = 0; x < BLOOM_CANVAS_W; x++) {
            const int dx = x - 180;
            const int r2 = dx * dx + dy2;
            if (r2 > 180 * 180) {
                dst[x] = 0;              /* outside the glass; never seen */
                continue;
            }
            const int sx = (x * 5) / 6;
            const uint16_t c = rowf[sx];
            int r5 = (c >> 11) & 0x1F, g6 = (c >> 5) & 0x3F, b5 = c & 0x1F;

            if (rowp != NULL) {
                const uint16_t p = rowp[sx];
                const int pr = (p >> 11) & 0x1F, pg = (p >> 5) & 0x3F, pb = p & 0x1F;
                r5 = pr + (((r5 - pr) * k) >> 8);
                g6 = pg + (((g6 - pg) * k) >> 8);
                b5 = pb + (((b5 - pb) * k) >> 8);
            }

            int m = dim256;
            if (use_scrim) {
                m = (m * s_scrim[r2 >> SCRIM_BITS]) >> 8;
            }
            r5 = (r5 * m) >> 8;
            g6 = (g6 * m) >> 8;
            b5 = (b5 * m) >> 8;
            dst[x] = (uint16_t)((r5 << 11) | (g6 << 5) | b5);
        }
    }
    albumart_unlock();
}

/* One composite. `pct` is 0..1 - track progress on NOW PLAYING, the dial value
 * on the dial screens. */

static void screen_compose(bool dial_up, float pct, lv_color_t lit)
{
    if (s_canvas == NULL) {
        return;
    }
    uint16_t *buf = (uint16_t *) s_canvas_buf;

    if (dial_up) {
        /* rev W dims the artwork to 6% here. At RGB565 that lands on one level
         * out of 31 - already invisible on the panel, and the photographs
         * confirm it reads as black. So this is a memset rather than a blit:
         * identical on the glass, and it removes the whole cost from the one
         * screen that redraws on every detent. */
        memset(buf, 0, BLOOM_CANVAS_SZ);
        bloom_draw_wedge(buf, lit, pct, 0.0f, false);
    } else if (s_art_level <= 0) {
        /* Cover fully out. Nothing to scale, so this is a memset - which is
         * why the dark part of the transition costs almost nothing however
         * long it lasts. */
        memset(buf, 0, BLOOM_CANVAS_SZ);
        bloom_draw_wedge(buf, lv_color_white(), s_bloom_pct, 0.55f, false);
        bloom_draw_chip(buf, lv_color_white(), s_bloom_pct);
        lv_obj_invalidate(s_canvas);
        return;
    } else if (s_awaiting_track && false) {
        /* A skip is in flight. Show black rather than the cover of the track
         * you just left - the press needs a visible effect at once, and the
         * old artwork sitting there reads as nothing having happened. The new
         * cover then arrives out of black, which is also the only moment the
         * cross-fade has nothing to fade from. */
        memset(buf, 0, BLOOM_CANVAS_SZ);
        bloom_draw_wedge(buf, lv_color_white(), 0.0f, 0.55f, false);
    } else {
        if (s_bg_buf != NULL) {
            if (!s_bg_valid) {
                art_blit((uint16_t *) s_bg_buf, 256, true);
                s_bg_valid = true;
            }
            if (s_art_level >= 256) {
                memcpy(buf, s_bg_buf, BLOOM_CANVAS_SZ);
            } else {
                /* Scale down from the cached full-brightness composite rather
                 * than re-running art_blit at a lower dim. Same result, but no
                 * source indexing, no scrim lookup and no circle test - the
                 * fade frames cost noticeably less than a fresh blit, which
                 * matters because there are ten of them per track change. */
                const uint16_t *src = (const uint16_t *) s_bg_buf;
                const int lv = s_art_level;
                for (int i = 0; i < BLOOM_CANVAS_W * BLOOM_CANVAS_H; i++) {
                    const uint16_t c = src[i];
                    const int r5 = (((c >> 11) & 0x1F) * lv) >> 8;
                    const int g6 = (((c >> 5) & 0x3F) * lv) >> 8;
                    const int b5 = ((c & 0x1F) * lv) >> 8;
                    buf[i] = (uint16_t)((r5 << 11) | (g6 << 5) | b5);
                }
            }
        } else {
            art_blit(buf, s_art_level, true);
        }
        /* Only the outer rim, so the cover stays visible inside it. The lit
         * boundary is progress; the chip on the bezel says exactly where. */
        /* Band 0.55, not rev W's 0.70. At 0.70 the rim is 25 px of radius and
         * read as a hairline on the panel; 0.55 is 38 px and roughly half as
         * many segments again, which is what makes it a rim rather than a
         * scratch (2026-09-03). */
        bloom_draw_wedge(buf, lv_color_white(), s_bloom_pct, 0.55f, false);
        bloom_draw_chip(buf, lv_color_white(), s_bloom_pct);
    }
    lv_obj_invalidate(s_canvas);
}

static void controls_show(bool on)
{
    if (s_ctl_group == NULL) {
        return;
    }
    s_ctl_up = on;
    if (on) {
        /* Exactly the NOW PLAYING composite underneath - full artwork, scrim,
         * and the progress rim.
         *
         * rev W dims the cover to 45% here and drops the rim. On the panel
         * that read as the screen going wrong rather than a layer arriving:
         * the artwork dulls and the one mark that was telling you where you
         * are in the track disappears, for no gain, because the icons carry
         * their own contrast anyway (2026-09-03). CONTROLS is a layer over
         * NOW PLAYING, so it should look like one. */
        s_drawn_pct_x1000 = -1;

        xSemaphoreTake(s_state_mutex, portMAX_DELAY);
        const bool playing = s_state.is_playing;
        const bool can_volume = s_state.supports_volume;
        const char *dev = s_state.device_name;
        xSemaphoreGive(s_state_mutex);

        lv_label_set_text(s_ctl_play, playing ? LV_SYMBOL_PAUSE : LV_SYMBOL_PLAY);
        lv_label_set_text_fmt(s_ctl_pill, LV_SYMBOL_AUDIO "  %s",
                              (dev[0] != '\0') ? dev : "no device");
        /* The VOLUME chip greys out where the device refuses volume - read
         * from supports_volume every poll, never assumed. */
        lv_obj_set_style_border_color(s_ctl_chip_vol,
                                      lv_color_hex(can_volume && !s_seek_once
                                                   ? COL_GREEN_LIT : 0x3A3F47), 0);
        lv_obj_set_style_text_color(s_ctl_chip_vol,
                                    lv_color_hex(can_volume ? 0xEAFFF1 : 0x5A5F67), 0);
        lv_obj_set_style_border_color(s_ctl_chip_seek,
                                      lv_color_hex(s_seek_once ? COL_AMBER_LIT : 0x3A3F47), 0);

        lv_obj_remove_flag(s_ctl_group, LV_OBJ_FLAG_HIDDEN);
        lv_obj_set_style_opa(s_ctl_group, LV_OPA_COVER, 0);
        ctl_arm_idle();
    } else {
        if (s_ctl_idle_timer != NULL) {
            lv_timer_delete(s_ctl_idle_timer);
            s_ctl_idle_timer = NULL;
        }
        lv_obj_add_flag(s_ctl_group, LV_OBJ_FLAG_HIDDEN);
        s_drawn_pct_x1000 = -1;      /* the next tick repaints NOW PLAYING */
    }
}

static void ctl_pill_cb(lv_event_t *e)
{
    (void) e;
    shell_haptic_firm();
    s_pending_cmd = CMD_TRANSFER;
    ctl_arm_idle();
}

/* Tap anywhere on NOW PLAYING raises CONTROLS. The shell owns the long-press
 * on this same screen, and LVGL sends CLICKED on release either way, so a
 * long-press has to be swallowed here or letting go of one would open CONTROLS
 * underneath the selector. */
static void screen_click_cb(lv_event_t *e)
{
    const lv_event_code_t code = lv_event_get_code(e);
    if (code == LV_EVENT_LONG_PRESSED) {
        s_swallow_click = true;
        return;
    }
    if (s_swallow_click) {
        s_swallow_click = false;
        return;
    }
    if (s_dial_up) {
        /* Tap the volume or seek screen and it goes at once rather than
         * waiting out its two seconds. You have finished with it - that is
         * what the tap means (Ryan, 2026-09-04). */
        dial_hide_now();
    } else if (!s_ctl_up) {
        controls_show(true);
    } else {
        ctl_arm_idle();          /* a tap on the ground keeps it up */
    }
}

/* Runs only while a cover is cross-fading, then deletes itself. */
static void fade_cb(lv_timer_t *t)
{
    (void) t;
    const int64_t el = (esp_timer_get_time() - s_fade_start_us) / 1000;
    s_drawn_pct_x1000 = -1;              /* force the next compose */
    s_bg_valid = false;                  /* the fade moved; rebuild the cover */
    s_last_compose_us = 0;               /* a fade step outranks the throttle */
    if (el >= FADE_MS) {
        s_fade_start_us = 0;
        lv_timer_delete(s_fade_timer);   /* not one-shot: it runs to a deadline */
        s_fade_timer = NULL;
    }
}

static void ui_timer_cb(lv_timer_t *t)
{
    player_state_t st;
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    st = s_state;
    xSemaphoreGive(s_state_mutex);

    /* Any change of track starts the transition, wherever it came from - the
     * button, the track ending, or someone on the PC. */
    if (st.valid && st.track_id[0] != '\0' &&
        strcmp(st.track_id, s_tfade_track) != 0) {
        snprintf(s_tfade_track, sizeof(s_tfade_track), "%s", st.track_id);
        track_change_begin();
    }

    /* Advance the two fades and the unwind. */
    const int art_was = s_art_level;
    s_art_level = fade_level(s_art_from, s_art_target, s_art_fade_us, s_art_fade_ms);

    const int title_was = s_title_opa;
    s_title_opa = fade_level(s_title_from, s_title_target, s_title_fade_us,
                             s_title_fade_ms);
    if (s_title_opa != title_was && s_title_label != NULL) {
        lv_obj_set_style_text_opa(s_title_label, (lv_opa_t) s_title_opa, 0);
        lv_obj_set_style_text_opa(s_artist_label, (lv_opa_t) s_title_opa, 0);
        /* The transport goes with them. Pressing next and having the buttons
         * stay lit over a black screen would look like the press was refused. */
        if (s_ctl_group != NULL && s_ctl_up) {
            lv_obj_set_style_opa(s_ctl_group, (lv_opa_t) s_title_opa, 0);
        }
    }

    /* The cover coming back is what ends the dark part. */
    if (s_art_target == 0 && albumart_generation() != s_tfade_gen) {
        s_tfade_gen = albumart_generation();
        fade_to(&s_art_from, &s_art_fade_us, &s_art_target, &s_art_fade_ms,
                s_art_level, 256, TR_ART_IN_MS);
        s_bg_valid = false;
    }

    /* A new cover landing starts the cross-fade. Watching the generation
     * counter means the screen never has to ask the art task anything. */
    const uint32_t gen = albumart_generation();
    if (gen != s_art_gen) {
        s_art_gen = gen;
        s_fade_start_us = esp_timer_get_time();
        s_drawn_pct_x1000 = -1;
        s_bg_valid = false;
        if (s_fade_timer == NULL) {
            /* 60 ms, not 30: each step is a full-screen redraw and flush, and
             * a 200 ms fade in four steps reads the same as one in seven for
             * half the load on the LVGL task. */
            s_fade_timer = lv_timer_create(fade_cb, 60, NULL);
        }
    }

    if (!st.valid || st.title[0] == '\0') {
        const int64_t now_us = esp_timer_get_time();
        const int64_t limited_left = s_limited_until_us - now_us;
        const int64_t backoff_left = s_backoff_until_us - now_us;
        if (limited_left > 0) {
            const int left_s = (int)(limited_left / 1000000);
            lv_label_set_text(s_title_label, "rate limited");
            lv_label_set_text_fmt(s_artist_label, "Spotify says wait %d:%02d",
                                  left_s / 60, left_s % 60);
            /* Two lines, so the title sits back above centre. The branch below
             * drops it to the true centre for its single line and nothing else
             * ever puts it back. */
            lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, -24);
        } else if (!st.valid && backoff_left > 0) {
            /* Wave 8: only when there is no track to show. A 5xx while
             * something is playing leaves the last known state alone, which is
             * the whole point of backing off rather than blanking. */
            const int left_s = (int)(backoff_left / 1000000) + 1;
            lv_label_set_text(s_title_label, "unavailable");
            lv_label_set_text_fmt(s_artist_label, "retrying in %d s", left_s);
            lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, -24);
        } else {
            /* The device names itself while it has nothing else to say. This
             * is the only screen TorqueOS is written on, which is the right
             * amount: a device that announces itself constantly is furniture
             * with a logo on it. */
            /* The title normally sits above centre to leave room for the
             * artist beneath it. With no artist there is nothing to leave room
             * for, so it drops to the true centre of the ring. */
            lv_label_set_text(s_title_label, st.valid ? "nothing playing" : "TORQUE OS");
            lv_label_set_text(s_artist_label, "");
            lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, 0);
        }
        if (!s_dial_up) {
            if (!st.valid) {
                /* Connecting: sweep the bloom so the wait has a pulse.
                 *
                 * The dim field goes into the spare buffer once; each frame is
                 * then a memcpy plus only the segments inside the tail, which
                 * is a small fraction of 300. Drawing all of them every frame
                 * held this to 5 fps - 45 degrees of travel per frame, which
                 * is why it stepped instead of sweeping. */
                static int64_t last_spin_us;
                const int64_t n = esp_timer_get_time();
                if (s_canvas != NULL && s_canvas_buf != NULL &&
                    n - last_spin_us >= 66000) {          /* ~15 fps */
                    last_spin_us = n;
                    if (s_bg_buf != NULL) {
                        if (!s_bg_valid) {
                            bloom_spinner_field((uint16_t *) s_bg_buf);
                            s_bg_valid = true;
                        }
                        memcpy(s_canvas_buf, s_bg_buf, BLOOM_CANVAS_SZ);
                    } else {
                        bloom_spinner_field((uint16_t *) s_canvas_buf);
                    }
                    bloom_spinner_head((uint16_t *) s_canvas_buf,
                                       (float) n / 1000000.0f);
                    lv_obj_invalidate(s_canvas);
                }
                /* The cover must rebuild from scratch once state lands - the
                 * spare buffer is holding the spinner field, not artwork. */
                s_drawn_pct_x1000 = -1;
            } else {
                screen_compose(false, 0.0f, lv_color_white());
                s_drawn_pct_x1000 = 0;
            }
            s_drawn_dial = false;
        }
        return;
    }

    if (!s_awaiting_track) {
        if (strcmp(st.title, s_shown_title) != 0) {
            /* New words. Put them up and bring them back, independently of
             * whatever the cover is doing. */
            snprintf(s_shown_title, sizeof(s_shown_title), "%s", st.title);
            lv_label_set_text(s_title_label, st.title);
            lv_label_set_text(s_artist_label, st.artist);
            lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, -24);
            if (s_title_target == 0) {
                fade_to(&s_title_from, &s_title_fade_us, &s_title_target,
                        &s_title_fade_ms, s_title_opa, 255, TR_TITLE_IN_MS);
            }
        }
        if (s_report_title && s_skip_press_us != 0) {
            s_report_title = false;
            ESP_LOGI(TAG, "skip -> title on screen: %lld ms",
                     (esp_timer_get_time() - s_skip_press_us) / 1000);
        }
    }

    /* The dial screens own the canvas while they are up. CONTROLS does not -
     * it is a layer of icons over the same NOW PLAYING composite. */
    if (s_dial_up) {
        if (s_dial_dirty) {
            const int64_t n = esp_timer_get_time();
            if (n - s_dial_drawn_us >= DIAL_COMPOSE_INTERVAL_US) {
                s_dial_dirty = false;
                s_dial_drawn_us = n;
                screen_compose(true, s_dial_pct, lv_color_hex(s_dial_colour));
            }
        }
        return;
    }

    const float pct = (st.duration_ms > 0)
                    ? (float) progress_now(&st) / (float) st.duration_ms : 0.0f;
    const int pct_x1000 = (int)(pct * 1000.0f);

    /* Repaint only when the chip would actually move, or when the dial screen
     * has just released the canvas. A full composite is ~10 ms; spending it
     * four times a second to draw the same pixels is not free. */
    /* Unwind the rim toward zero on a track change, then let it follow real
     * progress again. Eased, so it runs back quickly and settles rather than
     * dropping like a dial with the power cut. */
    if (s_bloom_unwind) {
        const int64_t el = (esp_timer_get_time() - s_bloom_us) / 1000;
        if (el >= TR_UNWIND_MS) {
            s_bloom_pct = 0.0f;
            s_bloom_unwind = false;
        } else {
            /* Ease out, so it leaves briskly and arrives at zero gently. */
            const float k = (float) el / (float) TR_UNWIND_MS;
            const float inv = 1.0f - k;
            s_bloom_pct = s_bloom_from * (inv * inv * inv);
        }
    } else if (s_awaiting_track) {
        /* Hold at zero until the new track's state actually arrives.
         *
         * Without this the rim ran back to zero and then immediately sprang
         * forward again, because `pct` is still derived from the track we just
         * left - the unwind ended, the rim resumed following progress, and the
         * only progress on record was the old track's. It then snapped back to
         * zero when the poll landed. Three moves where the eye expects one. */
        s_bloom_pct = 0.0f;
    } else {
        s_bloom_pct = pct;
    }

    const int64_t now_us = esp_timer_get_time();
    /* A moving fade or unwind has to repaint at its own rate, not once a
     * second - the throttle exists for the resting case, where only the
     * progress chip moves. */
    const bool animating = (s_art_level != art_was) || s_bloom_unwind ||
                           (s_art_level != s_art_target);
    const bool due = animating ||
                     (now_us - s_last_compose_us) >= COMPOSE_MIN_INTERVAL_US;
    /* s_drawn_dial means a dial screen or CONTROLS just released the canvas,
     * which has to repaint at once - the screen is showing the wrong thing
     * until it does. Everything else waits its turn. */
    if ((pct_x1000 != s_drawn_pct_x1000 && due) || s_drawn_dial || animating) {
        const int64_t c0 = esp_timer_get_time();
        screen_compose(false, pct, lv_color_white());
        if (s_report_cover && s_skip_press_us != 0 && albumart_front() != NULL) {
            s_report_cover = false;
            ESP_LOGI(TAG, "skip -> cover on screen: %lld ms (composite %lld ms)",
                     (esp_timer_get_time() - s_skip_press_us) / 1000,
                     (esp_timer_get_time() - c0) / 1000);
        }
        s_drawn_pct_x1000 = pct_x1000;
        s_drawn_dial = false;
        s_last_compose_us = now_us;
    }
}

static void spotify_on_enter(lv_obj_t *parent)
{
    lv_obj_set_style_bg_color(parent, lv_color_black(), 0);

    bloom_init();
    scrim_build();
    albumart_start();
    s_art_gen = albumart_generation();

    /* The canvas carries the cover and the bloom. 259 KB, PSRAM - the same
     * size the Clock's costs, and neither app is ever resident at once. */
    s_canvas_buf = heap_caps_malloc(BLOOM_CANVAS_SZ, MALLOC_CAP_SPIRAM);
    /* Optional: without it every redraw falls back to a full art_blit, which
     * works and is merely slow. */
    s_bg_buf = heap_caps_malloc(BLOOM_CANVAS_SZ, MALLOC_CAP_SPIRAM);
    s_bg_valid = false;
    if (s_canvas_buf != NULL) {
        memset(s_canvas_buf, 0, BLOOM_CANVAS_SZ);
        s_canvas = lv_canvas_create(parent);
        lv_canvas_set_buffer(s_canvas, s_canvas_buf, BLOOM_CANVAS_W,
                             BLOOM_CANVAS_H, LV_COLOR_FORMAT_RGB565);
        lv_obj_center(s_canvas);
        /* Every lv_obj is clickable by default, and a full-screen one that
         * stays that way swallows the long-press that opens the selector. */
        lv_obj_remove_flag(s_canvas, LV_OBJ_FLAG_CLICKABLE);
    } else {
        ESP_LOGE(TAG, "no PSRAM for the canvas - running without the bloom");
    }

    s_title_label = lv_label_create(parent);
    lv_obj_set_width(s_title_label, 260);
    lv_obj_set_style_text_align(s_title_label, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(s_title_label, LV_LABEL_LONG_SCROLL_CIRCULAR);
    lv_obj_set_style_text_font(s_title_label, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(s_title_label, lv_color_white(), 0);
    lv_label_set_text(s_title_label, "TORQUE OS");
    lv_obj_align(s_title_label, LV_ALIGN_CENTER, 0, -24);

    s_artist_label = lv_label_create(parent);
    lv_obj_set_width(s_artist_label, 240);
    lv_obj_set_style_text_align(s_artist_label, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_long_mode(s_artist_label, LV_LABEL_LONG_DOT);
    /* rev W says rgba(255,255,255,.6), which flattens to 0x999999 - measured
     * unreadable over real artwork on hardware (2026-09-03). Real covers are
     * far busier than the placeholder gradient the value was chosen against.
     * Bigger and much brighter; the scrim underneath does the rest. */
    lv_obj_set_style_text_font(s_artist_label, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_artist_label, lv_color_hex(0xE0E0E0), 0);
    lv_label_set_text(s_artist_label, "");
    lv_obj_align(s_artist_label, LV_ALIGN_CENTER, 0, 12);

    /* The dial value: the number takes the centre and carries no label, so it
     * simply replaces the title rather than covering it. Hidden until the
     * first detent. */
    s_dial_value = lv_label_create(parent);
    lv_obj_set_style_text_font(s_dial_value, &lv_font_montserrat_48, 0);
    lv_label_set_text(s_dial_value, "0");
    lv_obj_align(s_dial_value, LV_ALIGN_CENTER, 0, -6);
    lv_obj_add_flag(s_dial_value, LV_OBJ_FLAG_HIDDEN);

    s_dial_unit = lv_label_create(parent);
    /* "of 3:52" - the only supporting text on either dial screen. */
    lv_obj_set_style_text_color(s_dial_unit, lv_color_hex(0x666666), 0);
    lv_label_set_text(s_dial_unit, "");
    lv_obj_align(s_dial_unit, LV_ALIGN_CENTER, 0, 38);
    lv_obj_add_flag(s_dial_unit, LV_OBJ_FLAG_HIDDEN);

    /* --- CONTROLS, built now and hidden until a tap ---------------------- */
    s_ctl_group = lv_obj_create(parent);
    lv_obj_remove_style_all(s_ctl_group);
    lv_obj_set_size(s_ctl_group, 360, 360);
    lv_obj_center(s_ctl_group);
    lv_obj_remove_flag(s_ctl_group, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_flag(s_ctl_group, LV_OBJ_FLAG_HIDDEN);

    /* Device pill, top. Tapping it moves playback to the desktop. */
    s_ctl_pill = lv_label_create(s_ctl_group);
    lv_obj_set_style_text_color(s_ctl_pill, lv_color_hex(0xD8DCE4), 0);
    lv_obj_set_style_bg_color(s_ctl_pill, lv_color_hex(0x14171C), 0);
    lv_obj_set_style_bg_opa(s_ctl_pill, LV_OPA_70, 0);
    lv_obj_set_style_radius(s_ctl_pill, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_pad_hor(s_ctl_pill, 14, 0);
    lv_obj_set_style_pad_ver(s_ctl_pill, 7, 0);
    lv_label_set_text(s_ctl_pill, LV_SYMBOL_AUDIO "  --");
    lv_obj_align(s_ctl_pill, LV_ALIGN_TOP_MID, 0, 54);
    lv_obj_add_flag(s_ctl_pill, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_ext_click_area(s_ctl_pill, 12);
    lv_obj_add_event_cb(s_ctl_pill, ctl_pill_cb, LV_EVENT_CLICKED, NULL);

    /* Transport across the middle. Bare icons, no buttons drawn around them -
     * the tap target is 48 px of glass regardless of what the glyph looks
     * like, which is the design's whole point about not drawing chrome. */
    static const struct { const char *sym; int dx; player_cmd_t cmd; } tr[] = {
        { LV_SYMBOL_PREV, -86, CMD_PREV },
        { LV_SYMBOL_PLAY,   0, CMD_PLAY },
        { LV_SYMBOL_NEXT,  86, CMD_NEXT },
    };
    for (int i = 0; i < 3; i++) {
        lv_obj_t *b = lv_label_create(s_ctl_group);
        lv_obj_set_style_text_font(b, &lv_font_montserrat_36, 0);
        lv_obj_set_style_text_color(b, lv_color_white(), 0);
        lv_label_set_text(b, tr[i].sym);
        lv_obj_align(b, LV_ALIGN_CENTER, tr[i].dx, 0);
        lv_obj_add_flag(b, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_set_ext_click_area(b, TAP_TARGET / 2);
        lv_obj_add_event_cb(b, ctl_transport_cb, LV_EVENT_CLICKED,
                            (void *)(intptr_t) tr[i].cmd);
        if (i == 1) {
            s_ctl_play = b;
        }
    }

    /* Two chips below, assigning the dial. */
    static const struct { const char *txt; int dx; bool seek; } chips[] = {
        { "VOLUME", -52, false },
        { "SEEK",    52, true  },
    };
    for (int i = 0; i < 2; i++) {
        lv_obj_t *c = lv_label_create(s_ctl_group);
        lv_obj_set_style_text_color(c, lv_color_hex(0xEAFFF1), 0);
        lv_obj_set_style_bg_color(c, lv_color_hex(0x0E1013), 0);
        lv_obj_set_style_bg_opa(c, LV_OPA_60, 0);
        lv_obj_set_style_border_width(c, 1, 0);
        lv_obj_set_style_border_color(c, lv_color_hex(0x3A3F47), 0);
        lv_obj_set_style_radius(c, LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_pad_hor(c, 12, 0);
        lv_obj_set_style_pad_ver(c, 6, 0);
        lv_label_set_text(c, chips[i].txt);
        lv_obj_align(c, LV_ALIGN_CENTER, chips[i].dx, 64);
        lv_obj_add_flag(c, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_set_ext_click_area(c, 14);
        lv_obj_add_event_cb(c, ctl_chip_cb, LV_EVENT_CLICKED,
                            (void *)(intptr_t) chips[i].seek);
        if (chips[i].seek) {
            s_ctl_chip_seek = c;
        } else {
            s_ctl_chip_vol = c;
        }
    }

    /* Spotify's way out lives here rather than on NOW PLAYING, because NOW
     * PLAYING is the artwork and a chevron sitting on it permanently would be
     * chrome on the one screen that is meant to be the album. CONTROLS is one
     * tap away and is already the screen you reach for when you want the
     * device rather than the music. */
    shell_back_button(s_ctl_group);

    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_LONG_PRESSED, NULL);

    s_drawn_pct_x1000 = -1;
    s_drawn_dial = false;
    s_fade_start_us = 0;
    s_ctl_up = false;
    s_art_level = s_art_target = 256;
    s_title_opa = s_title_target = 255;
    s_art_fade_us = s_title_fade_us = 0;
    s_bloom_unwind = false;
    s_bloom_pct = 0.0f;
    s_tfade_track[0] = '\0';
    s_shown_title[0] = '\0';
    s_swallow_click = false;
    s_seek_once = false;

    /* 50 ms so the dial redraw above lands promptly. The expensive paths are
     * throttled individually, so a fast tick costs almost nothing. */
    s_ui_timer = lv_timer_create(ui_timer_cb, 50, NULL);

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
    if (s_fade_timer != NULL) {
        lv_timer_delete(s_fade_timer);
        s_fade_timer = NULL;
    }
    if (s_ctl_idle_timer != NULL) {
        lv_timer_delete(s_ctl_idle_timer);
        s_ctl_idle_timer = NULL;
    }
    s_dial_up = false;
    s_ctl_up = false;
    s_fade_start_us = 0;

    /* An app that is not on screen holds no cover, no canvas and no
     * connection. This is Wave 7 Checkpoint D's whole point: PSRAM has to come
     * back to the same figure every time. */
    albumart_stop();

    /* Delete the canvas object *before* freeing what it points at. The shell
     * deletes the app screen after this returns, and a canvas still in the
     * tree with a freed buffer is a draw away from a crash. */
    if (s_canvas != NULL) {
        lv_obj_delete(s_canvas);
        s_canvas = NULL;
    }
    if (s_canvas_buf != NULL) {
        heap_caps_free(s_canvas_buf);
        s_canvas_buf = NULL;
    }
    if (s_bg_buf != NULL) {
        heap_caps_free(s_bg_buf);
        s_bg_buf = NULL;
    }
    s_bg_valid = false;
    s_title_label = s_artist_label = NULL;
    s_dial_value = s_dial_unit = NULL;
    s_ctl_group = s_ctl_play = s_ctl_pill = NULL;
    s_ctl_chip_vol = s_ctl_chip_seek = NULL;
    ESP_LOGI(TAG, "exited, canvas and art released");
}

/* --- the dial (R5) -------------------------------------------------------
 * Volume, where the active device allows it. Where it does not, the dial does
 * not quietly become something else - it opens CONTROLS, which is where every
 * action the dial cannot perform lives. supports_volume is read from the poll
 * every time and never assumed. The screen updates at every detent; only the
 * write is debounced. */

static void dial_hide_cb(lv_timer_t *t)
{
    (void) t;
    s_dial_hide_timer = NULL;
    s_dial_up = false;
    lv_obj_add_flag(s_dial_value, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(s_dial_unit, LV_OBJ_FLAG_HIDDEN);
    lv_obj_remove_flag(s_title_label, LV_OBJ_FLAG_HIDDEN);
    lv_obj_remove_flag(s_artist_label, LV_OBJ_FLAG_HIDDEN);
    s_seek_once = false;         /* one adjustment, then the dial is volume again */
    /* The next UI tick repaints NOW PLAYING over the wedge. */
    s_drawn_dial = true;
    s_drawn_pct_x1000 = -1;
}

/* The two-second wait, cut short. The timer has to go before the callback
 * runs by hand, or the one-shot would fire again on a screen that has already
 * been put back. */
static void dial_hide_now(void)
{
    if (s_dial_hide_timer != NULL) {
        lv_timer_delete(s_dial_hide_timer);
        s_dial_hide_timer = NULL;
    }
    if (s_dial_up) {
        dial_hide_cb(NULL);
    }
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
        /* One line per second, not one per detent. A single turn of the dial
         * produced twelve identical lines on 2026-09-03, which buries whatever
         * else the log was trying to say. */
        static int64_t last_log_us;
        const int64_t now_us = esp_timer_get_time();
        if (now_us - last_log_us > 1000000) {
            last_log_us = now_us;
            ESP_LOGI(TAG, "dial ignored - no player state yet");
        }
        return;
    }

    /*
     * The dial is volume, or it is nothing.
     *
     * Until 2026-09-04 a device that refused volume - which is every phone,
     * per the Wave 0 result - silently got seek instead, and that is what R5
     * originally asked for. On the desk it was wrong: the dial is for volume,
     * and turning it to watch the track scrub is not a graceful fallback, it
     * is the device doing something else. Ryan's call; R5 in BUILD.md section
     * 1 now says so.
     *
     * What it does instead is open CONTROLS, the screen that carries every
     * action the dial cannot perform - SEEK among them, still available by
     * hand and still lasting exactly one adjustment.
     */
    if (!st.supports_volume && !s_seek_once) {
        if (s_ctl_up) {
            ctl_arm_idle();      /* already there; just keep it up */
        } else {
            controls_show(true);
        }
        return;
    }

    if (s_ctl_up) {
        controls_show(false);    /* the dial screen replaces it, never layers */
    }

    /* SEEK from CONTROLS assigns the dial for one adjustment, and it is now
     * the only way the dial ever seeks. */
    const bool seek = s_seek_once;
    if (!s_dial_up || seek != s_dial_seek) {
        /* First detent of a gesture: seed from what Spotify last told us. */
        s_dial_seek = seek;
        s_dial_volume = (st.volume_percent >= 0) ? st.volume_percent : 50;
        s_dial_seek_ms = (int) progress_now(&st);
        s_dial_up = true;
        /* The number takes the centre, so the title and artist step aside
         * rather than being covered. */
        lv_obj_add_flag(s_title_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(s_artist_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_dial_value, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_dial_unit, LV_OBJ_FLAG_HIDDEN);
        lv_obj_set_style_text_color(s_dial_value,
                                    lv_color_hex(seek ? COL_AMBER_LIT : COL_GREEN_LIT), 0);
        s_dial_drawn_us = 0;      /* first frame of a gesture draws immediately */
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

            /* Move our own idea of the position with the dial.
             *
             * Without this the progress rim went on interpolating from the
             * position we just seeked *away* from, so returning to NOW PLAYING
             * showed the old spot and then jumped when the poll confirmed -
             * two steps to land somewhere the device already knew (hardware,
             * 2026-09-03). BUILD.md section 6 asks for exactly this: act now,
             * reconcile on the next poll. If the write fails, the poll puts it
             * back, which is the correct outcome rather than a lost update. */
            xSemaphoreTake(s_state_mutex, portMAX_DELAY);
            s_state.progress_ms = s_dial_seek_ms;
            s_state.last_update_tick = esp_timer_get_time();
            xSemaphoreGive(s_state_mutex);
        }
        lv_label_set_text_fmt(s_dial_value, "%d:%02d",
                              s_dial_seek_ms / 60000, (s_dial_seek_ms / 1000) % 60);
        lv_label_set_text_fmt(s_dial_unit, "of %d:%02d",
                              st.duration_ms / 60000, (st.duration_ms / 1000) % 60);
        s_dial_pct = (st.duration_ms > 0)
                   ? (float) s_dial_seek_ms / (float) st.duration_ms : 0.0f;
        s_dial_colour = COL_AMBER_LIT;
        s_dial_dirty = true;
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

            /* Same reasoning as seek: the device acts on its own decision
             * rather than waiting to be told what it already did. */
            xSemaphoreTake(s_state_mutex, portMAX_DELAY);
            s_state.volume_percent = s_dial_volume;
            xSemaphoreGive(s_state_mutex);
        }
        /* rev W sets the % as a small dim suffix on the number. LVGL cannot
         * mix sizes inside one label, and a second positioned label for one
         * glyph is not worth the alignment it would cost, so the % rides the
         * number at full size. The only line that ever sits below the value is
         * seek's duration. */
        lv_label_set_text_fmt(s_dial_value, "%d%%", s_dial_volume);
        lv_label_set_text(s_dial_unit, "");
        s_dial_pct = (float) s_dial_volume / 100.0f;
        s_dial_colour = COL_GREEN_LIT;
        s_dial_dirty = true;
    }
    dial_arm_hide();
}

static void spotify_on_tick(void)
{
    /* Housekeeping slot; nothing needed in Wave 4. */
}

/* The menu is over us. The 50 ms UI tick composites into a 259 KB PSRAM
 * canvas, which is the most expensive repeating thing this app does, and
 * every frame of it is now invisible. The poll task is left alone: it costs
 * the LVGL thread nothing, and stopping it would only make coming back
 * slower. */
static void spotify_on_pause(void)
{
    if (s_ui_timer != NULL) {
        lv_timer_pause(s_ui_timer);
    }
}

static void spotify_on_resume(void)
{
    if (s_ui_timer != NULL) {
        lv_timer_resume(s_ui_timer);
        /* Whatever changed while we were covered has to be repainted now,
         * not on whatever schedule the throttles would have chosen. */
        s_drawn_pct_x1000 = -1;
        s_bg_valid = false;
    }
}

const knob_app_t spotify_app = {
    .name = "Spotify",
    /* Was NULL, which the selector passed straight to lv_label_set_text and
     * LVGL answered with its placeholder - the app showed as "Text" in the
     * ring (found on hardware 2026-09-03). */
    .glyph = LV_SYMBOL_AUDIO,
    .accent = LV_COLOR_MAKE(0x1D, 0xB9, 0x54),   /* Spotify green */
    .on_enter = spotify_on_enter,
    .on_exit = spotify_on_exit,
    .on_dial = spotify_on_dial,
    .on_pause = spotify_on_pause,
    .on_resume = spotify_on_resume,
    .on_tick = spotify_on_tick,
};

void spotify_app_init(void)
{
    s_state_mutex = xSemaphoreCreateMutex();
    s_wake = xSemaphoreCreateBinary();
    assert(s_state_mutex != NULL && s_wake != NULL);
    xTaskCreate(poll_task, "spotify_poll", 8192, NULL, 5, NULL);
}
