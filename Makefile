.PHONY: help install _test test _format _lint lint _run run clean

RULES ?= examples/rules
PLUGINS ?= examples/plugins

help:
	@echo "Available targets:"
	@echo "  install        Install all dependencies via Poetry"
	@echo "  test           Run pytest"
	@echo "  lint           Run ruff format + ruff check"
	@echo "  run            Run Motus locally"
	@echo "  clean          Remove caches"

install:
	python -m poetry install

_test:
	@PYTHONPATH=. python -m poetry run pytest

test: _test clean

_format:
	@python -m poetry run ruff format motus || true

_lint:
	@python -m poetry run ruff check --select ALL motus --fix --unsafe-fixes || true

lint: _format _lint clean

_run:
	@python -m poetry run python -m motus --rules-folder $(RULES) --plugins-root $(PLUGINS)

run: _run clean

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .ruff_cache
	@echo "Clean workspace"
