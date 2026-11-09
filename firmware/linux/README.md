# CAM4G — Linux application

Ứng dụng chạy trên Core1106 (Buildroot). Prototype, Python 3.11+.

## Chạy thử trên máy tính

```powershell
$env:PYTHONPATH="...\4g-camera\firmware\linux"
python -m cam4g.main --simulate --root .\tmp
```

Kết quả mô phỏng: boot → motion → ghi 30 s → live → tắt live → thermal fault → phục hồi,
kèm số segment và số message chờ gửi.

## Chạy test

```powershell
cd firmware\linux
python -m unittest discover -s tests -t . -v
```

10 test: state machine, recorder, thermal, uplink.

## Trạng thái

| Thành phần | Trạng thái |
|---|---|
| Power FSM | Đã có, test đầy đủ |
| Recorder (segment + fsync) | Đã có, test |
| Thermal policy | Đã có, test |
| Uplink queue + spool | Đã có, test |
| Camera V4L2/rkmpi | **Chưa nối** — cần board thật |
| PPP + MQTT transport | **Chưa nối** — cần SIM và modem |
| GPIO/PIR/RTC | **Chưa nối** — cần board thật |

## Việc cần làm trên target

1. `v4l2-ctl`/rkcif lấy frame JPEG → `app.tick(now, frame)`.
2. PIR qua GPIO sysfs → `app.on_motion(now)`.
3. Modem PPP (`quectel-CM` hoặc `pppd`) + MQTT client → thay `Uplink` transport.
4. Nhiệt độ: DS18B20 qua 1-Wire → `app.on_thermal(...)`.
5. Đóng gói thành service `S99cam4g` trong Buildroot.
