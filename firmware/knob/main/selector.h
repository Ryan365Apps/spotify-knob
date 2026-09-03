#pragma once

#include <stdbool.h>

/* The app selector - shell chrome, not an app (BUILD.md section 5).
 * Long-press from anywhere opens it; it sits above the running app's screen,
 * so backing out returns you to exactly what you were doing. */
void selector_open(void);
void selector_close(void);
bool selector_is_open(void);
void selector_dial(int delta);
