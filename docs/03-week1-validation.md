# Tuần 1 — Cổng kiểm tra trước khi cam kết IPC

> **Tài liệu lịch sử (vòng 1–4).** Trạng thái hiện tại xem [HANDOVER.md](../HANDOVER.md).


Mục đích: **đo 4 con số quyết định** trên Luckfox Pico Max trước khi đặt phần còn lại của BOM.
Nếu trượt cổng nào, có phương án xử lý ngay, không phải làm lại từ đầu.

Thiết bị cần: nguồn bench 5 V/3 A, ampe kế USB (FNIRSI FNB58 hoặc tương đương),
oscilloscope (nếu có), SIM 4G đã kích hoạt, thẻ microSD.

---

## Cổng 1 — Quick boot ≤ 2,0 s

**Đo:** từ lúc cấp 5 V đến lúc app bật GPIO `SOC_READY`.

Cách làm:
1. Viết app nhỏ: ngay sau khi khởi tạo camera xong → kéo GPIO lên cao.
2. Cấp nguồn bằng công tắc, bắt cạnh GPIO bằng scope; hoặc dùng serial log có timestamp.
3. Đo 5 lần, lấy trung bình.

| Kết quả | Hành động |
|---|---|
| ≤ 2,0 s | Đạt |
| 2,0–3,0 s | Chấp nhận được — bù bằng cách bật SoC sớm hơn PIR 200 ms (PIR có trễ tự nhiên) |
| > 3,0 s | Tối ưu kernel/bỏ dịch vụ; nếu vẫn > 3 s → cân nhắc quay lại ESP32-S3 |

**Lưu ý:** boot nhanh chỉ có ý nghĩa nếu camera sẵn sàng cùng lúc. Đo cả "frame đầu tiên ghi được", không chỉ boot kernel.

---

## Cổng 2 — Suspend ≤ 50 mW

**Đo:** `echo mem > /sys/power/state`, đo dòng ở đầu vào 5 V sau 30 s.

| Kết quả | Hành động |
|---|---|
| ≤ 50 mW | Đạt — chế độ "canh gác nhanh" khả dụng |
| 50–100 mW | Chấp nhận, nhưng standby chỉ ~20–30 ngày → mặc định tắt rail |
| > 100 mW | Bỏ suspend, chỉ dùng tắt rail; wake từ cloud sẽ chậm hoặc không có |

---

## Cổng 3 — Ghi 720p H.265 ≤ 1,2 W (board, chưa tính modem)

**Đo:** ghi 10 phút ra SD, đo dòng trung bình.

| Kết quả | Hành động |
|---|---|
| ≤ 1,2 W | Đạt — 7 h ≈ 8,4 Wh, pin 8 Ah dư |
| 1,2–1,5 W | Chấp nhận — 7 h ≈ 10,5 Wh (48 % pin) |
| > 1,5 W | Giảm fps/bitrate, tắt tính năng thừa; xem lại tản nhiệt |

---

## Cổng 4 — 4G: nhận SIM + upload ≥ 2 Mbps

**Đo:** `lsusb`, ModemManager nhận modem, `qmicli` lấy IP, `iperf3 -c <vps>`.

| Kết quả | Hành động |
|---|---|
| Nhận modem + ≥ 2 Mbps | Đạt |
| Nhận nhưng < 1 Mbps | Kiểm tra band/antenna/vị trí; thử 3 nhà mạng |
| Không nhận | Thử ECM/RNDIS/PPP; nếu vẫn lỗi → đổi modem (EC200U-EU hoặc EG25-G) |

---

## Bảng ghi kết quả

| Cổng | Mục tiêu | Đo lần 1 | Đo lần 2 | Đo lần 3 | TB | Đạt? |
|---|---|---|---|---|---|---|
| Quick boot | ≤ 2,0 s | | | | | |
| Suspend | ≤ 50 mW | | | | | |
| Ghi 720p | ≤ 1,2 W | | | | | |
| 4G upload | ≥ 2 Mbps | | | | | |

---

## Quyết định sau tuần 1

- **Đạt cả 4** → đặt phần còn lại của BOM, bắt đầu PCB/khung firmware Linux.
- **Trượt cổng 1 hoặc 2** → vẫn dùng IPC nhưng chấp nhận: wake chậm hơn, standby ngắn hơn; hoặc chuyển sang phương án lai (MCU giữ modem, SoC tắt).
- **Trượt nặng (boot > 5 s hoặc suspend > 200 mW)** → quay lại ESP32-S3 cho prototype, giữ IPC cho bản sản phẩm sau.

---

## Chuẩn bị môi trường build

SDK Luckfox chạy trên **Ubuntu 22.04**. Trên Windows phải dùng **WSL2**:

```bash
wsl --install -d Ubuntu-22.04
# trong WSL:
sudo apt update && sudo apt install -y build-essential git python3 cmake
git clone https://github.com/LuckfoxTECH/luckfox-pico.git
```

> Cần ~50 GB dung lượng trống cho toolchain + source.
