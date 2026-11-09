#include "stm32l011xx.h"
#include "hal.h"
#include "mcu.h"

static volatile uint8_t s_reg;
static volatile uint8_t s_first = 1;
static volatile uint8_t s_read;

static volatile uint32_t s_ticks;

void SysTick_Handler(void)
{
    s_ticks++;
}

static uint32_t mask_of(hal_gpio_t pin)
{
    switch (pin) {
    case HAL_PIR: return 1u << 0;           /* PA0 */
    case HAL_MODEM_PWRKEY: return 1u << 2;  /* PA2 */
    case HAL_MODEM_STATUS: return 1u << 3;  /* PA3 */
    case HAL_MODEM_EN: return 1u << 4;      /* PA4 */
    case HAL_SOC_EN: return 1u << 5;        /* PA5 (BOOST_EN) */
    case HAL_SOC_READY: return 1u << 6;     /* PA6 */
    case HAL_LED: return 1u << 7;           /* PA7 */
    default: return 0;
    }
}

static void set_mode(uint32_t mask, int output)
{
    uint32_t bit = (uint32_t)__builtin_ctz(mask) * 2u;
    GPIOA->MODER &= ~(3u << bit);
    if (output) {
        GPIOA->MODER |= (1u << bit);
    }
}

void hal_init(void)
{
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN | RCC_IOPENR_GPIOBEN;

    set_mode(mask_of(HAL_SOC_EN), 1);
    set_mode(mask_of(HAL_MODEM_EN), 1);
    set_mode(mask_of(HAL_MODEM_PWRKEY), 1);
    set_mode(mask_of(HAL_LED), 1);

    set_mode(mask_of(HAL_SOC_READY), 0);
    set_mode(mask_of(HAL_MODEM_STATUS), 0);
    set_mode(mask_of(HAL_PIR), 0);

    GPIOA->BRR = mask_of(HAL_SOC_EN) | mask_of(HAL_MODEM_EN) |
                 mask_of(HAL_MODEM_PWRKEY) | mask_of(HAL_LED);

    SysTick_Config(SystemCoreClock / 1000u);

    /* I2C1 slave on PA9/PA10, AF4, open-drain with pull-up. */
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    GPIOA->MODER = (GPIOA->MODER & ~((3u << 18) | (3u << 20))) | (2u << 18) | (2u << 20);
    GPIOA->OTYPER |= (1u << 9) | (1u << 10);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~((3u << 18) | (3u << 20))) | (1u << 18) | (1u << 20);
    GPIOA->AFR[1] = (GPIOA->AFR[1] & ~0x00000FF0u) | 0x00000440u;

    I2C1->CR1 = 0;
    I2C1->OAR1 = (uint32_t)(0x30u << 1) | (1u << 14);
    I2C1->CR2 = 16u;
    I2C1->CR1 = I2C_CR1_PE;
}

void hal_gpio_set(hal_gpio_t pin, int value)
{
    uint32_t mask = mask_of(pin);
    if (!mask) {
        return;
    }
    if (value) {
        GPIOA->BSRR = mask;
    } else {
        GPIOA->BRR = mask;
    }
}

int hal_gpio_get(hal_gpio_t pin)
{
    uint32_t mask = mask_of(pin);
    return (mask && (GPIOA->IDR & mask)) ? 1 : 0;
}

uint32_t hal_now_ms(void)
{
    return s_ticks;
}

void hal_delay_ms(uint32_t ms)
{
    uint32_t start = s_ticks;
    while ((s_ticks - start) < ms) {
        __WFI();
    }
}

uint16_t hal_battery_mv(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_ADCEN;
    GPIOB->MODER |= (3u << (1 * 2)); /* PB1 analog */

    ADC1->CFGR2 = 0;
    ADC1->CFGR1 = 0;
    ADC1->CHSELR = ADC_CHSELR_CHSEL9;
    ADC1->SMPR = 7u;

    if (!(ADC1->ISR & ADC_ISR_ADRDY)) {
        ADC1->CR |= ADC_CR_ADEN;
        while (!(ADC1->ISR & ADC_ISR_ADRDY)) {
        }
    }
    ADC1->CR |= ADC_CR_ADSTART;
    while (!(ADC1->ISR & ADC_ISR_EOC)) {
    }
    uint32_t raw = ADC1->DR & 0x0FFFu;
    return (uint16_t)((raw * 3300u) / 4095u);
}

int16_t hal_temp_c(void)
{
    return 25;
}

void hal_enter_stop(void)
{
    __WFI();
}


void hal_poll(void)
{
    uint32_t isr = I2C1->ISR;

    if (isr & I2C_ISR_ADDR) {
        I2C1->ICR = I2C_ICR_ADDRCF;
        s_first = 1;
        s_read = (isr & I2C_ISR_DIR) ? 1u : 0u;
        if (s_read) {
            I2C1->TXDR = proto_read(s_reg++);
        }
    }
    if (isr & I2C_ISR_RXNE) {
        uint8_t b = (uint8_t)I2C1->RXDR;
        if (s_first) {
            s_reg = b;
            s_first = 0;
        } else {
            proto_write(s_reg, b);
            s_reg++;
        }
    }
    if ((isr & I2C_ISR_TXE) && s_read) {
        I2C1->TXDR = proto_read(s_reg++);
    }
    if (isr & I2C_ISR_STOPF) {
        I2C1->ICR = I2C_ICR_STOPCF;
        s_first = 1;
        s_read = 0;
    }
    if (isr & I2C_ISR_NACKF) {
        I2C1->ICR = I2C_ICR_NACKCF;
    }
}
