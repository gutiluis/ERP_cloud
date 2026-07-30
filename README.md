>[!WARNING]
>CURRENTLY UNDER DEVELOPMENT

# ERP SaaS


---

## how it works:

```
cp .env.example .env
```

---

## development:

### 1 - start all services same time:

```
docker compose up -d --build
```

---

### 2 - check mysql db connection with docker, or preferred way

### test connection with docker compose, programming languages, or sql

### does not require password

```
docker compose exec db bash # enter service name not container name
```

# -interactive -pseudo tty terminal makes a session active
```
docker compose exec -it db bash
docker compose exec -it api bash
```

### 2.1 - or check mysql prompt without entering first bash. needs the password. without opening container shell first. enter password

```
docker compose exec db mysql -u erp -p erp
```

### 2.2 - or run command with docker compose passing shell and mysql 

```
docker compose exec db mysql -u erp -perp -e "SHOW DATABASES;"
docker compose exec db mysql -u erp -perp erp -e "SHOW TABLES;"
```

### 2.3 - or check with pymysql:
/tests/test_connection.py

---

### 3.1 - check route ok
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ # still in flask. shoud be UI
http://127.0.0.1:8000/api/admin/customers/

---

### 4.1 - run flask migrations after building all containers

```
cd /ERP
docker compose exec api flask --app wsgi db init
docker compose exec api flask --app wsgi db migrate -m "initial schema" # when models change
```

# when erp.customers table is not found even though the migrations folder exists

```
docker compose exec api flask --app wsgi db migrate -m "map tables"
docker compose exec api flask --app wsgi db upgrade # apply migration
```

### 4.2 check migrations

```
docker compose exec api flask db history
docker compose exec api flask db current
docker compose exec -it servicename sh
```

### 4.3 check routes

```
docker compose exec api flask routes
```

---

### 5 - check tables were mapped

```
cd /ERP
docker compose exec db mysql -u root -p
```

---

### 6 - update migrations and frontend even though table rows are in the container

```
docker compose up --build -d api
```

### or 

```
docker compose restart api
```

---

### 7 - enter admin

```
docker compose exec api bash
flask shell
```

---

### TODO:

### 7 -  make pytest for app/models


### 8 - design frontend: vire, react, tailwind

---

# TODO:

# oracle vm

# buy domain

# one user admin account to manage everything

# finish tests for backend and frontend

# finish docs

# finish frontend

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
