# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased]

### Added

* **frontend/e2e:** Playwright end-to-end test for the public product-to-cart flow
* **compose.e2e.yaml:** isolated E2E environment with MySQL, Flask API, frontend, and Playwright services
* **backend/tests/seed_e2e.py:** seed data for the E2E test environment

### Changed

* **frontend/playwright.config.js:** configure Playwright for local and CI execution
* **frontend/vite.config.js:** make the API proxy target configurable for E2E execution

## [1.3.0](https://github.com/gutiluis/ERP_cloud/compare/v1.2.0...v1.3.0) (2026-06-28)

### Added

* **routes/invoices.py:** invoice index, void, detail routes
* **routes/products.py:** products and product variants admin public routes

## [1.1.1] - [2026-06-25]

### Added
* **app/auth:** add flask-login authentication. Impelement further on
* **routes/customers.py:** add customers login_required

## [1.1.0] - [2026-06-19]


### Added

* **admin/customers:** implemented flasgger documentation for customer details


## [0.1.0] - [2026-06-18]

### Added
- Initial project structure and environment configuration.
- Core API routing framework and initial endpoints.
- Base Jinja templates, layouts, and global context variables.
