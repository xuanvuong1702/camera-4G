# Chọn module 4G — Quectel EC200U-EU

- Ngày: 2026-11-09
- Mục tiêu: module có sẵn, tài liệu/SDK phổ biến, dễ tích hợp, tương thích mạng Việt Nam, đi được tới sản xuất.

---

## 1. So sánh

| Tiêu chí | **EC200U-EU** | SIMCom A7670E | Quectel EC25-E |
|---|---|---|---|
| Cat | 1 (10/5 Mbps) | 1 (10/5 Mbps) | 4 (150/50 Mbps) |
| Band VN | B1/B3/B5/B7/B8/B20/B28 | B1/B3/B5/B7/B8/B20/B28 | B1/B3/B5/B7/B8/B20/B28 |
| Giao tiếp | UART + USB | UART + USB | USB |
| AT commands | Rất phổ biến | Phổ biến | Rất phổ biến |
| SDK | QuecOpen + QuecPython | AT only | QuecOpen |
| Giá tham khảo | ~$8–12 | ~$6–9 | ~$18–25 |
| Tài liệu | Đầy đủ (hardware design, AT manual) | Đầy đủ | Đầy đủ |
| Phù hợp dự án | **Có** | Có | Dư thừa |

**Chọn EC200U-EU** vì:
- Đủ băng tần cho cả 3 nhà mạng VN (B1/B3/B5/B8/B28).
- Cat-1 đủ cho 720p (1–2 Mbps), rẻ và ít điện hơn Cat-4.
- UART AT đơn giản hơn USB QMI — không cần driver, dễ debug bằng terminal.
- Có QuecOpen SDK nếu sau này muốn chạy ứng dụng trên module.
- Nguồn hàng phổ biến, có breakout board sẵn.

> Xác nhận band từ tài liệu Quectel: EC200U-EU hỗ trợ LTE-FDD B1/B3/B5/B7/B8/B20/B28 và TDD B38/B40/B41.

---

## 2. Cách tích hợp: breakout có sẵn

Dùng **board breakout EC200U-EU** (5 V vào, UART 3,3 V, khe SIM nano, u.FL) cắm vào header J11 của carrier.

Không cần thiết kế board modem riêng ở giai đoạn prototype.

### Ghép với J11 (2×6, 1,27 mm)

| J11 | Tín hiệu | Nối với EC200U |
|---|---|---|
| 1 | +5V_MODEM | VIN breakout (5 V) |
| 2 | GND | GND |
| 3 | USB_DP | **không dùng** (DNP R32) |
| 4 | USB_DM | **không dùng** (DNP R33) |
| 5 | MODEM_PWRKEY | PWRKEY |
| 6 | MODEM_STATUS | STATUS |
| 7 | MODEM_RESET | RESET |
| 8 | GND | GND |
| 9 | MODEM_UART_TX | RXD của module |
| 10 | MODEM_UART_RX | TXD của module |
| 11 | +3V3 | VIO (nếu breakout cần) |
| 12 | GND | GND |

**Thay đổi so với bản EC25:**
- R32/R33 (0 Ω nối USB SoC ↔ modem) → **DNP**, vì dùng UART.
- Không đổi PCB, không đổi Gerber — chỉ đổi BOM và cách lắp.

---

## 3. Nguồn và ăn-ten

- Breakout tự hạ 5 V → 3,8 V cho module; cần tụ bulk ≥ 470 µF trên rail 5 V.
- Dòng đỉnh khi TX Cat-1: ~0,5 A → boost 5 V 3 A hiện tại dư.
- Antenna: u.FL trên breakout, giữ vùng trống dưới board modem.
- SIM: nano, trên breakout.

---

## 4. UART và PPP trên Linux

- UART1 của Core1106 (pin 68/69) → `/dev/ttyS1` (hoặc ttyAML1 tùy device tree).
- Baud: 115200 lúc bring-up, 921600 khi chạy.
- PPP:

```bash
pppd /dev/ttyS1 921600 \
  noauth defaultroute usepeerdns persist \
  connect 'chat -v -f /etc/chatscripts/ec200u'
```

`/etc/chatscripts/ec200u`:

```
ABORT "NO CARRIER"
ABORT "ERROR"
TIMEOUT 30
"" AT
OK ATE0
OK AT+CGDCONT=1,"IP","<APN>"
OK ATD*99#
CONNECT ""
```

APN theo nhà mạng: Viettel `v-internet`, Vinaphone `m3-world`, Mobifone `m-wap`.

---

## 5. Lệnh AT dùng trong firmware

| Lệnh | Mục đích |
|---|---|
| `AT` | kiểm tra module sống |
| `ATE0` | tắt echo |
| `AT+CPIN?` | trạng thái SIM |
| `AT+CSQ` | cường độ sóng |
| `AT+CREG?` | đăng ký mạng |
| `AT+CGDCONT` | cấu hình APN |
| `AT+QNWINFO` | thông tin mạng/band |
| `AT+CFUN=1/4` | bật/tắt RF (tiết kiệm pin) |

---

## 6. Rủi ro

| # | Rủi ro | Giảm thiểu |
|---|---|---|
| 1 | Breakout dùng UART 1,8 V | Chọn loại 3,3 V; nếu không, thêm level shifter |
| 2 | UART 3 Mbps giới hạn throughput | 720p 1–2 Mbps vẫn đủ; giảm fps nếu cần |
| 3 | Cat-1 độ trễ cao hơn Cat-4 | Chấp nhận cho prototype |
| 4 | Nguồn breakout yếu | Tụ bulk + boost 3 A hiện có |
