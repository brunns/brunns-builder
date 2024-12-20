SHELL = /bin/bash

default: help

.PHONY: test
test: ## Run tests
	tox -e py39,py313

.PHONY: coverage
coverage: ## Test coverage report
	tox -e coverage

.PHONY: lint
lint: check-format ## Lint code

.PHONY: check-format
check-format:
	tox -e check-format

.PHONY: format
format: ## Format code
	tox -e format

.PHONY: precommit
precommit: test lint coverage ## Pre-commit targets
	@ python -m this

.PHONY: recreate
recreate: clean  ## Recreate tox environments
	tox --recreate --notest -p -s
	tox --recreate --notest -e coverage,format,check-format -p

.PHONY: clean
clean: ## Clean generated files
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	rm -rf build/ dist/ *.egg-info/ .cache .coverage .pytest_cache
	find . -name "__pycache__" -type d -print | xargs -t rm -r
	find . -name "test-output" -type d -print | xargs -t rm -r

.PHONY: repl
repl: ## Python REPL
	tox -e py313 -- python

.PHONY: outdated
outdated: ## List outdated dependancies
	tox -e py313 -- pip list -o

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1,$$2}'
