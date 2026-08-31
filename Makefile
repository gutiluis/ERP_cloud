.PHONY: dev prod down migrate upgrade test lint
# run with make dev, down, etc...
dev:
	docker compose up -d --build

prod:
	docker compose -f compose.production.yaml up -d --build

down:
	docker compose down

migrate:
	docker compose run --rm api flask --app wsgi db migrate

upgrade:
	docker compose run --rm api flask --app wsgi db upgrade

test:
	docker compose run --rm api pytest

lint:
	pre-commit run --all-files
