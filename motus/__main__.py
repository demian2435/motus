"""Entrypoint Motus."""

import argparse
import asyncio
import importlib
import logging
import sys
from pathlib import Path

from motus.core import DecisionEngine
from motus.logging_config import setup_logging
from motus.persistence import Persistence
from motus.registry import ADAPTER_REGISTRY, INGESTOR_REGISTRY
from motus.utils import load_rules_from_folder, watch_rules_folder


def _collect_plugin_requirements(rules: list[dict]) -> tuple[dict, dict]:
    """Return required ingestor and adapter definitions from rules."""
    ingestor_types: dict[str, dict] = {}
    adapter_types: dict[str, dict] = {}

    for rule in rules:
        input_info = rule.get("input")
        if input_info:
            ing_type = input_info.get("type")
            params = input_info.get("params", {})
            if ing_type and ing_type not in ingestor_types:
                ingestor_types[ing_type] = params

        then = rule.get("then")
        if not isinstance(then, list):
            msg = "Rule '{}' must define 'then' as a list of actions".format(
                rule.get(
                    "name",
                    "<unnamed>",
                ),
            )
            raise TypeError(msg)

        for action in then:
            target = action.get("target")
            if target and target not in adapter_types:
                adapter_types[target] = action.get("params", {})

    return ingestor_types, adapter_types


def _normalize_rules(rules: list[dict]) -> list[dict]:
    """Normalize rule fields: enforce lists for 'when' and 'then'."""
    normalized: list[dict] = []
    for rule in rules:
        rule_copy = dict(rule)

        when = rule_copy.get("when")
        if not isinstance(when, list):
            msg = "Rule '{}' must define 'when' as a list".format(
                rule_copy.get(
                    "name",
                    "<unnamed>",
                ),
            )
            raise TypeError(msg)

        then = rule_copy.get("then")
        if not isinstance(then, list):
            msg = "Rule '{}' must define 'then' as a list of actions".format(
                rule_copy.get(
                    "name",
                    "<unnamed>",
                ),
            )
            raise TypeError(msg)

        normalized.append(rule_copy)

    return normalized


def _load_plugins_from(
    root: str,
    package_prefix: str | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """Load plugin modules from a root folder."""
    log = logger or logging.getLogger("motus.plugins")
    abs_root = Path(root).resolve()
    if not abs_root.is_dir():
        log.warning("Plugin root not found: %s", abs_root)
        return
    if package_prefix is None and str(abs_root) not in sys.path:
        sys.path.insert(0, str(abs_root))

    def _import_module(mod: str) -> None:
        try:
            importlib.import_module(mod)
        except Exception:
            log.exception("Failed to import plugin module %s from %s", mod, abs_root)

    def _import_py_files(base: Path, prefix: str | None) -> None:
        for file in base.iterdir():
            if file.suffix == ".py" and file.name != "__init__.py":
                modname = file.stem
                full_mod = f"{prefix}.{modname}" if prefix else modname
                _import_module(full_mod)

    _import_py_files(abs_root, package_prefix)
    for subfolder in ("ingestors", "adapters"):
        folder = abs_root / subfolder
        if folder.is_dir():
            sub_prefix = (
                f"{package_prefix}.{subfolder}" if package_prefix else subfolder
            )
            _import_py_files(folder, sub_prefix)


def import_all_plugins(custom_root: str | None = None) -> None:
    """Load bundled plugins and optional custom plugins."""
    base_dir = Path(__file__).parent
    bundled_root = base_dir / "plugins"
    log = logging.getLogger("motus.plugins")
    _load_plugins_from(
        str(bundled_root),
        package_prefix="motus.plugins",
        logger=log,
    )
    if custom_root:
        _load_plugins_from(custom_root, package_prefix=None, logger=log)


def build_stack_from_rules(rules: list[dict]) -> tuple[list, list, list]:
    """Build ingestors and adapters dynamically from rules.

    Returns (ingestors, adapters, rules).
    """
    ingestor_types, adapter_types = _collect_plugin_requirements(rules)
    # Instantiate ingestors
    ingestors = []
    for ing_type, params in ingestor_types.items():
        ing_cls = INGESTOR_REGISTRY.get(ing_type)
        if not ing_cls:
            msg = f"Ingestor plugin '{ing_type}' not found"
            raise RuntimeError(msg)
        # The callback will be set later
        ingestors.append((ing_cls, params))
    # Instantiate adapters
    adapters = []
    for ad_type in adapter_types:
        ad_cls = ADAPTER_REGISTRY.get(ad_type)
        if not ad_cls:
            msg = f"Adapter plugin '{ad_type}' not found"
            raise RuntimeError(msg)
        adapters.append(ad_cls())
    return ingestors, adapters, rules


def _build_stack_with_retry(
    rules: list[dict],
    plugins_root: str | None,
    logger: logging.Logger,
) -> tuple[list, list, list]:
    """Try building the stack; if a plugin is missing, re-import and retry once."""
    try:
        return build_stack_from_rules(rules)
    except RuntimeError as exc:
        missing = str(exc)
        logger.warning("Missing plugin detected, attempting reload: %s", missing)
        import_all_plugins(plugins_root)
        return build_stack_from_rules(rules)


async def _run_engine(rules_folder: str, plugins_root: str | None) -> None:
    """Run Motus using the provided rules folder and plugin root."""
    setup_logging()
    logger = logging.getLogger("motus.main")
    logger.info("Motus is starting up...")
    import_all_plugins(plugins_root)
    extra = f" + custom from {plugins_root}" if plugins_root else ""
    logger.info("Plugins imported: bundled motus/plugins%s", extra)
    rules = _normalize_rules(load_rules_from_folder(rules_folder))
    logger.info("Loaded %d rule(s) from folder '%s'", len(rules), rules_folder)
    persistence = Persistence()
    logger.info("Persistence initialized")
    ingestor_defs, adapters, rules = _build_stack_with_retry(
        rules,
        plugins_root,
        logger,
    )
    logger.info(
        "Adapters loaded: %s",
        [adapter.__class__.__name__ for adapter in adapters],
    )
    engine = DecisionEngine(rules, adapters, persistence)
    logger.info("DecisionEngine ready")
    # Instantiate and start all ingestors; track them by plugin name
    ingestors: dict[str, asyncio.Task] = {}

    async def _start_ingestor(ing_cls: type, params: dict) -> None:
        instance = ing_cls(
            lambda event: asyncio.create_task(engine.handle_event(event)),
            **params,
        )
        task = asyncio.create_task(instance.start())
        key = getattr(ing_cls, "plugin_name", ing_cls.__name__)
        ingestors[key] = task
        logger.info(
            "Ingestor started: %s with params %s",
            ing_cls.__name__,
            params,
        )

    for ing_cls, params in ingestor_defs:
        await _start_ingestor(ing_cls, params)

    async def _reload_stack(updated_rules: list[dict]) -> None:
        """Reload plugins and rebuild adapters/ingestors when rules change."""
        try:
            normalized_rules = _normalize_rules(updated_rules)
            ing_defs, new_adapters, _ = _build_stack_with_retry(
                normalized_rules,
                plugins_root,
                logger,
            )
        except RuntimeError:  # pragma: no cover - defensive logging
            logger.exception("Reload failed during stack rebuild")
            return

        engine.adapters = new_adapters
        engine.rules = normalized_rules
        for ing_cls, params in ing_defs:
            key = getattr(ing_cls, "plugin_name", ing_cls.__name__)
            if key not in ingestors or ingestors[key].done():
                await _start_ingestor(ing_cls, params)
        logger.info(
            "Stack refreshed: %d rules, %d adapters, %d ingestors",
            len(updated_rules),
            len(new_adapters),
            len(ingestors),
        )

    tasks = list(ingestors.values())
    watcher = logging.getLogger("motus.rules_watcher")
    tasks.append(
        watch_rules_folder(
            rules_folder,
            engine,
            logger=watcher,
            on_change=_reload_stack,
        ),
    )
    await asyncio.gather(*tasks)


def main() -> None:
    """CLI entrypoint to start Motus with the provided rules and plugins."""
    parser = argparse.ArgumentParser(description="Motus Event-Driven Automation Engine")
    parser.add_argument(
        "--rules-folder",
        type=str,
        default=None,
        help="Folder containing YAML rule files",
    )
    parser.add_argument(
        "--plugins-root",
        type=str,
        default=None,
        help="Optional custom root containing ingestors/ and adapters/",
    )
    args = parser.parse_args()

    rules_folder = str(Path(args.rules_folder).resolve())
    asyncio.run(_run_engine(rules_folder, args.plugins_root))


if __name__ == "__main__":
    main()
