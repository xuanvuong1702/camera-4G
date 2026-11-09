# CAM4G — KiCad project (v4 final)

Carrier board cho Core1106 + modem EC200U-EU. **Thiết kế đã route xong và DRC sạch.**

## Trạng thái

| Hạng mục | Kết quả |
|---|---|
| Schematic | Hoàn chỉnh — U1 + nguồn + connector + MCU |
| ERC | **0 lỗi, 0 cảnh báo** |
| PCB | 100 × 70 mm, 4 lớp, **81 footprint** |
| Route | 1320 track + 182 via + zone VBAT B.Cu |
| DRC | **0 unconnected, 0 short, 0 clearance, 0 track width, 0 copper edge** |
| Lỗi còn lại | 4 silk_edge_clearance + 2 silk_over_copper (chỉ in lụa) |
| Gerber | 28 file + drill, đóng gói `gerber/CAM4G-fab.zip` |
| BOM | 81 dòng, value đúng (lấy từ netlist) |
| CPL | 79 dòng (TP1/TP2 không paste — đúng) |

## File chính

| File | Nội dung |
|---|---|
| `CAM4G.kicad_pro` | Project KiCad 10 |
| `CAM4G.kicad_sch` | Schematic đầy đủ (khổ User 1400×1150) |
| `CAM4G.kicad_pcb` | PCB 100×70, 4 lớp, đã route |
| `CAM4G.kicad_dru` | Rule tuỳ chỉnh |
| `CAM4G.net` | Netlist (85 net chức năng) |
| `CAM4G-bom.csv` | BOM 81 dòng |
| `CAM4G-bom-procurement.csv` | BOM mua hàng, có MPN gợi ý |
| `CAM4G-cpl.csv` | Toạ độ dán |
| `gerber/` | Gerber + drill + `CAM4G-fab.zip` |
| `CAM4G-schematic-preview.pdf` | Xem trước schematic |
| `CAM4G-pcb-preview.pdf` | Xem trước PCB |
| `erc-final.rpt` / `drc-final.rpt` | Báo cáo cuối |
| `libs/` | Symbol Core1106, symbol nguồn, footprint, 3D |
| `tools/` | Script dựng board và nhập route |
| `NETLIST.md` | Bảng kết nối, pinout camera 20P |

## Thông số board

| Thông số | Giá trị |
|---|---|
| Kích thước | 100 × 70 mm |
| Số lớp | 4 |
| Độ dày | 1,6 mm |
| Đồng | 1 oz |
| Bề mặt | ENIG |
| Min trace | 0,15 mm |
| Min clearance | 0,15 mm |
| Via | 0,45 mm / khoan 0,3 mm |
| Lỗ khoan | (5,3; 12,5), (95,5), (5,65), (95,65) |

## Các sửa đổi quan trọng

1. **Zone VBAT F.Cu toàn board bị export thành "plane"** → Freerouting bỏ qua net COMP_BOOST.
   Đã bỏ zone trước khi route, route lại, thêm zone B.Cu sau. **Đây là nguyên nhân 2 điểm COMP
   chưa nối tồn tại qua nhiều vòng.**
2. Footprint TPS61088 sửa theo land pattern TI RHL0020A: pad 0,24×0,6 tại ±1,525, EP 2,05.
3. Pad góc U2 giảm 0,24 → 0,23 mm để đủ clearance 0,15 mm (lệch 0,01 mm so với TI).
4. Lỗ khoan dời khỏi L1 và R21.
5. Netclass clearance hạ 0,2 → 0,15 mm cho khớp track thực tế.

## Quy trình dựng lại

```powershell
$py = "C:\Users\vuong\AppData\Local\Programs\KiCad\10.0\bin\python.exe"
$dir = "...\hardware\kicad\CAM4G"
& $py "$dir\tools\build_pcb.py"          # dựng board chưa route
& $py -c "import pcbnew; b=pcbnew.LoadBoard(r'...\CAM4G.kicad_pcb'); pcbnew.ExportSpecctraDSN(b, r'...\CAM4G.dsn')"
# route bằng Freerouting (jar Java 25)
& $py "$dir\tools\ses_import.py"          # nhập .ses
& $py "$dir\tools\post_route_fix.py"      # via + zone VBAT B.Cu
kicad-cli pcb drc ...
```

## Ghi chú

- **MIPI chưa kiểm soát impedance 100 Ω** — rủi ro nếu ảnh lỗi.
- Pad U2 0,23 mm thay vì 0,24 mm — trong dung sai hàn.
- Không còn file backup; lịch sử nằm trong git (`dev`).
