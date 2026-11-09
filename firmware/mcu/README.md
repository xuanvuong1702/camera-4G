# CAM4G — MCU firmware (STM32L011F4)

Supervisor MCU: quản lý nguồn, PIR, đọc pin/nhiệt, giao tiếp I2C với SoC.

## Kiến trúc

```
main.c  ──►  pir_update / power_tick / hal_enter_stop
              │
power.c  ─────┼──►  HAL: SOC_EN, SOC_READY, MODEM_EN
proto.c  ─────┘     thanh ghi I2C (0x30)
pir.c               lọc nhiễu 200 ms
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

## Build & test trên máy tính

```bash
cd firmware/mcu
make test        # clang, chạy 6 nhóm test
```

## Build cho target

Cần `arm-none-eabi-gcc` + STM32CubeL0 (CMSIS device header + HAL). Máy hiện tại
**không có** toolchain này, nên phần target chưa được biên dịch.

## Việc còn lại

- Viết `hal_stm32l0.c` (GPIO/I2C/ADC/UART/PWR) — cần board thật để kiểm tra.
- Startup + linker script cho STM32L011F4 (16 KB flash, 2 KB RAM).
- I2C slave interrupt handler gọi `proto_read/proto_write`.
- Nối PIR vào EXTI, đánh thức bằng STOP mode.

## Build cho target (đã chạy được)

Toolchain: `Arm.GnuArmEmbeddedToolchain` 14.2.Rel1 + CMSIS headers trong `target/cmsis/`.

```powershell
cd firmware/mcu/target
arm-none-eabi-gcc -mcpu=cortex-m0plus -mthumb -Os -std=c11 -Icmsis -I../include `
  -T linker.ld -nostartfiles -Wl,--gc-sections `
  ../src/main.c ../src/power.c ../src/proto.c ../src/pir.c `
  startup.c system_stm32l0xx.c hal_stm32l0.c -o build/firmware.elf
arm-none-eabi-objcopy -O binary build/firmware.elf build/firmware.bin
```

Kết quả: **1088 B text, 4 B data, 28 B bss** — vừa 16 KB flash / 2 KB RAM.

## Còn thiếu để chạy trên board

- **I2C1 slave interrupt** (PA9/PA10) gọi `proto_read/proto_write` — chưa viết
- PIR EXTI wake từ STOP mode
- Hiệu chỉnh ADC theo VREF thực

## Cập nhật vòng 13 — I2C slave

Đã thêm `hal_poll()` vào HAL và main loop:
- Cấu hình I2C1 slave 0x30 trên PA9/PA10 (AF4, open-drain, pull-up)
- Xử lý ADDR / RXNE / TXE / STOPF / NACKF
- Ghi: byte đầu = con trỏ thanh ghi, các byte sau = dữ liệu
- Đọc: trả `proto_read(reg)` và tự tăng con trỏ

**Build target:** 1760 B text, 8 B data, 32 B bss — vừa 16 KB / 2 KB.

**Chưa kiểm chứng trên phần cứng.** Hai điểm cần xác nhận khi có board:
- AF4 cho PA9/PA10 có đúng với STM32L011 không
- Chuỗi ADDR → TXE có cần preload TXDR sớm hơn không
