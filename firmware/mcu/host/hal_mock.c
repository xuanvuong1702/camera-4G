#include "hal.h"

static int gpio[HAL_GPIO_COUNT];
static uint32_t now_ms;
static uint16_t battery_mv = 3700;
static int16_t temp_c = 25;

void hal_init(void)
{
}

void hal_poll(void)
{
}

void hal_gpio_set(hal_gpio_t pin, int value)
{
    if (pin < HAL_GPIO_COUNT) {
        gpio[pin] = value ? 1 : 0;
    }
}

int hal_gpio_get(hal_gpio_t pin)
{
    return (pin < HAL_GPIO_COUNT) ? gpio[pin] : 0;
}

uint32_t hal_now_ms(void)
{
    return now_ms;
}

void hal_delay_ms(uint32_t ms)
{
    now_ms += ms;
}

uint16_t hal_battery_mv(void)
{
    return battery_mv;
}

int16_t hal_temp_c(void)
{
    return temp_c;
}

void hal_enter_stop(void)
{
    now_ms += 10;
}

/* test helpers */
void mock_set_time(uint32_t t) { now_ms = t; }
void mock_set_battery(uint16_t mv) { battery_mv = mv; }
void mock_set_temp(int16_t t) { temp_c = t; }
