"""Metriche Prometheus per Motus."""

from prometheus_client import Counter

events_received = Counter("motus_events_received", "Eventi ricevuti")
decisions_made = Counter("motus_decisions_made", "Decisioni prese")
actions_triggered = Counter("motus_actions_triggered", "Azioni triggerate")
actions_failed = Counter("motus_actions_failed", "Azioni fallite")
