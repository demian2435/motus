# ruff: noqa: S101
"""Adapter unit tests."""

from typing import Any

import pytest

from motus.adapter import OutputAdapter


class DummyAdapter(OutputAdapter):
    """Adapter used for testing."""

    async def execute(self, action: dict[str, Any], event: dict[str, Any]) -> None:
        """Flag execution for assertions."""
        _ = (action, event)
        self.executed = True


@pytest.mark.asyncio
async def test_adapter_execute() -> None:
    """Ensure execute sets executed flag."""
    adapter = DummyAdapter()
    await adapter.execute({}, {})
    assert hasattr(adapter, "executed")
