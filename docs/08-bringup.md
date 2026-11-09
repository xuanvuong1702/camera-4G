# Bring-up guide — CAM4G v1

Hướng dẫn cho lần cấp nguồn đầu tiên và 8 bước đưa board mẫu vào hoạt động.

---

## Dụng cụ

- Nguồn bench 0–30 V / 3 A, giới hạn dòng 0,5 A lúc đầu
- Đồng hồ vạn năng
- ST-Link V2 (nạp MCU qua J13 SWD)
- USB-TTL 3,3 V (console Core1106 qua J12)
- Thẻ microSD 32 GB đã ghi image Luckfox
- SIM 4G đã kích hoạt
- Kính lúp / camera soi mối hàn

---

## Bước 1 — Kiểm tra board trống (chưa cắm gì)

1. Soi U1, U2, U5 dưới kính: không cầu thiếc, không thiếu chân.
2. Đo VOM: 5V_SYS–GND, 3V3–GND, VBAT–GND phải > 1 kΩ.
3. Kiểm tra phân cực LED, diode, tụ.

**Nếu short:** dừng, tìm bằng cách cấp 0,5 V và đo nhiệt/điện trở.

## Bước 2 — Rail nguồn (chưa lắp pin, chưa lắp module)

1. Cấp 5 V qua USB-C, giới hạn 200 mA.
2. Đo 5V_SYS: 4,9–5,1 V; 3V3: 3,25–3,35 V.
3. Đo dòng không tải: < 15 mA.
4. Nếu 3V3 không lên: kiểm tra R31 (0 Ω nối BUCK_EN lên VBAT) và U3.

## Bước 3 — MCU

1. Nối ST-Link: 3V3, SWDIO (PA13), SWCLK (PA14), GND.
2. Nạp `firmware/mcu/target/build/firmware.bin` (địa chỉ 0x08000000).
3. Kiểm tra: PA5 (SOC_EN) phải ở mức thấp sau reset.
4. Nếu có USB-I2C: quét địa chỉ 0x30, đọc thanh ghi VERSION = 0x10.
5. Đo dòng STOP: < 10 µA.
6. **Dòng ngủ 0,3 mA không đo được bằng INA226** (3 µV trên shunt 0,01 Ω, dưới offset). Đo bằng nguồn có amper kế (Otii/µCurrent) hoặc điện trở cắm tạm.

**Lỗi thường gặp:** I2C không thấy 0x30 → kiểm tra AF4 cho PA9/PA10, và điện trở kéo I2C (R8/R9 4,7 kΩ).

## Bước 4 — Core1106

1. Ghi image Luckfox ra thẻ SD, cắm vào J4.
2. Cấp 5 V, theo dõi UART0 (J12: TX/RX/GND) ở 115200.
3. Board phải boot và cho login.
4. Nếu không boot: kiểm tra thẻ, điện áp 5V dưới tải, nút reset (SW1).

## Bước 5 — Camera

1. Cắm FPC 20P vào J3, **mặt tiếp điểm đúng hướng** (theo silkscreen).
2. Chạy `v4l2-ctl --list-devices`, phải thấy `rkisp_mainpath`.
3. Chụp thử: `v4l2-ctl --device=/dev/video15 --set-fmt-video=width=1280,height=720,pixelformat=NV12 --stream-mmap --stream-count=1 --stream-to=/tmp/a.raw`.
4. Nếu ảnh sai màu/nhiễu: nghi vấn impedance MIPI (board mẫu chưa kiểm soát 100 Ω).

## Bước 6 — 4G

1. Lắp SIM vào J11 (board con modem).
2. Kiểm tra `lsusb` thấy modem.
3. `AT+CPIN?` → READY; `AT+CREG?` → 1 hoặc 5.
4. Chạy PPP (`quectel-CM` hoặc `pppd`), kiểm tra `ip addr` có `ppp0`.
5. `iperf3 -c <vps>` ≥ 2 Mbps.

**Lỗi thường gặp:** modem sụp khi TX → kiểm tra tụ 1000 µF và boost 5 V đủ 3 A.

## Bước 7 — Hồng ngoại / IR-CUT

- Nếu dùng module tích hợp: chỉ cần kiểm tra ảnh đêm 3 m.
- Nếu dùng rời: đo J7 (5 V qua LED), J8 (xung IR-CUT), kiểm tra Q3.

## Bước 8 — Pin, sạc, nhiệt

1. Lắp pin LFP 10 Ah qua J2 (đúng cực).
2. Đo sạc: 0,9–1,1 A khi pin < 3,4 V.
3. Làm nóng pin > 40 °C → dòng sạc phải về 0.
4. Ghi 7 h, đo dung lượng tiêu thụ.

---

## Các điểm rủi ro đã biết

| # | Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|---|
| 1 | I2C slave không chạy | không thấy 0x30 | đổi AF4 hoặc preload TXDR |
| 2 | MIPI impedance | ảnh nhiễu/sọc | route lại MIPI thủ công |
| 3 | VBAT zone | 5V sụt khi modem TX | kiểm tra via nối zone |
| 4 | FPC ngược | không nhận camera | đảo chiều FPC |
| 5 | Modem peak current | reset modem | thêm tụ bulk |

---

## Thứ tự cấp nguồn an toàn

1. USB-C 5 V (không pin, không module)
2. MCU + kiểm tra rail
3. Core1106 + thẻ SD
4. Camera
5. Modem
6. Pin
