PROJECT_NAME	= backend-pet
PROJECT_VERSION	= $(shell poetry version -s)
PACKAGE_NAME	= backend_pet

lint:
	poetry run ruff check --fix .

fmt:
	poetry run ruff format .

test:
	poetry run flake8 src/${PACKAGE_NAME}
	poetry run mypy src/${PACKAGE_NAME}
	poetry run pytest

down:
	docker-compose down

build:
	docker-compose build

up:
	docker-compose up

run: down fmt build up