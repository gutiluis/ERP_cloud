#!/usr/bin/env bash




# file: /scripts/containers-and-migrations.sh
# descr: development script. change migrations to outside the containers after.
# migrations should be in git. when inside containers they aren't committed...

# add for production:
# services:  api:  volumes:  - ./migrations:/app/migrations







set -e
date -u

docker compose down -v

sleep 5

docker compose up -d --build
echo "[INFO] AWAITING CONTIANERS"
sleep 7

# migrations
docker compose exec api flask --app wsgi db init

sleep 2
docker compose exec api flask --app wsgi db migrate -m "initial schema"

sleep 2
docker compose exec api flask --app wsgi db upgrade