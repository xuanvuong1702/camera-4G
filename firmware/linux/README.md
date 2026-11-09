# CAM4G — Linux application (Core1106)

Ứng dụng chạy trên Buildroot. Python 3.11+.

## Module

| File | Nội dung |
|---|---|
| `power.py` | Máy trạng thái S0–S4: ngủ sâu, ngủ có kết nối, ghi, ghi + live, fault |
| `recorder.py` | Ghi segment MJPEG, fsync định kỳ, xoay file |
| `thermal.py` | Cấm sạc > 40 °C, throttle > 85 °C, shutdown > 95 °C |
| `uplink.py` | Hàng đợi batch, ack/nack, spool ra file |
| `modem.py` | AT client cho EC200U: alive, SIM, CSQ, CREG, APN, RF on/off |
| `camera.py` | Adapter V4L2 (v4l2-ctl) + SimCamera cho test |
| `gpio.py` | sysfs GPIO cho PIR / IR / IR-CUT |
| `app.py` | Ghép các khối, xử lý sự kiện |
| `main.py` | Chạy thật hoặc `--simulate` |

## Test

```powershell
cd firmware/linux
python -m unittest discover -s tests -t . -v
```

**17 test**: power FSM (5), recorder (2), thermal/uplink (3), modem AT (5), camera/GPIO (2).

## Chạy mô phỏng

```powershell
python -m cam4g.main --simulate --root .\tmp
```

Kết quả: boot → motion → RECORD → live → RECORD_LIVE → RECORD → thermal FAULT → phục hồi.

## Trạng thái tích hợp target

| Thành phần | Trạng thái |
|---|---|
| Power FSM | Đã có, test đầy đủ |
| Recorder | Đã có, test |
| Thermal | Đã có, test |
| Uplink queue | Đã có, test |
| Modem AT (EC200U) | Đã có, test với transport giả |
| Camera V4L2 | Adapter gọi `v4l2-ctl` — **chưa chạy trên board** |
| GPIO sysfs | Đã có — **chưa chạy trên board** |
| PPP + MQTT | Chưa nối (dùng `pppd` + chat script) |

## Việc cần làm trên target

1. Kiểm tra `/dev/ttyS1` (UART1) và PPP với EC200U.
2. `v4l2-ctl --list-devices` → chốt `/dev/video*` cho SC3336.
3. GPIO number thực tế của PIR/IR/IR-CUT.
4. DS18B20 qua 1-Wire (sysfs hoặc w1-gpio).
5. Đóng gói service `S99cam4g`.
