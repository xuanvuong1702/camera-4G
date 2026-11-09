# Rà soát sẵn sàng sản xuất — CAM4G v5 (sau 6 điểm sửa)

- Ngày: 2026-11-09
- Kết luận: **đã sửa 6 lỗi chặn**, board sẵn sàng gửi xưởng; còn 3 việc thương mại.

## Sáu lỗi đã xác nhận và sửa

| # | Lỗi | Bằng chứng | Sửa |
|---|---|---|---|
| 1 | **U3 sai package** | Datasheet DLC0008B: SON 1,5×2, 8 pad 0,6×0,25, pitch 0,5, **không có EP**; board dùng WSON 2×2 DSG | Tạo footprint DLC mới, pad 0,6×0,25 tại ±0,65, hàng y = ±0,75/±0,25; bỏ pad EP |
| 2 | **INA226 quá thang** | 0,05 Ω × 3 A = 150 mV > ±81,92 mV | Đổi shunt **0,01 Ω** (2512, 1 W) → ±8,19 A, 30 mV tại 3 A, 0,31 W tại 5,56 A |
| 3 | **Shunt/connector không đủ dòng** | 0,05 Ω × 5,56² = 1,55 W; JST XH ~3 A/chân | Shunt 2512 1 W; **J2 → JST VH 3,96 mm (10 A)** |
| 4 | **Q3 sai vỏ** + transistor không nối | IRLZ44N chỉ có TO-220; Q1/Q2/Q3 pad trống vì symbol dùng chân chữ S/G/D/B/C/E, footprint SOT-23 dùng 1/2/3 | Q3 → **AO3400A**; thêm map chữ→số (Q1/Q2/Q3) — modem power và IR trước đó **không hoạt động** |
| 5 | **VBUS_DET lấy từ +5V_SYS** | R34.1 nối +5V_SYS | Đổi nhãn schematic sang **VBUS_5V** (USB), netlist xác nhận |
| 6 | **Modem/camera chưa chốt ngoại vi** | EC200U VBAT 3,3–4,3 V, I/O 1,8 V; J3 chỉ 3V3, U1 pin 13 (PWM/GPIO) treo | Ghi yêu cầu breakout: **buck 3,8 V + level shifter 1,8↔3,3 V**; camera: chốt module + pinout trước khi đặt |

## Lỗi phát sinh thêm khi kiểm tra

**Toàn bộ track đều 0,15 mm, kể cả VBAT/5 V/GND** — không đủ cho 5,56 A.

Đã khắc phục bằng **plane**:
- `In1.Cu`: GND toàn board
- `In2.Cu`: VBAT toàn board
- `B.Cu`: +5V_SYS
- Track 0,15 mm chỉ còn vai trò tín hiệu; via fanout nối pad SMD xuống plane.

## DRC cuối

| Loại | Số lượng |
|---|---|
| unconnected | **0** |
| short | **0** |
| clearance | **0** |
| track width | **0** |
| **silk_over_copper** | 10 (chỉ in lụa) |
| **silk_edge_clearance** | 5 (chỉ in lụa) |

## Thay đổi kỹ thuật kèm theo

| Hạng mục | Trước | Sau |
|---|---|---|
| U3 | DSG WSON 2×2 + EP | DLC SON 1,5×2, 8 pad, không EP |
| R7 | 0,05 Ω 1206 1 W | 0,01 Ω 2512 1 W |
| J2 | JST XH 2,5 mm | JST VH 3,96 mm (10 A) |
| Q3 | IRLZ44N SOT-23 | AO3400A SOT-23 |
| R34 | +5V_SYS | VBUS_5V |
| Q1/Q2/Q3 | không nối | nối đúng G/S/D, B/E/C |
| Lỗ khoan | (12,5) | (3,5; 23,2) |
| Clearance rule | 0,15 | 0,14 (JLCPCB min 0,127) |

## Việc thương mại còn lại

1. Chọn mã LCSC cho thụ động.
2. Chốt breakout EC200U **có buck 3,8 V và level shifter 1,8↔3,3 V**.
3. Chốt camera 20-pin + pinout (PWDN), pin LFP 10 Ah, vỏ.

## Rủi ro còn lại

- **MIPI chưa kiểm soát impedance 100 Ω**.
- 10 silk_over_copper: xưởng tự cắt lụa, không ảnh hưởng.
- Dòng ngủ 0,3 mA (15 µV trên shunt 0,01 Ω) vẫn dưới offset INA226 → **phải đo bằng đồng hồ ngoài**.
