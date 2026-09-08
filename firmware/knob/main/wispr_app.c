/*
 * Wispr Flow (app 3). Drawn to design/screens.html rev W, screens 13 A (off)
 * and 13 B (capturing).
 *
 * The whole app is one keystroke. It does not talk to Wispr, know whether
 * Wispr is running, or need anything installed on the PC - it sends a combo
 * bound to Wispr's hands-free action and that is all. So there is nothing to
 * configure on screen and nothing to read, and the screen says only which way
 * to turn.
 *
 * The hard part is that hands-free is one toggle action rather than an on and
 * an off, so the device can only flip it and never set it. Three things make
 * that acceptable, all from BUILD.md section 6:
 *
 *   1. The dial is idempotent. Right means "I want it on" and left means "I
 *      want it off", so spinning right twice starts dictation once.
 *   2. Two spins the same way inside 2 s send the combo regardless of belief.
 *      That is the resync, and it is the only recovery needed.
 *   3. Wispr's own Flow Bar is the truth and is already on the screen you are
 *      looking at. A desync is visible before it is confusing.
 *
 * This screen therefore shows a belief and says so by never claiming more.
 * The elapsed time is counted from the moment the combo was sent, which is
 * honest about exactly what the device knows.
 *
 * Three detents, not one, because this must never fire from a knock.
 */
#include <math.h>
#include <stdbool.h>

#include "esp_log.h"
#include "esp_timer.h"

#include "esp_heap_caps.h"

#include "app_shell.h"
#include "bloom.h"
#include "hid.h"
#include "wispr_app.h"

static const char *TAG = "wispr";

/* rev W's palette. Red rather than green because every other red ring anyone
 * has seen means something is recording, and green already means volume
 * here. */
#define COL_LIVE      0xFF7A87
#define COL_GROUND    0x0A0B0D
#define COL_GREEN     0x3FE07A   /* rev W's green-lit: ready, not running */
#define COL_DIM_RING  0x1B1C1E   /* rgba(255,255,255,.09) over the ground */

#define SPIN_DETENTS      3
#define SPIN_GAP_MS     600      /* detents further apart than this are not one spin */
#define RESYNC_MS      2000

/* The breathe is stepped at 10 fps rather than animated at LVGL's refresh
 * rate. Changing the arc's opacity invalidates its whole bounding box, which
 * for a full-circle arc is effectively the screen - and BUILD.md section 6 is
 * blunt about counting per-frame work before flashing it. A 2.6 s breathe at
 * 10 fps is 26 steps, which is smooth for something this slow, and it is a
 * fifth of the redraws the default rate would have asked for. */
#define BREATHE_MS     2600      /* rev W's pulse period */

static lv_obj_t   *s_canvas = NULL;
static uint8_t    *s_canvas_buf = NULL;
static lv_obj_t   *s_mic = NULL;
static lv_obj_t   *s_mic_body = NULL;
static lv_obj_t   *s_mic_arc = NULL;
static lv_obj_t   *s_mic_stand = NULL;
static lv_obj_t   *s_state_label = NULL;
static lv_obj_t   *s_hint_label = NULL;
static lv_obj_t   *s_elapsed_label = NULL;
static lv_timer_t *s_ring_timer = NULL;

/* What the device believes, which is not what it knows. Deliberately not
 * persisted: after a reboot the device has no business claiming dictation is
 * running, and assuming off costs one spin to correct. */
static bool    s_believed_on = false;
static int64_t s_started_us = 0;

static int     s_accum = 0;          /* detents since the last spin or gap */
static int64_t s_last_detent_us = 0;
static int     s_last_spin_dir = 0;
static int64_t s_last_spin_us = 0;

static bool    s_swallow_click = false;

/* The ring lives further down, next to the reasoning about why it is a canvas
 * and not an lv_arc. paint() needs it first. */
/*
 * The ring is drawn into a canvas, never as an lv_arc.
 *
 * An LVGL arc rebooted the device twice (2026-09-04). LVGL draws one through
 * draw_border_complex -> lv_draw_sw_mask_radius_init, which builds an
 * anti-aliased mask for the whole 172 px radius **however small the
 * invalidated area is** - and the arc's bounding box is the entire screen, so
 * anything changing anywhere on the screen paid for it. Moving the animation
 * onto a 60 px object changed nothing at all, for that reason.
 *
 * bloom_draw_wedge at band 0.70 is the answer, and it is the same call the
 * Spotify progress rim already uses: only the outer 30% of the 300 segments
 * are drawn, so about 90 of them, roughly 1 500 pixel writes against the
 * Clock's measured 6 060 at 26 ms. Call it 7 ms a frame.
 */
#define RING_BAND    0.70f
#define RING_FPS_MS  200          /* 5 fps whenever the mark is moving */
#define SWEEP_TURN_S 4.0f         /* one lap of the rim; slow on purpose */

static void ring_draw(void)
{
    if (s_canvas_buf == NULL) {
        return;
    }
    uint16_t *buf = (uint16_t *) s_canvas_buf;
    const hid_state_t link = hid_state();

    /* A white rim with one coloured mark travelling round it.
     *
     * A whole rim in green was too much on glass (Ryan, 2026-09-05) - it read
     * as an alert rather than as readiness. White says "here is the edge of
     * the instrument" and the mark says "and it is awake", which is the same
     * division of labour the Spotify rim uses between its wedge and its chip.
     * bloom_draw_chip is that chip, and it takes an angle, so it costs one
     * disc a frame on top of a rim that only redraws when the colour changes.
     */
    const float secs = (float)(esp_timer_get_time() / 1000) / 1000.0f;
    const float phase = fmodf(secs / SWEEP_TURN_S, 1.0f);

    if (link == HID_STATE_CONNECTED && s_believed_on) {
        /* Live is the one state that should be impossible to miss, so here the
         * rim itself carries the colour. Red, because every other red ring
         * anyone has seen means something is recording. */
        const float k = 0.45f + 0.55f *
                        (0.5f + 0.5f * cosf(secs / (BREATHE_MS / 1000.0f) *
                                            2.0f * (float) M_PI));
        const lv_color_t red = lv_color_make((uint8_t)(0xFF * k),
                                             (uint8_t)(0x7A * k),
                                             (uint8_t)(0x87 * k));
        bloom_draw_wedge(buf, red, 1.0f, RING_BAND, true);
        bloom_draw_chip(buf, lv_color_hex(COL_LIVE), phase);
    } else if (link == HID_STATE_CONNECTED) {
        bloom_draw_wedge(buf, lv_color_hex(0xFFFFFF), 1.0f, RING_BAND, true);
        bloom_draw_chip(buf, lv_color_hex(COL_GREEN), phase);
    } else {
        /* No link: present, not inviting, and not going anywhere. */
        bloom_draw_wedge(buf, lv_color_hex(0x40444A), 1.0f, RING_BAND, true);
    }
    lv_obj_invalidate(s_canvas);
}

static void ring_timer_cb(lv_timer_t *t)
{
    (void) t;
    ring_draw();
}

/* The pulse only runs while it means something. At rest the ring is drawn once
 * on a state change and then costs nothing at all. */
static void ring_pulse_set(bool on)
{
    if (on && s_ring_timer == NULL) {
        s_ring_timer = lv_timer_create(ring_timer_cb, RING_FPS_MS, NULL);
    } else if (!on && s_ring_timer != NULL) {
        lv_timer_delete(s_ring_timer);
        s_ring_timer = NULL;
    }
}

/* --- what the screen says ------------------------------------------------ */

static void set_mic(uint32_t rgb)
{
    lv_obj_set_style_border_color(s_mic_body, lv_color_hex(rgb), 0);
    lv_obj_set_style_arc_color(s_mic_arc, lv_color_hex(rgb), LV_PART_MAIN);
    lv_obj_set_style_bg_color(s_mic_stand, lv_color_hex(rgb), 0);
}

static void set_line(const char *text, uint32_t rgb, const lv_font_t *font)
{
    lv_label_set_text(s_state_label, text);
    lv_obj_set_style_text_color(s_state_label, lv_color_hex(rgb), 0);
    lv_obj_set_style_text_font(s_state_label, font, 0);
}

static void elapsed_update(void)
{
    if (!s_believed_on || s_elapsed_label == NULL) {
        return;
    }
    const int s = (int)((esp_timer_get_time() - s_started_us) / 1000000);
    lv_label_set_text_fmt(s_elapsed_label, "%d:%02d", s / 60, s % 60);
}

static void paint(void)
{
    if (s_mic_body == NULL) {
        return;
    }
    const hid_state_t link = hid_state();

    /* Nothing to talk to. Say so here rather than only in the log: until
     * 2026-09-04 this screen looked identical paired and unpaired, and every
     * spin failed silently. */
    if (link != HID_STATE_CONNECTED) {
        set_mic(0x4D4D4D);
        lv_obj_add_flag(s_elapsed_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_hint_label, LV_OBJ_FLAG_HIDDEN);

        if (link == HID_STATE_PAIRING) {
            /* The passkey belongs on whatever screen you are standing on when
             * the PC asks for it, not only in Settings. */
            char pk[8];
            snprintf(pk, sizeof(pk), "%06lu", (unsigned long) hid_passkey());
            set_line(pk, 0xFFFFFF, &lv_font_montserrat_28);
            lv_label_set_text(s_hint_label, "TYPE THIS ON THE PC");
        } else if (link == HID_STATE_ADVERTISING) {
            set_line("Radial", 0xFFFFFF, &lv_font_montserrat_28);
            lv_label_set_text(s_hint_label, "ADD IT AS A BLUETOOTH KEYBOARD");
        } else {
            set_line("Dictation", 0xFFFFFF, &lv_font_montserrat_28);
            lv_label_set_text(s_hint_label, "NO KEYBOARD LINK");
        }
        ring_pulse_set(false);      /* nothing to say, nothing moving */
        ring_draw();
        return;
    }

    if (s_believed_on) {
        set_mic(COL_LIVE);
        set_line("Live", COL_LIVE, &lv_font_montserrat_28);
        lv_label_set_text(s_hint_label, "CLICK OR SPIN TO STOP");
        lv_obj_remove_flag(s_hint_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_remove_flag(s_elapsed_label, LV_OBJ_FLAG_HIDDEN);
    } else {
        /* White, not green. The travelling mark on the rim is the only green
         * on the screen, which is what lets it read as a state rather than as
         * decoration - and a green title fought the back chevron for the same
         * attention (Ryan, on glass, 2026-09-05). */
        set_mic(0xFFFFFF);
        set_line("Dictation", 0xFFFFFF, &lv_font_montserrat_28);
        lv_label_set_text(s_hint_label, "CLICK OR SPIN TO START");
        lv_obj_remove_flag(s_hint_label, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(s_elapsed_label, LV_OBJ_FLAG_HIDDEN);
    }
    /* The mark travels in both live and idle, so the timer runs whenever there
     * is a link at all - it is what says the device is awake. */
    ring_pulse_set(true);
    ring_draw();
}

/* --- the one thing it does ---------------------------------------------- */

static void send_toggle(const char *why)
{
    if (hid_send(HID_WISPR_TOGGLE) != ESP_OK) {
        /* Belief is only worth holding if the keystroke left. */
        ESP_LOGW(TAG, "combo not sent (%s) - belief unchanged", why);
        return;
    }
    s_believed_on = !s_believed_on;
    if (s_believed_on) {
        s_started_us = esp_timer_get_time();
    }
    shell_haptic_click();
    ESP_LOGI(TAG, "%s -> believed %s", why, s_believed_on ? "on" : "off");
    paint();
    elapsed_update();
}

/* One completed three-detent spin, direction signed. */
static void spin(int dir)
{
    const int64_t now = esp_timer_get_time();
    const bool resync = (dir == s_last_spin_dir) &&
                        (now - s_last_spin_us < (int64_t) RESYNC_MS * 1000);
    s_last_spin_dir = dir;
    s_last_spin_us = now;

    if (resync) {
        /* The only recovery gesture in the product: send regardless of what
         * the device believes, because the belief is what is wrong. */
        send_toggle("resync spin");
        return;
    }
    if (dir > 0 && !s_believed_on) {
        send_toggle("spin right");
    } else if (dir < 0 && s_believed_on) {
        send_toggle("spin left");
    } else {
        /* Idempotent by design. Spinning right when it is already believed on
         * does nothing, which is the whole reason for using direction rather
         * than a plain toggle. */
        ESP_LOGI(TAG, "spin %s ignored - already believed %s",
                 (dir > 0) ? "right" : "left", s_believed_on ? "on" : "off");
        shell_haptic_firm();
    }
}

static void wispr_on_dial(int delta)
{
    const int64_t now = esp_timer_get_time();

    /* Detents further apart than the gap are not one gesture. Without this a
     * slow drift over a minute would eventually add up to a spin. */
    if (now - s_last_detent_us > (int64_t) SPIN_GAP_MS * 1000) {
        s_accum = 0;
    }
    s_last_detent_us = now;

    /* A reversal starts a new count rather than cancelling out, so
     * right-right-left-left-left still reads as a left spin. */
    if ((s_accum > 0 && delta < 0) || (s_accum < 0 && delta > 0)) {
        s_accum = 0;
    }
    s_accum += delta;

    if (s_accum >= SPIN_DETENTS) {
        s_accum = 0;
        spin(+1);
    } else if (s_accum <= -SPIN_DETENTS) {
        s_accum = 0;
        spin(-1);
    }
}

/* Tap is the fast path when you are already looking at the screen: it always
 * sends, because you can see the state you are asking to change. The shell
 * owns the long-press on this same screen and LVGL sends CLICKED on release
 * either way, so the long-press has to be swallowed here - otherwise letting
 * go of one would toggle dictation underneath the selector. */
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
    send_toggle("tap");
}

/* --- the microphone ------------------------------------------------------
 *
 * Three shapes: the capsule, the arc cradling it, and the stand. Proportions
 * are rev W's 64-unit glyph scaled to whatever box it is given, so the same
 * drawing serves the app screen at 60 px and the menu's rim and centre at 28
 * and 52. Children are added body, arc, stand - wispr_on_enter relies on that
 * order to keep handles for recolouring. */
void wispr_draw_mic(lv_obj_t *into, int px, lv_color_t colour)
{
    const float k = (float) px / 60.0f;
    const int stroke = (int)(4.0f * k + 0.5f);

    lv_obj_t *body = lv_obj_create(into);
    lv_obj_remove_style_all(body);
    lv_obj_set_size(body, (int)(16 * k), (int)(28 * k));
    lv_obj_align(body, LV_ALIGN_CENTER, 0, (int)(-8 * k));
    lv_obj_remove_flag(body, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_radius(body, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_opa(body, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(body, stroke > 0 ? stroke : 1, 0);
    lv_obj_set_style_border_color(body, colour, 0);
    lv_obj_set_style_border_opa(body, LV_OPA_COVER, 0);

    lv_obj_t *arc = lv_arc_create(into);
    lv_obj_set_size(arc, (int)(28 * k), (int)(28 * k));
    lv_obj_align(arc, LV_ALIGN_CENTER, 0, (int)(-4 * k));
    lv_obj_remove_style(arc, NULL, LV_PART_KNOB);
    lv_obj_remove_flag(arc, LV_OBJ_FLAG_CLICKABLE);
    lv_arc_set_bg_angles(arc, 0, 180);        /* LVGL 0 deg is 3 o'clock */
    lv_arc_set_angles(arc, 0, 180);
    lv_obj_set_style_arc_width(arc, stroke > 0 ? stroke : 1, LV_PART_MAIN);
    lv_obj_set_style_arc_color(arc, colour, LV_PART_MAIN);
    lv_obj_set_style_arc_width(arc, 0, LV_PART_INDICATOR);
    lv_obj_set_style_arc_opa(arc, LV_OPA_TRANSP, LV_PART_INDICATOR);

    lv_obj_t *stand = lv_obj_create(into);
    lv_obj_remove_style_all(stand);
    lv_obj_set_size(stand, stroke > 0 ? stroke : 1, (int)(9 * k));
    lv_obj_align(stand, LV_ALIGN_CENTER, 0, (int)(16 * k));
    lv_obj_remove_flag(stand, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    lv_obj_set_style_bg_opa(stand, LV_OPA_COVER, 0);
    lv_obj_set_style_bg_color(stand, colour, 0);
    lv_obj_set_style_radius(stand, 2, 0);
}

/* What the menu calls to put a microphone on the rim instead of a telephone. */
static void mic_glyph(lv_obj_t *into, int px, lv_color_t colour)
{
    wispr_draw_mic(into, px, colour);
}

/* --- lifecycle ---------------------------------------------------------- */

static void wispr_on_enter(lv_obj_t *parent)
{
    /* The radio comes up here, not at boot. Spotify has just released its TLS
     * session in its own on_exit, so this is the moment there is internal RAM
     * to give - see the note on hid_start in hid.h. */
    hid_start();

    lv_obj_set_style_bg_color(parent, lv_color_hex(COL_GROUND), 0);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_CLICKED, NULL);
    lv_obj_add_event_cb(parent, screen_click_cb, LV_EVENT_LONG_PRESSED, NULL);

    /* The canvas carries the ring, and it goes in first so every label and the
     * mic sit over it. 259 KB of PSRAM, allocated here and freed in on_exit -
     * the same contract the Clock and Spotify screens keep. */
    s_canvas_buf = heap_caps_malloc(BLOOM_CANVAS_SZ, MALLOC_CAP_SPIRAM);
    if (s_canvas_buf != NULL) {
        bloom_init();
        s_canvas = lv_canvas_create(parent);
        lv_canvas_set_buffer(s_canvas, s_canvas_buf, BLOOM_CANVAS_W,
                             BLOOM_CANVAS_H, LV_COLOR_FORMAT_RGB565);
        lv_obj_center(s_canvas);
        lv_obj_remove_flag(s_canvas, LV_OBJ_FLAG_CLICKABLE);
        lv_canvas_fill_bg(s_canvas, lv_color_hex(COL_GROUND), LV_OPA_COVER);
    } else {
        ESP_LOGE(TAG, "no PSRAM for the ring canvas - running without it");
    }

    s_accum = 0;
    s_last_detent_us = 0;
    s_last_spin_dir = 0;
    s_last_spin_us = 0;
    s_swallow_click = false;

    /*
     * There is no rim ring on this screen, and that is a deviation from
     * design/screens.html rev W with a hardware reason behind it.
     *
     * A full-circle lv_arc rebooted the device twice (2026-09-04). LVGL draws
     * one through draw_border_complex -> lv_draw_sw_mask_radius_init, and that
     * builds an anti-aliased mask for the whole 172 px radius **however small
     * the invalidated area is**. The arc's bounding box is the entire screen,
     * so anything that changes anywhere - the breathing mic, the elapsed
     * seconds ticking over - lands inside it and pays the full mask build. The
     * first attempt at a fix moved the animation from the arc to the 60 px mic
     * and changed nothing at all, because the mic sits inside that same box.
     * Backtrace both times: circ_calc_aa4 -> lv_draw_sw_mask_radius_init ->
     * draw_border_complex -> lv_draw_sw_arc, taskLVGL running, IDLE0 starved.
     *
     * The mic and the word carry the state instead, which they already did -
     * red mic plus "Live" plus a running count is not ambiguous. If the ring
     * is wanted back it has to be drawn into a canvas by hand the way
     * bloom.c does it for the Spotify rim, not animated as an LVGL widget.
     */

    /* The mic. rev W's glyph is a stroke drawing of a capsule, the arc under
     * it and the stand, so that is exactly what it is made of. */
    lv_obj_t *mic = lv_obj_create(parent);
    s_mic = mic;
    lv_obj_remove_style_all(mic);
    lv_obj_set_size(mic, 60, 60);
    lv_obj_align(mic, LV_ALIGN_CENTER, 0, -38);
    lv_obj_remove_flag(mic, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    wispr_draw_mic(mic, 60, lv_color_white());
    s_mic_body  = lv_obj_get_child(mic, 0);
    s_mic_arc   = lv_obj_get_child(mic, 1);
    s_mic_stand = lv_obj_get_child(mic, 2);

    /* Sizes are a step or two above rev W's pixel figures, the same
     * correction Waves 5 and 6 had to make: those figures were read off a
     * monitor showing the panel at roughly twice life size, and everything
     * carried across straight was unreadable at 46 mm. */
    s_state_label = lv_label_create(parent);
    lv_obj_set_style_text_font(s_state_label, &lv_font_montserrat_28, 0);
    lv_obj_align(s_state_label, LV_ALIGN_CENTER, 0, 48);

    s_hint_label = lv_label_create(parent);
    lv_obj_set_style_text_font(s_hint_label, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_hint_label, lv_color_hex(0x6E7278), 0);
    lv_label_set_text(s_hint_label, "SPIN RIGHT TO START");
    lv_obj_align(s_hint_label, LV_ALIGN_CENTER, 0, 108);

    s_elapsed_label = lv_label_create(parent);
    lv_obj_set_style_text_font(s_elapsed_label, &lv_font_montserrat_24, 0);
    lv_obj_set_style_text_color(s_elapsed_label, lv_color_hex(0x8A8F96), 0);
    lv_label_set_text(s_elapsed_label, "0:00");
    /* Above the mic, not below the word. The count is the one thing here that
     * changes on its own, and under the hint it competed with the instruction
     * for the same corner of the eye. */
    lv_obj_align(s_elapsed_label, LV_ALIGN_CENTER, 0, -100);

    shell_back_button(parent);

    paint();          /* also draws the ring and starts the pulse if needed */
    elapsed_update();

    ESP_LOGI(TAG, "entered, believed %s%s", s_believed_on ? "on" : "off",
             hid_is_stub() ? " (HID is the Wave 10 stub)" : "");
}

static void wispr_on_exit(void)
{
    ring_pulse_set(false);
    /* The shell deletes the screen and every widget on it; this app holds no
     * buffers of its own, so there is nothing else to give back. The belief
     * survives on purpose - leaving the screen does not stop dictation, and
     * pretending otherwise would be the desync it is trying to avoid. */
    s_canvas = NULL;
    if (s_canvas_buf != NULL) {
        heap_caps_free(s_canvas_buf);
        s_canvas_buf = NULL;
    }
    s_mic = s_mic_body = s_mic_arc = s_mic_stand = NULL;
    s_state_label = s_hint_label = s_elapsed_label = NULL;

    /* Give the radio back. Always, even if dictation is still believed live.
     *
     * The alternative - hold it while live so stopping is instant - buys a
     * second and costs a silent failure: leave this screen mid-dictation and
     * Spotify quietly cannot reach the network until you happen to come back.
     * A predictable reconnect on re-entry is the better trade, and the bond is
     * in NVS so it is a reconnect rather than a re-pair. */
    hid_stop();
    ESP_LOGI(TAG, "exited, canvas freed, belief kept: %s", s_believed_on ? "on" : "off");
}

static void wispr_on_tick(void)
{
    /* The link state arrives from the BLE host task, so this screen has to
     * notice it rather than be told. Repaint only when it actually moves. */
    static hid_state_t last_link = (hid_state_t) -1;
    static uint32_t last_passkey = 0;
    const hid_state_t link = hid_state();
    const uint32_t passkey = hid_passkey();
    if (link != last_link || passkey != last_passkey) {
        last_link = link;
        last_passkey = passkey;
        paint();
    }
    elapsed_update();
}

/* The breathe invalidates a full-circle arc every 100 ms. Invisible under the
 * menu, and not free. */
static void wispr_on_pause(void)
{
    /* The menu covers this screen completely, so the ring pulse is drawing
     * into a canvas nobody can see, on the same thread the menu is animating
     * its own ring on. */
    ring_pulse_set(false);
}

static void wispr_on_resume(void)
{
    paint();          /* repaint, and restart the pulse if it is still live */
}

const knob_app_t wispr_app = {
    .name = "Dictation",
    .glyph = LV_SYMBOL_CALL,      /* fallback only; draw_glyph wins */
    .draw_glyph = mic_glyph,
    .accent = LV_COLOR_MAKE(0xFF, 0x7A, 0x87),
    .on_enter = wispr_on_enter,
    .on_exit = wispr_on_exit,
    .on_dial = wispr_on_dial,
    .on_tick = wispr_on_tick,
    .on_pause = wispr_on_pause,
    .on_resume = wispr_on_resume,
};
