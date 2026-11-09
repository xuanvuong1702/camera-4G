# Rà soát sẵn sàng sản xuất — CAM4G v4

- Ngày: 2026-11-09
- Câu hỏi: đã sẵn sàng mua linh kiện và gửi xưởng gia công chưa?

## Kết luận ngắn

**Chưa.** PCB có thể đặt gia công, nhưng **chưa nên** vì board còn 2 điểm chưa nối, và BOM chưa đủ để mua (thiếu MPN cho thụ động, thiếu model module/camera/pin).

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Schematic | ✅ ERC 0 | |
| PCB route | ⚠️ **2 unconnected** | Net COMP_BOOST: R5, C8 → U2.18 |
| DRC | ⚠️ 10 clearance 0,15 mm, 4 track 0,15 mm, 6 via cảnh báo | fab được nhưng chặt hơn rule 0,2 |
| Gerber | ✅ 13 file fab đã đóng zip | `gerber/CAM4G-fab.zip` |
| BOM giá trị | ✅ đã sửa | trước đó Value = tên footprint, nay là 10uF/100nF/… |
| BOM mua hàng | ⚠️ một phần | 55 nhóm, có MPN cho IC/connector, thụ động còn trống |
| Module 4G | ⚠️ chưa chốt MPN breakout | EC200U-EU đã chọn, cần mã cụ thể |
| Camera / pin / vỏ | ❌ chưa chốt | ảnh hưởng BOM hệ thống và cơ khí |

---

## 1. Lỗi chặn (phải xử lý trước khi đặt)

### 1.1 Hai điểm COMP_BOOST chưa nối

- `R5.1` (63,0; 51,1) → `U2.18` (66,4; 54,7)
- `C8.1` (68,1; 51,1) → `U2.18`

Đây là mạng bù của boost, **board sẽ không ổn định nếu hở**. Nguyên nhân: track do autorouter tạo không được nhập đúng, và đường đi trực tiếp bị trace khác chắn.

**Cách xử lý:**
1. **Bodge 2 dây** trên 5 mẫu (nhanh, chấp nhận cho prototype).
2. **v2**: dời R5/C8 sát chân 18 rồi route lại (sạch, nhưng tốn một vòng board).

### 1.2 DRC lệch rule

Board đang dùng clearance 0,2 mm nhưng thực tế có 10 chỗ 0,15 mm và 4 track 0,15 mm. JLCPCB làm được 0,127/0,1 mm, nên **không phải lỗi sản xuất**, nhưng nên hạ rule xuống 0,15 mm cho nhất quán trước khi gửi.

### 1.3 R32/R33

Hai trở 0 Ω nối USB SoC ↔ modem. Với EC200U dùng UART, cần **DNP**. BOM hiện vẫn liệt kê populated.

---

## 2. BOM — đã sửa nhưng chưa đủ mua

**Đã sửa:** BOM cũ lấy `Value` = tên footprint (ví dụ `C_0603_1608Metric` thay vì `100nF`) vì script build board không gán value từ netlist. Đã tạo lại từ netlist: 81 dòng, value đúng.

**Đã thêm:** `CAM4G-bom-procurement.csv` — 55 nhóm, gồm:
- MPN gợi ý cho IC, connector, transistor, diode, inductor, switch.
- Thụ động ghi "select by spec" — cần chọn mã LCSC/JLCPCB basic.

**Còn thiếu để mua:**
- Mã LCSC cho toàn bộ thụ động (hoặc để xưởng tự map theo value + footprint).
- Mã breakout EC200U-EU cụ thể (loại 5 V, UART 3,3 V, SIM nano, u.FL).
- Model camera 20-pin, pin LFP 10 Ah + BMS, antenna.

---

## 3. Gerber

Đã đóng gói **13 file cần thiết** vào `gerber/CAM4G-fab.zip`:
F.Cu, In1, In2, B.Cu, F/B mask, F/B silk, F/B paste, Edge.Cuts, drill, job.

Các lớp Adhesive/Courtyard/Fab/User/Margin đã bỏ khỏi zip.

Lưu ý: **MIPI chưa kiểm soát impedance 100 Ω** (autorouter). Với 720p và dây ngắn có thể chạy, nhưng là rủi ro số 1 nếu ảnh lỗi.

---

## 4. Cơ khí

- Board 100×70 mm, 4 lỗ khoan (12,5), (95,5), (5,65), (95,65).
- Chưa có bản vẽ vỏ, chưa chốt vị trí ăng-ten và khe camera.
- Chưa có bản vẽ lắp ráp (assembly drawing).

---

## 5. Trả lời trực tiếp

| Câu hỏi | Trả lời |
|---|---|
| Gửi xưởng gia công PCB được chưa? | **Được về mặt Gerber**, nhưng nên sửa 2 điểm COMP trước |
| Mua linh kiện được chưa? | **Chưa** — thiếu MPN thụ động và model module/camera/pin |
| Chạy thử được chưa? | **Chưa** — cần board, và cần bodge COMP nếu giữ v4 |

## 6. Đề xuất thứ tự

1. Chốt bodge COMP hoặc làm v2 (dời R5/C8).
2. Hạ rule DRC về 0,15 mm, chạy lại DRC.
3. Chọn mã LCSC cho thụ động (JLCPCB basic).
4. Chốt breakout EC200U, camera, pin, vỏ.
5. Xuất BOM mua hàng cuối + assembly drawing.
6. Đặt 5 bộ.
