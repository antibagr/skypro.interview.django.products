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

run: ## Run the development Django server
	poetry run python app/manage.py runserver
.PHONY: run

shell: ## Run the development Django shell
	poetry run python app/manage.py shell
.PHONY: shell

makemigrations: ## Create new migrations based on the changes detected in the models
	poetry run python app/manage.py makemigrations
.PHONY: makemigrations

migrate: ## Apply migrations to the database
	poetry run python app/manage.py migrate
.PHONY: migrate

db_update: makemigrations migrate ## Create new migrations and apply them to the database
.PHONY: db_update

compose-up: ## Run the development Django server with docker-compose
	docker-compose up --build --remove-orphans --force-recreate
.PHONY: compose-up

compose-down: ## Stop the development Django server with docker-compose
	docker-compose down
.PHONY: compose-down

tests-units: ## Run unit tests
	poetry run coverage run -m pytest -s ./tests/units
	poetry run coverage report  --precision=2 -m
.PHONY: tests-units

tests-integrations: ## Run integration tests
	poetry run pytest tests/integrations
.PHONY: tests-integrations

test: tests-units tests-integrations ## Run all available tests
.PHONY: test
