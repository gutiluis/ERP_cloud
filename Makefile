.PHONY: dev prod down migrate upgrade test lint \
	e2e e2e-up e2e-migrate e2e-seed e2e-test e2e-down

dev:
	docker compose up -d --build

prod:
	docker compose -f compose.production.yaml up -d --build

down:
	docker compose down

migrate:
	docker compose run --rm --entrypoint flask api --app wsgi db migrate

upgrade:
	docker compose run --rm --entrypoint flask api --app wsgi db upgrade

test:
	docker compose run --rm api pytest
# backend
lint:
	pre-commit run --all-files

e2e:
	$(MAKE) e2e-up
	$(MAKE) e2e-migrate
	$(MAKE) e2e-seed
	$(MAKE) e2e-test

e2e-up:
	docker compose -f compose.e2e.yaml up -d --build

e2e-migrate:
	docker compose -f compose.e2e.yaml exec e2e_api \
		flask --app wsgi db upgrade

e2e-seed:
	docker compose -f compose.e2e.yaml exec e2e_api \
		python -m tests.seed_e2e
# remove container after running
e2e-test:
	docker compose -f compose.e2e.yaml run --rm e2e_playwright

e2e-down:
	docker compose -f compose.e2e.yaml down -v --remove-orphans
