# Testing

This document describes the testing strategy, test commands, test environment, and production verification process for ERP_cloud.

## Test Suites

The project currently includes:

* Backend test suite
* Frontend test suite
* Unit tests
* Integration tests
* API contract tests
* Production verification
* End-to-end (E2E) tests

---

## Backend

The backend tests are implemented with `pytest`.

Run the complete backend test suite:

```bash
pytest backend/tests
```

### Backend test coverage

Backend tests cover application behavior including:

* API routes
* Database interactions
* Cart operations
* Stripe checkout and webhook behavior
* Inventory behavior
* Error handling
* Business logic

---

## Frontend

The frontend test suite uses Vitest.

Run the complete frontend test suite:

```bash
cd frontend
npm test -- --run
```

### Frontend test coverage

Frontend tests cover application behavior including:

* API modules
* Product catalog behavior
* Cart API integration
* Component behavior
* Error handling

---

## Unit Tests

Unit tests verify individual functions, modules, or components in isolation.

Examples include:

* Backend business logic
* Utility functions
* Frontend API modules
* React component behavior

Unit tests should avoid unnecessary external dependencies and should be deterministic.

---

## Integration Tests

Integration tests verify that multiple application components work together correctly.

Examples include:

* Flask routes with the database
* Cart API with cart persistence
* Stripe checkout with application state
* Frontend API modules communicating with backend endpoints

---

## API Contract Tests

API contract tests verify that the frontend and backend agree on:

* HTTP methods
* API endpoints
* Request payloads
* Response structures
* HTTP status codes
* Error responses

API changes should update the corresponding tests so that frontend and backend expectations remain synchronized.

---

## E2E Tests

End-to-end tests use Playwright and run against the application in a dedicated Docker environment.

The E2E suite verifies complete user workflows such as:

1. Open the storefront.
2. Browse products.
3. Add a product to the cart.
4. Retrieve and update the cart.
5. Start checkout.
6. Complete the payment workflow in the appropriate test environment.

The E2E environment consists of four services:

* `db` — MySQL E2E database
* `e2e_api` — backend API
* `e2e_frontend` — frontend application
* `e2e_playwright` — Playwright test runner

The E2E database is separate from the development database.

### Start the E2E Environment

Build the E2E images and start the API, database, and frontend:

```bash
docker compose -f compose.e2e.yaml up -d --build
```

Check the service status:

```bash
docker compose -f compose.e2e.yaml ps
```

The database must be healthy and the API and frontend must be running before starting the Playwright tests.

### Seed the E2E Database

Populate the E2E database with test data:

```bash
docker compose -f compose.e2e.yaml exec e2e_api \
    python -m tests.seed_e2e
```

The seed script creates the test data required by the E2E tests.

### Run the E2E Tests

Run the complete Playwright test suite:

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright
```

Playwright accesses the frontend through the Docker Compose network using:

```text
http://e2e_frontend:4173
```

The `BASE_URL` environment variable is configured automatically by `compose.e2e.yaml`.

### Run a Specific Playwright Test

Run a specific test file:

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright \
    npx playwright test tests/example.spec.ts
```

Replace `tests/example.spec.ts` with the test file you want to run.

### Run Playwright in Debug Mode

Run the tests with Playwright's debugger:

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright \
    npx playwright test --debug
```

### Run Playwright in Headed Mode

To run the browser in headed mode:

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright \
    npx playwright test --headed
```

Headed mode may require additional display configuration depending on the Docker environment.

## Test Reports

Playwright generates its HTML report inside the `e2e_playwright` container.

Because the current Compose configuration does not mount a host directory for the Playwright report, the report is not persisted when the one-off container is removed with `--rm`.

If you want to inspect the report after a test run, run the Playwright container without `--rm`:

```bash
docker compose -f compose.e2e.yaml run e2e_playwright
```

Then inspect the generated report from the container or copy it to the host with `docker cp`.

If persistent host access to the report becomes necessary, add a volume for the Playwright report directory to `compose.e2e.yaml`.

## Stop the E2E Environment

Stop the E2E services:

```bash
docker compose -f compose.e2e.yaml down
```

The E2E MySQL volume is preserved.

To remove the E2E database and all associated volumes:

```bash
docker compose -f compose.e2e.yaml down -v
```

Use `down -v` when you want to start with a completely clean E2E database.

## Typical E2E Workflow

A normal E2E development cycle is:

```bash
# Build and start the E2E environment
docker compose -f compose.e2e.yaml up -d --build

# Seed the E2E database
docker compose -f compose.e2e.yaml exec e2e_api \
    python -m tests.seed_e2e

# Run Playwright
docker compose -f compose.e2e.yaml run --rm e2e_playwright

# Stop the E2E environment
docker compose -f compose.e2e.yaml down
```

If backend, frontend, or Playwright code changes, rebuild the affected image before running the tests:

```bash
docker compose -f compose.e2e.yaml build e2e_api e2e_frontend e2e_playwright
```

Then recreate the services:

```bash
docker compose -f compose.e2e.yaml up -d
```


See [`docs/testing.md`](docs/testing.md) for instructions on starting the E2E environment, seeding test data, running Playwright, and viewing test reports.

---

## Production Verification

Production verification should be performed after a production deployment.

### Production build

Verify that the production frontend builds successfully:

```bash
npm run build
```

### Docker image build

Build the production Docker images:

```bash
docker compose -f compose.prod.yaml build
```

Use the project's actual production Compose filename if different.

### Nginx / Reverse Proxy Verification

Verify that Nginx:

* Starts successfully.
* Serves the frontend application.
* Proxies `/api/` requests to the backend.
* Returns the correct HTTP status codes.
* Supports SPA routing.
* Applies the expected security headers.

### API Integration Verification

Verify the production API manually or with automated checks:

* Product API responds successfully.
* Cart API responds successfully.
* Invalid requests return appropriate errors.
* API responses match the documented contract.

### Error Handling Verification

Verify that expected failures are handled correctly:

* Invalid API requests
* Missing resources
* Invalid cart operations
* Backend errors
* Frontend API failures

Production verification must not use real payment credentials or real customer transactions.

---

## Required Commands

### Backend

```bash
pytest backend/tests
```

### Frontend

```bash
cd frontend
npm test -- --run
npm run build
```

### Production Docker Build

```bash
docker compose -f compose.prod.yaml build
```

---

## Test Environment / Setup

### Backend

Backend tests require the project's configured test environment and test database.

The test environment should be isolated from production data.

### Frontend

Frontend tests run with the project's configured Node.js, Vitest, and test environment.

Install dependencies before running tests:

```bash
cd frontend
npm install
```

---

## Known Limitations

The following limitations currently apply:

* No automated E2E test suite is currently implemented.
* Production verification is not a replacement for automated tests.
* External payment-provider behavior should be tested using Stripe test-mode resources.
* Some production infrastructure behavior must be verified after deployment.
* Test coverage should continue to expand as new application features are added.

---

## Docstrings

Public and non-trivial backend functions should include concise PEP 257-compatible docstrings.

Example:

```python
def checkout():
    """Create Stripe Checkout Session for a cart."""
```

Docstrings should explain the purpose of the function rather than repeat its implementation.

---

## Testing Expectations

A change should include or update tests when it changes application behavior.

Before merging a change:

1. Run the relevant backend tests.
2. Run the relevant frontend tests.
3. Run the complete test suites when practical.
4. Verify production builds for production-related changes.
5. Update this document when the testing strategy or required commands change.
