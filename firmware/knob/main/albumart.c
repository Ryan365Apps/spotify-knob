/* albumart.c - see albumart.h. Wave 5 of BUILD.md section 8. */

#include "albumart.h"

#include <string.h>

#include "esp_crt_bundle.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "jpeg_decoder.h"

static const char *TAG = "art";

#define ART_PX        ((size_t) ALBUMART_DIM * ALBUMART_DIM)
#define ART_BYTES     (ART_PX * 2)

/* Covers at 300 px run 15-25 KB. 64 KB is room for an unusually busy one
 * without being room for something that is not a cover at all. */
#define JPEG_MAX      (64 * 1024)

/* Spotify's image CDN. A separate host from the API, so a separate client -
 * and keeping them separate also means an art fetch can never disturb the
 * player connection whose reuse Wave 4 spent a day proving. */
#define ART_TASK_STACK  6144
#define ART_TASK_PRIO   3

static uint16_t *s_art_a = NULL;         /* the two decode targets */
static uint16_t *s_art_b = NULL;
static uint8_t  *s_jpeg = NULL;          /* download buffer */

/* The thumbnail decodes here and is then upscaled into one of the pair above,
 * so everything downstream only ever sees a 300x300 buffer and never has to
 * know which stage produced it. Spotify's smallest entry is 64 px; 160 is
 * headroom for an artist whose smallest is larger. */
#define THUMB_MAX_DIM  160
static uint16_t *s_thumb = NULL;

static const uint16_t *s_front = NULL;   /* what the screen is showing */
static const uint16_t *s_prev  = NULL;   /* what it is fading from */
static uint32_t  s_generation = 0;
static lv_color_t s_tint;

static SemaphoreHandle_t s_mutex = NULL;
static SemaphoreHandle_t s_wake  = NULL;
static TaskHandle_t      s_task  = NULL;
static volatile bool     s_run   = false;
static volatile bool     s_idle  = true;   /* set while no app is showing art */

/* The URL currently shown, and the one asked for. Guarded by s_mutex. */
static char s_shown_url[256];
static char s_want_url[256];
static char s_shown_small[256];
static char s_want_small[256];

static esp_http_client_handle_t s_http = NULL;

/* When the last fetch finished, so the idle close can time out from it. */
static int64_t s_last_fetch_us = 0;
/* 10 s, halved from 20 after measuring what the window actually costs: while
 * it is open, free internal sits at 23-27 KB with a 14336 largest block, and
 * closed it is back to ~59 KB with 31744 (2026-09-03). The window exists to
 * cover a burst of skips, and a burst is a few seconds - the thumbnail and its
 * cover complete within about 600 ms of each other, so nothing needs 20. */
#define ART_CONN_IDLE_US  (10 * 1000000)

void albumart_lock(void)   { xSemaphoreTake(s_mutex, portMAX_DELAY); }
void albumart_unlock(void) { xSemaphoreGive(s_mutex); }

const uint16_t *albumart_front(void) { return s_front; }
const uint16_t *albumart_prev(void)  { return s_prev; }
uint32_t albumart_generation(void)   { return s_generation; }
lv_color_t albumart_tint(void)       { return s_tint; }

static void http_release(void)
{
    if (s_http != NULL) {
        esp_http_client_close(s_http);
        esp_http_client_cleanup(s_http);
        s_http = NULL;
    }
}

/* Stream the JPEG into s_jpeg. Returns its length, or -1.
 *
 * THE CONNECTION IS CLOSED 10 SECONDS AFTER THE LAST FETCH, not on a schedule
 * and not never. Both extremes were measured on hardware and both were wrong.
 *
 * Holding it open was the first version, by analogy with Wave 4's connection
 * reuse. On hardware it cost 41 KB of internal RAM: a resident mbedTLS session
 * plus this task's stack took free internal from 68 KB to 27 KB and halved the
 * largest free block from 31 KB to 14 KB (measured 2026-09-03). Nothing was
 * leaking - it was flat - but 14 KB is below the 16 KB input buffer a *new*
 * TLS handshake needs, so the moment this connection dropped it could not have
 * come back, and it would have failed as a certificate error rather than as
 * the memory problem it was. That trap is written up in WAVE-4.md.
 *
 * Closing it immediately after every fetch was the correction, and it restored
 * the heap - 60219 free, 31744 largest, flat over four minutes. But it made
 * every cover pay a handshake, and on this board that measured 2197-3183 ms
 * against BUILD.md's 1.5 s condition. A four-track skip run paid three
 * handshakes in a row.
 *
 * So: hold the connection for 10 s after a fetch, then drop it. Skipping
 * through tracks reuses one session and lands covers in ~100 ms, which is the
 * case where the delay is actually felt. A lone track change several minutes
 * later pays the handshake, which is the case where two seconds does not
 * matter. And the 41 KB is only held during those 10 s.
 *
 * The residual risk is honest and self-healing: inside that window free
 * internal is back near 27 KB with a ~14 KB largest block, so if the *player's*
 * connection happened to drop right then, its 16 KB handshake buffer might not
 * fit. It would release its handle and retry on the next poll, by which time
 * this connection has closed and the RAM is back. A one-poll delay, not a
 * wedged device.
 *
 * The general rule this leaves: reuse a connection you use every few seconds,
 * drop one you use every few minutes, and for anything bursty in between, hold
 * it just long enough to cover the burst. */
/* True once the URL being fetched is no longer the one wanted.
 *
 * Skipping four tracks in a row used to download four covers, three of them
 * for tracks already gone - visible in the 2026-09-03 log as two covers
 * landing back to back at 147 s and 151 s, long after their tracks had been
 * skipped. On a link running at 4-76 KB/s that is not a rounding error, it is
 * the reason the cover you actually want arrives last. */
static bool superseded(const char *url, bool is_small)
{
    xSemaphoreTake(s_mutex, portMAX_DELAY);
    const bool stale = (strcmp(url, is_small ? s_want_small : s_want_url) != 0);
    xSemaphoreGive(s_mutex);
    return stale;
}

static int fetch(const char *url, bool is_small)
{
    if (s_http == NULL) {
        const esp_http_client_config_t cfg = {
            .url = url,
            .method = HTTP_METHOD_GET,
            .crt_bundle_attach = esp_crt_bundle_attach,
            .timeout_ms = 10000,
            /* On, because the idle window above is what bounds the lifetime
             * now - not the absence of reuse. */
            .keep_alive_enable = true,
        };
        s_http = esp_http_client_init(&cfg);
        if (s_http == NULL) {
            return -1;
        }
    }
    /* Check before spending a handshake, not only during the read. A skip run
     * on 2026-09-03 paid three handshakes in a row because each abandoned
     * fetch closes the connection - the stream position is unknown after an
     * abandon, so it cannot be reused - and the next attempt then opened a
     * fresh one for a URL that was already stale. Checking here costs a mutex
     * and saves the whole exchange. */
    if (superseded(url, is_small)) {
        return -1;
    }

    esp_http_client_set_url(s_http, url);
    esp_http_client_set_method(s_http, HTTP_METHOD_GET);

    if (esp_http_client_open(s_http, 0) != ESP_OK) {
        http_release();
        return -1;
    }
    esp_http_client_fetch_headers(s_http);
    const int status = esp_http_client_get_status_code(s_http);
    if (status != 200) {
        ESP_LOGW(TAG, "cover HTTP %d", status);
        http_release();
        return -1;
    }

    int total = 0;
    for (;;) {
        const int n = esp_http_client_read(s_http, (char *) s_jpeg + total,
                                           JPEG_MAX - total);
        if (n <= 0) {
            break;
        }
        total += n;
        if (superseded(url, is_small)) {
            /* The track moved on mid-download. Drop the socket rather than
             * finish reading something nobody will look at. */
            http_release();
            return -1;
        }
        if (total >= JPEG_MAX) {
            ESP_LOGW(TAG, "cover larger than %d bytes, dropped", JPEG_MAX);
            http_release();
            return -1;
        }
    }
    const bool complete = esp_http_client_is_complete_data_received(s_http);
    if (!complete) {
        http_release();
        return -1;
    }
    s_last_fetch_us = esp_timer_get_time();
    return total;
}

/* Mean colour, sampled on a grid rather than over every pixel - 900 samples
 * say the same thing as 90 000 and cost a thousandth as much. Used to tint the
 * idle bloom, where only the broad cast of the cover matters. */
static lv_color_t average_of(const uint16_t *px)
{
    uint32_t r = 0, g = 0, b = 0, n = 0;
    for (int y = 0; y < ALBUMART_DIM; y += 10) {
        for (int x = 0; x < ALBUMART_DIM; x += 10) {
            const uint16_t c = px[y * ALBUMART_DIM + x];
            r += ((c >> 11) & 0x1F) << 3;
            g += ((c >> 5) & 0x3F) << 2;
            b += (c & 0x1F) << 3;
            n++;
        }
    }
    if (n == 0) {
        return lv_color_hex(0xE47846);
    }
    /* Covers average toward mud. Lift the result toward its own brightest
     * channel so the bloom keeps a recognisable cast instead of going grey. */
    uint8_t ar = (uint8_t)(r / n), ag = (uint8_t)(g / n), ab = (uint8_t)(b / n);
    const uint8_t peak = (ar > ag) ? ((ar > ab) ? ar : ab) : ((ag > ab) ? ag : ab);
    /* Scale in floating point. An integer lift quantises to 1x, 2x, 3x, which
     * meant a cover peaking at 106 got no lift at all and stayed grey while
     * one peaking at 99 got doubled - measured on 2026-09-03, tints 696A69 and
     * 99F482 from consecutive tracks. Multiplying all three channels by the
     * same factor preserves the hue; only the brightness moves. */
    if (peak > 0 && peak < 200) {
        /* Clamp the lift so the brightest channel lands exactly on 200 and
         * nothing clips.
         *
         * Clipping was shifting the hue: a muted cover lifted to, say,
         * (200, 120, 210) would clip red and blue at different points and come
         * out purple, which is what the Clock was showing (2026-09-03). Scaling
         * all three by one factor that cannot overflow keeps the cover's actual
         * hue and only moves its brightness. */
        const float lift = 200.0f / (float) peak;
        ar = (uint8_t)((float) ar * lift);
        ag = (uint8_t)((float) ag * lift);
        ab = (uint8_t)((float) ab * lift);
    }
    return lv_color_make(ar, ag, ab);
}

/* Decode the thumbnail sitting in s_jpeg and upscale it into whichever of the
 * 300x300 pair is not on screen, then publish it.
 *
 * Publishing with prev cleared means the thumbnail *appears* rather than fades
 * in - it is meant to be instant, and fading in something already blurry only
 * delays it further. The fade that matters is the next one, thumbnail to sharp,
 * which the full cover's publish sets up on its own. */
static bool decode_thumb(int len)
{
    esp_jpeg_image_cfg_t cfg = {
        .indata = s_jpeg,
        .indata_size = (uint32_t) len,
        .outbuf = (uint8_t *) s_thumb,
        .outbuf_size = (uint32_t)(THUMB_MAX_DIM * THUMB_MAX_DIM * 2),
        .out_format = JPEG_IMAGE_FORMAT_RGB565,
        .out_scale = JPEG_IMAGE_SCALE_0,
        .flags = { .swap_color_bytes = 0 },
    };
    esp_jpeg_image_output_t out = { 0 };
    if (esp_jpeg_decode(&cfg, &out) != ESP_OK) {
        return false;
    }
    const int sd = out.width;
    if (sd <= 0 || out.height <= 0 || sd > THUMB_MAX_DIM || out.height > THUMB_MAX_DIM) {
        return false;
    }

    /* Bilinear, not nearest-neighbour.
     *
     * 64 px to 300 is a 4.7x upscale, and then the screen takes it to 360.
     * Point-sampling that gives hard 6-pixel blocks, which read as the device
     * being broken for the few seconds before the real cover lands (hardware,
     * 2026-09-03). Interpolating instead makes the same data look like an
     * out-of-focus photograph coming into focus, which is what it actually is.
     *
     * It is one pass over 90 000 pixels on the art task, once per track. */
    uint16_t *target = (s_front == s_art_a) ? s_art_b : s_art_a;
    const int sh = out.height;
    for (int y = 0; y < ALBUMART_DIM; y++) {
        const int fy = (y * sh * 256) / ALBUMART_DIM;
        const int y0 = fy >> 8;
        const int wy = fy & 0xFF;
        const int y1 = (y0 + 1 < sh) ? (y0 + 1) : y0;
        const uint16_t *r0 = s_thumb + y0 * sd;
        const uint16_t *r1 = s_thumb + y1 * sd;
        uint16_t *dst = target + y * ALBUMART_DIM;

        for (int x = 0; x < ALBUMART_DIM; x++) {
            const int fx = (x * sd * 256) / ALBUMART_DIM;
            const int x0 = fx >> 8;
            const int wx = fx & 0xFF;
            const int x1 = (x0 + 1 < sd) ? (x0 + 1) : x0;

            const uint16_t a = r0[x0], b = r0[x1], c = r1[x0], d = r1[x1];
            /* Weights of the four corners, summing to 65536. */
            const int wa = (256 - wx) * (256 - wy), wb = wx * (256 - wy);
            const int wc = (256 - wx) * wy,         wd = wx * wy;

            const int r = (((a >> 11) & 0x1F) * wa + ((b >> 11) & 0x1F) * wb +
                           ((c >> 11) & 0x1F) * wc + ((d >> 11) & 0x1F) * wd) >> 16;
            const int g = (((a >> 5) & 0x3F) * wa + ((b >> 5) & 0x3F) * wb +
                           ((c >> 5) & 0x3F) * wc + ((d >> 5) & 0x3F) * wd) >> 16;
            const int bl = ((a & 0x1F) * wa + (b & 0x1F) * wb +
                            (c & 0x1F) * wc + (d & 0x1F) * wd) >> 16;
            dst[x] = (uint16_t)((r << 11) | (g << 5) | bl);
        }
    }

    const lv_color_t tint = average_of(target);

    xSemaphoreTake(s_mutex, portMAX_DELAY);
    s_prev = NULL;               /* appear, do not fade - see above */
    s_front = target;
    s_tint = tint;
    s_generation++;
    xSemaphoreGive(s_mutex);

    ESP_LOGI(TAG, "thumb: %d bytes, %dx%d upscaled, tint %02X%02X%02X",
             len, sd, out.height, tint.red, tint.green, tint.blue);
    return true;
}

static void art_task(void *arg)
{
    (void) arg;
    char url[sizeof(s_want_url)];
    char small[sizeof(s_want_small)];

    while (s_run) {
        if (xSemaphoreTake(s_wake, pdMS_TO_TICKS(500)) != pdTRUE) {
            /* Nothing to fetch. Age the connection out if it has gone quiet -
             * this is what stops 41 KB of mbedTLS sitting there for hours
             * between track changes. */
            if (s_http != NULL && s_last_fetch_us != 0 &&
                esp_timer_get_time() - s_last_fetch_us > ART_CONN_IDLE_US) {
                http_release();
                s_last_fetch_us = 0;
                ESP_LOGI(TAG, "connection closed after %d s idle",
                         (int)(ART_CONN_IDLE_US / 1000000));
            }
            continue;
        }
        if (!s_run) {
            break;
        }

        /* Going quiet happens here rather than inside albumart_stop, because
         * the connection belongs to this task and on_exit runs on the LVGL
         * thread - the whole app switch would freeze behind a blocking close. */
        if (s_idle) {
            http_release();
            xSemaphoreTake(s_mutex, portMAX_DELAY);
            s_front = NULL;
            s_prev = NULL;
            s_shown_url[0] = '\0';
            s_want_url[0] = '\0';
            s_shown_small[0] = '\0';
            s_want_small[0] = '\0';
            s_last_fetch_us = 0;
            xSemaphoreGive(s_mutex);
            continue;
        }

        xSemaphoreTake(s_mutex, portMAX_DELAY);
        snprintf(url, sizeof(url), "%s", s_want_url);
        snprintf(small, sizeof(small), "%s", s_want_small);
        const bool same = (strcmp(url, s_shown_url) == 0);
        xSemaphoreGive(s_mutex);

        if (url[0] == '\0' || same) {
            continue;
        }

        /* Stage one: the thumbnail. 2-4 KB, so it lands in a fraction of the
         * time the full cover takes and gets *something* of the right colour
         * on the glass immediately. Best effort - if it fails, stage two still
         * runs and the only loss is the blur. */
        if (small[0] != '\0' && strcmp(small, s_shown_small) != 0) {
            const int len = fetch(small, true);
            if (len > 0) {
                if (decode_thumb(len)) {
                    xSemaphoreTake(s_mutex, portMAX_DELAY);
                    snprintf(s_shown_small, sizeof(s_shown_small), "%s", small);
                    xSemaphoreGive(s_mutex);
                }
            }
        }

        /* If the track moved on while the thumbnail was in flight, `url` in
         * hand is already stale. Go back and read the current one rather than
         * opening a connection for a cover nobody is waiting for. */
        if (superseded(url, false)) {
            continue;
        }

        /* Stage two: the real cover. */
        const int64_t t0 = esp_timer_get_time();
        const int len = fetch(url, false);
        if (len <= 0) {
            continue;
        }
        const int64_t t_fetched = esp_timer_get_time();

        uint16_t *target = (s_front == s_art_a) ? s_art_b : s_art_a;

        esp_jpeg_image_cfg_t cfg = {
            .indata = s_jpeg,
            .indata_size = (uint32_t) len,
            .outbuf = (uint8_t *) target,
            .outbuf_size = ART_BYTES,
            .out_format = JPEG_IMAGE_FORMAT_RGB565,
            .out_scale = JPEG_IMAGE_SCALE_0,
            /* Native RGB565: the bloom writes native, and the panel's byte
             * swap happens once at flush in the lvgl_port config. Swapping
             * here as well would undo it. */
            .flags = { .swap_color_bytes = 0 },
        };
        esp_jpeg_image_output_t out = { 0 };
        const esp_err_t err = esp_jpeg_decode(&cfg, &out);
        if (err != ESP_OK) {
            ESP_LOGW(TAG, "decode failed: %s", esp_err_to_name(err));
            continue;
        }
        /* Covers are not always exactly square at the advertised size - a
         * 296x300 turned up on 2026-09-03. Decoding still fills the buffer
         * row-major at 300 stride, so it shows with a sliver of edge; not
         * worth a second code path. */
        if (out.width != ALBUMART_DIM || out.height != ALBUMART_DIM) {
            ESP_LOGW(TAG, "cover is %ux%u, expected %dx%d - shown anyway",
                     (unsigned) out.width, (unsigned) out.height,
                     ALBUMART_DIM, ALBUMART_DIM);
        }

        const lv_color_t tint = average_of(target);

        xSemaphoreTake(s_mutex, portMAX_DELAY);
        s_prev = s_front;
        s_front = target;
        s_tint = tint;
        s_generation++;
        snprintf(s_shown_url, sizeof(s_shown_url), "%s", url);
        xSemaphoreGive(s_mutex);

        ESP_LOGI(TAG, "cover: %d bytes in %lld ms, decoded in %lld ms, tint %02X%02X%02X",
                 len, (t_fetched - t0) / 1000,
                 (esp_timer_get_time() - t_fetched) / 1000,
                 tint.red, tint.green, tint.blue);
    }

    http_release();
    s_task = NULL;
    vTaskDelete(NULL);
}

esp_err_t albumart_start(void)
{
    if (s_mutex == NULL) {
        s_mutex = xSemaphoreCreateMutex();
        s_wake  = xSemaphoreCreateBinary();
        s_tint  = lv_color_hex(0xE47846);   /* the design's placeholder warmth */
    }
    if (s_mutex == NULL || s_wake == NULL) {
        return ESP_ERR_NO_MEM;
    }
    s_idle = false;
    if (s_task != NULL) {
        return ESP_OK;              /* already up; this just ends the idle */
    }

    if (s_art_a == NULL) {
        s_art_a = heap_caps_malloc(ART_BYTES, MALLOC_CAP_SPIRAM);
        s_art_b = heap_caps_malloc(ART_BYTES, MALLOC_CAP_SPIRAM);
        s_jpeg  = heap_caps_malloc(JPEG_MAX, MALLOC_CAP_SPIRAM);
        s_thumb = heap_caps_malloc(THUMB_MAX_DIM * THUMB_MAX_DIM * 2, MALLOC_CAP_SPIRAM);
        if (s_art_a == NULL || s_art_b == NULL || s_jpeg == NULL || s_thumb == NULL) {
            ESP_LOGE(TAG, "no PSRAM for the art buffers");
            s_idle = true;
            return ESP_ERR_NO_MEM;
        }
    }

    s_front = NULL;
    s_prev = NULL;
    s_shown_url[0] = '\0';
    s_want_url[0] = '\0';

    s_run = true;
    /* Pinned to core 1, away from LVGL.
     *
     * A 300x300 JPEG decode is fixed CPU work, and it measured anywhere from
     * 140 ms to 1702 ms across one session - a 12x spread on a number with no
     * network in it, which can only be the task not getting the CPU. LVGL runs
     * at priority 4 and this at 3, both unpinned, so they competed for core 0
     * while core 1 sat idle: the watchdog dumps caught exactly that, taskLVGL
     * on CPU 0 and IDLE1 on CPU 1 (2026-09-03).
     *
     * The decode has no reason to share a core with the compositor. Pinning it
     * away also means the cover arriving can no longer be slowed down by the
     * very transition that is waiting for it. */
    if (xTaskCreatePinnedToCore(art_task, "art", ART_TASK_STACK, NULL,
                                ART_TASK_PRIO, &s_task, 1) != pdPASS) {
        s_run = false;
        return ESP_FAIL;
    }
    return ESP_OK;
}

void albumart_stop(void)
{
    /* Returns immediately. The task notices within 500 ms, drops the cover and
     * closes its connection.
     *
     * Nothing is freed here. The three buffers - two 180 KB covers and the
     * 64 KB download - are allocated once on first use and kept for the life
     * of the device. That is BUILD.md's rule about never churning 180 KB per
     * track change, applied to app switches too: one permanent allocation is
     * exactly what keeps PSRAM returning to the *same* figure across ten
     * switches, which is what Wave 7 Checkpoint D measures. Freeing and
     * reallocating 424 KB every time you glance at the Clock is how that
     * number starts drifting.
     */
    s_idle = true;
    if (s_wake != NULL) {
        xSemaphoreGive(s_wake);
    }
}

void albumart_request(const char *url, const char *small_url)
{
    if (s_mutex == NULL || s_idle) {
        return;
    }
    xSemaphoreTake(s_mutex, portMAX_DELAY);
    const bool changed = (url != NULL) && (url[0] != '\0') &&
                         (strcmp(url, s_shown_url) != 0) &&
                         (strcmp(url, s_want_url) != 0);
    if (changed) {
        snprintf(s_want_url, sizeof(s_want_url), "%s", url);
        /* Both move in the same instant, so `superseded` abandons a stale
         * thumbnail fetch on exactly the track change that abandons a stale
         * cover fetch. */
        snprintf(s_want_small, sizeof(s_want_small), "%s",
                 (small_url != NULL) ? small_url : "");
    }
    xSemaphoreGive(s_mutex);

    if (changed) {
        xSemaphoreGive(s_wake);
    }
}
