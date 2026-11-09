# Có nên dùng IPC (Linux SoC) ngay từ prototype?

- Ngày: 2026-11-08
- Bối cảnh: yêu cầu đã chốt — 720p, IR ≤ 3 m, ghi local 7 h, không khí 40–45 °C, prototype 1–2 bộ
- Kết luận ngắn: **Nếu mục tiêu là sản phẩm → nên chuyển ngay. Nếu chỉ cần kiểm chứng ý tưởng trong 4 tuần → giữ ESP32-S3.**
- **Quyết định (2026-11-08): đã chốt chuyển sang IPC.** Prototype dùng Luckfox Pico Max + SC3336 + EC25-EU. Xem [BOM v2](../hardware/bom-prototype-v2.csv) và [đấu dây v2](../hardware/wiring-v2-ipc.md).

---

## 1. So sánh trên đúng thông số của bạn

| Tiêu chí | ESP32-S3 (hiện tại) | IPC — RV1106 (Luckfox Pico) |
|---|---|---|
| Giá board + camera | $15 + $12 = **$27** | $25 + $10 = **$35** |
| Công suất ghi 720p | 0,5–0,9 W | 0,9–1,4 W |
| Năng lượng 7 h (đêm + IR) | ~8,4 Wh | ~10,5 Wh |
| % pin LFP 8 Ah (21,8 Wh dùng được) | 39 % | 48 % |
| Ngủ (tắt rail SoC) | 0,3 mA | 0,3 mA + MCU |
| Ngủ (suspend DDR) | — | ~20–50 mW → ~30 ngày |
| Wake → frame đầu | ~0,3 s | 1–2 s (nếu tắt hẳn) / <0,2 s (nếu suspend) |
| Codec | MJPEG (sensor JPEG) | **H.264/H.265** |
| Data live 720p | 1,5–2,5 Mbps | **0,5–1,0 Mbps** |
| Mòn thẻ SD | Cao (0,9 GB/h) | Thấp (0,3 GB/h) |
| Ảnh đêm | Kém (không ISP) | **Tốt hơn** (ISP 3DNR/WDR) |
| Live view | MJPEG qua relay | RTSP → WebRTC (MediaMTX) |
| 4G | UART PPPoS ~3 Mbps | USB QMI/ECM, không nghẽn |
| Độ phức tạp dev | Thấp (ESP-IDF) | Cao (Buildroot, kernel, SDK Rockchip) |
| Thời gian tới prototype chạy | ~4 tuần | ~6–8 tuần |
| Tái sử dụng cho sản phẩm | **Phải viết lại phần lớn** | **Dùng luôn** |

---

## 2. Cái được khi chuyển ngay

1. **Không phải viết lại.** Nếu sản phẩm cuối dùng IPC, toàn bộ code camera/recorder/uplink viết cho ESP32-S3 là đồ bỏ. Đây là chi phí lớn nhất và ít người tính trước.
2. **H.265**: file nhỏ 3×, thẻ nhớ bền 3×, data 4G giảm 60 % — đúng bài toán pin và chi phí data.
3. **Ảnh đêm tốt hơn nhiều.** OV5640 không có ISP; RV1106 có 3DNR/WDR/HDR — khác biệt rõ khi trời tối.
4. **Live view dễ và mượt hơn.** RTSP/H.265 + MediaMTX (WebRTC, HLS) chạy sẵn trên VPS; không phải tự viết relay MJPEG.
5. **4G qua USB**, không bị nghẽn UART 3 Mbps, không cần level shifter 1,8 V.
6. **Hệ điều hành thật**: log, SSH, OTA, filesystem chống hỏng, debug dễ hơn nhiều so với MCU.

## 3. Cái mất

1. **+2–4 tuần** học SDK Rockchip, Buildroot, cấu hình kernel — tuần đầu sẽ chậm.
2. **Công suất cao hơn ~40 %** khi ghi. Vẫn nằm trong ngân sách pin (48 %), nhưng không còn dư nhiều.
3. **Boot chậm hơn** nếu tắt hẳn SoC → mất 1–2 s đầu khi có chuyển động. Phải đo quick-boot thực tế.
4. **Ngủ sâu khó hơn**: Linux suspend chỉ ~30 mW → ~30 ngày với pin 8 Ah, không đạt "càng lâu càng tốt". Muốn hàng tháng phải tắt rail và chờ boot.
5. **Nhiệt**: 1 W trong hộp kín ở 45 °C cần tản nhiệt tốt hơn — tấm nhôm + thermal pad là bắt buộc, không phải tuỳ chọn.

---

## 4. Kiến trúc nếu chuyển

Giữ nguyên triết lý cũ: **MCU luôn sống, SoC là tải được bật/tắt**.

```
   PIR ──IRQ──► MCU (STM32L0/ESP32-C6) ──EN──► Load switch 5V ──► RV1106
   RTC ◄─I2C───     │  ▲                                       ├── SC3336 (MIPI)
   Nhiệt ────────►   │  └──UART──► EC25-EU (USB) ──► 4G        ├── microSD
                     └── GPIO: IR PWM, IR-CUT                   └── USB 4G
   LFP 8Ah ── BMS ── boost 5V ── buck 3,3V / 3,8V
```

**Thay đổi so với bản ESP32-S3:**

| Khối | Cũ | Mới |
|---|---|---|
| SoC | ESP32-S3-CAM | Luckfox Pico Max (RV1106G3, 256 MB) |
| Camera | OV5640 DVP | SC3336 3 MP MIPI (kèm board) |
| Modem | EC200U qua UART 1,8 V | **EC25-EU qua USB** (ModemManager hỗ trợ tốt) |
| MCU | (chính là ESP32) | **Thêm** STM32L0/ESP32-C6 làm supervisor |
| Level shifter | Bắt buộc | Không cần |
| Live | MJPEG relay | RTSP → MediaMTX → WebRTC |

**BOM thay đổi:**
- Bỏ: ESP32-S3-CAM ($18), OV5640 ($12), TXS0108E ($2)
- Thêm: Luckfox Pico Max ($25), SC3336 ($10), EC25-EU + USB adapter ($30), MCU supervisor ($2)
- Giữ nguyên: pin, nguồn, IR, PIR, RTC, INA226, DS18B20, vỏ, tản nhiệt
- **Tổng: ~$150–165** (tăng ~$10–15)

---

## 5. Phần mềm thay đổi thế nào

| Thành phần | ESP32-S3 | IPC |
|---|---|---|
| OS | ESP-IDF / FreeRTOS | Buildroot Linux |
| Camera | driver DVP | V4L2 + Rockchip MPI (rkmpi) |
| Ghi file | tự viết MJPEG writer | ffmpeg/gstreamer hoặc mp4 muxer |
| Live | HTTP chunked | RTSP (MediaMTX) + WebRTC |
| Điều khiển | MQTT | MQTT (cùng topic, giữ nguyên) |
| OTA | partition A/B | A/B rootfs hoặc overlay |
| Power FSM | đã viết | port logic sang app Linux + MCU |

Phần **cloud, MQTT topic, app** giữ nguyên — chỉ thay đường truyền video.

---

## 6. Rủi ro riêng của đường IPC

| Rủi ro | Cách giảm |
|---|---|
| Boot 1–2 s làm lỡ chuyển động | Đo quick-boot trước khi cam kết; dùng suspend khi ở chế độ "canh gác" |
| Suspend 30 mW → standby chỉ 30 ngày | Mặc định tắt rail; bật suspend chỉ khi người dùng chọn "phản ứng nhanh" |
| SDK Rockchip ít tài liệu | Dùng Luckfox SDK + ví dụ có sẵn; chọn RV1106 chứ không phải SoC lạ |
| Modem USB không nhận | EC25-EU thay vì EC200U; test ModemManager trên board trước |
| Nhiệt 1 W trong hộp kín | Tấm nhôm + thermal pad + đo trong tủ sấy 45 °C ở tuần 3 |

---

## 7. Khuyến nghị

**Chuyển sang IPC ngay** nếu:
- Bạn chắc chắn sẽ làm sản phẩm (không chỉ demo), và
- Chấp nhận chậm 2–4 tuần ở giai đoạn đầu để đổi lấy việc không phải viết lại, và
- Cần ảnh đêm tốt + H.265 + live mượt.

**Giữ ESP32-S3** nếu:
- Bạn muốn cầm được một bản chạy trong 4 tuần để kiểm chứng pin/nhiệt/4G, hoặc
- Chưa chắc sản phẩm sẽ đi tiếp.

**Đề xuất của mình:** vì bạn đã chốt "prototype" nhưng mục tiêu dài hạn rõ ràng là sản phẩm, và vì 720p + IR 3 m không đòi hỏi gì ở ESP32-S3, **chuyển IPC ngay là hợp lý hơn về tổng chi phí** — với điều kiện tuần 1 đo được quick-boot ≤ 2 s và suspend ≤ 50 mW. Nếu hai con số đó tệ hơn, quay lại ESP32-S3.
