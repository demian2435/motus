# ruff: noqa: D100, D103

import pytest

from motus.core import DecisionEngine
from motus.plugins.adapters.dummy import DummyAdapter


@pytest.mark.asyncio
async def test_integration_event_to_action() -> None:
    rule = {
        "name": "integration",
        "when": {"type": "integration"},
        "then": {"target": "dummy"},
    }
    adapter = DummyAdapter()
    engine = DecisionEngine([rule], [adapter])
    await engine.handle_event({"type": "integration"})
    # Verifica che DummyAdapter abbia loggato l'azione
    # (qui si può estendere con mock/log capture)
