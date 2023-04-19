install:
	poetry install

build:
	poetry build

check: lint test

lint:
	poetry run flake8

test:
	poetry run pytest

dev:
	poetry run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
