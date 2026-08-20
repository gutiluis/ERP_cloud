#!/usr/bin/env bash




# file: /scripts/containers-and-migrations.sh
# descr: development script. change migrations to outside the containers after.
# migrations should be in git. when inside containers they aren't committed...

# add for production:
# services:  api:  volumes:  - ./migrations:/app/migrations







date -u

docker compose down -v

sleep 5

docker compose up -d --build
echo "[INFO] AWAITING CONTIANERS"
sleep 7

# migrations
docker compose exec api flask --app wsgi db init
echo "[INFO] INITIALIZE MIGRATIONS"

sleep 4
docker compose exec api flask --app wsgi db migrate -m "initial schema"
echo "[INFO] MIGRATIONS"

sleep 4
docker compose exec api flask --app wsgi db upgrade
echo "[INFO] MIGRATIONS UPGRADED"
