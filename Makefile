SOURCES = app tests

.DEFAULT_GOAL := help

help: ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

install: ## Install project dependencies
	poetry install --no-interaction --no-ansi
.PHONY: install

format: ## Format the source code
	poetry run black $(SOURCES)
	poetry run autopep8 $(SOURCES)
	poetry run isort $(SOURCES)
.PHONY: format

lint: ## Lint the source code
	poetry run black --check $(SOURCES)
	poetry run isort --check $(SOURCES)

	poetry run flake8 $(SOURCES)
	poetry run mypy $(SOURCES)
	poetry run bandit -c pyproject.toml -r app

.PHONY: lint

run: ## Run the project
	poetry run python app/main.py
.PHONY: run

tests-units: ## Run unit tests
	poetry run coverage run -m pytest -s --junitxml=report.xml ./tests/units
	poetry run coverage html
	# NB: Remove "|| true" when coverage level reach 80%.
	poetry run coverage report --precision=2 --fail-under=80 || true
.PHONY: tests-units

tests-integrations: ## Run integration tests
	poetry run pytest tests/integrations
.PHONY: tests-integrations

test: tests-units tests-integrations ## Run all available tests
.PHONY: test
