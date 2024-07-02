include .env
export

.PHONY: run
run:
	@poetry run python -m sistema_bancario

.PHONY: format
format:
	@poetry run ruff format

.PHONY: lint
lint:
	@poetry run ruff check --fix

.PHONY: format-lint
format-lint: format lint