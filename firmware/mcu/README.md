# CAM4G — MCU firmware (STM32L011F4)

Supervisor MCU: quản lý nguồn, PIR, OneWire, đọc pin, giao tiếp I2C với SoC.

## Kiến trúc

```
main.c  ──►  pir_update / power_tick / hal_poll
              │
power.c  ─────┼──►  HAL: BOOST_EN, SOC_READY, MODEM_EN
proto.c  ─────┘     thanh ghi I2C (0x30)
pir.c               lọc nhiễu 200 ms
target/hal_stm32l0.c  GPIO, SysTick, ADC, I2C slave, __WFI
```

## Thanh ghi I2C (slave 0x30)

| Reg | Tên | Nội dung |
|---|---|---|
| 0x00 | STATUS | bit0 SOC_READY, bit1 SOC_ON, bit2 MODEM_ON, bit3 FAULT |
| 0x01 | EVENT | bit0 PIR, bit1 SCHEDULE — đọc sẽ xoá |
| 0x02/0x03 | BAT_H/L | điện áp pin mV |
| 0x04 | TEMP | nhiệt độ (int8, °C) |
| 0x05 | CMD | 1 wake, 2 sleep, 3 modem on, 4 modem off |
| 0x06 | VERSION | 0x10 |

## Test trên máy tính

```powershell
cd firmware/mcu
clang -std=c11 -Wall -Wextra -Iinclude src/power.c src/proto.c src/pir.c host/hal_mock.c host/test_mcu.c -o build/test_mcu.exe
./build/test_mcu.exe
```

**6 nhóm test**: wake sequence, ready timeout, sleep, modem, PIR debounce, battery/temp.

## Build cho target (đã chạy được)

```powershell
cd firmware/mcu/target
arm-none-eabi-gcc -mcpu=cortex-m0plus -mthumb -Os -std=c11 -Icmsis -I../include `
  -T linker.ld -nostartfiles -Wl,--gc-sections `
  ../src/main.c ../src/power.c ../src/proto.c ../src/pir.c `
  startup.c system_stm32l0xx.c hal_stm32l0.c -o build/firmware.elf
arm-none-eabi-objcopy -O binary build/firmware.elf build/firmware.bin
```

Kết quả: **1720 B text, 8 B data, 36 B bss** — vừa 16 KB flash / 2 KB RAM.

## Đã có / chưa kiểm chứng

**Đã có:**
- Power sequencing với timeout 3 s
- I2C slave polling (ADDR/RXNE/TXE/STOPF/NACKF)
- PIR debounce 200 ms
- ADC pin, SysTick 1 ms, STOP mode

**Chưa kiểm chứng trên board:**
- AF4 cho PA9/PA10 có đúng với STM32L011
- Thời điểm preload TXDR khi đọc
- Hiệu chỉnh ADC theo VREF thực
- EXTI wake cho PIR từ STOP mode
