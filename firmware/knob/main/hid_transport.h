/*
 * The seam between HID policy and HID transport.
 *
 * `hid.c` owns the rule: an action enum in, a compile-time modifier and usage
 * pair out, and no string anywhere near either. `hid_ble.c` owns NimBLE and
 * knows nothing about actions - it is handed two bytes and told to send them.
 *
 * Keeping the split means the rule lives in one small file that can be read in
 * a minute, and the transport can be replaced without anyone re-deriving what
 * is and is not allowed to reach the wire.
 *
 * Private to the HID layer. Apps include hid.h and nothing else.
 */
#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

#include "hid.h"

/* Bring the stack up. Safe to call twice. */
esp_err_t hid_transport_init(void);

/* Take it down again: drop the link, stop advertising, and hand the
 * controller's memory and its share of the radio back. Safe to call twice. */
void hid_transport_deinit(void);

/* True while the teardown is in flight. It is asynchronous because it has to
 * wait for a disconnect and on_exit may not block. */
bool hid_transport_stopping(void);

/* One keyboard report: modifiers plus a single usage, then the release that
 * follows it. The transport sends both - a modifier left held down would make
 * every mouse click on the PC a ctrl-click for as long as it lasted. */
esp_err_t hid_transport_send(uint8_t modifiers, uint8_t usage);

bool        hid_transport_connected(void);
hid_state_t hid_transport_state(void);
uint32_t    hid_transport_passkey(void);

/* Drop every bond and start advertising again. The only destructive action in
 * Settings, which is why it is the only one that confirms. */
void hid_transport_forget_host(void);

/* Advertise on demand. The device advertises on boot anyway; this is the
 * "Pair" action for when a host has been forgotten or was never there. */
esp_err_t hid_transport_advertise(void);
