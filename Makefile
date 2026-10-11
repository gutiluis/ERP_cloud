.PHONY: dev prod down migrate upgrade test lint \
	e2e e2e-up e2e-migrate e2e-seed e2e-test e2e-down

dev:
	docker compose up -d --build

prod:
	docker compose -f compose.production.yaml up -d --build

down:
	docker compose down --remove-orphans

migrate:
	docker compose run --rm --entrypoint flask api --app wsgi db migrate

upgrade:
	docker compose run --rm --entrypoint flask api --app wsgi db upgrade

test:
	docker compose run --rm --entrypoint pytest api
# backend
lint:
	pre-commit run --all-files

e2e:
	$(MAKE) e2e-up
	$(MAKE) e2e-migrate
	$(MAKE) e2e-seed
	$(MAKE) e2e-test

E2E_COMPOSE = docker compose --env-file .env.e2e -f compose.e2e.yaml

e2e-up:
	$(E2E_COMPOSE) up -d --build

e2e-migrate:
	$(E2E_COMPOSE) exec e2e-api \
		flask --app wsgi db upgrade

e2e-seed:
	$(E2E_COMPOSE) exec e2e-api \
		python -m tests.seed_e2e

# Remove containers and the E2E database volume after running.
e2e-test:
	$(E2E_COMPOSE) run --rm e2e_playwright

e2e-down:
	$(E2E_COMPOSE) down -v --remove-orphans
