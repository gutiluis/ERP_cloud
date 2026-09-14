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
* End-to-end (E2E) tests, if/when added

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

End-to-end tests are not currently part of the project.

If E2E testing is added, it should verify complete user workflows such as:

1. Open the storefront.
2. Browse products.
3. Add a product to the cart.
4. Retrieve and update the cart.
5. Start checkout.
6. Complete the payment workflow in the appropriate test environment.

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
