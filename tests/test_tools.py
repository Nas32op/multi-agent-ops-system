"""Tests for tools and utilities."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from multi_agent_ops.tools import MemoryStore, now_iso


class TestNowIso:
    """Tests for now_iso function."""

    def test_now_iso_returns_string(self) -> None:
        """Test that now_iso returns a string."""
        result = now_iso()
        assert isinstance(result, str)

    def test_now_iso_format(self) -> None:
        """Test that now_iso returns ISO format."""
        result = now_iso()
        # Should be parseable as ISO format
        datetime.fromisoformat(result)


class TestMemoryStore:
    """Tests for MemoryStore class."""

    def test_memory_store_initialization(self) -> None:
        """Test MemoryStore initialization."""
        store = MemoryStore()
        assert len(store.items) == 0

    def test_memory_store_add(self) -> None:
        """Test adding items to MemoryStore."""
        store = MemoryStore()
        store.add("user", "test content")

        assert len(store.items) == 1
        assert store.items[0]["role"] == "user"
        assert store.items[0]["content"] == "test content"
        assert "ts" in store.items[0]

    def test_memory_store_export(self) -> None:
        """Test exporting items from MemoryStore."""
        store = MemoryStore()
        store.add("user", "content 1")
        store.add("planner", "content 2")

        exported = store.export()
        assert len(exported) == 2
        assert exported[0]["role"] == "user"
        assert exported[1]["role"] == "planner"

    def test_memory_store_clear(self) -> None:
        """Test clearing MemoryStore."""
        store = MemoryStore()
        store.add("user", "content")
        assert len(store) == 1

        store.clear()
        assert len(store) == 0

    def test_memory_store_get_by_role(self) -> None:
        """Test getting items by role."""
        store = MemoryStore()
        store.add("user", "content 1")
        store.add("planner", "content 2")
        store.add("user", "content 3")

        user_items = store.get_by_role("user")
        assert len(user_items) == 2
        assert all(item["role"] == "user" for item in user_items)

    def test_memory_store_len(self) -> None:
        """Test MemoryStore length."""
        store = MemoryStore()
        assert len(store) == 0

        store.add("user", "content")
        assert len(store) == 1

        store.add("planner", "content")
        assert len(store) == 2
