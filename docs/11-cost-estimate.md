# Dự tính chi phí linh kiện — CAM4G (lô 5 bộ)

- Ngày: 2026-11-09
- Đơn vị: USD, tỷ giá tham chiếu 1 USD ≈ 26.300 VND
- **Đây là ước tính**, không phải báo giá. Giá thay đổi theo nhà cung cấp, số lượng và thời điểm.

---

## 1. Linh kiện trên board (mỗi bộ)

| Nhóm | Giá/bộ | Ghi chú |
|---|---|---|
| Core1106G3 N256 (U1) | 22,00 | module chính |
| TPS61088 (U2) | 1,80 | boost 5 V |
| TPS62840 (U3) | 1,60 | buck 3,3 V |
| INA226 (U4) | 1,60 | đo dòng |
| CN3058E (U5) | 0,80 | sạc LFP |
| STM32L011F4 (U6) | 1,00 | MCU |
| Connector (USB-C, FPC, microSD, JST, header, SW) | 2,60 | 13 connector |
| Cuộn cảm, shunt, diode, LED, transistor | 1,60 | |
| Thụ động 0603 (~60 con) | 0,72 | ~0,012/con |
| NTC, test point, pin CR1220 | 0,54 | |
| **Tổng board** | **33,86** | |

## 2. Module và phụ kiện ngoài board (mỗi bộ)

| Hạng mục | Giá/bộ | Ghi chú |
|---|---|---|
| EC200U-EU breakout | 14,00 | 5 V, UART 3,3 V, SIM nano, u.FL |
| Camera SC3336 20-pin | 10,00 | mua kèm module để khớp FPC |
| Pin LFP 10 Ah + BMS | 30,00 | chưa gồm phí vận chuyển pin |
| Antenna 4G u.FL | 4,00 | |
| PIR AM312 | 1,50 | |
| DS18B20 ×2 (có dây) | 4,00 | |
| Vỏ nhôm (gia công prototype) | 20,00 | CNC, chưa gồm khuôn |
| Dây harness, keo tản nhiệt | 3,00 | |
| Pin CR1220 | 0,35 | |
| **Tổng phụ kiện** | **86,85** | |

## 3. Chi phí mỗi bộ

| | USD |
|---|---|
| Linh kiện board | 33,86 |
| Module + phụ kiện | 86,85 |
| **Mỗi bộ** | **120,71** |

## 4. Chi phí một lần (chia cho 5 bộ)

| Hạng mục | USD |
|---|---|
| PCB 5 bộ, 4 lớp, 100×70, ENIG | 45 |
| Stencil | 10 |
| Gia công SMT 5 bộ (81 linh kiện) | 100 |
| Vận chuyển linh kiện + PCB về VN | 50 |
| **Tổng một lần** | **205** |

## 5. Tổng lô 5 bộ

| | USD | VND |
|---|---|---|
| 5 × 120,71 | 603,55 | ~15,9 triệu |
| Chi phí một lần | 205,00 | ~5,4 triệu |
| **Tổng** | **~809** | **~21,3 triệu** |
| **Trung bình/bộ** | **~162** | **~4,3 triệu** |

**Khoảng hợp lý:** 650–1.000 USD cho 5 bộ (130–200 USD/bộ), tuỳ giá module và vỏ.

---

## 6. Chỗ chi phí dao động mạnh

| Yếu tố | Ảnh hưởng |
|---|---|
| Core1106 | 15–25 USD tuỳ bản N256 và nguồn |
| EC200U breakout | 8–18 USD tuỳ loại có/không vỏ, có/không antenna |
| Vỏ nhôm | 20 USD (CNC lẻ) → 5–10 USD nếu đặt số lượng lớn; khuôn thì hàng nghìn USD |
| Pin LFP 10 Ah | 25–40 USD, cộng phí vận chuyển hàng nguy hiểm |
| Gia công SMT | 60–150 USD tuỳ xưởng và việc ta cấp linh kiện hay không |

## 7. Chưa tính

- Công lao động của bạn (thiết kế, lắp, test).
- Dụng cụ: ST-Link, nguồn bench, đồng hồ, tủ sấy.
- Thuế nhập khẩu, VAT.
- Board dự phòng (nên đặt 7–8 bộ thay vì 5).
- Chứng nhận (CE/FCC), nếu bán sản phẩm.
- Khuôn vỏ nếu sản xuất hàng loạt.

## 8. Đề xuất

1. Đặt **8 bộ PCB** thay vì 5 — chi phí tăng ~15 USD nhưng có board dự phòng.
2. Mua **10 bộ linh kiện thụ động** — rẻ và tránh thiếu.
3. Mua module (Core1106, EC200U, camera) **dư 1–2 bộ** vì dễ hỏng khi hàn.
4. Vỏ: làm 2 bản CNC trước để kiểm tra cơ khí, sau đó đặt 5.
