# Hồ sơ sản xuất — CAM4G v1

Tài liệu gửi xưởng cho lô mẫu 5 bộ.

---

## 1. File cần gửi

| File | Vị trí |
|---|---|
| Gerber + drill | `hardware/kicad/CAM4G/gerber/` (28 file + `.drl` + `.gbrjob`) |
| BOM | `hardware/kicad/CAM4G/CAM4G-bom.csv` |
| CPL (toạ độ dán) | `hardware/kicad/CAM4G/CAM4G-cpl.csv` |
| Bản vẽ xem trước | `hardware/kicad/CAM4G/CAM4G-pcb-preview.pdf` |
| Schematic | `hardware/kicad/CAM4G/CAM4G-schematic-preview.pdf` |

---

## 2. Thông số PCB

| Thông số | Giá trị |
|---|---|
| Kích thước | **100 × 70 mm** |
| Số lớp | 4 |
| Độ dày | 1,6 mm |
| Đồng | 1 oz |
| Bề mặt | ENIG |
| Min trace | 0,15 mm |
| Min clearance | 0,15 mm |
| Via | 0,45 mm / khoan 0,3 mm |
| Màu mask | đen hoặc trắng (không ảnh hưởng) |
| Silkscreen | trắng |

### Stackup đề xuất

```
F.Cu (signal)
prepreg 0.1 mm
In1.Cu (GND)
core 1.0 mm
In2.Cu (PWR / VBAT zone)
prepreg 0.1 mm
B.Cu (signal)
```

---

## 3. Điện trở cách ly (impedance)

| Cặp | Mục tiêu | Ghi chú |
|---|---|---|
| USB D+/D− | 90 Ω vi sai | chiều dài ngắn, không cần kiểm soát chặt ở mẫu |
| MIPI CLK/D0/D1 | 100 Ω vi sai | **board hiện tại do autorouter đi dây, chưa kiểm soát impedance** |

> **Cảnh báo:** MIPI trên board mẫu không được kiểm soát impedance. Với 720p và chiều dài ngắn (< 60 mm) khả năng vẫn chạy, nhưng nếu có lỗi hình ảnh thì đây là nghi phạm đầu tiên. Bản sản xuất nên route lại MIPI thủ công.

---

## 4. Ghi chú lắp ráp

1. **U1 Core1106**: module stamp-hole 112 pad, cần stencil + reflow. Không hàn tay.
2. **U2 TPS61088**: VQFN-20 3,5×3,5, pad EP ở giữa — cần via thermal dưới EP.
3. **U5 CN3058E**: SOIC-8 có pad EP — cần dán và tản nhiệt.
4. **J3 camera FPC 20P 0,5 mm**: lắp bằng tay, kiểm tra hướng tiếp điểm.
5. **J11 modem 2×6 1,27 mm**: header, modem cắm rời.
6. **BT1 CR1220**: holder, lắp pin sau cùng.
7. **J1 USB-C**: kiểm tra chân CC (5,1 kΩ) trước khi cấp nguồn.

**Thứ tự ưu tiên dán:** mặt F.Cu trước, sau đó mặt B.Cu (VBAT zone + track B.Cu).

---

## 5. Ăng-ten và cơ khí

- Modem nằm trên board con, ăng-ten gắn trên board con.
- Trên board mẹ: giữ vùng trống dưới board con modem, không đặt đồng/via cao tần.
- Connector u.FL (nếu dùng) đặt sát cạnh board.
- Vỏ nhôm đúc, thermal pad 2 mm từ U1 lên vỏ.

---

## 6. Pin và an toàn

| Hạng mục | Yêu cầu |
|---|---|
| Pin | LFP 1S 10 Ah + BMS 10 A |
| Sạc | CN3058E 1 A, cấm sạc khi T > 40 °C |
| Vận chuyển | UN38.3 + MSDS nếu gửi kèm pin |
| Lắp ráp | Pin đấu sau khi đã kiểm tra rail 5 V/3,3 V |

---

## 7. DRC — các điểm đã chấp nhận

| Loại | Số lượng | Lý do chấp nhận |
|---|---|---|
| clearance 0,15 mm | 11 | JLCPCB standard min 0,127 mm |
| track width 0,15 mm | 4 | JLCPCB min 0,1 mm |
| via 0,45/0,3 | — | JLCPCB hỗ trợ via 0,45 mm |
| silk overlap | 6 | chỉ ảnh hưởng in lụa |

Không còn short, không còn unconnected, không còn lỗi khoan.

---

## 8. Kiểm tra trước khi gửi

- [ ] Mở Gerber bằng trình xem (gerbv/KiCad) — đủ 4 lớp + drill
- [ ] Đối chiếu BOM với CPL: đủ 81 ref
- [ ] Kiểm tra phân cực: LED, diode, tụ hoá (nếu có)
- [ ] Kiểm tra U1 pad 1 khớp silkscreen
- [ ] Xác nhận kích thước 100×70 và 4 lỗ khoan
