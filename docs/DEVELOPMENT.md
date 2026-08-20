# Development

**Created:** 2026-08-19

## Test Database

The development Docker Compose environment uses MySQL with the `erp` database. Backend tests use a separate `erp_test` database so tests do not modify the development database.

### Databases

```text
MySQL container
├── erp       → development
└── erp_test  → pytest
```

The application uses:

```text
mysql+pymysql://erp:erp@db:3306/erp
```

When pytest runs from the host, it uses:

```text
mysql+pymysql://erp:erp@127.0.0.1:3307/erp_test
```

### Create the Test Database

The `erp_test` database is not automatically created by the current `docker-compose.yml`. If it does not exist, create it manually:

```bash
docker compose exec db mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS erp_test;"
```

Grant the application/test user access:

```bash
docker compose exec db mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON erp_test.* TO 'erp'@'%'; FLUSH PRIVILEGES;"
```

Verify access:

```bash
docker compose exec db mysql -uerp -perp -e "USE erp_test; SELECT DATABASE();"
```

Expected result:

```text
DATABASE()
erp_test
```

### Run Backend Tests

Run pytest against the test database:

```bash
DATABASE_URL='mysql+pymysql://erp:erp@127.0.0.1:3307/erp_test' python -m pytest backend/tests
```

The `DATABASE_URL` must point to `erp_test` when running tests manually.

Do not point pytest at the development `erp` database because tests may create, modify, or delete database records.

### Pre-commit

The pytest pre-commit hook is configured to use the test database:

```yaml
entry: env DATABASE_URL=mysql+pymysql://erp:erp@127.0.0.1:3307/erp_test python -m pytest backend/tests
```

If pytest fails with MySQL error `1044 (Access denied)`, first verify that `erp_test` exists and that the `erp` user has privileges on it.

### Current Development Setup

The current setup uses one MySQL container with separate development and test databases. A second MySQL container or a second database service is not required solely for pytest.

A dedicated test Compose configuration can be introduced later if the test environment needs to be isolated further or needs to match CI more closely.

---

**Created:** 2026-08-19

## Development Workflow

ERP development is tracked through GitHub Issues, Pull Requests, and GitHub Projects.

### Current Workstreams

#### Backend Domain & Stripe
Reconcile and test the Order → Checkout → Invoice → Payment → Stripe workflow.

#### Production Readiness
Track the work required to prepare the ERP for production, including frontend development, testing, HTTPS, domain configuration, Oracle Cloud deployment, documentation, CI/CD, and authorized security testing.

### Development Project

**ERP Development** is the primary GitHub Project for iterative development.

The project tracks work from planning through implementation, review, testing, and completion.

The repository uses GitHub Issues for individual work items and Pull Requests for implementation and review.

[ERP Development Project](https://github.com/users/gutiluis/projects/4)
