#pragma once

#include "app_shell.h"

extern const knob_app_t wispr_app;

/* The microphone, from primitives, into a square container of `px`.
 *
 * It exists as a function rather than a font symbol because LVGL's symbol set
 * has no microphone in it - the nearest is a telephone handset, which is what
 * Dictation drew as in the menu until 2026-09-05. The same three shapes serve
 * the app's own screen at 60 px and the menu's rim and centre at 28 and 52. */
void wispr_draw_mic(lv_obj_t *into, int px, lv_color_t colour);
