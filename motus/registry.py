"""Global plugin registries for Motus."""

from collections.abc import Callable
from typing import TypeVar

INGESTOR_REGISTRY: dict[str, type] = {}
ADAPTER_REGISTRY: dict[str, type] = {}

T = TypeVar("T", bound=type)


def register_ingestor(name: str) -> Callable[[T], T]:
    """Register an ingestor class under the given plugin name."""

    def decorator(cls: T) -> T:
        cls.plugin_name = name
        INGESTOR_REGISTRY[name] = cls
        return cls

    return decorator


def register_adapter(name: str) -> Callable[[T], T]:
    """Register an adapter class under the given plugin name."""

    def decorator(cls: T) -> T:
        cls.plugin_name = name
        ADAPTER_REGISTRY[name] = cls
        return cls

    return decorator
