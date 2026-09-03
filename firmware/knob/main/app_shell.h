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

/* TEST ONLY (Wave 4 checkpoint D): overwrite the in-RAM access token so the
 * next API call 401s, proving the refresh-and-recover path. Removed when the
 * checkpoint passes. */
void shell_token_corrupt_for_test(void);
