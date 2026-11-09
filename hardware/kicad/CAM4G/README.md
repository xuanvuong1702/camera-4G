# CAM4G — KiCad project

Carrier board cho Core1106. **Schematic đã hoàn chỉnh và ERC sạch (0 vi phạm).**

## Trạng thái

| Hạng mục | Trạng thái |
|---|---|
| Schematic | **Hoàn chỉnh** — U1 + nguồn + connector + MCU |
| ERC | **0 lỗi, 0 cảnh báo** |
| Netlist | 85 net, xuất thành công |
| PCB | Chưa vẽ |

## Đã có gì

| File | Nội dung |
|---|---|
| `CAM4G.kicad_pro` | Project KiCad 10 |
| `CAM4G.kicad_sch` | **Bản chính**: toàn bộ schematic, khổ User 1400×1150 |
| `CAM4G-schematic-preview.pdf` | Bản xem trước |
| `CAM4G.net` | Netlist |
| `erc.rpt` | Kết quả ERC (0 vi phạm) |
| `libs/Core1106.kicad_sym` | Symbol chính thức của Luckfox (112 chân) |
| `libs/CAM4G.kicad_sym` | Symbol 4 IC nguồn |
| `libs/Core1106-PCB.pretty/` | Footprint chính thức (112 pad) |
| `libs/3D/Core1106-3D.stp` | Model 3D |
| `NETLIST.md` | Bảng kết nối, pinout camera 20P |
| `../POWER.md` | Thiết kế khối nguồn |
| `CAM4G-sheet0-backup.kicad_sch` | Bản chỉ có Core1106 (lưu) |
| `CAM4G-power-backup.kicad_sch` | Bản có Core1106 + nguồn (lưu) |
| `CAM4G-connectors-backup.kicad_sch` | Bản có thêm connector (lưu) |
| `tools/` | Script sinh schematic (prepare, gen_schematic, gen_symbols, gen_power, merge_power, gen_connectors, gen_mcu) |

## Mở project

```powershell
& "C:\Users\vuong\AppData\Local\Programs\KiCad\10.0\bin\kicad.exe" `
  "C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G\CAM4G.kicad_pro"
```

## Nội dung schematic

- **U1 Core1106** — 112 chân, 55 net chức năng, chân thừa đánh no-connect
- **Nguồn** — TPS61088 (5 V/3 A), TPS62840 (3,3 V), CN3058E (sạc LFP 1 A), INA226
- **Connector** — USB-C, microSD, modem 2×6, camera FPC 20P, PIR, IR, IR-CUT, DS18B20 ×2, pin
- **Công suất** — PMOS + NPN cắt nguồn modem, NMOS driver IR
- **MCU** — STM32L011F4, I2C slave, SWD, UART debug, RTC backup CR1220

## Việc tiếp theo

1. **PCB** — outline 80×55, 4 lớp, đặt module + connector, route.
2. **Hồ sơ sản xuất** — Gerber, BOM, CPL, test plan.
3. **Firmware** — Linux app + MCU.

## Nguyên tắc

Không đoán số chân IC. Pinout lấy từ datasheet hoặc symbol chính thức của KiCad/Luckfox.

## PCB (đang làm)

- `CAM4G.kicad_pcb` — board 80×55 mm, 4 lớp, 4 lỗ khoan, **81 footprint** đã đặt, net đã gán
- `CAM4G.dsn` — file Specctra để route
- `tools/build_pcb.py` — script dựng board (footprint map + placement)
- `tools/import_route.py` — script nhập kết quả route (.ses)
- `pcb-preview.pdf` / `pcb-zoom.png` — bản xem trước

**Trạng thái:** đã đặt linh kiện (auto + anchor), **chưa route**.
Placement hiện là bản nháp — cần tinh chỉnh trước khi route thật.

**Vấn đề gặp:** Freerouting native CLI v2.5.0 crash (GraalVM serialization bug).
Fallback: dùng bản Java jar với JRE 21 đã cài.

### Cập nhật PCB (vòng 3)

- 81/81 footprint đã đặt, **0 copper short**
- DRC còn: 22 clearance, 25 courtyard overlap, 101 silk overlap (cosmetic), 235 unconnected (chưa route)
- Placement dùng pad-bbox + margin, đặt theo tâm footprint (đã sửa lỗi gốc toạ độ JST)
- VQFN-20 TPS61088: footprint tự tạo, đã chuyển pad sang SMD, EP 1.8×1.8

### Cập nhật PCB (vòng 4) — đã route

- **Kích thước đổi 100×70 mm** (lý do: 81 linh kiện + khoảng hở cơ khí không vừa 80×55; xem ghi chú dưới)
- 1170 đoạn track + 172 via đã nhập từ Freerouting
- DRC: **14 unconnected** (toàn bộ net VBAT), 8 clearance 0,15 mm, 3 lỗi silk
- Không còn short, không còn courtyard overlap

**Việc còn lại:** nối 14 điểm VBAT (dùng plane In2 + via, hoặc bus thủ công), rồi Gerber/BOM/CPL.

> **Cảnh báo:** 80×55 không đủ chỗ cho 81 linh kiện với khoảng hở cơ khí tiêu chuẩn.
> Phương án: (a) giữ 100×70, hoặc (b) quay lại 80×55 và bỏ bớt linh kiện / dùng connector 1,25 mm.

### Cập nhật PCB (vòng 5)

- Thêm **VBAT pour trên F.Cu** → unconnected giảm 14 → **5**
- **0 short**, 8 clearance 0,15 mm (fab được), 3 lỗi silk
- Đã xuất **BOM** (`CAM4G-bom.csv`, 81 dòng) và **CPL** (`CAM4G-cpl.csv`)
- 5 điểm chưa nối: U2.9 (VBAT), COMP_BOOST ×2 (R5→U2.18, C8→U2.18), BT1_P (BT1→D6), 1 cảnh báo zone

**Kế hoạch vòng sau:** dời R5/C8 sát chân COMP và D6 sát BT1, rồi **route lại toàn bộ** (placement đổi → track cũ không dùng được).

### Cập nhật PCB (vòng 6) — Freerouting 100%

- Dời R5/C8 sát COMP, D6 sát BT1 → **route lại toàn bộ**
- Freerouting: **1000/1000, 0 unrouted, 0 violation**
- Nhập 1244 track + 176 via bằng parser riêng
- Thêm VBAT pour F.Cu → còn **1 điểm chưa nối**: một đảo VBAT quanh U2.9 tách khỏi mạng chính
- DRC: 8 clearance 0,15 mm, 6 via_dangling, 4 track_width 0,15 mm, 3 lỗi silk
- **BOM + CPL đã xuất**

**Chặn còn lại:** đảo VBAT của U2.9. Cần nối bằng track ngắn hoặc dời U2.

### Cập nhật PCB (vòng 7) — ĐÃ XUẤT GERBER

- **0 unconnected** — board nối đầy đủ
- 1244 track + 176 via + VBAT pour F.Cu + VBAT zone B.Cu
- **Gerber + drill đã xuất** vào `gerber/` (4 lớp, mask, silk, paste, edge, drill)
- **BOM + CPL đã cập nhật** theo placement cuối
- DRC còn: 9 clearance 0,15 mm, 2 hole_clearance, 4 track 0,15 mm, 6 via cảnh báo, lỗi silk
- Kích thước: 100×70 mm (không phải 80×55)

### Cập nhật PCB (vòng 8) — sạch lỗi thật

- **0 unconnected, 0 short, 0 hole_clearance, 0 copper_edge_clearance**
- Via VBAT dời xuống dưới pad U2.9, thêm via tại C1, nối bằng zone B.Cu
- Lỗ khoan góc trên-trái dời khỏi L1 (đến 3.5, 12.0)
- DRC còn: 11 clearance 0,15 mm, 4 track width 0,15 mm (JLCPCB min 0,127/0,1 → fab được), 6 via cảnh báo, lỗi silk
- **Gerber + drill + CPL + BOM đã xuất lại** theo board cuối
