# ruff: noqa: S101
"""Decision engine tests."""

import pytest

from motus.core import DecisionEngine


class DummyAdapter:
    """Collect execution calls for assertions."""

    def __init__(self) -> None:
        """Initialize adapter call flag."""
        self.called = False

    async def execute(self, action: dict, event: dict) -> None:
        """Mark adapter as called; args are intentionally unused."""
        _ = (action, event)
        self.called = True


@pytest.mark.asyncio
async def test_decision_engine_triggers_action() -> None:
    """Trigger matching rule executes adapter."""
    rule = {
        "name": "test",
        "when": {"type": "test"},
        "then": [{"target": "dummy"}],
    }
    adapter = DummyAdapter()
    engine = DecisionEngine([rule], [adapter])
    await engine.handle_event({"type": "test"})
    assert adapter.called


@pytest.mark.asyncio
async def test_decision_engine_and_or_and_nested_paths() -> None:
    """Match both OR branches and ensure non-match scenario."""
    rule = {
        "name": "complex",
        "when": {
            "or": [
                {"and": [{"type": "alpha"}, {"metadata.score": ">=10"}]},
                {"and": [{"type": "beta"}, {"metadata.level": "pro"}]},
            ],
        },
        "then": [{"target": "dummy"}],
    }
    adapter = DummyAdapter()
    engine = DecisionEngine([rule], [adapter])

    # match first OR branch
    adapter.called = False
    await engine.handle_event({"type": "alpha", "metadata": {"score": 12}})
    assert adapter.called is True

    # match second OR branch
    adapter.called = False
    await engine.handle_event({"type": "beta", "metadata": {"level": "pro"}})
    assert adapter.called is True

    # no match
    adapter.called = False
    await engine.handle_event({"type": "gamma", "metadata": {"score": 5}})
    assert adapter.called is False


@pytest.mark.asyncio
async def test_decision_engine_numeric_comparisons_and_non_match() -> None:
    """Validate numeric comparisons and non-match cases."""
    rule = {
        "name": "numeric",
        "when": {
            "and": [
                {"value": ">=5"},
                {"value": "<10"},
            ],
        },
        "then": [{"target": "dummy"}],
    }
    adapter = DummyAdapter()
    engine = DecisionEngine([rule], [adapter])

    adapter.called = False
    await engine.handle_event({"value": 7})
    assert adapter.called is True

    adapter.called = False
    await engine.handle_event({"value": 3})
    assert adapter.called is False

    adapter.called = False
    await engine.handle_event({"value": 12})
    assert adapter.called is False


@pytest.mark.asyncio
async def test_decision_engine_ignores_malformed_when() -> None:
    """Ensure malformed rules are safely ignored."""
    rule = {
        "name": "malformed",
        "when": "not-a-dict",
        "then": [{"target": "dummy"}],
    }
    adapter = DummyAdapter()
    engine = DecisionEngine([rule], [adapter])
    adapter.called = False
    await engine.handle_event({"type": "anything"})
    assert adapter.called is False
