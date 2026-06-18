### how it works:
cp .env.example .env

---

### development:

### 1 - start all services same time:
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

### 2.3 - or check with pymysql:
/tests/test_connection.py


---
### 3.1 - check route ok
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ # still in flask. shoud be UI
http://127.0.0.1:8000/api/admin/customers/

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

### TODO:

### 7 -  make pytest for app/models


### 8 - design frontend: vire, react, tailwind

---

# TODO:

# change docker to use python-dotenv

# oracle vm

# buy domain

# one user admin account to manage everything

# finish tests for backend and frontend

# finish docs

# finish frontend
