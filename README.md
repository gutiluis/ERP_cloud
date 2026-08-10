# how it works

cp .env.example .env

---

### development

### 1 - start all services same time

docker compose up -d --build

---

### 2 - check mysql db connection with docker, or preferred way

### test connection with docker compose, programming languages, or sql

### does not require password

docker compose exec db bash # enter service name not container name

# -interactive -pseudo tty terminal makes a session active

docker compose exec -it db bash
docker compose exec -it api bash

### 2.1 - or check mysql prompt without entering first bash. needs the password. without opening container shell first. enter password

docker compose exec db mysql -u erp -p erp

### 2.2 - or run command with docker compose passing shell and mysql

docker compose exec db mysql -u erp -perp -e "SHOW DATABASES;"
docker compose exec db mysql -u erp -perp erp -e "SHOW TABLES;"

### 2.3 - or check with pymysql

/tests/test_connection.py

---

### 3.1 - check route ok

<http://127.0.0.1:8000/health>
<http://127.0.0.1:8000/> # still in flask. shoud be UI
<http://127.0.0.1:8000/api/admin/customers/>

### 3.2 - cheeck logs

docker compose logs -f --tail 10 -t

---

### 4.1 - run flask migrations after building all containers

cd /ERP
docker compose exec api flask --app wsgi db init
docker compose exec api flask --app wsgi db migrate -m "initial schema" # when models change

# when erp.customers table is not found even though the migrations folder exists

docker compose exec api flask --app wsgi db migrate -m "map tables"
docker compose exec api flask --app wsgi db upgrade # apply migration

### 4.2 check migrations

docker compose exec api flask db history
docker compose exec api flask db current
docker compose exec -it servicename sh

### 4.3 check routes

docker compose exec api flask routes

---

### 5 - check tables were mapped

cd /ERP
docker compose exec db mysql -u root -p

---

### 6 - update migrations and frontend even though table rows are in the container

docker compose up --build -d api

### or

docker compose restart api

---

### 7 - enter admin in the db and create adminuser table in mysql

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

### 7.1 - make/load customer-model either from frontend or backend model/route

### 7.2 - make cart with customer/seller

---

### 8 - stripe testing after stripe cli and stripe login config

### make order needed for checkout, webhook

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

### make items

for item in cart.items:
    order_item = OrderItem(
        order_id=order.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.price
    )

    db.session.add(order_item)

db.session.commit()

select * from orders;

## 8.1 after order

npx stripe listen --forward-to localhost:8000/api/admin/stripe/webhook

# second terminal

npx stripe trigger payment_intent.succeeded
npx stripe trigger checkout.session.completed

---

### TODO

### 7 -  make pytest for app/models

### 8 - design frontend: vire, react, tailwind

---

# TODO

# oracle vm

# buy domain

# one user admin account to manage everything

# finish tests for backend and frontend

# finish docs

# finish frontend

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
