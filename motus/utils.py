"""Utility helpers for Motus."""

import asyncio
import logging
import os

import yaml


def load_rules_from_yaml(path: str) -> list[dict]:
    with open(path) as f:
        return list(yaml.safe_load_all(f))


def load_rules_from_folder(folder: str) -> list:
    """Load all rules from all YAML files in a folder."""
    folder_abs = os.path.abspath(folder)
    if not os.path.isdir(folder_abs):
        msg = f"Rules folder not found: {folder_abs}"
        raise FileNotFoundError(msg)
    rules = []
    for fname in os.listdir(folder_abs):
        if fname.endswith((".yaml", ".yml")):
            rules.extend(load_rules_from_yaml(os.path.join(folder_abs, fname)))
    return rules


def _rules_snapshot(folder: str) -> list:
    """Return a stable snapshot (name, mtime, size) for YAML files in a folder."""
    snapshot = []
    for fname in os.listdir(folder):
        if fname.endswith((".yaml", ".yml")):
            path = os.path.join(folder, fname)
            try:
                stat = os.stat(path)
            except FileNotFoundError:
                continue
            snapshot.append((fname, stat.st_mtime, stat.st_size))
    snapshot.sort()
    return snapshot


async def watch_rules_folder(
    folder: str,
    engine,
    interval: float = 2.0,
    logger: logging.Logger | None = None,
) -> None:
    """Periodically watch a rules folder and reload rules on changes."""
    log = logger or logging.getLogger("motus.rules_watcher")
    if not folder:
        log.warning("Rules watcher disabled: no folder specified")
        return
    folder_abs = os.path.abspath(folder)
    if not os.path.isdir(folder_abs):
        log.error("Rules folder not found: %s", folder_abs)
        return

    last_snapshot = _rules_snapshot(folder_abs)
    log.info("Rules watcher active on %s", folder_abs)

    while True:
        await asyncio.sleep(interval)
        snapshot = _rules_snapshot(folder_abs)
        if snapshot != last_snapshot:
            try:
                rules = load_rules_from_folder(folder_abs)
            except FileNotFoundError:
                log.exception("Rules folder missing during watch: %s", folder_abs)
                last_snapshot = []
                continue
            engine.rules = rules
            last_snapshot = snapshot
            log.info(
                "Rules reloaded (%d) after change in %s",
                len(rules),
                folder_abs,
            )
