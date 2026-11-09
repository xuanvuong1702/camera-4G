"""sysfs GPIO access for the Core1106 (Linux).

Pins used by the carrier (see hardware/kicad/CAM4G):
  PIR        - input, interrupt via poll() on value
  IR_PWM     - output (PWM handled separately by the SoC PWM driver)
  IRCUT_A/B  - output
  SOC_READY  - output to the MCU
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class SysfsGPIO:
    base: str = "/sys/class/gpio"

    def _path(self, pin: int, leaf: str) -> str:
        return os.path.join(self.base, f"gpio{pin}", leaf)

    def export(self, pin: int) -> None:
        path = os.path.join(self.base, "export")
        if not os.path.exists(os.path.join(self.base, f"gpio{pin}")):
            with open(path, "w") as fh:
                fh.write(str(pin))

    def set_direction(self, pin: int, output: bool) -> None:
        self.export(pin)
        with open(self._path(pin, "direction"), "w") as fh:
            fh.write("out" if output else "in")

    def write(self, pin: int, value: int) -> None:
        with open(self._path(pin, "value"), "w") as fh:
            fh.write("1" if value else "0")

    def read(self, pin: int) -> int:
        with open(self._path(pin, "value")) as fh:
            return 1 if fh.read().strip() == "1" else 0
