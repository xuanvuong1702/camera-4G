#ifndef CAM4G_MCU_H
#define CAM4G_MCU_H

#include <stdint.h>

/* I2C register map (slave 0x30) */
#define REG_STATUS   0x00
#define REG_EVENT    0x01
#define REG_BAT_H    0x02
#define REG_BAT_L    0x03
#define REG_TEMP     0x04
#define REG_CMD      0x05
#define REG_VERSION  0x06

#define STATUS_SOC_READY   (1u << 0)
#define STATUS_SOC_ON      (1u << 1)
#define STATUS_MODEM_ON    (1u << 2)
#define STATUS_FAULT       (1u << 3)

#define EVENT_PIR          (1u << 0)
#define EVENT_SCHEDULE     (1u << 1)

#define CMD_WAKE      1
#define CMD_SLEEP     2
#define CMD_MODEM_ON  3
#define CMD_MODEM_OFF 4

void proto_init(void);
uint8_t proto_read(uint8_t reg);
void proto_write(uint8_t reg, uint8_t value);
void proto_set_event(uint8_t bits);

void power_init(void);
void power_wake(void);
void power_request_sleep(void);
void power_tick(uint32_t now_ms);
int power_soc_on(void);

void pir_init(void);
void pir_update(int level, uint32_t now_ms);
int pir_take_event(void);

#endif
