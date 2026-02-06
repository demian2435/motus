"""Prometheus metrics for Motus."""

from prometheus_client import Counter

events_received = Counter("motus_events_received", "Events received")
decisions_made = Counter("motus_decisions_made", "Decisions taken")
actions_triggered = Counter("motus_actions_triggered", "Actions triggered")
actions_failed = Counter("motus_actions_failed", "Actions failed")
