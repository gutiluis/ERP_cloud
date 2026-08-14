>[!WARNING]
>CURRENTLY UNDER DEVELOPMENT

# ERP SaaS

Admin Panel, CRUD operations, public frontend

---

## how it works

```
cp .env.example .env
```

### - start all services same time

```
docker compose up -d --build
```

### 2 - check mysql db connection with docker, or preferred way

### test connection with docker compose, programming languages, or sql

### does not require password

```
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

### 2.3 - or check with pymysql

/tests/test_connection.py

---

### 3.1 - check route ok

http://127.0.0.1:8000/health
http://127.0.0.1:8000/ # still in flask. shoud be UI
http://127.0.0.1:8000/api/admin/customers/

### 3.2 - cheeck logs

```sh
docker compose logs -f --tail 10 -t
```

---

### 4.1 - run flask migrations after building all containers

```sh
cd /ERP
docker compose exec api flask --app wsgi db init
docker compose exec api flask --app wsgi db migrate -m "initial schema" # when models change
```

### when erp.customers table is not found even though the migrations folder exists

```sh
docker compose exec api flask --app wsgi db migrate -m "map tables"
docker compose exec api flask --app wsgi db upgrade
```

### 4.2 check migrations

```sh
docker compose exec api flask db history
docker compose exec api flask db current
docker compose exec -it servicename sh

```

### 4.3 check routes

```sh
docker compose exec api flask routes
```

---

### 5 - check tables were mapped

```sh
cd /ERP
docker compose exec db mysql -u root -p
```

---

### 6 - update migrations and frontend even though table rows are in the container


### or

```sh
docker compose up --build -d api
```

### or

```sh
docker compose restart api
```

---

### 7 - enter admin in the db and create adminuser table in mysql

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


### 7.1 - make/load customer-model either from frontend or backend model/route

### 7.2 - make cart with customer/seller



---

### 8 - stripe testing after stripe cli and stripe login config

### make order needed for checkout, webhook

```sh
docker compose exec api bash
flask shell
from app import db
from app.models.orders import Order
order = Order(
    customer_id=customer.id, # needs customer
    status="pending",
    total_amount=cart.total_amount
)
db.session.add(order)
db.session.flush()
```

### make items

```python
for item in cart.items:
    order_item = OrderItem(
        order_id=order.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.price
    )

    db.session.add(order_item)

db.session.commit()
```


### 8.1 after order

```sh
stripe listen --forward-to localhost:8000/api/admin/stripe/webhook
```

### second terminal

```sh
npx stripe trigger payment_intent.succeeded
npx stripe trigger checkout.session.completed
```

---

### TODO

### oracle vm

### buy domain

### one user admin account to manage everything

### finish tests for backend and frontend

### finish docs

### finish frontend

### http to https

---

buyer
cart
add/remove cartItem
checkout
flask api load cart
create order pending status
create stripe checkout session
buyer pays stripe
wbhook
    paid order status update
    payment creation
    invoice creation
    update inventory

---

## Tech-Stack

- Python
- Flask
- Gunicorn
- Docker
- MySQL

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
