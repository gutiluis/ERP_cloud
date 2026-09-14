# Development

## Development Database

The development Docker Compose environment uses MySQL with the `erp` database.

The application connects to the development database using:

```text
mysql+pymysql://<username>:<password>@db:3306/erp
```

The development database is intended for local application development and should not be used as the backend test database.

### Current Development Setup

The current development environment uses Docker Compose with a MySQL container.

The database architecture is:

```text
MySQL container
└── erp → development
```

Backend tests use a separate `erp_test` database to prevent test operations from modifying development data. Test database setup and test execution are documented separately in `docs/TESTING.md`.

A dedicated test Compose configuration can be introduced later if the test environment needs to be isolated further or needs to match CI more closely.

---

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
