# ruff: noqa: D100, D101, D102, D103, S101

from motus.ingestor import EventIngestor


class DummyIngestor(EventIngestor):
    async def start(self) -> None:
        pass


def test_normalize_event() -> None:
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
