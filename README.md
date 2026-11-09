# Camera 4G chạy pin — dự án sản phẩm

Camera ngoài trời, pin LFP, 4G, hồng ngoại, phát hiện chuyển động, ngủ sâu và đánh thức từ xa.

## Trạng thái

| Hạng mục | Trạng thái |
|---|---|
| Yêu cầu | Đã chốt |
| Kiến trúc | Core1106 (RV1106) + MCU giám sát |
| BOM | v2 — cần cập nhật v3 (Core1106, vỏ nhôm, pin 10 Ah) |
| Phần cứng | KiCad v0.1 — sheet 0 đã chạy ERC |
| Firmware | Khung (chưa chạy trên phần cứng) |
| Cloud/app | Chưa bắt đầu |

## Quyết định quan trọng

- **720p**, IR ≤ 3 m, ghi local 7 h, không khí 40–45 °C.
- **Core1106** (module 30×30, 112 chân) — không dùng dev board Pico Max.
- **Pin LFP 10 Ah** ngay từ đầu (dữ liệu thực: module cần 1 A @ 5 V, đỉnh 2,4 W).
- **Vỏ nhôm đúc** — bắt buộc, vì Core1106 chỉ rated −20…+60 °C.
- **Modem EC25-EU trên board con** cắm header, thay được.
- **Hai chế độ ngủ**: "canh gác nhanh" (~30–60 ngày, nhận lệnh 5–15 s) và "tiết kiệm tối đa" (nhiều tháng, không nhận lệnh từ xa).
- Sạc bị cấm khi nhiệt độ pin > 40 °C.

## Cấu trúc

```
4g-camera/
├── docs/
│   ├── 00-feasibility-and-architecture.md
│   ├── 01-design-decisions-v0.2.md
│   ├── 02-ipc-track-a.md
│   └── 03-week1-validation.md
├── hardware/
│   ├── bom-prototype-v2.csv
│   ├── carrier-bom.csv
│   ├── carrier-board-spec.md
│   ├── core1106/                 # file chính thức của Luckfox (symbol, footprint, 3D, datasheet)
│   └── kicad/CAM4G/              # project KiCad v0.1
└── firmware/                     # khung ESP-IDF (lưu tham khảo)
```

## Bước tiếp theo

1. Vẽ **sheet nguồn** (TPS61088, TPS62840, CN3058E, INA226) — cần datasheet.
2. Vẽ **sheet connector** — cần pinout FPC 24P của SC3336.
3. Vẽ **sheet MCU** (STM32L011, DS3231M, TS3USB221).
4. Xuất PCB 80×55, 4 lớp.
5. Cập nhật BOM v3 và đặt hàng.

## Nguyên tắc làm việc

- Mọi con số công suất/nhiệt đều là **ước tính** cho đến khi đo trên board thật.
- Không đoán số chân IC — sai một chân là hỏng board và mất 3 tuần.
- Không tuyên bố "chạy được" khi chưa có phép đo.

## Cập nhật firmware (vòng 10)

- **Linux app** (`firmware/linux`): 10/10 unit test pass, chạy mô phỏng được
- **MCU firmware** (`firmware/mcu`): biên dịch bằng clang, 6 nhóm test pass
- Toolchain đã cài trên máy: LLVM-MinGW (host), JDK 25 (Freerouting)
- Chưa có `arm-none-eabi-gcc` → firmware target STM32 chưa build được

## Hồ sơ sản xuất & kiểm tra (vòng 11)

- `docs/06-manufacturing.md` — thông số PCB, stackup, ghi chú lắp ráp, DRC đã chấp nhận, checklist gửi xưởng
- `docs/07-test-plan.md` — 8 giai đoạn kiểm tra từ board trống đến field test 72 h, tiêu chí nghiệm thu lô 5 bộ
- `docs/05-simplification.md` — 6 phương án giảm linh kiện (A–F) và khuyến nghị A+B+C

## Bàn giao (vòng 14)

- `HANDOVER.md` — tổng hợp trạng thái, cấu trúc, đã/chưa kiểm chứng, quyết định còn treo
- `docs/08-bringup.md` — hướng dẫn cấp nguồn lần đầu, 8 bước, 5 rủi ro đã biết
- Kiểm tra: BOM 81/81 khớp board, CPL 79/81 (TP1/TP2 không paste — đúng)
