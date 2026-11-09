# Kế hoạch kiểm tra — CAM4G v1

Dùng cho 5 bộ mẫu đầu tiên. Mỗi bộ ghi kết quả vào bảng cuối.

---

## Giai đoạn 0 — Kiểm tra board trống

| # | Việc | Dụng cụ | Đạt khi |
|---|---|---|---|
| 0.1 | Soi mối hàn, đặc biệt U1/U2/U5 | kính lúp | không cầu thiếc, không thiếu chân |
| 0.2 | Đo thông mạch 5V/GND, 3V3/GND | VOM | không short |
| 0.3 | Đo điện trở shunt / cầu phân áp | VOM | đúng giá trị ±5 % |

## Giai đoạn 1 — Nguồn (chưa lắp pin, cấp 5 V từ nguồn bench)

| # | Việc | Đạt khi |
|---|---|---|
| 1.1 | Cấp 5 V qua USB-C, đo rail 5V_SYS | 4,9–5,1 V |
| 1.2 | Đo rail 3V3 | 3,25–3,35 V |
| 1.3 | Đo dòng không tải | < 15 mA |
| 1.4 | Cấp pin LFP 3,2 V, đo sạc | 0,9–1,1 A khi pin < 3,4 V |
| 1.5 | Sạc khi pin > 40 °C (tủ sấy) | dòng sạc = 0 |

## Giai đoạn 2 — MCU

| # | Việc | Đạt khi |
|---|---|---|
| 2.1 | Nạp firmware qua SWD (J13) | nhận chip, verify OK |
| 2.2 | Đọc I2C 0x30 từ SoC | thấy VERSION = 0x10 |
| 2.3 | Ghi CMD_WAKE | SOC_EN = 3,3 V |
| 2.4 | Đo dòng STOP mode | < 10 µA (chưa tính cảm biến) |

## Giai đoạn 3 — Core1106

| # | Việc | Đạt khi |
|---|---|---|
| 3.1 | Boot từ thẻ SD | log UART ra console |
| 3.2 | SSH/RNDIS | ping được từ máy tính |
| 3.3 | Nhận camera | `/dev/video15` xuất hiện, chụp được JPEG |
| 3.4 | Ghi 720p ra SD | file phát được, không hỏng |

## Giai đoạn 4 — 4G

| # | Việc | Đạt khi |
|---|---|---|
| 4.1 | Nhận SIM, đăng ký mạng | `+CREG: 1` |
| 4.2 | PPP lên IP | `ip addr` có `ppp0` |
| 4.3 | Upload iperf3 | ≥ 2 Mbps |
| 4.4 | MQTT publish | broker nhận bản tin |
| 4.5 | Live view qua relay | độ trễ ≤ 1,5 s |

## Giai đoạn 5 — Chuyển động & IR

| # | Việc | Đạt khi |
|---|---|---|
| 5.1 | PIR kích hoạt | MCU báo EVENT_PIR trong 200 ms |
| 5.2 | Từ PIR đến frame đầu | ≤ 2 s |
| 5.3 | Ảnh đêm 3 m | nhận diện được người, không cháy sáng |
| 5.4 | IR-CUT chuyển ngày/đêm | nghe click, ảnh đổi màu |

## Giai đoạn 6 — Pin & nhiệt

| # | Việc | Đạt khi |
|---|---|---|
| 6.1 | Ghi liên tục 7 h | không sụp nguồn, file liền mạch |
| 6.2 | Đo dung lượng tiêu thụ 7 h | ≤ 80 % pin 10 Ah |
| 6.3 | Ngủ sâu 24 h | dòng trung bình < 1 mA |
| 6.4 | Tủ sấy 60 °C, ghi 1 h | không throttle, không tắt |
| 6.5 | Sạc ở 45 °C | bị cấm |

## Giai đoạn 7 — Field test 72 h

| # | Việc | Đạt khi |
|---|---|---|
| 7.1 | Lắp ngoài trời, có mái che | không vào nước |
| 7.2 | Sự kiện chuyển động | ghi + upload clip |
| 7.3 | Wake từ app | ≤ 10 s (chế độ online) |
| 7.4 | OTA | cập nhật thành công, rollback được |

---

## Bảng ghi kết quả

| Bộ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|
| #1 | | | | | | | | | |
| #2 | | | | | | | | | |
| #3 | | | | | | | | | |
| #4 | | | | | | | | | |
| #5 | | | | | | | | | |

---

## Tiêu chí nghiệm thu lô mẫu

- 5/5 bộ boot, nhận camera, ghi được 720p
- ≥ 4/5 bộ lên 4G và live view được
- ≥ 4/5 bộ đạt 7 h ghi liên tục
- 5/5 bộ ngủ sâu < 1 mA
- 0 bộ hỏng do quá nhiệt trong 72 h
