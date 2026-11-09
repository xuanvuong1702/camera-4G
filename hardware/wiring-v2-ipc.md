# CAM4G — Kiến trúc & đấu dây (bản cuối v4)

| Thành phần | Model |
|---|---|
| SoC | Luckfox **Core1106G3 N256** (RV1106G3, 30×30 mm, 112 pad) |
| Camera | SC3336 3 MP, FPC 20-pin 0,5 mm |
| Modem | **Quectel EC200U-EU** qua UART (breakout) |
| MCU giám sát | **STM32L011F4** (TSSOP-20) |
| Pin | LFP 1S **10 Ah** + BMS |
| Board | 100×70 mm, 4 lớp |

---

## 1. Sơ đồ khối

```
PIR ─────► STM32L011 (luôn sống, ~0,3 mA)
RTC ◄───►  • PIR, OneWire, ADC pin
           • I2C slave 0x30 ↔ SoC
           • BOOST_EN, MODEM_EN/PWRKEY/RESET
                │
                │ BOOST_EN
        ┌───────▼────────┐
        │ TPS61088 5 V   │──► Core1106 5 V
        │ 3 A            │──► EC200U breakout 5 V
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ TPS62840 3,3 V │──► MCU, camera, sensors, I2C
        └────────────────┘

LFP 10 Ah ── BMS ── VBAT ──► TPS61088 / TPS62840 / CN3058E (sạc)
```

---

## 2. Chân MCU (U6 — STM32L011F4, TSSOP-20)

| Pin | Net | Chức năng |
|---|---|---|
| 1 | MCU_BOOT0 | boot mode |
| 2 | MODEM_RESET | reset modem |
| 3 | — | NC |
| 4 | MCU_NRST | reset |
| 5, 16 | +3V3 | nguồn |
| 6 | PIR_OUT | PIR (vào) |
| 7 | ONEWIRE | DS18B20 ×2 |
| 8 | MODEM_PWRKEY | bật modem |
| 9 | MODEM_STATUS | trạng thái modem |
| 10 | MODEM_EN | cắt nguồn modem |
| 11 | BOOST_EN | bật rail 5 V cho SoC |
| 12 | SOC_READY | SoC báo sẵn sàng |
| 13 | INA_ALERT | cảnh báo INA226 |
| 14 | VBAT_SENSE | chia áp pin |
| 15 | GND | |
| 17 | I2C_SCL | I2C slave 0x30 |
| 18 | I2C_SDA | I2C slave 0x30 |
| 19 | SWDIO | nạp firmware |
| 20 | SWCLK | nạp firmware |

---

## 3. Kết nối SoC (U1 — Core1106)

| Chức năng | Chân module | Ghi chú |
|---|---|---|
| Camera MIPI | 2 lane + clock | FPC 20P J3 |
| Camera I2C | CAM_SCL/SDA | cấu hình SC3336 |
| SD | SD_CLK/CMD/D0–D3 | J4 microSD |
| USB | USB_DP/DM | J1 USB-C, R32/R33 sang modem |
| UART modem | UART1 TX/RX (pin 68/69) | J11 pin 9/10 |
| Modem control | MODEM_PWRKEY/STATUS/RESET | J11 |
| MCU | I2C1 (PA9/PA10) | slave 0x30 |
| Debug | UART0 | J12 |
| Nguồn | 5V_SYS, 3V3 | |

---

## 4. Modem EC200U-EU

- UART 3,3 V: TXD→U1 RX, RXD→U1 TX.
- 5 V vào breakout, PWRKEY/RESET/STATUS qua J11.
- R32/R33 (USB 0 Ω) **DNP** khi dùng UART.
- PPP `/dev/ttyS1` 921600; APN Viettel `v-internet`, Vina `m3-world`, Mobi `m-wap`.

Chi tiết: `docs/09-modem-ec200u.md`.

---

## 5. Hai chế độ ngủ (pin 10 Ah)

| Chế độ | SoC | Modem | Dòng chờ | Wake cloud | Standby |
|---|---|---|---|---|---|
| Canh gác nhanh | suspend | eDRX/PSM | 10–30 mW | 5–15 s | ~40–75 ngày |
| Tiết kiệm tối đa | tắt rail | tắt | ~0,3 mA | không (PIR/lịch) | nhiều tháng |

Đánh đổi không tránh được: muốn nhận lệnh từ xa thì phải có thứ gì đó thức.

---

## 6. Ghi chú

- I2C giữa SoC và MCU là kênh duy nhất để đọc pin/nhiệt và điều khiển nguồn.
- PIR wake: MCU đánh thức bằng EXTI, bật BOOST_EN, chờ SOC_READY.
- MIPI chưa kiểm soát impedance — xem `docs/06-manufacturing.md`.
