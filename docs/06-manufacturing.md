# Hồ sơ sản xuất — CAM4G v5

Tài liệu gửi xưởng cho lô mẫu 5 bộ.

---

## 1. File cần gửi

| File | Vị trí |
|---|---|
| Gerber + drill | `hardware/kicad/CAM4G/gerber/CAM4G-fab.zip` (13 file) |
| BOM | `hardware/kicad/CAM4G/CAM4G-bom.csv` |
| BOM mua hàng (MPN) | `hardware/kicad/CAM4G/CAM4G-bom-procurement.csv` |
| CPL | `hardware/kicad/CAM4G/CAM4G-cpl.csv` |
| Xem trước | `CAM4G-pcb-preview.pdf`, `CAM4G-schematic-preview.pdf` |

---

## 2. Thông số PCB

| Thông số | Giá trị |
|---|---|
| Kích thước | **100 × 70 mm** |
| Số lớp | 4 |
| Độ dày | 1,6 mm |
| Đồng | 1 oz |
| Bề mặt | ENIG |
| Min trace | **0,10 mm** (JLCPCB 4 lớp min 0,09) |
| Min clearance | **0,09 mm** (JLCPCB 4 lớp min 0,09) |
| Via | 0,45 mm / khoan 0,3 mm |
| Lỗ khoan | **(3,0; 24,1)**, (95,5), (5,65), (95,65) |

### Stackup

```
F.Cu   tín hiệu
prepreg 0.1 mm
In1.Cu GND plane (toàn board, không route tín hiệu)
core 1.0 mm
In2.Cu VBAT plane (toàn board, không route tín hiệu)
prepreg 0.1 mm
B.Cu   tín hiệu + zone +5V_SYS
```

---

## 3. Điện trở cách ly

| Cặp | Mục tiêu | Ghi chú |
|---|---|---|
| USB D+/D− | 90 Ω vi sai | ngắn, không kiểm soát chặt |
| MIPI CLK/D0/D1 | 100 Ω vi sai | **chưa kiểm soát**; khi đặt JLCPCB chọn **Impedance Control**, ghi rõ cặp MIPI |

---

## 4. Ghi chú lắp ráp

1. **U1 Core1106**: module stamp-hole 112 pad, stencil + reflow, không hàn tay.
2. **U2 TPS61088**: VQFN-20 3,5×3,5; **L1 đặt sát U2 (7,5 mm)**, mạch vòng boost ngắn; pad 0,23×0,6 (giảm 0,01 so với TI để đủ clearance), EP 2,05; cần via thermal dưới EP.
3. **U3 TPS62840**: **SON DLC 1,5×2 mm, 8 pad 0,6×0,25, pitch 0,5, KHÔNG có pad EP**. Không dùng footprint WSON 2×2.
4. **U5 CN3058E**: SOIC-8 có pad EP — cần dán và tản nhiệt.
5. **J2**: **JST VH 3,96 mm** (10 A), không phải XH.
6. **J3**: FPC 20P 0,5 mm, kiểm tra hướng tiếp điểm.
7. **J11**: header 2×6 1,27 mm, modem cắm rời.
8. **BT1**: holder CR1220, lắp pin sau cùng.
9. **J1 USB-C**: kiểm tra chân CC (5,1 kΩ) trước khi cấp nguồn.

**Thứ tự:** mặt F.Cu trước, mặt B.Cu sau (zone +5V).

---

## 5. Ăng-ten và cơ khí

- Modem trên breakout, antenna u.FL gắn breakout.
- Giữ vùng trống dưới breakout modem trên board mẹ.
- Vỏ nhôm đúc, thermal pad 2 mm từ U1 lên vỏ.
- Chưa có bản vẽ vỏ/assembly drawing.

---

## 6. Pin và an toàn

| Hạng mục | Yêu cầu |
|---|---|
| Pin | LFP 1S 10 Ah + BMS ≥ 10 A |
| Sạc | CN3058E **0,5 A** (R10 = 2,4 kΩ), cấm sạc khi T > 40 °C |
| Vận chuyển | UN38.3 + MSDS |
| Lắp ráp | Đấu pin sau khi kiểm tra rail 5 V/3,3 V |

---

## 7. DRC cuối

| Loại | Số lượng |
|---|---|
| unconnected | 0 |
| short | 0 |
| clearance | 0 |
| track width | 0 |
| silk_over_copper | 10 |
| silk_edge_clearance | 5 |

Chỉ còn lỗi in lụa — xưởng tự cắt lụa, không ảnh hưởng chức năng.

---

## 8. Kiểm tra trước khi gửi

- [ ] Mở `CAM4G-fab.zip` bằng gerbv/KiCad — đủ 4 lớp + drill
- [ ] Đối chiếu BOM với CPL: 81 ref (TP1/TP2 không dán — đúng)
- [ ] Kiểm tra phân cực LED, diode
- [ ] Kiểm tra U1 pad 1 khớp silkscreen
- [ ] Xác nhận 4 lỗ khoan đúng toạ độ
- [ ] Xác nhận J2 là JST VH, U3 là DLC
