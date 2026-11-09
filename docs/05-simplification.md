# Giảm linh kiện & dễ thi công — phân tích phương án

- Ngày: 2026-11-09
- Bối cảnh: kích thước board không còn là ràng buộc; ưu tiên **hoạt động được, gọn, dễ thi công**; vẫn phải đi được từ prototype sang sản xuất.

---

## 1. Nguyên tắc: "module" khác "dev board"

Được phép dùng module, nhưng chỉ module **cấp OEM**:

| Tiêu chí | Yêu cầu |
|---|---|
| Tài liệu | Datasheet + pinout + mechanical drawing |
| Vòng đời | Cam kết còn hàng ≥ 3–5 năm |
| MOQ | Có đường mua lẻ cho prototype, MOQ rõ cho sản xuất |
| Second source | Có ít nhất 1 module thay thế tương đương |
| Interface | Chốt trên carrier (chân cắm/FPC) để đổi module không đổi board |

**Không** dùng dev board (Pico Max) hay module không rõ nguồn gốc trong thiết kế sản xuất.

---

## 2. Các phương án giảm linh kiện

### A. Camera module tích hợp IR-CUT + IR LED (tự động)

Thay cụm rời: 2 LED IR + MOSFET + trở + 2 connector (J7, J8) bằng **module camera day/night** có IR-CUT và LED IR tích hợp, điều khiển tự động bằng quang trở.

- Giảm: **5 linh kiện** (Q3, R19, R20, J7, J8) + bỏ công căn chỉnh LED
- Giữ nguyên: giao tiếp 20-pin FPC, 3,3 V
- Rủi ro: chất lượng đêm phụ thuộc module; cần chốt pinout 20-pin và MOQ
- Tác động tính năng: không đổi (IR vẫn bật khi tối)

### B. Bỏ INA226

Đo dòng bằng **ADC 10-bit của SoC** qua shunt + op-amp? Không — op-amp lại thêm linh kiện. Thay bằng:
- Đo điện áp pin qua cầu phân áp (2 trở) → ước lượng % pin
- Hoặc fuel gauge 2 chân (MAX17048) nếu cần chính xác hơn

- Giảm: **3 linh kiện** (U4, R7 shunt, C12); nếu dùng MAX17048 thì giảm 2
- Mất: đo dòng ngủ chính xác (tính năng debug, không phải tính năng người dùng)
- Rủi ro: ước lượng pin kém chính xác khi tải thay đổi

### C. Gộp connector cảm biến

PIR (3) + IR (2) + IR-CUT (2) + DS18B20 ×2 (6) = 13 chân rời rạc trên 5 connector.
Gộp thành **1 connector 12 chân** (hoặc 2 connector 6 chân) + dây harness.

- Giảm: **4 connector**, giảm số mối hàn tay
- Rủi ro: harness phải làm đúng thứ tự; khó thay lẻ từng cảm biến

### D. Bỏ MCU giám sát (STM32L011)

Chuyển vai trò về SoC + mạch chốt nguồn rời:
- PIR/RTC/nút → chốt P-MOS bật 5 V
- SoC giữ chốt bằng 1 GPIO, tự tắt khi xong
- Đo pin/nhiệt bằng ADC/1-Wire của SoC
- Modem điều khiển trực tiếp bằng GPIO SoC

- Giảm: **~6 linh kiện** (U6 + R25 + C17–C19 + R31)
- Mất: telemetry I2C độc lập khi SoC tắt; wake theo lịch khó hơn (RTC domain không có chân alarm ra ngoài)
- Rủi ro: firmware SoC phức tạp hơn, khó debug hơn

### E. Module nguồn COTS (chỉ cho prototype)

Thay U2/U3/U5 + ~25 thụ động bằng module boost 5 V + module buck 3,3 V + module sạc LFP.

- Giảm: **~25 linh kiện** — nhiều nhất
- Nhưng: module nguồn rẻ thường không có datasheet đầy đủ, MOQ lạ, không đạt tiêu chí §1
- **Không khuyến nghị** cho đường sản xuất; chỉ dùng để test ý tưởng

### F. Module camera 4G tích hợp (SoC + 4G + camera)

Giảm nhiều nhất nhưng khoá vào nhà cung cấp, khó tuỳ biến firmware, MOQ cao.
**Không khuyến nghị** vì mục tiêu là làm sản phẩm có kiểm soát.

---

## 3. So sánh

| Phương án | Giảm | Giữ tính năng | Đường sản xuất | Rủi ro |
|---|---|---|---|---|
| A. Camera tích hợp IR | 5 | Có | Tốt | MOQ, pinout |
| B. Bỏ INA226 | 3 | Gần đủ | Tốt | Ước lượng pin |
| C. Gộp connector | 4 | Có | Tốt | Harness |
| D. Bỏ MCU | 6 | Một phần | Trung bình | Firmware, wake lịch |
| E. Module nguồn | 25 | Có | **Kém** | Không ổn định |
| F. Module 4G IPC | 40+ | Khó | **Kém** | Lock-in |

**Đề xuất: A + B + C** → 81 xuống **~69 linh kiện**, giảm 2 loại linh kiện khó (driver IR, INA226), vẫn giữ MCU và đường sản xuất sạch. Nếu cần mạnh hơn, thêm **D** → ~63.

---

## 4. Kiến trúc đề xuất sau giảm

- Core1106 (module OEM)
- EC25-EU trên board con (module OEM)
- Camera day/night 20-pin, IR-CUT + LED tích hợp (module OEM)
- Nguồn: giữ TPS61088 + TPS62840 + CN3058E (đã tối ưu cho LFP/5V/3A)
- MCU STM32L011 (giữ)
- 1 connector cảm biến 12 chân thay 5 connector rời
- Bỏ INA226, đo pin bằng ADC + cầu phân áp

---

## 5. Việc cần làm nếu chốt

1. Chọn module camera day/night 20-pin, lấy datasheet + pinout + MOQ
2. Sửa schematic: bỏ U4/R7/C12, bỏ Q3/R19/R20/J7/J8, gộp connector
3. Cập nhật BOM, PCB (giảm ~12 linh kiện, bớt 2 connector)
4. Chạy lại ERC/DRC, xuất Gerber mới
