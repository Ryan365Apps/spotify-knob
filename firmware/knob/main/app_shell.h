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

#include "esp_err.h"
#include "lvgl.h"

typedef struct {
    const char *name;          /* shown in the selector            */
    const void *glyph;         /* selector icon                    */
    lv_color_t  accent;        /* the app's colour in the UI       */

    void (*on_enter)(lv_obj_t *parent);   /* build widgets, start polling */
    void (*on_exit)(void);                /* free buffers, stop polling   */
    void (*on_dial)(int delta);           /* detents, signed              */
    void (*on_tick)(void);                /* ~1 Hz housekeeping           */
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
int  shell_sleep_min(void);             /* 0 = never */
void shell_sleep_min_set(int minutes);
int  shell_haptics(void);               /* 0 off, 1 light, 2 firm */
void shell_haptics_set(int level);
int  shell_dial_step(void);             /* volume % per detent: 2, 5 or 10 */
void shell_dial_step_set(int pct);
void shell_settings_save(void);

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
