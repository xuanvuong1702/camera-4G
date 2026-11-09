"""CAM4G application entry point.

Prototype behaviour:
  * `--simulate` runs a deterministic scenario with a fake clock and camera,
    useful on the bench and in CI.
  * On target the same loop is driven by real GPIO/PIR/RTC events, with the
    camera reading frames from V4L2 (rkcif) and the modem via PPP + MQTT.
"""

from __future__ import annotations

import argparse
import os
import time

from .app import CameraApp
from .power import PowerConfig, PowerManager
from .recorder import RecorderConfig, SegmentRecorder
from .thermal import ThermalPolicy
from .uplink import Uplink, UplinkConfig


def build_app(root: str) -> CameraApp:
    return CameraApp(
        power=PowerManager(PowerConfig()),
        recorder=SegmentRecorder(RecorderConfig(root=root)),
        thermal=ThermalPolicy(),
        uplink=Uplink(UplinkConfig(spool_dir=root)),
    )


def simulate(root: str) -> None:
    app = build_app(root)
    t = 0.0
    app.power.boot(t)
    frame = b"\xff\xd8" + b"\x00" * 512

    print("boot:", app.state.value)
    app.on_motion(t + 1.0)
    print("motion:", app.state.value)

    for i in range(40):
        t = 1.0 + i * 0.5
        app.tick(t, frame)
    print("after clip:", app.state.value)

    app.on_live(t, True)
    print("live on:", app.state.value)
    for i in range(20):
        t += 0.5
        app.tick(t, frame)
    app.on_live(t, False)
    print("live off:", app.state.value)

    app.on_thermal(45.0, 96.0, 50.0, t)
    print("thermal fault:", app.state.value)
    app.on_thermal(35.0, 60.0, 40.0, t + 1)
    print("recovered:", app.state.value)

    print("segments:", app.recorder.segments_written,
          "bytes:", app.recorder.bytes_written,
          "pending:", len(app.uplink.pending))


def run(root: str) -> None:
    app = build_app(root)
    now = time.time()
    app.power.boot(now)
    frame = b"\xff\xd8" + b"\x00" * 512
    print("CAM4G running; state =", app.state.value)
    while True:
        now = time.time()
        app.tick(now, frame)
        time.sleep(0.2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("CAM4G_ROOT", "/userdata/cam4g"))
    ap.add_argument("--simulate", action="store_true")
    args = ap.parse_args()
    if args.simulate:
        simulate(args.root)
    else:
        run(args.root)


if __name__ == "__main__":
    main()
