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


---

## 9. Kiểm tra bổ sung (vòng 39)

| # | Vấn đề | Xử lý |
|---|---|---|
| 1 | **J2 chạm lỗ khoan** (3,5; 23,2) — viền lụa cách tâm 1,4 mm, thân J2 tới y = 21,9 | Dời lỗ sang **(4,0; 24,1)**; J2 vẫn nhô 0,775 mm ra mép board (đúng kiểu JST VH, vỏ cần khoét) |
| 2 | **Hai zone B.Cu chồng nhau** (VBAT cục bộ và +5V toàn board, cùng priority 0) | Đặt **VBAT priority 1**, +5V priority 0; fill lại, DRC 0 short |
| 3 | Stackup chưa khai báo | Đã thêm vào file PCB: F.Cu 0,035 / prepreg 0,1 / In1 0,035 / core 1,26 / In2 0,035 / prepreg 0,1 / B.Cu 0,035, ENIG |
| 4 | Dòng ngủ không đo được bằng INA226 | Ghi rõ trong POWER.md và bring-up: đo bằng Otii/µCurrent |
| 5 | Tài liệu lệch | POWER.md: shunt 0,01 Ω/55,6 mV; docs/01: AO3400A |
| 6 | Sạc 1 A tỏa ~1,4 W trong vỏ kín | **Giảm còn 0,5 A**: R10 1,2 kΩ → **2,4 kΩ**, tổn hao ~0,7 W |
| 7 | U3 symbol còn pin 9 (EP) | **Chưa sửa** — DLC không có EP; cần xóa pin 9 khỏi symbol (v6) |
| 8 | MIPI/vòng boost vẫn autoroute | **Chưa sửa** — cần route tay + impedance control |


---

## 10. Chốt lại sau khi xóa U3 pin 9

| Hạng mục | Kết quả |
|---|---|
| U3 netlist | **8 chân** (1–8), không còn pin 9 EP |
| net_conflict | **0** |
| footprint_symbol_mismatch | **0** |
| R10 | **2,4 kΩ** → sạc 0,5 A |
| C8 | DNP đồng bộ schematic/board |
| Lỗ khoan | (4,0; 24,1) — cách J2 0,6 mm |
| Zone B.Cu | VBAT priority 1, +5V priority 0 |
| ERC | 0 lỗi, 6 cảnh báo (2 lib CAM4G, 4 symbol đã sửa) |
| DRC strict | 0 unconnected/short/clearance; 2 lib issues, 1 filter, 1 field, 13 silk |
| 3D | CAM4G.step (4,9 MB) |
| In 1:1 | CAM4G-1to1.pdf |

**Chưa làm:** route tay vòng boost và MIPI, impedance control, tạo lib CAM4G.pretty.


---

## 11. Parity đã về 0 (vòng 41)

- Tạo libs/CAM4G.pretty (VQFN20_3.5, DLC0008B), đăng ký trong p-lib-table.
- Thêm courtyard vào footprint thư viện Core1106.
- Sửa filter J3 (Connector_FFC-FPC:*) và description U1.
- **DRC strict: chỉ còn 10 silk_over_copper + 3 silk_edge_clearance** — 0 unconnected, 0 short, 0 clearance, 0 net conflict, 0 footprint mismatch, 0 lib issue.
- ERC: 0 lỗi, 5 cảnh báo lib_symbol_mismatch do các symbol đã sửa (TPS62840 bỏ EP, Q1–Q3 đổi số chân, Conn_01x20 thêm filter).

**Còn lại:** route tay boost/MIPI, impedance control, in 1:1.


---

## 12. Phát hiện chặn: L1 cách U2 ~80 mm

Khi kiểm tra vị trí linh kiện cho vòng boost:

| Linh kiện | Toạ độ |
|---|---|
| U2 (TPS61088) | (66,37; 56,21) |
| **L1 (1,2 µH)** | **(5,41; 5,41)** |
| C1 (10 µF vào) | (61,29; 54,94) |
| C4 (47 µF ra) | (58,75; 51,13) |

Khoảng cách L1–U2 ≈ **80 mm**. Với boost 600 kHz, 5 V/3 A, vòng SW dài như vậy gây điện cảm ký sinh lớn, ringing, EMI và giảm hiệu suất. Đây là **lỗi placement nghiêm trọng**, không phải lỗi route.

Đã thử dời L1 về (58,4; 56,2) và route lại vòng boost bằng track 0,3–1,2 mm:
- Kết quả: 15 short, 10 unconnected, 5 courtyard overlap — vùng quanh U2 quá chật cho cuộn 8×8 mm.
- Đã **revert** board về trạng thái trước đó.

**Kết luận:** board hiện tại **chưa nên đặt hàng**. Cần re-layout riêng vùng nguồn:
1. Đặt L1 sát chân SW (≤ 5 mm), C1/C11 sát VIN, C4/C9 sát VOUT.
2. Vòng C_in → L → SW → C_out ngắn nhất, track ≥ 1 mm hoặc dùng polygon.
3. Sau đó route lại vùng nguồn và kiểm tra DRC.

Các mục khác đã xong: parity 0, CAM4G lib, courtyard, filter, description.
