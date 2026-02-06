

# Motus

Motus is an event-driven automation engine written in Python. It ingests events from any source, evaluates declarative YAML rules, and triggers actions via pluggable adapters. The engine is modular, extensible, and ready for Docker/Kubernetes, serverless, or bare-metal deployments.

---

## Features

- Asynchronous event handling with pluggable ingestors and adapters
- Declarative YAML rules with AND/OR logic and numeric comparisons (>, <, >=, <=)
- Hot-reload of rule files via a filesystem watcher
- SQL db persistence for audit trails

---

## Installation

### Prerequisites
- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation)

### Setup

```bash
git clone <your-repo-url>
cd motus
poetry install
```

---

## Quick Start

1) Review a sample rule in `examples/rules/example_rule.yaml` or `examples/rules/complex_rule.yaml`.

2) Start Motus with the rules folder (required) and optionally a custom plugins root:

```bash
poetry run python -m motus --rules-folder examples/rules --custom-plugins examples/plugins
```

3) Send a sample event to the bundled webhook ingestor:

```bash
curl -X POST http://localhost:8080/event \
	-H "Content-Type: application/json" \
	-d '{"type": "data.arrival", "source": "test", "metadata": {"size_gb": 120}}'
```

You should see logs showing the matched rule and the triggered actions (e.g., `dummy`, `logger`, or `prometheus`). Rules in the folder are watched and reloaded automatically when files change.

---

## How Motus Works

- **Ingest**: An ingestor (e.g., webhook) normalizes incoming payloads into a standard event shape.
- **Decide**: The `DecisionEngine` evaluates each rule (`when` supports nested AND/OR and numeric comparators). On match it records the decision via SQLite persistence.
- **Act**: Matching actions are dispatched to adapters; each action entry in `then` targets a specific adapter.
- **Observe**: Prometheus counters (`motus_actions_total`, `motus_events_received`, etc.) are available; logging is colorized for quick scanning.
- **Reload**: A lightweight watcher keeps the in-memory rules list in sync with the rules directory without restarting the process.

Bundled plugins:
- Ingestors: `webhook`
- Adapters: `dummy`, `logger`, `http_post`, `email`

---

## Writing Rules

- Place YAML files under the folder passed to `--rules-folder` (e.g., `examples/rules`).
- A rule contains `name`, optional `input`, mandatory `when`, and `then` (both are lists: `when` entries are evaluated, `then` actions are executed).
- Nested fields use dot notation (e.g., `metadata.size_gb`). Comparisons accept `>`, `<`, `>=`, `<=` prefixes on string values.
- Multiple actions are supported by providing a list under `then`.

Example (multi-action):

```yaml
name: multi-action-bigdata
input:
	type: webhook
	params:
		port: 8080
when:
	- or:
		- and:
			- type: data.arrival
			- metadata.size_gb: ">=100"
		- and:
			- type: data.arrival
			- metadata.priority: "high"
then:
	- target: dummy
		params:
			mode: batch
			priority: high
	- target: logger
		message: "Big data event processed!"
```

---

## Creating Custom Plugins

Custom plugins live outside the codebase and are loaded with `--plugins-root <path>`. Under that root you can have `adapters/` and `ingestors/` packages (no special naming required beyond folder layout).

### Custom output adapter
```python
# adapters/my_notifier.py
from motus.adapter import OutputAdapter
from motus.registry import register_adapter

@register_adapter("my_notifier")
class MyNotifier(OutputAdapter):
		async def execute(self, action, event):
				target_url = action.get("url")
				if not target_url:
						self.logger.warning("No url provided")
						return
				# send the notification here
				self.logger.info("Notification sent to %s for event %s", target_url, event)
```

Then reference it from a rule (note: `then` is always a list):

```yaml
then:
	- target: my_notifier
	  url: "https://hooks.example.com/motus"
```

### Custom ingestor
```python
# ingestors/kafka_consumer.py
from motus.ingestor import EventIngestor
from motus.registry import register_ingestor

@register_ingestor("kafka")
class KafkaIngestor(EventIngestor):
		def __init__(self, callback, topic: str):
				super().__init__(callback)
				self.topic = topic

		async def start(self):
				while True:
						event = await self._poll_message()  # implement your poll
						self.callback(self.normalize_event(event))
```

Run Motus pointing to your plugin root (alongside bundled plugins):

```bash
poetry run python -m motus --rules-folder ./rules --plugins-root ./my_plugins
```

You can see a minimal adapter example in `examples/plugins/echo.py` paired with the rule `examples/rules/custom_echo_rule.yaml`.

---

## Local Testing

- Install dev dependencies once: `poetry install --with dev`
- Run the whole suite (async-friendly):

```bash
PYTHONPATH=. poetry run pytest
```

- Target a subset:

```bash
PYTHONPATH=. poetry run pytest tests/test_core.py -k numeric
```

- During development, add `-s` for live logs or `-q` for quiet output. Tests rely on `pytest-asyncio`, so keep `PYTHONPATH=.` to resolve the local package.

Linting/formatting (optional but recommended):

```bash
poetry run ruff format .
poetry run ruff check --select ALL .
```

---

## Troubleshooting

- No action firing: verify the event fields match the rule (including dot-notation keys) and that `then.target` matches a registered adapter name.
- Plugin not found: ensure the class is decorated with `@register_ingestor` or `@register_adapter` and that `--plugins-root` points to the directory containing `adapters/` or `ingestors/`.
- Rule changes not reflected: confirm you are editing files under the folder passed to `--rules-folder`; the watcher reloads on file changes.

---

## Contributing

Contributions are welcome! Please open issues or pull requests for bugfixes, features, or documentation improvements.

---

## License

MIT License
