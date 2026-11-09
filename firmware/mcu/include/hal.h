#ifndef CAM4G_HAL_H
#define CAM4G_HAL_H

#include <stdint.h>

typedef enum {
    HAL_SOC_EN = 0,
    HAL_SOC_READY,
    HAL_MODEM_EN,
    HAL_MODEM_PWRKEY,
    HAL_MODEM_STATUS,
    HAL_PIR,
    HAL_LED,
    HAL_GPIO_COUNT
} hal_gpio_t;

void hal_init(void);
void hal_poll(void);
void hal_gpio_set(hal_gpio_t pin, int value);
int hal_gpio_get(hal_gpio_t pin);
uint32_t hal_now_ms(void);
void hal_delay_ms(uint32_t ms);
uint16_t hal_battery_mv(void);
int16_t hal_temp_c(void);
void hal_enter_stop(void);

#endif
