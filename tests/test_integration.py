# ruff: noqa: S101
"""Integration-level tests for adapter execution."""

import pytest

from motus.core import DecisionEngine
from motus.plugins.adapters.dummy import DummyAdapter


@pytest.mark.asyncio
async def test_integration_event_to_action(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """End-to-end flow from event to adapter execution and logging."""
    rule = {
        "name": "integration",
        "when": [{"type": "integration"}],
        "then": [{"target": "dummy"}],
    }
    adapter = DummyAdapter()
    engine = DecisionEngine([rule], [adapter])
    with caplog.at_level("INFO", logger="DummyAdapter"):
        await engine.handle_event({"type": "integration"})

    messages = [record.message for record in caplog.records]
    assert any(
        "DummyAdapter: triggered for event type 'integration'" in message
        for message in messages
    )
