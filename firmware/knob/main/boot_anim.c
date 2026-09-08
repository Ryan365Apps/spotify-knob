/* boot_anim.c - see boot_anim.h. Drawn to design/boot-sequence.html. */

#include <math.h>
#include <string.h>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "boot_anim.h"

static const char *TAG = "boot";

#define CANVAS_W  360
#define CANVAS_H  360
#define CANVAS_SZ ((size_t) CANVAS_W * CANVAS_H * 2)
#define CX        180.0f
#define CY        180.0f
#define RIM       170.0f

/* The design is authored at 1080 px. Every length in it is written in those
 * units, so one factor converts the lot rather than each constant being
 * re-derived by hand and quietly drifting. */
#define U         (360.0f / 1080.0f)

/*
 * 800 points, and each one small.
 *
 * The design has 2 600 at 1080 px, where the mean spacing works out at about
 * 17.7 px and a dot is 2.5-8.3 px across. What makes it read as a field of
 * fine points rather than a smear is that ratio - roughly a third - and the
 * ratio is what has to survive the change of scale, not the count.
 *
 * The first attempt kept the count proportional to *area* (300) and then made
 * every dot 1.6x larger to cover the gaps. That is backwards: it produced 300
 * fat blobs overlapping into mush, which is what blurry looks like when it is
 * the code rather than the panel. Going the other way - many more points, each
 * at its honest size - costs the same pixels and looks like the drawing.
 *
 * At 600 the spacing is about 12 px against a dot of 0.8-2.6 px. Still denser
 * than the design's ratio and clearly separated.
 *
 * The count and the radius cap were both cut on 2026-09-06 after the frame
 * timer went in: 800 points with a 3.2 px cap measured 19 548 writes and a
 * 105 ms worst frame against a 66 ms budget, so the run was playing at about
 * 9 fps. The estimate that preceded the measurement said 6 400. Estimating
 * pixel writes is not a substitute for counting them.
 */
#define N 600

/* 15 fps. The counter below reports the worst frame, so this stays a
 * measurement rather than an assumption (BUILD.md section 6). */
#define FRAME_MS 66

/* Strict scaling from the design's 1080 px. It was 1.6x, and that multiplier
 * was the blur. */
#define RAD_SCALE 1.0f

/* --- the timeline, in seconds, verbatim from the design ------------------ */
#define T_SWELL0     2.55f
#define T_SWELL1     4.10f
#define T_RUN0       3.20f
#define T_RUN1       7.20f
#define T_STRIKE     7.20f
#define T_COL0       7.75f
#define T_COL_D      1.15f
#define T_BEATS0     8.90f
#define T_BEAT_P     1.30f        /* ~46 bpm */
#define T_WORD0      9.20f
#define T_WORD1     10.40f

#define BEAT_LIFE    1.15f
#define SECOND_GAP   0.23f

static lv_obj_t   *s_canvas = NULL;
static lv_obj_t   *s_word = NULL;
static uint16_t   *s_buf = NULL;
static lv_timer_t *s_timer = NULL;
static int64_t     s_t0_us = 0;
static int         s_px_worst = 0;
static int         s_ms_worst = 0;
static int         s_px_frame = 0;
static bool        s_px_logged = false;

/* Bytes, not floats. Three float arrays at 800 points would be 9.6 KB of the
 * scarcest memory on this board for values that only ever need a couple of
 * digits of precision. */
static uint8_t s_hash1[N];    /* granular ignition */
static uint8_t s_hash2[N];    /* flare weight      */
static uint8_t s_hash3[N];    /* bed weight        */
#define H(a, i) ((float)(a)[i] * (1.0f / 255.0f))

/* --- maths -------------------------------------------------------------- */

static inline float clamp01(float x)
{
    return x < 0.0f ? 0.0f : (x > 1.0f ? 1.0f : x);
}

static inline float seg(float t, float a, float b)
{
    return clamp01((t - a) / (b - a));
}

static inline float ease_out(float p)
{
    const float q = 1.0f - p;
    return 1.0f - q * q * q;
}

static inline float gauss(float x, float w)
{
    const float q = x / w;
    return expf(-q * q);
}

static float hashf(float i)
{
    const float x = sinf(i * 127.1f + 311.7f) * 43758.5453f;
    return x - floorf(x);
}

/*
 * The emission ramp, verbatim. Oxblood at the edge of visibility through to a
 * hot core that only the blinks and the rim strike ever reach. Deep red
 * throughout, which is the one place this device is allowed to be theatrical -
 * red is reserved for recording and for mute, never for the music.
 */
static void ramp(float v, int *r, int *g, int *b)
{
    static const float STOP_V[5] = { 0.00f, 0.28f, 0.55f, 0.80f, 1.00f };
    static const int   STOP_C[5][3] = {
        {  24,   1,   4 }, {  88,   4,  12 }, { 168,  11,  25 },
        { 232,  36,  38 }, { 255, 158, 126 },
    };
    v = clamp01(v);
    for (int i = 1; i < 5; i++) {
        if (v <= STOP_V[i]) {
            const float f = (v - STOP_V[i - 1]) / (STOP_V[i] - STOP_V[i - 1]);
            *r = (int)(STOP_C[i - 1][0] + (STOP_C[i][0] - STOP_C[i - 1][0]) * f);
            *g = (int)(STOP_C[i - 1][1] + (STOP_C[i][1] - STOP_C[i - 1][1]) * f);
            *b = (int)(STOP_C[i - 1][2] + (STOP_C[i][2] - STOP_C[i - 1][2]) * f);
            return;
        }
    }
    *r = STOP_C[4][0]; *g = STOP_C[4][1]; *b = STOP_C[4][2];
}

/*
 * Additive. The design composites with "lighter" - everything is emitted
 * light, so overlapping points add rather than replace, which is what takes
 * the centre hot without any single point being drawn hot.
 *
 * The channel values are RGB565 channel space, 0-31 for red and blue and 0-63
 * for green. Passing 8-bit values here is what made the loading spinner purple
 * (BUILD.md section 6): green has twice the levels, so the same number reaches
 * a different fraction of full.
 */
static inline void px_add(int x, int y, int r5, int g6, int b5)
{
    if (x < 0 || x >= CANVAS_W || y < 0 || y >= CANVAS_H) {
        return;
    }
    uint16_t *p = &s_buf[y * CANVAS_W + x];
    const uint16_t c = *p;
    int dr = ((c >> 11) & 0x1F) + r5;
    int dg = ((c >> 5) & 0x3F) + g6;
    int db = (c & 0x1F) + b5;
    if (dr > 31) { dr = 31; }
    if (dg > 63) { dg = 63; }
    if (db > 31) { db = 31; }
    *p = (uint16_t)((dr << 11) | (dg << 5) | db);
    s_px_frame++;
}

/*
 * One point of light, placed to sub-pixel accuracy.
 *
 * Two things here decide whether the field reads as fine points or as a smear,
 * and the first version got both wrong.
 *
 * **The centre is not rounded.** Distance is measured from the true fractional
 * position, so a dot moving across the screen slides rather than snapping from
 * one pixel column to the next. On a 2 px dot that snapping is the whole
 * difference, and it is the same fault BUILD.md section 6 already records for
 * the bloom's rasteriser - the fix there was sub-pixel coverage and it is the
 * fix here too.
 *
 * **The falloff is tight.** It was (1 - d2/r2)^2, which spreads most of a
 * dot's light into its outer half and reads as fog. This is a Gaussian on the
 * true distance with the tail cut at the radius: a defined core, a short edge,
 * and nothing beyond it.
 */
static void blob(float cx, float cy, float rad, float v)
{
    if (v <= 0.012f) {
        return;
    }
    if (rad < 0.62f) {
        rad = 0.62f;      /* never smaller than a pixel can show */
    }
    int r8, g8, b8;
    ramp(v, &r8, &g8, &b8);

    const int x0 = (int)floorf(cx - rad), x1 = (int)ceilf(cx + rad);
    const int y0 = (int)floorf(cy - rad), y1 = (int)ceilf(cy + rad);
    const float rr = rad * rad;
    /* 2.6 puts the Gaussian at about 7% of peak where it is cut, so the edge
     * lands without a visible step and without a halo. */
    const float k = -2.6f / rr;

    for (int y = y0; y <= y1; y++) {
        const float ddy = (float) y - cy;
        for (int x = x0; x <= x1; x++) {
            const float ddx = (float) x - cx;
            const float d2 = ddx * ddx + ddy * ddy;
            if (d2 > rr) {
                continue;
            }
            const float a = expf(d2 * k) * v;
            if (a < 0.008f) {
                continue;
            }
            px_add(x, y, (int)(r8 * a * 0.125f), (int)(g8 * a * 0.25f),
                   (int)(b8 * a * 0.125f));
        }
    }
}

/* --- the fronts --------------------------------------------------------- */

/*
 * Everything is a front: a radius, a softness and an amplitude. The run, the
 * collapse and every heartbeat are the same visual event at different times,
 * and every point sums the flare of every live front. That is the design's
 * own structure and it is why the heartbeat reads as the run firing again
 * rather than as a separate glow - because it is.
 */
#define MAX_FRONTS 10
static float s_fr_r[MAX_FRONTS];
static float s_fr_s[MAX_FRONTS];
static float s_fr_a[MAX_FRONTS];
static int   s_fr_n;

/* Velocity-matched at the rim, then accelerating away, so the head leaves the
 * edge without a kink in its speed. */
static float front_base(float t)
{
    if (t <= T_RUN1) {
        return RIM * powf(seg(t, T_RUN0, T_RUN1), 1.42f);
    }
    const float x = t - T_RUN1;
    return RIM * (1.0f + 0.355f * x + 0.45f * x * x);
}

static inline float collapse_p(float t)
{
    return seg(t, T_COL0, T_COL0 + T_COL_D);
}

static void push_front(float r, float soft, float amp)
{
    if (s_fr_n >= MAX_FRONTS || amp < 0.02f) {
        return;
    }
    s_fr_r[s_fr_n] = r;
    s_fr_s[s_fr_n] = soft;
    s_fr_a[s_fr_n] = amp;
    s_fr_n++;
}

static void build_fronts(float t)
{
    s_fr_n = 0;

    /* The spiral run, growing out of the ember and sliding off the edge. */
    if (t >= T_RUN0) {
        const float b = front_base(t);
        if (b < RIM * 1.45f) {
            push_front(b, (16.0f + 62.0f * clamp01(b / RIM)) * U, 1.0f);
        }
    }

    /* The collapse: the run in reverse, accelerating as it converges. */
    const float cp = collapse_p(t);
    if (cp > 0.0f && cp < 1.0f) {
        const float h = RIM * (1.0f - powf(cp, 1.9f));
        push_front(h, (26.0f + 52.0f * (h / RIM)) * U,
                   0.95f * fminf(1.0f, cp / 0.10f) * (1.0f - 0.22f * cp));
    }

    /* The heartbeats: a strong front, a weaker second sound 0.23 s behind,
     * then rest. Three cycles are kept alive, so the waves overlap. */
    if (t >= T_BEATS0) {
        const float tt = t - T_BEATS0;
        const int n = (int)(tt / T_BEAT_P);
        for (int k = 0; k <= 2; k++) {
            const int bi = n - k;
            if (bi < 0) {
                continue;
            }
            const float decay = 1.0f - 0.38f * clamp01((float) bi / 4.0f);
            for (int v = 0; v < 2; v++) {
                const float age = tt - (float) bi * T_BEAT_P - (v ? SECOND_GAP : 0.0f);
                if (age < 0.0f || age > BEAT_LIFE) {
                    continue;
                }
                const float q = age / BEAT_LIFE;
                const float pos = powf(q, 0.80f);
                const float amp = (v ? 0.52f : 1.0f) * decay * powf(1.0f - q, 1.15f);
                push_front(RIM * pos * 0.98f, (24.0f + 54.0f * pos) * U, amp);
            }
        }
    }
}

/* --- the frame ---------------------------------------------------------- */

static void render(float t)
{
    memset(s_buf, 0, CANVAS_SZ);
    s_px_frame = 0;

    /* Three rapid blinks, then two seconds of black - long enough that you
     * start to wonder, which is the whole point of it. */
    if ((t >= 0.00f && t < 0.11f) || (t >= 0.22f && t < 0.33f) ||
        (t >= 0.44f && t < 0.55f)) {
        blob(CX, CY, 34.0f, 1.0f);
        return;
    }

    /* The ember, growing without stopping. It overruns the start of the run on
     * purpose: nothing hands over. */
    const float swell = seg(t, T_SWELL0, T_SWELL1);
    if (swell > 0.0f) {
        blob(CX, CY, (6.0f + 26.0f * swell) * U * 2.4f, 0.30f + 0.50f * swell);
    }

    build_fronts(t);
    if (s_fr_n == 0 && swell <= 0.0f) {
        return;
    }

    const float run_r = front_base(t);
    const bool  lit = (t >= T_STRIKE);            /* the run has passed everything */
    const float lift = 0.05f * seg(t, T_STRIKE, T_STRIKE + 0.50f);

    /*
     * The spin is what makes it a spiral run rather than an expanding circle.
     *
     * Outer points are carried further than inner ones - the angle gains
     * spin * (1 + 0.55 * r/rim) - so the whole field shears as the front
     * passes through it. Without this the geometry is right and the motion is
     * wrong, which is exactly how the first version of this looked.
     */
    const float spin = 0.46f * ease_out(seg(t, T_RUN0, T_STRIKE + 0.60f));

    /* Nothing beyond the outermost live front plus its reach is lit, and r
     * rises with i, so the loop can stop rather than test every point. */
    float maxr = 0.0f;
    for (int f = 0; f < s_fr_n; f++) {
        const float e = s_fr_r[f] + s_fr_s[f] * 2.4f;
        if (e > maxr) {
            maxr = e;
        }
    }
    maxr = lit ? RIM * 1.6f : maxr + 12.0f * U;

    const float GOLD = (float) M_PI * (3.0f - sqrtf(5.0f));
    const float C = RIM / sqrtf((float) N);

    for (int i = 1; i <= N; i++) {
        const float r = C * sqrtf((float) i);
        if (r > maxr) {
            break;
        }
        const int h = i - 1;

        /* Granular ignition: each point's effective radius is offset by a hash
         * of its index, so embers catch slightly early or late. The front
         * stays circular; only its edge is grainy. */
        const float reff = r + (H(s_hash1, h) - 0.5f) * 20.0f * U;

        float flare = 0.0f;
        for (int f = 0; f < s_fr_n; f++) {
            const float dd = reff - s_fr_r[f];
            const float sf = s_fr_s[f];
            if (dd < -2.6f * sf || dd > 2.6f * sf) {
                continue;                  /* cheap reject before the exp */
            }
            flare += s_fr_a[f] * gauss(dd, sf);
        }
        flare *= (0.72f + 0.56f * H(s_hash2, h));

        const bool on = lit || (reff < run_r);
        const float bed = on ? (0.13f + 0.27f * (r / RIM)) *
                               (0.80f + 0.40f * H(s_hash3, h)) : 0.0f;
        const float v = clamp01(bed + flare * 0.92f + (on ? lift : 0.0f));
        if (v <= 0.015f) {
            continue;
        }

        const float a = (float) i * GOLD + spin * (1.0f + (r / RIM) * 0.55f);
        const float rw = r + 2.6f * U * sinf((float) i * 0.41f + t * 0.90f);
        const float aw = a + (2.2f * U / fmaxf(r, 9.0f * U)) *
                             sinf((float) i * 0.29f - t * 0.75f);
        /* The flare grows a point as the front passes through it, and that
         * growth has to be bounded or it dominates everything.
         *
         * Measured on hardware 2026-09-06: the run peaked at 48 775 pixel
         * writes a frame - eight times the estimate, and about 210 ms against
         * the Clock's 6 060 writes at 26 ms, so the run was playing at 5 fps
         * rather than 15. Nearly all of it was here. A point at the front
         * reached 1 + 1.28 * 1.8 = 3.3x its radius, which is eleven times the
         * area, and a fifth of the field is inside the front's reach at any
         * moment.
         *
         * The brightness already carries most of what the flare is saying, so
         * the growth is halved and then capped. */
        float rad = (2.5f + 5.8f * (r / RIM)) * U * RAD_SCALE *
                    (1.0f + flare * 0.9f);
        if (rad > 2.6f) {
            rad = 2.6f;
        }

        blob(CX + cosf(aw) * rw, CY + sinf(aw) * rw, rad, v);
    }

    if (s_px_frame > s_px_worst) {
        s_px_worst = s_px_frame;
    }
}

static void frame_cb(lv_timer_t *timer)
{
    (void) timer;
    if (s_buf == NULL) {
        return;
    }
    const float t = boot_anim_elapsed();
    const int64_t t0 = esp_timer_get_time();
    render(t);
    const int ms = (int)((esp_timer_get_time() - t0) / 1000);
    if (ms > s_ms_worst) {
        s_ms_worst = ms;
    }

    /* The wordmark fades in over the first heartbeat. TORQUE OS is the
     * wordmark on both builds - the design's own note says as much, and says
     * it is the longer of the two so it is what the fitting was written
     * against. Michroma is not on this device (BUILD.md section 10 has that
     * as an open question), so it is Montserrat, tracked out. */
    if (s_word != NULL) {
        const float a = seg(t, T_WORD0, T_WORD1);
        lv_obj_set_style_text_opa(s_word, (lv_opa_t)(242.0f * a), 0);
    }

    lv_obj_invalidate(s_canvas);

    if (!s_px_logged && t > T_STRIKE) {
        s_px_logged = true;
        /* Writes and milliseconds, because the write count only means
         * something next to a time. */
        ESP_LOGI(TAG, "run peaked at %d writes a frame, worst frame %d ms "
                      "(%d points, budget %d ms)",
                 s_px_worst, s_ms_worst, N, FRAME_MS);
    }
}

/* --- lifecycle ---------------------------------------------------------- */

void boot_anim_start(lv_obj_t *parent)
{
    if (s_buf != NULL) {
        return;
    }
    s_buf = heap_caps_malloc(CANVAS_SZ, MALLOC_CAP_SPIRAM);
    if (s_buf == NULL) {
        ESP_LOGE(TAG, "no PSRAM for the boot canvas - skipping the sequence");
        return;
    }
    for (int i = 0; i < N; i++) {
        s_hash1[i] = (uint8_t)(hashf((float)(i + 1)) * 255.0f);
        s_hash2[i] = (uint8_t)(hashf((float)((i + 1) * 3 + 7)) * 255.0f);
        s_hash3[i] = (uint8_t)(hashf((float)((i + 1) * 5 + 3)) * 255.0f);
    }
    s_px_worst = 0;
    s_ms_worst = 0;
    s_px_logged = false;

    lv_obj_set_style_bg_color(parent, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(parent, LV_OPA_COVER, 0);

    s_canvas = lv_canvas_create(parent);
    lv_canvas_set_buffer(s_canvas, s_buf, CANVAS_W, CANVAS_H, LV_COLOR_FORMAT_RGB565);
    lv_obj_center(s_canvas);
    lv_obj_remove_flag(s_canvas, LV_OBJ_FLAG_CLICKABLE);
    memset(s_buf, 0, CANVAS_SZ);

    s_word = lv_label_create(parent);
    lv_obj_set_style_text_font(s_word, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(s_word, lv_color_hex(0xD61424), 0);
    lv_obj_set_style_text_letter_space(s_word, 8, 0);
    lv_obj_set_style_text_opa(s_word, LV_OPA_TRANSP, 0);
    lv_label_set_text(s_word, "TORQUE OS");
    lv_obj_center(s_word);
    lv_obj_remove_flag(s_word, LV_OBJ_FLAG_CLICKABLE);

    s_t0_us = esp_timer_get_time();
    s_timer = lv_timer_create(frame_cb, FRAME_MS, NULL);
    ESP_LOGI(TAG, "boot sequence started, %d points at %d fps", N, 1000 / FRAME_MS);
}

float boot_anim_elapsed(void)
{
    if (s_t0_us == 0) {
        return 0.0f;
    }
    return (float)((esp_timer_get_time() - s_t0_us) / 1000) / 1000.0f;
}

bool boot_anim_at_heartbeat(void)
{
    return s_buf == NULL || boot_anim_elapsed() >= T_BEATS0;
}

bool boot_anim_running(void)
{
    return s_buf != NULL;
}

void boot_anim_stop(void)
{
    if (s_timer != NULL) {
        lv_timer_delete(s_timer);
        s_timer = NULL;
    }
    s_canvas = NULL;
    s_word = NULL;        /* both live on the layer the shell deletes */
    if (s_buf != NULL) {
        heap_caps_free(s_buf);
        s_buf = NULL;
        ESP_LOGI(TAG, "boot sequence ended, canvas freed, worst frame %d writes",
                 s_px_worst);
    }
}
