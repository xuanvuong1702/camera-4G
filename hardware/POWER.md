# Khối nguồn — Thiết kế chi tiết

- Ngày: 2026-11-09
- Nguồn xác minh: datasheet gốc (đã tải về `hardware/datasheets/`)
- Trạng thái: **pinout đã xác minh**, giá trị linh kiện phần lớn lấy từ mạch ứng dụng mẫu của nhà sản xuất; vài giá trị còn TBD.

---

## 1. Kiến trúc nguồn

```
USB-C 5V ──► CN3058E (sạc LFP 1A) ──► VBAT ◄── BMS ◄── pin LFP 10 Ah
                                        │
                                        ├──► TPS61088 boost ──► +5V_SYS (3 A)
                                        │        ├── Core1106 (1 A)
                                        │        ├── +5V_MODEM (load switch)
                                        │        └── IR LED
                                        └──► TPS62840 buck ──► +3V3 (0,75 A)
                                                 └── STM32L0, DS3231, INA226, cảm biến

INA226 đo dòng qua shunt 0,05 Ω giữa BMS và VBAT.
```

---

## 2. Pinout đã xác minh

### TPS61088-Q1 — RHL, 20 chân VQFN + pad
Nguồn: [datasheet TPS61088-Q1](https://www.ti.com/lit/ds/symlink/tps61088-q1.pdf), mục 6.

| Pin | Tên | Pin | Tên |
|---|---|---|---|
| 1 | VCC | 11, 12 | NC (nối GND) |
| 2 | EN | 13 | MODE |
| 3 | FSW | 14, 15, 16 | VOUT |
| 4, 5, 6, 7 | SW | 17 | FB |
| 8 | BOOT | 18 | COMP |
| 9 | VIN | 19 | ILIM |
| 10 | SS | 20 | AGND |
| | | 21 | PGND (pad) |

### TPS62840 — DLC, SON-8 + EP
Nguồn: [datasheet TPS62840](https://www.ti.com/lit/ds/symlink/tps62840.pdf), mục 6.

| Pin | Tên | Pin | Tên |
|---|---|---|---|
| 1 | GND | 5 | VSET |
| 2 | VIN | 6 | STOP |
| 3 | MODE | 7 | SW |
| 4 | EN | 8 | VOS |
| | | 9 | EP (GND) |

### INA226 — DGS, 10 chân VSSOP
Nguồn: [datasheet INA226](https://www.ti.com/lit/ds/symlink/ina226.pdf), mục 4.

| Pin | Tên | Pin | Tên |
|---|---|---|---|
| 1 | A1 | 6 | VS |
| 2 | A0 | 7 | GND |
| 3 | ALERT | 8 | VBUS |
| 4 | SDA | 9 | IN− |
| 5 | SCL | 10 | IN+ |

### CN3058E — eSOP8 + pad
Nguồn: [datasheet CN3058E](http://www.consonance-elec.com/en/static/upload/file/20231026/1698283098202214.pdf), mục Pin Description.

| Pin | Tên | Pin | Tên |
|---|---|---|---|
| 1 | TEMP | 5 | BAT |
| 2 | ISET | 6 | DONE |
| 3 | GND | 7 | CHRG |
| 4 | VIN | 8 | FB |
| | | 9 | EP (GND) |

---

## 3. TPS61088 — boost 5 V / 3 A

Mạch mẫu của TI (Figure 13, 3,3–4,2 V → 9 V/2 A) dùng đúng dải pin LFP, nên giữ nguyên tần số và bù, chỉ đổi phân áp hồi tiếp.

| Linh kiện | Giá trị | Ghi chú |
|---|---|---|
| L1 | 1,2 µH, Isat ≥ 8 A | theo mạch mẫu |
| C1 | 10 µF | input |
| C2 | 0,1 µF | input HF |
| C3 | 3,3 µF | VCC |
| C6 | 0,1 µF | BOOT→SW |
| C9 | 1 µF | output |
| C4 | 47 µF | output bulk |
| R1 | **178 kΩ** | tính cho 5 V |
| R2 | 56 kΩ | theo mạch mẫu |
| R3 | **267 kΩ** | FSW ≈ 597 kHz |
| R4 | **64,9 kΩ** | ILIM ≈ 8,47 A |
| C7 | 47 nF | SS |
| R5 | **10,5 kΩ** | bù COMP |
| C5 | **2,2 nF** | bù COMP |
| C8 | **DNP** | tính ra 5,7 pF < 10 pF → bỏ |
| MODE | nối GND | chế độ PWM |

**Tính R1:** VOUT = VREF × (1 + R1/R2), VREF = 1,204 V.
R1 = (5 / 1,204 − 1) × 56 k = **176,6 kΩ** → chọn 178 kΩ (E96) → VOUT = 5,03 V.

> Điện áp ra 5,03 V nằm trong dải cho phép của Core1106 (4,6–5,2 V).

---

## 4. TPS62840 — buck 3,3 V / 0,75 A

| Linh kiện | Giá trị | Ghi chú |
|---|---|---|
| L2 | 2,2 µH | theo mạch mẫu |
| C10 | 4,7 µF | input |
| C11 | 10 µF | output |
| R6 | **267 kΩ** | VSET → GND, đặt 3,3 V |
| MODE | GND | power-save |
| STOP | GND | không dùng |
| EN | BUCK_EN | từ MCU |

Nguồn: bảng "Output Voltage Setting, RSET" — hàng có VOUT 3,3 V dùng 267 kΩ.

> **Cần xác nhận:** bảng trong datasheet có 3 cột giá trị E96 cho 3 package. Dùng DLC (SON-8) nên cần đối chiếu đúng cột. Nếu sai, VOUT sẽ khác — đo trên bench trước khi nối tải.

---

## 5. INA226 — đo dòng hệ thống

| Linh kiện | Giá trị | Ghi chú |
|---|---|---|
| R7 | 0,05 Ω, 1 %, 1 W | shunt giữa BMS và VBAT |
| C12 | 0,1 µF | lọc VS |
| R8, R9 | 4,7 kΩ | pull-up SDA/SCL lên +3V3 |
| A0, A1 | GND | địa chỉ 0x40 |
| VBUS | VBAT | đo điện áp bus |

Dòng tối đa 3 A → shunt 0,05 Ω cho 150 mV, công suất 0,45 W. Chọn trở 1 W.

> Đo dòng ngủ 0,3 mA: 15 µV trên shunt — INA226 có LSB 2,5 µV nên đo được, nhưng cần calib và che chắn.

---

## 6. CN3058E — sạc LFP 1 A

| Linh kiện | Giá trị | Ghi chú |
|---|---|---|
| R10 (ISET) | **1,2 kΩ** | ICH = 1011 × 1,205 / 1200 ≈ 1,01 A |
| C13 | 10 µF | VIN |
| C14 | 10 µF | BAT |
| D1 + R11 | LED đỏ + 1 kΩ | CHRG |
| D2 + R12 | LED xanh + 1 kΩ | DONE |
| NTC + R13 | 10 kΩ NTC + 10 kΩ | TEMP (xem §7) |
| FB | nối BAT | điện áp điều chỉnh mặc định 3,6 V |

**Nhiệt:** tổn hao tuyến tính = (5 − 3,6) × 1 A = 1,4 W. Ở 45 °C môi trường, chip sẽ tự giảm dòng khi junction tới ~135 °C. Cần pad đồng lớn + 9 via thermal dưới pad.

---

## 7. Bốn điểm TBD — đã chốt

### 7.1. ILIM (Equation 6): ILIM = 550 000 / RILIM

Tính dòng đỉnh cần thiết ở VIN thấp nhất (3,0 V), VOUT 5 V, IOUT 3 A, hiệu suất 90 %:

- I_DC = 5 × 3 / (3,0 × 0,9) = **5,56 A**
- ΔI = VIN × (VOUT − VIN) / (L × fSW × VOUT) = 3,0 × 2,0 / (1,2 µ × 600 k × 5) = **1,67 A**
- I_peak = 5,56 + 1,67/2 = **6,39 A**
- Chọn ILIM 8,47 A → **R4 = 64,9 kΩ** (E96)
- Dòng giới hạn tối thiểu (trừ 1,3 A): 7,17 A > 6,39 A ✓
- **L1 phải có Isat ≥ 9 A**

### 7.2. FSW (Equation 5): RFREQ = 4 × (1/fSW − tDELAY × VOUT/VIN) / CFREQ

Với fSW = 600 kHz, VIN = 3,2 V, CFREQ = 23 pF, tDELAY = 89 ns:
RFREQ = 4 × (1,667 µ − 89 n × 5/3,2) / 23 p = **265,7 kΩ** → chọn **267 kΩ** → fSW ≈ 597 kHz.

### 7.3. Bù COMP (Equation 18–20)

Thông số: VOUT = 5 V, Rsense = 0,08 Ω, GEA = 190 µA/V (datasheet), VREF = 1,204 V,
D = 1 − 3,2/5 = 0,36, CO = 30 µF (47 µF + 1 µF sau derating), fC = 20 kHz, RO = 5/3 = 1,67 Ω.

- R5 = 2π × VOUT × Rsense × fC × CO / ((1−D) × VREF × GEA)
      = 2π × 5 × 0,08 × 20 000 × 30 µ / (0,64 × 1,204 × 190 µ) = **10,3 kΩ** → chọn **10,5 kΩ**
- C5 = RO × CO / (2 × R5) = 1,67 × 30 µ / 21 000 = **2,4 nF** → chọn **2,2 nF**
- C8 = RESR × CO / R5 ≈ 2 mΩ × 30 µ / 10,5 k = **5,7 pF** < 10 pF → **DNP**

### 7.4. Phân áp TEMP cho CN3058E

Ngưỡng của chip: V_LOW = 42,5–47,5 % VIN, V_HIGH = 77,5–82,5 % VIN.
Dùng NTC 10 kΩ B3950 nối TEMP→GND, điện trở R13 nối TEMP→VIN.

- Muốn cắt sạc ở **40 °C**: R_NTC(40 °C) = 5,31 kΩ.
  R13 = 5,31 × (1/0,425 − 1) = **7,18 kΩ** → chọn **7,15 kΩ**.
- Kiểm tra: ở 0 °C, R_NTC = 33,6 kΩ → VTEMP = 82,5 % VIN → cắt sạc (quá lạnh) ✓
- Ở 25 °C: VTEMP = 58,3 % VIN → trong dải cho phép ✓

→ **Sạc chỉ hoạt động trong khoảng 0–40 °C**, đúng yêu cầu.

### 7.5. Còn lại (không phải TBD, chỉ là lưu ý thiết kế)

- Thêm TVS + tụ 10 µF sát chân VIN của CN3058E khi cắm USB-C.
- Pad đồng + 9 via thermal dưới CN3058E (tổn hao 1,4 W).
- L1 phải chịu 9 A; chọn loại shielded.

---

## 8. Net của khối nguồn

| Net | Kết nối |
|---|---|
| `VBUS_5V` | USB-C VBUS, CN3058E VIN |
| `VBAT` | BMS, CN3058E BAT, TPS61088 VIN, TPS62840 VIN, INA226 IN− |
| `VBAT_BMS` | BMS, INA226 IN+ |
| `+5V_SYS` | TPS61088 VOUT, Core1106, load switch modem, IR |
| `+3V3` | TPS62840 VOS, MCU, cảm biến, INA226 VS |
| `SW_BOOST` | L1, TPS61088 SW (4–7), R3, C6 |
| `BOOT` | C6, TPS61088 BOOT |
| `FB_BOOST` | R1, R2, TPS61088 FB |
| `COMP` | R5, C8, TPS61088 COMP |
| `ILIM` | R4, TPS61088 ILIM |
| `SS` | C7, TPS61088 SS |
| `SW_BUCK` | L2, TPS62840 SW |
| `VSET` | R6, TPS62840 VSET |
| `CHG_STAT` | CN3058E CHRG, D1 |
| `CHG_DONE` | CN3058E DONE, D2 |
| `TEMP` | CN3058E TEMP, NTC, R13 |
| `BOOST_EN`, `BUCK_EN` | MCU GPIO |

---

## 9. Trạng thái KiCad

Khối nguồn **đã được ghép vào schematic gốc** `CAM4G.kicad_sch`:

- 4 IC + 32 linh kiện thụ động + 3 PWR_FLAG, nằm dưới U1 trên khổ A1
- Các net dùng chung (`GND`, `+5V_SYS`, `+3V3`, `I2C_SCL`, `I2C_SDA`, `VBAT`) nối trực tiếp với U1 bằng local label cùng tên
- ERC: **44 vi phạm, đều dự kiến**
  - 38 `isolated_pin_label`: các net camera/SD/modem chưa có connector ở đầu bên kia
  - 6 `pin_not_driven`: USB_VBUSDET, SARADC, 2 chân EN, +3V3_RTC, INA_ALERT — sẽ nối ở sheet MCU/connector
- Không còn `lib_symbol_issues` sau khi bỏ BOM khỏi `sym-lib-table`

`power.kicad_sch` vẫn giữ làm bản tham chiếu riêng; bản chính thức là `CAM4G.kicad_sch`.

### Việc tiếp theo

1. Sheet connector (USB-C, SD, FPC camera, modem header, PIR/IR/DS18B20).
2. Sheet MCU (STM32L011, DS3231M, TS3USB221).
3. PCB 100×70, 4 lớp.
