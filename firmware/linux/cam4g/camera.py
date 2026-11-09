"""Camera capture adapters.

Two backends:
  * V4L2Camera  - shells out to v4l2-ctl on the target (rkcif / rkisp)
  * SimCamera   - deterministic frames for tests and bench simulation
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class V4L2Camera:
    device: str = "/dev/video15"
    width: int = 1280
    height: int = 720
    fmt: str = "MJPG"

    def capture(self) -> Optional[bytes]:
        cmd = [
            "v4l2-ctl", f"--device={self.device}",
            f"--set-fmt-video=width={self.width},height={self.height},pixelformat={self.fmt}",
            "--stream-mmap", "--stream-count=1", "--stream-to=/tmp/cam4g-frame.jpg",
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=5)
            with open("/tmp/cam4g-frame.jpg", "rb") as fh:
                return fh.read()
        except (OSError, subprocess.SubprocessError):
            return None


@dataclass
class SimCamera:
    payload: bytes = b"\xff\xd8" + b"\x00" * 3000 + b"\xff\xd9"

    def capture(self) -> bytes:
        return self.payload
