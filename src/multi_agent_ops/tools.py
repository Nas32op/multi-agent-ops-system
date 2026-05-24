"""Tools and utilities for multi-agent-ops-system."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["now_iso", "MemoryStore"]


def now_iso() -> str:
    """Get current UTC time in ISO format.

    Returns:
        Current UTC time as ISO 8601 string
    """
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryStore:
    """Simple in-memory storage for agent interactions."""

    items: list[dict[str, Any]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        """Add an item to the memory store.

        Args:
            role: The role of the entity (e.g., 'user', 'planner', 'executor', 'reviewer')
            content: The content to store
        """
        self.items.append({"role": role, "content": content, "ts": now_iso()})
        logger.debug("Added item to memory store: role=%s, content_length=%d", role, len(content))

    def export(self) -> list[dict[str, Any]]:
        """Export all items from the memory store.

        Returns:
            List of all stored items
        """
        return list(self.items)

    def clear(self) -> None:
        """Clear all items from the memory store."""
        self.items.clear()
        logger.debug("Cleared memory store")

    def get_by_role(self, role: str) -> list[dict[str, Any]]:
        """Get all items for a specific role.

        Args:
            role: The role to filter by

        Returns:
            List of items matching the specified role
        """
        return [item for item in self.items if item["role"] == role]

    def __len__(self) -> int:
        """Get the number of items in the memory store.

        Returns:
            Number of items
        """
        return len(self.items)
