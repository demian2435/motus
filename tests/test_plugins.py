# ruff: noqa: D100,D103,ANN001,S101

from motus import __main__
from motus.registry import ADAPTER_REGISTRY, INGESTOR_REGISTRY


def test_import_all_plugins_registers_defaults() -> None:
    __main__.import_all_plugins()
    assert "webhook" in INGESTOR_REGISTRY
    assert "dummy" in ADAPTER_REGISTRY
    assert "logger" in ADAPTER_REGISTRY


def test_import_all_plugins_custom_root(tmp_path) -> None:
    # create a minimal custom adapter
    adapter_dir = tmp_path / "adapters"
    adapter_dir.mkdir(parents=True)
    (tmp_path / "__init__.py").write_text("")
    (adapter_dir / "__init__.py").write_text("")
    (adapter_dir / "echo.py").write_text(
        """
from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("echo")
class Echo(OutputAdapter):
    async def execute(self, action, event):
        return None
""",
    )

    __main__.import_all_plugins(str(tmp_path))
    assert "echo" in ADAPTER_REGISTRY
