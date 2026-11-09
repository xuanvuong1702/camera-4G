# Prototype v2 — Kiến trúc IPC (RV1106) & đấu dây

- SoC: Luckfox Pico Max (RV1106G3, 256 MB)
- Camera: SC3336 3 MP MIPI
- Modem: EC25-EU qua USB
- MCU giám sát: STM32L0 (Nucleo-32)
- Pin: LFP 1S 3,2 V 8 Ah

---

## 1. Nguyên tắc

**Hai tầng điều khiển:**
- **MCU luôn sống** (~0,3 mA): PIR, RTC, đo pin/nhiệt, bật/tắt rail 5 V của SoC, quyết định ngủ.
- **SoC là tải**: chỉ bật khi cần ghi hoặc xử lý. Tắt hẳn thì tiết kiệm nhất nhưng boot 1–2 s; suspend thì wake nhanh nhưng ~30 mW.

**Hai chế độ ngủ (người dùng chọn trong app):**

| Chế độ | SoC | Modem | Dòng chờ | Wake từ cloud | Standby (8 Ah) |
|---|---|---|---|---|---|
| Canh gác nhanh | suspend | eDRX/PSM | 10–30 mW | 5–15 s | ~30–60 ngày |
| Tiết kiệm tối đa | tắt rail | tắt | 0,3 mA | không (chỉ PIR/lịch) | nhiều tháng |

> Đây là đánh đổi **không thể tránh**: muốn nhận lệnh từ xa thì phải có thứ gì đó thức. Không có thiết kế pin nào vừa ngủ 0,3 mA vừa nhận lệnh tức thì.

---

## 2. Sơ đồ khối

```
        ┌──────────────────────────────┐
PIR ───►│ STM32L0 (luôn sống)          │
RTC ◄──►│ • PIR ISR, lịch RTC          │
        │ • ADC pin, DS18B20           │
        │ • điều khiển SOC_EN, CHG_EN  │
        └───────┬──────────────┬───────┘
                │ SOC_EN       │ UART (event/status)
        ┌───────▼───────┐      │
        │ Load switch   │      │
        │ 5V → SoC      │      │
        └───────┬───────┘      │
        ┌───────▼──────────────────────────┐
        │ Luckfox Pico Max (RV1106)        │
        │  • SC3336 MIPI                   │
        │  • microSD                       │
        │  • USB ──► EC25-EU ──► 4G        │
        │  • IR PWM, IR-CUT                │
        └──────────────────────────────────┘

LFP 3,2V ── BMS ── boost 5V/3A ──┬──► Luckfox 5V
                                 ├──► EC25 5V (USB adapter)
                                 └──► buck 3,3V ──► STM32L0 + sensors + IR gate
```

**Tại sao 5 V là rail chính:** Luckfox và USB modem đều nhận 5 V. Chỉ cần một boost 5 V/3 A khỏe + bulk cap; buck 3,3 V riêng cho MCU/cảm biến để nhiễu modem không ảnh hưởng.

---

## 3. Phân bổ chân STM32L0

| Tín hiệu | Hướng | Chân đề xuất | Ghi chú |
|---|---|---|---|
| PIR_OUT | vào | PA0 (EXTI) | AM312 |
| SOC_EN | ra | PA1 | Gate AO3401 / load switch |
| SOC_READY | vào | PA2 | SoC kéo cao khi app sẵn sàng |
| SOC_UART_TX | ra | PA9 | USART1 TX → SoC RX |
| SOC_UART_RX | vào | PA10 | USART1 RX ← SoC TX |
| I2C_SDA | 2 chiều | PB7 | DS3231 + INA226 |
| I2C_SCL | ra | PB6 | 4,7 kΩ pull-up |
| ONEWIRE | 2 chiều | PA4 | DS18B20 ×2, 4,7 kΩ |
| VBAT_ADC | vào | PA5 | Chia áp 1:2 |
| CHG_EN | ra | PA6 | Cấm sạc khi pin nóng |
| LED_STATUS | ra | PA7 | |

**Chân SoC (Luckfox) dùng cho:**
- MIPI CSI → SC3336
- USB → EC25
- SD → thẻ nhớ
- GPIO: IR PWM, IR-CUT A/B, SOC_READY
- UART → STM32L0

---

## 4. Đấu nối modem EC200U-EU (UART)

```
EC200U breakout VIN ──► +5V_MODEM (boost 5 V + 470–1000 µF sát chân)
EC200U GND ──────────► GND chung
EC200U TXD ──────────► U1 UART1_RX (pin 69), mức 3,3 V
EC200U RXD ──────────► U1 UART1_TX (pin 68), mức 3,3 V
EC200U PWRKEY ───────► J11 pin 5 (kéo xuống 500 ms để bật)
EC200U STATUS ───────► J11 pin 6
EC200U RESET ────────► J11 pin 7
Antenna u.FL ────────► keep-out ≥ 10 mm
SIM ─────────────────► khe nano trên breakout
```

- Dùng **UART thay USB**: không cần driver QMI, debug bằng terminal dễ hơn.
- R32/R33 (0 Ω nối USB SoC ↔ modem) để **DNP** ở bản EC200U.
- UART 3,3 V; nếu breakout chỉ ra 1,8 V thì thêm level shifter.
- PPP qua `/dev/ttyS1` 921600; APN: Viettel `v-internet`, Vina `m3-world`, Mobi `m-wap`.
- Nếu không nhận modem: kiểm tra `/dev/ttyS1`, gõ `AT` bằng terminal, xem `dmesg`.

---

## 5. Đấu nối camera + IR

```
SC3336 ──FPC 24-pin──► Luckfox MIPI CSI
IR-CUT ──► GPIO_A / GPIO_B (qua driver có sẵn trên module)
IR LED:
  5V ──► LED1 ──► LED2 ──► 10Ω 1W ──► Drain IRLZ44N
                                       Source ──► GND
                                       Gate ──► GPIO (qua 100Ω), 10kΩ kéo xuống
```

IR do **SoC** điều khiển (không phải MCU) để đồng bộ với frame/exposure.

---

## 6. Thứ tự bring-up

1. Cấp 5 V từ adapter, đo rail 5 V và 3,3 V.
2. Nạp image Luckfox, boot, SSH được.
3. Camera: chụp JPEG 720p, xem trên máy tính.
4. Đo **quick-boot** (xem docs/03) — cổng kiểm tra số 1.
5. Đo **suspend** — cổng kiểm tra số 2.
6. EC25: nhận SIM, QMI, ping, iperf3.
7. PIR → MCU → bật SoC → ghi clip; đo độ trễ.
8. IR: chụp trong tối 3 m, chỉnh dòng.
9. Lắp pin + BMS, xả 7 h.

> Trước khi hàn: xác nhận connector MIPI của Luckfox khớp SC3336 (số chân + bước 0,5 mm).
