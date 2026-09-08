/*
 * The BLE HID keyboard (Wave 10). NimBLE, not Bluedroid - roughly half the
 * footprint for a device that needs one GATT service.
 *
 * **This must never be USB HID.** The S3's USB HID and its USB-Serial-JTAG
 * flashing port are the same peripheral on the same pins, this board has no
 * BOOT and no RESET button, and GPIO0 carries `I2S_SWITCH_IN` rather than a
 * switch (BUILD.md section 3). Firmware that claims the USB peripheral may
 * leave no way back into download mode, which is a brick rather than an
 * inconvenience. Nothing in this file touches USB and nothing ever should.
 *
 * **Keyboard only.** No consumer control page, no mouse. A paired BLE HID
 * keyboard can type anything into the PC it is bonded to, so the descriptor
 * exposes the smallest surface that does the job. The parked idea of using
 * consumer-control volume steps to get round the phone's VOLUME_CONTROL_
 * DISALLOW stays parked: it would need a second report descriptor, and it
 * still cannot read the phone's level back, which is what the settled UI needs.
 *
 * Pairing uses a passkey shown on the panel, with MITM protection on. The
 * screen is right there, so there is no reason to ship the fixed 123456 the
 * IDF example uses.
 */
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "esp_bt.h"
#include "esp_log.h"
#include "esp_random.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_hidd.h"
#include "host/ble_hs.h"
#include "host/util/util.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "services/gap/ble_svc_gap.h"

#include "hid_transport.h"

static const char *TAG = "hid-ble";

#define DEVICE_NAME   "Radial"
#define REPORT_ID_KB  1

/* NimBLE's own bond store, which persists to NVS. Declared here because the
 * IDF examples declare it here too - it has no public header. */
void ble_store_config_init(void);

/*
 * A boot-protocol keyboard, and nothing else.
 *
 * Eight bytes in: modifiers, a reserved byte the spec requires, then six key
 * slots. Only the first slot is ever used - Radial sends single chords, never
 * a held combination of ordinary keys.
 *
 * The LED output report at the end is not optional in practice. It is part of
 * the standard boot descriptor and some hosts are unhappy without it, even
 * though nothing here has a caps-lock light to drive.
 */
static const uint8_t KEYBOARD_REPORT_MAP[] = {
    0x05, 0x01,        /* Usage Page (Generic Desktop)        */
    0x09, 0x06,        /* Usage (Keyboard)                    */
    0xA1, 0x01,        /* Collection (Application)            */
    0x85, REPORT_ID_KB,/*   Report ID (1)                     */

    0x05, 0x07,        /*   Usage Page (Keyboard/Keypad)      */
    0x19, 0xE0,        /*   Usage Minimum (Left Control)      */
    0x29, 0xE7,        /*   Usage Maximum (Right GUI)         */
    0x15, 0x00,        /*   Logical Minimum (0)               */
    0x25, 0x01,        /*   Logical Maximum (1)               */
    0x75, 0x01,        /*   Report Size (1)                   */
    0x95, 0x08,        /*   Report Count (8)                  */
    0x81, 0x02,        /*   Input (Data, Var, Abs) - modifiers */

    0x95, 0x01,        /*   Report Count (1)                  */
    0x75, 0x08,        /*   Report Size (8)                   */
    0x81, 0x01,        /*   Input (Const) - the reserved byte  */

    0x95, 0x05,        /*   Report Count (5)                  */
    0x75, 0x01,        /*   Report Size (1)                   */
    0x05, 0x08,        /*   Usage Page (LEDs)                 */
    0x19, 0x01,        /*   Usage Minimum (Num Lock)          */
    0x29, 0x05,        /*   Usage Maximum (Kana)              */
    0x91, 0x02,        /*   Output (Data, Var, Abs) - LEDs     */
    0x95, 0x01,        /*   Report Count (1)                  */
    0x75, 0x03,        /*   Report Size (3)                   */
    0x91, 0x01,        /*   Output (Const) - LED padding       */

    0x95, 0x06,        /*   Report Count (6)                  */
    0x75, 0x08,        /*   Report Size (8)                   */
    0x15, 0x00,        /*   Logical Minimum (0)               */
    0x25, 0x65,        /*   Logical Maximum (101)             */
    0x05, 0x07,        /*   Usage Page (Keyboard/Keypad)      */
    0x19, 0x00,        /*   Usage Minimum (0)                 */
    0x29, 0x65,        /*   Usage Maximum (101)               */
    0x81, 0x00,        /*   Input (Data, Array) - six key slots */
    0xC0               /* End Collection                      */
};

static esp_hid_raw_report_map_t s_report_maps[] = {
    {
        .data = KEYBOARD_REPORT_MAP,
        .len  = sizeof(KEYBOARD_REPORT_MAP),
    },
};

static const esp_hid_device_config_t s_hid_config = {
    .vendor_id         = 0x16C0,   /* Van Ooijen Technische Informatica, the
                                    * range that permits free use for
                                    * non-commercial devices */
    .product_id        = 0x27DB,
    .version           = 0x0100,
    .device_name       = DEVICE_NAME,
    .manufacturer_name = "Radial",
    .serial_number     = "1",
    .report_maps       = s_report_maps,
    .report_maps_len   = 1,
};

static esp_hidd_dev_t   *s_dev = NULL;
static volatile hid_state_t s_state = HID_STATE_OFF;
static volatile uint32_t s_passkey = 0;
static bool              s_started = false;
static struct ble_hs_adv_fields s_adv_fields;

/* Which address the controller should advertise from. Not hardcoded to
 * BLE_OWN_ADDR_PUBLIC any more: ble_hs_id_infer_auto asks NimBLE what this
 * controller actually has, which is the one HCI parameter it makes no sense to
 * assert from the application. Set at sync, before the first advertise. */
static uint8_t s_own_addr_type = BLE_OWN_ADDR_PUBLIC;

/* The live link, and whether a teardown is under way. Both are read from the
 * GAP callback on the host task and written from the teardown worker, so they
 * are volatile rather than merely static. */
static volatile uint16_t s_conn = BLE_HS_CONN_HANDLE_NONE;
static volatile bool     s_stopping = false;

/* --- advertising --------------------------------------------------------- */

static int gap_event(struct ble_gap_event *event, void *arg);

esp_err_t hid_transport_advertise(void)
{
    if (!s_started) {
        return ESP_ERR_INVALID_STATE;
    }
    if (s_state == HID_STATE_CONNECTED) {
        return ESP_OK;
    }

    int rc = ble_gap_adv_set_fields(&s_adv_fields);
    if (rc != 0) {
        ESP_LOGE(TAG, "advertisement data rejected, rc=%d", rc);
        return ESP_FAIL;
    }

    struct ble_gap_adv_params adv = { 0 };
    adv.conn_mode = BLE_GAP_CONN_MODE_UND;
    adv.disc_mode = BLE_GAP_DISC_MODE_GEN;
    adv.itvl_min = BLE_GAP_ADV_ITVL_MS(30);
    adv.itvl_max = BLE_GAP_ADV_ITVL_MS(50);

    /* All three advertising channels - 37, 38 and 39.
     *
     * This has to be set explicitly. Zeroing the struct leaves channel_map at
     * 0, NimBLE passes it straight through, and the Bluetooth spec requires at
     * least one channel bit to be set, so the controller rejects LE Set
     * Advertising Parameters outright: hci_err 0x212, INV_HCI_CMD_PARMS,
     * surfacing as rc=530 from ble_gap_adv_start (hardware, 2026-09-04). The
     * IDF example never sets it either, which is presumably why it took a log
     * line reading `adv_channel_map=0` to spot. */
    adv.channel_map = 0x07;

    /* BLE_HS_FOREVER, not the example's 180 s. This is a desk device that is
     * always powered, and a keyboard that stops being findable after three
     * minutes is one you have to reboot to pair. */
    rc = ble_gap_adv_start(s_own_addr_type, NULL, BLE_HS_FOREVER,
                           &adv, gap_event, NULL);
    if (rc != 0 && rc != BLE_HS_EALREADY) {
        /* rc is NimBLE's 0x0200 + HCI error, so 530 is HCI 0x12,
         * INV_HCI_CMD_PARMS. Print the parameters alongside it: a rejected
         * command is worth more as a set of values than as a number, and this
         * error cost three wrong guesses before the log was made to say what
         * it had actually sent. */
        ESP_LOGE(TAG, "advertising would not start, rc=%d "
                      "(own_addr_type %d, chan_map 0x%02X, itvl %d-%d)",
                 rc, s_own_addr_type, adv.channel_map, adv.itvl_min, adv.itvl_max);
        return ESP_FAIL;
    }
    s_state = HID_STATE_ADVERTISING;
    ESP_LOGI(TAG, "advertising as '%s'", DEVICE_NAME);
    return ESP_OK;
}

static int gap_event(struct ble_gap_event *event, void *arg)
{
    (void) arg;
    struct ble_gap_conn_desc desc;

    switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (event->connect.status == 0) {
            s_conn = event->connect.conn_handle;
            ESP_LOGI(TAG, "host connected");
            /* Not CONNECTED yet: a link without encryption cannot carry a
             * keystroke, and saying otherwise would let the Wispr app believe
             * it had sent something it had not. */
        } else {
            ESP_LOGW(TAG, "connection failed, status=%d", event->connect.status);
            hid_transport_advertise();
        }
        return 0;

    case BLE_GAP_EVENT_DISCONNECT:
        ESP_LOGI(TAG, "host disconnected, reason=%d", event->disconnect.reason);
        s_conn = BLE_HS_CONN_HANDLE_NONE;
        s_state = HID_STATE_OFF;
        s_passkey = 0;
        if (s_stopping) {
            return 0;      /* going down; do not start advertising again */
        }
        /* Straight back to advertising. Windows drops the link on sleep and
         * reconnects on wake, and BUILD.md's open risk about that reconnect
         * is exactly why this must not need a person. */
        hid_transport_advertise();
        return 0;

    case BLE_GAP_EVENT_ENC_CHANGE:
        if (event->enc_change.status == 0 &&
            ble_gap_conn_find(event->enc_change.conn_handle, &desc) == 0) {
            s_state = HID_STATE_CONNECTED;
            s_passkey = 0;
            ESP_LOGI(TAG, "encrypted%s - ready to send",
                     desc.sec_state.bonded ? " and bonded" : "");
        } else {
            ESP_LOGW(TAG, "encryption failed, status=%d", event->enc_change.status);
            s_state = HID_STATE_ADVERTISING;
            s_passkey = 0;
        }
        return 0;

    case BLE_GAP_EVENT_PASSKEY_ACTION: {
        struct ble_sm_io io = { 0 };
        if (event->passkey.params.action == BLE_SM_IOACT_DISP) {
            /* A fresh six-digit passkey per pairing, shown on the panel. The
             * IDF example hardcodes 123456; this device has a screen, so
             * there is no reason to. */
            s_passkey = 100000 + (esp_random() % 900000);
            s_state = HID_STATE_PAIRING;
            io.action = event->passkey.params.action;
            io.passkey = s_passkey;
            const int rc = ble_sm_inject_io(event->passkey.conn_handle, &io);
            ESP_LOGI(TAG, "pairing - type the passkey on the PC (inject rc=%d)", rc);
        } else if (event->passkey.params.action == BLE_SM_IOACT_NUMCMP) {
            io.action = event->passkey.params.action;
            io.numcmp_accept = 1;
            ble_sm_inject_io(event->passkey.conn_handle, &io);
        } else {
            ESP_LOGW(TAG, "unsupported passkey action %d",
                     event->passkey.params.action);
        }
        return 0;
    }

    case BLE_GAP_EVENT_REPEAT_PAIRING:
        /* The host has a bond we do not, or wants a new one. Drop ours and
         * let it pair again rather than refusing and looking broken. */
        if (ble_gap_conn_find(event->repeat_pairing.conn_handle, &desc) == 0) {
            ble_store_util_delete_peer(&desc.peer_id_addr);
        }
        return BLE_GAP_REPEAT_PAIRING_RETRY;

    default:
        return 0;
    }
}

static void on_sync(void)
{
    ble_hs_util_ensure_addr(0);

    /* Ask what address this controller has rather than asserting one. */
    const int rc = ble_hs_id_infer_auto(0, &s_own_addr_type);
    if (rc != 0) {
        ESP_LOGW(TAG, "no usable address, rc=%d - falling back to public", rc);
        s_own_addr_type = BLE_OWN_ADDR_PUBLIC;
    }
    ESP_LOGI(TAG, "host synced, advertising from address type %d", s_own_addr_type);
    hid_transport_advertise();
}

static void on_reset(int reason)
{
    ESP_LOGE(TAG, "nimble reset, reason=%d", reason);
    s_state = HID_STATE_OFF;
}

static void host_task(void *param)
{
    (void) param;
    nimble_port_run();               /* returns only on nimble_port_stop() */
    nimble_port_freertos_deinit();
}

/* --- the esp_hid device -------------------------------------------------- */

static void hidd_event(void *handler_args, esp_event_base_t base,
                       int32_t id, void *event_data)
{
    (void) handler_args;
    (void) base;
    const esp_hidd_event_t ev = (esp_hidd_event_t) id;
    switch (ev) {
    case ESP_HIDD_START_EVENT:
        ESP_LOGI(TAG, "hid device started");
        break;
    case ESP_HIDD_CONNECT_EVENT:
        ESP_LOGI(TAG, "hid connected");
        break;
    case ESP_HIDD_DISCONNECT_EVENT:
        ESP_LOGI(TAG, "hid disconnected");
        break;
    case ESP_HIDD_OUTPUT_EVENT:
        /* The host telling us about its lock-key LEDs. Nothing on this device
         * has a caps-lock light, so it is read and dropped - but the report
         * has to exist or some hosts are unhappy with the descriptor. */
        break;
    default:
        break;
    }
}

/* --- the public transport ------------------------------------------------ */

esp_err_t hid_transport_init(void)
{
    if (s_started) {
        return ESP_OK;
    }

    /* Classic Bluetooth's controller memory is handed back before anything
     * else. The S3 has no BR/EDR radio at all - that lives on the second MCU
     * (BUILD.md section 3) - so this is pure reclaim. */
    esp_err_t err = esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT);
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "could not release classic BT memory: %s", esp_err_to_name(err));
        return err;
    }

    err = nimble_port_init();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "nimble_port_init failed: %s", esp_err_to_name(err));
        return err;
    }

    /* Security: bonded, with MITM protection, using a passkey this device
     * displays. A keystroke injector on a desk is worth pairing properly. */
    ble_hs_cfg.sync_cb = on_sync;
    ble_hs_cfg.reset_cb = on_reset;
    ble_hs_cfg.sm_io_cap = BLE_SM_IO_CAP_DISP_ONLY;
    ble_hs_cfg.sm_bonding = 1;
    ble_hs_cfg.sm_mitm = 1;
    ble_hs_cfg.sm_sc = 1;
    ble_hs_cfg.sm_our_key_dist = BLE_SM_PAIR_KEY_DIST_ID | BLE_SM_PAIR_KEY_DIST_ENC;
    ble_hs_cfg.sm_their_key_dist = BLE_SM_PAIR_KEY_DIST_ID | BLE_SM_PAIR_KEY_DIST_ENC;

    ble_svc_gap_device_name_set(DEVICE_NAME);

    /* Advertise as a keyboard, so Windows offers the right pairing flow and
     * the right icon. */
    memset(&s_adv_fields, 0, sizeof(s_adv_fields));
    s_adv_fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    s_adv_fields.appearance = ESP_HID_APPEARANCE_KEYBOARD;
    s_adv_fields.appearance_is_present = 1;
    s_adv_fields.tx_pwr_lvl = BLE_HS_ADV_TX_PWR_LVL_AUTO;
    s_adv_fields.tx_pwr_lvl_is_present = 1;
    s_adv_fields.name = (uint8_t *) DEVICE_NAME;
    s_adv_fields.name_len = strlen(DEVICE_NAME);
    s_adv_fields.name_is_complete = 1;
    static const ble_uuid16_t hid_uuid = BLE_UUID16_INIT(0x1812);   /* HID service */
    s_adv_fields.uuids16 = &hid_uuid;
    s_adv_fields.num_uuids16 = 1;
    s_adv_fields.uuids16_is_complete = 1;

    err = esp_hidd_dev_init(&s_hid_config, ESP_HID_TRANSPORT_BLE, hidd_event, &s_dev);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "esp_hidd_dev_init failed: %s", esp_err_to_name(err));
        return err;
    }

    /* Bonds live in NVS, so the PC is remembered across a power cycle and a
     * reflash. Forgetting one is a deliberate act in Settings. */
    ble_store_config_init();
    ble_hs_cfg.store_status_cb = ble_store_util_status_rr;

    /* Set BEFORE the host task starts, not after.
     *
     * on_sync fires from that task and is what kicks off advertising, and it
     * can land before this function has returned. With the flag set after,
     * hid_transport_advertise saw s_started == false, refused, and the device
     * came up as a keyboard nobody could see - which on hardware looked like
     * every screen reporting "no host connected" forever (2026-09-04). */
    s_started = true;
    nimble_port_freertos_init(host_task);

    ESP_LOGI(TAG, "BLE HID keyboard up - keyboard only, no consumer control, no mouse");
    return ESP_OK;
}

/*
 * Down again, and the order is the whole of it.
 *
 * The first version called esp_hidd_dev_deinit while the link was still up and
 * then let nimble_port_stop terminate it. The disconnect event then arrived
 * and ble_gatts_connection_broken walked GATT structures esp_hid had already
 * freed: LoadProhibited in os_memblock_put, on hardware, 2026-09-06.
 *
 * So the link goes first, and the teardown waits for the disconnect to have
 * been *processed* before anything is freed. Only then does esp_hid go, and
 * only then the port.
 *
 * It runs on its own short-lived task because the wait is the point and
 * on_exit runs on the LVGL thread, where nothing may block - Wave 7 already
 * paid for that lesson with a frozen screen.
 */
#define TEARDOWN_WAIT_MS 600

static void teardown_task(void *arg)
{
    (void) arg;

    ble_gap_adv_stop();

    if (s_conn != BLE_HS_CONN_HANDLE_NONE) {
        ble_gap_terminate(s_conn, BLE_ERR_REM_USER_CONN_TERM);
        for (int i = 0; i < TEARDOWN_WAIT_MS / 10; i++) {
            if (s_conn == BLE_HS_CONN_HANDLE_NONE) {
                break;
            }
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        if (s_conn != BLE_HS_CONN_HANDLE_NONE) {
            ESP_LOGW(TAG, "host did not disconnect in %d ms - going down anyway",
                     TEARDOWN_WAIT_MS);
        }
    }

    if (s_dev != NULL) {
        esp_hidd_dev_deinit(s_dev);
        s_dev = NULL;
    }

    const int rc = nimble_port_stop();
    if (rc == 0) {
        nimble_port_deinit();
        s_started = false;
        ESP_LOGI(TAG, "radio down, bond kept in NVS");
    } else {
        ESP_LOGE(TAG, "nimble_port_stop refused (rc=%d) - radio left up", rc);
    }

    s_stopping = false;
    vTaskDelete(NULL);
}

void hid_transport_deinit(void)
{
    if (!s_started || s_stopping) {
        return;
    }
    s_stopping = true;
    s_state = HID_STATE_OFF;      /* the UI should stop claiming a link now */
    s_passkey = 0;

    if (xTaskCreate(teardown_task, "hid_down", 3072, NULL, 5, NULL) != pdPASS) {
        ESP_LOGE(TAG, "no room for the teardown task - radio left up");
        s_stopping = false;
    }
}

bool hid_transport_stopping(void)
{
    return s_stopping;
}

esp_err_t hid_transport_send(uint8_t modifiers, uint8_t usage)
{
    if (s_dev == NULL || s_state != HID_STATE_CONNECTED) {
        return ESP_ERR_INVALID_STATE;
    }

    /* Report ID 1, boot keyboard layout: modifiers, the reserved byte, then
     * six key slots of which only the first is ever used. */
    uint8_t report[8] = { modifiers, 0, usage, 0, 0, 0, 0, 0 };

    esp_err_t err = esp_hidd_dev_input_set(s_dev, 0, REPORT_ID_KB,
                                           report, sizeof(report));
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "press not delivered: %s", esp_err_to_name(err));
        return err;
    }

    /* The release, and it is not optional. A chord left pressed is a modifier
     * held down on the PC, which poisons every click and scroll until
     * something clears it. 15 ms is long enough for the host to see two
     * distinct reports and short enough to be one keystroke. */
    vTaskDelay(pdMS_TO_TICKS(15));
    memset(report, 0, sizeof(report));
    err = esp_hidd_dev_input_set(s_dev, 0, REPORT_ID_KB, report, sizeof(report));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "RELEASE NOT DELIVERED (%s) - a modifier may be stuck "
                      "on the PC", esp_err_to_name(err));
    }
    return err;
}

bool hid_transport_connected(void)
{
    return s_state == HID_STATE_CONNECTED;
}

hid_state_t hid_transport_state(void)
{
    return s_state;
}

uint32_t hid_transport_passkey(void)
{
    return s_passkey;
}

void hid_transport_forget_host(void)
{
    ble_store_clear();
    ESP_LOGW(TAG, "every bond forgotten - the PC will have to pair again");
    s_state = HID_STATE_OFF;
    s_passkey = 0;
    hid_transport_advertise();
}
