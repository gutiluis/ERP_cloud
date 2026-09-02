>[!WARNING]
>CURRENTLY UNDER DEVELOPMENT

---

# ERP SaaS

Admin Panel, CRUD operations, public frontend, e-commerce, CI/CD, Containers, Web Frameworks

**Flow**
buyer
cart
add/remove cartItem
checkout
flask api load cart
create order pending status
create stripe checkout session
buyer pays stripe
webhook
    paid order status update
    payment creation
    invoice creation
    update inventory

---

## how it works

```sh
git clone https://github.com/gutiluis/ERP_cloud.git
cd ERP_cloud/
cp .env.example .env
```

### 1 - Start all services

```sh
docker compose up -d --build
```

### 1.1 - Development

```sh
docker compose -f compose.production.yaml up -d --build
```

### 2 - check mysql db connection with docker, or preferred way

### test connection with docker compose, programming languages, or sql

### does not require password

```sh
docker compose exec db bash
```

### -interactive -pseudo tty terminal makes a session active

```sh
docker compose exec -it db bash
docker compose exec -it api bash
```

### 2.1 - or check mysql prompt without entering first bash. needs the password. without opening container shell first. enter password


### 2.2 - or run command with docker compose passing shell and mysql. this is inside the db container

```sh
docker compose exec db mysql -u erp -p erp
docker compose exec db mysql -u erp -perp -e "SHOW DATABASES;"
docker compose exec db mysql -u erp -perp erp -e "SHOW TABLES;"
```

### pytest testig db from inside db container
### test erp_test database inside the db container. connection context.

```sh
docker compose exec db mysql -u erp -p -h localhost erp_test
```

---

### 3.1 - Testing Endpoint Routes

```sh
curl -i [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
curl -i [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
```

### 3.2 - Testing Live Docker Logs

```sh
docker compose logs -f --tail 10 -t
```

---

### 4 - Testing Database and pre-commit hooks

```sh
docker compose exec db mysql -u root -p
```

### 4.1 - Create MySQL Testing DB for Pytest inside pre-commit and apply migrations

```sql
CREATE DATABASE erp_test
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
SHOW DATABASES LIKE 'erp_test';
GRANT ALL PRIVILEGES ON erp_test.* TO 'erp'@'%';
FLUSH PRIVILEGES;
```

### 4.2 - Run Flask Db Migrations

```sh
cd /ERP_cloud
docker compose exec api flask --app wsgi db init
docker compose exec api flask --app wsgi db migrate -m "initial schema"
docker compose exec api flask --app wsgi db upgrade
```

### 4.3 Populate Testing Database with migrations

```sh
docker compose exec api flask db history
docker compose exec api flask db current
docker compose exec -it servicename sh
```

### 4.3.1 - Move migrations into local host from container

```sh
docker cp erp_api:/app/migrations ./migrations
```

### 4.4 Testing Migrations Endpoint HTTP Method Routes

```sh
docker compose exec api flask routes
```

### 4.5 - Testing Pre-commit hooks

```sh
cd ERP_cloud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit run --all-files
```

---

### 6 - update migrations and frontend even though table rows are in the container


```sh
docker compose up --build -d api
```

### or

```sh
docker compose restart api
```

---

## Admin User Setup

### 7 - Enter admin in the db and create adminuser table in mysql

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

### 8 - Testing Stripe testing after stripe cli and stripe login config, after order


```sh
stripe listen --forward-to localhost:8000/api/admin/stripe/webhook
```

### second terminal

```sh
npx stripe trigger payment_intent.succeeded
npx stripe trigger checkout.session.completed
```

---

## Tech-Stack

- Python
- Flask
- Gunicorn
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
- Oracle Cloud
- React
- Vite
- Tailwind CSS
- Vitest
- Jsdom
- ESLint

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
