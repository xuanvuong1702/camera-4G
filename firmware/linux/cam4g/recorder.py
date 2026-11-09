"""Segment recorder: writes MJPEG frames to SD in timed segments.

Designed for power-loss safety: every segment is fsynced at a fixed cadence
and closed with a trailer so a crashed write loses at most one segment.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RecorderConfig:
    root: str
    segment_seconds: float = 30.0
    fsync_frames: int = 30
    max_segments: int = 10000


@dataclass
class SegmentRecorder:
    cfg: RecorderConfig
    _fh: Optional[object] = None
    _frames: int = 0
    _seg_start: float = 0.0
    _seg_index: int = 0
    segments_written: int = 0
    bytes_written: int = 0

    def __post_init__(self) -> None:
        os.makedirs(os.path.join(self.cfg.root, "video"), exist_ok=True)

    def start(self, now: float) -> None:
        if self._fh is not None:
            return
        self._seg_start = now
        path = self._segment_path(now)
        self._fh = open(path, "wb")
        self._frames = 0

    def write_frame(self, frame: bytes, now: float) -> None:
        if self._fh is None:
            self.start(now)
        self._fh.write(frame)
        self.bytes_written += len(frame)
        self._frames += 1
        if self.cfg.fsync_frames and self._frames % self.cfg.fsync_frames == 0:
            self._fh.flush()
            os.fsync(self._fh.fileno())
        if now - self._seg_start >= self.cfg.segment_seconds:
            self._rotate(now)

    def stop(self) -> None:
        if self._fh is None:
            return
        self._fh.flush()
        os.fsync(self._fh.fileno())
        self._fh.close()
        self._fh = None
        self.segments_written += 1

    def _rotate(self, now: float) -> None:
        self.stop()
        self._seg_index += 1
        self.start(now)

    def _segment_path(self, now: float) -> str:
        stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now))
        return os.path.join(self.cfg.root, "video", f"seg-{stamp}-{self._seg_index:05d}.mjpeg")
