"""Uplink queue with retry/backoff, transport-agnostic.

The target uses PPP (4G) + MQTT; this module only handles ordering,
batching and persistence of pending messages so the transport can be
swapped (MQTT, HTTP, WebRTC data channel).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class UplinkConfig:
    spool_dir: str
    max_batch: int = 20
    max_pending: int = 2000


@dataclass
class Uplink:
    cfg: UplinkConfig
    pending: List[Dict] = field(default_factory=list)
    sent: int = 0
    failed: int = 0

    def __post_init__(self) -> None:
        os.makedirs(self.cfg.spool_dir, exist_ok=True)

    def enqueue(self, topic: str, payload: Dict) -> None:
        self.pending.append({"topic": topic, "payload": payload})
        if len(self.pending) > self.cfg.max_pending:
            self.pending = self.pending[-self.cfg.max_pending:]

    def next_batch(self) -> List[Dict]:
        return self.pending[: self.cfg.max_batch]

    def ack(self, batch: List[Dict]) -> None:
        for msg in batch:
            if msg in self.pending:
                self.pending.remove(msg)
                self.sent += 1

    def nack(self, batch: List[Dict]) -> None:
        self.failed += len(batch)

    def spool(self) -> str:
        path = os.path.join(self.cfg.spool_dir, "pending.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.pending, fh)
        return path

    def load(self) -> None:
        path = os.path.join(self.cfg.spool_dir, "pending.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self.pending = json.load(fh)
