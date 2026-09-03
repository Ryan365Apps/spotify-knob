#pragma once

#include "app_shell.h"

extern const knob_app_t spotify_app;

/* One-time init (mutex creation), before any on_enter. */
void spotify_app_init(void);
