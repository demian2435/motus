# ruff: noqa: S101
"""Tests for ingestors."""

from motus.ingestor import EventIngestor


class DummyIngestor(EventIngestor):
    """Minimal ingestor used for normalization tests."""

    async def start(self) -> None:
        """No-op start implementation for tests."""
        return


def test_normalize_event() -> None:
    """Ensure normalization preserves expected fields."""
    ing = DummyIngestor(lambda e: e)
    raw = {
        "type": "foo",
        "source": "bar",
        "metadata": {"x": 1},
        "timestamp": "2024-01-01T00:00:00Z",
    }
    norm = ing.normalize_event(raw)
    assert norm["type"] == "foo"
    assert norm["source"] == "bar"
    assert norm["metadata"]["x"] == 1
    assert norm["timestamp"] == "2024-01-01T00:00:00Z"
