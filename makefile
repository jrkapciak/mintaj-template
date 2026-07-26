.DEFAULT_GOAL := all

isort:
	poetry run isort . $(diff)

isort-check:
	poetry run isort --check . $(diff)

black:
	poetry run black . $(diff)

black-check:
	poetry run black --check . $(diff)

flake8:
	poetry run flake8 .

pylint:
	poetry run pylint */*.py

bandit:
	poetry run bandit -c pyproject.toml -r .

mypy:
	poetry run mypy .

test:
	poetry run pytest --ds=config.settings.test --durations=1 -p no:warnings -n auto

lint: isort black flake8 pylint mypy bandit

pipeline: isort-check black-check flake8 pylint mypy bandit

all: lint test
