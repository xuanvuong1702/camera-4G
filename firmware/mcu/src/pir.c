#include "hal.h"
#include "mcu.h"

#define PIR_STABLE_MS 200u

static int s_last = 0;
static int s_stable = 0;
static uint32_t s_change_ms = 0;
static int s_event = 0;

void pir_init(void)
{
    s_last = 0;
    s_stable = 0;
    s_change_ms = hal_now_ms();
    s_event = 0;
}

void pir_update(int level, uint32_t now_ms)
{
    level = level ? 1 : 0;
    if (level != s_last) {
        s_last = level;
        s_change_ms = now_ms;
        return;
    }
    if (level != s_stable && (now_ms - s_change_ms) >= PIR_STABLE_MS) {
        s_stable = level;
        if (level) {
            s_event = 1;
            proto_set_event(EVENT_PIR);
        }
    }
}

int pir_take_event(void)
{
    int e = s_event;
    s_event = 0;
    return e;
}
