"""Power state machine for CAM4G.

States map 1:1 to the hardware design:
  SLEEP_DEEP      - SoC rail off, modem off, MCU + PIR + RTC only (~0.3 mA)
  SLEEP_CONNECTED - SoC suspended or off, modem in eDRX/PSM (few mA)
  RECORD          - SoC on, camera + SD, modem off
  RECORD_LIVE     - SoC on, camera + SD + modem streaming
  FAULT           - thermal/battery fault, all loads off
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class State(str, Enum):
    SLEEP_DEEP = "SLEEP_DEEP"
    SLEEP_CONNECTED = "SLEEP_CONNECTED"
    RECORD = "RECORD"
    RECORD_LIVE = "RECORD_LIVE"
    FAULT = "FAULT"


@dataclass
class PowerConfig:
    clip_seconds: float = 30.0
    idle_to_sleep_seconds: float = 10.0
    live_hold_seconds: float = 120.0
    low_battery_pct: float = 15.0
    critical_battery_pct: float = 5.0


@dataclass
class PowerManager:
    cfg: PowerConfig = field(default_factory=PowerConfig)
    state: State = State.SLEEP_DEEP
    state_since: float = 0.0
    record_until: float = 0.0
    live_until: float = 0.0
    battery_pct: float = 100.0
    thermal_fault: bool = False
    actions: List[str] = field(default_factory=list)

    # ---- events ----
    def boot(self, now: float) -> None:
        self._enter(State.SLEEP_CONNECTED, now)

    def on_motion(self, now: float) -> None:
        self.record_until = now + self.cfg.clip_seconds
        if self.state in (State.SLEEP_DEEP, State.SLEEP_CONNECTED):
            self._enter(State.RECORD, now)
        elif self.state == State.RECORD:
            pass  # extend recording window

    def on_live_request(self, now: float, on: bool) -> None:
        if on:
            self.live_until = now + self.cfg.live_hold_seconds
            if self.state != State.FAULT:
                self._enter(State.RECORD_LIVE, now)
        else:
            self.live_until = 0.0
            if self.state == State.RECORD_LIVE:
                self._enter(State.RECORD, now)

    def on_thermal_fault(self, fault: bool, now: float) -> None:
        self.thermal_fault = fault
        if fault:
            self._enter(State.FAULT, now)
        elif self.state == State.FAULT:
            self._enter(State.SLEEP_DEEP, now)

    def on_battery(self, pct: float, now: float) -> None:
        self.battery_pct = pct
        if pct <= self.cfg.critical_battery_pct and self.state != State.FAULT:
            self._enter(State.FAULT, now)

    # ---- periodic ----
    def tick(self, now: float) -> None:
        if self.state == State.FAULT:
            return
        if self.state == State.RECORD:
            if now >= self.record_until:
                self._enter(State.SLEEP_DEEP, now)
        elif self.state == State.RECORD_LIVE:
            if self.live_until and now >= self.live_until:
                self.live_until = 0.0
                self._enter(State.RECORD, now)

    # ---- helpers ----
    def _enter(self, new: State, now: float) -> None:
        if new == self.state:
            return
        self.actions.append(f"{self.state.value}->{new.value}")
        self.state = new
        self.state_since = now

    @property
    def soc_on(self) -> bool:
        return self.state in (State.RECORD, State.RECORD_LIVE)

    @property
    def modem_on(self) -> bool:
        return self.state in (State.SLEEP_CONNECTED, State.RECORD_LIVE)

    @property
    def recording(self) -> bool:
        return self.state in (State.RECORD, State.RECORD_LIVE)
