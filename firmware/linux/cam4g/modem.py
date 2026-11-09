"""EC200U AT command client.

Transport-agnostic: on target it wraps a serial port, in tests a mock.
Only the AT layer lives here; PPP is configured by the OS (pppd + chat).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol


class Transport(Protocol):
    def write(self, data: bytes) -> None: ...
    def readline(self) -> bytes: ...


class ATError(RuntimeError):
    pass


@dataclass
class ATClient:
    transport: Transport
    timeout_s: float = 5.0
    _pending: List[bytes] = field(default_factory=list)

    def command(self, cmd: str, timeout_s: Optional[float] = None) -> List[str]:
        self.transport.write((cmd + "\r\n").encode())
        lines: List[str] = []
        for _ in range(200):
            raw = self.transport.readline()
            if not raw:
                break
            line = raw.decode(errors="replace").strip()
            if not line:
                continue
            if line in ("OK",):
                return lines
            if line.startswith("ERROR") or line.startswith("+CME ERROR"):
                raise ATError(f"{cmd} -> {line}")
            lines.append(line)
        if timeout_s is not None and not lines:
            raise ATError(f"{cmd} -> timeout")
        return lines

    # ---- helpers ----
    def alive(self) -> bool:
        try:
            self.command("AT")
            return True
        except ATError:
            return False

    def sim_ready(self) -> bool:
        try:
            lines = self.command("AT+CPIN?")
        except ATError:
            return False
        return any("READY" in ln for ln in lines)

    def signal_quality(self) -> int:
        lines = self.command("AT+CSQ")
        for ln in lines:
            if ln.startswith("+CSQ:"):
                try:
                    return int(ln.split(":")[1].split(",")[0])
                except (IndexError, ValueError):
                    return -1
        return -1

    def registration(self) -> int:
        lines = self.command("AT+CREG?")
        for ln in lines:
            if ln.startswith("+CREG:"):
                try:
                    return int(ln.split(",")[1])
                except (IndexError, ValueError):
                    return -1
        return -1

    def set_apn(self, apn: str) -> None:
        self.command(f'AT+CGDCONT=1,"IP","{apn}"')

    def network_info(self) -> str:
        lines = self.command("AT+QNWINFO")
        return lines[0] if lines else ""

    def rf_on(self, on: bool) -> None:
        self.command(f"AT+CFUN={1 if on else 4}")
