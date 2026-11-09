"""Thermal policy for outdoor operation (air 40-45 C, surface up to 70 C)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ThermalConfig:
    charge_max_c: float = 40.0
    throttle_c: float = 85.0
    shutdown_c: float = 95.0
    ambient_fault_c: float = 75.0


@dataclass
class ThermalPolicy:
    cfg: ThermalConfig = field(default_factory=ThermalConfig)

    def can_charge(self, battery_c: float) -> bool:
        return battery_c <= self.cfg.charge_max_c

    def throttle_level(self, soc_c: float) -> str:
        if soc_c >= self.cfg.shutdown_c:
            return "shutdown"
        if soc_c >= self.cfg.throttle_c:
            return "reduced"
        return "normal"

    def should_shutdown(self, soc_c: float, ambient_c: float) -> bool:
        return soc_c >= self.cfg.shutdown_c or ambient_c >= self.cfg.ambient_fault_c
