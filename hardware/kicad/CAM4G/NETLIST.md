# Netlist — Carrier board CAM4G v1

Nguồn xác minh: symbol `Core1106.kicad_sym` (112 chân) do Luckfox cung cấp.
Đây là **nguồn sự thật** cho việc vẽ schematic. Cột "Pin" là số chân thực trên module.

---

## 1. Quy ước tên net

| Net | Ý nghĩa |
|---|---|
| `VBAT` | Đầu ra BMS, 3,0–3,65 V |
| `+5V_SYS` | Boost TPS61088, 5 V/3 A |
| `+5V_MODEM` | +5V_SYS qua load switch |
| `+3V3` | Buck TPS62840 |
| `+3V3_RTC` | +3V3 qua 0 Ω cho domain RTC |
| `GND` | Mass chung |
| `USB_DP/DM` | USB 2.0 của Core1106 |
| `USB_MODEM_DP/DM` | Nhánh sang modem |
| `USB_DBG_DP/DM` | Nhánh sang USB-C debug |

---

## 2. Core1106 — bảng chân đã dùng

| Pin | Tên trên symbol | Net | Ghi chú |
|---|---|---|---|
| 9 | MIPI_CSI_RX_CK0N | CAM_MIPI_CK_N | Clock lane 0 |
| 10 | MIPI_CSI_RX_CK0P | CAM_MIPI_CK_P | |
| 11 | MIPI_CSI_RX_D0N | CAM_MIPI_D0_N | Lane 0 |
| 12 | MIPI_CSI_RX_D0P | CAM_MIPI_D0_P | |
| 7 | MIPI_CSI_RX_D1N | CAM_MIPI_D1_N | Lane 1 |
| 8 | MIPI_CSI_RX_D1P | CAM_MIPI_D1_P | |
| 1–6 | CK1 / D2 / D3 | NC | Không dùng (2-lane) |
| 13 | GPIO3_D3 | CAM_PWDN | |
| 14 | I2C3_SDA_M2 | CAM_SDA | |
| 15 | I2C3_SCL_M2 | CAM_SCL | |
| 16 | GPIO3_C7 | CAM_RESET | |
| 18 | VI_CIF_VSYNC_M0 | CAM_VSYNC | Có thể bỏ nếu sensor không cần |
| 19 | VI_CIF_CLKO_M0 | CAM_MCLK | 24 MHz |
| 60 | PWM3_IR_M0 | IR_PWM | LEDC |
| 67 | GPIO1_A2 | SOC_READY | Báo MCU |
| 70 | GPIO1_B0 | IRCUT_A | |
| 71 | GPIO1_B1 | IRCUT_B | |

### SD / SDMMC

| Pin | Tên | Net |
|---|---|---|
| 48 | SDMMC_DET | SD_CD |
| 49 | SDMMC_D0 | SD_D0 |
| 50 | SDMMC_D1 | SD_D1 |
| 51 | SDMMC_D2 | SD_D2 |
| 52 | SDMMC_D3 | SD_D3 |
| 53 | SDMMC_CMD | SD_CMD |
| 54 | SDMMC_CLK | SD_CLK |

### USB

| Pin | Tên | Net |
|---|---|---|
| 22 | USB_N | USB_DM |
| 23 | USB_P | USB_DP |
| 24 | USB_VBUSDET | VBUS_DET (chia 10k/10k từ +5V_SYS) |

### UART / I2C

| Pin | Tên | Net | Ghi chú |
|---|---|---|---|
| 58 | UART0_RX_M0 | DBG_TX | Debug console (qua USB-UART) |
| 59 | UART0_TX_M0 | DBG_RX | |
| 68 | UART1_TX_M0 | MODEM_UART_TX | Tùy chọn, modem chính dùng USB |
| 69 | UART1_RX_M0 | MODEM_UART_RX | |
| 63 | I2C1_SCL_M0 | I2C_SCL | DS3231 + INA226 |
| 64 | I2C1_SDA_M0 | I2C_SDA | |

### Nguồn / điều khiển

| Pin | Tên | Net | Ghi chú |
|---|---|---|---|
| 74 | NPOR | RESET_N | 10 kΩ lên +3V3, 100 nF xuống GND, nút RESET |
| 76 | VCC3V3_RTC | +3V3_RTC | |
| 77 | VCC_1V8 | TP_1V8 | Chỉ test point, không tải |
| 78 | VCC_3V3 | TP_3V3 | Chỉ test point, tối đa 300 mA |
| 79, 80, 81 | VCC5V0_SYS | +5V_SYS | Cần 1 A |
| 21, 25, 28, 29, 36, 47, 55, 56, 57, 75, 82, 83, 84, 89, 112 | GND | GND | 15 chân |

### Không dùng (để NC)

| Nhóm | Pin |
|---|---|
| Audio | 30–35 |
| eMMC / FSPI | 37–46 |
| JTAG | 72, 73 |
| Ethernet | 85–88 |
| LCD / GPIO thừa | 90–111 |
| ADC1 | 27 |
| PWR_CTRL | 61, 62 |

> Các chân NC phải đặt **no-connect flag** trong KiCad để ERC không báo.

---

## 3. Connector

### J1 — USB-C 16P (sạc + debug)

| Pin | Net |
|---|---|
| A1/B1/A12/B12 | GND |
| A4/B4/A9/B9 | VBUS_5V |
| A5 | CC1 (5,1 kΩ xuống GND) |
| B5 | CC2 (5,1 kΩ xuống GND) |
| A6 | USB_DBG_DP |
| A7 | USB_DBG_DM |
| A8 | NC |
| B6 | USB_DBG_DP |
| B7 | USB_DBG_DM |

### J2 — Pin (JST-XH 2P)

| Pin | Net |
|---|---|
| 1 | VBAT |
| 2 | GND |

### J3 — Camera FPC **20P**

Lấy từ schematic chính thức `Luckfox-Pico-Pro-Max.pdf` (khối CAM, connector H1).
Đây là pinout của module SC3336 Camera (A) — khớp trực tiếp với Core1106.

| Pin | Net | Pin | Net |
|---|---|---|---|
| 1 | GND | 11 | CAM_MIPI_D1_N |
| 2 | CAM_MCLK | 12 | GND |
| 3 | GND | 13 | CAM_SCL |
| 4 | CAM_MIPI_D0_P | 14 | CAM_SDA |
| 5 | CAM_MIPI_D0_N | 15 | GND |
| 6 | GND | 16 | CAM_RESET |
| 7 | CAM_MIPI_CK_P | 17 | GND |
| 8 | CAM_MIPI_CK_N | 18 | GND |
| 9 | GND | 19 | +3V3 |
| 10 | CAM_MIPI_D1_P | 20 | +3V3 |

> **Lưu ý sản phẩm:** module SC3336 của Luckfox **không có IR-CUT**, nên chưa dùng được cho
> chế độ ban đêm có hồng ngoại. J8 (IR-CUT 2 chân) được giữ lại để sau này thay bằng module
> camera tự làm (sensor + IR-CUT + lens), vẫn dùng đúng 20 chân này.

### J4 — microSD

| Pin | Tên | Net |
|---|---|---|
| 1 | DAT2 | SD_D2 |
| 2 | CD/DAT3 | SD_D3 |
| 3 | CMD | SD_CMD |
| 4 | VDD | +3V3 |
| 5 | CLK | SD_CLK |
| 6 | VSS | GND |
| 7 | DAT0 | SD_D0 |
| 8 | DAT1 | SD_D1 |
| 9 | CD | SD_CD |
| 10–13 | GND | GND |

### J5 — Antenna u.FL

| Pin | Net |
|---|---|
| 1 | ANT_4G |
| 2 | GND |

### J6 — PIR (JST-XH 3P)

| Pin | Net |
|---|---|
| 1 | +3V3 |
| 2 | PIR_OUT |
| 3 | GND |

### J7 — IR LED (JST-XH 2P)

| Pin | Net |
|---|---|
| 1 | +5V_SYS |
| 2 | IR_LED_DRIVE (drain MOSFET) |

### J8 — IR-CUT (JST-XH 2P)

| Pin | Net |
|---|---|
| 1 | IRCUT_A |
| 2 | IRCUT_B |

### J9 / J10 — DS18B20

| Pin | Net |
|---|---|
| 1 | +3V3 |
| 2 | ONEWIRE |
| 3 | GND |

### J11 — Modem daughterboard (2×6, 1,27 mm)

| Pin | Net | Pin | Net |
|---|---|---|---|
| 1 | +5V_MODEM | 2 | GND |
| 3 | USB_MODEM_DP | 4 | USB_MODEM_DM |
| 5 | MODEM_PWRKEY | 6 | MODEM_STATUS |
| 7 | MODEM_RESET | 8 | GND |
| 9 | MODEM_UART_TX | 10 | MODEM_UART_RX |
| 11 | +3V3 | 12 | GND |

### SW1–SW3

| Switch | Net |
|---|---|
| SW1 BOOT | BOOT_N (kéo xuống GND khi nhấn) |
| SW2 RESET | RESET_N |
| SW3 PAIR | PAIR_N |

---

## 4. Khối nguồn

| Khối | Kết nối |
|---|---|
| CN3058E | VBUS_5V → VBAT, có LED sạc |
| BMS | VBAT ↔ pack LFP |
| TPS61088 | VBAT → +5V_SYS, EN từ MCU |
| TPS62840 | VBAT → +3V3 |
| INA226 | Shunt giữa VBAT và toàn bộ tải |
| Load switch Q1 | +5V_SYS → +5V_MODEM, EN = MODEM_EN |
| Load switch Q2 | +5V_SYS → +5V_IR, EN = IR_EN |

> Chi tiết mạch của TPS61088 / TPS62840 / CN3058E / INA226 sẽ được vẽ khi đối chiếu datasheet từng con — **không đoán số chân**.

---

## 5. Việc còn thiếu để schematic hoàn chỉnh

- [ ] Pinout FPC 24P của SC3336
- [ ] Datasheet + pinout: TPS61088, TPS62840, CN3058E, INA226, DS3231M, STM32L011, TS3USB221
- [ ] Giá trị R/C cho từng khối nguồn (tính theo datasheet)
- [ ] Mạch reset / boot cho Core1106
