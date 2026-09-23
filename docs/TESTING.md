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
6. Complete the checkout workflow when the public checkout endpoint is available.

The E2E environment consists of three services:

* `db` — isolated MySQL E2E database
* `e2e_api` — Flask backend API configured for the E2E database
* `e2e_playwright` — Playwright test runner

Vite runs inside the `e2e_playwright` container. Playwright's `webServer` configuration starts Vite automatically before the tests run.

The E2E database is separate from the development and production databases.

### Run the E2E Tests

The recommended local E2E workflow is:

```bash
make e2e
```

This:

1. Builds and starts the E2E services.
2. Waits for the database and API readiness checks.
3. Runs the E2E database migrations.
4. Seeds deterministic test data.
5. Starts Vite through Playwright.
6. Runs the Playwright test suite.

The E2E environment does not require the developer to manually start the backend or frontend.

### E2E Database

The E2E backend connects to the dedicated `erp_e2e` database:

```text
mysql+pymysql://erp:erp@db:3306/erp_e2e
```

The database is isolated from the development database.

Migrations are applied with:

```bash
make e2e-migrate
```

Deterministic test data is created with:

```bash
make e2e-seed
```

The E2E database can be recreated safely because it uses a dedicated Docker volume.

### E2E Services

Start the E2E environment without running the tests:

```bash
make e2e-up
```

Check service status:

```bash
docker compose -f compose.e2e.yaml ps
```

The API service depends on the MySQL health check before becoming available.

### Run Playwright

Run the complete E2E suite:

```bash
make e2e-test
```

Playwright starts Vite on:

```text
http://127.0.0.1:5173
```

The browser accesses Vite through the loopback interface because Vite and Playwright run in the same container.

Vite proxies frontend API requests to the E2E Flask backend using:

```text
http://e2e_api:8000
```

The API target is configured through:

```text
VITE_API_TARGET
```

This keeps the frontend configuration independent of the E2E environment.

### Run a Specific Playwright Test

Run a specific test file:

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright \
    npx playwright test e2e/example.spec.ts
```

Replace `e2e/example.spec.ts` with the test file you want to run.

### Run Playwright in Debug Mode

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright \
    npx playwright test --debug
```

### Run Playwright in Headed Mode

```bash
docker compose -f compose.e2e.yaml run --rm e2e_playwright \
    npx playwright test --headed
```

Headed mode may require additional display configuration depending on the Docker environment.

## Test Artifacts

Playwright is configured to produce:

```text
frontend/results.json
frontend/test-results/
```

`results.json` contains the JSON test report.

`test-results/` contains Playwright test artifacts such as screenshots and traces when applicable.

These paths are bind-mounted from the Playwright container to the host so the artifacts remain available after the test container exits.

The Playwright configuration uses:

```text
trace: on-first-retry
screenshot: only-on-failure
```

### Stop the E2E Environment

Stop and remove the E2E services:

```bash
make e2e-down
```

This runs:

```bash
docker compose -f compose.e2e.yaml down -v --remove-orphans
```

The `-v` option removes the disposable E2E MySQL volume, ensuring the next E2E run starts with a clean database.

### Typical E2E Workflow

For normal development, use:

```bash
make e2e
```

To run the individual lifecycle steps:

```bash
make e2e-up
make e2e-migrate
make e2e-seed
make e2e-test
```

After testing:

```bash
make e2e-down
```

If an E2E test fails, the environment remains available so that logs and artifacts can be inspected before cleanup.

For example:

```bash
docker compose -f compose.e2e.yaml ps
docker compose -f compose.e2e.yaml logs e2e_api
```

Then clean up with:

```bash
make e2e-down
```

The same E2E Compose environment is used locally and in CI to keep the test environment consistent.

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
