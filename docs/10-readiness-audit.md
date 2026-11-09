# Rà soát sẵn sàng sản xuất — CAM4G v4 (kết quả cuối)

- Ngày: 2026-11-09
- Kết luận: **Sẵn sàng gửi xưởng gia công PCB và mua linh kiện** (còn 3 việc thương mại bên dưới).

## Trạng thái cuối

| Hạng mục | Kết quả |
|---|---|
| ERC schematic | **0 lỗi, 0 cảnh báo** |
| DRC PCB | **0 unconnected, 0 short, 0 clearance, 0 track width** |
| Lỗi còn lại | 4 silk_edge_clearance + 2 silk_over_copper (chỉ in lụa) |
| Gerber | 28 file + drill, đã đóng `gerber/CAM4G-fab.zip` (13 file) |
| BOM | 81 dòng, value đúng, khớp board |
| CPL | 79 dòng (TP1/TP2 không paste — đúng) |

## Nguyên nhân gốc đã tìm ra

**Zone VBAT toàn board trên F.Cu bị xuất thành "plane" trong file DSN.** Freerouting coi F.Cu là mặt phẳng nên **bỏ qua net COMP_BOOST** — đó là lý do board luôn còn 2 điểm chưa nối dù router báo 0 unrouted.

**Cách sửa:** bỏ zone F.Cu trước khi export DSN → route lại → net COMP được route bình thường → thêm lại zone B.Cu cho VBAT sau khi route.

## Các sửa đổi khác

| # | Vấn đề | Xử lý |
|---|---|---|
| 1 | BOM value = tên footprint | Tạo lại từ netlist, value đúng (10uF, 100nF…) |
| 2 | Lỗ khoan (12,5) cách pad R21 0,055 mm | Dời đến (5,3; 12,5) |
| 3 | 2 pad góc U2 cách 0,1485 mm | Giảm pad 0,24 → 0,23 mm (lệch 0,01 so với land pattern TI) |
| 4 | Netclass clearance 0,2 trong khi track 0,15 | Hạ netclass xuống 0,15 |
| 5 | Track 0,10/0,12 mm | Nới lên 0,15 mm |
| 6 | BOM hệ thống ghi Pico Max | Sửa thành Core1106G3 N256 |

## Việc thương mại còn lại (không phải lỗi thiết kế)

1. **Chọn mã LCSC cho thụ động** — hoặc để JLCPCB tự map theo value + footprint.
2. **Chốt breakout EC200U-EU** cụ thể (5 V, UART 3,3 V, SIM nano, u.FL).
3. **Chốt camera 20-pin, pin LFP 10 Ah + BMS, vỏ nhôm.**

## Rủi ro kỹ thuật đã biết

- **MIPI chưa kiểm soát impedance 100 Ω** — rủi ro số 1 nếu ảnh lỗi; với 720p và dây ngắn có thể chạy.
- **Pad U2 0,23 mm** thay vì 0,24 mm — vẫn trong dung sai hàn.
- **Chưa có bản vẽ vỏ / assembly drawing.**

## File gửi xưởng

- `hardware/kicad/CAM4G/gerber/CAM4G-fab.zip`
- `hardware/kicad/CAM4G/CAM4G-bom.csv`
- `hardware/kicad/CAM4G/CAM4G-cpl.csv`
- `hardware/kicad/CAM4G/CAM4G-bom-procurement.csv` (MPN gợi ý)
- `docs/06-manufacturing.md` (thông số, stackup, ghi chú lắp ráp)
