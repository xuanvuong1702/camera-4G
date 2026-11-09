#include "stm32l011xx.h"

uint32_t SystemCoreClock = 16000000u;

void SystemInit(void)
{
    /* HSI16 is the reset clock on STM32L011; keep it simple. */
    SystemCoreClock = 16000000u;
}
