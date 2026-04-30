from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryStore:
    items: list[dict[str, Any]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.items.append({"role": role, "content": content, "ts": now_iso()})

    def export(self) -> list[dict[str, Any]]:
        return list(self.items)
