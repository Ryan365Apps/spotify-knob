/* bloom.c - the phyllotaxis field. See bloom.h for what each lighting is for.
 *
 * Geometry is verbatim from `design/screens.html` rev W:
 *
 *   r    = sqrt(RI^2 + (i/N) * (RO^2 - RI^2))     equal-area packing
 *   a    = i * divergence + spin - pi/2           twelve o'clock is -pi/2
 *   t    = (r - RI) / (RO - RI)                   0 at the inner edge, 1 at the rim
 *   len  = (2.2 + r*0.045) * (0.4 + 1.35*hash(i)) uneven, so the field has grain
 *
 * r, t and len never change, so they are computed once and the per-frame work
 * is an angle and a line.
 *
 * ON DRAWING DIRECTLY INTO THE BUFFER. The first implementation of this called
 * lv_draw_line once per segment. LVGL's draw machinery - a task dispatch and a
 * blend pass each time - is built for a few shapes per frame, not three
 * hundred into a PSRAM buffer. On hardware it starved the LVGL task so
 * completely that the idle task never ran and the task watchdog fired
 * (2026-09-03). A segment is a handful of pixels. Writing them directly is
 * both faster and less code, and it measured 27 ms for the full 300.
 *
 * ON OPACITY. Every alpha here is roughly double the figure in screens.html.
 * That is not a change of intent - it is display calibration. The simulator's
 * range was set against a bright monitor; on this panel at the 40% working
 * backlight the segments came out at about RGB(74,28,8), which is not there at
 * all. Measured and corrected on hardware, 2026-09-03. Anything carried from
 * the simulator to the panel needs looking at on glass before it is believed.
 */

#include "bloom.h"

#include <math.h>
#include <string.h>

#define BLOOM_RI     86.0f
#define BLOOM_RO     170.0f
#define BLOOM_CX     180.0f
#define BLOOM_CY     180.0f
#define GOLDEN_RAD   2.39996323f          /* 137.507764 degrees */
#define DRIFT_RAD    0.00122173f          /* 0.07 degrees, either side */

static float s_r[BLOOM_N];                /* radius of each segment's midpoint */
static float s_t[BLOOM_N];                /* 0 at the inner edge, 1 at the rim */
static float s_len[BLOOM_N];              /* half-length, before any swell */
static bool  s_ready = false;

static int      s_px_written;
static uint16_t s_px_max;

/* The scatter that gives the field its grain. Deterministic, so the bloom is
 * the same figure on every boot rather than a different one each time. */
static float bloom_hash(int i)
{
    const float v = sinf((float) i * 12.9898f) * 43758.5453f;
    return v - floorf(v);
}

void bloom_init(void)
{
    if (s_ready) {
        return;
    }
    for (int i = 0; i < BLOOM_N; i++) {
        const float frac = (float) i / (float) BLOOM_N;
        const float r = sqrtf(BLOOM_RI * BLOOM_RI +
                              frac * (BLOOM_RO * BLOOM_RO - BLOOM_RI * BLOOM_RI));
        s_r[i]   = r;
        s_t[i]   = (r - BLOOM_RI) / (BLOOM_RO - BLOOM_RI);
        s_len[i] = (2.2f + r * 0.045f) * (0.4f + 1.35f * bloom_hash(i));
    }
    s_ready = true;
}

/* White, in the channel space px_blend actually works in.
 *
 * This exists because three call sites were passing 255, 255, 255 - which
 * looks like white and is not, because px_blend blends toward a *channel*
 * value: 0..31 for red and blue, 0..63 for green. Passing 255 makes every
 * channel saturate, but not at the same rate: at alpha 25 red and blue reach
 * 24 of their 31 levels while green reaches 24 of 63, so a "white" segment
 * comes out strongly magenta. That is the purple Ryan saw on the loading
 * spinner (2026-09-04), and it was in the unlit field of the dial screens
 * too.
 *
 * It is a separate fault from the per-channel *threshold* problem the Bayer
 * dither below fixes, and it was hiding underneath it. */
#define WHITE_R5 31
#define WHITE_G6 63
#define WHITE_B5 31

static inline void px_blend(uint16_t *buf, int x, int y,
                            int r5, int g6, int b5, int alpha)
{
    if (x < 0 || x >= BLOOM_CANVAS_W || y < 0 || y >= BLOOM_CANVAS_H) {
        return;
    }
    if (alpha <= 0) {
        return;
    }
    if (alpha > 255) {
        alpha = 255;
    }
    s_px_written++;
    uint16_t *p = &buf[y * BLOOM_CANVAS_W + x];
    const uint16_t c = *p;
    int dr = (c >> 11) & 0x1F, dg = (c >> 5) & 0x3F, db = c & 0x1F;

    /* Ordered dither on the sub-level remainder.
     *
     * RGB565 gives red and blue 32 levels and green 64. A truncating blend
     * therefore has *different thresholds per channel*: lighting a black pixel
     * white needs alpha >= 9 before red or blue move at all, but only >= 5 for
     * green. Anti-aliasing split each segment's alpha into small pieces and
     * dropped a lot of the unlit field straight into that gap, so those pixels
     * came out green - which on hardware read as coloured striping through the
     * unlit bloom while the lit wedge, whose alpha is far higher, looked
     * perfect (2026-09-03).
     *
     * A 4x4 Bayer offset spreads that sub-level remainder across neighbouring
     * pixels instead of discarding it. The faint parts of the field become a
     * stipple that averages to the right tone, which is what dithering is for,
     * and the per-channel thresholds stop mattering. */
    static const uint8_t BAYER[16] = {
         0,  8,  2, 10,
        12,  4, 14,  6,
         3, 11,  1,  9,
        15,  7, 13,  5,
    };
    const int d = (int) BAYER[((y & 3) << 2) | (x & 3)] << 4;   /* 0..240 */
    dr += ((r5 - dr) * alpha + d) >> 8;
    dg += ((g6 - dg) * alpha + d) >> 8;
    db += ((b5 - db) * alpha + d) >> 8;
    if (dr > 31) { dr = 31; }
    if (dg > 63) { dg = 63; }
    if (db > 31) { db = 31; }
    const uint16_t out = (uint16_t)((dr << 11) | (dg << 5) | db);
    *p = out;
    if (out > s_px_max) {
        s_px_max = out;
    }
}

/* One segment, centred at (cx,cy) and lying along (ca,sa) for +/-half.
 *
 * `width` is in pixels and may be fractional - the anti-aliasing below is what
 * makes a fraction mean anything. `glow` adds a faint halo either side,
 * standing in for the shadowBlur the design puts behind lit segments; a real
 * blur would cost far more than the field itself and read no differently at
 * 46 mm.
 */
static void draw_segment(uint16_t *buf, float cx, float cy, float ca, float sa,
                         float half, int r5, int g6, int b5, int alpha,
                         float width, bool glow)
{
    if (width < 1.0f) {
        width = 1.0f;
    }
    const float half_w = width * 0.5f;

    const float x0 = cx - ca * half, y0 = cy - sa * half;
    const float dx = 2.0f * ca * half, dy = 2.0f * sa * half;
    const float adx = fabsf(dx), ady = fabsf(dy);

    /* March the dominant axis one pixel at a time and fill a run across the
     * other one, with the end pixels of each run partially covered.
     *
     * The first anti-aliased version instead walked the perpendicular in unit
     * steps and splatted each sample bilinearly into four pixels, twice per
     * pixel of length. That is roughly twenty pixel writes where the original
     * did one, and pixel writes are the entire cost here - the canvas lives in
     * PSRAM, and the Clock measured 6060 writes at 26 ms. The dial screens,
     * which redraw on every detent, went from instant to visibly laggy
     * (hardware, 2026-09-03).
     *
     * A scanline run gives the same sub-pixel smoothness for about a fifth of
     * the writes, and it cannot double-count: each pixel is touched once per
     * segment rather than by several overlapping splats. */
    const bool x_major = (adx >= ady);
    const int steps = (int)(x_major ? adx : ady) + 1;
    const float sx = dx / (float) steps, sy = dy / (float) steps;

    /* A band of perpendicular width w cuts the minor axis over a longer span
     * the more slanted the segment is. */
    const float slant = x_major ? (1.0f / fmaxf(fabsf(ca), 0.2f))
                                : (1.0f / fmaxf(fabsf(sa), 0.2f));
    const float span = half_w * slant;

    float px = x0, py = y0;
    for (int s = 0; s <= steps; s++) {
        const float c  = x_major ? py : px;      /* centre on the minor axis */
        const float lo = c - span, hi = c + span;
        const int n0 = (int) floorf(lo), n1 = (int) floorf(hi);

        for (int n = n0; n <= n1; n++) {
            /* Coverage is how much of this pixel the band actually covers. */
            const float a0 = (lo > (float) n) ? lo : (float) n;
            const float a1 = (hi < (float) (n + 1)) ? hi : (float) (n + 1);
            float cov = a1 - a0;
            if (cov <= 0.0f) {
                continue;
            }
            if (cov > 1.0f) {
                cov = 1.0f;
            }
            const int a = (int)((float) alpha * cov);
            if (x_major) {
                px_blend(buf, (int)(px + 0.5f), n, r5, g6, b5, a);
            } else {
                px_blend(buf, n, (int)(py + 0.5f), r5, g6, b5, a);
            }
        }
        if (glow) {
            const int g = alpha >> 3;
            if (x_major) {
                px_blend(buf, (int)(px + 0.5f), n0 - 1, r5, g6, b5, g);
                px_blend(buf, (int)(px + 0.5f), n1 + 1, r5, g6, b5, g);
            } else {
                px_blend(buf, n0 - 1, (int)(py + 0.5f), r5, g6, b5, g);
                px_blend(buf, n1 + 1, (int)(py + 0.5f), r5, g6, b5, g);
            }
        }
        px += sx;
        py += sy;
    }
}
void bloom_draw_idle(uint16_t *buf, lv_color_t tint, float secs)
{
    bloom_init();

    /* Divergence must stay very close to the golden angle. Push it further and
     * the packing degenerates into a few thick spokes, which is precisely what
     * the golden angle uniquely avoids. The visible change comes from the
     * swell instead, which cannot degenerate because it never touches the
     * packing. */
    const float div  = GOLDEN_RAD + DRIFT_RAD * sinf(secs / 240.0f * 2.0f * (float) M_PI);
    const float spin = secs / 600.0f * 2.0f * (float) M_PI;
    const float swell_phase = secs / 34.0f * 2.0f * (float) M_PI;

    memset(buf, 0, BLOOM_CANVAS_SZ);
    s_px_written = 0;
    s_px_max = 0;

    const int r5 = tint.red >> 3, g6 = tint.green >> 2, b5 = tint.blue >> 3;

    for (int i = 0; i < BLOOM_N; i++) {
        const float a = (float) i * div + spin - (float) M_PI_2;
        const float ca = cosf(a), sa = sinf(a);
        const float swell = 0.72f + 0.42f * sinf(3.0f * a + swell_phase);
        const int alpha = (int)(255.0f * (0.10f + 0.55f * s_t[i] * swell));

        /* Fatter than the design's 0.8-1.3 px. Those figures were read off a
         * monitor showing the panel at about twice life size; at 46 mm they
         * came out as hairlines (2026-09-03). 1.6-3.4 px gives the field the
         * spindle shape it has in the reference rather than a wire frame. */
        draw_segment(buf, BLOOM_CX + ca * s_r[i], BLOOM_CY + sa * s_r[i],
                     ca, sa, s_len[i] * swell, r5, g6, b5, alpha,
                     1.6f + 1.8f * s_t[i], false);
    }
}

/* Fraction of the way clockwise from twelve, 0..1, for a segment at angle a.
 * The +pi/2 undoes the -pi/2 that put index 0 at twelve o'clock. */
static inline float angle_frac(float a)
{
    const float two_pi = 2.0f * (float) M_PI;
    float f = fmodf(a + (float) M_PI_2, two_pi);
    if (f < 0.0f) {
        f += two_pi;
    }
    return f / two_pi;
}

void bloom_draw_wedge(uint16_t *buf, lv_color_t lit, float pct, float band,
                      bool clear)
{
    bloom_init();

    if (pct < 0.0f) {
        pct = 0.0f;
    } else if (pct > 1.0f) {
        pct = 1.0f;
    }

    if (clear) {
        memset(buf, 0, BLOOM_CANVAS_SZ);
    }
    s_px_written = 0;
    s_px_max = 0;

    const int lr5 = lit.red >> 3, lg6 = lit.green >> 2, lb5 = lit.blue >> 3;
    const bool banded = (band > 0.0f);

    /* Unlit first, lit second: the lit pass carries a halo, and drawing it
     * last means the halo lands on top of its neighbours rather than under
     * them. Two passes over 300 segments is still nothing. */
    for (int pass = 0; pass < 2; pass++) {
        for (int i = 0; i < BLOOM_N; i++) {
            if (s_t[i] < band) {
                continue;          /* inside the band: artwork shows through */
            }
            const float a = (float) i * GOLDEN_RAD - (float) M_PI_2;
            const float frac = angle_frac(a);
            const bool on = (frac < pct);
            if (on != (pass == 1)) {
                continue;
            }
            /* Soften the last degree or so of the wedge.
             *
             * Lighting strictly by angle means each segment snaps fully on the
             * instant progress passes it, and because a phyllotaxis scatters
             * neighbours all round the field, those snaps land in unrelated
             * places - which is what made the progress rim sparkle rather than
             * advance on hardware (2026-09-03). Fading the segments within the
             * boundary band turns the edge into a gradient that sweeps. */
            const float EDGE = 0.02f;          /* ~7 degrees of the circle */
            float edge = 1.0f;
            if (on && frac > pct - EDGE) {
                edge = (pct - frac) / EDGE;    /* newest segments fade in */
            }
            if (edge < 0.0f) {
                edge = 0.0f;
            }
            const float ca = cosf(a), sa = sinf(a);
            const float cx = BLOOM_CX + ca * s_r[i];
            const float cy = BLOOM_CY + sa * s_r[i];

            if (on) {
                /* 0.34 + 0.66*t in the design, and bright enough already that
                 * it needs no calibration lift - unlike the unlit field. */
                const int alpha = (int)(255.0f * (0.34f + 0.66f * s_t[i]) * edge);
                draw_segment(buf, cx, cy, ca, sa, s_len[i], lr5, lg6, lb5,
                             alpha, 2.2f + 2.0f * s_t[i], true);
            } else {
                /* Doubled from the design for the panel, as at the top of this
                 * file. Banded rim sits over artwork, so it holds a flat value
                 * rather than fading inward - there is nothing inward of it. */
                /* The banded rim draws *nothing* where it is unlit.
                 *
                 * A flat 30% there made the whole ring read as white with the
                 * lit part barely distinguishable - the progress mark was
                 * competing with a full circle of the same colour instead of
                 * being the only thing on it (hardware, 2026-09-03). Time
                 * spent is visible; time remaining is not drawn.
                 *
                 * The full-field dial screens keep their faint unlit ground,
                 * because there the bloom *is* the screen and a wedge floating
                 * in nothing has no shape to sit in. */
                if (banded) {
                    continue;
                }
                const int alpha = (int)(255.0f * (0.08f + 0.40f * s_t[i]));
                draw_segment(buf, cx, cy, ca, sa, s_len[i],
                             WHITE_R5, WHITE_G6, WHITE_B5,
                             alpha, 1.6f + 1.8f * s_t[i], false);
            }
        }
    }
}

/* Tuned together: the tail is long and its ramp is smooth at both ends, so
 * discrete frames blend into each other instead of reading as steps. A short
 * sharp head is the thing that makes a low frame rate obvious. */
/* 1.92 s per turn, 20% slower than the 1.6 it shipped with - Ryan's call on
 * glass, 2026-09-04. Nothing else about the spinner changed, so the cost is
 * identical: the head still lights the same fraction of the ring, it just
 * takes longer to get round. */
#define SPIN_TURN_S   1.92f
#define SPIN_TAIL     0.45f       /* fraction of the circle the glow trails */
#define SPIN_BASE     0.10f       /* the always-present dim field */
#define SPIN_LIT      0.72f       /* added at the head */

/* A hue straight to RGB565 channel space, full saturation and full value.
 *
 * Six linear ramps and no divisions. It runs once per ray - 300 times for a
 * field that is then drawn once, and only for the lit ones on the head - so it
 * could be an order of magnitude more expensive and still not register against
 * the pixel writes, which are the whole cost here (BUILD.md section 6). */
static inline void hue_to_565(float h, int *r5, int *g6, int *b5)
{
    h -= floorf(h);
    const float x = h * 6.0f;
    int seg = (int) x;
    if (seg > 5) {
        seg = 5;
    }
    const float f = x - (float) seg;
    float r, g, b;
    switch (seg) {
    case 0:  r = 1.0f;     g = f;        b = 0.0f;     break;
    case 1:  r = 1.0f - f; g = 1.0f;     b = 0.0f;     break;
    case 2:  r = 0.0f;     g = 1.0f;     b = f;        break;
    case 3:  r = 0.0f;     g = 1.0f - f; b = 1.0f;     break;
    case 4:  r = f;        g = 0.0f;     b = 1.0f;     break;
    default: r = 1.0f;     g = 0.0f;     b = 1.0f - f; break;
    }
    *r5 = (int)(r * 31.0f + 0.5f);
    *g6 = (int)(g * 63.0f + 0.5f);
    *b5 = (int)(b * 31.0f + 0.5f);
}

static inline float spinner_lit(int i, float secs)
{
    const float a = (float) i * GOLDEN_RAD - (float) M_PI_2;
    float behind = fmodf(secs / SPIN_TURN_S, 1.0f) - angle_frac(a);
    if (behind < 0.0f) {
        behind += 1.0f;
    }
    if (behind >= SPIN_TAIL) {
        return 0.0f;
    }
    /* Smoothstep rather than a square. Squared gave a hard leading edge, which
     * is exactly what shows up the frame rate; this eases in and out. */
    const float k = 1.0f - (behind / SPIN_TAIL);
    return k * k * (3.0f - 2.0f * k);
}

void bloom_spinner_field(uint16_t *buf)
{
    bloom_init();
    memset(buf, 0, BLOOM_CANVAS_SZ);
    s_px_written = 0;
    s_px_max = 0;

    for (int i = 0; i < BLOOM_N; i++) {
        const float a = (float) i * GOLDEN_RAD - (float) M_PI_2;
        const float ca = cosf(a), sa = sinf(a);
        const int alpha = (int)(255.0f * SPIN_BASE * (0.35f + 0.65f * s_t[i]));
        /* The resting field stays neutral. A rainbow at 10% alpha is a rainbow
         * nobody can see - it is two or three RGB565 levels per channel, which
         * the dither turns into faint coloured noise rather than colour. The
         * spectrum belongs to the head, where there is enough alpha to carry
         * it. */
        draw_segment(buf, BLOOM_CX + ca * s_r[i], BLOOM_CY + sa * s_r[i],
                     ca, sa, s_len[i], WHITE_R5, WHITE_G6, WHITE_B5, alpha,
                     1.6f + 1.8f * s_t[i], false);
    }
}

void bloom_spinner_head(uint16_t *buf, float secs)
{
    bloom_init();
    s_px_written = 0;
    s_px_max = 0;

    for (int i = 0; i < BLOOM_N; i++) {
        const float lit = spinner_lit(i, secs);
        if (lit <= 0.01f) {
            continue;              /* most of the ring, most of the time */
        }
        const float a = (float) i * GOLDEN_RAD - (float) M_PI_2;
        const float ca = cosf(a), sa = sinf(a);
        const int alpha = (int)(255.0f * SPIN_LIT * lit * (0.35f + 0.65f * s_t[i]));

        /* Hue by where the ray sits on the circle, not by where it is in the
         * tail. The tail spans 45% of the ring, so at any moment the comet
         * carries about 160 degrees of spectrum trailing its head, and the
         * colours stay put while the light sweeps across them - which reads as
         * a rainbow being lit rather than a coloured object moving. */
        int r5, g6, b5;
        hue_to_565(angle_frac(a), &r5, &g6, &b5);

        draw_segment(buf, BLOOM_CX + ca * s_r[i], BLOOM_CY + sa * s_r[i],
                     ca, sa, s_len[i], r5, g6, b5, alpha,
                     1.6f + 1.8f * s_t[i], false);
    }
}

void bloom_draw_chip(uint16_t *buf, lv_color_t colour, float pct)
{
    bloom_init();

    if (pct < 0.0f) {
        pct = 0.0f;
    } else if (pct > 1.0f) {
        pct = 1.0f;
    }

    /* A disc riding the bezel at the exact progress angle. rev W puts it at
     * inset 9 px - outside the bloom's rim rather than within it - so it reads
     * as a mark on the edge of the glass rather than one more lit segment.
     *
     * It is the one precise thing on a deliberately ragged edge: the bloom
     * says roughly, the chip says exactly. That is why it earns its place on a
     * long podcast episode even when it is redundant on a three-minute track.
     */
    const float a  = pct * 2.0f * (float) M_PI - (float) M_PI_2;
    const float cx = BLOOM_CX + cosf(a) * 171.0f;
    const float cy = BLOOM_CY + sinf(a) * 171.0f;
    const int r5 = colour.red >> 3, g6 = colour.green >> 2, b5 = colour.blue >> 3;

    /* 11 px across in the design, plus a soft halo. Alpha falls off with the
     * square of the distance, which is cheap and reads as a glow at 46 mm. */
    const int rad = 8;
    for (int dy = -rad; dy <= rad; dy++) {
        for (int dx = -rad; dx <= rad; dx++) {
            const float d = sqrtf((float)(dx * dx + dy * dy));
            int alpha;
            if (d <= 5.0f) {
                alpha = 255;                                   /* the chip */
            } else if (d <= (float) rad) {
                const float f = 1.0f - (d - 5.0f) / ((float) rad - 5.0f);
                alpha = (int)(200.0f * f * f);                 /* the halo */
            } else {
                continue;
            }
            px_blend(buf, (int)(cx + 0.5f) + dx, (int)(cy + 0.5f) + dy,
                     r5, g6, b5, alpha);
        }
    }
}

int      bloom_last_px_written(void) { return s_px_written; }
uint16_t bloom_last_px_max(void)     { return s_px_max; }
