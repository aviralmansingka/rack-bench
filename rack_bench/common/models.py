"""Shared check and per-host/scope result envelopes."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


@dataclass
class Check:
    name: str
    status: Literal["pass", "warn", "fail", "skip"]
    value: Any = None
    expected: Any = None
    detail: str = ""
    source: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.status not in ("pass", "warn", "fail", "skip"):
            raise ValueError(f"Invalid check status: {self.status}")


@dataclass
class Result:
    scope: str
    host: str
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checks: list[Check] = field(default_factory=list)
    manifest: dict[str, Any] = field(default_factory=dict)
