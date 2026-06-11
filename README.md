# TODO:
# change docker to use python-dotenv
# oracle vm
# flask production server change from development server
# buy domain
# one user admin account to manage everything
# finish tests for backend and frontend
# finish docs
# finish frontend

---

# how it works:
cp .env.example .env

---
# development:
# 1 start all services same time:
docker compose up -d --build

---

# 2- check mysql db connection with docker, or preferred way
# test connection with docker compose, programming languages, or sql
# does not require password
docker compose exec db bash # enter service name not container name


# 2.1 - or check mysql prompt without entering first bash. needs the password. without opening container shell first. enter password
docker compose exec db mysql -u erp -p erp


# 2.2 - or run command with docker compose passing shell and mysql 
docker compose exec db mysql -u erp -perp -e "SHOW DATABASES;"
docker compose exec db mysql -u erp -perp erp -e "SHOW TABLES;"

# 2.3 - or check with pymysql:
/tests/test_connection.py


---
# 3.1 - check route ok
http://127.0.0.1:8000/health 

---

# 4.1 - run flask migrations
cd /ERP
docker compose exec api flask --app wsgi db initial

# 4.2 -  make pytest for app/models

---

# TODO:
# 6 - check normal route/view
http://127.0.0.1:500

# TODO:
# 7 - design frontend