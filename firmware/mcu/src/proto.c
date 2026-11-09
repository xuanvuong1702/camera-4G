#include "hal.h"
#include "mcu.h"

static uint8_t s_status;
static uint8_t s_event;

void proto_init(void)
{
    s_status = 0;
    s_event = 0;
}

void proto_set_event(uint8_t bits)
{
    s_event |= bits;
}

static void refresh_status(void)
{
    if (power_soc_on()) {
        s_status |= STATUS_SOC_ON;
    } else {
        s_status &= (uint8_t)~STATUS_SOC_ON;
    }
}

uint8_t proto_read(uint8_t reg)
{
    uint16_t mv;
    int16_t tc;

    refresh_status();
    switch (reg) {
    case REG_STATUS:
        return s_status;
    case REG_EVENT: {
        uint8_t v = s_event;
        s_event = 0;
        return v;
    }
    case REG_BAT_H:
        mv = hal_battery_mv();
        return (uint8_t)(mv >> 8);
    case REG_BAT_L:
        mv = hal_battery_mv();
        return (uint8_t)(mv & 0xFF);
    case REG_TEMP:
        tc = hal_temp_c();
        return (uint8_t)(int8_t)tc;
    case REG_VERSION:
        return 0x10;
    default:
        return 0;
    }
}

void proto_write(uint8_t reg, uint8_t value)
{
    if (reg != REG_CMD) {
        return;
    }
    switch (value) {
    case CMD_WAKE:
        power_wake();
        break;
    case CMD_SLEEP:
        power_request_sleep();
        break;
    case CMD_MODEM_ON:
        hal_gpio_set(HAL_MODEM_EN, 1);
        s_status |= STATUS_MODEM_ON;
        break;
    case CMD_MODEM_OFF:
        hal_gpio_set(HAL_MODEM_EN, 0);
        s_status &= (uint8_t)~STATUS_MODEM_ON;
        break;
    default:
        s_status |= STATUS_FAULT;
        break;
    }
}
