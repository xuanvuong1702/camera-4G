"""Application glue: power FSM + recorder + thermal + uplink."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .power import PowerManager, State
from .recorder import SegmentRecorder
from .thermal import ThermalPolicy
from .uplink import Uplink


@dataclass
class CameraApp:
    power: PowerManager
    recorder: SegmentRecorder
    thermal: ThermalPolicy
    uplink: Uplink

    # ---- events ----
    def on_motion(self, now: float) -> None:
        self.power.on_motion(now)
        self.uplink.enqueue("event/motion", {"ts": now})

    def on_live(self, now: float, on: bool) -> None:
        self.power.on_live_request(now, on)
        self.uplink.enqueue("event/live", {"ts": now, "on": on})

    def on_thermal(self, battery_c: float, soc_c: float, ambient_c: float, now: float) -> None:
        if self.thermal.should_shutdown(soc_c, ambient_c):
            self.power.on_thermal_fault(True, now)
        else:
            self.power.on_thermal_fault(False, now)
        if not self.thermal.can_charge(battery_c):
            self.uplink.enqueue("event/charge_inhibit", {"ts": now, "battery_c": battery_c})

    # ---- periodic ----
    def tick(self, now: float, frame: Optional[bytes] = None) -> None:
        self.power.tick(now)
        if self.power.recording and frame is not None:
            self.recorder.write_frame(frame, now)
        elif not self.power.recording:
            self.recorder.stop()

    @property
    def state(self) -> State:
        return self.power.state
