"""Motus Decision Engine."""

import logging
from typing import Any


class DecisionEngine:
    def __init__(
        self,
        rules: list[dict],
        adapters: list[Any],
        persistence: Any | None = None,
    ) -> None:
        self.rules = rules
        self.adapters = adapters
        self.persistence = persistence
        self.logger = logging.getLogger("motus.core")

    async def handle_event(self, event: dict[str, Any]) -> None:
        self.logger.info(f"Event received: {event}")
        for rule in self.rules:
            if self.evaluate_rule(rule, event):
                self.logger.info(f"Rule matched: {rule.get('name')}")
                await self.trigger_actions(rule, event)
                if self.persistence:
                    self.persistence.save_decision(event, rule)

    def evaluate_rule(self, rule: dict, event: dict) -> bool:
        # Support AND/OR logic in 'when'
        when = rule.get("when", {})
        return self._evaluate_conditions(when, event)

    def _evaluate_conditions(self, conditions: dict, event: dict) -> bool:
        # Recursive AND/OR logic with support for >=, <=, >, <
        import re

        if isinstance(conditions, dict):
            if "and" in conditions:
                return all(
                    self._evaluate_conditions(cond, event) for cond in conditions["and"]
                )
            if "or" in conditions:
                return any(
                    self._evaluate_conditions(cond, event) for cond in conditions["or"]
                )
            # Flat dict: all AND
            for key, value in conditions.items():
                if "." in key:
                    parts = key.split(".")
                    val = event
                    for p in parts:
                        val = val.get(p, None)
                        if val is None:
                            return False
                    if isinstance(value, str):
                        # Support >=, <=, >, <
                        m = re.match(r"^(>=|<=|>|<)(.+)$", value)
                        if m:
                            op, num = m.groups()
                            try:
                                val_f = float(val)
                                num_f = float(num)
                            except Exception:
                                return False
                            if op == ">":
                                if not val_f > num_f:
                                    return False
                            elif op == "<":
                                if not val_f < num_f:
                                    return False
                            elif op == ">=":
                                if not val_f >= num_f:
                                    return False
                            elif op == "<=" and not val_f <= num_f:
                                return False
                        elif val != value:
                            return False
                    elif val != value:
                        return False
                else:
                    current = event.get(key)
                    if isinstance(value, str):
                        m = re.match(r"^(>=|<=|>|<)(.+)$", value)
                        if m:
                            op, num = m.groups()
                            try:
                                cur_f = float(current)
                                num_f = float(num)
                            except Exception:
                                return False
                            if op == ">" and not cur_f > num_f:
                                return False
                            if op == "<" and not cur_f < num_f:
                                return False
                            if op == ">=" and not cur_f >= num_f:
                                return False
                            if op == "<=" and not cur_f <= num_f:
                                return False
                        elif current != value:
                            return False
                    elif current != value:
                        return False
            return True
        if isinstance(conditions, list):
            # List: all AND
            return all(self._evaluate_conditions(cond, event) for cond in conditions)
        return False

    async def trigger_actions(self, rule: dict, event: dict) -> None:
        then = rule.get("then", {})
        actions = then if isinstance(then, list) else [then]
        for action in actions:
            target = action.get("target")
            for adapter in self.adapters:
                plugin_name = getattr(
                    adapter,
                    "plugin_name",
                    adapter.__class__.__name__,
                ).lower()
                class_name = adapter.__class__.__name__.lower()
                # Only trigger the adapter matching the target
                if target and (
                    plugin_name == target.lower()
                    or class_name.startswith(target.lower())
                ):
                    await adapter.execute(action, event)
                    self.logger.info(f"Action executed: {action}")
