"""Utility helpers for Motus."""

import asyncio
import logging
import os
from pathlib import Path

import yaml

from motus.core import DecisionEngine


def load_rules_from_yaml(path: str | Path) -> list[dict]:
    """Load a YAML file and return all documents as a list of dicts."""
    path_obj = Path(path)
    with path_obj.open() as file:
        return list(yaml.safe_load_all(file))


def load_rules_from_folder(folder: str | Path) -> list:
    """Load all rules from all YAML files in a folder."""
    folder_path = Path(folder).resolve()
    if not folder_path.is_dir():
        msg = f"Rules folder not found: {folder_path}"
        raise FileNotFoundError(msg)

    rules: list[dict] = []
    for rule_file in folder_path.iterdir():
        if rule_file.suffix in {".yaml", ".yml"}:
            rules.extend(load_rules_from_yaml(rule_file))
    return rules


def _rules_snapshot(folder: Path) -> list[tuple[str, float, int]]:
    """Return a stable snapshot (name, mtime, size) for YAML files in a folder."""
    snapshot: list[tuple[str, float, int]] = []
    for rule_file in folder.iterdir():
        if rule_file.suffix in {".yaml", ".yml"}:
            try:
                stat = rule_file.stat()
            except FileNotFoundError:
                continue
            snapshot.append((rule_file.name, stat.st_mtime, stat.st_size))
    snapshot.sort()
    return snapshot


async def watch_rules_folder(
    folder: str | Path,
    engine: DecisionEngine,
    interval: float = 2.0,
    logger: logging.Logger | None = None,
) -> None:
    """Periodically watch a rules folder and reload rules on changes."""
    log = logger or logging.getLogger("motus.rules_watcher")
    if not folder:
        log.warning("Rules watcher disabled: no folder specified")
        return

    folder_path = Path(folder)
    exists = await asyncio.to_thread(os.path.isdir, folder_path)
    if not exists:
        log.error("Rules folder not found: %s", folder_path)
        return

    last_snapshot = _rules_snapshot(folder_path)
    log.info("Rules watcher active on %s", folder_path)

    while True:
        await asyncio.sleep(interval)
        snapshot = _rules_snapshot(folder_path)
        if snapshot != last_snapshot:
            try:
                rules = load_rules_from_folder(folder_path)
            except FileNotFoundError:
                log.exception("Rules folder missing during watch: %s", folder_path)
                last_snapshot = []
                continue
            engine.rules = rules
            last_snapshot = snapshot
            log.info(
                "Rules reloaded (%d) after change in %s",
                len(rules),
                folder_path,
            )
