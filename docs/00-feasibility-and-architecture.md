# Camera 4G chạy pin — Phân tích khả thi & Kiến trúc v0.1

> **Tài liệu lịch sử (vòng 1–4).** Trạng thái hiện tại xem [HANDOVER.md](../HANDOVER.md).


- Ngày: 2026-11-08
- Trạng thái: **draft** — đã được cập nhật bởi [v0.2](01-design-decisions-v0.2.md) với các yêu cầu đã chốt
- Mọi con số công suất dưới đây là **ước tính để tính toán**, phải đo lại trên board thật ở Giai đoạn 1.

---

## 1. Yêu cầu ghi nhận

| # | Yêu cầu | Diễn giải kỹ thuật | Ưu tiên |
|---|---|---|---|
| R1 | Camera 4G dùng pin | 1S Li-ion, sạc USB-C, không cần dây mạng | Bắt buộc |
| R2 | Chế độ ngủ, đánh thức qua phần mềm | MCU quản lý nguồn + modem nhận lệnh từ cloud | Bắt buộc |
| R3 | Xem qua 4G: P2P hoặc qua server | WebRTC (P2P + TURN relay) hoặc RTSP/FLV qua server | Bắt buộc |
| R4 | Phát hiện chuyển động | PIR (chính) + phát hiện pixel trên ISP (phụ) | Bắt buộc |
| R5 | Hồng ngoại (night vision) | IR 850/940nm + IR-cut removable | Bắt buộc |
| R6 | Tự đánh thức ghi hình theo điều kiện | Lịch RTC, PIR, lệnh cloud, ngưỡng pin | Bắt buộc |
| R7 | Ghi liên tục ≥ 7 giờ | Pin đủ cho 7h ở điều kiện X (xem §5) | Bắt buộc |
| R8 | Ngủ càng lâu càng tốt | Mục tiêu ≥ 30 ngày, hướng tới 90 ngày | Cao |

**Điều kiện X chưa xác định** — đây là biến quan trọng nhất của toàn bộ bài toán:
7h ghi **chỉ vào thẻ nhớ** khác rất nhiều với 7h **vừa ghi vừa xem live 4G**, và khác nữa với 7h **ban đêm bật IR**.

---

## 2. Kết luận nhanh

**Khả thi về kỹ thuật**, với 3 lưu ý:

1. **Nút thắt không phải camera, mà là IR ban đêm + truyền 4G.** Cụm camera + encode + thẻ nhớ chỉ ~1,2–1,7 W; modem 4G và IR mới là thứ ăn pin.
2. **7h ban ngày + live 720p** thoải mái với pin 10 Ah. **7h ban đêm bật IR full** cần pin 15–20 Ah hoặc phải duty-cycle IR.
3. **P2P trên 4G thường không đi trực tiếp được** vì CGNAT của nhà mạng. Kiến trúc đúng là WebRTC + TURN relay (vẫn gọi là "P2P" trên app, nhưng thực tế có thể đi qua server).

---

## 3. Kiến trúc hệ thống

```
                    ┌──────────────────────────────────┐
   PIR ────IRQ─────►│ MCU giám sát                     │
   RTC ◄───I2C─────►│ (STM32L0 / ESP32-C6)             │
   Nút nhấn ───────►│ • quản lý trạng thái nguồn       │
                    │ • đánh thức SoC, đếm sự kiện     │
                    │ • đọc pin, điều khiển load-switch│
                    └──────┬───────────────────┬───────┘
                           │ EN (load switch)  │ UART / USB
                    ┌──────▼────────┐   ┌──────▼─────────┐
   Camera ──MIPI───►│ SoC xử lý     │   │ Modem 4G       │
   IR LED ◄──PWM────│ RV1106 / T31  │◄──┤ EC200U / EC25  │──► Antenna
   ICR ─────GPIO────│ ISP + H.265   │   │ Cat-1bis/Cat-4 │
                    │ + ghi SD      │   └────────────────┘
                    └──────┬────────┘
                           │ SDIO
                    ┌──────▼────────┐
                    │ microSD       │
                    │ (high endure) │
                    └───────────────┘

   Pin 1S ── BMS + fuel gauge ── buck 3,3 V ── boost 5 V (IR)
                              └─ load switch từng rail (SoC / modem / IR)
```

**Nguyên tắc thiết kế:**
- MCU giám sát **luôn sống** ở ~0,1–0,3 mA, có quyền bật/tắt SoC và modem.
- SoC là thứ tốn pin nhất → chỉ bật khi cần ghi hoặc cần xử lý.
- Modem có 2 chế độ: tắt hẳn (tiết kiệm nhất) hoặc giữ đăng ký eDRX/PSM (nhận lệnh nhanh).
- PIR đánh thức MCU bằng interrupt, không cần CPU chạy.

---

## 4. Trạng thái nguồn

| Trạng thái | Thành phần chạy | Dòng @3,7 V | Công suất | Dùng khi |
|---|---|---|---|---|
| S0 Ngủ sâu | MCU stop + RTC + PIR | 0,1–0,3 mA | 0,4–1,1 mW | Ban đêm / không ai xem |
| S1 Ngủ có kết nối | S0 + modem eDRX | 2–4 mA | 7–15 mW | Cần nhận lệnh trong vài giây |
| S2 Ghi local | SoC + camera + encode + SD | 300–450 mA | 1,1–1,7 W | Có chuyển động, ghi thẻ |
| S3 Ghi + live 720p | S2 + modem ~1 Mbps | 500–750 mA | 1,9–2,8 W | Đang xem trên app |
| S4 Ghi + live 1080p | S2 + modem ~2,5 Mbps | 650–950 mA | 2,4–3,5 W | Xem nét hơn |
| S5 Ban đêm + IR | S2/S3 + IR LED | +250–550 mA | +0,9–2,0 W | Trời tối |

---

## 5. Bài toán pin

Giả định pin 1S Li-ion, dùng được 85% dung lượng (còn lại cho lão hoá + lạnh):

| Phương án | Năng lượng danh định | Dùng được |
|---|---|---|
| 10 Ah (2×21700 5 Ah) | 37 Wh | 31,5 Wh |
| 15 Ah (3×21700 5 Ah) | 55,5 Wh | 47 Wh |
| 20 Ah (4×21700 5 Ah) | 74 Wh | 63 Wh |

### 5.1. 7 giờ ghi liên tục

| Kịch bản | Công suất | Năng lượng 7h | % pin 10 Ah | % pin 15 Ah |
|---|---|---|---|---|
| Ghi local 1080p | 1,4 W | 9,8 Wh | 31% | 21% |
| Ghi + live 720p | 2,3 W | 16,1 Wh | 51% | 34% |
| Ghi + live 1080p | 2,9 W | 20,3 Wh | 64% | 43% |
| Ban đêm + IR + live 720p | 3,8 W | 26,6 Wh | **84%** | 57% |
| Ban đêm + IR mạnh + live 1080p | 4,8 W | 33,6 Wh | **107% ✗** | 71% |

**Kết luận:**
- Pin 10 Ah: đủ cho 7h ban ngày (kể cả có live), **không đủ margin** cho 7h đêm bật IR liên tục.
- Pin 15 Ah: đáp ứng mọi kịch bản trên với margin 30–40%, chịu được lạnh và lão hoá.
- **Khuyến nghị: 15 Ah** (3×21700 hoặc pouch 1S), hoặc 10 Ah nếu chấp nhận IR duty-cycle ~50% và giới hạn tầm IR.

### 5.2. Chế độ ngủ

| Trạng thái | Dòng trung bình | Thời gian với pin 15 Ah |
|---|---|---|
| S0 ngủ sâu | 0,2 mA | ~6 năm lý thuyết → thực tế 1–2 năm (tự xả) |
| S1 eDRX | 3 mA | ~208 ngày |
| Poll mỗi 5 phút (thức 20 s) | ~0,6 mA | ~1,5 năm lý thuyết |

→ **Nếu cần đánh thức nhanh (vài giây), chấp nhận S1 và standby ~6 tháng.** Nếu chấp nhận trễ 5 phút, standby gần như chỉ bị giới hạn bởi tự xả của pin.

---

## 6. Bài toán 4G

### 6.1. Dung lượng data (quan trọng vì tốn tiền hàng tháng)

| Chất lượng | Bitrate | 1 giờ | 7 giờ |
|---|---|---|---|
| 720p | ~1 Mbps | 0,45 GB | 3,2 GB |
| 1080p | ~2,5 Mbps | 1,1 GB | 7,9 GB |
| 1080p nét | ~4 Mbps | 1,8 GB | 12,6 GB |

→ Thiết kế nên **mặc định ghi local + xem live theo yêu cầu + upload clip sự kiện**, không stream 24/7.

### 6.2. P2P hay server?

- 4G của nhà mạng VN hầu hết là **CGNAT** → hai thiết bị không có IP công khai, P2P trực tiếp thường thất bại.
- Giải pháp thực tế: **WebRTC + STUN + TURN relay**. Ưu tiên P2P khi may mắn NAT mở, fallback TURN khi không.
- Nếu tự làm: LiveKit (SFU + TURN sẵn) hoặc mediasoup + coturn trên 1 VPS.
- Nếu muốn nhanh: dùng nền tảng có sẵn (Tuya IPC SDK, Agora, 100ms) — đổi lại phụ thuộc và phí.

### 6.3. Band 4G cho Việt Nam
Cần module hỗ trợ **B1 / B3 / B5 / B8 / B28** (và B40/B41 nếu cần). Chọn đúng variant:
- Quectel **EC200U-EU** / **EG915U-EU** (Cat-1bis, rẻ, ít điện)
- Quectel **EC25-E** (Cat-4, nhanh hơn, tốn điện hơn)

---

## 7. Đánh thức bằng phần mềm — 4 phương án

| Phương án | Độ trễ | Dòng chờ | Nhận xét |
|---|---|---|---|
| A. Modem giữ idle (DRX) + SMS/UDP | < 2–5 s | 2–5 mA | Nhanh nhất, tốn pin nhất |
| B. Modem eDRX (5–10 s) + MQTT | 5–15 s | 1–3 mA | **Cân bằng tốt — khuyến nghị mặc định** |
| C. Poll server mỗi 1–5 phút | 1–5 phút | 0,2–1 mA | Đơn giản, phù hợp chế độ tiết kiệm |
| D. PSM + RTC wake mỗi 30–60 phút | 30–60 phút | ~0,05 mA | Tiết kiệm nhất, gần như "offline" |

**Khuyến nghị:** B làm mặc định, C làm "chế độ tiết kiệm pin", D cho "chế độ mùa đông/để lâu". Cho người dùng chọn trong app.

---

## 8. Phần cứng — 2 hướng

### Track A (khuyến nghị): SoC Linux IPC + modem rời
Ưu: H.265, chất lượng ảnh tốt, boot nhanh, kiến trúc giống camera thương mại.
Nhược: SDK vendor phức tạp hơn, cần thêm MCU giám sát.

| Khối | Linh kiện đề xuất | Giá ước tính (qty 100) |
|---|---|---|
| SoC | Rockchip RV1106G3 (256 MB) hoặc Ingenic T31X | $6–9 |
| Sensor | SC3336 (2 MP) / IMX307 (STARVIS, low-light tốt hơn) | $4–9 |
| Modem | Quectel EC200U-EU / EG915U-EU | $9–13 |
| MCU giám sát | STM32L011 hoặc ESP32-C6-MINI | $1,2–2,5 |
| PIR | Panasonic EKMB1101111 (1 µA) hoặc tương đương | $2–5 |
| IR | 4–6 LED 850 nm + driver AL8860/MP3431 | $2–4 |
| IR-cut | ICR + driver | $2–3 |
| Nguồn | Sạc 1S + fuel gauge + buck TPS62840 + load switch | $4–6 |
| Lưu trữ | microSD high-endurance 64 GB | $8–12 |
| Khác | PCB, connector, antenna, SIM/eSIM, vỏ IP65 | $20–35 |
| Pin | 15 Ah 1S | $15–25 |
| **Tổng** | | **~$70–120** |

### Track B (nhanh, ít rủi ro): ESP32-S3 + MJPEG
Ưu: đơn giản, rẻ, dev nhanh, cộng đồng lớn.
Nhược: không có H.264/H.265 cứng → data lớn, thẻ nhớ mòn nhanh, chất lượng đêm kém hơn.

| Khối | Linh kiện | Giá ước tính |
|---|---|---|
| MCU | ESP32-S3-WROOM-1 (N8R8) | $3 |
| Camera | OV5640 (5 MP, JPEG) | $5 |
| Modem | EC200U-EU | $10 |
| PIR + IR + nguồn + vỏ + pin | như trên | $35–45 |
| **Tổng** | | **~$55–75** |

### Có nên tự làm?
Nếu mục tiêu là **có sản phẩm dùng ngay**, thị trường đã có camera 4G pin (Reolink Argus, Eufy, Xiaomi) làm tốt hơn với giá thấp hơn chi phí tự làm 1 chiếc.
Tự làm hợp lý khi: cần tuỳ biến sâu (giao thức riêng, tích hợp hệ thống, AI edge), số lượng ≥ 100, hoặc cần chủ động nguồn cung/thương hiệu.

---

## 9. Phần mềm

### 9.1. Firmware
- **Track A:** Buildroot Linux + vendor SDK (RKMPI/Ingenic ISP), chia 2 tiến trình: `recorder` và `uplink`.
- **Track B:** ESP-IDF.
- Thành phần bắt buộc:
  - `power-manager`: máy trạng thái S0–S5, đọc pin, quyết định ngủ/thức.
  - `camera-pipeline`: cấu hình sensor, expose, IR-cut, IR PWM.
  - `recorder`: ghi vòng (ring buffer) ra MP4/H.265, chống hỏng file khi mất điện (fsync theo segment 10–30 s).
  - `motion`: PIR ISR + lọc nhiễu + MD trên ISP để giảm báo giả.
  - `uplink`: MQTT (control/telemetry) + WebRTC (live) + upload clip sự kiện.
  - `ota`: A/B partition, rollback.
  - `provisioning`: BLE/QR để nhập Wi-Fi (nếu có) và SIM/eSIM.
  - `watchdog` + `crashlog`.

### 9.2. Cloud
- MQTT broker: EMQX / Mosquitto.
- Signaling: WebSocket.
- WebRTC: LiveKit (dễ nhất) hoặc mediasoup + coturn.
- API: Go/Node, Postgres (+ Timescale cho telemetry pin/nhiệt).
- Lưu trữ: S3/MinIO cho clip + thumbnail.
- Push: FCM/APNs.
- Bảo mật: TLS, chứng chỉ riêng từng thiết bị, secure boot nếu SoC hỗ trợ.

### 9.3. App
- Flutter (iOS + Android): live view, timeline, xem lại sự kiện, cài đặt vùng chuyển động, lịch ghi, mức pin, dung lượng data, chọn chế độ ngủ.

---

## 10. Rủi ro chính

| # | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| 1 | 7h ban đêm + IR vượt pin | Cao | Pin 15 Ah, IR duty-cycle, giảm số LED |
| 2 | CGNAT → P2P thất bại | Cao | WebRTC + TURN, test sớm trên 3 nhà mạng |
| 3 | Hỏng file khi mất điện đột ngột | Trung bình | Segment ngắn + fsync + supercap nhỏ (tuỳ chọn) |
| 4 | Boot chậm → lỡ chuyển động | Trung bình | Giữ SoC ở suspend-to-RAM thay vì tắt hẳn; hoặc MCU ghi buffer |
| 5 | Nhiệt ngoài trời làm chai pin | Trung bình | Tách ngăn pin, cân nhắc LiFePO4 nếu > 45 °C |
| 6 | Mòn thẻ nhớ | Trung bình | H.265, thẻ high-endurance, giám sát SMART |
| 7 | Chi phí data | Trung bình | Mặc định event-based, nén tốt, giới hạn bitrate |
| 8 | Nhiễu antenna / vỏ kín | Thấp–TB | Giữ khoảng trống antenna, test thực địa |

---

## 11. Kế hoạch

| Giai đoạn | Thời lượng | Đầu ra |
|---|---|---|
| G0. Chốt yêu cầu | 3–5 ngày | Bảng yêu cầu cuối, chọn Track A/B, chốt pin |
| G1. Prototype trên dev board | 2–4 tuần | Đo dòng thực từng trạng thái (INA219/Joulescope), xác nhận pin, test 4G 3 nhà mạng |
| G2. PCB v1 + firmware + cloud MVP | 4–8 tuần | Board chạy được, live view, ghi SD, motion, OTA |
| G3. Vỏ + field test | 4–6 tuần | IP65, test 72h, tối ưu pin, sản xuất thử 5–10 chiếc |

### Tiêu chí nghiệm thu (đề xuất)
- Ghi liên tục 7h ở điều kiện X, không sụp nguồn, file không hỏng.
- Wake từ app ≤ 10 s (chế độ online), ≤ 60 s (chế độ tiết kiệm).
- Standby ≥ 30 ngày (mục tiêu 90 ngày).
- Có chuyển động → bắt đầu ghi ≤ 1,5 s.
- Live 720p, độ trễ ≤ 1,5 s.

---

## 12. Câu hỏi cần trả lời trước khi vẽ schematic

1. **Số lượng và ngân sách** mỗi chiếc (prototype / 100 / 1000)?
2. **7h ghi** là ghi vào thẻ nhớ, hay vừa ghi vừa xem live 4G? Ban đêm có bật IR không?
3. **Độ phân giải / FPS** mong muốn (720p hay 1080p/2K) và **tầm IR** cần bao xa?
4. **Tự làm cloud + app** hay dùng nền tảng có sẵn (Tuya/Agora)?
5. **Môi trường**: trong nhà hay ngoài trời (IP65?), nhiệt độ tối đa, và **standby mong muốn** bao lâu?
6. Bạn đã có **thiết bị đo** (đồng hồ vạn năng, oscilloscope, nguồn DC) và kinh nghiệm hàn/SMD chưa?
