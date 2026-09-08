/*
 * The app-shell contract (BUILD.md section 6, R9 - the requirement that the
 * firmware is an app shell hosting apps behind one interface).
 *
 * The shell owns everything shared and nothing app-specific: Wi-Fi, the token,
 * the haptic driver, dial dispatch, the 1 Hz tick, and (from Wave 7) the
 * selector. Apps own their screen, their network calls and their buffers, and
 * free all of it in on_exit. One app is active at a time; the rest are
 * stopped, not hidden.
 *
 * Nothing above this seam mentions Spotify, HTTP or JSON.
 */
#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "lvgl.h"

typedef struct {
    const char *name;          /* shown in the selector            */
    const void *glyph;         /* selector icon, as a font symbol  */

    /* Optional, and only for an app whose icon does not exist in the font.
     *
     * LVGL's symbol set has no microphone - it runs to speakers, bells,
     * keyboards and a telephone handset - so Dictation drew as a phone, which
     * is the wrong idea entirely. An app that needs a shape the font cannot
     * spell draws it here from primitives instead, into a square container of
     * `px`, using `colour` for every stroke. Leave it NULL and `glyph` is
     * used. */
    void (*draw_glyph)(lv_obj_t *into, int px, lv_color_t colour);
    lv_color_t  accent;        /* the app's colour in the UI       */

    void (*on_enter)(lv_obj_t *parent);   /* build widgets, start polling */
    void (*on_exit)(void);                /* free buffers, stop polling   */
    void (*on_dial)(int delta);           /* detents, signed              */
    void (*on_tick)(void);                /* ~1 Hz housekeeping           */

    /* Optional. The menu has opened over you, or has closed again.
     *
     * You are still the active app and you keep every buffer - this is not a
     * small on_exit. It means: stop animating. The menu covers you completely,
     * so anything you draw is thrown away, and on this device that waste is
     * not free. The Clock's bloom is 27 ms of work per render on the LVGL
     * thread, and 27 ms landing in the middle of a 33 ms animation frame is a
     * visible stutter in the ring the menu is trying to turn.
     *
     * Pause your timers, do not delete them. Leave polling alone: it costs the
     * LVGL thread nothing and stopping it would make coming back slower. */
    void (*on_pause)(void);
    void (*on_resume)(void);

    /* Optional. Has this app got anything worth looking at yet?
     *
     * The boot sequence uses it to decide when to get out of the way. Without
     * it the sequence ended on its own clock, Spotify was entered a moment
     * later with no state, and its connecting field flashed up for a second
     * before the first poll landed - one animation cutting to a different one
     * and back, which is worse than either. Now the app is entered *behind*
     * the boot sequence and the sequence lifts when this says yes. */
    bool (*is_ready)(void);
} knob_app_t;

/* Shell services available to apps. */

/* Copy the current access token into buf. ESP_ERR_INVALID_STATE before the
 * first refresh has succeeded. */
esp_err_t shell_token_get(char *buf, size_t buf_len);

/* Force a refresh now (an app saw a 401). Blocks until done or failed. */
esp_err_t shell_token_refresh_now(void);

/* True once the refresh token has been declared dead (invalid_grant) - the
 * app should show its re-auth state and stop polling. */
bool shell_auth_dead(void);

/* --- haptics -------------------------------------------------------------
 * The shell owns the DRV2605 and fires one click per detent by itself. These
 * are for the extra feedback an app asks for; no app ever touches I2C.
 * Vocabulary in docs/SOFTWARE-INTERACTION-CORE.md. */
void shell_haptic_click(void);   /* a detent accepted */
void shell_haptic_firm(void);    /* a press, or a clamp refusing a detent */

/* --- the timer -----------------------------------------------------------
 * The shell owns the clock (BUILD.md section 6), so it owns the timer with
 * it: a timer that stopped counting when you left the Clock app would be
 * useless, and it has to fire wherever you are. The Clock app is its UI, not
 * its owner - the same split as the token and the Spotify app.
 *
 * Sixty detents, sixty minutes. Setting 0 cancels. */
void shell_timer_set(int minutes);
bool shell_timer_running(void);
int  shell_timer_remaining_ms(void);
int  shell_timer_total_ms(void);

/* --- device settings -----------------------------------------------------
 * The shell's, not any app's: these are facts about the device, and the shell
 * is what acts on them. The Settings app is their UI. Persisted to NVS when a
 * value screen is left, never on every detent.
 *
 * No setting here can be typed. Each is a value the dial picks - which is
 * what a rotary encoder is actually good at (BUILD.md section 6). */
int  shell_brightness(void);            /* 10..100, floor so it cannot be lost */
void shell_brightness_set(int pct);     /* applies to the backlight immediately */

/* A transient 0..256 scale over the chosen brightness, for fades. 256 is
 * normal. Does not change the Settings value and is never written to NVS -
 * whoever sets it owns putting it back to 256. */
void shell_backlight_scale(int per256);
int  shell_sleep_min(void);             /* 0 = never */
void shell_sleep_min_set(int minutes);
int  shell_haptics(void);               /* 0 off, 1 light, 2 firm */
void shell_haptics_set(int level);
int  shell_dial_step(void);             /* volume % per detent: 2, 5 or 10 */
void shell_dial_step_set(int pct);
void shell_settings_save(void);

/* Bumped every time the device acquires an IP. An app that has backed off
 * after a network failure watches this to notice the network is back, instead
 * of sitting out the rest of a backoff it no longer needs. The seam holds:
 * this says the network changed, not what any app should do about it. */
uint32_t shell_net_generation(void);

/* Facts the Settings app displays and cannot compute for itself. */
const char *shell_wifi_ssid(void);
int         shell_wifi_rssi(void);
const char *shell_ip(void);
int         shell_uptime_s(void);
int         shell_reauth_days(void);    /* until the refresh token dies */

/* --- apps and switching --------------------------------------------------
 * The shell owns the app registry, the screen lifecycle and the selector.
 * An app never switches itself; the selector asks the shell to. */
int  shell_app_count(void);
const knob_app_t *shell_app_at(int index);
int  shell_app_active_index(void);

/* Exit the current app, enter the given one, and load its screen. Safe to
 * call from an LVGL callback; must not be called with the LVGL lock held. */
void shell_switch_to(int index);

/* Open the menu - the radial app selector, which is what every back
 * affordance in the product leads to. Safe from an LVGL event callback: the
 * open is deferred, because the menu builds objects over the screen the event
 * is still being dispatched on. */
void shell_open_menu(void);

/* Called by the menu as it opens and closes, to drive on_pause / on_resume on
 * whatever is underneath. Not for apps to call on themselves. */
void shell_active_app_set_paused(bool paused);

/* The back affordance, in the same place on every screen: a chevron at the
 * bottom of the ring, with a generous tap area around it. Tapping it opens
 * the menu.
 *
 * An app with levels inside it - Spotify's CONTROLS, a Settings value, the
 * Launcher's Task View - handles its own back first and only reaches this at
 * its root. That two-level rule is written out in docs/USER-JOURNEY.md. */
lv_obj_t *shell_back_button(lv_obj_t *parent);

/* True while the screen is dark. The first touch or detent after that only
 * wakes it and is not delivered to the app - reaching for a dark screen is
 * how you turn it on, not how you press what happens to be under your
 * finger. */
bool shell_is_asleep(void);
void shell_wake(void);

/* Back to the default screen - app 0, which is what the device shows on boot
 * and what an app returns to when its job is finished. Named rather than
 * written as shell_switch_to(0) in five places, because the registry order is
 * the shell's business and an app should not have to know it. */
void shell_switch_home(void);
