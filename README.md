>[!WARNING]
>CURRENTLY UNDER DEVELOPMENT

---

[![E2E Playwright](https://github.com/gutiluis/ERP_cloud/actions/workflows/e2e.yml/badge.svg?branch=testing)](https://github.com/gutiluis/ERP_cloud/actions/workflows/e2e.yml)
[![Frontend CI](https://github.com/gutiluis/ERP_cloud/actions/workflows/frontend-test.yml/badge.svg?branch=testing)](https://github.com/gutiluis/ERP_cloud/actions/workflows/frontend-test.yml)
[![Pytest CI](https://github.com/gutiluis/ERP_cloud/actions/workflows/pytest-ci.yml/badge.svg?branch=testing)](https://github.com/gutiluis/ERP_cloud/actions/workflows/pytest-ci.yml)


# ERP SaaS

Full-stack e-commerce plattform with an admin Panel, CRUD operations, public frontend, CI/CD, and containerization.

## Core Features

- Admin panel
- Product and product variant management
- Product catalog
- Shopping cart
- E-commerce checkout
- Stripe payments
- Inventory management
- Order processing

---

## How it works

### 1 - Clone Repository

```sh
git clone https://github.com/gutiluis/ERP_cloud.git
cd ERP_cloud/
cp .env.example .env
```

### 2 - Start all services

#### 2.1 - Development

```sh
make dev
```

---

### 3 - Test the Application

#### 3.1 - Testing Endpoint Routes

```sh
curl -i http://localhost/health
```

### 3.2 - Testing Live Docker Logs

```sh
docker compose logs -f --tail 10 -t
```

---

### 3.3 Testing Endpoint HTTP Method Routes

```sh
docker compose exec api flask routes
```

### 3.4 - Testing Pre-commit hooks

```sh
cd ERP_cloud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit run --all-files
```

### 3.5 - Testing Stripe testing after stripe cli and stripe login config, after order


```sh
stripe listen --forward-to localhost:8000/api/admin/stripe/webhook
```

### second terminal

```sh
npx stripe trigger payment_intent.succeeded
npx stripe trigger checkout.session.completed
```

---

## 4 - Admin User Setup

### 4.1 - Enter admin in the db and create adminuser table in mysql

```
docker compose exec api bash
flask shell
from app import db
from app.models.admin_user import AdminUser
from werkzeug.security import generate_password_hash
admin = AdminUser(
admin_id="adminid",
username="username",
email="<email@example.com>",
password_hash=generate_password_hash("some password")
)
db.session.add(admin)
db.session.commit()
```

---

## Tech-Stack

- Python
- Flask
- Gunicorn
- Nginx
- Docker
- MySQL
- Stripe
- CLI
- Pytest
- JavaScript
- JSON
- YAML
- Pre-commit
- SQLAlchemy
- Flask SQLAlchemy
- Flask Migrations
- Python dotenv
- Jinja2
- Werkzeug
- Ruff
- Bash
- GitHub/Git
- React
- Vite
- Tailwind CSS
- Vitest
- Jsdom
- ESLint
- React Router

---

## Contributing

If you are interested in reporting/fixing issues and contributing directly to the code base, please see [CONTRIBUTING.md](https://github.com/gutiluis/.github/blob/main/CONTRIBUTING.md) for more information on what we're looking for and how to get started.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](https://github.com/gutiluis/.github/blob/main/CODE_OF_CONDUCT.md).

---

## Security Policy

If you discover a security vulnerability, please review our [Security Policy](https://github.com/gutiluis/.github/blob/main/SECURITY.md) for reporting guidelines.

---

## Support

If you run into any issues or have questions, please check our [SUPPORT.md](https://github.com/gutiluis/.github/blob/main/SUPPORT.md) file for guidance, or reach out through one of our community channels below.

---

## Community

Info on reporting bugs, getting help, finding third-party tools and sample apps, and more can be found on our **Community** channels:
* **Discord:** [Community channel](https://discord.gg/5xdAFuadP)
* **Slack Workspace:** [technobool.slack.com](https://technobool.slack.com)
* **GitHub Discussions:** [Open a discussion](https://github.com/gutiluis/ERP_cloud/discussions)

---

## License

[MIT LICENSE](LICENSE)
