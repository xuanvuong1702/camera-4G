# Camera 4G chạy pin — CAM4G

Camera ngoài trời, pin LFP 10 Ah, 4G, hồng ngoại, phát hiện chuyển động, ngủ sâu và đánh thức từ xa.

> **Bắt đầu đọc từ [`HANDOVER.md`](HANDOVER.md)** — tổng hợp trạng thái, đã/chưa kiểm chứng và việc còn lại.

## Trạng thái

| Hạng mục | Trạng thái |
|---|---|
| Yêu cầu & kiến trúc | Đã chốt |
| Schematic | **ERC 0 lỗi, 0 cảnh báo** |
| PCB | 100×70 mm, 4 lớp, 3 plane (GND/VBAT/+5V), **DRC 0 unconnected / 0 short / 0 clearance** — chỉ còn silk |
| Gerber + drill | Đã xuất, đóng gói `gerber/CAM4G-fab.zip` |
| BOM | 81 dòng, value đúng; kèm BOM mua hàng có MPN |
| CPL | 79 dòng (TP1/TP2 không paste — đúng) |
| Firmware Linux | **17/17 test pass** (mô phỏng) |
| Firmware MCU | **6/6 test host**, build ARM 1720 B |
| Cloud/app | Chưa bắt đầu |

## Quyết định quan trọng

- **720p**, IR ≤ 3 m, ghi local 7 h, không khí 40–45 °C.
- **Core1106G3 N256** (module 30×30, 112 pad) — không dùng dev board Pico Max.
- **Pin LFP 10 Ah** + BMS ngay từ đầu.
- **Vỏ nhôm đúc** — bắt buộc, Core1106 chỉ rated −20…+60 °C.
- **Modem Quectel EC200U-EU** qua UART, breakout cắm header J11; R32/R33 DNP.
- **Hai chế độ ngủ**: "canh gác nhanh" (~40–75 ngày, nhận lệnh 5–15 s) và "tiết kiệm tối đa" (nhiều tháng, chỉ PIR/lịch).
- Sạc bị cấm khi nhiệt độ pin > 40 °C.
- Board **100×70 mm** (80×55 không đủ chỗ cho 81 linh kiện).
- **v5**: sửa U3 sang SON DLC, shunt 0,01 Ω, J2 JST VH 10 A, Q3 AO3400A, VBUS_DET đúng, Q1–Q3 đã nối.

## Cấu trúc

```
4g-camera/
├── HANDOVER.md                   # tổng hợp trạng thái + việc còn lại
├── README.md
├── docs/
│   ├── 00–04                     # phân tích lịch sử (đã lưu)
│   ├── 05-simplification.md      # phương án giảm linh kiện
│   ├── 06-manufacturing.md       # hồ sơ gửi xưởng
│   ├── 07-test-plan.md           # kế hoạch kiểm tra 8 giai đoạn
│   ├── 08-bringup.md             # hướng dẫn cấp nguồn lần đầu
│   ├── 09-modem-ec200u.md        # chọn & đấu modem
│   ├── 10-readiness-audit.md     # rà soát sẵn sàng sản xuất
│   └── 11-cost-estimate.md       # dự tính chi phí lô 5 bộ
├── hardware/
│   ├── POWER.md                  # thiết kế khối nguồn
│   ├── wiring-v2-ipc.md          # kiến trúc & đấu dây
│   ├── bom-prototype-v3.csv      # BOM hệ thống
│   ├── datasheets/               # datasheet gốc
│   └── kicad/CAM4G/              # project, gerber, BOM, CPL, libs, tools
└── firmware/
    ├── linux/                    # app Python + 17 test
    └── mcu/                      # C + host test + target build (CMSIS)
```

## Hồ sơ gửi xưởng

| File | Vị trí |
|---|---|
| Gerber + drill | `hardware/kicad/CAM4G/gerber/CAM4G-fab.zip` |
| BOM | `hardware/kicad/CAM4G/CAM4G-bom.csv` |
| BOM mua hàng (MPN) | `hardware/kicad/CAM4G/CAM4G-bom-procurement.csv` |
| CPL | `hardware/kicad/CAM4G/CAM4G-cpl.csv` |
| Thông số & lắp ráp | `docs/06-manufacturing.md` |

## Nguyên tắc làm việc

- Mọi con số công suất/nhiệt là **ước tính** cho đến khi đo trên board thật.
- Không đoán số chân IC — sai một chân là hỏng board và mất 3 tuần.
- Không tuyên bố "chạy được" khi chưa có phép đo.

## Đã kiểm chứng / chưa

**Đã:** ERC, DRC, BOM↔board, Gerber, firmware test trên host, build ARM.

**Chưa:** chạy trên board thật, I2C slave, dòng ngủ, 7 h ghi ở 60 °C, 4G trên 3 nhà mạng, sạc LFP.

## Việc tiếp theo

1. Chọn mã LCSC cho thụ động (hoặc để JLCPCB map theo value + footprint).
2. Chốt breakout EC200U, camera 20-pin, pin 10 Ah, vỏ.
3. Đặt 5 bộ → làm theo `docs/08-bringup.md`.
