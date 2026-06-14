#!/usr/bin/env bash

# filename: entrypoint.sh
 
# descr: run flask migrations after containers run to check models are mapping to the mysql db
# before flask app starts
# after the db container is starting
# 1. docker starts api container
# 2. entrypoint.sh starts immediately
# 3. entrypoint waits for DB (nc loop)
# 4. DB becomes ready
# 5. migrations run
# 6. gunicorn starts
#


set -e
date -u


echo "[INFO] Waiting for DB..."
# 3306 networking
while ! nc -z db 3306; do
    echo "[INFO] Waiting for database..."
    sleep 1
done;

echo "[WARN] DEBUG MODE IS ON!!! TURN IT OFF IN PRODUCTION ROOKIE!!"
echo "[INFO] DB is up..."
echo "[INFO] Running application..."
# gunicorn upfront and nginx behind. # put nginx upfront and gunicorn behind for production.
# any lines after exec will never execute
# after exec the terminal closes
# it wasnt debugging so added defualt.conf file and changed frontend.Dockerfile and nging.Dockerfile
exec gunicorn -b 0.0.0.0:5000 wsgi:app --log-level=debug --reload