# Thiết kế v0.2 — Yêu cầu đã chốt & điều chỉnh

- Ngày: 2026-11-08
- Thay thế phần "câu hỏi mở" của [v0.1](00-feasibility-and-architecture.md)
- Trạng thái: **chốt được hướng prototype**

---

## 1. Yêu cầu đã chốt

| # | Yêu cầu | Giá trị chốt |
|---|---|---|
| R1 | Mục tiêu | **Prototype** (1–2 bộ), chưa tối ưu cho sản xuất hàng loạt |
| R2 | Ghi liên tục 7h | **Chỉ ghi vào thẻ nhớ**, không stream trong 7h đó |
| R3 | Độ phân giải | **720p** là đủ |
| R4 | Tầm IR | **≤ 3 m** (rất gần — giảm mạnh công suất IR) |
| R5 | Môi trường | **Ngoài trời** |
| R6 | Nhiệt độ | **Không khí 40–45 °C**; bề mặt vỏ dưới nắng 60–70 °C |
| R7 | Ngủ / đánh thức | Ngủ sâu, đánh thức bằng PIR / lịch / lệnh cloud |
| R8 | Xem live | Qua 4G, P2P hoặc qua server |

---

## 2. Điều gì thay đổi so với v0.1

Ba câu trả lời làm bài toán nhẹ đi rất nhiều, và một câu làm nặng lên:

| Thay đổi | Tác động |
|---|---|
| 720p thay vì 1080p | Công suất encode giảm ~40%, data giảm ~60% |
| IR chỉ 3 m | IR từ 1–2 W xuống **0,3–0,6 W** — đây là thay đổi lớn nhất |
| Chỉ ghi thẻ, không stream | Bỏ được modem khỏi đường ghi 7h → tiết kiệm 0,4–0,8 W |
| **Ngoài trời 60–70 °C** | **Nút thắt mới: nhiệt, không còn là pin** |

**Kết luận: pin không còn là vấn đề.** Với 720p + IR 3 m + ghi local, 7h chỉ cần ~5–9 Wh. Một pack LFP 6–8 Ah là dư. Vấn đề thật sự là **sống sót ở 60–70 °C**.

---

## 3. Nhiệt độ 60–70 °C — cần phân biệt rõ

Đây là điểm quan trọng nhất của buổi trao đổi này. "60–70 °C" có thể là 3 thứ khác nhau, và chúng dẫn tới 3 thiết kế khác nhau:

| Khái niệm | Ý nghĩa | Hệ quả |
|---|---|---|
| **Nhiệt độ không khí** | Nhiệt độ môi trường xung quanh thiết bị | Đây là con số linh kiện phải chịu |
| **Nhiệt độ bề mặt vỏ** | Vỏ nhựa đen dưới nắng trực tiếp | Cao hơn không khí 20–30 °C |
| **Nhiệt độ bên trong hộp kín** | Không khí trong hộp IP65 | Cao hơn không khí 10–25 °C (hiệu ứng nhà kính + tự toả nhiệt) |

### Giới hạn thực tế của linh kiện

| Linh kiện | Giới hạn vận hành điển hình |
|---|---|
| Module 4G (EC200U, A7670E) | −35…+75 °C (một số bản industrial +85 °C) |
| ESP32-S3 | −40…+85 °C |
| RV1106 / SoC Linux | −40…+85 °C (bản industrial) |
| Pin Li-ion (NMC) | Xả ≤ 60 °C, **sạc ≤ 45 °C** |
| Pin LiFePO4 (LFP) | Xả ≤ 60 °C, **sạc ≤ 55 °C** |

### Kết luận thẳng

- Nếu **60–70 °C là nhiệt độ không khí kéo dài**: trong hộp kín sẽ là **80–95 °C** → vượt spec của module 4G và pin. Không có cách thụ động nào cứu được. Khi đó phải: giảm yêu cầu, hoặc chấp nhận tuổi thọ ngắn + cấm sạc, hoặc dùng làm mát chủ động (không thực tế cho camera pin).
- Nếu **60–70 °C là bề mặt vỏ dưới nắng** (không khí thực tế ~40–45 °C): hoàn toàn thiết kế được — đây là điều kiện bình thường của camera ngoài trời ở Việt Nam.

### Spec đề xuất (an toàn, làm được)

| Thông số | Giá trị |
|---|---|
| Vận hành liên tục | −10…+55 °C (không khí) |
| Đỉnh ngắn hạn | +60 °C trong ≤ 4 h/ngày |
| Sống sót (không hoạt động) | −20…+75 °C |
| Sạc pin | Chỉ khi T_pin = 0…40 °C (ngưỡng bảo vệ 40 °C) |
| Ngắt khẩn cấp | T > 75 °C → tắt, ghi log, báo cloud |

> **Đã xác nhận (2026-11-08):** không khí **40–45 °C**, bề mặt vỏ **60–70 °C** khi nắng trực tiếp.
> Đây là điều kiện thiết kế được — spec dưới đây có margin, không cần hạ yêu cầu.
> Điều kiện bắt buộc: vỏ trắng, có nắp che nắng, tách ngăn pin, cấm sạc khi pin > 40 °C.

---

## 4. Thiết kế nhiệt

1. **Vỏ trắng / ASA hoặc PC phủ UV**, không dùng nhựa đen hấp thụ nhiệt. Nắp che nắng phía trên.
2. **Tấm nhôm mặt trước** làm heatsink cho SoC + modem, dùng thermal pad 1–2 mm. Đây là đường tản nhiệt chính vì hộp kín không có đối lưu.
3. **Tách ngăn pin** khỏi ngăn điện tử bằng vách + foam cách nhiệt. Pin áp sát vỏ phía bóng râm.
4. **Van cân bằng áp Gore** (không tản nhiệt, nhưng tránh ẩm và nứt gioăng).
5. **Cảm biến nhiệt 2 điểm**: DS18B20 dán lên pin + NTC/DS18B20 trên SoC.
6. **Chính sách nhiệt trong firmware**:
   - T_pin > 40 °C → cấm sạc.
   - T_SoC > 85 °C → giảm fps 15 → 10, tắt IR nếu đang bật.
   - T_SoC > 95 °C → dừng ghi, hạ tải.
   - T > 75 °C → tắt khẩn cấp.
7. **Lắp đặt**: khuyến nghị dưới mái/hiên. Nắng trực tiếp + hộp kín là kịch bản xấu nhất, giảm được 15–25 °C nếu có bóng râm.

---

## 5. Pin — tính lại

### 5.1. Công suất thực tế (720p, ghi thẻ)

| Thành phần | Công suất |
|---|---|
| ESP32-S3 + camera OV5640 + ghi SD | 0,5–0,9 W |
| IR 2 LED 850 nm cho 3 m (duty ~50%) | 0,3–0,6 W |
| Modem 4G (chỉ khi live/upload) | 0,4–0,8 W |
| Ngủ sâu (MCU + RTC + PIR) | 0,4–1,1 mW |

### 5.2. Năng lượng 7h

| Kịch bản | Công suất | 7h |
|---|---|---|
| Ngày, ghi local | ~0,7 W | 4,9 Wh |
| Đêm, ghi + IR | ~1,2 W | 8,4 Wh |
| Đêm, ghi + IR + live 720p | ~1,8 W | 12,6 Wh |

### 5.3. Chọn pin

| Phương án | Dung lượng dùng được | 7h đêm + IR | 7h đêm + live | Ghi chú |
|---|---|---|---|---|
| LFP 1S 6 Ah (19,2 Wh) | ~16,3 Wh | 52% | 77% | **Khuyến nghị** — chịu nhiệt tốt nhất |
| LFP 1S 8 Ah (25,6 Wh) | ~21,8 Wh | 39% | 58% | Margin tốt, nặng hơn |
| Li-ion 1S 10 Ah (37 Wh) | ~31,5 Wh | 27% | 40% | Nhẹ hơn nhưng sạc ≤ 45 °C, chai nhanh khi nóng |

**Khuyến nghị: LFP 1S 8 Ah** cho prototype ngoài trời.
- Ưu: an toàn nhiệt, 2000–4000 cycle, không cháy khi hỏng.
- Nhược: cần boost 3,2 V → 5 V, sạc đặc thù (CN3058E hoặc charger LFP), nặng hơn Li-ion cùng Wh.
- Nếu ưu tiên nhẹ: Li-ion 10 Ah + ngưỡng cấm sạc 40 °C, chấp nhận tuổi thọ 1–2 năm ở khí hậu nóng.

### 5.4. Ngủ

Với 21,8 Wh dùng được và dòng ngủ 0,3 mA (1,1 mW): thời gian lý thuyết ~19.000 h. Thực tế bị giới hạn bởi **tự xả + mạch bảo vệ + nhiệt** → 1–2 năm. Ở 60 °C, tự xả và lão hoá tăng mạnh, nên thực tế 6–12 tháng.

---

## 6. Kiến trúc prototype — chọn ESP32-S3

Với 720p + IR 3 m + ghi local, **ESP32-S3 là lựa chọn đúng cho prototype**:

| Tiêu chí | ESP32-S3 | RV1106 (Track A) |
|---|---|---|
| Giá dev board | $12–18 | $25–40 |
| Boot / wake | ~0,3 s (deep sleep) | 1–3 s (Linux) |
| Công suất 720p | 0,5–0,9 W | 0,8–1,3 W |
| Chất lượng ảnh đêm | Trung bình (OV5640) | Tốt (ISP + STARVIS) |
| Live view 4G | MJPEG qua relay | WebRTC/H.265 |
| Độ phức tạp | Thấp | Cao (SDK vendor) |

→ Prototype: **ESP32-S3**. Nếu sau này cần ảnh đêm tốt hơn hoặc H.265, chuyển Track A — kiến trúc phần mềm giữ nguyên.

### Sơ đồ khối prototype

```
   PIR AM312 ──IRQ──► ESP32-S3 ◄──I2C── DS3231 (RTC)
                        │  ▲            INA226 (đo dòng)
                        │  └──1-Wire── DS18B20 ×2 (pin, SoC)
        OV5640 ──DVP──► │
        IR LED ◄─PWM────┤
        ICR ◄──GPIO─────┤
        microSD ◄─SDMMC─┤
                        └──UART──► EC200U-EU ──► 4G ──► VPS relay
   LFP 3,2 V ── BMS ── boost 5 V ── buck 3,3 V ── load switch
```

**Lưu ý kỹ thuật:**
- EC200U qua **UART PPPoS**: UART ~3 Mbps là giới hạn thực tế → 720p MJPEG nên để 10–15 fps, bitrate 1,5–2,5 Mbps.
- Nếu cần nét hơn: giảm fps, tăng JPEG quality, hoặc chuyển modem sang USB (phức tạp hơn).
- ESP32-S3-CAM có sẵn khe camera + SD; cần kiểm tra xung đột chân với UART modem.

---

## 7. BOM prototype (1 bộ)

| # | Linh kiện | Ghi chú | Giá ước tính |
|---|---|---|---|
| 1 | ESP32-S3-WROOM-1 N16R8 + board camera | Freenove/Waveshare ESP32-S3-CAM | $15 |
| 2 | OV5640 + IR-CUT | Module day/night, 5 MP | $12 |
| 3 | Quectel EC200U-EU breakout | Cat-1bis, B1/3/5/7/8/20/28 | $20 |
| 4 | PIR AM312 | ~10–20 µA | $2 |
| 5 | 2× LED 850 nm 1 W + MOSFET IRLZ44N + trở | Tầm 3 m | $4 |
| 6 | DS3231 RTC | | $2 |
| 7 | INA226 | Đo dòng từng trạng thái | $3 |
| 8 | DS18B20 ×2 | Pin + SoC | $3 |
| 9 | microSD 32 GB high-endurance | | $8 |
| 10 | LFP 1S 8 Ah + BMS + charger CN3058E | | $25 |
| 11 | Boost 5 V 3 A (MT3608) + buck 3,3 V | | $3 |
| 12 | Hộp IP65 trắng + tấm nhôm + thermal pad + van Gore | | $12 |
| 13 | Dây, header, proto board | | $8 |
| | **Tổng** | | **~$117** |

---

## 8. Kế hoạch 4 tuần

| Tuần | Việc | Đo / nghiệm thu |
|---|---|---|
| W1 | Camera 720p + ghi SD + PIR wake + IR | Dòng ở 4 trạng thái; PIR → frame đầu ≤ 1 s |
| W2 | EC200U PPP + MQTT + relay server + live MJPEG | Latency ≤ 1,5 s; test 3 nhà mạng; data/giờ |
| W3 | Test nhiệt (tủ sấy 60 °C hoặc phơi nắng có che) + xả pin 7h | Không throttle; file không hỏng; nhiệt độ trong hộp |
| W4 | Tích hợp, field test 72 h, chốt Track A/B | Báo cáo: pin thực, nhiệt thực, lỗi |

### Tiêu chí nghiệm thu prototype
- Ghi 720p liên tục 7h ở 55–60 °C, file play được, không mất segment.
- PIR → bắt đầu ghi ≤ 1 s.
- Live 720p qua 4G ≤ 1,5 s.
- Ngủ sâu ≤ 1 mA (mục tiêu 0,3 mA).
- Cấm sạc khi T_pin > 40 °C hoạt động đúng.
- Standby ≥ 30 ngày.

---

## 9. Phần mềm prototype

**Firmware (ESP-IDF):**
- `power_fsm`: S0 ngủ sâu / S1 ngủ có kết nối / S2 ghi / S3 ghi + live.
- `camera`: OV5640 720p, JPEG, IR-cut, IR PWM.
- `recorder`: ghi file `.mjpeg`/`.mp4` theo segment 30 s, fsync, ring buffer.
- `motion`: PIR ISR + lọc nhiễu 2 lần trong 3 s.
- `uplink`: PPPoS → MQTT (control) + HTTP chunked (live MJPEG) + upload clip.
- `thermal`: đọc DS18B20, chính sách §4.6.
- `ota`: partition A/B.

**Server (VPS nhỏ):**
- MQTT broker (Mosquitto).
- Relay MJPEG: device push → server fan-out cho app.
- API + lưu clip (MinIO).
- Web app đơn giản (xem live, timeline, điều khiển) — chưa cần mobile app ở giai đoạn prototype.

---

## 10. Câu hỏi còn lại

1. **60–70 °C là nhiệt độ không khí hay bề mặt vỏ?** Có được lắp dưới mái/che nắng không?
2. Ngân sách prototype khoảng **$100–150** có ổn không?
3. Live view ở prototype: chấp nhận **MJPEG qua server** (đơn giản, làm nhanh) hay cần **WebRTC** ngay?
4. Có dự định **sạc bằng pin mặt trời** không? (chưa thấy nhắc — nếu có thì thêm MPPT và thay đổi bài toán năng lượng)
