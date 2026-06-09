# how it works:
cp .env.example .env

---

# development:
# 1- first make mysql container db with docker
docker compose up -d db

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

# 3 - after testing and building the db docker service build the api service
docker compose up --build api


---

# 4 - run flask with the virtual environment
source venv/bin/activate
flask --app app run

---

# 5 - check route ok
http://127.0.0.1:5000/health 

---

# 6 - check normal route/view
http://127.0.0.1:500
