"""Motus Decision Engine."""

import logging
import re
from typing import Any

from motus.persistence import Persistence


class DecisionEngine:
    """Evaluate rules and dispatch matching actions."""

    def __init__(
        self,
        rules: list[dict],
        adapters: list[Any],
        persistence: Persistence | None = None,
    ) -> None:
        """Create an engine with rules, adapters, and optional persistence."""
        self.rules = rules
        self.adapters = adapters
        self.persistence = persistence
        self.logger = logging.getLogger("motus.core")

    async def handle_event(self, event: dict[str, Any]) -> None:
        """Process an incoming event against all rules."""
        self.logger.info("Event received: %s", event)
        for rule in self.rules:
            if self.evaluate_rule(rule, event):
                self.logger.info("Rule matched: %s", rule.get("name"))
                await self.trigger_actions(rule, event)
                if self.persistence:
                    self.persistence.save_decision(event, rule)

    def evaluate_rule(self, rule: dict, event: dict) -> bool:
        """Return True if the event satisfies the rule conditions."""
        when = rule.get("when", {})
        return self._evaluate_conditions(when, event)

    def _evaluate_conditions(self, conditions: dict, event: dict) -> bool:
        """Recursive AND/OR logic with numeric comparison support."""
        if isinstance(conditions, dict):
            if "and" in conditions:
                return all(
                    self._evaluate_conditions(cond, event) for cond in conditions["and"]
                )
            if "or" in conditions:
                return any(
                    self._evaluate_conditions(cond, event) for cond in conditions["or"]
                )
            return all(
                self._match_condition(key, value, event)
                for key, value in conditions.items()
            )

        if isinstance(conditions, list):
            return all(self._evaluate_conditions(cond, event) for cond in conditions)

        return False

    def _match_condition(self, key: str, expected: object, event: dict) -> bool:
        """Evaluate a single key/value condition against an event."""
        candidate = self._get_nested_value(event, key)
        if candidate is None:
            return False

        if isinstance(expected, str):
            numeric = re.match(r"^(>=|<=|>|<)(.+)$", expected)
            if numeric:
                op, raw_threshold = numeric.groups()
                return self._compare_numeric(candidate, raw_threshold, op)
            return candidate == expected

        return candidate == expected

    @staticmethod
    def _get_nested_value(event: dict, dotted_key: str) -> object | None:
        """Traverse dotted keys (e.g., metadata.size) within an event dict."""
        current: object = event
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    @staticmethod
    def _compare_numeric(candidate: object, threshold: str, op: str) -> bool:
        """Compare numeric values using the provided operator."""
        try:
            current_val = float(candidate)
            threshold_val = float(threshold)
        except (TypeError, ValueError):
            return False

        if op == ">":
            return current_val > threshold_val
        if op == "<":
            return current_val < threshold_val
        if op == ">=":
            return current_val >= threshold_val
        if op == "<=":
            return current_val <= threshold_val
        return False

    async def trigger_actions(self, rule: dict, event: dict) -> None:
        """Dispatch matching actions to the configured adapters."""
        then = rule.get("then")
        if not isinstance(then, list):
            msg = "Rule '{}' must define 'then' as a list of actions".format(
                rule.get(
                    "name",
                    "<unnamed>",
                ),
            )
            raise TypeError(msg)
        actions = then
        if not actions:
            self.logger.warning("Rule '%s' has no actions", rule.get("name"))
            return
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
                    self.logger.info("Action executed: %s", action)
