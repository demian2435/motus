# ruff: noqa: D100,D103,ANN001,S101

import pytest

from motus import __main__
from motus.utils import load_rules_from_folder


def test_load_rules_from_folder_raises_on_missing(tmp_path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        load_rules_from_folder(str(missing))


def test_load_rules_from_folder_reads_all(tmp_path) -> None:
    f1 = tmp_path / "a.yaml"
    f2 = tmp_path / "b.yml"
    f1.write_text(
        """
---
name: r1
when:
  type: foo
then:
  target: dummy
""",
    )
    f2.write_text(
        """
---
name: r2
when:
  type: bar
then:
  target: dummy
""",
    )
    rules = load_rules_from_folder(str(tmp_path))
    names = {r.get("name") for r in rules}
    assert names == {"r1", "r2"}


def test_build_stack_from_rules_requires_plugins() -> None:
    __main__.import_all_plugins()
    rules = [
        {
            "name": "with-ingestor",
            "input": {"type": "webhook", "params": {}},
            "when": {"type": "demo"},
            "then": {"target": "dummy"},
        },
    ]
    ingestors, adapters, _ = __main__.build_stack_from_rules(rules)
    assert len(ingestors) == 1
    assert len(adapters) == 1


def test_build_stack_from_rules_missing_adapter_raises() -> None:
    __main__.import_all_plugins()
    rules = [
        {
            "name": "bad",
            "when": {"type": "demo"},
            "then": {"target": "nonexistent"},
        },
    ]
    with pytest.raises(RuntimeError):
        __main__.build_stack_from_rules(rules)
