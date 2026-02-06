"""Global plugin registries for Motus."""

INGESTOR_REGISTRY = {}
ADAPTER_REGISTRY = {}


def register_ingestor(name: str):
    def decorator(cls):
        cls.plugin_name = name
        INGESTOR_REGISTRY[name] = cls
        return cls

    return decorator


def register_adapter(name: str):
    def decorator(cls):
        cls.plugin_name = name
        ADAPTER_REGISTRY[name] = cls
        return cls

    return decorator
