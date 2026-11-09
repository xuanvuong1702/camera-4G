#include <stdio.h>

#include "hal.h"
#include "mcu.h"

void mock_set_time(uint32_t t);
void mock_set_battery(uint16_t mv);
void mock_set_temp(int16_t t);

static int failures;

#define CHECK(cond) do { \
    if (!(cond)) { \
        printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
        failures++; \
    } \
} while (0)

static void test_wake_sequence(void)
{
    proto_init();
    power_init();
    mock_set_time(0);
    hal_gpio_set(HAL_SOC_READY, 0);

    CHECK(proto_read(REG_STATUS) & STATUS_SOC_ON ? 0 : 1);

    proto_write(REG_CMD, CMD_WAKE);
    CHECK(hal_gpio_get(HAL_SOC_EN) == 1);
    CHECK(power_soc_on() == 1);

    hal_gpio_set(HAL_SOC_READY, 1);
    power_tick(100);
    CHECK(proto_read(REG_STATUS) & STATUS_SOC_ON);
}

static void test_ready_timeout(void)
{
    proto_init();
    power_init();
    mock_set_time(0);
    hal_gpio_set(HAL_SOC_READY, 0);

    power_wake();
    CHECK(hal_gpio_get(HAL_SOC_EN) == 1);
    power_tick(4000);
    CHECK(hal_gpio_get(HAL_SOC_EN) == 0);
}

static void test_sleep(void)
{
    proto_init();
    power_init();
    hal_gpio_set(HAL_SOC_READY, 1);
    power_wake();
    power_tick(10);
    CHECK(hal_gpio_get(HAL_SOC_EN) == 1);

    proto_write(REG_CMD, CMD_SLEEP);
    CHECK(hal_gpio_get(HAL_SOC_EN) == 0);
}

static void test_modem(void)
{
    proto_init();
    power_init();
    proto_write(REG_CMD, CMD_MODEM_ON);
    CHECK(hal_gpio_get(HAL_MODEM_EN) == 1);
    CHECK(proto_read(REG_STATUS) & STATUS_MODEM_ON);

    proto_write(REG_CMD, CMD_MODEM_OFF);
    CHECK(hal_gpio_get(HAL_MODEM_EN) == 0);
}

static void test_pir_debounce(void)
{
    proto_init();
    pir_init();
    hal_gpio_set(HAL_PIR, 0);
    pir_update(0, 0);

    hal_gpio_set(HAL_PIR, 1);
    pir_update(1, 10);   /* change recorded */
    pir_update(1, 50);   /* not stable yet */
    CHECK(pir_take_event() == 0);
    pir_update(1, 300);  /* stable > 200 ms */
    CHECK(pir_take_event() == 1);
    CHECK(proto_read(REG_EVENT) & EVENT_PIR);

    /* impulse shorter than debounce is ignored */
    pir_update(0, 400);
    pir_update(1, 450);
    pir_update(1, 500);
    CHECK(pir_take_event() == 0);
}

static void test_battery_temp(void)
{
    proto_init();
    mock_set_battery(3456);
    mock_set_temp(-5);

    uint8_t hi = proto_read(REG_BAT_H);
    uint8_t lo = proto_read(REG_BAT_L);
    CHECK(((hi << 8) | lo) == 3456);
    CHECK((int8_t)proto_read(REG_TEMP) == -5);
}

int main(void)
{
    test_wake_sequence();
    test_ready_timeout();
    test_sleep();
    test_modem();
    test_pir_debounce();
    test_battery_temp();

    if (failures) {
        printf("FAILED: %d\n", failures);
        return 1;
    }
    printf("OK: all MCU tests passed\n");
    return 0;
}
