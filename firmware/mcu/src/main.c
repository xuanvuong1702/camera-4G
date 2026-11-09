#include "hal.h"
#include "mcu.h"

int main(void)
{
    uint32_t now;

    hal_init();
    power_init();
    proto_init();
    pir_init();

    for (;;) {
        now = hal_now_ms();
        pir_update(hal_gpio_get(HAL_PIR), now);
        if (pir_take_event()) {
            power_wake();
        }
        power_tick(now);
        hal_poll();
        hal_enter_stop();
    }
}
