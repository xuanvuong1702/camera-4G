# CAM4G — Bàn giao gói thiết kế + firmware

Tài liệu tổng hợp để bàn giao cho xưởng và đội firmware.

---

## 1. Trạng thái

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Schematic | **Hoàn chỉnh, ERC 0** | Core1106 + nguồn + connector + MCU |
| PCB | **Đã route, 0 unconnected, 0 short** | 100×70 mm, 4 lớp |
| Gerber + drill | **Đã xuất** | 28 file + `.drl` |
| BOM | **81 linh kiện** | khớp 100 % với board |
| CPL | **79 linh kiện** | thiếu TP1/TP2 (test point không có paste — đúng) |
| DRC | Còn 11 clearance 0,15 mm + 4 track 0,15 mm | trong khả năng JLCPCB |
| Firmware Linux | **10/10 test pass**, mô phỏng chạy | chưa nối phần cứng |
| Firmware MCU | **Build target OK**, 6/6 test host | I2C slave chưa kiểm chứng trên board |
| Tài liệu sản xuất | Có | stackup, lắp ráp, DRC waiver |
| Test plan | Có | 8 giai đoạn, tiêu chí lô 5 bộ |
| Bring-up guide | Có | 8 bước + rủi ro |

**Chưa đạt:** chạy trên phần cứng thật. Không thể xác minh nếu không có board.

---

## 2. Cấu trúc bàn giao

```
4g-camera/
├── docs/
│   ├── 00…04 (phân tích, quyết định, IPC, validation)
│   ├── 05-simplification.md      # phương án giảm linh kiện
│   ├── 06-manufacturing.md       # hồ sơ gửi xưởng
│   ├── 07-test-plan.md           # kế hoạch kiểm tra
│   └── 08-bringup.md             # hướng dẫn cấp nguồn lần đầu
├── hardware/
│   ├── kicad/CAM4G/              # project, gerber, BOM, CPL, preview
│   ├── core1106/                 # symbol, footprint, datasheet gốc
│   ├── datasheets/               # TPS61088, TPS62840, INA226, CN3058E, EC200U…
│   ├── bom-prototype-v2.csv
│   └── carrier-board-spec.md
└── firmware/
    ├── linux/                    # app Python + 10 test
    └── mcu/                      # C + host test + target build
```

---

## 3. Đã kiểm chứng

- ERC schematic: **0 lỗi, 0 cảnh báo**
- Netlist ↔ board: 81/81 linh kiện, net khớp
- BOM ↔ board: 81/81
- CPL ↔ board: 79/81 (TP1/TP2 không dán — đúng thiết kế)
- Gerber: 28 file + drill, mở được
- Firmware Linux: 10 unit test
- Firmware MCU: 6 nhóm test host + build ARM (1760 B text)

---

## 4. Chưa kiểm chứng (cần board)

1. I2C slave giữa SoC và MCU (AF4, thời điểm TXDR)
2. MIPI impedance — board mẫu do autorouter đi dây
3. Dòng ngủ thực tế (mục tiêu < 1 mA)
4. 7 h ghi liên tục ở 55–60 °C
5. 4G attach + PPP trên 3 nhà mạng
6. Sạc LFP và cấm sạc > 40 °C

---

## 5. Quyết định còn treo

1. **v1 (81 linh kiện) hay v2 giảm linh kiện** (A+B+C → ~69)
2. **Module camera**: dùng module tích hợp IR-CUT hay giữ driver rời
3. **Kích thước**: 100×70 hiện tại (80×55 không đủ chỗ với 81 linh kiện)

---

## 6. Đề xuất bước tiếp theo

1. Đặt PCB 5 bộ + linh kiện theo BOM
2. Nhận board → làm theo `08-bringup.md`
3. Ghi kết quả vào `07-test-plan.md`
4. Nếu mẫu chạy: làm v2 giảm linh kiện trước khi sản xuất hàng loạt

---

## 7. Cập nhật v3 — module 4G EC200U-EU

**Chọn Quectel EC200U-EU** (Cat-1, UART AT, có bảng tần VN B1/B3/B5/B8/B28, tài liệu + QuecOpen SDK phổ biến, ~14 USD kèm breakout).

**Thay đổi:**
- System BOM: `hardware/bom-prototype-v3.csv` (thay EC25 + USB adapter bằng EC200U-EU breakout)
- R32/R33 (0 Ω nối USB) → **DNP**, vì modem dùng UART1
- Firmware: thêm `cam4g/modem.py` (AT client) + 5 test → **15/15 test Linux**
- Tài liệu: `docs/09-modem-ec200u.md`

**Không thay đổi:**
- Schematic carrier (ERC vẫn 0)
- PCB, Gerber, BOM/CPL của carrier — J11 đã có sẵn UART, 5 V, PWRKEY, STATUS, RESET
- Firmware MCU

**Lý do chọn EC200U thay EC25:**
- Cat-1 đủ 720p, rẻ hơn, ít điện hơn
- UART đơn giản hơn USB QMI, không cần driver
- Cùng băng tần VN, cùng nhà sản xuất (Quectel) nên tài liệu đồng nhất

---

## 8. Rà soát thiết kế lần cuối (v4)

Các lỗi tìm thấy và đã sửa:

| # | Lỗi | Mức | Xử lý |
|---|---|---|---|
| 1 | **Footprint TPS61088 sai land pattern** (0,26×0,8 @ ±1,6; EP 1,8) so với TI RHL0020A (0,24×0,6 @ ±1,525; EP 2,05) | Cao — có thể không hàn được | Đã sửa, build lại, route lại |
| 2 | Lỗ khoan góc trên-trái cắt xuyên cuộn L1 | Cao — mất lỗ treo | Dời sang (12, 5) |
| 3 | R32/R33 nối USB trong khi EC200U dùng UART | Trung bình | Đánh **DNP** khi lắp |
| 4 | Net COMP_BOOST (R5/C8 → U2.18) không nối được sau khi nhập route | Trung bình | **2 dây bodge** cho mẫu; v2 dời R5/C8 sát chân 18 |

Trạng thái sau sửa:
- 1374 track + 177 via, route 100 % theo Freerouting
- (đã sửa ở mục 9) DRC khi đó còn 2 unconnected COMP — nguyên nhân và cách xử lý ở mục 9
- Gerber/BOM/CPL đã xuất lại theo board mới

Firmware:
- Linux: **17/17 test pass** (thêm modem AT, camera, GPIO)
- MCU: 6/6 test host, build ARM OK

---

## 9. Chốt sản xuất (v4 final)

**DRC cuối: 0 unconnected, 0 short, 0 clearance, 0 track width.** Chỉ còn 4 lỗi silk_edge và 2 silk_over_copper (in lụa).

Nguyên nhân 2 điểm COMP chưa nối suốt các vòng trước: **zone VBAT toàn board trên F.Cu bị export thành plane**, Freerouting bỏ qua net COMP. Đã bỏ zone trước khi route, route lại, thêm zone B.Cu sau.

Đã sửa thêm:
- Lỗ khoan dời (12,5) → (5,3; 12,5) để cách pad R21 > 0,2 mm
- Pad U2 0,24 → 0,23 mm cho đủ clearance 0,15 ở pad góc
- Netclass clearance 0,2 → 0,15; track 0,10/0,12 → 0,15
- Gerber/BOM/CPL xuất lại; `gerber/CAM4G-fab.zip` 13 file

Còn lại (thương mại): mã LCSC cho thụ động, model breakout EC200U, camera, pin, vỏ.

---

## 10. Sửa 6 lỗi chặn (v5)

| # | Lỗi | Sửa |
|---|---|---|
| 1 | U3 TPS62840 dùng footprint WSON 2×2 thay vì **SON DLC 1,5×2** (8 pad 0,6×0,25, không EP) | Tạo footprint DLC đúng datasheet; board sẽ không khởi động nếu giữ lỗi cũ |
| 2 | INA226 bão hoà: 0,05 Ω × 3 A = 150 mV > ±81,92 mV | Shunt **0,01 Ω** 2512 1 W → ±8,19 A |
| 3 | Shunt 1,55 W ở 5,56 A; JST XH ~3 A | Shunt 2512 1 W; **J2 → JST VH 3,96 mm (10 A)** |
| 4 | Q3 IRLZ44N (TO-220) trong SOT-23; **Q1/Q2/Q3 pad trống** do symbol chân chữ vs SOT-23 1/2/3 | Q3 → **AO3400A**; map chữ→số; modem power và IR giờ đã nối |
| 5 | R34 lấy VBUS_DET từ +5V_SYS | Đổi nhãn schematic sang **VBUS_5V** |
| 6 | Modem/camera chưa chốt ngoại vi | Ghi yêu cầu: breakout có **buck 3,8 V + level shifter 1,8↔3,3 V**; camera chốt pinout/PWDN |

**Phát sinh:** toàn bộ track 0,15 mm kể cả nguồn → thêm plane **In1 GND, In2 VBAT, B.Cu +5V**.

**DRC cuối:** 0 unconnected, 0 short, 0 clearance, 0 track width; chỉ còn 10 silk_over_copper + 5 silk_edge.

**Còn lại:** chọn LCSC cho thụ động, chốt breakout EC200U/camera/pin/vỏ, MIPI chưa kiểm soát impedance.
