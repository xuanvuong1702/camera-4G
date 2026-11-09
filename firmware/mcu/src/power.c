#include "hal.h"
#include "mcu.h"

typedef enum {
    PWR_OFF = 0,
    PWR_WAIT_READY,
    PWR_ON,
    PWR_SHUTDOWN
} pwr_state_t;

static pwr_state_t s_state = PWR_OFF;
static uint32_t s_since = 0;

#define READY_TIMEOUT_MS 3000u
#define SHUTDOWN_HOLD_MS 500u

void power_init(void)
{
    hal_gpio_set(HAL_SOC_EN, 0);
    hal_gpio_set(HAL_MODEM_EN, 0);
    hal_gpio_set(HAL_LED, 0);
    s_state = PWR_OFF;
}

void power_wake(void)
{
    if (s_state == PWR_ON || s_state == PWR_WAIT_READY) {
        return;
    }
    hal_gpio_set(HAL_SOC_EN, 1);
    s_state = PWR_WAIT_READY;
    s_since = hal_now_ms();
}

void power_request_sleep(void)
{
    if (s_state == PWR_OFF) {
        return;
    }
    hal_gpio_set(HAL_MODEM_EN, 0);
    hal_gpio_set(HAL_SOC_EN, 0);
    s_state = PWR_OFF;
    s_since = hal_now_ms();
}

int power_soc_on(void)
{
    return s_state == PWR_ON || s_state == PWR_WAIT_READY;
}

void power_tick(uint32_t now_ms)
{
    switch (s_state) {
    case PWR_WAIT_READY:
        if (hal_gpio_get(HAL_SOC_READY)) {
            s_state = PWR_ON;
            s_since = now_ms;
            proto_set_event(0);
        } else if (now_ms - s_since > READY_TIMEOUT_MS) {
            /* SoC did not boot: drop the rail and retry next wake. */
            hal_gpio_set(HAL_SOC_EN, 0);
            s_state = PWR_OFF;
        }
        break;
    case PWR_ON:
        break;
    default:
        break;
    }
}
